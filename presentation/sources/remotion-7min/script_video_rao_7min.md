# Vidéo « Le projet RAO en 5 minutes » : script pour ElevenLabs v3

## Comment lire ce script

- **Voix** : le texte à donner à ElevenLabs, modèle Eleven v3.
- **Écran** : ce que l'animation Remotion montre pendant ce temps.
- Les mots entre crochets ([curious], [excited], [serious]) sont des balises d'ElevenLabs v3. Elles restent en anglais parce que c'est la syntaxe de l'outil, et la voix ne les prononce pas. Elles dépendent de la voix choisie : à tester et ajuster.
- « … » marque une courte pause.
- Dans la voix, les nombres sont écrits en lettres et les sigles avec des tirets pour être épelés. L'écran affiche les chiffres exacts.
- Durée visée : environ 7 minutes, environ 6 500 caractères. Chaque scène fait moins de 5 000 caractères, la limite d'une génération.

---

## Scène 1 : l'accroche (environ 20 s)

**Écran** : une carte de France et du monde. 530 points s'allument un à un, puis des traits les relient à deux centres. Titre : « Le projet RAO en 5 minutes ».

**Voix** :
[curious] Comment protéger cinq cent trente sites, dix mille utilisateurs et des données de santé… sans faire exploser le budget ?
C'est la question que nous a posée notre client. [excited] Voici notre réponse, en cinq minutes.

---

## Scène 2 : le client (environ 45 s)

**Écran** : trois compteurs qui défilent : 530 sites (2 sièges, 498 agences en France, 30 à l'international), 10 000 utilisateurs, environ 100 partenaires. Puis un pictogramme de dossier médical, avec un cadenas qui se ferme.

**Voix** :
Notre client est une grande mutuelle santé, fictive. Deux sièges, quatre cent quatre-vingt-dix-huit agences en France, trente à l'étranger. Dix mille utilisateurs. Et une centaine de partenaires, qui doivent eux aussi accéder à certaines applications.
[serious] Le point sensible, ce sont les données : des informations de santé. Une fuite, et c'est la confiance des adhérents qui s'effondre.
Le client lance donc un appel d'offres : il veut une nouvelle architecture de sécurité, pour ses centres de données comme pour ses agences.

---

## Scène 3 : ce que le client va noter (environ 30 s)

**Écran** : trois cartes qui se retournent l'une après l'autre : « 1. Les équipements », « 2. Les schémas d'architecture », « 3. Le coût par poste ». Sur la troisième, un tampon « abonnement de préférence ».

**Voix** :
Il annonce trois critères. Un : pour chaque fonction, l'équipement retenu, et pourquoi. Deux : les schémas d'architecture, pour le centre de données et pour les agences. Trois : le coût, poste par poste… avec une préférence nette pour l'abonnement plutôt que l'achat.

---

## Scène 4 : la solution en quatre briques (environ 2 min 10)

### 4a. Relier les sites (environ 35 s)

**Écran** : un site reçoit un boîtier FortiGate, puis deux accès Internet (opérateurs A et B). Les tunnels se dessinent vers les deux centres de données et des paquets y circulent. Puis la ligne A se coupe en rouge, le trafic repart par la ligne B, et un compteur affiche « 3,8 s, mesurées sur notre maquette ».

**Voix** :
Notre solution tient en quatre briques.
Première brique : relier les sites. Chaque site reçoit un pare-feu FortiGate. Avec ses deux accès à Internet, il monte des tunnels chiffrés vers les deux centres de données. C'est ce qu'on appelle le S-D-WAN : un réseau étendu piloté par logiciel, qui choisit à chaque instant le meilleur chemin.
[excited] Et si un opérateur tombe ? Le trafic bascule sur l'autre… en moins de quatre secondes.

### 4b. Deux centres de données (environ 30 s)

**Écran** : deux bâtiments marqués « HDS ». Les applications s'allument dans les deux, puis une flèche de copie part de l'un vers l'autre. Un coffre-fort « sauvegarde immuable » se ferme.

**Voix** :
Deuxième brique : deux centres de données, chez des hébergeurs certifiés pour les données de santé, H-D-S. Les applications publiées tournent dans les deux. Les bases sont copiées de l'un vers l'autre. Et une sauvegarde immuable, que même un attaquant ne peut pas effacer.

### 4c. Filtrer chaque échange (environ 35 s)

**Écran** : de gauche à droite, Internet, puis le pare-feu de périmètre, puis la zone tampon (pare-feu applicatif web, passerelle de transfert chiffré), puis le pare-feu interne et cinq zones (DMZ, applications, données, administration, partenaires).
- Un paquet va du serveur web à l'application : il passe, en vert.
- Un paquet va du serveur web directement à la base : il est stoppé devant elle, avec une croix rouge.
- Un administrateur passe par le bastion : une ligne « action tracée » s'affiche.

**Voix** :
Troisième brique : filtrer chaque échange. Ce qui vient d'Internet s'arrête dans une zone tampon, la D-M-Z, où un pare-feu applicatif bloque les attaques web. Derrière, un second pare-feu découpe le centre de données en cinq zones.
[serious] La règle est simple : tout est interdit, sauf ce qui est explicitement autorisé. Le serveur web parle à l'application… jamais directement à la base de données. Et les administrateurs passent tous par un bastion, qui trace chaque action.

### 4d. Ceux qui travaillent à distance (environ 30 s)

**Écran** : à gauche, des salariés nomades (3 000) et des partenaires (environ 60 organisations). Un cadenas « second facteur » s'ouvre, puis seule l'application de l'utilisateur s'allume, le reste du réseau restant sombre. À droite, en grisé, « VPN classique » : tout le réseau s'allume, avec un poste piraté en rouge au milieu.

**Voix** :
Quatrième brique : ceux qui travaillent à distance. Trois mille salariés nomades, et les utilisateurs des partenaires. Ici, on applique le Zéro Confiance, le Z-T-N-A : chacun prouve son identité avec un second facteur, puis n'atteint que ses applications… jamais le réseau entier.
[curious] La différence avec un réseau privé virtuel classique, un V-P-N ? Un poste piraté ne devient plus une porte d'entrée.

---

## Scène 5 : combien ça coûte (environ 45 s)

**Écran** :
1. Un grand compteur défile jusqu'à « 221 424 € HT par mois, sur 36 mois ».
2. Deux petites cartes : « 22,14 € par utilisateur et par mois », « 418 € par site et par mois ».
3. « Coût total sur 36 mois : 7,97 M€ ».
4. Une balance : à gauche, l'achat, avec « 4,22 M€ à avancer » ; à droite, l'abonnement, avec « environ 470 000 € de plus sur 3 ans, rien à avancer ». La balance penche vers l'abonnement.

**Voix** :
Combien ça coûte ?… Environ deux cent vingt et un mille euros hors taxes par mois, sur trois ans. Rapporté à chacun : vingt-deux euros par utilisateur et par mois. Sur trente-six mois, le coût total atteint près de huit millions d'euros.
L'abonnement coûte un peu plus cher que l'achat : environ quatre cent soixante-dix mille euros de plus sur trois ans. Mais le client n'a pas à avancer quatre virgule deux millions d'euros dès le départ. [excited] C'est exactement ce qu'il demandait.

---

## Scène 6 : la preuve (environ 50 s)

**Écran** : le schéma de la maquette (7 routeurs, 8 serveurs et postes). Une liste de tests se coche ligne par ligne, avec un compteur qui monte jusqu'à « 17 / 17 ». Puis la bascule rejouée : coupure, chronomètre, « 3,8 s ». À la fin, un bandeau « prouve nos principes, pas les produits ».

**Voix** :
[excited] Et nous ne nous sommes pas contentés d'un dossier. Nous avons construit une maquette : quinze machines, qui reproduisent un siège, une agence, un partenaire, les opérateurs et les centres de données.
Dix-sept tests : les échanges autorisés passent, les interdits sont bloqués et journalisés. Résultat… dix-sept sur dix-sept.
On coupe un opérateur en pleine démonstration : le trafic bascule en trois virgule huit secondes.
[serious] Et nous le disons franchement au jury : la maquette prouve nos principes, pas les produits Fortinet eux-mêmes.

---

## Scène 7 : les limites que nous assumons (environ 40 s)

**Écran** : quatre cartes qui arrivent l'une après l'autre, avec un liseré rouge :
1. « FortiGate 600F : successeur probable, le 700G, rechiffré au devis » ;
2. « Licence Zéro Confiance des 4 pare-feu d'entrée : non incluse » ;
3. « Stockage : extension probable » ;
4. « HDS : pas forcément obligatoire, exigé par prudence ».

**Voix** :
Une bonne offre dit aussi ses limites. Nous en assumons quatre.
Le pare-feu prévu à l'entrée des centres de données, le six cents F, n'est plus commercialisé : son successeur probable sera rechiffré au devis.
La licence Zéro Confiance des quatre pare-feu d'entrée n'est pas incluse dans le prix.
Le stockage prévu sera sans doute trop juste : une extension est probable.
Et la certification H-D-S n'est pas forcément obligatoire pour une mutuelle… nous l'exigeons par prudence.

---

## Scène 8 : l'équipe (environ 40 s)

**Écran** : sept cartes alignées dans l'ordre de passage, chacune avec un prénom et un rôle : Farah (chef de projet), Valentin (réseau entre les sites), Nolan (centres de données), Fatih (filtrage des échanges), Younes (exploitation et agences), Maxime (accès Zéro Confiance), Diane (coûts). Puis trois flèches de retour : Valentin (démonstration), Younes (risques), Farah (conclusion).

**Voix** :
Le jour de la soutenance, nous sommes sept, avec un domaine chacun.
Farah ouvre et pilote le projet. Valentin présente le réseau entre les sites. Nolan, les centres de données. Fatih, le filtrage des échanges. Younes, l'exploitation et les agences. Maxime, l'accès Zéro Confiance. Et Diane, les coûts.
Valentin, Younes et Farah reviennent à la fin : pour la démonstration, les risques… et la conclusion.

---

## Scène 9 : la fin (environ 15 s)

**Écran** : « Une architecture sécurisée pour 530 sites, en abonnement », puis trois chiffres : 221 424 € HT/mois · 17/17 tests · 3,8 s de bascule. En petit en bas : « Voix générée par intelligence artificielle (ElevenLabs) ».

**Voix** :
Cinq cent trente sites protégés, un prix au mois, et des preuves. [excited] Voilà notre réponse.

---

## Chiffres à vérifier dans le dépôt avant de générer la voix

Tous viennent de `docs/CHIFFRAGE.md`, `docs/OFFRE_TECHNIQUE.md`, `docs/QUESTIONS_JURY.md` et du suivi du projet :

| Chiffre | Valeur |
|---|---|
| Sites | 530 : 2 sièges, 498 agences en France, 30 à l'international |
| Utilisateurs | 10 000 |
| Partenaires | environ 100, dont 40 % site à site et 60 % nomades (environ 60 organisations, 300 utilisateurs) |
| Nomades | 3 000 salariés (hypothèse H6) |
| Prix | 221 424 € HT par mois, sur 36 mois |
| Par utilisateur | 22,14 € par mois |
| Par site | 418 € par mois |
| Coût total sur 36 mois | 7,97 M€ |
| Abonnement face à l'achat | environ 470 000 € de plus sur 3 ans ; évite d'avancer 4,22 M€ |
| Maquette | 15 machines (7 routeurs dans EVE-NG, 8 serveurs et postes en conteneurs), 17 tests sur 17 |
| Bascule | 3,8 s (valeur des diapos) |
