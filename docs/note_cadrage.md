# Note de cadrage — v1

> Binôme : Mohamed Rayen Aissa, Mouhamad Aicha · Dépôt : https://github.com/NoRules04/Projet-IA · Version : v1 du 13/11/2026 (v0 du 13/11/2026)
> Une rubrique encore vide s'écrit « à préciser en S2 », jamais laissée blanche.

## 1. Public cible

Persona : chargé(e) de mission au rectorat de l'académie de Créteil.
Besoin : savoir quels collèges accompagner en priorité, en préparant chaque année une liste de collèges prioritaires.
Contraintes : peu de temps, à l'aise avec un tableur mais pas avec le code, consulte l'outil dans un navigateur, usage une à deux fois par an.

## 2. Problématique

Parmi les collèges socialement défavorisés de l'académie de Créteil, lesquels obtiennent au brevet des résultats inférieurs à ceux attendus pour leur profil, et doivent être accompagnés en priorité à la rentrée 2027 ?

Test des cinq critères :

- [x] Décideur : on peut nommer qui utilisera l'observatoire.
- [x] Décision : une action change selon le résultat.
- [x] Vérifiabilité : on saura dire si on a répondu.
- [x] Faisabilité : au moins deux sources ouvertes qui se croisent.
- [x] Prudence : la question n'exige pas de preuve causale.

## 3. Décision visée

Proposer une liste de collèges prioritaires pour un dispositif d'accompagnement, avant la préparation de la rentrée 2027 (échéance exacte : à préciser en S2).

Règle de priorité retenue (D-009) : un collège est prioritaire si son IPS est inférieur à la médiane des collèges de l'académie **et** si sa valeur ajoutée au brevet est négative **aux deux sessions 2024 et 2025**. 72 collèges remplissent cette règle. Ils sont présentés dans un ordre de priorité (valeur ajoutée moyenne sur les deux sessions, de la plus basse à la plus haute) pour que le rectorat puisse en retenir 10 ou 20. Les règles « une seule session, VA < 0 » et « une seule session, VA ≤ -5 » restent affichées à titre de comparaison.

## 4. Critères de succès

Chacun se vérifie par oui ou non le jour de la démonstration.

1. Une personne qui découvre l'outil obtient la liste des collèges prioritaires en moins de 2 minutes.
2. Chaque collège affiché montre son IPS, sa valeur ajoutée, la source et l'année des données.
3. Les collèges aux données manquantes sont signalés et comptés, pas masqués.

## 5. Métriques

| Indicateur | Définition | Unité | Maille | Période | Source |
| --- | --- | --- | --- | --- | --- |
| IPS du collège | Indice de position sociale moyen des élèves ; plus il est bas, plus les élèves sont d'origine défavorisée | Indice (sans unité) | Collège | Rentrées 2023-2024 et 2024-2025 (= sessions 2024 et 2025, D-005, D-007) | ips_colleges |
| Valeur ajoutée au brevet | Écart entre le taux de réussite constaté et le taux attendu pour le profil du collège | Points | Collège | Sessions 2024 et 2025 (D-007) | ivac_colleges |
| Taux de réussite au brevet | Part des candidats admis au diplôme national du brevet | % | Collège | Sessions 2024 et 2025 (D-007) | ivac_colleges |

## 6. Sources pressenties

| Jeu de données | Producteur | Lien | Licence | Date d'accès |
| --- | --- | --- | --- | --- |
| Indices de position sociale des collèges (à partir de 2023) | DEPP, ministère de l'Éducation nationale | https://www.data.gouv.fr/datasets/ips-colleges-a-partir-de-2023 | Licence Ouverte v2.0 (selon le producteur ; data.gouv.fr affiche « non spécifiée ») | 2026-11-13 |
| Indicateurs de valeur ajoutée des collèges (IVAC) | DEPP, ministère de l'Éducation nationale | https://www.data.gouv.fr/datasets/indicateurs-de-valeur-ajoutee-des-colleges | Licence Ouverte v2.0 | 2026-11-13 |

## 7. Hypothèses

- Les deux fichiers se joignent par l'identifiant de l'établissement (UAI) : vérifié, 859 lignes sur 882 trouvées dans les deux fichiers (D-008).
- « Défavorisé » = IPS inférieur à la médiane des collèges de l'académie (100,9 en 2024 et en 2025) ; « sous-performant » = valeur ajoutée négative aux deux sessions 2024 et 2025 : règle retenue en D-009.
- Les années des deux sources se recouvrent : deux sessions communes, 2024 et 2025 (D-007).

## 8. Hors-périmètre

- Ce que l'observatoire ne traitera pas : les collèges hors contrat, les autres académies, les lycées et les écoles.
- Ce qu'il ne permettra pas de conclure : pourquoi un collège réussit moins bien qu'attendu, ni si le dispositif d'accompagnement sera efficace. Le lien entre IPS et résultats est une corrélation, pas une cause.

## 9. Risques et éthique

- Biais possibles : petits collèges aux indicateurs instables ou absents (IPS non renseigné sous 5 élèves, valeur ajoutée non calculée sous 40 candidats) ; comparaisons public/privé et entre années à interpréter avec précaution.
- Données personnelles : aucune, données agrégées par établissement.
- Accessibilité : l'information ne doit jamais reposer sur la couleur seule ; contrastes suffisants.
- Usage détourné : la liste peut être lue comme un palmarès des « mauvais collèges » ; les écrans parlent de priorité d'accompagnement, pas de classement.

## 10. Questions ouvertes

- [ ] Quelle est l'échéance exacte de préparation de la rentrée 2027 ?
- [ ] Pourquoi 13 collèges de l'académie sont-ils absents du fichier IVAC (explication probable : moins de 20 élèves présents en série générale, fiche non publiée selon le guide IVAC 2025) ? À vérifier.

Questions tranchées en v1 :

- [x] Combien de collèges compte l'académie de Créteil dans les deux fichiers ? 441 collèges dans IPS, dont 428 (session 2024) et 431 (session 2025) présents aussi dans IVAC.
- [x] Quel seuil d'IPS et quel seuil de valeur ajoutée retenir ? IPS inférieur à la médiane de l'académie et valeur ajoutée négative (D-009).
- [x] Une seule année ou une moyenne sur plusieurs sessions ? Les deux sessions 2024 et 2025 : la difficulté doit être répétée (D-009).
- [x] Combien de collèges dans la liste finale ? 72 collèges éligibles, présentés dans un ordre de priorité ; le rectorat en retient 10 ou 20 (D-009).
- [x] Quelle licence pour chacune des deux sources ? Licence Ouverte v2.0 pour les deux (sources.yaml).
