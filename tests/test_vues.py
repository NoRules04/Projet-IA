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


def test_correlation_en_mots_seuils_de_cohen():
    from observatoire.vues import qualifier_correlation as q

    assert q(0.73) == "Lien fort (r = 0,73)"
    assert q(-0.28) == "Lien faible (r = -0,28)"
    assert q(-0.14) == "Lien faible (r = -0,14)"
    assert q(0.42) == "Lien modéré (r = 0,42)"
    assert q(0.05) == "Lien quasi nul (r = 0,05)"
    # Bornes : 0,10 / 0,30 / 0,50 appartiennent à la catégorie supérieure.
    assert q(0.10).startswith("Lien faible") and q(-0.30).startswith("Lien modéré") and q(0.50).startswith("Lien fort")
    # Le mot suit le chiffre arrondi affiché : 0,299 s'affiche 0,30 → « modéré », jamais « faible (r = 0,30) ».
    assert q(0.299) == "Lien modéré (r = 0,30)"
    assert q(None) == "Corrélation non calculable" and q(float("nan")) == "Corrélation non calculable"


def _deux_sessions():
    # Médiane 100 chaque année (IPS 80, 90, 110, 120 + un collège sans VA à 100).
    lignes = []
    for annee, vas in [(2024, [-2, 3, -1, 2, None]), (2025, [-4, -1, 1, -3, None])]:
        for uai, ips, va in zip(["A", "B", "C", "D", "E"], [80, 90, 110, 120, 100], vas):
            lignes.append({"uai": uai, "annee": annee, "ips": ips, "va_taux_reussite_g": va,
                           "code_departement": "93", "secteur": "public", "presence": "les_deux",
                           "nom_etablissement": uai, "commune": "X", "departement": "SEINE-SAINT-DENIS"})
    df = pd.DataFrame(lignes)
    df["va_taux_reussite_g"] = df["va_taux_reussite_g"].astype("Float64")
    return df


def test_groupes_selection_regle_c_et_a():
    from observatoire.priority import G_IPS_BAS_VA_OK, G_IPS_HAUT_VA_BASSE, G_IPS_HAUT_VA_OK, G_MANQUANT, G_PRIORITAIRE
    from observatoire.vues import groupes_selection

    f = Filtres(["93"], ["public"], 2025)
    g = groupes_selection(_deux_sessions(), f, "C")
    # 2025 : A (80, -4) et B (90, -1) → IPS bas · VA négative ; C (110, +1) ; D (120, -3) ; E sans VA.
    assert g["effectifs"] == {G_PRIORITAIRE: 2, G_IPS_BAS_VA_OK: 0, G_IPS_HAUT_VA_BASSE: 1,
                              G_IPS_HAUT_VA_OK: 1, G_MANQUANT: 1}
    assert g["n_selection"] == 5 and g["n_places"] == 4
    assert g["n_repetes"] == 1  # seul A est aussi « IPS bas · VA négative » en 2024
    assert g["effectifs"] == groupes_selection(_deux_sessions(), f, "A")["effectifs"]  # même seuil que A
    assert list(g["tableau"].index) == [2024, 2025] and int(g["tableau"].loc[2024].sum()) == 5


def test_groupes_selection_regle_b_et_libelles():
    from observatoire.priority import G_PRIORITAIRE
    from observatoire.vues import groupes_selection, libelles_groupes, part

    g = groupes_selection(_deux_sessions(), Filtres(["93"], ["public"], 2025), "B")
    assert g["effectifs"][G_PRIORITAIRE] == 0  # aucun IPS bas avec VA ≤ -5 en 2025
    assert libelles_groupes("B")[G_PRIORITAIRE] == "IPS bas · VA ≤ -5"
    assert libelles_groupes("C")[G_PRIORITAIRE] == "IPS bas · VA négative"
    assert part(1, 4) == "25 %" and part(0, 0) == "—"


LISTE = pd.DataFrame({
    "ordre_priorite": [1, 2, 3, 4, 5],
    "uai": ["U1", "U2", "U3", "U4", "U5"],
    "nom_etablissement": ["COLLEGE A", "COLLEGE B", "COLLEGE C", "COLLEGE D", "COLLEGE E"],
    "commune": ["X"] * 5,
    "code_departement": ["93", "94", "93", "77", "93"],
    "departement": ["SEINE-SAINT-DENIS", "VAL-DE-MARNE", "SEINE-SAINT-DENIS", "SEINE-ET-MARNE", "SEINE-SAINT-DENIS"],
    "secteur": ["public", "public", "privé", "public", "public"],
    "ips_2024": [80.1, 85.0, 90.0, 95.0, 99.0], "ips_2025": [81.0, 86.0, 91.0, 96.0, 98.5],
    "va_2024": [-12.0, -9.0, -10.0, -8.0, -1.0], "va_2025": [-8.0, -10.0, -9.0, -10.0, -1.0],
    "va_moyenne": [-10.0, -9.5, -9.5, -9.0, -1.0],
})


def test_premiers_avec_egalites_d010():
    from observatoire.vues import premiers_avec_egalites

    garde, ajoutes = premiers_avec_egalites(LISTE, 2)  # la 2e place (-9,5) est partagée avec la 3e
    assert garde["uai"].tolist() == ["U1", "U2", "U3"] and ajoutes == 1
    garde, ajoutes = premiers_avec_egalites(LISTE, 3)
    assert len(garde) == 3 and ajoutes == 0
    assert premiers_avec_egalites(LISTE, None)[0].equals(LISTE)  # « Tous »
    garde, ajoutes = premiers_avec_egalites(LISTE, 20)  # plus que la liste : tout, sans ajout
    assert len(garde) == 5 and ajoutes == 0


def test_table_et_csv_pour_tableur_francais():
    from observatoire.vues import csv_liste, table_liste

    table = table_liste(LISTE, [2024, 2025], source="Source : test")
    assert list(table.columns)[:5] == ["Ordre de priorité (académie)", "Collège", "Commune", "Département", "Secteur"]
    assert "Valeur ajoutée 2025 (points)" in table.columns and table.loc[0, "Département"] == "93 · Seine-Saint-Denis"
    contenu = csv_liste(table)
    assert contenu.startswith(b"\xef\xbb\xbf")  # BOM : accents corrects dans Excel
    texte = contenu.decode("utf-8-sig")
    entete, ligne1 = texte.splitlines()[:2]
    assert entete.startswith("Ordre de priorité (académie);Collège;")
    assert ";80,1;" in ligne1 and ";-10,0;" in ligne1 and ligne1.endswith("Source : test")
