"""Chiffrage de l'offre RAO : applique les règles de quantité de docs/CHIFFRAGE.csv,
convertit en EUR HT et écrit docs/CHIFFRAGE.md.
Lancer depuis la racine du projet : python automation/chiffrage/calcul.py
"""
import csv
import datetime
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Volumes du PDF (p.1-2) et hypothèses affichées dans docs/EXIGENCES.md §3
P = {
    "SIEGE": 2, "AG_FR": 498, "AG_INT": 30,  # PDF p.1
    "DC": 2,                                 # choix de l'équipe (housing redondé)
    "U_SIEGE": 2000,                         # H11 : 4 000 utilisateurs, moitié par siège
    "U_AG_FR": 4000, "U_INT": 2000,          # PDF p.1
    "NOMADES": 3000,                         # H6 : 30 % des 10 000 utilisateurs
    "PART_USERS": 300,                       # H7 : 60 partenaires nomades x 5 utilisateurs
    "ADMINS": 50,                            # H9 : administrateurs internes + infogérants
    "VM": 300,                               # H8
    "HOTES_DC": 4, "COEURS_HOTE": 64,        # cluster N+1 par DC, 2 x 32 cœurs par hôte
    "PORTS_USER": 1.25, "USERS_AP": 25,      # règles LAN et Wi-Fi
}
FX = {"EUR": 1.0, "USD": 1.1208, "CAD": 1.5923, "GBP": 0.84610}  # BCE 15/10/2026, devise pour 1 €
TAUX = 0.07  # HYP : taux annuel de la location financière, à faire confirmer par un bailleur
MOIS = 36
SCENARIOS = {  # le premier est l'offre retenue
    "Offre retenue (ZTNA par FortiSASE)": {"base"},
    "Variante écartée (avec Zscaler ZPA)": {"base", "zpa"},
}
OFFRE = SCENARIOS["Offre retenue (ZTNA par FortiSASE)"]
# Lignes « matériel et licences éditeur » touchées par une remise négociée (sensibilité seulement)
REMISABLE = ("SRV-HOTE", "SRV-SAUV", "SRV-VVF", "SRV-VEEAM", "NET-", "SEC-", "SPR-")
UTILISATEURS, SITES = 10_000, 530
NON_INCLUS = [
    "Cross-connects opérateurs dans les DC (sur devis de l'hébergeur).",
    "Déplacements et logistique : envoi des 528 kits, transport et douanes vers les 30 pays.",
    "Extension vSAN au-delà du droit VVF (0,25 TiB par cœur, soit 64 TiB par DC), si le besoin réel le dépasse.",
    "Surcoût éventuel d'un hébergeur certifié HDS par rapport au prix de référence retenu.",
    "SOC 24/7 : l'infogérance chiffrée couvre les heures ouvrées.",
    "Fournisseur d'identité et MFA : supposés existants chez le client (H12).",
    "Renouvellements au-delà de 36 mois.",
    "Optiques SFP+/QSFP28 et câbles DAC (uplinks des switches d'accès, cœurs, ToR et FortiGate des DC) : "
    "quantité à fixer avec le plan de câblage.",
    "Couche de distribution des sièges : 53 switches d'accès par siège en double attachement dépassent les "
    "24 ports SFP+ d'une paire de CX 8100 ; étage de distribution ou cœur plus dense à dimensionner.",
    "Onduleurs en agence, licences des systèmes et applications des 300 VM : supposés fournis par le client.",
    "Protection DDoS volumétrique chez les opérateurs de transit des DC : option sur devis.",
]


def mensualite(capital, taux=TAUX, n=MOIS):
    """Loyer constant qui rembourse `capital` en n mois au taux annuel `taux`."""
    r = taux / 12
    return capital / n if r == 0 else capital * r / (1 - (1 + r) ** -n)


def lire(p=P, remise=0.0):
    """`p` (paramètres) et `remise` ne changent que pour l'analyse de sensibilité."""
    lignes = []
    with open(ROOT / "docs" / "CHIFFRAGE.csv", encoding="utf-8-sig") as f:
        for l in csv.DictReader(f, delimiter=";"):
            # Fichier du projet, pas une entrée externe : eval restreint aux paramètres
            l["q"] = eval(l["regle_quantite"], {"__builtins__": {}, "ceil": math.ceil}, p)
            l["pu"] = float(l["prix_unitaire"].replace(",", ".")) / FX[l["devise"]]
            l["pu"] *= 1 - remise if l["id"].startswith(REMISABLE) else 1
            total = l["q"] * l["pu"]
            l["init"] = total if l["periodicite"] in ("unique", "36mois") else 0.0
            l["mens"] = {"mois": total, "an": total / 12}.get(l["periodicite"], 0.0)
            lignes.append(l)
    return lignes


def verifier(lignes):
    assert P["SIEGE"] + P["AG_FR"] == 500 and P["SIEGE"] + P["AG_FR"] + P["AG_INT"] == SITES
    assert P["SIEGE"] * P["U_SIEGE"] + P["U_AG_FR"] + P["U_INT"] == UTILISATEURS
    assert abs(mensualite(36_000, 0) - 1000) < 1e-9
    fg = sum(l["q"] for l in lignes if l["id"].startswith("SEC-FG"))
    assert fg == P["AG_FR"] + 2 * P["AG_INT"] + 2 * P["SIEGE"] + 4 * P["DC"] == 570, fg


def eur(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",") + " €"


def bilan(lignes, garder):
    postes = {}
    for l in lignes:
        if l["scenario"] in garder:
            p = postes.setdefault(l["poste"], [0.0, 0.0])
            p[0] += l["init"]
            p[1] += l["mens"]
    init = sum(p[0] for p in postes.values())
    mens = sum(p[1] for p in postes.values())
    return postes, init, mens


def sensibilite(lignes):
    """Offre retenue quand UNE hypothèse varie ; P n'est jamais modifié (copies via dict)."""
    def cas(p=P, remise=0.0, taux=TAUX):
        _, init, mens = bilan(lire(p, remise), OFFRE)
        return init, mens, mensualite(init, taux) + mens
    n = P["NOMADES"]
    res = [
        (f"Base : {n:,} nomades".replace(",", " ") + f", taux {TAUX * 100:.0f} %, prix publics", cas()),
        (f"{n - 1000:,} nomades (−1 000)".replace(",", " "), cas(dict(P, NOMADES=n - 1000))),
        (f"{n + 1000:,} nomades (+1 000)".replace(",", " "), cas(dict(P, NOMADES=n + 1000))),
        ("Taux de location 5 %", cas(taux=0.05)),
        ("Taux de location 9 %", cas(taux=0.09)),
        ("Remise négociée 20 % sur matériel et licences éditeur", cas(remise=0.20)),
        ("Remise négociée 30 % sur matériel et licences éditeur", cas(remise=0.30)),
        ("Une agence FR de plus (coût marginal)", cas(dict(P, AG_FR=P["AG_FR"] + 1))),
    ]
    _, init, mens = bilan(lignes, OFFRE)
    a = [c[2] for _, c in res]
    # La sensibilité ne déplace pas la base ; les nomades n'agissent que sur des lignes linéaires
    assert cas() == res[0][1] == (init, mens, mensualite(init) + mens)
    assert abs((a[2] - a[0]) - (a[0] - a[1])) < 1e-6
    assert a[3] < a[0] < a[4] and a[6] < a[5] < a[0] < a[7], a
    return res


def signe(x):
    return ("+" if x >= 0 else "−") + eur(abs(x))


def rapport(lignes):
    sens = sensibilite(lignes)
    postes, init, mens = bilan(lignes, OFFRE)
    abo = mensualite(init) + mens
    ecart = [c[2] - abo for _, c in sens]
    gros = sorted(postes.items(), key=lambda kv: -(mensualite(kv[1][0]) + kv[1][1]))[:3]
    ex = mensualite(100_000)
    o = [
        "# Chiffrage de l'offre",
        "",
        f"Généré par `automation/chiffrage/calcul.py` le {datetime.date.today():%d/%m/%Y}. "
        "Ne pas modifier à la main : corriger `docs/CHIFFRAGE.csv` puis relancer le script.",
        "",
        "Montants en **euros hors taxes**. Devises converties au taux de référence BCE du 15/10/2026 "
        "(1 € = 1,1208 $ = 1,5923 $ CA = 0,8461 £).",
        "",
        "## Lecture rapide",
        "",
        f"- **Ce que paie la mutuelle : {eur(abo)} HT par mois pendant {MOIS} mois**, sans investissement de "
        "départ. Ce loyer couvre tout : matériel, licences, liens opérateurs, hébergement en datacenter, "
        "déploiement et exploitation.",
        f"- Rapporté à l'usage : **{eur(abo / UTILISATEURS, 2)} par utilisateur et par mois**, "
        f"{eur(abo / SITES)} par site et par mois.",
        f"- Sur 3 ans, le coût total est de **{eur(MOIS * abo)}**. Payer comptant coûterait "
        f"{eur(init + MOIS * mens)} : l'écart de {eur(MOIS * abo - init - MOIS * mens)} est le prix de "
        "l'étalement (intérêts de la location).",
        "- Les trois postes les plus lourds : " + ", ".join(
            f"{p} ({eur(mensualite(i) + m)}/mois)" for p, (i, m) in gros) + ".",
        f"- Ce qui peut faire bouger la facture : une remise de 20 % sur le matériel et les licences, courante "
        f"sur un tel volume, ferait {signe(ecart[5])}/mois ; 1 000 nomades de plus, {signe(ecart[2])}/mois ; "
        f"chaque agence ouverte en plus, {signe(ecart[7])}/mois.",
        "- Les prix sont publics ou estimés : ils seront confirmés par devis. Les renouvellements après "
        f"{MOIS} mois ne sont pas inclus.",
        "",
        "## Méthode",
        "",
        "1. **Quantités.** Chaque ligne de `docs/CHIFFRAGE.csv` porte une règle de quantité écrite avec les "
        "paramètres du tableau « Hypothèses de quantité ». Exemples : `AG_FR` = un équipement par agence FR "
        "(498) ; `2*SIEGE` = deux boîtiers par siège (haute disponibilité) ; `ceil(VM/10)` = packs de 10 VM "
        "arrondis au pack supérieur. Changer une hypothèse recalcule toutes les lignes.",
        "2. **Prix.** Chaque prix a une source (lien dans le détail) et une nature : **P** = prix public "
        "constaté chez un revendeur ou un comparateur, **E** = estimation à partir d'une source, **D** = "
        "devis obligatoire (fourchette large). Les prix en devises sont convertis au taux BCE ci-dessus.",
        "3. **Frais initiaux ou récurrents.** *unique* = payé une fois (matériel, mise en service, "
        "déploiement). *36mois* = licence prépayée pour 3 ans (bundles FortiGate, FortiSASE, FortiManager, "
        "Aruba Central) : elle est facturée à la commande pour toute la durée du contrat, donc comptée en "
        "frais initiaux comme le matériel. *mois* et *an* = récurrent ; un prix annuel est divisé par 12.",
        f"4. **Mensualité de location.** Les frais initiaux sont financés par une location financière : loyer "
        f"constant M = C × r / (1 − (1 + r)^−{MOIS}), avec C les frais initiaux et r = taux annuel / 12 "
        f"(taux de {TAUX * 100:.0f} %, hypothèse à faire confirmer par un bailleur). Exemple : 100 000 € de "
        f"frais initiaux donnent {eur(ex, 2)}/mois, soit {eur(MOIS * ex)} remboursés sur {MOIS} mois.",
        f"5. **Achat ou abonnement.** Achat : frais initiaux payés au départ + récurrent × {MOIS}. Abonnement "
        "(préféré par la DSI du client) : mensualité de location + récurrent, chaque mois. L'abonnement coûte "
        "un peu plus au total mais supprime la grosse dépense de départ.",
        "",
        "## Synthèse",
        "",
        f"Location financière sur {MOIS} mois au taux annuel de {TAUX * 100:.0f} % (hypothèse à faire confirmer "
        "par un bailleur) : tous les frais initiaux sont lissés, il ne reste **aucun investissement de départ**.",
        "",
        "| Scénario | Frais initiaux | Récurrent mensuel | TCO 36 mois (achat) | Abonnement mensuel tout compris | TCO 36 mois (abonnement) | € / utilisateur / mois | € / site / mois |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for nom, garder in SCENARIOS.items():
        _, i, m = bilan(lignes, garder)
        a = mensualite(i) + m
        o.append(f"| {nom} | {eur(i)} | {eur(m)} | {eur(i + MOIS * m)} | {eur(a)} | "
                 f"{eur(MOIS * a)} | {eur(a / UTILISATEURS, 2)} | {eur(a / SITES)} |")

    o += ["", "La variante avec Zscaler ZPA est écartée (16/10/2026) : le ZTNA est déjà inclus dans FortiSASE. "
          "Justification : `docs/OFFRE_TECHNIQUE.md`, section « Choix du ZTNA »."]
    o += ["", f"## Par poste du PDF : {next(iter(SCENARIOS))}", "",
          "| Poste | Frais initiaux | Récurrent mensuel | Abonnement mensuel (36 mois) | TCO 36 mois (abonnement) |",
          "|---|---:|---:|---:|---:|"]
    for poste, (i, m) in postes.items():
        a = mensualite(i) + m
        o.append(f"| {poste} | {eur(i)} | {eur(m)} | {eur(a)} | {eur(MOIS * a)} |")
    o.append(f"| **Total** | **{eur(init)}** | **{eur(mens)}** | **{eur(abo)}** | **{eur(MOIS * abo)}** |")

    o += ["", "## Analyse de sensibilité (offre retenue)", "",
          "Calculée par le script : une seule hypothèse change à chaque ligne, les autres restent celles de la "
          "base. La remise porte sur le matériel et les licences éditeur (serveurs, VMware, Veeam, Aruba, "
          "Fortinet, F5, WALLIX), pas sur les liens, l'hébergement ni les services.", "",
          "| Hypothèse modifiée | Frais initiaux | Récurrent mensuel | Abonnement mensuel | Écart / base | Écart en % |",
          "|---|---:|---:|---:|---:|---:|"]
    for (nom, (i, m, a)), d in zip(sens, ecart):
        pct = f"{d / abo * 100:+.1f} %".replace(".", ",").replace("-", "−")
        o.append(f"| {nom} | {eur(i)} | {eur(m)} | {eur(a)} | {signe(d)} | {pct} |")
    i1, m1, _ = sens[7][1]
    o += ["", f"Une agence FR de plus (pare-feu, switch, borne Wi-Fi, licences, une journée de déploiement, "
          f"fibre et SIM de secours) coûte {eur(i1 - init)} de frais initiaux et {eur(m1 - mens)}/mois de "
          f"récurrent, soit **{eur(ecart[7])}/mois d'abonnement**. Chaque tranche de 1 000 nomades pèse "
          f"{eur(ecart[2])}/mois (licences FortiSASE)."]

    o += ["", "## Non inclus (à chiffrer ou hors périmètre)", ""] + [f"- {x}" for x in NON_INCLUS]
    o += ["", "## Hypothèses de quantité", "",
          "| Paramètre | Valeur | Origine |", "|---|---:|---|"]
    origines = {"SIEGE": "PDF", "AG_FR": "PDF", "AG_INT": "PDF", "U_AG_FR": "PDF", "U_INT": "PDF",
                "DC": "choix de l'équipe", "U_SIEGE": "H11", "NOMADES": "H6", "PART_USERS": "H7",
                "ADMINS": "H9", "VM": "H8"}
    for k, v in P.items():
        o.append(f"| `{k}` | {v} | {origines.get(k, 'règle de dimensionnement')} |")

    o += ["", "## Détail des lignes", "",
          "| Id | Poste | Libellé | Règle de quantité | Qté | Prix unitaire | Périodicité | Montant | Nature | Scénario | Source |",
          "|---|---|---|---|---:|---:|---|---:|---|---|---|"]
    for l in lignes:
        montant = eur(l["init"]) if l["periodicite"] in ("unique", "36mois") else f"{eur(l['mens'])}/mois"
        url, _, note = l["source"].partition(" ")  # « URL (note de vérification) » ou texte libre
        src = f"[lien]({url}) {note}".strip() if url.startswith("http") else l["source"]
        o.append(f"| {l['id']} | {l['poste']} | {l['libelle']} | `{l['regle_quantite']}` | {l['q']} | "
                 f"{eur(l['pu'], 2)} | {l['periodicite']} | {montant} | {l['nature']} | {l['scenario']} | {src} |")
    return "\n".join(o) + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows en cp1252 sinon
    lignes = lire()
    verifier(lignes)
    (ROOT / "docs" / "CHIFFRAGE.md").write_text(rapport(lignes), encoding="utf-8")
    for nom, garder in SCENARIOS.items():
        _, init, mens = bilan(lignes, garder)
        print(f"{nom} : initial {eur(init)}, mensuel {eur(mens)}, abonnement {eur(mensualite(init) + mens)}/mois")
