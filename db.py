import csv
import sqlite3

CHEMIN_DB = "alternance.db"


def connexion():
    c = sqlite3.connect(CHEMIN_DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


def initialiser():
    """Crée les tables. Remplace l'ancienne table offres, vide et trop plate."""
    with connexion() as c:
        colonnes = [r[1] for r in c.execute("PRAGMA table_info(offres)")]
        if colonnes and "entreprise_cle" not in colonnes:
            c.execute("DROP TABLE offres")

        c.executescript("""
            CREATE TABLE IF NOT EXISTS entreprises (
                cle              TEXT PRIMARY KEY,
                siret            TEXT,
                nom              TEXT NOT NULL,
                adresse          TEXT,
                code_postal      TEXT,
                departement      TEXT,
                code_naf         TEXT,
                libelle_naf      TEXT,
                taille           TEXT,
                site             TEXT,
                telephone        TEXT,
                lien_candidature TEXT,
                latitude         REAL,
                longitude        REAL,
                source           TEXT,
                cree_le          TEXT NOT NULL DEFAULT (datetime('now')),
                maj_le           TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS offres (
                cle             TEXT PRIMARY KEY,
                titre           TEXT NOT NULL,
                description     TEXT,
                entreprise_cle  TEXT REFERENCES entreprises(cle),
                entreprise_nom  TEXT,
                adresse         TEXT,
                code_postal     TEXT,
                departement     TEXT,
                latitude        REAL,
                longitude       REAL,
                date_creation   TEXT,
                lien            TEXT,
                partenaire      TEXT,
                codes_rome      TEXT,
                type_contrat    TEXT,
                duree_mois      INTEGER,
                pertinente      INTEGER NOT NULL DEFAULT 1,
                notifiee        INTEGER NOT NULL DEFAULT 0,
                premiere_vue    TEXT NOT NULL DEFAULT (datetime('now')),
                derniere_vue    TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS suivis (
                id             INTEGER PRIMARY KEY,
                entreprise_cle TEXT REFERENCES entreprises(cle),
                offre_cle      TEXT REFERENCES offres(cle),
                statut         TEXT NOT NULL DEFAULT 'a_contacter',
                date_contact   TEXT,
                note           TEXT,
                cree_le        TEXT NOT NULL DEFAULT (datetime('now')),
                maj_le         TEXT NOT NULL DEFAULT (datetime('now')),
                CHECK (entreprise_cle IS NOT NULL OR offre_cle IS NOT NULL)
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_entreprises_siret
                ON entreprises(siret) WHERE siret IS NOT NULL AND siret != '';
            CREATE INDEX IF NOT EXISTS idx_entreprises_dept ON entreprises(departement);
            CREATE INDEX IF NOT EXISTS idx_entreprises_naf ON entreprises(code_naf);
            CREATE INDEX IF NOT EXISTS idx_offres_dept ON offres(departement, pertinente);
            CREATE INDEX IF NOT EXISTS idx_offres_notifiee ON offres(notifiee, pertinente);
            CREATE INDEX IF NOT EXISTS idx_suivis_entreprise ON suivis(entreprise_cle);
        """)


def enregistrer_entreprise(c, entreprise):
    """Insère ou met à jour. Les champs vides ne remplacent pas une valeur déjà connue."""
    if not entreprise.get("cle") or not entreprise.get("nom"):
        return False
    existe = c.execute(
        "SELECT 1 FROM entreprises WHERE cle = ?", (entreprise["cle"],)
    ).fetchone()
    c.execute("""
        INSERT INTO entreprises (
            cle, siret, nom, adresse, code_postal, departement,
            code_naf, libelle_naf, taille, site, telephone, lien_candidature,
            latitude, longitude, source
        ) VALUES (
            :cle, :siret, :nom, :adresse, :code_postal, :departement,
            :code_naf, :libelle_naf, :taille, :site, :telephone, :lien_candidature,
            :latitude, :longitude, :source
        )
        ON CONFLICT(cle) DO UPDATE SET
            siret = COALESCE(NULLIF(excluded.siret, ''), entreprises.siret),
            nom = excluded.nom,
            adresse = COALESCE(NULLIF(excluded.adresse, ''), entreprises.adresse),
            code_postal = COALESCE(NULLIF(excluded.code_postal, ''), entreprises.code_postal),
            departement = COALESCE(NULLIF(excluded.departement, ''), entreprises.departement),
            code_naf = COALESCE(NULLIF(excluded.code_naf, ''), entreprises.code_naf),
            libelle_naf = COALESCE(NULLIF(excluded.libelle_naf, ''), entreprises.libelle_naf),
            taille = COALESCE(NULLIF(excluded.taille, ''), entreprises.taille),
            site = COALESCE(NULLIF(excluded.site, ''), entreprises.site),
            telephone = COALESCE(NULLIF(excluded.telephone, ''), entreprises.telephone),
            lien_candidature = COALESCE(NULLIF(excluded.lien_candidature, ''), entreprises.lien_candidature),
            latitude = COALESCE(excluded.latitude, entreprises.latitude),
            longitude = COALESCE(excluded.longitude, entreprises.longitude),
            source = COALESCE(NULLIF(excluded.source, ''), entreprises.source),
            maj_le = datetime('now')
    """, entreprise)
    return existe is None


def enregistrer_offre(c, offre):
    """Insère l'offre. Si elle existe déjà, rafraîchit le contenu sans perdre le suivi."""
    if not offre.get("entreprise_cle"):
        offre["entreprise_cle"] = None
    existe = c.execute("SELECT 1 FROM offres WHERE cle = ?", (offre["cle"],)).fetchone()
    if existe is None:
        c.execute("""
            INSERT INTO offres (
                cle, titre, description, entreprise_cle, entreprise_nom,
                adresse, code_postal, departement, latitude, longitude,
                date_creation, lien, partenaire, codes_rome, type_contrat,
                duree_mois, pertinente
            ) VALUES (
                :cle, :titre, :description, :entreprise_cle, :entreprise_nom,
                :adresse, :code_postal, :departement, :latitude, :longitude,
                :date_creation, :lien, :partenaire, :codes_rome, :type_contrat,
                :duree_mois, :pertinente
            )
        """, offre)
        return True
    c.execute("""
        UPDATE offres SET
            titre = :titre,
            description = COALESCE(NULLIF(:description, ''), description),
            entreprise_cle = COALESCE(:entreprise_cle, entreprise_cle),
            entreprise_nom = COALESCE(NULLIF(:entreprise_nom, ''), entreprise_nom),
            adresse = COALESCE(NULLIF(:adresse, ''), adresse),
            code_postal = COALESCE(NULLIF(:code_postal, ''), code_postal),
            departement = COALESCE(NULLIF(:departement, ''), departement),
            latitude = COALESCE(:latitude, latitude),
            longitude = COALESCE(:longitude, longitude),
            date_creation = COALESCE(NULLIF(:date_creation, ''), date_creation),
            lien = COALESCE(NULLIF(:lien, ''), lien),
            partenaire = COALESCE(NULLIF(:partenaire, ''), partenaire),
            codes_rome = COALESCE(NULLIF(:codes_rome, ''), codes_rome),
            type_contrat = COALESCE(NULLIF(:type_contrat, ''), type_contrat),
            duree_mois = COALESCE(:duree_mois, duree_mois),
            pertinente = :pertinente,
            derniere_vue = datetime('now')
        WHERE cle = :cle
    """, offre)
    return False


def enregistrer(entreprises, offres):
    """Enregistre un lot. Les entreprises passent avant les offres à cause de la clé étrangère."""
    nouvelles_entreprises = 0
    nouvelles_offres = []
    with connexion() as c:
        for entreprise in entreprises:
            if enregistrer_entreprise(c, entreprise):
                nouvelles_entreprises += 1
        for offre in offres:
            if enregistrer_offre(c, offre):
                nouvelles_offres.append(offre)
    return nouvelles_entreprises, nouvelles_offres


def offres_a_notifier(age_max_jours):
    with connexion() as c:
        return c.execute("""
            SELECT * FROM offres
            WHERE pertinente = 1
              AND notifiee = 0
              AND (
                    date_creation IS NULL
                    OR date_creation = ''
                    OR date(date_creation) >= date('now', ?)
                  )
            ORDER BY date_creation DESC
        """, (f"-{int(age_max_jours)} days",)).fetchall()


def marquer_notifiee(cle):
    with connexion() as c:
        c.execute("UPDATE offres SET notifiee = 1 WHERE cle = ?", (cle,))


def ajouter_suivi(entreprise_cle=None, offre_cle=None, statut="a_contacter", note=""):
    if not entreprise_cle and not offre_cle:
        raise ValueError("Un suivi vise une entreprise ou une offre.")
    with connexion() as c:
        c.execute("""
            INSERT INTO suivis (entreprise_cle, offre_cle, statut, note)
            VALUES (?, ?, ?, ?)
        """, (entreprise_cle, offre_cle, statut, note))


def resume():
    with connexion() as c:
        return {
            "entreprises": c.execute("SELECT COUNT(*) FROM entreprises").fetchone()[0],
            "offres": c.execute("SELECT COUNT(*) FROM offres").fetchone()[0],
            "offres_a_notifier": c.execute(
                "SELECT COUNT(*) FROM offres WHERE pertinente = 1 AND notifiee = 0"
            ).fetchone()[0],
            "suivis": c.execute("SELECT COUNT(*) FROM suivis").fetchone()[0],
        }


def exporter_entreprises(chemin="recruteurs_it.csv"):
    with connexion() as c:
        lignes = c.execute("""
            SELECT nom, adresse, code_postal, departement, libelle_naf, taille,
                   site, lien_candidature, telephone
            FROM entreprises
            ORDER BY departement, code_postal, nom
        """).fetchall()
    if not lignes:
        print("Aucune entreprise à exporter.")
        return 0
    champs = lignes[0].keys()
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(dict(ligne) for ligne in lignes)
    return len(lignes)


if __name__ == "__main__":
    initialiser()
    print("Base prête :", CHEMIN_DB)
    print(resume())
