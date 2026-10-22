# Browser demonstration / Démonstration navigateur

CPU functional checks performed locally on Linux x86-64, 22 October 2026.
24 unit/native tests passed; historical record hashes remained valid. Chromium
checked real-model search, source text, human decisions, CSV export, French and
English, mobile layout and rejection of long queries. A separate native server
restart restored all three cached indexes, identical predictions and a saved
decision. Test decisions were undone. This is not a Mac execution, hosted CI
run, retrieval-quality evaluation or accelerator performance result.

Contrôles fonctionnels CPU effectués localement sur Linux x86-64 le 22 octobre
2026. Les 24 tests unitaires/natifs passent ; les empreintes historiques restent
valides. Chromium a vérifié la recherche avec le vrai modèle, les textes sources,
les décisions humaines, le CSV, les deux langues, l’affichage mobile et le refus
des requêtes trop longues. Un redémarrage natif distinct a restauré les trois
index, les mêmes prédictions et une décision enregistrée. Les décisions de test
ont été annulées. Il ne s’agit ni d’une exécution Mac, ni d’une CI hébergée, ni
d’une évaluation de pertinence ou de performance sur accélérateur.

The original source from commit `0af7ae2` is frozen in `evidence/browser-demo-v1/` because the live demo has since gained a comparison screen. / Le code initial du commit `0af7ae2` est figé dans `evidence/browser-demo-v1/` ; la démonstration courante a depuis reçu un écran comparatif.

From the repository root / Depuis la racine du dépôt :

```bash
cd evidence/browser-demo-v1
sha256sum -c SHA256SUMS
# macOS:
shasum -a 256 -c SHA256SUMS
```

Browser screenshots and generated indexes remain in the local ignored `runs/`
directory. / Les captures navigateur et les index restent dans le dossier local
`runs/`, exclu de Git.

© 2026 ENINCA CONSULTING. Original code and project documentation / code
original et documentation du projet : all rights reserved / tous droits réservés.
