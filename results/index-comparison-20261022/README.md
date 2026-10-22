# Paired indexing comparison / Comparaison appariée d’indexation

Native CPU measurements on a shared Linux x86-64 VPS (AMD EPYC-Milan), 22 October 2026. / Mesures CPU natives sur un VPS Linux x86-64 partagé (AMD EPYC-Milan), le 22 octobre 2026.

48 public texts, 591 chunks, batch four, two ONNX threads, seven paired repetitions. Only length grouping changes. / 48 textes publics, 591 fenêtres, lots de quatre, deux threads ONNX, sept répétitions appariées. Seul le regroupement par longueur change.

**Inconclusive speed result / Gain de vitesse non confirmé.** Reference median: 20.767762 s; grouping median: 20.832523 s. Median paired ratio: 1.009614; descriptive bootstrap 95%: [0.958335, 1.055805]. All 80 classification decisions match; 33 accepted, 27 correct, 6 incorrect, 47 abstentions. No business or accelerator gain established. / Les 80 décisions concordent ; 33 acceptations dont 27 correctes et 6 incorrectes, 47 abstentions. Aucun gain métier ou sur accélérateur établi.

- `plan.json`: frozen configuration, input IDs/hashes, source hashes and pair order / configuration, données, code et ordre figés avant mesures.
- `timings.csv`: all 14 measured passes / les 14 passages chronométrés.
- `report.json`: results, provenance and limits / résultats, provenance et limites.
- `calibration.json`, `predictions.json`: validation policy and held-out decisions / calibration et décisions de test.
- `run.log`: original campaign output / sortie d’origine de la campagne.

Verify from repository root / Vérifier depuis la racine :

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.check_comparison_record results/index-comparison-20261022
```

[English protocol](../../docs/en/comparison.md) · [Protocole français](../../docs/fr/comparison.md).

© 2026 ENINCA CONSULTING. Original code/documentation: all rights reserved. / Code et documentation propres au projet : tous droits réservés. Third-party rights remain separate / droits tiers distincts.
