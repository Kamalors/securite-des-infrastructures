"""Génère la voix off avec Kyutai TTS 1.6B, en local, une unité à la fois (scènes 1 à 9 ; la scène 4 en 4a à 4d).

Usage : NO_TORCH_COMPILE=1 .venv-tts\\Scripts\\python scripts\\voix.py [--graine N] [unité ...]
        sans unité : génère celles qui manquent. Avec unités (ex. 04c 07) : les régénère.
Écrit out/voix/<unité>.wav (24 kHz mono) et out/voix/<unité>.json (texte et minutage brut des mots).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import sphn
import torch
from moshi.models.loaders import CheckpointInfo
from moshi.models.tts import DEFAULT_DSM_TTS_REPO, TTSModel

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "out" / "voix"
VOIX = "unmute-prod-website/fabieng-enhanced-v2.wav"

# Graphies « au son », pour la voix seulement, quand le moteur lit mal la graphie du script.
# Chaque remplacement garde le même nombre de mots, pour que le minutage reste aligné sur le script.
AU_SON: dict[str, str] = {
    "S-D-WAN": "SD-WAN",  # « S-D-WAN » était lu « S de WAN »
    "Fortinet": "Fortinette",  # « Fortinet » était lu « fortiné »
}


def unites_du_script() -> dict[str, str]:
    """Texte de chaque unité, sans les balises entre crochets (propres à ElevenLabs)."""
    md = (RACINE / "script_video_rao_7min.md").read_text(encoding="utf-8")
    unites = {}
    for bloc in re.split(r"^#{2,3} ", md, flags=re.M)[1:]:
        titre, _, corps = bloc.partition("\n")
        m = re.match(r"Scène (\d+)", titre)
        cle = f"{int(m.group(1)):02d}" if m else None
        m = re.match(r"(4)([a-d])\.", titre)
        cle = f"04{m.group(2)}" if m else cle
        if cle is None or "**Voix** :" not in corps:
            continue
        texte = corps.split("**Voix** :")[1].split("\n---")[0]
        texte = re.sub(r"\[[a-z]+\]", " ", texte)
        unites[cle] = " ".join(texte.split())
    return unites


def main():
    args = sys.argv[1:]
    graine = 0
    if "--graine" in args:
        i = args.index("--graine")
        graine = int(args[i + 1])
        del args[i:i + 2]
    unites = unites_du_script()
    demandees = args or [u for u in unites if not (SORTIE / f"{u}.wav").exists()]
    SORTIE.mkdir(parents=True, exist_ok=True)

    tts = TTSModel.from_checkpoint_info(CheckpointInfo.from_hf_repo(DEFAULT_DSM_TTS_REPO), n_q=32, temp=0.6, device="cuda")
    attributs = tts.make_condition_attributes([tts.get_voice_path(VOIX)], cfg_coef=2.0)
    for u in demandees:
        texte = unites[u]
        dit = texte
        for ecrit, son in AU_SON.items():
            assert len(ecrit.split()) == len(son.split()), f"« {son} » doit garder le nombre de mots de « {ecrit} »"
            dit = dit.replace(ecrit, son)
        torch.manual_seed(graine)
        resultat = tts.generate([tts.prepare_script([dit], padding_between=1)], [attributs])
        with tts.mimi.streaming(1), torch.no_grad():
            pcm = np.concatenate(
                [np.clip(tts.mimi.decode(t[:, 1:, :]).cpu().numpy()[0, 0], -1, 1) for t in resultat.frames[tts.delay_steps:]],
                axis=-1)
        sphn.write_wav(str(SORTIE / f"{u}.wav"), pcm, tts.mimi.sample_rate)
        (SORTIE / f"{u}.json").write_text(json.dumps({
            "texte": texte,
            "dit": dit,
            "graine": graine,
            "pas_par_seconde": tts.mimi.frame_rate,
            "mots": resultat.all_transcripts[0],  # [mot, pas]
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"ok {u} : {len(pcm) / tts.mimi.sample_rate:.1f} s, {len(texte)} caractères, graine {graine}", flush=True)


if __name__ == "__main__":
    main()
