# Journal des décisions

Règle de preuve : toute décision importante se relie à une exigence, une source, un test, une mesure ou une validation identifiable. Les hypothèses restent marquées comme telles.

Une entrée par décision, la plus récente en haut. On ne supprime pas une entrée : on en ajoute une qui la remplace et on l'indique.

## Modèle

```
## D-XXX — [titre court]
- Date : AAAA-MM-JJ
- Auteur(s) : [nom]
- Contexte : [quel problème ou quelle question]
- Options envisagées : [A, B, C]
- Décision : [l'option retenue]
- Justification / preuve : [exigence, source, test, mesure ou validation ; lien ou chemin de fichier]
- Statut : hypothèse | validée | remplacée par D-YYY
```

---

## D-011 — Organisation et accessibilité du tableau de bord

- Date : 2026-11-14
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : 7 écrans demandés, avec des filtres communs, des sources visibles et des contrastes suffisants.
- Options envisagées : (A) une seule longue page ; (B) un écran par fichier, menu et filtres communs dans la barre latérale ; thème : (1) laisser le choix clair/sombre au navigateur ; (2) imposer le thème clair
- Décision : (B) et (2) ; calculs dans `src/observatoire/vues.py` (testés), affichage dans `app/` ; filtre « session » à une seule valeur, les écrans qui utilisent les deux sessions le disent
- Justification / preuve : contrastes calculés selon WCAG sur fond blanc (bleu #1F4E79 : 8,7:1 ; gris #595959 : 7,0:1 ; minimum demandé 4,5:1) ; un thème imposé permet de garantir ces contrastes ; tests `tests/test_app.py` et `tests/test_vues.py`.
- Statut : validée

## D-010 — Présentation de l'ordre de priorité

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : la liste est triée par VA moyenne pour permettre de retenir 10 ou 20 collèges, mais les VA sont des points entiers et 5 collèges ont la même VA moyenne (-9,5) autour de la 10e place.
- Options envisagées : (A) couper strictement à 10 ou 20 (égalités départagées par UAI) ; (B) quand le rectorat choisit « les N premiers », inclure tous les collèges à égalité avec le N-ième, et l'annoncer
- Décision : (B) ; le nombre de collèges ajoutés par égalité est annoncé à l'écran
- Justification / preuve : guide IVAC 2025 (écart de 2 points « trop faible pour en tirer des conclusions ») ; égalités mesurées sur `data/processed/liste_prioritaire.csv`. Vocabulaire : « ordre de priorité », jamais « rang » ni « classement ».
- Statut : validée

## D-009 — Règle de priorité d'accompagnement

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : définir « défavorisé » et « sous-performant » pour construire la liste prioritaire (question ouverte de la note de cadrage).
- Options envisagées : (A) IPS < médiane de l'académie et VA < 0, par session ; (B) IPS < médiane et VA ≤ -5 (≈ premier quartile), par session ; (C) IPS < médiane et VA < 0 aux deux sessions 2024 et 2025
- Décision : (C) pour la liste prioritaire ; liste triée par valeur ajoutée moyenne sur les deux sessions, de la plus basse à la plus haute, pour que le rectorat puisse retenir les 10 ou 20 premiers ; A et B restent visibles dans le tableau de bord à titre de comparaison, avec un sélecteur
- Justification / preuve : la VA est instable d'une année à l'autre (corrélation 0,53 entre 2024 et 2025 ; 116 collèges sur 410 changent de signe), donc une difficulté répétée est plus fiable ; guide IVAC 2025 : un écart de 2 points est « trop faible pour en tirer des conclusions ». Médiane IPS des collèges de l'académie = 100,9 (2024 et 2025), calculée sur toute l'académie et non sur la sélection filtrée. Effectifs : A = 121 (2024) / 96 (2025) ; B = 72 / 47 ; C = 72 collèges. IPS égal à la médiane → « haut » ; VA = 0 → « positive ou nulle » ; collège sans VA à l'une des deux sessions → non classable (31 collèges), montré à part.
- Statut : validée

## D-008 — Filtre académique par code et jointure qui conserve les collèges non appariés

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : filtrer Créteil, puis joindre IPS et IVAC sur (uai, annee).
- Options envisagées : filtre par libellé « CRETEIL » ou par code « 24 » ; jointure interne (on ne garde que les collèges présents des deux côtés) ou jointure complète avec une colonne de provenance
- Décision : filtre par code académie « 24 » (identique dans les deux fichiers, insensible à l'orthographe) ; jointure complète (outer) avec une colonne `presence` = « les_deux » / « ips_seul » / « ivac_seul »
- Justification / preuve : critère de succès n° 3 de la note de cadrage (« les collèges aux données manquantes sont signalés et comptés, pas masqués ») ; le nombre de collèges non appariés est publié dans le rapport qualité.
- Statut : validée

## D-007 — Années retenues : uniquement les années communes

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : IPS couvre les sessions 2024 à 2026, IVAC les sessions 2022 à 2025.
- Options envisagées : (A) années communes seulement ; (B) toutes les années, avec des trous
- Décision : (A) sessions 2024 et 2025
- Justification / preuve : la question croise IPS et valeur ajoutée, qui doivent être présents la même année.
- Statut : validée

## D-006 — Harmonisation du secteur

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : IPS code « public » / « privé sous contrat », IVAC code « PU » / « PR ».
- Options envisagées : (A) deux valeurs « public » / « privé » ; (B) garder les codes d'origine
- Décision : (A) ; toute valeur inconnue devient manquante et est signalée par un contrôle qualité
- Justification / preuve : valeurs observées le 2026-11-13 (seules ces 4 modalités existent) ; aucun collège de Créteil ne change de secteur entre les deux fichiers (367 public/PU, 64 privé/PR).
- Statut : validée

## D-005 — Correspondance entre session du brevet et année scolaire

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : IPS est daté par rentrée (« 2024-2025 »), IVAC par session du brevet (« 2025 »).
- Options envisagées : (A) session N ↔ année scolaire (N-1)-N ; (B) session N ↔ rentrée N-(N+1)
- Décision : (A) ; la colonne commune `annee` contient l'année de la session (ex. 2025 = rentrée 2024-2025)
- Justification / preuve : guide méthodologique IVAC 2025 (pièce jointe de la source ivac_colleges) : « élèves inscrits à la rentrée N-1 au brevet en juin N ».
- Statut : validée

## D-004 — Télécharger les fichiers nationaux et filtrer Créteil dans le code

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : l'API du producteur permet de filtrer à la source ; on peut aussi tout télécharger.
- Options envisagées : (A) télécharger seulement l'académie de Créteil via un filtre dans l'URL ; (B) télécharger les fichiers France entière et filtrer dans clean.py
- Décision : (B)
- Justification / preuve : le filtre est visible, testé et versionné dans le code ; les fichiers restent légers (~4 Mo chacun) ; on garde la possibilité de comparer à la France entière. Liens et empreintes dans `sources.yaml` et `data/raw/manifest.json`.
- Statut : validée

## D-003 — Versions des bibliothèques

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : requirements.txt ne fixait que des versions minimales ; reproductibilité du pipeline.
- Options envisagées : (A) garder les minimums ; (B) figer les versions exactes testées
- Décision : (B) versions figées dans `requirements.txt` : pandas==3.1.1, pyyaml==6.0.3, plotly==7.1.0, streamlit==1.67.0, pytest==9.2.0
- Justification / preuve : pipeline `--sample` et 10 tests passés le 2026-11-13 avec ces versions (Python 3.12.0).
- Statut : validée

## D-002 — Choix du périmètre : académie de Créteil

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : choisir le territoire étudié par l'observatoire.
- Options envisagées : Créteil, Lille, Aix-Marseille, La Réunion
- Décision : académie de Créteil
- Justification / preuve : trois départements contrastés (Seine-Saint-Denis, Val-de-Marne, Seine-et-Marne), zones urbaines et rurales, ce qui permet la comparaison exigée par le sujet. Nombre de collèges à mesurer au premier chargement.
- Statut : hypothèse (à confirmer en S2)

## D-001 — Choix de la problématique

- Date : 2026-11-13
- Auteur(s) : Mohamed Rayen Aissa
- Contexte : séance 1, atelier 1 ; plusieurs thèmes envisagés.
- Options envisagées : (A) Éducation : collèges défavorisés dont les résultats au brevet sont inférieurs à ceux attendus ; (B) Santé : communes où les plus de 75 ans ont le moins accès à un médecin généraliste ; (C) Mobilité : communes à équiper en priorité en bornes de recharge.
- Décision : option A, avec la question écrite dans `docs/note_cadrage.md`.
- Justification / preuve : passe les cinq critères (décideur, décision, vérifiabilité, faisabilité, prudence) ; sondage data.gouv.fr du 2026-11-13 : « Indices de position sociale des collèges (à partir de 2023) » et « Indicateurs de valeur ajoutée des collèges », DEPP, une ligne par collège. B écartée car trop proche de l'exemple du cours ; C écartée car sources non vérifiées et jointure par commune plus risquée.
- Statut : hypothèse (faisabilité à confirmer en S2)
