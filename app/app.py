"""Tableau de bord Streamlit — point de départ.

Lancement : streamlit run app/app.py
Principe : chaque écran répond à une question de la note de cadrage, affiche sa source,
signale les données manquantes et reste lisible sans la couleur.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from observatoire.config import OUTPUT_CSV  # noqa: E402

st.set_page_config(page_title="Observatoire décisionnel", layout="wide")

# Une seule couleur d'accent, contrastée ; la couleur ne porte jamais seule l'information.
ACCENT = "#1F4E79"
SOURCE_LABEL = (
    "Sources : DEPP, « Indices de position sociale des collèges (à partir de 2023) » et "
    "« Indicateurs de valeur ajoutée des collèges », Licence Ouverte v2.0, consultés le 2026-11-13. "
    "Traitements : voir le dépôt."
)


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"uai": str, "code_departement": str, "code_commune": str})


st.title("Observatoire décisionnel — collèges de l'académie de Créteil")
st.caption(
    "Parmi les collèges socialement défavorisés de l'académie de Créteil, lesquels obtiennent au brevet "
    "des résultats inférieurs à ceux attendus pour leur profil ?"
)
st.info("Prototype technique (étape J2) : les écrans du récit visuel restent à construire (J3).")

if not OUTPUT_CSV.exists():
    st.error(
        "Aucune donnée préparée. Lancez d'abord le pipeline : "
        "`python -m observatoire.pipeline --sample` (échantillon) ou `python -m observatoire.pipeline`."
    )
    st.stop()

df = load_data(OUTPUT_CSV)

# --- Filtres -----------------------------------------------------------------
with st.sidebar:
    st.header("Filtres")
    departements = sorted(df["code_departement"].dropna().unique())
    choix_dep = st.multiselect("Départements", departements, default=departements)
    annees = sorted(df["annee"].dropna().astype(int).unique())
    choix_annee = st.selectbox("Session du brevet", annees, index=len(annees) - 1)

vue = df[df["code_departement"].isin(choix_dep) & (df["annee"] == choix_annee)]

if vue.empty:
    st.warning("Aucun collège ne correspond à ces filtres. Élargissez la sélection de départements.")
    st.stop()

# --- Indicateurs clés ------------------------------------------------------------
manquants = int(vue["va_taux_reussite_g"].isna().sum())
non_apparies = int((vue["presence"] != "les_deux").sum())
c1, c2, c3 = st.columns(3)
c1.metric("Collèges affichés", len(vue))
c2.metric("Valeur ajoutée médiane (points)", f"{vue['va_taux_reussite_g'].median():.1f}")
c3.metric("Sans valeur ajoutée", manquants)
if manquants:
    st.info(
        f"{manquants} collège(s) sans valeur ajoutée, dont {non_apparies} absent(s) du fichier IVAC : "
        "ils n'apparaissent pas dans le graphique, mais restent listés dans le tableau détaillé."
    )

# --- IPS et valeur ajoutée ----------------------------------------------------------
st.subheader(f"IPS et valeur ajoutée du taux de réussite au brevet — session {choix_annee}")
points = vue.dropna(subset=["ips", "va_taux_reussite_g"])
fig = px.scatter(
    points,
    x="ips",
    y="va_taux_reussite_g",
    symbol="secteur",
    hover_name="nom_etablissement",
    hover_data={"commune": True, "uai": True, "nb_candidats_g": True},
    labels={"ips": "IPS du collège", "va_taux_reussite_g": "Valeur ajoutée (points)", "secteur": "Secteur"},
    color_discrete_sequence=[ACCENT],
)
fig.add_hline(y=0, line_dash="dash", line_color="#555555")
fig.add_annotation(x=points["ips"].max(), y=0, text="Résultat conforme à l'attendu", showarrow=False, yshift=10)
st.plotly_chart(fig, width="stretch")
st.caption(SOURCE_LABEL)

# --- Limites ------------------------------------------------------------------
with st.expander("Ce que ce tableau de bord ne permet pas de conclure"):
    st.markdown(
        "- Pourquoi un collège réussit moins bien qu'attendu, ni si un dispositif d'accompagnement sera efficace.\n"
        "- Le lien entre IPS et résultats est une corrélation, pas une cause.\n"
        "- La valeur ajoutée n'est pas calculée sous 40 candidats (guide IVAC) : les petits collèges sont absents du graphique."
    )

with st.expander("Données détaillées"):
    st.dataframe(vue, width="stretch", hide_index=True)
    st.download_button("Télécharger la sélection (CSV)", vue.to_csv(index=False).encode("utf-8"), "selection.csv")
