# -*- coding: utf-8 -*-
"""Contrôle du texte affiché (sous-titres, transcription) : python test_build.py"""
from build import chiffres, pour_affichage

CAS = {
    "cinq cent trente sites": "530 sites",
    "deux cent vingt et un mille quatre cent vingt-quatre euros hors taxes par mois": "221 424 € HT par mois",
    "quatre cent quatre-vingt-dix-huit agences": "498 agences",
    "sept virgule quatre-vingt-dix-sept millions d'euros": "7,97 M€",
    "vingt-deux euros quatorze par utilisateur": "22,14 € par utilisateur",
    "depuis mai deux mille vingt-six": "depuis mai 2026",
    "mille soixante tunnels, mille cent avec les partenaires, pour deux mille": "1 060 tunnels, 1 100 avec les partenaires, pour 2 000",
    "le six cents F ou le sept cents G": "le 600F ou le 700G",
    "Diapos dix-neuf, vingt et vingt et un": "Diapos 19, 20 et 21",
    "Deux, les schémas": "Deux, les schémas",
    "Fin. Deux points de vigilance, dont deux sièges.": "Fin. Deux points de vigilance, dont 2 sièges.",
    "au moins un million et demi d'euros": "au moins un million et demi d'euros",
    "quarante pour cent reliés": "40 % reliés",
    "en trois minutes trente": "en 3 min 30",
    "cent quatre-vingt-quinze mille euros par mois": "195 000 € par mois",
    "soixante et onze": "71",
    "un jour d'ingénieur": "un jour d'ingénieur",
    "Mille nomades de plus": "1 000 nomades de plus",
    "en trois virgule huit secondes": "en 3,8 secondes",
    "Neuf n'ont qu'une note courte": "Neuf n'ont qu'une note courte",
    "listées : neuf diapos": "listées : 9 diapos",
}
AFF = {
    "une sauvegarde dite trois-deux-un": "une sauvegarde dite 3-2-1",
    "Diapos un à quatre, puis vingt-quatre": "Diapos 1 à 4, puis 24",
    "un S-D WAN certifié H-D-S, dits I-P sec": "un SD-WAN certifié HDS, dits IPsec",
    "C'est le Wan, le réseau": "C'est le WAN, le réseau",
    "le coût total sur trente-six mois": "le coût total sur 36 mois",
}
for src, attendu in CAS.items():
    obtenu = chiffres(src).replace(" ", " ")
    assert obtenu == attendu, f"{src!r} -> {obtenu!r}, attendu {attendu!r}"
for src, attendu in AFF.items():
    obtenu = pour_affichage(src).replace(" ", " ")
    assert obtenu == attendu, f"{src!r} -> {obtenu!r}, attendu {attendu!r}"
print("ok", len(CAS) + len(AFF), "cas")
