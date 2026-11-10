#!/bin/bash
# Crée les 8 conteneurs LXC du lab (hôtes et clients), reliés aux nœuds réseau d'EVE par les ponts vmbr10-16.
# Décision D1 : EVE Freemium garde les 7 nœuds réseau, les hôtes tournent en LXC sur Proxmox.
# À lancer en root sur l'hôte (SSH + su -). Relançable : un conteneur existant est ignoré.
# Prérequis : 01_prep_hote.sh appliqué ; clé publique d'administration copiée dans /tmp/cle_lab.pub.
set -euo pipefail
CLE=/tmp/cle_lab.pub
test -s "$CLE"

# Modèle Debian 13 officiel Proxmox
pveam update >/dev/null
T=$(pveam available --section system | awk '/debian-13-standard_.*_amd64/ {print $2}' | sort -V | tail -1)
[ -n "$T" ]
[ -f "/var/lib/vz/template/cache/$T" ] || pveam download local "$T"

# id nom pont ip/masque passerelle(nœud EVE) RAM(Mo) — source : inventory/addressing.csv
while read -r id nom pont ip gw ram; do
  pct status "$id" >/dev/null 2>&1 && { echo "CT $id ($nom) existe déjà"; continue; }
  pct create "$id" "local:vztmpl/$T" --hostname "$nom" --unprivileged 1 --features nesting=1 \
    --cores 1 --memory "$ram" --swap 0 --rootfs local:4 \
    --net0 "name=eth0,bridge=$pont,ip=$ip,gw=$gw" \
    --net1 "name=eth1,bridge=vmbr2,ip=10.98.0.$((id - 200))/24" \
    --ssh-public-keys "$CLE" --onboot 0 --start 1
  echo "CT $id ($nom) créé : $ip sur $pont, gestion 10.98.0.$((id - 200))"
done <<'EOF'
301 srv-web vmbr10 10.11.10.10/24 10.11.10.1 256
302 srv-app vmbr11 10.11.20.20/24 10.11.20.1 256
303 srv-db vmbr12 10.11.30.30/24 10.11.30.1 512
304 bastion vmbr13 10.11.99.10/24 10.11.99.1 256
305 logs vmbr13 10.11.99.20/24 10.11.99.1 512
306 cli-ag vmbr14 10.40.1.10/24 10.40.1.1 256
307 cli-ext vmbr15 192.0.2.10/24 192.0.2.1 256
308 cli-inv vmbr16 10.40.2.10/24 10.40.2.1 256
EOF

pct list
# Retour arrière : for i in $(seq 301 308); do pct stop $i; pct destroy $i; done
