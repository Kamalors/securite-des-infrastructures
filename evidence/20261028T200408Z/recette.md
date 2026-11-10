# Recette du lab RAO — 20261028T200408Z

Tests de flux : **17/17 réussis**, 4 non exécutés (hors périmètre de la maquette).

Lignes de journal pare-feu collectées pendant la recette : 27 (fichier `journaux_pare-feu.log`).

## Bascule WAN (agence FR)

Résultat : **réussi** — 16 paquets perdus, soit environ 3.2 s d'interruption.

- Route pendant la coupure de l'opérateur A : `10.11.20.20 via 10.255.2.1 dev xb-dc1 src 10.255.2.2 uid 0 `
- Ping 0,2 s depuis cli-ag : `125 packets transmitted, 109 received, +9 errors, 12.8% packet loss, time 24995ms`
- Route après rétablissement : `10.11.20.20 via 10.255.1.1 dev xa-dc1 src 10.255.1.2 uid 0 `

