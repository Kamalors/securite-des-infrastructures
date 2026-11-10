#!/bin/bash
# Crée la VM EVE-NG (VMID 200) sur PAR861454, dimensionnement du plan v2 §2.1. À lancer en root.
# Prérequis : 03_p0_securite.sh puis 01_prep_hote.sh appliqués (vmbr1, vmbr2, vmbr10 à vmbr16).
set -euo pipefail
ISO=eve-pro-prod-bm-7.2.0-18-full.iso
SRC=/home/administrateur/$ISO
DST=/var/lib/vz/template/iso/$ISO

qm status 200 >/dev/null 2>&1 && { echo "VM 200 existe déjà, rien à faire"; exit 0; }
for br in vmbr1 vmbr2 vmbr10 vmbr11 vmbr12 vmbr13 vmbr14 vmbr15 vmbr16; do
  ip link show "$br" >/dev/null || { echo "Pont $br absent : lancer 01_prep_hote.sh"; exit 1; }
done

# ISO téléchargée par administrateur : rangée dans le stockage local de Proxmox
if [ ! -f "$DST" ] && [ -f "$SRC" ]; then mv "$SRC" "$DST" && chown root:root "$DST"; fi
test -f "$DST"
ls -l "$DST"          # attendu : 10775506944 octets
sha256sum "$DST"      # à reporter dans inventory/images.yml

# 6 vCPU sur 8 threads (marge pour l'hôte), RAM fixe, cartes sans pare-feu Proxmox (pas de filtre MAC)
qm create 200 --name eve-ng-rao --ostype l26 \
  --memory 20480 --balloon 0 --sockets 1 --cores 6 --cpu host \
  --scsihw virtio-scsi-single --scsi0 local:200,format=qcow2,iothread=1,discard=on,ssd=1 \
  --net0 virtio,bridge=vmbr1 --net1 virtio,bridge=vmbr2 \
  --net2 virtio,bridge=vmbr10 --net3 virtio,bridge=vmbr11 --net4 virtio,bridge=vmbr12 \
  --net5 virtio,bridge=vmbr13 --net6 virtio,bridge=vmbr14 --net7 virtio,bridge=vmbr15 \
  --net8 virtio,bridge=vmbr16 \
  --ide2 "local:iso/$ISO,media=cdrom" \
  --boot 'order=ide2;scsi0'
qm start 200
qm status 200
# Dans EVE, netN = ethN = pnetN : pnet0 gestion EVE (10.99.0.10/24, passerelle 10.99.0.1, DNS 1.1.1.1),
#   Cloud1 = gestion lab (vmbr2), Cloud2 dc1-dmz, Cloud3 dc1-app, Cloud4 dc1-data, Cloud5 dc1-adm,
#   Cloud6 agfr-lan, Cloud7 inet-cli, Cloud8 agfr-invites.
# IMPORTANT : quand l'installeur affiche « Reboot Now », AVANT de valider :
#   qm stop 200 && qm set 200 --ide2 none --boot order=scsi0 && qm start 200
# sinon la VM redémarre sur l'ISO et relance l'installation en boucle. Ensuite supprimer l'ISO (10,8 Go).
# Retour arrière : qm stop 200 && qm destroy 200   (supprime aussi le disque)
