from gtts import gTTS
import os
from a1a2vocab import a1_vocab, a2_vocab  # ✅ import both

# Combine both lists
all_vocab = a1_vocab + a2_vocab

os.makedirs("audio", exist_ok=True)

for word, _ in all_vocab:
    filename = word.replace(" ", "_").replace(".", "").replace("/", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss") + ".mp3"
    path = os.path.join("audio", filename)
    if not os.path.exists(path):
        tts = gTTS(word, lang="de")
        tts.save(path)
        print(f"✅ Saved: {path}")
