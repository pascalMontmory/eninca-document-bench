# Comparison UI verification / Vérification de l’interface comparative

Native Linux CPU service checked in Chromium, 22 October 2026. The 28 unit/native tests passed, including the pinned real model. / Service Linux CPU natif contrôlé dans Chromium, le 22 octobre 2026. Les 28 tests unitaires/natifs passent, avec le vrai modèle figé.

`comparison-browser.json`: first-tab results match raw medians; conditional cost arithmetic, CSV/ZIP downloads, French/English and mobile layout checked. Starting and cancelling an actual native run retained the prior completed result. / Les médianes affichées concordent avec le rapport ; calcul conditionnel du coût, téléchargements CSV/ZIP, français/anglais et mobile vérifiés. Le lancement puis l’arrêt d’un véritable essai conserve le résultat complet précédent.

`workflow-browser.json`: real-model search, original text, human review, export and undo still pass. Model metrics remain unchanged. The test decision was undone. / Recherche avec le vrai modèle, texte original, revue humaine, export et annulation toujours fonctionnels. Les métriques du modèle restent inchangées. La décision de test a été annulée.

These are functional checks, separate from both native timing campaigns. Screenshots remain in ignored local `runs/`. / Contrôles fonctionnels distincts des deux campagnes chronométrées. Les captures restent dans le dossier local `runs/`, exclu de Git.

From the repository root / Depuis la racine :

```bash
sha256sum -c results/performance-ui-20261022/SHA256SUMS
# macOS: shasum -a 256 -c results/performance-ui-20261022/SHA256SUMS
```

© 2026 ENINCA CONSULTING. Original code and project documentation: all rights reserved / code et documentation du projet : tous droits réservés. Third-party rights remain separate / droits tiers distincts.
