"""Écran 3 — Les quatre groupes : effectifs et explication de chaque groupe."""

import streamlit as st

import commun
from observatoire.priority import (
    G_IPS_BAS_VA_OK,
    G_IPS_HAUT_VA_BASSE,
    G_IPS_HAUT_VA_OK,
    G_MANQUANT,
    G_PRIORITAIRE,
    LIBELLES_REGLES,
    REGLE_RETENUE,
    mediane_ips,
)
from observatoire.vues import fr, groupes_selection, libelles_groupes, part

df = commun.donnees_ou_arret()
filtres = commun.filtres_courants()
session = filtres.session

st.title(f"Les quatre groupes : combien de collèges dans chaque situation ? Session {session}")
st.markdown(
    "Chaque collège est placé dans un groupe selon deux questions : **ses élèves viennent-ils de milieux plutôt "
    "défavorisés** (IPS sous la médiane de l'académie) ? **Ses résultats au brevet sont-ils inférieurs à ceux "
    "attendus** pour ces élèves (valeur ajoutée sous le seuil) ? Les quatre cases sont disposées comme les "
    "quatre quarts du graphique de la vue d'ensemble."
)

regle = st.radio(
    "Règle de priorité affichée",
    list(LIBELLES_REGLES),
    format_func=LIBELLES_REGLES.get,
    index=list(LIBELLES_REGLES).index(REGLE_RETENUE),
    key="regle_groupes",
)

commun.selection_ou_arret(df)
g = groupes_selection(df, filtres, regle)
eff, n_places = g["effectifs"], g["n_places"]
titres = libelles_groupes(regle)
mediane = fr(float(mediane_ips(df).get(session)))

# Explication de chaque groupe : ce qu'il décrit, ce qu'il ne dit pas.
EXPLICATIONS = {
    G_PRIORITAIRE: (
        "Élèves de milieux plutôt défavorisés **et** résultats inférieurs à ceux attendus pour ces élèves. "
        "C'est la situation visée par la question de l'observatoire."
    ),
    G_IPS_BAS_VA_OK: (
        "Élèves de milieux plutôt défavorisés, avec des résultats **au moins égaux** à ceux attendus pour ces élèves. "
        "Le milieu social ne détermine donc pas à lui seul les résultats."
    ),
    G_IPS_HAUT_VA_BASSE: (
        "Élèves de milieux plutôt favorisés, avec des résultats **inférieurs** à ceux attendus pour ces élèves. "
        "Hors du champ de la question, qui porte sur les collèges défavorisés, mais montré pour être complet."
    ),
    G_IPS_HAUT_VA_OK: "Élèves de milieux plutôt favorisés, avec des résultats au moins égaux à ceux attendus.",
}


def case(conteneur, groupe: str, symbole: str) -> None:
    with conteneur.container(border=True):
        st.markdown(f"**{symbole} {titres[groupe]}**")
        st.metric(titres[groupe], eff[groupe], label_visibility="collapsed")
        st.caption(f"{part(eff[groupe], n_places)} des {n_places} collèges placés")
        st.markdown(EXPLICATIONS[groupe])
        if groupe == G_PRIORITAIRE:
            if regle == "C":
                st.markdown(
                    f"Parmi eux, **{g['n_repetes']}** sont dans cette situation **aux deux sessions** : ce sont "
                    "les collèges proposés pour un accompagnement prioritaire (écran 4). Les "
                    f"{eff[groupe] - g['n_repetes']} autres ne le sont que cette session."
                )
            else:
                st.markdown(f"Avec cette règle de comparaison, ces **{eff[groupe]}** collèges seraient proposés.")


# --- Les quatre cases ---------------------------------------------------------------
gauche, droite = st.columns(2)
gauche.markdown(f"##### IPS bas (sous la médiane de l'académie, {mediane})")
droite.markdown(f"##### IPS haut (médiane de l'académie ou plus)")
haut_g, haut_d = st.columns(2)
case(haut_g, G_IPS_BAS_VA_OK, "○")
case(haut_d, G_IPS_HAUT_VA_OK, "○")
bas_g, bas_d = st.columns(2)
case(bas_g, G_PRIORITAIRE, "▲")
case(bas_d, G_IPS_HAUT_VA_BASSE, "○")

st.info(
    f"**{eff[G_MANQUANT]} collège(s) de la sélection n'ont pas de valeur ajoutée** en {session} : ils ne peuvent être "
    "placés dans aucun groupe. Ils ne sont pas oubliés : voir l'écran « Données manquantes ».",
    icon="ℹ️",
)
commun.source([session])

st.markdown(
    "**À retenir.** Un groupe décrit une situation **observée** une année donnée ; il ne dit pas pourquoi un "
    "collège s'y trouve. La valeur ajoutée varie d'une année à l'autre : un collège peut changer de groupe "
    "entre 2024 et 2025, c'est pourquoi la règle retenue demande une difficulté répétée."
)

with st.expander("Effectifs des deux sessions (tableau)"):
    tableau = g["tableau"].rename(columns=titres)
    tableau.index = [f"Session {a}" for a in tableau.index]
    st.dataframe(tableau, width="stretch")
    st.caption(
        "Lignes : sessions du brevet. Colonnes : groupes. Chaque collège compte une fois par session. "
        "Filtres de département et de secteur appliqués ; le filtre de session ne s'applique pas à ce tableau."
    )

st.divider()
commun.source(sorted(int(a) for a in df["annee"].unique()))  # le tableau couvre les deux sessions
