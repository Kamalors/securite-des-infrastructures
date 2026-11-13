# -*- coding: utf-8 -*-
"""Planches de l'état final de chaque scène (relecture visuelle) : python planches_scenes.py script.json dossier_de_travail"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

script, work = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")), Path(sys.argv[2])
etats = work / "etats"
finals = []
for si, sc in enumerate(script["scenes"]):
    ks = sorted(int(p.stem.split("_")[2]) for p in etats.glob(f"etat_{si:02d}_*.png"))
    finals.append({"scene": si, "id": sc["id"], "image": str(etats / f"etat_{si:02d}_{ks[-1]}.png"),
                   "etats": [str(etats / f"etat_{si:02d}_{k}.png") for k in ks]})
(work / "etats_finals.json").write_text(json.dumps(finals, ensure_ascii=False, indent=1), encoding="utf-8")
W, H = 960, 540
for page in range((len(finals) + 3) // 4):
    sheet = Image.new("RGB", (2 * W + 8, 2 * H + 8), (60, 60, 60))
    for j, f in enumerate(finals[page * 4:page * 4 + 4]):
        im = Image.open(f["image"]).convert("RGB").resize((W, H), Image.LANCZOS)
        ImageDraw.Draw(im).text((10, 8), f"{f['scene']:02d} {f['id']}", fill=(220, 40, 40))
        sheet.paste(im, ((j % 2) * (W + 8), (j // 2) * (H + 8)))
    sheet.save(work / f"planche_scenes_{page + 1}.png")
print("ok", len(finals), "scènes")
