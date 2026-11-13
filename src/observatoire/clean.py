"""Nettoyage et typage.

Règle : chaque fonction fait une seule chose, est testée dans tests/test_clean.py,
et chaque choix non évident est justifié dans DECISIONS.md.
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


def normalize_column_name(name: str) -> str:
    """« Code Commune » → « code_commune » (minuscules, sans accents, sans espaces)."""
    text = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text.strip().lower())
    return text.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={c: normalize_column_name(c) for c in df.columns})


def clean_code_commune(codes: pd.Series) -> pd.Series:
    """Codes INSEE en texte sur 5 caractères ; « 1001 » devient « 01001 », « 2A004 » reste tel quel.

    Piège classique : un code lu comme un nombre perd son zéro initial.
    """
    as_text = codes.astype("string").str.strip().str.upper()
    as_text = as_text.str.replace(r"\.0$", "", regex=True)  # 1001.0 si la colonne a été lue en float
    return as_text.where(~as_text.str.fullmatch(r"\d{1,5}", na=False), as_text.str.zfill(5))


def departement_from_code(codes: pd.Series) -> pd.Series:
    """Département déduit du code commune : 3 caractères en outre-mer (97x), 2 sinon."""
    codes = codes.astype("string")
    outre_mer = codes.str.startswith("97", na=False)
    return codes.str[:2].where(~outre_mer, codes.str[:3])


def to_numeric_fr(values: pd.Series) -> pd.Series:
    """Convertit « 1 234,5 » en 1234.5 ; une valeur illisible devient NaN (jamais 0)."""
    text = (
        values.astype("string")
        .str.replace(" ", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    return pd.to_numeric(text, errors="coerce")


# --- Collèges : IPS et IVAC ---------------------------------------------------

# D-006 : seules ces quatre modalités existent dans les fichiers du 2026-11-13.
SECTEUR = {
    "public": "public",              # IPS
    "privé sous contrat": "privé",   # IPS
    "PU": "public",                  # IVAC
    "PR": "privé",                   # IVAC
}

# Colonnes communes aux deux sources, combinées après la jointure (IPS prioritaire).
COLONNES_PARTAGEES = ["nom_etablissement", "commune", "code_departement", "departement", "secteur"]

PRESENCE = {"both": "les_deux", "left_only": "ips_seul", "right_only": "ivac_seul"}


def clean_text(values: pd.Series) -> pd.Series:
    """Texte sans espaces superflus ; une chaîne vide devient manquante."""
    text = values.astype("string").str.strip()
    return text.mask(text == "")


def clean_uai(values: pd.Series) -> pd.Series:
    """Identifiant d'établissement en majuscules, sans espaces (ex. « 0930917s » → « 0930917S »)."""
    return clean_text(values).str.upper()


def harmonize_secteur(values: pd.Series) -> pd.Series:
    """« public » / « privé » (D-006). Une valeur inconnue devient manquante : elle n'est pas devinée."""
    return clean_text(values).map(SECTEUR).astype("string")


def session_from_annee_scolaire(values: pd.Series) -> pd.Series:
    """« 2024-2025 » → 2025 (session du brevet de cette année scolaire, D-005). Format inattendu → manquant."""
    parts = clean_text(values).str.extract(r"^(\d{4})-(\d{4})$")
    debut = pd.to_numeric(parts[0], errors="coerce")
    fin = pd.to_numeric(parts[1], errors="coerce")
    return fin.where(fin == debut + 1).astype("Int64")


def filter_academie(df: pd.DataFrame, code: str) -> pd.DataFrame:
    """Garde les lignes d'une académie, d'après son code (D-008)."""
    return df[clean_text(df["code_academie"]) == code]


def clean_ips(df: pd.DataFrame, code_academie: str) -> pd.DataFrame:
    """Source ips_colleges : filtre académique, typage, une ligne par (uai, annee)."""
    out = filter_academie(normalize_columns(df), code_academie).copy()
    res = pd.DataFrame(
        {
            "uai": clean_uai(out["uai"]),
            "annee": session_from_annee_scolaire(out["annee_scolaire"]),
            "nom_etablissement": clean_text(out["nom_de_l_etablissement"]),
            "code_commune": clean_code_commune(out["code_commune_insee"]),
            "commune": clean_text(out["libelle_commune"]),
            "code_departement": clean_text(out["code_departement"]),
            "departement": clean_text(out["libelle_departement"]),
            "secteur": harmonize_secteur(out["secteur"]),
            "ips": to_numeric_fr(out["ips"]),
            "ecart_type_ips": to_numeric_fr(out["ecart_type_de_l_ips"]),
        }
    )
    # Doublons stricts : supprimés. Doublons de clé avec valeurs différentes : gardés, le contrôle qualité les signale.
    return res.drop_duplicates().reset_index(drop=True)


def clean_ivac(df: pd.DataFrame, code_academie: str) -> pd.DataFrame:
    """Source ivac_colleges : filtre académique, typage, une ligne par (uai, annee)."""
    out = filter_academie(normalize_columns(df), code_academie).copy()
    res = pd.DataFrame(
        {
            "uai": clean_uai(out["uai"]),
            "annee": pd.to_numeric(clean_text(out["session"]), errors="coerce").astype("Int64"),
            "nom_etablissement": clean_text(out["nom_de_l_etablissement"]),
            "commune": clean_text(out["commune"]),
            "code_departement": clean_text(out["code_departement"]),
            "departement": clean_text(out["departement"]),
            "secteur": harmonize_secteur(out["secteur"]),
            "nb_candidats_g": to_numeric_fr(out["nb_candidats_g"]).astype("Int64"),
            "taux_reussite_g": to_numeric_fr(out["taux_de_reussite_g"]),
            "va_taux_reussite_g": to_numeric_fr(out["va_du_taux_de_reussite_g"]),
        }
    )
    return res.drop_duplicates().reset_index(drop=True)


def join_sources(ips: pd.DataFrame, ivac: pd.DataFrame, key: list[str]) -> pd.DataFrame:
    """Jointure complète sur `key`, limitée aux années communes (D-007, D-008).

    Les collèges présents dans une seule source sont gardés et étiquetés dans `presence`.
    """
    annees = sorted(set(ips["annee"].dropna()) & set(ivac["annee"].dropna()))
    ips = ips[ips["annee"].isin(annees)]
    ivac = ivac[ivac["annee"].isin(annees)]
    merged = ips.merge(ivac, on=key, how="outer", suffixes=("_ips", "_ivac"), indicator=True)
    for col in COLONNES_PARTAGEES:
        merged[col] = merged[f"{col}_ips"].combine_first(merged[f"{col}_ivac"])
    merged["presence"] = merged["_merge"].astype(str).map(PRESENCE).astype("string")
    colonnes = [
        "uai", "annee", "nom_etablissement", "commune", "code_commune", "code_departement", "departement",
        "secteur", "ips", "ecart_type_ips", "nb_candidats_g", "taux_reussite_g", "va_taux_reussite_g", "presence",
    ]
    return merged[colonnes].sort_values(key).reset_index(drop=True)
