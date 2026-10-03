# Tests frontend

```bash
cd frontend
npm install
npm test               # une passe
npm run test:watch     # en continu pendant le développement
npm run test:coverage
```

## Organisation

Les tests vivent à côté du code qu'ils couvrent, dans un dossier `__tests__/` :

| Fichier | Couvre |
|---|---|
| `utils/__tests__/documentStatus.spec.ts` | libellés et styles des statuts |
| `components/__tests__/markdown-sanitization.spec.ts` | assainissement XSS du rendu Markdown |
| `services/__tests__/api.spec.ts` | intercepteurs : injection du jeton, renouvellement sur 401, mutualisation |
| `stores/__tests__/auth.spec.ts` | cycle de vie de la session |

## Deux partis pris

**Les tests d'assainissement portent sur le DOM, pas sur la chaîne HTML.** Chercher « onload »
dans le texte de sortie échouerait sur une charge que `marked` a échappée en
`&lt;svg/onload=…&gt;` : la sous-chaîne est toujours là, mais c'est devenu du texte inerte. Ce
qui compte est l'absence d'élément exécutable, pas l'absence du mot.

**Les tests d'intercepteurs remplacent l'adaptateur d'axios, pas le module axios.** Les
intercepteurs s'exécutent donc réellement ; seul le transport est simulé. Mocker axios entier
ne testerait plus rien.
