import pandas as pd

from observatoire.clean import (
    clean_code_commune,
    departement_from_code,
    normalize_column_name,
    to_numeric_fr,
)


def test_normalize_column_name():
    assert normalize_column_name(" Code Commune ") == "code_commune"
    assert normalize_column_name("Année") == "annee"


def test_code_commune_retrouve_le_zero_initial():
    result = clean_code_commune(pd.Series(["1001", "1001.0", "75056"]))
    assert result.tolist() == ["01001", "01001", "75056"]


def test_code_commune_corse_inchange():
    assert clean_code_commune(pd.Series(["2a004"])).tolist() == ["2A004"]


def test_departement_metropole_corse_outre_mer():
    codes = pd.Series(["01001", "2A004", "97411"])
    assert departement_from_code(codes).tolist() == ["01", "2A", "974"]


def test_nombres_au_format_francais():
    result = to_numeric_fr(pd.Series(["1 234,5", "69 140", "abc", None]))
    assert result.iloc[0] == 1234.5
    assert result.iloc[1] == 69140
    assert pd.isna(result.iloc[2])  # illisible → NaN, jamais 0
    assert pd.isna(result.iloc[3])


# --- Collèges (étape 4) ---------------------------------------------------------

from observatoire.clean import (  # noqa: E402
    clean_ips,
    clean_ivac,
    clean_uai,
    harmonize_secteur,
    join_sources,
    session_from_annee_scolaire,
)
from observatoire.config import KEY  # noqa: E402


def test_uai_majuscules_sans_espaces():
    assert clean_uai(pd.Series([" 0930917s "])).tolist() == ["0930917S"]


def test_secteur_harmonise_et_valeur_inconnue_manquante():
    result = harmonize_secteur(pd.Series(["public", "privé sous contrat", "PU", "PR", "hors contrat", None]))
    assert result.iloc[:4].tolist() == ["public", "privé", "public", "privé"]
    assert result.iloc[4:].isna().all()  # D-006 : on ne devine pas


def test_session_depuis_annee_scolaire():
    result = session_from_annee_scolaire(pd.Series(["2024-2025", "2023-2024", "2024-2026", "2025", None]))
    assert result.iloc[:2].tolist() == [2025, 2024]  # D-005
    assert result.iloc[2:].isna().all()  # années non consécutives ou format inattendu


IPS_BRUT = pd.DataFrame(
    {
        "Année scolaire": ["2024-2025", "2024-2025", "2024-2025"],
        "Code académie": ["24", "24", "19"],
        "Code département": ["93", "93", "51"],
        "Libellé département": ["SEINE-SAINT-DENIS"] * 2 + ["MARNE"],
        "Code commune Insee": ["93066", "93066", "51507"],
        "Libellé commune": ["SAINT-DENIS"] * 2 + ["SAINTE MENEHOULD"],
        "UAI": ["0930001A", "0930001A", "0511191T"],
        "Nom de l'établissement": ["COLLEGE A", "COLLEGE A", "COLLEGE HORS ACADEMIE"],
        "Secteur": ["public", "public", "public"],
        "IPS": ["85.2", "85.2", "91.4"],
        "Ecart type de l'IPS": ["30.1", "30.1", "27.8"],
    }
)

IVAC_BRUT = pd.DataFrame(
    {
        "Session": ["2025", "2025", "2022"],
        "UAI": ["0930001A", "0930002B", "0930001A"],
        "Nom de l'établissement": ["COLLEGE A", "COLLEGE B", "COLLEGE A"],
        "Commune": ["SAINT-DENIS"] * 3,
        "Code académie": ["24"] * 3,
        "Code département": ["93"] * 3,
        "Département": ["SEINE-SAINT-DENIS"] * 3,
        "Secteur": ["PU", "PR", "PU"],
        "Nb candidats G": ["120", "30", "110"],
        "Taux de réussite G": ["82.0", "95.0", "80.0"],
        "VA du taux de réussite G": ["-3.0", None, "1.0"],
    }
)


def test_clean_ips_filtre_l_academie_et_supprime_doublon_strict():
    ips = clean_ips(IPS_BRUT, "24")
    assert ips["uai"].tolist() == ["0930001A"]  # hors académie exclu, doublon strict supprimé
    assert ips.loc[0, "annee"] == 2025
    assert ips.loc[0, "ips"] == 85.2


def test_clean_ivac_type_les_colonnes():
    ivac = clean_ivac(IVAC_BRUT, "24")
    assert ivac["nb_candidats_g"].dtype == "Int64"
    assert ivac["secteur"].tolist() == ["public", "privé", "public"]
    assert ivac["va_taux_reussite_g"].isna().sum() == 1  # VA non calculée : manquante, jamais 0


def test_jointure_annees_communes_et_presence():
    df = join_sources(clean_ips(IPS_BRUT, "24"), clean_ivac(IVAC_BRUT, "24"), KEY)
    assert df["annee"].unique().tolist() == [2025]  # session 2022 absente d'IPS : écartée (D-007)
    presence = dict(zip(df["uai"], df["presence"]))
    assert presence == {"0930001A": "les_deux", "0930002B": "ivac_seul"}  # rien n'est perdu (D-008)
    ligne_b = df[df["uai"] == "0930002B"].iloc[0]
    assert pd.isna(ligne_b["ips"])
    assert ligne_b["nom_etablissement"] == "COLLEGE B"  # repris d'IVAC quand IPS manque
