"""Prépare la livraison : ajoute les chapitres à la vidéo rendue et écrit les sous-titres SRT.

Usage : python scripts/livraison.py video_rendue.mp4 sortie.mp4      (écrit aussi sortie.srt)
Le déroulé vient de src/plan.json et du minutage des mots (src/voix/NN.json), comme dans la vidéo :
début d'une scène = somme des scènes précédentes, moins une transition par enchaînement.
Affiche aussi, pour chaque scène, où sa voix doit commencer : de quoi lancer scripts/controle_video.py.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

RACINE = Path(__file__).resolve().parent.parent
PLAN = json.loads((RACINE / "src" / "plan.json").read_text(encoding="utf-8"))
FPS, DEBUT, TRANSITION = PLAN["fps"], PLAN["debut"], PLAN["transition"]
# Dans les sous-titres, les sigles s'écrivent comme on les lit d'habitude (le script les épelle pour la voix).
SIGLES = {"S-D-WAN": "SD-WAN", "H-D-S": "HDS", "D-M-Z": "DMZ", "Z-T-N-A": "ZTNA", "V-P-N": "VPN"}
LIGNE = 42  # caractères par ligne de sous-titre
FIN_DE_PHRASE = re.compile(r"[.?!…]$")


def images(secondes):
    return math.ceil(round(secondes * FPS * 1000) / 1000)  # même calcul que images() dans src/Scene.tsx


def deroule():
    """Pour chaque scène : son début dans la vidéo, le début de sa voix, et ses mots (en secondes de la vidéo)."""
    scenes, image = [], 0
    for s in PLAN["scenes"]:
        voix = json.loads((RACINE / "src" / "voix" / f"{s['fichier']}.json").read_text(encoding="utf-8"))
        partie = voix["parties"][s["id"]]
        debut = image / FPS
        mots = [
            {"mot": m["mot"], "debut": debut + DEBUT + m["debut"] - partie["debut"], "fin": debut + DEBUT + m["fin"] - partie["debut"]}
            for m in voix["mots"]
            if partie["debut"] <= m["debut"] < partie["debut"] + partie["duree"]
        ]
        scenes.append({**s, "debut": debut, "voix": debut + DEBUT, "dans_fichier": partie["debut"], "mots": mots})
        image += images(DEBUT + partie["duree"] + s["fin"]) - TRANSITION
    return scenes, (image + TRANSITION) / FPS


def horodatage(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def texte_de(mots):
    return " ".join(m["mot"] for m in mots)


def decouper(mots):
    """Coupe une phrase trop longue pour deux lignes : à la virgule la plus proche du milieu, à défaut entre deux mots."""
    if len(texte_de(mots)) <= 2 * LIGNE or len(mots) < 2:
        return [mots]
    coupes = [k for k, m in enumerate(mots[:-1]) if m["mot"][-1] in ",;:"] or list(range(len(mots) - 1))
    k = min(coupes, key=lambda k: abs(len(texte_de(mots[:k + 1])) - len(texte_de(mots)) / 2))
    return decouper(mots[:k + 1]) + decouper(mots[k + 1:])


def sous_titres(scenes):
    """Une réplique par phrase ; les phrases trop longues sont coupées à la virgule. Deux lignes au plus."""
    repliques = []
    for scene in scenes:
        phrase = []
        for m in scene["mots"]:
            mot = m["mot"]
            for epele, sigle in SIGLES.items():
                mot = mot.replace(epele, sigle)
            if mot[0] in "?!" and phrase:  # ponctuation isolée : elle rejoint le mot précédent
                phrase[-1] = {**phrase[-1], "mot": phrase[-1]["mot"] + "\u00a0" + mot, "fin": m["fin"]}
            else:
                phrase.append({**m, "mot": mot})
            if FIN_DE_PHRASE.search(phrase[-1]["mot"]):
                repliques += decouper(phrase)
                phrase = []
        if phrase:  # une réplique ne chevauche jamais deux scènes
            repliques += decouper(phrase)
    blocs = []
    for i, r in enumerate(repliques):
        texte = texte_de(r)
        if len(texte) > LIGNE:  # deux lignes, coupées au plus près du milieu
            k = min((k for k, c in enumerate(texte) if c == " "), key=lambda k: abs(k - len(texte) / 2))
            texte = texte[:k] + "\n" + texte[k + 1:]
        fin = max(r[-1]["fin"], r[0]["debut"] + 1.0)
        if i + 1 < len(repliques):
            fin = min(fin, repliques[i + 1][0]["debut"] - 0.04)
        blocs.append(f"{i + 1}\n{horodatage(r[0]['debut'])} --> {horodatage(fin)}\n{texte}\n")
    return "\n".join(blocs)


def chapitres(scenes, duree):
    titres = [s for s in scenes if "chapitre" in s]
    lignes = [";FFMETADATA1", "title=Le projet RAO en 5 minutes"]
    for s, suivant in zip(titres, titres[1:] + [{"debut": duree}]):
        lignes += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={round(s['debut'] * 1000)}", f"END={round(suivant['debut'] * 1000)}", f"title={s['chapitre']}"]
    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    rendue, sortie = Path(sys.argv[1]), Path(sys.argv[2])
    scenes, duree = deroule()
    meta = sortie.with_suffix(".chapitres.txt")
    meta.write_text(chapitres(scenes, duree), encoding="utf-8")
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(rendue), "-i", str(meta),
                    "-map", "0", "-map_metadata", "1", "-map_chapters", "1", "-c", "copy", "-movflags", "+faststart", str(sortie)], check=True)
    meta.unlink()
    sortie.with_suffix(".srt").write_text(sous_titres(scenes), encoding="utf-8")
    print(f"ok {sortie} ({duree:.2f} s, {sum('chapitre' in s for s in scenes)} chapitres) et {sortie.with_suffix('.srt').name}")
    print("Début attendu de la voix de chaque scène (fichier@début_dans_le_fichier:début_dans_la_vidéo) :")
    print(" ".join(f"{s['fichier']}.mp3@{s['dans_fichier']:.3f}:{s['voix']:.3f}" for s in scenes))
