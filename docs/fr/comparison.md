# Comparer les performances documentaires

[English](../en/comparison.md) · [Accueil](../../README.fr.md) · [Preuves](../../results/index-comparison-20261022/)

L’écran « Comparer les performances » sert à décider si un changement technique mérite d’être adopté sur une charge donnée. Il affiche deux temps mesurés, le contrôle des sorties, les erreurs de classement et les fichiers permettant de refaire le calcul. Il ne compare pas encore notre bibliothèque à un logiciel métier externe.

## Résultat disponible

Essai du 22 octobre 2026, CPU x86-64 AMD EPYC-Milan sur VPS partagé, deux threads ONNX, MiniLM multilingue figé :

| Mesure | Ordre d’entrée | Regroupement par longueur |
|---|---:|---:|
| Temps médian d’indexation de 48 textes | 20,768 s | 20,833 s |
| Textes par seconde | 2,311 | 2,304 |
| Remplissage inutile des lots (padding) | 3,027 % | 0,215 % |

**Gain non confirmé sur cet essai.** Les sept paires donnent un ratio médian de 1,010 et un intervalle descriptif à 95 % de [0,958 ; 1,056], qui inclut 1. Cinq paires sont plus rapides avec regroupement. La réduction médiane appariée est de 0,95 %, mais sa variabilité ne permet pas de retenir une accélération. Le ratio des deux temps médians et la médiane des ratios appariés sont deux calculs distincts : leurs signes peuvent différer.

Les 80 décisions de classement concordent entre les deux configurations. Le modèle accepte 33 propositions, dont 27 correctes et **6 incorrectes**, et s’abstient sur 47 documents. La précision parmi les acceptations est de 81,8 % (intervalle de Wilson 95 % : 65,6–91,4 %). Trois des vingt documents hors périmètre sont acceptés à tort. Préserver ces décisions ne corrige pas les erreurs du modèle.

Ce résultat complète les observations antérieures sur Mac ; il ne les remplace pas. Le changement de machine, le périmètre chronométré et la variabilité empêchent d’en déduire un gain universel.

Une [seconde campagne via le service web](../../results/index-comparison-service-20261022/) est également terminée : 22,624 s pour la référence et 22,125 s avec regroupement ; ratio apparié médian 0,999, intervalle [0,935 ; 1,041], **gain toujours non confirmé**. Les 80 décisions concordent à nouveau. Le service impose un quota CPU de 200 % et une limite mémoire de 2 Gio. Ces deux campagnes restent séparées ; l’interface affiche la dernière terminée localement.

## Utiliser l’écran

Lancer `bash demo.sh`, puis ouvrir le premier onglet. Le dossier de preuves archivé s’affiche immédiatement une fois l’application prête. Il est identifié comme un essai archivé sur Linux x86-64, même si le navigateur tourne sur Mac.

« Lancer un nouvel essai » exécute réellement les deux versions sur l’hôte du serveur. Un navigateur Mac connecté au VPS mesure le VPS. Le bouton ne rejoue pas une animation de résultats. Prévoir plusieurs minutes : l’essai archivé a pris environ huit minutes, hors chargement initial du modèle. Les autres fonctions sont suspendues pendant la mesure pour éviter les inférences concurrentes de cette application ; les autres charges de l’hôte restent possibles.

L’arrêt prend effet entre deux passages d’inférence. Le dernier rapport complet reste disponible après un arrêt ou une erreur. Les nouveaux résultats restent dans le dossier d’état, sous `comparisons/`, et ne sont pas envoyés ailleurs. CSV et ZIP permettent d’examiner les mesures brutes.

Le champ de coût reste vide tant que l’opérateur ne saisit pas son tarif horaire. Le calcul est `temps médian / 48 × volume / 3600 × tarif horaire`. Il s’agit d’une extrapolation linéaire conditionnelle, sans coût de revue humaine, de migration, d’OCR ou de stockage distant. Une différence négative reste affichée comme telle. Ce calcul ne démontre pas une économie en production.

## Protocole

- Même modèle, découpage, textes, ressources et taille de lot de quatre. Seul le regroupement des fenêtres par longueur change ; les sorties sont remises dans l’ordre initial.
- 48 textes sélectionnés dans les partitions d’apprentissage et de validation, 591 fenêtres. Les identifiants, empreintes et ordres d’exécution sont écrits dans `plan.json` avant les mesures.
- Deux préchauffages complets, puis sept paires. Les ordres AB/BA alternent dans le plan avant un mélange déterministe. Aucun réglage n’est choisi à partir des temps obtenus.
- Temps mural synchrone de l’indexation : lecture JSONL, tokenisation, inférence CPU, pooling, validation et écriture tamponnée de l’index. Chargement du modèle, préchauffage, vérification des sorties et suppression des fichiers temporaires sont exclus. Pas de `fsync`, de réseau ni de stockage distant.
- Chaque sortie chronométrée est comparée à la référence : identifiants, textes, fenêtres et encodeur identiques ; vecteurs contrôlés avec `atol=rtol=3e-5`.
- Calibration sur 80 documents de validation, figée avant le test de 80 autres documents. Comparaison des décisions et comptage des erreurs dans les deux versions. La qualité de recherche et le temps de correction humaine restent non évalués.
- Intervalle descriptif obtenu par 10 000 rééchantillonnages des paires complètes. Sept répétitions sur les mêmes textes ne couvrent ni la variabilité des corpus métier ni toutes les dérives d’un hôte partagé. Les données ont déjà servi aux essais précédents.

Le maximum mémoire est celui de tout le processus, y compris les tableaux de référence et d’éventuels index chargés ; ce n’est pas une comparaison mémoire entre variantes. L’essai archivé a été lancé en CLI ; le service de démonstration peut avoir ses propres limites de ressources. Conserver le contexte d’exécution pour comparer des campagnes.

## Exécuter ou vérifier sans navigateur

Depuis la racine du dépôt après installation et téléchargement du modèle :

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --model-dir .models/minilm --out runs/comparison-new
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --verify results/index-comparison-20261022
PYTHONPATH=src .venv/bin/python -m benchmarks.check_comparison_record \
  results/index-comparison-20261022
```

Le dernier contrôle recalcule aussi les métriques de qualité à partir des prédictions et des étiquettes publiques, et vérifie le lien avec les sources. Les empreintes détectent une incohérence ; elles ne sont pas une signature externe.

Pour un lot local autorisé, fournir au moins 48 objets JSONL avec `id` unique et `text` non vide :

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.comparison \
  --model-dir .models/minilm --input private-data/documents.jsonl \
  --documents 48 --out runs/comparison-private
```

Ce mode contrôle les sorties et les temps, mais affiche **qualité métier non évaluée**. Le rapport contient les identifiants et empreintes ; le conserver dans le périmètre autorisé. Aucun import privé n’est exposé dans la démonstration web.

## Passer à une décision métier

Un pilote doit ajouter un lot représentatif, des réponses attendues indépendantes, le temps du processus actuel et le temps de revue humaine. Comparer à périmètre égal : extraction initiale, modèle, longueurs, ressources et stockage. Définir à l’avance les seuils acceptables de précision, de faux positifs, de latence et de coût. La conclusion peut être de conserver l’existant.

Aucun gain industriel, OCR, TPU ou GPU n’est établi ici.

© 2026 ENINCA CONSULTING — Tous droits réservés sur le code original et la documentation du projet. Droits tiers distincts.
