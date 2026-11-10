# Suivi et reprise — RAO Mutuelle / EVE-NG

## 1. Point de reprise immédiat

- Dernière mise à jour : 28/10/2026 soir (CET).
- Intervenant : Claude Code (Opus) pour kamaravael@gmail.com.
- État : **offre, chiffrage, diaporama et maquette terminés et mis en cohérence le 28/10** (revue à 6 agents). Offre v1.0 (`docs/OFFRE_TECHNIQUE.md`, 19 sections, table de correspondance des 21 exigences) ; chiffrage : **221 424 € HT/mois sur 36 mois, TCO 7,97 M€, 22,14 €/utilisateur/mois** ; diaporama de 24 diapositives avec notes d'orateur ; maquette EVE vérifiée, recette **17/17 conforme** le 28/10 (`evidence/20261028T200408Z/`).
- Objectif : soutenance de groupe à 7 (rôles dans `docs/ROLES_SOUTENANCE.md`).
- À lire dans l'ordre : `README.md`, `docs/GUIDE_EXPLICATIF.md`, `docs/OFFRE_TECHNIQUE.md`, `docs/CHIFFRAGE.md`, `docs/MAQUETTE.md`, `docs/DEMO_EVE.md`, `docs/ROLES_SOUTENANCE.md`. `docs/HLD.md` et `inventory/images.yml` sont obsolètes (historique).
- Mode : **A** (déploiement direct sur l'hôte distant PAR861454).
- Décisions en attente : voir la section 9 (points à arbitrer avant la soutenance).
- Opération en cours : aucune.
- Prochaine action : remplir `[Prénom N]` et `[Date de soutenance]`, répéter avec `docs/ROLES_SOUTENANCE.md`.

## 2. Environnement et accès

| Élément | Valeur vérifiée | Date / preuve |
|---|---|---|
| Poste local | Win 11 Pro, Ryzen 7 7435HS 8c/16t, 15,7 Go RAM, 75 Go libres : insuffisant pour la maquette | 15/10 ~11:15, `docs/PREFLIGHT.md` |
| Hyperviseur cible | Proxmox VE 9.2.20, nœud PAR861454, serveur dédié distant joint via tunnel sur https://localhost:8006 | 15/10 ~11:50, `docs/PREFLIGHT.md` |
| CPU / RAM / disque du nœud | Xeon E3-1245 v5 4c/8t, 31,1 Go (24,5 utilisés), 410 Go libres ; VM 101 `llm-security-lab` 16 Go en marche | idem |
| Virtualisation imbriquée / KVM | `kvm_intel nested` = Y | 15/10, sortie de `01_prep_hote.sh` |
| Réseau hôte | vmbr0 public (+ 10.10.10.1/24 existant) ; **vmbr1 10.99.0.1/24 NAT créé** | idem, sauvegarde interfaces.bak-* sur l’hôte |
| Token API | *(obsolète : `root@pam!claude-audit` effacé par la réinstallation du 16/10)*. Nouveau token à créer (plan v2 §4-P1) | — |
| EVE-NG : édition et version | PRO 7.2.0-18 **Freemium = 7 nœuds/instance** (sources off.). ISO en téléchargement | 16/10, 4 agents |
| Serveur et chemin du lab | Non renseignés | À définir |
| Accès SSH / console | Non fournis | Référencer le détenteur, aucun secret |
| Dossier partagé ou dépôt Git | Non renseigné | À définir avec l’équipe |
| Branche / commit / modifications locales | Sans objet à ce stade | À compléter si Git utilisé |

## 3. Tableau des tâches

Statuts : à faire / en cours / bloqué / terminé. Préciser séparément la validation : documenté / généré / appliqué / testé.

| ID | Tâche | Responsable | Statut | Validation / preuve |
|---|---|---|---|---|
| T01 | Rédiger le plan et les règles de reprise | ChatGPT | Terminé | Plan fourni ; infrastructure non testée |
| T02 | Extraire la matrice des exigences du PDF | Claude Code | Terminé | Documenté : `docs/EXIGENCES.md` v1 relue contre le PDF (réf. de page) |
| T03 | Auditer la machine et sélectionner le profil | Claude Code | Terminé | `docs/PREFLIGHT.md` ; hôte distant audité, mode A |
| T04 | Définir HLD, LLD, inventaires et flux | Claude Code | Terminé | HLD dans l'offre (sections 3, 9, 10) et le diaporama ; `docs/FLUX.md` (13 flux, 9 refus) ; LLD de la maquette dans `docs/MAQUETTE.md` |
| T05 | Recenser et acquérir les images | Claude Code | Terminé | Image Debian 13 + FRR 10.3 + strongSwan 6.0 installée dans EVE (`docs/MAQUETTE.md`) |
| T06 | Installer ou vérifier EVE et valider le mini-lab | Claude Code | Terminé | VM 200 EVE PRO 7.2.0-18 Freemium, 7 nœuds + 8 conteneurs LXC |
| T07 | Générer le lab et les configurations | Claude Code | Terminé | `automation/eve/creer_lab.js`, `automation/lab/deploy.py` (rejouable, sans secret stocké) |
| T08 | Déployer progressivement selon les accès | Claude Code | Terminé | Appliqué le 16/10, revérifié le 28/10 |
| T09 | Exécuter la recette et collecter les preuves | Claude Code | Terminé, testé | `automation/lab/recette.py` : 17/17 conformes, bascule 3 à 4 s ; `evidence/20261016T181400Z/`, `evidence/20261028T200408Z/` (référence : scripts finaux, 3 passages conformes le 28/10) |
| T10 | Rédiger l’offre et le chiffrage sourcé | Claude Code | Terminé (v1.0, 28/10) | `docs/OFFRE_TECHNIQUE.md` v1.0, `docs/EXIGENCES.md` v1.1, `docs/CHIFFRAGE.md` (généré, sensibilité incluse) ; diaporama 24 diapositives : https://claude.ai/artifact/957Rryu9hkuprq9MUcjuns (privé, à partager au groupe) |
| T11 | Vérifier le paquet et préparer la passation | Claude Code | Terminé (28/10) | `README.md`, `docs/GUIDE_EXPLICATIF.md`, `docs/GLOSSAIRE.md`, `docs/ROLES_SOUTENANCE.md`, `docs/DEMO_EVE.md` |

## 4. Images et dépendances

Aucune image sélectionnée ou téléchargée à ce stade. Tenir le détail technique dans `inventory/images.yml` dès sa création.

| Image / version | Source officielle | Dossier EVE / disques | État | Empreinte / preuve | Blocage |
|---|---|---|---|---|---|
| À déterminer | À vérifier | Selon template officiel | Manquante | Aucun contrôle exécuté | Inventaire à faire |

Ne pas confondre téléchargée, vérifiée, installée et démarrage validé. Ne pas enregistrer de jetons dans les URLs.

## 5. Décisions et hypothèses

| Décision ou hypothèse | Justification | État |
|---|---|---|
| **D1 : maquette en LXC Proxmox + EVE** (EVE garde les 7 nœuds réseau, hôtes/clients en conteneurs) | Contourne la limite 7 nœuds Freemium sans payer, garde 15 nœuds | **Retenu 16/10 (utilisateur)** |
| **D2 : l'offre d'abord**, maquette ≤~30 % du temps avec critère d'abandon | Le PDF note l'offre, pas la maquette | **Retenu 16/10 (utilisateur)** |
| D3 pare-feu, D4 SIEM, D5 Git | Voir `docs/PLAN_V2.md` §1 | Défauts du plan v2 sauf avis contraire |
| **D6 : ZTNA par FortiSASE, Zscaler ZPA écarté** | ZTNA déjà inclus dans FortiSASE Standard, 1,99 M€ évités sur 36 mois, un seul agent ; justification dans `docs/OFFRE_TECHNIQUE.md` | **Retenu 16/10 (utilisateur)** |
| Cible de 530 sites ; maquette réduite | Périmètre du PDF et faisabilité de démonstration | Principe retenu |

Ajouter ici les arbitrages et leur motif. Distinguer les exigences du PDF des hypothèses de l’équipe.

## 6. Modifications appliquées et preuves de tests

Aucune modification serveur et aucun test à ce stade.

| Horodatage avec fuseau | Cible / fichier | Action réellement réalisée | Résultat | Preuve relative |
|---|---|---|---|---|

Pour chaque test, indiquer réussi / échoué / non exécuté, le résultat attendu et observé. Ne pas déclarer fonctionnel ce qui a seulement été généré.

## 7. Blocages, erreurs et tentatives

- **16/10 : hôte RÉINSTALLÉ par l’utilisateur** depuis la console Dedibox (Proxmox 9). Preuves **non collectées** avant réinstallation (`collecte_rescue.sh` non exécuté) : l’analyse de l’incident s’arrête aux constats de `docs/INCIDENT_PAR861454.md`. Tout a été effacé : VM 101, ISO EVE, vmbr1, token. Nouvelles empreintes SSH de l’hôte : ED25519 `SHA256:ITO0NZL0m0eAnTKFksTLPeN5n9G1hztAxHGE15upBDY`, ECDSA `SHA256:W8bJKxj89ZLBLpPlH8qWtK9weAT9Nh92zbvk+mXRs30`. Port 22 ouvert, 8006 fermé depuis Internet. Prochaines étapes : durcir l’hôte (clés SSH), relancer `01_prep_hote.sh`, retélécharger l’ISO, puis `02_create_eve_vm.sh`.
  **État vérifié le 16/10 ~11h** : PVE 9.2.21, noyau 7.0.14-24, 28 Go RAM libres ; **aucune trace de l’implant** (pas de `/etc/ld.so.preload`, pas de `sshdd.so`, 0 processus). Mot de passe `administrateur` changé par l’utilisateur ; root accessible par `su -` (mot de passe détenu par l’utilisateur). Clé `~/.ssh/id_ed25519_par861454` (PC utilisateur) autorisée pour `administrateur` : Claude Code s’y connecte par clé, sans root (sudo demande un mot de passe). Dépôt enterprise désactivé (`*.disabled`), dépôt `pve-no-subscription` ajouté, mises à jour faites, sudo installé (administrateur dans le groupe sudo). Scripts 00/01/02 copiés dans `/tmp`. ~11h : `00_durcissement_ssh.sh` appliqué (password/kbdinteractive no, root sans mot de passe, MaxAuthTries 3), vérifié de l’extérieur : `Permission denied (publickey)`, la clé fonctionne. `01_prep_hote.sh` appliqué (nested=Y, vmbr1 10.99.0.1/24 NAT). 10.10.10.0/24 n’existe plus sur vmbr0.
  **ISO en cours** : téléchargement lancé par Claude Code (compte administrateur) le 16/10 à 11:03, un seul wget (PID 6309), `~administrateur/eve-pro-prod-bm-7.2.0-18-full.iso(.part)`, journal `~administrateur/eve-iso.log`, environ 3 Mo/s. Une fois fini : en root, `mv /home/administrateur/eve-pro-prod-bm-7.2.0-18-full.iso /var/lib/vz/template/iso/ && chown root:root …`, puis `sha256sum`, puis `02_create_eve_vm.sh`.
- **🚨 INCIDENT DE SÉCURITÉ PROBABLE (16/10)**, avant la réinstallation : `dmesg` montre `unix_chkpwd` qui charge `/usr/local/lib/sshdd.so` (verrou `/run/sshdd.lock`). C’est typique d’un rootkit injecté dans tous les programmes (ld.so.preload), capable de capturer les mots de passe. Il expliquerait aussi le refus de `rename` dans `/var/log` sans refus du noyau (AppArmor écarté : shell et pvedaemon `unconfined`). Mesures conseillées à l’utilisateur : ne plus saisir de mot de passe sur l’hôte, considérer les identifiants comme compromis, conserver les preuves, prévenir le responsable du serveur, prévoir une réinstallation de l’hôte. **Maquette EVE en pause sur PAR861454** jusqu’à décision. **Confirmé le 16/10 ~10h** : un `rename` par appel système direct réussit là où `mv` échoue (hook dans la libc) ; `ld.so.preload` et `sshdd.so` sont illisibles par root ; `sshdd.so` est daté du 01/10 18:37, hors paquet ; 11 processus le chargent. Détails et recommandations : `docs/INCIDENT_PAR861454.md`. Un fichier de test vide `/var/log/t2` reste sur l’hôte.
- **BLOQUANT (16/10)** : sur PAR861454, root ne peut renommer aucun fichier dans `/var/log` (`mv` refusé, alors que `/tmp` fonctionne ; capacités complètes, ext4 rw, pas d’attribut chattr sur tasks/ ; LSM actifs : lockdown, capability, yama, apparmor, ima, evm ; pas d’eBPF LSM). Toutes les tâches Proxmox échouent sur `/var/log/pve/tasks/active`. Piste principale : AppArmor (profil sur le shell ou sur pvedaemon), en cours de vérification. Le serveur est partagé avec d’autres projets : toute correction de politique de sécurité doit être validée par la personne qui l’a déployée.
- *(Obsolète : effacé par la réinstallation du 16/10, ne rien exécuter.)* Avant la réinstallation, une VM 200 était créée à moitié. La future VM 200 sera la VM EVE : ne pas la détruire.
- Informations encore nécessaires : PDF de l’AO, accès Proxmox (token API ou SSH), EVE présent ou non (version/édition), images disponibles.
- Poste local trop juste (15,7 Go RAM) : la maquette doit tourner sur le Proxmox.
- `Get-VM` refusé (droits admin Windows) : on ne sait pas encore si le Proxmox est une VM Hyper-V locale ou un serveur distant tunnelé.
- Aucune dépendance commerciale ou licence identifiée à ce stade.

| Problème | Tentative et résultat | Cause connue ou hypothèse | Prochaine action |
|---|---|---|---|

## 8. Opérations en cours et retour arrière

- Processus en cours : **re-téléchargement de l'ISO** sur l'hôte réinstallé, lancé le 16/10 ~11:03 (compte administrateur, un seul wget PID 6309, `~administrateur/eve-pro-prod-bm-7.2.0-18-full.iso(.part)`, journal `~administrateur/eve-iso.log`). À 11:48 : 31 %, ~3 Mo/s, fin ~13h30. Fin : fichier en `.iso`, puis en root `mv … /var/lib/vz/template/iso/ && chown root:root`, `sha256sum`, puis `02_create_eve_vm.sh` corrigé (dimensionnement plan v2 §2.1). Reprise si coupure : même commande avec `-c`, **seulement si `pgrep -a wget` ne renvoie rien**.
- *(Historique d'avant la réinstallation, sans objet : premier téléchargement du 15/10 effacé ; incident de double wget corrigé ; anomalies `pvesh`/AppArmor dues au rootkit, disparues à la réinstallation.)*
- Sauvegarde / snapshot : aucun créé ; à prévoir avant modification de l’existant.
- Procédure de retour arrière : à définir après audit, avant déploiement.

Avant chaque opération longue, renseigner la cible, la commande ou le script sans secret, le journal et le contrôle de fin. Après une interruption, inspecter l’état réel avant de relancer.

## 9. Trois prochaines actions

1. Groupe : remplacer `[Prénom N]` (diapositive 2 et `docs/ROLES_SOUTENANCE.md`) et `[Date de soutenance]` ; partager le diaporama ; répétition chronométrée.
2. Utilisateur, en root sur l'hôte : `qm snapshot 200 eve-lab-ok` ; changer le mot de passe du compte web `admin` d'EVE ; appliquer `automation/host/05_acces_camarades.sh` pour les camarades.
3. Points à arbitrer par le groupe (ils sont déjà signalés comme limites ou hypothèses dans l'offre) : reprise après perte d'un DC limitée au périmètre critique, ou un serveur de plus par DC ; licences FortiSASE des infogérants ; protection DDoS (option) ; certification HDS du stockage de sauvegarde ; WALLIX (seule la version 6.0 de 2019 a une CSPN) ; DORA à confirmer ; étage de distribution des sièges non chiffré.

Les remplacer après chaque jalon par des actions précises avec fichiers, commandes ou tests pertinents. Ne pas conserver des instructions déjà exécutées.

## 10. Journal de passation

### 15 octobre 2026 — Préparation initiale

- Plan créé puis enrichi : acquisition des images, nommage EVE et continuité multi-intervenants.
- Présent fichier initialisé, sans prétendre à un déploiement.
- Livrables disponibles : ce suivi et le plan. Le PDF source doit accompagner la remise.
- À reprendre : cadrage opérationnel et audit de la machine.

### 15/10/2026 ~11:10–11:40 CEST — Claude Code (Opus 5.5), cadrage

- Tâches : T02, T03, T04 (partiels).
- État initial vérifié : dossier = plan + suivi + un `.crdownload` Chrome non identifié ; PDF absent.
- Actions : audit local et Proxmox en lecture seule ; création de `docs/EXIGENCES.md`, `docs/PREFLIGHT.md`, `inventory/topology.yml`, `inventory/addressing.csv`, `inventory/images.yml`.
- Tests : aucun test de maquette. Proxmox joignable (HTTP 200, API 401).
- Modifications serveur : aucune. Opérations en cours : aucune.
- Prochaine action : voir §9. Les tâches restent attribuées à Claude Code ; elles sont libres si un collègue reprend avant.

### 16/10/2026 — réinstallation, durcissement, revue à 4 agents

- Hôte compromis (rootkit LD_PRELOAD) → réinstallé par l'utilisateur (PVE 9.2.21), vérifié sans trace de l'implant. Durci : SSH par clé (`00_durcissement_ssh.sh`), nested=Y + vmbr1 NAT (`01_prep_hote.sh`). Détails : `docs/INCIDENT_PAR861454.md`, `docs/PREFLIGHT.md`.
- PDF récupéré et lu ; `docs/EXIGENCES.md` v1 relue contre le PDF (ajout E17 LAN/Wi-Fi, hypothèses H6–H11).
- Re-téléchargement de l'ISO EVE en cours.
- **Revue du plan par 4 agents** (automatisation, performance, sécurité, pilotage) → `docs/PLAN_V2.md`. Constats majeurs : EVE Freemium = 7 nœuds (≠ 15 prévus), priorité à remettre sur l'offre, hôte à filtrer (nftables) et plan de gestion à sécuriser. Script 02 corrigé (la VM 101 n'existe plus). Commande dangereuse `qm destroy 200` retirée du suivi.
- Prochaine action : voir §9.

### 16/10/2026 ~12h20 — chiffrage v1

- Candidat A validé par l'utilisateur pour toutes les fonctions. Prix sourcés (revendeurs, comparateurs, pages éditeurs ; BCE du 15/10 pour les devises), quantités calculées par règles depuis les volumes du PDF et les hypothèses H6–H12.
- Résultat : 4,52 M€ de frais initiaux + 91 k€/mois ; en abonnement 36 mois tout compris 230,6 k€/mois (8,30 M€), soit 23,06 €/utilisateur/mois. Avec ZPA : 285,8 k€/mois (10,29 M€).
- Lignes estimées ou sur devis à consolider : FTTO/transit/inter-DC, énergie DC, WALLIX, ZPA, serveur de sauvegarde, taux de location (7 %).
- ~13h40 : relecture critique → ajout d'un stock de spare (2 %) et d'une section « Non inclus » au rapport. Nouveau total : 231,7 k€/mois en abonnement (8,34 M€ sur 36 mois) ; 286,9 k€/mois avec ZPA.

### 16/10/2026 ~17h50–18h00 — démarrage du projet Proxmox

- Constat avant P0 : 8006 et 3128 écoutaient sur toutes les adresses, rpcbind (111) et BIND (53) sur l'IP publique.
- `03_p0_securite.sh` appliqué (1er essai interrompu : lancé depuis la console web, coupée par le redémarrage de pveproxy ; relancé en SSH). Vérifié depuis l'extérieur à 17:56 : seul 22 répond ; 111, 53, 8006, 3128 fermés. Pare-feu rendu permanent (`systemctl enable nftables`).
- `01_prep_hote.sh` : ponts vmbr2 et vmbr10 à vmbr16 créés (sans IP), vmbr0 et NAT inchangés.
- `02_create_eve_vm.sh` : ISO rangée dans `/var/lib/vz/template/iso` (10 775 506 944 octets), **VM 200 créée et démarrée** (20 Go, 6 vCPU, 9 cartes réseau). SHA256 à reporter dans `inventory/images.yml`.
- Reste côté utilisateur : installation d'EVE en console, `passwd` root, MFA Scaleway, suppression de `proxmox.ps1`.
- ~19h25 : **EVE installé** (Ubuntu 24.04.5, noyau 7.1.1-eve-ksm, hôte `eve-rao`, 10.99.0.10), accessible en SSH depuis l'hôte, NTP synchronisé (Europe/Paris). Boucle d'installation rencontrée (ISO en premier dans l'ordre de démarrage) : avertissement ajouté dans `02_create_eve_vm.sh`. Empreinte ED25519 d'EVE : `SHA256:BvCQBwtTonO8u7ntunGqq/Am/fd7oqfJnrW56LJZ58c`.
- ~19h30 : contrôles EVE OK (6 vCPU avec vmx, pnet0 à pnet8 actifs, Internet OK, 19 Gio). **Snapshot `eve-base` pris** (VM arrêtée).
- ~19h35 : **8 conteneurs LXC 301-308 en marche** (Debian 13.6 amd64, ponts vmbr10-16, gestion vmbr2 10.98.0.101-108). 1er essai raté : le script avait pris le modèle arm64 (tri alphabétique) ; filtre corrigé sur `_amd64`, conteneurs ARM supprimés et recréés. Avertissement non bloquant : `pveam update failed` (voir `/var/log/pveam.log`).
- ~19h40 : clé de l'utilisateur ajoutée pour root sur EVE ; **Claude pilote EVE en SSH par rebond via l'hôte** (empreinte EVE vérifiée).
- ~19h50 : **image `linux-debian13-routeur` installée** dans `/opt/unetlab/addons/qemu/linux-debian13-routeur/virtioa.qcow2` : Debian 13 genericcloud officielle (SHA512 vérifié) + FRR 10.3, strongSwan 6.0 (swanctl), nftables, rsyslog et outils de test ; cloud-init retiré ; noms `ethX`, console série ; clé root ; clés d'hôte SSH et machine-id régénérées au 1er démarrage. SHA256 `9b73dd01d9fba6225b4f52d7ce1b8dda81605185cdfb40c981745544bc79ee29`. Fabrication : `virt-customize` n'a pas de réseau dans EVE → paquets installés par `qemu-nbd` + chroot, réglages hors ligne par `virt-customize --no-network` (dossier `/root/build` sur EVE).
- ~19h55 : **DHCP de gestion** : service `rao-dhcp` sur EVE (dnsmasq-base, `pnet1` = Cloud1 = vmbr2, EVE en 10.98.0.2, plage 10.98.0.50-99, réservations `/etc/rao/dhcp-hosts`, ni passerelle ni DNS annoncés). Vérifié : les conteneurs 10.98.0.101/105/108 répondent depuis EVE.
- Le code d'EVE PRO est chiffré (format des labs non lisible) → lab créé par l'API depuis la session web de l'utilisateur (Chrome, tunnel 8443), sans mot de passe côté Claude. Compte web `admin` : mot de passe d'usine à changer (rappel donné à l'utilisateur).
- ~20h00 : **lab `/RAO.unl` créé et démarré** : 14 réseaux (Cloud1-8 + 6 ponts internes), 7 nœuds Debian (isp-a, isp-b, fw-dc1, fw-dc2, gw-hq, gw-agfr, gw-part), câblage vérifié interface par interface. Script reproductible : `automation/eve/creer_lab.js`. MAC EVE = `50:00:00:<nœud>:00:<interface>` → réservations DHCP 10.98.0.11-17. L'arrêt par `GET …/stop` renvoie 400 (syntaxe à trouver).
- **Les 15 machines répondent par leur nom** (`ssh -F automation/ssh_config <nom>`, rebond hôte → EVE). Inventaire mis à jour : `inventory/topology.yml` (état déployé). RAM EVE : ~4 Go utilisés sur 20 avec les 7 nœuds.
- ~20h05 : **réseau du lab configuré** par `automation/lab/deploy.py` (rejouable, clés IPsec régénérées à chaque passage, aucun secret stocké) : adressage systemd-networkd, 6 tunnels IPsec IKEv2 route-based (XFRM) depuis fw-dc1, OSPF (opérateur A coût 10, B coût 100, hello 1 s / dead 4 s), routes statiques pour le partenaire, nftables en refus par défaut avec journalisation (politique FLUX sur fw-dc1, invités et sortie locale avec NAT sur gw-agfr), DNAT de la publication, anti-usurpation BCP 38 sur les opérateurs, journaux kern → `logs` (10.98.0.105:6514). Services de test Python sur les conteneurs.
- Corrections trouvées pendant la recette : sonde ICMP bloquée par la politique (ping autorisé depuis les sites internes) ; opérateurs sans anti-usurpation ; **MOBIKE** déplaçait le tunnel A sur l'opérateur B et masquait la bascule (`mobike = no`) ; un gabarit swanctl cassé a fait tomber les tunnels quelques minutes (corrigé, contrôle `assert` + échec explicite si swanctl refuse la configuration).
- ~20h14 : **recette finale `automation/lab/recette.py` : 17/17 flux conformes (10 autorisés, 7 refus), bascule WAN réussie (~3,8 s d'interruption)**, F07/F08/N07/N09 non exécutés (pas de ZTNA/IdP dans la maquette). Preuves : `evidence/20261016T181400Z/` (CSV, rapport, journaux pare-feu, mesure de bascule, SHA256SUMS). Les deux essais précédents ont été supprimés (bascule non valable).

### 19/10/2026 — accès des membres du groupe

- `automation/connexion_rao.ps1` (à envoyer aux camarades) : crée leur clé SSH, épingle la clé de l'hôte, ouvre le tunnel 8443 → EVE et le navigateur. `automation/host/05_acces_camarades.sh` (root, sur l'hôte) : compte `camarade` sans mot de passe ni shell, une clé par membre limitée à `10.99.0.10:443`.
- Testé depuis le PC le 19/10 : clé non autorisée → refus détecté ; tunnel autorisé → EVE répond. **Script 05 pas encore appliqué sur l'hôte.** Avant de partager : changer le mot de passe d'usine du compte web `admin` d'EVE.

### 28/10/2026 — reprise à 6 agents : amélioration et explication

- Demande : « retravaille le projet, autant d'agents (max 6) pour améliorer le projet et bien l'expliquer ». Six agents en parallèle : chiffrage, offre, diaporama, guide, maquette, jury ; mise en cohérence finale par Claude Code.
- **Chiffrage** (`docs/CHIFFRAGE.csv`, `automation/chiffrage/calcul.py`) : prix corrigés (borne AP-615 au modèle RW, commutateurs CX 6100 sourcés), sections « Lecture rapide », « Méthode » et analyse de sensibilité, contrôles `assert` ajoutés. Nouveau total : **221 424 €/mois** (contre 231 737), TCO 7,97 M€, achat 7,50 M€ (4,22 M€ initiaux + 91 147 €/mois), 22,14 €/utilisateur, 418 €/site. Postes non inclus complétés (optiques, distribution des sièges, onduleurs, licences des VM, DDoS).
- **Offre** v1.0 et **exigences** v1.1 : 19 sections, correspondance avec les 21 exigences, alternatives écartées, glossaire et sources ; limites corrigées (N02 non journalisé, PRA limité au périmètre critique, syslog TCP non chiffré dans la maquette).
- **Diaporama** : 24 diapositives, notes d'orateur réécrites, chiffres recalés (synthèse et coûts recalés par Claude Code).
- **Explications** : `README.md`, `docs/GUIDE_EXPLICATIF.md`, `docs/GLOSSAIRE.md`.
- **Maquette** : revérifiée, `docs/MAQUETTE.md` écrit, recette conforme (`evidence/20261028T200408Z/`), `docs/DEMO_EVE.md` revu.
- Cohérence : `docs/ROLES_SOUTENANCE.md` et `docs/FLUX.md` (F11) recalés ; `docs/HLD.md` et `inventory/images.yml` marqués obsolètes.

### 10/11/2026 — fenêtre de démonstration et panne de la maquette

- Ajout de la fenêtre de démonstration `automation/demo_rao.ps1` (lancement : `automation/Demo_RAO.cmd`) : vérification, 7 étapes du scénario, verdict lisible, schéma animé, bouton de réparation.
- Panne trouvée au premier essai : **disque de fw-dc1 plein à 100 %**. strongSwan journalisait chaque paquet DPD (1,7 Go en 13 jours), FRR plantait en boucle (SIGBUS) : plus d'OSPF, trafic des sites hors tunnels, F05 et F09 en échec (recette `evidence/20261110T182053Z/`, non conforme).
- Réparation : journaux de maintien vidés sur les 5 routeurs (35 % d'occupation), `deploy.py` corrigé (strongSwan au niveau 0, journal système plafonné à 50 Mo, bruit multicast refusé sans journal) et relancé. Recette **conforme 17/17, bascule 3,4 s** : `evidence/20261110T183628Z/`.

### 10/11/2026 — dépôt GitHub et accès du groupe

- Dépôt **privé** https://github.com/Kamalors/securite-des-infrastructures (privé : l'adresse du serveur et le rapport d'incident y figurent). Fichiers personnels exclus par `.gitignore`.
- Accès des membres : `docs/ACCES_CAMARADES.md`. Côté serveur, en root : `05_acces_camarades.sh` (tunnels EVE-NG et Proxmox) et `06_comptes_proxmox.sh` (comptes Proxmox limités au lab). **Pas encore appliqués** ; changer d'abord le mot de passe d'usine du compte web `admin` d'EVE-NG.

### Modèle d’entrée à recopier

- Date/heure/fuseau ; intervenant et IA :
- Tâche réservée / cible :
- État initial vérifié :
- Actions réalisées et fichiers modifiés :
- Tests et preuves :
- Erreurs, limites, blocages :
- Opérations encore en cours :
- Sauvegarde et retour arrière :
- Branche/commit et fichiers non commités, si applicable :
- Prochaine action précise :
- Tâche libérée ou responsable de la suite :

## 11. Instruction pour l’IA qui reprend

Lis ce suivi, puis le plan et les fichiers référencés. Vérifie les états réels sans écraser les modifications existantes. Identifie la prochaine tâche, réserve-la avec le nom du collègue, et poursuis à partir du dernier résultat vérifié. Mets à jour ce fichier après chaque tâche significative et avant de terminer. Les fichiers et l’accès serveur nécessaires doivent être partagés par l’équipe ; ce suivi ne remplace pas leur transmission. Aucun secret ne doit apparaître ici.
