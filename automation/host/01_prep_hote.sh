#!/bin/bash
# Préparation de l'hôte Proxmox PAR861454 pour la future VM EVE-NG.
# À lancer en root sur l'hôte. Relançable : ne refait rien si c'est déjà en place.
# Ne touche pas à vmbr0 (accès de gestion). Retour arrière en fin de fichier.
set -euo pipefail

echo "== Virtualisation imbriquée =="
cat /sys/module/kvm_intel/parameters/nested   # attendu : Y (ou 1)

echo "== Bridge interne vmbr1 (10.99.0.1/24, NAT vers vmbr0) =="
if grep -q '^auto vmbr1$' /etc/network/interfaces; then
  echo "vmbr1 déjà déclaré, rien à faire"
else
  cp -a /etc/network/interfaces "/etc/network/interfaces.bak-$(date +%Y%m%d-%H%M%S)"
  cat >> /etc/network/interfaces <<'EOF'

auto vmbr1
iface vmbr1 inet static
	address 10.99.0.1/24
	bridge-ports none
	bridge-stp off
	bridge-fd 0
	post-up   echo 1 > /proc/sys/net/ipv4/ip_forward
	post-up   iptables -t nat -A POSTROUTING -s 10.99.0.0/24 -o vmbr0 -j MASQUERADE
	post-down iptables -t nat -D POSTROUTING -s 10.99.0.0/24 -o vmbr0 -j MASQUERADE
#Lab EVE-NG RAO (NAT interne)
EOF
  ifup vmbr1   # monte uniquement vmbr1, pas de rechargement global
fi

echo "== Ponts du lab : ni IP, ni NAT, ni port physique (correspondance : inventory/addressing.csv) =="
# vmbr2 gestion lab | vmbr10 dc1-dmz | vmbr11 dc1-app | vmbr12 dc1-data | vmbr13 dc1-adm
# vmbr14 agfr-lan | vmbr15 inet-cli | vmbr16 agfr-invites
manquants=()
for br in vmbr2 vmbr10 vmbr11 vmbr12 vmbr13 vmbr14 vmbr15 vmbr16; do
  grep -q "^auto $br\$" /etc/network/interfaces || manquants+=("$br")
done
if [ ${#manquants[@]} -gt 0 ]; then
  cp -a /etc/network/interfaces "/etc/network/interfaces.bak-$(date +%Y%m%d-%H%M%S)"
  for br in "${manquants[@]}"; do
    printf '\nauto %s\niface %s inet manual\n\tbridge-ports none\n\tbridge-stp off\n\tbridge-fd 0\n#Lab RAO\n' "$br" "$br" >> /etc/network/interfaces
    ifup "$br"
  done
fi

echo "== Vérifications =="
ip -br link show type bridge
ip -br addr show vmbr1
ip -br addr show vmbr0          # doit être inchangé
sysctl net.ipv4.ip_forward
iptables -t nat -S POSTROUTING | grep 10.99.0.0/24

# Retour arrière :
#   ifdown vmbr1 && cp -a /etc/network/interfaces.bak-<horodatage> /etc/network/interfaces
