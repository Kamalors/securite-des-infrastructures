# Vidéo « Le projet RAO en 5 minutes » : sources Remotion

Sources de la vidéo [`presentation/video/projet_rao_7min.mp4`](../../video/projet_rao_7min.mp4) : 4 min 56, 1920 × 1080, 30 images par seconde, voix off en français, 9 chapitres, sous-titres dans `projet_rao_7min.srt`.

Le fichier et la branche gardent « 7min » dans leur nom : c'était la durée visée. Le texte de la voix compte environ 4 500 caractères, soit 4 min 36 de parole ; le titre de la vidéo dit donc « en 5 minutes ».

## Revoir ou refaire la vidéo

```
npm install
npx remotion studio                      # aperçu : la composition « Video », et chaque scène dans le dossier « Scenes »
npx remotion render Video out/video_brute.mp4 --hardware-acceleration=if-possible --color-space=bt709 --video-bitrate=1500k --audio-bitrate=160k
python scripts/livraison.py out/video_brute.mp4 out/projet_rao_7min.mp4    # chapitres et sous-titres
```

Le débit de 1,5 Mbit/s garde le fichier sous 50 Mo pour le dépôt : à 8 Mbit/s, l'encodage matériel dépasse la limite de 100 Mo de GitHub.

Python demande `imageio-ffmpeg` et `numpy` (plus `faster-whisper` et `num2words` pour contrôler la voix).

## Comment la vidéo est construite

| Étape | Fichier | Ce qu'il fait |
|---|---|---|
| Script | `script_video_rao_7min.md` | Le texte de la voix et les indications d'écran, scène par scène |
| Voix | `scripts/voix.py` | Génère chaque scène avec Kyutai TTS 1.6B, en local sur carte graphique, et relève l'instant de chaque mot |
| Assemblage | `scripts/assembler_voix.py` | Écrit `public/voix/01.mp3` à `09.mp3` (-16 LUFS) et `src/voix/NN.json` (minutage des mots), puis compare une transcription Whisper au script |
| Déroulé | `src/plan.json` | L'ordre des scènes, les chapitres et les temps de pause : seule source, lue par la vidéo et par la livraison |
| Calage | `src/calage.ts`, `src/Scene.tsx` | `a("deux cent vingt")` rend la seconde où la voix dit ces mots ; une expression absente arrête le rendu |
| Animation | `src/anim.tsx`, `src/elements.tsx`, `src/scenes/` | Tous les mouvements passent par `spring()` ; une scène par fichier |
| Montage | `src/Video.tsx` | Enchaîne les scènes avec `@remotion/transitions` et un effet sonore par transition |
| Livraison | `scripts/livraison.py` | Ajoute les 9 chapitres avec ffmpeg et écrit les sous-titres à partir du minutage des mots |
| Contrôle | `scripts/controle_video.py`, `scripts/planche.py` | Décodage complet, position de la voix mesurée dans la piste son, planche d'images |

Les animations sont pilotées par le minutage de la voix : elles ne se règlent pas à la souris dans Remotion Studio. Pour décaler un élément, on change l'expression qui le déclenche dans le fichier de la scène.

Couleurs fixes (`src/theme.ts`) : bleu canard pour le réseau, orange pour le Zéro Confiance, rouge pour les refus et les limites, vert pour ce qui est autorisé.

## Changer le texte de la voix

1. Modifier `script_video_rao_7min.md`.
2. Installer l'environnement de synthèse (une fois) : Python 3.12, `torch` avec CUDA, `moshi`, `sphn`. Sous Windows, lancer avec `NO_TORCH_COMPILE=1`.
3. `python scripts/voix.py 05` régénère la scène 5 (`--graine 1` pour une autre prise), puis `python scripts/assembler_voix.py 05`.
4. Relancer le rendu : les animations se recalent seules sur les nouveaux instants.

Deux mots sont écrits « au son » pour la voix seulement (`AU_SON` dans `scripts/voix.py`) : « SD-WAN » et « Fortinette ». Les balises entre crochets du script (`[excited]`…) sont propres à ElevenLabs : elles sont retirées avant la synthèse.

## Ce qui est décoratif

- Scène 1 : la position des 530 points est tirée au hasard dans les contours de la France et du monde (`scripts/carte.py`, graine fixe). Le dossier ne situe pas les sites, ni les deux centres.
- Scène 4a : avant la coupure, le trafic passe par l'opérateur A seul ; les tunnels par B sont montés mais vides, pour que la bascule se lise.
- Scène 6 : le schéma reprend l'inventaire de `docs/MAQUETTE.md` (7 équipements réseau, 8 serveurs et postes).

## Licences

| Élément | Licence |
|---|---|
| Voix : modèle Kyutai TTS 1.6B (`kyutai/tts-1.6b-en_fr`) | CC BY 4.0 ; la vidéo porte la mention « Voix générée par intelligence artificielle (Kyutai TTS) » |
| Voix : échantillon `unmute-prod-website/fabieng-enhanced-v2.wav` (`kyutai/tts-voices`) | CC0 |
| Contours de la carte : Natural Earth (`ne_110m_land`, `ne_50m_admin_0_countries`) | Domaine public |
| Police Instrument Sans | SIL Open Font License (`public/fonts/InstrumentSans-OFL.txt`) |
| Effets sonores | Synthétisés par `scripts/sfx.py` : aucun fichier tiers |
| Remotion | Gratuit pour les particuliers et les très petites structures ; licence payante au-delà (remotion.dev/license) |

Aucune musique d'ambiance.
