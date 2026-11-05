# Support de soutenance

`docs/Soutenance-HelpMeDraft.pptx` — 34 diapositives, notes de l'orateur remplies
(≈ 4 500 mots, soit environ 40 minutes avec les pauses et les diagrammes commentés).
Chaque note s'ouvre sur son créneau cumulé ; la suite est continue et se referme
sur 40:00.
Script oral télégraphique : [`script-oral.md`](./script-oral.md).
Fiches de révision : [`fiches-revision.md`](./fiches-revision.md) — 26 fiches, une par
temps fort, à réviser une fois le script connu.

`docs/Soutenance-HelpMeDraft.pdf` en est l'export, à garder comme secours le jour J.

Le contenu est repris du dossier projet : aucune affirmation du diaporama ne
contredit `docs/Dossier-projet-HelpMeDraft.pdf`. Les figures sont les fichiers
d'origine, pas des recopies.

La diapositive 19 présente les douze captures d'interfaces en vignettes. Elles
sont lues dans `docs/captures/vignettes/`, rognées PAR LE HAUT au rapport de la
case : un recadrage centré ferait disparaître l'en-tête des pages longues
(accueil, tableau de bord). Les régénérer après un changement de captures :

```sh
python3 -c "
from PIL import Image
import glob, os
RATIO, LARGE = 1.8667 / 1.45, 620
for f in sorted(glob.glob('docs/captures/C-*.png')):
    im = Image.open(f).convert('RGB')
    im = im.crop((0, 0, im.width, min(round(im.width / RATIO), im.height)))
    im = im.resize((LARGE, round(LARGE * im.height / im.width)), Image.LANCZOS)
    im.save('docs/captures/vignettes/' + os.path.basename(f), 'PNG', optimize=True)
"
```

Le modèle de données occupe deux diapositives, 14 et 15 : le modèle conceptuel
avec ses cardinalités, puis le modèle logique avec ses clés étrangères. Elles
affichent `docs/dossier/fig/mcd.png` et `mld.png` — remplacer ces deux fichiers
et relancer le build suffit à les mettre à jour.

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
npm install
NODE_PATH=$PWD/node_modules node build.js ../Soutenance-HelpMeDraft.pptx
```

La version de pptxgenjs est figée dans `package.json`, et `package-lock.json`
est versionné — pour la raison exposée en § 4 du dossier.

Export PDF de secours, à refaire après chaque build :

```sh
cd docs && soffice --headless --convert-to pdf --outdir . Soutenance-HelpMeDraft.pptx
```

Le script applique ensuite le thème via `apply_theme.js` de la compétence pptx ;
sans elle, retirer l'appel `applyTheme` en fin de fichier (les couleurs de thème
repassent alors sur la palette Office par défaut).

## Vidéo de démonstration

`demo-helpmedraft.mp4` — 1 min 57, 1440 × 900, sous-titres incrustés.
Onze séquences : accueil, connexion, tableau de bord, liste, éditeur et
enregistrement automatique, génération IA, traçabilité des passages générés,
quota (429), cloisonnement (404), back-office, clôture.

Ce n'est pas un montage : un Chromium réel est piloté sur l'application en
fonctionnement, et les sous-titres sont injectés dans la page, donc gravés
dans l'image. Les données sont celles de `database/jeu_essai.py`, les mêmes
qu'au § 10 du dossier.

**Le fichier versionné ici a été enregistré sans Ollama** — la machine
d'enregistrement n'en disposait pas. Le parcours applicatif est réel de bout en
bout (interface, API, contrôles, base, journalisation) ; seul le modèle de
langage est remplacé par un substitut qui rend une réponse écrite d'avance. La
vidéo le dit elle-même, au moment de la génération et sur la carte finale.

### Refaire la vidéo, avec un vrai modèle

Sur une machine disposant d'Ollama, le script détecte un moteur réel et retire
de lui-même les deux mentions.

```sh
cd backend && python database/jeu_essai.py --vider   # données reproductibles
python run.py                                         # port 5000
```

```sh
cd frontend && npm run dev                            # port 5173
```

```sh
ollama serve && ollama pull qwen2.5:3b                # port 11434
```

```sh
node docs/soutenance/enregistrer-demo.mjs docs/soutenance/demo
```

```sh
ffmpeg -i docs/soutenance/demo/demo-helpmedraft.webm -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p docs/soutenance/demo-helpmedraft.mp4
```

Variables reconnues : `DEMO_URL` (défaut `http://localhost:5173`), `DEMO_API`
(`http://localhost:5000`), `DEMO_MDP` (`JeuDEssai1`), `DEMO_DOC_AUTRUI` —
l'identifiant d'un document d'un AUTRE compte, pour que le 404 de la séquence
« cloisonnement » soit un vrai refus de propriété et non un identifiant
inexistant.

Une séquence qui échoue n'interrompt pas la captation : le script enregistre
une capture `echec-<n>-<etape>.png` dans le dossier de sortie et passe à la
suivante.

## Teaser d'ouverture

`pub-helpmedraft.mp4` — 20 s, 1600 × 900, muet.

À passer avant de prendre la parole, ou en boucle pendant l'installation. Huit
plans, coupes sèches : l'accroche de la page d'accueil, la connexion, le
tableau de bord, un brouillon écrit vite, la génération, la lettre obtenue, les
passages tracés, et la marque posée sur l'application assombrie.

Tout ce qu'on y voit est l'application réelle — aucun carton, aucune
reconstitution. Les quelques mots affichés en bas à gauche sont posés dans la
page même, à la charte de l'app.

`pub-20s.mjs` l'enregistre et le monte en une passe : captation d'un parcours
au rythme naturel, relevé des bornes de chaque plan, puis découpe et
accélération par ffmpeg pour tomber sur 20 s. Le tableau `MONTAGE` en fin de
fichier donne la durée visée de chaque plan — c'est là qu'on règle le rythme.

Mêmes prérequis que la vidéo de démonstration (backend, frontend, Ollama, jeu
d'essai chargé) :

```sh
node docs/soutenance/pub-20s.mjs
```

Enregistré ici sans Ollama, comme la démonstration : la génération affichée est
réelle côté application — appel, attente, flux, insertion — mais le texte vient
d'un substitut. À refaire sur une machine équipée avant de la diffuser hors
soutenance.
