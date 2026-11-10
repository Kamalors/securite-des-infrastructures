# Plan v2 — mise en place, après revue par 4 agents critiques

Synthèse du 16/10/2026 (Claude Code, Opus). Quatre revues indépendantes : **automatisation**, **performance**, **sécurité/exploitation**, **pilotage/livrables**. Ce plan complète `PLAN_CLAUDE_CODE_RAO_EVE_NG.md` (le plan initial) sans le remplacer. Sources citées dans les rapports d'agents (consignées au besoin dans les fichiers concernés).

## 0. Les 3 constats qui changent le plan

1. **EVE-NG PRO 7.2 édition Freemium = 7 nœuds par instance** (confirmé par les 4 agents, sources officielles eve-ng.net : page de comparaison des éditions + notes de version). La maquette en prévoit 15. **À trancher avant de créer la VM** → décision D1.
2. **Priorité mal placée.** Le PDF note 3 volets (modèles d'équipement justifiés, HLD DC+agences, coûts par poste avec abonnement). Après 2 jours, ~0 % sur ces 3 volets ; presque tout le temps est allé à l'infra. La maquette n'est **pas** demandée par le client → décision D2 (la sortir du chemin critique).
3. **L'hôte peut être recompromis sans alerte.** `ip_forward=1` sans aucun filtre, plan de gestion (compte Scaleway, mot de passe root) non vérifié, aucune détection. → bloc sécurité P0.

## 1. Décisions à prendre (bloquantes)

| N° | Décision | Options | Reco |
|---|---|---|---|
| D1 | Contourner la limite 7 nœuds | A) licence Base ~150 € · B) Freemium, ≤7 nœuds actifs par scénario · **C) hôtes/clients en conteneurs LXC Proxmox reliés à EVE** | **✅ C retenu (16/10)** |
| D2 | Place de la maquette | chemin critique / **hors chemin critique, ≤~30 %, critère d'abandon** | **✅ offre d'abord (16/10)** |
| D3 | Pare-feu de la maquette | 5 appliances OPNsense (3 Go ch.) / ≤3 appliances + reste Debian+nftables / tout Debian+nftables | ≤3 appliances (fw-dc1, fw-dc2, gw-agfr) + reste Debian |
| D4 | VM Services / SIEM | VM Wazuh 8 Go / nœud `logs` rsyslog seul / wazuh-manager 2 Go sans indexeur | Nœud `logs` au départ ; wazuh-manager seul si on veut montrer de la détection |
| D5 | Dépôt | Git privé / un propriétaire par fichier | Git privé dès qu'on est à plusieurs |

## 2. Architecture révisée (maquette)

### 2.1 Dimensionnement VM EVE (remplace `02_create_eve_vm.sh`)
- `--memory 20480 --balloon 0 --sockets 1 --cores 6 --cpu host` (6 vCPU sur 8 threads, pas 8 : éviter la famine de l'hôte ; `host` obligatoire pour exposer vmx).
- `--scsi0 local:200,format=qcow2,iothread=1,discard=on,ssd=1`.
- qcow2 gardé (snapshots). Défauts Proxmox conservés : cache=none, io_uring.
- Après install : `qm set 200 --ide2 none --boot order=scsi0` ; supprimer l'ISO (10,8 Go) ; `qm snapshot 200 eve-base` VM arrêtée.

### 2.2 Budget ressources (15 nœuds actifs ; ~8 Go si Freemium 7 nœuds)
| Composant | vCPU | RAM | Disque |
|---|---|---|---|
| Hôte Proxmox | ~2 | ~2 Go + marge | ~10 Go |
| VM EVE (OS + QEMU) | — | ~2,5 Go | ~15 Go |
| ≤3 appliances (OPNsense 2 Go / pfSense 1 Go) | 1 ch. | 2 Go ch. | 8–20 Go |
| 5 routeurs/passerelles Debian | 1 | 512 Mo | 2 Go |
| 7 hôtes Debian | 1 | 512 Mo | 2–4 Go |
| **Marge hôte** | — | **~8 Go** | **>20 % libre** |

### 2.3 Réseau de gestion séparé (sinon tests faussés)
- `vmbr2` sur l'hôte : `inet manual`, `bridge-ports none`, **ni IP ni NAT**. Carte `net1` de la VM EVE dessus, **sans pare-feu Proxmox sur la carte** (le filtre MAC par défaut bloque les nœuds imbriqués).
- Dans EVE : Cloud1 = pnet1 → eth0 de gestion de chaque nœud, MAC fixée. dnsmasq sur le nœud de contrôle **n'annonce ni passerelle ni DNS** (sinon un test qui passe par la gestion donne un faux « réussi »).
- Les journaux du lab (syslog TCP 6514 dans la maquette, TLS en production) passent par vmbr2 vers le nœud `logs`/Services, qui ne route rien.

### 2.4 Topologie — corrections (sinon preuves invalides)
- `gw-agfr` relié aussi à `opB` (sinon le secours 4G/5G du profil agence n'est pas démontrable).
- `isp-a` ↔ `isp-b` reliés (sinon `cli-ext` ne peut pas basculer d'opérateur).
- Ajouter un **segment invités** (sinon F13 et N05 non testables).
- Ajouter dans `inventory/topology.yml` les **IP d'interface et IP/MAC de gestion** : il doit devenir la source unique (aujourd'hui les IP ne vivent que dans le texte de HLD/FLUX → divergence garantie).

## 3. Chaîne d'automatisation révisée

- **Pas de Terraform** (2 VM, install ISO interactive, état avec secrets). Unanime.
- **Source unique** : `inventory/topology.yml` → construction du lab + inventaire Ansible + tests, tout lu au même endroit.
- **Nœud de contrôle** : petit conteneur LXC Debian sur l'hôte (CT 210, 512 Mo, sur vmbr1+vmbr2), avec Ansible + dnsmasq + git. Claude s'y connecte par clé (ProxyJump via l'hôte), **sans être root sur l'hôte**. Le code y arrive par `git push`.
- **Lab par l'API EVE** (login HTTPS `html5`, création lab/réseaux/nœuds, start/stop) plutôt qu'un `.unl` écrit à la main. L'export ZIP de l'interface est versionné dans `lab/` (réimportable ailleurs).
- **Une image Debian « dorée »** (virt-customize : frr, strongswan, nftables, nginx, postgresql, rsyslog ; clé ansible ; `net.ifnames=0`) → lab sans Internet, reconstruction identique.
- **Tests de flux rejouables** : `tests/flows.yml` (F01–F13, N01–N09) → script qui, pour chaque cas, vérifie d'abord que le trafic ne sort pas par la gestion (`ip route get`), teste le port, puis cherche la trace dans `logs`. Sortie horodatée `evidence/<UTC>/flows.csv` + SHA256. Deuxième passage Ansible avec `changed=0` = preuve d'idempotence.
- **Git** : `git init`, `.gitattributes` (`* text=auto eol=lf` — le poste a `autocrlf=true`, sinon CRLF chez un collègue casse les scripts Linux), `.gitignore` (`*.iso *.qcow2 *.crdownload *.hdr id_* proxmox.ps1 secrets/ evidence/hote/`).

## 4. Sécurité de l'hôte (post-incident)

**P0 — avant toute VM (~1 h, utilisateur en root + console Scaleway)**
1. Compte Scaleway : mot de passe unique + MFA (garder les codes de secours), retirer clés SSH/API inconnues.
2. `passwd root` (le mot de passe d'install affiché par Dedibox est à considérer comme compromis) ; vérifier `/root/.ssh/authorized_keys` ; **supprimer `proxmox.ps1`** (mots de passe en clair).
3. Vérifier que 8006 est bien fermé **depuis la 4G** (pas seulement depuis le réseau du PC), puis lier pveproxy à localhost : `echo 'LISTEN_IP="127.0.0.1"' >> /etc/default/pveproxy && systemctl restart pveproxy spiceproxy`. Tunnel inchangé.
4. Pare-feu hôte **nftables** (fichier simple, réparable en rescue ; ne pas cumuler avec le pare-feu Proxmox) : policy drop en input (sauf 22, lo, ICMP, établi) et en forward (lab→Internet limité à 53/80/123/443, lab→gestion refusé). Poser une minuterie de rollback avant d'appliquer, pour ne pas se verrouiller.

**P1 — avant le lab (~2 h)**
5. Compte `claude` **sans sudo**, clé dédiée (ligne `authorized_keys` avec `restrict,permitopen=127.0.0.1:8006,...,expiry-time=...`). `PermitRootLogin no`, `AllowUsers administrateur claude`. Séparer l'humain (qui tape sudo/su) de Claude.
6. TOTP + codes de secours sur `root@pam` ; token API `claude@pve` PVEAuditor (lecture) à durée limitée ; secret hors projet, transmis par `curl -H @fichier` (à tester : le garde-fou l'accepte ou non).
7. Changer les mots de passe par défaut d'EVE (root/eve, admin/eve) ; SSH par clé sur EVE.
8. Contrôle d'intégrité horaire `04_integrite.sh` (avec busybox statique, que LD_PRELOAD ne détourne pas) : empreintes de `ld.so.preload`, `/usr/local`, ssh, PAM, sudoers, cron, systemd, comptes, ports, RAID. Écart → arrêt. (Répond directement au type d'implant trouvé le 16/10.)

**À NE PAS faire** : fail2ban/CrowdSec (inutile avec clés seules), liste d'IP `from=` (IP dynamique = risque de verrouillage), activer le pare-feu Proxmox sans règle SSH préalable, déplacer le port 22, exposer 8006/EVE, sudo NOPASSWD pour Claude, restaurer une image antérieure au 16/10.

## 5. Livrables RAO (le vrai chemin critique)

Ordre du diaporama = ordre du PDF : synthèse → besoin+hypothèses → HLD global → WAN → housing → compute → nord/sud → est/ouest → **HLD DC** → **HLD agences par profil (LAN+Wi-Fi)** → infogérance → nomadisme → partenaires 40/60 → exploitation → **tableau des modèles** → **coûts par poste (Housing, WAN, Serveurs, Équip. réseau, Équip. sécurité, Etc.)** → options → phasage → maquette+limites → risques. Annexes : EXIGENCES, FLUX, CHIFFRAGE. Schémas finaux : draw.io (mieux que mermaid pour le rendu).

Chiffrage : abonnement = licences + **location financière du matériel sur 36 mois** + services managés (répond à « pas de grosse somme d'un coup »). Quantités : 530 sites + 2 DC = 532 implantations ; règle HA explicite (ex. agences internationales ~67 utilisateurs → HA). Prix sourcés, datés, HT, nature (initial/mensuel) ; jamais inventés.

Arguments réglementaires à vérifier et intégrer : **HDS** (données de santé, housing+infogérant), **DORA** (assurance, prestataires TIC tiers), RGPD art. 9 + transferts internationaux.

## 6. Ce qu'on coupe (YAGNI)

Générateur `.unl` écrit à la main, `IMPORT.md`, paquet ZIP mode B (un seul serveur partagé → un export versionné suffit), LLD complet (les configs en tiennent lieu), IPAM 530 sites (1 diapo de principe), plan de migration détaillé (1 diapo), 2 offres complètes (1 offre + tableau d'options), TCO 60 mois en plus de 36 (1 durée), Terraform/proxmoxer/ansible-vault/evengsdk, les 7 états d'image, HA/réplication/IdP dans la maquette, 2e image Debian, `collecte_rescue.sh` (garder juste la note du nom du md racine pour un futur rescue).

## 7. Ordre d'exécution (U = utilisateur root · C = Claude non-root)

1. **C** : Git init + `.gitattributes`/`.gitignore` ; EXIGENCES v1 (fait) ; purge SUIVI ; correction script 02 (fait). *Critère : `git ls-files --eol` = lf.*
2. **U** : sécurité P0 (Scaleway MFA, passwd root, supprimer proxmox.ps1, LISTEN_IP, nftables avec rollback). *Critère : depuis la 4G, seul 22 répond.*
3. **U+C** : décision D1 écrite dans SUIVI. Puis **U** : script 02 corrigé, install EVE, snapshot `eve-base`. *Critère : `curl -sk https://10.99.0.10` répond depuis l'hôte.*
4. **U** : conteneur de contrôle (CT 210), vmbr2, token API ; sécurité P1 (compte claude, TOTP, intégrité). *Critère C : `ssh ctl ansible --version` OK ; lecture snapshot VM 200 = 200, autre VMID = 403.*
5. **U** : image dorée. **C** : mini-lab 8 nœuds pour tester la limite Freemium + noms eth*, DHCP, `ansible -m ping`.
6. **C** : lab complet par lots, `site.yml` ×2, snapshots `eve-image`/`eve-lab`.
7. **C** : `run_flows.yml`, preuves commitées.

**Plan B performance** (si ça ne tient pas, dans l'ordre) : moins de nœuds simultanés → agences en Debian → hôtes/`logs` en LXC Proxmox reliés à EVE → maquette directement sur Proxmox sans imbrication (le PDF n'impose pas EVE). Installer EVE à nu sur l'hôte est **exclu** (serveur partagé).

**Critère d'abandon maquette** : si le chemin principal (nord/sud, est/ouest, bastion) n'est pas prouvé à J+3, on ne présente que ce qui est prouvé et l'offre passe avant.
