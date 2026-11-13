# Dictionnaire des variables

Une ligne par colonne du jeu de données final (`data/processed/observatoire.csv`) : 14 colonnes, 882 lignes.

- **Plages** : valeurs observées le 2026-11-13 sur les sessions 2024 et 2025.
- **Sources** : `ips_colleges` et `ivac_colleges`, déclarées dans `sources.yaml`.
- **« IPS prioritaire »** : quand la colonne existe dans les deux sources, on prend la valeur d'IPS, et celle d'IVAC seulement si IPS n'a pas la ligne.

| Variable | Description | Type | Unité | Valeurs possibles / plage | Source | Traitement appliqué |
| --- | --- | --- | --- | --- | --- | --- |
| uai | Identifiant national de l'établissement (Unité administrative immatriculée) | texte (8 caractères) | — | 7 chiffres + 1 lettre, ex. 0940003T ; 441 valeurs distinctes | les deux | majuscules, espaces retirés (`clean_uai`) ; clé de jointure |
| annee | Session du brevet ; pour IPS, année scolaire correspondante (2025 = rentrée 2024-2025) | entier | année | 2024, 2025 | les deux | IPS : `session_from_annee_scolaire` (D-005) ; seules les années communes sont gardées (D-007) ; clé de jointure |
| nom_etablissement | Nom du collège | texte | — | ex. COLLEGE LAPLACE | IPS prioritaire, sinon IVAC | espaces retirés ; les deux sources n'écrivent pas toujours le nom pareil (ex. IVAC : COLLEGE AMEDEE LAPLACE) |
| commune | Nom de la commune du collège | texte | — | ex. CRETEIL | IPS prioritaire, sinon IVAC | espaces retirés |
| code_commune | Code officiel géographique INSEE de la commune | texte (5 caractères) | — | ex. 94028 | ips_colleges | complété à 5 caractères (`clean_code_commune`) ; manquant si la ligne vient seulement d'IVAC (aucun cas au 2026-11-13) |
| code_departement | Code du département | texte | — | 77, 93, 94 | IPS prioritaire, sinon IVAC | espaces retirés ; contrôle bloquant : uniquement les départements de l'académie |
| departement | Nom du département | texte | — | SEINE-ET-MARNE, SEINE-SAINT-DENIS, VAL-DE-MARNE | IPS prioritaire, sinon IVAC | espaces retirés |
| secteur | Secteur de l'établissement | texte | — | public, privé (privé = privé sous contrat) | IPS prioritaire, sinon IVAC | IPS « public » / « privé sous contrat » et IVAC « PU » / « PR » harmonisés ; une valeur inconnue devient manquante et bloque le pipeline (D-006) |
| ips | Indice de position sociale moyen des élèves du collège ; plus il est élevé, plus le milieu social est favorisé | décimal | indice (sans unité) | 70.2 à 158.0 ; 0 manquant | ips_colleges | texte converti en nombre (`to_numeric_fr`) |
| ecart_type_ips | Écart type de l'IPS des élèves du collège : plus il est grand, plus le collège mélange des milieux sociaux différents | décimal | indice (sans unité) | 16.7 à 43.2 ; 0 manquant | ips_colleges | texte converti en nombre |
| nb_candidats_g | Nombre de candidats au brevet, série générale | entier | élèves | 20 à 314 ; 23 manquants (lignes `ips_seul`) | ivac_colleges | texte converti en entier |
| taux_reussite_g | Part des candidats de série générale admis au brevet | décimal | % | 55.0 à 100.0 ; 23 manquants (lignes `ips_seul`) | ivac_colleges | texte converti en nombre ; contrôle bloquant : entre 0 et 100 |
| va_taux_reussite_g | Valeur ajoutée du taux de réussite = taux constaté − taux attendu par le modèle de la DEPP ; négative = réussite inférieure à l'attendu | décimal | points de % | -24.0 à 23.0 ; 49 manquants (23 `ips_seul` + 26 non calculés par la DEPP, notamment sous 40 candidats) | ivac_colleges | texte converti en nombre ; une valeur absente reste manquante, jamais 0 |
| presence | Source(s) où la ligne a été trouvée | texte | — | les_deux (859), ips_seul (23), ivac_seul (0) | dérivé | créé par la jointure complète (`join_sources`, D-008) |
