"""Outils partagés par tous les écrans : chargement des données, filtres, ligne de source.

Les calculs sont dans src/observatoire/vues.py (testés) ; ce fichier ne fait que de l'affichage Streamlit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from observatoire.config import OUTPUT_CSV, load_sources  # noqa: E402
from observatoire.quality import REQUIRED  # noqa: E402
from observatoire.vues import (  # noqa: E402
    Filtres,
    appliquer_filtres,
    diagnostic_selection_vide,
    libelles_departements,
    texte_source,
)

ACCENT = "#1F4E79"  # bleu foncé, contraste 8,7:1 sur blanc (calculé selon WCAG)
GRIS = "#595959"    # gris foncé, contraste 7,0:1 sur blanc

MESSAGE_FICHIER_ABSENT = (
    "Les données préparées sont introuvables (`data/processed/observatoire.csv`).\n\n"
    "Lancez d'abord le pipeline dans un terminal, depuis le dossier du projet :\n\n"
    "- vraies données : `python -m observatoire.pipeline`\n"
    "- échantillon, sans internet : `python -m observatoire.pipeline --sample`\n\n"
    "Puis rechargez cette page."
)


@st.cache_data
def _lire(chemin: str, date_modif: float) -> pd.DataFrame:
    # `date_modif` fait partie de la clé du cache : si le pipeline réécrit le fichier, il est relu.
    return pd.read_csv(chemin, dtype={"uai": str, "code_departement": str, "code_commune": str})


def charger_donnees() -> tuple[pd.DataFrame | None, str | None]:
    """Renvoie (données, None) ou (None, message d'erreur lisible)."""
    if not OUTPUT_CSV.exists():
        return None, MESSAGE_FICHIER_ABSENT
    try:
        df = _lire(str(OUTPUT_CSV), OUTPUT_CSV.stat().st_mtime)
    except Exception as erreur:  # fichier corrompu, illisible…
        return None, f"Le fichier de données existe mais n'a pas pu être lu ({erreur}). Relancez le pipeline."
    manquantes = [c for c in REQUIRED if c not in df.columns]
    if manquantes:
        return None, f"Le fichier de données est incomplet (colonnes manquantes : {manquantes}). Relancez le pipeline."
    if df.empty:
        return None, "Le fichier de données est vide. Relancez le pipeline."
    return df, None


def donnees_ou_arret() -> pd.DataFrame:
    """Pour les écrans qui ont besoin des données : affiche l'erreur et arrête l'écran si besoin."""
    df, erreur = charger_donnees()
    if erreur:
        st.error(erreur, icon="⚠️")
        st.stop()
    return df


def barre_filtres(df: pd.DataFrame) -> Filtres:
    """Filtres communs à tous les écrans, dans la barre latérale."""
    libelles = libelles_departements(df)
    sessions = sorted(int(a) for a in df["annee"].dropna().unique())
    with st.sidebar:
        st.header("Filtres")
        departements = st.multiselect(
            "Départements", list(libelles), default=list(libelles), format_func=libelles.get, key="f_dep"
        )
        secteurs = st.multiselect("Secteur", ["public", "privé"], default=["public", "privé"], key="f_sect")
        session = st.radio(
            "Session du brevet", sessions, index=len(sessions) - 1, horizontal=True, key="f_session",
            help="Session 2025 = année scolaire 2024-2025. Certains écrans utilisent les deux sessions : ils l'indiquent.",
        )
        st.caption(
            "Les seuils (médiane de l'IPS) sont toujours calculés sur toute l'académie : "
            "les filtres changent ce qui est affiché, pas la définition de « prioritaire »."
        )
    filtres = Filtres(departements=list(departements), secteurs=list(secteurs), session=int(session))
    st.session_state["filtres"] = filtres
    return filtres


def filtres_courants() -> Filtres:
    return st.session_state["filtres"]


def selection_ou_arret(df: pd.DataFrame, toutes_sessions: bool = False) -> pd.DataFrame:
    """Données filtrées ; si aucun collège ne correspond, message clair et arrêt de l'écran."""
    filtres = filtres_courants()
    vue = appliquer_filtres(df, filtres, toutes_sessions=toutes_sessions)
    if vue.empty:
        st.warning(diagnostic_selection_vide(filtres), icon="🔎")
        st.stop()
    return vue


def source(sessions: list[int]) -> None:
    """Ligne de source sous un chiffre ou un graphique : producteur, jeux, années, licence, date d'accès."""
    st.caption(texte_source(load_sources(), sessions))
