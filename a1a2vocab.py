import re
import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import Optional, List, Dict
from supabase import create_client, Client, AuthApiError

# -------------------------------
# Setup
# -------------------------------
st.set_page_config(page_title="Inventory (Supabase)", page_icon="📦", layout="wide")

url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_ANON_KEY", "")
sb: Client = create_client(url, key)

MIN_PASSWORD_LENGTH = 6

# (Optional) quick debug so you can confirm the project pointed to by this app
st.caption(f"Target project host: {url.split('//')[-1]}")
st.caption(f"Anon key prefix: {key[:10]}… len={len(key)}")

# -------------------------------
# Diagnostics & helpers
# -------------------------------
def validate_config():
    """Basic sanity checks for Supabase config before doing any network calls."""
    problems = []
    if not url or ".supabase.co" not in url:
        problems.append("❌ `SUPABASE_URL` is missing or looks incorrect.")
    if not key or len(key) < 20:
        problems.append("❌ `SUPABASE_ANON_KEY` is missing or too short.")
    if problems:
        for p in problems:
            st.error(p)
        st.stop()

def show_supabase_error(stage: str, err: Exception):
    """Surface useful fields from Supabase exceptions inside Streamlit."""
    parts = [f"{stage} failed."]
    for attr in ("message", "msg", "code", "status"):
        val = getattr(err, attr, None)
        if val:
            parts.append(f"{attr}: {val}")
    resp = getattr(err, "response", None)
    if resp is not None:
        try:
            parts.append(f"response_json: {resp.json()}")
        except Exception:
            try:
                parts.append(f"response_text: {resp.text}")
            except Exception:
                pass
    parts.append(f"args: {getattr(err, 'args', None)}")
    st.error("\n".join(str(p) for p in parts))
    st.exception(err)  # still useful locally

def success_rerun(msg: str):
    st.success(msg)
    st.rerun()

# -------------------------------
# Email cleaning/validation
# -------------------------------
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

def clean_email(s: str) -> str:
    return (s or "").strip().replace("\u200b", "").replace("\u00A0", "")

def is_valid_email(s: str) -> bool:
    return bool(EMAIL_RE.match(s))

# -------------------------------
# Session helpers
# -------------------------------
def attach_tokens(access: str, refresh: str):
    """Attach tokens to both auth and postgrest clients (RLS needs the bearer)."""
    sb.auth.set_session(access_token=access, refresh_token=refresh)
    sb.postgrest.auth(access)

def reattach_session():
    """Re-attach tokens on reruns if saved (handle expired sessions)."""
    access = st.session_state.get("jwt")
    refresh = st.session_state.get("rt")
    if access and refresh:
        try:
            sb.auth.set_session(access_token=access, refresh_token=refresh)
            sb.postgrest.auth(access)
        except AuthApiError:
            for key in ("user", "jwt", "rt", "org_id", "role"):
                st.session_state.pop(key, None)
            st.warning("Session expired. Please log in again.")
        except Exception:
            for key in ("user", "jwt", "rt", "org_id", "role"):
                st.session_state.pop(key, None)

def logout():
    """Clear only local state; do not try to unauth PostgREST with None token."""
    for k in ("user", "jwt", "rt", "org_id", "role"):
        st.session_state.pop(k, None)
    st.rerun()

def check_db_identity():
    """
    Optional debug: show who the DB thinks we are.
    Requires two helper RPCs in DB (safe to try even if missing):
      whoami() returns uuid; whoami_role() returns text
    """
    try:
        who = sb.rpc("whoami").execute().data
        role = sb.rpc("whoami_role").execute().data
        st.info(f"DB sees user: {who}, role: {role}")
    except Exception:
        pass

validate_config()
reattach_session()

# -------------------------------
# Org & membership
# -------------------------------
def get_user_orgs(user_id: str) -> List[Dict]:
    res = sb.table("org_members").select("org_id, role").eq("user_id", user_id).execute()
    return res.data or []

def create_store_for_logged_in_user(store_name: str) -> str:
    """
    Creates org (name only) + membership(owner) using the current user's JWT.
    Does NOT require an owner_id column on orgs.
    """
    # Ensure PostgREST is using the current JWT *now*
    jwt = st.session_state.get("jwt")
    if jwt:
        sb.postgrest.auth(jwt)

    user_id = st.session_state["user"]["id"]

    # 1) Create the org (no owner_id field assumed)
    try:
        org = sb.table("orgs").insert({"name": store_name}).execute()
    except Exception as e:
        # Surface useful info from PostgREST/Supabase errors
        msg = code = ""
        try:
            payload = e.args[0] if e.args else {}
            msg = (payload.get("message") or "").strip()
            code = (payload.get("code") or "").strip()
        except Exception:
            pass
        raise Exception(f"Org insert failed (code={code}): {msg}") from e

    org_id = org.data[0]["id"]

    # 2) Create membership for current user (owner)
    try:
        sb.table("org_members").insert({
            "user_id": user_id,
            "org_id": org_id,
            "role": "owner",
        }).execute()
    except Exception as e:
        msg = code = ""
        try:
            payload = e.args[0] if e.args else {}
            msg = (payload.get("message") or "").strip()
            code = (payload.get("code") or "").strip()
        except Exception:
            pass
        raise Exception(f"Membership insert failed (code={code}): {msg}") from e

    return org_id

def ensure_membership_and_bootstrap(default_store_name: str = "My Store") -> None:
    """
    Guarantees the logged-in user has an org + membership in session state.
    If none exists, creates one and then sets st.session_state['org_id']/['role'].
    """
    jwt = st.session_state.get("jwt")
    if jwt:
        sb.postgrest.auth(jwt)

    user_id = st.session_state["user"]["id"]

    rows = get_user_orgs(user_id)
    if not rows:
        try:
            create_store_for_logged_in_user(default_store_name)
        except Exception as e:
            show_supabase_error("Auto-create org", e)
            st.stop()
        # read again (race-safe)
        rows = get_user_orgs(user_id)

    if not rows:
        st.error("Could not find your organization after creating it. "
                 "Check RLS on org_members (select/insert) so user_id = auth.uid().")
        check_db_identity()
        st.stop()

    st.session_state["org_id"] = rows[0]["org_id"]
    st.session_state["role"] = rows[0]["role"]
    st.rerun()

# -------------------------------
# Data access (Supabase)
# -------------------------------
def list_products(org_id: str) -> pd.DataFrame:
    res = sb.table("products").select("*").eq("org_id", org_id).order("name").execute()
    return pd.DataFrame(res.data or [])

def upsert_product(org_id: str,
                   pid: Optional[str],
                   sku: str,
                   name: str,
                   category: Optional[str],
                   unit: Optional[str],
                   unit_cost: float,
                   price: float,
                   min_stock: float):
    now = datetime.utcnow().isoformat()
    data = {
        "org_id": org_id,
        "sku": sku,
        "name": name,
        "category": (category or None),
        "unit": (unit or "pcs"),
        "unit_cost": float(unit_cost or 0),
        "price": float(price or 0),
        "min_stock": float(min_stock or 0),
        "updated_at": now,
    }
    if pid:
        sb.table("products").update(data).eq("id", pid).eq("org_id", org_id).execute()
    else:
        data["created_at"] = now
        ins = sb.table("products").insert(data).execute()
        new_id = ins.data[0]["id"]
        sb.table("stock").upsert({"product_id": new_id, "qty": 0}).execute()

def delete_product(org_id: str, pid: str):
    sb.table("products").delete().eq("id", pid).eq("org_id", org_id).execute()

def get_stock_df(org_id: str) -> pd.DataFrame:
    prods = list_products(org_id)
    if prods.empty:
        return pd.DataFrame(columns=["id", "sku", "name", "unit", "qty", "min_stock", "category"])
    ids = prods["id"].tolist()
    st_rows = sb.table("stock").select("*").in_("product_id", ids).execute().data
    stock = pd.DataFrame(st_rows or []).rename(columns={"product_id": "id"})
    merged = prods.merge(stock[["id", "qty"]], on="id", how="left")
    merged["qty"] = merged["qty"].fillna(0)
    return merged[["id", "sku", "name", "unit", "qty", "min_stock", "category"]]

def receive_stock(org_id: str, product_id: str, qty: float, unit_cost: float):
    cur = sb.table("stock").select("qty").eq("product_id", product_id).single().execute().data or {"qty": 0}
    new_qty = float(cur["qty"] or 0) + float(qty)
    sb.table("stock").upsert({
        "product_id": product_id,
        "qty": new_qty,
        "updated_at": datetime.utcnow().isoformat()
    }).execute()
    sb.table("products").update({"unit_cost": float(unit_cost)}).eq("id", product_id).eq("org_id", org_id).execute()

def sell_items(org_id: str, lines: List[Dict], ref: Optional[str]):
    total = sum(float(l["qty"]) * float(l["unit_price"]) for l in lines)
    sale = sb.table("sales").insert({"org_id": org_id, "ref": (ref or None), "total": total}).execute().data[0]
    sale_id = sale["id"]
    for l in lines:
        sb.table("sale_items").insert({
            "sale_id": sale_id,
            "product_id": l["product_id"],
            "qty": float(l["qty"]),
            "unit_price": float(l["unit_price"]),
        }).execute()
        cur = sb.table("stock").select("qty").eq("product_id", l["product_id"]).single().execute().data or {"qty": 0}
        new_qty = float(cur["qty"] or 0) - float(l["qty"])
        sb.table("stock").upsert({
            "product_id": l["product_id"],
            "qty": new_qty,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

def adjust_stock(product_id: str, new_qty: float):
    sb.table("stock").upsert({
        "product_id": product_id,
        "qty": float(new_qty),
        "updated_at": datetime.utcnow().isoformat()
    }).execute()

def list_sales(org_id: str) -> pd.DataFrame:
    res = sb.table("sales").select("*").eq("org_id", org_id).order("created_at", desc=True).limit(50).execute()
    return pd.DataFrame(res.data or [])

# -------------------------------
# UI Pages
# -------------------------------
def page_dashboard():
    st.markdown("# Dashboard")
    org_id = st.session_state["org_id"]
    stock = get_stock_df(org_id)
    c1, c2, c3 = st.columns(3)
    total_items = len(stock)
    total_qty = float(stock["qty"].sum()) if not stock.empty else 0
    low = stock[stock["qty"] < stock["min_stock"]] if not stock.empty else pd.DataFrame()
    with c1:
        st.metric("Item count", total_items)
    with c2:
        st.metric("Total stock on hand", f"{total_qty:.2f}")
    with c3:
        st.metric("Low-stock items", 0 if stock.empty else int((stock["qty"] < stock["min_stock"]).sum()))
    st.subheader("Low stock")
    if low.empty:
        st.info("No low-stock items. 🎉")
    else:
        st.dataframe(low[["sku", "name", "qty", "min_stock", "category"]], use_container_width=True)
    st.subheader("Recent sales")
    st.dataframe(list_sales(org_id), use_container_width=True)

def page_products():
    st.markdown("# Products")
    org_id = st.session_state["org_id"]
    items = list_products(org_id)
    with st.expander("➕ Create / Edit product", expanded=True):
        edit = st.checkbox("Edit existing product", key="prod_edit")
        row = None
        if edit and not items.empty:
            items["display"] = items["sku"] + " — " + items["name"]
            sel = st.selectbox("Select product", items["display"], index=None, key="prod_select")
            if sel:
                row = items.loc[items["display"] == sel].iloc[0]
        sku = st.text_input("SKU", value=(row["sku"] if row is not None else "")).strip()
        name = st.text_input("Name", value=(row["name"] if row is not None else "")).strip()
        unit = st.text_input("Unit", value=(row["unit"] if row is not None else "pcs")).strip()
        category = st.text_input("Category", value=(row["category"] if row is not None else "")).strip()
        unit_cost = st.number_input("Unit cost", min_value=0.0, value=float(row["unit_cost"]) if row is not None else 0.0, step=0.01)
        price = st.number_input("Price", min_value=0.0, value=float(row["price"]) if row is not None else 0.0, step=0.01)
        min_stock = st.number_input("Min stock", min_value=0.0, value=float(row["min_stock"]) if row is not None else 0.0, step=1.0)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save product", type="primary", use_container_width=True, key="btn_save_prod"):
                if not sku or not name:
                    st.error("SKU and Name are required.")
                else:
                    pid = row["id"] if row is not None else None
                    upsert_product(org_id, pid, sku, name, category, unit, unit_cost, price, min_stock)
                    success_rerun("Saved.")
        with c2:
            if row is not None and st.button("Delete product", use_container_width=True, key="btn_del_prod"):
                delete_product(org_id, row["id"])
                success_rerun("Deleted.")
    st.divider()
    st.subheader("Products list")
    items = list_products(org_id)
    show = ["sku", "name", "unit", "unit_cost", "price", "min_stock", "category", "updated_at"]
    st.dataframe(items[show] if not items.empty else items, use_container_width=True)

def page_receive():
    st.markdown("# Receive Stock")
    org_id = st.session_state["org_id"]
    prods = list_products(org_id)
    if prods.empty:
        st.info("Add products first.")
        return
    prods["display"] = prods["sku"] + " — " + prods["name"]
    sel = st.selectbox("Product", prods["display"], index=None, key="recv_select")
    if not sel:
        return
    row = prods.loc[prods["display"] == sel].iloc[0]
    qty = st.number_input("Quantity received", min_value=0.0, step=1.0, key="recv_qty")
    unit_cost = st.number_input("Unit cost", min_value=0.0, step=0.01, value=float(row["unit_cost"] or 0), key="recv_cost")
    if st.button("Record receipt", type="primary", key="btn_recv"):
        if qty <= 0:
            st.error("Quantity must be > 0")
        else:
            receive_stock(org_id, row["id"], unit_cost=unit_cost, qty=qty)
            success_rerun("Receipt recorded.")

def page_sell():
    st.markdown("# Sell / Issue")
    org_id = st.session_state["org_id"]
    stock = get_stock_df(org_id)
    if stock.empty:
        st.info("Add products first.")
        return
    stock["display"] = stock["sku"] + " — " + stock["name"] + "  (on hand: " + stock["qty"].astype(str) + ")"
    sel = st.selectbox("Product", stock["display"], index=None, key="sell_select")
    if not sel:
        return
    row = stock.loc[stock["display"] == sel].iloc[0]
    st.info(f"On hand: {row['qty']} {row['unit']}")
    qty = st.number_input("Quantity to sell", min_value=0.0, step=1.0, key="sell_qty")
    unit_price = st.number_input("Unit price", min_value=0.0, step=0.01, value=float(row.get("price", 0) or 0), key="sell_price")
    ref = st.text_input("Reference / Order #", key="sell_ref")
    if st.button("Complete sale", type="primary", key="btn_sell"):
        if qty <= 0:
            st.error("Quantity must be > 0")
        else:
            sell_items(org_id, [{"product_id": row["id"], "qty": qty, "unit_price": unit_price}], ref)
            success_rerun("Sale recorded.")

def page_adjust():
    st.markdown("# Adjustments")
    org_id = st.session_state["org_id"]
    stock = get_stock_df(org_id)
    if stock.empty:
        st.info("Add products first.")
        return
    stock["display"] = stock["sku"] + " — " + stock["name"] + "  (current: " + stock["qty"].astype(str) + ")"
    sel = st.selectbox("Product", stock["display"], index=None, key="adj_select")
    if not sel:
        return
    row = stock.loc[stock["display"] == sel].iloc[0]
    st.info(f"Current on hand: {row['qty']} {row['unit']}")
    desired = st.number_input("New counted quantity", min_value=0.0, step=1.0, value=float(row["qty"]), key="adj_qty")
    if st.button("Record adjustment", type="primary", key="btn_adj"):
        adjust_stock(row["id"], desired)
        success_rerun("Adjustment recorded.")

def page_sales():
    st.markdown("# Sales")
    org_id = st.session_state["org_id"]
    df = list_sales(org_id)
    if df.empty:
        st.info("No sales yet.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Export CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"sales_{date.today().isoformat()}.csv",
            mime="text/csv",
            key="btn_export_sales"
        )

def page_settings():
    st.markdown("# Settings")
    st.caption("Supabase-backed, multi-tenant inventory.")
    st.write(f"**Org ID:** {st.session_state.get('org_id','—')}")
    st.write(f"**Role:** {st.session_state.get('role','')}")
    if st.button("Log out", key="btn_logout"):
        logout()

# -------------------------------
# Auth screen
# -------------------------------
def auth_screen():
    st.title("📦 Inventory (Supabase)")
    st.caption("Create a store or log in.")

    tab_login, tab_signup = st.tabs(["Log in", "Create store"])

    # --- SIGN UP ---
    with tab_signup:
        store = st.text_input("Store name", key="signup_store")
        raw_email = st.text_input("Owner email", key="signup_email")
        pw = st.text_input("Password", type="password", key="signup_pw")

        if st.button("Create my store", type="primary", use_container_width=True, key="btn_create_store"):
            email = clean_email(raw_email)

            if not (store and email and pw):
                st.error("All fields required."); st.stop()
            if not is_valid_email(email):
                st.error("Enter a valid email (e.g., name@example.com)."); st.stop()
            if len(pw) < MIN_PASSWORD_LENGTH:
                st.error(f"Password must be at least {MIN_PASSWORD_LENGTH} characters."); st.stop()

            # 1) sign up
            try:
                out = sb.auth.sign_up({"email": email, "password": pw})
            except AuthApiError as e:
                msg = getattr(e, "message", "") or getattr(e, "msg", "") or ""
                code = getattr(e, "code", "") or getattr(e, "error_code", "") or ""
                normalized = f"{msg} {code}".lower()
                if "already registered" in normalized or "already exists" in normalized or "user_already_exists" in normalized:
                    st.info("An account with this email already exists. Please log in instead."); st.stop()
                else:
                    show_supabase_error("Sign-up", e); st.stop()
            except Exception as e:
                show_supabase_error("Sign-up", e); st.stop()

            if not out or not out.user:
                st.error("Sign-up returned no user (email may exist or confirmation required)."); st.stop()

            # 2) sign in to get session/JWT (email confirmation may block this if enabled)
            try:
                sess = sb.auth.sign_in_with_password({"email": email, "password": pw})
            except Exception as e:
                show_supabase_error("Auto-login", e); st.stop()

            if not sess or not sess.user:
                st.error("Auto-login returned no user. If email confirmation is enabled, check your inbox."); st.stop()

            # 3) store tokens and attach (and reattach to be safe)
            st.session_state["user"] = {"id": sess.user.id, "email": email}
            st.session_state["jwt"] = sess.session.access_token
            st.session_state["rt"] = sess.session.refresh_token
            attach_tokens(st.session_state["jwt"], st.session_state["rt"])
            reattach_session()

            # (Optional) Show what DB sees
            check_db_identity()

            # 4) ensure you have an org + membership and jump into the app
            ensure_membership_and_bootstrap(default_store_name=store)

    # --- LOG IN ---
    with tab_login:
        raw_login_email = st.text_input("Email", key="login_email")
        pw_l = st.text_input("Password", type="password", key="login_pw")

        if st.button("Log in", type="primary", use_container_width=True, key="btn_login"):
            email_l = clean_email(raw_login_email)
            if not is_valid_email(email_l):
                st.error("Enter a valid email (e.g., name@example.com)."); st.stop()

            try:
                sess = sb.auth.sign_in_with_password({"email": email_l, "password": pw_l})
            except Exception as e:
                show_supabase_error("Login", e); st.stop()

            if not sess or not sess.user:
                st.error("Invalid email or password, or email not confirmed."); st.stop()

            # keep session + attach tokens (and reattach)
            st.session_state["user"] = {"id": sess.user.id, "email": email_l}
            st.session_state["jwt"] = sess.session.access_token
            st.session_state["rt"] = sess.session.refresh_token
            attach_tokens(st.session_state["jwt"], st.session_state["rt"])
            reattach_session()

            # (Optional) DB identity
            check_db_identity()

            # Guarantee membership and jump in (auto-creates a default store if needed)
            default_name = st.session_state.get("store_after_login") or "My Store"
            ensure_membership_and_bootstrap(default_store_name=default_name)

# -------------------------------
# Main
# -------------------------------
def main():
    # If not logged in or no org yet, show auth screen
    if "user" not in st.session_state or ("org_id" not in st.session_state):
        auth_screen()
        return

    st.sidebar.success(f"Signed in as {st.session_state['user']['email']}")
    tabs = st.tabs(["Dashboard", "Products", "Receive", "Sell", "Adjustments", "Sales", "Settings"])
    with tabs[0]:
        page_dashboard()
    with tabs[1]:
        page_products()
    with tabs[2]:
        page_receive()
    with tabs[3]:
        page_sell()
    with tabs[4]:
        page_adjust()
    with tabs[5]:
        page_sales()
    with tabs[6]:
        page_settings()

if __name__ == "__main__":
    main()
