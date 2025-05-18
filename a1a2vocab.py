import os
import streamlit as st
import pandas as pd
import random
import re
import difflib
from datetime import datetime

st.set_page_config(page_title="German Learning App", page_icon="🇩🇪", layout="centered")

# --- Rerun Helper ---
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

# --- Leaderboard Helpers ---
LEADERBOARD_FILE = "leaderboard.csv"
def save_score(student_code, module, level, score, total):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = {"student_code": student_code, "module": module, "level": level, "score": score, "total": total, "datetime": now}
    try:
        df = pd.read_csv(LEADERBOARD_FILE)
        df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    except:
        df = pd.DataFrame([entry])
    df.to_csv(LEADERBOARD_FILE, index=False)

def show_leaderboard(module, level):
    if not os.path.exists(LEADERBOARD_FILE):
        st.info("No scores saved yet.")
        return
    df = pd.read_csv(LEADERBOARD_FILE)
    filtered = df[(df["module"]==module)&(df["level"]==level)]
    if filtered.empty:
        st.info(f"No scores for {module} ({level}) yet.")
        return
    filtered = filtered.sort_values(by="score", ascending=False).head(10)
    st.markdown("### 🏆 Leaderboard")
    st.dataframe(filtered[["student_code","score","total","datetime"]], hide_index=True)

# --- Back Button ---
def back_button():
    if st.button("⬅️ Back to Dashboard"):
        if "section_override" in st.session_state:
            del st.session_state["section_override"]
        rerun()
        
def load_grammar_data():
    return [
        # --- A1 Topics ---
        {"level":"A1","topic":"Word Classes (Wortarten)","keywords":["word classes","wortarten","nouns","verbs","adjectives","adverbs","pronouns","articles","prepositions","conjunctions","numerals","interjections"],"explanation":"German Wortarten categorize words by function (e.g., nouns, verbs, adjectives, adverbs, pronouns, articles, prepositions, conjunctions, numerals, interjections).","example":"Das schnelle Auto fährt sehr laut."},
        {"level":"A1","topic":"Personal Pronouns","keywords":["ich","du","er","sie","es","wir","ihr","Sie"],"explanation":"Pronouns replace nouns: ich (I), du (you). Must match case, number, and gender.","example":"Ich bin Felix."},
        {"level":"A1","topic":"Nouns & Genders","keywords":["nouns","genders","genus"],"explanation":"All German nouns are capitalized and have three genders: der (masc), die (fem), das (neut).","example":"Der Tisch, die Lampe, das Auto."},
        {"level":"A1","topic":"Verb Conjugation","keywords":["verb","conjugation","regular","irregular"],"explanation":"Regular verbs follow predictable endings (ich mache); irregular verbs change stems (ich gehe).","example":"Ich mache Hausaufgaben. Du gehst zur Schule."},
        {"level":"A1","topic":"'sein' and 'haben'","keywords":["sein","haben"],"explanation":"'sein' describes states and identity; 'haben' indicates possession and forms compound tenses.","example":"Ich bin müde. Ich habe ein Buch."},
        {"level":"A1","topic":"Present Tense (Präsens)","keywords":["present","präsens"],"explanation":"Used for current, habitual, or scheduled actions. Conjugate to match the subject.","example":"Ich lerne Deutsch. Er spielt Fußball."},
        {"level":"A1","topic":"Sentence Structure","keywords":["word order","satzstellung"],"explanation":"In main clauses, the finite verb is in the second position. Yes/no questions invert subject and verb.","example":"Kommst du morgen?"},
        {"level":"A1","topic":"Imperative (Imperativ)","keywords":["imperative","imperativ","du","ihr","Sie"],"explanation":"The imperative expresses commands: for informal singular (du) use the verb stem without ending (e.g., 'Komm!'); for informal plural (ihr) add '-t' to the stem (e.g., 'Kommt!'); for formal (Sie) use the infinitive + Sie (e.g., 'Kommen Sie!').","example":"Komm hier! Kommt hier! Kommen Sie hier!"},
        {"level":"A1","topic":"Definite & Indefinite Articles","keywords":["articles","der","die","das","ein","eine"],"explanation":"Definite (der, die, das) vs. indefinite (ein, eine) articles indicate gender and definiteness.","example":"Der Mann. Eine Frau."},
        {"level":"A1","topic":"Negation","keywords":["nicht","kein"],"explanation":"nicht negates verbs/adjectives; kein negates nouns.","example":"Ich komme nicht. Ich habe keinen Hund."},
        {"level":"A1","topic":"Modal Verbs","keywords":["können","müssen","dürfen","wollen","sollen"],"explanation":"Express ability, necessity, permission, or desire.","example":"Ich kann schwimmen."},
        {"level":"A1","topic":"Possessive Pronouns","keywords":["mein","dein","sein","ihr"],"explanation":"Indicate ownership: mein Buch, deine Tasche.","example":"Das ist mein Buch."},
        {"level":"A1","topic":"Adjective Endings (Basic)","keywords":["adjective endings","adjektivdeklination"],"explanation":"Basic adjective endings agree with the noun's gender, case, and number: der gute Mann, die schöne Blume.","example":"Die schöne Blume."},
        {"level":"A1","topic":"Adverbs (Basic)","keywords":["adverbs","adverbien"],"explanation":"Modify verbs, adjectives, or other adverbs: sehr (very), oft (often), hier (here), dort (there).","example":"Ich lerne sehr schnell."},
        {"level":"A1","topic":"Prepositions (2-way & Dative)","keywords":["prepositions","in","auf","mit"],"explanation":"Two-way prepositions use accusative for movement and dative for location; some prepositions (mit, zu) always take dative.","example":"Ich gehe in die Schule. Ich bin in der Schule. Ich fahre mit dem Bus."},
        {"level":"A1","topic":"Separable Verbs","keywords":["separable","verbs"],"explanation":"Prefixes separate in the present tense and move to the end of the clause: aufstehen, anrufen.","example":"Ich stehe um 7 Uhr auf."},
        {"level":"A1","topic":"Time & Date Expressions","keywords":["time","date","um","am","im"],"explanation":"Express times and dates: um 8 Uhr (time), am Montag (day), im Januar (month).","example":"Der Unterricht beginnt um 8 Uhr am Montag im Januar."},
        {"level":"A1","topic":"Common Connectors","keywords":["und","oder","aber","denn"],"explanation":"Basic coordinating conjunctions join clauses without changing word order: und (and), oder (or), aber (but), denn (because).","example":"Ich bin müde, aber glücklich."},
        {"level":"A1","topic":"Numbers & Dates","keywords":["numbers","dates"],"explanation":"Numbers and dates use cardinal and ordinal forms: eins, zwei; der 1. Januar.","example":"Heute ist der 1. Januar."},
        {"level":"A1","topic":"Definite & Indefinite Articles Declension","keywords":["der","die","das","ein","eine"],"explanation":"Declines articles by case and number: Nom: der Mann/ein Mann; Acc: den Mann/einen Mann; Dat: dem Mann/einem Mann; Gen: des Mannes/eines Mannes.","example":"Nominativ: der Hund; Akkusativ: den Hund; Dativ: dem Hund; Genitiv: des Hundes."},
        {"level":"A1","topic":"Modal Verbs Present Conjugation","keywords":["können","müssen","dürfen","wollen","sollen","mögen","möchten"],"explanation":"Present forms for modals: ich kann/muss/darf/will/soll/mag/möchte; du kannst/musst/darfst/willst/sollst/magst/möchtest.","example":"ich kann, du kannst; ich möchte, du möchtest."},
        {"level":"A1","topic":"Main Verbs Present Conjugation","keywords":["machen","gehen","haben","sein","sprechen"],"explanation":"Present forms for main verbs: ich mache/gehe/habe/bin/spreche; du machst/gehst/hast/bist/sprichst.","example":"ich mache, du machst; ich gehe, du gehst."},
        {"level":"A1","topic":"Modal Verbs Präteritum Conjugation","keywords":["dürfen","können","müssen","sollen","wollen","mögen","möchten"],"explanation":"Simple past for modals: ich durfte/konnte/musste/sollte/wollte/mochte/möchte;","example":"ich durfte, du durftest; ich mochte, du mochtest."},
        {"level":"A1","topic":"Statement Structure Rule","keywords":["statement rule","satzbau","svo"],"explanation":"In declarative sentences the finite verb is in the second position (SVO): Subject-Verb-Object.","example":"Ich kaufe einen Apfel."},
        {"level":"A1","topic":"Yes/No Questions","keywords":["yes or no questions","ja nein fragen","inversion"],"explanation":"Form yes/no questions by inverting subject and verb, without a question word.","example":"Kommst du morgen?"},
        {"level":"A1","topic":"W-Questions (W-Fragen)","keywords":["wer","was","wo","wann","warum","wie"],"explanation":"Use W-question words at the beginning; verb remains in second position.","example":"Wo wohnst du?"},
        {"level":"A1","topic":"Modal Verb Rule","keywords":["modal verb rule","modalverben"],"explanation":"Modal verbs occupy second position; the main infinitive goes to the end of the clause.","example":"Ich kann heute nicht kommen."},
        {"level":"A1","topic":"'Weil' Subordinate Clause Rule","keywords":["weil","subordinate clause","verb end"],"explanation":"In subordinate clauses with weil, the verb moves to the end of the clause.","example":"Ich bleibe zu Hause, weil ich krank bin."},
        {"level":"A1","topic":"Main Verbs Präteritum Conjugation","keywords":["machen","gehen","haben","sein","sprechen"],"explanation":"Simple past for main verbs: ich machte/ging/hatte/war/sprach;","example":"ich machte, du machtest; ich ging, du gingst."},

        # --- A2 Topics ---
        {"level":"A2","topic":"Accusative Prepositions","keywords":["bis","durch","für","gegen","ohne","um","entlang"],"explanation":"Always accusative: bis, durch, für, gegen, ohne, um, entlang.","example":"Ich gehe durch den Park."},
        {"level":"A2","topic":"Dative Prepositions","keywords":["aus","außer","bei","mit","nach","seit","von","zu","gegenüber"],"explanation":"Always dative: aus, außer, bei, mit, nach, seit, von, zu, gegenüber.","example":"Ich fahre mit dem Bus."},
        {"level":"A2","topic":"Two-way Prepositions (Full)","keywords":["an","auf","hinter","in","neben","über","unter","vor","zwischen"],"explanation":"Accusative for movement, dative for location for these preps.","example":"Ich lege das Buch auf den Tisch. Das Buch liegt auf dem Tisch."},
        {"level":"A2","topic":"Dative Case Expanded","keywords":["dativ","wem"],"explanation":"The dative case marks indirect objects and answers 'Wem?'; verbs like helfen, danken, gehören require dative.","example":"Ich helfe meinem Freund."},
        {"level":"A2","topic":"Two-way Prepositions","keywords":["wechselpräpositionen","in","an","auf","über","unter","zwischen"],"explanation":"Use accusative for movement (Ich lege das Buch auf den Tisch) and dative for location (Das Buch liegt auf dem Tisch).","example":"Ich lege das Buch auf den Tisch."},
        {"level":"A2","topic":"Comparison of Adjectives","keywords":["komparativ","superlativ"],"explanation":"Form comparatives with -er + als and superlatives with am + adjective + -sten.","example":"Er ist schneller als ich. Er ist am schnellsten."},
        {"level":"A2","topic":"Perfect Tense (Perfekt)","keywords":["perfekt","haben","sein"],"explanation":"Formed with haben/sein + Partizip II to describe completed past actions; use sein for motion and change of state.","example":"Ich habe gegessen. Sie ist gekommen."},
        {"level":"A2","topic":"Future Tense (Futur I)","keywords":["futur","werden"],"explanation":"Use werden + infinitive to express future actions and predictions.","example":"Ich werde morgen lernen."},
        {"level":"A2","topic":"Reflexive Verbs","keywords":["reflexive","sich"],"explanation":"Use reflexive pronouns when subject and object refer to the same entity: Ich freue mich.","example":"Ich freue mich auf das Wochenende."},
        {"level":"A2","topic":"Subordinate Clauses","keywords":["weil","dass","wenn","ob"],"explanation":"In subordinate clauses introduced by conjunctions, the verb goes to the end of the clause.","example":"Ich komme nicht, weil ich krank bin."},
        {"level":"A2","topic":"Indirect Questions","keywords":["indirekte frage","wo","ob"],"explanation":"Use ob for yes/no indirect questions and question words for W-questions in reported speech.","example":"Ich weiß nicht, ob er kommt."},
        {"level":"A2","topic":"Relative Clauses","keywords":["relativsatz","der","die","das"],"explanation":"Provide additional information about a noun using relative pronouns and proper word order.","example":"Das ist der Mann, der Deutsch spricht."},
        {"level":"A2","topic":"Genitive Case","keywords":["genitiv","des","der"],"explanation":"Shows possession or relationships; used with genitive endings on articles or nouns.","example":"Das Buch des Bruders."},
        {"level":"A2","topic":"Adjective Endings After Articles","keywords":["adjective endings","adjektivdeklination"],"explanation":"Detailed adjective endings based on the gender, case, and type of article.","example":"eine rote Jacke, mit dem kleinen Kind."},
        {"level":"A2","topic":"Genitive Prepositions","keywords":["trotz","während","wegen","anstatt"],"explanation":"Prepositions that require the genitive case, expressing cause, time, or exception.","example":"Trotz des Regens gehen wir spazieren."},
        {"level":"A2","topic":"Separable & Inseparable Verbs","keywords":["trennbar","untrennbar"],"explanation":"Separable verbs detach their prefix; inseparable verbs keep it attached. Placement affects meaning.","example":"Ich stehe auf vs. Ich beschäftige mich."},
        {"level":"A2","topic":"Passive Voice (Present)","keywords":["passiv","werden","partizip"],"explanation":"Form passive sentence with werden + Partizip II to focus on the receiver of the action.","example":"Die Pizza wird geliefert."},
        {"level":"A2","topic":"Adverbs of Frequency & Degree","keywords":["oft","manchmal","sehr","kaum"],"explanation":"Use adverbs like oft, manchmal for frequency and sehr, kaum for degree to modify verbs.","example":"Ich bin meistens pünktlich."},
        {"level":"A2","topic":"TMP Rule","keywords":["time","manner","place"],"explanation":"Adverbs and adverbial phrases follow the order: Time - Manner - Place.","example":"Ich lerne heute gerne hier."},
        {"level":"A2","topic":"Common Connectors","keywords":["deshalb","außerdem","zwar aber"],"explanation":"Link ideas logically with connectors like deshalb, außerdem, zwar … aber.","example":"Ich lerne viel, deshalb verstehe ich besser."}
    ]

def search_grammar_topics(query, grammar_data, level_filter):
    query_keywords = [w.strip("?.!").lower() for w in query.split() if len(w) > 2]
    return [e for e in grammar_data if e['level'] in level_filter and any(qk in ak for qk in query_keywords for ak in e.get('keywords',[])+[e['topic'].lower()])]

def show_grammar_ui(grammar_data):
    level_filter = st.sidebar.multiselect("Select Level(s)", ["A1","A2","B1","B2"], default=["A1","A2","B1","B2"])
    query = st.text_input("🔍 Type a grammar question or keyword")
    if query:
        results = search_grammar_topics(query, grammar_data, level_filter)
        if results:
            for entry in results:
                st.subheader(f"{entry['topic']} ({entry['level']})")
                st.markdown(f"**Explanation:** {entry['explanation']}")
                st.markdown(f"**Example:** _{entry['example']}_")
                related = [t['topic'] for t in grammar_data if t['level']==entry['level'] and t['topic']!=entry['topic']]
                if related:
                    st.markdown(f"💡 **Related Topics:** {', '.join(related[:3])}")
                st.markdown("*Refer to your textbook or tutor for more detail.*")
        else:
            st.warning("No matching topics found.")

def show_letter_and_essay_samples():
    st.sidebar.markdown("---")
    samples = {
        "A1": {"intro":"Sehr geehrte Damen und Herren, ich hoffe, es geht Ihnen gut.","body":"Ich möchte einen Termin vereinbaren. Bitte teilen Sie mir mögliche Zeiten mit.","conclusion":"Ich freue mich im Voraus auf Ihre Rückmeldung. Mit freundlichen Grüßen, [Ihr Name]"},
        "A2": {"intro":"Hallo [Name], vielen Dank für deine Nachricht.","body":"Ich interessiere mich für Ihre Wohnung. Ist sie noch verfügbar?","conclusion":"Ich freue mich auf Ihre Antwort. Viele Grüße, [Ihr Name]"},
        "B1": {"intro":"Heutzutage ist das Thema Lernen ein wichtiges Thema in unserem Leben.","body":"Ich bin der Meinung, dass Lernen sehr wichtig ist, weil es uns hilft, unser Wissen zu erweitern. Einerseits gibt es viele Vorteile. Zum Beispiel hilft uns das Lernen mit Apps, flexibler und schneller zu lernen.","conclusion":"Abschließend lässt sich sagen, dass Lernen mit neuen Methoden sehr nützlich ist, auch wenn es manchmal herausfordernd sein kann."},
        "B2": {"intro":"In der heutigen digitalen Ära spielt Social Media eine zentrale Rolle in unserem Alltag.","body":"Während es die Kommunikation erleichtert, kann es auch zu Ablenkung und oberflächlichen Interaktionen führen.","conclusion":"Letztendlich hängt der Nutzen von Social Media von bewusster Nutzung ab."}
    }
    levels = st.sidebar.multiselect("Show Letters/Essays for:", ["A1","A2","B1","B2"], default=["A1","A2","B1","B2"])
    if st.sidebar.checkbox("📬 Show Letter Samples"):
        st.subheader("📬 Letter Samples")
        for lvl in levels:
            sample = samples.get(lvl)
            if sample:
                st.markdown(f"**{lvl} Letter:**")
                st.markdown(f"- **Introduction:** {sample['intro']}")
                st.markdown(f"- **Body:** {sample['body']}")
                st.markdown(f"- **Conclusion:** {sample['conclusion']}")
    if st.sidebar.checkbox("📝 Show Essay Samples"):
        st.subheader("📝 Essay Samples")
        for lvl in levels:
            sample = samples.get(lvl)
            if sample:
                st.markdown(f"**{lvl} Essay:**")
                st.markdown(f"- **Introduction:** {sample['intro']}")
                st.markdown(f"- **Body:** {sample['body']}")
                st.markdown(f"- **Conclusion:** {sample['conclusion']}")

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

# --- Level Selection (Main Page) ---
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

# --- Dashboard Buttons ---
SCHOOL_NAME = "Learn Language Education Academy"
st.markdown(f"## 🏫 {SCHOOL_NAME}")
st.markdown(f"Welcome **{student_code}**! 👋")
st.markdown("---")
st.subheader("📌 Available Modules")
cols = st.columns(3)
with cols[0]:
    if st.button("📚 Start Vocabulary Quiz"):
        clear_states('vocab_index','vocab_score','vocab_quiz','vocab_feedback')
        st.session_state["section_override"] = "📚 Vocabulary Quiz"
        rerun()
    if st.button("✍️ Start Sentence Trainer"):
        clear_states('sent_index','sent_feedback','sent_correct')
        st.session_state["section_override"] = "✍️ Sentence Trainer"
        rerun()
    if st.button("🏆 Show Leaderboard"):
        st.session_state["section_override"] = "🏆 Leaderboard"
        rerun()
with cols[1]:
    if st.button("🔢 Start Grammar Practice"):
        st.session_state["section_override"] = "🔢 Grammar Practice"
        rerun()
    if st.button("🧪 Start Grammar Quiz"):
        clear_states('gq_index')
        st.session_state["section_override"] = "🧪 Grammar Quiz"
        rerun()
with cols[2]:
    if st.button("📘 Grammar Helper"):
        st.session_state["section_override"] = "📘 Grammar Helper"
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
            ["📚 Vocabulary Quiz", "✍️ Sentence Trainer", "🔢 Grammar Practice", "📘 Grammar Helper"],
            key="topic_a1"
        )
    else:
        section = st.radio(
            "Choose a topic:",
            ["📚 Vocabulary Quiz", "✍️ Sentence Trainer", "🧪 Grammar Quiz", "🔢 Grammar Practice", "📘 Grammar Helper"],
            key="topic_a2"
        )

# --- Vocabulary Lists (abbreviated; paste full lists) ---
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
            save_score(student_code, "Vocabulary Quiz", st.session_state["level"], score, total_q)
            show_leaderboard("Vocabulary Quiz", st.session_state["level"])
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

    if st.button("➡ Next Question"):
        st.session_state.gq_index = (st.session_state.gq_index + 1) % len(qlist)
        rerun()
    if st.button("⬅️ Back to Dashboard"):
        del st.session_state["section_override"]
        st.session_state.gq_index = 0
        rerun()

# --- Leaderboard Only View ---
elif section == "🏆 Leaderboard":
    back_button()
    st.title("🏆 Leaderboard")
    module = st.selectbox("Module:", ["Vocabulary Quiz", "Sentence Trainer", "Grammar Quiz"])
    show_leaderboard(module, st.session_state["level"])

# --- German Grammar Helper Section ---
elif section == "📘 Grammar Helper":
    back_button()
    st.title("📘 German Grammar Helper: A1–B2")
    st.markdown("#### Powered by Learn Language Education Academy")
    show_letter_and_essay_samples()
    show_grammar_ui(load_grammar_data())
