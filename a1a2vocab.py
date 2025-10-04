# streamlit_app.py
import streamlit as st
from supabase import create_client, Client
import sqlite3
import pandas as pd
from datetime import datetime, date
from typing import Optional
import bcrypt


# Initialize Supabase client
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase: Client = create_client(url, key)


DB_PATH = "data.db"

# -------------------------------
# SQLite helpers & bootstrap
# -------------------------------

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def col_exists(cur, table: str, col: str) -> bool:
    cur.execute(f"PRAGMA table_info({table})")
    return any(r["name"] == col for r in cur.fetchall())

def init_db():
    """Create base tables and add multi-tenant/auth columns safely."""
    conn = get_conn()
    cur = conn.cursor()

    # --- Multi-tenant: stores & users
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('owner','manager','cashier')) DEFAULT 'owner',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(store_id, email),
            FOREIGN KEY(store_id) REFERENCES stores(id)
        )
        """
    )

    # --- Domain tables
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'pcs',
            cost REAL NOT NULL DEFAULT 0,
            price REAL NOT NULL DEFAULT 0,
            min_stock REAL NOT NULL DEFAULT 0,
            category TEXT,
            default_supplier_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            address TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('receive','issue','adjust','transfer')),
            qty REAL NOT NULL,
            unit_cost REAL,
            ref TEXT,
            note TEXT,
            from_location TEXT,
            to_location TEXT,
            moved_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
        """
    )

    # --- Add store_id columns if missing
    for tbl in ("items", "suppliers", "movements"):
        if not col_exists(cur, tbl, "store_id"):
            cur.execute(f"ALTER TABLE {tbl} ADD COLUMN store_id INTEGER")

    # Indexes for performance / uniqueness per store
    cur.execute("CREATE INDEX IF NOT EXISTS idx_items_store ON items(store_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_suppliers_store ON suppliers(store_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_movements_store ON movements(store_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_movements_item ON movements(item_id)")

    conn.commit()

# -------------------------------
# Auth helpers (very simple)
# -------------------------------

def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_pw(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception:
        return False

def create_store_and_owner(store_name: str, email: str, password: str) -> int:
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO stores(name) VALUES (?)", (store_name.strip(),))
    store_id = cur.lastrowid
    cur.execute(
        "INSERT INTO users(store_id,email,password_hash,role) VALUES (?,?,?,?)",
        (store_id, email.strip().lower(), hash_pw(password), "owner"),
    )
    conn.commit()
    return store_id

def login(email: str, password: str) -> Optional[dict]:
    cur = get_conn().cursor()
    cur.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),))
    u = cur.fetchone()
    if u and verify_pw(password, u["password_hash"]):
        return dict(u)
    return None

def current_store_id() -> int:
    return int(st.session_state["store_id"])

def require_auth():
    if "user" not in st.session_state:
        auth_screen()
        st.stop()

def logout():
    for k in ("user", "store_id"):
        st.session_state.pop(k, None)
    st.experimental_rerun()

# -------------------------------
# Data access (scoped by store)
# -------------------------------

def upsert_item(item_id: Optional[int], sku, name, unit, cost, price, min_stock, category, default_supplier_id):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    store_id = current_store_id()

    if item_id:
        cur.execute(
            """
            UPDATE items
            SET sku=?, name=?, unit=?, cost=?, price=?, min_stock=?, category=?, default_supplier_id=?, updated_at=?
            WHERE id=? AND store_id=?
            """,
            (sku, name, unit, cost, price, min_stock, category, default_supplier_id, now, item_id, store_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO items (sku, name, unit, cost, price, min_stock, category, default_supplier_id,
                               created_at, updated_at, store_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """,
            (sku, name, unit, cost, price, min_stock, category, default_supplier_id, now, now, store_id),
        )
    conn.commit()

def delete_item(item_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM items WHERE id=? AND store_id=?", (item_id, current_store_id()))
    conn.commit()

def upsert_supplier(supplier_id: Optional[int], name, email, phone, address):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    store_id = current_store_id()

    if supplier_id:
        cur.execute(
            """
            UPDATE suppliers
            SET name=?, email=?, phone=?, address=?, updated_at=?
            WHERE id=? AND store_id=?
            """,
            (name, email, phone, address, now, supplier_id, store_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO suppliers (name, email, phone, address, created_at, updated_at, store_id)
            VALUES (?,?,?,?,?,?,?)
            """,
            (name, email, phone, address, now, now, store_id),
        )
    conn.commit()

def delete_supplier(supplier_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM suppliers WHERE id=? AND store_id=?", (supplier_id, current_store_id()))
    conn.commit()

def record_movement(item_id: int, type_: str, qty: float, unit_cost: Optional[float],
                    ref: str, note: str, from_loc: Optional[str], to_loc: Optional[str], moved_at: str):
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO movements (item_id, type, qty, unit_cost, ref, note, from_location, to_location, moved_at, store_id)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,
        (item_id, type_, qty, unit_cost, ref, note, from_loc, to_loc, moved_at, current_store_id()),
    )
    conn.commit()

def df_items() -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT * FROM items WHERE store_id=? ORDER BY name",
        get_conn(), params=(current_store_id(),)
    )

def df_suppliers() -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT * FROM suppliers WHERE store_id=? ORDER BY name",
        get_conn(), params=(current_store_id(),)
    )

def df_movements() -> pd.DataFrame:
    return pd.read_sql_query(
        """
        SELECT m.id, m.moved_at, m.type,
               i.sku, i.name as item_name, m.qty, m.unit_cost, m.ref, m.note,
               m.from_location, m.to_location
        FROM movements m
        JOIN items i ON i.id = m.item_id
        WHERE m.store_id=? AND i.store_id=?
        ORDER BY m.moved_at DESC, m.id DESC
        """,
        get_conn(), params=(current_store_id(), current_store_id())
    )

def stock_on_hand(item_id: int) -> float:
    cur = get_conn().cursor()
    cur.execute(
        """
        SELECT COALESCE(SUM(CASE WHEN type IN ('receive','adjust') THEN qty ELSE -qty END), 0)
        FROM movements
        WHERE item_id=? AND store_id=?
        """,
        (item_id, current_store_id()),
    )
    (qty,) = cur.fetchone()
    return float(qty or 0)

def df_stock() -> pd.DataFrame:
    items = df_items()
    if items.empty:
        return pd.DataFrame(columns=["id", "sku", "name", "unit", "on_hand", "min_stock", "category", "supplier"])
    items = items.copy()
    items["on_hand"] = items["id"].apply(stock_on_hand)
    sup = df_suppliers().rename(columns={"id": "supplier_id"})[["supplier_id", "name"]]
    items = items.merge(sup, left_on="default_supplier_id", right_on="supplier_id", how="left")
    items.rename(columns={"name_y": "supplier", "name_x": "name"}, inplace=True)
    return items[["id", "sku", "name", "unit", "on_hand", "min_stock", "category", "supplier"]]

# -------------------------------
# UI helpers
# -------------------------------

def page_header(title: str, subtitle: Optional[str] = None):
    st.markdown(f"# {title}")
    if subtitle:
        st.caption(subtitle)

def success_rerun(msg: str):
    st.success(msg)
    st.experimental_rerun()

# -------------------------------
# Auth screen
# -------------------------------

def auth_screen():
    st.set_page_config(page_title="Inventory App", page_icon="📦", layout="wide")
    init_db()
    st.title("📦 Inventory — Sign in")
    st.caption("Create a store or log in to continue")

    tab_login, tab_signup = st.tabs(["Log in", "Create store"])

    with tab_signup:
        sname = st.text_input("Store name", key="signup_store")
        semail = st.text_input("Owner email", key="signup_email")
        spass = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Create my store", type="primary", use_container_width=True):
            if not (sname and semail and spass):
                st.error("All fields are required.")
            else:
                try:
                    _ = create_store_and_owner(sname, semail, spass)
                    st.success("Store created. Please log in on the next tab.")
                except sqlite3.IntegrityError as e:
                    st.error(f"Could not create store: {e}")

    with tab_login:
        email = st.text_input("Email", key="login_email")
        pwd = st.text_input("Password", type="password", key="login_pw")
        if st.button("Log in", type="primary", use_container_width=True):
            user = login(email, pwd)
            if user:
                st.session_state["user"] = user
                st.session_state["store_id"] = user["store_id"]
                st.experimental_rerun()
            else:
                st.error("Invalid email or password.")

# -------------------------------
# Pages
# -------------------------------

def page_dashboard():
    page_header("Dashboard", "Today at a glance")
    stock = df_stock()

    c1, c2, c3 = st.columns(3)
    total_items = len(stock)
    total_qty = float(stock["on_hand"].sum()) if not stock.empty else 0
    low_stock_df = stock[stock["on_hand"] < stock["min_stock"]] if not stock.empty else pd.DataFrame()

    with c1:
        st.metric("Item count", total_items)
    with c2:
        st.metric("Total stock on hand", f"{total_qty:.2f}")
    with c3:
        st.metric("Low-stock items", 0 if stock.empty else int((stock["on_hand"] < stock["min_stock"]).sum()))

    st.subheader("Low stock alerts")
    if low_stock_df is None or low_stock_df.empty:
        st.info("No low-stock items. 🎉")
    else:
        st.dataframe(low_stock_df[["sku", "name", "on_hand", "min_stock", "supplier"]], use_container_width=True)

    st.subheader("Recent movements")
    moves = df_movements().head(20)
    st.dataframe(moves, use_container_width=True)

def page_items():
    page_header("Items", "Manage your catalog")
    items = df_items()
    suppliers = df_suppliers()

    with st.expander("➕ Create / Edit item", expanded=True):
        edit_mode = st.checkbox("Edit existing item", key="items_edit")
        row = None
        if edit_mode and not items.empty:
            # show SKU + name for uniqueness
            items["display"] = items["sku"] + " — " + items["name"]
            choice = st.selectbox("Select item", items["display"], index=None, key="items_select")
            if choice:
                row = items.loc[items["display"] == choice].iloc[0]

        sku = st.text_input("SKU", value=(row["sku"] if row is not None else ""), key="items_sku").strip()
        name = st.text_input("Name", value=(row["name"] if row is not None else ""), key="items_name").strip()
        unit = st.text_input("Unit", value=(row["unit"] if row is not None else "pcs"), key="items_unit").strip()
        cost = st.number_input("Cost", min_value=0.0, value=float(row["cost"]) if row is not None else 0.0, step=0.01, key="items_cost")
        price = st.number_input("Price", min_value=0.0, value=float(row["price"]) if row is not None else 0.0, step=0.01, key="items_price")
        min_stock = st.number_input("Min stock", min_value=0.0, value=float(row["min_stock"]) if row is not None else 0.0, step=1.0, key="items_min_stock")
        category = st.text_input("Category", value=(row["category"] if row is not None else ""), key="items_category")

        supplier_display = ["—"] + (suppliers["name"].tolist() if not suppliers.empty else [])
        supplier_choice = st.selectbox("Default supplier", supplier_display, index=0, key="items_supplier")
        default_supplier_id = None
        if supplier_choice != "—" and not suppliers.empty:
            default_supplier_id = int(suppliers.loc[suppliers["name"] == supplier_choice, "id"].iloc[0])

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save item", use_container_width=True, type="primary", key="items_save"):
                if not sku or not name:
                    st.error("SKU and Name are required.")
                else:
                    item_id = int(row["id"]) if row is not None else None
                    try:
                        upsert_item(item_id, sku, name, unit, cost, price, min_stock, category, default_supplier_id)
                        success_rerun("Item saved")
                    except sqlite3.IntegrityError as e:
                        st.error(f"Error: {e}")
        with c2:
            if row is not None and st.button("Delete item", use_container_width=True, key="items_delete"):
                delete_item(int(row["id"]))
                success_rerun("Item deleted")

    st.divider()
    st.subheader("Items list")
    if items.empty:
        st.info("No items yet.")
    else:
        show_cols = ["sku", "name", "unit", "cost", "price", "min_stock", "category"]
        st.dataframe(items[show_cols], use_container_width=True)

def page_suppliers():
    page_header("Suppliers", "Who you buy from")
    suppliers = df_suppliers()

    with st.expander("➕ Create / Edit supplier", expanded=True):
        edit_mode = st.checkbox("Edit existing supplier", key="sup_edit")
        row = None
        if edit_mode and not suppliers.empty:
            choice = st.selectbox("Select supplier", suppliers["name"], index=None, key="sup_select")
            if choice:
                row = suppliers.loc[suppliers["name"] == choice].iloc[0]

        name = st.text_input("Name", value=(row["name"] if row is not None else ""), key="sup_name").strip()
        email = st.text_input("Email", value=(row["email"] if row is not None else ""), key="sup_email").strip()
        phone = st.text_input("Phone", value=(row["phone"] if row is not None else ""), key="sup_phone").strip()
        address = st.text_area("Address", value=(row["address"] if row is not None else "").strip(), key="sup_address")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Save supplier", type="primary", use_container_width=True, key="sup_save"):
                if not name:
                    st.error("Name is required.")
                else:
                    supplier_id = int(row["id"]) if row is not None else None
                    upsert_supplier(supplier_id, name, email, phone, address)
                    success_rerun("Supplier saved")
        with c2:
            if row is not None and st.button("Delete supplier", use_container_width=True, key="sup_delete"):
                delete_supplier(int(row["id"]))
                success_rerun("Supplier deleted")

    st.divider()
    st.subheader("Suppliers list")
    if suppliers.empty:
        st.info("No suppliers yet.")
    else:
        show_cols = ["name", "email", "phone", "address"]
        st.dataframe(suppliers[show_cols], use_container_width=True)

def movement_form(type_: str):
    pfx = f"{type_}_"
    items = df_items()
    if items.empty:
        st.warning("Create items first.")
        return

    items["display"] = items["sku"] + " — " + items["name"]
    item_display = st.selectbox("Item", items["display"], index=None, key=pfx + "item")
    if not item_display:
        return
    row = items.loc[items["display"] == item_display].iloc[0]
    item_id = int(row["id"])

    if type_ == "receive":
        qty = st.number_input("Quantity received", min_value=0.0, step=1.0, key=pfx + "qty")
        unit_cost = st.number_input("Unit cost", min_value=0.0, step=0.01, value=float(row["cost"]), key=pfx + "unit_cost")
        ref = st.text_input("Reference / Invoice #", key=pfx + "ref")
        note = st.text_area("Note", key=pfx + "note")
        moved_at = st.date_input("Date", value=date.today(), key=pfx + "date").isoformat()
        if st.button("Record receipt", type="primary", key=pfx + "btn"):
            if qty <= 0:
                st.error("Quantity must be greater than 0")
            else:
                record_movement(item_id, "receive", qty, unit_cost, ref, note, None, None, moved_at)
                success_rerun("Receipt recorded")

    elif type_ == "issue":
        on_hand = stock_on_hand(item_id)
        st.info(f"On hand: {on_hand} {row['unit']}")
        qty = st.number_input("Quantity issued", min_value=0.0, step=1.0, key=pfx + "qty")
        unit_cost = None
        ref = st.text_input("Reference / Order #", key=pfx + "ref")
        note = st.text_area("Note", key=pfx + "note")
        moved_at = st.date_input("Date", value=date.today(), key=pfx + "date").isoformat()
        if st.button("Record issue", type="primary", key=pfx + "btn"):
            if qty <= 0:
                st.error("Quantity must be greater than 0")
            elif qty > on_hand:
                st.warning("Issuing more than on-hand will drive stock negative.")
                record_movement(item_id, "issue", qty, unit_cost, ref, note, None, None, moved_at)
                success_rerun("Issue recorded (negative stock)")
            else:
                record_movement(item_id, "issue", qty, unit_cost, ref, note, None, None, moved_at)
                success_rerun("Issue recorded")

    elif type_ == "adjust":
        on_hand = stock_on_hand(item_id)
        st.info(f"Current on hand: {on_hand} {row['unit']}")
        desired = st.number_input("New counted quantity", min_value=0.0, step=1.0, value=on_hand, key=pfx + "desired")
        delta = desired - on_hand
        st.caption(f"Adjustment delta: {delta}")
        ref = st.text_input("Reference", key=pfx + "ref")
        note = st.text_area("Reason / Note", key=pfx + "note")
        moved_at = st.date_input("Date", value=date.today(), key=pfx + "date").isoformat()
        if st.button("Record adjustment", type="primary", key=pfx + "btn"):
            if delta == 0:
                st.info("No change needed.")
            else:
                record_movement(item_id, "adjust", delta, None, ref, note, None, None, moved_at)
                success_rerun("Adjustment recorded")

def page_receive():
    page_header("Receive Stock", "Add inventory coming in")
    movement_form("receive")

def page_issue():
    page_header("Issue Stock", "Record inventory going out")
    movement_form("issue")

def page_adjustments():
    page_header("Adjustments", "Correct counts after stocktake or damage")
    movement_form("adjust")

def page_movements():
    page_header("Stock Movements", "All receipts, issues and adjustments")
    df = df_movements()
    if df.empty:
        st.info("No movements yet.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Export CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"movements_{datetime.now().date()}.csv",
            mime="text/csv",
        )

def page_settings():
    page_header("Settings", "General configuration")
    st.write(
        "This MVP stores data in a local SQLite file (`data.db`). "
        "For multi-user cloud use, switch to a hosted DB like Supabase/Postgres and add real auth."
    )
    st.code(
        "# Example: connect to Postgres instead of SQLite\n"
        "import psycopg2\n"
        "conn = psycopg2.connect(dsn_from_streamlit_secrets)",
        language="python",
    )
    st.divider()
    if st.button("Log out", type="secondary"):
        logout()

# -------------------------------
# Main
# -------------------------------

def main():
    st.set_page_config(page_title="Inventory App", page_icon="📦", layout="wide")
    init_db()

    # Require login
    if "user" not in st.session_state:
        auth_screen()
        return

    st.title("📦 Inventory")
    st.caption("Multi-tenant (per-store) · Data stored in data.db · Use the tabs below")

    tabs = st.tabs([
        "Dashboard",
        "Items",
        "Suppliers",
        "Receive",
        "Issue",
        "Adjustments",
        "Movements",
        "Settings",
    ])

    with tabs[0]:
        page_dashboard()
    with tabs[1]:
        page_items()
    with tabs[2]:
        page_suppliers()
    with tabs[3]:
        page_receive()
    with tabs[4]:
        page_issue()
    with tabs[5]:
        page_adjustments()
    with tabs[6]:
        page_movements()
    with tabs[7]:
        page_settings()

if __name__ == "__main__":
    main()
