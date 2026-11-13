# Échantillon (extraits réels)

`ips_colleges_extrait.csv` et `ivac_colleges_extrait.csv` sont des **extraits non modifiés** des deux sources
déclarées dans `sources.yaml` (DEPP, Licence Ouverte v2.0), téléchargées le 2026-11-13 : toutes les lignes,
toutes années confondues, de 7 collèges choisis. Même format que les fichiers bruts (séparateur `;`, BOM UTF-8).

Ils servent à `python -m observatoire.pipeline --sample` (sans réseau) et aux tests. Ce ne sont pas des résultats :
7 collèges ne représentent pas l'académie.

| UAI | Pourquoi il est là |
| --- | --- |
| 0770002J | collège public du 77, présent dans les deux sources |
| 0771216D | collège privé du 77, présent dans les deux sources |
| 0940003T | collège public du 94, présent dans les deux sources |
| 0930593P | valeur ajoutée manquante en session 2025 malgré plus de 40 candidats |
| 0932302X | collège privé, moins de 40 candidats : valeur ajoutée non calculée |
| 0772923J | présent dans IPS mais absent d'IVAC en sessions 2024 et 2025 (`presence = ips_seul`) |
| 0511191T | académie de Reims : doit être exclu par le filtre académique |

Pièges couverts : BOM en début de fichier, codes de secteur différents (`public` / `PU`), années écrites
différemment (`2024-2025` / `2025`), années présentes dans une seule source (sessions 2022, 2023, 2026).
