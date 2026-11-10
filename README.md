# RAO « Sécurité des infrastructures » : mutuelle santé

Projet étudiant du cours « Sécurité des infrastructures ». Nous répondons à l'appel d'offres (RAO) d'une mutuelle santé fictive : **530 sites, 10 000 utilisateurs, une centaine de partenaires**. Le client veut une architecture sécurisée de bout en bout (datacenters, réseau étendu, agences, accès distants), des schémas de principe (HLD) et un coût **en abonnement**. Le cahier des charges fait 3 pages : `RAO (Réponse Appel d'Offre) - Sécurité des Infrastructures.pdf`.

**Notre réponse en une phrase** : un SD-WAN Fortinet sur Internet relie tous les sites à deux datacenters certifiés HDS ; tout est filtré et refusé par défaut ; nomades et partenaires passent par un accès Zero Trust (FortiSASE et MFA) ; le tout coûte **221,4 k€ HT par mois sur 36 mois**, sans investissement de départ. Une maquette prouve les principes : **17 flux testés sur 17 conformes, bascule WAN en 3,8 s**.

Nouveau dans le projet ? Lisez d'abord **[docs/GUIDE_EXPLICATIF.md](docs/GUIDE_EXPLICATIF.md)** (30 minutes), puis gardez **[docs/GLOSSAIRE.md](docs/GLOSSAIRE.md)** ouvert à côté.

**Membres du groupe** : pour vous connecter à EVE-NG et à Proxmox, suivez **[docs/ACCES_CAMARADES.md](docs/ACCES_CAMARADES.md)**. Présentation du projet pour tous : `presentation/RAO_projet_explique.pdf` ; rôles de la soutenance : `docs/ROLES_SOUTENANCE.md`.

## Chiffres clés

| Indicateur | Valeur | Source |
|---|---|---|
| Abonnement mensuel tout compris (36 mois, HT) | 221 424 € | `docs/CHIFFRAGE.md`, « Lecture rapide » |
| Coût total sur 36 mois (TCO) | 7,97 M€ | `docs/CHIFFRAGE.md` |
| Par utilisateur et par mois | 22,14 € | `docs/CHIFFRAGE.md` |
| Économie du choix FortiSASE plutôt que Zscaler ZPA | 1,99 M€ sur 36 mois | `docs/CHIFFRAGE.md` (synthèse), `docs/OFFRE_TECHNIQUE.md` |
| Pare-feu FortiGate proposés | 570 (+10 en spare) | `docs/OFFRE_TECHNIQUE.md` §15 |
| Recette de la maquette | 17/17 flux conformes, bascule en 3,8 s | `evidence/20261016T181400Z/` |

## État d'avancement

Constaté dans les fichiers le 28/10/2026. Les dates sont celles des documents.

| Livrable | État | Où |
|---|---|---|
| Exigences du PDF et hypothèses | v1, relue contre le PDF (16/10) | `docs/EXIGENCES.md` |
| Offre technique (choix, modèles, sections 4 à 19) | v1 (16/10) | `docs/OFFRE_TECHNIQUE.md` |
| Chiffrage sourcé | Régénéré le 28/10 (fait foi) : lecture rapide, méthode, analyse de sensibilité | `docs/CHIFFRAGE.csv` → `docs/CHIFFRAGE.md` |
| 4 schémas HLD (global, datacenter, agences, accès distants) | Dans le diaporama, diapositives 5, 9, 13 et 17 | Diaporama |
| Diaporama de soutenance | 24 diapositives, notes d'orateur | [lien privé](https://claude.ai/artifact/957Rryu9hkuprq9MUcjuns) |
| Répartition des rôles à l'oral | Faite ; prénoms à compléter | `docs/ROLES_SOUTENANCE.md` |
| Maquette EVE-NG | Déployée et recettée (16/10) | `evidence/20261016T181400Z/` |
| Démonstration en direct | Scénario de 4 minutes | `docs/DEMO_EVE.md` |
| Accès des camarades à EVE | Scripts prêts ; application sur le serveur à confirmer (journal du 19/10) | `automation/connexion_rao.ps1`, `automation/host/05_acces_camarades.sh` |

Restent ouverts : les prix « sur devis » (nature D dans le chiffrage), les RPO/RTO à fixer avec le client (hypothèse H4), les prénoms sur la diapositive 2.

## Où trouver quoi

```
.
├── README.md                          ce fichier
├── RAO (Réponse Appel d'Offre) ….pdf  cahier des charges du client (3 pages)
├── SUIVI_PROJET.md                    journal de bord du projet (historique, ne pas modifier)
├── PLAN_CLAUDE_CODE_RAO_EVE_NG.md     plan initial du 15/10 (offre + maquette)
├── docs/
│   ├── GUIDE_EXPLICATIF.md            comprendre tout le projet en 30 minutes
│   ├── GLOSSAIRE.md                   tous les sigles et termes, avec leur rôle dans le projet
│   ├── OFFRE_TECHNIQUE.md             l'offre : choix, justifications, modèles, phasage, risques
│   ├── EXIGENCES.md                   exigences du PDF → solution → preuve ; hypothèses H1 à H12
│   ├── CHIFFRAGE.csv                  lignes de prix sourcées et règles de quantité (fichier à modifier)
│   ├── CHIFFRAGE.md                   rapport de coûts généré à partir du CSV (ne pas modifier à la main)
│   ├── FLUX.md                        matrice des flux autorisés (F01-F13) et des refus testés (N01-N09)
│   ├── HLD.md                         brouillon v0.1 de l'architecture (15/10), dépassé pour la maquette
│   ├── ROLES_SOUTENANCE.md            qui présente quelles diapositives, questions probables
│   ├── DEMO_EVE.md                    démonstration en direct pas à pas
│   ├── PLAN_V2.md                     plan révisé du 16/10 et décisions D1 à D5
│   ├── PREFLIGHT.md                   audit du PC et du serveur avant la maquette (15/10)
│   └── INCIDENT_PAR861454.md          rapport sur la compromission du serveur (rootkit)
├── inventory/
│   ├── topology.yml                   nœuds, conteneurs et réseaux de la maquette (état déployé)
│   ├── addressing.csv                 plan d'adressage de la maquette
│   └── images.yml                     inventaire des images, non mis à jour depuis le 15/10
├── automation/
│   ├── host/00_durcissement_ssh.sh    serveur : SSH par clé uniquement
│   ├── host/01_prep_hote.sh           serveur : ponts réseau du lab (vmbr1, vmbr2, vmbr10 à vmbr16)
│   ├── host/02_create_eve_vm.sh       serveur : création de la VM EVE-NG (VM 200)
│   ├── host/03_p0_securite.sh         serveur : interface Proxmox en local + pare-feu nftables
│   ├── host/04_lxc_lab.sh             serveur : les 8 conteneurs LXC (serveurs et clients du lab)
│   ├── host/05_acces_camarades.sh     serveur : autorise la clé d'un camarade (tunnel vers EVE seulement)
│   ├── incident/collecte_rescue.sh    collecte de preuves en mode rescue (préparé, jamais exécuté)
│   ├── eve/creer_lab.js               crée le lab « RAO » dans EVE par son API (console du navigateur)
│   ├── lab/deploy.py                  configure les routeurs et les services (IPsec, OSPF, nftables, journaux)
│   ├── lab/recette.py                 rejoue les tests de flux et la bascule, écrit les preuves
│   ├── chiffrage/calcul.py            calcule le chiffrage : CHIFFRAGE.csv → CHIFFRAGE.md
│   ├── ssh_config                     accès SSH à chaque nœud du lab, par rebond via le serveur
│   └── connexion_rao.ps1              ouvre l'interface EVE pour un camarade (Windows)
└── evidence/20261016T181400Z/         preuves de la recette : CSV, rapport, journaux, bascule, empreintes
```

Deux fichiers de la racine sont **sans rapport avec le projet** : `resume_complet_chat_force_combat_seche.md` et `planning_20262027.pdf`.

## Rejouer le travail

Toutes les commandes se lancent **depuis la racine du projet**. Il faut Python 3.11 ou plus (bibliothèque standard seulement) et le client OpenSSH.

### 1. Le chiffrage

```
python automation/chiffrage/calcul.py
```

Le script lit `docs/CHIFFRAGE.csv`, applique les règles de quantité, vérifie les totaux (530 sites, 10 000 utilisateurs, 570 FortiGate) et **réécrit** `docs/CHIFFRAGE.md`. Pour changer un prix ou une hypothèse, modifiez le CSV (ou les paramètres en tête du script), jamais le `.md`.

Dans le rapport généré, commencez par « Lecture rapide » (le prix et ce qui le fait bouger), puis « Méthode » (comment on passe des prix au loyer mensuel) et « Analyse de sensibilité » (effet d'une remise, du nombre de nomades, du taux de location).

### 2. Accéder à la maquette

- **Camarade du groupe (Windows)** : `powershell -ExecutionPolicy Bypass -File automation\connexion_rao.ps1`. Au premier lancement, le script crée votre clé et la copie dans le presse-papiers : envoyez-la au responsable du serveur, qui l'autorise avec `bash 05_acces_camarades.sh`. Relancez ensuite : EVE s'ouvre sur https://localhost:8443, lab `RAO`.
- **Détenteur de la clé d'administration** : `ssh -F automation/ssh_config fw-dc1` (même chose pour n'importe quel nœud : `gw-agfr`, `srv-db`…).

### 3. Reconstruire la maquette de zéro

Sur le serveur Proxmox, en root, dans cet ordre (voir l'en-tête de chaque script) :

1. `00_durcissement_ssh.sh`, après avoir copié sa clé publique.
2. `03_p0_securite.sh`, **depuis une session SSH** (pas la console web). Puis, si une 2e session SSH fonctionne : `systemctl stop fwrb.timer && systemctl enable nftables`.
3. `01_prep_hote.sh`, puis `02_create_eve_vm.sh` et installation d'EVE en console (attention à la boucle d'installation décrite dans le script).
4. `04_lxc_lab.sh`, avec la clé d'administration dans `/tmp/cle_lab.pub`.
5. Étapes **non scriptées**, décrites seulement dans `SUIVI_PROJET.md` (16/10, ~19h50-19h55) : l'image de routeur `linux-debian13-routeur` et le service DHCP de gestion sur EVE.
6. Dans le navigateur, sur l'interface EVE : coller `automation/eve/creer_lab.js` dans la console (F12), puis démarrer les 7 nœuds.

Ensuite, depuis le PC :

```
python automation/lab/deploy.py
python automation/lab/recette.py
```

`deploy.py` configure tout et régénère les clés IPsec à chaque passage (aucun secret n'est stocké). `recette.py` rejoue les 17 tests et la coupure WAN ; `--sans-bascule` saute la coupure (répétition rapide avant la soutenance).

### 4. Vérifier les preuves

Chaque recette crée un dossier `evidence/<date UTC>/` avec un fichier d'empreintes. Pour contrôler que rien n'a été modifié (le fichier a des fins de ligne Windows, d'où le `tr`) :

```
cd evidence/20261016T181400Z && tr -d '\r' < SHA256SUMS | sha256sum -c -
```

Les 4 fichiers doivent afficher `OK`.

### 5. La démonstration en soutenance

Scénario complet et plan B : `docs/DEMO_EVE.md`.

## Liens

- Diaporama de soutenance (24 diapositives, privé) : https://claude.ai/artifact/957Rryu9hkuprq9MUcjuns
- Comprendre le projet : [docs/GUIDE_EXPLICATIF.md](docs/GUIDE_EXPLICATIF.md)
- Sigles et termes : [docs/GLOSSAIRE.md](docs/GLOSSAIRE.md)
- Préparer son rôle à l'oral : [docs/ROLES_SOUTENANCE.md](docs/ROLES_SOUTENANCE.md)

**Sécurité** : aucun mot de passe ni clé privée ne doit entrer dans ce dossier. Les clés IPsec de la maquette sont générées à chaque déploiement et ne sont jamais écrites dans le projet.
