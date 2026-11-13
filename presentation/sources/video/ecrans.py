# -*- coding: utf-8 -*-
"""Écrans de la vidéo RAO : direction artistique de présentation technique sobre.
Fond uni, Instrument Sans (crénage GPOS), texte d'au moins 30 px, couleurs fonctionnelles constantes :
réseau et tunnels en bleu canard, Zero Trust et nomades en orange, refus et pièges en rouge.
render_state(scène, k, chapitres) -> (image 1920x1080, méta) ; la méta décrit les chemins à dessiner à l'entrée de l'état."""
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent))
sys.path.insert(0, str(ICI))
import generer as g  # noqa: E402
import kerning  # noqa: E402

g.S = S = 2
W, H = 1920, 1080

# ------------------------------------------------------------------ jetons
FOND = g.PAPER
ENCRE, ENCRE2, GRIS, FILET = g.INK, g.INK2, (98, 103, 112), g.RULE
CARTE = (250, 248, 243)
RESEAU, RESEAU_CLAIR = g.TEAL, g.TEAL_L
ZT, ZT_CLAIR = g.ORANGE, g.ORANGE_L
ALERTE, ALERTE_CLAIR = (176, 48, 40), (247, 224, 219)
BLANC = (255, 255, 255)
MARGE, DROITE = 140, 1780
HAUT, BAS = 120, 950          # zone utile ; la bande sous y = 965 reste libre pour les sous-titres
NAV_Y = 70                    # repères de chapitres et barre de progression
EQUIPE = ["Farah", "Valentin", "Nolan", "Fatih", "Younes", "Maxime", "Diane"]
RETOURS = [("Valentin", "démo"), ("Younes", "risques"), ("Farah", "conclusion")]


def mix(a, b, t):
    return g.mix(a, b, t)


def pale(c, t=0.55):
    return mix(c, FOND, t)


# ------------------------------------------------------------------ polices et texte
def REG(t):
    return g.font("InstrumentSans-Regular", t)


def GRAS(t):
    return g.font("InstrumentSans-Bold", t)


def MONO(t):
    return g.font("IBMPlexMono-Regular", t)


_NOTDEF, _HAS, _AV, _KERN = {}, {}, {}, {}


def _a_glyphe(f, c):
    cle = (f.path, f.size, c)
    if cle not in _HAS:
        if c.isspace():
            _HAS[cle] = True
        else:
            nd = _NOTDEF.setdefault((f.path, f.size), (f.getmask("").size, bytes(f.getmask(""))))
            m = f.getmask(c)
            _HAS[cle] = (m.size, bytes(m)) != nd
    return _HAS[cle]


@lru_cache(None)
def _repli(path, size):
    return g.ImageFont.truetype(str(g.FONTS / "IBMPlexMono-Regular.ttf"), size)


def _avance(f, c):
    cle = (f.path, f.size, c)
    if cle not in _AV:
        _AV[cle] = f.getlength(c)
    return _AV[cle]


def _crenage(f):
    if f.path not in _KERN:
        _KERN[f.path] = kerning.crenage(f.path) if "InstrumentSans" in f.path else ({}, {})
    return _KERN[f.path]


def fr(s):
    """Typographie française (espaces insécables, apostrophe courbe) ; séparateurs « · » aérés."""
    s = re.sub(r"(\d) (M€|k€|€|To|TiB|Go|%|h|s|min)(?!\w)", "\\1\u00a0\\2", g.fr(s))
    return s.replace(" · ", "  ·  ")


def _glyphes(txt, f, suivi=0):
    """[(caractère, police, avance en px du canevas)] : crénage GPOS entre deux lettres d'Instrument Sans,
    repli sur IBM Plex Mono pour les caractères absents (≈, ≥, →)."""
    cmap, kern = _crenage(f)
    out = []
    for c in txt:
        fc = f if _a_glyphe(f, c) else _repli(f.path, f.size)
        if out and fc is f and out[-1][1] is f:
            g1, g2 = cmap.get(ord(out[-1][0])), cmap.get(ord(c))
            if g1 and g2:
                k = kern.get((g1, g2), 0) * f.size
                out[-1] = (out[-1][0], f, out[-1][2] + k)
        out.append((c, fc, _avance(fc, c) + suivi * S))
    return out


def largeur(txt, f, suivi=0):
    return sum(a for _, _, a in _glyphes(fr(txt), f, suivi)) / S


def texte(p, x, y, txt, f, couleur, ancre="l", suivi=0):
    """Texte sur sa ligne de base y ; ancre l, m ou r. Renvoie la largeur."""
    gl = _glyphes(fr(txt), f, suivi)
    w = sum(a for _, _, a in gl) / S
    x = x - w if ancre == "r" else x - w / 2 if ancre == "m" else x
    X = x * S
    for c, fc, a in gl:
        if not c.isspace():
            p.d.text((X, y * S), c, font=fc, fill=couleur, anchor="ls")
        X += a
    return w


def lignes(txt, f, maxw):
    """Découpe aux espaces ordinaires (jamais aux insécables), en respectant les retours à la ligne."""
    out = []
    for par in fr(txt).split("\n"):
        cur = ""
        for mot in par.split(" "):
            cand = (cur + " " + mot) if cur else mot
            if cur and largeur(cand, f) > maxw:
                out.append(cur)
                cur = mot
            else:
                cur = cand
        out.append(cur)
    return out


def paragraphe(p, x, y, txt, f, couleur, maxw, interligne, ancre="l"):
    """Dessine le paragraphe ; renvoie la ligne de base suivante."""
    for ln in lignes(txt, f, maxw):
        texte(p, x, y, ln, f, couleur, ancre)
        y += interligne
    return y


def hauteur(txt, f, maxw, interligne):
    return len(lignes(txt, f, maxw)) * interligne


def etiquette(p, x, y, txt, couleur=GRIS, taille=22, ancre="l"):
    return texte(p, x, y, txt.upper(), GRAS(taille), couleur, ancre, suivi=2.2)


# ------------------------------------------------------------------ formes
class Page(g.Page):
    def __init__(self):
        super().__init__(dark=False)


def ligne(p, pts, couleur, w=2.0):
    p.line(pts, couleur, w)


def tirets(p, pts, couleur, w=2.0, on=12, off=9):
    for a, b in zip(pts, pts[1:]):
        p.dashed(a, b, couleur, w, on, off)


def tete_fleche(p, a, b, couleur, taille=16):
    (x0, y0), (x1, y1) = a, b
    n = math.hypot(x1 - x0, y1 - y0) or 1
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    bx, by = x1 - ux * taille, y1 - uy * taille
    px, py, hw = -uy, ux, taille * 0.45
    p.d.polygon([(x1 * S, y1 * S), ((bx + px * hw) * S, (by + py * hw) * S), ((bx - px * hw) * S, (by - py * hw) * S)],
                fill=couleur)


def fleche(p, pts, couleur, w=3.0, pointilles=False, tete=True):
    """Chemin brisé terminé par une pointe."""
    if tete:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        n = math.hypot(x1 - x0, y1 - y0) or 1
        fin = (x1 - (x1 - x0) / n * 14, y1 - (y1 - y0) / n * 14)
        corps = pts[:-1] + [fin]
    else:
        corps = pts
    (tirets if pointilles else ligne)(p, corps, couleur, w)
    if tete:
        tete_fleche(p, pts[-2], pts[-1], couleur)


def croix(p, x, y, r, couleur, w=5):
    p.line([(x - r, y - r), (x + r, y + r)], couleur, w)
    p.line([(x - r, y + r), (x + r, y - r)], couleur, w)


def coche(p, x, y, r, couleur, w=5):
    p.line([(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.7)], couleur, w)


def pastille(p, x, y, txt, couleur, r=24, taille=26, contour=False):
    if contour:
        p.circle(x, y, r, fill=FOND, outline=couleur, w=3)
        texte(p, x, y + taille * 0.36, str(txt), GRAS(taille), couleur, "m")
    else:
        p.circle(x, y, r, fill=couleur)
        texte(p, x, y + taille * 0.36, str(txt), GRAS(taille), BLANC, "m")


def cadenas(p, x, y, couleur, echelle=1.0):
    e = echelle
    p.arc(x, y - 10 * e, 13 * e, 180, 360, couleur, 4 * e)
    p.line([(x - 13 * e, y - 10 * e), (x - 13 * e, y - 2 * e)], couleur, 4 * e)
    p.line([(x + 13 * e, y - 10 * e), (x + 13 * e, y - 2 * e)], couleur, 4 * e)
    p.rect(x - 19 * e, y - 3 * e, x + 19 * e, y + 22 * e, fill=couleur, r=4 * e)


def boite(p, x0, y0, x1, y1, titre, sous=None, style="site", taille=32, attenue=False):
    """Composant de schéma. style : site (contour encre), dc (plein encre), cloud (bleu clair), zt (orange),
    partenaire (pointillés bleus), neutre (carte)."""
    st = {"site": (CARTE, ENCRE, ENCRE, ENCRE2), "dc": (ENCRE, ENCRE, BLANC, g.D_TXT2),
          "cloud": (RESEAU_CLAIR, None, RESEAU, RESEAU), "zt": (ZT_CLAIR, ZT, ENCRE, ENCRE2),
          "ztcontour": (CARTE, ZT, ENCRE, ENCRE2), "partenaire": (CARTE, None, ENCRE, ENCRE2),
          "neutre": (CARTE, FILET, ENCRE, ENCRE2)}[style]
    fond, bord, c1, c2 = st
    if attenue:
        fond, bord, c1, c2 = (pale(fond, .5) if fond else None, pale(bord) if bord else None, pale(c1), pale(c2))
    p.rect(x0, y0, x1, y1, fill=fond, outline=bord, w=2.5, r=12)
    if style == "partenaire":
        p.dashed_rect(x0, y0, x1, y1, pale(RESEAU) if attenue else RESEAU, 2.5)
    cx = (x0 + x1) / 2
    if sous:
        texte(p, cx, (y0 + y1) / 2 - 4, titre, GRAS(taille), c1, "m")
        texte(p, cx, (y0 + y1) / 2 + 34, sous, REG(26), c2, "m")
    else:
        texte(p, cx, (y0 + y1) / 2 + taille * 0.35, titre, GRAS(taille), c1, "m")


# ------------------------------------------------------------------ cadre commun
def nav(p, chapitres, courant):
    """Repères de chapitres en haut ; la barre de progression est tracée image par image par build.py."""
    p.line([(MARGE, NAV_Y), (DROITE, NAV_Y)], FILET, 1.5)
    n = len(chapitres)
    pas = (DROITE - MARGE) / n
    for i, c in enumerate(chapitres):
        x = MARGE + i * pas
        p.line([(x, NAV_Y - 7), (x, NAV_Y + 7)], FILET, 1.5)
        actif = c == courant
        texte(p, x + 12, NAV_Y - 16, c.upper(), REG(20), RESEAU if actif else GRIS, suivi=1.6)


def titre_ecran(p, titre, chapeau=None):
    texte(p, MARGE, 186, titre, GRAS(58), ENCRE)
    if chapeau:
        texte(p, MARGE, 240, chapeau, REG(32), ENCRE2)
    return 300 if chapeau else 250


# ------------------------------------------------------------------ mises en page générales
def lay_titre(sc, k):
    p = Page()
    etiquette(p, MARGE, 250, "Réponse à appel d'offres · mutuelle santé", RESEAU, 24)
    y = paragraphe(p, MARGE - 4, 360, sc["title"], GRAS(84), ENCRE, 1400, 96)
    y = paragraphe(p, MARGE, y + 10, sc.get("subtitle", ""), REG(36), ENCRE2, 1400, 48)
    yy = max(y + 70, 640)
    etiquette(p, MARGE, yy, "Au programme", GRIS, 22)
    x = MARGE
    for i, c in enumerate(sc.get("agenda", [])):
        w = texte(p, x + 44, yy + 66, c, REG(32), ENCRE)
        pastille(p, x + 18, yy + 56, i + 1, RESEAU, r=18, taille=20)
        x += 44 + w + 46
    return p, {}


def intro(p, sc, y=430):
    """Énoncé affiché pendant la phrase d'introduction, avant le premier élément."""
    paragraphe(p, MARGE, y, sc["intro"], GRAS(48), ENCRE, DROITE - MARGE - 160, 62)


def lay_chiffres(sc, k):
    p = Page()
    titre_ecran(p, sc["title"], sc.get("subtitle"))
    if k == 0 and sc.get("intro"):
        intro(p, sc)
        return p, {"ecran": 0, "bande": 260}
    items = sc["items"]
    n = len(items)
    gap = 60
    cw = (DROITE - MARGE - gap * (n - 1)) / n
    for i, it in enumerate(items):
        if i >= k:
            break
        x = MARGE + i * (cw + gap)
        p.line([(x, 400), (x + cw, 400)], FILET, 2)
        p.line([(x, 400), (x + 70, 400)], RESEAU, 5)
        texte(p, x - 4, 560, it["value"], GRAS(136), RESEAU)
        texte(p, x, 630, it["label"], GRAS(40), ENCRE)
        paragraphe(p, x, 690, it.get("detail", ""), REG(32), ENCRE2, cw - 10, 44)
    return p, {}


def lay_liste(sc, k):
    """Items qui apparaissent au rythme de la voix ; le dernier apparu est mis en avant."""
    p = Page()
    y0 = titre_ecran(p, sc["title"], sc.get("subtitle")) + 40
    if k == 0 and sc.get("intro"):
        intro(p, sc)
        return p, {"ecran": 0, "bande": 260}
    items = sc["items"]
    n = len(items)
    pas = min(124, (BAS - y0) / max(1, n))
    tl, td, dd = (40, 32, 46) if n <= 5 else (36, 30, 42)
    for i, it in enumerate(items):
        if i >= k:
            break
        y = y0 + i * pas
        actif = i == k - 1
        col = RESEAU if actif else pale(RESEAU, .35)
        pastille(p, MARGE + 24, y + 22, i + 1, col)
        texte(p, MARGE + 76, y + 36, it["label"], GRAS(tl), ENCRE if actif else ENCRE2)
        if it.get("detail"):
            texte(p, MARGE + 76, y + 36 + dd, it["detail"], REG(td), ENCRE2 if actif else GRIS)
        if it.get("value"):
            texte(p, DROITE, y + 36, it["value"], GRAS(30), col, "r")
    return p, {}


def lay_criteres(sc, k):
    """Trois colonnes ; à partir du premier volet, la colonne commentée est mise en avant."""
    p = Page()
    titre_ecran(p, sc["title"], sc.get("subtitle"))
    cols = sc["colonnes"]
    gap = 70
    cw = (DROITE - MARGE - gap * 2) / 3
    for i, c in enumerate(cols):
        x = MARGE + i * (cw + gap)
        actif = k == 0 or k == i + 1
        c1, c2, cn = (ENCRE, ENCRE2, RESEAU) if actif else (pale(ENCRE, .6), pale(ENCRE2, .6), pale(RESEAU, .6))
        texte(p, x, 470, str(i + 1), GRAS(120), cn)
        p.line([(x, 500), (x + cw, 500)], FILET if not (actif and k) else RESEAU, 2 if not (actif and k) else 4)
        texte(p, x, 560, c["titre"], GRAS(40), c1)
        paragraphe(p, x, 615, c["texte"], REG(32), c2, cw, 44)
    note = sc.get("notes", {}).get(str(k))
    if note:
        p.rect(MARGE, 830, DROITE, 930, fill=CARTE, outline=FILET, w=2, r=12)
        p.rect(MARGE, 830, MARGE + 8, 930, fill=RESEAU)
        texte(p, MARGE + 36, 892, note, REG(32), ENCRE)
    return p, {}


# ------------------------------------------------------------------ schéma de la solution
# Composants et relations de la page 6 du PDF et de l'offre § 3 : 3 profils de site, 2 datacenters HDS,
# Internet (opérateurs A et B), nomades via FortiSASE vers les 2 DC, 40 partenaires site à site vers les 2 DC.
SITES = [("2 sièges", "≈ 2 000 personnes chacun", 300), ("498 agences France", "≈ 8 personnes chacune", 450),
         ("30 agences à l'étranger", "≈ 67 personnes chacune", 600)]
SX0, SX1, SH = MARGE, 560, 110
NUAGE = (790, 290, 1130, 720)
DCS = [(1380, 290, DROITE, 460), (1380, 550, DROITE, 720)]
BAS_Y0, BAS_Y1 = 800, 900
NOMADES, SASE, PART = (MARGE, BAS_Y0, 560, BAS_Y1), (760, BAS_Y0, 1160, BAS_Y1), (1380, BAS_Y0, DROITE, BAS_Y1)
LEGENDES_SOLUTION = [
    ("Trois types de sites, deux datacenters", "certifiés HDS, en région parisienne"),
    ("Traits bleus : tunnels chiffrés IPsec", "chaque site a au moins deux accès Internet et rejoint les deux datacenters"),
    ("SD-WAN : le GPS des tunnels", "il choisit le meilleur accès et bascule seul en cas de panne"),
    ("Orange : accès Zero Trust", "nomades et partenaires nomades via FortiSASE, vers les deux datacenters"),
    ("MFA, puis ses seules applications", "mot de passe + second facteur ; jamais le réseau entier"),
    ("Pointillés : 40 partenaires site à site", "un tunnel vers la zone partenaire de chacun des deux datacenters"),
]


def _tunnels():
    """Chemins site -> datacenter, en traversant le nuage Internet."""
    out = []
    for s, (_, _, y) in enumerate(SITES):
        cy = y + SH / 2
        for d, (x0, y0, x1, y1) in enumerate(DCS):
            dy = (y0 + y1) / 2 + (s - 1) * 26
            out.append([(SX1, cy + (d - .5) * 22), (x0, dy)])
    return out


def _chemins_zt():
    sx0, sy0, sx1, sy1 = SASE
    return [[(NOMADES[2], (BAS_Y0 + BAS_Y1) / 2), (sx0, (BAS_Y0 + BAS_Y1) / 2)],
            [(sx1, sy0 + 30), (1300, sy0 + 30), (1300, DCS[1][3] - 40), (DCS[1][0], DCS[1][3] - 40)],
            [(sx1 - 40, sy0), (sx1 - 40, 760), (1250, 760), (1250, DCS[0][3] - 40), (DCS[0][0], DCS[0][3] - 40)]]


def _chemins_bascule():
    """Agences France : l'accès B prend le relais, jusqu'aux deux datacenters."""
    y = SITES[1][2] + SH / 2
    b = [(SX1 + 18, y + 14), (700, y + 70), (NUAGE[2], y + 70)]
    return [b + [(DCS[0][0], (DCS[0][1] + DCS[0][3]) / 2 + 10)], b + [(DCS[1][0], (DCS[1][1] + DCS[1][3]) / 2 - 10)]]


def _chemins_partenaires():
    px0, py0, px1, py1 = PART
    return [[(1700, py0), (1700, DCS[1][3])],
            [(px1, py0 + 30), (1850, py0 + 30), (1850, (DCS[0][1] + DCS[0][3]) / 2), (DROITE, (DCS[0][1] + DCS[0][3]) / 2)]]


def _pilule(p, x, y, txt, f, couleur, fond, ancre="m"):
    """Étiquette posée sur un fond, lisible même au-dessus des tunnels."""
    w = largeur(txt, f)
    x0 = x - w / 2 if ancre == "m" else x
    h = f.size / S
    p.rect(x0 - 12, y - h * 0.85, x0 + w + 12, y + h * 0.3, fill=fond, r=8)
    texte(p, x0, y, txt, f, couleur)


def lay_architecture(sc, k, sans_chemins=False):
    p = Page()
    texte(p, MARGE, 186, sc["title"], GRAS(58), ENCRE)
    lab, det = LEGENDES_SOLUTION[min(k, 5)]
    w = texte(p, MARGE, 240, lab, GRAS(32), ZT if k in (3, 4) else RESEAU)
    texte(p, MARGE + w, 240, " — " + det, REG(32), ENCRE2)
    chemins, seq = [], False
    efface = 2 <= k <= 4  # étapes 2 à 4 : les tunnels s'effacent au profit du nouvel élément ; l'étape 5 montre tout
    fond_nuage = pale(RESEAU_CLAIR, .35) if efface else RESEAU_CLAIR
    # étape 1 : nuage Internet et tunnels
    if k >= 1:
        x0, y0, x1, y1 = NUAGE
        p.rect(x0, y0, x1, y1, fill=fond_nuage, r=60)
        if not (sans_chemins and k == 1):
            for ch in _tunnels():
                ligne(p, ch, pale(RESEAU, .6) if efface else RESEAU, 3)
        cc = pale(RESEAU) if efface else RESEAU
        _pilule(p, (x0 + x1) / 2, y0 + 50, "Internet", GRAS(32), cc, fond_nuage)
        _pilule(p, (x0 + x1) / 2, y1 - 26, "opérateurs A et B", REG(30), cc, fond_nuage)
        if k == 1:
            chemins += _tunnels()
    # étape 0 : sites et datacenters (les datacenters, destination de tous les flux, restent toujours pleins)
    for t_, s_, y in SITES:
        boite(p, SX0, y, SX1, y + SH, t_, s_, "site", 32, attenue=1 <= k <= 4)
    for i, (x0, y0, x1, y1) in enumerate(DCS):
        p.rect(x0, y0, x1, y1, fill=ENCRE, r=12)
        texte(p, (x0 + x1) / 2, y0 + 62, f"Datacenter {i + 1}", GRAS(34), BLANC, "m")
        texte(p, (x0 + x1) / 2, y0 + 100, "région parisienne · HDS", REG(26), g.D_TXT2, "m")
    if k >= 1:  # un pare-feu FortiGate par site
        col = pale(RESEAU) if efface else RESEAU
        for _, _, y in SITES:
            p.rect(SX1 - 20, y + SH / 2 - 20, SX1 + 20, y + SH / 2 + 20, fill=col, r=6)
            texte(p, SX1, y + SH / 2 + 9, "FG", GRAS(22), BLANC, "m")
        texte(p, SX0, SITES[2][2] + SH + 44, "FG : pare-feu FortiGate", REG(30), col)
    # étape 2 : SD-WAN, deux accès et bascule (agences France)
    if k == 2:
        y = SITES[1][2] + SH / 2
        a = [(SX1 + 18, y - 14), (700, y - 70), (NUAGE[0] + 10, y - 70)]
        ligne(p, a, ALERTE, 5)
        croix(p, 680, y - 64, 15, ALERTE, 5)
        _pilule(p, 590, y - 96, "accès A : panne", GRAS(28), ALERTE, FOND, "l")
        for ch in ([] if sans_chemins else _chemins_bascule()):
            ligne(p, ch, RESEAU, 7)
        _pilule(p, 590, y + 124, "accès B : bascule automatique", GRAS(28), RESEAU, FOND, "l")
        chemins += _chemins_bascule()
    # étape 3 : nomades via FortiSASE (orange)
    if k >= 3:
        boite(p, *NOMADES, "Nomades", "3 000 salariés + ~60 partenaires", "ztcontour", 32)
        boite(p, *SASE, "FortiSASE", "sécurité dans le cloud", "zt", 32)
        for ch in ([] if sans_chemins and k == 3 else _chemins_zt()):
            fleche(p, ch, ZT, 4)
        if k == 3:
            chemins += _chemins_zt()
            seq = True
    # étape 4 : MFA, puis seulement ses applications
    if k >= 4:
        cx = (NOMADES[2] + SASE[0]) / 2
        cadenas(p, cx, BAS_Y0 - 18, ZT)
        texte(p, cx, BAS_Y0 - 54, "MFA", GRAS(28), ZT, "m")
        for x0, y0, x1, y1 in DCS:
            p.rect(x0 + 24, y1 - 52, x0 + 250, y1 - 12, fill=BLANC, outline=ZT, w=3, r=8)
            texte(p, x0 + 137, y1 - 24, "ses applications", GRAS(24), ENCRE, "m")
    # étape 5 : partenaires site à site
    if k >= 5:
        boite(p, *PART, "40 partenaires", "site à site", "partenaire", 32)
        for ch in ([] if sans_chemins else _chemins_partenaires()):
            fleche(p, ch, RESEAU, 4, pointilles=True)
        chemins += _chemins_partenaires()
        texte(p, DROITE, 945, "Partout : tout est refusé par défaut, sauf ce qui est écrit.", GRAS(30), ENCRE, "r")
    return p, {"chemins": chemins, "sequentiel": seq, "zone_texte": (0, 204, W, 258)}  # chapeau : remplacé en passant par le fond


# ------------------------------------------------------------------ fiches de rôle
def bandeau_role(p, per, sections, actuelle):
    """En-tête commun à tous les écrans d'une fiche : identité, diapos, durée, sections."""
    etiquette(p, MARGE, 132, f"Rôle {per['order']} sur 7", RESEAU, 22)
    w = texte(p, MARGE, 200, per["name"], GRAS(60), ENCRE)
    texte(p, MARGE + w + 24, 200, per["role"], REG(36), RESEAU)
    texte(p, DROITE, 160, per["slides"], GRAS(32), ENCRE, "r")
    texte(p, DROITE, 202, per["duration"], REG(30), ENCRE2, "r")
    y = 262
    p.line([(MARGE, y + 18), (DROITE, y + 18)], FILET, 2)
    x = MARGE
    for s in sections:
        actif = s == actuelle
        w = texte(p, x, y, s.upper(), REG(23), RESEAU if actif else GRIS, suivi=1.8)
        if actif:
            p.line([(x, y + 18), (x + w, y + 18)], RESEAU, 5)
        x += w + 44


def corps_titre(p, titre, couleur=ENCRE, y=352):
    texte(p, MARGE, y, titre, GRAS(42), couleur)
    return y + 40


def ecr_identite(p, e, sc):
    per = sc["person"]
    order = int(per["order"])
    y0 = corps_titre(p, "Ordre de passage")
    x0, x1, fy = MARGE + 40, DROITE - 40, y0 + 120
    p.line([(x0, fy), (x1, fy)], FILET, 3)
    for i, n in enumerate(EQUIPE):
        x = x0 + i * (x1 - x0) / 6
        if i + 1 == order:
            pastille(p, x, fy, i + 1, RESEAU, r=34, taille=34)
            texte(p, x, fy + 86, n, GRAS(36), RESEAU, "m")
        else:
            pastille(p, x, fy, i + 1, pale(ENCRE2, .25), r=24, taille=26)
            texte(p, x, fy + 76, n, REG(32), ENCRE2, "m")
    yy = fy + 170
    w = texte(p, MARGE, yy, "Puis, en fin de parcours :", REG(32), ENCRE2)
    x = MARGE + w + 20
    for j, (n, quoi) in enumerate(RETOURS):
        c = RESEAU if n == per["name"] else ENCRE
        x += texte(p, x, yy, n, GRAS(32), c)
        x += texte(p, x, yy, f" ({quoi})" + ("  →  " if j < 2 else ""), REG(32), ENCRE2)
    if e.get("note"):
        p.rect(MARGE, yy + 50, DROITE, yy + 140, fill=CARTE, outline=FILET, w=2, r=12)
        texte(p, MARGE + 34, yy + 107, e["note"], REG(32), ENCRE)


def ecr_presente(p, e, sc):
    y = corps_titre(p, e.get("titre", "Ce que vous présentez")) + 40
    diapos = e["diapos"]
    pas = 78 if len(diapos) > 3 else 92
    for num, titre in diapos:
        p.rect(MARGE, y - 42, MARGE + 150, y + 18, fill=RESEAU, r=10)
        texte(p, MARGE + 75, y, f"diapo {num}", GRAS(28), BLANC, "m")
        texte(p, MARGE + 180, y, titre, REG(34), ENCRE)
        y += pas
    y += 14
    for nt in e.get("notes", []):
        nt = nt if isinstance(nt, dict) else {"texte": nt}
        col = ALERTE if nt.get("alerte") else RESEAU
        p.rect(MARGE, y - 30, MARGE + 8, y + 8, fill=col)
        y = paragraphe(p, MARGE + 30, y, nt["texte"], REG(32), ENCRE if nt.get("alerte") else ENCRE2,
                       DROITE - MARGE - 40, 44) + 14


def ecr_message(p, e, sc):
    y = corps_titre(p, e.get("titre", "Message clé"))
    y = paragraphe(p, MARGE, y + 70, "« " + e["phrase"] + " »", GRAS(46), ENCRE, DROITE - MARGE, 60)
    y += 20
    for pt in e.get("points", []):
        p.rect(MARGE, y - 30, MARGE + 8, y + 8, fill=RESEAU)
        y = paragraphe(p, MARGE + 34, y, pt, REG(34), ENCRE2, DROITE - MARGE - 40, 46) + 18


def ecr_compare(p, e, sc):
    """Deux cartes côte à côte : le choix retenu et l'option écartée (ou avant / après)."""
    y0 = corps_titre(p, e.get("titre", "Notre choix")) + 30
    gap = 60
    cw = (DROITE - MARGE - gap) / 2
    def haut(c):
        h = 112 + hauteur(c["titre"], GRAS(40), cw - 68, 50) + 10
        return h + sum(hauteur("– " + pt, REG(32), cw - 68, 44) + 10 for pt in c.get("points", [])) + 30
    bas = y0 + max(haut(e["gauche"]), haut(e["droite"]))
    for i, cote in enumerate((e["gauche"], e["droite"])):
        x = MARGE + i * (cw + gap)
        etat = cote.get("etat", "neutre")
        col = {"retenu": RESEAU, "ecarte": ALERTE}.get(etat, ENCRE2)
        p.rect(x, y0, x + cw, bas, fill=CARTE, outline=col, w=3, r=16)
        etiquette(p, x + 34, y0 + 52, cote.get("etiquette", {"retenu": "Retenu", "ecarte": "Écarté"}.get(etat, "")), col, 22)
        if etat in ("retenu", "ecarte"):
            (coche if etat == "retenu" else croix)(p, x + cw - 50, y0 + 44, 16, col, 6)
        yy = paragraphe(p, x + 34, y0 + 112, cote["titre"], GRAS(40), ENCRE, cw - 68, 50) + 10
        for pt in cote.get("points", []):
            yy = paragraphe(p, x + 34, yy, "– " + pt, REG(32), ENCRE2, cw - 68, 44) + 10
    if e.get("note"):
        paragraphe(p, MARGE, bas + 60, e["note"], REG(32), ENCRE, DROITE - MARGE, 44)


def ecr_chiffres(p, e, sc):
    y0 = corps_titre(p, e.get("titre", "Chiffres à citer"))
    items = e["chiffres"]
    n = len(items)
    gap = 56
    cw = (DROITE - MARGE - gap * (n - 1)) / n
    for i, it in enumerate(items):
        x = MARGE + i * (cw + gap)
        p.line([(x, y0 + 50), (x + cw, y0 + 50)], FILET, 2)
        p.line([(x, y0 + 50), (x + 70, y0 + 50)], RESEAU, 5)
        texte(p, x - 4, y0 + 190, it["valeur"], GRAS(110 if n <= 3 else 92), RESEAU)
        yy = paragraphe(p, x, y0 + 252, it["unite"], GRAS(34), ENCRE, cw - 10, 44)
        if it.get("detail"):
            paragraphe(p, x, yy + 8, it["detail"], REG(30), ENCRE2, cw - 10, 40)


def ecr_question(p, e, sc):
    y = corps_titre(p, e.get("titre", "Question probable"), ALERTE if e.get("piege") else ENCRE)
    y += 60
    etiquette(p, MARGE, y, "Le jury", GRIS)
    y = paragraphe(p, MARGE, y + 50, "« " + e["question"] + " »", GRAS(42), ENCRE, DROITE - MARGE, 54) + 20
    etiquette(p, MARGE, y, "Réponse courte", RESEAU)
    y = paragraphe(p, MARGE, y + 48, e["reponse"], REG(36), ENCRE, DROITE - MARGE, 48) + 20
    if e.get("pourquoi"):
        etiquette(p, MARGE, y, "Pourquoi", GRIS)
        paragraphe(p, MARGE, y + 46, e["pourquoi"], REG(32), ENCRE2, DROITE - MARGE - 260, 44)
    if e.get("source"):
        texte(p, DROITE, 920, e["source"], REG(26), GRIS, "r")


def ecr_piege(p, e, sc):
    """Ne dites pas / dites : une vue avant-après, en rouge et en bleu."""
    y0 = corps_titre(p, e.get("titre", "Piège à éviter"), ALERTE)
    if e.get("sujet"):
        paragraphe(p, MARGE, y0 + 60, e["sujet"], REG(34), ENCRE, DROITE - MARGE, 46)
    gap = 60
    cw = (DROITE - MARGE - gap) / 2
    yb = y0 + 120
    for i, (lab, txt, col, fond) in enumerate((("Ne dites pas", e["nepas"], ALERTE, ALERTE_CLAIR),
                                                ("Dites", e["dire"], RESEAU, RESEAU_CLAIR))):
        x = MARGE + i * (cw + gap)
        p.rect(x, yb, x + cw, yb + 300, fill=fond, r=16)
        etiquette(p, x + 34, yb + 54, lab, col, 24)
        (croix if i == 0 else coche)(p, x + cw - 50, yb + 46, 16, col, 6)
        paragraphe(p, x + 34, yb + 116, txt, GRAS(36), ENCRE, cw - 68, 48)
    if e.get("pourquoi"):
        paragraphe(p, MARGE, yb + 360, e["pourquoi"], REG(32), ENCRE2, DROITE - MARGE, 44)


def ecr_etapes(p, e, sc):
    y0 = corps_titre(p, e.get("titre", "Étapes"))
    etapes = e["etapes"]
    n = len(etapes)
    x0, x1, fy = MARGE + 40, DROITE - 40, y0 + 110
    p.line([(x0, fy), (x1, fy)], FILET, 3)
    for i, t in enumerate(etapes):
        x = x0 + i * (x1 - x0) / (n - 1)
        pastille(p, x, fy, i + 1, RESEAU, r=28, taille=28)
        for j, ln in enumerate(lignes(t, REG(30), (x1 - x0) / (n - 1) - 12)):
            texte(p, x, fy + 74 + j * 38, ln, REG(30), ENCRE, "m")
    y = fy + 170
    notes = e.get("notes", [])
    gap = 50
    cw = (DROITE - MARGE - gap * (len(notes) - 1)) / max(1, len(notes))
    for i, nt in enumerate(notes):
        x = MARGE + i * (cw + gap)
        col = ALERTE if nt.get("alerte") else RESEAU
        p.rect(x, y, x + cw, 940, fill=CARTE, outline=FILET, w=2, r=14)
        p.rect(x, y, x + 8, 940, fill=col)
        etiquette(p, x + 34, y + 50, nt["titre"], col)
        paragraphe(p, x + 34, y + 100, nt["texte"], REG(32), ENCRE, cw - 68, 44)


def ecr_corrections(p, e, sc):
    y0 = corps_titre(p, e.get("titre", "À corriger sur vos diapos"), ALERTE)
    texte(p, MARGE, y0 + 52, "À faire sur le diaporama : ce n'est pas encore corrigé.", REG(32), ENCRE2)
    y = y0 + 110
    lig = e["lignes"]
    hl = min(220, (920 - y) / max(1, len(lig)))
    for ln in lig:
        p.rect(MARGE, y, DROITE, y + hl - 20, fill=CARTE, outline=FILET, w=2, r=14)
        p.rect(MARGE, y, MARGE + 8, y + hl - 20, fill=ALERTE)
        texte(p, MARGE + 34, y + 52, f"Diapo {ln['diapo']}", GRAS(34), ENCRE)
        etiquette(p, MARGE + 330, y + 46, "Écrit", GRIS)
        paragraphe(p, MARGE + 470, y + 50, ln["ecrit"], REG(32), ALERTE, DROITE - MARGE - 510, 42)
        etiquette(p, MARGE + 330, y + 46 + (hl - 20) / 2, "À écrire", RESEAU)
        paragraphe(p, MARGE + 470, y + 50 + (hl - 20) / 2, ln["faire"], REG(32), ENCRE, DROITE - MARGE - 510, 42)
        y += hl


def ecr_transition(p, e, sc):
    y = corps_titre(p, e.get("titre", "Transition à dire au jury")) + 50
    for ph in e["phrases"]:
        if ph.get("quand"):
            etiquette(p, MARGE, y, ph["quand"], GRIS)
            y += 54
        y = paragraphe(p, MARGE, y + 10, "« " + ph["phrase"] + " »", GRAS(42), ENCRE, DROITE - MARGE - 300, 54)
        if ph.get("vers"):
            texte(p, DROITE, y - 54, "→ " + ph["vers"], GRAS(40), RESEAU, "r")
        y += 50


def ecr_vigilance(p, e, sc):
    """Point de vigilance : le constat, puis la phrase à dire au jury."""
    y0 = corps_titre(p, e.get("titre", "Point de vigilance"), ALERTE)
    y = y0 + 40
    h1 = 70 + hauteur(e["constat"], REG(34), DROITE - MARGE - 68, 46)
    p.rect(MARGE, y, DROITE, y + h1, fill=CARTE, outline=FILET, w=2, r=14)
    p.rect(MARGE, y, MARGE + 8, y + h1, fill=ALERTE)
    etiquette(p, MARGE + 34, y + 46, "Le constat", ALERTE)
    paragraphe(p, MARGE + 34, y + 96, e["constat"], REG(34), ENCRE, DROITE - MARGE - 68, 46)
    y += h1 + 30
    h2 = 70 + hauteur(e["dire"], GRAS(36), DROITE - MARGE - 68, 48)
    p.rect(MARGE, y, DROITE, y + h2, fill=RESEAU_CLAIR, r=14)
    etiquette(p, MARGE + 34, y + 46, "À dire au jury", RESEAU)
    paragraphe(p, MARGE + 34, y + 98, e["dire"], GRAS(36), ENCRE, DROITE - MARGE - 68, 48)
    if e.get("pourquoi"):
        paragraphe(p, MARGE, y + h2 + 56, e["pourquoi"], REG(32), ENCRE2, DROITE - MARGE, 44)


def ecr_tableau(p, e, sc):
    y = corps_titre(p, e.get("titre", "Règles de dimensionnement")) + 50
    lignes_t = e["lignes"]
    pas = min(110, (930 - y) / max(1, len(lignes_t)))
    for i, (lab, val) in enumerate(lignes_t):
        total = i == len(lignes_t) - 1 and e.get("total")
        p.line([(MARGE, y + 30), (DROITE, y + 30)], RESEAU if total else FILET, 3 if total else 2)
        texte(p, MARGE, y, lab, GRAS(36), ENCRE)
        texte(p, 760, y, val, GRAS(38) if total else REG(36), RESEAU if total else ENCRE)
        y += pas


def ecr_gantt(p, e, sc):
    """Phasage : une barre par phase, de M0 à M9."""
    y0 = corps_titre(p, e.get("titre", "Le phasage")) + 30
    x0, x1, n = 660, DROITE, e.get("mois", 9)
    u = (x1 - x0) / n
    phases = e["phases"]
    pas = min(110, ((870 if e.get("note") else 930) - y0 - 50) / len(phases))  # place pour la note
    bas = y0 + 50 + pas * len(phases)
    for m in range(n + 1):
        x = x0 + m * u
        p.line([(x, y0 + 20), (x, bas)], FILET, 1.5)
        texte(p, x, y0 + 8, f"M{m}", REG(24), GRIS, "m")
    for i, ph in enumerate(phases):
        cy = y0 + 50 + pas * i + pas / 2
        texte(p, MARGE, cy - 8, ph["nom"], GRAS(32), ENCRE)
        texte(p, MARGE, cy + 28, ph.get("detail", ""), REG(30), ENCRE2)
        col = ZT if ph.get("zt") else RESEAU
        p.rect(x0 + ph["debut"] * u + 3, cy - 22, x0 + ph["fin"] * u - 3, cy + 22, fill=col, r=22)
        texte(p, x0 + (ph["debut"] + ph["fin"]) / 2 * u, cy + 9, f"M{ph['debut']} – M{ph['fin']}", GRAS(24), BLANC, "m")
    if e.get("note"):  # correction à faire sur les diapos du rôle
        p.rect(MARGE, 912, MARGE + 8, 950, fill=ALERTE)
        texte(p, MARGE + 30, 942, e["note"], REG(30), ENCRE)


def ecr_barres(p, e, sc):
    """Ventilation d'un montant : barres horizontales, unité et périmètre écrits ; encadré optionnel à droite."""
    y0 = corps_titre(p, e.get("titre", "Ventilation")) + 26
    texte(p, MARGE, y0 + 26, e.get("perimetre", ""), REG(30), ENCRE2)
    postes = e["postes"]
    vmax = max(v for _, v in postes)
    xl, xb, xmax = MARGE, MARGE + 330, (1060 if e.get("encadre") else 1500)
    y = y0 + 100
    pas = min(76, (860 - y) / len(postes))
    for i, (lab, v) in enumerate(postes):
        texte(p, xl, y + 12, lab, GRAS(30), ENCRE)
        w = (xmax - xb) * v / vmax
        p.rect(xb, y - 18, xb + w, y + 22, fill=RESEAU if i == 0 else pale(RESEAU, .25), r=6)
        texte(p, xb + w + 16, y + 12, f"{v:,} €".replace(",", "\u00a0"), GRAS(30), ENCRE)
        y += pas
    if e.get("total"):
        p.line([(xl, y - 10), (xmax + 150, y - 10)], ENCRE2, 2)
        texte(p, xl, y + 36, e["total"], GRAS(34), RESEAU)
    if e.get("encadre"):
        enc = e["encadre"]
        xa = 1290
        p.rect(xa, y0 + 60, DROITE, 930, fill=CARTE, outline=FILET, w=2, r=14)
        p.rect(xa, y0 + 60, xa + 8, 930, fill=ALERTE)
        etiquette(p, xa + 34, y0 + 110, enc["titre"], ALERTE)
        yy = y0 + 160
        for it in enc["points"]:
            yy = paragraphe(p, xa + 34, yy, "– " + it, REG(30), ENCRE, DROITE - xa - 60, 40) + 6


def _zone(p, x0, y0, x1, y1, titre, sous=None, style="neutre", taille=30):
    boite(p, x0, y0, x1, y1, titre, sous, style, taille)


def sch_nord_sud(p, e):
    """Diapo 10 : Internet -> pare-feu périmètre -> DMZ (WAF, passerelle SFTP) -> zones internes ; sorties filtrées."""
    y0 = 430
    x, y = MARGE, y0 + 40
    p.rect(x, y, x + 280, y + 260, fill=RESEAU_CLAIR, r=60)
    texte(p, x + 140, y + 120, "Internet", GRAS(34), RESEAU, "m")
    texte(p, x + 140, y + 162, "connexions entrantes", REG(26), RESEAU, "m")
    _zone(p, 560, y + 50, 860, y + 210, "Pare-feu", "périmètre (FortiGate)", "site", 32)
    p.rect(980, y - 40, 1440, y + 300, fill=CARTE, outline=ENCRE2, w=3, r=16)
    etiquette(p, 1004, y - 6, "DMZ · services publiés", ENCRE2)
    _zone(p, 1010, y + 30, 1410, y + 130, "WAF F5", "bloque les attaques web", "neutre", 32)
    _zone(p, 1010, y + 160, 1410, y + 260, "Passerelle SFTP", "le FTP devient du SFTP, chiffré", "neutre", 32)
    _zone(p, 1530, y + 50, DROITE, y + 210, "Zones internes", "via pare-feu interne", "dc", 32)
    fleche(p, [(x + 280, y + 130), (560, y + 130)], RESEAU, 4)
    fleche(p, [(860, y + 130), (980, y + 130)], RESEAU, 4)
    fleche(p, [(1440, y + 130), (1530, y + 130)], RESEAU, 4)
    fleche(p, [(1655, y + 210), (1655, y + 345), (710, y + 345), (710, y + 210)], ENCRE2, 3, pointilles=True)
    fleche(p, [(560, y + 180), (x + 280, y + 180)], ENCRE2, 3, pointilles=True)
    texte(p, 760, y + 440, "Sorties vers Internet filtrées et journalisées (DC, agences ; FortiSASE pour les nomades)",
          REG(30), ENCRE2, "m")


def sch_est_ouest(p, e):
    """Diapo 11 et 12 : cinq zones derrière la seconde paire de pare-feu ; tests de la maquette ; bastion."""
    y = 420
    zw, gap = 216, 12
    xz = MARGE + 5 * zw + 4 * gap
    p.rect(MARGE, y, xz, y + 56, fill=ENCRE, r=10)
    texte(p, (MARGE + xz) / 2, y + 38, "Pare-feu interne : seconde paire FortiGate", GRAS(30), BLANC, "m")
    zones = ["DMZ", "Applications", "Données", "Administration", "Partenaires"]
    for i, z in enumerate(zones):
        x0 = MARGE + i * (zw + gap)
        _zone(p, x0, y + 100, x0 + zw, y + 190, z, None, "neutre", 28)
        p.line([(x0 + zw / 2, y + 56), (x0 + zw / 2, y + 100)], FILET, 3)
    yy = y + 270
    tests = [("Web → application", True), ("Application → base", True), ("Web → base", False)]
    for i, (lab, ok) in enumerate(tests):
        cy = yy + i * 62
        (coche if ok else croix)(p, MARGE + 20, cy - 10, 14, RESEAU if ok else ALERTE, 5)
        texte(p, MARGE + 56, cy, lab, GRAS(30), ENCRE)
        texte(p, MARGE + 420, cy, "autorisé" if ok else "refusé et journalisé", REG(30), RESEAU if ok else ALERTE)
    xb = 1300
    p.rect(xb, y, DROITE, 900, fill=CARTE, outline=FILET, w=2, r=14)
    etiquette(p, xb + 30, y + 46, "Infogérance", RESEAU)
    _zone(p, xb + 30, y + 80, DROITE - 30, y + 170, "Infogérants", "via FortiSASE", "ztcontour", 28)
    _zone(p, xb + 30, y + 230, DROITE - 30, y + 330, "Bastion WALLIX", "porte unique, enregistrée", "neutre", 28)
    fleche(p, [((xb + DROITE) / 2, y + 170), ((xb + DROITE) / 2, y + 230)], ZT, 4)
    paragraphe(p, xb + 30, y + 390, "Jamais d'accès direct aux équipements ; MFA, accès limité dans le temps.",
               REG(30), ENCRE2, DROITE - xb - 60, 40)


def sch_dc_actif(p, e):
    """Offre § 5.1 : publication en actif/actif, bases en actif/passif copiées en différé vers l'autre DC."""
    y = 430
    for i, x0 in enumerate((MARGE, 1080)):
        x1 = x0 + 700
        p.rect(x0, y, x1, y + 420, fill=CARTE, outline=ENCRE, w=3, r=16)
        texte(p, x0 + 34, y + 58, f"Datacenter {i + 1}", GRAS(38), ENCRE)
        texte(p, x1 - 34, y + 58, "HDS", GRAS(30), RESEAU, "r")
        p.rect(x0 + 34, y + 100, x1 - 34, y + 200, fill=RESEAU_CLAIR, r=12)
        texte(p, x0 + 60, y + 144, "Publication web et API", GRAS(30), ENCRE)
        texte(p, x0 + 60, y + 182, "active dans les deux datacenters", REG(30), RESEAU)
        p.rect(x0 + 34, y + 240, x1 - 34, y + 360, fill=BLANC if i == 0 else CARTE, outline=ENCRE if i == 0 else FILET, w=2, r=12)
        texte(p, x0 + 60, y + 288, "Bases de données", GRAS(30), ENCRE)
        texte(p, x0 + 60, y + 328, "en service" if i == 0 else "copie, prête à prendre le relais", REG(30), ENCRE2)
    fleche(p, [(MARGE + 700 - 34, y + 300), (1080 + 34, y + 300)], RESEAU, 4, pointilles=True)
    texte(p, 960, y + 280, "copie en différé", GRAS(26), RESEAU, "m")
    texte(p, 960, y + 336, "(asynchrone, à confirmer)", REG(26), RESEAU, "m")
    texte(p, 960, y + 480, "Deux datacenters certifiés HDS et indépendants.", GRAS(32), ENCRE, "m")


SCHEMAS = {"nord_sud": sch_nord_sud, "est_ouest": sch_est_ouest, "dc_actif": sch_dc_actif}


def ecr_schema(p, e, sc):
    corps_titre(p, e.get("titre", "Schéma"))
    SCHEMAS[e["schema"]](p, e)
    if e.get("note"):  # correction à faire sur les diapos du rôle
        p.rect(MARGE, 922, MARGE + 8, 960, fill=ALERTE)
        texte(p, MARGE + 30, 952, e["note"], REG(30), ENCRE)


def _etapes_risques(items):
    """(indice du risque, partiel) pour chaque état à partir de 1. Un risque « en_deux » occupe deux états, quand
    la voix le traite en deux phrases : ses champs sont alors des listes [dit d'abord, ajouté ensuite]."""
    out = []
    for i, r in enumerate(items):
        out += [(i, True), (i, False)] if r.get("en_deux") else [(i, False)]
    return out


def _champ(r, cle, partiel):
    v = r.get(cle) or ""
    if isinstance(v, str):
        return v
    v = v[:1] if partiel else v
    return (", " if cle == "repond" else " ").join(x for x in v if x)


def lay_risques(sc, k):
    """État 0 : la liste, avec qui répond ; états suivants : problème -> conséquence -> réponse."""
    p = Page()
    items = sc["risques"]
    if k == 0:
        y0 = titre_ecran(p, sc["title"], sc.get("subtitle")) + 40
        pas = min(112, (BAS - y0) / len(items))
        for i, r in enumerate(items):
            y = y0 + i * pas
            pastille(p, MARGE + 24, y + 22, i + 1, ENCRE2)
            texte(p, MARGE + 76, y + 36, r["titre"], GRAS(40), ENCRE)
            if r.get("repond"):
                texte(p, DROITE, y + 36, _champ(r, "repond", False), GRAS(32), RESEAU, "r")
        return p, {"ecran": 0}
    etapes = _etapes_risques(items)
    ir, partiel = etapes[min(k, len(etapes)) - 1]
    r = items[ir]
    etiquette(p, MARGE, 132, f"{sc.get('rubrique', 'Problématique')} {ir + 1} sur {len(items)}", GRIS, 22)
    texte(p, MARGE, 200, r["titre"], GRAS(56), ENCRE)
    if r.get("repond"):
        x_rep = DROITE - largeur("Répond : " + _champ(r, "repond", False), GRAS(32))
        texte(p, x_rep, 200, "Répond : " + _champ(r, "repond", partiel), GRAS(32), RESEAU)
    entetes = sc.get("entetes", ["Problème", "Conséquence", "Notre réponse"])
    cles = ("probleme", "consequence", "reponse")
    cols = [ALERTE, ENCRE2, RESEAU]
    gap = 70
    cw = (DROITE - MARGE - 2 * gap) / 3
    y0 = 290  # hauteur calculée sur le texte complet : les cartes ne bougent pas quand un risque se complète
    y1 = y0 + max(400, 190 + max(hauteur(_champ(r, c, False), GRAS(34), cw - 60, 48) for c in cles))
    for i, (cle, ent) in enumerate(zip(cles, entetes)):
        x = MARGE + i * (cw + gap)
        txt = _champ(r, cle, partiel)
        fond = (RESEAU_CLAIR if i == 2 else CARTE) if txt else FOND
        p.rect(x, y0, x + cw, y1, fill=fond, outline=FILET if (i < 2 or not txt) else None, w=2, r=16)
        p.rect(x, y0, x + cw, y0 + 10, fill=cols[i], r=4)
        etiquette(p, x + 30, y0 + 66, ent, cols[i], 24)
        paragraphe(p, x + 30, y0 + 132, txt, REG(34) if i < 2 else GRAS(34), ENCRE, cw - 60, 48)
        if i < 2:
            fleche(p, [(x + cw + 12, (y0 + y1) / 2), (x + cw + gap - 12, (y0 + y1) / 2)], GRIS, 4)
    return p, {"ecran": ir + 1, "bande": 100, "zone_texte": (1100, 160, W, 215)}  # « Répond : … » qui s'allonge


ECRANS = {"identite": ecr_identite, "presente": ecr_presente, "message": ecr_message, "compare": ecr_compare,
          "chiffres": ecr_chiffres, "question": ecr_question, "piege": ecr_piege, "etapes": ecr_etapes,
          "corrections": ecr_corrections, "transition": ecr_transition, "vigilance": ecr_vigilance,
          "tableau": ecr_tableau, "gantt": ecr_gantt, "barres": ecr_barres, "schema": ecr_schema}


def lay_fiche(sc, k):
    p = Page()
    ecrans = sc["ecrans"]
    e = ecrans[min(k, len(ecrans) - 1)]
    sections = []
    for x in ecrans:
        if x.get("section") and x["section"] not in sections:
            sections.append(x["section"])
    bandeau_role(p, sc["person"], sections, e.get("section"))
    ECRANS[e["type"]](p, e, sc)
    return p, {"ecran": min(k, len(ecrans) - 1), "bande": 300}


LAYOUTS = {"titre": lay_titre, "chiffres": lay_chiffres, "liste": lay_liste, "criteres": lay_criteres,
           "architecture": lay_architecture, "fiche": lay_fiche, "risques": lay_risques}


def render_state(sc, k, chapitres):
    lay = LAYOUTS[sc["layout"]]
    p, meta = lay(sc, k)
    nav(p, chapitres, sc.get("section"))
    if meta.get("chemins"):  # même état sans ses nouveaux chemins, base du tracé progressif
        p2, _ = lay(sc, k, sans_chemins=True)
        nav(p2, chapitres, sc.get("section"))
        meta["sans"] = p2.im.resize((W, H), Image.LANCZOS)
    return p.im.resize((W, H), Image.LANCZOS), meta
