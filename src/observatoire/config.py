"""Chemins du projet et lecture de sources.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
SAMPLE = DATA / "sample"
SOURCES_FILE = ROOT / "sources.yaml"

OUTPUT_CSV = PROCESSED / "observatoire.csv"
QUALITY_REPORT = PROCESSED / "rapport_qualite.md"

# Clé qui identifie une ligne du jeu final : un collège (UAI) une année (session du brevet, D-005).
KEY = ["uai", "annee"]

# Périmètre (D-002, D-008) : filtre par code académie, identique dans les deux sources.
CODE_ACADEMIE = "24"  # CRETEIL
DEPARTEMENTS_ACADEMIE = ["77", "93", "94"]  # Seine-et-Marne, Seine-Saint-Denis, Val-de-Marne

# Extraits réels versionnés, utilisés par `--sample` et par les tests (voir data/sample/README.md).
SAMPLE_FILES = {
    "ips_colleges": SAMPLE / "ips_colleges_extrait.csv",
    "ivac_colleges": SAMPLE / "ivac_colleges_extrait.csv",
}


def load_sources(path: Path = SOURCES_FILE) -> list[dict]:
    """Retourne la liste des sources déclarées dans sources.yaml."""
    with open(path, encoding="utf-8") as f:
        content = yaml.safe_load(f) or {}
    return content.get("sources", [])
