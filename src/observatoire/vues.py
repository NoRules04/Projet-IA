"""Calculs du tableau de bord, sans Streamlit (donc testables).

Les écrans de app/ appellent ces fonctions ; ils ne font que de l'affichage.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Filtres:
    departements: list[str]
    secteurs: list[str]
    session: int


def rentree_de_session(session: int) -> str:
    """Session du brevet N → année scolaire « N-1-N » (D-005). Ex. 2025 → « 2024-2025 »."""
    return f"{session - 1}-{session}"


PETITS_MOTS = {"et", "de", "du", "des", "la", "le", "les", "sur", "sous", "en"}


def nom_propre(nom: str) -> str:
    """« SEINE-ET-MARNE » → « Seine-et-Marne » (petits mots en minuscules, sauf en tête)."""
    def mot(m: str, premier: bool) -> str:
        return m.lower() if (m.lower() in PETITS_MOTS and not premier) else m.capitalize()

    return " ".join(
        "-".join(mot(m, i == 0 and j == 0) for j, m in enumerate(bloc.split("-")))
        for i, bloc in enumerate(nom.split())
    )


def libelles_departements(df: pd.DataFrame) -> dict[str, str]:
    """{code: « code · Nom »}, ex. {"93": "93 · Seine-Saint-Denis"}, d'après les données."""
    paires = df[["code_departement", "departement"]].dropna().drop_duplicates("code_departement")
    return {
        code: f"{code} · {nom_propre(nom)}"
        for code, nom in sorted(zip(paires["code_departement"], paires["departement"]))
    }


def appliquer_filtres(df: pd.DataFrame, filtres: Filtres, toutes_sessions: bool = False) -> pd.DataFrame:
    """Lignes du département et du secteur choisis ; une seule session sauf si `toutes_sessions`."""
    masque = df["code_departement"].isin(filtres.departements) & df["secteur"].isin(filtres.secteurs)
    if not toutes_sessions:
        masque &= df["annee"] == filtres.session
    return df[masque]


def diagnostic_selection_vide(filtres: Filtres) -> str:
    """Message clair quand les filtres ne renvoient aucun collège."""
    if not filtres.departements:
        return "Aucun département n'est sélectionné : choisissez-en au moins un dans la barre latérale."
    if not filtres.secteurs:
        return "Aucun secteur n'est sélectionné : choisissez « public », « privé » ou les deux dans la barre latérale."
    return (
        "Aucun collège ne correspond à cette combinaison de filtres. "
        "Élargissez la sélection de départements ou de secteurs."
    )


def _court(texte: str, separateur: str) -> str:
    return texte.split(separateur)[0].strip()


def texte_source(sources: list[dict], sessions: list[int]) -> str:
    """Ligne de source à afficher sous chaque chiffre : producteur, jeux, années, licence, date d'accès."""
    sessions = sorted(sessions)
    rentrees = ", ".join(rentree_de_session(s) for s in sessions)
    libelle_sessions = ", ".join(str(s) for s in sessions)
    par_id = {s["id"]: s for s in sources}
    producteurs = sorted({_court(s["producteur"], ",") for s in sources})
    licences = sorted({_court(_court(s["licence"], "("), ",") for s in sources})
    dates = sorted({str(s["date_acces"]) for s in sources})
    pluriel = "s" if len(sessions) > 1 else ""
    return (
        f"Source : {', '.join(producteurs)}, « {par_id['ips_colleges']['nom']} » (rentrée{pluriel} {rentrees}) "
        f"et « {par_id['ivac_colleges']['nom']} » (session{pluriel} {libelle_sessions}). "
        f"{', '.join(licences)}. Consulté le {', '.join(dates)}."
    )


# --- Formatage -----------------------------------------------------------------

def fr(valeur: float | None, decimales: int = 1) -> str:
    """Nombre à la française : 100.9 → « 100,9 » ; -0.14 → « -0,14 » ; manquant → « — »."""
    if valeur is None or pd.isna(valeur):
        return "—"
    return f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")


# --- Corrélations en mots ----------------------------------------------------------------

# Seuils conventionnels de Cohen (1988) sur la valeur absolue de r (D-013).
SEUILS_CORRELATION = [(0.50, "Lien fort"), (0.30, "Lien modéré"), (0.10, "Lien faible"), (0.0, "Lien quasi nul")]


def qualifier_correlation(r: float | None) -> str:
    """« Lien fort (r = 0,73) ». Le mot est choisi sur la valeur ARRONDIE affichée (2 décimales),
    pour que le mot et le chiffre ne se contredisent jamais. Le signe ne change pas le mot."""
    if r is None or pd.isna(r):
        return "Corrélation non calculable"
    arrondi = round(float(r), 2)
    mot = next(m for seuil, m in SEUILS_CORRELATION if abs(arrondi) >= seuil)
    return f"{mot} (r = {fr(arrondi, 2)})"


# --- Écran 2 : vue d'ensemble ---------------------------------------------------------

MIN_POUR_CORRELATION = 10


def vue_ensemble(df: pd.DataFrame, filtres: Filtres, regle: str) -> tuple[pd.DataFrame, dict]:
    """Points de la session choisie (avec `prioritaire`) et chiffres clés de l'écran 2.

    `df` = toute l'académie : la médiane et la règle C sont calculées AVANT les filtres.
    """
    from observatoire.priority import marquer_prioritaires, mediane_ips, seuil_va

    complet = df.assign(prioritaire=marquer_prioritaires(df, regle))
    selection = appliquer_filtres(complet, filtres)
    places = selection.dropna(subset=["ips", "va_taux_reussite_g"])
    n = len(places)
    resume = {
        "session": filtres.session,
        "regle": regle,
        "mediane_ips": float(mediane_ips(df).get(filtres.session)),
        "seuil_va": seuil_va(regle),
        "n_selection": len(selection),
        "n_places": n,
        "n_prioritaires": int(places["prioritaire"].sum()),
        "n_sans_va": int(selection["va_taux_reussite_g"].isna().sum()),
        "r_ips_taux": places["ips"].corr(places["taux_reussite_g"]) if n >= MIN_POUR_CORRELATION else None,
        "r_ips_va": places["ips"].corr(places["va_taux_reussite_g"]) if n >= MIN_POUR_CORRELATION else None,
    }
    return places, resume


# --- Écran 3 : les quatre groupes --------------------------------------------------------

def libelles_groupes(regle: str) -> dict[str, str]:
    """Titres lisibles des groupes selon la règle (seuil 0 pour A et C, -5 pour B)."""
    from observatoire.priority import (
        G_IPS_BAS_VA_OK, G_IPS_HAUT_VA_BASSE, G_IPS_HAUT_VA_OK, G_MANQUANT, G_PRIORITAIRE,
    )

    sous, dessus = ("VA ≤ -5", "VA > -5") if regle == "B" else ("VA négative", "VA positive ou nulle")
    return {
        G_PRIORITAIRE: f"IPS bas · {sous}",
        G_IPS_BAS_VA_OK: f"IPS bas · {dessus}",
        G_IPS_HAUT_VA_BASSE: f"IPS haut · {sous}",
        G_IPS_HAUT_VA_OK: f"IPS haut · {dessus}",
        G_MANQUANT: "Sans valeur ajoutée",
    }


def groupes_selection(df: pd.DataFrame, filtres: Filtres, regle: str) -> dict:
    """Effectifs des groupes pour la sélection et la session choisies (médiane : toute l'académie).

    Règle C : groupes de la session au seuil 0 (comme A) ; `n_repetes` compte, dans le groupe
    « IPS bas · VA négative », les collèges qui y sont aussi à l'autre session (= liste prioritaire).
    """
    from observatoire.priority import GROUPES, G_MANQUANT, G_PRIORITAIRE, classer_session, marquer_prioritaires

    classe = classer_session(df, "B" if regle == "B" else "A")
    classe["prioritaire_c"] = marquer_prioritaires(df, "C")
    selection = appliquer_filtres(classe, filtres)
    effectifs = {g: int((selection["groupe"] == g).sum()) for g in GROUPES}
    deux_sessions = appliquer_filtres(classe, filtres, toutes_sessions=True)
    tableau = (
        pd.crosstab(deux_sessions["annee"], deux_sessions["groupe"]).reindex(columns=GROUPES, fill_value=0)
        if not deux_sessions.empty else pd.DataFrame(columns=GROUPES)
    )
    return {
        "effectifs": effectifs,
        "n_selection": len(selection),
        "n_places": len(selection) - effectifs[G_MANQUANT],
        "n_repetes": int(((selection["groupe"] == G_PRIORITAIRE) & selection["prioritaire_c"]).sum()),
        "tableau": tableau,
    }


def part(n: int, total: int) -> str:
    """« 23 % » ; « — » si le total est nul."""
    return "—" if total == 0 else f"{round(100 * n / total)} %"


# --- Écran 4 : liste prioritaire -------------------------------------------------------

CHOIX_NOMBRE = {"10 premiers": 10, "20 premiers": 20, "Tous": None}


def liste_selection(df: pd.DataFrame, filtres: Filtres) -> pd.DataFrame:
    """Liste de la règle C calculée sur TOUTE l'académie, puis filtrée (département, secteur).

    Le filtre de session ne s'applique pas : la règle porte sur les deux sessions.
    L'ordre de priorité reste celui de l'académie.
    """
    from observatoire.priority import liste_prioritaire

    liste = liste_prioritaire(df)
    garde = liste["code_departement"].isin(filtres.departements) & liste["secteur"].isin(filtres.secteurs)
    return liste[garde].reset_index(drop=True)


def premiers_avec_egalites(liste: pd.DataFrame, n: int | None) -> tuple[pd.DataFrame, int]:
    """Les n premiers de la liste (triée), plus tous ceux à égalité avec le n-ième (D-010).

    Renvoie (lignes gardées, nombre de collèges ajoutés à cause d'une égalité).
    """
    if n is None or n >= len(liste):
        return liste, 0
    seuil = liste["va_moyenne"].iloc[n - 1]
    garde = liste[liste["va_moyenne"] <= seuil]
    return garde, len(garde) - n


def table_liste(liste: pd.DataFrame, sessions: list[int], source: str | None = None) -> pd.DataFrame:
    """Tableau lisible (titres en français) ; avec `source`, ajoute une colonne Source (pour le CSV)."""
    colonnes = {
        "ordre_priorite": "Ordre de priorité (académie)",
        "nom_etablissement": "Collège",
        "commune": "Commune",
        "departement_lisible": "Département",
        "secteur": "Secteur",
        **{f"ips_{a}": f"IPS {a}" for a in sessions},
        **{f"va_{a}": f"Valeur ajoutée {a} (points)" for a in sessions},
        "va_moyenne": "Valeur ajoutée moyenne (points)",
        "uai": "UAI",
    }
    table = liste.assign(
        departement_lisible=liste["code_departement"] + " · " + liste["departement"].map(nom_propre)
    )[list(colonnes)].rename(columns=colonnes)
    if source is not None:
        table["Source"] = source
    return table.reset_index(drop=True)


def csv_liste(table: pd.DataFrame) -> bytes:
    """CSV pour un tableur français : séparateur « ; », virgule décimale, UTF-8 avec BOM (accents dans Excel)."""
    return table.to_csv(sep=";", decimal=",", index=False).encode("utf-8-sig")
