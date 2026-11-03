# config.py : critères de recherche d'alternance
# Tout est écrit en minuscules : le scraper comparera en minuscules aussi.

# --- Critères de recherche (utilisés pour interroger les sources) ---
INTITULES = [
    "développeur web",
    "développeur python",
    "développeur full stack",
    "intégrateur web",
]

VILLES = ["nice", "cannes"]
RAYON_KM = 30
TELETRAVAIL = True

# --- Filtres appliqués sur les offres récupérées ---
# Une offre est écartée si son titre ou sa description contient un de ces mots.
MOTS_EXCLUS = [
    "senior",
    "confirmé",
    "expérimenté",
    "5 ans",
    "bac+5",
    "bac +5",
    "bac + 5",
    "master",
]

# Mots qui rendent une offre plus intéressante (utilisés plus tard pour un score).
MOTS_BONUS = ["python", "javascript", "html", "css", "git"]

# Une offre plus vieille que ça (en jours) n'est pas notifiée.
AGE_MAX_JOURS = 3

# --- Informations personnelles (pour toi, pas utilisées pour filtrer) ---
RYTHME = ""      # exemple : "1 semaine école / 3 semaines entreprise"
DEBUT = ""       # exemple : "septembre 2027"
