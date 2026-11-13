# -*- coding: utf-8 -*-
"""Assemble la vidéo RAO : voix par phrase, chronologie, images révélées au rythme de la voix, montage ffmpeg.
Usage : python build.py script.json dossier_de_travail [--audio dossier_mp3] [--debit=-6%] [--apercu]
La voix de chaque phrase est mise en cache sous l'empreinte de son texte : seules les phrases modifiées sont resynthétisées."""
import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ecrans  # noqa: E402
from ecrans import H, W  # noqa: E402

PROGRESS_Y = ecrans.NAV_Y

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 48000
FPS = 30
# silences : avant la première phrase, entre deux phrases, entre deux scènes, entre deux chapitres, après la dernière
LEAD, BEAT_GAP, SCENE_GAP, SECTION_GAP, TAIL = 1.5, 0.65, 1.5, 2.0, 4.0
XF_BEAT, XF_SCENE, ANTICIPE = 0.35, 0.7, 0.30   # fondus (s) ; une révélation précède la voix de ANTICIPE
XF_ECRAN, D_CHEMIN, LARGEUR_TRACE = 0.5, 1.4, 34  # changement d'écran d'une fiche ; tracé progressif des chemins
XF_TEXTE = 0.6  # pendant un tracé, le chapeau du schéma s'efface puis réapparaît (zone_texte)


def run(args, **kw):
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)
    if r.returncode:
        raise RuntimeError(f"échec : {' '.join(map(str, args[:6]))}…\n{r.stderr[-1500:]}")
    return r


# ------------------------------------------------------------------ texte lu et texte affiché
# (motif, remplacement) appliqués au seul texte lu, validés par un banc d'essai : synthèse puis transcription Whisper.
# Sans eux, « datacenter » était compris « data santé », « Forti-Gate » « fortiguette », « V-SAN » « V100 ».
LEXIQUE = [
    (r"\b[Dd]atacenter(s?)\b", r"data-center\1"),
    (r"\bForti-Gate\b", "Forti-Guéite"),
    (r"\bForti-SASE\b", "FortiSASE"),
    (r"\bV-SAN\b", "vSAN"),
    (r"\bR-P-O et R-T-O\b", "RPO et RTO"),
    (r"\bS-D WAN\b", "S-D-WAN"),
    (r"\bYounes\b", "Younesse"),
    (r"\bChallenger\b", "tchalènndjeur"),   # second banc : sinon la phrase était mal découpée
    (r"\bS-I-E-M\b", "Siem"),               # « S-I-E-M » était compris « SEM »
    (r"\btébioctets\b", "tébi-octets"),
]

# graphie normale pour les sous-titres et la transcription (le texte lu épelle les sigles : « H-D-S »)
AFFICHAGE = [(r"\bS-D WAN\b", "SD-WAN"), (r"\bI-P sec\b", "IPsec"), (r"Ève N-G\b", "EVE-NG"),
             (r"\bForti-(Gate|SASE|net|Manager)\b", r"Forti\1"), (r"\bV-SAN\b", "vSAN"), (r"\bMo-baïk\b", "MOBIKE"),
             (r"\bWazou\b", "Wazuh"), (r"\btéra-octets\b", "téraoctets"), (r"\btrois-deux-un\b", "3-2-1"),
             (r"\b[Dd]iapos un\b", "Diapos 1"), (r"\bfichier Démo Ève\b", "fichier DEMO_EVE"), (r"\bWan\b", "WAN"),
             (r"\bopérateur ([AB])\b", "opérateur \\1")]

# ---- nombres en lettres -> chiffres (sous-titres, transcription)
_VAL = {"zéro": 0, "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8,
        "neuf": 9, "dix": 10, "onze": 11, "douze": 12, "treize": 13, "quatorze": 14, "quinze": 15, "seize": 16,
        "vingt": 20, "vingts": 20, "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60,
        "cent": 100, "cents": 100, "mille": 1000}
_NW = "(?:" + "|".join(sorted(_VAL, key=len, reverse=True)) + ")"
_DIZ = "".join(f"(?<={d})|" for d in ("vingt", "trente", "quarante", "cinquante", "soixante"))[:-1]
_RUN = rf"{_NW}(?:[ -]{_NW}|(?:{_DIZ}) et (?:une?|onze)\b)*"
_NOMBRE = re.compile(rf"\b(?P<ent>{_RUN})(?: virgule (?P<dec>{_RUN}))?\b(?P<mult> millions?| milliards?)?", re.I)
# unités collées au nombre par une espace insécable : jamais « 221 000 » en fin de ligne et « € HT » au début de la suivante
_POST = [(r"(\d) euros hors taxes\b", "\\1\u00a0€\u00a0HT"), (r"(\d) millions? d'euros\b", "\\1\u00a0M€"),
         (r"(\d) euros (\d{2})\b", "\\1,\\2\u00a0€"), (r"(\d) euros\b", "\\1\u00a0€"),
         (r"(\d) minutes (\d{2})\b", "\\1\u00a0min\u00a0\\2"), (r"\b(\d+) ([FG])\b", r"\1\2"),
         (r"(\d) mois\b", "\\1\u00a0mois")]


def _valeur(texte):
    """« quatre-vingt-dix-huit » -> 98 ; None si la suite de mots n'est pas un seul nombre (« trois-deux-un »)."""
    total, cur = 0, 0
    for m in re.split(r"[ -]+", texte.lower()):
        if m == "et":
            continue
        v, bas = _VAL[m], cur % 100
        if m.startswith("vingt") and bas == 4:      # quatre-vingt(s)
            cur += 76
        elif v < 100:
            if bas and not ((bas % 10 == 0 and v < 10) or (bas in (60, 80) and 10 <= v < 20)):
                return None
            cur += v
        elif v == 100:
            if cur >= 100:
                return None
            cur = (cur or 1) * 100
        else:                                        # mille
            if total:
                return None
            total, cur = (cur or 1) * 1000, 0
    return total + cur


def _fmt(n):
    annee = 1900 <= n <= 2099 and n % 100
    return str(n) if n < 1000 or annee else f"{n:,}".replace(",", " ")


def chiffres(texte):
    texte = re.sub(r" ?\bpour cent\b", " %", texte)

    def rempl(m):
        ent, dec, mult = m.group("ent"), m.group("dec"), m.group("mult") or ""
        n = _valeur(ent)
        d = _valeur(dec) if dec else None
        if n is None or (dec and d is None):
            return m.group(0)
        if ent.lower() in ("un", "une") and not dec:
            return m.group(0)                        # article (« un pare-feu », « un million et demi »)
        debut = texte[:m.start()]
        if n < 10 and not dec and not mult and (not debut.strip() or re.search(r"[.!?]\s*$", debut)):
            return m.group(0)                        # jamais un chiffre en début de phrase : « Deux, les schémas… »
        return _fmt(n) + (f",{d}" if dec else "") + mult

    texte = _NOMBRE.sub(rempl, texte)
    for motif, r in _POST:
        texte = re.sub(motif, r, texte)
    return texte


def pour_affichage(texte):
    for motif, rempl in AFFICHAGE:  # cas particuliers d'abord (« S-D WAN » donne « SD-WAN », pas « SD WAN »)
        texte = re.sub(motif, rempl, texte)
    texte = re.sub(r"\b[A-Z](?:-[A-Z])+\b", lambda m: m.group(0).replace("-", ""), texte)
    return chiffres(texte)


def en_lettres(t):
    """« 221 424 € », « 7,97 M€ », « 20 % » -> mots : longueur parlée d'un sous-titre, comparaison avec Whisper."""
    from num2words import num2words
    t = re.sub(r"(\d)[\s  ](?=\d{3}\b)", r"\1", t)
    t = t.replace("%", " pour cent ").replace("M€", " millions d'euros ").replace("€", " euros ")
    t = re.sub(r"(\d+),(\d+)", lambda m: f"{num2words(int(m[1]), lang='fr')} virgule {num2words(int(m[2]), lang='fr')}", t)
    return re.sub(r"\d+", lambda m: num2words(int(m[0]), lang="fr"), t)


def prononcer(texte):
    for motif, rempl in LEXIQUE:
        texte = re.sub(motif, rempl, texte)
    return texte


# ------------------------------------------------------------------ voix
def empreinte(texte, voix, debit, ton):
    return hashlib.sha1(f"{voix}|{debit}|{ton}|{texte}".encode("utf-8")).hexdigest()[:16]


async def _edge(texte, voix, debit, ton, mp3, sem):
    import edge_tts
    async with sem:
        for essai in range(4):
            try:
                await edge_tts.Communicate(texte, voix, rate=debit, pitch=ton).save(str(mp3))
                return
            except Exception:  # coupure réseau : on réessaie
                if essai == 3:
                    raise
                await asyncio.sleep(2 + essai * 3)


def synthese_edge(taches, voix, ton):
    async def tout():
        sem = asyncio.Semaphore(4)
        await asyncio.gather(*(_edge(t, voix, d, ton, mp3, sem) for t, mp3, d in taches))
    asyncio.run(tout())


def vers_wav(src, dst):
    """48 kHz mono, silences de début et de fin retirés (les pauses sont ensuite maîtrisées par la chronologie)."""
    trim = "silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.05," \
           "areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.08,areverse"
    run([FFMPEG, "-y", "-i", str(src), "-af", trim, "-ar", str(SR), "-ac", "1", "-sample_fmt", "s16", str(dst)])


def lire_wav(path):
    with wave.open(str(path)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)


# ------------------------------------------------------------------ chronologie
def chronologie(script, durees, metas=None):
    """durees[(si, bi)] -> secondes. Renvoie les phrases (si, bi, début, durée), les changements d'image
    (instant, (scène, état), durée de la transition), le début de chaque scène et la durée totale.
    metas[(si, k)] : un état qui trace des chemins a une transition plus longue (D_CHEMIN) ; un changement
    d'écran dans une fiche passe par le fond (XF_ECRAN). « pause » sur un beat : silence ajouté après lui."""
    metas = metas or {}
    t, beats, cles, debuts, gap = LEAD, [], [], [], 0.0
    scs = script["scenes"]
    for si, sc in enumerate(scs):
        if si:
            gap = SECTION_GAP if sc.get("section") != scs[si - 1].get("section") else SCENE_GAP
            t += gap
        for bi, b in enumerate(sc["beats"]):
            if bi:
                t += BEAT_GAP
            cle = (si, max(0, b.get("reveal", 0)))
            beats.append((si, bi, t, durees[(si, bi)]))
            if not cles:
                cles.append((0.0, cle, 0.0))
                debuts.append(0.0)
            elif cles[-1][1] != cle:
                if si != cles[-1][1][0]:   # nouvelle scène : fondu centré dans le silence qui la précède
                    t0 = t - gap / 2 - XF_SCENE / 2
                    cles.append((t0, cle, XF_SCENE))
                    debuts.append(t0)
                else:
                    m, avant = metas.get(cle, {}), metas.get(cles[-1][1], {})
                    xf = D_CHEMIN if m.get("chemins") else XF_ECRAN if m.get("ecran") != avant.get("ecran") else XF_BEAT
                    cles.append((max(cles[-1][0] + cles[-1][2], t - ANTICIPE), cle, xf))
            t += durees[(si, bi)] + b.get("pause", 0)
    return beats, cles, debuts, t + TAIL


def sections_de(script):
    sections = []
    for sc in script["scenes"]:
        if sc.get("section") and sc["section"] not in sections and sc["layout"] not in ("ouverture", "titre"):
            sections.append(sc["section"])
    return sections


# ------------------------------------------------------------------ sous-titres
MAX_CUE, MAX_LIGNE, MIN_DUREE = 82, 44, 1.2


_MAL_COUPE = re.compile(r"\b(?:le|la|les|de|du|des|un|une|à|au|aux|et|en|par|pour|sur|dans|sans|ne|ce|ses|son|sa|nos|vos|que|qui)$")  # jamais de coupure après


def _moities(m):
    """Morceau trop long : moitiés équilibrées (pas de reste orphelin comme « B. » en tête du bloc suivant)."""
    if len(m) <= MAX_CUE:
        return [m]
    a, b = _deux_lignes(m, MAX_CUE).split("\n")
    return _moities(a) + _moities(b)


def _reequilibre(t):
    """Deux blocs d'au moins 25 caractères : coupure à la ponctuation la plus centrale, sinon entre deux mots."""
    m = [x for x in re.split(r"(?<=[,;:]) +", t) if x]
    coupes = [(" ".join(m[:k]), " ".join(m[k:])) for k in range(1, len(m))]
    coupes = [c for c in coupes if min(map(len, c)) >= 25 and max(map(len, c)) <= MAX_CUE]
    return list(min(coupes, key=lambda c: max(map(len, c)))) if coupes else _moities(t)


def _decoupe(texte):
    """Blocs de 84 caractères au plus : coupure aux fins de phrase, puis à la ponctuation, puis entre deux mots.
    Les espaces insécables (« 221 424 € ») ne sont jamais des points de coupure."""
    phrases = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", texte) if s.strip()]
    blocs = []
    for ph in phrases:
        if len(ph) <= MAX_CUE:
            blocs.append(ph)
            continue
        morceaux = [m.strip() for m in re.split(r"(?<=[,;:]) +", ph) if m.strip()]
        bp, cur = [], ""
        for m in morceaux:
            if len(m) > MAX_CUE:
                if cur:
                    bp.append(cur)
                *debut, cur = _moities(m)
                bp += debut
            elif len(cur) + len(m) + 1 <= MAX_CUE:
                cur = (cur + " " + m).strip()
            else:
                bp.append(cur)
                cur = m
        if cur:
            bp.append(cur)
        if len(bp) > 1 and len(bp[-1]) < 25:  # reste orphelin : les deux derniers blocs rééquilibrés
            bp[-2:] = _reequilibre(bp[-2] + " " + bp[-1])
        blocs += bp
    fusion = []  # regroupe les blocs courts avec le suivant tant que la limite le permet
    for b in blocs:
        if fusion and len(fusion[-1]) + len(b) + 1 <= MAX_CUE and (len(fusion[-1]) < 30 or len(b) < 30):
            fusion[-1] = fusion[-1] + " " + b
        else:
            fusion.append(b)
    return fusion


def _deux_lignes(b, limite=MAX_LIGNE):
    """Deux lignes équilibrées, coupées de préférence après une ponctuation, jamais après un nombre ou un article."""
    if len(b) <= limite:
        return b
    mots, meilleur = b.split(" "), None
    for i in range(1, len(mots)):
        l1, l2 = " ".join(mots[:i]), " ".join(mots[i:])
        score = abs(len(l1) - len(l2)) + (0 if l1[-1] in ",;:." else 6) + (100 if l1[-1].isdigit() else 12 if _MAL_COUPE.search(l1) else 0) \
            + (100 if max(len(l1), len(l2)) > limite else 0)
        if meilleur is None or score < meilleur[0]:
            meilleur = (score, l1, l2)
    return meilleur[1] + "\n" + meilleur[2]


def _poids(b):
    """Durée relative d'un bloc : sa longueur parlée, plus les pauses de ponctuation et les sigles épelés."""
    t = re.sub(r"\bHT\b", "hors taxes", re.sub(r"\bmin\b", "minutes", en_lettres(b)))
    return len(t) + 4 * len(re.findall(r"[,;]", b)) + 8 * len(re.findall(r"[.:?!]", b)) \
        + 2 * len(re.findall(r"[A-Z](?=[A-Z])|(?<=[A-Z])[A-Z]", b))


def sous_titres(script, beats, chemin):
    """Sous-titres SRT en chiffres ; durée de chaque bloc au prorata de sa longueur parlée, 1,2 s au minimum."""
    def ts(x):  # arrondi à la milliseconde d'abord : 394,9996 s donne 00:06:35,000, pas 00:06:34,000
        ms = round(x * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    cues, n = [], 1
    for si, bi, t0, d in beats:
        blocs = _decoupe(pour_affichage(script["scenes"][si]["beats"][bi]["say"].strip()))
        # un bloc qu'aucune coupure ne met en deux lignes de 44 caractères devient deux blocs d'une ligne
        blocs = [x for b in blocs for x in ([b] if max(map(len, _deux_lignes(b).split("\n"))) <= MAX_LIGNE
                                             else _deux_lignes(b, len(b) // 2 + 12).split("\n"))]
        poids = [_poids(b) for b in blocs]
        durees = [d * p / (sum(poids) or 1) for p in poids]
        for i, du in enumerate(durees):  # un bloc trop bref emprunte du temps à son voisin
            if du < MIN_DUREE and len(durees) > 1:
                j = i - 1 if i else i + 1
                manque = min(MIN_DUREE - du, max(0.0, durees[j] - MIN_DUREE))
                durees[i] += manque
                durees[j] -= manque
        t = t0
        for b, du in zip(blocs, durees):
            cues.append(f"{n}\n{ts(t)} --> {ts(t + du)}\n{_deux_lignes(b)}\n")
            n += 1
            t += du
    Path(chemin).write_text("\n".join(cues), encoding="utf-8")


def chapitres_ffmetadata(script, debuts, duree, chemin):
    """Chapitres MP4 (un par scène) : chaque membre saute directement à son rôle depuis le lecteur."""
    def esc(s):
        return re.sub(r"([=;#\\\n])", r"\\\1", s)
    lignes = [";FFMETADATA1", f"title={esc(script.get('title', 'Le projet RAO expliqué'))}"]
    debuts = [0.0] + [d + XF_SCENE for d in debuts[1:]]  # un chapitre commence sur son propre écran, fondu fini
    fins = debuts[1:] + [duree]
    for sc, t0, t1 in zip(script["scenes"], debuts, fins):
        lignes += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(t0 * 1000)}", f"END={int(t1 * 1000)}",
                   f"title={esc(sc.get('chapitre') or sc['title'])}"]
    Path(chemin).write_text("\n".join(lignes) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ images
def images_etats(script, dossier):
    """Une image par état ; la méta décrit l'écran affiché et les chemins à tracer à l'entrée de l'état."""
    sections = sections_de(script)
    cache, metas = {}, {}
    for si, sc in enumerate(script["scenes"]):
        for k in sorted({max(0, b.get("reveal", 0)) for b in sc["beats"]}):
            im, meta = ecrans.render_state(sc, k, sections)
            cache[(si, k)], metas[(si, k)] = im, meta
            im.save(dossier / f"etat_{si:02d}_{k}.png")
    return cache, metas


def couleur_barre(im):
    return ecrans.RESEAU


def _prefixe(chemin, f):
    """Début d'un chemin brisé, sur la fraction f de sa longueur."""
    segs = list(zip(chemin, chemin[1:]))
    longs = [((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5 for a, b in segs]
    reste, out = f * sum(longs), [chemin[0]]
    for (a, b), lg in zip(segs, longs):
        if reste >= lg:
            out.append(b)
            reste -= lg
        else:
            r = reste / lg if lg else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            break
    return out


def masque_trace(chemins, f, seq=False):
    """Blanc sur la partie déjà tracée des chemins (fraction f de leur longueur), noir ailleurs.
    seq : le premier chemin se trace d'abord (40 % du temps), les autres ensuite, dans l'ordre du flux."""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for j, ch in enumerate(chemins):
        fj = f if not seq else (min(1.0, f / .4) if j == 0 else max(0.0, (f - .4) / .6))
        if fj > 0:
            d.line(_prefixe(ch, fj), fill=255, width=LARGEUR_TRACE, joint="curve")
    return m


def x_barre(t, bornes):
    """Barre par chapitre : chaque chapitre remplit son propre segment, sous son repère."""
    n = len(bornes) - 1
    i = next((j for j in range(n - 1, -1, -1) if bornes[j] <= t), None)
    if i is None:
        return ecrans.MARGE
    return ecrans.MARGE + (ecrans.DROITE - ecrans.MARGE) * (i + min(1.0, (t - bornes[i]) / (bornes[i + 1] - bornes[i]))) / n


def _creux(im, avant, apres, zone, a):
    """Texte remplacé au même endroit : l'ancien s'efface jusqu'au fond, puis le nouveau apparaît (pas de mélange)."""
    za, zb = avant.crop(zone), apres.crop(zone)
    if za.tobytes() != zb.tobytes():
        fond = Image.new("RGB", za.size, apres.getpixel((5, 5)))
        im.paste(Image.blend(za, fond, 2 * a) if a < 0.5 else Image.blend(fond, zb, 2 * a - 1), zone[:2])
    return im


def _adouci(a):
    a = min(1.0, max(0.0, a))
    return a * a * (3 - 2 * a)


def image_a(t, i, cles, cache, metas=None):
    metas = metas or {}
    t0, cle, xf = cles[i]
    if not (xf and t < t0 + xf and i > 0):
        return cache[cle].copy()
    a = _adouci((t - t0) / xf)
    avant, apres = cache[cles[i - 1][1]], cache[cle]
    m, m0 = metas.get(cle, {}), metas.get(cles[i - 1][1], {})
    zone = m.get("zone_texte") if m.get("zone_texte") == m0.get("zone_texte") else None
    if cle[0] == cles[i - 1][1][0] and m.get("chemins"):
        base = Image.blend(avant, m["sans"], min(1.0, (t - t0) / XF_BEAT))  # le reste du nouvel état, en fondu
        im = Image.composite(apres, base, masque_trace(m["chemins"], a, m.get("sequentiel")))      # puis les chemins, au fil du tracé
        return _creux(im, avant, apres, zone, _adouci((t - t0) / XF_TEXTE)) if zone else im
    if cle[0] == cles[i - 1][1][0] and m.get("ecran") == m0.get("ecran"):
        im = Image.blend(avant, apres, a)
        return _creux(im, avant, apres, zone, a) if zone else im
    # changement de scène : passage par le fond de la scène qui arrive (pas de superposition de deux mises en page)
    # même passage par le fond pour un changement d'écran dans une fiche, en gardant l'en-tête de la fiche en place
    fond = Image.new("RGB", (W, H), apres.getpixel((5, 5)))
    im = Image.blend(avant, fond, 2 * a) if a < 0.5 else Image.blend(fond, apres, 2 * a - 1)
    if avant.getpixel((5, 5)) == apres.getpixel((5, 5)):  # même fond : les repères (et l'en-tête de fiche) restent
        bande = m.get("bande", 100) if cle[0] == cles[i - 1][1][0] else 100  # fiche : l'en-tête du rôle reste
        im.paste(Image.blend(avant.crop((0, 0, W, bande)), apres.crop((0, 0, W, bande)), a), (0, 0))
    return im


def encoder(cles, cache, metas, duree, bornes, audio, srt, chap, sortie, apercu=False):
    n = int(round(duree * FPS))
    vcodec = ["-c:v", "libx264", "-preset", "veryfast" if apercu else "slow", "-crf", "26" if apercu else "20",
              "-tune", "stillimage", "-pix_fmt", "yuv420p"]
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-nostats",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(audio), "-i", str(srt), "-i", str(chap),
           "-map", "0:v", "-map", "1:a", "-map", "2:s", "-map_metadata", "3", "-map_chapters", "3", *vcodec,
           "-c:a", "aac", "-b:a", "160k", "-c:s", "mov_text", "-metadata:s:a:0", "language=fre",
           "-metadata:s:s:0", "language=fre", "-disposition:s:0", "0",  # ne suffit pas en MP4 : voir couper_sous_titres_par_defaut()
           "-movflags", "+faststart", str(sortie)]
    # journal dans un fichier : un tube non lu se remplirait et bloquerait ffmpeg (interblocage)
    journal = open(Path(sortie).with_suffix(".log"), "w+b")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=journal)
    i = 0
    for f in range(n):
        t = f / FPS
        while i + 1 < len(cles) and cles[i + 1][0] <= t:
            i += 1
        im = image_a(t, i, cles, cache, metas)
        ImageDraw.Draw(im).line([(ecrans.MARGE, PROGRESS_Y), (x_barre(t, bornes), PROGRESS_Y)], fill=couleur_barre(im), width=3)
        if t > duree - 1:  # fondu au noir sur la dernière seconde
            im = Image.blend(im, Image.new("RGB", (W, H)), min(1.0, t - duree + 1))
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    code = proc.wait()
    journal.seek(0)
    err = journal.read().decode(errors="replace")
    journal.close()
    if code:
        raise RuntimeError(err[-2000:])


def couper_sous_titres_par_defaut(mp4):
    """Le multiplexeur MP4 de ffmpeg réactive la piste malgré -disposition:s:0 0 : on éteint le bit « enabled » de son tkhd,
    pour que la piste soit proposée sans s'afficher d'office."""
    with open(mp4, "r+b") as f:
        tete = f.read(8_000_000)                          # moov en tête grâce à +faststart
        i = tete.find(b"hdlr" + bytes(8) + b"sbtl")       # hdlr de la piste de sous-titres
        j = tete.rfind(b"tkhd", 0, i)                     # tkhd de la même piste
        assert i > 0 and j > 0, "piste de sous-titres introuvable"
        f.seek(j + 7)                                     # octet de poids faible des flags
        f.write(bytes([tete[j + 7] & 0xFE]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("sortie")
    ap.add_argument("--audio", help="dossier des MP3 de la voix (défaut : <sortie>/audio)")
    ap.add_argument("--voix", default="fr-FR-RemyMultilingualNeural")
    ap.add_argument("--debit", default="-6%")
    ap.add_argument("--ton", default="+0Hz")
    ap.add_argument("--apercu", action="store_true")
    a = ap.parse_args()
    script = json.loads(Path(a.script).read_text(encoding="utf-8"))
    out = Path(a.sortie)
    dmp3 = Path(a.audio) if a.audio else out / "audio"
    for d in (dmp3, out / "wav", out / "etats"):
        d.mkdir(parents=True, exist_ok=True)

    taches, durees, fichiers = [], {}, {}
    for si, sc in enumerate(script["scenes"]):
        for bi, b in enumerate(sc["beats"]):
            lu, debit = prononcer(b["say"]), b.get("debit", a.debit)
            h = empreinte(lu, a.voix, debit, a.ton)
            mp3, wav = dmp3 / f"{h}.mp3", out / "wav" / f"{h}.wav"
            fichiers[(si, bi)] = (lu, mp3, wav)
            if not mp3.exists() and (lu, mp3, debit) not in taches:
                taches.append((lu, mp3, debit))
    if taches:
        print(f"voix : {len(taches)} phrases à synthétiser")
        synthese_edge(taches, a.voix, a.ton)
    for (si, bi), (lu, mp3, wav) in fichiers.items():
        if not wav.exists():
            vers_wav(mp3, wav)
        durees[(si, bi)] = len(lire_wav(wav)) / SR

    print("images…")
    cache, metas = images_etats(script, out / "etats")
    beats, cles, debuts, duree = chronologie(script, durees, metas)
    sections = sections_de(script)
    premiere = {s: next(si for si, sc in enumerate(script["scenes"]) if sc.get("section") == s) for s in sections}
    bornes = [debuts[premiere[s]] + XF_SCENE / 2 for s in sections] + [duree]
    print(f"durée : {duree / 60:.1f} min, {len(beats)} phrases, {len(cles)} changements d'image")

    piste = np.zeros(int(round(duree * FPS)) * SR // FPS, dtype=np.int32)  # exactement la durée de l'image
    for si, bi, t0, d in beats:
        s = lire_wav(fichiers[(si, bi)][2]).astype(np.int32)
        i0 = int(t0 * SR)
        piste[i0:i0 + len(s)] += s[:max(0, len(piste) - i0)]
    brut = out / "voix_brute.wav"
    with wave.open(str(brut), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.clip(piste, -32768, 32767).astype(np.int16).tobytes())
    # normalisation du volume (EBU R128, -16 LUFS, crête -1,5 dB), en deux passes
    mesure = run([FFMPEG, "-hide_banner", "-i", str(brut), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
                  "-f", "null", "-"]).stderr
    m = json.loads(mesure[mesure.rfind("{"):mesure.rfind("}") + 1])
    norm = out / "voix.wav"
    run([FFMPEG, "-y", "-i", str(brut), "-af",
         f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
         "-ar", str(SR), str(norm)])

    srt = out / "sous-titres_fr.srt"  # autre nom que la vidéo : VLC ne le charge pas d'office
    sous_titres(script, beats, srt)
    chap = out / "chapitres.txt"
    chapitres_ffmetadata(script, debuts, duree, chap)
    (out / "chronologie.json").write_text(json.dumps(
        {"duree": duree, "scenes": [{"si": si, "id": sc["id"], "debut": round(t0, 2),
                                     "chapitre": sc.get("chapitre") or sc["title"]}
                                    for si, (sc, t0) in enumerate(zip(script["scenes"], debuts))],
         "beats": [{"si": si, "scene": script["scenes"][si]["id"], "beat": bi, "debut": round(t0, 2),
                    "duree": round(d, 2), "texte": script["scenes"][si]["beats"][bi]["say"],
                    "lu": fichiers[(si, bi)][0], "audio": str(fichiers[(si, bi)][2])}
                   for si, bi, t0, d in beats],
         "changements": [{"t": round(t0, 2), "scene": si, "etat": k, "transition": xf}
                         for t0, (si, k), xf in cles]}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("encodage…")
    sortie = out / ("apercu.mp4" if a.apercu else "projet_rao_explique.mp4")
    encoder(cles, cache, metas, duree, bornes, norm, srt, chap, sortie, a.apercu)
    couper_sous_titres_par_defaut(sortie)
    print("ok :", sortie, f"{sortie.stat().st_size / 1e6:.1f} Mo")


if __name__ == "__main__":
    main()
