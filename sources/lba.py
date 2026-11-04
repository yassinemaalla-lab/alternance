import os
import re
import time

import requests
from dotenv import load_dotenv

import config

URL = "https://api.apprentissage.beta.gouv.fr/api/job/v1/search"


def _code_postal(adresse):
    trouve = re.search(r"\b(\d{5})\b", adresse or "")
    return trouve.group(1) if trouve else ""


def _departement(code_postal):
    if len(code_postal) < 2:
        return ""
    if code_postal.startswith(("97", "98")) and len(code_postal) >= 3:
        return code_postal[:3]
    return code_postal[:2]


def _nombre(valeur):
    if valeur is None or valeur == "":
        return None
    return float(valeur)


def _coordonnees(lieu):
    point = ((lieu.get("location") or {}).get("geopoint") or {}).get("coordinates") or []
    if len(point) < 2:
        return None, None
    return _nombre(point[1]), _nombre(point[0])


def _cle_entreprise(lieu, adresse):
    siret = lieu.get("siret") or ""
    if siret:
        return siret
    nom = lieu.get("name") or ""
    if nom or adresse:
        return f"{nom}|{adresse}"
    return ""


def normaliser_entreprise(bloc, source=""):
    """Lit un recruteur, ou le lieu d'une offre, et renvoie une entreprise."""
    lieu = bloc.get("workplace") or bloc
    adresse = (lieu.get("location") or {}).get("address") or ""
    naf = (lieu.get("domain") or {}).get("naf") or {}
    apply = bloc.get("apply") or {}
    latitude, longitude = _coordonnees(lieu)
    code_postal = _code_postal(adresse)
    return {
        "cle": _cle_entreprise(lieu, adresse),
        "siret": lieu.get("siret") or "",
        "nom": lieu.get("name") or "entreprise non précisée",
        "adresse": adresse,
        "code_postal": code_postal,
        "departement": _departement(code_postal),
        "code_naf": naf.get("code") or "",
        "libelle_naf": naf.get("label") or "",
        "taille": lieu.get("size") or "",
        "site": lieu.get("website") or "",
        "telephone": apply.get("phone") or "",
        "lien_candidature": apply.get("url") or "",
        "latitude": latitude,
        "longitude": longitude,
        "source": source or (bloc.get("identifier") or {}).get("partner_label") or "",
    }


def normaliser_offre(bloc):
    """Transforme une offre brute de l'API en dictionnaire prêt pour la base."""
    ident = bloc.get("identifier") or {}
    offre = bloc.get("offer") or {}
    lieu = bloc.get("workplace") or {}
    contrat = bloc.get("contract") or {}
    adresse = (lieu.get("location") or {}).get("address") or ""
    latitude, longitude = _coordonnees(lieu)
    code_postal = _code_postal(adresse)
    types = contrat.get("type") or []
    return {
        "cle": f"{ident.get('partner_label')}:{ident.get('partner_job_id')}",
        "titre": offre.get("title") or "",
        "description": offre.get("description") or "",
        "entreprise_cle": _cle_entreprise(lieu, adresse),
        "entreprise_nom": lieu.get("name") or "",
        "adresse": adresse,
        "code_postal": code_postal,
        "departement": _departement(code_postal),
        "latitude": latitude,
        "longitude": longitude,
        "date_creation": (offre.get("publication") or {}).get("creation") or "",
        "lien": (bloc.get("apply") or {}).get("url") or "",
        "partenaire": ident.get("partner_label") or "",
        "codes_rome": ",".join(offre.get("rome_codes") or []),
        "type_contrat": ",".join(types) if isinstance(types, list) else str(types or ""),
        "duree_mois": None if contrat.get("duration") is None else int(float(contrat.get("duration"))),
        "pertinente": 1 if pertinente(offre.get("title") or "", offre.get("description") or "") else 0,
    }


def pertinente(titre, description=""):
    titre_min = titre.lower()
    if not any(mot in titre_min for mot in config.MOTS_CLES_TITRE):
        return False
    texte = f"{titre_min}\n{description.lower()}"
    return not any(mot in texte for mot in config.MOTS_EXCLUS)


def secteur_informatique(code_naf):
    return bool(code_naf) and code_naf.startswith(config.NAF_OK)


def _get(params):
    load_dotenv()
    token = os.getenv("LBA_TOKEN")
    if not token:
        raise SystemExit("LBA_TOKEN manquant : ajoute-le dans le fichier .env")
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(2):
        reponse = requests.get(URL, headers=headers, params=params, timeout=30)
        if reponse.status_code == 429:
            time.sleep(int(reponse.headers.get("retry-after", 60)))
            continue
        reponse.raise_for_status()
        return reponse.json()
    return {}


def _zones(romes):
    for zone, (latitude, longitude) in config.ZONES.items():
        donnees = _get({
            "latitude": latitude,
            "longitude": longitude,
            "radius": config.RAYON_KM,
            "romes": ",".join(romes),
        })
        yield zone, donnees


def chercher_offres():
    """Offres pertinentes autour des zones, sans doublon."""
    trouvees = {}
    for _zone, donnees in _zones(config.CODES_ROME):
        for brute in donnees.get("jobs") or []:
            offre = normaliser_offre(brute)
            if offre["pertinente"]:
                trouvees[offre["cle"]] = (brute, offre)
    return trouvees


def chercher_recruteurs():
    """Entreprises informatiques renvoyées par l'API sur les mêmes zones."""
    trouvees = {}
    for _zone, donnees in _zones(config.CODES_ROME_RECRUTEURS):
        for brute in donnees.get("recruiters") or []:
            entreprise = normaliser_entreprise(brute, source="recherche")
            if not secteur_informatique(entreprise["code_naf"]):
                continue
            if entreprise["cle"]:
                trouvees[entreprise["cle"]] = entreprise
    return trouvees
