"""Téléchargement des sources déclarées dans sources.yaml.

Chaque téléchargement est tracé dans data/raw/manifest.json (date, taille, empreinte
SHA-256) : on peut ainsi prouver quelle version des données a produit quel résultat.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from observatoire.config import RAW, load_sources


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(source: dict, dest_dir: Path = RAW, force: bool = False) -> Path:
    """Télécharge une source si elle n'est pas déjà présente dans data/raw/."""
    url = (source.get("url") or "").strip()
    if not url:
        raise ValueError(
            f"La source « {source.get('id')} » n'a pas d'url dans sources.yaml. "
            "Renseignez le lien direct vers le fichier."
        )
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source["fichier"]
    if dest.exists() and not force:
        print(f"[collect] {dest.name} déjà présent, téléchargement ignoré (force=True pour refaire).")
        return dest

    print(f"[collect] Téléchargement de {source['id']} depuis {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "observatoire-prj450"})
    with urllib.request.urlopen(request, timeout=120) as response, open(dest, "wb") as out:
        out.write(response.read())

    _update_manifest(dest_dir, source, dest)
    return dest


def _update_manifest(dest_dir: Path, source: dict, dest: Path) -> None:
    manifest_path = dest_dir / "manifest.json"
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[source["id"]] = {
        "fichier": dest.name,
        "url": source.get("url"),
        "telecharge_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "octets": dest.stat().st_size,
        "sha256": sha256(dest),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")


def collect_all(force: bool = False) -> dict[str, Path]:
    """Télécharge toutes les sources ; retourne {id: chemin local}."""
    return {s["id"]: download(s, force=force) for s in load_sources()}


def read_raw(source: dict, path: Path) -> pd.DataFrame:
    """Lit un fichier brut avec le séparateur et l'encodage déclarés dans sources.yaml.

    Tout est lu en texte (dtype=str) : le typage se fait ensuite dans clean.py,
    ce qui évite de perdre un zéro initial (UAI « 0930917S », codes département).
    """
    if source.get("format", "csv") != "csv":
        raise ValueError(f"Format « {source.get('format')} » non pris en charge pour « {source['id']} ».")
    return pd.read_csv(
        path,
        sep=source.get("separateur", ";"),
        encoding=source.get("encodage", "utf-8"),
        dtype=str,
    )


def load_all(force: bool = False) -> dict[str, pd.DataFrame]:
    """Télécharge (si besoin) puis charge toutes les sources ; retourne {id: table brute}."""
    sources = {s["id"]: s for s in load_sources()}
    paths = collect_all(force=force)
    return {sid: read_raw(sources[sid], path) for sid, path in paths.items()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Télécharge et charge les sources de sources.yaml")
    parser.add_argument("--force", action="store_true", help="retélécharger même si le fichier existe")
    args = parser.parse_args()
    try:
        tables = load_all(force=args.force)
    except (ValueError, OSError) as error:
        print(f"[collect] ERREUR : {error}", file=sys.stderr)
        return 1
    for sid, df in tables.items():
        print(f"[collect] {sid} : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
