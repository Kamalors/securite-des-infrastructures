# Soutenance — rôles des 7 membres du groupe

Diaporama : https://claude.ai/artifact/957Rryu9hkuprq9MUcjuns (24 diapositives, notes d'orateur sur chacune).
Hypothèse de durée : ~20 minutes de présentation (≈ 50 s par diapositive), puis questions. À ajuster dès que la durée est connue.
Répartition arrêtée le 10/11/2026. Diapositive de l'équipe : `presentation/equipe_soutenance.png` (et diapositive 2 du diaporama).

| Ordre | Rôle | Qui | Diapositives | Temps cible |
|---|---|---|---|---|
| 1 | Chef de projet | Farah | 1 couverture, 2 équipe, 3 synthèse, 4 besoin · 24 conclusion | 3 min 30 |
| 2 | Architecte WAN | Valentin | 5 HLD global, 6 SD-WAN · 22 maquette | 2 min 30 |
| 3 | Architecte datacenter | Nolan | 7 housing, 8 compute, 9 HLD datacenter | 2 min 30 |
| 4 | Responsable sécurité des flux | Fatih | 10 nord/sud, 11 est/ouest, 12 infogérance | 2 min 30 |
| 5 | Architecte agences et exploitation | Younes | 13 HLD agences, 14 exploitation · 23 risques | 2 min 30 |
| 6 | Expert Zero Trust | Maxime | 15 nomadisme, 16 partenaires, 17 HLD accès distants, 18 choix du ZTNA | 3 min 20 |
| 7 | Responsable financier | Diane | 19 modèles, 20 coûts, 21 phasage | 2 min 30 |

Enchaînement : chacun présente un bloc continu ; seuls la maquette (2), les risques (5) et la conclusion (1) reviennent en fin de parcours.

## Fiche par rôle

### 1. Chef de projet — Farah
- **Message** : une architecture complète, en abonnement (221,4 k€ HT/mois, rien à avancer), dont les principes sont prouvés sur maquette.
- **À maîtriser** : les volumes du PDF, les hypothèses (3 000 nomades, 300 VM, 50 comptes à privilèges…) et pourquoi elles sont affichées.
- **Questions probables** : « Pourquoi ces hypothèses ? » « Qu'est-ce qui change si elles sont fausses ? » (réponse : le chiffrage se recalcule en une commande).
- **Passage de relais** : « Valentin va vous présenter comment les 530 sites sont reliés. »

### 2. Architecte WAN — Valentin
- **Message** : SD-WAN Fortinet sur Internet, double hub vers les 2 DC ; pas de MPLS.
- **À maîtriser** : profils d'accès par type de site, dimensionnement des hubs (~1 060 tunnels requis, 2 000 acceptés par FortiGate 600F, plus commandable depuis mai 2026 : 700G, successeur probable, même capacité de tunnels), bascule mesurée à 3,8 s.
- **Maquette (diapo 22)** : 17/17 flux conformes, ce qui est prouvé et ce qui ne l'est pas ; anecdote MOBIKE (le tunnel « déménageait » sur l'autre opérateur et masquait la bascule). **Démonstration en direct dans EVE : scénario pas à pas dans `docs/DEMO_EVE.md`** (≈ 4 min, à ajouter au temps de passage).
- **Questions probables** : « Pourquoi pas MPLS ? » « Que se passe-t-il si les deux accès d'une agence tombent ? » « Votre maquette prouve-t-elle vos produits ? » (non, les principes).

### 3. Architecte datacenter — Nolan
- **Message** : 2 DC certifiés HDS, domaines de panne distincts, compute VMware N+1, sauvegarde 3-2-1 avec copie immuable.
- **À maîtriser** : 4 hôtes Dell R760 par DC, vSAN RAID 5 inclus (64 TiB bruts/DC ; 70 à 80 requis, extension probable), actif/actif pour la publication, actif/passif pour les bases.
- **Questions probables** : « Quelle distance entre les DC ? Réplication synchrone ou asynchrone ? » « RPO/RTO ? » (à fixer avec le client) « Pourquoi VMware après le rachat par Broadcom ? » (alternative Proxmox/Nutanix documentée).

### 4. Responsable sécurité des flux — Fatih
- **Message** : tout est refusé par défaut ; chaque flux autorisé est écrit, justifié, journalisé.
- **À maîtriser** : DMZ, WAF F5, FTP remplacé par SFTP, deux paires de pare-feu par DC (périmètre, interne), bastion WALLIX et MFA.
- **Questions probables** : « Comment gérez-vous un partenaire qui ne sait faire que du FTP ? » (exception temporaire isolée) « Que se passe-t-il si le serveur web est compromis ? » (il n'atteint pas la base) « Ransomware ? »

### 5. Architecte agences et exploitation — Younes
- **Message** : trois profils de site standardisés (siège, agence FR, agence internationale), LAN et Wi-Fi compris, pilotés depuis une console.
- **À maîtriser** : règles de dimensionnement (1,25 port/utilisateur, 1 borne/25, HA au-delà de 50 utilisateurs), segmentation invités, FortiManager, SIEM Wazuh.
- **Risques (diapo 23)** : HDS, DORA (plan de réversibilité), RGPD (transferts hors UE), risques projet.
- **Questions probables** : « Comment déployez-vous 498 agences ? » « DORA s'applique-t-il ? » « Cloud Act ? »

### 6. Expert Zero Trust — Maxime
- **Message** : personne n'accède au réseau, chacun n'atteint que ses applications, après MFA et contrôle du poste.
- **À maîtriser** : FortiSASE pour 3 000 nomades, partenaires 40 % site à site / 60 % nomades (portail sans agent), choix du ZTNA : ZPA écarté, 1,99 M€ bruts évités (de 1,24 à 3,31 M€ selon les estimations), au moins 1,5 M€ après la licence d'accès privé des 4 FortiGate hubs (Q47).
- **Questions probables** : « VPN ou ZTNA, quelle différence ? » « Et si le fournisseur SASE tombe ? » « Dépendance à un seul éditeur ? » (identité indépendante, plan de réversibilité).

### 7. Responsable financier — Diane
- **Message** : 221,4 k€ HT/mois sur 36 mois (TCO 7,97 M€), soit 22,14 € par utilisateur et par mois, sans investissement initial.
- **À maîtriser** : ventilation par poste du PDF, location financière (hypothèse 7 %/an), différence avec l'achat (4,22 M€ + 91 k€/mois, soit 7,50 M€ sur 36 mois), analyse de sensibilité et postes non inclus de `docs/CHIFFRAGE.md`, phasage en 9 mois.
- **Questions probables** : « D'où viennent vos prix ? » (revendeurs et comparateurs sourcés, taux BCE, devis à confirmer) « Coût par site ? » (418 €/mois) « Pourquoi l'abonnement coûte-t-il plus cher que l'achat ? » (0,47 M€ de plus sur 36 mois : le prix du financement, qui évite d'avancer 4,22 M€) « Réversibilité de l'abonnement ? »

## Répétition
1. Chacun lit les notes d'orateur de ses diapositives et vérifie ses chiffres dans `docs/CHIFFRAGE.md` et `docs/OFFRE_TECHNIQUE.md`.
2. Une répétition chronométrée complète, avec les passages de relais.
3. Une séance de questions croisées : chacun pose aux autres les « questions probables » de leur fiche.
