"""Modèle de données : une mesure météo pour une ville à un instant donné."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Mesure(Base):
    """Une mesure météo collectée pour une ville."""

    __tablename__ = "mesures"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ville: Mapped[str] = mapped_column(String(80), index=True)
    temperature: Mapped[float] = mapped_column(Float)
    temperature_ressentie: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidite: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vitesse_vent: Mapped[float | None] = mapped_column(Float, nullable=True)
    code_meteo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mesuree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Mesure {self.ville} {self.temperature}°C le {self.mesuree_le:%d/%m %H:%M}>"


def creer_tables(moteur):
    """Crée les tables en base si elles n'existent pas encore."""
    Base.metadata.create_all(moteur)
