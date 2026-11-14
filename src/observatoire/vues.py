"""Calculs du tableau de bord, sans Streamlit (donc testables).

Les écrans de app/ appellent ces fonctions ; ils ne font que de l'affichage.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Filtres:
    departements: list[str]
    secteurs: list[str]
    session: int


def rentree_de_session(session: int) -> str:
    """Session du brevet N → année scolaire « N-1-N » (D-005). Ex. 2025 → « 2024-2025 »."""
    return f"{session - 1}-{session}"


PETITS_MOTS = {"et", "de", "du", "des", "la", "le", "les", "sur", "sous", "en"}


def nom_propre(nom: str) -> str:
    """« SEINE-ET-MARNE » → « Seine-et-Marne » (petits mots en minuscules, sauf en tête)."""
    def mot(m: str, premier: bool) -> str:
        return m.lower() if (m.lower() in PETITS_MOTS and not premier) else m.capitalize()

    return " ".join(
        "-".join(mot(m, i == 0 and j == 0) for j, m in enumerate(bloc.split("-")))
        for i, bloc in enumerate(nom.split())
    )


def libelles_departements(df: pd.DataFrame) -> dict[str, str]:
    """{code: « code · Nom »}, ex. {"93": "93 · Seine-Saint-Denis"}, d'après les données."""
    paires = df[["code_departement", "departement"]].dropna().drop_duplicates("code_departement")
    return {
        code: f"{code} · {nom_propre(nom)}"
        for code, nom in sorted(zip(paires["code_departement"], paires["departement"]))
    }


def appliquer_filtres(df: pd.DataFrame, filtres: Filtres, toutes_sessions: bool = False) -> pd.DataFrame:
    """Lignes du département et du secteur choisis ; une seule session sauf si `toutes_sessions`."""
    masque = df["code_departement"].isin(filtres.departements) & df["secteur"].isin(filtres.secteurs)
    if not toutes_sessions:
        masque &= df["annee"] == filtres.session
    return df[masque]


def diagnostic_selection_vide(filtres: Filtres) -> str:
    """Message clair quand les filtres ne renvoient aucun collège."""
    if not filtres.departements:
        return "Aucun département n'est sélectionné : choisissez-en au moins un dans la barre latérale."
    if not filtres.secteurs:
        return "Aucun secteur n'est sélectionné : choisissez « public », « privé » ou les deux dans la barre latérale."
    return (
        "Aucun collège ne correspond à cette combinaison de filtres. "
        "Élargissez la sélection de départements ou de secteurs."
    )


def _court(texte: str, separateur: str) -> str:
    return texte.split(separateur)[0].strip()


def texte_source(sources: list[dict], sessions: list[int]) -> str:
    """Ligne de source à afficher sous chaque chiffre : producteur, jeux, années, licence, date d'accès."""
    sessions = sorted(sessions)
    rentrees = ", ".join(rentree_de_session(s) for s in sessions)
    libelle_sessions = ", ".join(str(s) for s in sessions)
    par_id = {s["id"]: s for s in sources}
    producteurs = sorted({_court(s["producteur"], ",") for s in sources})
    licences = sorted({_court(_court(s["licence"], "("), ",") for s in sources})
    dates = sorted({str(s["date_acces"]) for s in sources})
    pluriel = "s" if len(sessions) > 1 else ""
    return (
        f"Source : {', '.join(producteurs)}, « {par_id['ips_colleges']['nom']} » (rentrée{pluriel} {rentrees}) "
        f"et « {par_id['ivac_colleges']['nom']} » (session{pluriel} {libelle_sessions}). "
        f"{', '.join(licences)}. Consulté le {', '.join(dates)}."
    )
