"""Assemble la voix par scène, écrit le minutage des mots et contrôle la prononciation.

Usage : python scripts/assembler_voix.py [scène ...]      (ex. 01 04 ; sans argument : toutes celles déjà générées)
Entrée  : out/voix/<unité>.wav et .json (produits par scripts/voix.py)
Sorties : public/voix/NN.mp3 (-16 LUFS), src/voix/NN.json (durée, mots avec début et fin, début et durée des parties)
Contrôle : transcription Whisper comparée au script, écart de minutage avec Whisper, variation de hauteur.
"""
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from faster_whisper import WhisperModel
from num2words import num2words

RACINE = Path(__file__).resolve().parent.parent
BRUT = RACINE / "out" / "voix"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 24000
PAUSE = 0.45  # silence entre deux parties d'une même scène, en secondes
SCENES = {f"{n:02d}": [f"{n:02d}"] for n in range(1, 10)}
SCENES["04"] = ["04a", "04b", "04c", "04d"]


def ffmpeg(*args, entree=None):
    return subprocess.run([FFMPEG, "-hide_banner", "-nostdin" if entree is None else "-y", *args],
                          input=entree, capture_output=True, check=True)


def charger(chemin, sr=SR):
    return np.frombuffer(ffmpeg("-v", "error", "-i", str(chemin), "-f", "f32le", "-ac", "1", "-ar", str(sr), "-").stdout,
                         dtype=np.float32)


def fin_de_parole(x):
    """Dernier instant au-dessus de -45 dB, en secondes."""
    fort = np.flatnonzero(np.abs(x) > 10 ** (-45 / 20))
    return (fort[-1] + 1) / SR if len(fort) else len(x) / SR


def normaliser(s):
    s = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", s)  # 10 000 -> 10000
    s = s.replace("€", " euros ")
    s = re.sub(r"\d+(?:[,.]\d+)?", lambda m: " " + num2words(float(m.group().replace(",", ".")) if re.search("[,.]", m.group()) else int(m.group()), lang="fr") + " ", s)
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s).split()


def hauteur(x, sr=16000):
    """Écart-type de la hauteur de la voix, en demi-tons (autocorrélation, 75 à 400 Hz) : un indice de monotonie."""
    n, pas, lo, hi = int(0.04 * sr), int(0.01 * sr), sr // 400, sr // 75
    seuil = 0.1 * np.sqrt(np.mean(x ** 2))
    f0 = []
    for i in range(0, len(x) - n, pas):
        t = x[i:i + n] - x[i:i + n].mean()
        if np.sqrt(np.mean(t ** 2)) < seuil:
            continue
        ac = np.correlate(t, t, "full")[n - 1:]
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[0] > 0 and ac[k] / ac[0] > 0.5:
            f0.append(sr / k)
    return float(np.std(12 * np.log2(np.array(f0) / np.median(f0))))


def assembler(scene):
    morceaux, mots, parties, textes, t0 = [], [], {}, [], 0.0
    for unite in SCENES[scene]:
        meta = json.loads((BRUT / f"{unite}.json").read_text(encoding="utf-8"))
        x = charger(BRUT / f"{unite}.wav")
        fin = fin_de_parole(x)
        x = x[: int((fin + 0.35) * SR)]
        originaux = []
        for jeton in meta["texte"].split():
            if jeton == ":" and originaux:  # Kyutai ne minute pas les deux-points : on les rattache au mot précédent
                originaux[-1] += " :"
            else:
                originaux.append(jeton)
        assert len(originaux) == len(meta["mots"]), f"{unite} : {len(originaux)} mots dans le script, {len(meta['mots'])} minutés"
        debuts = [pas / meta["pas_par_seconde"] for _, pas in meta["mots"]]
        for i, mot in enumerate(originaux):
            suivant = debuts[i + 1] if i + 1 < len(debuts) else fin
            mots.append({"mot": mot, "debut": round(t0 + debuts[i], 3), "fin": round(t0 + max(suivant, debuts[i] + 0.08), 3)})
        parties[unite] = {"debut": round(t0, 3), "duree": round(len(x) / SR, 3)}
        textes.append(meta["texte"])
        morceaux += [x, np.zeros(int(PAUSE * SR), dtype=np.float32)]
        t0 += len(x) / SR + PAUSE
    audio = np.concatenate(morceaux[:-1])  # sans la pause finale

    # Volume : un seul gain par scène pour viser -16 LUFS, sans dépasser -1,5 dB en crête. Aucune compression.
    mesure = ffmpeg("-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", "loudnorm=print_format=json", "-f", "null", "-",
                    entree=audio.tobytes()).stderr.decode("utf-8", "replace")
    m = json.loads(mesure[mesure.rindex("{"):mesure.rindex("}") + 1])
    gain = min(-16 - float(m["input_i"]), -1.5 - float(m["input_tp"]))
    (RACINE / "public" / "voix").mkdir(parents=True, exist_ok=True)
    ffmpeg("-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"volume={gain:.2f}dB",
           "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "160k", str(RACINE / "public" / "voix" / f"{scene}.mp3"), entree=audio.tobytes())
    (RACINE / "src" / "voix").mkdir(parents=True, exist_ok=True)
    (RACINE / "src" / "voix" / f"{scene}.json").write_text(
        json.dumps({"duree": round(len(audio) / SR, 3), "parties": parties, "mots": mots}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return audio, mots, " ".join(textes)


def controler(scene, audio, mots, texte, whisper):
    x16 = charger(RACINE / "public" / "voix" / f"{scene}.mp3", 16000)  # contrôle sur le fichier livré
    segments, _ = whisper.transcribe(x16, language="fr", word_timestamps=True)
    entendus = [w for s in segments for w in s.words]
    attendu, entendu = normaliser(texte), normaliser(" ".join(w.word for w in entendus))
    sm = difflib.SequenceMatcher(None, attendu, entendu, autojunk=False)
    ecarts = [f"« {' '.join(attendu[i1:i2])} » -> « {' '.join(entendu[j1:j2])} »"
              for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]

    # Écart de minutage : début de chaque mot selon Kyutai, comparé à Whisper, sur les mots identiques.
    a = [(j, m["debut"]) for m in mots for j in normaliser(m["mot"])[:1]]
    b = [(j, w.start) for w in entendus for j in normaliser(w.word)[:1]]
    sm2 = difflib.SequenceMatcher(None, [j for j, _ in a], [j for j, _ in b], autojunk=False)
    d = np.array([a[i + k][1] - b[j + k][1] for i, j, n in sm2.get_matching_blocks() for k in range(n)])
    print(f"\nScène {scene} : {len(audio) / SR:.1f} s | ressemblance {sm.ratio():.3f} | variation de hauteur {hauteur(x16):.1f} dt"
          f" | minutage Kyutai - Whisper : médiane {np.median(d) * 1000:+.0f} ms, 90 % sous {np.percentile(np.abs(d - np.median(d)), 90) * 1000:.0f} ms")
    for e in ecarts:
        print("   écart :", e)
    if ecarts:
        print("   entendu :", " ".join(w.word.strip() for w in entendus))


if __name__ == "__main__":
    scenes = sys.argv[1:] or [s for s, unites in SCENES.items() if all((BRUT / f"{u}.wav").exists() for u in unites)]
    whisper = WhisperModel("medium", device="cpu", compute_type="int8")
    for scene in scenes:
        controler(scene, *assembler(scene), whisper)
