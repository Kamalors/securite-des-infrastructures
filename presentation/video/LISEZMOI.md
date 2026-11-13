# Vidéo : le projet RAO expliqué

**[projet_rao_explique.mp4](projet_rao_explique.mp4)** · 19 min 40 · 1920 × 1080 · voix off en français · 48 Mo

Cette vidéo sert à préparer la soutenance. Elle présente :
- le cas : le client, sa demande, la notation ;
- la finalité : ce que nous livrons, et pourquoi ;
- la solution, en une image ;
- **chacun des sept rôles** : diapos, durée, message clé, chiffres à citer, questions probables, points de vigilance, corrections à faire sur ses diapos et phrase de transition ;
- les problématiques du client et les obstacles rencontrés pendant le projet ;
- les règles pour les questions du jury et la suite du travail.

Chaque scène est un **chapitre** de la vidéo. Dans VLC (menu Lecture > Chapitre) ou dans le lecteur de Windows, on saute directement à sa fiche.

Les sous-titres sont intégrés à la vidéo, mais désactivés par défaut. Pour les afficher, passez par le menu Sous-titres de VLC. Dans un autre lecteur, ouvrez le fichier [sous-titres_fr.srt](sous-titres_fr.srt) livré avec la vidéo. Le texte complet est dans [TRANSCRIPTION.md](TRANSCRIPTION.md).

## Chapitres

| Début | Chapitre |
|---|---|
| 0:00 | Ouverture |
| 0:14 | Le cas · le client |
| 0:56 | Le cas · la demande |
| 1:41 | Le cas · la notation |
| 2:14 | La finalité |
| 3:16 | La solution |
| 4:16 | Rôle 1 · Farah, chef de projet |
| 5:51 | Rôle 2 · Valentin, architecte SD-WAN |
| 7:55 | Rôle 3 · Nolan, architecte datacenter |
| 9:32 | Rôle 4 · Fatih, sécurité des flux |
| 11:12 | Rôle 5 · Younes, exploitation et agences |
| 12:56 | Rôle 6 · Maxime, Zero Trust (ZTNA) |
| 14:27 | Rôle 7 · Diane, finances |
| 15:55 | Problématiques du client et de l'offre |
| 17:13 | Obstacles rencontrés pendant le projet |
| 18:31 | À retenir |

## À faire sur le diaporama avant la répétition

Le diaporama est privé : demandez à Maxime l'accès en écriture. La vidéo demande ces corrections :

| Diapo | Rôle | Ce qui est écrit | À faire |
|---|---|---|---|
| 1 | Farah | « [Nom du groupe] », « [Date de soutenance] » | Remplir |
| 5 | Valentin | note : « garantie de rétablissement en 8 heures » | Écrire « garantie de temps d'intervention de 8 h » |
| 8 | Nolan | « 64 TiB par DC inclus dans la licence, aucune baie de stockage à acheter » | Nuancer : il faut 70 à 80 TiB bruts par DC, une extension vSAN est probable |
| 15 et 18 | Maxime | « inclus dans la licence Standard », « Déjà payé », « 24 % du coût total » | ZTNA inclus côté utilisateur, mais licence à ajouter sur les 4 hubs (écart net d'au moins 1,5 M€) ; 25 % au lieu de 24 % |
| 22 | Valentin | « preuves horodatées et signées par empreinte » | Écrire « accompagnées de leurs empreintes SHA-256 » : une empreinte n'est pas une signature |
| 23 | Younes | note : « mot de passe faible » | Ne pas le dire : la cause du piratage n'est que probable |
| 9, 10, 11, 19 | Nolan, Fatih, Diane | FortiGate 600F | Dire « 600F ou son successeur » : le 700G, recoté au devis |
| 3, 6, 7, 8, 18, 19, 20, 22, 23 | plusieurs | note d'orateur courte | Écrire le texte à dire |

Pour la démonstration, le scénario est [docs/DEMO_EVE.md](../../docs/DEMO_EVE.md). La recette se lance depuis le PC de Maxime, qui détient la clé d'administration ; l'accès des autres membres est décrit dans [docs/ACCES_CAMARADES.md](../../docs/ACCES_CAMARADES.md).

## Documents corrigés en même temps que la vidéo

Les relecteurs de la vidéo ont trouvé des contradictions entre les documents du dépôt et nos propres réponses aux questions du jury (Q47, Q48). Elles ont été corrigées :
- `docs/OFFRE_TECHNIQUE.md` :
  - Fortinet n'est plus dit « Leader » du Magic Quadrant SASE 2026 (§ 4.4, annexe B) ;
  - le ZTNA est « compris côté utilisateur », avec une licence à ajouter sur les 4 FortiGate hubs (§ 1, § 12.3) ;
  - cette licence et l'EDR figurent dans les non-inclus (§ 16.4) ;
  - deux sources externes sont ajoutées en annexe B.
- `docs/CHIFFRAGE.md`, régénéré par `automation/chiffrage/calcul.py`, et `docs/GLOSSAIRE.md` : même correction sur le ZTNA et les non-inclus. Le prix ne change pas : 221 424 € HT par mois.
- `docs/QUESTIONS_JURY.md` (Q3, Q36, sources) et `docs/ROLES_SOUTENANCE.md` (fiches 1, 2, 3 et 6) : alignés sur ces corrections.
- [RAO_projet_explique.pdf](../RAO_projet_explique.pdf), corrigé dans le générateur `presentation/sources/generer.py` :
  - page 4 : « Les solutions techniques » ;
  - page 6 : 3 000 + 300 nomades, zone partenaire des 2 datacenters ;
  - page 11 : licence des hubs ;
  - page 18 : profils rédigés sans accord masculin ni féminin.

## La voix : pourquoi celle-ci

**Voix retenue : Microsoft « Rémy » (`fr-FR-RemyMultilingualNeural`), via la bibliothèque [edge-tts](https://github.com/rany2/edge-tts) 7.3.1, débit -6 %.**

Ce que disent les forums et les tests publiés (recherche du 13/11/2026) :
- Les voix Microsoft sont les voix gratuites et sans compte les plus recommandées pour une lecture longue en français. Les voix « Multilingual » sont présentées comme le choix le plus sûr pour un contenu technique : elles prononcent correctement les termes anglais ([iancr.com](https://iancr.com/tutoriels/tutoriel-edge-tts-voix-ia)).
- Un utilisateur génère 17 minutes d'audio avec ces voix et corrige les mots mal lus en les réécrivant au son ([bidouilledebian](https://bidouilledebian.wordpress.com/2026/08/23/samuser-avec-edge-tts/)). C'est la méthode suivie ici.
- Les modèles libres testés en français sont moins fiables sur une vingtaine de minutes :
  - XTTS v2 : selon [LinuxFr](https://linuxfr.org/users/mrlem/journaux/lecture-de-texte-avec-coqui-tts), les hallucinations sont trop fréquentes ;
  - Qwen3-TTS : un accent anglais dans environ 80 % des sorties ([discussion](https://github.com/QwenLM/Qwen3-TTS/discussions/230)) ;
  - Kokoro : une seule voix française, notée B- ([VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)).
- Kyutai TTS 1.6B est le seul modèle local évalué en français : MUSHRA 62,5, contre 66,4 pour ElevenLabs ([article](https://arxiv.org/html/2509.08753v2)). Aucun test ne le compare aux voix Microsoft : il reste le repli local.
- ElevenLabs et Cartesia sont les plus naturels en français, mais ils exigent un compte et une clé payante.
- Limites :
  - Reddit était inaccessible pendant la recherche ;
  - aucune écoute à l'aveugle en français ne compare ces voix entre elles ;
  - pour écouter vous-même : [voix edge-tts](https://huggingface.co/spaces/manzing/edge-tts-fr/tree/main/example), [voix Kyutai](https://kyutai.org/tts).
- Usage : le service est non officiel. Microsoft Q&A juge un usage personnel ou étudiant sans risque ([réponse](https://learn.microsoft.com/en-us/answers/questions/2392491/unofficial-edge-tts-api)), mais pas un usage commercial ([réponse](https://learn.microsoft.com/en-us/answers/questions/2088770/are-opensource-edge-tts-free-for-commercial-use)).

**Prononciation contrôlée par une machine.** Chaque phrase a été transcrite avec Whisper et comparée au texte prévu. Les mots mal compris ont été réécrits au son, pour la voix seulement, après quatre bancs d'essai qui comparaient plusieurs graphies. Avant correction :
- « datacenter » était compris « data santé » ;
- « FortiGate » était compris « fortiguette » ;
- « vSAN » était compris « V100 » ;
- « 530 sites » était compris « 536 ».

La liste des graphies corrigées est dans `LEXIQUE`, dans [build.py](../sources/video/build.py). Résultat final : similarité médiane de 0,95 entre le texte prévu et la transcription. Les écarts restants sont des orthographes de prénoms et des pluriels inaudibles.

## Comment elle a été faite

1. **Recherche** : choix de la voix (ci-dessus).
2. **Script** : 16 scènes et 103 phrases, écrites à partir des documents du dépôt (`docs/`, diaporama et notes d'orateur). Fichier [script.json](../sources/video/script.json).
3. **Critique par plusieurs agents**, en trois tours :
   - **premier tour**, cinq relecteurs : exactitude, préparation de l'oral, design, rythme, spectateur novice ;
   - **deuxième tour**, quatre relecteurs : exactitude, préparation de l'oral, visuel, rythme. Les constats des trois premiers ont été contre-vérifiés par des sceptiques chargés de les réfuter ;
   - **vérification finale**, trois vérificateurs et leurs sceptiques.

   Les relecteurs ne pouvaient pas écouter : ils se sont appuyés sur la transcription Whisper, sur des mesures (débit, durées, volume) et sur les images de la vidéo.
4. **Montage** :
   - [scenes.py](../sources/video/scenes.py) dessine chaque écran, avec les polices et couleurs du PDF explicatif ;
   - [build.py](../sources/video/build.py) synthétise la voix phrase par phrase, cale les révélations sur la voix, normalise le volume (-16 LUFS), écrit les sous-titres et les chapitres, puis encode avec ffmpeg.

## Régénérer la vidéo

Les voix des 103 phrases sont archivées dans [voix/](../sources/video/voix/), sous l'empreinte de leur texte. Sans modification du script, la vidéo se remonte donc sans le service de synthèse. Si une phrase change, elle seule est resynthétisée.

```powershell
cd presentation/sources/video
python -m pip install edge-tts==7.3.1 imageio-ffmpeg pillow numpy num2words
python test_build.py                                                       # contrôle du texte affiché
python build.py script.json ../preview/video --audio voix                  # environ 10 min ; ../preview est ignoré par git
python chapitres.py script.json ../preview/video ../../video/TRANSCRIPTION.md
python -m pip install faster-whisper; python mesures.py ../preview/video --asr    # facultatif : contrôle de prononciation
```

La vidéo produite est `../preview/video/projet_rao_explique.mp4`. L'option `--apercu` encode plus vite, en qualité moindre.
