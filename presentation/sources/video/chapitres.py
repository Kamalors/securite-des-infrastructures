# -*- coding: utf-8 -*-
"""Chapitres horodatés et transcription lisible de la vidéo, à partir du script et de la chronologie de build.py.
Usage : python chapitres.py script.json dossier_de_travail sortie.md"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import pour_affichage  # noqa: E402


def hms(t):
    m, s = divmod(int(t), 60)
    return f"{m}:{s:02d}"


def main():
    script = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    chrono = json.loads((Path(sys.argv[2]) / "chronologie.json").read_text(encoding="utf-8"))
    debut = {s["si"]: s["debut"] for s in chrono["scenes"]}
    nom = [sc.get("chapitre") or sc["title"] for sc in script["scenes"]]
    lignes = ["# Le projet RAO expliqué : chapitres et transcription", "",
              f"Vidéo : [projet_rao_explique.mp4](projet_rao_explique.mp4) · durée : {hms(chrono['duree'])}", "",
              "## Chapitres", ""]
    lignes += [f"- **{hms(debut[si])}** {nom[si]}" for si in range(len(nom))]
    lignes += ["", "## Transcription", ""]
    for si, sc in enumerate(script["scenes"]):
        lignes += [f"### {hms(debut[si])} · {nom[si]}", "",
                   pour_affichage(" ".join(b["say"] for b in sc["beats"])), ""]
    Path(sys.argv[3]).write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("ok", sys.argv[3])


if __name__ == "__main__":
    main()
