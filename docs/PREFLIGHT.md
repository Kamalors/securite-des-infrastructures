# Préflight — audit des moyens (lecture seule)

Audit du 15/10/2026, ~11:10–11:40 CEST, Claude Code (Opus 5.5). Aucune modification n'a été faite.

## Poste local (DESKTOP-LQK0CT4)

| Élément | Valeur relevée | Méthode |
|---|---|---|
| OS | Windows 11 Pro 10.0.26200 | environnement Claude Code |
| CPU | AMD Ryzen 7 7435HS, 8 cœurs / 16 threads, virtualisation firmware activée | Win32_Processor |
| RAM | 15,7 Go | Win32_ComputerSystem |
| Disque | C: 75 Go libres sur 476 Go | Win32_LogicalDisk |
| Hyper-V | Processus vmms/vmwp actifs ; `Get-VM` refusé (droits admin requis) | Get-Process / Get-VM |

Conclusion : le poste est **sous le profil « Réduit »** du plan (32 Go RAM, 150–250 Go SSD). Il ne suffit pas pour héberger la maquette, même avec des Linux légers en scénarios séquentiels.

## Proxmox

| Élément | Valeur relevée | Méthode |
|---|---|---|
Audit du 15/10/2026 ~11:50 CEST : requêtes GET via la session navigateur de l'utilisateur (root@pam), aucune modification.

| Élément | Valeur relevée | Méthode |
|---|---|---|
| Accès | https://localhost:8006 → **serveur dédié distant** (IP publique sur vmbr0), joint via tunnel | /nodes/…/network |
| Nœud / version | PAR861454, Proxmox VE 9.2.20, noyau 7.0.14-19-pve | En-tête UI, /nodes/…/status |
| CPU | Intel Xeon E3-1245 v5, 1 socket, 4 cœurs / 8 threads, flag `vmx` présent | cpuinfo |
| RAM | 31,1 Go au total, 24,5 Go utilisés | /nodes/…/status |
| Stockage | `local` (dir) : 410 Go libres sur 466 Go ; images, ISO et sauvegardes au même endroit | /nodes/…/storage |
| Réseau | Seulement `vmbr0` (bridge public sur enp1s0f0) ; enp1s0f1 libre ; **aucun bridge interne/NAT** | /nodes/…/network |
| VM existantes | 101 `llm-security-lab` : 6 vCPU, 16 Go, 48 Go, **en cours d'exécution** (autre projet) | /nodes/…/qemu |
| EVE-NG | Non installé (confirmé par l'utilisateur) | — |
| Virtualisation imbriquée | `vmx` exposé ; le paramètre `kvm_intel nested` reste à lire (shell requis) | à vérifier |

### Capacité pour EVE-NG

- 8 threads et 31 Go : on est à la limite basse du profil « Réduit ».
- Avec la VM 101 allumée, il reste environ 6,5 Go : **pas assez** pour EVE.
- VM 101 arrêtée : on peut donner environ 22–24 Go à la VM EVE (en gardant ~6 Go pour l'hôte). Ça suffit pour le socle de 15 nœuds légers (Debian 512 Mo–1 Go, pare-feu 1 Go), démarrés progressivement.
- Pas de seconde IP publique connue. La VM EVE doit donc aller sur un bridge interne (NAT ou accès par tunnel SSH). Cela demande de **créer un bridge `vmbr1` sur l'hôte distant**, une modification réseau à faire valider avant (règle du plan §2).

## Autres éléments

- Le fichier `Non confirmé 609852.crdownload` (environ 586 Mo) est un téléchargement Chrome non terminé dans le dossier projet. Son contenu n'est pas identifié et je n'y ai pas touché.
- Le PDF de l'appel d'offres est absent du dossier.

## Décision de mode

**Mode B (paquet reproductible) dès maintenant.** Le mode A est possible sur PAR861454 sous trois conditions, à valider par l'utilisateur :
1. la VM 101 est arrêtée pendant les sessions de maquette (ou sa RAM est réduite) ;
2. la création d'un bridge interne `vmbr1` (NAT) sur l'hôte est autorisée ;
3. le module `kvm_intel` a bien `nested=Y`.

### Préparation de l'hôte : appliquée le 15/10/2026 (exécutée par l'utilisateur, sortie vérifiée)

- `kvm_intel nested` = **Y**.
- `vmbr1` monté en 10.99.0.1/24, sans port physique (état UNKNOWN, normal pour un bridge vide). NAT : `-A POSTROUTING -s 10.99.0.0/24 -o vmbr0 -j MASQUERADE`, `ip_forward = 1`.
- `vmbr0` est inchangé (163.172.105.87/24). Il porte aussi **10.10.10.1/24** (réseau existant, sans doute celui de la VM 101), d'où le décalage de DC1 en 10.11.0.0/16 dans `inventory/addressing.csv`.
- Une sauvegarde `/etc/network/interfaces.bak-<horodatage>` est sur l'hôte. Retour arrière : voir la fin de `automation/host/01_prep_hote.sh`.

Conditions du mode A : 2 sur 3 remplies. Il reste à arrêter la VM 101 au moment d'installer EVE, puis à obtenir l'ISO EVE-NG.

## Token API

`root@pam!claude-audit` a été créé le 15/10 ~11:45 CEST : privsep=1, ACL `/` → `PVEAuditor`, pas d'expiration. Son secret, affiché une seule fois, **n'a pas été conservé** : le stockage a été refusé par le garde-fou de Claude Code. Pour l'utiliser, il faut régénérer le secret dans l'UI (Datacenter → Permissions → API Tokens → Regenerate) et le garder hors du projet.
