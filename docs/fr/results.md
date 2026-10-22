# Résultats mesurés et limites

[English](../en/results.md) · [Méthode](methodology.md) · [Accueil](../../README.fr.md)

## Corpus public français — 22 octobre 2026

220 fiches DILA, 107 familles de dossiers, quatre thèmes connus et deux thèmes inconnus. Apprentissage : 60 documents. Validation : 80. Test final : **80**, dont 20 hors périmètre. Il s'agit d'un cas de routage sur données publiques, pas d'une évaluation client ou d'une tâche d'OCR.

| Résultat du test séparé | Seuils fixes initiaux | Seuils calibrés sur la validation |
|---|---:|---:|
| Décisions acceptées | 57 / 80 | 33 / 80 |
| Décisions acceptées correctes | 38 / 57 | 27 / 33 |
| Précision des décisions acceptées | 66,7 % | **81,8 %** |
| Documents envoyés en revue | 23 / 80 | **47 / 80** |
| Couverture des thèmes connus | 44 / 60 (73,3 %) | 30 / 60 (50,0 %) |
| Thèmes inconnus acceptés à tort | 13 / 20 (65,0 %) | **3 / 20 (15,0 %)** |
| Exactitude sur thèmes connus, abstentions comptées comme erreurs | 38 / 60 (63,3 %) | 27 / 60 (45,0 %) |

La politique choisie sur la validation utilise un score cosinus minimal d'environ **0,75** et une marge de **0,01**. Sa précision sur validation était de 27/30 = 90 %. **Cet objectif n'est pas atteint sur le test** : 27/33 = 81,8 %, avec un intervalle descriptif de Wilson à 95 % d'environ 65,6–91,4 %. L'intervalle des fausses acceptations hors périmètre est d'environ 5,2–36,0 %. Ces intervalles sur petits effectifs ne garantissent pas la production et ne corrigent pas la corrélation entre fiches d'un même dossier.

Le compromis est explicite : moins de thèmes inconnus acceptés à tort et une meilleure précision des décisions acceptées, mais davantage de revue et moins de documents connus correctement traités au total. Six des 33 décisions acceptées restent erronées. Ne pas présenter ce résultat comme un classement autonome ni réutiliser ces seuils comme valeurs universelles. Enrichir l'apprentissage et la validation métier dans un nouveau protocole évalué séparément.

Preuves brutes : [`report.json`](../../results/public-cpu-20261022/report.json), [`calibration.json`](../../results/public-cpu-20261022/calibration.json), [`quality.json`](../../results/public-cpu-20261022/quality.json), [`timings.csv`](../../results/public-cpu-20261022/timings.csv), [`run.log`](../../results/public-cpu-20261022/run.log). Toutes les prédictions sont conservées, y compris abstentions et erreurs. Les thèmes éditoriaux DILA peuvent se recouper ; il faut examiner les échecs.

## Traitement CPU par lots sur le corpus public

VPS AMD EPYC-Milan (Linux x86-64) et Mac (Darwin ARM64), deux threads d'inférence ONNX sur chaque machine. Les deux essais utilisent le même code, modèle figé, corpus et échantillon chronométré de **48 documents / 591 fenêtres**, répartis sur les longueurs de l'apprentissage et de la validation. Trois répétitions préchauffées par configuration ; initialisation et entrées-sorties fichiers exclues. Le rapport Mac indique `cpu_model: arm`, sans désignation précise de la puce Apple.

| Taille des lots de fenêtres | Ordre | Médiane VPS | Médiane Mac | Documents/s VPS | Documents/s Mac |
|---|---|---:|---:|---:|---:|
| 4 | Entrée | 22,661 s | 20,007 s | 2,118 | 2,399 |
| 4 | Groupé par longueur | 21,554 s | **18,958 s** | 2,227 | **2,532** |
| 8 | Entrée | 21,557 s | 19,736 s | 2,227 | 2,432 |
| 8 | Groupé par longueur | 20,672 s | 19,150 s | 2,322 | 2,507 |
| 16 | Entrée | 22,223 s | 19,929 s | 2,160 | 2,409 |
| 16 | Groupé par longueur | **20,461 s** | 19,372 s | **2,346** | 2,478 |

Les 18 sorties chronométrées de chaque machine respectent l'ordre des fenêtres et la tolérance des embeddings. Le pic mémoire du processus est d'environ **1 188 Mio sur le VPS** et **1 389 Mio sur le Mac**, modèle, tableaux conservés et préchauffages inclus ; ce sont des pics cumulés, pas des mesures isolées par configuration. Les textes longs diminuent fortement les documents/s par rapport au petit jeu fictif ; fenêtres/s et longueurs doivent accompagner les annonces de débit.

Sur le Mac, grouper les fenêtres par longueur avec des lots de 4 réduit la durée médiane de **5,24 %** par rapport aux lots de 4 non triés. La meilleure configuration observée est le lot de 4 trié sur Mac (31,174 fenêtres/s), contre le lot de 16 trié sur VPS (28,884 fenêtres/s) : **7,93 % de débit supplémentaire** en comparant le meilleur résultat observé de chaque machine. À configuration identique de lots de 4 triés, le débit Mac observé est supérieur de 13,69 %. Ces comparaisons sont distinctes et n'isolent pas l'effet de l'architecture : Python 3.13.5 contre 3.11.2, NumPy 2.5.4 contre 2.4.6, OS/matériel/charge différents. ONNX Runtime 1.31.0 et Tokenizers 0.23.3 sont identiques. Il n'y a ni campagne indépendante de confirmation des performances ni preuve d'économie en production.

## Qualité et provenance entre machines

L'archive Mac a été importée sans modification de ses octets et vérifiée contre les **12 empreintes sources enregistrées**, l'identité du modèle, le manifeste du corpus et les trois empreintes de sortie. Sur les 80 documents du test séparé, **les 80 décisions coïncident pour chacune des deux politiques**, y compris suggestions et abstentions. Les seuils de calibration et les indicateurs agrégés coïncident aussi. Cela confirme les mêmes décisions sur cet échantillon figé ; l'objectif de précision de 90 % sur validation reste non atteint au test (27/33 = 81,8 %).

Les scores cosinus diffèrent au maximum de **7,15 × 10⁻⁷** et les marges de **1,07 × 10⁻⁶**. Les résultats flottants ne sont donc pas identiques bit à bit. Les tableaux d'embeddings bruts n'ont pas été archivés : leur égalité entre machines n'est pas établie. L'archive importée contient quatre fichiers JSON/CSV, pas le journal terminal des tests.

Preuves Mac : [`report.json`](../../results/public-mac-20261022T110024Z/report.json), [`calibration.json`](../../results/public-mac-20261022T110024Z/calibration.json), [`quality.json`](../../results/public-mac-20261022T110024Z/quality.json), [`timings.csv`](../../results/public-mac-20261022T110024Z/timings.csv), [reçu d'import et empreinte d'archive](../../results/public-mac-20261022T110024Z/import.json). La [comparaison structurée](../../results/mac-vps-public-comparison-20261022.json) est recalculable hors ligne avec `python benchmarks/compare_cpu_records.py` ; elle compare les preuves archivées sans nouvelle inférence.

## Première petite démonstration fictive

| Observation | Mac ARM64 CPU | VPS x86-64 CPU |
|---|---:|---:|
| Documents / fenêtres chronométrés | 12 / 13 | 12 / 13 |
| Encodage médian dans l'ordre d'entrée | 0,315548 s | 0,374635 s |
| Encodage médian groupé par longueur | 0,252202 s | 0,291689 s |
| Documents/s après groupement | 47,58 | 41,14 |
| Recherche : rang 1 correct / requêtes | 7 / 8 | 7 / 8 |
| Recherche : rappel à 3 | 100 % | 100 % |
| Classement sur le jeu fictif initial | 8 / 8 | 8 / 8 |

Sources : [rapport Mac](../../results/historical/mac-smoke.json), [rapport VPS](../../results/historical/vps-smoke.json), [code figé de l'encodeur](../../evidence/encoder-v0.1.0). Trois répétitions temporelles, très petits jeux rédigés pour l'exemple. Les versions Python/NumPy et conditions matérielles différentes empêchent une comparaison contrôlée du seul effet de l'architecture. Aucune égalité des tableaux d'embeddings bruts entre machines n'est démontrée.

Le [test complémentaire](../../results/historical/challenge.json) a révélé un bail commercial classé à tort comme facture, et un document de thème connu envoyé en revue. Il obtenait 3/4 nouvelles requêtes correctes au premier rang, 7/8 classements connus corrects, et seulement 1/2 documents inconnus correctement rejeté. Ces échecs ont motivé la validation séparée et l'évaluation hors périmètre ; ils n'ont pas servi à régler la politique du corpus public.

## Portée des conclusions

Le fonctionnement sur CPU et des mesures reproductibles sont démontrés. Les tests natifs vérifient textes Unicode longs, padding, invariance à l'ordre des lots et refus des requêtes trop longues. Ils n'établissent pas un niveau de service industriel. Les débits du corpus public ne sont pas directement comparables à ceux des courts exemples fictifs : les textes longs nécessitent beaucoup plus de fenêtres.

Aucun gain mesuré d'encodeur TPU/GPU, d'OCR complet, de passage à des millions de documents, de coût cloud ou de conformité n'est revendiqué. Les attributions du modèle et des dépendances figurent dans les [notices tierces](../../THIRD_PARTY_NOTICES.md).
