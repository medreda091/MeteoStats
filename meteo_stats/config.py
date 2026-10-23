"""Configuration de l'application : villes suivies, base de données, API météo."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Ville:
    nom: str
    latitude: float
    longitude: float


# Villes dont la météo est collectée (coordonnées : latitude, longitude)
VILLES = [
    Ville("Lyon", 45.75, 4.85),
    Ville("Paris", 48.85, 2.35),
    Ville("Marseille", 43.30, 5.37),
    Ville("Bordeaux", 44.84, -0.58),
    Ville("Lille", 50.63, 3.07),
    Ville("Strasbourg", 48.57, 7.75),
    Ville("Toulouse", 43.60, 1.44),
    Ville("Agadir", 30.43, -9.60),
]

# URL de la base : prise dans l'environnement, sinon SQLite local.
# Exemple PostgreSQL : postgresql://meteo:meteo@localhost:5432/meteo
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///meteo.db")

# API météo gratuite Open-Meteo (aucune clé requise)
API_METEO_URL = "https://api.open-meteo.com/v1/forecast"
API_TIMEOUT = 15


def trouver_ville(nom: str) -> Ville | None:
    """Retourne la ville suivie correspondant au nom (insensible à la casse)."""
    nom_nettoye = nom.strip().lower()
    for ville in VILLES:
        if ville.nom.lower() == nom_nettoye:
            return ville
    return None
