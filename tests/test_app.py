"""Le tableau de bord s'exécute sans erreur et affiche des messages clairs (Streamlit AppTest)."""

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP))
import commun  # noqa: E402


def lancer() -> AppTest:
    return AppTest.from_file(str(APP / "app.py"), default_timeout=60).run()


@pytest.fixture
def donnees_presentes():
    if not commun.OUTPUT_CSV.exists():
        pytest.skip("Lancer d'abord `python -m observatoire.pipeline --sample`.")


def test_accueil_s_affiche_sans_erreur(donnees_presentes):
    at = lancer()
    assert not at.exception
    assert at.title[0].value.startswith("Quels collèges accompagner en priorité")
    assert any("Licence Ouverte v2.0" in c.value for c in at.caption)  # la source est affichée
    assert len(at.sidebar.multiselect) == 2 and len(at.sidebar.radio) == 1  # filtres présents


def test_fichier_absent_message_clair(monkeypatch, tmp_path):
    monkeypatch.setattr(commun, "OUTPUT_CSV", tmp_path / "absent.csv")
    at = lancer()
    assert not at.exception
    assert any("introuvables" in e.value and "observatoire.pipeline" in e.value for e in at.error)


def test_vocabulaire_sans_classement(donnees_presentes):
    """Charte : on parle de priorité d'accompagnement, jamais de classement ni de mauvais collèges."""
    at = lancer()
    texte = " ".join(m.value for m in at.markdown).lower()
    assert "priorité d'accompagnement" in texte
    for interdit in ["palmarès", "mauvais collège", "meilleurs collèges", "classement des"]:
        assert interdit not in texte
