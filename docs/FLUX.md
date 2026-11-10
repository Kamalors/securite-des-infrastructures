# Matrice de flux — maquette (transposable à la cible)

Politique : **refus par défaut** à chaque frontière, tout flux autorisé est journalisé. Adresses : `inventory/addressing.csv`. Les ports applicatifs (8443, 5432) sont des choix de maquette, à remplacer par ceux du client.
État : **appliqué et testé le 16/10/2026** (`automation/lab/deploy.py`, recette `automation/lab/recette.py`) : flux F01-F06, F09-F11, F13 et refus N01-N06, N08 conformes ; F07, F08, N07, N09 non exécutés (nomadisme ZTNA non modélisé). F12 (DNS/NTP) non testé. Les journaux passent par le réseau de gestion (10.98.0.105:6514) et non par le flux F11. Preuves : `evidence/20261016T181400Z/`.

## Flux autorisés

| ID | Source | Destination | Proto / port | Justification | Journal |
|---|---|---|---|---|---|
| F01 | Internet (192.0.2.0/24) | srv-web 10.11.10.10 | TCP 443 | Publication web/API via RP | Oui |
| F02 | Internet | srv-web 10.11.10.10 | TCP 22 (SFTP, compte chrooté) | Remplace FTP (E08) | Oui |
| F03 | srv-web 10.11.10.10 | srv-app 10.11.20.20 | TCP 8443 | RP → application | Oui |
| F04 | srv-app 10.11.20.20 | srv-db 10.11.30.30 | TCP 5432 | Application → base, seul flux vers les données | Oui |
| F05 | Agences / siège (10.30–10.50) | srv-app 10.11.20.20 | TCP 8443 via tunnel IPsec | Utilisateurs internes → application | Oui |
| F06 | Partenaire S2S 10.60.1.0/24 | srv-app 10.11.20.20 | TCP 8443 via IPsec, zone partenaire | Application contractuelle seule | Oui |
| F07 | Nomades 10.70.1.0/24 (groupe salariés) | srv-app 10.11.20.20 | TCP 8443 | Accès distant authentifié | Oui |
| F08 | Nomades 10.70.1.0/24 (groupe partenaires) | srv-web 10.11.10.10 | TCP 443 | Portail partenaire seul | Oui |
| F09 | Administrateurs / infogérants (via VPN) | bastion 10.11.99.10 | TCP 22 / 443 | Seule porte d'administration | Oui |
| F10 | bastion 10.11.99.10 | Tous les équipements | TCP 22 / 443 | Administration tracée | Oui (session) |
| F11 | Tous les équipements | logs 10.11.99.20 | TCP 6514 (syslog TCP en maquette, TLS en production) | Centralisation des journaux | Non (volume) |
| F12 | Tous les équipements | DNS / NTP DC1 | UDP/TCP 53, UDP 123 | Services socles | Échantillonné |
| F13 | Invités agence | Internet | TCP 80/443 | Sortie invités | Oui |

## Refus attendus (tests négatifs)

| ID | Tentative | Résultat attendu | Frontière |
|---|---|---|---|
| N01 | Internet → srv-db 5432 | Refusé, journalisé | Nord/sud |
| N02 | Internet → bastion 22 | Refusé | Nord/sud |
| N03 | srv-web → srv-db 5432 | Refusé | Est/ouest |
| N04 | srv-app → srv-db autre que 5432 (ex. 22) | Refusé | Est/ouest |
| N05 | Invité agence → 10.0.0.0/8 | Refusé | Agence |
| N06 | Partenaire S2S → srv-db, bastion, réseaux agences | Refusé | Partenaires |
| N07 | Nomade partenaire → srv-app 8443 | Refusé (droits distincts des salariés) | Nomadisme |
| N08 | Agence → équipements en SSH sans bastion | Refusé | Administration |
| N09 | Nomade révoqué → tout | Refusé après révocation | Nomadisme |
