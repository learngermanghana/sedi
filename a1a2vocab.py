import streamlit as st
import random
import re

st.title("German Vocabulary Quiz")
st.write("Welcome to the German Vocabulary Quiz by **Learn Language Education Academy**.")

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
    ("die Kreuzung", "intersection"), ("der Parkplatz", "parking lot"), ("der Fahrplan", "schedule")
]

# --- SMART CLEANING FUNCTION ---
def clean_answer(text):
    text = text.lower().strip()
    text = re.sub(r'\b(the|a|an|to)\b', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words.sort()
    return ' '.join(words)
# --- FULL A2 VOCABULARY ---
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

# --- SYNONYMS DICTIONARY ---
extra_synonyms = {
    "retten": ["rescue", "save"],
    "laufen": ["to run", "run"],
    "tragen": ["to carry", "carry"],
    "beenden": ["to finish", "to end"],
    "verletzt": ["injured", "hurt"],
    "schmutzig": ["dirty", "unclean"],
    "deprimiert": ["depressed", "sad"],
    "bauen": ["to build", "construct"],
    "erfahren": ["to learn", "to find out", "find out"],
    "aufbleiben": ["to stay up", "remain awake"],
    "baden": ["to bathe", "to swim"],
    "kennenlernen": ["to get to know", "meet"],
    "streiten": ["to argue", "to fight"],
    "böse": ["angry", "evil", "mad"],
    "kaputt": ["broken", "damaged"]
}

# --- SESSION SETUP ---
level = st.selectbox("Select the level", ["A1", "A2"])
vocab_list = a1_vocab if level == "A1" else a2_vocab

num_words = st.slider("How many words do you want to answer?", min_value=5, max_value=len(vocab_list), step=1)
st.write(f"Total available: {len(vocab_list)}")

if "quiz_vocab" not in st.session_state or st.session_state.get("level") != level or st.session_state.get("num_words") != num_words:
    st.session_state.quiz_vocab = random.sample(vocab_list, num_words)
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.started = False
    st.session_state.submitted = False
    st.session_state.answers = []
    st.session_state.level = level
    st.session_state.num_words = num_words
if st.button("Start Quiz") and not st.session_state.started:
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.started = True
    st.session_state.submitted = False
    st.session_state.answers = []
    st.session_state.quiz_vocab = random.sample(vocab_list, num_words)

if st.session_state.started:
    total = len(st.session_state.quiz_vocab)

    if st.session_state.current_index < total:
        word, correct_answer = st.session_state.quiz_vocab[st.session_state.current_index]

        st.progress((st.session_state.current_index + 1) / total)
        st.subheader(f"Question {st.session_state.current_index + 1} of {total}")
        st.subheader(f"Translate to English: '{word}'")

        user_input = st.text_input("Your answer:", key=f"input_{st.session_state.current_index}")

        if not st.session_state.submitted:
            if st.button("Submit"):
                student = clean_answer(user_input)
                correct = clean_answer(correct_answer)

                # Synonyms matching
                word_key = word.lower().split()[0]  # base word only
                accepted_answers = [correct]
                if word_key in extra_synonyms:
                    accepted_answers.extend([clean_answer(ans) for ans in extra_synonyms[word_key]])

                if student in accepted_answers:
                    st.success("Correct!")
                    st.session_state.score += 1
                    result = "Correct"
                else:
                    st.error(f"Wrong. Correct answer: {correct_answer}")
                    result = "Incorrect"

                st.session_state.answers.append({
                    "word": word,
                    "your_answer": user_input,
                    "correct_answer": correct_answer,
                    "result": result
                })

                st.session_state.submitted = True

        elif st.button("Next"):
            st.session_state.current_index += 1
            st.session_state.submitted = False

    else:
        score = st.session_state.score
        percent = (score / num_words) * 100

        # Bilingual feedback
        if percent >= 90:
            message = "Excellent work! 🌟 / Ausgezeichnete Arbeit! 🌟"
        elif percent >= 75:
            message = "Great job! 👍 / Gute Arbeit! 👍"
        elif percent >= 50:
            message = "Good effort, keep practicing! / Gute Mühe, übe weiter!"
        else:
            message = "Don't give up! Review and try again. / Gib nicht auf! Wiederhole und versuche es erneut."

        st.success(f"Quiz complete! Your score: {score} / {num_words} ({percent:.0f}%)")
        st.info(message)

        st.subheader("Answer Review")
        for item in st.session_state.answers:
            st.write(
                f"{item['word']}: Your answer: {item['your_answer']} — {item['result']} (Correct: {item['correct_answer']})"
            )

        if st.button("Restart"):
            st.session_state.started = False
            st.session_state.quiz_vocab = random.sample(vocab_list, num_words)
            st.session_state.current_index = 0
            st.session_state.score = 0
            st.session_state.submitted = False
            st.session_state.answers = []
