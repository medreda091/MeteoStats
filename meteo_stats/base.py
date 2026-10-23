"""Moteur SQLAlchemy et fabrique de sessions."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import config


def creer_moteur(url: str | None = None):
    """Crée le moteur SQLAlchemy pour l'URL donnée (ou celle de la config)."""
    return create_engine(url or config.DATABASE_URL)


def creer_session(moteur):
    """Retourne une fabrique de sessions liée au moteur."""
    return sessionmaker(bind=moteur)
