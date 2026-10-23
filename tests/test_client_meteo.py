"""Tests du client météo : parsing de la réponse API et gestion des erreurs."""

import pytest
import requests

from meteo_stats import client_meteo, config

REPONSE_EXEMPLE = {
    "current": {
        "temperature_2m": 18.4,
        "relative_humidity_2m": 62,
        "apparent_temperature": 17.9,
        "weather_code": 2,
        "wind_speed_10m": 12.5,
    }
}


class ReponseSimulee:
    def __init__(self, json_data):
        self._json_data = json_data

    def raise_for_status(self):
        pass

    def json(self):
        return self._json_data


def test_recuperer_meteo_parse_la_reponse(monkeypatch):
    monkeypatch.setattr(
        client_meteo.requests, "get", lambda *a, **k: ReponseSimulee(REPONSE_EXEMPLE)
    )
    ville = config.Ville("Lyon", 45.75, 4.85)
    resultat = client_meteo.recuperer_meteo(ville)
    assert resultat["temperature"] == 18.4
    assert resultat["temperature_ressentie"] == 17.9
    assert resultat["humidite"] == 62
    assert resultat["vitesse_vent"] == 12.5
    assert resultat["code_meteo"] == 2


def test_recuperer_meteo_envoie_les_bonnes_coords(monkeypatch):
    appele_avec = {}

    def faux_get(url, params=None, timeout=None):
        appele_avec["url"] = url
        appele_avec["params"] = params
        return ReponseSimulee(REPONSE_EXEMPLE)

    monkeypatch.setattr(client_meteo.requests, "get", faux_get)
    ville = config.Ville("Agadir", 30.43, -9.60)
    client_meteo.recuperer_meteo(ville)
    assert appele_avec["params"]["latitude"] == 30.43
    assert appele_avec["params"]["longitude"] == -9.60


def test_recuperer_meteo_erreur_reseau(monkeypatch):
    def faux_get(*a, **k):
        raise requests.ConnectionError("coupure")

    monkeypatch.setattr(client_meteo.requests, "get", faux_get)
    with pytest.raises(client_meteo.ErreurMeteo):
        client_meteo.recuperer_meteo(config.Ville("Lyon", 45.75, 4.85))


def test_recuperer_meteo_reponse_incomplete(monkeypatch):
    monkeypatch.setattr(
        client_meteo.requests, "get", lambda *a, **k: ReponseSimulee({"current": {}})
    )
    with pytest.raises(client_meteo.ErreurMeteo):
        client_meteo.recuperer_meteo(config.Ville("Lyon", 45.75, 4.85))
