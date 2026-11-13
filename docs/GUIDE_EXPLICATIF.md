# Comprendre le projet en 30 minutes

Ce guide s'adresse à un membre du groupe qui n'a pas suivi les travaux. Il explique **ce que le client demande, ce que nous proposons, pourquoi, et ce que notre maquette prouve**. Il ne remplace pas les documents de référence : il vous dit où regarder.

Les sigles sont expliqués dans [GLOSSAIRE.md](GLOSSAIRE.md). Chaque chiffre vient d'un fichier du projet, cité entre parenthèses. Les montants sont **hors taxes**.

| Partie | Temps de lecture |
|---|---|
| 1. Le besoin du client | 3 min |
| 2. La solution en une image | 2 min |
| 3. Domaine par domaine (11 fiches) | 15 min |
| 4. Comment marche la maquette | 6 min |
| 5. Ce que l'incident nous a appris | 3 min |
| 6. À retenir | 1 min |

---

## 1. Le besoin du client en clair

Une grande mutuelle santé française veut **reconstruire toute son architecture de sécurité** : ses datacenters et tous ses sites. Le cahier des charges tient en 3 pages (le PDF à la racine).

### Le périmètre

| Élément | Volume (PDF p.1-2) |
|---|---|
| Sites en France | 500 : 2 sièges et 498 agences |
| Agences à l'international | 30 (530 sites au total) |
| Utilisateurs | 10 000 : 4 000 dans les sièges, 4 000 en agences France, 2 000 à l'international |
| Partenaires | Une centaine : 40 % reliés « site à site », 60 % en « utilisateurs nomades » |

Ordres de grandeur utiles (`docs/EXIGENCES.md`) : une agence France compte environ **8 personnes** (4 000 / 498), une agence internationale environ **67** (2 000 / 30), un siège environ **2 000**.

### Ce qu'il faut couvrir

Le PDF liste les sujets : connectivité WAN (datacenters et sites), housing des datacenters, compute, sécurité nord-sud (publication web, API et FTP sur Internet), sécurité est-ouest, agences (réseau et sécurité), administration à distance par l'infogérant, nomadisme des collaborateurs, accès des partenaires.

### Ce qui sera noté (PDF p.3)

1. **Les solutions techniques** : le concept, le **modèle d'équipement** retenu, la justification.
2. **Les schémas HLD** (schémas de principe) du datacenter et des agences.
3. **Les coûts**, ventilés en Housing, Connectivité WAN, Serveurs, Équipements réseau, Équipements de sécurité, Etc. Le client préfère **un abonnement** : « ma DSI ne me permet de débloquer une grosse somme d'un coup ».

Le PDF ne demande pas de maquette. Nous en avons fait une pour **prouver** nos principes.

### Ce que le PDF ne dit pas : nos hypothèses

Le client ne donne ni débits, ni nombre de nomades, ni nombre de serveurs. Nous avons donc posé des **hypothèses affichées** (`docs/EXIGENCES.md` §3). Les principales :

| Hypothèse | Valeur retenue |
|---|---|
| H6 : nomades | 3 000 (30 % des utilisateurs) |
| H7 : utilisateurs chez les partenaires nomades | 300 (60 partenaires × 5) |
| H8 : machines virtuelles | 300 (2 vCPU, 8 Go, 150 Go en moyenne) |
| H9 : comptes à privilèges (admins, infogérants) | 50 |
| H11 : répartition des sièges | 2 000 utilisateurs par siège |
| H12 : identité et MFA | le client a déjà un fournisseur d'identité (ex. Entra ID) |
| H4 : RPO / RTO | **à fixer avec le client** |

Si une hypothèse est fausse, le chiffrage se recalcule en une commande (voir le [README](../README.md)).

---

## 2. La solution en une image

Les quatre vrais schémas HLD sont dans le diaporama (diapositives 5, 9, 13 et 17). En voici une version texte :

```
INTERNET ───────────────────────────────────────────────────────────────────
   │ clients web / API                 │ nomades + partenaires nomades
   │                                   ▼
   │                      FortiSASE (cloud) : ZTNA + MFA + filtrage web
   ▼                                   ▼
DEUX DATACENTERS (housing certifié HDS, 2 domaines de panne, reliés par 2 liens)
   ① pare-feu périmètre (paire FortiGate 600F), qui sert aussi de hub SD-WAN
   ② DMZ : reverse proxy / WAF F5, passerelle SFTP
   ③ pare-feu interne (2e paire FortiGate 600F), tout est refusé par défaut
   ④ zones : applications │ données │ administration (bastion, SIEM) │ partenaires
   ⑤ cluster VMware vSAN de 4 serveurs + sauvegarde Veeam avec copie immuable
   ▲
   │ tunnels IPsec chiffrés : chaque site vers les 2 DC, sur chacun de ses accès (SD-WAN)
   │
SITES : 2 sièges · 498 agences France · 30 agences internationales · partenaires site à site
   dans chaque site : FortiGate (pare-feu + SD-WAN) · switchs Aruba · Wi-Fi Aruba · réseau invités isolé
```

À lire de haut en bas :

- **Le public** arrive par Internet sur la DMZ du datacenter, et nulle part ailleurs.
- **Les nomades et partenaires nomades** passent par FortiSASE, un service cloud. Il vérifie l'identité (MFA) et l'état du poste, puis ouvre l'accès à une application précise, jamais au réseau entier.
- **Les sites** (sièges, agences, partenaires site à site) montent des tunnels chiffrés vers les deux datacenters.
- **Dans le datacenter**, deux barrières successives : le pare-feu périmètre, puis le pare-feu interne qui sépare les zones.

L'idée maîtresse : **personne n'est de confiance par défaut**. Chaque flux autorisé est écrit, justifié et journalisé ; tout le reste est refusé.

---

## 3. Domaine par domaine

Chaque fiche suit le même plan : le problème, notre réponse, pourquoi (et l'alternative écartée), le chiffre clé, ce que la maquette prouve. Les identifiants F01, N03… renvoient à la matrice des flux (`docs/FLUX.md`) : **F** = flux autorisé, **N** = refus attendu.

### 3.1 WAN et SD-WAN : relier 530 sites

**Le problème.** Relier 530 sites, dont 30 à l'étranger, aux datacenters. Il faut que ce soit chiffré, que ça tienne quand un lien tombe, et que ça ne coûte pas une fortune.

**Notre réponse.** Un **SD-WAN Fortinet sur des accès Internet**, en **double hub** (`docs/OFFRE_TECHNIQUE.md` §4). Chaque site a un FortiGate qui monte des tunnels IPsec chiffrés vers **les deux** datacenters, sur **chacun** de ses accès. Le SD-WAN mesure en continu la qualité de chaque chemin (latence, gigue, perte) et choisit le meilleur pour chaque application. Si un accès tombe, il bascule tout seul.

| Profil | Accès | Boîtier |
|---|---|---|
| 2 sièges | 2 fibres dédiées FTTO 1 Gbit/s chez 2 opérateurs + secours 4G/5G | 2 × FortiGate 200G en HA |
| 498 agences France | 1 fibre pro FTTH + secours 4G intégré au boîtier | 1 × FortiGate 40F-3G4G |
| 30 agences internationales | 2 accès Internet locaux | 2 × FortiGate 70G en HA |
| 2 datacenters | 2 transits Internet 1 Gbit/s + 2 liaisons inter-DC | paire de FortiGate 600F par DC |

*Analogie* : le SD-WAN fonctionne comme un GPS. Il connaît plusieurs routes, mesure les bouchons en temps réel et vous fait changer de route sans que vous ayez à y penser.

**Pourquoi.**
- **Pas de MPLS** (le réseau privé classique des opérateurs). L'Internet professionnel coûte une fraction du prix et se commande en abonnement mensuel. La sécurité est portée par le chiffrement et les pare-feu, pas par le réseau de l'opérateur. Le MPLS reste une option pour les sièges si un SLA de bout en bout est exigé (`docs/HLD.md` §1.3).
- **Double hub** : si un datacenter tombe, les sites joignent l'autre.
- **HA au-delà de 50 utilisateurs** : un siège ou une agence internationale a deux boîtiers ; une agence de 8 personnes en a un seul, avec un secours 4G.
- **Alternative écartée** : Cato Networks, un SASE entièrement dans le cloud. Dans le Magic Quadrant SASE 2026 de Gartner, Cato est « Leader » et Fortinet « Challenger » (« Leader » en 2025) ; Fortinet est en revanche « Leader » 2026 des pare-feu, l'essentiel de notre usage. Nous avons retenu Fortinet pour avoir une seule famille de produits du datacenter à l'agence et aux nomades : une politique, une console, un support (`docs/OFFRE_TECHNIQUE.md`, « Choix du ZTNA », point 4).

**Chiffres clés.** Connectivité WAN : **41 273 €/mois** en abonnement (`docs/CHIFFRAGE.md`). Une agence France : fibre à 34,99 €/mois + SIM 4G à 13,99 €/mois. Dimensionnement des hubs : environ **1 060 tunnels** nécessaires par hub (530 sites × 2 accès), **2 000** acceptés par un FortiGate 600F.

**Ce que la maquette prouve.** 6 tunnels IPsec chiffrés depuis le pare-feu du DC1. Coupure de l'opérateur A d'une agence : le trafic passe sur l'opérateur B en **3,8 s**, puis revient seul sur A (`evidence/20261016T181400Z/bascule_wan.txt`). **Limite** : un tunnel IPsec avec du routage n'est pas un SD-WAN complet. La maquette ne choisit pas le chemin par application.

### 3.2 Datacenters, housing et compute

**Le problème.** Héberger les applications et les données de santé de la mutuelle. Le PDF demande une solution de **housing** (on loue de la place dans un datacenter et on y installe nos serveurs), la répartition, la redondance, et le choix « virtuel ou physique ».

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §5-6).
- **Deux datacenters en colocation** en région parisienne, dans deux **domaines de panne** distincts : alimentation, opérateurs et site différents.
- Chaque DC : **certifié HDS**, niveau Tier III, « carrier-neutral » (plusieurs opérateurs présents). 2 baies 42U, 6 kW, alimentation doublée (A+B).
- **Mode de fonctionnement** : actif/actif pour la publication web et les accès distants (répartition DNS) ; actif/passif pour les bases de données (réplication asynchrone).
- **Compute** : VMware vSphere Foundation sur **4 serveurs Dell PowerEdge R760 par DC** (2 × 32 cœurs, 512 Go chacun), en cluster hyperconvergé **vSAN**, dimensionné **N+1**. Base : 300 VM.
- **Sauvegarde Veeam**, règle 3-2-1 : une copie dans l'autre DC et une **copie immuable** chez un hébergeur de stockage objet français.

*Analogie* : le housing, c'est louer une place dans un parking gardé pour sa propre voiture. Le parking fournit le toit, l'électricité, la climatisation et le gardien. La voiture, c'est-à-dire les serveurs, reste à nous. Le N+1, c'est la roue de secours : un serveur peut tomber sans perte de capacité utile.

**Pourquoi.**
- **Deux DC** : un seul serait un point de panne unique.
- **HDS** : la mutuelle traite des données de santé. Il faut un hébergeur certifié, vérifié dans l'annuaire du certificateur.
- **Virtuel par défaut** : le physique est réservé aux cas imposés par un éditeur de logiciel.
- **vSAN** : le stockage est compris dans la licence VVF (0,25 TiB par cœur, soit 64 TiB par DC). Pas de baie de stockage séparée à acheter.
- **Copie immuable** : personne ne peut la modifier ni l'effacer pendant sa durée de rétention, pas même un attaquant devenu administrateur. C'est la parade au rançongiciel.
- **Alternatives** : Proxmox VE ou Nutanix pour la virtualisation (question probable du jury : « pourquoi VMware après le rachat par Broadcom ? », voir `docs/ROLES_SOUTENANCE.md`).
- **Attention** : deux DC ne font pas un PRA tant que les objectifs RPO/RTO ne sont pas fixés avec le client (`docs/HLD.md` §1.2, hypothèse H4).

**Chiffres clés.** Housing : **4 511 €/mois** (baie à 470,40 €/mois, énergie à 1 314,66 €/mois par DC). Serveurs : **14 221 €/mois** en abonnement (`docs/CHIFFRAGE.md`). Stockage vSAN : 64 TiB par DC.

**Ce que la maquette prouve.** Rien sur ce domaine, et nous le disons : la maquette ne prouve ni la résilience physique, ni la réplication, ni la capacité. Le DC2 y est réduit à un seul routeur.

### 3.3 Sécurité nord-sud et publication

**Le problème.** Le trafic « nord-sud » entre Internet et le datacenter. Le client publie un site web, des API et un serveur FTP. Il faut aussi sécuriser l'accès à Internet des serveurs et des utilisateurs.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §7).
- **Pare-feu périmètre** : une paire de FortiGate 600F en HA par DC (IPS, antivirus, filtrage applicatif). Ce sont aussi les hubs SD-WAN.
- **DMZ** dédiée à la publication, avec un **reverse proxy et WAF F5 BIG-IP Advanced WAF** (2 instances par DC) devant le web et les API : terminaison TLS, protection contre les attaques web courantes (OWASP), protection des API.
- **FTP remplacé par SFTP** : une passerelle SFTP en DMZ, authentification par clé, liste d'adresses des partenaires. Le FTP en clair n'est gardé qu'en exception temporaire, isolée et journalisée.
- **Sorties Internet** : filtrage central pour les serveurs du DC ; filtrage local dans chaque agence (UTP du FortiGate) ; FortiSASE pour les nomades.
- **DDoS volumétrique** : protection en option chez les opérateurs de transit.

*Analogie* : la DMZ, c'est le hall d'accueil d'une banque. Le public entre dans le hall, jamais dans la salle des coffres. Le WAF, c'est le vigile qui ouvre les colis, alors qu'un pare-feu classique ne regarde que l'adresse sur l'étiquette.

**Pourquoi.**
- Si le serveur web est piraté, il reste dans la DMZ : il n'atteint pas la base de données.
- Le FTP fait circuler mots de passe et fichiers en clair. SFTP chiffre tout.
- **Alternatives** : Cloudflare WAF (dans le cloud) plutôt que F5 (sur site) ; Palo Alto plutôt que FortiGate. FortiGate a été retenu par cohérence avec le SD-WAN (`docs/OFFRE_TECHNIQUE.md`, grille des modèles).

**Chiffres clés.** WAF : **5 004 €/mois** pour 4 instances. 8 FortiGate 600F en tout (2 paires par DC).

**Ce que la maquette prouve.** Publication HTTPS (F01) et SFTP (F02) joignables depuis Internet ; base de données (N01) et bastion (N02) injoignables. Le refus N01 apparaît dans les journaux du pare-feu. **Limite** : ni WAF ni DDoS dans la maquette.

### 3.4 Sécurité est-ouest

**Le problème.** Le trafic « est-ouest » circule entre les serveurs, à l'intérieur du datacenter. Un attaquant qui a pris pied sur un serveur essaie de rebondir vers les autres : c'est le **mouvement latéral**.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §8). Une **seconde paire de FortiGate 600F par DC** filtre entre les zones **DMZ, applications, données, administration et partenaires**. Tout est **refusé par défaut**. Chaque flux autorisé est documenté (source, destination, port, justification) et journalisé dans le SIEM. La matrice complète : `docs/FLUX.md`.

*Analogie* : les cloisons étanches d'un navire. Une voie d'eau dans un compartiment ne coule pas le bateau. Et le refus par défaut, c'est une soirée sur liste d'invités : si votre nom n'est pas sur la liste, vous n'entrez pas.

**Pourquoi.**
- La chaîne web → application → base est cloisonnée : chaque maillon ne parle qu'au suivant, sur un seul port.
- Deux barrières successives (périmètre puis interne) : c'est la **défense en profondeur**. Il faut les franchir toutes les deux.
- **Alternatives** mentionnées dans `docs/HLD.md` §1.5 : des contextes virtuels séparés sur la même plateforme, ou une micro-segmentation dans l'hyperviseur (en option).

**Chiffres clés.** 13 flux autorisés documentés, 9 refus attendus (`docs/FLUX.md`).

**Ce que la maquette prouve.** Le web n'atteint l'application que sur le port 8443 (F03), l'application n'atteint la base que sur le port 5432 (F04). Web → base (N03) et application → base sur un autre port (N04) sont refusés et journalisés.

### 3.5 Agences : réseau local, Wi-Fi et sécurité

**Le problème.** Dans chaque site, les utilisateurs doivent aller sur Internet et joindre les applications des datacenters. Le PDF demande l'architecture, les « solutions réseaux » (LAN, Wi-Fi) et la sécurité.

**Notre réponse** : **trois profils standardisés** (`docs/OFFRE_TECHNIQUE.md` §10).

| | Siège (×2, ~2 000 utilisateurs) | Agence France (×498, ~8) | Agence internationale (×30, ~67) |
|---|---|---|---|
| Sécurité / SD-WAN | 2 × FortiGate 200G (HA) | FortiGate 40F-3G4G | 2 × FortiGate 70G (HA) |
| Switchs | 53 × Aruba CX 6100 48G PoE + cœur 2 × CX 8100 | 1 × Aruba CX 6100 12G PoE | 2 × Aruba CX 6100 48G PoE |
| Wi-Fi 6E | 80 × Aruba AP-615 | 1 × AP-615 | 3 × AP-615 |
| Accès | 2 FTTO + 4G/5G | FTTH + 4G | 2 accès Internet |

- **Règles de dimensionnement** : 1,25 port de switch par utilisateur, 1 borne Wi-Fi pour 25 utilisateurs, HA au-delà de 50 utilisateurs.
- **Segmentation dans chaque site** : utilisateurs, invités (Internet seulement), administration, téléphonie et imprimantes.
- **Wi-Fi** : un réseau d'entreprise authentifié (802.1X via le fournisseur d'identité) et un réseau invités isolé.
- **Pilotage central** : FortiManager pour les FortiGate, Aruba Central pour les switchs et le Wi-Fi.

**Pourquoi.**
- Des profils identiques permettent un déploiement industriel : environ 25 agences par semaine (`docs/OFFRE_TECHNIQUE.md` §17).
- Le modem 4G intégré au FortiGate 40F-3G4G donne un secours sans boîtier supplémentaire.
- La sortie Internet est filtrée localement : le trafic web ne remonte pas jusqu'au datacenter.
- **Alternatives** : Cisco Catalyst et Meraki pour le LAN et le Wi-Fi ; Peplink pour le boîtier d'agence.

**Chiffres clés.** Équipements réseau : **52 448 €/mois** (`docs/CHIFFRAGE.md`). 748 bornes Wi-Fi, 664 switchs d'accès (498 + 166), 8 switchs de cœur.

**Point ouvert** (`docs/CHIFFRAGE.md`, « Non inclus ») : dans chaque siège, 53 switchs d'accès en double attachement dépassent les ports de la paire de switchs de cœur. Il faudra un étage de distribution ou un cœur plus dense. Les optiques et câbles de raccordement restent aussi à chiffrer.

**Ce que la maquette prouve.** L'agence joint l'application du DC par le tunnel (F05). Les invités n'ont qu'Internet (F13) et aucun réseau interne (N05). Pas de SSH direct vers les serveurs (N08). **Limite** : ni switch ni Wi-Fi dans la maquette, et seulement 2 sites témoins (un siège, une agence).

### 3.6 Infogérance et bastion

**Le problème.** Des prestataires extérieurs (l'infogérant) administrent le système d'information. Ce sont les accès les plus dangereux : un compte administrateur volé ouvre tout.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §11).
- **Bastion WALLIX**, éditeur français : **seule porte d'administration**. Comptes nominatifs, **MFA**, approbation et durée limitée, **enregistrement des sessions**.
- Les infogérants se connectent par FortiSASE (ZTNA) **vers le bastion uniquement**. Aucun accès direct aux équipements.
- **Infogérance chiffrée** : NOC/SOC en heures ouvrées (3 ETP) ; SOC 24/7 en option.

*Analogie* : le sas unique d'une salle des coffres, avec un registre des entrées et une caméra qui filme chaque intervention.

**Pourquoi.**
- On sait qui a fait quoi, quand, et on peut le revoir.
- WALLIX : souveraineté (éditeur français) et enregistrement de session. **Alternatives** : Delinea, CyberArk.
- Notre propre serveur de maquette a été piraté par un accès d'administration exposé (partie 5) : nous savons concrètement ce que ça coûte.

**Chiffres clés.** 50 comptes à privilèges (H9), 55 764 € **sur devis** (prix estimé). Infogérance : 32 130 €/mois (`docs/CHIFFRAGE.md`).

**Ce que la maquette prouve.** L'administration passe par le bastion (F09, F10). Le SSH direct depuis une agence vers un serveur est refusé (N08). **Limite** : le bastion de la maquette est un simple conteneur Linux, sans approbation ni enregistrement vidéo.

### 3.7 Nomadisme et Zero Trust (ZTNA)

**Le problème.** 3 000 collaborateurs (hypothèse H6) travaillent hors des locaux. Ils doivent joindre les applications internes et naviguer sur Internet en sécurité.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §12). **FortiSASE**, avec un seul agent sur le poste (FortiClient), qui assure :
- la sécurité de l'accès Internet : filtrage web, DNS, antivirus, CASB ;
- l'**accès Zero Trust** (ZTNA) aux applications privées ;
- la **MFA** par le fournisseur d'identité de la mutuelle (H12) et le **contrôle de l'état du poste** (posture).

Les droits sont donnés par groupe et par application, jamais au réseau entier.

*Analogie* : un VPN classique, c'est un badge qui ouvre tout l'immeuble une fois la porte d'entrée franchie. Le ZTNA, c'est un badge vérifié à chaque porte, qui n'ouvre que les bureaux dont vous avez besoin.

**Pourquoi FortiSASE plutôt que Zscaler ZPA** (`docs/OFFRE_TECHNIQUE.md`, « Choix du ZTNA ») :
1. **La fonction est incluse côté utilisateur** : la souscription FortiSASE comprend l'accès privé ; le guide de commande Fortinet demande en plus une licence sur chacun des 4 hubs FortiGate, à chiffrer au devis (`docs/QUESTIONS_JURY.md`, Q47).
2. **1,99 M€ évités sur 36 mois** (de 1,24 à 3,31 M€ selon les estimations du prix de ZPA, qui n'a pas de prix public) ; après la licence des hubs, l'écart reste d'au moins 1,5 M€.
3. **Un seul agent** sur le poste au lieu de deux qui se disputeraient le trafic.
4. **Une seule politique et une seule console** du datacenter aux nomades.
5. **Les partenaires sans poste géré restent couverts** par un portail sans agent.
6. Fortinet est « Leader » 2026 des pare-feu selon Gartner ; en SASE, il est « Challenger » en 2026 (« Leader » en 2025).

**Le risque assumé** : dépendre d'un seul éditeur. C'est justement le sujet de la « stratégie de sortie » exigée par DORA. Parades : identité et MFA chez un fournisseur indépendant, protocoles standard (IPsec, SAML/OIDC), engagement de 36 mois aligné sur la location, plan de réversibilité.

**Chiffres clés.** 3 300 licences FortiSASE (3 000 nomades + 300 utilisateurs partenaires) : 443 717 € pour 3 ans. ZPA aurait ajouté 55 206 €/mois (`docs/CHIFFRAGE.md`).

**Ce que la maquette prouve.** **Rien sur ce domaine.** Les tests F07, F08, N07 et N09 sont marqués « non exécutés » : il n'y a ni ZTNA ni fournisseur d'identité dans la maquette. Il faut le dire franchement à l'oral.

### 3.8 Partenaires

**Le problème.** Une centaine de partenaires utilisent des applications de la mutuelle : 40 % se relient « site à site », 60 % sont des personnes isolées. Chacun ne doit voir que ses applications.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §13).

| Partenaires | Solution | Contrôle |
|---|---|---|
| 40 % site à site | Tunnel IPsec vers une **zone partenaire** du DC (hubs FortiGate 600F) | Seules les applications prévues au contrat ; traduction d'adresses (NAT) si les plages se chevauchent |
| 60 % nomades | FortiSASE : **portail sans agent** pour les applications web, agent si besoin | Comptes partenaires distincts, MFA, durée de vie limitée, revue trimestrielle, révocation immédiate |

**Pourquoi.**
- Une zone dédiée : un partenaire piraté ne voit pas le reste du système.
- Portail sans agent : on ne peut pas installer de logiciel sur les postes d'une autre entreprise.
- **Limite** : l'accès sans agent ne couvre que les applications web. Un autre protocole demande l'agent ou le site à site.

**Chiffres clés.** 300 utilisateurs partenaires (hypothèse H7), compris dans les 3 300 licences FortiSASE.

**Ce que la maquette prouve.** Le partenaire site à site joint l'application (F06) et rien d'autre : la base est refusée et journalisée (N06). Les partenaires nomades ne sont pas modélisés.

### 3.9 Exploitation

**Le problème.** Faire vivre au quotidien 570 pare-feu, plus de 670 switchs, 748 bornes et deux datacenters. Et détecter les attaques.

**Notre réponse** (`docs/OFFRE_TECHNIQUE.md` §14 et §17).
- **Pilotage central** : FortiManager Cloud (6 lots de 100 équipements) et Aruba Central.
- **SIEM Wazuh** (open source) et supervision, hébergés sur le compute.
- DNS et NTP internes, gestion des mises à jour et des changements, **sauvegardes testées** par des restaurations planifiées.
- **Déploiement en 5 phases sur 9 mois** :

| Phase | Période | Contenu |
|---|---|---|
| 1. Socle | M0 – M2 | 2 DC, transits, compute, hubs SD-WAN, pilotage, bastion, SIEM |
| 2. Sièges et pilote | M2 – M3 | 2 sièges, 10 agences pilotes |
| 3. Généralisation France | M3 – M8 | ~25 agences par semaine, en coexistence avec l'existant |
| 4. International | M6 – M9 | 30 agences, avec les opérateurs locaux |
| 5. Nomades et partenaires | M3 – M9 | FortiSASE par vagues, puis bascule des partenaires site à site |

*Analogie* : le SIEM, c'est la salle de vidéosurveillance qui regroupe les images de toutes les caméras du bâtiment.

**Pourquoi Wazuh.** Licence gratuite. **Alternatives** : Splunk ou Microsoft Sentinel, dont le coût dépend du volume de journaux (hypothèse H10).

**Chiffres clés.** SIEM : 0 € de licence. 9 mois de déploiement.

**Ce que la maquette prouve.** Chaque décision des pare-feu (« RAO-OK » ou « RAO-REFUS ») part vers un collecteur central : 27 lignes de journal pendant la recette (`evidence/20261016T181400Z/journaux_pare-feu.log`). Le flux DNS/NTP (F12) n'a pas été testé.

### 3.10 Coûts et abonnement

**Le problème.** Le client veut un coût global, ventilé par poste, et préfère payer **chaque mois** plutôt qu'investir d'un coup.

**Notre réponse.** Le matériel et les licences de 3 ans (environ **4,2 M€** de frais initiaux) sont financés par une **location financière sur 36 mois** au taux de 7 % par an (hypothèse à faire confirmer par un bailleur). S'y ajoutent environ **91 k€ par mois** de coûts récurrents (fibres, housing, infogérance…). Résultat : **221 424 € HT par mois, sans rien avancer**.

*Analogie* : c'est le leasing d'une voiture. Vous roulez tout de suite et vous payez une mensualité, au lieu de sortir le prix du véhicule le premier jour.

**Où lire les chiffres.** `docs/CHIFFRAGE.md` est la seule référence pour les montants. Lisez dans cet ordre :
1. **« Lecture rapide »** : le prix, les postes les plus lourds (sécurité, réseau, services), ce qui fait bouger la facture.
2. **« Méthode »** : comment une règle de quantité et un prix sourcé deviennent un loyer mensuel. La formule du loyer y est expliquée avec un exemple.
3. **« Par poste du PDF »** : la ventilation demandée par le client (Housing, WAN, Serveurs, Équipements réseau, Équipements de sécurité, Etc.).
4. **« Analyse de sensibilité »** : l'effet d'une remise négociée, de 1 000 nomades de plus ou de moins, d'un autre taux de location, d'une agence de plus.

**Comment on a chiffré, en bref.** Chaque ligne de `docs/CHIFFRAGE.csv` a un prix sourcé (lien vers le revendeur ou le comparateur), une nature (**P** = prix public, **E** = estimation, **D** = devis obligatoire) et une **règle de quantité** (par exemple « 1 borne pour 25 utilisateurs »). Le script `automation/chiffrage/calcul.py` applique les règles, convertit les devises au taux BCE et vérifie les totaux (530 sites, 10 000 utilisateurs, 570 FortiGate). Un stock de spare de 2 % est inclus.

**Chiffres clés** (`docs/CHIFFRAGE.md`, « Lecture rapide »).
- **221,4 k€ par mois**, soit **7,97 M€** sur 36 mois et **22,14 € par utilisateur** et par mois.
- Payer comptant coûterait moins cher au total : l'écart, environ **0,47 M€** sur 3 ans, est le prix de l'étalement.
- Le choix de FortiSASE plutôt que ZPA évite 1,99 M€.

**Non inclus** : la liste complète est dans la section « Non inclus » du rapport. À connaître : cross-connects dans les DC, logistique, SOC 24/7, fournisseur d'identité (supposé existant), renouvellements au-delà de 36 mois.

### 3.11 Risques et conformité

(`docs/OFFRE_TECHNIQUE.md` §19 et `docs/EXIGENCES.md` §4)

- **HDS** : hébergeur et infogérant certifiés, sites dans l'Espace économique européen.
- **DORA** (assurance, applicable depuis le 17/01/2025) : prestataires TIC inscrits au registre, clauses contractuelles, **plan de réversibilité**, en particulier face à la dépendance à Fortinet. L'applicabilité exacte à la mutuelle reste à vérifier.
- **RGPD** : les données de santé sont une catégorie particulière (article 9). Les transferts vers les agences hors UE sont à encadrer (clauses contractuelles types).
- **Risques projet** : délais d'approvisionnement de 570 boîtiers, éligibilité des agences à la fibre, dépendance à un seul éditeur.

---

## 4. Comment marche la maquette

### 4.1 À quoi elle sert

La maquette prouve **les principes**, pas les produits : segmentation et refus par défaut, publication en DMZ, tunnels chiffrés, bascule WAN, passage obligé par le bastion, journalisation. En production, ce sont des FortiGate qui appliquent la même politique (`docs/DEMO_EVE.md`).

### 4.2 L'empilement : des poupées russes

```
Serveur dédié loué (4 cœurs, 31 Go de RAM : docs/PREFLIGHT.md)
└── Proxmox VE : l'hyperviseur, qui fait tourner des machines virtuelles et des conteneurs
    ├── VM EVE-NG (20 Go, 6 vCPU) : le simulateur de réseau
    │   └── 7 routeurs Debian : isp-a, isp-b, fw-dc1, fw-dc2, gw-hq, gw-agfr, gw-part
    └── 8 conteneurs LXC : srv-web, srv-app, srv-db, bastion, logs, cli-ag, cli-ext, cli-inv
        (branchés aux routeurs d'EVE par des ponts réseau)
```

**Pourquoi des conteneurs à côté d'EVE ?** L'édition gratuite d'EVE-NG (Freemium) limite chaque lab à **7 nœuds**. Les 7 routeurs restent dans EVE ; les serveurs et les postes clients tournent en conteneurs LXC, plus légers, reliés à EVE. C'est la décision D1 (`docs/PLAN_V2.md`).

Chaque routeur est une Debian 13 avec trois outils libres : **strongSwan** (IPsec), **FRR** (routage OSPF) et **nftables** (pare-feu). Chacun utilise 1 vCPU et 512 Mo.

### 4.3 Qui joue quel rôle

| Nœud de la maquette | Joue le rôle de |
|---|---|
| `isp-a`, `isp-b` | Les opérateurs A et B, c'est-à-dire « Internet » |
| `fw-dc1` | Les FortiGate du DC1 : hub SD-WAN, pare-feu périmètre **et** pare-feu interne, réunis dans un seul routeur |
| `fw-dc2` | Le DC2, réduit à un routeur et un réseau |
| `gw-hq` | Le boîtier d'un siège (deux opérateurs) |
| `gw-agfr` | Le boîtier d'une agence France (opérateurs A et B, réseau des employés, réseau invités) |
| `gw-part` | Un partenaire site à site (opérateur A seulement) |
| `srv-web`, `srv-app`, `srv-db` | Les zones DMZ, applications et données du DC1 |
| `bastion`, `logs` | La zone d'administration : bastion et collecteur de journaux |
| `cli-ag`, `cli-inv`, `cli-ext` | Un poste d'agence, un invité de l'agence, un client sur Internet |

L'agence internationale (`gw-agint`) prévue au départ n'a pas été déployée : elle suit le même schéma que le siège (`inventory/topology.yml`).

**Les adresses** (`inventory/addressing.csv`). « Internet » utilise des plages réservées à la documentation (RFC 5737) : 198.51.100.0/24 pour l'opérateur A, 203.0.113.0/24 pour l'opérateur B, 192.0.2.0/24 pour les clients externes. L'interne utilise des adresses privées : 10.11.x.x pour le DC1 (DMZ en .10, applications en .20, données en .30, administration en .99), 10.30 pour le siège, 10.40 pour l'agence, 10.60 pour le partenaire.

### 4.4 Les briques, expliquées simplement

**IPsec (strongSwan) : les tunnels chiffrés.** C'est une enveloppe scellée qui voyage sur la route publique : l'opérateur la transporte sans pouvoir l'ouvrir ni la modifier. Le pare-feu du DC1 monte **6 tunnels** : agence (opérateurs A et B), siège (A et B), partenaire (A), DC2 (A). La négociation se fait en IKEv2. Chaque tunnel apparaît comme une interface réseau (`xa-agfr`, `xb-agfr`…), ce qui permet au routage de choisir entre eux. Les clés sont **régénérées à chaque déploiement** et jamais écrites dans le projet.

**OSPF (FRR) : le GPS du réseau.** Les routeurs se parlent toutes les secondes et partagent la carte du réseau. Chaque tunnel a un coût : 10 par l'opérateur A, 100 par l'opérateur B. Le trafic prend donc A tant que A répond. Un voisin silencieux pendant **4 secondes** est déclaré mort : la route bascule sur B. C'est cohérent avec la bascule mesurée de **3,8 s**.

**nftables : le videur avec sa liste.** Chaque routeur refuse tout par défaut. Seuls passent les flux écrits dans la liste, chacun étiqueté avec son identifiant de `docs/FLUX.md` (« RAO-OK F03 », par exemple). Tout le reste est rejeté et noté « RAO-REFUS ». Pour la publication, le pare-feu traduit l'adresse publique vers le serveur web de la DMZ (DNAT), sur les ports 443 et 22 seulement. À l'agence, il cache les adresses internes derrière l'adresse de l'opérateur pour sortir sur Internet (NAT).

**La journalisation.** Chaque décision du noyau est envoyée au conteneur `logs`, comme un registre central que personne ne peut effacer depuis le routeur.

**Un réseau de gestion séparé.** Pour administrer les nœuds, il existe un réseau à part (10.98.0.0/24). Il n'annonce volontairement ni passerelle ni DNS. Sinon, un test pourrait « réussir » en passant par ce réseau au lieu du chemin testé, et donner un faux résultat (`docs/PLAN_V2.md` §2.3).

### 4.5 La recette : comment on prouve

Le script `automation/lab/recette.py` rejoue **17 tests** : 10 flux qui doivent passer et 7 qui doivent être refusés. Pour chacun, il tente une connexion depuis le bon nœud (`nc`), compare le résultat à l'attendu, puis récupère les traces dans les journaux.

Ensuite, il **coupe l'opérateur A de l'agence pendant 10 secondes**, pendant qu'un poste de l'agence envoie un ping toutes les 0,2 s vers l'application. Résultat du 16/10/2026 :

- 19 pings perdus sur 125, soit 19 × 0,2 s = **3,8 s d'interruption** ;
- pendant la coupure, la route passe par le tunnel B (`xb-dc1`) ; après, elle revient sur A (`xa-dc1`).

Tout est rangé dans `evidence/20261016T181400Z/` : le tableau des tests, le rapport, les 27 lignes de journal, la mesure de bascule et un fichier d'**empreintes SHA-256**. L'empreinte permet de vérifier que les fichiers n'ont pas été retouchés depuis la recette (commande dans le [README](../README.md)).

### 4.6 Deux bugs instructifs (bonnes anecdotes pour l'oral)

- **MOBIKE.** Cette option d'IKEv2 permet à un tunnel de « déménager » quand une adresse change. Lors des premiers essais, quand on coupait l'opérateur A, le tunnel A déménageait sur l'opérateur B. Le trafic passait toujours, mais la bascule était invisible. Nous l'avons désactivée : chaque tunnel reste attaché à son opérateur, et c'est OSPF qui bascule (`automation/lab/deploy.py`).
- **BCP 38.** Nos faux opérateurs laissaient passer des paquets portant l'adresse de l'autre opérateur. Le tunnel A survivait donc à la coupure du lien A. Les vrais opérateurs filtrent ces paquets usurpés : nous avons ajouté ce filtrage anti-usurpation à la maquette pour qu'elle soit réaliste.

### 4.7 Ce que la maquette ne prouve pas

Les produits de l'offre (ce sont des routeurs Linux, pas des FortiGate), le choix du chemin par application du SD-WAN, le ZTNA et la MFA, la haute disponibilité, la capacité pour 10 000 utilisateurs, la résilience physique des datacenters (`docs/OFFRE_TECHNIQUE.md` §18). Le dire nous rend crédibles.

---

## 5. Ce que l'incident nous a appris

### 5.1 Ce qui s'est passé

Le serveur loué pour la maquette a été **piraté** avant même que la maquette existe (`docs/INCIDENT_PAR861454.md`).

| Date | Événement |
|---|---|
| 01/10/2026, 18:37 | Date du fichier malveillant (`sshdd.so`) : début probable de la compromission |
| 15/10 vers 11:57 | Premier symptôme : les tâches de Proxmox échouent (« Permission denied » en root) |
| 16/10, matin | Diagnostic : une bibliothèque malveillante est injectée dans les programmes du système ; rapport d'incident |
| 16/10 | Serveur réinstallé par son responsable, **sans collecte préalable des preuves** |
| 16/10, journée | Durcissement : SSH par clé uniquement, interface Proxmox fermée à Internet, pare-feu |
| 19/10 | Accès des camarades limité à un tunnel vers l'interface EVE |

**Le point d'entrée le plus probable** : le SSH, ouvert sur Internet, avec authentification par mot de passe. Des mots de passe faibles circulaient dans un script partagé. Ce point n'a pas pu être confirmé, faute de preuves conservées.

### 5.2 Comment fonctionnait l'implant, en clair

Un **rootkit** s'était glissé dans le mécanisme de chargement des bibliothèques de Linux (`ld.so.preload`). Chaque programme lancé chargeait aussi le code de l'attaquant. Ce code :

- se cachait lui-même, même à l'administrateur root ;
- était chargé par le programme qui vérifie les mots de passe : **chaque mot de passe tapé pouvait être volé** ;
- bloquait certaines opérations sur les journaux.

*Analogie* : un faux guichetier s'est installé entre vous et la banque. Il transmet vos opérations normalement, mais il lit votre code au passage, et il efface sa propre photo des caméras.

Une conséquence importante : **un système compromis ment**. Les constats faits depuis le système en marche peuvent être faussés. Il faut les vérifier depuis un système sain (le mode rescue).

### 5.3 Les leçons, et leur traduction dans notre offre

| Ce qu'on a constaté | Ce qu'on a fait sur notre serveur | Ce que ça donne dans l'offre |
|---|---|---|
| Un SSH par mot de passe exposé sur Internet est une cible | SSH par clé uniquement (`00_durcissement_ssh.sh`) | MFA partout ; administration par le bastion seulement |
| Des interfaces d'administration étaient joignables | Interface Proxmox liée à la machine elle-même, jointe par tunnel ; pare-feu en refus par défaut (`03_p0_securite.sh`) ; vérifié depuis l'extérieur : seul SSH répond | Aucune interface d'administration sur Internet ; infogérants par ZTNA vers le bastion uniquement |
| Trop de droits pour trop de monde | Compte sans droits root pour l'IA ; compte « camarade » sans mot de passe ni shell, limité à un tunnel (`05_acces_camarades.sh`) | Moindre privilège : comptes nominatifs, approbation, durée limitée (WALLIX) |
| Intrusion invisible pendant au moins deux semaines, découverte par hasard | Contrôle d'intégrité horaire prévu (`docs/PLAN_V2.md` §4) | SIEM Wazuh, journaux envoyés hors des équipements, SOC |
| Réinstaller sans collecter les preuves arrête l'enquête | Script de collecte en mode rescue préparé (`automation/incident/collecte_rescue.sh`) | Procédure de réponse à incident : collecter, puis reconstruire |
| Reconstruire vite et à l'identique | Tout est scripté (scripts 00 à 05, `deploy.py`) | Configurations centralisées (FortiManager), sauvegardes immuables |

Un détail qui compte : le pare-feu du serveur a été appliqué avec une **minuterie de retour arrière** de 5 minutes. Si la règle nous avait enfermés dehors, elle se serait retirée toute seule. C'est une bonne pratique à citer pour tout changement à distance.

---

## 6. À retenir

1. **Le besoin** : 530 sites, 10 000 utilisateurs, une centaine de partenaires, des données de santé, et un client qui veut payer au mois.
2. **La réponse** : SD-WAN Fortinet sur Internet vers 2 datacenters HDS, refus par défaut partout, Zero Trust pour les accès distants, bastion pour l'infogérance.
3. **Le coût** : 221,4 k€ HT par mois sur 36 mois, sans investissement de départ, soit 22,14 € par utilisateur (`docs/CHIFFRAGE.md`).
4. **La preuve** : 17 flux sur 17 conformes et une bascule WAN en 3,8 s, avec des preuves horodatées et vérifiables.
5. **L'honnêteté** : la maquette prouve des principes, pas les produits ; le ZTNA, la MFA et la haute disponibilité n'y sont pas.
6. **Le retour d'expérience** : notre propre serveur a été piraté par un accès d'administration mal protégé. Notre offre applique ce que nous avons appris.

Pour aller plus loin : votre fiche de rôle dans `docs/ROLES_SOUTENANCE.md`, puis la section de `docs/OFFRE_TECHNIQUE.md` qui correspond à vos diapositives.
