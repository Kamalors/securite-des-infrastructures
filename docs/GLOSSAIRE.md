# Glossaire du projet

Tous les sigles et termes techniques du projet, par ordre alphabétique. Pour chacun : une définition courte, puis **où il intervient chez nous**. Pour le contexte général, lisez d'abord [GUIDE_EXPLICATIF.md](GUIDE_EXPLICATIF.md).

Les montants cités renvoient à `docs/CHIFFRAGE.md`, qui fait foi.

Accès rapide : [0-9](#0-9) · [A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [J-K](#j-k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w) · [X-Z](#x-z)

## 0-9

| Terme | Définition | Dans notre projet |
|---|---|---|
| **3-2-1 (règle)** | Règle de sauvegarde : 3 copies des données, sur 2 supports différents, dont 1 hors site. | Sauvegarde Veeam : dépôt dans l'autre DC et copie immuable chez un hébergeur de stockage objet français (`docs/OFFRE_TECHNIQUE.md` §6). |
| **4G / 5G (secours)** | Accès Internet par le réseau mobile, utilisé quand la fibre tombe. | Intégré au FortiGate 40F-3G4G des agences (SIM data), en secours dans les sièges. |
| **802.1X** | Norme d'authentification à l'entrée du réseau : un poste doit prouver son identité avant d'obtenir un accès filaire ou Wi-Fi. | Wi-Fi d'entreprise authentifié via le fournisseur d'identité, dans tous les sites (`docs/OFFRE_TECHNIQUE.md` §10). |

## A

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Actif/actif, actif/passif** | Actif/actif : les deux sites servent en même temps. Actif/passif : un site sert, l'autre attend pour prendre le relais. | Actif/actif pour la publication web et les accès distants ; actif/passif pour les bases de données (`docs/OFFRE_TECHNIQUE.md` §5). |
| **Agent / sans agent** | Un agent est un logiciel installé sur le poste. « Sans agent » : l'accès se fait par un simple navigateur, via un portail. | FortiClient sur les postes des nomades ; portail sans agent pour les partenaires nomades, dont on ne gère pas les postes. |
| **AO, RAO** | Appel d'offres ; réponse à appel d'offres. | Le sujet du projet : répondre au PDF de la mutuelle. |
| **API** | Interface qui permet à des logiciels de dialoguer entre eux (souvent en HTTPS). | Publiée sur Internet derrière le WAF F5. EVE-NG a aussi une API, utilisée pour créer le lab (`automation/eve/creer_lab.js`). |
| **Aruba (HPE)** | Constructeur de switchs et de bornes Wi-Fi. Aruba Central est sa console de gestion dans le cloud. | Switchs CX 6100 et CX 8100, bornes Wi-Fi 6E AP-615, pilotés par Aruba Central. Alternative : Cisco Catalyst / Meraki. |

## B

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Baie 42U, U** | Armoire standard pour serveurs. Un U (unité) vaut 4,445 cm de hauteur ; une baie de 42U accueille 42 unités. | 2 baies 42U et 6 kW par datacenter. |
| **Bascule (failover)** | Passage automatique sur un équipement ou un chemin de secours quand le principal tombe. | Mesurée dans la maquette : coupure de l'opérateur A d'une agence, bascule sur B en 3,8 s (`evidence/20261016T181400Z/bascule_wan.txt`). |
| **Bastion, PAM** | Le bastion est le point de passage obligé pour administrer les systèmes. PAM (Privileged Access Management) : gestion des comptes à privilèges (MFA, approbation, enregistrement des sessions). | WALLIX Bastion pour 50 comptes à privilèges. Dans la maquette, un conteneur `bastion` seul autorisé à joindre les serveurs en SSH (F09, F10, N08). |
| **BCE (taux)** | Taux de change de référence publié par la Banque centrale européenne. | Conversion des prix en dollars et en livres (taux du 15/10/2026, `docs/CHIFFRAGE.md`). |
| **BCP 38** | Bonne pratique (RFC 2827) : un opérateur rejette les paquets dont l'adresse source n'appartient pas au client qui les envoie. C'est un filtre anti-usurpation. | Ajouté aux faux opérateurs de la maquette : sans lui, le tunnel A survivait à la coupure du lien A (`automation/lab/deploy.py`). |
| **Broadcom** | Société qui a racheté VMware et changé ses licences. | Question probable du jury : « pourquoi VMware après le rachat ? ». Alternatives documentées : Proxmox VE, Nutanix. |

## C

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Carrier-neutral** | Datacenter où plusieurs opérateurs télécoms sont présents : le client choisit librement les siens. | Critère de choix des 2 datacenters (au moins deux opérateurs par chemins distincts). |
| **CASB** | Cloud Access Security Broker : contrôle l'usage des applications cloud (quelles applications, quelles données). | Inclus dans FortiSASE pour les nomades. |
| **Cato Networks** | Éditeur SASE entièrement dans le cloud. | Candidat B pour le WAN et le SASE, écarté au profit de Fortinet. |
| **Clauses contractuelles types (CCT)** | Modèles de contrat de la Commission européenne pour encadrer un transfert de données personnelles hors de l'UE. | Transferts vers les agences hors UE (`docs/OFFRE_TECHNIQUE.md` §19). |
| **Cloud Act** | Loi américaine de 2018 : les autorités des États-Unis peuvent exiger des données d'un fournisseur américain, même stockées hors des États-Unis. | Question probable du jury (`docs/ROLES_SOUTENANCE.md`, rôle 5). À préparer : nos services cloud (FortiSASE, FortiManager Cloud) sont fournis par un éditeur américain. |
| **Colocation** | Voir *Housing*. | — |
| **Conteneur LXC** | Voir *LXC*. | — |
| **Cross-connect** | Câble physique, dans le datacenter, entre la baie du client et l'équipement d'un opérateur. Facturé par l'hébergeur. | Non inclus dans le chiffrage (sur devis de l'hébergeur). |

## D

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Datacenter (DC)** | Bâtiment sécurisé qui héberge des serveurs, avec alimentation, refroidissement et accès réseau. | 2 DC en housing, certifiés HDS, dans deux domaines de panne distincts. |
| **DDoS** | Attaque par déni de service distribué : des milliers de machines saturent un service. | Protection volumétrique en option chez les opérateurs de transit. |
| **Défense en profondeur** | Empiler plusieurs barrières indépendantes, pour qu'une seule faille ne suffise pas. | Pare-feu périmètre puis pare-feu interne, WAF, bastion, MFA, journalisation. |
| **DHCP** | Protocole qui distribue automatiquement les adresses IP. | Réseau de gestion de la maquette : DHCP sans passerelle ni DNS, pour éviter les faux résultats de test. |
| **DMZ** | Zone démilitarisée : réseau isolé qui accueille les serveurs exposés à Internet, séparé du réseau interne. | Contient le WAF et la passerelle SFTP. Dans la maquette : `srv-web` (10.11.10.10). |
| **DNAT, NAT** | Traduction d'adresses. Le NAT source cache les adresses internes derrière une adresse publique. Le DNAT (destination) redirige une adresse publique vers un serveur interne. | Maquette : DNAT de l'adresse publique vers `srv-web` (ports 443 et 22) ; NAT de sortie Internet à l'agence. Cible : NAT des partenaires dont les plages d'adresses se chevauchent. |
| **DNS** | Annuaire d'Internet : traduit un nom en adresse IP. | DNS internes ; répartition DNS pour l'actif/actif entre les 2 DC. Flux F12, non testé. |
| **DORA** | Digital Operational Resilience Act, règlement UE 2022/2554, applicable depuis le 17/01/2025 aux entités financières dont les assurances. Exige notamment la maîtrise des prestataires informatiques et une stratégie de sortie. | Registre des prestataires, clauses, plan de réversibilité face à la dépendance à Fortinet. Applicabilité exacte à la mutuelle à vérifier (`docs/EXIGENCES.md` §4). |
| **DPD** | Dead Peer Detection : un bout du tunnel IPsec vérifie régulièrement que l'autre répond. | Toutes les 5 s dans la maquette. |
| **DSI** | Direction des systèmes d'information. | La DSI du client « ne permet pas de débloquer une grosse somme d'un coup » : d'où l'abonnement. |

## E

| Terme | Définition | Dans notre projet |
|---|---|---|
| **EEE** | Espace économique européen : UE + Islande, Liechtenstein, Norvège. | Les sites d'hébergement des données de santé doivent s'y trouver. |
| **Empreinte (SHA-256)** | Résumé unique d'un fichier, calculé par une fonction de hachage. Si un seul octet change, l'empreinte change. Ce n'est pas une signature : elle prouve l'intégrité, pas l'auteur. | Fichier `SHA256SUMS` dans chaque dossier de preuves ; commande de vérification dans le README. |
| **Entra ID** | Fournisseur d'identité de Microsoft (ex-Azure AD). | Exemple de fournisseur d'identité supposé existant chez le client (H12). |
| **Erasure coding, RAID 5** | Technique qui répartit données et parité sur plusieurs disques ou serveurs : on survit à la perte d'un élément sans tout dupliquer. | Stockage vSAN des clusters (`docs/OFFRE_TECHNIQUE.md` §6). |
| **Est-ouest** | Trafic entre serveurs, à l'intérieur du datacenter. | Filtré par la 2e paire de FortiGate 600F ; refus testés N03 et N04. |
| **ETP** | Équivalent temps plein. | Infogérance NOC/SOC : 3 ETP en heures ouvrées. |
| **EVE-NG** | Logiciel qui simule des réseaux complets avec de vrais systèmes (routeurs, pare-feu) dans des machines virtuelles. L'édition gratuite PRO Freemium limite chaque lab à 7 nœuds. | Héberge les 7 routeurs de la maquette ; la limite de 7 nœuds a conduit à mettre les serveurs en LXC (décision D1, `docs/PLAN_V2.md`). |

## F

| Terme | Définition | Dans notre projet |
|---|---|---|
| **F5 BIG-IP Advanced WAF** | Reverse proxy et pare-feu applicatif web de l'éditeur F5. | 4 instances virtuelles en abonnement (2 par DC), devant le web et les API. Alternative : Cloudflare WAF. |
| **FortiCare, FortiGuard** | FortiCare : support de Fortinet. FortiGuard : services de renseignement sur les menaces (signatures, réputation) qui alimentent les FortiGate. | Inclus dans les bundles FortiGate 3 ans (FortiCare Premium, UTP). |
| **FortiClient** | Agent Fortinet installé sur le poste du nomade. | Un seul agent pour la sécurité Internet et le ZTNA, au lieu de deux avec ZPA. |
| **FortiGate** | Pare-feu nouvelle génération de Fortinet, qui fait aussi le SD-WAN. | 570 boîtiers : 498 × 40F-3G4G (agences FR), 60 × 70G (international), 4 × 200G (sièges), 8 × 600F (DC). Plus 10 en spare. |
| **FortiManager** | Console centrale qui configure tous les FortiGate. | FortiManager Cloud, 6 lots de 100 équipements. |
| **FortiSASE** | Service SASE de Fortinet dans le cloud : sécurité Internet et ZTNA pour les utilisateurs hors des locaux. | 3 300 licences (3 000 nomades + 300 utilisateurs partenaires) ; remplace Zscaler ZPA. |
| **FRR** | Logiciel libre de routage (OSPF, BGP…) pour Linux. | Fait tourner OSPF sur les routeurs de la maquette. |
| **FTP, FTPS, SFTP** | FTP : transfert de fichiers en clair (mots de passe compris). FTPS : FTP chiffré par TLS. SFTP : transfert de fichiers par SSH, un autre protocole. | Le FTP du client est remplacé par une passerelle SFTP en DMZ (flux F02). Le FTP en clair reste une exception isolée. |
| **FTTH, FTTO** | FTTH : fibre mutualisée, débit non garanti, peu chère. FTTO : fibre dédiée à l'entreprise, débit garanti, plus chère. | FTTH dans les 498 agences ; 2 FTTO 1 Gbit/s par siège, chez deux opérateurs. |

## G

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Gartner Magic Quadrant** | Classement annuel des éditeurs d'un marché par le cabinet Gartner ; les mieux placés sont les « Leaders ». | SASE 2026 : Cato est « Leader », Fortinet « Challenger » (« Leader » en 2025) ; Fortinet est « Leader » 2026 des pare-feu (`docs/QUESTIONS_JURY.md`, Q48). |
| **Gigue** | Variation du délai de transmission entre paquets. Gênante pour la voix et la vidéo. | Mesurée par le SD-WAN, avec la latence et la perte, pour choisir le chemin. |
| **GTI** | Garantie de temps d'intervention de l'opérateur après une panne. | Fibre des agences avec GTI 8 h (`docs/CHIFFRAGE.csv`). |

## H

| Terme | Définition | Dans notre projet |
|---|---|---|
| **HA (haute disponibilité)** | Deux équipements en paire : si l'un tombe, l'autre prend le relais. | Règle : HA au-delà de 50 utilisateurs (sièges, agences internationales, DC). Non prouvée par la maquette. |
| **HDS** | Hébergeur de données de santé : certification obligatoire en France pour héberger des données de santé pour le compte d'un tiers. | Exigée pour les 2 datacenters et l'infogérant ; à vérifier dans l'annuaire du certificateur. |
| **HLD, LLD** | High Level Design : schéma de principe, sans le détail. Low Level Design : configuration détaillée. | 4 HLD demandés par le client, dans le diaporama (diapositives 5, 9, 13, 17). Pas de LLD : les scripts de la maquette en tiennent lieu. |
| **Housing (colocation)** | Location d'espace, d'électricité et de refroidissement dans un datacenter ; le client y installe ses propres serveurs. | Imposé par le PDF. 2 baies par DC, prix de référence 470,40 € par baie et par mois hors énergie. |
| **HT** | Hors taxes. | Tous les montants du chiffrage. |
| **Hub & spoke, double hub** | Topologie en étoile : les sites (rayons) se relient à un centre (hub). Double hub : chaque site est relié à deux centres. | Chaque site monte des tunnels vers les 2 DC. Les FortiGate 600F du périmètre sont les hubs. |
| **Hyperviseur** | Logiciel qui fait tourner plusieurs machines virtuelles sur un serveur physique. | VMware vSphere en production ; Proxmox VE pour la maquette. |

## I

| Terme | Définition | Dans notre projet |
|---|---|---|
| **IdP (fournisseur d'identité)** | Service central qui authentifie les utilisateurs (et applique la MFA) pour les autres applications, via SAML ou OIDC. | Supposé existant chez le client (H12) ; utilisé par FortiSASE, le Wi-Fi 802.1X et le bastion. Indépendant de Fortinet, pour limiter la dépendance. |
| **IKEv2** | Protocole qui authentifie les deux bouts d'un tunnel IPsec et négocie les clés de chiffrement. | Tous les tunnels de la maquette (strongSwan), avec une clé partagée régénérée à chaque déploiement. |
| **Immuable (sauvegarde)** | Copie qu'on ne peut ni modifier ni effacer pendant sa durée de rétention, même avec des droits d'administrateur. | Copie Veeam chez un hébergeur de stockage objet français : parade au rançongiciel. |
| **Infogérance** | Exploitation du système d'information confiée à un prestataire. | Accès des infogérants par ZTNA vers le bastion seulement ; NOC/SOC en heures ouvrées chiffré. |
| **IoC** | Indicateur de compromission : trace technique qui signale une intrusion (fichier, empreinte, adresse). | Listés dans `docs/INCIDENT_PAR861454.md` (fichier `sshdd.so`, verrou `/run/sshdd.lock`…). |
| **IPS** | Système de prévention d'intrusion : détecte et bloque les attaques connues dans le trafic. | Fonction des FortiGate (pack UTP). |
| **IPsec** | Ensemble de protocoles qui chiffre et authentifie le trafic IP entre deux points : c'est le « tunnel VPN ». | Base du SD-WAN et des liaisons partenaires site à site. Maquette : 6 tunnels depuis `fw-dc1`. |
| **ISP, opérateur, transit** | Fournisseur d'accès Internet. Le transit est l'accès Internet haut débit d'un datacenter. | 2 transits 1 Gbit/s par DC. Dans la maquette, `isp-a` et `isp-b` jouent les opérateurs. |

## J-K

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Journalisation** | Enregistrer chaque événement (connexion acceptée, refusée…) dans un journal, de préférence hors de l'équipement. | Chaque flux autorisé est journalisé (SIEM). Maquette : étiquettes « RAO-OK » et « RAO-REFUS », envoyées au conteneur `logs`. |
| **KVM, virtualisation imbriquée** | KVM : la virtualisation intégrée au noyau Linux. Imbriquée : une machine virtuelle qui fait elle-même tourner des machines virtuelles. | La VM EVE-NG fait tourner les routeurs : il a fallu activer la virtualisation imbriquée sur le serveur (`docs/PREFLIGHT.md`). |

## L

| Terme | Définition | Dans notre projet |
|---|---|---|
| **LAN, WAN** | LAN : réseau local d'un site. WAN : réseau étendu qui relie des sites distants. | LAN Aruba dans chaque site ; WAN en SD-WAN sur Internet. |
| **Latence** | Temps de trajet d'un paquet. | Mesurée par le SD-WAN pour choisir le chemin. |
| **ld.so.preload, LD_PRELOAD** | Mécanisme de Linux qui charge une bibliothèque dans tous les programmes au démarrage. Détourné, il permet d'espionner tout le système. | Technique du rootkit trouvé sur notre serveur (`docs/INCIDENT_PAR861454.md`). |
| **Location financière** | Un bailleur achète le matériel et le loue au client contre des loyers mensuels constants. | Finance les frais initiaux sur 36 mois à 7 % par an (hypothèse) : c'est ce qui permet l'abonnement. Formule dans `docs/CHIFFRAGE.md`, « Méthode ». |
| **LXC** | Conteneurs Linux : des environnements isolés qui partagent le noyau de l'hôte. Plus légers qu'une machine virtuelle. | Les 8 serveurs et postes clients de la maquette (`automation/host/04_lxc_lab.sh`). |

## M

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Maquette, recette** | Maquette : modèle réduit qui démontre les principes. Recette : série de tests qui vérifie le résultat attendu. | 7 routeurs + 8 conteneurs ; recette de 17 tests, tous conformes (`automation/lab/recette.py`). |
| **MFA** | Authentification multifacteur : il faut deux preuves de natures différentes (mot de passe + code ou clé). | Exigée pour les nomades, les partenaires et le bastion. Non modélisée dans la maquette. |
| **Micro-segmentation** | Filtrage au plus près de chaque machine virtuelle, dans l'hyperviseur. | Option mentionnée pour l'est-ouest (`docs/HLD.md` §1.5). |
| **Moindre privilège** | Donner à chacun uniquement les droits nécessaires, et pour une durée limitée. | Bastion, droits par application en ZTNA, compte « camarade » limité à un tunnel. |
| **MOBIKE** | Extension d'IKEv2 qui permet à un tunnel de changer d'adresse sans être recréé. | Désactivée dans la maquette : elle « déménageait » le tunnel A sur l'opérateur B et masquait la bascule. |
| **Mouvement latéral** | Rebond d'un attaquant d'une machine compromise vers les autres du même réseau. | Ce que la segmentation est-ouest empêche. |
| **MPLS** | Réseau privé d'opérateur, avec qualité de service garantie, mais cher. | Écarté au profit du SD-WAN sur Internet ; option pour les sièges si un SLA de bout en bout est exigé. |
| **MTU** | Taille maximale d'un paquet sur un lien. Le chiffrement ajoute des en-têtes : il faut la réduire dans les tunnels. | 1 400 octets sur les tunnels de la maquette. |

## N

| Terme | Définition | Dans notre projet |
|---|---|---|
| **N+1** | Dimensionnement avec un élément de plus que nécessaire : on peut en perdre un sans perte de capacité utile. | Cluster de 4 serveurs par DC. |
| **nc (netcat)** | Petit outil qui ouvre une connexion vers une adresse et un port. | Utilisé par la recette pour tester chaque flux. |
| **NGFW** | Pare-feu nouvelle génération : filtre par application et par utilisateur, avec IPS et antivirus, et pas seulement par adresse et port. | Les FortiGate. Alternative : Palo Alto. |
| **nftables** | Le pare-feu intégré au noyau Linux (successeur d'iptables). | Pare-feu des routeurs de la maquette et du serveur Proxmox ; politique « refus par défaut ». |
| **NOC, SOC** | NOC : centre qui surveille le réseau. SOC : centre qui surveille la sécurité et traite les alertes. | 3 ETP en heures ouvrées ; SOC 24/7 en option, non chiffré. |
| **Nœud** | Un équipement simulé dans EVE-NG. | 7 nœuds : la limite de l'édition Freemium. |
| **Nord-sud** | Trafic entre Internet et le datacenter. | Pare-feu périmètre, DMZ, WAF ; tests F01, F02, N01, N02. |
| **NTP** | Protocole de synchronisation de l'heure. Indispensable pour corréler les journaux. | Service socle (flux F12). |

## O

| Terme | Définition | Dans notre projet |
|---|---|---|
| **OSPF** | Protocole de routage dynamique : les routeurs échangent la carte du réseau et calculent le chemin le moins coûteux. | Maquette : coût 10 par l'opérateur A, 100 par B ; un voisin muet 4 s est déclaré mort, ce qui est cohérent avec la bascule mesurée de 3,8 s. |
| **Overlay, underlay** | L'underlay est le réseau physique (les accès Internet). L'overlay est le réseau logique construit par-dessus (les tunnels). | Le SD-WAN est un overlay de tunnels IPsec sur un underlay d'accès Internet. |
| **OWASP** | Fondation qui publie notamment le « Top 10 » des risques des applications web. | Protections OWASP assurées par le WAF F5. |

## P

| Terme | Définition | Dans notre projet |
|---|---|---|
| **PAM** | Voir *Bastion, PAM*. | — |
| **Perte de paquets** | Part des paquets qui n'arrivent pas. | Mesurée par le SD-WAN ; dans la recette, 19 paquets perdus sur 125 pendant la bascule. |
| **PoE** | Power over Ethernet : le switch alimente l'appareil (borne Wi-Fi, téléphone) par le câble réseau. | Switchs Aruba CX 6100 PoE. |
| **Posture (contrôle de)** | Vérification de l'état du poste avant de donner l'accès : système à jour, antivirus actif, poste géré. | Exigée par FortiSASE pour les nomades. |
| **PRA, PCA** | Plan de reprise d'activité (redémarrer après un sinistre) ; plan de continuité d'activité (ne pas s'arrêter). | Deux DC ne font pas un PRA tant que les RPO/RTO ne sont pas fixés (H4). |
| **Proxmox VE** | Hyperviseur libre qui gère des machines virtuelles (KVM) et des conteneurs (LXC). | Socle de la maquette ; alternative documentée à VMware. |
| **PSK** | Clé pré-partagée : le même secret configuré aux deux bouts d'un tunnel. | Maquette : PSK aléatoires, régénérées à chaque `deploy.py`, jamais stockées dans le projet. |
| **PUE** | Power Usage Effectiveness : énergie totale du datacenter divisée par l'énergie des serveurs. 1,5 signifie 50 % de plus pour le refroidissement et le reste. | Calcul du coût de l'énergie (PUE 1,5, `docs/CHIFFRAGE.csv`). |

## R

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Rançongiciel (ransomware)** | Logiciel malveillant qui chiffre les données et exige une rançon. | Parades : copie immuable, segmentation, bastion, MFA. |
| **Refus par défaut** | Tout est interdit, sauf ce qui est explicitement autorisé (liste blanche). | Principe de toute l'architecture : 13 flux autorisés et documentés dans `docs/FLUX.md`. |
| **Réplication synchrone / asynchrone** | Synchrone : l'écriture est confirmée quand les deux sites l'ont enregistrée (zéro perte, mais exige des sites proches). Asynchrone : l'autre site reçoit la copie avec un léger décalage. | Réplication asynchrone des bases vers l'autre DC. |
| **Reverse proxy** | Serveur placé devant les applications : il reçoit les requêtes d'Internet et les transmet, après contrôle. | Le F5 en DMZ, qui termine aussi le TLS. |
| **Réversibilité, stratégie de sortie** | Capacité à quitter un fournisseur et à récupérer ses données et ses services. | Exigée par DORA ; plan de réversibilité face à la dépendance à Fortinet. |
| **RFC 1918, RFC 5737** | RFC 1918 : plages d'adresses privées (10.0.0.0/8…). RFC 5737 : plages réservées à la documentation. | Maquette : adresses privées 10.x en interne, plages RFC 5737 pour simuler Internet (`inventory/addressing.csv`). |
| **RGPD (article 9)** | Règlement européen sur les données personnelles. L'article 9 encadre les catégories particulières, dont la santé. | Données de santé de la mutuelle ; transferts hors UE à encadrer. |
| **Rootkit** | Logiciel malveillant qui s'installe au cœur du système et se cache, même à l'administrateur. | Trouvé sur notre serveur : `sshdd.so`, chargé par `ld.so.preload` (`docs/INCIDENT_PAR861454.md`). |
| **Route-based (VPN)** | Tunnel qui apparaît comme une interface réseau : c'est le routage qui décide d'y envoyer le trafic. | Tunnels de la maquette (interfaces XFRM `xa-…`, `xb-…`), ce qui laisse OSPF choisir. |
| **RPO, RTO** | RPO : quantité maximale de données qu'on accepte de perdre, exprimée en temps. RTO : durée maximale d'interruption acceptée. | À fixer avec le client (hypothèse H4). |

## S

| Terme | Définition | Dans notre projet |
|---|---|---|
| **SASE, SSE** | SASE (Secure Access Service Edge) : réseau (SD-WAN) et sécurité réunis dans un service cloud. SSE (Security Service Edge) : la partie sécurité seule (SWG, CASB, ZTNA). | FortiSASE pour les nomades et les partenaires nomades. |
| **SD-WAN** | Réseau étendu piloté par logiciel : il utilise plusieurs accès (fibre, 4G…) et choisit le meilleur chemin par application, selon la qualité mesurée. | Fortinet Secure SD-WAN sur tous les sites, en double hub vers les 2 DC. |
| **Segmentation, zone** | Découper le réseau en zones isolées, avec un filtrage entre elles. | Zones DMZ, applications, données, administration, partenaires dans le DC ; utilisateurs, invités, administration, téléphonie dans les sites. |
| **SIEM** | Outil qui centralise et corrèle les journaux de tous les équipements pour détecter les attaques. | Wazuh (open source, 0 € de licence). Alternatives : Splunk, Sentinel. |
| **SLA** | Engagement de niveau de service (disponibilité, délai de rétablissement…). | Critère pour garder une option MPLS sur les sièges ; à fixer avec le client (H4). |
| **Spare** | Stock d'équipements de rechange. | 2 % du parc agences : 10 FortiGate, 10 switchs, 15 bornes. |
| **SSH, ProxyJump** | SSH : connexion chiffrée à distance à une machine. ProxyJump : passer par une machine intermédiaire (rebond). | Accès aux nœuds de la maquette par rebond via le serveur puis EVE (`automation/ssh_config`). Porte d'entrée probable de l'incident. |
| **strongSwan** | Logiciel libre IPsec/IKEv2 pour Linux. | Tunnels de la maquette. |
| **SWG** | Secure Web Gateway : filtre la navigation web (catégories, réputation, antivirus). | Inclus dans FortiSASE. |
| **Syslog** | Protocole standard d'envoi des journaux vers un collecteur. Le port 6514 est celui du syslog chiffré par TLS. | Maquette : journaux du noyau envoyés au conteneur `logs` sur le port 6514, par le réseau de gestion. |

## T

| Terme | Définition | Dans notre projet |
|---|---|---|
| **TCO** | Total Cost of Ownership : coût complet sur une durée (achat, abonnements, exploitation). | Calculé sur 36 mois, en achat et en abonnement (`docs/CHIFFRAGE.md`). |
| **Tier III** | Niveau de l'Uptime Institute : le datacenter peut être entretenu sans arrêt, grâce à des équipements et chemins redondants (environ 99,98 % de disponibilité). | Critère de choix des 2 datacenters. |
| **TJM** | Taux journalier moyen d'un prestataire. | Déploiement et infogérance à 510 € par jour, pilotage à 750 € (`docs/CHIFFRAGE.csv`). |
| **TLS, HTTPS** | TLS : protocole de chiffrement des connexions. HTTPS : le web chiffré par TLS. La « terminaison TLS » consiste à déchiffrer au reverse proxy pour inspecter. | Publication web en HTTPS (F01) ; terminaison TLS sur le WAF. |
| **TOTP** | Code à usage unique qui change toutes les 30 secondes (application d'authentification). | Prévu pour la MFA du serveur Proxmox (`docs/PLAN_V2.md`) ; mentionné comme preuve visée pour le bastion dans `docs/EXIGENCES.md`, non réalisé dans la maquette. |
| **Tunnel SSH** | Redirection d'un port local vers une machine distante, à travers une connexion SSH. | Accès à l'interface d'EVE (https://localhost:8443) pour le groupe (`automation/connexion_rao.ps1`). |

## U

| Terme | Définition | Dans notre projet |
|---|---|---|
| **UTP** | Unified Threat Protection : pack de services de sécurité Fortinet (IPS, antivirus, filtrage web et applicatif…) vendu avec le boîtier. | Tous les FortiGate sont chiffrés avec 3 ans d'UTP. Sert au filtrage de la sortie Internet locale en agence. |

## V

| Terme | Définition | Dans notre projet |
|---|---|---|
| **Veeam** | Logiciel de sauvegarde des machines virtuelles. | Veeam Data Platform pour 300 VM, avec copie immuable. |
| **VM** | Machine virtuelle : un ordinateur simulé par l'hyperviseur. | 300 VM en production (hypothèse H8) ; la maquette tourne dans une VM EVE-NG. |
| **VMware vSphere Foundation (VVF)** | Offre de virtualisation VMware, vendue par cœur et par an, qui inclut une part de stockage vSAN. | 512 cœurs (8 serveurs × 64). |
| **VPN** | Réseau privé virtuel : tunnel chiffré qui relie un poste ou un site à un réseau. Un VPN donne en général accès à tout le réseau. | IPsec site à site pour les sites et les partenaires. Pour les nomades, nous préférons le ZTNA. |
| **vSAN** | Stockage de VMware qui utilise les disques internes des serveurs du cluster (architecture « hyperconvergée »). | 64 TiB par DC inclus dans la licence VVF ; extension éventuelle non chiffrée. |

## W

| Terme | Définition | Dans notre projet |
|---|---|---|
| **WAF** | Web Application Firewall : pare-feu qui lit le contenu des requêtes web et bloque les attaques applicatives (injection, etc.). | F5 BIG-IP Advanced WAF en DMZ. Non testé dans la maquette. |
| **WALLIX** | Éditeur français de bastion (PAM). | Bastion de l'offre, 50 comptes. Alternatives : Delinea, CyberArk. |
| **Wazuh** | SIEM et outil de détection open source. | SIEM de l'offre, hébergé sur le compute. |
| **Wi-Fi 6E** | Wi-Fi 6 étendu à la bande des 6 GHz, moins encombrée. | Bornes Aruba AP-615 : 1 pour 25 utilisateurs, 748 au total. |

## X-Z

| Terme | Définition | Dans notre projet |
|---|---|---|
| **XFRM** | Le cadre du noyau Linux qui gère IPsec. Une « interface XFRM » fait apparaître un tunnel comme une interface réseau. | Chaque tunnel de la maquette est une interface (`xa-agfr`, `xb-dc1`…). |
| **Zero Trust** | Principe « ne jamais faire confiance, toujours vérifier » : aucun utilisateur ni réseau n'est de confiance par défaut ; chaque accès est vérifié. | Fil rouge de l'offre : ZTNA, MFA, refus par défaut, bastion. |
| **Zone partenaire** | Zone du datacenter réservée aux partenaires, isolée du reste. | Terminaison des tunnels IPsec des partenaires site à site ; accès aux seules applications contractuelles (F06, N06). |
| **Zscaler ZPA** | Zscaler Private Access, service ZTNA de l'éditeur Zscaler. | Candidat initial, écarté : la fonction est comprise côté utilisateur dans FortiSASE (1,99 M€ bruts évités sur 36 mois, au moins 1,5 M€ une fois ajoutées les licences des hubs, Q47). |
| **ZTNA** | Zero Trust Network Access : accès à une application précise après vérification de l'identité, de la MFA et du poste, au lieu d'un accès au réseau entier. | Assuré par FortiSASE pour les nomades, les partenaires nomades et les infogérants (vers le bastion). Non modélisé dans la maquette (F07, F08, N07, N09). |
