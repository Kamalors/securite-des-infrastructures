# -*- coding: utf-8 -*-
"""Rendu des scènes de la vidéo RAO (style « Topologie silencieuse », mêmes polices et couleurs que la présentation).
Chaque scène produit une image par état de révélation : état k = les k premiers items visibles."""
import math
import random
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image

SCRATCH = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRATCH))
import generer as g  # noqa: E402

g.S = 2  # rendu 3840x2160 puis réduction : anticrénelage suffisant et deux fois plus rapide
from generer import (D_MUTED, D_RULE, D_TEAL, D_TXT, D_TXT2, INK, INK2, MONO, ORANGE, PAPER,  # noqa: E402
                     RULE, SANS, SANS_B, SERIF, TEAL, Page, mix)

# gris des repères assombri pour la vidéo : contraste 4,7:1 sur le papier (au lieu de 3,4:1)
g.MUTED = MUTED = (104, 108, 117)

# séparateurs « · » aérés : l'espace d'Instrument Sans est étroite. Deux espaces de chaque côté ; la coupure
# possible reste juste après le point, et l'insécable qui suit est au début du mot suivant (wrap() efface
# les insécables en fin de ligne provisoire, ce qui rendait le séparateur asymétrique).
_FR = g.fr
g.fr = lambda s: _FR(s).replace(" · ", "  ·  ")

W, H = 1920, 1080

# ------------------------------------------------------------------ repli des glyphes absents
# Instrument Serif et Instrument Sans n'ont ni « ≈ » ni « ≥ » : ces caractères sont dessinés avec IBM Plex Mono.
_ORIG_TEXT = g.Page.text
_NOTDEF, _HAS, _MONO = {}, {}, {}


def _has(f, ch):
    key = (f.path, f.size, ch)
    if key not in _HAS:
        if ch.isspace():
            _HAS[key] = True
        else:
            # référence : le glyphe « absent » (.notdef), obtenu avec un caractère de la zone privée
            nd = _NOTDEF.setdefault((f.path, f.size), (f.getmask("").size, bytes(list(f.getmask("")))))
            m = f.getmask(ch)
            _HAS[key] = (m.size, bytes(list(m))) != nd
    return _HAS[key]


def _mono(f):
    return _MONO.setdefault(f.size, g.ImageFont.truetype(str(g.FONTS / "IBMPlexMono-Regular.ttf"), f.size))


def _text(self, x, y, txt, f, fill, anchor="ls", track=0):
    txt = g.fr(txt)
    if track or "Mono" in getattr(f, "path", "") or all(_has(f, c) for c in txt):
        return _ORIG_TEXT(self, x, y, txt, f, fill, anchor, track)
    runs, cur, cur_f = [], "", None
    for c in txt:
        fc = f if _has(f, c) else _mono(f)
        if fc is not cur_f and cur:
            runs.append((cur, cur_f))
            cur = ""
        cur, cur_f = cur + c, fc
    runs.append((cur, cur_f))
    w = sum(rf.getlength(r) for r, rf in runs) / g.S
    x = x - w if anchor[0] == "r" else x - w / 2 if anchor[0] == "m" else x
    for r, rf in runs:
        _ORIG_TEXT(self, x, y, r, rf, fill, "l" + anchor[1])
        x += rf.getlength(r) / g.S
    return w


g.Page.text = _text
BOTTOM = 965                    # bas de la zone de contenu : la bande du dessous reste libre pour les sous-titres
PROGRESS_Y = 88                 # repères de chapitres et barre de progression, en haut de l'image
EQUIPE = ["Farah", "Valentin", "Nolan", "Fatih", "Younes", "Maxime", "Diane"]
RETOURS = [("Valentin", "démo"), ("Younes", "risques"), ("Farah", "conclusion")]
NOMS_PROPRES = {"Gartner", "Fortinet", "FortiGate", "FortiSASE", "Linux", "Wazuh", "Aruba", *EQUIPE}


def suite(detail):
    """Début de détail en minuscule après « — », sauf sigle ou nom propre."""
    if len(detail) > 1 and detail[0].isupper() and (detail[1].islower() or detail[1] in "'’") \
            and detail.split(" ", 1)[0] not in NOMS_PROPRES:
        return detail[0].lower() + detail[1:]
    return detail


def to_rgb(p):
    return p.im.resize((W, H), Image.LANCZOS)


def fit_lines(p, txt, font_fn, size, maxw, max_lines, min_size):
    """Réduit la taille jusqu'à tenir en max_lines lignes."""
    while True:
        f = font_fn(size)
        lines = p.wrap(txt, f, maxw)
        if len(lines) <= max_lines or size <= min_size:
            return f, lines[:max_lines] if size <= min_size else lines, size
        size -= 1


def voiler(p, rects, a=0.62):
    """Voile couleur de fond sur les zones que la voix ne commente pas : l'œil suit le commentaire."""
    fond = INK if p.dark else PAPER
    for x0, y0, x1, y1 in rects:
        box = tuple(round(v * g.S) for v in (x0, y0, x1, y1))
        zone = p.im.crop(box)
        p.im.paste(Image.blend(zone, Image.new("RGB", zone.size, fond), a), box)


def chrome(p, sections, current):
    """Chapitres en haut : le chapitre en cours est en couleur ; la barre de progression est tracée image par image."""
    teal, muted, rule = (D_TEAL, D_MUTED, D_RULE) if p.dark else (TEAL, MUTED, RULE)
    p.line([(120, PROGRESS_Y), (1800, PROGRESS_Y)], rule, 1.2)
    n = len(sections)
    for i, s in enumerate(sections):
        x = 120 + i * 1680 / n
        p.line([(x, PROGRESS_Y - 6), (x, PROGRESS_Y + 6)], rule, 1.2)
        p.text(x + 10, PROGRESS_Y - 16, s.upper(), MONO(16), teal if s == current else muted, track=2)


def title_block(p, scene):
    """Même titre et même chapeau que les pages reprises du PDF (generer.title) : rien ne saute d'une scène à l'autre."""
    f, lines, _ = fit_lines(p, scene["title"], SERIF, 68, 1640, 1, 50)
    p.text(118, 184, lines[0], f, INK)
    y = 184
    if scene.get("subtitle"):
        y = p.para(120, 238, scene["subtitle"], SANS(26), INK2, 1580, 37) - 37
    return y + 70


def marker(p, x, y, n, col):
    p.circle(x, y, 19, fill=col)
    p.text(x, y + 1, str(n), MONO(16), PAPER, anchor="mm")


def _is_question(it):
    t = it.get("label", "").strip().lower()
    return t.endswith("?") or any(m in t for m in ("question", "jury", "vigilance", "limite", "corriger"))


def item_rows(p, items, k, x0, y0, y1, width, accent, numbered=True, label_size=None, detail_size=None):
    """Liste verticale d'items : les k premiers à l'encre, les suivants en fantôme (libellé seul) pour annoncer la suite."""
    if not items:
        return
    n = len(items)
    if label_size is None:
        label_size, detail_size = (44, 34) if n <= 3 else (40, 32) if n == 4 else (38, 31)
    rows = []
    for it in items:
        lab_f, lab_lines, _ = fit_lines(p, it["label"], SANS_B, label_size, width - 80, 2, 24)
        det_lines = p.wrap(it.get("detail", ""), SANS(detail_size), width - 80)[:3] if it.get("detail") else []
        h = len(lab_lines) * (label_size + 10) + len(det_lines) * (detail_size + 9)
        rows.append((lab_f, lab_lines, det_lines, h))
    total = sum(r[3] for r in rows)
    gap = max(18, min(46, (y1 - y0 - total) / max(1, n - 1))) if n > 1 else 0
    y = y0
    for i, (it, (lab_f, lab_lines, det_lines, h)) in enumerate(zip(items, rows)):
        vis = i < k
        col = (ORANGE if _is_question(it) else TEAL) if accent == "auto" else accent
        if not vis:
            col = RULE
        if numbered:  # pastille centrée sur les capitales du libellé
            marker(p, x0 + 19, y + 0.62 * label_size - 4, i + 1, col)
        else:
            p.rect(x0, y - 6, x0 + 5, y + h - 14, fill=col)
        tx = x0 + (64 if numbered else 30)
        yy = y + label_size - 4
        for ln in lab_lines:
            p.text(tx, yy, ln, lab_f, INK if vis else RULE)
            yy += label_size + 10
        if vis:
            for ln in det_lines:
                p.text(tx, yy + 2, ln, SANS(detail_size), INK2)
                yy += detail_size + 9
            if it.get("value"):
                p.text(x0 + width, y + label_size - 2, it["value"], SERIF(44), col, anchor="rs")
        y += h + gap


# ------------------------------------------------------------------ mises en page
def lay_ouverture(scene, k, ctx):
    p = Page(dark=True)
    random.seed(11)
    cols, rows, dx, dy = 53, 10, 32, 18
    pts = [(128 + c * dx, 798 + r * dy) for r in range(rows) for c in range(cols)]  # dernière rangée au-dessus de y=965
    sieges = {4 * cols + 12, 6 * cols + 38}
    intl = set(random.sample([i for i in range(530) if i not in sieges], 30))
    dcs, ring = [(1580, 300), (1730, 424)], 24

    def end(pt, dc):
        vx, vy = pt[0] - dc[0], pt[1] - dc[1]
        n = math.hypot(vx, vy)
        return dc[0] + vx / n * ring, dc[1] + vy / n * ring

    for sel, col in ((lambda i: i not in sieges and i not in intl, mix(INK, D_TEAL, .2)),
                     (lambda i: i in intl, mix(INK, ORANGE, .45)),
                     (lambda i: i in sieges, mix(INK, D_TXT, .6))):
        for i, pt in enumerate(pts):
            if sel(i):
                for dc in dcs:
                    p.line([pt, end(pt, dc)], col, 0.55)
    for i, (x, y) in enumerate(pts):
        p.circle(x, y, 5.5 if i in sieges else 3.2 if i in intl else 2.6,
                 fill=D_TXT if i in sieges else ORANGE if i in intl else D_TEAL)
    for kk, (cx, cy) in enumerate(dcs):
        p.circle(cx, cy, 58, outline=D_RULE, w=0.8)
        p.circle(cx, cy, 40, outline=mix(INK, D_TEAL, .35), w=0.8)
        p.circle(cx, cy, ring, fill=INK, outline=D_TXT, w=1.6)
        p.circle(cx, cy, 6, fill=D_TEAL)
        p.text(cx, cy - 74, f"DC{kk + 1}", MONO(16), D_TXT2, anchor="ms", track=3)
    p.text(120, 168, "RÉPONSE À APPEL D'OFFRES  ·  MUTUELLE SANTÉ", MONO(17), D_TEAL, track=4)
    f, lines, size = fit_lines(p, scene["title"], SERIF, 112, 1300, 2, 72)
    y = 300
    for ln in lines:
        p.text(114, y, ln, f, D_TXT)
        y += size * 1.0
    if scene.get("subtitle"):
        p.para(120, y + 30, scene["subtitle"], SANS(32), D_TXT2, 1040, 44)
    p.text(120, 772, "Chaque point est un site, relié à DC1 et DC2 ; en orange, les 30 agences à l'étranger ; "
                     "en blanc, les 2 sièges.", SANS(20), D_TXT2)
    return p


def lay_texte(scene, k, ctx, accent="auto", numbered=True):
    p = Page()
    y0 = title_block(p, scene)
    item_rows(p, scene["items"], k, 120, max(y0, 300), BOTTOM - 20, 1680, accent, numbered)
    return p


def lay_problemes(scene, k, ctx):
    return lay_texte(scene, k, ctx, accent=ORANGE)


def lay_chiffres(scene, k, ctx):
    p = Page()
    y0 = max(title_block(p, scene), 420)
    items = scene["items"][:4]
    n = max(1, len(items))
    gap = 60
    cw = (1680 - gap * (n - 1)) / n
    for i, it in enumerate(items):
        vis = i < k
        x = 120 + i * (cw + gap)
        p.line([(x, y0), (x + cw, y0)], RULE, 1)
        val = it.get("value") or it["label"]
        vf, vl, vs = fit_lines(p, val, SERIF, 140 if n <= 3 else 110, cw - 10, 1, 60)
        p.text(x - 4, y0 + 40 + vs * 0.9, vl[0], vf, TEAL if vis else RULE)
        if not vis:
            continue
        p.line([(x, y0), (x + 56, y0)], TEAL, 2.6)
        yy = p.para(x, y0 + 92 + vs, it["label"] if it.get("value") else "", SANS_B(30), INK, cw - 10, 40)
        if it.get("detail"):
            p.para(x, yy + 8, it["detail"], SANS(25), INK2, cw - 10, 35)
    return p


# Pages du PDF reprises telles quelles, sans leurs renvois aux autres pages du PDF.
REMPLACE = {"BONUS NON DEMANDÉ  ·  P. 16": "BONUS NON DEMANDÉ"}
# Voiles par page reprise et par état : zones (x0, y0, x1, y1) que la voix ne commente pas encore ou plus.
# Page 6 : les rectangles se touchent sans se chevaucher ; les deux datacenters restent visibles quand on parle
# des nomades et des partenaires, qui arrivent dans les deux.
_BAS = (110, 796, 1810, 952)
_FLECHES = [(1092, 738, 1328, 796), (1628, 763, 1652, 796)]   # haut de la flèche orange, haut de la flèche pointillée
VOILES = {
    4: {1: [(660, 320, 1810, 815), (110, 842, 1810, 970)],
        2: [(100, 320, 660, 815), (1240, 320, 1810, 815), (110, 842, 1810, 970)],
        3: [(100, 320, 1240, 815), (1272, 842, 1810, 970)]},
    6: {0: [(523, 290, 1328, 796), _BAS, _FLECHES[1]],
        1: [_BAS, *_FLECHES],
        2: [_BAS, *_FLECHES],
        3: [(110, 290, 1328, 738), (110, 738, 1092, 796), (1326, 766, 1810, 952)],
        4: [(110, 290, 1328, 738), (110, 738, 1092, 796), (1326, 766, 1810, 952)],
        5: [(110, 290, 1326, 952)]},
}


def lay_schema(scene, k, ctx):
    page = scene.get("reuse_page") or 6
    fn = getattr(g, f"p{page:02d}")
    old_chrome, old_text, old_mono = g.chrome, g.Page.text, g.MONO
    g.chrome = lambda *a, **kw: None  # la page sans son en-tête ni son pied : la vidéo a les siens
    g.MONO = lambda s: old_mono(max(s, 16))  # étiquettes lisibles sur un portable

    def filtre(self, x, y, txt, f, fill, anchor="ls", track=0):
        if txt.startswith("VOIR P."):
            return 0
        return old_text(self, x, y, REMPLACE.get(txt, txt), f, fill, anchor, track)

    g.Page.text = filtre
    try:
        p = fn()
    finally:
        g.chrome, g.Page.text, g.MONO = old_chrome, old_text, old_mono
    voiler(p, VOILES.get(page, {}).get(k, []))
    items = scene.get("items") or []
    if items and k > 0:  # légende à la place du chapeau de la page
        it = items[min(k, len(items)) - 1]
        p.rect(110, 205, 1810, 252, fill=PAPER)
        w = p.text(120, 238, it["label"], SANS_B(26), ORANGE if it.get("accent") == "orange" else TEAL)
        if it.get("detail"):
            p.text(120 + w, 238, " — " + suite(it["detail"]), SANS(26), INK2)
    return p


VW, VH = 420, 236


@lru_cache(None)
def vignette(page):
    """Page du PDF explicatif réduite, à l'échelle du canevas (g.S)."""
    return getattr(g, f"p{page:02d}")().im.resize((VW * g.S, VH * g.S), Image.LANCZOS)


def lay_personne(scene, k, ctx):
    p = Page()
    per = scene["person"]
    order, nom = int(per.get("order", 1)), per["name"]
    # colonne gauche : identité, diapos, durée
    p.text(120, 196, f"RÔLE {order:02d} SUR 7", MONO(16), TEAL, track=3)
    nf, nl, _ = fit_lines(p, nom, SERIF, 120, 560, 1, 70)
    p.text(114, 318, nl[0], nf, INK)
    y = p.para(120, 374, per["role"], SANS_B(32), TEAL, 560, 40)
    p.text(120, y + 26, per.get("slides", ""), SANS_B(24), INK2)
    p.text(120, y + 60, per.get("duration", ""), SANS(24), INK2)
    # frise des sept rôles, puis les retours de fin de parcours
    fx0, fx1, fy = 140, 640, y + 160
    p.text(120, fy - 44, "ORDRE DE PASSAGE", MONO(16), MUTED, track=3)
    p.line([(fx0, fy), (fx1, fy)], RULE, 1.4)
    for i, n in enumerate(EQUIPE):
        x = fx0 + i * (fx1 - fx0) / 6
        if i + 1 == order:
            p.circle(x, fy, 18, fill=TEAL)
            p.text(x, fy + 1, str(i + 1), MONO(15), PAPER, anchor="mm")
            p.text(x, fy + 46, n, SANS_B(19), TEAL, anchor="ms")
        else:
            p.circle(x, fy, 14, fill=INK2)
            p.text(x, fy + 1, str(i + 1), MONO(14), PAPER, anchor="mm")
            p.text(x, fy + 46, n, SANS(17), MUTED, anchor="ms")
    x, yy = 120, fy + 92
    x += p.text(x, yy, "Puis : ", SANS(18), INK2)
    for j, (n, quoi) in enumerate(RETOURS):
        x += p.text(x, yy, n, SANS_B(18) if n == nom else SANS(18), TEAL if n == nom else INK2)
        x += p.text(x, yy, f" ({quoi})" + ("  →  " if j < len(RETOURS) - 1 else ""), SANS(18), INK2)
    if per.get("page"):  # la page du PDF explicatif qui détaille ce rôle
        yv = fy + 132
        p.text(120, yv, f"presentation/RAO_projet_explique.pdf, page {per['page']}", SANS(18), MUTED)
        p.im.paste(vignette(int(per["page"])), (120 * g.S, (yv + 14) * g.S))
        p.rect(120, yv + 14, 120 + VW, yv + 14 + VH, outline=RULE, w=1)
    p.line([(740, 170), (740, 960)], RULE, 0.9)
    item_rows(p, scene["items"], k, 800, 196, BOTTOM, 1000, "auto", numbered=False, label_size=29, detail_size=24)
    return p


def lay_conclusion(scene, k, ctx):
    p = Page(dark=True)
    f, lines, size = fit_lines(p, scene["title"], SERIF, 88, 1600, 2, 60)
    y = 236
    for ln in lines:
        p.text(116, y, ln, f, D_TXT)
        y += size * 1.05
    if scene.get("subtitle"):
        y = p.para(120, y + 4, scene["subtitle"], SANS(26), D_TXT2, 1600, 36)
    yy = y + 46
    for i, it in enumerate(scene["items"]):
        lab = it["label"] + (" — " + suite(it["detail"]) if it.get("detail") else "")
        if i < k:
            p.circle(132, yy - 10, 7, fill=D_TEAL)
            yy = p.para(160, yy, lab, SANS(30), D_TXT, 1640, 42) + 18
        else:  # fantôme : le libellé seul, à sa place
            p.text(160, yy, it["label"], SANS(30), D_RULE)
            yy += len(p.wrap(lab, SANS(30), 1640)) * 42 + 18
    p.text(120, 930, "  ·  ".join(n.upper() for n in EQUIPE), MONO(16), D_TEAL, track=3)
    return p


LAYOUTS = {"ouverture": lay_ouverture, "texte": lay_texte, "chiffres": lay_chiffres, "schema": lay_schema,
           "personne": lay_personne, "problemes": lay_problemes, "conclusion": lay_conclusion}


def render_state(scene, k, sections, ctx=None):
    p = LAYOUTS.get(scene["layout"], lay_texte)(scene, k, ctx or {})
    chrome(p, sections, scene.get("section"))
    return to_rgb(p)
