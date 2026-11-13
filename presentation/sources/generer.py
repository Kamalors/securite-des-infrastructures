# -*- coding: utf-8 -*-
"""Présentation « Le projet expliqué » (philosophie : presentation/philosophie_visuelle.md, Topologie silencieuse).
Usage : python generer.py <sortie.pdf> [numéros de pages pour ne produire que des aperçus]
Aperçus PNG dans ./preview (non suivi par Git)."""
import math
import random
import re
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONTS = HERE / "fonts"
PREV = HERE / "preview"
W, H, S = 1920, 1080, 3          # coordonnées logiques 1920x1080, rendu x3 puis réduction (anticrénelage)
OUT = (2560, 1440)
N = 18

PAPER, PAPER2 = (244, 241, 234), (235, 231, 221)
INK, INK2, MUTED, RULE = (16, 27, 44), (58, 68, 86), (128, 132, 140), (212, 206, 194)
TEAL, TEAL_L = (31, 122, 140), (214, 232, 234)
ORANGE, ORANGE_L = (204, 98, 38), (247, 226, 210)
D_TXT, D_TXT2, D_MUTED, D_TEAL, D_RULE = (240, 236, 228), (190, 198, 210), (132, 145, 165), (127, 200, 214), (48, 62, 84)


def mix(a, b, t):
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


@lru_cache(None)
def font(name, size):
    return ImageFont.truetype(str(FONTS / f"{name}.ttf"), round(size * S))


SERIF = lambda s: font("InstrumentSerif-Regular", s)
SERIF_I = lambda s: font("InstrumentSerif-Italic", s)
SANS = lambda s: font("InstrumentSans-Regular", s)
SANS_B = lambda s: font("InstrumentSans-Bold", s)
MONO = lambda s: font("IBMPlexMono-Regular", s)


def fr(s):
    """Typographie française : espaces insécables et apostrophe courbe."""
    s = s.replace("'", "\u2019")
    s = re.sub(r"(\d) (\d)", "\\1\u00a0\\2", s)
    s = re.sub(r" ([:;€%?!»])", "\u00a0\\1", s)
    s = re.sub(r"(\d) (s|M€|k€|min|ans|mois|personnes|sites)\b", "\\1\u00a0\\2", s)
    return s.replace("« ", "«\u00a0")


class Page:
    def __init__(self, dark=False):
        self.dark = dark
        self.im = Image.new("RGB", (W * S, H * S), INK if dark else PAPER)
        self.d = ImageDraw.Draw(self.im)
        self.ink, self.ink2 = (D_TXT, D_TXT2) if dark else (INK, INK2)
        self.muted, self.rule, self.teal = (D_MUTED, D_RULE, D_TEAL) if dark else (MUTED, RULE, TEAL)

    # --- texte ---
    def width(self, txt, f, track=0):
        return (f.getlength(fr(txt)) + track * S * max(len(txt) - 1, 0)) / S

    def text(self, x, y, txt, f, fill, anchor="ls", track=0):
        txt = fr(txt)
        w = self.width(txt, f, track)
        x = x - w if anchor[0] == "r" else x - w / 2 if anchor[0] == "m" else x
        if not track:
            self.d.text((x * S, y * S), txt, font=f, fill=fill, anchor="l" + anchor[1])
        else:
            cx = x * S
            for ch in txt:
                self.d.text((cx, y * S), ch, font=f, fill=fill, anchor="l" + anchor[1])
                cx += f.getlength(ch) + track * S
        return w

    def wrap(self, txt, f, maxw):
        lines = []
        for par in fr(txt).split("\n"):
            cur = ""
            for word in par.split(" "):
                cand = (cur + " " + word).strip()
                if not cur or self.width(cand, f) <= maxw:
                    cur = cand
                else:
                    lines.append(cur)
                    cur = word
            lines.append(cur)
        return lines

    def para(self, x, y, txt, f, fill, maxw, lh, anchor="ls"):
        for ln in self.wrap(txt, f, maxw):
            self.text(x, y, ln, f, fill, anchor)
            y += lh
        return y

    # --- formes ---
    def line(self, pts, fill, w=1.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=max(1, round(w * S)), joint="curve")

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, w=1.0, r=0):
        self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=fill,
                                 outline=outline, width=max(1, round(w * S)) if outline else 0)

    def circle(self, cx, cy, r, fill=None, outline=None, w=1.0):
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill,
                       outline=outline, width=max(1, round(w * S)) if outline else 0)

    def arc(self, cx, cy, r, a0, a1, fill, w=1.0):
        self.d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], a0, a1, fill=fill, width=max(1, round(w * S)))

    def dashed(self, p0, p1, fill, w=1.0, on=9, off=7):
        (x0, y0), (x1, y1) = p0, p1
        length = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        t = 0
        while t < length:
            e = min(t + on, length)
            self.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * e, y0 + uy * e)], fill, w)
            t += on + off

    def dashed_rect(self, x0, y0, x1, y1, fill, w=1.2):
        for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            self.dashed(a, b, fill, w, 8, 6)

    def arrow(self, p0, p1, fill, w=2.0, head=12, dashed=False):
        (x0, y0), (x1, y1) = p0, p1
        length = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        bx, by = x1 - ux * head, y1 - uy * head
        if dashed:
            self.dashed((x0, y0), (bx, by), fill, w)
        else:
            self.line([(x0, y0), (bx, by)], fill, w)
        px, py, hw = -uy, ux, head * 0.42
        self.d.polygon([(x1 * S, y1 * S), ((bx + px * hw) * S, (by + py * hw) * S),
                        ((bx - px * hw) * S, (by - py * hw) * S)], fill=fill)

    def cross(self, cx, cy, r, fill, w=2.6):
        self.line([(cx - r, cy - r), (cx + r, cy + r)], fill, w)
        self.line([(cx - r, cy + r), (cx + r, cy - r)], fill, w)

    def check(self, cx, cy, r=15):
        self.circle(cx, cy, r, fill=TEAL)
        self.line([(cx - 6.5, cy + 0.5), (cx - 2, cy + 5), (cx + 7, cy - 5)], PAPER, 2.4)


def chrome(p, n, tag, caption):
    p.text(120, 66, f"{n:02d}", MONO(16), p.teal, track=2)
    p.text(162, 66, tag, MONO(16), p.muted, track=3)
    p.text(1800, 66, "RAO · SÉCURITÉ DES INFRASTRUCTURES", MONO(14), p.muted, anchor="rs", track=3)
    p.line([(120, 88), (1800, 88)], p.rule, 0.8)
    p.line([(120, 88), (172, 88)], p.teal, 2.2)
    p.text(120, 1034, caption, MONO(14), p.muted, track=2)
    p.text(1800, 1034, f"{n:02d} / {N}", MONO(14), p.muted, anchor="rs", track=2)


def title(p, txt, lede=None, w=1580):
    p.text(118, 184, txt, SERIF(68), p.ink)
    return p.para(120, 238, lede, SANS(26), p.ink2, w, 37) if lede else 238


# ---------------------------------------------------------------- pictogrammes (boîte 56x56)
def ic_dc(p, x, y, c=TEAL):
    for k in range(3):
        yy = y + 4 + k * 17
        p.rect(x + 4, yy, x + 52, yy + 13, outline=c, w=2, r=2)
        p.circle(x + 44, yy + 6.5, 2.2, fill=c)


def ic_hds(p, x, y, c=TEAL):
    p.circle(x + 28, y + 28, 25, outline=c, w=2)
    p.rect(x + 24, y + 14, x + 32, y + 42, fill=c)
    p.rect(x + 14, y + 24, x + 42, y + 32, fill=c)


def ic_fw(p, x, y, c=TEAL):
    p.rect(x + 4, y + 6, x + 52, y + 54, outline=c, w=2)
    for r in range(1, 4):
        p.line([(x + 4, y + 6 + r * 12), (x + 52, y + 6 + r * 12)], c, 2)
    for r in range(4):
        y0 = y + 6 + r * 12
        for bx in ([x + 28] if r % 2 == 0 else [x + 16, x + 40]):
            p.line([(bx, y0), (bx, y0 + 12)], c, 2)


def ic_tunnel(p, x, y, c=TEAL):
    p.line([(x + 4, y + 15), (x + 52, y + 15)], c, 2)
    p.line([(x + 4, y + 41), (x + 52, y + 41)], c, 2)
    p.dashed((x + 4, y + 28), (x + 18, y + 28), c, 1.6, 4, 4)
    p.dashed((x + 38, y + 28), (x + 52, y + 28), c, 1.6, 4, 4)
    p.circle(x + 28, y + 28, 6, fill=c)


def ic_sdwan(p, x, y, c=TEAL):
    p.line([(x + 13, y + 25), (x + 42, y + 12)], c, 2)
    p.dashed((x + 13, y + 31), (x + 42, y + 44), c, 2, 5, 4)
    p.circle(x + 8, y + 28, 6, fill=c)
    p.circle(x + 48, y + 10, 6, outline=c, w=2)
    p.circle(x + 48, y + 46, 6, outline=c, w=2)


def ic_dmz(p, x, y, c=TEAL):
    p.rect(x + 4, y + 8, x + 52, y + 48, outline=c, w=2)
    p.rect(x + 21, y + 8, x + 35, y + 48, fill=c)


def ic_ztna(p, x, y, c=ORANGE):
    p.line([(x + 13, y + 28), (x + 40, y + 28)], c, 2)
    for k, yy in enumerate((y + 8, y + 28, y + 48)):
        if k == 1:
            p.rect(x + 40, yy - 7, x + 54, yy + 7, fill=c)
        else:
            p.rect(x + 40, yy - 7, x + 54, yy + 7, outline=RULE, w=2)
    p.circle(x + 8, y + 28, 6, fill=c)


def ic_bastion(p, x, y, c=TEAL):
    p.arc(x + 28, y + 20, 14, 180, 360, c, 2)
    p.line([(x + 14, y + 20), (x + 14, y + 54), (x + 42, y + 54), (x + 42, y + 20)], c, 2)
    p.circle(x + 36, y + 39, 2.4, fill=c)
    p.circle(x + 51, y + 7, 4, fill=ORANGE)


# ---------------------------------------------------------------- pages
def p01():
    p = Page(dark=True)
    random.seed(11)
    cols, rows, dx, dy = 53, 10, 32, 18
    pts = [(128 + c * dx, 806 + r * dy) for r in range(rows) for c in range(cols)]
    sieges = {4 * cols + 12, 6 * cols + 38}
    intl = set(random.sample([i for i in range(530) if i not in sieges], 30))
    dcs, ring = [(1580, 268), (1730, 392)], 24

    def end(pt, dc):
        vx, vy = pt[0] - dc[0], pt[1] - dc[1]
        n = math.hypot(vx, vy)
        return dc[0] + vx / n * ring, dc[1] + vy / n * ring

    # 530 sites x 2 datacenters = 1 060 traits
    for sel, col in ((lambda i: i not in sieges and i not in intl, mix(INK, D_TEAL, .2)),
                     (lambda i: i in intl, mix(INK, ORANGE, .45)),
                     (lambda i: i in sieges, mix(INK, D_TXT, .6))):
        for i, pt in enumerate(pts):
            if sel(i):
                for dc in dcs:
                    p.line([pt, end(pt, dc)], col, 0.55)
    for i, (x, y) in enumerate(pts):
        if i in sieges:
            p.circle(x, y, 5.5, fill=D_TXT)
        elif i in intl:
            p.circle(x, y, 3.2, fill=ORANGE)
        else:
            p.circle(x, y, 2.6, fill=D_TEAL)
    for k, (cx, cy) in enumerate(dcs):
        p.circle(cx, cy, 58, outline=D_RULE, w=0.8)
        p.circle(cx, cy, 40, outline=mix(INK, D_TEAL, .35), w=0.8)
        p.circle(cx, cy, ring, fill=INK, outline=D_TXT, w=1.6)
        p.circle(cx, cy, 6, fill=D_TEAL)
        p.text(cx, cy - 74, f"DC{k + 1}", MONO(15), D_TXT2, anchor="ms", track=3)

    p.text(120, 150, "RÉPONSE À APPEL D'OFFRES  ·  MUTUELLE SANTÉ", MONO(17), D_TEAL, track=4)
    p.text(114, 292, "Sécurité des", SERIF(124), D_TXT)
    p.text(114, 410, "infrastructures", SERIF(124), D_TXT)
    p.text(120, 484, "Le projet expliqué simplement,", SANS(32), D_TXT2)
    p.text(120, 528, "pour les sept membres du groupe.", SANS(32), D_TXT2)
    p.text(120, 1034, "530 SITES  ·  2 DATACENTERS  ·  10 000 UTILISATEURS", MONO(14), D_MUTED, track=3)
    p.text(1800, 1034, "NOVEMBRE 2026", MONO(14), D_MUTED, anchor="rs", track=3)
    return p


def p02():
    p = Page()
    chrome(p, 2, "SOMMAIRE", "FIG. 02 — LE PARCOURS DE CE DOCUMENT")
    title(p, "Ce que vous allez comprendre")
    p.text(120, 300, "EN UNE PHRASE", MONO(15), TEAL, track=3)
    p.para(118, 362, "Nous relions 530 sites à deux datacenters sécurisés, nous protégeons chaque accès, et le client paie au mois.",
           SERIF_I(46), INK, 1080, 58)
    stations = [("01", "Le client", "Qui il est, ce qu'il demande, et les mots à connaître.", "P. 03 — 05"),
                ("02", "La solution", "Cinq briques : réseau, datacenters, flux, agences, accès à distance.", "P. 06 — 12"),
                ("03", "Le coût", "Combien, comment c'est payé, et le planning du déploiement.", "P. 13 — 15"),
                ("04", "La preuve", "La maquette qui a testé l'architecture, et ce qui reste à confirmer.", "P. 16 — 17"),
                ("05", "Les rôles", "Qui présente quoi pendant la soutenance, et dans quel ordre.", "P. 18")]
    p.line([(120, 620), (1800, 620)], RULE, 1)
    for i, (num, t, d, pg) in enumerate(stations):
        x = 120 + i * 344
        p.text(x - 2, 584, num, SERIF(56), TEAL)
        p.circle(x + 7, 620, 7, fill=TEAL if i < 4 else ORANGE)
        p.text(x, 690, t, SANS_B(28), INK)
        y = p.para(x, 732, d, SANS(23), INK2, 290, 32)
        p.text(x, max(y, 860) + 10, pg, MONO(15), MUTED, track=2)
    return p


def p03():
    p = Page()
    chrome(p, 3, "LE CLIENT", "FIG. 03 — VOLUMES INDIQUÉS DANS L'APPEL D'OFFRES")
    title(p, "Le client : une grande mutuelle santé",
          "Elle rembourse les frais de santé de ses adhérents. Ses données sont des données de santé : "
          "elles doivent être hébergées chez un hébergeur certifié HDS.")
    for x in (670, 1250):
        p.line([(x, 350), (x, 940)], RULE, 0.8)

    def head(x, big, label):
        p.text(x - 4, 436, big, SERIF(104), INK)
        p.text(x, 476, label, MONO(15), MUTED, track=3)

    def legend(x, y, items):
        for shape, col, txt in items:
            if shape == "dot":
                p.circle(x + 8, y - 8, 7, fill=col)
            elif shape == "ring":
                p.circle(x + 8, y - 8, 7, outline=col, w=2)
            else:
                p.rect(x + 1, y - 15, x + 15, y - 1, fill=col)
            p.text(x + 30, y, txt, SANS(23), INK2)
            y += 36

    x = 120
    head(x, "530", "SITES")
    for i in range(530):
        cx, cy = x + 6 + (i % 30) * 17, 516 + (i // 30) * 17
        if i < 2:
            p.circle(cx, cy, 6, fill=INK)
        else:
            p.circle(cx, cy, 4.2, fill=TEAL if i < 500 else ORANGE)
    legend(x, 866, [("dot", INK, "2 sièges"), ("dot", TEAL, "498 agences en France"), ("dot", ORANGE, "30 agences à l'étranger")])

    x = 700
    head(x, "10 000", "UTILISATEURS")
    for i in range(100):
        sx, sy = x + (i % 10) * 32, 506 + (i // 10) * 32
        p.rect(sx, sy, sx + 24, sy + 24, fill=INK if i < 40 else TEAL if i < 80 else ORANGE)
    p.text(x + 352, 524, "1 CARRÉ =", MONO(14), MUTED, track=2)
    p.text(x + 352, 548, "100 PERSONNES", MONO(14), MUTED, track=2)
    legend(x, 866, [("sq", INK, "4 000 dans les 2 sièges"), ("sq", TEAL, "4 000 dans les agences France"),
                    ("sq", ORANGE, "2 000 dans les agences à l'étranger")])

    x = 1280
    head(x, "100", "PARTENAIRES (ENVIRON)")
    for i in range(100):
        cx, cy = x + 12 + (i % 10) * 32, 518 + (i // 10) * 32
        if i < 40:
            p.circle(cx, cy, 11, fill=TEAL)
        else:
            p.circle(cx, cy, 10, outline=ORANGE, w=2)
    legend(x, 866, [("dot", TEAL, "40 % reliés par un tunnel permanent"), ("ring", ORANGE, "60 % se connectent en nomade")])
    return p


def p04():
    p = Page()
    chrome(p, 4, "LA DEMANDE", "FIG. 04 — CRITÈRES D'ÉVALUATION, PAGE 3 DE L'APPEL D'OFFRES")
    title(p, "Ce que le client va noter", "L'appel d'offres fixe trois critères. Toute notre offre est construite pour y répondre.")
    items = [("1", "Les solutions techniques", "Pour chaque fonction, le modèle d'équipement retenu et la justification du choix.", "VOIR P. 12"),
             ("2", "Les schémas", "Des schémas de principe (HLD) du datacenter et des agences, lisibles d'un coup d'œil.", "VOIR P. 06, 08 ET 10"),
             ("3", "Le coût", "Le coût global, ventilé par poste (housing, WAN, serveurs…), de préférence en abonnement.",
              "VOIR P. 13 ET 14")]
    for x, (n, t, d, ref) in zip((120, 700, 1280), items):
        p.text(x - 8, 506, n, SERIF(210), TEAL)
        p.line([(x, 540), (x + 500, 540)], RULE, 0.8)
        p.text(x, 600, t, SERIF(46), INK)
        p.para(x, 648, d, SANS(25), INK2, 470, 35)
        p.text(x, 798, ref, MONO(15), TEAL, track=3)
    p.rect(120, 850, 1800, 962, fill=PAPER2)
    p.rect(120, 850, 126, 962, fill=ORANGE)
    p.text(160, 898, "Le client l'écrit : sa DSI ne peut pas débloquer une grosse somme d'un coup.", SERIF_I(32), INK)
    p.text(160, 936, "D'où notre offre en abonnement mensuel.", SANS(23), INK2)
    p.line([(1280, 872), (1280, 940)], RULE, 0.8)
    p.text(1312, 896, "BONUS NON DEMANDÉ  ·  P. 16", MONO(15), TEAL, track=3)
    p.text(1312, 934, "Une maquette qui teste nos principes.", SANS(23), INK2)
    return p


def p05():
    p = Page()
    chrome(p, 5, "VOCABULAIRE", "FIG. 05 — GLOSSAIRE COMPLET : docs/GLOSSAIRE.md")
    title(p, "Huit mots pour tout comprendre", "Le vocabulaire qui revient partout dans le projet, expliqué simplement.")
    words = [(ic_dc, "Datacenter", "Bâtiment sécurisé où tournent les serveurs. Nous y louons de la place : c'est le housing."),
             (ic_hds, "HDS", "Certification obligatoire pour héberger des données de santé en France."),
             (ic_fw, "Pare-feu", "Boîtier qui autorise ou bloque chaque échange selon des règles. Ici : FortiGate."),
             (ic_tunnel, "Tunnel IPsec", "Liaison chiffrée à travers Internet : personne ne peut lire ce qui y passe."),
             (ic_sdwan, "SD-WAN", "Réseau qui relie les sites par Internet et change de ligne tout seul en cas de panne."),
             (ic_dmz, "DMZ et WAF", "Zone tampon où sont publiés les sites web ; le WAF y bloque les attaques web."),
             (ic_ztna, "ZTNA", "Accès « zéro confiance » : on ouvre une application, jamais tout le réseau."),
             (ic_bastion, "Bastion", "Porte unique, contrôlée et enregistrée, par laquelle passent les administrateurs.")]
    cw, ch, g = 399, 296, 28
    for i, (icon, word, d) in enumerate(words):
        x, y = 120 + (i % 4) * (cw + g), 318 + (i // 4) * (ch + g)
        p.rect(x, y, x + cw, y + ch, outline=RULE, w=1, r=6)
        icon(p, x + 34, y + 34)
        p.text(x + cw - 30, y + 52, f"{i + 1:02d}", MONO(14), MUTED, anchor="rs", track=2)
        p.text(x + 34, y + 152, word, SERIF(42), INK)
        p.para(x + 34, y + 198, d, SANS(23), INK2, cw - 64, 31)
    return p


def p06():
    p = Page()
    chrome(p, 6, "LA SOLUTION", "FIG. 06 — TRAIT BLEU : TUNNEL CHIFFRÉ · ORANGE : ACCÈS ZÉRO CONFIANCE · POINTILLÉS : PARTENAIRES")
    title(p, "Notre solution en une image",
          "Chaque site a au moins deux accès Internet et des tunnels chiffrés vers les deux datacenters.")
    sites = [("2 sièges", "environ 2 000 personnes chacun", "2 × FORTIGATE 200G"),
             ("498 agences France", "environ 8 personnes chacune", "FORTIGATE 40F-3G4G"),
             ("30 agences à l'étranger", "environ 67 personnes chacune", "2 × FORTIGATE 70G")]
    ys, bh = (318, 478, 638), 124
    dc_mid = (406, 674)
    p.rect(770, 298, 1090, 784, fill=TEAL_L, r=70)
    p.text(930, 334, "INTERNET", MONO(15), TEAL, anchor="ms", track=4)
    p.text(930, 762, "OPÉRATEURS A ET B", MONO(14), TEAL, anchor="ms", track=3)
    # un faisceau par couple site/datacenter, deux traits par faisceau (accès A et B)
    for s, y in enumerate(ys):
        cy = y + bh / 2
        for k, dm in enumerate(dc_mid):
            for off, col in ((-5, TEAL), (5, mix(TEAL, PAPER, .45))):
                p.line([(520, cy + (k - .5) * 34 + off), (1330, dm + (s - 1) * 34 + off)], col, 1.8)
    for y, (t, s, m) in zip(ys, sites):
        p.rect(120, y, 520, y + bh, fill=PAPER, outline=TEAL, w=1.5, r=8)
        p.text(146, y + 44, t, SANS_B(25), INK)
        p.text(146, y + 76, s, SANS(21), INK2)
        p.text(146, y + 106, m, MONO(14), TEAL, track=2)
    for k, (y0, y1) in enumerate(((318, 494), (586, 762))):
        p.rect(1330, y0, 1800, y1, fill=INK, r=8)
        p.text(1360, y0 + 60, f"Datacenter {k + 1}", SERIF(40), D_TXT)
        p.text(1360, y0 + 98, "Région parisienne · certifié HDS", SANS(21), D_TXT2)
        p.text(1360, y0 + 146, "HUB SD-WAN · PARE-FEU · SERVEURS", MONO(14), D_TEAL, track=2)
    p.line([(1556, 494), (1556, 586)], INK, 2)
    p.line([(1572, 494), (1572, 586)], INK, 2)
    p.text(1598, 546, "2 liaisons dédiées", SANS(21), INK2)
    # rangée du bas : accès à distance
    p.rect(120, 832, 520, 940, outline=ORANGE, w=1.5, r=8)
    p.text(146, 876, "Nomades (3 000 + 300)", SANS_B(25), INK)
    p.text(146, 908, "salariés + utilisateurs partenaires", SANS(21), INK2)
    p.rect(770, 832, 1090, 940, fill=ORANGE_L, outline=ORANGE, w=1.5, r=8)
    p.text(930, 876, "FortiSASE (cloud)", SANS_B(25), INK, anchor="ms")
    p.text(930, 908, "ZTNA · MFA · filtrage web", SANS(21), INK2, anchor="ms")
    p.dashed_rect(1330, 832, 1800, 940, TEAL, 1.5)
    p.text(1360, 876, "40 partenaires site à site", SANS_B(25), INK)
    p.text(1360, 908, "tunnel vers la zone partenaire des 2 DC", SANS(21), INK2)
    p.arrow((520, 886), (768, 886), ORANGE, 2.2)
    p.arrow((1090, 868), (1328, 742), ORANGE, 2.2)
    p.arrow((1640, 832), (1640, 764), TEAL, 2, dashed=True)
    return p


def p07():
    p = Page()
    chrome(p, 7, "BRIQUE 1 · LE RÉSEAU", "FIG. 07 — BASCULE MESURÉE SUR LA MAQUETTE LES 16 ET 28/10/2026 : DE 3,2 À 3,8 SECONDES")
    title(p, "Brique 1 · Relier 530 sites par Internet",
          "Un pare-feu FortiGate par site, deux accès Internet et des tunnels chiffrés vers les deux datacenters : c'est le SD-WAN.")
    fib, g4 = (480, 450), (480, 740)
    dc1, dc2 = (760, 360, 960, 450), (760, 740, 960, 830)
    faded = mix(RULE, PAPER, .1)
    # fibre en panne (estompée), 4G active
    p.dashed((310, 570), fib, faded, 2)
    for tgt in ((760, 398), (760, 772)):
        p.dashed(fib, tgt, faded, 2)
    p.line([(310, 620), g4], TEAL, 3)
    for tgt in ((760, 412), (760, 788)):
        p.line([g4, tgt], TEAL, 3)
    p.circle(*fib, 9, fill=PAPER, outline=faded, w=2)
    p.circle(*g4, 9, fill=TEAL)
    p.text(fib[0], fib[1] - 26, "FIBRE", MONO(15), MUTED, anchor="ms", track=3)
    p.text(g4[0], g4[1] + 44, "4G", MONO(15), TEAL, anchor="ms", track=3)
    p.cross(395, 510, 13, ORANGE, 3.4)
    p.text(268, 470, "panne", SERIF_I(30), ORANGE)
    p.rect(120, 540, 310, 650, fill=INK, r=8)
    p.text(146, 590, "Agence", SERIF(36), D_TXT)
    p.text(146, 626, "FORTIGATE", MONO(14), D_TEAL, track=3)
    for (x0, y0, x1, y1), name in ((dc1, "Datacenter 1"), (dc2, "Datacenter 2")):
        p.rect(x0, y0, x1, y1, fill=PAPER, outline=INK, w=1.5, r=8)
        p.text((x0 + x1) / 2, y0 + 54, name, SANS_B(22), INK, anchor="ms")
    p.para(120, 900, "Si la fibre tombe, le FortiGate passe sur la 4G tout seul, sans intervention.", SANS(23), INK2, 840, 32)

    p.line([(1010, 330), (1010, 960)], RULE, 0.8)
    p.text(1054, 476, "3,8 s", SERIF(170), TEAL)
    p.para(1060, 528, "pour basculer sur l'autre accès, mesuré sur notre maquette", SANS(25), INK2, 720, 34)
    cols = (1060, 1330, 1560)
    for x, h in zip(cols, ("PROFIL", "ACCÈS", "ÉQUIPEMENT")):
        p.text(x, 640, h, MONO(14), MUTED, track=3)
    p.line([(1060, 656), (1800, 656)], RULE, 0.8)
    rows = [("Sièges ×2", "2 fibres + 4G/5G", "2 × FortiGate 200G"), ("Agences France ×498", "Fibre + 4G", "FortiGate 40F-3G4G"),
            ("Agences étranger ×30", "2 accès Internet", "2 × FortiGate 70G"), ("Datacenters ×2", "2 transits Internet", "FortiGate 600F (hub)")]
    for i, row in enumerate(rows):
        y = 696 + i * 52
        for x, cell, f in zip(cols, row, (SANS_B(22), SANS(22), SANS(22))):
            p.text(x, y, cell, f, INK)
        p.line([(1060, y + 18), (1800, y + 18)], RULE, 0.6)
    p.para(1060, 938, "Pas de ligne privée (MPLS) : plus chère et plus lente à livrer. La sécurité vient du chiffrement.",
           SANS(22), INK2, 740, 30)
    return p


def p08():
    p = Page()
    chrome(p, 8, "BRIQUE 2 · LES DATACENTERS", "FIG. 08 — SCHÉMA DE PRINCIPE (HLD) DU DATACENTER, IDENTIQUE DANS LES DEUX")
    title(p, "Brique 2 · Deux datacenters identiques",
          "Deux bâtiments certifiés HDS en région parisienne. Si l'un tombe, l'autre redémarre les applications critiques.")
    X0, X1, cx = 120, 1000, 560
    p.dashed_rect(X0, 318, X1, 372, MUTED, 1.2)
    p.text(cx, 351, "INTERNET  ·  2 OPÉRATEURS", MONO(15), MUTED, anchor="ms", track=3)
    layers = [(400, 468, INK, None, "Pare-feu périmètre", "2 × FORTIGATE 600F"),
              (496, 564, ORANGE_L, ORANGE, "DMZ : sites web publiés", "WAF F5 · SFTP"),
              (592, 660, INK, None, "Pare-feu interne", "2 × FORTIGATE 600F")]
    for y0, y1, fill, outl, t, m in layers:
        dark = fill == INK
        p.rect(X0, y0, X1, y1, fill=fill, outline=outl, w=1.5, r=6)
        p.text(148, y0 + 43, t, SANS_B(25), D_TXT if dark else INK)
        p.text(972, y0 + 41, m, MONO(14), D_TEAL if dark else ORANGE, anchor="rs", track=2)
    for y in (372, 468, 564):
        p.arrow((cx, y + 2), (cx, y + 27), INK2, 1.6, 9)
    zones = ("Applications", "Données", "Administration", "Partenaires")
    for i, z in enumerate(zones):
        x = X0 + i * 224
        p.arrow((cx, 662), (x + 104, 686), INK2, 1.4, 9)
        p.rect(x, 688, x + 208, 790, fill=PAPER, outline=TEAL, w=1.5, r=6)
        p.text(x + 104, 746, z, SANS_B(22), INK, anchor="ms")
    p.rect(X0, 818, X1, 888, fill=TEAL_L, r=6)
    p.text(148, 862, "Serveurs : 4 Dell R760, VMware et stockage vSAN", SANS(23), INK)
    p.text(972, 860, "≈ 150 VM PAR DC", MONO(14), TEAL, anchor="rs", track=2)
    p.text(120, 936, "Vers l'autre datacenter : deux liaisons dédiées pour la réplication et la sauvegarde.", SANS(22), INK2)

    p.line([(1040, 330), (1040, 950)], RULE, 0.8)
    blocks = [("HOUSING", "2 baies par datacenter",
               "De la place louée dans deux bâtiments distincts (énergie, opérateurs), certifiés HDS."),
              ("SERVEURS", "8 serveurs, environ 300 machines virtuelles",
               "4 Dell R760 par datacenter, virtualisés avec VMware ; le stockage (vSAN) est intégré aux serveurs."),
              ("SAUVEGARDE", "Une copie que personne ne peut effacer",
               "Veeam sauvegarde vers l'autre datacenter, plus une copie immuable : même un rançongiciel ne peut pas la supprimer.")]
    for k, (tag, t, d) in enumerate(blocks):
        y = 340 + k * 212
        p.text(1080, y, tag, MONO(15), TEAL, track=3)
        p.text(1078, y + 50, t, SERIF(38), INK)
        p.para(1080, y + 92, d, SANS(23), INK2, 720, 32)
    return p


def p09():
    p = Page()
    chrome(p, 9, "BRIQUE 3 · LES FLUX", "FIG. 09 — EXTRAIT DE LA MATRICE : 13 FLUX AUTORISÉS, 9 REFUS TESTÉS (docs/FLUX.md)")
    title(p, "Brique 3 · Tout est interdit, sauf ce qui est écrit",
          "Chaque échange autorisé est listé, justifié et enregistré. Tout le reste est bloqué par défaut.")
    cxs = (510, 690, 870, 1040)
    p.text(120, 372, "DEPUIS ↓   VERS →", MONO(14), MUTED, track=2)
    for cx, h in zip(cxs, ("Serveur web", "Application", "Base de données", "Bastion")):
        p.text(cx, 372, h, SANS_B(21), INK, anchor="ms")
    M = [("Internet", "A", ".", "X", "X"), ("Serveur web", "-", "A", "X", "."), ("Application", ".", "-", "A", "."),
         ("Agence", ".", "A", ".", "."), ("Partenaire", ".", "A", "X", "X")]
    p.line([(120, 400), (1130, 400)], INK2, 1)
    for r, (name, *cells) in enumerate(M):
        cy = 440 + r * 80
        p.text(120, cy + 8, name, SANS(24), INK)
        for cx, c in zip(cxs, cells):
            if c == "A":
                p.check(cx, cy)
            elif c == "X":
                p.cross(cx, cy, 10, ORANGE, 3)
            elif c == ".":
                p.circle(cx, cy, 3.5, fill=mix(MUTED, PAPER, .3))
            else:
                p.line([(cx - 10, cy), (cx + 10, cy)], RULE, 1.5)
        p.line([(120, cy + 40), (1130, cy + 40)], RULE, 0.7)
    lx = 120
    for kind, txt in (("A", "autorisé et enregistré"), ("X", "refusé, testé sur la maquette"), (".", "refusé par défaut")):
        if kind == "A":
            p.check(lx + 12, 866, 12)
        elif kind == "X":
            p.cross(lx + 12, 866, 8, ORANGE, 2.6)
        else:
            p.circle(lx + 12, 866, 3.5, fill=mix(MUTED, PAPER, .3))
        lx += 36 + p.text(lx + 36, 874, txt, SANS(22), INK2) + 54

    p.line([(1190, 330), (1190, 950)], RULE, 0.8)
    for y, tag, t, d in ((340, "NORD / SUD", "Entre Internet et le datacenter",
                          "Pare-feu périmètre, DMZ et WAF : depuis Internet, seuls les sites web publiés sont visibles."),
                         (610, "EST / OUEST", "Entre les zones, à l'intérieur",
                          "Un second pare-feu sépare les zones. Si le serveur web est piraté, l'attaquant n'atteint pas la base de données.")):
        p.text(1230, y, tag, MONO(15), TEAL, track=3)
        p.text(1228, y + 52, t, SERIF(38), INK)
        p.para(1230, y + 96, d, SANS(23), INK2, 570, 32)
    p.text(1230, 930, "Le FTP en clair est remplacé par du SFTP, chiffré.", SANS(22), INK2)
    return p


def building(p, x, base, w, h, n_fg, n_sw, n_wf):
    top = base - h
    p.rect(x, top, x + w, base, outline=INK, w=1.6, r=4)
    cx, cy = x + 20, top + 20
    for k in range(n_fg):
        p.rect(cx + k * 50, cy, cx + k * 50 + 40, cy + 22, fill=TEAL, r=2)
    cy += 36
    per = max(1, int((w - 40 + 8) // 52))
    for k in range(n_sw):
        sx, sy = cx + (k % per) * 52, cy + (k // per) * 18
        p.rect(sx, sy, sx + 44, sy + 10, fill=INK, r=1)
    cy += ((n_sw - 1) // per + 1) * 18 + 14
    per = max(1, int((w - 40) // 16))
    for k in range(n_wf):
        p.circle(cx + 5 + (k % per) * 16, cy + 5 + (k // per) * 16, 5, fill=ORANGE)


def p10():
    p = Page()
    chrome(p, 10, "BRIQUE 4 · LES AGENCES", "FIG. 10 — SCHÉMAS DE PRINCIPE (HLD) DES TROIS PROFILS DE SITE")
    title(p, "Brique 4 · Trois modèles d'agence",
          "Chaque site reçoit un kit standard, déjà configuré et piloté à distance : sur place, il suffit de brancher.")
    profiles = [(120, 220, 150, (1, 1, 1), "Agence France", "×498  ·  ≈ 8 PERSONNES",
                 ["1 pare-feu FortiGate 40F (4G intégrée)", "1 switch Aruba CX 6100", "1 borne Wi-Fi 6E"]),
                (700, 330, 200, (2, 2, 3), "Agence à l'étranger", "×30  ·  ≈ 67 PERSONNES",
                 ["2 pare-feu FortiGate 70G (secours)", "2 switches Aruba CX 6100", "3 bornes Wi-Fi 6E"]),
                (1280, 520, 286, (2, 53, 80), "Siège", "×2  ·  ≈ 2 000 PERSONNES",
                 ["2 pare-feu FortiGate 200G (secours)", "53 switches + 2 switches de cœur", "80 bornes Wi-Fi 6E"])]
    for x, w, h, (fg, sw, wf), t, sub, lines in profiles:
        building(p, x, 620, w, h, fg, sw, wf)
        p.text(x - 2, 682, t, SERIF(40), INK)
        p.text(x, 716, sub, MONO(14), TEAL, track=2)
        for k, (ln, mark) in enumerate(zip(lines, ("fg", "sw", "wf"))):
            y = 764 + k * 34
            if mark == "fg":
                p.rect(x, y - 15, x + 18, y - 5, fill=TEAL, r=1)
            elif mark == "sw":
                p.rect(x, y - 12, x + 18, y - 7, fill=INK)
            else:
                p.circle(x + 9, y - 10, 5, fill=ORANGE)
            p.text(x + 30, y, ln, SANS(23), INK2)
    p.text(120, 884, "DANS CHAQUE SITE, QUATRE RÉSEAUX SÉPARÉS", MONO(14), MUTED, track=3)
    x = 120
    for chip in ("Utilisateurs", "Invités : Internet seulement", "Administration", "Téléphonie et imprimantes"):
        w = p.width(chip, SANS(22)) + 44
        p.rect(x, 902, x + w, 948, outline=INK2, w=1.2, r=23)
        p.text(x + w / 2, 932, chip, SANS(22), INK, anchor="ms")
        x += w + 16
    p.text(x + 12, 932, "Le pare-feu filtre les échanges entre ces réseaux.", SANS(22), INK2)
    return p


def p11():
    p = Page()
    chrome(p, 11, "BRIQUE 5 · LES ACCÈS À DISTANCE", "FIG. 11 — SCHÉMA DE PRINCIPE (HLD) DES ACCÈS DISTANTS")
    title(p, "Brique 5 · Travailler de l'extérieur",
          "On ne donne jamais accès à tout le réseau : seulement à l'application dont la personne a besoin.")
    lanes = [("Salarié nomade", "3 000 personnes", "FortiSASE", "identité, MFA, poste contrôlé", "Ses applications", "et rien d'autre", ORANGE),
             ("Partenaire nomade", "environ 300 personnes", "Portail FortiSASE", "compte limité dans le temps", "L'application prévue", "par le contrat", ORANGE),
             ("Partenaire site à site", "40 entreprises", "Tunnel IPsec", "chiffré et permanent", "La zone partenaire", "des deux datacenters", TEAL),
             ("Infogérant", "administrateur externe", "FortiSASE puis bastion", "chaque session enregistrée", "Les équipements", "sur autorisation", INK)]
    for k, (t1, s1, t2, s2, t3, s3, col) in enumerate(lanes):
        cy = 366 + k * 128
        p.arrow((476, cy), (676, cy), col, 2.2)
        p.arrow((1114, cy), (1316, cy), col, 2.2)
        p.circle(132, cy - 8, 9, fill=col)
        p.text(156, cy - 2, t1, SANS_B(25), INK)
        p.text(156, cy + 28, s1, SANS(21), INK2)
        p.rect(680, cy - 46, 1110, cy + 46, fill=mix(col, PAPER, .9), outline=col, w=1.5, r=46)
        p.text(895, cy - 4, t2, SANS_B(24), INK, anchor="ms")
        p.text(895, cy + 26, s2, SANS(20), INK2, anchor="ms")
        p.rect(1320, cy - 46, 1800, cy + 46, fill=PAPER2, r=8)
        p.text(1348, cy - 4, t3, SANS_B(24), INK)
        p.text(1348, cy + 26, s3, SANS(20), INK2)
    p.line([(120, 846), (1800, 846)], RULE, 0.8)
    p.text(116, 942, "1,99 M€", SERIF(88), ORANGE)
    p.para(470, 898, "bruts évités sur 3 ans. Le ZTNA est compris côté utilisateur dans FortiSASE ; une licence reste à "
                     "ajouter sur les 4 FortiGate hubs (écart net d'au moins 1,5 M€). Pas de Zscaler ZPA en doublon.",
           SANS(25), INK2, 1330, 36)
    return p


def p12():
    p = Page()
    chrome(p, 12, "LES ÉQUIPEMENTS", "FIG. 12 — TABLEAU COMPLET : OFFRE TECHNIQUE, SECTION 15 · PRIX : docs/CHIFFRAGE.md")
    title(p, "Un modèle par fonction, et pourquoi lui",
          "Les quantités viennent de règles simples (un pare-feu par agence, une borne Wi-Fi pour 25 personnes).")
    cols = (120, 560, 960, 1180)
    for x, h in zip(cols, ("FONCTION", "MODÈLE RETENU", "QUANTITÉ", "POURQUOI")):
        p.text(x, 316, h, MONO(14), MUTED, track=3)
    p.line([(120, 332), (1800, 332)], INK2, 1)
    rows = [("Pare-feu agence France", "FortiGate 40F-3G4G", "498", "4G intégrée : un seul boîtier"),
            ("Pare-feu agence à l'étranger", "FortiGate 70G", "60", "en paire : pas de coupure si l'un casse"),
            ("Pare-feu siège", "FortiGate 200G", "4", "6 Gbit/s inspectés pour 2 000 personnes"),
            ("Pare-feu datacenter", "FortiGate 600F", "8", "2 000 tunnels par boîtier, environ 1 100 requis"),
            ("Nomades et ZTNA", "FortiSASE", "3 300", "sécurité et ZTNA dans un seul logiciel"),
            ("Protection des sites web", "F5 Advanced WAF", "4", "un autre éditeur que les pare-feu"),
            ("Bastion d'administration", "WALLIX Bastion", "50 comptes", "éditeur français, sessions enregistrées"),
            ("Switches et Wi-Fi", "Aruba CX 6100 · AP-615", "664 · 748", "une seule console pour tout le réseau local"),
            ("Serveurs", "Dell R760 + VMware", "8", "standard, stockage vSAN inclus"),
            ("Journaux (SIEM)", "Wazuh", "1", "gratuit, les journaux restent en HDS")]
    for i, (a, b, c, d) in enumerate(rows):
        y = 372 + i * 54
        p.text(cols[0], y, a, SANS(23), INK2)
        p.text(cols[1], y, b, SANS_B(23), INK)
        p.text(cols[2], y, c, MONO(19), TEAL)
        p.text(cols[3], y, d, SANS(23), INK2)
        p.line([(120, y + 20), (1800, y + 20)], RULE, 0.6)
    p.text(118, 950, "Fortinet pour toute la sécurité réseau : une politique, une console, un contrat.", SERIF_I(32), INK)
    return p


def p13():
    p = Page(dark=True)
    chrome(p, 13, "LE COÛT", "FIG. 13 — PRIX PUBLICS OU ESTIMÉS, SOURCÉS, À CONFIRMER PAR DEVIS (docs/CHIFFRAGE.md)")
    title(p, "Ce que paie le client")
    p.text(110, 478, "221 424 €", SERIF(200), D_TXT)
    p.text(120, 540, "HT par mois, pendant 36 mois. Rien à payer au départ.", SANS(32), D_TXT2)
    p.line([(1150, 330), (1150, 560)], D_RULE, 0.8)
    for k, (v, lab) in enumerate((("22,14 €", "par utilisateur et par mois"), ("418 €", "par site et par mois"),
                                  ("7,97 M€", "au total sur 3 ans"))):
        y = 386 + k * 84
        p.text(1190, y, v, SERIF(62), D_TEAL)
        p.text(1440, y - 6, lab, SANS(22), D_TXT2)
    segs = [("Sécurité", 64478, D_TEAL), ("Réseau (LAN, Wi-Fi)", 52448, (76, 150, 168)),
            ("Services et infogérance", 44493, (200, 196, 186)), ("Connectivité WAN", 41273, ORANGE),
            ("Serveurs", 14221, (232, 160, 120)), ("Housing", 4511, (120, 132, 150))]
    total = sum(v for _, v, _ in segs)
    assert total == 221424
    p.text(120, 668, "RÉPARTITION DE LA MENSUALITÉ", MONO(14), D_MUTED, track=3)
    x = 120.0
    for _, v, col in segs:
        w = 1680 * v / total
        p.rect(x, 690, x + w - 3, 744, fill=col)
        x += w
    for i, (name, v, col) in enumerate(segs):
        lx = 120 + i * 280
        p.rect(lx, 786, lx + 14, 800, fill=col)
        p.text(lx + 26, 801, name, SANS(20), D_TXT)
        p.text(lx + 26, 832, f"{v:,} €/MOIS".replace(",", " "), MONO(15), D_MUTED, track=1)
    p.text(120, 936, "La sécurité et le réseau pèsent le plus : 570 pare-feu, 664 switches et 748 bornes Wi-Fi.", SANS(24), D_TXT2)
    return p


def p14():
    p = Page()
    chrome(p, 14, "LE COÛT", "FIG. 14 — MÊME ÉCHELLE POUR LES DEUX LIGNES · LOCATION FINANCIÈRE À 7 %/AN (HYPOTHÈSE)")
    title(p, "Pourquoi l'abonnement ?",
          "Acheter coûterait un peu moins cher au total, mais il faudrait avancer 4,22 M€ le premier jour. La DSI du client ne le peut pas.")
    x0, pitch, bw, sc = 520, 28, 18, 250 / 4219196
    rows = [(610, "Acheter", ("4,22 M€ le premier jour,", "puis 91 k€ par mois"), "7,50 M€",
             lambda i: 4219196 if i == 0 else 91147, INK2),
            (830, "En abonnement", ("0 € le premier jour,", "puis 221 k€ par mois"), "7,97 M€",
             lambda i: 0 if i == 0 else 221424, TEAL)]
    for base, name, (s1, s2), tot, val, col in rows:
        p.line([(x0 - 8, base), (x0 + 36 * pitch + bw + 8, base)], RULE, 1)
        for i in range(37):
            h = val(i) * sc
            if h:
                p.rect(x0 + i * pitch, base - h, x0 + i * pitch + bw, base, fill=ORANGE if (i == 0 and col == INK2) else col)
        p.text(118, base - 50, name, SERIF(44), INK)
        p.text(120, base - 12, s1, SANS(22), INK2)
        p.text(120, base + 18, s2, SANS(22), INK2)
        p.text(1800, base - 10, tot, SERIF(56), INK, anchor="rs")
        p.text(1800, base + 22, "TOTAL SUR 3 ANS", MONO(14), MUTED, anchor="rs", track=2)
    p.text(x0 + bw / 2, 610 - 250 - 14, "4,22 M€", MONO(15), ORANGE, anchor="ms", track=1)
    for m in (0, 12, 24, 36):
        p.text(x0 + m * pitch + bw / 2, 870, f"M{m}", MONO(14), MUTED, anchor="ms", track=1)
    p.text(120, 944, "L'écart, 0,47 M€, est le prix de l'étalement : ce sont les intérêts de la location sur 36 mois.", SANS(26), INK)
    return p


def p15():
    p = Page()
    chrome(p, 15, "LE PLANNING", "FIG. 15 — PHASAGE DU DÉPLOIEMENT, OFFRE TECHNIQUE SECTION 17")
    title(p, "Le déploiement en 9 mois",
          "D'abord le cœur (les datacenters), puis un pilote, puis les agences par vagues.")
    ax0, ax1 = 600, 1800
    u = (ax1 - ax0) / 9
    for m in range(10):
        x = ax0 + m * u
        p.line([(x, 344), (x, 860)], RULE, 0.6)
        p.text(x, 330, f"M{m}", MONO(14), MUTED, anchor="ms", track=1)
    phases = [("Socle", "datacenters, serveurs, bastion, SIEM", 0, 2, TEAL),
              ("Sièges et pilote", "2 sièges et 10 agences tests", 2, 3, TEAL),
              ("Agences France", "environ 25 agences par semaine", 3, 8, TEAL),
              ("Agences à l'étranger", "30 agences, opérateurs locaux", 6, 9, TEAL),
              ("Nomades et partenaires", "par vagues successives", 3, 9, ORANGE)]
    for k, (t, s, a, b, col) in enumerate(phases):
        cy = 404 + k * 100
        p.text(120, cy - 2, t, SANS_B(25), INK)
        p.text(120, cy + 28, s, SANS(21), INK2)
        p.rect(ax0 + a * u + 3, cy - 18, ax0 + b * u - 3, cy + 18, fill=col, r=18)
        p.text(ax0 + (a + b) / 2 * u, cy + 6, f"M{a} – M{b}", MONO(14), PAPER, anchor="ms", track=1)
    p.para(120, 930, "Chaque agence reçoit son matériel déjà configuré à partir du modèle de son profil : sur place, il suffit de brancher.",
           SANS(24), INK2, 1680, 34)
    return p


def p16():
    p = Page()
    chrome(p, 16, "LA PREUVE", "FIG. 16 — PREUVES HORODATÉES : evidence/20261028T200408Z/ · DÉMO : docs/DEMO_EVE.md")
    title(p, "La preuve : nous l'avons construite en petit",
          "Une maquette de 15 machines, sur un serveur Proxmox avec EVE-NG, reproduit l'architecture et la teste automatiquement.")
    link = mix(INK2, PAPER, .4)
    nodes = {"dc1": (150, 470, 370, 530, "pare-feu DC1"), "dc2": (150, 744, 370, 804, "pare-feu DC2"),
             "hq": (830, 384, 1090, 444, "routeur siège"), "ag": (830, 592, 1090, 652, "routeur agence"),
             "pa": (830, 800, 1090, 860, "routeur partenaire")}
    opa, opb = (610, 520), (610, 750)
    mid = lambda k, side: ((nodes[k][2] if side == "r" else nodes[k][0]), (nodes[k][1] + nodes[k][3]) / 2)
    for k in ("dc1", "dc2"):
        p.line([mid(k, "r"), opa], link, 1.4)
        p.line([mid(k, "r"), opb], link, 1.4)
    for k in ("hq", "ag"):
        p.line([mid(k, "l"), opa], link, 1.4)
        p.line([mid(k, "l"), opb], link, 1.4)
    p.line([mid("pa", "l"), opa], link, 1.4)
    p.line([opa, opb], link, 1.4)
    for k in ("hq", "ag", "pa"):
        p.dashed(mid("dc1", "r"), mid(k, "l"), TEAL, 2.2, 10, 7)
    p.dashed((260, 530), (260, 744), TEAL, 2.2, 10, 7)
    for c, lab in ((opa, "Op. A"), (opb, "Op. B")):
        p.circle(*c, 44, fill=PAPER2, outline=INK2, w=1.4)
        p.text(c[0], c[1] + 8, lab, SANS_B(21), INK, anchor="ms")
    for k, (x0, y0, x1, y1, lab) in nodes.items():
        p.rect(x0, y0, x1, y1, fill=INK, r=8)
        p.text((x0 + x1) / 2, y0 + 38, lab, SANS(21), D_TXT, anchor="ms")
    p.text(150, 340, "5 serveurs : web, appli, base, bastion, journaux", SANS(20), INK2)
    for i in range(5):
        sx = 160 + i * 44
        p.rect(sx, 364, sx + 30, 394, outline=TEAL, w=1.6, r=3)
        p.line([(sx + 15, 394), (sx + 15 + (260 - sx - 15) * .35, 470)], RULE, 1)
    p.text(830, 688, "+ un poste et un invité", SANS(20), INK2)
    p.dashed((120, 930), (170, 930), TEAL, 2.2, 10, 7)
    p.text(184, 937, "tunnel IPsec chiffré", SANS(21), INK2)
    p.line([(430, 930), (480, 930)], link, 1.4)
    p.text(494, 937, "câble", SANS(21), INK2)

    p.line([(1150, 330), (1150, 960)], RULE, 0.8)
    p.text(1190, 462, "17 / 17", SERIF(150), TEAL)
    p.para(1196, 512, "tests réussis : 10\u00a0échanges autorisés passent, 7\u00a0échanges interdits sont bloqués.", SANS(24), INK2, 600, 34)
    p.text(1192, 688, "3 à 4 s", SERIF(96), INK)
    p.para(1196, 732, "de coupure quand on débranche une ligne, puis retour automatique.", SANS(24), INK2, 600, 34)
    p.rect(1190, 824, 1800, 950, fill=PAPER2, r=6)
    p.rect(1190, 824, 1196, 950, fill=TEAL)
    p.para(1222, 870, "Elle prouve les principes, pas les produits : des routeurs Linux y jouent le rôle des FortiGate.",
           SANS(23), INK, 550, 32)
    return p


def p17():
    p = Page()
    chrome(p, 17, "LES LIMITES", "FIG. 17 — DÉTAIL : OFFRE TECHNIQUE, SECTIONS 16.4, 18 ET 19")
    title(p, "Ce qui reste à confirmer",
          "Une bonne offre dit aussi ce qu'elle ne sait pas encore. Le jury posera ces questions : voici nos réponses.")
    cards = [("Les prix", "Prix publics ou estimés, tous sourcés. Ils seront confirmés par devis."),
             ("Les pertes acceptables", "Combien de données on peut perdre (RPO) et combien de temps couper (RTO) : à fixer avec le client."),
             ("La perte d'un datacenter", "Le datacenter restant redémarre seulement les applications critiques, pas tout."),
             ("HDS et DORA", "Les règles santé et finance s'appliquent ; leur périmètre exact est à confirmer avec le client."),
             ("Les sièges", "Avec 53 switches par siège, un étage réseau intermédiaire reste à dimensionner."),
             ("La maquette", "Elle valide les principes, pas la tenue en charge ni les vrais produits.")]
    for i, (t, d) in enumerate(cards):
        x, y = 120 + (i % 3) * 580, 330 + (i // 3) * 296
        p.line([(x, y), (x + 520, y)], RULE, 0.8)
        p.line([(x, y), (x + 48, y)], TEAL, 2.4)
        p.text(x, y + 46, f"{i + 1:02d}", MONO(15), TEAL, track=2)
        p.text(x - 2, y + 104, t, SERIF(40), INK)
        p.para(x, y + 148, d, SANS(23), INK2, 490, 32)
    p.text(120, 948, "Hors offre : SOC 24 h/24, protection DDoS (en option), optiques et câbles, onduleurs en agence.", SANS(22), MUTED)
    return p


def p18():
    p = Page()
    chrome(p, 18, "LES RÔLES", "FIG. 18 — LES DIAPOS CITÉES SONT CELLES DU DIAPORAMA DE SOUTENANCE (24 DIAPOSITIVES)")
    title(p, "Sept rôles, sept prénoms",
          "Chaque rôle présente un bloc, dans cet ordre, et répond aux questions du jury sur son domaine.")
    roles = [("Farah", "Chef de projet", "l'équipe, la synthèse, le besoin du client et la conclusion", "à l'aise à l'oral, vision d'ensemble", "≈ 3 MIN 30 · DIAPOS 1–4, 24"),
             ("Valentin", "Architecte SD-WAN", "le schéma global, le SD-WAN et la démo de la maquette", "aime le réseau et la démonstration", "≈ 2 MIN 30 + DÉMO · DIAPOS 5, 6, 22"),
             ("Nolan", "Architecte datacenter", "le housing, les serveurs et le schéma du datacenter", "systèmes, serveurs, sauvegarde", "≈ 2 MIN 30 · DIAPOS 7–9"),
             ("Fatih", "Sécurité des flux", "nord/sud, est/ouest et l'administration à distance", "goût pour la cybersécurité", "≈ 2 MIN 30 · DIAPOS 10–12"),
             ("Younes", "Exploitation et agences", "le schéma des agences, l'exploitation et les risques", "méthode, terrain, réglementation", "≈ 2 MIN 30 · DIAPOS 13, 14, 23"),
             ("Maxime", "Zero Trust (ZTNA)", "nomades, partenaires, accès à distance et choix du ZTNA", "goût des approches récentes", "≈ 3 MIN 20 · DIAPOS 15–18"),
             ("Diane", "Finances", "les modèles retenus, les coûts et le planning", "à l'aise avec les chiffres", "≈ 2 MIN 30 · DIAPOS 19–21")]
    cw, ch, g = 402, 330, 18
    for i in range(8):
        x, y = 120 + (i % 4) * (cw + 24), 298 + (i // 4) * (ch + g)
        if i == 7:
            p.rect(x, y, x + cw, y + ch, fill=INK, r=6)
            p.text(x + 28, y + 40, "MODE D'EMPLOI", MONO(15), D_TEAL, track=3)
            yy = y + 86
            for ln in ("1. Lisez ce document en entier.", "2. Repérez votre rôle et vos diapositives.",
                       "3. Lisez votre fiche détaillée :"):
                yy = p.para(x + 28, yy, ln, SANS(21), D_TXT, cw - 56, 29) + 8
            p.text(x + 28, yy - 4, "docs/ROLES_SOUTENANCE.md", MONO(15), D_TEAL)
            p.para(x + 28, yy + 38, "4. Répétition chronométrée, puis questions croisées.", SANS(21), D_TXT, cw - 56, 29)
            continue
        nom, name, pres, prof, meta = roles[i]
        p.rect(x, y, x + cw, y + ch, outline=RULE, w=1, r=6)
        p.text(x + 28, y + 40, f"RÔLE {i + 1:02d}", MONO(15), TEAL, track=3)
        p.text(x + 26, y + 86, name, SERIF(34), INK)
        p.text(x + 28, y + 124, "PRÉSENTE", MONO(13), MUTED, track=3)
        p.para(x + 28, y + 152, pres, SANS(21), INK2, cw - 56, 28)
        p.text(x + 28, y + 216, "PROFIL", MONO(13), MUTED, track=3)
        p.text(x + 28, y + 244, prof, SANS(21), INK2)
        p.text(x + 28, y + 278, meta, MONO(13), TEAL, track=1)
        p.text(x + 28, y + 312, "PRÉNOM", MONO(13), MUTED, track=3)
        p.text(x + 112, y + 310, nom, SANS_B(22), INK)
        p.line([(x + 110, y + 316), (x + cw - 28, y + 316)], RULE, 1)
    return p


PAGES = [p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18]
assert len(PAGES) == N


def main():
    out_pdf = Path(sys.argv[1])
    only = {int(a) for a in sys.argv[2:]}
    PREV.mkdir(exist_ok=True)
    imgs = []
    for i, fn in enumerate(PAGES, 1):
        if only and i not in only:
            continue
        img = fn().im.resize(OUT, Image.LANCZOS)
        img.resize((1600, 900), Image.LANCZOS).save(PREV / f"page{i:02d}.png")
        imgs.append(img)
    if not only:
        imgs[0].save(out_pdf, save_all=True, append_images=imgs[1:], resolution=192, quality=94)
        print("PDF :", out_pdf)


if __name__ == "__main__":
    main()
