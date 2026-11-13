# Data card

> Une section par source, plus une section pour le jeu de données final (après jointure).
> État au 2026-11-13 (fichiers téléchargés le 2026-11-13, voir `data/raw/manifest.json`). Chiffres recalculés par le pipeline : `python -m observatoire.pipeline`.

## Source : Indices de position sociale des collèges (à partir de 2023) (`ips_colleges` dans sources.yaml)

| Champ | Valeur |
| --- | --- |
| Producteur | DEPP, ministère chargé de l'Éducation nationale |
| Lien | https://www.data.gouv.fr/datasets/ips-colleges-a-partir-de-2023 (fichier : export CSV de data.education.gouv.fr, jeu `fr-en-ips-colleges-ap2023`) |
| Licence | Licence Ouverte v2.0 (Etalab), selon la fiche du producteur sur data.education.gouv.fr. Attention : data.gouv.fr affiche « licence non spécifiée » pour ce jeu. |
| Date d'accès | 2026-11-13 (dernière modification indiquée par le producteur : 2026-09-01) |
| Fréquence de mise à jour | Annuelle (selon data.gouv.fr) |
| Maille | Établissement (collège), une ligne par collège et par année scolaire |
| Période couverte | Rentrées 2023-2024, 2024-2025 et 2025-2026 |
| Nombre de lignes / colonnes (brut) | 21 061 lignes × 24 colonnes (France entière) ; 1 325 lignes pour l'académie de Créteil (441 + 441 + 443) |
| Clé de jointure | `UAI` + année (rentrée « 2024-2025 » convertie en session 2025, D-005) |
| Empreinte du fichier utilisé | SHA-256 `7ae96dec710116a69b1535cefaab1d713a4554c556882d92e824826059cd91e1` |

**Comment les données sont produites** : données administratives. Selon le guide méthodologique IVAC 2025 de la DEPP, chaque élève reçoit un indice d'après les catégories socioprofessionnelles de ses deux parents. L'IPS d'un collège est la valeur moyenne pour ses élèves (plus il est élevé, plus le milieu social est favorisé). Le fichier fournit aussi l'écart type de l'IPS dans le collège et des IPS de référence (académique, départemental, national, public et privé).

**Qualité constatée** (académie de Créteil, code académie 24) :
- 0 IPS manquant (8 IPS manquants sur 21 061 lignes en France entière) ;
- 0 doublon sur (UAI, année) ;
- 100 % des UAI au format attendu (7 chiffres + 1 lettre) ;
- IPS entre 70.2 et 158.0 sur les sessions retenues ;
- le fichier commence par un BOM (3 octets invisibles), retiré par l'encodage `utf-8-sig` ;
- le secteur est codé « public » / « privé sous contrat » (harmonisé, D-006).

**Biais connus** :
- seuls les collèges publics et privés sous contrat sont présents ; les collèges hors contrat sont absents ;
- l'IPS est une moyenne : deux collèges au même IPS peuvent accueillir des publics très différents (voir `ecart_type_ips`) ;
- il repose sur la profession déclarée des parents, et ne mesure pas directement les revenus ni le diplôme.

**Usages à éviter** :
- juger la qualité d'un collège avec l'IPS (il décrit les élèves accueillis, pas l'enseignement) ;
- en déduire une cause des résultats scolaires.

## Source : Indicateurs de valeur ajoutée des collèges (`ivac_colleges` dans sources.yaml)

| Champ | Valeur |
| --- | --- |
| Producteur | DEPP, ministère chargé de l'Éducation nationale |
| Lien | https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-colleges (fichier : export CSV de data.education.gouv.fr, jeu `fr-en-indicateurs-valeur-ajoutee-colleges`) |
| Licence | Licence Ouverte v2.0 (Etalab), sur data.gouv.fr comme chez le producteur |
| Date d'accès | 2026-11-13 (dernière modification indiquée par le producteur : 2026-08-03) |
| Fréquence de mise à jour | Annuelle (selon data.gouv.fr) |
| Maille | Établissement (collège), une ligne par collège et par session du brevet |
| Période couverte | Sessions du brevet 2022, 2023, 2024 et 2025 |
| Nombre de lignes / colonnes (brut) | 26 869 lignes × 27 colonnes (France entière) ; 1 705 lignes pour l'académie de Créteil (422 + 424 + 428 + 431) |
| Clé de jointure | `UAI` + session |
| Empreinte du fichier utilisé | SHA-256 `5c792aa082eefd1f5d1d57e185c703e824ad3221d74eb952382147437e49c30e` |

**Comment les données sont produites** : résultats administratifs du diplôme national du brevet (DNB), combinés par un modèle statistique de la DEPP (guide méthodologique IVAC 2025).
- Le modèle estime pour chaque élève sa probabilité de réussir, d'après son âge, son niveau aux évaluations de 6e, son origine sociale et son sexe.
- Le **taux attendu** du collège est la moyenne de ces probabilités.
- **Valeur ajoutée = taux constaté − taux attendu**, en points.
- Le guide précise que le calcul ne peut pas être refait « à la main » : on utilise les valeurs publiées.

**Qualité constatée** (académie de Créteil) :
- 0 doublon sur (UAI, session) ;
- 0 taux de réussite manquant ;
- **53 valeurs ajoutées manquantes** sur 1 705 lignes (18 en 2022, 9 en 2023, 11 en 2024, 15 en 2025) ; en France entière : 1 784 sur 26 869 ;
- parmi les 26 manquantes des sessions retenues (2024 et 2025), 10 concernent des collèges de moins de 40 candidats et 16 des collèges de 40 candidats ou plus ;
- fichier avec BOM ; secteur codé « PU » / « PR » (harmonisé, D-006).

**Biais connus** :
- la valeur ajoutée n'est **pas calculée** (« ND ») sous 40 candidats en série générale, ni quand moins de 75 % des scores de 6e ou des professions des parents sont retrouvés (guide IVAC 2025) : les petits collèges et ceux aux données incomplètes disparaissent des analyses ;
- 15 des 26 valeurs ajoutées manquantes en 2024-2025 concernent des collèges privés, alors que le privé représente 71 collèges sur 441 : **le privé est sous-représenté** dans les analyses de valeur ajoutée ;
- seule la **série générale** du brevet a une valeur ajoutée (pas la série professionnelle) ;
- le guide signale un changement de méthode : depuis la session 2025, les élèves en UPE2A sont retirés du calcul du taux d'accès. Cet indicateur n'est pas utilisé dans l'observatoire.

**Usages à éviter** :
- classer les collèges entre eux comme un palmarès ;
- interpréter un petit écart (quelques points) comme une différence certaine ;
- expliquer pourquoi un collège est au-dessus ou en dessous de l'attendu.

## Jeu de données final

| Champ | Valeur |
| --- | --- |
| Fichier | `data/processed/observatoire.csv` |
| Lignes / colonnes | 882 lignes × 14 colonnes = 441 collèges × 2 sessions (2024 et 2025) ; 370 publics et 71 privés ; 159 en Seine-Saint-Denis, 150 en Seine-et-Marne, 132 dans le Val-de-Marne |
| Lignes écartées avant la jointure | **Volontairement**, années présentes dans une seule source (D-007) : 443 lignes IPS de la rentrée 2025-2026 et 846 lignes IVAC des sessions 2022 et 2023 |
| Lignes perdues à la jointure | **0** : la jointure est complète (D-008). **23 lignes (2,6 %) sont présentes seulement dans IPS** (`presence = ips_seul` : 13 en 2024, 10 en 2025), soit 13 collèges différents (15 lignes privées, 8 publiques ; 11 en Seine-et-Marne, 6 en Seine-Saint-Denis, 6 dans le Val-de-Marne). 3 de ces collèges figurent dans IVAC pour d'autres sessions. La raison de leur absence n'est pas documentée dans les sources : **à vérifier**. 0 ligne présente seulement dans IVAC. |
| Valeurs manquantes par colonne | `nb_candidats_g` : 23 (2,6 %) ; `taux_reussite_g` : 23 (2,6 %) ; `va_taux_reussite_g` : 49 (5,6 %), soit les 23 lignes `ips_seul` + 26 lignes dont la valeur ajoutée n'est pas calculée par la DEPP ; toutes les autres colonnes : 0 |
| Contrôles qualité | 11 contrôles bloquants OK, 2 alertes (présence, valeurs manquantes) : voir `data/processed/rapport_qualite.md` |

**Traitements appliqués** (fonctions de `src/observatoire/clean.py`) :
1. **Lecture** de tout en texte, BOM retiré : `read_raw` dans `collect.py`.
2. **Filtre** sur le code académie « 24 » : `filter_academie` (D-002, D-004, D-008).
3. **Noms de colonnes** normalisés : `normalize_columns`.
4. **Typage** :
   - nombres : `to_numeric_fr` (une valeur illisible devient manquante, jamais 0) ;
   - UAI : `clean_uai` ;
   - code commune : `clean_code_commune`.
5. **Année** : la rentrée « 2024-2025 » est convertie en session 2025 avec `session_from_annee_scolaire` (D-005).
6. **Secteur** harmonisé en « public » / « privé » : `harmonize_secteur` (D-006).
7. **Doublons stricts** supprimés : `clean_ips`, `clean_ivac`.
8. **Années communes** seulement, puis **jointure complète** sur (uai, annee) avec la colonne `presence`. Pour le nom, la commune, le département et le secteur, IPS est prioritaire : `join_sources` (D-007, D-008).
