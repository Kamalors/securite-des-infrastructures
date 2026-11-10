#!/bin/bash
# Sécurité P0 de PAR861454 (plan v2 §4) : Proxmox lié à localhost + pare-feu nftables de l'hôte.
# À lancer en root depuis une session SSH (su -), PAS depuis la console web Proxmox : le redémarrage
# de pveproxy coupe cette console et arrête le script en cours de route. Relançable. Une minuterie retire le pare-feu au bout de 5 minutes :
# ouvrir une 2e session SSH pour vérifier l'accès, puis confirmer avec la commande affichée à la fin.
set -euo pipefail

echo "== Interface Proxmox (8006) et proxy SPICE (3128) sur 127.0.0.1 uniquement =="
if grep -q '^LISTEN_IP=' /etc/default/pveproxy 2>/dev/null; then
  echo "LISTEN_IP déjà réglé"
else
  echo 'LISTEN_IP="127.0.0.1"' >> /etc/default/pveproxy
  systemctl restart pveproxy spiceproxy   # coupe les sessions web ouvertes ; le tunnel SSH reste valable
fi

echo "== Pare-feu de l'hôte =="
[ -f /etc/nftables.conf.orig ] || cp -a /etc/nftables.conf /etc/nftables.conf.orig
cat > /etc/nftables.conf <<'EOF'
#!/usr/sbin/nft -f
# Pare-feu de l'hôte PAR861454. Pas de "flush ruleset" : il effacerait le NAT de vmbr1 (iptables-nft).
table inet hostfw
delete table inet hostfw
table inet hostfw {
  chain input {
    type filter hook input priority 0; policy drop;
    ct state established,related accept
    ct state invalid drop
    iif lo accept
    meta l4proto { icmp, ipv6-icmp } accept
    tcp dport 22 accept
    limit rate 5/minute log prefix "hostfw-in-drop "
  }
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    # Défensif : si br_netfilter est chargé un jour (pare-feu Proxmox), le trafic ponté du lab passerait ici
    iifname "vmbr2" oifname "vmbr2" accept
    iifname "vmbr1*" oifname "vmbr1*" accept
    # VM EVE et conteneur de contrôle vers Internet : ports utiles seulement, jamais vers les réseaux privés
    iifname "vmbr1" oifname "vmbr0" ip daddr != { 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 } meta l4proto { tcp, udp } th dport { 53, 80, 123, 443 } accept
    iifname "vmbr1" oifname "vmbr0" icmp type echo-request accept
    limit rate 5/minute log prefix "hostfw-fwd-drop "
  }
}
EOF
nft -c -f /etc/nftables.conf

# Filet de sécurité : sans confirmation, la table est retirée dans 5 minutes
systemctl stop fwrb.timer 2>/dev/null || true
systemctl reset-failed fwrb.timer fwrb.service 2>/dev/null || true
systemd-run --on-active=5min --unit=fwrb /usr/sbin/nft delete table inet hostfw
nft -f /etc/nftables.conf

echo "== Vérifications =="
sleep 2
ss -tlnH | awk '{print $4}' | grep -E ':(8006|3128)$' || true   # attendu : 127.0.0.1 uniquement
nft list chain inet hostfw input | grep -c accept || true
echo
echo "Pare-feu actif pour 5 minutes. Ouvre MAINTENANT une 2e session SSH depuis ton PC."
echo "Si elle fonctionne, rends-le permanent :  systemctl stop fwrb.timer && systemctl enable nftables"
echo "Sinon, ne fais rien : il se retire tout seul dans 5 minutes."
# Retour arrière complet : nft delete table inet hostfw ; systemctl disable nftables ;
#   cp -a /etc/nftables.conf.orig /etc/nftables.conf ; sed -i '/^LISTEN_IP=/d' /etc/default/pveproxy ;
#   systemctl restart pveproxy spiceproxy
