import pandas as pd

from observatoire.config import load_sources
from observatoire.vues import (
    Filtres,
    appliquer_filtres,
    diagnostic_selection_vide,
    libelles_departements,
    rentree_de_session,
    texte_source,
)

DF = pd.DataFrame(
    {
        "uai": ["A", "A", "B", "C"],
        "annee": [2024, 2025, 2025, 2025],
        "code_departement": ["93", "93", "94", "77"],
        "departement": ["SEINE-SAINT-DENIS", "SEINE-SAINT-DENIS", "VAL-DE-MARNE", "SEINE-ET-MARNE"],
        "secteur": ["public", "public", "privé", "public"],
    }
)


def test_rentree_de_session():
    assert rentree_de_session(2025) == "2024-2025"


def test_libelles_departements_tries_et_lisibles():
    assert libelles_departements(DF) == {
        "77": "77 · Seine-et-Marne",
        "93": "93 · Seine-Saint-Denis",
        "94": "94 · Val-de-Marne",
    }


def test_filtres_departement_secteur_session():
    f = Filtres(departements=["93", "94"], secteurs=["public"], session=2025)
    assert appliquer_filtres(DF, f)["uai"].tolist() == ["A"]
    assert appliquer_filtres(DF, f, toutes_sessions=True)["uai"].tolist() == ["A", "A"]


def test_selection_vide_messages():
    assert "Aucun département" in diagnostic_selection_vide(Filtres([], ["public"], 2025))
    assert "Aucun secteur" in diagnostic_selection_vide(Filtres(["93"], [], 2025))
    assert "combinaison" in diagnostic_selection_vide(Filtres(["93"], ["privé"], 2025))


def test_texte_source_contient_annees_licence_et_date():
    texte = texte_source(load_sources(), [2025])
    assert "rentrée 2024-2025" in texte and "session 2025" in texte
    assert "Licence Ouverte v2.0" in texte
    assert "2026-11-13" in texte
    assert "DEPP" in texte
    deux = texte_source(load_sources(), [2025, 2024])
    assert "rentrées 2023-2024, 2024-2025" in deux and "sessions 2024, 2025" in deux
