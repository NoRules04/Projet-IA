"""Contrôles qualité.

Un contrôle « bloquant » arrête le pipeline ; une « alerte » est rapportée mais n'arrête rien.
Le rapport est écrit dans data/processed/rapport_qualite.md et alimente la data card.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

BLOQUANT = "bloquant"
ALERTE = "alerte"


@dataclass
class Check:
    nom: str
    ok: bool
    detail: str
    gravite: str = BLOQUANT


@dataclass
class QualityReport:
    checks: list[Check] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks if c.gravite == BLOQUANT)

    def add(self, check: Check) -> None:
        self.checks.append(check)

    def to_markdown(self) -> str:
        lines = ["# Rapport qualité", "", "| Contrôle | Gravité | Résultat | Détail |", "| --- | --- | --- | --- |"]
        for c in self.checks:
            lines.append(f"| {c.nom} | {c.gravite} | {'OK' if c.ok else 'ÉCHEC'} | {c.detail} |")
        return "\n".join(lines) + "\n"


class QualityError(Exception):
    pass


def check_required_columns(df: pd.DataFrame, required: list[str]) -> Check:
    missing = [c for c in required if c not in df.columns]
    return Check("Colonnes attendues présentes", not missing, f"manquantes : {missing}" if missing else "toutes présentes")


def check_unique_key(df: pd.DataFrame, key: list[str]) -> Check:
    n = int(df.duplicated(subset=key, keep=False).sum())
    return Check(f"Clé unique {key}", n == 0, f"{n} lignes en doublon sur la clé")


def check_key_complete(df: pd.DataFrame, key: list[str]) -> Check:
    n = int(df[key].isna().any(axis=1).sum())
    return Check(f"Clé complète {key}", n == 0, f"{n} lignes avec une clé manquante")


def check_uai_format(df: pd.DataFrame, column: str = "uai") -> Check:
    """UAI : 7 chiffres puis une lettre (ex. 0930917S)."""
    valid = df[column].astype("string").str.fullmatch(r"\d{7}[A-Z]", na=False)
    n = int((~valid).sum())
    return Check("Format des UAI", n == 0, f"{n} UAI invalides")


def check_allowed_values(df: pd.DataFrame, column: str, allowed: list[str]) -> Check:
    """Toutes les valeurs (manquantes comprises) doivent appartenir à `allowed`."""
    bad = ~df[column].isin(allowed)
    exemples = sorted(df.loc[bad, column].astype(str).unique())[:5]
    return Check(f"Valeurs autorisées de {column} {allowed}", not bad.any(), f"{int(bad.sum())} hors liste {exemples}")


def check_presence(df: pd.DataFrame, column: str = "presence") -> Check:
    """Alerte : lignes présentes dans une seule source (perdues par une jointure interne)."""
    counts = df[column].value_counts().to_dict()
    seules = len(df) - counts.get("les_deux", 0)
    detail = ", ".join(f"{k} : {v}" for k, v in sorted(counts.items()))
    return Check("Présence dans les deux sources", seules == 0, detail, gravite=ALERTE)


def check_missing(df: pd.DataFrame, columns: list[str]) -> Check:
    counts = {c: int(df[c].isna().sum()) for c in columns}
    total = sum(counts.values())
    detail = ", ".join(f"{c} : {n} ({n / len(df):.0%})" for c, n in counts.items()) if len(df) else "table vide"
    return Check("Valeurs manquantes", total == 0, detail, gravite=ALERTE)


def check_range(df: pd.DataFrame, column: str, low: float | None = None, high: float | None = None) -> Check:
    values = df[column].dropna()
    bad = pd.Series(False, index=values.index)
    if low is not None:
        bad |= values < low
    if high is not None:
        bad |= values > high
    return Check(f"Plage de {column} [{low} ; {high}]", not bad.any(), f"{int(bad.sum())} valeurs hors plage")


def check_not_empty(df: pd.DataFrame) -> Check:
    return Check("Table non vide", len(df) > 0, f"{len(df)} lignes")


REQUIRED = [
    "uai", "annee", "nom_etablissement", "code_departement", "secteur",
    "ips", "nb_candidats_g", "taux_reussite_g", "va_taux_reussite_g", "presence",
]


def run_checks(df: pd.DataFrame, key: list[str], departements: list[str] | None = None) -> QualityReport:
    """Contrôles du jeu final. Chaque hypothèse sur les données a son contrôle."""
    report = QualityReport()
    report.add(check_not_empty(df))
    report.add(check_required_columns(df, REQUIRED))
    if not report.ok:
        return report
    # Bloquants : ce qui rendrait les résultats faux.
    report.add(check_key_complete(df, key))
    report.add(check_unique_key(df, key))
    report.add(check_uai_format(df))
    report.add(check_allowed_values(df, "secteur", ["public", "privé"]))
    if departements is not None:
        report.add(check_allowed_values(df, "code_departement", departements))
    report.add(check_range(df, "annee", low=2000, high=2100))
    report.add(check_range(df, "ips", low=0))
    report.add(check_range(df, "nb_candidats_g", low=0))
    report.add(check_range(df, "taux_reussite_g", low=0, high=100))
    # Alertes : ce qu'il faut montrer à l'utilisateur, sans arrêter le pipeline.
    report.add(check_presence(df))
    report.add(check_missing(df, ["ips", "taux_reussite_g", "va_taux_reussite_g"]))
    return report
