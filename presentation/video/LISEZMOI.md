# Vidéo : le projet RAO expliqué

**[projet_rao_explique.mp4](projet_rao_explique.mp4)** · 19 min 56 · 1920 × 1080 · voix off en français · 52 Mo

Cette vidéo sert à préparer la soutenance. Elle présente :
- le cas : le client, sa demande, les volets attendus ;
- la finalité : ce que nous livrons, et pourquoi ;
- la solution, dont le schéma se construit au fil de la voix ;
- **chacun des sept rôles**, sur plusieurs écrans de même structure : diapos et durée, ce qu'il faut présenter, message clé, chiffres à citer, questions probables et réponses, pièges, corrections à faire sur ses diapos, phrase de transition ;
- les problématiques du client et les obstacles rencontrés pendant le projet, en trois temps : problème, conséquence, réponse ;
- ce qu'il faut retenir et la suite du travail.

Chaque scène est un **chapitre** de la vidéo. Dans VLC (menu Lecture > Chapitre) ou dans le lecteur de Windows, on saute directement à sa fiche.

Les sous-titres sont intégrés à la vidéo, mais désactivés par défaut. Pour les afficher, passez par le menu Sous-titres de VLC. Dans un autre lecteur, ouvrez le fichier [sous-titres_fr.srt](sous-titres_fr.srt) livré avec la vidéo. Le texte complet est dans [TRANSCRIPTION.md](TRANSCRIPTION.md).

## Chapitres

| Début | Chapitre |
|---|---|
| 0:00 | Ouverture |
| 0:15 | Le cas · le client |
| 0:57 | Le cas · la demande |
| 1:42 | Le cas · la notation |
| 2:14 | La finalité |
| 3:17 | La solution |
| 4:19 | Rôle 1 · Farah, chef de projet |
| 5:55 | Rôle 2 · Valentin, architecte SD-WAN |
| 8:00 | Rôle 3 · Nolan, architecte datacenter |
| 9:39 | Rôle 4 · Fatih, sécurité des flux |
| 11:20 | Rôle 5 · Younes, exploitation et agences |
| 13:04 | Rôle 6 · Maxime, Zero Trust (ZTNA) |
| 14:40 | Rôle 7 · Diane, finances |
| 16:10 | Problématiques du client et de l'offre |
| 17:28 | Obstacles rencontrés pendant le projet |
| 18:47 | À retenir |

## La refonte du 13/11 au soir

**Les écrans ont été refaits** pour une vidéo de formation plus lisible :
- **sobriété** : fond uni, une seule police (Instrument Sans), ni décor ni animation permanente. Le texte courant mesure au moins 30 px en 1920 × 1080 ; un écran trop chargé est découpé plutôt que réduit ;
- **couleurs fonctionnelles, les mêmes partout** : bleu canard pour le réseau et les tunnels, orange pour le Zero Trust et les nomades, rouge pour les refus, les pièges et les corrections à faire ;
- **la solution se construit au rythme de la voix** : sites, Internet et opérateurs, datacenters, tunnels SD-WAN qui se dessinent, bascule, nomades et FortiSASE, MFA, partenaires. Chaque étape reste affichée de 7 à 14 secondes ; la dernière montre le schéma complet ;
- **chaque fiche de rôle tient sur plusieurs écrans** : un en-tête commun (rôle, diapos, durée) et des onglets qui situent l'écran affiché. Les corrections sont toujours présentées comme à faire sur le diaporama, jamais comme faites ;
- **comparaisons** en colonnes retenu / écarté, **chiffres** avec leur unité et leur périmètre, **non-inclus** encadrés à part, **questions du jury** en trois temps : question, réponse courte, justification ;
- **problématiques et obstacles** en trois cartes : problème, conséquence, réponse. Quand la voix traite un point en deux phrases, la carte se complète à la seconde ;
- **transitions** courtes et sans musique : fondu de 0,35 s entre deux états, passage par le fond entre deux écrans d'une fiche (0,5 s) et entre deux scènes (0,7 s). Un texte remplacé au même endroit s'efface avant que le nouveau apparaisse ;
- **crénage** : sans la bibliothèque Raqm, Pillow ignore le crénage des polices récentes (table GPOS). [kerning.py](../sources/video/kerning.py) lit cette table et [ecrans.py](../sources/video/ecrans.py) l'applique lettre par lettre : « SD-WAN » ne s'affiche plus « SD-W AN ».

**La voix reste Rémy**, avec les mêmes corrections de prononciation. Un audit de fiabilité a comparé chaque montant, sigle, nom et négation aux documents ; 17 des 103 phrases ont été corrigées et resynthétisées :
- montants arrondis lus comme exacts : « 221 400 € » devient 221 424 € HT par mois (Farah, conclusion) ; « environ » est ajouté devant 195 000 € et 470 000 € (Diane) ; « 418 » devient « 418 € par site, chaque mois » ; « environ 1 060 tunnels » et « plus de 64 000 € » pour la sécurité ;
- négations ambiguës à l'oral : diapo 8 (« laisse croire que le stockage inclus suffit »), diapos 15 et 18 (« à l'oral, dites : inclus côté utilisateur, licence à ajouter sur les hubs »), HDS (« ne vise pas, en principe, le remboursement des frais de santé ») ;
- formulations qu'un juré peut contester : « hubs » désigne les pare-feu d'entrée des datacenters, pas les datacenters ; « ses applications » au lieu d'« une application » ; la DMZ « héberge les services ouverts à Internet » ; un VPN classique « place le poste dans le réseau » ; réplication asynchrone « sous réserve des objectifs de reprise » ; l'édition gratuite d'EVE-NG PRO ; la recette « doit redonner 17 sur 17 » ;
- « Neuf d'entre elles n'ont qu'une note courte » : Whisper entendait « Neuf noms ».

Les écrans ont été alignés sur ces corrections (cartes de risque, chiffres de Diane et de Valentin, carte du VPN chez Maxime, conclusion, schéma de la solution). Une vérification de cette version par trois relecteurs et leurs sceptiques a ensuite fait corriger : l'orange réservé au Zero Trust (alertes et pièges en rouge), le texte courant porté à 30 px, le schéma nord-sud (les sorties traversent le pare-feu de périmètre), « ~60 partenaires » au lieu de « 300 partenaires », les hypothèses signalées (H6, H8, H9), les corrections de diapos ajoutées dans la fiche de chaque rôle concerné, et des coupures de sous-titres.

## Limites constatées

- Personne n'a écouté la vidéo pendant ces contrôles. La synchronisation voix / écran a été vérifiée par le calcul (chronologie) et sur des images extraites ; la prononciation des phrases nouvelles, par une transcription Whisper (similarité de 0,82 à 1,0 sur les 15 premières ; écarts limités à des pluriels inaudibles, à des homophones et à l'orthographe des sigles). Whisper ne prouve pas l'exactitude : les montants, sigles, noms et négations ont été relus à part.
- Les apparitions sont calées sur les phrases. Quand une phrase énumère plusieurs chiffres, ils apparaissent ensemble au début de la phrase.
- Lecture contrôlée avec ffmpeg seulement (durée, pistes, chapitres, sous-titres non activés par défaut) : pas d'essai dans VLC, le lecteur de Windows ou un navigateur.
- Certaines corrections de diapos sont affichées dans la fiche du rôle (notes rouges) sans être dites par la voix : le 600F chez Nolan, Fatih et Diane, les diapos 3 et 24 chez Farah, la diapo 23 chez Younes, la note de la diapo 20 chez Diane.
- Restent sous 30 px (de 20 à 28 px) : les étiquettes en capitales, les onglets des fiches, les repères de navigation, les sous-titres des boîtes du schéma, les mois du phasage et les sources des questions. Ce sont des repères, pas du texte à lire ; à vérifier sur un petit écran, ce qui n'a pas été fait.

## À faire sur le diaporama avant la répétition

Le diaporama est privé : demandez à Maxime l'accès en écriture. La vidéo et l'audit du 13/11 demandent ces corrections ; **aucune n'est encore faite** :

| Diapo | Rôle | Ce qui est écrit | À faire |
|---|---|---|---|
| 1 | Farah | « [Nom du groupe] », « [Date de soutenance] » | Remplir |
| 3 et 24 | Farah | « Un seul éditeur de sécurité », « Un éditeur, une politique » | Nuancer : Fortinet pour les pare-feu, le SD-WAN et le SASE ; le WAF (F5), le bastion (WALLIX) et le SIEM (Wazuh) viennent d'autres éditeurs, ce que l'offre présente comme un atout |
| 5 | Valentin | note : « garantie de rétablissement en 8 heures » | Écrire « garantie de temps d'intervention de 8 h » |
| 8 | Nolan | « 64 TiB par DC inclus dans la licence, aucune baie de stockage à acheter » | Nuancer : il faut 70 à 80 TiB bruts par DC, une extension vSAN est probable |
| 15 et 18 | Maxime | « inclus dans la licence Standard », « Déjà payé », « 24 % du coût total » | ZTNA inclus côté utilisateur, mais licence à ajouter sur les 4 hubs (écart net d'au moins 1,5 M€) ; 25 % au lieu de 24 % |
| 20 | Diane | note : liste des non-inclus | Ajouter la licence ZTNA des 4 hubs, la protection des postes (EDR), le fournisseur d'identité et les renouvellements après 36 mois |
| 22 | Valentin | « preuves horodatées et signées par empreinte » | Écrire « accompagnées de leurs empreintes SHA-256 » : une empreinte n'est pas une signature |
| 23 | Younes | note : « mot de passe faible » | Ne pas le dire : la cause du piratage n'est que probable |
| 23 | Younes | titre : « ce qui s'impose » | Nuancer pour HDS : pas forcément obligatoire, exigé par prudence |
| 9, 10, 11, 19 | Nolan, Fatih, Diane | FortiGate 600F | Dire « 600F ou son successeur probable, le 700G, recoté au devis » |
| 3, 6, 7, 8, 18, 19, 20, 22, 23 | plusieurs | note d'orateur courte | Écrire le texte à dire |

Pour la démonstration, le scénario est [docs/DEMO_EVE.md](../../docs/DEMO_EVE.md). La recette se lance depuis le PC de Maxime, qui détient la clé d'administration ; l'accès des autres membres est décrit dans [docs/ACCES_CAMARADES.md](../../docs/ACCES_CAMARADES.md).

## Contradictions relevées entre documents : signalées, non corrigées

L'audit de fiabilité du 13/11 au soir a comparé la vidéo aux documents du dépôt, puis un sceptique a revérifié chaque point. Ces documents n'ont pas été modifiés : ils sortent du périmètre de la vidéo. Les points qui comptent le plus pour la soutenance :

| Sujet | Ce qui se contredit | Ce que dit la vidéo |
|---|---|---|
| FortiGate 600F | L'offre le cite sur 15 lignes sans dire qu'il n'est plus commandable ; QUESTIONS_JURY (Q10) le dit, et propose le 700G recoté au devis | « 600F ou son successeur probable, le 700G, recoté au devis » |
| Plan de réversibilité (DORA) | L'offre (§ 12.3) le dit « documenté » ; Q43 : « annoncé, pas encore rédigé » ; le dépôt n'en contient aucun | « encore à rédiger » |
| Diapos 3 et 24 | « Un seul éditeur de sécurité » ; l'offre fait de la diversité des éditeurs un argument (WAF F5, bastion WALLIX, SIEM Wazuh) | non abordé ; ajouté au tableau des corrections ci-dessus |
| Note de la diapo 20 | Liste des non-inclus sans la licence ZTNA des 4 hubs, l'EDR, le fournisseur d'identité ni les renouvellements | la vidéo cite la licence des hubs et l'EDR parmi les non-inclus |
| Réplication des bases | L'offre laisse le mode ouvert (il dépend du RPO) ; le glossaire et le guide disent « asynchrone » sans réserve ; Q19 concilie | « asynchrone, sous réserve des objectifs de reprise à fixer avec le client » |
| HDS | Diapo 23 et guide : « ce qui s'impose » ; Q24 et l'offre : pas forcément obligatoire, exigé par prudence | « ne vise pas, en principe, le remboursement des frais de santé, mais nous l'exigeons par prudence » |
| Accès des partenaires sans agent | L'offre promet un contrôle du poste à tous ; Q52 : sans agent, pas de contrôle du poste | « sans agent, seulement des applications web peu sensibles » |
| Décision D6 (SUIVI_PROJET.md) | Le tableau des décisions dit toujours « ZTNA déjà inclus, 1,99 M€ évités » ; CHIFFRAGE et Q47 ajoutent la licence des hubs | « inclus côté utilisateur, licence à ajouter sur les 4 hubs ; écart d'au moins 1,5 M€ » |

Autres écarts mineurs :
- version de l'offre restée « 1.0 du 28 octobre » malgré les corrections du 13/11 ;
- trois dossiers de recette cités comme référence (16/10, 28/10, 10/11), avec des bascules mesurées de 3,8, 3,2 et 3,4 s ; les diapos citent 3,8 s ;
- intitulés des rôles différents entre ROLES_SOUTENANCE et la diapo 2 ;
- glossaire : « 4 HLD demandés par le client », alors que l'appel d'offres demande des schémas du datacenter et des agences, sans en fixer le nombre ;
- matrice des flux : administrateurs « via VPN », alors que l'offre les fait passer par FortiSASE ;
- WALLIX « certifié CSPN » sans réserve, alors que seule la version 6.0 de 2019 l'est ;
- vSAN : extension « éventuelle » (glossaire, note de la diapo 20) ou « probable » (ROLES_SOUTENANCE, Q22).

## Documents corrigés avec la première version de la vidéo

Les relecteurs de la première version ont trouvé des contradictions entre les documents du dépôt et nos propres réponses aux questions du jury (Q47, Q48). Elles ont été corrigées le 13/11 :
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

La liste des graphies corrigées est dans `LEXIQUE`, dans [build.py](../sources/video/build.py). Résultat : similarité médiane de 0,95 entre le texte prévu et la transcription. Les écarts restants sont des orthographes de prénoms et des pluriels inaudibles.

## Comment elle a été faite

1. **Recherche** : choix de la voix (ci-dessus).
2. **Script** : 16 scènes et 103 phrases, écrites à partir des documents du dépôt (`docs/`, diaporama et notes d'orateur). Le fichier [script.json](../sources/video/script.json) contient la narration et le contenu structuré de chaque écran.
3. **Critique par plusieurs agents** :
   - première version : trois tours de relecture (exactitude, préparation de l'oral, design, rythme, spectateur novice), avec contre-vérification par des sceptiques ;
   - refonte : un audit de la première version (trois auditeurs visuels, un contrôle de fiabilité et son sceptique), un extrait de 97 s corrigé avant d'étendre la nouvelle direction artistique, puis une vérification de la nouvelle version (lisibilité et transitions, synchronisation et pédagogie, fiabilité), chaque constat important étant contre-vérifié par un sceptique.

   Les relecteurs ne pouvaient pas écouter : ils se sont appuyés sur la transcription Whisper, sur des mesures (durées, chronologie, tailles de texte) et sur les images de la vidéo.
4. **Montage** :
   - [ecrans.py](../sources/video/ecrans.py) dessine chaque écran (mises en page, schémas, fiches) et [kerning.py](../sources/video/kerning.py) fournit le crénage des polices ;
   - [build.py](../sources/video/build.py) synthétise la voix phrase par phrase, cale les écrans sur la voix, trace les chemins du schéma, normalise le volume (-16 LUFS), écrit les sous-titres et les chapitres, puis encode avec ffmpeg.

## Régénérer la vidéo

Les voix des 103 phrases sont archivées dans [voix/](../sources/video/voix/), sous l'empreinte de leur texte. Sans modification du script, la vidéo se remonte donc sans le service de synthèse. Si une phrase change, elle seule est resynthétisée.

```powershell
cd presentation/sources/video
python -m pip install edge-tts==7.3.1 imageio-ffmpeg pillow numpy num2words
python test_build.py                                                       # contrôle du texte affiché
python build.py script.json ../preview/video --audio voix                  # environ 15 min ; ../preview est ignoré par git
python chapitres.py script.json ../preview/video ../../video/TRANSCRIPTION.md
python planches_scenes.py script.json ../preview/video                     # facultatif : planches de relecture des écrans
python -m pip install faster-whisper; python mesures.py ../preview/video --asr    # facultatif : contrôle de prononciation
```

La vidéo produite est `../preview/video/projet_rao_explique.mp4`. L'option `--apercu` encode plus vite, en qualité moindre.
