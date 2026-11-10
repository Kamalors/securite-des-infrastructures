# Matrice des exigences — RAO Sécurité des infrastructures

État : **v1.1 du 28/10/2026**, relue contre le PDF (`RAO (Réponse Appel d'Offre) - Sécurité des Infrastructures.pdf`, 3 pages) et alignée sur l'offre finale (`docs/OFFRE_TECHNIQUE.md` v1.0) et sur le chiffrage (`docs/CHIFFRAGE.md`).
Légende origine : **PDF** = exigence du client ; **ÉQ** = choix de l'équipe, justifié dans l'offre ; **HYP** = hypothèse affichée dans l'offre.

## 0. Ce que le client évalue en priorité (PDF p.3)

1. **Solutions techniques** : concept, **modèle d'équipement retenu**, justification des choix → offre, sections 4 à 14 et tableau de la section 15.
2. **Architecture datacenter et agences** en **schémas HLD** (schémas de principe) → offre, sections 3, 9 et 10, et schémas du diaporama.
3. **Coûts globaux**, avec une préférence pour **l'abonnement** (« ma DSI ne me permet de débloquer une grosse somme d'un coup »), ventilés en **Housing, Connectivité WAN, Serveurs, Équipements réseau, Équipements de sécurité, Etc.** → offre, section 16.

Le PDF ne demande pas de maquette : l'équipe la propose comme preuve (ÉQ). Le PDF parle de « chaque groupe » et de « présentation » : il s'agit vraisemblablement d'une soutenance de groupe, format à confirmer.

## 1. Volumétrie

| ID | Exigence | Origine | Réf. PDF |
|---|---|---|---|
| V1 | 500 sites France : 2 sièges + 498 agences distantes | PDF | p.1 « Périmètre technique » |
| V2 | 30 agences à l'international (530 sites au total) | PDF | p.1 |
| V3 | 10 000 utilisateurs : 4 000 sur les 2 sièges, 4 000 en agences FR, 2 000 en agences internationales | PDF | p.1 |
| V4 | ~100 partenaires : 40 % site à site, 60 % utilisateurs nomades | PDF | p.2 « accès partenaire » |

Ratios dérivés (ÉQ) : ~8 utilisateurs par agence FR (4 000/498), ~67 par agence internationale (2 000/30).

## 2. Exigence → solution → preuve → limite → poste de coût

Les identifiants de preuve renvoient à `docs/FLUX.md` et à la recette `evidence/20261016T181400Z/recette.md` (17/17 tests conformes, 4 non exécutés).

| ID | Exigence | Réf. PDF | Solution proposée | Offre § | Preuve (maquette) | Limite | Poste de coût (libellés du PDF) |
|---|---|---|---|---|---|---|---|
| E01 | Solution housing DC : répartition, redondance | p.1 « Architecture datacenter » | 2 DC en housing certifiés HDS, région parisienne, domaines de panne distincts ; 2 baies 42U et 6 kW par DC, alimentation A+B, 2 opérateurs ; actif/actif pour la publication, actif/passif pour les bases | 5 | Aucune (physique) | La maquette ne prouve pas la résilience physique ; RPO/RTO à fixer (H4) | Housing |
| E02 | Compute : virtuel ou physique, **quelles technologies** | p.1 | Virtuel : VMware vSphere Foundation + vSAN sur 4 Dell PowerEdge R760 par DC (N+1) ; sauvegarde Veeam avec copie immuable | 6 | Zones DC simulées (hôtes en conteneurs) | Capacité non prouvée ; reprise après perte d'un DC limitée au périmètre critique (2 To de mémoire par DC pour 2,4 To requis par les 300 VM), à définir avec le client (H4) | Serveurs |
| E03 | Connectivité WAN en DC et sur les sites | p.1 | Fortinet Secure SD-WAN sur accès Internet, double hub vers les 2 DC ; 2 transits par DC, 2 liaisons inter-DC ; profils d'accès par type de site | 4 | Bascule WAN mesurée à 3,8 s, retour automatique (`bascule_wan.txt`) | Pare-feu Linux (nftables, strongSwan, FRR) et non des FortiGate : tunnels IPsec routés, pas de pilotage SD-WAN par application | Connectivité WAN |
| E04 | Nord/sud : segmentation | p.2 | Paire FortiGate 600F de périmètre par DC, DMZ dédiée | 7.1 | F01, N01, N02 | N02 refusé car non routé depuis Internet : pas de journal (le paquet n'atteint pas le pare-feu) | Équipements de sécurité |
| E07 | Publication Internet : web, API | p.2 | F5 BIG-IP Advanced WAF en DMZ (2 par DC), TLS terminé dans le DC | 7.2 | F01 (HTTPS), N01 | WAF F5 non représenté (reverse proxy simple en maquette) | Équipements de sécurité |
| E08 | Publication Internet : FTP | p.2 | Passerelle SFTP en DMZ ; FTP en clair en exception temporaire isolée | 7.3 | F02 (SFTP) | — | Équipements de sécurité |
| E06 | Sécurité des accès Internet des ressources DC et « d'autres usages potentiels » | p.2 | Sortie centrale filtrée pour les serveurs ; sortie locale filtrée par le FortiGate en agence ; FortiSASE pour les nomades ; réseau invités isolé | 7.4 | F13, N05 (invités) | Sortie filtrée des serveurs du DC non testée | Équipements de sécurité |
| E05 | Est/ouest : segmentation, solutions entre réseaux DC | p.2 | Seconde paire FortiGate 600F par DC ; zones DMZ, applications, données, administration, partenaires ; refus par défaut | 8 | F03, F04, N03, N04 | Pas de micro-segmentation dans l'hyperviseur | Équipements de sécurité |
| E09 | Agences : architecture, solutions de sécurité, Internet + accès aux DC | p.2 | 3 profils : FortiGate 40F-3G4G (agence FR), 2 × FortiGate 70G en HA (agence internationale), 2 × FortiGate 200G en HA (siège) ; tunnels vers les 2 DC, sortie Internet locale filtrée | 4.2, 10 | F05, N08 | 2 sites simulés sur 530 (siège, agence FR) ; agence internationale non déployée | Équipements de sécurité / Connectivité WAN |
| E17 | Agences : « Solutions réseaux » (LAN, Wi-Fi), y compris sièges | p.2 | Aruba CX 6100 (accès), CX 8100 (cœur des sièges), bornes Aruba AP-615 RW (Wi-Fi 6E), Aruba Central ; réseaux utilisateurs, invités, administration, téléphonie séparés ; 802.1X | 10.1, 10.2 | F13, N05 (segment invités) | Pas de Wi-Fi ni de 802.1X en maquette ; distribution des sièges à dimensionner (53 commutateurs pour 24 ports de cœur) | Équipements réseau |
| E10 | Administration distante : accès d'infogérance | p.2 | Bastion WALLIX (MFA, approbation, enregistrement des sessions), accessible uniquement par FortiSASE ; NOC/SOC en heures ouvrées | 11 | F09, F10, N08 ; journaux F11 (syslog TCP non chiffré en maquette, TLS en production) | MFA et enregistrement de session non représentés (bastion Linux en maquette) | Équipements de sécurité / Etc. |
| E11 | Nomadisme des collaborateurs | p.2 | FortiSASE Standard (3 000 nomades) : sécurité Internet + ZTNA, MFA, contrôle du poste | 12 | Non exécuté (F07, N09) | ZTNA et MFA non représentés | Équipements de sécurité |
| E12 | Partenaires site à site (40 %) | p.2-3 | Tunnel IPsec vers une zone partenaire des 2 DC (hubs FortiGate 600F), accès aux seules applications contractuelles | 13 | F06, N06 | — | Équipements de sécurité |
| E13 | Partenaires nomades (60 %) | p.2-3 | FortiSASE : portail sans agent (applications web) ou agent ; comptes distincts, MFA, durée limitée (300 utilisateurs) | 12.3, 13 | Non exécuté (F08, N07) | Accès nomade non représenté | Équipements de sécurité |
| E14 | Concept, **modèle d'équipement**, justification | p.3 | Un modèle par fonction, justifié face à une alternative écartée | 4 à 15 | — | Prix publics ou estimés, devis requis | — |
| E15 | Schémas HLD **DC et agences** | p.3 | HLD global, HLD datacenter, HLD agences par profil, HLD accès distants | 3, 9, 10 + diaporama | — | — | — |
| E16 | Coûts globaux, abonnement privilégié | p.3 | 221 424 € HT/mois sur 36 mois sans investissement initial (location financière à 7 %/an + récurrent), ventilés par poste du PDF ; TCO 7,97 M€ | 16 | — | Prix publics ou estimés, devis requis | — |

## 3. Hypothèses affichées (non fournies par le client)

| ID | Hypothèse | Valeur retenue dans l'offre | Utile pour |
|---|---|---|---|
| H1 | Débits par profil de site | Fibre pro FTTH en agence FR ; 2 × FTTO 1 Gbit/s par siège ; 2 accès par agence internationale ; 2 transits 1 Gbit/s par DC | WAN |
| H2 | Applications et volumes publiés | Non communiqués ; 4 WAF de 1 Gbit/s | DMZ, WAF |
| H3 | Pays des 30 agences internationales (UE / hors UE) | Inconnus ; tarif français de référence | WAN, RGPD |
| H4 | RPO / RTO / SLA | À fixer avec le client | Housing, compute |
| H6 | Nombre de nomades parmi les 10 000 utilisateurs | 3 000 (30 %) | Licences FortiSASE |
| H7 | Nombre d'utilisateurs chez les ~60 partenaires nomades (organisations ≠ personnes) | 300 (60 × 5) | Licences FortiSASE, IdP |
| H8 | Nombre de VM et volume de stockage | 300 VM (moyenne 2 vCPU, 8 Go, 150 Go) | Serveurs |
| H9 | Nombre d'administrateurs et d'infogérants | 50 comptes à privilèges | Licences du bastion |
| H10 | Volume de journaux | Non communiqué ; Wazuh hébergé sur le compute | SIEM |
| H11 | Répartition des 4 000 utilisateurs entre les 2 sièges | 2 000 par siège | LAN, Wi-Fi, WAN sièges |
| H12 | Le client dispose déjà d'un fournisseur d'identité avec MFA (ex. Entra ID P1) | Oui ; sinon option FortiToken/FortiAuthenticator à chiffrer | Nomadisme, partenaires, bastion |

Le numéro H5 n'est pas utilisé (hypothèse retirée) ; la numérotation des autres est conservée car `docs/CHIFFRAGE.md` y fait référence.

Règles de dimensionnement : 1,25 port LAN par utilisateur, 1 borne Wi-Fi pour 25 utilisateurs (1 par agence FR), HA au-delà de 50 utilisateurs, spare de 2 % du parc agences. Chiffrage recalculé par `automation/chiffrage/calcul.py`.

## 4. Cadre réglementaire (arguments de justification, détail en section 19 de l'offre)

- Données de santé : RGPD art. 9 ; certification **HDS** exigée de l'hébergeur, du stockage de sauvegarde et de l'infogérant (assujettissement exact de chaque traitement à confirmer avec le client). Le référentiel HDS v2 impose un hébergement physique dans l'Espace économique européen.
- **DORA** (règlement UE 2022/2554), applicable aux entreprises d'assurance depuis le 17/01/2025, hors petites structures exclues de Solvabilité II pour raison de taille : une grande mutuelle est vraisemblablement concernée (à confirmer par sa conformité). Points traités : registre et contrats des prestataires TIC (hébergeur, infogérant, SD-WAN, SASE), continuité sur 2 DC, plan de réversibilité face à la dépendance à Fortinet.
