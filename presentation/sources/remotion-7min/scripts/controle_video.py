"""Contrôle une vidéo rendue : décodage complet sans erreur, et position réelle de la voix dans la piste son.

Usage : python scripts/controle_video.py video.mp4 fichier@début:attendu [...]
  fichier  : voix de public/voix (ex. 04.mp3)
  début    : seconde où commence l'extrait dans ce fichier
  attendu  : seconde où cet extrait doit commencer dans la vidéo
La position est mesurée par corrélation croisée entre la piste son de la vidéo et 6 secondes de l'extrait.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
RACINE = Path(__file__).resolve().parent.parent
SR = 8000


def son(chemin):
    brut = subprocess.run([FFMPEG, "-v", "error", "-i", str(chemin), "-vn", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                          capture_output=True, check=True).stdout
    return np.frombuffer(brut, dtype=np.float32)


def position(piste, extrait):
    """Seconde de la piste où l'extrait se trouve (maximum de la corrélation croisée, calculée par FFT)."""
    n = len(piste) + len(extrait)
    correlation = np.fft.irfft(np.fft.rfft(piste, n) * np.conj(np.fft.rfft(extrait, n)), n)
    return int(np.argmax(correlation[: len(piste)])) / SR


video = sys.argv[1]
erreurs = subprocess.run([FFMPEG, "-v", "error", "-i", video, "-f", "null", "-"], capture_output=True).stderr.decode("utf-8", "replace").strip()
infos = subprocess.run([FFMPEG, "-hide_banner", "-i", video], capture_output=True).stderr.decode("utf-8", "replace")
print("Décodage complet :", "sans erreur" if not erreurs else "ERREURS\n" + erreurs)
for ligne in infos.splitlines():
    if "Duration" in ligne or "Stream #" in ligne:
        print("  ", ligne.strip())

piste = son(video)
pire = 0.0
for arg in sys.argv[2:]:
    fichier, reste = arg.split("@")
    debut, attendu = map(float, reste.split(":"))
    extrait = son(RACINE / "public" / "voix" / fichier)[int(debut * SR): int((debut + 6) * SR)]
    mesure = position(piste, extrait)
    pire = max(pire, abs(mesure - attendu))
    print(f"Voix {fichier} à partir de {debut:.2f} s : attendue à {attendu:.3f} s, mesurée à {mesure:.3f} s, écart {1000 * (mesure - attendu):+.0f} ms")
assert not erreurs, "la vidéo ne se décode pas proprement"
assert pire < 0.034, f"voix décalée de {pire * 1000:.0f} ms : plus d'une image"
