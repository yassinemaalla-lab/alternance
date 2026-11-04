"""Verse le fichier national export_offres.json dans la base, filtré.

Ne garde que le département configuré. Les fiches « recruteurs » sont
conservées si leur code NAF est informatique. Les offres le sont si leur
titre correspond aux mots-clés.
"""

import ijson

import config
import db
from sources.lba import normaliser_entreprise, normaliser_offre, pertinente, secteur_informatique

CHEMIN = "export_offres.json"
LOT = 500


def _dans_departement(fiche):
    return fiche.get("departement") in config.DEPARTEMENTS


def importer(chemin=CHEMIN):
    db.initialiser()
    entreprises = []
    offres = []
    vues = 0
    nouvelles_entreprises = 0
    nouvelles_offres = 0

    def vider():
        nonlocal nouvelles_entreprises, nouvelles_offres
        if not entreprises and not offres:
            return
        ajout_e, ajout_o = db.enregistrer(entreprises, offres)
        nouvelles_entreprises += ajout_e
        nouvelles_offres += len(ajout_o)
        entreprises.clear()
        offres.clear()

    with open(chemin, "rb") as fichier:
        for bloc in ijson.items(fichier, "item"):
            vues += 1
            if vues % 100_000 == 0:
                print(f"{vues} fiches lues...")
            partenaire = (bloc.get("identifier") or {}).get("partner_label")
            if partenaire == "recruteurs_lba":
                entreprise = normaliser_entreprise(bloc)
                if _dans_departement(entreprise) and secteur_informatique(entreprise["code_naf"]):
                    entreprises.append(entreprise)
            else:
                offre = normaliser_offre(bloc)
                if not _dans_departement(offre):
                    continue
                if not pertinente(offre["titre"], offre["description"]):
                    continue
                entreprise = normaliser_entreprise(bloc, source=offre["partenaire"])
                if entreprise["cle"]:
                    entreprises.append(entreprise)
                else:
                    offre["entreprise_cle"] = ""
                offres.append(offre)
            if len(entreprises) + len(offres) >= LOT:
                vider()
        vider()

    exportes = db.exporter_entreprises()
    print(f"{vues} fiches lues")
    print(f"{nouvelles_entreprises} entreprises nouvelles, {nouvelles_offres} offres nouvelles")
    print(f"{exportes} entreprises écrites dans recruteurs_it.csv")
    print(db.resume())


if __name__ == "__main__":
    importer()
