# Recette du lab RAO — 20261110T182053Z

Tests de flux : **15/17 réussis**, 4 non exécutés (hors périmètre de la maquette).

Lignes de journal pare-feu collectées pendant la recette : 28 (fichier `journaux_pare-feu.log`).

## Bascule WAN (agence FR)

Résultat : **échoué** — non mesurée.

- Route pendant la coupure de l'opérateur A : `10.11.20.20 via 203.0.113.1 dev eth2 src 203.0.113.40 uid 0 `
- Ping 0,2 s depuis cli-ag : ``
- Route après rétablissement : `10.11.20.20 via 198.51.100.1 dev eth1 src 198.51.100.40 uid 0 `

