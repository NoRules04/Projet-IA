"""Tableau de bord Streamlit — point d'entrée.

Lancement : streamlit run app/app.py
Ce fichier charge les données, affiche les filtres communs et le menu des écrans.
Chaque écran est un fichier de app/pages/ ; la liste des écrans est dans commun.ECRANS.
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
    st.Page(fichier, title=titre, default=(i == 0))
    for i, (fichier, titre) in enumerate(commun.ecrans_disponibles())
]
# Menu dans la barre latérale (Streamlit le masque tant qu'il n'y a qu'un seul écran).
st.navigation(pages, position="sidebar").run()
