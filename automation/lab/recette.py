"""Recette du lab RAO : rejoue la matrice de flux (docs/FLUX.md), compare à l'attendu, cherche la trace
dans les journaux centralisés, mesure la bascule WAN, et écrit les preuves dans evidence/<horodatage UTC>/.
Usage depuis la racine du projet : python automation/lab/recette.py [--sans-bascule]
"""
import csv
import datetime
import hashlib
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SSH = ["ssh", "-F", "automation/ssh_config"]

# id, description, nœud source, adresse source (routeurs) ou "", destination, port, attendu
TESTS = [
    ("F01", "Internet -> publication web HTTPS", "cli-ext", "", "198.51.100.10", 443, "ok"),
    ("F02", "Internet -> SFTP publie (port 22)", "cli-ext", "", "198.51.100.10", 22, "ok"),
    ("F03", "srv-web -> srv-app 8443", "srv-web", "", "10.11.20.20", 8443, "ok"),
    ("F04", "srv-app -> srv-db 5432", "srv-app", "", "10.11.30.30", 5432, "ok"),
    ("F05", "agence FR -> application (tunnel)", "cli-ag", "", "10.11.20.20", 8443, "ok"),
    ("F06", "partenaire S2S -> application", "gw-part", "10.60.1.1", "10.11.20.20", 8443, "ok"),
    ("F09", "admin (siege) -> bastion 22", "gw-hq", "10.30.1.1", "10.11.99.10", 22, "ok"),
    ("F10", "bastion -> serveur (administration)", "bastion", "", "10.11.30.30", 22, "ok"),
    ("F11", "serveur -> collecteur de journaux", "srv-app", "", "10.11.99.20", 6514, "ok"),
    ("F13", "invite agence -> Internet 80", "cli-inv", "", "192.0.2.10", 80, "ok"),
    ("N01", "Internet -> base de donnees", "cli-ext", "", "198.51.100.10", 5432, "refus"),
    ("N02", "Internet -> bastion", "cli-ext", "", "10.11.99.10", 22, "refus"),
    ("N03", "srv-web -> srv-db 5432", "srv-web", "", "10.11.30.30", 5432, "refus"),
    ("N04", "srv-app -> srv-db autre port (22)", "srv-app", "", "10.11.30.30", 22, "refus"),
    ("N05", "invite agence -> reseau interne", "cli-inv", "", "10.11.20.20", 8443, "refus"),
    ("N06", "partenaire -> base de donnees", "gw-part", "10.60.1.1", "10.11.30.30", 5432, "refus"),
    ("N08", "agence -> serveur en SSH sans bastion", "cli-ag", "", "10.11.30.30", 22, "refus"),
]
NON_EXECUTES = [("F07", "nomade salarie -> application", "ZTNA/VPN nomade non modelise dans la maquette"),
                ("F08", "nomade partenaire -> portail", "ZTNA/VPN nomade non modelise dans la maquette"),
                ("N07", "nomade partenaire -> application", "ZTNA/VPN nomade non modelise dans la maquette"),
                ("N09", "nomade revoque", "IdP/MFA non modelise dans la maquette")]


def ssh(noeud, cmd, timeout=60):
    r = subprocess.run(SSH + [noeud, cmd], cwd=ROOT, capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).decode(errors="replace").strip()


def tcp(noeud, src, dst, port):
    opt = f"-s {src} " if src else ""
    code, sortie = ssh(noeud, f"nc -z -w 3 {opt}{dst} {port} && echo OUVERT || echo FERME")
    detail = sortie.splitlines()[-1] if sortie else ""
    if "OUVERT" in sortie:
        return "ok", detail
    # Sans FERME, le test n'a pas tourné (SSH en échec) : ne pas le compter comme un refus réussi
    return ("refus" if "FERME" in sortie else "erreur"), detail


def bascule():
    """Coupe l'opérateur A de l'agence pendant 10 s ; mesure les pertes vers l'application (ping 0,2 s)."""
    ssh("cli-ag", "rm -f /tmp/ping.log; nohup ping -D -i 0.2 -c 125 10.11.20.20 > /tmp/ping.log 2>&1 &")
    time.sleep(5)
    t0 = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    ssh("gw-agfr", "ip link set eth1 down")
    try:
        time.sleep(10)
        route_b = ssh("gw-agfr", "ip route get 10.11.20.20")[1]
    finally:  # même sur Ctrl+C ou erreur : ne jamais laisser l'agence sans son opérateur A
        if ssh("gw-agfr", "ip link set eth1 up")[0] != 0:
            print("ATTENTION : eth1 de gw-agfr peut être resté coupé ; lancer : "
                  "ssh -F automation/ssh_config gw-agfr 'ip link set eth1 up'")
    time.sleep(12)
    _, resume = ssh("cli-ag", "tail -2 /tmp/ping.log")
    retour = ssh("gw-agfr", "ip route get 10.11.20.20")[1]
    return t0, route_b, resume, retour


def main():
    horo = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    dossier = ROOT / "evidence" / horo
    dossier.mkdir(parents=True)
    ssh("logs", "wc -l < /var/log/rao/central.log > /tmp/debut_recette")
    lignes, ok = [], 0
    for tid, desc, noeud, src, dst, port, attendu in TESTS:
        quand = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
        obtenu, detail = tcp(noeud, src, dst, port)
        statut = "réussi" if obtenu == attendu else "échoué"
        ok += statut == "réussi"
        lignes.append([tid, desc, noeud, src or "-", f"{dst}:{port}", attendu, obtenu, statut, quand, detail])
        print(f"{tid} {statut:7} attendu={attendu:5} obtenu={obtenu:5} {desc}")
    for tid, desc, motif in NON_EXECUTES:
        lignes.append([tid, desc, "-", "-", "-", "-", "-", "non exécuté", "-", motif])
    time.sleep(3)  # laisse arriver les derniers journaux
    _, journaux = ssh("logs", "tail -n +$(( $(cat /tmp/debut_recette) + 1 )) /var/log/rao/central.log | grep -E 'RAO-(OK|REFUS)'")
    (dossier / "journaux_pare-feu.log").write_text(journaux + "\n", encoding="utf-8", newline="\n")

    with open(dossier / "recette.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["id", "description", "source", "ip_source", "destination", "attendu", "obtenu", "statut", "horodatage_utc", "detail"])
        w.writerows(lignes)
    rapport = [f"# Recette du lab RAO — {horo}", "", f"Tests de flux : **{ok}/{len(TESTS)} réussis**, "
               f"{len(NON_EXECUTES)} non exécutés (hors périmètre de la maquette).", "",
               f"Lignes de journal pare-feu collectées pendant la recette : {len(journaux.splitlines())} "
               "(fichier `journaux_pare-feu.log`).", ""]
    bascule_ok = True
    if "--sans-bascule" not in sys.argv:
        t0, route_b, resume, retour = bascule()
        (dossier / "bascule_wan.txt").write_text(
            f"Coupure de l'opérateur A sur gw-agfr à {t0} (UTC), pendant 10 s\n"
            f"Route pendant la coupure : {route_b}\nRésultat du ping (0,2 s) depuis cli-ag :\n{resume}\n"
            f"Route après rétablissement : {retour}\n", encoding="utf-8", newline="\n")
        stats = resume.splitlines()[0] if resume else ""
        try:
            envoyes, recus = int(stats.split()[0]), int(stats.split(",")[1].split()[0])
            coupure = f"{envoyes - recus} paquets perdus, soit environ {(envoyes - recus) * 0.2:.1f} s d'interruption"
        except (IndexError, ValueError):
            coupure = "non mesurée"
        bascule_ok = "xb-dc1" in route_b and "xa-dc1" in retour
        rapport += ["## Bascule WAN (agence FR)", "",
                    f"Résultat : **{'réussi' if bascule_ok else 'échoué'}** — {coupure}.", "",
                    f"- Route pendant la coupure de l'opérateur A : `{route_b.splitlines()[0]}`",
                    f"- Ping 0,2 s depuis cli-ag : `{stats}`",
                    f"- Route après rétablissement : `{retour.splitlines()[0]}`", ""]
        print(f"Bascule WAN : {'réussi' if bascule_ok else 'échoué'} ({coupure})")
    (dossier / "recette.md").write_text("\n".join(rapport) + "\n", encoding="utf-8", newline="\n")
    empreintes = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n"
                         for p in sorted(dossier.iterdir()) if p.name != "SHA256SUMS")
    (dossier / "SHA256SUMS").write_text(empreintes, encoding="utf-8", newline="\n")
    print(f"Preuves : evidence/{horo}/")
    echecs = [l[0] for l in lignes if l[7] == "échoué"]
    succes = ok == len(TESTS) and bascule_ok
    print(f"RÉSULTAT : {'CONFORME' if succes else 'NON CONFORME'} — flux {ok}/{len(TESTS)}"
          + (f" (échecs : {', '.join(echecs)})" if echecs else "")
          + ("" if "--sans-bascule" in sys.argv else f", bascule {'réussie' if bascule_ok else 'échouée'}"))
    if any(l[6] == "erreur" for l in lignes):
        print("Des tests n'ont pas pu s'exécuter (obtenu=erreur) : vérifier l'accès SSH aux nœuds concernés.")
    return succes


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if main() else 1)
