# -*- coding: utf-8 -*-
"""Mesures objectives d'une vidéo produite par build.py, pour la relecture critique (les relecteurs ne peuvent pas écouter).
Usage : python mesures.py <dossier_de_travail> [--asr]   ->  <dossier>/mesures.json
--asr : transcrit chaque phrase avec Whisper et la compare au texte prévu (repère les mots mal prononcés)."""
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import imageio_ffmpeg

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import en_lettres  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def norm(t):
    t = re.sub(r"\b[A-Z](?:-[A-Z])+\b", lambda m: m.group(0).replace("-", ""), t)  # « H-D-S » -> « HDS »
    t = en_lettres(t)
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^a-z0-9 ]+", " ", t.replace("-", " ").replace("'", " ").replace("’", " "))
    return t.split()


def audio_16k(path):
    """Décodage par ffmpeg (évite PyAV, dont l'API a changé) : flottants 16 kHz mono, attendus par Whisper."""
    import numpy as np
    raw = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def info_video(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path)], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stderr
    return [l.strip() for l in err.splitlines() if "Duration" in l or "Stream" in l]


def volume(path):
    err = subprocess.run([FFMPEG, "-hide_banner", "-i", str(path), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return {"lufs_integre": float(m["input_i"]), "crete_vraie_db": float(m["input_tp"]), "plage_lra": float(m["input_lra"])}


def main():
    work = Path(sys.argv[1])
    chrono = json.loads((work / "chronologie.json").read_text(encoding="utf-8"))
    beats = chrono["beats"]
    video = next(iter(sorted(work.glob("projet_rao_explique.mp4"))), None) or next(iter(sorted(work.glob("*.mp4"))))
    res = {"video": str(video), "taille_mo": round(video.stat().st_size / 1e6, 1), "flux": info_video(video),
           "duree_min": round(chrono["duree"] / 60, 2), "volume": volume(work / "voix.wav")}
    scenes, lignes = {}, []
    for b in beats:
        mots = len(b["texte"].split())
        wpm = mots / b["duree"] * 60 if b["duree"] else 0
        lignes.append({**b, "mots": mots, "mots_par_minute": round(wpm)})
        s = scenes.setdefault(b["scene"], {"debut": b["debut"], "fin": 0, "mots": 0, "phrases": 0})
        s["fin"] = b["debut"] + b["duree"]
        s["mots"] += mots
        s["phrases"] += 1
    for s in scenes.values():
        s["duree"] = round(s["fin"] - s["debut"], 1)
        s["mots_par_minute"] = round(s["mots"] / max(1e-6, s["duree"]) * 60)
    debits = sorted(l["mots_par_minute"] for l in lignes)
    res["debit"] = {"median": debits[len(debits) // 2], "min": debits[0], "max": debits[-1],
                    "phrases_les_plus_rapides": sorted(lignes, key=lambda l: -l["mots_par_minute"])[:5],
                    "phrases_les_plus_longues": sorted(lignes, key=lambda l: -l["duree"])[:5]}
    res["scenes"] = scenes

    if "--asr" in sys.argv:
        from faster_whisper import WhisperModel
        modele = WhisperModel("medium", device="cuda" if "--cuda" in sys.argv else "cpu",
                              compute_type="float16" if "--cuda" in sys.argv else "int8")
        ecarts = []
        for l in lignes:
            wav = Path(l["audio"]) if l.get("audio") else work / "audio" / f"b_{int(l['si']):02d}_{int(l['beat']):02d}.wav"
            if not wav.exists():
                continue
            segs, _ = modele.transcribe(audio_16k(wav), language="fr", beam_size=5, vad_filter=False)
            entendu = " ".join(s.text.strip() for s in segs)
            # comparé au texte écrit et au texte lu (graphies phonétiques du lexique) : on garde le meilleur
            ratio = max(difflib.SequenceMatcher(None, norm(t), norm(entendu)).ratio()
                        for t in {l["texte"], l.get("lu") or l["texte"]})
            l["entendu"], l["similarite"] = entendu, round(ratio, 3)
            if ratio < 0.9:
                ecarts.append({"scene": l["scene"], "beat": l["beat"], "prevu": l["texte"], "entendu": entendu,
                               "similarite": round(ratio, 3)})
        res["asr"] = {"modele": "faster-whisper medium", "phrases_suspectes": sorted(ecarts, key=lambda e: e["similarite"])}
    res["phrases"] = lignes
    (work / "mesures.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k not in ("phrases", "scenes")}, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main()
