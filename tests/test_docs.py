"""Cohérence entre la documentation et le code."""

from observatoire.config import ROOT
from observatoire.pipeline import load_sample


def _variables_du_dictionnaire() -> list[str]:
    lignes = (ROOT / "docs" / "dictionnaire.md").read_text(encoding="utf-8").splitlines()
    tableau = [l for l in lignes if l.startswith("| ") and not l.startswith("| Variable") and not l.startswith("| ---")]
    return [l.split("|")[1].strip() for l in tableau]


def test_dictionnaire_decrit_exactement_les_colonnes_du_fichier_final():
    assert _variables_du_dictionnaire() == list(load_sample().columns)
