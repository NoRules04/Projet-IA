"""Écran 2 — Vue d'ensemble : chiffres clés et nuage de points IPS / valeur ajoutée."""

import plotly.graph_objects as go
import streamlit as st

import commun
from observatoire.priority import LIBELLES_REGLES, REGLE_RETENUE
from observatoire.vues import fr, qualifier_correlation, rentree_de_session, vue_ensemble

df = commun.donnees_ou_arret()
filtres = commun.filtres_courants()
session = filtres.session

st.title(f"Vue d'ensemble : milieu social et résultats au brevet, session {session}")
st.markdown(
    "Chaque point est un collège. **À gauche**, les collèges dont les élèves viennent de milieux plus "
    "défavorisés (IPS bas). **En bas**, ceux dont les résultats au brevet sont inférieurs à ceux attendus "
    "pour leurs élèves (valeur ajoutée négative). La zone encadrée en bas à gauche réunit les deux situations."
)

regle = st.radio(
    "Règle de priorité affichée",
    list(LIBELLES_REGLES),
    format_func=LIBELLES_REGLES.get,
    index=list(LIBELLES_REGLES).index(REGLE_RETENUE),
    key="regle_vue_ensemble",
    help="La règle retenue pour la liste prioritaire est la première. Les deux autres sont affichées pour comparaison.",
)

commun.selection_ou_arret(df)  # message clair si les filtres ne renvoient aucun collège
points, r = vue_ensemble(df, filtres, regle)
sessions_regle = sorted(int(a) for a in df["annee"].unique()) if regle == "C" else [session]

# --- Chiffres clés ---------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Collèges dans la sélection", r["n_selection"])
c2.metric("Placés sur le graphique", r["n_places"], help="Collèges qui ont une valeur ajoutée cette session.")
c3.metric("Dans la zone prioritaire", r["n_prioritaires"], help=LIBELLES_REGLES[regle])
c4.metric("Sans valeur ajoutée", r["n_sans_va"], help="Non placés sur le graphique : voir l'écran « Données manquantes ».")
commun.source(sessions_regle)

if r["n_places"] == 0:
    st.warning("Aucun collège de la sélection n'a de valeur ajoutée pour cette session : rien à placer sur le graphique.")
    st.stop()

# --- Nuage de points ---------------------------------------------------------------
med, seuil = r["mediane_ips"], r["seuil_va"]
x_min, x_max = min(points["ips"].min(), med) - 3, max(points["ips"].max(), med) + 3
y_min, y_max = min(points["va_taux_reussite_g"].min(), seuil) - 2, max(points["va_taux_reussite_g"].max(), 0) + 2

fig = go.Figure()
# Zone prioritaire : fond très léger + cadre + étiquette écrite (pas seulement une couleur).
fig.add_shape(
    type="rect", x0=x_min, x1=med, y0=y_min, y1=seuil, layer="below",
    fillcolor="rgba(42,120,214,0.07)", line=dict(color=commun.MARQUE_PRIORITAIRE, width=1, dash="dot"),
)
fig.add_annotation(
    x=x_min, y=y_min, xanchor="left", yanchor="bottom", showarrow=False,
    text="<b>Zone prioritaire</b><br>IPS bas et valeur ajoutée sous le seuil",
    font=dict(color=commun.ENCRE, size=12), align="left", bgcolor="rgba(255,255,255,0.85)",
)
infobulle = (
    "<b>%{customdata[0]}</b><br>%{customdata[1]} · %{customdata[2]}<br>"
    "IPS : %{x:.1f}<br>Valeur ajoutée : %{y:+.0f} points<br>"
    "Candidats : %{customdata[3]}<br>UAI : %{customdata[4]}<extra></extra>"
)
for prioritaire, nom, symbole, couleur, taille in [
    (False, "Autre collège", "circle-open", commun.MARQUE_CONTEXTE, 8),
    (True, "Collège prioritaire", "triangle-up", commun.MARQUE_PRIORITAIRE, 11),
]:
    sous = points[points["prioritaire"] == prioritaire]
    fig.add_trace(go.Scatter(
        x=sous["ips"], y=sous["va_taux_reussite_g"], mode="markers", name=f"{nom} ({len(sous)})",
        marker=dict(symbol=symbole, color=couleur, size=taille, line=dict(width=1.5, color=couleur if not prioritaire else "white")),
        customdata=sous[["nom_etablissement", "commune", "secteur", "nb_candidats_g", "uai"]].astype(str).values,
        hovertemplate=infobulle,
    ))
fig.add_vline(x=med, line=dict(color=commun.GRIS, width=1.5, dash="dash"))
fig.add_annotation(
    x=med, y=y_max, yanchor="bottom", showarrow=False, font=dict(color=commun.ENCRE, size=12),
    text=f"Médiane de l'IPS (académie) : {fr(med)}",
)
fig.add_hline(y=seuil, line=dict(color=commun.GRIS, width=1.5, dash="dash"))
fig.add_annotation(
    x=x_max, y=seuil, xanchor="right", yanchor="bottom", showarrow=False, font=dict(color=commun.ENCRE, size=12),
    bgcolor="rgba(255,255,255,0.85)",
    text="Résultats conformes à l'attendu (VA = 0)" if seuil == 0 else f"Seuil de valeur ajoutée : {fr(seuil, 0)} points",
)
if seuil != 0:
    fig.add_hline(y=0, line=dict(color=commun.MARQUE_CONTEXTE, width=1, dash="dot"))
fig.update_layout(
    height=580, margin=dict(l=70, r=20, t=70, b=70), plot_bgcolor="white",
    xaxis=dict(title="IPS du collège (plus bas = élèves de milieux plus défavorisés)", range=[x_min, x_max],
               gridcolor="#ececec", zeroline=False, automargin=True),
    yaxis=dict(title="Valeur ajoutée (points)", range=[y_min, y_max],
               gridcolor="#ececec", zeroline=False, automargin=True),
    legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="left", x=0),
    hoverlabel=dict(bgcolor="white", font_color=commun.ENCRE),
)
st.plotly_chart(fig, width="stretch")

# --- Lecture en texte (l'information ne dépend pas du graphique) -----------------------------
if regle == "C":
    lecture_regle = "IPS sous la médiane et valeur ajoutée négative **en 2024 et en 2025**"
else:
    lecture_regle = f"IPS sous la médiane et valeur ajoutée {'négative' if seuil == 0 else '≤ ' + fr(seuil, 0)} **en {session}**"
st.markdown(
    f"**Lecture.** Sur les {r['n_places']} collèges de la sélection placés sur le graphique "
    f"(session {session}, rentrée {rentree_de_session(session)}), **{r['n_prioritaires']}** sont prioritaires "
    f"selon la règle affichée ({lecture_regle}). Ils sont représentés par des triangles pleins ; les autres "
    f"collèges par des cercles vides. {r['n_sans_va']} collège(s) de la sélection n'ont pas de valeur ajoutée "
    "et ne sont pas placés."
)
if regle == "C":
    st.markdown(
        "Des **cercles vides apparaissent aussi dans la zone** : ces collèges ont une valeur ajoutée négative "
        f"en {session}, mais pas à l'autre session. La règle retenue demande une difficulté **répétée** sur les deux "
        "sessions, car la valeur ajoutée varie beaucoup d'une année à l'autre."
    )

# --- Pourquoi la valeur ajoutée ----------------------------------------------------------
st.subheader("Pourquoi regarder la valeur ajoutée plutôt que le taux de réussite ?")
if r["r_ips_taux"] is None:
    st.info("Sélection trop petite (moins de 10 collèges) pour calculer une corrélation fiable.")
else:
    k1, k2 = st.columns(2)
    k1.metric("IPS et taux de réussite brut", qualifier_correlation(r["r_ips_taux"]))
    k2.metric("IPS et valeur ajoutée", qualifier_correlation(r["r_ips_va"]))
    st.markdown(
        "Le **taux de réussite brut** suit de près le milieu social : plus l'IPS est élevé, plus le taux est élevé. "
        "Le comparer entre collèges reviendrait surtout à comparer leurs publics. La **valeur ajoutée** tient compte "
        "du profil des élèves : son lien avec l'IPS est bien plus faible. C'est pourquoi l'outil s'appuie sur elle.\n\n"
        "*r est le coefficient de corrélation : 0 = aucun lien linéaire, 1 ou -1 = lien parfait. "
        "Le mot suit une règle fixe, appliquée à la valeur absolue de r : moins de 0,10 = lien quasi nul ; "
        "de 0,10 à moins de 0,30 = faible ; de 0,30 à moins de 0,50 = modéré ; 0,50 ou plus = fort "
        "(seuils usuels de Cohen). Une corrélation décrit un lien, elle ne prouve pas une cause.*"
    )

with st.expander("Voir les données du graphique (tableau)"):
    tableau = points.assign(
        prioritaire=points["prioritaire"].map({True: "oui", False: "non"})
    )[["nom_etablissement", "commune", "code_departement", "secteur", "ips", "va_taux_reussite_g", "nb_candidats_g", "prioritaire", "uai"]]
    st.dataframe(
        tableau.sort_values(["prioritaire", "va_taux_reussite_g"], ascending=[False, True]),
        hide_index=True, width="stretch",
        column_config={
            "nom_etablissement": "Collège", "commune": "Commune", "code_departement": "Dépt", "secteur": "Secteur",
            "ips": st.column_config.NumberColumn("IPS", format="%.1f"),
            "va_taux_reussite_g": st.column_config.NumberColumn("Valeur ajoutée (points)", format="%+.0f"),
            "nb_candidats_g": "Candidats", "prioritaire": "Prioritaire", "uai": "UAI",
        },
    )

st.divider()
commun.source([session])  # source du graphique, des corrélations et du tableau
