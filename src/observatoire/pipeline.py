"""Pipeline reproductible : collecte → nettoyage → jointure → contrôles → export.

Usage :
    python -m observatoire.pipeline --sample   # échantillon versionné, sans réseau
    python -m observatoire.pipeline            # vraies sources de sources.yaml
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from observatoire.clean import clean_ips, clean_ivac, join_sources
from observatoire.collect import collect_all, read_raw
from observatoire.config import (
    CODE_ACADEMIE,
    DEPARTEMENTS_ACADEMIE,
    KEY,
    OUTPUT_CSV,
    PROCESSED,
    QUALITY_REPORT,
    SAMPLE_FILES,
    load_sources,
)
from observatoire.quality import QualityError, run_checks


def build_dataset(paths: dict, verbose: bool = True) -> pd.DataFrame:
    """Lit, nettoie et joint les deux sources ; `paths` = {id de source: fichier brut}."""
    sources = {s["id"]: s for s in load_sources()}
    ips = clean_ips(read_raw(sources["ips_colleges"], paths["ips_colleges"]), CODE_ACADEMIE)
    ivac = clean_ivac(read_raw(sources["ivac_colleges"], paths["ivac_colleges"]), CODE_ACADEMIE)
    df = join_sources(ips, ivac, KEY)
    if verbose:
        print(f"[pipeline] Académie {CODE_ACADEMIE} : {len(ips)} lignes IPS, {len(ivac)} lignes IVAC (toutes années)")
        print(f"[pipeline] Années communes retenues : {sorted(df['annee'].unique().tolist())}")
        print("[pipeline] Présence après jointure, par année :")
        print(pd.crosstab(df["annee"], df["presence"]).to_string())
    return df


def load_sample() -> pd.DataFrame:
    """Même traitement que les vraies données, sur les extraits versionnés de data/sample/."""
    return build_dataset(SAMPLE_FILES, verbose=False)


def run(sample: bool = False) -> pd.DataFrame:
    if sample:
        print("[pipeline] Mode échantillon (data/sample/)")
        df = load_sample()
    else:
        paths = collect_all()
        df = build_dataset(paths)

    report = run_checks(df, key=KEY, departements=DEPARTEMENTS_ACADEMIE)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    QUALITY_REPORT.write_text(report.to_markdown(), encoding="utf-8")
    print(report.to_markdown())

    if not report.ok:
        raise QualityError(f"Contrôle bloquant en échec, voir {QUALITY_REPORT}")

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"[pipeline] {len(df)} lignes écrites dans {OUTPUT_CSV}")
    return df


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline de l'observatoire")
    parser.add_argument("--sample", action="store_true", help="utiliser l'échantillon versionné")
    args = parser.parse_args()
    try:
        run(sample=args.sample)
    except (QualityError, NotImplementedError, ValueError) as error:
        print(f"[pipeline] ERREUR : {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
