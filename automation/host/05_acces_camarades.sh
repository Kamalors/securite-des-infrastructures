#!/bin/bash
# Accès des membres du groupe aux interfaces web d'EVE-NG et de Proxmox (client : automation/connexion_rao.ps1
# ou automation/Demo_RAO.cmd). Compte partagé « camarade » : ni mot de passe ni shell ; chaque clé ne peut ouvrir
# que deux tunnels : EVE-NG (10.99.0.10:443) et l'interface Proxmox (127.0.0.1:8006). Se connecter à Proxmox
# demande en plus un compte personnel : 06_comptes_proxmox.sh.
# Usage en root : bash 05_acces_camarades.sh        puis coller la clé publique reçue (ligne « ssh-ed25519 … rao-prenom »)
# Retirer un membre : supprimer sa ligne dans /home/camarade/.ssh/authorized_keys (effet immédiat pour les connexions suivantes).
set -euo pipefail
U=camarade
AK=/home/$U/.ssh/authorized_keys

CLE=${1:-}
[ -n "$CLE" ] || read -rp "Clé publique : " CLE
CLE=${CLE//$'\r'/}   # collage depuis Windows
# Une clé nue uniquement : refuse les options (command=, permitopen=…) qui contourneraient les restrictions
[[ $CLE =~ ^(ssh-ed25519|ecdsa-sha2-nistp(256|384|521)|ssh-rsa)\ [A-Za-z0-9+/]+=*(\ [^[:cntrl:]]*)?$ ]] \
  && echo "$CLE" | ssh-keygen -lf - >/dev/null || { echo "Clé invalide : rien changé"; exit 1; }

if ! id "$U" &>/dev/null; then
  useradd -m -s /usr/sbin/nologin "$U"
  usermod -p '*' "$U"   # aucun mot de passe possible, sans « verrou » que sshd refuserait
fi
# Fichier à root : le compte ne peut pas lever ses propres restrictions
install -d -m 755 -o root -g root "/home/$U/.ssh"
[ -f "$AK" ] || install -m 644 -o root -g root /dev/null "$AK"

# Clés autorisées avant l'ouverture de Proxmox : on leur ajoute le tunnel vers son interface web
sed -i '/permitopen="127.0.0.1:8006"/! s/permitopen="10.99.0.10:443"/permitopen="10.99.0.10:443",permitopen="127.0.0.1:8006"/' "$AK"

if grep -qF "$(echo "$CLE" | cut -d' ' -f2)" "$AK"; then echo "Clé déjà autorisée"; exit 0; fi
echo "restrict,port-forwarding,permitopen=\"10.99.0.10:443\",permitopen=\"127.0.0.1:8006\" $CLE" >> "$AK"
echo "Autorisée : $(echo "$CLE" | ssh-keygen -lf -)"
echo "Membres autorisés : $(grep -c . "$AK")"
