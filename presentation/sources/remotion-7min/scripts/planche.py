"""Planche de contrôle : des images extraites d'une vidéo, rangées en grille, chacune avec son instant.

Usage : python scripts/planche.py video.mp4 sortie.jpg colonnes image [image ...]     (numéros d'images, à 30 images/s)
À lancer depuis la racine du projet (la police est lue dans public/fonts).
"""
import subprocess
import sys

import imageio_ffmpeg

FPS = 30
video, sortie, colonnes, *images = sys.argv[1:]
colonnes = int(colonnes)
L, H = 640, 360

entrees, filtres = [], []
for i, n in enumerate(map(int, images)):
    t = n / FPS
    entrees += ["-ss", f"{t:.4f}", "-i", video]
    texte = f"{int(t // 60)}\\:{t % 60:04.1f}"
    filtres.append(
        f"[{i}:v]trim=end_frame=1,scale={L}:{H},drawtext=fontfile=public/fonts/InstrumentSans-Bold.ttf:text='{texte}':"
        f"x=14:y=h-46:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=8[v{i}]")
disposition = "|".join(f"{(i % colonnes) * L}_{(i // colonnes) * H}" for i in range(len(images)))
filtres.append("".join(f"[v{i}]" for i in range(len(images))) + f"xstack=inputs={len(images)}:layout={disposition}[planche]")
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", *entrees, "-filter_complex", ";".join(filtres),
                "-map", "[planche]", "-frames:v", "1", "-q:v", "2", sortie], check=True)
print("ok", sortie)
