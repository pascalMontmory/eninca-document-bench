# Démonstration documentaire locale

[English](../en/demo.md) · [Accueil](../../README.fr.md)

**© 2026 ENINCA CONSULTING — Tous droits réservés.** Le code original et la documentation propre au projet sont la propriété d’ENINCA CONSULTING. Les données DILA, le modèle MiniLM et les dépendances conservent leurs droits respectifs. Voir [LICENSE](../../LICENSE) et les [notices tierces](../../THIRD_PARTY_NOTICES.md).

## Lancer sur le Mac

Depuis une copie Git existante :

```bash
cd ~/Downloads/eninca-document-bench
git pull --ff-only
bash demo.sh
```

Un dossier provenant d’une archive ne contient pas de répertoire `.git` : télécharger et extraire la nouvelle archive à la place de `git pull`, en conservant `.venv`, `.models` et `runs`. Pour un nouveau dossier, cloner le dépôt public puis lancer `bash demo.sh`.

Python 3.11 ou plus récent est nécessaire. Le lanceur réutilise `.venv` et `.models/minilm`. S’ils manquent, il installe les dépendances et télécharge explicitement le modèle figé, environ 479 Mo. Pour réutiliser le modèle d’un autre dossier :

```bash
ENINCA_DOCUMENT_MODEL="$HOME/Downloads/eninca-documents/.models/minilm" bash demo.sh
```

Ouvrir **http://127.0.0.1:8765** si le navigateur ne s’ouvre pas automatiquement. Garder le Terminal ouvert. Un double-clic sur `demo.command` est aussi possible après installation. **Ctrl+C** arrête le serveur. Si le port est occupé : `bash demo.sh --port 8766`, puis utiliser l’adresse affichée.

La préparation encode 60 documents d’apprentissage, 80 de validation et 80 de test. L’interface indique l’étape en cours. L’encodage peut prendre plusieurs minutes selon la machine. Les lancements suivants chargent les index puis recalculent les centroïdes et la calibration sans réencoder les fiches. Le chargement suit le même chemin numérique que lors du premier lancement.

## Une présentation de cinq minutes

Préparer l’index avant le rendez-vous. Pour partir sans décision humaine, utiliser un état neuf : `bash demo.sh --state-dir runs/demo-presentation`. Ce nouvel état nécessite sa propre première indexation.

1. **Recherche, une minute.** Cliquer sur « Logement à louer » ou poser une question courte. Ouvrir un résultat : passage, texte intégral et source sont accessibles. Il s’agit de recherche dans des textes existants, pas d’une réponse rédigée par une IA. Le score est une similarité, pas une probabilité.
2. **Classement, deux minutes.** Ouvrir « Classer et vérifier », puis « Abstentions à examiner ». Lire un document, choisir un thème ou « Hors des quatre thèmes » et enregistrer. Montrer aussi qu’une proposition retenue automatiquement peut être corrigée. Une proposition automatique n’est jamais présentée comme une validation humaine.
3. **Bilan, une minute.** Montrer les décisions, les documents restant à examiner et les suggestions corrigées. Les résultats initiaux du modèle restent séparés : la revue humaine ne les améliore pas artificiellement.
4. **Export, une minute.** Télécharger le CSV : suggestion initiale, décision humaine, date et identifiant de configuration. Les 80 lignes sont exportées, y compris celles sans décision. Dans « Décisions enregistrées », une décision peut être modifiée ou remise à examiner.

L’interface peut passer en anglais ; les textes DILA restent en français. Les exemples ne constituent pas un test de qualité de recherche : la pertinence doit être évaluée sur des questions indépendantes avant toute promesse commerciale.

## Lire les compteurs

- **Recherche : 220 documents**, issus des trois partitions. Les étiquettes de référence ne servent pas à rechercher.
- **Revue : 80 documents de test.** L’apprentissage et la calibration utilisent uniquement leurs partitions respectives. Les corrections humaines ne les réentraînent pas.
- **À examiner** : sans avis humain enregistré, même si le modèle a accepté sa proposition. **Abstentions à examiner** : sous-ensemble où le modèle s’est abstenu.
- **Suggestions corrigées** : avis humain différent du premier thème suggéré, y compris « hors périmètre ». Ce compteur recoupe les décisions hors périmètre ; les quatre cartes ne s’additionnent pas.
- **Précision automatique** : propositions automatiques correctes selon les étiquettes publiques de référence, divisées par les propositions acceptées. Ce n’est ni la couverture ni la précision des avis humains. L’intervalle et les faux positifs hors périmètre sont affichés.
- **Temps** : préparation de la session, encodage initial conservé dans le cache, recherches de la session. Un chargement de cache n’est pas un nouvel encodage chronométré.

La configuration utilise quatre documents par lot, le tri par longueur et deux threads CPU. Ce choix issu du petit essai Mac n’est pas un optimum garanti. Les benchmarks historiques restent dans [les résultats](results.md) ; la démonstration recalcule ses résultats avec le modèle local.

## Fonctionnement et conservation

Le serveur écoute uniquement sur `127.0.0.1`. Aucun import de documents privés, envoi de données, télémétrie ou appel à une IA externe n’est exposé. Polices et scripts sont locaux. Les liens vers une source ou le dépôt ouvrent volontairement un site externe. Ce serveur de démonstration monoposte ne doit pas être exposé sur Internet.

`runs/browser-demo/indexes/` contient textes et embeddings ; `reviews.sqlite3` conserve chaque révision des décisions, y compris les remises à examiner. Ces fichiers sont exclus de Git. Les clés de cache incluent le modèle, le corpus, le code de la bibliothèque et les versions des dépendances. Une configuration de prédiction modifiée utilise un espace de décisions distinct sans appliquer silencieusement les anciennes corrections.

Les empreintes détectent une corruption accidentelle ; elles ne constituent ni signature ni preuve juridique. Si le cache est refusé, arrêter le serveur et renommer le sous-dossier `indexes` concerné pour le conserver avant reconstruction. Sauvegarder le dossier d’état pour conserver les décisions. Un second processus ne peut pas utiliser le même dossier. Des onglets concurrents ne peuvent pas écraser silencieusement une décision plus récente.

## Contrôles

```bash
ENINCA_DOCUMENT_MODEL=.models/minilm .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_records.py
```

Les nouveaux tests couvrent cache, persistance, conflits entre onglets, annulation, séparation des configurations, export et protections HTTP locales. Le contrôle navigateur facultatif utilise Playwright et Chromium déjà installés ; ils ne sont pas nécessaires à l’utilisation :

```bash
python demo/check_browser.py --url http://127.0.0.1:8765 --out runs/browser-check
```

Ce script vérifie recherche avec le vrai modèle, revue, export, deux langues et affichage mobile. Il ajoute puis annule une décision : utiliser un état séparé si l’on souhaite garder un historique sans ces événements. Le contrôle de redémarrage reste distinct. **Ces vérifications CPU ne démontrent aucun gain TPU/GPU ou industriel.** La CI GitHub reste désactivée.
