# Alternance informatique — Alpes-Maritimes

Recherche d'offres et d'entreprises via l'API [La Bonne Alternance](https://api.apprentissage.beta.gouv.fr). Les critères sont dans `config.py`. Le jeton `LBA_TOKEN` est dans `.env`.

## Base

SQLite, fichier `alternance.db` (non versionné).

- `entreprises` : recruteurs, identifiés par SIRET quand il existe
- `offres` : annonces liées à une entreprise, avec un drapeau « déjà notifiée »
- `suivis` : contacts (statut, date, note)

## Commandes

```bash
python main.py            # interroge l'API autour de Nice, Sophia et Cannes
python export_offres.py   # télécharge le fichier national
python importer.py        # en garde le département 06 dans la base
python db.py              # crée la base et affiche les comptes
```
