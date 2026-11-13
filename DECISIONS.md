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
