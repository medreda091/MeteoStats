"""Collecte : récupère la météo de chaque ville suivie et l'enregistre en base."""

from . import config
from .client_meteo import ErreurMeteo, recuperer_meteo
from .models import Mesure


def collecter(session, villes: list[config.Ville] | None = None) -> dict:
    """Collecte la météo des villes et enregistre une mesure par ville.

    Retourne un résumé : {"reussies": [...], "echouees": {ville: raison}}.
    Les villes en échec n'empêchent pas les autres d'être collectées.
    """
    villes = villes if villes is not None else config.VILLES
    reussies, echouees = [], {}
    for ville in villes:
        try:
            donnees = recuperer_meteo(ville)
        except ErreurMeteo as exc:
            echouees[ville.nom] = str(exc)
            continue
        session.add(Mesure(
            ville=ville.nom,
            temperature=donnees["temperature"],
            temperature_ressentie=donnees["temperature_ressentie"],
            humidite=donnees["humidite"],
            vitesse_vent=donnees["vitesse_vent"],
            code_meteo=donnees["code_meteo"],
        ))
        reussies.append(ville.nom)
    session.commit()
    return {"reussies": reussies, "echouees": echouees}
