# Protocole d'évaluation

[English](../en/methodology.md) · [Accueil](../../README.fr.md)

## Qualité sur données publiques

L'instantané DILA a été récupéré le 22 octobre 2026. Le [manifeste](../../data/dila-v1/manifest.json) contient l'empreinte de l'archive amont, celles des XML, les dates de mise à jour individuelles, les URL d'attribution, étiquettes, familles de dossiers et affectations aux ensembles. Les XML sélectionnés sont inclus pour vérifier l'extraction sans dépendre de l'URL changeante `latest.zip`. Commande : `python scripts/verify_corpus.py`.

Seules les fiches pratiques de 500 à 12 000 caractères Unicode extraits sont admissibles. Ce filtre exclut les pages très courtes ou très longues ; il ne tronque pas les textes retenus. Le titre et le corps sont conservés. Navigation, métadonnées de thème, fil d'Ariane et listes de pages connexes sont exclus du texte encodé. Les espaces sont normalisés lors de la conversion XML-texte. La bibliothèque conserve ensuite ce texte et les positions Unicode des extraits.

Quatre thèmes sources sont les classes connues : argent/impôts/consommation (`N19803`), travail/formation (`N19806`), logement (`N19808`), social/santé (`N19811`). Papiers/citoyenneté (`N19810`) et transports (`N19812`) servent de thèmes inconnus. Ces étiquettes éditoriales permettent d'étudier un routage thématique ; elles ne constituent pas des annotations de factures ou contrats.

Les familles de dossiers sont affectées aux ensembles avant la sélection des fiches, dans un ordre SHA-256 déterministe. Aucune famille ne traverse les ensembles. Chaque thème connu fournit 15 fiches par ensemble ; chaque thème inconnu en fournit 10 pour la validation et 10 pour le test, aucune pour l'apprentissage. Une similarité de Jaccard d'au moins 0,70 sur les suites de cinq mots élimine les textes trop proches parmi les fiches retenues. Un recouvrement sémantique reste possible. Aucune sortie du modèle n'intervient dans cette sélection.

L'apprentissage consiste uniquement à calculer les centroïdes normalisés des classes à partir de 60 embeddings documentaires ; le transformer préentraîné n'est pas réentraîné. Chaque embedding documentaire est la moyenne normalisée des embeddings de ses fenêtres. Celles-ci se chevauchent de 16 tokens et contiennent au maximum 128 tokens, dont deux spéciaux. Un token présent dans plusieurs fenêtres contribue plusieurs fois.

Les seuils sont choisis sur les 80 documents de validation. La grille contient 39 scores minimaux entre 0 et 0,95 et 31 marges entre 0 et 0,30. Une politique admissible doit accepter au moins cinq documents avec une précision empirique de 90 % ; accepter un thème inconnu compte comme une erreur. On maximise d'abord la couverture des classes connues, puis la précision, puis les seuils les plus stricts. Sans politique admissible, tout part en revue. La politique est enregistrée avant l'encodage du test et n'est jamais réajustée sur ses résultats.

Le test final de 80 documents compare cette politique aux seuils initiaux non calibrés (score 0,4 ; marge 0,05). On publie les nombres d'acceptations et d'erreurs, la couverture et l'exactitude sur classes connues, ainsi que les fausses acceptations hors périmètre. La précision est indéfinie sans acceptation. Les intervalles de Wilson sont des approximations descriptives, pas une garantie ni une correction des corrélations entre fiches ou du choix des seuils. Répéter l'inférence n'augmente jamais l'effectif statistique.

## Mesures CPU

Révision du modèle et fichiers sont figés et vérifiés par SHA-256. Backend : `CPUExecutionProvider` ; deux threads intra-op, un thread inter-op, exécution ONNX séquentielle. Chaque rapport conserve les versions Python, NumPy, ONNX Runtime, Tokenizers, le CPU, l'OS et le nombre de processeurs logiques.

Les trois ensembles de qualité sont encodés une fois chacun. Le chronométrage utilise 48 documents répartis sur les longueurs en caractères de l'apprentissage et de la validation, sans document de test. Six configurations : lots de fenêtres de taille 4, 8 ou 16, dans l'ordre d'entrée ou groupés par longueur. Toutes sont préchauffées ; leur ordre de mesure est pseudo-aléatoire selon une séquence fixée, pour trois répétitions.

Chaque sortie chronométrée est comparée à la référence en ordre d'entrée avec lot de taille 4 : identité et ordre des fenêtres inchangés, embeddings dans `atol=rtol=3e-5`. Les comparaisons sont hors chronométrage. Les rapports conservent les durées de chaque appel synchrone, tokenisation/inférence/pooling, tokens/padding, extrema, médianes, documents/s et fenêtres/s. Chargement et vérification du modèle, lecture des fichiers, exports et comparaisons sont exclus de ces appels préchauffés. L'initialisation et les encodages de qualité sont rapportés séparément. Le pic mémoire du processus inclut les tableaux conservés et préchauffages ; ce n'est pas une mesure mémoire isolée par configuration.

Trois répétitions sur un VPS partagé constituent une exploration. La configuration la plus rapide n'a pas fait l'objet d'une campagne de confirmation indépendante. Ne pas extrapoler les documents/s sans considérer longueur, nombre de fenêtres, machine, concurrence et entrées-sorties. Le téléchargement et l'initialisation du modèle comptent pour les traitements ponctuels.

## Reproduire

```bash
python -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/eninca-documents fetch-model --model-dir .models/minilm
ENINCA_DOCUMENT_MODEL=.models/minilm .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python benchmarks/run_public.py --model-dir .models/minilm --out runs/public-check
.venv/bin/python scripts/check_records.py
```

`report.json` identifie code et données ; `calibration.json` conserve la politique et les identifiants de validation ; `quality.json` conserve chaque prédiction ; `timings.csv` contient les mesures brutes. Une modification du code exige un nouvel essai nommé ou un instantané historique explicite ; ne jamais modifier les mesures anciennes pour les présenter comme actuelles.

## Travail TPU restant

La recherche PRNG/Pallas concerne une autre charge de calcul. Elle ne démontre pas une accélération de l'inférence d'un transformer. Un portage devra conserver tokenisation, fenêtres, masques, pooling et poids du modèle, puis comparer embeddings, rangs et décisions avec des tolérances adaptées à la précision numérique. Établir d'abord une référence JAX ordinaire, profiler la chaîne complète, puis envisager des noyaux Pallas ciblés. Inclure transferts, compilation, débit, qualité et coût réel d'infrastructure. Les performances TPU exigent un essai sur TPU natif.
