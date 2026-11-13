# Chiffrage de l'offre

Généré par `automation/chiffrage/calcul.py` le 13/11/2026. Ne pas modifier à la main : corriger `docs/CHIFFRAGE.csv` puis relancer le script.

Montants en **euros hors taxes**. Devises converties au taux de référence BCE du 15/10/2026 (1 € = 1,1208 $ = 1,5923 $ CA = 0,8461 £).

## Lecture rapide

- **Ce que paie la mutuelle : 221 424 € HT par mois pendant 36 mois**, sans investissement de départ. Ce loyer couvre tout : matériel, licences, liens opérateurs, hébergement en datacenter, déploiement et exploitation.
- Rapporté à l'usage : **22,14 € par utilisateur et par mois**, 418 € par site et par mois.
- Sur 3 ans, le coût total est de **7 971 248 €**. Payer comptant coûterait 7 500 489 € : l'écart de 470 759 € est le prix de l'étalement (intérêts de la location).
- Les trois postes les plus lourds : Équipements de sécurité (64 478 €/mois), Équipements réseau (52 448 €/mois), Services et autres (Etc.) (44 493 €/mois).
- Ce qui peut faire bouger la facture : une remise de 20 % sur le matériel et les licences, courante sur un tel volume, ferait −26 087 €/mois ; 1 000 nomades de plus, +4 152 €/mois ; chaque agence ouverte en plus, +177 €/mois.
- Les prix sont publics ou estimés : ils seront confirmés par devis. Les renouvellements après 36 mois ne sont pas inclus.

## Méthode

1. **Quantités.** Chaque ligne de `docs/CHIFFRAGE.csv` porte une règle de quantité écrite avec les paramètres du tableau « Hypothèses de quantité ». Exemples : `AG_FR` = un équipement par agence FR (498) ; `2*SIEGE` = deux boîtiers par siège (haute disponibilité) ; `ceil(VM/10)` = packs de 10 VM arrondis au pack supérieur. Changer une hypothèse recalcule toutes les lignes.
2. **Prix.** Chaque prix a une source (lien dans le détail) et une nature : **P** = prix public constaté chez un revendeur ou un comparateur, **E** = estimation à partir d'une source, **D** = devis obligatoire (fourchette large). Les prix en devises sont convertis au taux BCE ci-dessus.
3. **Frais initiaux ou récurrents.** *unique* = payé une fois (matériel, mise en service, déploiement). *36mois* = licence prépayée pour 3 ans (bundles FortiGate, FortiSASE, FortiManager, Aruba Central) : elle est facturée à la commande pour toute la durée du contrat, donc comptée en frais initiaux comme le matériel. *mois* et *an* = récurrent ; un prix annuel est divisé par 12.
4. **Mensualité de location.** Les frais initiaux sont financés par une location financière : loyer constant M = C × r / (1 − (1 + r)^−36), avec C les frais initiaux et r = taux annuel / 12 (taux de 7 %, hypothèse à faire confirmer par un bailleur). Exemple : 100 000 € de frais initiaux donnent 3 087,71 €/mois, soit 111 158 € remboursés sur 36 mois.
5. **Achat ou abonnement.** Achat : frais initiaux payés au départ + récurrent × 36. Abonnement (préféré par la DSI du client) : mensualité de location + récurrent, chaque mois. L'abonnement coûte un peu plus au total mais supprime la grosse dépense de départ.

## Synthèse

Location financière sur 36 mois au taux annuel de 7 % (hypothèse à faire confirmer par un bailleur) : tous les frais initiaux sont lissés, il ne reste **aucun investissement de départ**.

| Scénario | Frais initiaux | Récurrent mensuel | TCO 36 mois (achat) | Abonnement mensuel tout compris | TCO 36 mois (abonnement) | € / utilisateur / mois | € / site / mois |
|---|---:|---:|---:|---:|---:|---:|---:|
| Offre retenue (ZTNA par FortiSASE) | 4 219 196 € | 91 147 € | 7 500 489 € | 221 424 € | 7 971 248 € | 22,14 € | 418 € |
| Variante écartée (avec Zscaler ZPA) | 4 219 196 € | 146 353 € | 9 487 909 € | 276 630 € | 9 958 668 € | 27,66 € | 522 € |

La variante avec Zscaler ZPA est écartée (16/10/2026) : le ZTNA est compris dans la souscription utilisateur FortiSASE ; seule une licence d'accès privé reste à ajouter sur les 4 FortiGate hubs, à chiffrer au devis (offre, section 12.3). Justification : `docs/OFFRE_TECHNIQUE.md`, section « Choix du ZTNA ».

## Par poste du PDF : Offre retenue (ZTNA par FortiSASE)

| Poste | Frais initiaux | Récurrent mensuel | Abonnement mensuel (36 mois) | TCO 36 mois (abonnement) |
|---|---:|---:|---:|---:|
| Housing | 0 € | 4 511 € | 4 511 € | 162 393 € |
| Connectivité WAN | 35 000 € | 40 192 € | 41 273 € | 1 485 818 € |
| Serveurs | 159 036 € | 9 311 € | 14 221 € | 511 959 € |
| Équipements réseau | 1 698 619 € | 0 € | 52 448 € | 1 888 143 € |
| Équipements de sécurité | 1 926 161 € | 5 004 € | 64 478 € | 2 321 202 € |
| Services et autres (Etc.) | 400 380 € | 32 130 € | 44 493 € | 1 601 733 € |
| **Total** | **4 219 196 €** | **91 147 €** | **221 424 €** | **7 971 248 €** |

## Analyse de sensibilité (offre retenue)

Calculée par le script : une seule hypothèse change à chaque ligne, les autres restent celles de la base. La remise porte sur le matériel et les licences éditeur (serveurs, VMware, Veeam, Aruba, Fortinet, F5, WALLIX), pas sur les liens, l'hébergement ni les services.

| Hypothèse modifiée | Frais initiaux | Récurrent mensuel | Abonnement mensuel | Écart / base | Écart en % |
|---|---:|---:|---:|---:|---:|
| Base : 3 000 nomades, taux 7 %, prix publics | 4 219 196 € | 91 147 € | 221 424 € | +0 € | +0,0 % |
| 2 000 nomades (−1 000) | 4 084 736 € | 91 147 € | 217 272 € | −4 152 € | −1,9 % |
| 4 000 nomades (+1 000) | 4 353 655 € | 91 147 € | 225 575 € | +4 152 € | +1,9 % |
| Taux de location 5 % | 4 219 196 € | 91 147 € | 217 600 € | −3 823 € | −1,7 % |
| Taux de location 9 % | 4 219 196 € | 91 147 € | 225 316 € | +3 893 € | +1,8 % |
| Remise négociée 20 % sur matériel et licences éditeur | 3 462 433 € | 88 427 € | 195 337 € | −26 087 € | −11,8 % |
| Remise négociée 30 % sur matériel et licences éditeur | 3 084 051 € | 87 067 € | 182 294 € | −39 130 € | −17,7 % |
| Une agence FR de plus (coût marginal) | 4 223 333 € | 91 196 € | 221 600 € | +177 € | +0,1 % |

Une agence FR de plus (pare-feu, switch, borne Wi-Fi, licences, une journée de déploiement, fibre et SIM de secours) coûte 4 137 € de frais initiaux et 49 €/mois de récurrent, soit **177 €/mois d'abonnement**. Chaque tranche de 1 000 nomades pèse 4 152 €/mois (licences FortiSASE).

## Non inclus (à chiffrer ou hors périmètre)

- Cross-connects opérateurs dans les DC (sur devis de l'hébergeur).
- Déplacements et logistique : envoi des 528 kits, transport et douanes vers les 30 pays.
- Extension vSAN au-delà du droit VVF (0,25 TiB par cœur, soit 64 TiB par DC), si le besoin réel le dépasse.
- Surcoût éventuel d'un hébergeur certifié HDS par rapport au prix de référence retenu.
- SOC 24/7 : l'infogérance chiffrée couvre les heures ouvrées.
- Fournisseur d'identité et MFA : supposés existants chez le client (H12).
- Renouvellements au-delà de 36 mois.
- Optiques SFP+/QSFP28 et câbles DAC (uplinks des switches d'accès, cœurs, ToR et FortiGate des DC) : quantité à fixer avec le plan de câblage.
- Couche de distribution des sièges : 53 switches d'accès par siège en double attachement dépassent les 24 ports SFP+ d'une paire de CX 8100 ; étage de distribution ou cœur plus dense à dimensionner.
- Onduleurs en agence, licences des systèmes et applications des 300 VM : supposés fournis par le client.
- Protection DDoS volumétrique chez les opérateurs de transit des DC : option sur devis.
- Licence d'accès privé FortiSASE sur les 4 FortiGate hubs (ou édition Advanced) : de ~30 k€ à ~410 k€ sur 36 mois, à chiffrer au devis (offre, section 12.3).
- Protection des postes de travail (EDR) : supposée existante chez le client, à chiffrer si besoin.

## Hypothèses de quantité

| Paramètre | Valeur | Origine |
|---|---:|---|
| `SIEGE` | 2 | PDF |
| `AG_FR` | 498 | PDF |
| `AG_INT` | 30 | PDF |
| `DC` | 2 | choix de l'équipe |
| `U_SIEGE` | 2000 | H11 |
| `U_AG_FR` | 4000 | PDF |
| `U_INT` | 2000 | PDF |
| `NOMADES` | 3000 | H6 |
| `PART_USERS` | 300 | H7 |
| `ADMINS` | 50 | H9 |
| `VM` | 300 | H8 |
| `HOTES_DC` | 4 | règle de dimensionnement |
| `COEURS_HOTE` | 64 | règle de dimensionnement |
| `PORTS_USER` | 1.25 | règle de dimensionnement |
| `USERS_AP` | 25 | règle de dimensionnement |

## Détail des lignes

| Id | Poste | Libellé | Règle de quantité | Qté | Prix unitaire | Périodicité | Montant | Nature | Scénario | Source |
|---|---|---|---|---:|---:|---|---:|---|---|---|
| HOU-BAIE | Housing | Baie 42U en colocation à Paris, 2 par DC (11,20 €/U/mois x 42U, hors énergie, HDS à exiger au devis) | `2*DC` | 4 | 470,40 € | mois | 1 882 €/mois | P | base | [lien](https://yorkhost.fr/en/housing/) |
| HOU-ENER | Housing | Énergie : 6 kW par DC x 730 h x PUE 1,5 x 0,2001 €/kWh (tarif base pris comme majorant) | `DC` | 2 | 1 314,66 € | mois | 2 629 €/mois | E | base | [lien](https://www.quelleenergie.fr/energie/tarif-electricite) |
| WAN-FTTH | Connectivité WAN | Fibre pro agence FR (Bbox Pro Fibre, secours 4G du boîtier inclus, GTI 8 h) | `AG_FR` | 498 | 34,99 € | mois | 17 425 €/mois | P | base | [lien](https://lafibreoptique.fr/fibre-pro/bouygues) |
| WAN-SIM-AG | Connectivité WAN | SIM data 4G de secours agence FR, insérée dans le FortiGate (SIM Pro 20 Go) | `AG_FR` | 498 | 13,99 € | mois | 6 967 €/mois | P | base | [lien](https://mediaspro.lapostemobile.fr/portail_mobile/pdf/LPM-PRO-Recapitulatif-Contractuel-FSIM.pdf) |
| WAN-FTTO-SIEGE | Connectivité WAN | Fibre dédiée FTTO 1 Gbit/s, 2 opérateurs par siège (haut de fourchette, devis) | `2*SIEGE` | 4 | 1 000,00 € | mois | 4 000 €/mois | E | base | [lien](https://entreprises.selectra.info/telecom/fibre-pro) |
| WAN-SIM-SIEGE | Connectivité WAN | SIM data 4G/5G de secours siège (SIM Pro 200 Go) | `SIEGE` | 2 | 19,99 € | mois | 40 €/mois | P | base | [lien](https://mediaspro.lapostemobile.fr/portail_mobile/pdf/LPM-PRO-Recapitulatif-Contractuel-FSIM.pdf) |
| WAN-INT | Connectivité WAN | Accès Internet pro agence internationale, 2 par agence (base : Orange Connect Pro Fibre, pays inconnus H3) | `2*AG_INT` | 60 | 96,00 € | mois | 5 760 €/mois | E | base | [lien](https://entreprises.selectra.info/telecom/guides/comparatifs/internet-pro) |
| WAN-TRANSIT | Connectivité WAN | Transit Internet 1 Gbit/s en DC, 2 opérateurs par DC (devis) | `2*DC` | 4 | 1 000,00 € | mois | 4 000 €/mois | E | base | [lien](https://entreprises.selectra.info/telecom/fibre-pro) |
| WAN-INTERDC | Connectivité WAN | Liaison inter-DC 1 Gbit/s, 2 chemins distincts (devis) | `2` | 2 | 1 000,00 € | mois | 2 000 €/mois | E | base | [lien](https://entreprises.selectra.info/telecom/fibre-pro) |
| WAN-FAS | Connectivité WAN | Frais de mise en service des liens dédiés (FTTO sièges, transit DC, inter-DC) | `2*SIEGE+2*DC+2` | 10 | 3 500,00 € | unique | 35 000 € | E | base | [lien](https://entreprises.selectra.info/telecom/fibre-pro) |
| SRV-HOTE | Serveurs | Dell PowerEdge R760 2 x 32 cœurs, 512 Go, SSD vSAN : cluster N+1 de 4 hôtes par DC | `HOTES_DC*DC` | 8 | 14 773,67 € | unique | 118 189 € | P | base | [lien](https://shop.bytestock.com/servers/dell/dell-rack-servers/16th-generation/dell-poweredge-r760) |
| SRV-VVF | Serveurs | VMware vSphere Foundation par cœur et par an (vSAN 0,25 TiB/cœur inclus) | `HOTES_DC*DC*COEURS_HOTE` | 512 | 120,45 € | an | 5 139 €/mois | E | base | [lien](https://redresscompliance.com/broadcom-vmware-vcf-vs-vvf-licensing-comparison-2026.html) |
| SRV-SAUV | Serveurs | Serveur de dépôt de sauvegarde 12 x 20 To, 1 par DC (annonce reconditionnée eBay relevée le 16/10/2026, à remplacer par un devis neuf) | `DC` | 2 | 20 423,12 € | unique | 40 846 € | E | base | eBay UK, annonce R760 2x32c 512 Go 12x20 To |
| SRV-VEEAM | Serveurs | Veeam Data Platform Foundation, pack de 10 instances par an | `ceil(VM/10)` | 30 | 1 382,94 € | an | 3 457 €/mois | P | base | [lien](https://stonefly.com/product/veeam-backup-replication-annual-subscription-per-universal-license-bundle/) |
| SRV-OBJ | Serveurs | Stockage objet immuable hors site, en To par mois (VM x 150 Go x 1,5 de rétention) | `ceil(VM*0.15*1.5)` | 68 | 10,50 € | mois | 714 €/mois | E | base | [lien](https://www.iloveblogs.blog/post/scaleway-object-storage-vs-aws-s3-eu-pricing) |
| NET-SW12 | Équipements réseau | Switch d'accès agence FR Aruba CX 6100 12G PoE (JL679A) | `AG_FR` | 498 | 975,99 € | unique | 486 043 € | P | base | [lien](https://bechtle.com/de-en/finder/product-family/hpe-aruba-cx-6100-switch--3399--f) (JL679A#ABB, prix net HT relevé le 28/10/2026, 854,99 € le 16/10/2026) |
| NET-SW48 | Équipements réseau | Switch d'accès 48G PoE Aruba CX 6100 (JL675A), sièges et agences internationales (1,25 port par utilisateur) | `SIEGE*ceil(U_SIEGE*PORTS_USER/48)+AG_INT*ceil(ceil(U_INT/AG_INT)*PORTS_USER/48)` | 166 | 2 191,00 € | unique | 363 706 € | P | base | [lien](https://bechtle.com/de-en/finder/product-family/hpe-aruba-cx-6100-switch--3399--f) (JL675A#ABB, prix net HT relevé le 28/10/2026, remplace pcnation.com en rupture à 3 691,89 $, recoupé aio.lv 2 005,78 € HT et lambda-tek.com 1 690,81 £ HT) |
| NET-CORE | Équipements réseau | Switch de cœur siège et ToR DC Aruba CX 8100 24XF4C (R9W94A), 2 par site | `2*SIEGE+2*DC` | 8 | 21 890,60 € | unique | 175 125 € | P | base | [lien](https://fleetnetwork.ca/products/r9w94a) |
| NET-AP | Équipements réseau | Borne Wi-Fi 6E Aruba AP-615 RW (R7J49A, modèle Europe) (1 pour 25 utilisateurs, 1 par agence FR) | `SIEGE*ceil(U_SIEGE/USERS_AP)+AG_FR+AG_INT*ceil(ceil(U_INT/AG_INT)/USERS_AP)` | 748 | 404,44 € | unique | 302 524 € | P | base | [lien](https://4networks.co.uk/r7j49a.html) (prix HT relevé le 28/10/2026, remplace la fiche CDW-G du modèle US non utilisable en France, recoupé galador.eu 413,95 à 427,18 € HT) |
| NET-AP-LIC | Équipements réseau | Licence Aruba Central Foundation par borne, 3 ans | `SIEGE*ceil(U_SIEGE/USERS_AP)+AG_FR+AG_INT*ceil(ceil(U_INT/AG_INT)/USERS_AP)` | 748 | 195,39 € | 36mois | 146 150 € | P | base | [lien](https://www.cdw.com/product/hpe-networking-central-foundation-subscription-license-3-years-1-acce/6483096) |
| NET-SW-LIC | Équipements réseau | Licence Aruba Central Foundation par switch, 3 ans (niveau CX 6100, à confirmer pour les CX 8100) | `AG_FR+SIEGE*ceil(U_SIEGE*PORTS_USER/48)+AG_INT*ceil(ceil(U_INT/AG_INT)*PORTS_USER/48)+2*SIEGE+2*DC` | 672 | 311,38 € | 36mois | 209 245 € | P | base | [lien](https://www.cdw.com/product/hpe-networking-central-foundation-subscription-license-3-years-1-swit/6489778) |
| SEC-FG-AG | Équipements de sécurité | FortiGate 40F-3G4G + 3 ans UTP et FortiCare Premium, agence FR (4G intégrée) | `AG_FR` | 498 | 1 739,79 € | 36mois | 866 417 € | P | base | [lien](https://datacenter360.ca/?p=21273) (vérifié le 28/10/2026 : même ordre de grandeur chez networkdevicesinc.com 1 849,17 $ et hummingbirdnetworks.com 1 901,61 $, prix catalogue 2 759,95 $) |
| SEC-FG-INT | Équipements de sécurité | FortiGate 70G + 3 ans UTP, agence internationale en HA (2 par agence, plus de 50 utilisateurs) | `2*AG_INT` | 60 | 1 778,01 € | 36mois | 106 680 € | P | base | [lien](https://datacenter360.ca/shop/network-security/firewall/bundle/fortinet-fortigate-70g-hardware-plus-3-year-forticare-premium-and-fortiguard-unified-threat-protection-utp-fg-70g-bdl-950-36/) |
| SEC-FG-SIEGE | Équipements de sécurité | FortiGate 200G + 3 ans UTP, siège en HA (2 par siège) | `2*SIEGE` | 4 | 14 757,57 € | 36mois | 59 030 € | P | base | [lien](https://datacenter360.ca/shop/network-security/firewall/bundle/fortinet-fortigate-200g-hardware-plus-3-year-forticare-premium-and-fortiguard-unified-threat-protection-utp-fg-200g-bdl-950-36/) |
| SEC-FG-DC | Équipements de sécurité | FortiGate 600F + 3 ans UTP, DC : une paire périmètre et hub SD-WAN, une paire segmentation interne (2 000 tunnels site à site par boîtier) | `4*DC` | 8 | 34 705,06 € | 36mois | 277 640 € | P | base | [lien](https://datacenter360.ca/shop/network-security/firewall/appliance/fortigate-600f-hardware-plus-3-year-forticare-premium-and-fortiguard-unified-threat-protection-utp-fg-600f-bdl-950-36) |
| SEC-FMG | Équipements de sécurité | FortiManager Cloud, lot de 100 équipements, 3 ans (pilotage central des FortiGate) | `ceil((AG_FR+2*AG_INT+2*SIEGE+4*DC)/100)` | 6 | 16 585,84 € | 36mois | 99 515 € | P | base | [lien](https://datacenter360.ca/?p=109729) |
| SEC-SASE | Équipements de sécurité | FortiSASE Standard 3 ans par utilisateur, nomades et partenaires nomades (ZTNA Secure Private Access inclus) | `NOMADES+PART_USERS` | 3300 | 134,46 € | 36mois | 443 717 € | P | base | [lien](https://datacenter360.ca/shop/zero-trust-access/sase/fortisase-standard-subscription-3-year-fortisase-standard-subscription-for-2000-9999-users-cloud-delivered-security-ips-web-dns-ssl-anti-malware-casb-with-secure-private-access-via-unified-a/) (vérifié le 28/10/2026 : 214,10 $ CA par utilisateur, palier 2 000 à 9 999, FC4-10-EMS05-547-02-36, recoupé firewalls.com 167,79 $) |
| SEC-ZPA | Équipements de sécurité | Zscaler Private Access par utilisateur et par an (estimation tierce, palier avancé, devis) | `NOMADES+PART_USERS` | 3300 | 200,75 € | an | 55 206 €/mois | E | zpa | [lien](https://underdefense.com/industry-pricings/zscaler-pricing-2026-ultimate-guide-for-security-products/) |
| SEC-WAF | Équipements de sécurité | F5 BIG-IP VE Advanced WAF 1 Gbit/s en abonnement mensuel, 2 par DC | `2*DC` | 4 | 1 250,89 € | mois | 5 004 €/mois | P | base | [lien](https://www.publicsector.shidirect.com/product/38383479/BIG-IP-Virtual-Edition-Advanced-Web-Application-Firewall) |
| SEC-PAM | Équipements de sécurité | WALLIX Bastion, comptes à privilèges (milieu de la fourchette 500 à 2 000 $ par utilisateur, devis) | `ADMINS` | 50 | 1 115,27 € | unique | 55 764 € | D | base | [lien](https://costbench.com/software/privileged-access-management/wallix-bastion/calculator/) |
| SEC-SIEM | Équipements de sécurité | SIEM Wazuh et supervision open source (licence 0 €, hébergés sur le compute) | `1` | 1 | 0,00 € | unique | 0 € | P | base | [lien](https://documentation.wazuh.com/current/quickstart.html) |
| SPR-FG | Équipements de sécurité | Stock de spare FortiGate 40F-3G4G, 2 % du parc agences (prix du bundle pris comme majorant) | `ceil(AG_FR*0.02)` | 10 | 1 739,79 € | 36mois | 17 398 € | E | base | [lien](https://datacenter360.ca/?p=21273) (vérifié le 28/10/2026, voir SEC-FG-AG) |
| SPR-SW12 | Équipements réseau | Stock de spare switch Aruba CX 6100 12G, 2 % du parc agences | `ceil(AG_FR*0.02)` | 10 | 975,99 € | unique | 9 760 € | E | base | [lien](https://bechtle.com/de-en/finder/product-family/hpe-aruba-cx-6100-switch--3399--f) (prix de NET-SW12 relevé le 28/10/2026) |
| SPR-AP | Équipements réseau | Stock de spare bornes Aruba AP-615, 2 % du parc | `ceil((SIEGE*ceil(U_SIEGE/USERS_AP)+AG_FR+AG_INT*ceil(ceil(U_INT/AG_INT)/USERS_AP))*0.02)` | 15 | 404,44 € | unique | 6 067 € | E | base | [lien](https://4networks.co.uk/r7j49a.html) (prix de NET-AP relevé le 28/10/2026) |
| SVC-DEPLOI | Services et autres (Etc.) | Déploiement sur site, ingénieur confirmé (1 j par agence FR, 2 j par agence internationale, 20 j par siège, 20 j par DC) | `AG_FR+2*AG_INT+20*SIEGE+20*DC` | 638 | 510,00 € | unique | 325 380 € | E | base | [lien](https://travail-industrie.com/simulateur-tjm/cybersecurite-reseaux/ingenieur-reseau/confirme) |
| SVC-PROJET | Services et autres (Etc.) | Architecture et pilotage du projet, expert (100 j) | `100` | 100 | 750,00 € | unique | 75 000 € | E | base | [lien](https://travail-industrie.com/simulateur-tjm/cybersecurite-reseaux/ingenieur-reseau/expert) |
| SVC-RUN | Services et autres (Etc.) | Infogérance NOC/SOC en heures ouvrées, 3 ETP x 21 j par mois | `3*21` | 63 | 510,00 € | mois | 32 130 €/mois | E | base | [lien](https://travail-industrie.com/simulateur-tjm/cybersecurite-reseaux/ingenieur-reseau/confirme) |
