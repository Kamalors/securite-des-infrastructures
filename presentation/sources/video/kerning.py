# -*- coding: utf-8 -*-
"""Crénage d'Instrument Sans lu dans le GPOS de la police, pour le moteur de texte de la vidéo (ecrans.py).
Sans le moteur Raqm, Pillow ignore le GPOS ; et la table « kern » qu'il sait lire est appliquée 64 fois trop faible
(constaté avec Pillow 12.3 et FreeType 2.14). Le crénage est donc appliqué par ecrans.py, caractère par caractère.
Usage : python kerning.py   ->  contrôle sur « SD-WAN », « AV », « To »."""
import struct
from functools import lru_cache
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent / "fonts"
POLICES = ["InstrumentSans-Regular", "InstrumentSans-Bold"]
# caractères susceptibles d'apparaître à l'écran : ASCII, lettres latines du français, ponctuation typographique
CARACTERES = "".join(chr(c) for c in range(32, 127)) + "".join(chr(c) for c in range(0xA0, 0x100)) + "œŒ‘’“”«»–—…·•€→"


def u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


def s16(b, o):
    return struct.unpack_from(">h", b, o)[0]


def u32(b, o):
    return struct.unpack_from(">I", b, o)[0]


def repertoire(b):
    return {b[12 + 16 * i:16 + 16 * i].decode("latin-1"): (u32(b, 20 + 16 * i), u32(b, 24 + 16 * i))
            for i in range(u16(b, 4))}


def cmap(b, t):
    """Caractère -> glyphe (sous-table Windows Unicode, format 4 ou 12)."""
    base, choix = t["cmap"][0], None
    for i in range(u16(b, base + 2)):
        pid, eid, off = struct.unpack_from(">HHI", b, base + 4 + 8 * i)
        fmt = u16(b, base + off)
        if pid == 3 and eid in (1, 10) and fmt in (4, 12) and (choix is None or fmt == 12):
            choix = (fmt, base + off)
    fmt, o = choix
    m = {}
    if fmt == 12:
        for i in range(u32(b, o + 12)):
            sc, ec, sg = struct.unpack_from(">III", b, o + 16 + 12 * i)
            m.update({c: sg + c - sc for c in range(sc, ec + 1)})
        return m
    seg2 = u16(b, o + 6)
    fins, debuts = o + 14, o + 16 + seg2
    deltas, plages = debuts + seg2, debuts + 2 * seg2
    for s in range(seg2 // 2):
        fin, debut, delta, ro = u16(b, fins + 2 * s), u16(b, debuts + 2 * s), s16(b, deltas + 2 * s), u16(b, plages + 2 * s)
        for c in range(debut, min(fin, 0xFFFE) + 1):
            g = (c + delta) & 0xFFFF if ro == 0 else u16(b, plages + 2 * s + ro + 2 * (c - debut))
            if ro and g:
                g = (g + delta) & 0xFFFF
            if g:
                m[c] = g
    return m


def couverture(b, o):
    if u16(b, o) == 1:
        return {u16(b, o + 4 + 2 * i): i for i in range(u16(b, o + 2))}
    r = {}
    for i in range(u16(b, o + 2)):
        s, e, idx = struct.unpack_from(">HHH", b, o + 4 + 6 * i)
        r.update({g: idx + g - s for g in range(s, e + 1)})
    return r


def classes(b, o):
    if u16(b, o) == 1:
        debut = u16(b, o + 2)
        return {debut + i: u16(b, o + 6 + 2 * i) for i in range(u16(b, o + 4))}
    r = {}
    for i in range(u16(b, o + 2)):
        s, e, c = struct.unpack_from(">HHH", b, o + 4 + 6 * i)
        r.update({g: c for g in range(s, e + 1)})
    return r


def x_advance(b, o, fmt):
    """XAdvance d'un ValueRecord ; XPlacement et YPlacement le précèdent s'ils sont présents."""
    return s16(b, o + 2 * bin(fmt & 0x3).count("1")) if fmt & 0x4 else 0


def pairpos(b, so, glyphes, kern, decides):
    """Sous-table PairPos (formats 1 et 2) : dans une recherche, la première sous-table qui s'applique l'emporte."""
    fmt, cov = u16(b, so), couverture(b, so + u16(b, so + 2))
    vf1, vf2 = u16(b, so + 4), u16(b, so + 6)
    t1, t2 = 2 * bin(vf1 & 0xFF).count("1"), 2 * bin(vf2 & 0xFF).count("1")
    if fmt == 1:
        for g1, idx in cov.items():
            if g1 not in glyphes:
                continue
            ps = so + u16(b, so + 10 + 2 * idx)
            for k in range(u16(b, ps)):
                rec = ps + 2 + k * (2 + t1 + t2)
                g2 = u16(b, rec)
                if g2 in glyphes and (g1, g2) not in decides:
                    decides.add((g1, g2))
                    kern[(g1, g2)] = kern.get((g1, g2), 0) + x_advance(b, rec + 2, vf1)
    elif fmt == 2:
        cd1, cd2 = classes(b, so + u16(b, so + 8)), classes(b, so + u16(b, so + 10))
        n2 = u16(b, so + 14)
        for g1 in cov:
            if g1 not in glyphes:
                continue
            for g2 in glyphes:
                if (g1, g2) not in decides:
                    decides.add((g1, g2))
                    rec = so + 16 + (cd1.get(g1, 0) * n2 + cd2.get(g2, 0)) * (t1 + t2)
                    kern[(g1, g2)] = kern.get((g1, g2), 0) + x_advance(b, rec, vf1)


def crenage_gpos(b, t, glyphes):
    """Somme des ajustements d'avance des recherches de la fonction « kern » (types 2 et 9), en unités de la police."""
    base = t["GPOS"][0]
    features, lookups = base + u16(b, base + 6), base + u16(b, base + 8)
    retenues = set()
    for i in range(u16(b, features)):
        if b[features + 2 + 6 * i:features + 6 + 6 * i] == b"kern":
            fo = features + u16(b, features + 6 + 6 * i)
            retenues.update(u16(b, fo + 4 + 2 * j) for j in range(u16(b, fo + 2)))
    kern = {}
    for li in sorted(retenues):
        lo, decides = lookups + u16(b, lookups + 2 + 2 * li), set()
        for si in range(u16(b, lo + 4)):
            so, typ = lo + u16(b, lo + 6 + 2 * si), u16(b, lo)
            if typ == 9:  # extension : le vrai type et la vraie sous-table sont plus loin
                typ, so = u16(b, so + 2), so + u32(b, so + 4)
            if typ == 2:
                pairpos(b, so, glyphes, kern, decides)
    return {p: v for p, v in kern.items() if v}


@lru_cache(None)
def crenage(chemin):
    """(caractère -> glyphe, {(glyphe1, glyphe2): ajustement en fraction d'em}) pour les caractères de CARACTERES."""
    b = Path(chemin).read_bytes()
    t = repertoire(b)
    m = cmap(b, t)
    glyphes = {ord(c): m[ord(c)] for c in CARACTERES if ord(c) in m}
    upem = u16(b, t["head"][0] + 18)
    return glyphes, {p: v / upem for p, v in crenage_gpos(b, t, set(glyphes.values())).items()}


def controle():
    glyphes, kern = crenage(FONTS / "InstrumentSans-Regular.ttf")
    k = {mot: kern.get((glyphes[ord(mot[0])], glyphes[ord(mot[1])]), 0) for mot in ("WA", "AV", "To", "nn")}
    print("crénage (fraction d'em) :", k)
    assert k["WA"] < -0.05 and k["To"] < -0.05 and k["nn"] == 0, "crénage GPOS mal lu"


if __name__ == "__main__":
    controle()
    print("ok")
