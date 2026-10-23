"""Client pour l'API météo gratuite Open-Meteo (aucune clé requise)."""

import requests

from . import config


class ErreurMeteo(Exception):
    """Levée quand la récupération des données météo échoue."""


def recuperer_meteo(ville: config.Ville) -> dict:
    """Récupère les conditions actuelles pour une ville.

    Retourne un dict avec : temperature, temperature_ressentie, humidite,
    vitesse_vent, code_meteo. Lève ErreurMeteo en cas de problème réseau
    ou de réponse inattendue.
    """
    params = {
        "latitude": ville.latitude,
        "longitude": ville.longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                   "weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    try:
        reponse = requests.get(config.API_METEO_URL, params=params,
                               timeout=config.API_TIMEOUT)
        reponse.raise_for_status()
        donnees = reponse.json().get("current", {})
    except (requests.RequestException, ValueError) as exc:
        raise ErreurMeteo(f"impossible de récupérer la météo de {ville.nom}") from exc

    try:
        return {
            "temperature": float(donnees["temperature_2m"]),
            "temperature_ressentie": float(donnees["apparent_temperature"]),
            "humidite": int(donnees["relative_humidity_2m"]),
            "vitesse_vent": float(donnees["wind_speed_10m"]),
            "code_meteo": int(donnees["weather_code"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ErreurMeteo(f"réponse inattendue de l'API pour {ville.nom}") from exc
