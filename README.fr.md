# ENINCA Document Bench

[English](README.md) · [Méthode](docs/fr/methodology.md) · [Résultats](docs/fr/results.md) · [Pilote](docs/fr/pilot.md)

Bibliothèque Python locale de recherche documentaire, de classement assisté et d'évaluation reproductible sur CPU. Développée par Pascal Montmory pour **ENINCA CONSULTING**.

L'objectif est de mesurer la qualité documentaire, la charge de revue humaine et le coût du traitement avant d'investir dans une accélération matérielle. C'est un prototype CPU fonctionnel et un kit d'évaluation ; ce n'est pas un système de gestion documentaire déployé.

## Ce qui fonctionne

- Recherche sémantique avec déduplication par document et extraits du texte original.
- Classement par centroïdes calculés sur des exemples étiquetés, avec décision explicite de revue humaine.
- Seuils d'abstention réglés sur un ensemble de validation séparé, comprenant des thèmes hors périmètre.
- Découpage des textes longs sans suppression silencieuse de leur fin.
- Corpus figé et attribué de **220 documents administratifs publics français**, issus de Service Public / DILA : 60 pour l'apprentissage, 80 pour la validation, 80 pour le test ; 107 familles de dossiers maintenues séparées entre ensembles.
- Mesures CPU par lots après préchauffage, embeddings contrôlés, CSV brut, empreintes du modèle/code/données et tests.

**Aucun OCR, encodeur TPU/GPU natif ou gain de coût en production n'est démontré.** Le modèle actuel utilise ONNX Runtime sur CPU. Le corpus public contient des fiches pratiques, pas des scans ni des courriers d'entreprise réels. Pallas/TPU constitue une évaluation future distincte, pas un backend disponible.

## Démarrer sur macOS ou Linux

Python 3.11 ou ultérieur est nécessaire. Le téléchargement du modèle représente environ 479 Mo ; prévoir aussi l'environnement Python. Seules l'installation des dépendances et la commande explicite de téléchargement du modèle nécessitent le réseau.

```bash
git clone https://github.com/pascalMontmory/eninca-document-bench.git
cd eninca-document-bench
bash run.sh
```

L'accès au dépôt privé nécessite une authentification GitHub et une autorisation. Le script installe la bibliothèque, télécharge et vérifie le modèle figé, exécute les tests puis le benchmark CPU public. Il crée `runs/<horodatage>-public-cpu/`. La campagne complète peut prendre plusieurs minutes selon la machine ; sa progression est affichée. **Aucun résultat n'est envoyé automatiquement.**

Pour réutiliser un cache : `ENINCA_DOCUMENT_MODEL=/chemin/du/modele bash run.sh`. Avec l'ancien kit Mac, ce cache se trouve habituellement dans `~/Downloads/eninca-documents/.models/minilm` ; vérifier son existence.

Pour la courte démonstration fictive après installation :

```bash
.venv/bin/eninca-documents demo --model-dir .models/minilm \
  --data-dir examples --out runs/demo --repetitions 3
```

Les chemins de sortie doivent être nouveaux ; les résultats existants ne sont pas écrasés.

## Tester ses propres textes

Format JSONL UTF-8 : un objet par ligne. Les étiquettes sont facultatives pour indexer ou classer de nouveaux documents, obligatoires pour l'apprentissage et la validation.

```json
{"id":"document-001","text":"Le texte complet extrait du document.","label":"facture"}
```

```bash
.venv/bin/eninca-documents index --model-dir .models/minilm \
  --input private-data/documents.jsonl --out runs/my-index
.venv/bin/eninca-documents search --model-dir .models/minilm \
  --index runs/my-index --query "Quelle facture doit être réglée ?"
```

Classement assisté avec validation séparée :

```bash
.venv/bin/python scripts/assisted_classify.py --model-dir .models/minilm \
  --training private-data/train.jsonl --validation private-data/validation.jsonl \
  --input private-data/new-documents.jsonl --out runs/classification
```

La validation doit comprendre des exemples étiquetés de thèmes absents de l'apprentissage. L'objectif par défaut est une précision empirique de 90 % parmi les décisions acceptées, avec au moins cinq acceptations. **Ce n'est pas une garantie** sur les nouveaux documents. Si aucun seuil ne satisfait l'objectif, tous les documents sont envoyés en revue. Les chevauchements de textes/identifiants sont refusés ; l'opérateur doit aussi séparer les familles, modèles de documents et doublons lors de la préparation des données privées.

## Preuves et limites

Consulter [les résultats mesurés et les échecs](docs/fr/results.md), [le protocole précis](docs/fr/methodology.md) et [le cadrage d'un petit pilote](docs/fr/pilot.md). Les essais historiques Mac ARM64 et VPS x86-64 sont conservés avec leur code figé. Les embeddings flottants sont contrôlés avec des tolérances numériques ; aucune identité bit à bit entre architectures n'est revendiquée.

L'encodeur est le modèle multilingue MiniLM existant, pas un nouveau modèle entraîné par ENINCA. La recherche cosinus exacte fonctionne en mémoire ; ce n'est pas une base vectorielle pour des millions de documents. Pour le classement, la moyenne des fenêtres chevauchantes peut diluer un thème local. Les scores cosinus et les marges ne sont pas des probabilités. Les exports d'index contiennent le texte intégral : les traiter comme confidentiels avec des documents privés.

La CI contrôle les contrats unitaires, la séparation des données et la cohérence des preuves. Les tests avec le vrai modèle sont disponibles par déclenchement manuel du workflow ; l'essai CPU local archivé les inclut. Aucun chiffre de performance issu de la CI n'est mis en avant.

## Droits

Le code d'intégration original a été développé pour ENINCA CONSULTING. L'accès ne vaut pas licence générale open source ou de production : voir [LICENSE](LICENSE). Le modèle, les dépendances et les données DILA conservent leurs propres droits et attributions : [notices tierces](THIRD_PARTY_NOTICES.md). Aucun document juridique privé n'est inclus.
