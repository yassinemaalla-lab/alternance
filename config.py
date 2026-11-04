# Critères de recherche d'alternance informatique, autour de Nice.
# Les comparaisons de texte se font en minuscules.

# Département conservé quand on importe le fichier national.
DEPARTEMENTS = ("06",)

ZONES = {
    "Nice": (43.7102, 7.2620),
    "Sophia Antipolis": (43.6163, 7.0551),
    "Cannes": (43.5528, 7.0174),
}
RAYON_KM = 50

# Code ROME confirmé : études et développement informatique.
CODES_ROME = ["M1805"]

# Recherche de recruteurs, élargie puis resserrée par le code NAF.
CODES_ROME_RECRUTEURS = ["M1805", "M1801", "M1818", "M1830", "M1856"]

# Programmation, édition de logiciels, traitement de données, portails.
NAF_OK = ("62.", "58.29", "63.11", "63.12")

# Un de ces mots doit apparaître dans le titre.
MOTS_CLES_TITRE = [
    "développeur", "developpeur", "informatique", "full stack", "fullstack",
    "devops", "cyber", "administrateur système", "administrateur réseau",
    "technicien support", "support informatique", "intégrateur web",
    "data analyst", "data scientist", "ingénieur logiciel",
]

# L'offre est écartée si le titre ou la description contient un de ces mots.
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

# Sert plus tard à classer les offres.
MOTS_BONUS = ["python", "javascript", "html", "css", "git"]

# Au-delà de cet âge, une offre n'est plus proposée à la notification.
AGE_MAX_JOURS = 3

# Repères personnels, non utilisés pour filtrer.
RYTHME = ""  # exemple : "1 semaine école / 3 semaines entreprise"
DEBUT = ""   # exemple : "septembre 2027"
