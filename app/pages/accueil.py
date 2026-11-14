"""Écran 1 — Accueil : la question, le public, comment lire l'outil."""

import streamlit as st

import commun

st.title("Quels collèges accompagner en priorité ? Académie de Créteil, brevet 2024 et 2025")

st.markdown(
    "**La question.** Parmi les collèges socialement défavorisés de l'académie de Créteil, lesquels "
    "obtiennent au brevet des résultats **inférieurs à ceux attendus pour leur profil**, et doivent être "
    "accompagnés en priorité à la rentrée 2027 ?"
)

if commun.ecran_disponible(commun.PAGE_LISTE):
    if st.button("Voir la liste prioritaire", type="primary", icon="➡️"):
        st.switch_page(commun.PAGE_LISTE)
else:
    st.button(
        "Voir la liste prioritaire", type="primary", icon="➡️", disabled=True,
        help="Disponible avec l'écran 4 (en cours de construction).",
    )

st.markdown(
    "**Pour qui.** Les chargés de mission du rectorat qui préparent la liste des collèges à accompagner. "
    "L'outil s'utilise dans un navigateur, sans connaissance technique."
)

df, erreur = commun.charger_donnees()
if erreur:
    st.error(erreur, icon="⚠️")
else:
    st.subheader("Ce que couvre l'outil")
    sessions = sorted(int(a) for a in df["annee"].unique())
    c1, c2 = st.columns(2)
    c1.metric("Collèges de l'académie", df["uai"].nunique())
    c2.metric("Sessions du brevet", " et ".join(str(s) for s in sessions))
    st.caption("Chiffres pour toute l'académie, sans tenir compte des filtres.")
    commun.source(sessions)

st.subheader("Comment lire l'outil")
st.markdown(
    """
**Deux indicateurs, publiés par le ministère (DEPP) pour chaque collège :**

- **IPS (indice de position sociale)** : il résume le milieu social des élèves à partir de la profession
  de leurs parents. **Plus il est bas, plus les élèves viennent de milieux défavorisés.**
- **Valeur ajoutée (VA)** au brevet : l'écart, en points, entre le taux de réussite **constaté** et le taux
  **attendu** pour des élèves comparables. **Une VA négative signifie des résultats inférieurs à ceux
  attendus pour ce profil d'élèves.**

**La règle de priorité.** Un collège est proposé pour un accompagnement prioritaire
si son IPS est inférieur à la médiane des collèges de l'académie **et** si sa valeur ajoutée est négative
**aux deux sessions, 2024 et 2025**. Deux résultats de suite sont plus fiables qu'un seul, car la valeur
ajoutée varie beaucoup d'une année à l'autre.

**Les filtres** (barre latérale, à gauche) : département, secteur et session. Ils s'appliquent à tous
les écrans. La médiane de l'IPS reste calculée sur toute l'académie, quels que soient les filtres.
"""
)

st.subheader("Le parcours, en 7 écrans")
st.markdown(
    """
1. **Accueil** : cette page.
2. **Vue d'ensemble** : chiffres clés et position de chaque collège (IPS et valeur ajoutée).
3. **Les quatre groupes** : combien de collèges dans chaque situation, et ce que cela veut dire.
4. **Liste prioritaire** : les collèges proposés, dans un ordre de priorité, à télécharger.
   *Pour aller droit au but, commencez ici.*
5. **Comparaisons** : départements, public et privé, sessions 2024 et 2025.
6. **Données manquantes** : les collèges sans valeur ajoutée, et pourquoi.
7. **Méthode et limites** : sources, licence, dates, et ce que l'outil ne permet pas de conclure.
"""
)

st.subheader("Trois précautions de lecture")
st.markdown(
    """
- **Priorité d'accompagnement, pas jugement.** L'outil indique où un appui semble le plus utile ; il ne
  classe pas les collèges et ne dit pas qu'un collège est « bon » ou « mauvais ».
- **Un écart n'est pas une cause.** Le lien entre milieu social et résultats est une corrélation : l'outil
  ne dit pas *pourquoi* un collège obtient des résultats inférieurs à l'attendu.
- **Les données manquantes sont montrées, pas cachées.** Certains collèges n'ont pas de valeur ajoutée
  (trop peu de candidats, informations incomplètes) : ils sont listés à part.
"""
)

with st.expander("Les mots à connaître"):
    st.markdown(
        """
- **Médiane** : la valeur du milieu ; la moitié des collèges est en dessous, l'autre moitié au-dessus.
- **Session 2025** : le brevet de juin 2025, donc l'année scolaire 2024-2025.
- **UAI** : l'identifiant national d'un établissement scolaire (7 chiffres et 1 lettre, ex. 0940003T).
- **Point** : une unité de pourcentage ; passer de 80 % à 83 % de réussite, c'est 3 points de plus.
"""
    )
