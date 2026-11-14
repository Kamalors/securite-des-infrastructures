"""Synthèse vocale locale avec Kyutai TTS 1.6B (anglais / français), sur carte graphique.

Usage : .venv-tts\\Scripts\\python scripts\\kyutai_tts.py texte.txt dossier_sortie voix1 [voix2 ...]
Les voix sont des chemins du dépôt Hugging Face kyutai/tts-voices.
Écrit dossier_sortie/<nom de la voix>.wav (24 kHz mono).
D'après scripts/tts_pytorch.py du dépôt kyutai-labs/delayed-streams-modeling.
"""
import sys
from pathlib import Path

import numpy as np
import sphn
import torch
from moshi.models.loaders import CheckpointInfo
from moshi.models.tts import DEFAULT_DSM_TTS_REPO, TTSModel

texte = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
sortie = Path(sys.argv[2])
sortie.mkdir(parents=True, exist_ok=True)

tts = TTSModel.from_checkpoint_info(CheckpointInfo.from_hf_repo(DEFAULT_DSM_TTS_REPO), n_q=32, temp=0.6, device="cuda")
entrees = tts.prepare_script([texte], padding_between=1)
for voix in sys.argv[3:]:
    attributs = tts.make_condition_attributes([tts.get_voice_path(voix)], cfg_coef=2.0)
    resultat = tts.generate([entrees], [attributs])
    with tts.mimi.streaming(1), torch.no_grad():
        pcm = np.concatenate(
            [np.clip(tts.mimi.decode(t[:, 1:, :]).cpu().numpy()[0, 0], -1, 1) for t in resultat.frames[tts.delay_steps:]],
            axis=-1)
    sphn.write_wav(str(sortie / (Path(voix).stem + ".wav")), pcm, tts.mimi.sample_rate)
    print("ok", voix, f"{len(pcm) / tts.mimi.sample_rate:.1f} s", flush=True)
