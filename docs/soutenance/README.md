# Support de soutenance

`docs/Soutenance-HelpMeDraft.pptx` — 29 diapositives, notes de l'orateur remplies
(≈ 4 200 mots, soit environ 40 minutes avec les pauses et les diagrammes commentés).
`docs/Soutenance-HelpMeDraft.pdf` en est l'export, à garder comme secours le jour J.

Le contenu est repris du dossier projet : aucune affirmation du diaporama ne
contredit `docs/Dossier-projet-HelpMeDraft.pdf`. Les figures sont les fichiers
d'origine, pas des recopies.

## Régénérer

```sh
cd docs/soutenance
npm install pptxgenjs
NODE_PATH=$PWD/node_modules node build.js Soutenance-HelpMeDraft.pptx
```

Le script applique ensuite le thème via `apply_theme.js` de la compétence pptx ;
sans elle, retirer l'appel `applyTheme` en fin de fichier (les couleurs de thème
repassent alors sur la palette Office par défaut).
