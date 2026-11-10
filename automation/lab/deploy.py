"""Configure le lab RAO : adressage, routage (OSPF), tunnels IPsec route-based (XFRM), filtrage nftables
selon docs/FLUX.md, envoi des journaux, services de test. Tout est poussé par SSH (automation/ssh_config).
Relançable : chaque exécution réécrit les fichiers et régénère les clés IPsec (aucun secret stocké).
Usage depuis la racine du projet : python automation/lab/deploy.py [nom ...]   (sans argument : tout)
"""
import pathlib
import secrets
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SSH = ["ssh", "-F", "automation/ssh_config"]
LOGS = "10.98.0.105"  # collecteur (conteneur logs), joint par le réseau de gestion

# Adressage (inventory/addressing.csv) ; eth0 = gestion en DHCP, déjà configurée dans l'image
ROUTEURS = {
    "isp-a": {"eth1": "198.51.100.1/24", "eth2": "192.0.2.1/24", "eth3": "100.64.0.1/30"},
    "isp-b": {"eth1": "203.0.113.1/24", "eth2": "100.64.0.2/30"},
    "fw-dc1": {"eth1": "198.51.100.10/24", "eth2": "203.0.113.10/24", "eth3": "10.11.10.1/24",
               "eth4": "10.11.20.1/24", "eth5": "10.11.30.1/24", "eth6": "10.11.99.1/24"},
    "fw-dc2": {"eth1": "198.51.100.20/24", "eth2": "203.0.113.20/24", "eth3": "10.20.10.1/24"},
    "gw-hq": {"eth1": "198.51.100.30/24", "eth2": "203.0.113.30/24", "eth3": "10.30.1.1/24"},
    "gw-agfr": {"eth1": "198.51.100.40/24", "eth2": "203.0.113.40/24", "eth3": "10.40.1.1/24", "eth4": "10.40.2.1/24"},
    "gw-part": {"eth1": "198.51.100.60/24", "eth2": "10.60.1.1/24"},
}
ROUTES = {  # routes statiques (destination, passerelle)
    "isp-a": [("203.0.113.0/24", "100.64.0.2")],
    "isp-b": [("198.51.100.0/24", "100.64.0.1"), ("192.0.2.0/24", "100.64.0.1")],
}
OSPF = {"fw-dc1": ("10.255.0.1", ["eth3", "eth4", "eth5", "eth6"]), "fw-dc2": ("10.255.0.2", ["eth3"]),
        "gw-hq": ("10.255.0.3", ["eth3"]), "gw-agfr": ("10.255.0.4", ["eth3"])}  # LAN annoncés (passifs)
# Tunnels : hub, site, transport, if_id, coût OSPF (None = routes statiques, cas du partenaire)
TUNNELS = [("fw-dc1", "gw-agfr", "a", 11, 10), ("fw-dc1", "gw-agfr", "b", 12, 100),
           ("fw-dc1", "gw-hq", "a", 13, 10), ("fw-dc1", "gw-hq", "b", 14, 100),
           ("fw-dc1", "gw-part", "a", 15, None), ("fw-dc1", "fw-dc2", "a", 16, 10)]
STATIQUES_TUNNEL = {("fw-dc1", 15): "10.60.1.0/24",   # retour vers le partenaire
                    ("gw-part", 15): "10.11.0.0/16"}  # le partenaire envoie tout le DC1 au tunnel ; fw-dc1 filtre
SERVICES = {"srv-web": ["443-https"], "srv-app": ["8443-https"], "srv-db": ["5432-tcp"],
            "logs": ["6514-syslog"], "cli-ext": ["80-http", "443-https"]}


def public(noeud, t):
    return ROUTEURS[noeud]["eth1" if t == "a" else "eth2"].split("/")[0]


def court(noeud):
    return noeud.split("-")[1]


def network(nom, adresse, extra=""):
    return f"[Match]\nName={nom}\n[Network]\nAddress={adresse}\n{extra}"


def config_routeur(n):
    f = {}
    for ifname, addr in ROUTEURS[n].items():
        extra = "".join(f"[Route]\nDestination={d}\nGateway={g}\n" for d, g in ROUTES.get(n, []) if
                        g.rsplit(".", 1)[0] == addr.rsplit(".", 1)[0])
        if n not in ("isp-a", "isp-b") and ifname in ("eth1", "eth2") and addr.startswith(("198.51.100.", "203.0.113.")):
            gw = "198.51.100.1" if ifname == "eth1" else "203.0.113.1"
            extra += f"[Route]\nGateway={gw}\nMetric={10 if ifname == 'eth1' else 100}\n"
        f[f"/etc/systemd/network/20-{ifname}.network"] = network(ifname, addr, extra)

    swan, secs, frr_if = [], [], []
    for hub, site, t, if_id, cout in TUNNELS:
        if n not in (hub, site):
            continue
        cote_hub = n == hub
        x = f"x{t}-{court(site) if cote_hub else court(hub)}"
        local, distant = (public(hub, t), public(site, t)) if cote_hub else (public(site, t), public(hub, t))
        ip_int = f"10.255.{if_id - 10}.{1 if cote_hub else 2}/30"
        f[f"/etc/systemd/network/30-{x}.netdev"] = f"[NetDev]\nName={x}\nKind=xfrm\n[Xfrm]\nInterfaceId={if_id}\nIndependent=yes\n"
        route = STATIQUES_TUNNEL.get((n, if_id))
        f[f"/etc/systemd/network/30-{x}.network"] = network(
            x, ip_int, "[Link]\nMTUBytes=1400\nRequiredForOnline=no\n" + (f"[Route]\nDestination={route}\n" if route else ""))
        demarrage = "none" if cote_hub else "start"
        # mobike = no : le tunnel reste attaché à son opérateur ; c'est OSPF qui bascule sur l'autre tunnel
        swan.append(f"""  {x} {{
    version = 2
    local_addrs = {local}
    remote_addrs = {distant}
    dpd_delay = 5s
    keyingtries = 0
    mobike = no
    local {{ auth = psk }}
    remote {{ auth = psk }}
    children {{
      {x} {{
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        if_id_in = {if_id}
        if_id_out = {if_id}
        start_action = {demarrage}
        dpd_action = {'restart' if demarrage == 'start' else 'clear'}
        close_action = {demarrage}
      }}
    }}
  }}""")
        secs.append(f'  ike-{if_id} {{\n    id-1 = {local}\n    id-2 = {distant}\n    secret = "{PSK[if_id]}"\n  }}')
        if cout:
            frr_if.append(f"interface {x}\n ip ospf area 0\n ip ospf network point-to-point\n ip ospf cost {cout}\n"
                          " ip ospf hello-interval 1\n ip ospf dead-interval 4\n!")
    if swan:
        f["/etc/swanctl/conf.d/rao.conf"] = "connections {\n" + "\n".join(swan) + "\n}\nsecrets {\n" + "\n".join(secs) + "\n}\n"
        # swanctl charge par défaut des plugins absents de Debian : ~30 avertissements à chaque commande (gênant en démo)
        f["/etc/strongswan.d/rao-swanctl.conf"] = "swanctl {\n  load = random nonce openssl pem pkcs1 pkcs8 x509 pubkey\n}\n"
        # Par défaut, charon journalise chaque paquet DPD (toutes les 5 s par tunnel) : 1,7 Go en 13 jours sur fw-dc1,
        # disque plein et FRR planté (SIGBUS). Niveau 0 : seulement l'ouverture et la fermeture des tunnels.
        f["/etc/strongswan.d/rao-journal.conf"] = "charon-systemd {\n  journal {\n    default = 0\n  }\n}\n"
    if n in OSPF:
        rid, lans = OSPF[n]
        f["/etc/frr/frr.conf"] = (f"frr defaults traditional\nhostname {n}\nlog syslog informational\n!\n" + "\n".join(frr_if) + "\n"
                                  + "".join(f"interface {i}\n ip ospf area 0\n ip ospf passive\n!\n" for i in lans)
                                  + f"router ospf\n ospf router-id {rid}\n!\n")
    f["/etc/nftables.conf"] = nftables(n)
    # Démonstration : console série EVE ouverte directement en root (lab uniquement ; l'accès à la console
    # passe déjà par l'administration d'EVE, qui contrôle entièrement les nœuds)
    f["/etc/systemd/system/serial-getty@ttyS0.service.d/autologin.conf"] = (
        "[Service]\nExecStart=\nExecStart=-/sbin/agetty --autologin root --keep-baud 115200,57600,38400,9600 - $TERM\n")
    f["/etc/motd"] = (f"\n  {n} — lab RAO (démonstration)\n"
                      "  swanctl --list-sas | grep ESTABLISHED     tunnels IPsec\n"
                      "  vtysh -c 'show ip ospf neighbor'          voisins OSPF\n"
                      "  ip route                                  routes (proto ospf = apprises)\n"
                      "  nft list ruleset | less                   politique de filtrage\n"
                      "  journalctl -k -f | grep RAO               flux acceptés / refusés en direct\n\n")
    f["/etc/rsyslog.d/90-rao.conf"] = (f'kern.* action(type="omfwd" target="{LOGS}" port="6514" protocol="tcp" '
                                       'action.resumeRetryCount="-1" queue.type="LinkedList")\n')
    # disques de 3 Go et maquette allumée des semaines : plafond du journal système
    f["/etc/systemd/journald.conf.d/rao.conf"] = "[Journal]\nSystemMaxUse=50M\n"
    return f


ENTREE_COMMUNE = """    ct state established,related accept
    iif lo accept
    iifname "eth0" tcp dport 22 accept
    iifname "eth0" udp sport 67 udp dport 68 accept
    iifname { "eth1", "eth2" } udp dport { 500, 4500 } accept
    iifname { "eth1", "eth2" } meta l4proto esp accept
    iifname "x*" ip protocol ospf accept
    icmp type { echo-request, echo-reply, destination-unreachable, time-exceeded } accept"""


def nftables(n):
    if n.startswith("isp-"):
        # Opérateurs : routage sans filtrage, sauf anti-usurpation (BCP 38) sur l'accès clients : un site ne peut
        # pas émettre avec l'adresse de l'autre opérateur (sinon le tunnel A survit à la coupure du lien A).
        bloc = ROUTEURS[n]["eth1"].rsplit(".", 1)[0] + ".0/24"
        return f"""flush ruleset
table inet filter {{
  chain forward {{
    type filter hook forward priority 0; policy accept;
    iifname "eth1" ip saddr != {bloc} counter drop
  }}
}}
"""
    if n == "fw-dc1":
        transit = """    iifname { "eth1", "eth2" } ip daddr 10.11.10.10 tcp dport { 443, 22 } log prefix "RAO-OK F01-F02 " accept
    ip saddr 10.11.10.10 ip daddr 10.11.20.20 tcp dport 8443 log prefix "RAO-OK F03 " accept
    ip saddr 10.11.20.20 ip daddr 10.11.30.30 tcp dport 5432 log prefix "RAO-OK F04 " accept
    iifname { "xa-agfr", "xb-agfr", "xa-hq", "xb-hq", "xa-dc2" } ip daddr 10.11.20.20 tcp dport 8443 log prefix "RAO-OK F05 " accept
    iifname "xa-part" ip saddr 10.60.1.0/24 ip daddr 10.11.20.20 tcp dport 8443 log prefix "RAO-OK F06 " accept
    iifname { "xa-hq", "xb-hq" } ip saddr 10.30.1.0/24 ip daddr 10.11.99.10 tcp dport 22 log prefix "RAO-OK F09 " accept
    ip saddr 10.11.99.10 tcp dport { 22, 443 } log prefix "RAO-OK F10 " accept
    ip daddr 10.11.99.20 tcp dport 6514 accept
    iifname { "xa-agfr", "xb-agfr", "xa-hq", "xb-hq", "xa-dc2" } icmp type echo-request accept"""
        transit += """
    oifname { "xa-agfr", "xb-agfr", "xa-hq", "xb-hq", "xa-dc2" } ip saddr 10.11.0.0/16 accept"""
        nat = """table ip nat {
  chain prerouting {
    type nat hook prerouting priority dstnat;
    iifname { "eth1", "eth2" } ip daddr { 198.51.100.10, 203.0.113.10 } tcp dport { 443, 22 } dnat to 10.11.10.10
  }
}
"""
    elif n == "gw-agfr":
        transit = """    iifname "eth3" oifname "x*" accept
    iifname "x*" oifname "eth3" accept
    iifname { "eth3", "eth4" } oifname { "eth1", "eth2" } ip daddr != 10.0.0.0/8 tcp dport { 80, 443 } log prefix "RAO-OK F13 " accept"""
        nat = """table ip nat {
  chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname { "eth1", "eth2" } ip saddr 10.40.0.0/16 masquerade
  }
}
"""
    else:  # fw-dc2, gw-hq, gw-part : le LAN passe par le tunnel, fw-dc1 applique la politique
        lan = "eth2" if n == "gw-part" else "eth3"
        transit = f"""    iifname "{lan}" oifname "x*" accept
    iifname "x*" oifname "{lan}" accept"""
        nat = ""
    return f"""flush ruleset
table inet filter {{
  chain input {{
    type filter hook input priority 0; policy drop;
{ENTREE_COMMUNE}
    # bruit de découverte (LLMNR, mDNS) : refusé sans encombrer le journal ni la démonstration
    meta pkttype {{ broadcast, multicast }} drop
    log prefix "RAO-REFUS-ENTREE " drop
  }}
  chain forward {{
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    tcp flags syn tcp option maxseg size set rt mtu
{transit}
    log prefix "RAO-REFUS " drop
  }}
}}
{nat}"""


APPLIQUER_ROUTEUR = """set -e
sysctl -q --system
networkctl reload
for i in $(ls /sys/class/net | grep -E '^(eth[1-9]|x[ab]-)'); do networkctl reconfigure "$i"; done
nft -f /etc/nftables.conf
if [ -f /etc/frr/frr.conf ] && grep -q 'router ospf' /etc/frr/frr.conf; then
  sed -i 's/^ospfd=no/ospfd=yes/' /etc/frr/daemons; systemctl restart frr
fi
if [ -f /etc/swanctl/conf.d/rao.conf ]; then systemctl enable -q strongswan; systemctl restart strongswan; sleep 1; swanctl --load-all >/dev/null
  swanctl --list-conns | grep -q IKEv2 || { echo "ERREUR : configuration swanctl refusée"; exit 1; }; fi
systemctl enable -q rsyslog; systemctl restart rsyslog; systemctl restart systemd-journald
systemctl daemon-reload; systemctl restart serial-getty@ttyS0
echo "$(hostname) : $(ip -br -4 addr | grep -vcE '^(lo|eth0)') interfaces configurées"
"""

SERVICE_PY = '''#!/usr/bin/env python3
"""Service de test du lab RAO. Argument : <port>-<http|https|tcp|syslog>."""
import datetime, http.server, socket, socketserver, ssl, sys
port, mode = sys.argv[1].split("-")
port, nom = int(port), socket.gethostname()

class Web(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        corps = f"{nom} OK {mode}:{port}\\n".encode()
        self.send_response(200); self.send_header("Content-Length", str(len(corps))); self.end_headers(); self.wfile.write(corps)
    def log_message(self, *a): pass

class Tcp(socketserver.StreamRequestHandler):
    def handle(self):
        if mode == "syslog":
            with open("/var/log/rao/central.log", "a") as f:
                for ligne in self.rfile:
                    f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} {self.client_address[0]} "
                            f"{ligne.decode(errors='replace').rstrip()}\\n"); f.flush()
        else:
            self.wfile.write(f"{nom} OK tcp:{port}\\n".encode())

socketserver.ThreadingTCPServer.allow_reuse_address = True
if mode in ("http", "https"):
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", port), Web)
    if mode == "https":
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain("/etc/rao/cert.pem", "/etc/rao/key.pem")
        srv.socket = ctx.wrap_socket(srv.socket, server_side=True)
else:
    srv = socketserver.ThreadingTCPServer(("0.0.0.0", port), Tcp)
srv.serve_forever()
'''

UNITE = """[Unit]
Description=Service de test RAO %i
After=network-online.target
[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/rao_service.py %i
Restart=always
[Install]
WantedBy=multi-user.target
"""


def config_hote(n):
    return {"/usr/local/bin/rao_service.py": SERVICE_PY, "/etc/systemd/system/rao@.service": UNITE}


def appliquer_hote(n):
    inst = " ".join(f"rao@{s}" for s in SERVICES[n])
    return f"""set -e
chmod +x /usr/local/bin/rao_service.py; mkdir -p /etc/rao /var/log/rao
[ -f /etc/rao/cert.pem ] || openssl req -x509 -newkey rsa:2048 -nodes -days 365 -subj "/CN=$(hostname)" \\
  -keyout /etc/rao/key.pem -out /etc/rao/cert.pem 2>/dev/null
systemctl daemon-reload; systemctl enable -q --now {inst}; systemctl restart {inst}
echo "$(hostname) : services {inst} actifs"
"""


def pousser(noeud, fichiers, commande):
    script = "".join(f"mkdir -p $(dirname {p}) && cat > {p} <<'RAO_EOF'\n{c}RAO_EOF\n" for p, c in fichiers.items())
    r = subprocess.run(SSH + [noeud, "bash -s"], input=(script + commande).encode(), cwd=ROOT, capture_output=True)
    sortie = (r.stdout + r.stderr).decode(errors="replace").strip().splitlines()
    print(f"[{'OK' if r.returncode == 0 else 'ÉCHEC'}] {noeud} : " + (sortie[-1] if sortie else ""))
    if r.returncode == 255:
        print(f"    SSH impossible vers {noeud} : nœud démarré dans EVE ? essayer « ssh -F automation/ssh_config {noeud} »")
    return r.returncode == 0


PSK = {t[3]: secrets.token_urlsafe(32) for t in TUNNELS}  # nouvelles clés à chaque déploiement

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cibles = sys.argv[1:] or list(ROUTEURS) + list(SERVICES)
    # Les deux bouts d'un tunnel doivent recevoir la même clé : on pousse tous les routeurs concernés ensemble
    if any(c in ROUTEURS for c in cibles) and set(cibles) & set(ROUTEURS) != set(ROUTEURS):
        sys.exit("Les clés IPsec sont régénérées : déployer tous les routeurs ensemble (sans argument).")
    ok = all([pousser(n, config_routeur(n), APPLIQUER_ROUTEUR) for n in cibles if n in ROUTEURS]
             + [pousser(n, config_hote(n), appliquer_hote(n)) for n in cibles if n in SERVICES])
    if not ok:
        print("Déploiement incomplet : corriger le nœud en échec puis relancer sans argument (les clés IPsec doivent rester identiques des deux côtés).")
    sys.exit(0 if ok else 1)
