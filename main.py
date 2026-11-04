"""Interroge La Bonne Alternance et enregistre les nouveautés."""

import config
import db
from sources.lba import chercher_offres, chercher_recruteurs, normaliser_entreprise


def main():
    db.initialiser()
    offres_brutes = chercher_offres()
    recruteurs = chercher_recruteurs()

    entreprises = dict(recruteurs)
    offres = []
    for brute, offre in offres_brutes.values():
        entreprise = normaliser_entreprise(brute, source=offre["partenaire"])
        if entreprise["cle"]:
            entreprises.setdefault(entreprise["cle"], entreprise)
        else:
            offre["entreprise_cle"] = ""
        offres.append(offre)

    nouvelles_entreprises, nouvelles_offres = db.enregistrer(
        entreprises.values(), offres
    )
    a_voir = db.offres_a_notifier(config.AGE_MAX_JOURS)

    print(f"{nouvelles_entreprises} entreprises nouvelles")
    print(f"{len(nouvelles_offres)} offres nouvelles, {len(a_voir)} à notifier")
    for offre in a_voir:
        print("-", offre["titre"], "|", offre["entreprise_nom"] or "?", "|", offre["adresse"])
    print(db.resume())


if __name__ == "__main__":
    main()
