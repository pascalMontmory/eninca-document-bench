# Frozen evidence / Preuves figées

`encoder-v0.1.0/` contains the six exact source files used by the historical Mac/VPS demonstrations and the additional synthetic challenge. SHA-256 values in those reports are verified against this snapshot, not against subsequently extended source. `challenge-v0.1.0.py` is the exact historical challenge runner; it expects the original extraction layout and is retained for provenance, not as the current entry point. The new command is `benchmarks/run_public.py` from the repository root.

`encoder-v0.1.0/` contient les six fichiers sources exacts des démonstrations historiques Mac/VPS et du test fictif complémentaire. Les empreintes de ces rapports sont vérifiées contre cet instantané, pas contre du code enrichi ultérieurement. `challenge-v0.1.0.py` est le script historique exact ; il attend l'ancienne arborescence et sert à la provenance, pas de point d'entrée actuel. La nouvelle commande est `benchmarks/run_public.py` depuis la racine du dépôt.

The native CPU test log in `results/native-tests.log` covers the current library. CI checks core contracts without the large model by default; the three native tests require the explicit pinned model. Public-data benchmarking and test results do not constitute a commercial license or a deployment certification.

Le journal `results/native-tests.log` couvre la bibliothèque actuelle sur CPU natif. La CI contrôle par défaut les contrats sans le gros modèle ; les trois tests natifs exigent le modèle figé explicite. Les benchmarks et tests ne constituent ni une licence commerciale ni une certification de déploiement.
