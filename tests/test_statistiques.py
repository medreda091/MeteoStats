"""Tests des statistiques : résumés, classements, historique journalier."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from meteo_stats import statistiques
from meteo_stats.codes import libelle_code
from meteo_stats.models import Mesure, creer_tables


@pytest.fixture
def session():
    moteur = create_engine("sqlite:///:memory:")
    creer_tables(moteur)
    with Session(moteur) as s:
        # Lyon : 3 mesures, Paris : 2 mesures, aucune pour Marseille
        for temp in (10.0, 14.0, 12.0):
            s.add(Mesure(ville="Lyon", temperature=temp, code_meteo=1,
                         mesuree_le=datetime.now() - timedelta(hours=1)))
        s.add(Mesure(ville="Paris", temperature=8.0, code_meteo=3,
                     mesuree_le=datetime.now() - timedelta(days=2)))
        s.add(Mesure(ville="Paris", temperature=22.0, code_meteo=0,
                     mesuree_le=datetime.now()))
        s.commit()
        yield s


def test_resumer_ville(session):
    resume = statistiques.resumer_ville(session, "Lyon")
    assert resume["nb_mesures"] == 3
    assert resume["temp_min"] == 10.0
    assert resume["temp_max"] == 14.0
    assert resume["temp_moyenne"] == 12.0


def test_resumer_ville_sans_mesure(session):
    assert statistiques.resumer_ville(session, "Marseille") is None


def test_tableau_villes_trie_par_moyenne(session):
    tableau = statistiques.tableau_villes(session)
    assert [r["ville"] for r in tableau] == ["Paris", "Lyon"]  # 15.0 > 12.0


def test_ville_la_plus_chaude_et_froide(session):
    chaude = statistiques.ville_la_plus_chaude(session)
    froide = statistiques.ville_la_plus_froide(session)
    # derniers relevés : Paris 22.0, Lyon 12.0 (le plus récent des trois)
    assert chaude.ville == "Paris"
    assert froide.ville == "Lyon"


def test_villes_sans_mesure(session):
    session.query(Mesure).delete()
    assert statistiques.ville_la_plus_chaude(session) is None
    assert statistiques.ville_la_plus_froide(session) is None


def test_moyennes_journalieres(session):
    lignes = statistiques.moyennes_journalieres(session, "Paris", jours=7)
    assert len(lignes) == 2  # deux jours distincts
    assert lignes[0]["min"] == 8.0
    assert lignes[1]["max"] == 22.0


def test_libelle_code():
    assert libelle_code(0) == "ciel dégagé"
    assert libelle_code(95) == "orage"
    assert libelle_code(999) == "inconnu"
    assert libelle_code(None) == "inconnu"
