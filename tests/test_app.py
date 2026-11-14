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


def test_accueil_sans_code_interne_et_avec_bouton_liste(donnees_presentes):
    at = lancer()
    texte = " ".join(m.value for m in at.markdown)
    assert "D-0" not in texte  # les codes de décision sont réservés à l'écran Méthode et limites
    assert any(b.label == "Voir la liste prioritaire" for b in at.button)


def ouvrir(page: str) -> AppTest:
    at = AppTest.from_file(str(APP / "app.py"), default_timeout=60).run()
    at.switch_page(page)
    return at.run()


def test_vue_ensemble_s_affiche_avec_les_trois_regles(donnees_presentes):
    at = ouvrir("pages/vue_ensemble.py")
    assert not at.exception
    assert at.title[0].value.startswith("Vue d'ensemble")
    for regle in ["C", "A", "B"]:
        at.radio(key="regle_vue_ensemble").set_value(regle).run()
        assert not at.exception, regle
        assert [m.label for m in at.metric][:4] == [
            "Collèges dans la sélection", "Placés sur le graphique", "Dans la zone prioritaire", "Sans valeur ajoutée",
        ]
        assert any("Source : DEPP" in c.value for c in at.caption)


def test_vue_ensemble_aucun_departement_message_clair(donnees_presentes):
    from observatoire.vues import Filtres

    # AppTest exécute l'écran sans repasser par app.py : on fixe les filtres directement.
    at = AppTest.from_file(str(APP / "app.py"), default_timeout=60).run()
    at.switch_page("pages/vue_ensemble.py")
    at.session_state["filtres"] = Filtres(departements=[], secteurs=["public", "privé"], session=2025)
    at.run()
    assert not at.exception
    assert any("Aucun département" in w.value for w in at.warning)


def _sources(at) -> int:
    return sum(c.value.startswith("Source :") for c in at.caption)


def test_vue_ensemble_deux_sources_et_correlations_en_mots(donnees_presentes):
    at = ouvrir("pages/vue_ensemble.py")
    assert _sources(at) == 2  # une sous les chiffres clés, une en bas de page
    valeurs = [m.value for m in at.metric if m.label.startswith("IPS et")]
    if valeurs:  # absentes si moins de 10 collèges (échantillon)
        assert all(v.startswith("Lien ") and "(r = " in v for v in valeurs)


def test_groupes_s_affiche_avec_les_trois_regles(donnees_presentes):
    at = ouvrir("pages/groupes.py")
    assert not at.exception
    assert at.title[0].value.startswith("Les quatre groupes")
    for regle in ["C", "A", "B"]:
        at.radio(key="regle_groupes").set_value(regle).run()
        assert not at.exception, regle
        assert _sources(at) == 2
        assert len(at.metric) == 4  # les quatre cases


def test_groupes_aucun_secteur_message_clair(donnees_presentes):
    from observatoire.vues import Filtres

    at = AppTest.from_file(str(APP / "app.py"), default_timeout=60).run()
    at.switch_page("pages/groupes.py")
    at.session_state["filtres"] = Filtres(departements=["93"], secteurs=[], session=2025)
    at.run()
    assert not at.exception
    assert any("Aucun secteur" in w.value for w in at.warning)


def test_liste_prioritaire_choix_du_nombre_et_telechargement(donnees_presentes):
    at = ouvrir("pages/liste_prioritaire.py")
    assert not at.exception
    assert at.title[0].value.startswith("Liste prioritaire")
    assert _sources(at) == 2
    for choix in ["10 premiers", "20 premiers", "Tous"]:
        at.radio(key="nombre_liste").set_value(choix).run()
        assert not at.exception, choix
    texte = " ".join(m.value for m in at.markdown).lower()
    assert "ordre de priorité" in texte and "palmarès" not in texte and "mauvais collège" not in texte
    boutons = at.get("download_button")
    assert [b.proto.label for b in boutons] == ["Télécharger la liste affichée (CSV)"]


def test_liste_prioritaire_selection_sans_college_eligible(donnees_presentes):
    from observatoire.vues import Filtres, liste_selection
    import pandas as pd

    df = pd.read_csv(commun.OUTPUT_CSV, dtype={"uai": str, "code_departement": str, "code_commune": str})
    # Seine-et-Marne, privé : aucun collège éligible (vraies données au 2026-11-14 et échantillon).
    f = Filtres(departements=["77"], secteurs=["privé"], session=2025)
    assert liste_selection(df, f).empty
    at = AppTest.from_file(str(APP / "app.py"), default_timeout=60).run()
    at.switch_page("pages/liste_prioritaire.py")
    at.session_state["filtres"] = f
    at.run()
    assert not at.exception
    assert any("ne remplit la règle" in w.value for w in at.warning)


def test_accueil_bouton_actif_mene_a_la_liste(donnees_presentes):
    at = lancer()
    bouton = [b for b in at.button if b.label == "Voir la liste prioritaire"][0]
    assert not bouton.disabled
    bouton.click().run()
    assert not at.exception
    assert at.title[0].value.startswith("Liste prioritaire")
