import streamlit as st
import pandas as pd
import random
import re
import difflib

# ----------------- APP SETUP -----------------
st.set_page_config(page_title="German Learning App", page_icon="🇩🇪", layout="centered")
st.title("🔐 German Learning App Login")

# ----------------- LOGIN -----------------
try:
    codes_df = pd.read_csv("student_codes.csv")
    codes_df.columns = codes_df.columns.str.strip().str.lower()
    valid_codes = set(codes_df["code"].astype(str).str.strip().str.lower())
except Exception:
    st.error("❗ 'student_codes.xlsx' file missing or incorrectly formatted.")
    st.stop()

student_code = st.text_input("Enter your student code (if you dont have contact your tutor):").strip().lower()

if student_code == "":
    st.stop()

if student_code not in valid_codes:
    st.warning("Access denied. Please enter a valid code.")
    st.stop()

st.success(f"✅ Welcome, {student_code}!")

# ----------------- SCHOOL CONFIG -----------------
SCHOOL_NAME = "Learn Language Education Academy"

# ----------------- DASHBOARD -----------------
st.markdown(f"## 🏫 {SCHOOL_NAME}")
st.markdown(f"Welcome **{student_code}**! 👋")

st.markdown("---")
st.subheader("📌 Available Modules")

cols = st.columns(2)
with cols[0]:
    if st.button("📚 Start Vocabulary Quiz"):
        st.session_state["section_override"] = "📚 Vocabulary Quiz"
    if st.button("🧪 Start Grammar Quiz"):
        st.session_state["section_override"] = "🧪 Grammar Quiz"
with cols[1]:
    if st.button("✍️ Start Sentence Trainer"):
        st.session_state["section_override"] = "✍️ Sentence Trainer"
    if st.button("🔢 Start Grammar Practice"):
        st.session_state["section_override"] = "🔢 Grammar Practice"

# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.title("🇩🇪 German Training Center")
level = st.sidebar.selectbox("Select your level:", ["A1", "A2"])

# Smart section selection (override buttons take priority)
if "section_override" not in st.session_state:
    if level == "A1":
        section = st.sidebar.radio("Choose a topic:", [
            "📚 Vocabulary Quiz",
            "✍️ Sentence Trainer",
            "🔢 Grammar Practice"
        ])
    else:
        section = st.sidebar.radio("Choose a topic:", [
            "📚 Vocabulary Quiz",
            "✍️ Sentence Trainer",
            "🧪 Grammar Quiz",
            "🔢 Grammar Practice"
        ])
else:
    section = st.session_state["section_override"]
    del st.session_state["section_override"]

# --- A1 VOCABULARY ---
a1_vocab = [
    ("Südseite", "south side"), ("3. Stock", "third floor"), ("Geschenk", "present/gift"),
    ("Buslinie", "bus line"), ("Ruhetag", "rest day (closed)"), ("Heizung", "heating"),
    ("Hälfte", "half"), ("die Wohnung", "apartment"), ("das Zimmer", "room"), ("die Miete", "rent"),
    ("der Balkon", "balcony"), ("der Garten", "garden"), ("das Schlafzimmer", "bedroom"),
    ("das Wohnzimmer", "living room"), ("das Badezimmer", "bathroom"), ("die Garage", "garage"),
    ("der Tisch", "table"), ("der Stuhl", "chair"), ("der Schrank", "cupboard"), ("die Tür", "door"),
    ("das Fenster", "window"), ("der Boden", "floor"), ("die Wand", "wall"), ("die Lampe", "lamp"),
    ("der Fernseher", "television"), ("das Bett", "bed"), ("die Küche", "kitchen"), ("die Toilette", "toilet"),
    ("die Dusche", "shower"), ("das Waschbecken", "sink"), ("der Ofen", "oven"),
    ("der Kühlschrank", "refrigerator"), ("die Mikrowelle", "microwave"), ("die Waschmaschine", "washing machine"),
    ("die Spülmaschine", "dishwasher"), ("das Haus", "house"), ("die Stadt", "city"), ("das Land", "country"),
    ("die Straße", "street"), ("der Weg", "way"), ("der Park", "park"), ("die Ecke", "corner"),
    ("die Bank", "bank"), ("der Supermarkt", "supermarket"), ("die Apotheke", "pharmacy"),
    ("die Schule", "school"), ("die Universität", "university"), ("das Geschäft", "store"),
    ("der Markt", "market"), ("der Flughafen", "airport"), ("der Bahnhof", "train station"),
    ("die Haltestelle", "bus stop"), ("die Fahrt", "ride"), ("das Ticket", "ticket"), ("der Zug", "train"),
    ("der Bus", "bus"), ("das Taxi", "taxi"), ("das Auto", "car"), ("die Ampel", "traffic light"),
    ("die Kreuzung", "intersection"), ("der Parkplatz", "parking lot"), ("der Fahrplan", "schedule"),
    ("zumachen", "to close"), ("aufmachen", "to open"), ("ausmachen", "to turn off"),
    ("übernachten", "to stay overnight"), ("anfangen", "to begin"), ("vereinbaren", "to arrange"),
    ("einsteigen", "to get in / board"), ("umsteigen", "to change (trains)"), ("aussteigen", "to get out / exit"),
    ("anschalten", "to switch on"), ("ausschalten", "to switch off"),
    ("Anreisen", "to arrive"), ("Ankommen", "to arrive"), 
    ("Abreisen", "to depart"), ("Absagen", "to cancel"),
    ("Zusagen", "to agree"), ("günstig", "cheap"), ("billig", "inexpensive")
]

# --- A2 VOCABULARY ---
a2_vocab = [
    ("die Verantwortung", "responsibility"), ("die Besprechung", "meeting"), ("die Überstunden", "overtime"),
    ("laufen", "to run"), ("das Fitnessstudio", "gym"), ("die Entspannung", "relaxation"), ("der Müll", "waste, garbage"),
    ("trennen", "to separate"), ("der Umweltschutz", "environmental protection"), ("der Abfall", "waste, rubbish"),
    ("der Restmüll", "residual waste"), ("die Anweisung", "instruction"), ("die Gemeinschaft", "community"),
    ("der Anzug", "suit"), ("die Beförderung", "promotion"), ("die Abteilung", "department"), ("drinnen", "indoors"),
    ("die Vorsorgeuntersuchung", "preventive examination"), ("die Mahlzeit", "meal"), ("behandeln", "to treat"),
    ("Hausmittel", "home remedies"), ("Salbe", "ointment"), ("Tropfen", "drops"), ("nachhaltig", "sustainable"),
    ("berühmt / bekannt", "famous / well-known"), ("einleben", "to settle in"), ("sich stören", "to be bothered"),
    ("liefern", "to deliver"), ("zum Mitnehmen", "to take away"), ("erreichbar", "reachable"), ("bedecken", "to cover"),
    ("schwanger", "pregnant"), ("die Impfung", "vaccination"), ("am Fluss", "by the river"), ("das Guthaben", "balance / credit"),
    ("kostenlos", "free of charge"), ("kündigen", "to cancel / to terminate"), ("der Anbieter", "provider"),
    ("die Bescheinigung", "certificate / confirmation"), ("retten", "rescue"), ("die Falle", "trap"),
    ("die Feuerwehr", "fire department"), ("der Schreck", "shock, fright"), ("schwach", "weak"), ("verletzt", "injured"),
    ("der Wildpark", "wildlife park"), ("die Akrobatik", "acrobatics"), ("bauen", "to build"), ("extra", "especially"),
    ("der Feriengruß", "holiday greeting"), ("die Pyramide", "pyramid"), ("regnen", "to rain"), ("schicken", "to send"),
    ("das Souvenir", "souvenir"), ("wahrscheinlich", "probably"), ("das Chaos", "chaos"), ("deutlich", "clearly"),
    ("der Ohrring", "earring"), ("verlieren", "to lose"), ("der Ärger", "trouble"), ("besorgt", "worried"),
    ("deprimiert", "depressed"), ("der Streit", "argument"), ("sich streiten", "to argue"), ("dagegen sein", "to be against"),
    ("egal", "doesn't matter"), ("egoistisch", "selfish"), ("kennenlernen", "to get to know"), ("nicht leiden können", "to dislike"),
    ("der Mädchentag", "girls' day"), ("der Ratschlag", "advice"), ("tun", "to do"), ("zufällig", "by chance"),
    ("ansprechen", "to approach"), ("plötzlich", "suddenly"), ("untrennbar", "inseparable"), ("sich verabreden", "to make an appointment"),
    ("versprechen", "to promise"), ("weglaufen", "to run away"), ("ab (+ Dativ)", "from, starting from"), ("das Aquarium", "aquarium"),
    ("der Flohmarkt", "flea market"), ("der Jungentag", "boys' day"), ("kaputt", "broken"), ("kostenlos", "free"),
    ("präsentieren", "to present"), ("das Quiz", "quiz"), ("schwitzen", "to sweat"), ("das Straßenfest", "street festival"),
    ("täglich", "daily"), ("vorschlagen", "to suggest"), ("wenn", "if, when"), ("die Bühne", "stage"), ("dringend", "urgently"),
    ("die Reaktion", "reaction"), ("unterwegs", "on the way"), ("vorbei", "over, past"), ("die Bauchschmerzen", "stomach ache"),
    ("der Busfahrer", "bus driver"), ("die Busfahrerin", "female bus driver"), ("der Fahrplan", "schedule"),
    ("der Platten", "flat tire"), ("die Straßenbahn", "tram"), ("streiken", "to strike"), ("der Unfall", "accident"),
    ("die Ausrede", "excuse"), ("baden", "to bathe"), ("die Grillwurst", "grilled sausage"), ("klingeln", "to ring"),
    ("die Mitternacht", "midnight"), ("der Nachbarhund", "neighbor's dog"), ("verbieten", "to forbid"), ("wach", "awake"),
    ("der Wecker", "alarm clock"), ("die Wirklichkeit", "reality"), ("zuletzt", "lastly, finally"), ("das Bandmitglied", "band member"),
    ("loslassen", "to let go"), ("der Strumpf", "stocking"), ("anprobieren", "to try on"), ("aufdecken", "to uncover / flip over"),
    ("behalten", "to keep"), ("der Wettbewerb", "competition"), ("schmutzig", "dirty"), ("die Absperrung", "barricade"),
    ("böse", "angry, evil"), ("trocken", "dry"), ("aufbleiben", "to stay up"), ("hässlich", "ugly"), ("ausweisen", "to identify"),
    ("erfahren", "to learn, find out"), ("entdecken", "to discover"), ("verbessern", "to improve"), ("aufstellen", "to set up"),
    ("das Geländer", "railing"), ("die Leidenschaft", "passion"), ("schnuppern", "to try out"), ("zeichnen", "to draw"),
    ("röntgen", "to x-ray"), ("das Pech", "bad luck"), ("abmelden", "to log off / unregister"), ("fegen", "to sweep"),
    ("tragen", "to carry"), ("aufschreiben", "to write down"), ("abwechselnd", "alternately"), ("aufsagen", "to recite"),
    ("aussetzen", "to skip"), ("beenden", "to finish"), ("die Steckdose", "socket"), ("die Salbe", "ointment")
]

# existing content above

# ----------------- VOCABULARY QUIZ -----------------
if section == "📚 Vocabulary Quiz":
    st.title("📚 Vocabulary Quiz")

    vocab_list = a1_vocab if level == "A1" else a2_vocab
    total_vocab = len(vocab_list)

    if "vocab_length" not in st.session_state:
        st.session_state.vocab_length = min(5, total_vocab)

    if "vocab_index" not in st.session_state:
        st.markdown(f"Total available words: **{total_vocab}**")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("➖"):
                st.session_state.vocab_length = max(3, st.session_state.vocab_length - 1)
        with col3:
            if st.button("➕"):
                st.session_state.vocab_length = min(total_vocab, st.session_state.vocab_length + 1)
        with col2:
            st.write(f"**Questions:** {st.session_state.vocab_length}")

        if st.checkbox("🔍 Preview all vocabulary words"):
            for word, meaning in vocab_list:
                st.write(f"- **{word}** → {meaning}")

        if st.button("🚀 Start Quiz"):
            st.session_state.vocab_index = 0
            st.session_state.vocab_score = 0
            st.session_state.vocab_quiz = random.sample(vocab_list, st.session_state.vocab_length)
            st.session_state.vocab_feedback = False
            st.rerun()
    else:
        current = st.session_state.vocab_index
        if current < len(st.session_state.vocab_quiz):
            word, correct = st.session_state.vocab_quiz[current]
            st.markdown(f"### {current + 1}. What is the English meaning of: **{word}**")
            user_input = st.text_input("Your answer:", key=f"vocab_input_{current}")

            if not st.session_state.vocab_feedback:
                if st.button("✅ Submit"):
                    user_clean = re.sub(r"[^a-zA-Z]", "", user_input.lower().strip())
                    correct_clean = re.sub(r"[^a-zA-Z]", "", correct.lower().strip())
                    if user_clean == correct_clean:
                        st.success("✅ Correct!")
                        st.session_state.vocab_score += 1
                    else:
                        st.error(f"❌ Incorrect. Correct answer: {correct}")
                    st.session_state.vocab_feedback = True
            elif st.button("➡ Next"):
                st.session_state.vocab_index += 1
                st.session_state.vocab_feedback = False
                st.rerun()
        else:
            score = st.session_state.vocab_score
            total = len(st.session_state.vocab_quiz)
            st.success(f"🎉 Quiz Complete! Score: {score} / {total} ({(score / total) * 100:.0f}%)")
            if st.button("🔁 Restart Quiz"):
                for key in ["vocab_index", "vocab_score", "vocab_quiz", "vocab_feedback"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()


# ----------------- SENTENCE TRAINER -----------------
if section == "✍️ Sentence Trainer":
    st.title("✍️ Sentence Trainer")
    st.markdown("Translate each sentence into German. Submit → Feedback → Next.")

    sentence_data = {
        "Translate: I am learning German.": ["Ich lerne Deutsch."],
        "Translate: She works in an office.": ["Sie arbeitet in einem Büro."],
        "Translate: We are going to the cinema today.": ["Wir gehen heute ins Kino."],
        "Translate: I cannot come because I have to work.": ["Ich kann nicht kommen, weil ich arbeiten muss."],
        "Translate: Would you like tea or coffee?": ["Möchtest du Tee oder Kaffee?", "Möchten Sie Tee oder Kaffee?"]
    }

    questions = list(sentence_data.keys())

    if "sent_index" not in st.session_state:
        st.session_state.sent_index = 0
        st.session_state.sent_correct = []
        st.session_state.sent_wrong = []
        st.session_state.sent_feedback = False

        # Preview before starting
        if st.checkbox("🔍 Preview all translation tasks"):
            for i, q in enumerate(questions, 1):
                st.write(f"{i}. {q} → {', '.join(sentence_data[q])}")
        if st.button("🚀 Start Trainer"):
            st.rerun()

    else:
        current = st.session_state.sent_index
        total_questions = len(questions)

        if current < total_questions:
            q = questions[current]
            correct_answers = sentence_data[q]
            st.markdown(f"### {current + 1} of {total_questions}. {q}")
            user_input = st.text_input("✍ Your German sentence:", key=f"sent_input_{current}")

            if not st.session_state.sent_feedback:
                if st.button("✅ Submit", key=f"submit_{current}"):
                    user_clean = user_input.lower().strip()
                    if user_clean in [ans.lower() for ans in correct_answers]:
                        st.success("✅ Correct!")
                        st.session_state.sent_correct.append(q)
                    else:
                        closest = max(correct_answers, key=lambda x: difflib.SequenceMatcher(None, user_clean, x.lower()).ratio())
                        st.error(f"❌ Closest correct: {closest}")
                        st.session_state.sent_wrong.append((q, closest))
                    st.session_state.sent_feedback = True
            elif st.button("➡ Next"):
                st.session_state.sent_index += 1
                st.session_state.sent_feedback = False
                st.rerun()

        else:
            total = len(questions)
            score = len(st.session_state.sent_correct)
            st.success(f"🎉 Done! You got {score} / {total} correct ({(score / total) * 100:.0f}%)")

            if st.session_state.sent_wrong:
                st.markdown("### Review incorrect answers:")
                for q, a in st.session_state.sent_wrong:
                    st.write(f"- **{q}** → Correct: *{a}*")

            if st.button("🔁 Restart Trainer"):
                for key in ["sent_index", "sent_correct", "sent_wrong", "sent_feedback"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()



# ----------------- GRAMMAR PRACTICE -----------------
if section == "🔢 Grammar Practice":
    st.title("🔢 Grammar Practice")

    practice_topic = st.selectbox("Choose a topic:", [
        "Verb Conjugation (Present)",
        "Perfekt Builder",
        "Number Spelling"
    ])

    grammar_practice = {
        "Verb Conjugation (Present)": [
            {"question": "Conjugate 'gehen' in ich-form:", "answer": "ich gehe"},
            {"question": "Conjugate 'lernen' in ich-form:", "answer": "ich lerne"},
            {"question": "Conjugate 'haben' in ich-form:", "answer": "ich habe"},
            {"question": "Conjugate 'sein' in ich-form:", "answer": "ich bin"},
            {"question": "Conjugate 'wohnen' in ich-form:", "answer": "ich wohne"}
        ],
        "Perfekt Builder": [
            {"question": "Build Perfekt: ich + essen", "answer": "habe gegessen"},
            {"question": "Build Perfekt: wir + gehen", "answer": "sind gegangen"},
            {"question": "Build Perfekt: du + sehen", "answer": "hast gesehen"},
            {"question": "Build Perfekt: sie (pl) + kommen", "answer": "sind gekommen"},
            {"question": "Build Perfekt: er + schreiben", "answer": "hat geschrieben"}
        ],
        "Number Spelling": [
            {"question": "Spell 25 in German:", "answer": "fünfundzwanzig"},
            {"question": "Spell 456 in German:", "answer": "vierhundertsechsundfünfzig"},
            {"question": "Spell 321 in German:", "answer": "dreihunderteinundzwanzig"},
            {"question": "Spell 4445 in German:", "answer": "viertausendvierhundertfünfundvierzig"},
            {"question": "Spell 6654 in German:", "answer": "sechstausendsechshundertvierundfünfzig"}
        ]
    }

    key_prefix = f"practice_{practice_topic}"

    if f"{key_prefix}_index" not in st.session_state:
        st.session_state[f"{key_prefix}_index"] = 0
        st.session_state[f"{key_prefix}_score"] = 0
        st.session_state[f"{key_prefix}_answers"] = []

        # Preview before starting
        if st.checkbox("🔍 Preview all tasks"):
            for i, item in enumerate(grammar_practice[practice_topic], 1):
                st.write(f"{i}. {item['question']} → {item['answer']}")
        if st.button("🚀 Start Practice"):
            st.rerun()

    else:
        index = st.session_state[f"{key_prefix}_index"]
        questions = grammar_practice[practice_topic]
        total = len(questions)

        if index < total:
            q = questions[index]
            st.markdown(f"### Task {index + 1} of {total}")
            st.markdown(f"**{q['question']}**")
            user_input = st.text_input("Your answer:", key=f"practice_input_{index}")

            if st.button("✅ Submit", key=f"submit_practice_{index}"):
                correct = q["answer"].lower().strip()
                user = user_input.lower().strip()
                st.session_state[f"{key_prefix}_answers"].append((q["question"], user, correct))
                if user == correct:
                    st.success("✅ Correct!")
                    st.session_state[f"{key_prefix}_score"] += 1
                else:
                    st.error(f"❌ Incorrect. Correct: {correct}")
                st.session_state[f"{key_prefix}_index"] += 1
                st.rerun()

        else:
            score = st.session_state[f"{key_prefix}_score"]
            st.success(f"🎉 Practice complete! Score: {score} / {total} ({(score / total) * 100:.0f}%)")

            st.markdown("### Review:")
            for q_text, user, correct in st.session_state[f"{key_prefix}_answers"]:
                st.write(f"- **{q_text}** → Your answer: *{user}* — Correct: *{correct}*")

            if st.button("🔁 Restart Practice"):
                for k in [f"{key_prefix}_index", f"{key_prefix}_score", f"{key_prefix}_answers"]:
                    del st.session_state[k]
                st.rerun()


# ----------------- A2 GRAMMAR QUIZ -----------------
if section == "🧪 Grammar Quiz":
    st.title("🧪 A2 Grammar Quiz")
    st.markdown("Choose a grammar topic and test your knowledge.")

    quiz_topics = {
        "Konjunktionen": [
            {"question": "Ich bleibe zu Hause, ___ ich krank bin.", "options": ["weil", "ob", "dass"], "answer": "weil"},
            {"question": "Er sagt, ___ er keine Zeit hat.", "options": ["dass", "ob", "weil"], "answer": "dass"},
            {"question": "Ich weiß nicht, ___ sie kommt.", "options": ["ob", "dass", "weil"], "answer": "ob"},
            {"question": "Wir glauben, ___ es regnet.", "options": ["dass", "ob", "weil"], "answer": "dass"},
            {"question": "Er fragt, ___ ich morgen Zeit habe.", "options": ["ob", "weil", "dass"], "answer": "ob"}
        ],
        "Trennbare Verben": [
            {"question": "Ich ___ um 7 Uhr ___", "options": ["stehe ... auf", "aufstehe ... um", "stehe ... an"], "answer": "stehe ... auf"},
            {"question": "Er ___ seine Freundin ___", "options": ["ruft ... an", "anruft ... Freundin", "ruft ... mit"], "answer": "ruft ... an"},
            {"question": "Wir ___ am Samstag ___", "options": ["kaufen ... ein", "einkaufen ... gehen", "kaufen ... aus"], "answer": "kaufen ... ein"},
            {"question": "Sie ___ die Tür ___", "options": ["macht ... auf", "aufmacht ... Tür", "macht ... an"], "answer": "macht ... auf"},
            {"question": "Kommst du heute Abend ___?", "options": ["mit", "an", "ein"], "answer": "mit"}
        ],
        "Perfekt": [
            {"question": "Ich ___ einen Apfel ___", "options": ["habe ... gegessen", "bin ... gegessen", "habe ... essen"], "answer": "habe ... gegessen"},
            {"question": "Wir ___ nach Berlin ___", "options": ["sind ... gefahren", "haben ... gefahren", "sind ... geflogen"], "answer": "sind ... gefahren"},
            {"question": "Er ___ das Buch ___", "options": ["hat ... gelesen", "ist ... gelesen", "hat ... lesen"], "answer": "hat ... gelesen"},
            {"question": "Sie ___ einen Brief ___", "options": ["hat ... geschrieben", "ist ... geschrieben", "hat ... schrieben"], "answer": "hat ... geschrieben"},
            {"question": "Du ___ zu spät ___", "options": ["bist ... gekommen", "hast ... gekommen", "bist ... gegangen"], "answer": "bist ... gekommen"}
        ]
    }

    topic = st.selectbox("Choose a topic:", list(quiz_topics.keys()))

    if topic:
        key_prefix = f"grammar_{topic}"
        questions = quiz_topics[topic]

        if f"{key_prefix}_index" not in st.session_state:
            st.session_state[f"{key_prefix}_index"] = 0
            st.session_state[f"{key_prefix}_score"] = 0
            st.session_state[f"{key_prefix}_answers"] = []

            if st.checkbox("🔍 Preview all questions and answers"):
                for i, q in enumerate(questions, 1):
                    st.write(f"{i}. {q['question']} → **{q['answer']}**")

            if st.button("🚀 Start Quiz"):
                st.rerun()
        else:
            index = st.session_state[f"{key_prefix}_index"]

            if index < len(questions):
                q = questions[index]
                st.markdown(f"### {index + 1}. {q['question']}")
                user_ans = st.radio("Choose the correct answer:", q["options"], key=f"radio_{index}")

                if st.button("✅ Submit", key=f"submit_{index}"):
                    st.session_state[f"{key_prefix}_answers"].append((q["question"], user_ans, q["answer"]))
                    if user_ans == q["answer"]:
                        st.success("✅ Correct!")
                        st.session_state[f"{key_prefix}_score"] += 1
                    else:
                        st.error(f"❌ Incorrect. Correct answer: {q['answer']}")
                    st.session_state[f"{key_prefix}_index"] += 1
                    st.rerun()
            else:
                total = len(questions)
                score = st.session_state[f"{key_prefix}_score"]
                st.success(f"🎉 Done! You scored {score} / {total} ({(score / total) * 100:.0f}%)")

                st.markdown("### Review:")
                for q_text, user, correct in st.session_state[f"{key_prefix}_answers"]:
                    st.write(f"- **{q_text}** → Your answer: *{user}* — Correct: *{correct}*")

                if st.button("🔁 Restart Topic"):
                    for k in [f"{key_prefix}_index", f"{key_prefix}_score", f"{key_prefix}_answers"]:
                        del st.session_state[k]
                    st.rerun()
