#!/bin/bash
# Comptes Proxmox personnels des membres du groupe (interface https://localhost:8006, via le tunnel de 05_acces_camarades.sh).
# Droits limités au lab : voir, ouvrir la console, démarrer et arrêter la VM EVE-NG (200) et les conteneurs 301 à 308,
# et voir l'état du serveur. Ni création, ni suppression, ni modification de configuration, ni accès aux autres machines.
# Usage en root : bash 06_comptes_proxmox.sh farah valentin nolan   (un mot de passe provisoire est demandé pour chaque nouveau compte ;
#                 le transmettre en privé, jamais dans le dépôt ; chacun le change ensuite : menu de son nom > Password)
# Retirer un membre : pveum user delete <prénom>@pve
set -euo pipefail
[ $# -ge 1 ] || { echo "Usage : bash $0 prénom1 [prénom2 …]"; exit 1; }
GROUPE=rao-lab
ROLE=RAOLab
VMS="200 301 302 303 304 305 306 307 308"

pveum role add "$ROLE" --privs "VM.Audit VM.Console VM.PowerMgmt" 2>/dev/null \
  || pveum role modify "$ROLE" --privs "VM.Audit VM.Console VM.PowerMgmt"
pveum group add "$GROUPE" --comment "Membres du projet RAO" 2>/dev/null || true
for vm in $VMS; do pveum acl modify "/vms/$vm" --groups "$GROUPE" --roles "$ROLE"; done
pveum acl modify "/nodes/$(hostname)" --groups "$GROUPE" --roles PVEAuditor   # état du serveur, en lecture seule

for p in "$@"; do
  nom=${p,,}
  [[ $nom =~ ^[a-z][a-z0-9._-]{1,30}$ ]] || { echo "Nom refusé (lettres sans accent, chiffres, . _ -) : $p"; continue; }
  u="$nom@pve"
  if pveum user list --output-format json | grep -q "\"$u\""; then
    pveum user modify "$u" --groups "$GROUPE" --append 1
    echo "$u existe déjà : ajouté au groupe $GROUPE"
  else
    pveum user add "$u" --groups "$GROUPE" --comment "Projet RAO"
    echo "Mot de passe provisoire de $u :"
    pveum passwd "$u"
  fi
done
pveum group list
