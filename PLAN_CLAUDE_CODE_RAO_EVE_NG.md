# Plan de réalisation — Réponse à appel d’offres et maquette EVE-NG

Document de travail pour Claude Code — 15 octobre 2026.
Source : « RAO (Réponse Appel d'Offre) - Sécurité des Infrastructures.pdf » fourni par l’utilisateur.
Statut : plan de réalisation, aucune infrastructure déployée et aucun import EVE-NG testé à ce stade.

## 1. Objectif et périmètre exact

Construire une réponse technique et financière argumentée, accompagnée d’une maquette démontrable. Le PDF ne demande pas explicitement EVE-NG : la maquette est le moyen retenu pour prouver les choix.

- 500 sites en France : 2 sièges et 498 agences.
- 30 agences internationales, soit 530 sites au total.
- 10 000 utilisateurs : 4 000 dans les sièges, 4 000 dans les agences françaises, 2 000 à l’international.
- Environ 100 partenaires : 40 % en interconnexion site à site, 60 % en accès nomade. Ce sont des catégories de partenaires, pas nécessairement 40 tunnels et 60 utilisateurs.
- Housing datacenter, compute, WAN, flux nord/sud et est/ouest, accès Internet, publication web/API/FTP, agences, infogérance, nomadisme et partenaires.
- Livrables demandés : solutions et modèles d’équipement justifiés, schémas HLD, coûts globaux, préférence pour des abonnements afin de limiter l’investissement initial.

Ne pas émuler 530 sites : dimensionner l’offre pour 530 sites et prouver les principes sur quelques sites représentatifs. Les débits, applications, volumes, pays, RPO/RTO et SLA ne sont pas fournis : les enregistrer comme hypothèses, jamais comme exigences du client.

## 2. Deux modes de réalisation possibles

### Mode A — Déployer directement sur la machine

Claude Code utilise le terminal et SSH ; la prise de contrôle graphique n’est pas nécessaire pour l’essentiel. Il faut une connexion réseau, un accès autorisé à la machine et les droits adaptés. Une API ou une automatisation de navigateur ne sera utilisée que si elle est effectivement disponible et vérifiée sur l’édition installée.

1. Auditer le matériel, l’OS, les disques, la virtualisation et les réseaux existants en lecture seule.
2. Identifier si EVE-NG existe déjà. Sinon, préparer une installation officielle compatible, de préférence dans une VM dédiée sur l’hyperviseur existant si la virtualisation imbriquée fonctionne.
3. Si seule une machine physique vierge est disponible, préparer l’installation depuis l’ISO officielle. L’installation initiale peut nécessiter une console locale ou distante ; SSH seul ne remplace pas cette console.
4. Sauvegarder les éléments existants et disposer d’un accès console avant toute modification de réseau de gestion.
5. Installer/importer les images légalement disponibles, créer le laboratoire, démarrer les nœuds, injecter les configurations et exécuter les tests.
6. Exporter ensuite une version reproductible avec les résultats réels.

Ne jamais formater un disque, réinstaller un hôte existant ou modifier sa route de gestion sans validation explicite de cette opération. Ne jamais réutiliser automatiquement un ancien serveur ou d’anciens identifiants issus d’un autre projet.

### Mode B — Préparer un paquet importable

À retenir si Claude Code n’a pas accès à la machine. Il construit un dossier puis une archive ZIP contenant :

- `SUIVI_PROJET.md` : état du travail, journal et procédure de reprise par un collègue et son IA ;
- `lab/RAO_Mutuelle.unl` : nœuds, interfaces, réseaux et positionnement ;
- `inventory/images.yml` : noms exacts des images, versions, provenance, licences, empreintes disponibles, ressources et noms des disques attendus ;
- `inventory/topology.yml` et `inventory/addressing.csv` : inventaire et adressage de référence ;
- `configs/` : configurations par équipement, sans secrets réels ;
- `automation/` : précontrôles, génération du lab, déploiement des configurations et vérifications ;
- `docs/IMPORT.md` : images à installer, méthode d’import, configuration, démarrage et dépannage ;
- `tests/` et `evidence/` : scénarios, résultats observés et preuves ;
- `docs/HLD.md`, `docs/LLD.md`, `docs/OFFRE_TECHNIQUE.md` et `docs/CHIFFRAGE.csv`.

Un `.unl` n’embarque pas les disques des VM. L’archive du projet n’est pas nécessairement importable telle quelle par l’interface EVE-NG : produire séparément l’archive d’import native conforme à la version cible, en plus du paquet complet. Ne pas promettre un chargement en un clic si une installation d’images ou une configuration initiale reste nécessaire.

Si la version cible n’est pas connue, produire un générateur paramétrable et un modèle provisoire clairement signalé. Valider le schéma avec un petit lab exporté par l’EVE cible ; ne pas inventer les attributs XML ou les noms de templates. Sans accès à EVE, qualifier le paquet « préparé, non testé sur EVE-NG ».

**Méthode recommandée : construire systématiquement le paquet reproductible du mode B, puis l’appliquer en mode A dès que les accès sont disponibles.**

## 3. Architecture cible proposée pour l’offre

Il s’agit de choix à justifier, pas d’exigences présentes dans le PDF.

| Domaine | Proposition à étudier et justifier |
|---|---|
| Datacenters | Deux sites de housing dans des domaines de panne distincts ; alimentation et connectivité redondées ; stratégie de reprise documentée |
| Compute | Clusters de virtualisation, capacité N+1 et stockage adapté ; définir quelles applications restent actives après perte d’un DC |
| WAN | Overlay chiffré/SD-WAN sur accès opérateurs ; double accès diversifié pour sièges/DC, profils d’agence avec secours selon criticité |
| Agences | Segments utilisateurs, invités et administration ; sortie Internet locale sécurisée et accès DC via tunnels |
| Nord/sud | Pare-feu périmétriques, DMZ, reverse proxy/WAF pour web/API, filtrage des sorties et journalisation |
| Est/ouest | Zones web, applicative, données et administration ; filtrage explicite et refus par défaut |
| Nomadisme | VPN ou ZTNA avec identité et MFA ; droits par groupe et application |
| Partenaires | Zone dédiée ; VPN site à site pour interconnexions, accès applicatif authentifié pour nomades ; aucun accès général au SI |
| Infogérance | Accès nominatif MFA, bastion, périmètre limité, durée contrôlée, traçabilité des sessions |
| Exploitation | DNS/NTP, collecte centralisée de journaux, supervision, sauvegardes et procédures de reprise |

Pour le service FTP du sujet : proposer une migration SFTP ou FTPS selon compatibilité métier. SFTP n’est pas du FTP chiffré. Si le FTP historique est indispensable, documenter l’exception, les contraintes et l’isolation ; ne pas l’exposer en clair par défaut.

Ne pas assimiler deux DC à un PRA opérationnel : expliciter réplication, cohérence des données, dépendances, sauvegardes et tests de restauration. EVE-NG ne prouve ni la résilience physique du housing, ni la performance à 10 000 utilisateurs.

## 4. Maquette représentative

### Socle initial : environ 14 à 18 nœuds

- 2 routeurs de transport représentant deux opérateurs indépendants ;
- 2 passerelles/pare-feu, une par DC ;
- 1 siège, 1 agence française et 1 agence internationale, chacun avec sa passerelle ;
- 1 passerelle de partenaire site à site ;
- 1 service web/API en DMZ, 1 serveur applicatif et 1 serveur de données ;
- 1 bastion et 1 collecteur de journaux ;
- 1 à 3 clients de test pouvant représenter successivement agence, Internet, salarié nomade et partenaire nomade.

Les réseaux L2 simples peuvent être représentés par des réseaux EVE sans VM de commutateur. Ne prétendre tester VLAN, STP ou sécurité des commutateurs qu’avec des nœuds qui implémentent réellement ces fonctions.

### Extension après validation du socle

Ajouter une paire HA dans un DC, la réplication d’un service vers le second DC, un serveur d’identité/MFA et des clients distincts. Définir précisément les scénarios de bascule : perte WAN, perte pare-feu, perte DC sont trois cas différents.

Pour réduire les licences et ressources, étudier des VM Linux avec routage, filtrage et IPsec. Pour une démonstration proche de l’offre commerciale, utiliser les appliances éditeur disponibles légalement. Dans tous les cas, vérifier les templates EVE, les ressources et les mécanismes de configuration des versions choisies. Un tunnel IPsec avec routage ne constitue pas à lui seul une solution SD-WAN ; un VPN ne constitue pas à lui seul une solution ZTNA.

### Budget matériel indicatif de la maquette

| Profil | Ressources envisagées | Utilisation |
|---|---|---|
| Réduit | Environ 8 threads CPU, 32 Go RAM, 150 à 250 Go SSD libres | Linux légers, scénarios séquentiels, pas de SIEM lourd |
| Confort | Environ 16 threads CPU, 64 Go RAM, 300 à 500 Go SSD libres | Plus de simultanéité, identité et HA |
| Étendu | 128 Go RAM ou plus selon appliances | Plusieurs pare-feu commerciaux et services plus lourds |

Ce sont des estimations de travail, pas des minima officiels ni une garantie. Calculer la somme des allocations réellement retenues, réserver de la RAM pour EVE/l’hyperviseur et mesurer la charge. Vérifier l’exposition des extensions de virtualisation dans la VM EVE et le fonctionnement KVM ; ne pas conclure à la compatibilité sur le seul nom du processeur.

## 5. Adressage et politique de flux

Proposition de maquette, à adapter après recherche de conflits avec le LAN, le VPN d’administration et les réseaux existants :

| Zone | Bloc proposé |
|---|---|
| DC1 | 10.10.0.0/16, sous-réseaux /24 par zone |
| DC2 | 10.20.0.0/16, sous-réseaux /24 par zone |
| Siège témoin | 10.30.0.0/16 |
| Agence France témoin | 10.40.1.0/24 |
| Agence internationale témoin | 10.50.1.0/24 |
| Partenaire témoin | 10.60.1.0/24 |
| Accès nomade | 10.70.1.0/24 |
| Administration lab | 10.99.0.0/24 |

Pour l’offre cible, produire un véritable IPAM tenant compte des 530 sites, de leur taille et de la croissance. Les blocs de cette table ne sont pas le dimensionnement complet de l’entreprise.

Matrice minimale : Internet vers reverse proxy en HTTPS ; reverse proxy vers application sur port documenté ; application vers base sur port strictement nécessaire ; utilisateurs vers services autorisés ; invités interdits vers réseaux privés ; partenaires limités aux applications prévues ; infogérants via bastion uniquement. DNS, NTP, mises à jour et collecte de logs ont leurs propres règles. Documenter source, destination, protocole, port, justification et journalisation. Prévoir un test négatif pour chaque frontière de confiance.

Les réseaux Internet/opérateur sont simulés et isolés. L’accès réel à Internet, si nécessaire aux installations, passe par une sortie contrôlée. Ne pas brancher directement un réseau de test non filtré sur le réseau de gestion via un Cloud EVE.

## 6. Séquence d’exécution pour Claude Code

### Étape 1 — Cadrer sans bloquer inutilement

Lire le PDF et ce plan. Créer une matrice « exigence → solution → preuve → limite → coût ». Demander seulement les informations bloquantes : machine cible, ressources, hyperviseur/OS, EVE installé ou non, édition/version et images disponibles. Préparer les documents et le paquet pendant que les accès manquent. Ne pas demander de mots de passe dans les documents : utiliser des clés SSH ou un mécanisme de secrets local.

### Étape 2 — Auditer et choisir le profil

Collecter CPU/RAM/disque, réseau, accès console et disponibilité de la virtualisation imbriquée. Distinguer possibilité technique et support officiel de la plateforme. Produire `docs/PREFLIGHT.md`, avec résultats, blocages et ressources allouées. Sélectionner le mode A ou B sans supposer une prise de contrôle disponible.

### Étape 3 — Concevoir avant de configurer

Produire HLD cible et HLD maquette séparés, puis LLD : interfaces, liens, adressage, routes, tunnels, NAT, zones, ACL, identité et dépendances. Définir un inventaire unique utilisé par le générateur `.unl` et les configurations pour éviter les divergences.

### Étape 4 — Prouver la chaîne sur un mini-lab

Créer deux nœuds et un lien. Vérifier import, démarrage, nom réel des interfaces, console, application et persistance de la configuration. Ne pas supposer que toutes les images QEMU savent consommer une startup-config EVE. Choisir par famille : SSH/Ansible après bootstrap, console automatisée, cloud-init si réellement supporté, ou import de configuration documenté. Ne pas modifier une image de base partagée pour y enregistrer la configuration d’un seul nœud.

### Étape 5 — Construire progressivement

Déployer transport → DC → services → siège/agences → partenaires → nomadisme/MFA → administration/journaux → redondance. À chaque jalon, vérifier la connectivité autorisée et les refus attendus. Les scripts doivent être relançables, limités au laboratoire et sans secrets en sortie. Fournir nettoyage ciblé et restauration, sans suppression générale des labs existants.

### Étape 6 — Recette et preuves

| Test | Résultat attendu |
|---|---|
| Agence vers application | Accès via le tunnel prévu et journal visible |
| Internet vers web/API | HTTPS fonctionne ; accès direct à la base et à l’administration refusé |
| Segmentation | Web ne peut pas joindre librement la base ; application accède au seul port autorisé |
| Invité | Sortie prévue possible, réseaux internes inaccessibles |
| Partenaire site à site | Application partenaire accessible ; applications internes interdites |
| Nomade salarié/partenaire | Authentification et MFA prouvés si configurés ; droits distincts et révocation testée |
| Infogérant | Passage par bastion et trace de session ; accès direct refusé |
| Coupure WAN | Bascule observée et temps de perte mesuré ; retour nominal vérifié |
| Pare-feu/DC | Tests uniquement si redondance et services secondaires implémentés ; pertes et limites documentées |
| Redémarrage/import propre | Configuration conservée ou réappliquée conformément à la procédure |

Conserver commandes, horodatages, résultats et captures utiles. Marquer chaque test « réussi », « échoué » ou « non exécuté ». Ne jamais produire de preuves fictives ou déclarer le MFA/HA fonctionnel après une simple génération de configuration.

### Étape 7 — Préparer la réponse à l’appel d’offres

Rédiger une synthèse exécutive, l’offre technique, les HLD, les choix de modèles/licences/support, le plan de migration, les modalités d’exploitation et les limites de la maquette. Pour chaque solution commerciale, rechercher des sources officielles à jour et distinguer prix public, estimation et devis nécessaire.

Chiffrer séparément : housing des deux DC, raccordements et WAN, secours opérateur, serveurs/stockage, réseau, pare-feu, licences, accès nomades/partenaires, supervision, sauvegardes, support, déploiement et exploitation. Préciser devise, date, HT/TTC et hypothèses de conversion. Utiliser des profils et quantités qui totalisent bien 2 sièges + 498 agences françaises + 30 internationales. Inclure les deux DC en plus si ce sont des implantations distinctes des sièges ; éviter les doubles comptes.

Présenter abonnement/location/services managés, frais initiaux et TCO sur 36 et 60 mois. Formule de base : TCO = frais initiaux + durée × récurrents mensuels + autres dépenses prévues. Adapter la formule aux renouvellements et échéances contractuelles. Ne pas annoncer des tarifs inventés pour compléter un tableau. Comparer au moins une offre économique et une offre résiliente, avec périmètres clairement indiqués.

## 6 bis. Gestion obligatoire des images manquantes

Claude Code doit rechercher et télécharger lui-même les images nécessaires absentes, lorsque leur distribution et les accès disponibles le permettent. Ne pas se limiter à demander à l’utilisateur de tout télécharger.

1. Comparer les images requises à celles déjà présentes ; vérifier version, format, intégrité, template et compatibilité avec l’édition EVE cible. Ne pas écraser une image existante utilisée par d’autres labs.
2. Rechercher les téléchargements officiels de l’éditeur ou des dépôts autorisés. Utiliser les accès déjà fournis de manière sécurisée. Si un compte, une licence payante ou une acceptation contractuelle manque, documenter le blocage et demander seulement l’intervention nécessaire ; continuer les autres tâches. Ne pas contourner ces restrictions ni substituer discrètement un autre produit.
3. Télécharger dans un répertoire temporaire avec gestion des erreurs et des fichiers incomplets. Vérifier l’espace libre pour le téléchargement, la décompression et la conversion. Contrôler l’empreinte ou la signature publiée par l’éditeur lorsqu’elle existe. À défaut, calculer une empreinte locale pour la traçabilité sans la présenter comme une preuve d’authenticité.
4. Consulter la table officielle de nommage QEMU et la procédure propre à l’appliance. Respecter exactement le préfixe de dossier, le nom du disque attendu, la version et le template. Le nom du disque varie selon l’appliance : ne pas appliquer un nom universel.
5. Extraire ou convertir réellement le format si nécessaire ; renommer une extension ne convertit pas un disque. Enregistrer le nom et l’empreinte du fichier source, la commande de conversion et l’empreinte du résultat.
6. En mode direct, installer l’image dans le répertoire attendu par EVE (pour QEMU : `/opt/unetlab/addons/qemu/`), appliquer la procédure de permissions documentée pour la version installée, puis vérifier sa détection et le démarrage d’un nœud minimal. Ne pas considérer un téléchargement réussi comme une image validée.
7. En mode hors ligne, préparer les téléchargements accessibles et un script reproductible d’acquisition/installation. Ne joindre les images au paquet partagé que si leur redistribution est permise ; sinon fournir le manifeste et la procédure pour chaque collègue autorisé.
8. Mettre à jour `inventory/images.yml` et `SUIVI_PROJET.md` après chaque image traitée : produit, version, source officielle sans jeton, fichier original, empreinte, template, dossier EVE, noms des disques, ressources, licence, état et preuve du test.

États à distinguer : `manquante`, `téléchargement en cours`, `téléchargée`, `vérifiée`, `installée`, `démarrage validé`, `bloquée`. Toute image non vérifiée reste explicitement signalée. Proposer une alternative libre si une image est indisponible, en précisant l’impact sur la démonstration et sur l’offre.

## 6 ter. Continuité du travail entre collègues et IA

Créer dès le démarrage un fichier **`SUIVI_PROJET.md` à la racine du projet**. Ce fichier doit permettre à un collègue, avec Claude Code ou une autre IA, de reprendre sans disposer de l’historique de conversation. Utiliser le modèle fourni et le faire évoluer avec les résultats réels.

### Rythme obligatoire de mise à jour

- Au début d’une session : lire le suivi, identifier l’intervenant, contrôler l’état réel et annoncer la tâche prise en charge dans le fichier.
- Avant une opération longue ou sensible : enregistrer son intention, la cible, l’état préalable et le moyen de vérifier son exécution.
- Après chaque tâche significative, téléchargement, modification de configuration ou test : enregistrer le résultat et les fichiers concernés.
- Avant toute pause, changement d’IA, fin de session ou transfert : noter le dernier point vérifié et les prochaines actions exécutables.
- Après une interruption brutale : vérifier les processus, fichiers partiels, nœuds et journaux avant de relancer ; le dernier suivi peut précéder une opération réellement terminée.

### Contenu minimal

Date/heure avec fuseau, responsable, objectif, mode A/B, environnement et versions, branche/commit si Git existe, fichiers non commités, tâches par statut, décisions et justifications, images et état de validation, modifications réellement appliquées, tests avec preuves, erreurs et tentatives déjà réalisées, blocages, opérations en cours, sauvegardes/retour arrière et trois prochaines actions précises.

Séparer « prévu », « généré », « appliqué » et « testé ». Ne jamais inscrire de mots de passe, clés privées, jetons, liens de téléchargement signés ou configurations contenant des secrets. Référencer uniquement le mécanisme d’accès et le détenteur autorisé.

Le suivi doit pointer vers les fichiers et preuves partagés avec des chemins relatifs. Un Markdown seul ne transmet ni les VM ni les images ni les configurations : fournir le dossier projet à jour et l’accès autorisé au serveur. Si un dépôt Git partagé est disponible, versionner les documents, scripts et configurations expurgées ; exclure secrets, disques VM et gros journaux. Ne pas créer de dépôt public ou publier des fichiers sans instruction.

Pour éviter des modifications concurrentes incompatibles, réserver une tâche et une cible avant intervention, attribuer un seul responsable par équipement en cours de configuration et consigner la fin de prise en charge. Si plusieurs collègues travaillent simultanément, utiliser des branches distinctes pour les fichiers et coordonner les changements sur le serveur partagé.

### Instruction de reprise à transmettre à toute nouvelle IA

> Lis d’abord SUIVI_PROJET.md, puis le plan, les inventaires et les fichiers référencés par la tâche en cours. Résume ce qui est réellement terminé, les blocages et la prochaine action. Vérifie l’état réel du serveur et des fichiers avant toute relance. Ne recommence pas les travaux validés et n’écrase pas les changements d’un collègue. Prends en charge une tâche clairement identifiée, exécute-la puis actualise le suivi avec les résultats et les preuves. Si les accès manquent, avance sur les livrables hors ligne et indique précisément ce qui reste à appliquer.

## 7. Critères de livraison

Le résultat est terminé lorsque :

1. Toutes les exigences du PDF ont une réponse ou une réserve explicite.
2. Le dossier cible distingue correctement architecture de production et démonstrateur.
3. La version EVE et les images exactes sont enregistrées, ou les dépendances manquantes sont listées.
4. Le lab est déployé et testé en mode A, ou le paquet et sa notice sont livrés avec leur niveau réel de validation en mode B.
5. Les configurations sont reproductibles et les secrets absents du paquet.
6. Les résultats de recette sont factuels ; les limites ne sont pas masquées.
7. Le coût récurrent, les frais initiaux, les quantités et les hypothèses sont vérifiables.
8. Les images manquantes accessibles ont été téléchargées, vérifiées et nommées selon les règles EVE ; les autres dépendances sont précisément documentées.
9. `SUIVI_PROJET.md` est à jour et permet une reprise sans historique de conversation, avec les fichiers, preuves et prochaines actions nécessaires.

## 8. Instruction de lancement à copier dans Claude Code

> Lis le PDF de l’appel d’offres et le fichier PLAN_CLAUDE_CODE_RAO_EVE_NG.md du projet. Prépare la réponse technique et financière ainsi qu’une maquette EVE-NG représentative. Commence par relever les exigences et auditer les moyens disponibles sans modifier l’existant. Construis un paquet reproductible comprenant topologie .unl, inventaire des images, configurations, automatisation, documentation d’import et tests. Si une machine cible et des accès autorisés sont fournis, installe ou utilise EVE-NG, déploie ce même paquet puis réalise la recette. Sinon, termine le paquet et indique précisément ce qui reste à installer ou vérifier. Distingue la cible de 530 sites du démonstrateur réduit. Avance de façon autonome sur les décisions réversibles ; demande seulement les informations réellement bloquantes et une validation avant une opération destructive sur l’hôte. Vérifie la compatibilité de la version EVE et des images avant de générer le lab final. Ne considère jamais le .unl seul comme une infrastructure configurée. Produis les HLD cible/maquette, la matrice de flux, les preuves de recette et un chiffrage sourcé avec option d’abonnement. Télécharge toi-même les images manquantes depuis des sources officielles ou autorisées, respecte le nommage propre à chaque template EVE et vérifie leur intégrité et leur démarrage. Crée SUIVI_PROJET.md dès le début, actualise-le après chaque tâche significative et avant toute interruption afin qu’un collègue et son IA puissent reprendre. S’il existe déjà, lis-le avant toute action et vérifie l’état réel. Commence maintenant par le cadrage, l’inventaire et la structure du projet.

## 9. Références techniques de départ

Documentation officielle consultée le 15 octobre 2026 ; recontrôler les exigences de la version choisie avant installation.

- Matériel et virtualisation : https://www.eve-ng.net/index.php/supported-hardware-and-software-systems/
- Nommage des images QEMU : https://www.eve-ng.net/index.php/documentation/qemu-image-namings/
- Préparation des images : https://www.eve-ng.net/index.php/documentation/howtos/
- Images Linux : https://www.eve-ng.net/index.php/documentation/howtos/howto-create-own-linux-host-image/
- Fonctionnalités et format de lab : https://www.eve-ng.net/index.php/features/

Ces références établissent les mécanismes EVE ; elles ne valident pas à elles seules les produits commerciaux, leur dimensionnement ou les tarifs de l’offre à construire.
