import pytest

from observatoire.collect import download, read_raw

SOURCE = {"id": "test", "format": "csv", "separateur": ";", "encodage": "utf-8-sig"}


def test_read_raw_retire_le_bom_et_garde_le_texte(tmp_path):
    fichier = tmp_path / "brut.csv"
    # Le BOM (EF BB BF) est présent au début des fichiers de data.education.gouv.fr.
    fichier.write_bytes("﻿UAI;IPS\n0930917S;91.4\n".encode("utf-8"))
    df = read_raw(SOURCE, fichier)
    assert list(df.columns) == ["UAI", "IPS"]  # pas de « ﻿UAI »
    assert df.loc[0, "UAI"] == "0930917S"
    assert df.loc[0, "IPS"] == "91.4"  # encore du texte : le typage se fait dans clean.py


def test_url_manquante_donne_un_message_clair(tmp_path):
    with pytest.raises(ValueError, match="n'a pas d'url"):
        download({"id": "sans_url", "url": "", "fichier": "x.csv"}, dest_dir=tmp_path)


def test_format_non_csv_refuse(tmp_path):
    with pytest.raises(ValueError, match="non pris en charge"):
        read_raw({**SOURCE, "format": "json"}, tmp_path / "x.json")
