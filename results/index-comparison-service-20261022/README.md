# Native browser-launched comparison / Comparaison native lancée dans le navigateur

22 October 2026, same fixed protocol as [the CLI record](../index-comparison-20261022/), launched through the persistent VPS service. / Le 22 octobre 2026, même protocole figé que [le dossier CLI](../index-comparison-20261022/), lancé via le service persistant du VPS.

Service resource limits: CPU quota 200%, memory 2 GiB; two ONNX threads. Pre-existing cached indexes remain loaded. Shared host, without machine-wide isolation. / Limites du service : quota CPU 200 %, mémoire 2 Gio ; deux threads ONNX. Les index préexistants restent chargés. Hôte partagé, sans isolation globale.

**Inconclusive / Gain non confirmé.** Median complete indexing: 22.623653 s reference, 22.124513 s length grouping. Median paired ratio 0.998542, descriptive 95% interval [0.934596, 1.041346]; 3 of 7 pairs faster with grouping. All 80 decisions match; 6 incorrect acceptances remain. / Temps médians complets : 22,623653 s pour la référence, 22,124513 s pour le regroupement. Ratio apparié médian 0,998542, intervalle descriptif à 95 % [0,934596 ; 1,041346] ; 3 paires sur 7 plus rapides. Les 80 décisions concordent ; les 6 acceptations erronées restent présentes.

Do not pool this service run with the CLI run or choose the more favorable summary. A median of paired ratios and a ratio of medians differ. / Ne pas fusionner cet essai avec le CLI ni sélectionner le résumé le plus favorable. La médiane des ratios appariés diffère du ratio des médianes.

Verify / Vérifier :

```bash
PYTHONPATH=src .venv/bin/python -m benchmarks.check_comparison_record results/index-comparison-service-20261022
```

© 2026 ENINCA CONSULTING. Original code and project documentation: all rights reserved / code et documentation du projet : tous droits réservés. Third-party rights remain separate / droits tiers distincts.
