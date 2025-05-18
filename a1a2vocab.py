import os
import streamlit as st
import pandas as pd
import random
import re
import difflib

st.set_page_config(page_title="German Learning App", page_icon="🇩🇪", layout="centered")

# --- Helper to Rerun ---
def rerun():
    try:
        st.experimental_rerun()
    except Exception:
        pass

# --- Session Reset Helper ---
def clear_states(*keys):
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]

# --- Load Codes ---
st.title("🔐 German Learning App Login")
codes_file_csv = "student_codes.csv"
codes_file_xlsx = "student_codes.xlsx"
if os.path.exists(codes_file_csv):
    codes_df = pd.read_csv(codes_file_csv)
elif os.path.exists(codes_file_xlsx):
    codes_df = pd.read_excel(codes_file_xlsx)
else:
    st.error(f"❗ '{codes_file_csv}' or '{codes_file_xlsx}' file missing.")
    st.stop()

codes_df.columns = codes_df.columns.str.strip().str.lower()
if "code" not in codes_df.columns:
    st.error("❗ 'code' column missing in student codes file.")
    st.stop()

valid_codes = set(codes_df["code"].astype(str).str.strip().str.lower())
student_code = st.text_input(
    "Enter your student code (if you don't have one contact your tutor):"
).strip().lower()
if not student_code:
    st.stop()
if student_code not in valid_codes:
    st.warning("Access denied. Please enter a valid code.")
    st.stop()

st.success(f"✅ Welcome, {student_code}!")

# --- Level Selection: Main Page & Mobile-Friendly ---
if "level" not in st.session_state:
    st.session_state["level"] = "A1"
st.markdown("### Please select your level:")
level = st.radio(
    "Level:", 
    ["A1", "A2"], 
    index=0 if st.session_state["level"] == "A1" else 1, 
    key="level", 
    horizontal=True
)
# No manual session_state assignment needed! The widget key does it.

# --- Dashboard Buttons ---
SCHOOL_NAME = "Learn Language Education Academy"
st.markdown(f"## 🏫 {SCHOOL_NAME}")
st.markdown(f"Welcome **{student_code}**! 👋")
st.markdown("---")
st.subheader("📌 Available Modules")
cols = st.columns(2)
with cols[0]:
    if st.button("📚 Start Vocabulary Quiz"):
        clear_states('vocab_index','vocab_score','vocab_quiz','vocab_feedback')
        st.session_state["section_override"] = "📚 Vocabulary Quiz"
        rerun()
    if st.button("🧪 Start Grammar Quiz"):
        clear_states('gq')
        st.session_state["section_override"] = "🧪 Grammar Quiz"
        rerun()
with cols[1]:
    if st.button("✍️ Start Sentence Trainer"):
        clear_states('sent_index','sent_feedback','sent_correct')
        st.session_state["section_override"] = "✍️ Sentence Trainer"
        rerun()
    if st.button("🔢 Start Grammar Practice"):
        st.session_state["section_override"] = "🔢 Grammar Practice"
        rerun()

# --- Sidebar Info ---
st.sidebar.title("🇩🇪 German Training Center")
st.sidebar.info("Tip: You can change your level at the top of the main page. If you don't see your modules, scroll up!")

# --- Section Selection ---
if "section_override" in st.session_state:
    section = st.session_state["section_override"]
else:
    if st.session_state["level"] == "A1":
        section = st.radio(
            "Choose a topic:",
            ["📚 Vocabulary Quiz", "✍️ Sentence Trainer", "🔢 Grammar Practice"],
            key="topic_a1"
        )
    else:
        section = st.radio(
            "Choose a topic:",
            ["📚 Vocabulary Quiz", "✍️ Sentence Trainer", "🧪 Grammar Quiz", "🔢 Grammar Practice"],
            key="topic_a2"
        )

# --- Add Back Button in Each Module ---
def back_button():
    if st.button("⬅️ Back to Dashboard"):
        if "section_override" in st.session_state:
            del st.session_state["section_override"]
        rerun()

# --- Vocabulary Lists ---
a1_vocab = [
    ("Südseite","south side"), ("3. Stock","third floor"), ("Geschenk","present/gift"),
    ("Buslinie","bus line"), ("Ruhetag","rest day (closed)"), ("Heizung","heating"),
    ("Hälfte","half"), ("die Wohnung","apartment"), ("das Zimmer","room"), ("die Miete","rent"),
    ("der Balkon","balcony"), ("der Garten","garden"), ("das Schlafzimmer","bedroom"),
    ("das Wohnzimmer","living room"), ("das Badezimmer","bathroom"), ("die Garage","garage"),
    ("der Tisch","table"), ("der Stuhl","chair"), ("der Schrank","cupboard"), ("die Tür","door"),
    ("das Fenster","window"), ("der Boden","floor"), ("die Wand","wall"), ("die Lampe","lamp"),
    ("der Fernseher","television"), ("das Bett","bed"), ("die Küche","kitchen"), ("die Toilette","toilet"),
    ("die Dusche","shower"), ("das Waschbecken","sink"), ("der Ofen","oven"),
    ("der Kühlschrank","refrigerator"), ("die Mikrowelle","microwave"), ("die Waschmaschine","washing machine"),
    ("die Spülmaschine","dishwasher"), ("das Haus","house"), ("die Stadt","city"), ("das Land","country"),
    ("die Straße","street"), ("der Weg","way"), ("der Park","park"), ("die Ecke","corner"),
    ("die Bank","bank"), ("der Supermarkt","supermarket"), ("die Apotheke","pharmacy"),
    ("die Schule","school"), ("die Universität","university"), ("das Geschäft","store"),
    ("der Markt","market"), ("der Flughafen","airport"), ("der Bahnhof","train station"),
    ("die Haltestelle","bus stop"), ("die Fahrt","ride"), ("das Ticket","ticket"), ("der Zug","train"),
    ("der Bus","bus"), ("das Taxi","taxi"), ("das Auto","car"), ("die Ampel","traffic light"),
    ("die Kreuzung","intersection"), ("der Parkplatz","parking lot"), ("der Fahrplan","schedule"),
    ("zumachen","to close"), ("aufmachen","to open"), ("ausmachen","to turn off"),
    ("übernachten","to stay overnight"), ("anfangen","to begin"), ("vereinbaren","to arrange"),
    ("einsteigen","to get in / board"), ("umsteigen","to change (trains)"), ("aussteigen","to get out / exit"),
    ("anschalten","to switch on"), ("ausschalten","to switch off"), ("Anreisen","to arrive"), ("Ankommen","to arrive"),
    ("Abreisen","to depart"), ("Absagen","to cancel"), ("Zusagen","to agree"), ("günstig","cheap"),
    ("billig","inexpensive")
]

a2_vocab = [
    ("die Verantwortung", "responsibility"), ("die Besprechung", "meeting"), ("die Überstunden", "overtime"),
    ("laufen", "to run"), ("das Fitnessstudio", "gym"), ("die Entspannung", "relaxation"),
    ("der Müll", "waste, garbage"), ("trennen", "to separate"), ("der Umweltschutz", "environmental protection"),
    ("der Abfall", "waste, rubbish"), ("der Restmüll", "residual waste"), ("die Anweisung", "instruction"),
    ("die Gemeinschaft", "community"), ("der Anzug", "suit"), ("die Beförderung", "promotion"),
    ("die Abteilung", "department"), ("drinnen", "indoors"), ("die Vorsorgeuntersuchung", "preventive examination"),
    ("die Mahlzeit", "meal"), ("behandeln", "to treat"), ("Hausmittel", "home remedies"),
    ("Salbe", "ointment"), ("Tropfen", "drops"), ("nachhaltig", "sustainable"),
    ("berühmt / bekannt", "famous / well-known"), ("einleben", "to settle in"), ("sich stören", "to be bothered"),
    ("liefern", "to deliver"), ("zum Mitnehmen", "to take away"), ("erreichbar", "reachable"),
    ("bedecken", "to cover"), ("schwanger", "pregnant"), ("die Impfung", "vaccination"),
    ("am Fluss", "by the river"), ("das Guthaben", "balance / credit"), ("kostenlos", "free of charge"),
    ("kündigen", "to cancel / to terminate"), ("der Anbieter", "provider"), ("die Bescheinigung", "certificate / confirmation"),
    ("retten", "rescue"), ("die Falle", "trap"), ("die Feuerwehr", "fire department"),
    ("der Schreck", "shock, fright"), ("schwach", "weak"), ("verletzt", "injured"),
    ("der Wildpark", "wildlife park"), ("die Akrobatik", "acrobatics"), ("bauen", "to build"),
    ("extra", "especially"), ("der Feriengruß", "holiday greeting"), ("die Pyramide", "pyramid"),
    ("regnen", "to rain"), ("schicken", "to send"), ("das Souvenir", "souvenir"),
    ("wahrscheinlich", "probably"), ("das Chaos", "chaos"), ("deutlich", "clearly"),
    ("der Ohrring", "earring"), ("verlieren", "to lose"), ("der Ärger", "trouble"),
    ("besorgt", "worried"), ("deprimiert", "depressed"), ("der Streit", "argument"),
    ("sich streiten", "to argue"), ("dagegen sein", "to be against"), ("egal", "doesn't matter"),
    ("egoistisch", "selfish"), ("kennenlernen", "to get to know"), ("nicht leiden können", "to dislike"),
    ("der Mädchentag", "girls' day"), ("der Ratschlag", "advice"), ("tun", "to do"),
    ("zufällig", "by chance"), ("ansprechen", "to approach"), ("plötzlich", "suddenly"),
    ("untrennbar", "inseparable"), ("sich verabreden", "to make an appointment"),
    ("versprechen", "to promise"), ("weglaufen", "to run away"), ("ab (+ Dativ)", "from, starting from"),
    ("das Aquarium", "aquarium"), ("der Flohmarkt", "flea market"), ("der Jungentag", "boys' day"),
    ("kaputt", "broken"), ("kostenlos", "free"), ("präsentieren", "to present"),
    ("das Quiz", "quiz"), ("schwitzen", "to sweat"), ("das Straßenfest", "street festival"),
    ("täglich", "daily"), ("vorschlagen", "to suggest"), ("wenn", "if, when"),
    ("die Bühne", "stage"), ("dringend", "urgently"), ("die Reaktion", "reaction"),
    ("unterwegs", "on the way"), ("vorbei", "over, past"), ("die Bauchschmerzen", "stomach ache"),
    ("der Busfahrer", "bus driver"), ("die Busfahrerin", "female bus driver"),
    ("der Fahrplan", "schedule"), ("der Platten", "flat tire"), ("die Straßenbahn", "tram"),
    ("streiken", "to strike"), ("der Unfall", "accident"), ("die Ausrede", "excuse"),
    ("baden", "to bathe"), ("die Grillwurst", "grilled sausage"), ("klingeln", "to ring"),
    ("die Mitternacht", "midnight"), ("der Nachbarhund", "neighbor's dog"),
    ("verbieten", "to forbid"), ("wach", "awake"), ("der Wecker", "alarm clock"),
    ("die Wirklichkeit", "reality"), ("zuletzt", "lastly, finally"), ("das Bandmitglied", "band member"),
    ("loslassen", "to let go"), ("der Strumpf", "stocking"), ("anprobieren", "to try on"),
    ("aufdecken", "to uncover / flip over"), ("behalten", "to keep"), ("der Wettbewerb", "competition"),
    ("schmutzig", "dirty"), ("die Absperrung", "barricade"), ("böse", "angry, evil"),
    ("trocken", "dry"), ("aufbleiben", "to stay up"), ("hässlich", "ugly"),
    ("ausweisen", "to identify"), ("erfahren", "to learn, find out"), ("entdecken", "to discover"),
    ("verbessern", "to improve"), ("aufstellen", "to set up"), ("die Notaufnahme", "emergency department"),
    ("das Arzneimittel", "medication"), ("die Diagnose", "diagnosis"), ("die Therapie", "therapy"),
    ("die Rehabilitation", "rehabilitation"), ("der Chirurg", "surgeon"), ("die Anästhesie", "anesthesia"),
    ("die Infektion", "infection"), ("die Entzündung", "inflammation"), ("die Unterkunft", "accommodation"),
    ("die Sehenswürdigkeit", "tourist attraction"), ("die Ermäßigung", "discount"), ("die Verspätung", "delay"),
    ("die Quittung", "receipt"), ("die Veranstaltung", "event"), ("die Bewerbung", "application")
]

# --- Vocabulary Quiz ---
if section == "📚 Vocabulary Quiz":
    back_button()
    st.title("📚 Vocabulary Quiz")
    vocab_list = a1_vocab if st.session_state["level"] == "A1" else a2_vocab
    total = len(vocab_list)

    if "vocab_length" not in st.session_state:
        st.session_state.vocab_length = min(5, total)
    if "vocab_index" not in st.session_state:
        st.markdown(f"Total available words: **{total}**")
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            if st.button("➖"): st.session_state.vocab_length = max(3, st.session_state.vocab_length-1)
        with col3:
            if st.button("➕"): st.session_state.vocab_length = min(total, st.session_state.vocab_length+1)
        with col2:
            st.write(f"**Questions:** {st.session_state.vocab_length}")

        if st.checkbox("🔍 Preview all vocabulary words"):
            for w,m in vocab_list: st.write(f"- **{w}** → {m}")

        if st.button("🚀 Start Quiz"):
            st.session_state.vocab_index = 0
            st.session_state.vocab_score = 0
            st.session_state.vocab_quiz = random.sample(vocab_list, st.session_state.vocab_length)
            st.session_state.vocab_feedback = False
            rerun()
    else:
        idx = st.session_state.vocab_index
        quiz = st.session_state.vocab_quiz
        if idx < len(quiz):
            word, answer = quiz[idx]
            st.markdown(f"### {idx+1}. Meaning of **{word}**?")
            inp = st.text_input("Your answer:", key=f"vocab_{idx}")
            if not st.session_state.vocab_feedback and st.button("✅ Submit"):
                clean = lambda s: re.sub(r"[^a-zA-Z]","",s.lower())
                if clean(inp)==clean(answer):
                    st.success("✅ Correct!")
                    st.session_state.vocab_score += 1
                else:
                    st.error(f"❌ Incorrect. Correct: {answer}")
                st.session_state.vocab_feedback = True
            elif st.session_state.vocab_feedback and st.button("➡ Next"):
                st.session_state.vocab_index += 1
                st.session_state.vocab_feedback = False
                rerun()
        else:
            score = st.session_state.vocab_score
            total_q = len(st.session_state.vocab_quiz)
            st.success(f"🎉 Quiz Complete! {score}/{total_q} ({score/total_q*100:.0f}%)")
            if st.button("⬅️ Back to Dashboard"):
                del st.session_state["section_override"]
                rerun()

# --- Sentence Trainer ---
elif section == "✍️ Sentence Trainer":
    back_button()
    st.title("✍️ Sentence Trainer")
    phrases = [
        "Translate: I am learning German.",
        "Translate: She works in an office.",
        "Translate: We are going to the cinema today.",
        "Translate: I cannot come because I have to work.",
        "Translate: Would you like tea or coffee?"
    ]
    answers = [
        ["Ich lerne Deutsch."],
        ["Sie arbeitet in einem Büro."],
        ["Wir gehen heute ins Kino."],
        ["Ich kann nicht kommen, weil ich arbeiten muss."],
        ["Möchtest du Tee oder Kaffee?", "Möchten Sie Tee oder Kaffee?"]
    ]

    if "sent_index" not in st.session_state:
        st.session_state.sent_index = 0
        st.session_state.sent_feedback = False
        st.session_state.sent_correct = 0

    i = st.session_state.sent_index
    if i < len(phrases):
        st.markdown(f"**{phrases[i]}**")
        inp = st.text_input("Your German:", key=f"sent_{i}")
        if not st.session_state.sent_feedback and st.button("✅ Submit"):
            if inp.strip().lower() in [a.lower() for a in answers[i]]:
                st.success("✅ Correct!")
                st.session_state.sent_correct += 1
            else:
                close = difflib.get_close_matches(inp, answers[i], n=1)
                st.error(f"❌ Incorrect. Closest: {close[0] if close else '–'}")
            st.session_state.sent_feedback = True
        elif st.session_state.sent_feedback and st.button("➡ Next"):
            st.session_state.sent_index += 1
            st.session_state.sent_feedback = False
            rerun()
    else:
        c = st.session_state.sent_correct
        st.success(f"🎉 Done! {c}/{len(phrases)} correct.")
        if st.button("⬅️ Back to Dashboard"):
            del st.session_state["section_override"]
            rerun()

# --- Grammar Practice ---
elif section == "🔢 Grammar Practice":
    back_button()
    st.title("🔢 Grammar Practice")
    topic = st.selectbox("Choose a topic:", ["Verb Conjugation","Perfekt Builder","Number Spelling"])
    items = []
    if topic=="Verb Conjugation":
        items = [
            {"q":"Conjugate 'gehen' for ich","a":"ich gehe"},
            {"q":"Conjugate 'sein' for du","a":"du bist"},
            {"q":"Conjugate 'lernen' for er","a":"er lernt"}
        ]
    elif topic=="Perfekt Builder":
        items = [
            {"q":"Build Perfekt: ich + essen","a":"habe gegessen"},
            {"q":"Build Perfekt: wir + gehen","a":"sind gegangen"}
        ]
    else:
        items = [
            {"q":"Spell 25 in German","a":"fünfundzwanzig"},
            {"q":"Spell 456 in German","a":"vierhundertsechsundfünfzig"}
        ]
    for j, itm in enumerate(items):
        st.markdown(f"{j+1}. {itm['q']}")
        ans = st.text_input("Your answer:", key=f"gp_{j}")
        if st.button("✅ Submit", key=f"gpsb_{j}"):
            if ans.strip().lower()==itm["a"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Wrong—correct is {itm['a']}")

# --- A2 Grammar Quiz ---
elif section == "🧪 Grammar Quiz":
    back_button()
    st.title("🧪 A2 Grammar Quiz")
    quiz = {
        "Konjunktionen":[
            {"q":"Ich bleibe..., ___ ich krank bin.","opts":["weil","ob","dass"],"a":"weil"}
        ],
        "Perfekt":[
            {"q":"Ich habe einen Apfel ___","opts":["gegessen","essen"],"a":"gegessen"}
        ]
    }
    t = st.selectbox("Topic:", list(quiz))
    q0 = quiz[t][0]
    st.markdown(q0["q"])
    choice = st.radio("Options:", q0["opts"], key="gq")
    if st.button("✅ Check"):
        if choice==q0["a"]:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect—should be {q0['a']}")
