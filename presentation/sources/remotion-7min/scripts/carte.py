"""Prépare la carte de la scène 1 : contours de la France et du monde, et 530 points de sites.

Usage : python scripts/carte.py dossier_geojson   ->  src/donnees/carte.json
Contours : Natural Earth (domaine public), fichiers ne_110m_land.geojson et ne_50m_admin_0_countries.geojson.
La position des points est décorative : le dossier ne situe pas les sites. 500 points en France
(2 sièges et 498 agences) et 30 à l'international, tirés au hasard avec une graine fixe.
"""
import json
import math
import random
import sys
from pathlib import Path

GEO = Path(sys.argv[1])
SORTIE = Path(__file__).resolve().parent.parent / "src" / "donnees" / "carte.json"
rng = random.Random(530)

# Cadres dans l'image 1920 × 1080
FR = dict(x=120, y=230, taille=620)  # la France tient dans un carré
MONDE = dict(x=1000, y=130, largeur=800, lat_haut=84, lat_bas=-58)


def anneaux(geometrie):
    polygones = geometrie["coordinates"] if geometrie["type"] == "MultiPolygon" else [geometrie["coordinates"]]
    return [p[0] for p in polygones]  # contour extérieur de chaque polygone


def dedans(lon, lat, anneau):
    """Lancer de rayon : le point est-il dans le polygone ?"""
    r = False
    for (x1, y1), (x2, y2) in zip(anneau, anneau[1:]):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
            r = not r
    return r


def trace(anneau, projeter):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in map(projeter, anneau)) + " Z"


# France métropolitaine : le polygone qui contient Paris, et la Corse.
pays = json.loads((GEO / "pays50.geojson").read_text(encoding="utf-8"))["features"]
france = next(f for f in pays if f["properties"]["ADM0_A3"] == "FRA")
metropole = [a for a in anneaux(france["geometry"]) if dedans(2.35, 48.85, a) or dedans(9.1, 42.2, a)]
assert len(metropole) == 2, "métropole et Corse attendues"
lons = [p[0] for a in metropole for p in a]
lats = [p[1] for a in metropole for p in a]
k = math.cos(math.radians(46.5))  # un degré de longitude est plus court qu'un degré de latitude
echelle = FR["taille"] / max((max(lons) - min(lons)) * k, max(lats) - min(lats))


def vers_france(p):
    return FR["x"] + (p[0] - min(lons)) * k * echelle, FR["y"] + (max(lats) - p[1]) * echelle


terres = [a for f in json.loads((GEO / "land110.geojson").read_text(encoding="utf-8"))["features"] for a in anneaux(f["geometry"])]
px = MONDE["largeur"] / 360


def vers_monde(p):
    return MONDE["x"] + (p[0] + 180) * px, MONDE["y"] + (MONDE["lat_haut"] - p[1]) * px


points = []
while len(points) < 500:  # sièges et agences de France
    lon, lat = rng.uniform(min(lons), max(lons)), rng.uniform(min(lats), max(lats))
    if any(dedans(lon, lat, a) for a in metropole):
        points.append(vers_france((lon, lat)))
while len(points) < 530:  # agences à l'international, hors France et hors régions polaires
    lon, lat = rng.uniform(-170, 180), rng.uniform(-40, 62)
    if any(dedans(lon, lat, a) for a in terres) and not (-6 < lon < 10 and 41 < lat < 52):
        points.append(vers_monde((lon, lat)))
rng.shuffle(points)  # ordre d'allumage

SORTIE.parent.mkdir(parents=True, exist_ok=True)
SORTIE.write_text(json.dumps({
    "france": " ".join(trace(a, vers_france) for a in metropole),
    "monde": " ".join(trace(a, vers_monde) for a in terres if max(p[1] for p in a) > MONDE["lat_bas"]),
    "points": [[round(x, 1), round(y, 1)] for x, y in points],
}, separators=(",", ":")) + "\n", encoding="utf-8")
print("ok", SORTIE, f"{SORTIE.stat().st_size // 1024} Ko, {len(points)} points")
