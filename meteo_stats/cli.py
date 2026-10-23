"""Ligne de commande MeteoStats : collecter, stats, historique, villes."""

import argparse

from . import config, statistiques
from .base import creer_moteur, creer_session
from .codes import libelle_code
from .collecte import collecter
from .models import creer_tables


def _ouvrir_session(url: str | None):
    moteur = creer_moteur(url)
    creer_tables(moteur)
    return creer_session(moteur)()


def commande_collecter(args):
    session = _ouvrir_session(args.db)
    resultat = collecter(session)
    for ville in resultat["reussies"]:
        print(f"  ✓ {ville}")
    for ville, raison in resultat["echouees"].items():
        print(f"  ✗ {ville} : {raison}")
    print(f"{len(resultat['reussies'])} ville(s) collectée(s).")


def commande_stats(args):
    session = _ouvrir_session(args.db)
    resumes = statistiques.tableau_villes(session)
    if not resumes:
        print("Aucune mesure en base pour le moment — lancez d'abord « collecter ».")
        return
    print(f"{'Ville':<12} {'Mesures':>7} {'Min':>6} {'Moy':>6} {'Max':>6}  Dernier relevé")
    print("-" * 70)
    for r in resumes:
        print(
            f"{r['ville']:<12} {r['nb_mesures']:>7} {r['temp_min']:>5}°C"
            f" {r['temp_moyenne']:>5}°C {r['temp_max']:>5}°C"
            f"  {r['derniere_temperature']}°C ({libelle_code(r['dernier_code_meteo'])})"
        )
    chaude = statistiques.ville_la_plus_chaude(session)
    froide = statistiques.ville_la_plus_froide(session)
    print()
    print(f"La plus chaude : {chaude.ville} ({chaude.temperature}°C)")
    print(f"La plus froide : {froide.ville} ({froide.temperature}°C)")


def commande_historique(args):
    if config.trouver_ville(args.ville) is None:
        print(f"Ville inconnue : {args.ville} (voir « villes » pour la liste).")
        return
    session = _ouvrir_session(args.db)
    lignes = statistiques.moyennes_journalieres(session, args.ville, args.jours)
    if not lignes:
        print(f"Aucune mesure pour {args.ville} sur la période.")
        return
    print(f"Historique {args.ville} — {args.jours} derniers jours")
    print(f"{'Jour':<12} {'Moyenne':>7} {'Min':>6} {'Max':>6}")
    print("-" * 35)
    for ligne in lignes:
        print(f"{ligne['jour']:<12} {ligne['moyenne']:>6}°C {ligne['min']:>5}°C"
              f" {ligne['max']:>5}°C")


def commande_villes(_args):
    print("Villes suivies :")
    for ville in config.VILLES:
        print(f"  - {ville.nom} ({ville.latitude}, {ville.longitude})")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="meteo-stats", description="Collecte et statistiques météo par ville."
    )
    parser.add_argument("--db", default=None,
                        help="URL de la base (défaut : DATABASE_URL ou SQLite local)")
    sous = parser.add_subparsers(dest="commande", required=True)

    sous.add_parser("collecter", help="récupère la météo et l'enregistre en base")
    sous.add_parser("stats", help="affiche les statistiques par ville")

    p_histo = sous.add_parser("historique", help="moyennes journalières d'une ville")
    p_histo.add_argument("--ville", required=True)
    p_histo.add_argument("--jours", type=int, default=7)

    sous.add_parser("villes", help="liste les villes suivies")

    args = parser.parse_args(argv)
    {"collecter": commande_collecter, "stats": commande_stats,
     "historique": commande_historique, "villes": commande_villes}[args.commande](args)


if __name__ == "__main__":
    main()
