# MeteoStats

Pipeline de collecte météo qui récupère les conditions actuelles de plusieurs villes,
les stocke dans une base PostgreSQL (ou SQLite en local) et calcule des statistiques
par ville : températures min / max / moyennes, ville la plus chaude, historique.

Les données viennent de l'API gratuite **Open-Meteo** (aucune clé requise).

## Stack

- Python 3.12
- SQLAlchemy (PostgreSQL en prod via Docker, SQLite en local)
- API Open-Meteo (données météo, sans clé)
- Docker / Docker Compose
- GitHub Actions (CI : tests automatiques)

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copier la configuration d'exemple puis adapter si besoin :

```bash
cp .env.example .env
```

Par défaut, sans `DATABASE_URL`, l'application utilise un fichier SQLite `meteo.db`
dans le dossier courant.

## Utilisation

Collecter la météo de toutes les villes suivies :

```bash
python -m meteo_stats.cli collecter
```

Afficher les statistiques par ville :

```bash
python -m meteo_stats.cli stats
```

Voir l'historique d'une ville (moyennes journalières) :

```bash
python -m meteo_stats.cli historique --ville Lyon --jours 7
```

Lister les villes suivies :

```bash
python -m meteo_stats.cli villes
```

On peut forcer une autre base avec `--db` :

```bash
python -m meteo_stats.cli --db postgresql://user:pass@localhost:5432/meteo collecter
```

### Avec Docker

```bash
docker compose up -d
```

Le service `db` démarre PostgreSQL et le service `collecteur` lance une collecte
toutes les heures. Les statistiques restent consultables avec la CLI :

```bash
docker compose exec collecteur python -m meteo_stats.cli stats
```

## Villes suivies

Lyon, Paris, Marseille, Bordeaux, Lille, Strasbourg, Toulouse et Agadir.
La liste se configure dans `meteo_stats/config.py`.

## Structure du projet

```
MeteoStats/
├── meteo_stats/
│   ├── config.py        # villes suivies, URL de la base, paramètres API
│   ├── base.py          # moteur SQLAlchemy et sessions
│   ├── models.py        # modèle Mesure
│   ├── client_meteo.py  # appels à l'API Open-Meteo
│   ├── codes.py         # libellés français des codes météo (WMO)
│   ├── collecte.py      # collecte et enregistrement des mesures
│   ├── statistiques.py  # calculs : résumés, classements, historique
│   └── cli.py           # ligne de commande
├── tests/               # tests automatisés (pytest)
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Tests

```bash
pytest -v
```

Les tests utilisent une base SQLite en mémoire et simulent les appels réseau :
aucune connexion réelle n'est nécessaire.

## Licence

MIT — voir le fichier `LICENSE`.
