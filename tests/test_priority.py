import pandas as pd

from observatoire.priority import (
    G_IPS_BAS_VA_OK,
    G_IPS_HAUT_VA_BASSE,
    G_IPS_HAUT_VA_OK,
    G_MANQUANT,
    G_PRIORITAIRE,
    GROUPES,
    classer_session,
    effectifs_groupes,
    ips_bas,
    liste_prioritaire,
    mediane_ips,
    non_classables,
)


def _df(lignes):
    """lignes : (uai, annee, ips, va, presence)."""
    df = pd.DataFrame(lignes, columns=["uai", "annee", "ips", "va_taux_reussite_g", "presence"])
    df["nom_etablissement"] = "COLLEGE " + df["uai"]
    df["commune"] = "COMMUNE"
    df["code_departement"] = "93"
    df["departement"] = "SEINE-SAINT-DENIS"
    df["secteur"] = "public"
    return df


# Une session : IPS 80, 90, 100, 110, 120 → médiane 100.
UNE_SESSION = _df(
    [
        ("A", 2025, 80.0, -1.0, "les_deux"),   # IPS bas, VA négative
        ("B", 2025, 90.0, 0.0, "les_deux"),    # IPS bas, VA nulle → au-dessus du seuil
        ("C", 2025, 100.0, -8.0, "les_deux"),  # IPS = médiane → « haut »
        ("D", 2025, 110.0, 3.0, "les_deux"),
        ("E", 2025, 120.0, None, "ips_seul"),  # VA manquante
    ]
)


def test_mediane_par_session():
    assert mediane_ips(UNE_SESSION).to_dict() == {2025: 100.0}


def test_ips_egal_a_la_mediane_est_haut():
    assert ips_bas(UNE_SESSION).tolist() == [True, True, False, False, False]


def test_regle_a_groupes():
    groupes = classer_session(UNE_SESSION, "A")["groupe"].tolist()
    assert groupes == [G_PRIORITAIRE, G_IPS_BAS_VA_OK, G_IPS_HAUT_VA_BASSE, G_IPS_HAUT_VA_OK, G_MANQUANT]


def test_regle_b_seuil_moins_5_inclus():
    # IPS 80, 90, 130, 140 → médiane 110 : A et B ont un IPS bas.
    df = _df([
        ("A", 2025, 80.0, -5.0, "les_deux"), ("B", 2025, 90.0, -4.0, "les_deux"),
        ("C", 2025, 130.0, 1.0, "les_deux"), ("D", 2025, 140.0, 1.0, "les_deux"),
    ])
    groupes = classer_session(df, "B")["groupe"].tolist()
    assert groupes[:2] == [G_PRIORITAIRE, G_IPS_BAS_VA_OK]


def test_effectifs_toutes_les_colonnes_et_total():
    table = effectifs_groupes(classer_session(UNE_SESSION, "A"))
    assert list(table.columns) == GROUPES
    assert int(table.loc[2025].sum()) == len(UNE_SESSION)


# Deux sessions : médiane 100 chaque année.
DEUX_SESSIONS = _df(
    [
        ("P1", 2024, 80.0, -2.0, "les_deux"), ("P1", 2025, 82.0, -4.0, "les_deux"),   # prioritaire, VA moy -3
        ("P2", 2024, 85.0, -9.0, "les_deux"), ("P2", 2025, 84.0, -1.0, "les_deux"),   # prioritaire, VA moy -5
        ("X1", 2024, 85.0, -3.0, "les_deux"), ("X1", 2025, 86.0, 1.0, "les_deux"),    # VA négative 1 seule fois
        ("X2", 2024, 90.0, -3.0, "les_deux"), ("X2", 2025, 120.0, -3.0, "les_deux"),  # IPS bas 1 seule fois
        ("X3", 2024, 95.0, None, "les_deux"), ("X3", 2025, 95.0, -6.0, "les_deux"),   # VA manquante en 2024
        ("H1", 2024, 110.0, 2.0, "les_deux"), ("H1", 2025, 105.0, 2.0, "les_deux"),
        ("H2", 2024, 115.0, 0.0, "les_deux"), ("H2", 2025, 110.0, 0.0, "les_deux"),
        ("H3", 2024, 120.0, 1.0, "les_deux"), ("H3", 2025, 115.0, 1.0, "les_deux"),
        ("H4", 2024, 125.0, 1.0, "les_deux"), ("H4", 2025, 125.0, 1.0, "les_deux"),
        ("H5", 2024, 130.0, None, "ips_seul"), ("H5", 2025, 130.0, None, "ips_seul"),
    ]
)


def test_liste_prioritaire_regle_c():
    liste = liste_prioritaire(DEUX_SESSIONS)
    assert liste["uai"].tolist() == ["P2", "P1"]  # VA moyenne -5 avant -3
    assert liste["ordre_priorite"].tolist() == [1, 2]
    assert liste.loc[0, "va_moyenne"] == -5.0
    assert liste.loc[0, "va_2024"] == -9.0 and liste.loc[0, "va_2025"] == -1.0


def test_egalite_de_va_moyenne_departagee_par_uai():
    df = _df([
        ("Z", 2024, 80.0, -2.0, "les_deux"), ("Z", 2025, 80.0, -2.0, "les_deux"),
        ("Y", 2024, 81.0, -1.0, "les_deux"), ("Y", 2025, 81.0, -3.0, "les_deux"),
        ("H", 2024, 120.0, 1.0, "les_deux"), ("H", 2025, 120.0, 1.0, "les_deux"),
        ("I", 2024, 125.0, 1.0, "les_deux"), ("I", 2025, 125.0, 1.0, "les_deux"),
    ])
    assert liste_prioritaire(df)["uai"].tolist() == ["Y", "Z"]


def test_non_classables():
    nc = non_classables(DEUX_SESSIONS).set_index("uai")
    assert set(nc.index) == {"X3", "H5"}
    assert nc.loc["X3", "sessions_sans_va"] == "2024"
    assert nc.loc["H5", "sessions_sans_va"] == "2024, 2025"
    assert bool(nc.loc["H5", "absent_d_ivac"]) and not bool(nc.loc["X3", "absent_d_ivac"])


def test_liste_vide_si_aucun_college_eligible():
    df = DEUX_SESSIONS[DEUX_SESSIONS["uai"].str.startswith("H")]
    df = df.assign(va_taux_reussite_g=1.0)  # aucune VA négative
    liste = liste_prioritaire(df)
    assert liste.empty
    assert {"ordre_priorite", "uai", "va_2024", "va_2025", "va_moyenne"} <= set(liste.columns)
