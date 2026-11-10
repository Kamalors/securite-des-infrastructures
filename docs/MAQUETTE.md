# Maquette EVE-NG du projet RAO — documentation de référence

État : **vérifiée le 10/11/2026**, après réparation du disque plein de fw-dc1 (§ 8). Les 15 machines répondent, avec 6 tunnels IPsec et 5 voisins OSPF. La recette est **conforme** (17/17 flux, bascule WAN en 3 à 4 s). Preuves : `evidence/20261110T183628Z/` ; recettes précédentes : `evidence/20261028T200408Z/`, `evidence/20261016T181400Z/`.
Démonstration de soutenance pas à pas : `docs/DEMO_EVE.md`. Matrice de flux : `docs/FLUX.md`. Inventaire : `inventory/topology.yml`, `inventory/addressing.csv`.

---

## 1. À quoi sert la maquette (et ce qu'elle ne prouve pas)

L'offre propose une architecture pour 530 sites et deux datacenters (FortiGate, FortiSASE, WAF F5, bastion WALLIX, SIEM). La maquette en est une **réduction fonctionnelle**. Elle reproduit les mêmes principes avec des logiciels libres, puis vérifie automatiquement qu'ils tiennent.

| Principe de l'offre | Ce que la maquette démontre, preuve à l'appui |
|---|---|
| Segmentation et refus par défaut | 10 flux autorisés passent, 7 flux interdits sont bloqués (`recette.csv`) |
| WAN chiffré sur deux opérateurs | 6 tunnels IPsec IKEv2 (AES-GCM) depuis le hub du DC1 |
| Continuité en cas de panne d'un opérateur | Coupure de l'accès A d'une agence : environ 3 à 4 s d'interruption, puis retour automatique sur A |
| Publication maîtrisée | Seuls HTTPS et SFTP sont exposés ; la base de données reste inaccessible depuis Internet |
| Administration par le bastion seul | Le bastion atteint les serveurs ; une agence qui tente de s'y connecter directement est refusée |
| Traçabilité | Chaque flux accepté ou refusé est journalisé et centralisé (`journaux_pare-feu.log`) |
| Reproductibilité | Toute la configuration vient de `deploy.py`, et toute la vérification de `recette.py` |

**Elle ne prouve pas** : la tenue en charge, la haute disponibilité des équipements, le SD-WAN applicatif, le ZTNA, la MFA, le WAF ou un vrai SIEM. Elle ne valide pas non plus le comportement des produits Fortinet eux-mêmes. Voir § 9.

---

## 2. Architecture physique : Proxmox → EVE → nœuds + conteneurs

Pourquoi deux étages ? EVE-NG Freemium limite un lab à **7 nœuds** (décision D1). EVE porte donc les 7 équipements réseau, tandis que les 8 serveurs et clients tournent en **conteneurs LXC Proxmox**. Les deux mondes sont reliés par des ponts Proxmox, vus dans EVE comme des réseaux « Cloud ».

```
 PC (Windows) ── SSH par clé ──► Hôte Proxmox VE 9 « PAR861454 »  163.172.105.87 (seul le port 22 répond)
                                  │
                                  ├─ vmbr0     IP publique
                                  ├─ vmbr1     10.99.0.1/24 + NAT vers Internet (gestion de la VM EVE)
                                  ├─ vmbr2     gestion du lab 10.98.0.0/24 (aucune IP sur l'hôte)
                                  ├─ vmbr10-16 segments métier (aucune IP) ───────────────┐
                                  │                                                       │
                                  ├─ VM 200 « eve-ng-rao » : EVE-NG PRO 7.2 Freemium       │
                                  │    pnet0 = vmbr1 → 10.99.0.10                         │
                                  │    pnet1 = vmbr2 → Cloud1 (DHCP de gestion 10.98.0.2)  │
                                  │    pnet2-8 = vmbr10-16 → Cloud2-8 ◄────────────────────┤
                                  │    lab /RAO.unl : 7 nœuds Debian 13                    │
                                  │      (FRR, strongSwan, nftables, rsyslog)              │
                                  │                                                       │
                                  └─ Conteneurs LXC 301-308 (Debian 13) ◄──────────────────┘
                                       eth0 = segment métier (passerelle = nœud EVE)
                                       eth1 = vmbr2 (gestion 10.98.0.101-108)
```

| Pont Proxmox | Réseau EVE | Segment | Conteneur(s) |
|---|---|---|---|
| vmbr2 | Cloud1 (pnet1) | gestion 10.98.0.0/24 | tous (eth1) |
| vmbr10 | Cloud2 | dc1-dmz | srv-web (301) |
| vmbr11 | Cloud3 | dc1-app | srv-app (302) |
| vmbr12 | Cloud4 | dc1-data | srv-db (303) |
| vmbr13 | Cloud5 | dc1-adm | bastion (304), logs (305) |
| vmbr14 | Cloud6 | agfr-lan | cli-ag (306) |
| vmbr15 | Cloud7 | inet-cli | cli-ext (307) |
| vmbr16 | Cloud8 | agfr-invites | cli-inv (308) |

**Accès** : `ssh -F automation/ssh_config <nom>` depuis la racine du projet. La connexion rebondit de l'hôte (compte `administrateur`) vers EVE (root), puis vers le nœud par le réseau de gestion. On n'utilise ni mot de passe ni `~/.ssh/config`.

### Topologie logique

```
                        cli-ext 192.0.2.10  (« Internet », conteneur)
                              │ inet-cli 192.0.2.0/24
   Opérateur A  ┌───────┐     │      100.64.0.0/30      ┌───────┐  Opérateur B
 198.51.100.0/24│ isp-a ├─────┴─────────────────────────┤ isp-b │203.0.113.0/24
                └───┬───┘                               └───┬───┘
     .10 fw-dc1 ────┤                                       ├──── fw-dc1 .10
     .20 fw-dc2 ────┤                                       ├──── fw-dc2 .20
     .30 gw-hq  ────┤                                       ├──── gw-hq  .30
     .40 gw-agfr────┤                                       ├──── gw-agfr.40
     .60 gw-part────┘   (le partenaire n'a que l'opérateur A)

 Tunnels IPsec (tous terminés sur fw-dc1, le hub) :
                         ┌── xa-agfr  A  coût OSPF 10  ──┐
                         ├── xb-agfr  B  coût OSPF 100 ──┤ gw-agfr ─┬─ cli-ag  10.40.1.10 (agence)
   srv-web  10.11.10.10 ─┤                               │          └─ cli-inv 10.40.2.10 (invités)
   srv-app  10.11.20.20 ─┤                               │
   srv-db   10.11.30.30 ─┼ fw-dc1 ── xa-hq A 10 / xb-hq B 100 ── gw-hq   ── 10.30.1.0/24 (siège)
   bastion  10.11.99.10 ─┤                               │
   logs     10.11.99.20 ─┤                               │
                         ├── xa-dc2   A  coût OSPF 10  ──┤ fw-dc2  ── 10.20.10.0/24 (DC2)
                         └── xa-part  A  routes statiques┘ gw-part ── 10.60.1.0/24 (partenaire)
```

---

## 3. Correspondance cible ↔ maquette

| Cible (offre) | Maquette | Prouvé | Non prouvé |
|---|---|---|---|
| Hubs DC : paire FortiGate 600F en HA par DC (périmètre et hub SD-WAN) | `fw-dc1` seul : Debian avec nftables, strongSwan et FRR | Terminaison des tunnels, routage, filtrage nord/sud | HA, débit, IPS et antivirus |
| Pare-feu interne (2e paire 600F) entre zones | Le même `fw-dc1` : une interface par zone (eth3 DMZ, eth4 app, eth5 données, eth6 admin) | Matrice est/ouest et tests négatifs N03, N04 | Séparation physique périmètre / interne |
| DC2 actif | `fw-dc2` et son LAN, un tunnel via A | DC2 joint par le réseau chiffré | Services, réplication, PRA, tunnel B |
| Sièges : 2 × FortiGate 200G HA, 2 fibres | `gw-hq` sur A et B | Double tunnel, administration F09 | HA |
| 498 agences FR : FortiGate 40F + secours 4G | `gw-agfr` sur A et B (B joue le rôle de la 4G) | Bascule automatique, invités isolés (F13, N05) | Lien 4G réel, choix de chemin par application (SLA SD-WAN) |
| 30 agences internationales | Non déployées (`gw-agint` : même schéma que `gw-hq`) | — | — |
| Opérateurs Internet | `isp-a`, `isp-b`, avec anti-usurpation BCP 38 | Comportement réaliste à la coupure | Latence, perte, MTU réels |
| WAF F5 et SFTP en DMZ | DNAT de fw-dc1 vers `srv-web` (service HTTPS de test) | Seuls 443 et 22 publiés (F01, F02, N01) | WAF, DDoS, ré-chiffrement TLS |
| Partenaires site à site, zone partenaire | `gw-part`, tunnel A, routes statiques | Application seule (F06), base refusée (N06) | NAT de préfixes qui se chevauchent |
| Nomades : FortiSASE ZTNA + MFA | **Non modélisés** | — | F07, F08, N07, N09 |
| Bastion WALLIX | Conteneur `bastion` (SSH simple) | Seule porte d'administration (F09, F10, N08) | MFA, approbation, enregistrement des sessions |
| SIEM Wazuh | Conteneur `logs` : récepteur syslog minimal | Journaux centralisés et horodatés | Corrélation, alertes, rétention, TLS |
| Pilotage central FortiManager | `deploy.py` (configuration décrite dans un fichier, poussée par SSH) | Reproductibilité totale | Gestion à l'échelle de 530 sites |

---

## 4. Adressage

Source : `inventory/addressing.csv`. Les adresses « Internet » viennent des blocs de documentation (RFC 5737), donc ne correspondent à aucun réseau réel.

| Segment | Préfixe | Passerelle | Machines |
|---|---|---|---|
| Opérateur A (opA) | 198.51.100.0/24 | isp-a .1 | fw-dc1 .10, fw-dc2 .20, gw-hq .30, gw-agfr .40, gw-part .60 |
| Opérateur B (opB) | 203.0.113.0/24 | isp-b .1 | fw-dc1 .10, fw-dc2 .20, gw-hq .30, gw-agfr .40 |
| Inter-opérateurs | 100.64.0.0/30 | — | isp-a .1, isp-b .2 |
| Internet simulé (inet-cli) | 192.0.2.0/24 | isp-a .1 | cli-ext .10 |
| DC1 DMZ | 10.11.10.0/24 | fw-dc1 .1 | srv-web .10 |
| DC1 applications | 10.11.20.0/24 | fw-dc1 .1 | srv-app .20 |
| DC1 données | 10.11.30.0/24 | fw-dc1 .1 | srv-db .30 |
| DC1 administration | 10.11.99.0/24 | fw-dc1 .1 | bastion .10, logs .20 |
| DC2 LAN | 10.20.10.0/24 | fw-dc2 .1 | (interne à EVE) |
| Siège LAN | 10.30.1.0/24 | gw-hq .1 | (interne à EVE) |
| Agence FR LAN | 10.40.1.0/24 | gw-agfr .1 | cli-ag .10 |
| Agence FR invités | 10.40.2.0/24 | gw-agfr .1 | cli-inv .10 |
| Partenaire LAN | 10.60.1.0/24 | gw-part .1 | (interne à EVE) |
| Tunnels | 10.255.N.0/30 (N = if_id − 10) | — | .1 = fw-dc1, .2 = site |
| Identifiants OSPF | 10.255.0.1 à .4 | — | fw-dc1, fw-dc2, gw-hq, gw-agfr |
| Gestion du lab | 10.98.0.0/24 | aucune | EVE .2 ; nœuds .11 à .17 ; conteneurs .101 à .108 |
| Gestion EVE | 10.99.0.0/24 | hôte .1 (NAT) | VM EVE .10 |

| Tunnel (hub / site) | if_id | Opérateur | Réseau | Coût OSPF |
|---|---|---|---|---|
| xa-agfr / xa-dc1 | 11 | A | 10.255.1.0/30 | 10 |
| xb-agfr / xb-dc1 | 12 | B | 10.255.2.0/30 | 100 |
| xa-hq / xa-dc1 | 13 | A | 10.255.3.0/30 | 10 |
| xb-hq / xb-dc1 | 14 | B | 10.255.4.0/30 | 100 |
| xa-part / xa-dc1 | 15 | A | 10.255.5.0/30 | routes statiques |
| xa-dc2 / xa-dc1 | 16 | A | 10.255.6.0/30 | 10 |

Le réseau de gestion 10.98.0.0/24 est **hors bande** : il sert à l'administration et aux journaux, pas aux flux testés. Le DHCP d'EVE (`rao-dhcp`) l'alimente sans annoncer ni passerelle ni DNS. Les nœuds EVE y reçoivent une adresse fixe, réservée d'après leur MAC (`50:00:00:0N:00:00`, N = numéro du nœud).

---

## 5. Comment ça marche

Tout ce qui suit est écrit par `automation/lab/deploy.py`. Pour vérifier un point, il suffit de lire le fichier généré sur le nœud (chemin indiqué entre parenthèses).

### 5.1 Adressage

systemd-networkd (`/etc/systemd/network/20-ethX.network`). Chaque site a deux routes par défaut : par A (métrique 10) et par B (métrique 100). Les opérateurs reçoivent des routes statiques pour se joindre mutuellement par 100.64.0.0/30.

### 5.2 IPsec « route-based » (interfaces XFRM)

- Chaque tunnel est une **interface réseau** (`xa-agfr`, `xb-hq`…) de type XFRM, marquée par un `if_id` (`/etc/systemd/network/30-x*.netdev`). Les sélecteurs de trafic sont `0.0.0.0/0` des deux côtés : **c'est la table de routage qui décide** quel paquet part dans quel tunnel, et non une liste de sous-réseaux figée dans IPsec. Ce fonctionnement est celui des tunnels SD-WAN des FortiGate.
- IKEv2 avec clé partagée (`/etc/swanctl/conf.d/rao.conf`). Les **clés sont régénérées à chaque déploiement** et ne sont stockées nulle part dans le projet. C'est pourquoi `deploy.py` refuse de configurer un seul routeur : les deux bouts d'un tunnel doivent recevoir la même clé.
- Les sites ouvrent les tunnels (`start_action = start`, `dpd_action = restart`) ; le hub ne fait que répondre (`start_action = none`). La détection de pair mort (DPD) est réglée à 5 s et les tentatives de reconnexion sont illimitées.
- `Independent=yes` : l'interface du tunnel ne dépend d'aucune carte physique, elle survit donc quand `eth1` tombe.
- MTU de 1400 sur les tunnels ; nftables ajuste la taille de segment TCP (MSS) pour éviter la fragmentation.

### 5.3 OSPF et bascule WAN

- FRR (`/etc/frr/frr.conf`), zone 0. Chaque tunnel est un lien point à point. Les LAN sont annoncés en interfaces passives. Le tunnel A coûte **10**, le tunnel B **100** : le trafic passe par A tant que A répond.
- Timers rapides : hello toutes les 1 s, voisin déclaré mort après 4 s. Si l'opérateur A d'une agence tombe, OSPF perd le voisin du tunnel A en 4 s au plus et bascule sur B. Mesure : 3,2 à 3,8 s d'interruption selon les passages (ping toutes les 0,2 s). Au rétablissement, le trafic revient sur A tout seul.
- Le partenaire (`gw-part`) n'utilise pas OSPF : il a deux routes statiques. fw-dc1 joint 10.60.1.0/24 par `xa-part`, et le partenaire envoie 10.11.0.0/16 dans le tunnel. On ne fait pas entrer un tiers dans son routage dynamique.

### 5.4 Pourquoi `mobike = no`

MOBIKE (extension d'IKEv2) **déplace** un tunnel vers une autre adresse quand celle d'origine disparaît. Sans `mobike = no`, couper l'opérateur A de l'agence faisait migrer le tunnel *A* sur l'opérateur B. OSPF ne voyait donc aucune panne, la route restait sur `xa-dc1`, et la bascule devenait invisible et non mesurable. Avec `mobike = no`, chaque tunnel reste attaché à son opérateur, et c'est le routage (OSPF) qui choisit le tunnel : c'est le modèle SD-WAN visé.

### 5.5 Anti-usurpation BCP 38 chez les opérateurs

Un vrai opérateur refuse les paquets dont l'adresse source ne lui appartient pas (bonne pratique BCP 38). Sur `isp-a` et `isp-b` (`/etc/nftables.conf`), l'accès client rejette toute source hors du bloc de l'opérateur. **Sans cette règle**, quand A était coupé, l'agence envoyait les paquets du tunnel A (source 198.51.100.40) par l'opérateur B. Celui-ci les acheminait jusqu'au DC, si bien que le tunnel A « survivait » à la coupure de A, ce qui est irréaliste.

### 5.6 Filtrage nftables et matrice de flux

- **Refus par défaut** (`policy drop`) en entrée et en transit sur tous les routeurs de site et sur fw-dc1. Seuls entrent : SSH et DHCP depuis la gestion (eth0), IKE (UDP 500/4500) et ESP depuis les opérateurs, OSPF depuis les tunnels, et ICMP.
- **fw-dc1** applique la politique de `docs/FLUX.md` : une règle par flux, préfixée de son identifiant (`RAO-OK F05`…). Le reste est journalisé sous `RAO-REFUS` (transit) ou `RAO-REFUS-ENTREE` (à destination du pare-feu lui-même) puis rejeté.
- **Publication** : DNAT de 198.51.100.10 et 203.0.113.10, ports 443 et 22, vers srv-web (F01, F02).
- **gw-agfr** : le LAN agence va aux tunnels ; les invités (eth4) ne sortent que vers Internet en 80/443, avec NAT, et jamais vers 10.0.0.0/8 (F13, N05). Les autres sites laissent passer leur LAN vers le tunnel ; **le contrôle se fait au DC**, comme dans la cible.
- Le ping (echo-request) des sites internes vers le DC est autorisé : c'est la sonde de la bascule.

### 5.7 Journalisation

Le noyau journalise chaque décision `RAO-*`. rsyslog (`/etc/rsyslog.d/90-rao.conf`) renvoie `kern.*` en TCP vers `logs` (10.98.0.105:6514) par le réseau de gestion, avec une file d'attente et des tentatives illimitées. Le conteneur `logs` écrit tout dans `/var/log/rao/central.log`, horodaté à la réception. À noter : le port 6514 est celui de syslog sur TLS, mais **ici le flux n'est pas chiffré** (limite de maquette).

### 5.8 Services de test et confort de démonstration

- Les conteneurs font tourner `rao@<port>-<mode>` (`/usr/local/bin/rao_service.py`) : HTTPS 443 sur srv-web, 8443 sur srv-app, TCP 5432 sur srv-db, HTTP/HTTPS sur cli-ext, récepteur syslog sur logs. Les certificats sont auto-signés.
- Les consoles série des nœuds (clic dans EVE) s'ouvrent **directement en root** et affichent un aide-mémoire : réservé au lab.
- `/etc/strongswan.d/rao-swanctl.conf` limite les plugins chargés par `swanctl`. Sans lui, chaque commande affiche une trentaine d'avertissements « plugin failed to load » (ajout du 28/10/2026).

### 5.9 La recette (`automation/lab/recette.py`)

1. Pour chaque flux de `docs/FLUX.md` testable dans la maquette (17), la recette ouvre une connexion TCP (`nc -z -w 3`) depuis la vraie machine source. Elle compare le résultat à l'attendu : `ok` ou `refus`. Si le test n'a pas pu s'exécuter (SSH en échec), elle note `erreur`, qui ne compte jamais comme un refus réussi.
2. Elle récupère sur `logs` les lignes `RAO-OK` et `RAO-REFUS` produites pendant la recette.
3. Bascule (sauf avec `--sans-bascule`) : un ping toutes les 0,2 s part de cli-ag vers srv-app. Pendant ce temps, la recette coupe `eth1` de gw-agfr 10 s, relève la route pendant la coupure (attendu : `xb-dc1`) puis après (attendu : `xa-dc1`), et compte les pertes. Le lien est **toujours** rétabli, même si on interrompt le script.
4. Elle écrit `evidence/<horodatage UTC>/` : `recette.csv`, `recette.md`, `journaux_pare-feu.log`, `bascule_wan.txt` et les empreintes `SHA256SUMS`. Contrôle d'intégrité, dans Git Bash : `cd evidence/<horodatage> && tr -d '\r' < SHA256SUMS | sha256sum -c`. Cette forme marche pour tous les dossiers : avant le 28/10, recette.py écrivait les fichiers avec des fins de ligne Windows (CRLF), et `sha256sum -c SHA256SUMS` échoue alors avec « No such file ». Les preuves déjà produites ne sont pas réécrites ; les nouvelles le sont en LF, et `sha256sum -c SHA256SUMS` suffit pour elles.
5. Elle termine par `RÉSULTAT : CONFORME` (code de sortie 0) ou `NON CONFORME` avec la liste des échecs (code 1). Durée : environ 75 s, ou 45 s sans la bascule.

---

## 6. Utilisation courante

```bash
# depuis la racine du projet (Git Bash ou PowerShell)
ssh -F automation/ssh_config fw-dc1 "swanctl --list-sas | grep -c ESTABLISHED"        # attendu : 6
ssh -F automation/ssh_config fw-dc1 "vtysh -c 'show ip ospf neighbor'"                  # attendu : 5 voisins Full
python automation/lab/recette.py                 # recette complète avec bascule (coupe l'accès A de gw-agfr 10 s)
python automation/lab/recette.py --sans-bascule  # flux seulement
python automation/lab/deploy.py                  # reconfigure tout (sans argument : tous les nœuds ensemble)
```

Après `deploy.py`, attendre environ 15 s (tunnels puis OSPF) avant de lancer la recette.

---

## 7. Reconstruire la maquette de zéro

Légende : **[root hôte]** = l'utilisateur, en root sur l'hôte Proxmox (`ssh administrateur@163.172.105.87` puis `su -`). Claude n'a pas ce droit. **[root EVE]** = root sur la VM EVE, par clé (`ssh -F automation/ssh_config eve`). **[navigateur]** = l'utilisateur dans l'interface web. **[PC]** = depuis la racine du projet, sans droit particulier.

Prérequis : serveur dédié sous Proxmox VE 9 (VT-x, 8 threads, 32 Go de RAM, environ 100 Go libres), compte `administrateur` membre de `sudo`. Côté PC : client OpenSSH, Python 3 (bibliothèque standard seulement) et la clé `~/.ssh/id_ed25519_par861454` autorisée pour `administrateur`. Copier les scripts : `scp automation/host/*.sh administrateur@163.172.105.87:/tmp/`.

| # | Qui | Action | Contrôle de fin |
|---|---|---|---|
| 1 | [root hôte] | `bash /tmp/00_durcissement_ssh.sh` : SSH par clé uniquement. **Garder la session ouverte** et tester une 2e connexion avant de fermer. | `sshd -T` affiche `passwordauthentication no` |
| 2 | [root hôte] | `bash /tmp/01_prep_hote.sh` : virtualisation imbriquée, vmbr1 (NAT), vmbr2 et vmbr10-16. Relançable. | `nested` = Y, ponts listés |
| 3 | [root hôte] | `bash /tmp/03_p0_securite.sh` **depuis SSH, pas depuis la console web** (le redémarrage de pveproxy la coupe) : interface Proxmox limitée à 127.0.0.1 et pare-feu nftables avec retour arrière automatique à 5 min. Ouvrir une 2e session SSH, puis `systemctl stop fwrb.timer && systemctl enable nftables`. | Depuis l'extérieur, seul le port 22 répond |
| 4 | administrateur (sans root) | Télécharger l'ISO (10 775 506 944 octets, plusieurs heures) : `nohup wget -c -o ~/eve-iso.log https://customers.eve-ng.net/eve-pro-prod-bm-7.2.0-18-full.iso &`. Un seul wget à la fois (`pgrep -a wget`). | Taille exacte atteinte |
| 5 | [root hôte] | `bash /tmp/02_create_eve_vm.sh` : range l'ISO et crée puis démarre la VM 200 (20 Go, 6 vCPU, 9 cartes : net0 = vmbr1, net1 = vmbr2, net2-8 = vmbr10-16). | `qm status 200` : running |
| 6 | utilisateur (console Proxmox : tunnel `ssh -N -L 8006:127.0.0.1:8006 administrateur@163.172.105.87`, puis https://localhost:8006) | Installer EVE : IP 10.99.0.10/24, passerelle 10.99.0.1, DNS 1.1.1.1. **À l'écran « Reboot Now », avant de valider**, [root hôte] : `qm stop 200 && qm set 200 --ide2 none --boot order=scsi0 && qm start 200` (sinon l'installation recommence en boucle). Ensuite : `passwd` root sur EVE, clé publique du PC dans `/root/.ssh/authorized_keys`, mot de passe du compte web `admin` changé. [root hôte] : VM arrêtée, `qm snapshot 200 eve-base`, puis suppression de l'ISO. | `ssh -F automation/ssh_config eve uptime` |
| 7 | [root hôte] | Copier la clé publique du PC dans `/tmp/cle_lab.pub`, puis `bash /tmp/04_lxc_lab.sh` : crée les conteneurs 301-308 (modèle Debian 13 **amd64**). | `pct list` : 8 conteneurs running |
| 8 | [root EVE] | Fabriquer l'image routeur `linux-debian13-routeur` : **§ 7.1** (non scripté dans le dépôt). | `virtioa.qcow2` présent, nœud de test joignable en SSH |
| 9 | [root EVE] | Installer le DHCP de gestion `rao-dhcp` : **§ 7.2** (non scripté dans le dépôt). | `systemctl is-active rao-dhcp` ; `ping -c1 10.98.0.101` depuis EVE |
| 10 | [navigateur] | Tunnel `ssh -N -L 8443:10.99.0.10:443 administrateur@163.172.105.87`, https://localhost:8443, se connecter. Touche F12, onglet Console : coller `automation/eve/creer_lab.js` (**une seule fois**, sur une instance sans lab RAO, sinon on dépasse 7 nœuds). Ouvrir le lab `RAO`, tout sélectionner, clic droit, Start. | 7 icônes en couleur |
| 11 | [PC] | Vérifier les 15 accès : `for n in isp-a isp-b fw-dc1 fw-dc2 gw-hq gw-agfr gw-part srv-web srv-app srv-db bastion logs cli-ag cli-ext cli-inv; do ssh -F automation/ssh_config $n hostname; done` | 15 noms affichés |
| 12 | [PC] | `python automation/lab/deploy.py` | 12 lignes `[OK]` |
| 13 | [PC] | Attendre 15 s, puis `python automation/lab/recette.py` | `RÉSULTAT : CONFORME` |
| 14 | [root hôte] (facultatif) | Accès web des camarades : `bash /tmp/05_acces_camarades.sh "<clé publique>"`. Côté camarade : `automation/connexion_rao.ps1`. | Le camarade ouvre EVE dans son navigateur |

**Après un redémarrage de l'hôte**, [root hôte] : `qm start 200` puis `for i in $(seq 301 308); do pct start $i; done` (les conteneurs ne démarrent pas seuls). Ensuite, [navigateur] : démarrer les 7 nœuds du lab. Les nœuds gardent leur configuration sur disque ; si l'un d'eux a été réinitialisé (*wipe*) ou recréé, relancer `deploy.py`.

### 7.1 Fabriquer l'image routeur `linux-debian13-routeur` (étape 8)

Cette image sert aux 7 nœuds EVE : une Debian 13 officielle à laquelle on ajoute les paquets du routeur, et rien d'autre. Toute la configuration réseau est faite ensuite par `deploy.py`. L'image d'origine a été fabriquée le 16/10 dans `/root/build` sur EVE. Les commandes ci-dessous sont **reconstituées** à partir de ce dossier (toujours présent), du journal et de l'état relevé sur les nœuds le 28/10 (paquets, services, fichiers). Elles ne sont pas un enregistrement de la session d'origine : vérifier chaque contrôle au passage.

Fichiers du dossier `/root/build`, à recréer s'ils manquent :

| Fichier | Contenu | Rôle |
|---|---|---|
| `10-eth0.network` | `[Match]` `Name=eth0` / `[Network]` `DHCP=ipv4` (sur 4 lignes) | eth0 = gestion, adresse fournie par `rao-dhcp` |
| `90-routeur.conf` | `net.ipv4.ip_forward=1` | le nœud route |
| `90-rao.cfg` | `GRUB_CMDLINE_LINUX="$GRUB_CMDLINE_LINUX net.ifnames=0 biosdevname=0 console=tty0 console=ttyS0,115200"` | interfaces nommées `eth0`, `eth1`… dans l'ordre d'EVE ; console série (clic sur le nœud) |
| `cle.pub` | clé publique SSH du PC (une ligne `ssh-ed25519 …`) | accès root par clé, sans mot de passe |

```bash
# [root EVE] 1. Image officielle, vérifiée par son empreinte SHA512 publiée par Debian
mkdir -p /root/build && cd /root/build
wget https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2
wget https://cloud.debian.org/images/cloud/trixie/latest/SHA512SUMS
sha512sum -c --ignore-missing SHA512SUMS        # attendu : debian-13-genericcloud-amd64.qcow2: OK
cp debian-13-genericcloud-amd64.qcow2 routeur.qcow2

# 2. Paquets. Dans EVE, virt-customize n'a pas de réseau (son appliance ne sort pas) :
#    on monte le disque avec qemu-nbd et on installe depuis un chroot, qui utilise le réseau d'EVE.
modprobe nbd max_part=8
qemu-nbd --connect=/dev/nbd0 routeur.qcow2
lsblk -f /dev/nbd0                               # repérer la partition racine ext4 (nbd0p1 sur cette image)
mount /dev/nbd0p1 /mnt
for d in dev proc sys; do mount --bind /$d /mnt/$d; done
rm -f /mnt/etc/resolv.conf && echo "nameserver 1.1.1.1" > /mnt/etc/resolv.conf   # lien vers resolved, inutilisable en chroot
chroot /mnt apt-get update
chroot /mnt env DEBIAN_FRONTEND=noninteractive apt-get install -y \
  frr strongswan-swanctl charon-systemd nftables rsyslog netcat-openbsd tcpdump traceroute mtr-tiny iperf3 curl
chroot /mnt apt-get purge -y cloud-init         # sinon il attend un serveur de métadonnées à chaque démarrage
for d in sys proc dev; do umount /mnt/$d; done; umount /mnt
qemu-nbd --disconnect /dev/nbd0

# 3. Réglages hors ligne, sans réseau
virt-customize -a routeur.qcow2 --no-network \
  --copy-in 10-eth0.network:/etc/systemd/network \
  --copy-in 90-routeur.conf:/etc/sysctl.d \
  --mkdir /etc/default/grub.d --copy-in 90-rao.cfg:/etc/default/grub.d --run-command update-grub \
  --ssh-inject root:file:cle.pub \
  --run-command 'systemctl enable systemd-networkd strongswan frr rsyslog nftables' \
  --run-command 'rm -f /etc/ssh/ssh_host_*' --truncate /etc/machine-id
# Les deux dernières options rendent chaque nœud unique : machine-id vide = « premier démarrage »,
# donc sshd-keygen.service (ssh-keygen -A) crée de nouvelles clés d'hôte et systemd un nouveau machine-id.

# 4. Installation dans EVE (dossier et nom de disque imposés par EVE : linux-<nom>/virtioa.qcow2)
mkdir -p /opt/unetlab/addons/qemu/linux-debian13-routeur
cp routeur.qcow2 /opt/unetlab/addons/qemu/linux-debian13-routeur/virtioa.qcow2
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions
sha256sum /opt/unetlab/addons/qemu/linux-debian13-routeur/virtioa.qcow2   # à noter dans inventory/images.yml
```

Contrôle : l'image apparaît dans EVE (modèle *Linux*, image `linux-debian13-routeur`). Un nœud créé avec elle démarre, obtient son adresse de gestion (§ 7.2), accepte `ssh -F automation/ssh_config <nœud>`, et `swanctl --version`, `vtysh -c 'show version'` et `nft --version` y répondent. L'image du 16/10 a pour SHA256 `9b73dd01d9fba6225b4f52d7ce1b8dda81605185cdfb40c981745544bc79ee29` (702 218 240 octets) ; une image refaite aura une autre empreinte.

### 7.2 DHCP de gestion `rao-dhcp` sur EVE (étape 9)

Le réseau de gestion (Cloud1 = pnet1 = vmbr2, 10.98.0.0/24) a besoin d'un serveur DHCP pour donner aux nœuds EVE une **adresse fixe, réservée d'après leur MAC**. EVE attribue les MAC selon la règle `50:00:00:<n° du nœud>:00:<n° d'interface>`, donc eth0 du nœud N vaut `50:00:00:0N:00:00`. Le serveur n'annonce **ni passerelle ni DNS** : le réseau de gestion ne doit mener nulle part ailleurs. Les conteneurs, eux, ont une adresse statique (`04_lxc_lab.sh`).

```bash
# [root EVE] dnsmasq-base est déjà présent sur EVE 7.2 (sinon : apt-get install -y dnsmasq-base)
mkdir -p /etc/rao
cat > /etc/rao/dhcp-hosts <<'EOF'
50:00:00:01:00:00,10.98.0.11,isp-a
50:00:00:02:00:00,10.98.0.12,isp-b
50:00:00:03:00:00,10.98.0.13,fw-dc1
50:00:00:04:00:00,10.98.0.14,fw-dc2
50:00:00:05:00:00,10.98.0.15,gw-hq
50:00:00:06:00:00,10.98.0.16,gw-agfr
50:00:00:07:00:00,10.98.0.17,gw-part
EOF
cat > /etc/systemd/system/rao-dhcp.service <<'EOF'
[Unit]
Description=DHCP de gestion du lab RAO sur pnet1 (Cloud1, vmbr2) : ni passerelle ni DNS annonces
After=network-online.target
[Service]
ExecStartPre=-/sbin/ip addr add 10.98.0.2/24 dev pnet1
ExecStart=/usr/sbin/dnsmasq --keep-in-foreground --port=0 --interface=pnet1 --bind-interfaces --dhcp-range=10.98.0.50,10.98.0.99,12h --dhcp-option=3 --dhcp-option=6 --dhcp-hostsfile=/etc/rao/dhcp-hosts --dhcp-leasefile=/var/lib/misc/rao-dhcp.leases --log-dhcp
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable --now rao-dhcp
```

Ce que font les options : `--port=0` désactive la partie DNS de dnsmasq. `--dhcp-option=3` et `--dhcp-option=6`, sans valeur, n'annoncent ni passerelle ni DNS. La plage 10.98.0.50-99 sert aux machines inconnues ; les réservations tirées de `dhcp-hosts` ont la priorité. `ExecStartPre` donne à EVE son adresse 10.98.0.2 sur pnet1, qui sert de rebond SSH vers le lab (`ProxyJump eve`). Après une modification de `dhcp-hosts` : `systemctl reload rao-dhcp`.

Contrôle (relevé du 28/10/2026) : `systemctl is-active rao-dhcp` renvoie `active`, `ip -br addr show pnet1` affiche 10.98.0.2/24, et une fois les nœuds démarrés, `cat /var/lib/misc/rao-dhcp.leases` liste une ligne par nœud (`… 50:00:00:07:00:00 10.98.0.17 gw-part …`).

---

## 8. Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `ssh -F automation/ssh_config <nœud>` : *timed out* | Nœud arrêté dans EVE, conteneur arrêté, ou DHCP de gestion absent | Démarrer le nœud (interface EVE) ou le conteneur ([root hôte] `pct start 30X`) ; [root EVE] `systemctl status rao-dhcp` |
| *REMOTE HOST IDENTIFICATION HAS CHANGED* | Nœud recréé : ses clés d'hôte sont régénérées au 1er démarrage | `ssh-keygen -R 10.98.0.1N` (adresse du nœud), puis se reconnecter |
| `ospfd is not running` ; FRR redémarre en boucle (*Received signal 7*, SIGBUS) ; F05 et F09 échouent, la bascule ne passe plus par les tunnels | Disque du routeur plein (`df -h /` à 100 %). Avant le 10/11/2026, strongSwan journalisait chaque paquet DPD : 1,7 Go en 13 jours sur fw-dc1 | [root nœud] vider `/var/log/syslog*` et `/var/log/user.log*`, puis relancer `deploy.py` (strongSwan au niveau 0 et journal plafonné à 50 Mo depuis). Dans la fenêtre de démo : bouton « Réparer la maquette » |
| `deploy.py` : `[ÉCHEC]` sur un routeur | SSH impossible, ou configuration refusée (`ERREUR : configuration swanctl refusée`) | Corriger, puis relancer `deploy.py` **sans argument** : les clés doivent être identiques aux deux bouts |
| Tunnels absents (`ESTABLISHED` < 6) | Clés désynchronisées (déploiement interrompu) ou fichier swanctl invalide | `python automation/lab/deploy.py`, attendre 15 s. Sur le nœud : `journalctl -u strongswan -n 50` |
| Tunnels tombés quelques minutes après une modification de `deploy.py` (16/10) | Gabarit swanctl cassé (accolade) | Corrigé : `deploy.py` vérifie que swanctl accepte la configuration et échoue explicitement sinon |
| Bascule « réussie » mais la route reste sur `xa-dc1` pendant la coupure (16/10) | MOBIKE a déplacé le tunnel A sur l'opérateur B | `mobike = no` (§ 5.4), déjà dans `deploy.py` |
| Le tunnel A survit à la coupure de l'opérateur A (16/10) | Les opérateurs simulés laissaient passer les adresses usurpées | Anti-usurpation BCP 38 sur isp-a et isp-b (§ 5.5) |
| Bascule non mesurable, 100 % de perte (16/10) | La politique bloquait la sonde ICMP | Ping autorisé des sites internes vers le DC (règle `icmp type echo-request` sur fw-dc1) |
| `obtenu=erreur` dans la recette | Le test n'a pas pu s'exécuter (SSH vers la source) | Vérifier l'accès au nœud source, puis relancer |
| Accès A de l'agence resté coupé (démo interrompue) | `ip link set eth1 down` sans le `up` correspondant | `ssh -F automation/ssh_config gw-agfr "ip link set eth1 up"` |
| ~30 lignes *plugin '…': failed to load* à chaque `swanctl` | Liste de plugins par défaut de swanctl, absents sous Debian | Corrigé le 28/10 (`rao-swanctl.conf`, § 5.8) ; sur une ancienne configuration : `deploy.py` |
| Tunnel ouvert sous PowerShell : *Permission denied (publickey)* | `%USERPROFILE%` n'est remplacé que dans cmd.exe | PowerShell : `$env:USERPROFILE\.ssh\…`, ou `~/.ssh/…` |
| L'installation d'EVE recommence en boucle (16/10) | La VM redémarre sur l'ISO | Étape 6 : retirer l'ISO et démarrer sur le disque **avant** « Reboot Now » |
| Conteneurs qui ne démarrent pas, *exec format error* (16/10) | `04_lxc_lab.sh` avait pris le modèle arm64 (tri alphabétique) | Corrigé : filtre `_amd64` ; supprimer puis recréer les conteneurs concernés |
| `03_p0_securite.sh` interrompu (16/10) | Lancé depuis la console web, coupée par le redémarrage de pveproxy | Le relancer depuis une session SSH (il est relançable) |
| `virt-customize` sans réseau dans EVE | Pas de réseau pour l'appliance libguestfs | Paquets installés par `qemu-nbd` et `chroot`, réglages en `--no-network` |
| Lab EVE illisible sur disque, arrêt par `GET …/stop` en erreur 400 | Format des labs chiffré dans EVE PRO ; syntaxe d'arrêt inconnue | Créer par l'API depuis le navigateur (`creer_lab.js`), arrêter depuis l'interface web |
| `pveam update failed` pendant `04_lxc_lab.sh` | Avertissement de mise à jour de la liste des modèles | Sans conséquence si le modèle est trouvé (voir `/var/log/pveam.log`) |

Commandes utiles sur un nœud (aide-mémoire affiché à la connexion) : `swanctl --list-sas`, `vtysh -c 'show ip ospf neighbor'`, `ip route`, `nft list ruleset`, `journalctl -k -f -n 0 | grep RAO`.

---

## 9. Limites

- **EVE Freemium : 7 nœuds.** Les serveurs et clients sont donc des conteneurs LXC. Pas d'agence internationale (`gw-agint`). DC2 se réduit à son pare-feu et à un LAN vide, joint par un seul tunnel (A).
- **Linux à la place des FortiGate** : nftables, strongSwan et FRR démontrent les mécanismes (zones, IPsec route-based, routage dynamique, journalisation), pas les fonctions propres aux produits : IPS, antivirus, filtrage applicatif, SD-WAN piloté par SLA applicatif, FortiManager, HA en paire.
- **Pas de nomadisme** : ni ZTNA, ni IdP, ni MFA ; F07, F08, N07 et N09 ne sont pas exécutés. F12 (DNS/NTP) n'est pas testé.
- **Bastion et SIEM minimaux** : SSH simple, sans enregistrement de session ; récepteur syslog sans corrélation ni alerte. Les journaux passent en clair sur le réseau de gestion.
- **Authentification IPsec par clé partagée** (régénérée à chaque déploiement), et non par certificats d'une PKI.
- **Tests de connectivité, pas d'application** : la recette vérifie l'ouverture TCP (et l'acceptation par le pare-feu), pas le contenu échangé. Aucun test de débit ni de charge.
- **La bascule mesurée (3 à 4 s)** dépend des timers OSPF du lab (1 s / 4 s) sur un réseau sans perte. Ce n'est pas un engagement de niveau de service pour la production.
- **Un seul serveur physique** : aucune redondance matérielle réelle ; le réseau de gestion échappe à la politique de flux.
- **Confort de démonstration** : console série ouverte en root ; le compte web `admin` d'EVE doit avoir un mot de passe changé avant tout partage.

