"""Tableau de bord Streamlit — point d'entrée.

Lancement : streamlit run app/app.py
Ce fichier charge les données, affiche les filtres communs et le menu des écrans.
Chaque écran est un fichier de app/pages/.
"""

from __future__ import annotations

import streamlit as st

import commun

st.set_page_config(
    page_title="Observatoire — collèges de l'académie de Créteil",
    layout="wide",
)

df, erreur = commun.charger_donnees()
if df is not None:
    commun.barre_filtres(df)

pages = [
    st.Page("pages/accueil.py", title="1. Accueil", default=True),
]
st.navigation(pages).run()
