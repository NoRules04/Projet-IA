"""Règle de priorité d'accompagnement (D-009).

Vocabulaire : on parle de « priorité d'accompagnement » et d'« ordre de priorité »,
jamais de classement ni de « mauvais » collèges.

Important : la médiane de l'IPS se calcule sur TOUTE l'académie, session par session,
avant d'appliquer les filtres du tableau de bord. Sinon, filtrer un département
changerait la définition de « défavorisé ».
"""

from __future__ import annotations

import pandas as pd

# Règles par session, gardées pour comparaison (D-009). VA = valeur ajoutée du taux de réussite.
REGLES = {
    "A": {"libelle": "A : IPS bas et VA < 0 (session par session)", "seuil": 0.0, "inclusif": False},
    "B": {"libelle": "B : IPS bas et VA ≤ -5 (session par session)", "seuil": -5.0, "inclusif": True},
}

# Les quatre groupes, plus les lignes sans valeur ajoutée.
G_PRIORITAIRE = "IPS bas · VA sous le seuil"
G_IPS_BAS_VA_OK = "IPS bas · VA au-dessus du seuil"
G_IPS_HAUT_VA_BASSE = "IPS haut · VA sous le seuil"
G_IPS_HAUT_VA_OK = "IPS haut · VA au-dessus du seuil"
G_MANQUANT = "VA manquante"
GROUPES = [G_PRIORITAIRE, G_IPS_BAS_VA_OK, G_IPS_HAUT_VA_BASSE, G_IPS_HAUT_VA_OK, G_MANQUANT]


def mediane_ips(df: pd.DataFrame) -> pd.Series:
    """Médiane de l'IPS des collèges, pour chaque session : {annee: médiane}."""
    return df.groupby("annee")["ips"].median()


def ips_bas(df: pd.DataFrame) -> pd.Series:
    """Vrai si l'IPS est strictement inférieur à la médiane de sa session (égal à la médiane → « haut »)."""
    return df["ips"] < df.groupby("annee")["ips"].transform("median")


def va_sous_seuil(va: pd.Series, seuil: float, inclusif: bool) -> pd.Series:
    """Vrai si la VA est sous le seuil ; une VA manquante donne Faux (elle est traitée à part)."""
    return (va <= seuil) if inclusif else (va < seuil)


def classer_session(df: pd.DataFrame, regle: str = "A") -> pd.DataFrame:
    """Ajoute `ips_bas` et `groupe` (un des GROUPES) à chaque ligne collège × session."""
    params = REGLES[regle]
    out = df.copy()
    out["ips_bas"] = ips_bas(out)
    va = out["va_taux_reussite_g"]
    sous = va_sous_seuil(va, params["seuil"], params["inclusif"])
    groupe = pd.Series(G_IPS_HAUT_VA_OK, index=out.index, dtype="string")
    groupe[out["ips_bas"] & ~sous] = G_IPS_BAS_VA_OK
    groupe[~out["ips_bas"] & sous] = G_IPS_HAUT_VA_BASSE
    groupe[out["ips_bas"] & sous] = G_PRIORITAIRE
    groupe[va.isna()] = G_MANQUANT
    out["groupe"] = groupe
    return out


def effectifs_groupes(classe: pd.DataFrame) -> pd.DataFrame:
    """Nombre de lignes par session et par groupe (toutes les colonnes de GROUPES, même vides)."""
    table = pd.crosstab(classe["annee"], classe["groupe"])
    return table.reindex(columns=GROUPES, fill_value=0)


def liste_prioritaire(df: pd.DataFrame) -> pd.DataFrame:
    """Règle C (D-009) : IPS bas ET VA < 0 à TOUTES les sessions du fichier (2024 et 2025).

    Un collège sans VA à l'une des sessions n'est pas classable : il n'est pas dans la liste
    (voir `non_classables`). Ordre de priorité : VA moyenne croissante, puis UAI pour départager.
    """
    sessions = sorted(df["annee"].dropna().unique())
    travail = df.assign(ips_bas=ips_bas(df), va_negative=df["va_taux_reussite_g"] < 0)
    par_college = travail.groupby("uai").agg(
        nb_sessions=("annee", "nunique"),
        ips_bas_partout=("ips_bas", "all"),
        va_negative_partout=("va_negative", "all"),
        va_complete=("va_taux_reussite_g", lambda s: s.notna().all()),
    )
    eligibles = par_college[
        (par_college["nb_sessions"] == len(sessions))
        & par_college["va_complete"]
        & par_college["ips_bas_partout"]
        & par_college["va_negative_partout"]
    ].index

    retenus = df[df["uai"].isin(eligibles)]
    large = retenus.pivot(index="uai", columns="annee", values=["ips", "va_taux_reussite_g"])
    large.columns = [f"{'ips' if v == 'ips' else 'va'}_{int(a)}" for v, a in large.columns]
    # Si aucun collège n'est éligible, le tableau est vide et sans colonnes : on les crée.
    large = large.reindex(columns=[f"{p}_{int(a)}" for p in ("ips", "va") for a in sessions])
    infos = (
        retenus.sort_values("annee")
        .groupby("uai")[["nom_etablissement", "commune", "code_departement", "departement", "secteur"]]
        .last()
    )
    liste = infos.join(large)
    liste["va_moyenne"] = liste[[f"va_{int(a)}" for a in sessions]].mean(axis=1)
    liste = liste.reset_index().sort_values(["va_moyenne", "uai"]).reset_index(drop=True)
    liste.insert(0, "ordre_priorite", range(1, len(liste) + 1))
    return liste


def non_classables(df: pd.DataFrame) -> pd.DataFrame:
    """Collèges sans VA à au moins une session (absents d'IVAC ou VA non calculée) : à montrer à part."""
    manque = df[df["va_taux_reussite_g"].isna()]
    return (
        manque.groupby("uai")
        .agg(
            nom_etablissement=("nom_etablissement", "first"),
            code_departement=("code_departement", "first"),
            secteur=("secteur", "first"),
            sessions_sans_va=("annee", lambda s: ", ".join(str(int(a)) for a in sorted(s))),
            absent_d_ivac=("presence", lambda s: bool((s == "ips_seul").any())),
        )
        .reset_index()
    )
