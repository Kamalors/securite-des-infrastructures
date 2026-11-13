# Questions probables du jury et réponses modèles

Préparation de la séance de questions qui suit la soutenance. Rédigé le 28/10/2026 par l'agent « jury et vérification ».
Les chiffres viennent de `docs/CHIFFRAGE.md` (régénéré le 13/11/2026, il fait foi) et de `docs/OFFRE_TECHNIQUE.md` v1.0. Les sources des faits externes repris dans l'offre sont dans l'annexe B de `docs/OFFRE_TECHNIQUE.md`.

**Mode d'emploi.** Chaque question indique qui répond (rôle de `docs/ROLES_SOUTENANCE.md`), une réponse modèle de 2 à 4 phrases, le chiffre à citer et, s'il y a lieu, la faiblesse à reconnaître. Reconnaître une faiblesse avant que le jury la pointe vaut mieux que la défendre après.

**Trois règles pour toute l'équipe.**
1. Ne jamais inventer un chiffre. Dire plutôt : « c'est une hypothèse affichée (H…), le script recalcule le prix si vous nous donnez la vraie valeur ».
2. Distinguer ce qui est **prouvé** (maquette, calcul), **sourcé** (fiche, texte officiel) et **supposé** (hypothèse).
3. Trois affirmations ont été corrigées le 28/10 (détail : Q10, Q47 et Q48 ci-dessous) : Fortinet **n'est pas** « Leader » du Magic Quadrant SASE 2026 ; le **FortiGate 600F n'est plus commercialisé** depuis le 01/05/2026 ; l'accès privé de **FortiSASE Standard demande une licence sur les hubs FortiGate**. Ne plus les répéter.

## Les chiffres à connaître par cœur

| Sujet | Valeur |
|---|---|
| Abonnement mensuel tout compris, 36 mois | **221 424 € HT** (221,4 k€), sans investissement initial |
| Coût total sur 36 mois (abonnement) | **7,97 M€** (7 971 248 €) ; achat comptant : 7,50 M€ ; coût du lissage : 470 759 € |
| Par utilisateur / par site | **22,14 €** par utilisateur et par mois ; **418 €** par site et par mois |
| Composition | frais initiaux 4 219 196 € lissés en un loyer de 130 277 €/mois (location financière, 7 %/an supposé) + 91 147 €/mois de récurrent |
| Par poste (abonnement mensuel) | Sécurité 64 478 € ; Réseau 52 448 € ; Services 44 493 € ; WAN 41 273 € ; Serveurs 14 221 € ; Housing 4 511 € |
| Sensibilité | remise de 20 % : 195 337 €/mois (−26 087 €) ; ±1 000 nomades : ±4 152 €/mois ; une agence France de plus : +177 €/mois ; taux 5 % / 9 % : −3 823 € / +3 893 € |
| Variante Zscaler ZPA écartée | 276 630 €/mois, 9,96 M€ sur 36 mois : +1,99 M€ (+25 %), fourchette 1,24 à 3,31 M€ |
| Parc | 570 FortiGate (498 × 40F-3G4G, 60 × 70G, 4 × 200G, 8 × 600F) + 10 en spare ; 664 commutateurs d'accès + 8 Aruba CX 8100 ; 748 bornes AP-615 RW ; 8 Dell R760 + 2 dépôts de sauvegarde ; 512 cœurs VMware VVF ; 3 300 utilisateurs FortiSASE ; 4 F5 ; 50 comptes WALLIX |
| Hubs SD-WAN | ~1 100 tunnels requis (1 060 sites + 40 partenaires) pour 2 000 par boîtier |
| Maquette | 7 nœuds EVE-NG + 8 conteneurs ; **17/17** tests conformes (10 flux autorisés, 7 refus), 4 non exécutés (nomadisme) ; bascule WAN **3,8 s** (19 pings perdus × 0,2 s) |

---

## 1. Chef de projet

**Q1. « Résumez votre offre en une minute. Pourquoi vous ? »**
- Réponse : un SD-WAN Fortinet sur Internet relie les 530 sites à deux datacenters certifiés HDS en housing ; tout est refusé par défaut, avec deux paires de pare-feu par datacenter, un WAF F5, un bastion WALLIX et un SIEM Wazuh ; nomades et partenaires passent en Zero Trust par FortiSASE. Le tout en abonnement, sans avance, comme le demande la DSI. Chaque choix est justifié face à une alternative et les principes sont éprouvés sur maquette.
- Chiffre : 221,4 k€ HT/mois, 22,14 €/utilisateur/mois, 17/17 tests.
- Faiblesse : prix publics et estimations, à confirmer par devis.

**Q2. « D'où sortent vos hypothèses (3 000 nomades, 300 VM, 50 comptes) ? Et si elles sont fausses ? »**
- Réponse : le PDF ne donne ni débits, ni nombre de VM, ni nombre de nomades. Nous affichons nos hypothèses (H1 à H12), chacune avec ce qu'elle fait varier. Le chiffrage est un script : une valeur corrigée recalcule toutes les lignes en une commande.
- Chiffre : 1 000 nomades de plus ou de moins = ±4 152 €/mois (±1,9 %).
- Faiblesse : H8 (300 VM de 2 vCPU, 8 Go, 150 Go) pèse sur les serveurs, le stockage vSAN et la sauvegarde ; c'est la plus fragile.

**Q3. « Qu'est-ce qui n'est pas dans votre prix ? »**
- Réponse : c'est listé (offre § 16.4) : raccordements opérateurs en datacenter, logistique et douanes, extension vSAN, surcoût d'un hébergeur HDS, SOC 24/7, protection DDoS, fournisseur d'identité et MFA (supposés existants), optiques et câbles, étage de distribution des sièges, onduleurs d'agence, licences des systèmes et applications des VM, renouvellements après 36 mois, licence d'accès privé FortiSASE des 4 hubs (Q47), protection des postes de travail (EDR, Q36).
- Faiblesse : les postes qui risquent le plus de faire bouger le prix sont la distribution des sièges, l'extension vSAN, le surcoût HDS et la licence des hubs.

**Q4. « Le client n'a pas demandé de maquette. Pourquoi en faire une ? »**
- Réponse : le PDF demande de justifier nos choix. La maquette transforme des affirmations (refus par défaut, segmentation, bascule) en tests rejouables, avec des preuves horodatées. Elle a aussi révélé et fait corriger trois défauts, dont l'effet MOBIKE qui masquait la bascule (Q13) : c'est exactement à cela que sert une recette.
- Chiffre : 17/17, bascule 3,8 s.
- Faiblesse : elle prouve des principes, pas les produits (Q11).

**Q5. « Quels sont les trois risques majeurs de votre projet ? »**
- Réponse : (1) l'approvisionnement et le cycle de vie du matériel : 570 FortiGate à livrer, et le modèle de datacenter retenu (600F) n'est plus commercialisé, il faut coter son successeur ; (2) l'éligibilité fibre des agences et les opérateurs des 30 pays inconnus (H3) ; (3) la dépendance à Fortinet, que DORA demande de maîtriser. S'y ajoute un risque de cadrage : les RPO/RTO ne sont pas fixés.
- Chiffre : 570 boîtiers, 9 mois de déploiement.

**Q6. « Comment êtes-vous sûrs de couvrir tout le cahier des charges ? »**
- Réponse : `docs/EXIGENCES.md` reprend chaque exigence du PDF (V1 à V4, E01 à E17) et la relie à une solution, une section de l'offre, une preuve de maquette, une limite et un poste de coût. Les trois volets notés p.3 (modèles justifiés, HLD, coûts en abonnement) ont chacun leur section.

---

## 2. Architecte WAN (et maquette)

**Q7. « Pourquoi pas MPLS ? »**
- Réponse : le MPLS est un réseau privé d'opérateur : plus cher, long à livrer, et il ne chiffre pas les données. Notre WAN repose sur des accès Internet professionnels souscrits au mois, avec des tunnels IPsec chiffrés et un SD-WAN qui choisit le meilleur accès par application. Le MPLS reste une option pour les sièges si un engagement de bout en bout était exigé.
- Chiffre : tout le WAN (sites, transits et liaisons des datacenters) coûte 41 273 €/mois, soit ~78 € par site ; une agence France : 48,98 €/mois (fibre 34,99 € + SIM 4G 13,99 €).
- Faiblesse : pas de garantie de bout en bout sur Internet. Nous n'avons pas de prix MPLS sourcé : ne pas avancer de multiplicateur chiffré.

**Q8. « Que se passe-t-il si les deux accès d'une agence tombent ? »**
- Réponse : fibre et 4G passent par deux réseaux différents, une double panne vient surtout d'une coupure électrique ou d'une panne du boîtier. Boîtier en panne : remplacement depuis le stock de 10 spares, préconfiguré. Coupure totale : les collaborateurs équipés de l'agent FortiClient peuvent travailler comme des nomades via FortiSASE, par exemple sur le partage de connexion d'un téléphone.
- Faiblesse : onduleurs d'agence non inclus ; seuls les utilisateurs licenciés FortiSASE (3 000 nomades) ont ce secours.

**Q9. « Comment dimensionnez-vous les hubs ? »**
- Réponse : chaque site monte un tunnel par accès vers chaque datacenter : 498 × 2 + 30 × 2 + 2 × 3 ≈ 1 060 tunnels par hub, plus ~40 partenaires site à site, soit ~1 100. La fiche constructeur annonce 2 000 tunnels site à site par boîtier ; en haute disponibilité actif/passif, c'est la capacité de la paire.
- Chiffre : ~1 100 / 2 000, environ 45 % de marge.
- Faiblesse : chiffre de fiche relayé par des revendeurs, et le 600F n'est plus commercialisé (Q10).

**Q10. « Le FortiGate 600F est-il encore vendu ? »** *(question dangereuse)*
- Réponse : non, plus en commande neuve. D'après les bases de cycle de vie, sa fin de commande date du 1er mai 2026 et son support court jusqu'au 1er mai 2031. Nous le remplaçons par un modèle de la génération G de capacité équivalente (FortiGate 700G : 2 000 tunnels site à site d'après les fiches revendeurs ; Fortinet doit confirmer le successeur officiel), recoté au devis. L'architecture ne change pas.
- Chiffre : 8 boîtiers, 277 640 € de frais initiaux au prix du 600F.
- Faiblesse : notre chiffrage repose sur un modèle en fin de vie ; à reconnaître sans détour.

**Q11. « Votre maquette prouve-t-elle vos produits ? »** *(question dangereuse)*
- Réponse : non, et nous l'écrivons. Elle prouve les principes : refus par défaut, segmentation, tunnels chiffrés en double hub, bascule d'opérateur, administration par bastion, journalisation. Elle utilise Linux (nftables, strongSwan, FRR), pas des FortiGate. Elle ne prouve ni le SD-WAN par application, ni la haute disponibilité, ni le ZTNA et le MFA, ni la capacité pour 10 000 utilisateurs ; le profil international et le second datacenter complet ne sont pas déployés.
- Chiffre : 17/17 (10 autorisés, 7 refus), 4 tests non exécutés (F07, F08, N07, N09).
- Désamorçage : proposer au client une preuve de concept sur FortiGate comme première étape du projet.

**Q12. « D'où vient le chiffre de 3,8 s ? Et si la panne est en amont, chez l'opérateur ? »**
- Réponse : un ping toutes les 0,2 s, 125 envoyés, 19 perdus : 3,8 s d'interruption. C'est le temps de détection d'OSPF dans les tunnels (un message par seconde, voisin déclaré mort après 4 s), pas une performance de produit. Comme la détection passe par des messages envoyés dans le tunnel, elle voit aussi une panne en amont (lien local allumé mais trafic perdu), pas seulement un câble débranché. En production, les sondes de qualité du SD-WAN FortiGate jouent ce rôle et se règlent.
- Chiffre : 3,8 s (3,2 à 3,8 s selon les passages, `docs/MAQUETTE.md`).
- Faiblesse : la coupure a été simulée en éteignant l'interface ; une seule série de mesures publiée.

**Q13. « Racontez-nous l'histoire de MOBIKE. »**
- Réponse : MOBIKE (RFC 4555) permet à IKEv2 de déplacer une association de sécurité, IKE et IPsec, vers une autre adresse sans la renégocier. Dans la maquette, quand on coupait l'opérateur A, le tunnel « A » déménageait tout seul sur l'accès B : il restait vivant, OSPF ne voyait rien et la bascule devenait invisible. Corrections : MOBIKE désactivé (chaque tunnel reste attaché à son opérateur) et filtrage anti-usurpation BCP 38 (RFC 2827) chez les opérateurs simulés, qui refuse un paquet portant l'adresse de l'autre opérateur.
- Leçon : avec plusieurs opérateurs, il faut maîtriser quel tunnel emprunte quel lien ; c'est le sujet de la RFC 3704 (filtrage en multi-opérateurs).

**Q14. « Pourquoi ne pas avoir mis de FortiGate virtuels dans la maquette ? »**
- Réponse : les versions d'évaluation sont bridées et l'édition gratuite d'EVE-NG est limitée à 7 nœuds par instance. Nous avons choisi des briques libres, entièrement scriptées : la maquette se reconstruit et se rejoue en une commande. La politique (zones, flux, ports) est transposable telle quelle sur FortiGate.
- Faiblesse : l'écart entre la maquette et le produit demeure (Q11).

**Q15. « Votre test N02, "Internet vers bastion", prouve-t-il quelque chose ? »**
- Réponse : peu, et nous l'avons écrit : l'adresse du bastion est privée et n'est pas routée depuis Internet, le paquet n'atteint même pas le pare-feu, donc aucune trace au journal. La preuve utile du nord/sud est N01 : le port de la base sur l'adresse publique du datacenter, refusé et journalisé. Un test plus probant viserait un port non publié de l'adresse publique.

**Q16. « De la fibre FTTH mutualisée pour une mutuelle ? Quelle garantie ? »**
- Réponse : fibre professionnelle avec garantie de temps d'intervention de 8 h, plus une SIM 4G sur un autre réseau dans le FortiGate. Une agence de 8 personnes tolère une courte coupure ; la fibre dédiée (FTTO) est réservée aux sièges et peut être proposée en option pour des agences critiques.
- Chiffre : 34,99 € + 13,99 € par mois et par agence.
- Faiblesse : FTTH sans débit garanti ; garantie de temps d'intervention, pas de rétablissement.

**Q17. « Et les 30 agences internationales : quels opérateurs, quel prix ? »**
- Réponse : les pays ne sont pas connus (H3). Nous avons pris un tarif français de référence, 96 €/mois par accès, deux accès par agence ; en pratique, opérateurs locaux ou agrégateur international, cotés pays par pays. Deux FortiGate 70G en haute disponibilité, car ~67 utilisateurs et loin du stock de spare.
- Chiffre : 5 760 €/mois pour 60 accès.
- Faiblesse : c'est la ligne WAN la plus incertaine, et les transferts de données hors UE sont à encadrer (Q45).

---

## 3. Architecte datacenter

**Q18. « Deux datacenters en région parisienne : et la crue de la Seine ? »**
- Réponse : les deux sites sont dans des domaines de panne distincts (bâtiments, alimentations, opérateurs), choisis proches pour la réplication, la densité d'opérateurs et la proximité des sièges. Un sinistre régional est un risque résiduel reconnu : nous retiendrons deux sites hors zone inondable, la copie immuable est hors des deux datacenters, et deux régions éloignées sont proposées en option si l'analyse de risques l'exige.
- Faiblesse : un sinistre régional majeur peut toucher les deux sites. Exiger que la copie immuable soit stockée hors d'Île-de-France.

**Q19. « Réplication synchrone ou asynchrone ? Quelle distance ? »**
- Réponse : asynchrone pour les bases (actif/passif) : pas de contrainte forte de distance ni de pénalité sur les écritures, mais une perte possible des dernières secondes ou minutes. Le synchrone (aucune perte) impose une faible latence, donc des sites très proches, et ralentit les écritures. Le choix final découle du RPO.

**Q20. « Quels RPO et RTO ? »** *(question dangereuse)*
- Réponse : le client ne les a pas donnés (H4) ; c'est une décision métier, que nous ne pouvons pas fixer seuls. Nous proposons de les arrêter en atelier par classe d'application, par exemple : critique (réplication asynchrone vers l'autre datacenter, perte de quelques minutes, reprise en quelques heures) ; standard (sauvegarde Veeam quotidienne, reprise dans la journée). Ces valeurs dimensionnent le datacenter de secours.
- Faiblesse : sans RPO/RTO, deux datacenters ne font pas un plan de reprise. Les valeurs ci-dessus sont des propositions, à présenter comme telles.

**Q21. « Si un datacenter brûle, l'autre porte-t-il toute la charge ? »** *(question dangereuse)*
- Réponse : non, pas la totalité, et c'est écrit (offre § 6.1). Les 300 VM demandent 2,4 To de mémoire ; un datacenter en a 2 To (1,5 To en gardant un serveur de marge). Le site restant redémarre le périmètre critique ; tout reprendre demanderait des serveurs supplémentaires, non chiffrés.
- Chiffre : 2,4 To requis, 2 To disponibles.

**Q22. « Le stockage vSAN de 64 TiB "inclus" suffit-il ? »**
- Réponse : le droit VVF est de 0,25 TiB par cœur, soit 64 TiB de capacité **brute** par datacenter. Avec notre hypothèse (300 VM × 150 Go = 45 To, soit ~41 TiB, portés par chaque site pour sa production et la réplique de l'autre), la protection RAID 5 (×1,33 à ×1,5) et la réserve d'espace libre, il faut de l'ordre de 70 à 80 TiB bruts. Le droit inclus sera donc probablement dépassé : extension vSAN à prévoir (listée en non inclus).
- Faiblesse : la formule « 64 TiB inclus, aucune baie à acheter » est trop optimiste ; les disques des R760 doivent aussi fournir cette capacité (~16 TiB par serveur au minimum).

**Q23. « Pourquoi VMware après le rachat par Broadcom ? »**
- Réponse : maturité, compétences disponibles, compatibilité avec les éditeurs, et vSAN inclus. La licence VVF est estimée à ~135 $ par cœur et par an (estimation d'un cabinet, Broadcom ne publie pas de grille), soit 5 139 €/mois pour 512 cœurs, 2,3 % de l'abonnement. Les risques sont connus (hausses au renouvellement, minimum d'achat relevé à 72 cœurs en 2025, pénalité de renouvellement tardif) : prix figé 36 mois et sortie vers Proxmox VE préparée (Veeam restaure des VM VMware vers Proxmox).
- Faiblesse : après 36 mois, la dépendance à Broadcom est réelle.

**Q24. « La mutuelle est-elle obligée de recourir à un hébergeur HDS ? »** *(question dangereuse)*
- Réponse : la certification HDS vise ceux qui hébergent des données de santé **pour le compte d'un tiers** (article L.1111-8 du code de la santé publique) ; un responsable qui héberge lui-même n'y est pas soumis, et l'ANS indique que les organismes complémentaires ne sont en principe pas visés pour le remboursement des frais de santé. Mais une grande mutuelle a souvent des activités de soins ou de prévention (centres de santé, optique, dentaire) dont les données relèvent d'HDS, et c'est la norme du marché. Nous l'exigeons donc par prudence : hébergeur (activité 1), infogérant (activité 5), stockage de sauvegarde externalisé (activité 6), hébergement physique dans l'Espace économique européen (référentiel v2).
- Faiblesse : l'assujettissement exact est à confirmer par le juridique ou le DPO de la mutuelle ; le surcoût HDS n'est pas chiffré.

**Q25. « 470 € la baie par mois, c'est réaliste pour un datacenter Tier III certifié HDS ? »**
- Réponse : c'est un prix public d'hébergeur parisien dont la certification HDS n'est pas établie : un plancher, et nous l'écrivons. Le surcoût d'un hébergeur certifié est listé en non inclus.
- Chiffre : le housing pèse 4 511 €/mois, 2 % de l'abonnement : même doublé, l'impact reste d'environ 2 %.

**Q26. « Pourquoi pas le cloud public ? »**
- Réponse : le PDF demande une solution de housing. Le cloud public des grands fournisseurs américains pose la question du Cloud Act (Q44), avec des coûts variables et une réversibilité plus difficile. Des clouds français qualifiés et certifiés HDS restent une option pour certaines charges.

**Q27. « Après un rançongiciel, comment restaurez-vous ? »**
- Réponse : règle 3-2-1 : un dépôt Veeam dans l'autre datacenter et une copie immuable chez un fournisseur de stockage objet, non modifiable ni supprimable pendant sa rétention, même avec des droits d'administrateur. On restaure dans un environnement assaini, après avoir identifié le point d'entrée, et les restaurations sont testées régulièrement.
- Chiffre : 68 To immuables, 714 €/mois.
- Faiblesse : la durée de restauration des 300 VM n'est pas mesurée ; le fournisseur de stockage objet doit lui aussi être certifié HDS.

---

## 4. Responsable sécurité des flux

**Q28. « Un partenaire ne sait faire que du FTP. Comment faites-vous ? »**
- Réponse : par défaut, SFTP (clé, liste d'adresses, répertoire cloisonné). S'il ne sait faire que du FTP : exception temporaire, datée et contractualisée, sur une passerelle isolée en DMZ, avec compte dédié, adresse source autorisée, fichiers analysés et journalisation. Mieux : faire passer ce FTP dans un tunnel IPsec site à site, qui chiffre identifiants et données ; ou FTPS si son logiciel le permet.
- Faiblesse : du FTP en clair sur Internet expose identifiants et fichiers ; pour des données de santé, l'exception ne doit pas durer.

**Q29. « Votre serveur web est compromis. Que se passe-t-il ? »**
- Réponse : il est en DMZ ; il n'atteint l'application que sur son port (8443, F03) et jamais la base (N03, refusé et journalisé) ; aucune administration possible hors bastion ; l'alerte remonte au SIEM. L'attaquant doit encore franchir la paire de pare-feu interne.
- Faiblesse : si l'application elle-même est vulnérable, la base reste joignable à travers elle : le WAF et le durcissement applicatif restent nécessaires.

**Q30. « Comment empêchez-vous un rançongiciel de se propager ? »**
- Réponse : segmentation par zones et refus par défaut (pas de partage de fichiers ni de bureau à distance entre zones) ; administration uniquement par le bastion avec MFA, ce qui limite l'usage d'identifiants volés ; nomades et partenaires sans accès au réseau entier (ZTNA) ; copie immuable pour reconstruire ; détection par le SIEM Wazuh.
- Faiblesse : le SOC ne travaille qu'en heures ouvrées (3 ETP) ; une attaque lancée la nuit ou le week-end sera vue tard. SOC 24/7 et protection des postes (EDR) non chiffrés.

**Q31. « F5 a été piraté en 2025. Pourquoi le choisir ? »**
- Réponse : en octobre 2025, F5 a révélé qu'un acteur étatique avait dérobé du code source BIG-IP et des informations sur des failles non publiées ; l'agence américaine CISA a émis une directive d'urgence (ED 26-01). Nos parades : interfaces d'administration jamais exposées (bastion seulement), correctifs appliqués, WAF placé derrière le pare-feu de périmètre (deux éditeurs à franchir). Alternatives : FortiWeb (dépendance accrue à Fortinet) ou WAF en cloud (déchiffrement hors du périmètre HDS).
- Faiblesse : le risque éditeur est réel ; tout grand éditeur de sécurité, Fortinet compris, a connu des failles critiques exploitées.

**Q32. « Deux paires de pare-feu du même éditeur : est-ce vraiment de la défense en profondeur ? »**
- Réponse : il y a séparation physique et de rôle (une erreur sur le périmètre n'ouvre pas l'intérieur), mais pas de diversité de code : une faille de FortiOS toucherait les deux paires. La diversité est ailleurs : WAF F5 entre les deux, bastion WALLIX, SIEM indépendant. Si le client veut aussi diversifier les pare-feu, la paire interne peut venir d'un autre éditeur (par exemple Stormshield, éditeur français), au prix d'une seconde console.

**Q33. « Déchiffrez-vous le trafic ? Et les données de santé ? »**
- Réponse : pour l'accès Internet des agences et des nomades, inspection TLS avec exclusion des catégories sensibles (santé, banque). Les flux vers les applications internes restent chiffrés de bout en bout. Le WAF déchiffre le trafic des assurés uniquement dans nos datacenters HDS.
- Faiblesse : l'inspection TLS doit être encadrée (information des salariés, charte, CNIL).

**Q34. « Et les attaques DDoS ? »**
- Réponse : la protection volumétrique se souscrit chez les opérateurs de transit (option non chiffrée) ; le WAF limite les attaques applicatives (limitation de débit) et les deux datacenters servent en actif/actif.
- Faiblesse : non chiffré ; pour un portail d'assurés, c'est un manque à combler au devis.

**Q35. « Comment l'infogérant administre-t-il ? Et si son poste est compromis ? »**
- Réponse : FortiSASE (ZTNA, MFA, contrôle du poste) vers le bastion WALLIX uniquement ; comptes nominatifs, approbation, durée limitée, sessions enregistrées, mots de passe gardés dans le coffre du bastion. Un poste compromis n'atteint que le bastion, et chaque session y est approuvée et enregistrée.
- Chiffre : 50 comptes à privilèges.
- Faiblesse : MFA et enregistrement de session non représentés dans la maquette.

**Q36. « Et les postes de travail : antivirus, EDR ? »**
- Réponse : l'offre traite le réseau, les datacenters et les accès ; la protection des 10 000 postes est supposée existante. C'est pourtant une brique clé contre le rançongiciel : nous recommandons un EDR, à chiffrer.
- Faiblesse : non chiffré, seulement listé dans les non inclus (offre § 16.4) ; à reconnaître.

---

## 5. Architecte agences et exploitation (et risques)

**Q37. « Comment déployez-vous 498 agences ? »**
- Réponse : pilote sur 2 sièges et 10 agences (M2 à M3), puis ~25 agences par semaine de M3 à M8. Chaque agence reçoit des équipements préconfigurés depuis le modèle de son profil (FortiManager, Aruba Central) : sur place, on branche. Une journée d'ingénieur par agence, en coexistence avec l'existant.
- Chiffre : 638 jours de déploiement (325 380 €), 9 mois au total.
- Faiblesse : dépend des délais de livraison du matériel et de la fibre.

**Q38. « Vos 53 commutateurs par siège se raccordent à un cœur CX 8100 de 24 ports : comment ? »** *(question dangereuse)*
- Réponse : en l'état, ils ne se raccordent pas, et nous l'avons écrit (offre § 10.2). En double attachement, 53 commutateurs demandent 53 ports par cœur, un CX 8100 24XF4C n'en a que 24. Il faut un étage de distribution (commutateurs d'agrégation par bâtiment ou par étage) ou un cœur plus dense, à dimensionner avec le plan de câblage ; ce n'est pas chiffré.
- Ordre de grandeur, calculé par nos soins et à valider : 3 paires d'agrégation de même modèle par siège, soit 12 commutateurs, ~263 k€ au prix unitaire du chiffrage, environ 8 k€/mois en location (+3,7 %), hors optiques.

**Q39. « Comment séparez-vous les invités et les salariés en agence ? »**
- Réponse : deux réseaux Wi-Fi : entreprise en 802.1X via le fournisseur d'identité, invités isolés avec Internet seulement ; réseaux séparés pour utilisateurs, administration, téléphonie et imprimantes, filtrés par le FortiGate. En maquette : invités vers Internet autorisé (F13), vers le réseau interne refusé (N05).
- Chiffre : 748 bornes, une pour 25 utilisateurs.
- Faiblesse : une seule borne par agence France, donc pas de redondance radio ; pas de Wi-Fi en maquette.

**Q40. « Wazuh tient-il la charge de 570 pare-feu ? Qui regarde les alertes ? »**
- Réponse : Wazuh est gratuit, hébergé dans nos datacenters HDS, sans facturation au volume. Son dimensionnement dépend du volume de journaux, non communiqué (H10). Les alertes sont traitées par le NOC/SOC en heures ouvrées ; hors heures, astreinte ou SOC 24/7 en option.
- Faiblesse : ressources du SIEM et stockage des journaux à prendre sur le compute, non isolés dans le chiffrage ; l'outil demande des compétences.

**Q41. « Fortinet publie beaucoup de failles critiques. Comment patchez-vous 570 boîtiers ? »**
- Réponse : Gartner le relève dans son Magic Quadrant SASE 2026 (correctifs fréquents, base installée très ciblée). Nos parades : aucune interface d'administration ni VPN SSL exposé sur Internet (nomades via FortiSASE) ; mises à jour par vagues depuis FortiManager (pilote, puis généralisation) ; veille sur les avis de sécurité Fortinet et sur le catalogue des failles exploitées de la CISA pour prioriser.
- Faiblesse : c'est une charge d'exploitation réelle et récurrente.

**Q42. « DORA s'applique-t-il à la mutuelle ? »**
- Réponse : très probablement. DORA (règlement UE 2022/2554) s'applique depuis le 17 janvier 2025 aux entreprises d'assurance, sauf aux plus petites, exclues de Solvabilité II pour leur taille (article 2.3 b, renvoyant à l'article 4 de la directive 2009/138/CE). Une grande mutuelle santé dépasse ces seuils. Conséquences : registre des prestataires informatiques (article 28.3), clauses contractuelles, stratégies de sortie pour les services qui soutiennent des fonctions critiques (article 28.8), tests de résilience, notification des incidents majeurs.
- Faiblesse : confirmation à obtenir de la conformité de la mutuelle.

**Q43. « Que contient votre plan de réversibilité ? »**
- Réponse : inventaire des services et des données détenus par chaque prestataire, formats d'export (configurations, journaux, sauvegardes), protocoles standard (IPsec, SAML/OIDC, syslog), durée d'assistance à la sortie dans les contrats, solution de repli identifiée par brique (ex. Proxmox pour VMware, autre SASE pour FortiSASE), et un test de sortie partiel.
- Faiblesse : le plan est annoncé, pas encore rédigé.

**Q44. « Cloud Act : vos données sont-elles à l'abri ? »**
- Réponse : le Cloud Act oblige un fournisseur américain à remettre les données qu'il détient, même stockées hors des États-Unis. Exposés : les services en cloud de sociétés américaines, FortiSASE (trafic des nomades), FortiManager Cloud et Aruba Central (configuration, supervision), et le fournisseur d'identité s'il est américain. Non exposés directement : les équipements installés dans nos datacenters, dont la mutuelle détient les données, le bastion WALLIX (français) et Wazuh (hébergé chez nous). Parades : points de présence européens, flux vers les applications internes chiffrés de bout en bout, FortiManager installable sur site, offre « Sovereign SASE » de Fortinet à étudier.
- Faiblesse : aucune alternative qualifiée SecNumCloud pour le SASE dans l'offre.

**Q45. « RGPD : des agences hors UE accèdent à des données de santé ? »**
- Réponse : oui, c'est un transfert à encadrer : décision d'adéquation ou clauses contractuelles types avec analyse du transfert, droits limités par application, analyse d'impact (AIPD) pour le traitement de données de santé (article 9).
- Faiblesse : les pays sont inconnus (H3), l'analyse reste à faire.

**Q46. « Le serveur de votre maquette a été piraté. Vos preuves sont-elles fiables ? »** *(question dangereuse, rôle 5, avec le rôle 2 en appui)*
- Réponse : le serveur loué pour la maquette a été compromis avant que la maquette existe : implant découvert le 16/10, début probable le 01/10. Il a été réinstallé le 16/10 et durci (SSH par clé seulement, interface d'administration fermée à Internet, pare-feu) ; la maquette et la recette ont été faites ensuite. Les empreintes SHA-256 garantissent que les fichiers de preuve n'ont pas changé depuis leur production, pas que l'hôte était sain : la meilleure preuve reste de rejouer la recette devant vous. Nous en tirons nos choix : bastion, MFA, journaux envoyés hors des équipements.
- Faiblesse : le point d'entrée n'a pas été confirmé (réinstallation sans collecte des preuves). Dire « le plus probable : SSH avec mot de passe », pas « un mot de passe faible » comme une certitude.

---

## 6. Expert Zero Trust

**Q47. « Le ZTNA est-il vraiment inclus dans FortiSASE Standard ? »** *(question dangereuse)*
- Réponse : la souscription utilisateur Standard comprend l'accès privé, avec l'agent ou sans agent par le navigateur (intitulé de la référence chez les revendeurs). Mais le guide de commande Fortinet de septembre 2026 précise que l'accès privé à travers un FortiGate demande une licence par FortiGate hub, chaque membre d'un cluster HA compris, incluse d'office seulement dans les éditions Advanced et Comprehensive. Il faut donc ajouter 4 licences sur nos hubs (2 paires de périmètre) ou passer en Advanced : à chiffrer au devis.
- Chiffre : d'après les prix revendeurs relevés, de ~30 k€ à ~410 k€ sur 36 mois pour les 4 hubs ; l'écart avec ZPA reste d'au moins 1,5 M€.
- Faiblesse : notre « déjà payé, inclus » était trop rapide.

**Q48. « Fortinet est-il Leader du Magic Quadrant SASE 2026 ? »** *(question dangereuse)*
- Réponse : non, et nous corrigeons notre support : dans le Magic Quadrant Gartner des plateformes SASE 2026 (publié le 28 juillet 2026), Fortinet est « Challenger » ; il était « Leader » en 2025. Les Leaders 2026 sont Netskope, Cato Networks, Palo Alto Networks et Zscaler. Fortinet est en revanche Leader du Magic Quadrant 2026 des pare-feu (« Hybrid Mesh Firewall »), ce qui correspond à l'essentiel de notre usage : 570 pare-feu de sites et de datacenters.
- Faiblesse : Gartner reproche à Fortinet des évolutions tardives, une expérience client moyenne et des correctifs fréquents (Q41). Notre alternative Cato, elle, est Leader.

**Q49. « Quelle différence entre un VPN et un ZTNA ? »**
- Réponse : un VPN place le poste « dans le réseau » : une fois connecté, il voit de nombreux serveurs, et un poste compromis devient une porte d'entrée. Le ZTNA n'ouvre que les applications autorisées pour cet utilisateur, après vérification de son identité (MFA) et de l'état de son poste, à chaque session, avec révocation immédiate.
- Faiblesse : non démontré en maquette (F07, F08, N07, N09 non exécutés).

**Q50. « Tout repose sur Fortinet. Et la dépendance ? »**
- Réponse : risque assumé et encadré. Fortinet porte pare-feu, SD-WAN et SASE ; mais l'identité et le MFA (fournisseur du client), le réseau local et le Wi-Fi (Aruba), le WAF (F5), le bastion (WALLIX) et le SIEM (Wazuh) sont ailleurs. Protocoles standard, engagement de 36 mois aligné sur la location, plan de réversibilité exigé par DORA.
- Faiblesse : une sortie de Fortinet resterait un projet lourd (570 boîtiers) ; ne pas prétendre le contraire.

**Q51. « Et si FortiSASE tombe en panne ? »**
- Réponse : les sites n'en dépendent pas (tunnels directs vers les datacenters) ; seuls les nomades et partenaires nomades sont touchés. Secours : bascule vers un autre point de présence européen, et à défaut un accès de repli documenté (tunnel IPsec du poste directement vers les hubs, limité aux applications critiques).
- Faiblesse : secours ni chiffré ni testé ; engagement de disponibilité de FortiSASE à obtenir dans le contrat.

**Q52. « Un partenaire n'a pas de poste géré. Comment le contrôlez-vous ? Comment le révoquez-vous ? »**
- Réponse : portail sans agent, par navigateur, documenté par Fortinet pour les sous-traitants ; comptes nominatifs, MFA, durée de vie limitée, revue trimestrielle, révocation immédiate dans le fournisseur d'identité. Sans agent, on ne contrôle pas l'état du poste : on limite ces accès aux applications web les moins sensibles.
- Faiblesse : la révocation (N09) n'est pas testée en maquette.

**Q53. « Quel MFA ? Résiste-t-il à l'hameçonnage ? »**
- Réponse : celui du fournisseur d'identité de la mutuelle (H12, par exemple Entra ID). Pour les administrateurs et les infogérants, nous recommandons un MFA résistant à l'hameçonnage (clés FIDO2). Si le client n'a pas de fournisseur d'identité, FortiToken ou FortiAuthenticator sont à chiffrer.
- Faiblesse : supposé existant, non chiffré.

**Q54. « Et si les 10 000 salariés passent en télétravail ? »**
- Réponse : les licences sont par utilisateur : chaque tranche de 1 000 nomades ajoute 4 152 €/mois ; passer de 3 000 à 10 000 nomades coûterait ~29 k€/mois de plus (+13 %). FortiSASE est un service cloud qui absorbe la charge côté utilisateurs ; côté datacenters, les transits (2 × 1 Gbit/s par site) seraient à revoir.

---

## 7. Responsable financier

**Q55. « D'où viennent vos prix ? »**
- Réponse : chaque ligne de `docs/CHIFFRAGE.md` a une source et une nature : prix public relevé chez un revendeur ou un comparateur (P), estimation sourcée (E) ou devis obligatoire (D). Devises converties au taux BCE du 15/10/2026, calcul par script, quantités tirées de règles écrites.
- Faiblesse : revendeurs étrangers (Canada, États-Unis, Royaume-Uni), pas de devis ; certains prix sont des planchers (housing) ou des estimations tierces (VMware, WALLIX, ZPA).

**Q56. « Combien coûte votre abonnement par rapport à un achat ? »**
- Réponse : les 4,22 M€ de frais initiaux sont financés par une location financière sur 36 mois à 7 % par an (hypothèse à faire confirmer par un bailleur), soit un loyer de 130 277 €/mois, auquel s'ajoutent 91 147 €/mois de services récurrents. Le lissage coûte 470 759 € sur 36 mois (7,97 M€ contre 7,50 M€ à l'achat) : c'est le prix de l'absence d'avance.
- Chiffre : taux de 5 % ou 9 % : −3 823 € ou +3 893 €/mois.
- Faiblesse : un bailleur finance parfois moins bien les licences que le matériel.

**Q57. « Que se passe-t-il au bout de 36 mois ? »**
- Réponse : les renouvellements ne sont pas inclus. Le matériel loué est racheté à sa valeur résiduelle ou renouvelé ; les licences (UTP, FortiSASE, VMware, Aruba Central) sont à renouveler, avec un risque de hausse, surtout chez VMware. Nous recommandons de négocier dès la signature des prix de renouvellement plafonnés.
- Faiblesse : pas de coût total sur 5 ans.

**Q58. « 418 € par site et par mois : c'est cher ou pas ? »**
- Réponse : c'est un prix tout compris : WAN, sécurité, réseau local et Wi-Fi, datacenters, déploiement et infogérance. Rapporté à l'utilisateur : 22,14 € par mois. Le coût marginal d'une agence France est de 177 €/mois.
- Faiblesse : pas de référence de marché sourcée pour comparer ; ne pas en inventer.

**Q59. « Comment chiffrez-vous l'économie sur Zscaler sans prix public ? »**
- Réponse : par une fourchette d'estimations tierces, de 140 à 375 $ par utilisateur et par an, soit 1,24 à 3,31 M€ sur 36 mois ; au palier central (225 $), 1,99 M€, soit +25 % sur le coût total. Ce montant doit être diminué de la licence d'accès privé des hubs FortiSASE (Q47) : l'économie nette est de l'ordre de 1,6 à 2,0 M€.

**Q60. « Pourquoi la sécurité est-elle le poste le plus lourd ? Et la remise ? »**
- Réponse : 64 478 €/mois : 570 FortiGate avec 3 ans de protection (≈1,33 M€ de frais initiaux), FortiSASE pour 3 300 utilisateurs (443 717 €), FortiManager, F5, WALLIX. C'est le cœur d'un appel d'offres de sécurité des infrastructures. Notre prix est calculé sur des prix publics : une remise de 20 %, courante sur ce volume, le ramènerait à 195 337 €/mois, 30 % à 182 294 €/mois.

---

## Les 10 questions les plus dangereuses et comment les désamorcer

| # | Question | Pourquoi elle est dangereuse | Comment la désamorcer |
|---|---|---|---|
| 1 | « Fortinet est Leader SASE 2026 ? » (Q48) | Affirmation fausse, retirée le 13/11/2026 de l'offre, du guide, du glossaire et du diaporama ; un jury qui la vérifie mettrait en doute toutes nos sources | Retirer l'affirmation partout avant la soutenance ; si la question vient, corriger nous-mêmes : « Challenger en 2026, Leader en 2025 ; Leader 2026 des pare-feu » |
| 2 | « Le 600F est-il encore vendu ? » (Q10) | Modèle en fin de commande depuis le 01/05/2026 : un expert réseau le sait | Annoncer d'emblée « 600F ou son successeur de la génération G (700G), même capacité de tunnels, recoté au devis » |
| 3 | « Le ZTNA est-il vraiment inclus ? » (Q47) | Pilier de l'argument à 1,99 M€ ; le guide de commande Fortinet exige une licence par hub en Standard | Dire « inclus côté utilisateur, licence à ajouter sur 4 hubs, l'écart avec ZPA reste d'au moins 1,5 M€ » |
| 4 | « Votre maquette prouve-t-elle vos produits ? » (Q11) | Tentation de survendre | Répondre « non, les principes », citer ce qui n'est pas prouvé, proposer une preuve de concept FortiGate |
| 5 | « Votre serveur a été piraté : preuves fiables ? » (Q46) | Touche à la crédibilité de toute la démonstration | Chronologie claire (compromis avant la maquette, réinstallé, durci) ; rejouer la recette en direct ; ne pas affirmer la cause comme certaine ; en faire un retour d'expérience |
| 6 | « Si un datacenter brûle, l'autre tient-il ? » et « 64 TiB suffisent ? » (Q21, Q22) | Calcul simple qui montre un sous-dimensionnement | Le dire avant : « périmètre critique seulement, 2 To pour 2,4 To ; extension vSAN probable » |
| 7 | « Quels RPO/RTO ? » (Q20) | Sans eux, deux datacenters ne font pas un plan de reprise | Proposer des classes d'applications et un atelier ; ne pas inventer de valeur présentée comme un engagement |
| 8 | « Tout Fortinet, alors que Gartner pointe ses correctifs fréquents ? » (Q41, Q50) | Combine dépendance éditeur et réputation de sécurité | Citer la diversité (Aruba, F5, WALLIX, Wazuh, identité), aucune interface exposée, correctifs par vagues, plan de réversibilité DORA |
| 9 | « HDS est-il obligatoire ? » et « Cloud Act ? » (Q24, Q44) | Réponse juridique facile à rater dans un sens ou dans l'autre | « Pas forcément pour le remboursement, mais exigé par prudence » ; « services cloud américains exposés, équipements chez nous non » |
| 10 | « 53 commutateurs sur 24 ports ? » et « que n'avez-vous pas chiffré ? » (Q38, Q3) | Montre une erreur de conception et des trous de chiffrage | Reconnaître, donner l'ordre de grandeur (~8 k€/mois), renvoyer à la liste des non inclus, qui est complète et assumée |
