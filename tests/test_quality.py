import pandas as pd

from observatoire.config import DEPARTEMENTS_ACADEMIE, KEY
from observatoire.pipeline import load_sample
from observatoire.quality import (
    ALERTE,
    check_allowed_values,
    check_key_complete,
    check_uai_format,
    check_unique_key,
    run_checks,
)


def _check(report, debut_nom):
    return [c for c in report.checks if c.nom.startswith(debut_nom)][0]


def test_echantillon_passe_les_controles_bloquants():
    report = run_checks(load_sample(), key=KEY, departements=DEPARTEMENTS_ACADEMIE)
    assert report.ok, report.to_markdown()


def test_echantillon_hors_academie_exclu():
    df = load_sample()
    assert "0511191T" not in df["uai"].tolist()  # collège de l'académie de Reims dans l'extrait
    assert set(df["code_departement"]) <= set(DEPARTEMENTS_ACADEMIE)


def test_echantillon_college_non_apparie_signale_en_alerte():
    df = load_sample()
    assert (df["presence"] == "ips_seul").any()
    controle = _check(run_checks(df, key=KEY), "Présence dans les deux sources")
    assert controle.gravite == ALERTE
    assert not controle.ok
    assert "ips_seul" in controle.detail


def test_valeur_ajoutee_manquante_signalee_en_alerte():
    controle = _check(run_checks(load_sample(), key=KEY), "Valeurs manquantes")
    assert controle.gravite == ALERTE
    assert not controle.ok


def test_doublon_de_cle_detecte():
    df = pd.DataFrame({"uai": ["0930001A", "0930001A"], "annee": [2025, 2025]})
    assert not check_unique_key(df, KEY).ok


def test_cle_manquante_detectee():
    df = pd.DataFrame({"uai": ["0930001A", "0930002B"], "annee": [2025, None]})
    assert not check_key_complete(df, KEY).ok


def test_uai_invalide_detecte():
    df = pd.DataFrame({"uai": ["930001A", "0930001A", None]})
    assert not check_uai_format(df).ok


def test_secteur_inconnu_detecte():
    df = pd.DataFrame({"secteur": ["public", "privé", None]})
    assert not check_allowed_values(df, "secteur", ["public", "privé"]).ok
