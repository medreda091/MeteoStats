"""Libellés français des codes météo WMO retournés par l'API."""

_LIBELLES = {
    0: "ciel dégagé",
    1: "plutôt dégagé",
    2: "partiellement nuageux",
    3: "couvert",
    45: "brouillard",
    48: "brouillard givrant",
    51: "bruine légère",
    53: "bruine",
    55: "bruine dense",
    56: "bruine verglaçante légère",
    57: "bruine verglaçante dense",
    61: "pluie faible",
    63: "pluie",
    65: "pluie forte",
    66: "pluie verglaçante légère",
    67: "pluie verglaçante forte",
    71: "neige faible",
    73: "neige",
    75: "neige forte",
    77: "grésil",
    80: "averses faibles",
    81: "averses",
    82: "averses violentes",
    85: "averses de neige faibles",
    86: "averses de neige fortes",
    95: "orage",
    96: "orage avec grêle légère",
    99: "orage avec grêle forte",
}


def libelle_code(code: int | None) -> str:
    """Retourne le libellé français d'un code météo WMO (ou « inconnu »)."""
    if code is None:
        return "inconnu"
    return _LIBELLES.get(code, "inconnu")
