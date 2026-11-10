# Accéder au projet, à EVE-NG et à Proxmox

Deux parties : **pour les membres du groupe** (Farah, Valentin, Nolan, Fatih, Younes, Diane), puis **pour le responsable du serveur** (Maxime), qui autorise les accès.

Rien de secret ne passe par ce dépôt : chacun garde sa clé privée sur son PC et reçoit ses mots de passe en privé.

---

## Partie 1 — Membres du groupe

### 1. Récupérer le projet

Accepte l'invitation GitHub reçue par e-mail, puis :

```powershell
git clone https://github.com/Kamalors/securite-des-infrastructures.git
```

Sans Git : sur la page du dépôt, **Code > Download ZIP**, puis décompresse.

### 2. Créer ta clé et la faire autoriser (une seule fois)

1. Dans le dossier du projet, clic droit sur `automation\connexion_rao.ps1` > **Exécuter avec PowerShell**.
2. Le script crée ta clé SSH (une phrase de passe est conseillée), puis tente la connexion. La première fois, elle est refusée : c'est normal.
3. Ta **clé publique** est alors copiée dans le presse-papiers (une ligne qui commence par `ssh-ed25519` et finit par `rao-<ton nom>`). Envoie-la à Maxime. Elle n'est pas secrète. Ta clé privée, elle, ne quitte jamais ton PC.
4. Attends la confirmation de Maxime, qui te transmet aussi tes identifiants EVE-NG et Proxmox, en privé.

Le client OpenSSH est inclus dans Windows 10 et 11. S'il manque : Paramètres > Système > Fonctionnalités facultatives > « Client OpenSSH ».

### 3. Se connecter

Au choix :

- **Fenêtre de démonstration** : double-clic sur `automation\Demo_RAO.cmd`, puis **Ouvrir EVE-NG** ou **Ouvrir Proxmox**.
- **Script simple** : relance `automation\connexion_rao.ps1`. EVE-NG s'ouvre dans le navigateur ; Proxmox est sur https://localhost:8006. Garde la fenêtre ouverte : la fermer coupe l'accès.

Le navigateur signale un certificat auto-signé : accepte l'avertissement.

| Interface | Adresse | Identifiants |
|---|---|---|
| EVE-NG | https://localhost:8443, lab **RAO** | ton compte EVE-NG |
| Proxmox | https://localhost:8006 | ton compte, royaume **Proxmox VE authentication server** |

À ta première connexion à Proxmox, change ton mot de passe : menu à ton nom, en haut à droite > **Password**.

### 4. Ce que tu peux faire

- **EVE-NG** : ouvrir le lab RAO et la console de chaque nœud (clic sur le nœud). La démonstration pas à pas est dans `docs/DEMO_EVE.md`.
- **Proxmox** : voir la VM EVE-NG (200) et les conteneurs du lab (301 à 308), ouvrir leur console, les démarrer ou les arrêter. Tu ne peux rien créer, supprimer ni reconfigurer, ni voir les autres machines du serveur.
- Les **tests automatiques** de la fenêtre de démonstration (étapes 1 à 7) demandent la clé d'administration : ils se lancent depuis le PC de Maxime.

### 5. Si ça ne marche pas

| Message | Cause | Solution |
|---|---|---|
| `Permission denied (publickey)` | Ta clé n'est pas encore autorisée | Envoie ta clé publique à Maxime (elle est dans le presse-papiers) |
| Port 8443 ou 8006 déjà utilisé | Un tunnel est déjà ouvert dans une autre fenêtre | Ouvre directement l'adresse dans le navigateur |
| Proxmox : « Login failed » | Mauvais royaume ou mot de passe | Choisis le royaume **Proxmox VE authentication server** |
| EVE-NG ne charge pas | La VM ou le lab est arrêté | Préviens Maxime ; dans Proxmox, tu peux démarrer la VM 200 |

Sur Mac ou Linux, après `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_rao` et l'autorisation de ta clé :

```bash
ssh -N -L 8443:10.99.0.10:443 -L 8006:127.0.0.1:8006 -i ~/.ssh/id_ed25519_rao camarade@163.172.105.87
```

---

## Partie 2 — Responsable du serveur (Maxime)

### Inviter quelqu'un sur le dépôt

Sur GitHub : **Settings > Collaborators > Add people**, ou en ligne de commande :

```powershell
gh api -X PUT repos/Kamalors/securite-des-infrastructures/collaborators/<pseudo-github>
```

### Avant de partager l'accès : changer le mot de passe d'usine d'EVE-NG

Le compte web `admin` d'EVE-NG a encore son mot de passe d'usine. Change-le avant d'ouvrir l'accès à qui que ce soit.

### Autoriser une clé et créer les comptes (en root sur le serveur)

Depuis le dossier du projet, sur ton PC :

```powershell
scp -F automation/ssh_config automation/host/05_acces_camarades.sh automation/host/06_comptes_proxmox.sh lab-host:/tmp/
ssh -t -F automation/ssh_config lab-host
```

Puis, sur le serveur (`su -` ou `sudo` te demande ton mot de passe root ; tape-le toi-même) :

```bash
# une fois par membre : colle la clé publique reçue
bash /tmp/05_acces_camarades.sh
# comptes Proxmox personnels (un mot de passe provisoire demandé pour chaque nouveau compte)
bash /tmp/06_comptes_proxmox.sh farah valentin nolan fatih younes diane
```

- `05_acces_camarades.sh` : compte partagé `camarade`, sans mot de passe ni shell. Chaque clé n'ouvre que deux tunnels : EVE-NG (`10.99.0.10:443`) et l'interface Proxmox (`127.0.0.1:8006`). Les clés autorisées avant cette version reçoivent automatiquement le second tunnel.
- `06_comptes_proxmox.sh` : groupe `rao-lab` et rôle `RAOLab` (voir, console, démarrer et arrêter) sur la VM 200 et les conteneurs 301 à 308, plus la lecture seule de l'état du serveur.
- **Comptes EVE-NG** : dans l'interface web d'EVE-NG, en `admin` : **Management > User management > Add user**, un compte par membre. Si l'édition Freemium refuse d'en créer, partage un compte unique en privé, jamais dans le dépôt.

Transmets chaque mot de passe en privé (message direct), jamais dans le dépôt ni dans un canal de groupe.

### Retirer un accès

| Accès | Commande ou action |
|---|---|
| Tunnel SSH | Supprimer sa ligne dans `/home/camarade/.ssh/authorized_keys` |
| Proxmox | `pveum user delete <prénom>@pve` |
| EVE-NG | Management > User management > supprimer le compte |
| Dépôt GitHub | Settings > Collaborators > Remove |
