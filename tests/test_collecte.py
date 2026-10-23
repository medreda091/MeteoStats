"""Tests de la collecte : enregistrement des mesures, villes en échec."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from meteo_stats import collecte, config
from meteo_stats.client_meteo import ErreurMeteo
from meteo_stats.models import Base, Mesure, creer_tables


@pytest.fixture
def session():
    moteur = create_engine("sqlite:///:memory:")
    creer_tables(moteur)
    with Session(moteur) as s:
        yield s


def _meteo_fausse(temperature):
    return {
        "temperature": temperature,
        "temperature_ressentie": temperature - 1,
        "humidite": 60,
        "vitesse_vent": 10.0,
        "code_meteo": 1,
    }


def test_collecter_enregistre_une_mesure_par_ville(session, monkeypatch):
    monkeypatch.setattr(
        collecte, "recuperer_meteo", lambda ville: _meteo_fausse(20.0)
    )
    villes = [config.Ville("Lyon", 45.75, 4.85), config.Ville("Paris", 48.85, 2.35)]
    resultat = collecte.collecter(session, villes)
    assert resultat["reussies"] == ["Lyon", "Paris"]
    assert resultat["echouees"] == {}
    mesures = session.query(Mesure).all()
    assert len(mesures) == 2
    assert {m.ville for m in mesures} == {"Lyon", "Paris"}
    assert all(m.temperature == 20.0 for m in mesures)


def test_collecter_continue_malgre_une_ville_en_echec(session, monkeypatch):
    def faux_recuperer(ville):
        if ville.nom == "Paris":
            raise ErreurMeteo("panne réseau")
        return _meteo_fausse(15.0)

    monkeypatch.setattr(collecte, "recuperer_meteo", faux_recuperer)
    villes = [config.Ville("Lyon", 45.75, 4.85), config.Ville("Paris", 48.85, 2.35)]
    resultat = collecte.collecter(session, villes)
    assert resultat["reussies"] == ["Lyon"]
    assert "Paris" in resultat["echouees"]
    assert session.query(Mesure).count() == 1


def test_tables_creees_si_absentes():
    moteur = create_engine("sqlite:///:memory:")
    creer_tables(moteur)  # ne doit pas lever
    assert "mesures" in Base.metadata.tables
