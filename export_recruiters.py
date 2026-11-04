import csv
import os

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("LBA_TOKEN")
URL = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

CODES = ["M1805", "M1801", "M1818", "M1830", "M1856"]
ZONES = {
    "Nice": (43.7102, 7.2620),
    "Sophia Antipolis": (43.6163, 7.0551),
    "Cannes": (43.5528, 7.0174),
}
# Secteurs informatiques (NAF) : programmation, conseil, édition de logiciels, données, portails
NAF_OK = ("62.", "58.29", "63.11", "63.12")

vus = {}
for zone, (lat, lon) in ZONES.items():
    r = requests.get(URL, headers=HEADERS, timeout=30, params={
        "latitude": lat, "longitude": lon, "radius": 30,
        "romes": ",".join(CODES),
    })
    if r.status_code != 200:
        print(zone, r.status_code, r.text[:200])
        continue
    for rec in r.json().get("recruiters", []):
        w = rec["workplace"]
        naf = (w.get("domain") or {}).get("naf") or {}
        code_naf = naf.get("code") or ""
        if not code_naf.startswith(NAF_OK):
            continue
        cle = w.get("siret") or (w.get("name"), w["location"]["address"])
        if cle in vus:
            continue
        apply = rec.get("apply") or {}
        vus[cle] = {
            "entreprise": w.get("name"),
            "adresse": w["location"]["address"],
            "secteur": naf.get("label"),
            "taille": w.get("size"),
            "lien_candidature": apply.get("url"),
            "telephone": apply.get("phone"),
            "statut": "",
            "date_contact": "",
        }

lignes = sorted(vus.values(), key=lambda x: x["adresse"][-12:])
with open("recruteurs_it.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
    w.writeheader()
    w.writerows(lignes)

print(len(lignes), "entreprises informatiques enregistrées dans recruteurs_it.csv")