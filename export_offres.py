"""Télécharge le fichier national des offres (lien valable deux minutes)."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("LBA_TOKEN")
if not TOKEN:
    raise SystemExit("LBA_TOKEN manquant : ajoute-le dans le fichier .env")

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

reponse = requests.get(
    "https://api.apprentissage.beta.gouv.fr/api/job/v1/export",
    headers=HEADERS,
    timeout=60,
)
print("Code HTTP :", reponse.status_code)
if reponse.status_code != 200:
    print(reponse.text[:300])
    raise SystemExit(1)

info = reponse.json()
print("Export du :", info["lastUpdate"])

with requests.get(info["url"], stream=True, timeout=120) as telechargement:
    telechargement.raise_for_status()
    with open("export_offres.json", "wb") as fichier:
        for morceau in telechargement.iter_content(chunk_size=1024 * 1024):
            fichier.write(morceau)

taille = os.path.getsize("export_offres.json") / 1_000_000
print(f"Téléchargé : {taille:.0f} Mo")
