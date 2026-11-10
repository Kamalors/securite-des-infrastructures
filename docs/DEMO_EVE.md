# Démonstration EVE-NG — scénario de soutenance (≈ 4 minutes)

Pour l'orateur de la diapositive « Maquette » (rôle 2, architecte WAN). Toutes les commandes ont été revérifiées le 28/10/2026. Documentation complète de la maquette : `docs/MAQUETTE.md`.

## Avant la soutenance (la veille et 15 min avant)

1. Tunnel vers EVE ouvert, dans PowerShell : `ssh -i "$env:USERPROFILE\.ssh\id_ed25519_par861454" -N -L 8443:10.99.0.10:443 administrateur@163.172.105.87` (dans l'invite cmd : `%USERPROFILE%` à la place de `$env:USERPROFILE` ; sous PowerShell, `%USERPROFILE%` n'est pas remplacé et la clé est refusée), puis https://localhost:8443, lab `RAO`. Plus court : `ssh -F automation/ssh_config -N eve-web` ouvre EVE-NG (https://localhost:8443) et l'interface Proxmox (https://localhost:8006) d'un coup ; `lab-host` désigne le serveur, `eve-rao` la VM EVE. Les camarades utilisent `automation/connexion_rao.ps1`.
2. Les 7 nœuds tournent (icônes en couleur). Sinon : sélectionner tout, clic droit, Start.
3. Répétition rapide depuis le dossier du projet : `python automation/lab/recette.py --sans-bascule` → doit afficher 17 « réussi » et `RÉSULTAT : CONFORME`.
4. Option sans terminal : double-clic sur `automation/Demo_RAO.cmd`. La fenêtre « Maquette RAO » ouvre EVE-NG et Proxmox (boutons en haut, même tunnel que `ssh -L 8443:10.99.0.10:443 lab-host`), ouvre une console sur le serveur (clic sur sa pastille), vérifie les 15 machines et lance chaque étape ci-dessous d'un clic (touches 1 à 7), avec le verdict en grand et le chemin testé allumé sur le schéma. « Vérifier la maquette » contrôle aussi le disque, OSPF et les tunnels du datacenter ; si une étape échoue, le bouton « Réparer la maquette » relance la configuration (environ une minute). Elle demande la clé d'administration ; sur le PC d'un camarade, elle ne fait qu'ouvrir EVE-NG.
5. Plan B si le réseau de la salle bloque le tunnel : montrer les preuves de `evidence/20261110T183628Z/` (ou `20261016T181400Z/`) et une capture de la topologie.

Clic sur un nœud = console. Elle s'ouvre **directement en root** et affiche les commandes utiles. Si elle est noire, appuyer sur Entrée.

## Déroulé

| Étape | Où | Commande | Ce qu'on montre |
|---|---|---|---|
| 1. Topologie | Vue du lab | — | DC1 et DC2 à gauche, opérateurs A et B au centre, siège, agence et partenaire à droite, réseau de gestion en bas ; serveurs et clients réels en conteneurs, branchés par les nuages « Cloud » |
| 2. Tunnels | Console `fw-dc1` | `swanctl --list-sas \| grep ESTABLISHED` | 6 tunnels IPsec chiffrés vers les sites |
| 3. Routage | Console `fw-dc1` | `vtysh -c 'show ip ospf neighbor'` | 5 voisins : chaque site a un tunnel par opérateur |
| 4. Journal en direct | Console `fw-dc1` | `journalctl -k -f -n 0 \| grep RAO` | laisser ouvert pendant l'étape 5 (`-n 0` : seulement les nouvelles lignes, sans l'historique) |
| 5. Autorisé / refusé | Console `gw-part` (partenaire) | `nc -zv -w3 -s 10.60.1.1 10.11.20.20 8443` puis `nc -zv -w3 -s 10.60.1.1 10.11.30.30 5432` | 1re : « succeeded » (application) ; 2e : « timed out » (base de données refusée). Sur `fw-dc1`, apparaissent `RAO-OK F06` puis `RAO-REFUS` |
| 6. Bascule WAN | Console `gw-agfr` (agence) | `ip route get 10.11.20.20` → `ip link set eth1 down` → attendre 5 s → `ip route get 10.11.20.20` → `ping -c3 -I 10.40.1.1 10.11.20.20` → `ip link set eth1 up` | la route passe de `xa-dc1` (opérateur A) à `xb-dc1` (opérateur B), l'application reste joignable, puis retour sur A |
| 7. Recette complète | Terminal du PC (projeté) | `python automation/lab/recette.py` | 17/17 flux conformes, bascule mesurée (3 à 4 s), preuves horodatées et empreintes dans `evidence/` |

**Phrase de conclusion** : « La maquette prouve les principes (segmentation, chiffrement, bascule, traçabilité), pas les produits : en production, ce sont des FortiGate qui appliquent la même politique. »

## Si quelque chose ne marche pas

- Console muette : appuyer sur Entrée ; sinon fermer et rouvrir la console.
- Tunnels absents (étape 2) : `python automation/lab/deploy.py` depuis le PC, puis attendre 10 s.
- Bascule non observée : vérifier que l'étape 6 commence avec `xa-dc1` ; après la démo, toujours remettre `ip link set eth1 up`.
