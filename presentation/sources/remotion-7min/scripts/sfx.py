"""Effets sonores synthétisés localement (aucun fichier tiers, donc aucune licence à gérer).

Usage : python scripts/sfx.py   ->  public/sfx/transition.wav, public/sfx/compteur.wav
"""
import wave
from pathlib import Path

import numpy as np

SR = 44100
SORTIE = Path(__file__).resolve().parent.parent / "public" / "sfx"
rng = np.random.default_rng(7)  # graine fixe : mêmes fichiers à chaque exécution


def ecrire(nom, x, crete=0.5):
    x = x / np.max(np.abs(x)) * crete
    with wave.open(str(SORTIE / nom), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((x * 32767).astype(np.int16).tobytes())


def transition(duree=0.55):
    """Souffle doux : bruit filtré dont la fréquence de coupure monte puis redescend."""
    n = int(duree * SR)
    t = np.arange(n) / n
    bruit = rng.standard_normal(n)
    coupure = 300 + 3200 * np.sin(np.pi * t) ** 2  # Hz
    a = 1 - np.exp(-2 * np.pi * coupure / SR)
    y = np.zeros(n)
    etat = 0.0
    for i in range(n):  # passe-bas à un pôle, coupure variable
        etat += a[i] * (bruit[i] - etat)
        y[i] = etat
    return y * np.sin(np.pi * t) ** 2


def compteur(duree_tics=0.9, queue=0.5):
    """Tics rapides qui ralentissent, puis une note claire quand le compteur s'arrête."""
    n = int((duree_tics + queue) * SR)
    y = np.zeros(n)
    tic = np.sin(2 * np.pi * 1800 * np.arange(int(0.012 * SR)) / SR) * np.exp(-np.arange(int(0.012 * SR)) / (0.003 * SR))
    instant = 0.0
    ecart = 0.028
    while instant < duree_tics:
        i = int(instant * SR)
        y[i:i + len(tic)] += 0.5 * tic
        instant += ecart
        ecart *= 1.07  # ralentit
    i0 = int(duree_tics * SR)
    t = np.arange(n - i0) / SR
    y[i0:] += (np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1320 * t)) * np.exp(-t / 0.12)
    return y


SORTIE.mkdir(parents=True, exist_ok=True)
ecrire("transition.wav", transition())
ecrire("compteur.wav", compteur())
print("ok", [p.name for p in sorted(SORTIE.glob("*.wav"))])
