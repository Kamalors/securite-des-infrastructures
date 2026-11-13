# -*- coding: utf-8 -*-
"""Planche contact : images extraites de la vidéo aux instants donnés (contrôle visuel et critique).
Usage : python planche.py video.mp4 sortie.png t1 t2 ... [--colonnes 2] [--largeur 960]"""
import subprocess
import sys
from io import BytesIO

import imageio_ffmpeg
from PIL import Image, ImageDraw

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opts = dict(a[2:].split("=") for a in sys.argv[1:] if a.startswith("--") and "=" in a)
video, sortie, temps = args[0], args[1], [float(t) for t in args[2:]]
cols, larg = int(opts.get("colonnes", 2)), int(opts.get("largeur", 960))
haut = larg * 9 // 16
imgs = []
for t in temps:
    r = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
                        "-i", video, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    png = r.stdout
    if not png:
        print(f"instant {t} : aucune image ({r.stderr.decode(errors='replace')[:200]})")
        continue
    im = Image.open(BytesIO(png)).convert("RGB").resize((larg, haut), Image.LANCZOS)
    ImageDraw.Draw(im).text((8, 6), f"{int(t // 60)}:{t % 60:04.1f}", fill=(220, 40, 40))
    imgs.append(im)
rows = (len(imgs) + cols - 1) // cols
planche = Image.new("RGB", (cols * larg + (cols - 1) * 8, rows * haut + (rows - 1) * 8), (60, 60, 60))
for i, im in enumerate(imgs):
    planche.paste(im, ((i % cols) * (larg + 8), (i // cols) * (haut + 8)))
planche.save(sortie)
print("ok", sortie, len(imgs))
