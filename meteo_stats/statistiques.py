"""Statistiques calculées à partir des mesures : résumés, classements, historique."""

from datetime import datetime, timedelta

from sqlalchemy import desc, func

from .models import Mesure


def resumer_ville(session, ville: str) -> dict | None:
    """Statistiques globales pour une ville : nb de mesures, min/max/moyenne,
    dernière mesure. Retourne None si la ville n'a aucune mesure."""
    ligne = (
        session.query(
            func.count(Mesure.id),
            func.min(Mesure.temperature),
            func.max(Mesure.temperature),
            func.avg(Mesure.temperature),
        )
        .filter(Mesure.ville == ville)
        .one()
    )
    if not ligne[0]:
        return None
    derniere = (
        session.query(Mesure)
        .filter(Mesure.ville == ville)
        .order_by(desc(Mesure.mesuree_le))
        .first()
    )
    return {
        "ville": ville,
        "nb_mesures": ligne[0],
        "temp_min": round(ligne[1], 1),
        "temp_max": round(ligne[2], 1),
        "temp_moyenne": round(float(ligne[3]), 1),
        "derniere_temperature": derniere.temperature,
        "dernier_releve": derniere.mesuree_le,
        "dernier_code_meteo": derniere.code_meteo,
    }


def tableau_villes(session) -> list[dict]:
    """Résumé pour chaque ville ayant au moins une mesure, trié par température
    moyenne décroissante."""
    villes = [v for (v,) in session.query(Mesure.ville).distinct().all()]
    resumes = [r for v in villes if (r := resumer_ville(session, v)) is not None]
    return sorted(resumes, key=lambda r: r["temp_moyenne"], reverse=True)


def _derniere_mesure_par_ville(session) -> dict[str, Mesure]:
    """La mesure la plus récente de chaque ville."""
    sous_requete = (
        session.query(Mesure.ville, func.max(Mesure.mesuree_le).label("max_le"))
        .group_by(Mesure.ville)
        .subquery()
    )
    mesures = (
        session.query(Mesure)
        .join(
            sous_requete,
            (Mesure.ville == sous_requete.c.ville)
            & (Mesure.mesuree_le == sous_requete.c.max_le),
        )
        .all()
    )
    return {m.ville: m for m in mesures}


def ville_la_plus_chaude(session) -> Mesure | None:
    """La ville avec la température la plus élevée au dernier relevé."""
    dernieres = _derniere_mesure_par_ville(session)
    if not dernieres:
        return None
    return max(dernieres.values(), key=lambda m: m.temperature)


def ville_la_plus_froide(session) -> Mesure | None:
    """La ville avec la température la plus basse au dernier relevé."""
    dernieres = _derniere_mesure_par_ville(session)
    if not dernieres:
        return None
    return min(dernieres.values(), key=lambda m: m.temperature)


def moyennes_journalieres(session, ville: str, jours: int = 7) -> list[dict]:
    """Températures moyennes par jour pour une ville sur les N derniers jours."""
    debut = datetime.now() - timedelta(days=jours)
    lignes = (
        session.query(
            func.date(Mesure.mesuree_le).label("jour"),
            func.avg(Mesure.temperature),
            func.min(Mesure.temperature),
            func.max(Mesure.temperature),
            func.count(Mesure.id),
        )
        .filter(Mesure.ville == ville, Mesure.mesuree_le >= debut)
        .group_by(func.date(Mesure.mesuree_le))
        .order_by("jour")
        .all()
    )
    return [
        {
            "jour": str(ligne[0]),
            "moyenne": round(float(ligne[1]), 1),
            "min": round(ligne[2], 1),
            "max": round(ligne[3], 1),
            "nb_mesures": ligne[4],
        }
        for ligne in lignes
    ]
