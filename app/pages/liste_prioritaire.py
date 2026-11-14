"""Écran 4 — Liste prioritaire : collèges proposés, ordre de priorité, téléchargement CSV."""

import streamlit as st

import commun
from observatoire.config import load_sources
from observatoire.priority import liste_prioritaire
from observatoire.vues import (
    CHOIX_NOMBRE,
    csv_liste,
    fr,
    liste_selection,
    premiers_avec_egalites,
    table_liste,
    texte_source,
)

df = commun.donnees_ou_arret()
filtres = commun.filtres_courants()
sessions = sorted(int(a) for a in df["annee"].unique())
sessions_txt = " et ".join(str(s) for s in sessions)

st.title("Liste prioritaire : les collèges proposés pour un accompagnement")
st.markdown(
    f"Un collège est proposé si **ses élèves viennent de milieux plutôt défavorisés** (IPS sous la médiane de "
    f"l'académie) **et** si **ses résultats au brevet sont inférieurs à ceux attendus pour ces élèves aux deux "
    f"sessions, {sessions_txt}** (valeur ajoutée négative les deux fois). Les collèges sont présentés dans un "
    "**ordre de priorité** : la valeur ajoutée moyenne la plus basse d'abord."
)
st.caption(
    f"Cet écran utilise toujours les deux sessions ({sessions_txt}) : le filtre « Session du brevet » ne s'y applique "
    "pas. Les filtres de département et de secteur s'appliquent."
)

commun.selection_ou_arret(df, toutes_sessions=True)
liste = liste_selection(df, filtres)
total_academie = len(liste_prioritaire(df))

c1, c2 = st.columns(2)
c1.metric("Collèges proposés dans la sélection", len(liste))
c2.metric("Collèges proposés dans toute l'académie", total_academie)
commun.source(sessions)

if liste.empty:
    st.warning(
        "Aucun collège de la sélection ne remplit la règle. Élargissez la sélection de départements ou de secteurs "
        "(très peu de collèges privés ont un IPS sous la médiane de l'académie).",
        icon="🔎",
    )
    st.stop()

# --- Combien de collèges afficher (D-010 : égalités incluses) ----------------------------
choix = st.radio("Nombre de collèges à afficher", list(CHOIX_NOMBRE), horizontal=True, key="nombre_liste")
n = CHOIX_NOMBRE[choix]
affichee, ajoutes = premiers_avec_egalites(liste, n)
if ajoutes:
    seuil = liste["va_moyenne"].iloc[n - 1]
    a_egalite = int((liste["va_moyenne"] == seuil).sum())
    st.info(
        f"**Égalité autour de la {n}e place** : {a_egalite} collèges ont la même valeur ajoutée moyenne "
        f"({fr(seuil)} points). Ils sont tous affichés : la liste compte **{len(affichee)} collèges** au lieu de {n}.",
        icon="⚖️",
    )
elif n is not None and n > len(liste):
    st.caption(f"La sélection ne compte que {len(liste)} collège(s) : ils sont tous affichés.")

table = table_liste(affichee, sessions)
st.dataframe(
    table,
    hide_index=True,
    width="stretch",
    column_config={
        **{f"IPS {a}": st.column_config.NumberColumn(format="%.1f") for a in sessions},
        **{f"Valeur ajoutée {a} (points)": st.column_config.NumberColumn(format="%+.0f") for a in sessions},
        "Valeur ajoutée moyenne (points)": st.column_config.NumberColumn(format="%+.1f"),
    },
)
st.caption("Cliquez sur le titre d'une colonne pour trier le tableau autrement (par commune, par IPS…).")

fichier = f"liste_prioritaire_creteil_{'tous' if n is None else n}.csv"
st.download_button(
    "Télécharger la liste affichée (CSV)",
    data=csv_liste(table_liste(affichee, sessions, source=texte_source(load_sources(), sessions))),
    file_name=fichier,
    mime="text/csv",
    icon="⬇️",
    type="primary",
)
st.caption(
    f"{len(affichee)} collège(s). Format tableur français : séparateur point-virgule, virgule décimale. "
    "Chaque ligne indique la source des données."
)

# --- Comment lire cette liste ------------------------------------------------------------
st.subheader("Comment lire cette liste")
st.markdown(
    """
- **Un ordre de priorité, pas un classement.** L'ordre aide à décider par où commencer ; il ne dit pas qu'un
  collège est « moins bon » qu'un autre.
- **Les petits écarts ne sont pas significatifs.** La valeur ajoutée est publiée en points entiers, et le guide
  méthodologique de la DEPP juge un écart de 2 points « trop faible pour en tirer des conclusions ». Deux collèges
  voisins dans la liste doivent être considérés comme dans une situation comparable.
- **La liste ne dit pas pourquoi.** Une valeur ajoutée négative est un constat ; ses causes demandent une analyse
  sur le terrain.
- **Des collèges ne peuvent pas être classés.** Ceux qui n'ont pas de valeur ajoutée à l'une des deux sessions
  (trop peu de candidats, données incomplètes) ne figurent pas ici : voir l'écran « Données manquantes ».
"""
)

st.divider()
commun.source(sessions)
