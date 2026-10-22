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

VPS AMD EPYC-Milan, Linux x86-64, deux threads d'inférence ONNX. L'échantillon chronométré contient **48 documents / 591 fenêtres**, répartis sur les longueurs de l'apprentissage et de la validation. Trois répétitions préchauffées par configuration ; initialisation et entrées-sorties fichiers exclues.

| Taille des lots de fenêtres | Ordre | Durée médiane d'appel | Documents/s | Fenêtres/s |
|---|---|---:|---:|---:|
| 4 | Entrée | 22,661 s | 2,118 | 26,080 |
| 4 | Groupé par longueur | 21,554 s | 2,227 | 27,419 |
| 8 | Entrée | 21,557 s | 2,227 | 27,415 |
| 8 | Groupé par longueur | 20,672 s | 2,322 | 28,590 |
| 16 | Entrée | 22,223 s | 2,160 | 26,594 |
| 16 | Groupé par longueur | 20,461 s | 2,346 | 28,884 |

Les 18 sorties chronométrées respectent l'ordre des fenêtres et la tolérance des embeddings. Le pic mémoire du processus est d'environ **1 188 Mio**, modèle, tableaux conservés et préchauffages inclus. C'est une comparaison exploratoire de configurations, sans campagne de confirmation séparée ni preuve d'économie en production. Les textes longs diminuent fortement les documents/s par rapport au petit jeu fictif ; fenêtres/s et longueurs doivent accompagner les annonces de débit.

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
