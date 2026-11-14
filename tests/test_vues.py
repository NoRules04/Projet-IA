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


def test_format_francais():
    from observatoire.vues import fr

    assert fr(100.9) == "100,9"
    assert fr(-0.1449, 2) == "-0,14"
    assert fr(1234.5) == "1 234,5"
    assert fr(None) == "—" and fr(float("nan")) == "—"


def test_vue_ensemble_mediane_academie_et_filtres():
    from observatoire.vues import vue_ensemble

    # 10 collèges en 2025 : IPS 80..170 → médiane 125 ; dépts 93 (5 premiers) et 94.
    ips = [80, 90, 100, 110, 120, 130, 140, 150, 160, 170]
    va = [-3, 2, -1, None, 4, -2, 1, 0, -5, 3]
    df = pd.DataFrame({
        "uai": [f"U{i}" for i in range(10)], "annee": 2025, "ips": ips, "va_taux_reussite_g": va,
        "taux_reussite_g": [70 + i for i in range(10)],
        "code_departement": ["93"] * 5 + ["94"] * 5, "secteur": "public",
    })
    df["va_taux_reussite_g"] = df["va_taux_reussite_g"].astype("Float64")
    places, r = vue_ensemble(df, Filtres(["93"], ["public"], 2025), "A")
    assert r["mediane_ips"] == 125.0  # calculée sur toute l'académie, pas sur le 93 seul
    assert r["n_selection"] == 5 and r["n_places"] == 4 and r["n_sans_va"] == 1
    assert sorted(places.loc[places["prioritaire"], "uai"]) == ["U0", "U2"]  # IPS < 125 et VA < 0
    assert r["n_prioritaires"] == 2
    assert r["r_ips_taux"] is None  # moins de 10 collèges : pas de corrélation affichée
