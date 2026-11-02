# Support de soutenance

`docs/Soutenance-HelpMeDraft.pptx` — 30 diapositives, notes de l'orateur remplies
(≈ 4 500 mots, soit environ 40 minutes avec les pauses et les diagrammes commentés).
Chaque note s'ouvre sur son créneau cumulé ; la suite est continue et se referme
sur 40:00.
`docs/Soutenance-HelpMeDraft.pdf` en est l'export, à garder comme secours le jour J.

Le contenu est repris du dossier projet : aucune affirmation du diaporama ne
contredit `docs/Dossier-projet-HelpMeDraft.pdf`. Les figures sont les fichiers
d'origine, pas des recopies.

## Charte

Celle de l'application, relevée dans `frontend/src` : fond parchemin `#F4F1EA`,
surfaces `#FAF8F5`, noir plein `#111111` pour le texte et les bordures, accent
brique `#C4341C` — la teinte retenue après l'audit d'accessibilité du 03/10, qui
avait écarté `#E0533C` faute de contraste sur fond clair. `#E0533C` sert
uniquement sur les fonds noirs, où c'est lui qui passe le seuil de 4,5:1.

Le parti pris visuel suit celui du § 5.3 : bordures pleines, ombres portées dures
(`8px 8px 0 #111111`, reproduites par un rectangle noir décalé plutôt que par un
effet d'ombre, qui varie d'un lecteur à l'autre), aucun arrondi, surtitres en
capitales monospace encadrés. Titres en Georgia, corps en Calibri, monospace en
Courier New — ces deux dernières pour qu'aucune substitution de police ne décale
la mise en page sur un autre poste.

## Régénérer

```sh
cd docs/soutenance
npm install pptxgenjs
NODE_PATH=$PWD/node_modules node build.js Soutenance-HelpMeDraft.pptx
```

Le script applique ensuite le thème via `apply_theme.js` de la compétence pptx ;
sans elle, retirer l'appel `applyTheme` en fin de fichier (les couleurs de thème
repassent alors sur la palette Office par défaut).
