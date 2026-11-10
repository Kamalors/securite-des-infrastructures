# Rapport d'incident — serveur Proxmox PAR861454

Rédigé le 16/10/2026 (CEST). Constats faits depuis le système en marche, donc potentiellement faussés par le rootkit : **à confirmer depuis le mode rescue**.
Aucune modification de remédiation n'a été faite. Aucun mot de passe ne figure dans ce document.

## Résumé

Une bibliothèque injectée (`/usr/local/lib/sshdd.so`) est chargée par les processus du système, dont `unix_chkpwd`, qui vérifie les mots de passe. Elle cache ses propres fichiers à root et bloque les renommages dans `/var/log`. Conclusion : **compromission root probable depuis au moins le 01/10/2026 à 18:37 CEST**, avec risque de vol d'identifiants.

## Indicateurs de compromission

| Indicateur | Valeur |
|---|---|
| Fichier | `/usr/local/lib/sshdd.so`, 32 688 octets, mtime 2026-10-01 18:37:05.105946180 +0200, n'appartient à aucun paquet Debian (`dpkg -S`) |
| Dossier | `/usr/local/lib/` modifié le 2026-10-01 18:37:04 +0200 |
| Verrou | `/run/sshdd.lock` |
| Préchargement | `/etc/ld.so.preload` illisible pour root (`Permission denied`) : fichier caché par le hook |
| Processus porteurs | 11 processus ont `sshdd` dans `/proc/*/maps`, dont `unix_chkpwd` |
| Journal noyau | `apparmor="ALLOWED" … profile="unix-chkpwd" name="/usr/local/lib/sshdd.so"` (file_mmap, file_mprotect), puis open/lock sur `/run/sshdd.lock` et open sur `/proc/` |
| Empreinte SHA256 | Non obtenue (lecture refusée par le hook) : à calculer depuis le mode rescue |

## Éléments probants

1. `mv /var/log/t1 /var/log/t2` → `Permission denied` en root, avec CapEff=000001ffffffffff, ext4 en rw, sans attribut chattr, avec AppArmor `unconfined` pour le shell et pour pvedaemon.
2. Le même renommage par appel système direct (`perl syscall(82, …)`) → **réussit**. Le refus vient donc d'une fonction de la libc détournée, pas du noyau.
3. Effet visible : toutes les tâches Proxmox échouent (`close (rename) atomic file '/var/log/pve/tasks/active' failed: Permission denied`). Observé dès le 15/10 vers 11:57 CEST.

## Autres observations à analyser

- Bruit AppArmor massif (plus de 55 M d'événements d'audit) généré par `ntpd` et `named`.
- Fichiers d'origine inconnue dans `/root` (`pb.sh`, `max.sh`, `resume.sh`, `deploy*.pid`/`.log`, `artemis*`, `Infra-Garah`) et dans `/tmp` (`sshd.txt`, `crontab_list.txt`). Ils peuvent appartenir à d'autres projets : non ouverts.
- Exposition : IP publique, SSH par mot de passe, mots de passe faibles circulant dans un script partagé. Test depuis l'extérieur le 16/10 : `sd-115254.dedibox.fr` = 163.172.105.87 ; **22/tcp ouvert sur Internet**, 8006/tcp fermé (Proxmox joint seulement par tunnel). Point d'entrée le plus probable : SSH, à vérifier dans les journaux d'authentification autour du 01/10.

## Identifiants à considérer comme compromis

Tous les mots de passe saisis sur l'hôte depuis le 01/10 : SSH (`administrateur`, root), `sudo`/`su`, connexion PAM à l'interface Proxmox (root@pam). Également le token API `root@pam!claude-audit` (secret non conservé, mais à supprimer).

## Recommandations

1. Ne plus saisir d'identifiant sur l'hôte. Prévenir le responsable du serveur et l'équipe.
2. Démarrer en mode rescue chez l'hébergeur. Acquérir les preuves : image disque si possible, sinon `sshdd.so`, `ld.so.preload`, `/var/log`, crontabs, unités systemd, `/etc/pam.d`, `sshd_config`, `authorized_keys`, `/etc/passwd` et `/etc/shadow`. Calculer les empreintes.
3. Rechercher la persistance et le point d'entrée (journaux d'authentification autour du 01/10 18:37, binaires modifiés via `debsums`).
4. Changer tous les identifiants depuis une machine saine.
5. Réinstaller l'hôte. Durcir : clés SSH uniquement, `PermitRootLogin no`, SSH et 8006 fermés à Internet (VPN ou liste d'IP), double authentification sur Proxmox, fail2ban, journaux envoyés hors de l'hôte.
6. Analyser la VM 101 avant toute remise en service.
