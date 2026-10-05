# Rapport d'audit d'accessibilité — HelpMeDraft

> Livrable fonctionnel exigé par le [cahier des charges](./cahier-des-charges.md) : *« Rapport
> d'audit d'accessibilité et de sécurité »*.
> Critères de performance **CP 2** (« la règlementation en vigueur est respectée ») et **CP 5**
> (« comprendre les notions d'accessibilité des contenus pour les personnes en situation de
> handicap »).

| | |
|---|---|
| **Date** | 3 octobre 2026 — **contre-audit le 5 octobre 2026, voir §9** |
| **Référentiel** | **RGAA 4.1.2**, fondé sur WCAG 2.1 niveau AA |
| **Périmètre** | 16 écrans, zones publique, invité, authentifiée et administration |
| **Méthode** | axe-core piloté par Playwright sur l'application réellement démarrée, complété par des contrôles manuels sur le DOM |
| **Version auditée** | branche `claude/gracious-goldberg-0o31o8`, commit du 3 octobre 2026 |
| **Données brutes** | [`audits/accessibilite-2026-10-03.json`](./audits/accessibilite-2026-10-03.json), puis [`accessibilite-2026-10-05.json`](./audits/accessibilite-2026-10-05.json) |
| **Script de mesure** | [`audits/audit-accessibilite.mjs`](./audits/audit-accessibilite.mjs) |

> **Nature de cet audit.** Il est **automatisé et instrumenté**, pas manuel au sens du RGAA. Un
> audit RGAA officiel exige le passage des 106 critères par un auditeur, dont beaucoup ne sont
> pas automatisables : pertinence des alternatives textuelles, cohérence de l'ordre de lecture,
> restitution par un lecteur d'écran réel. Les outils automatiques détectent de l'ordre de
> **30 à 40 % des non-conformités**. Ce rapport établit donc un **plancher** : tout ce qu'il
> liste est non conforme, mais une page absente de la liste n'est pas conforme pour autant.

---

## 1 · Synthèse

**120 occurrences de non-conformité** réparties sur **3 règles**, sur l'ensemble des 16 écrans.

| Gravité | Règle | Occurrences | Écrans |
|---|---|---:|---:|
| 🔴 Critique | `label` — champ de formulaire sans étiquette | 1 | 1 |
| 🟠 Sérieux | `color-contrast` — contraste insuffisant | **117** | **16** |
| 🟠 Sérieux | `aria-input-field-name` — champ ARIA sans nom accessible | 2 | 2 |

À quoi s'ajoutent **5 non-conformités structurelles** que les outils automatiques ne signalent
pas, relevées par contrôle manuel (§4).

> **Le résultat tient en une phrase : 117 des 120 occurrences viennent d'une seule couleur.**
> Le orange d'accentuation `#E0533C` sur le fond crème `#F4F1EA` donne un rapport de **3,40:1**
> là où le niveau AA en exige **4,5:1** pour du texte courant. Changer cette valeur de palette
> règle 97 % du volume relevé.

### Répartition par écran

| Écran | | Occurrences |
|---|---|---:|
| E01 | Accueil | 15 |
| E07 | Confidentialité | 14 |
| E06 | CGU | 10 |
| E05 | Mentions légales | 9 |
| E12 | Tableau de bord | 9 |
| E13 | Mes documents | 8 |
| E15 | Éditeur de document | 7 |
| E09 | Inscription | 6 |
| E14 | Nouveau document | 6 |
| E16 | Back-office | 6 |
| E02 E03 E04 | Fonctionnalités, Tarifs, Modèles | 5 chacun |
| E08 E10 E11 | Connexion, Mot de passe oublié, Nouveau mot de passe | 5 chacun |

---

## 2 · Ce qui est déjà conforme

Il faut le dire, parce que ce sont des points souvent manqués et qu'ils sont acquis ici :

| Point | Critère RGAA | État |
|---|---|:---:|
| Langue de la page déclarée (`lang="fr"`) | 8.3 | ✅ sur les 16 écrans |
| Toutes les images portent un attribut `alt` | 1.1 | ✅ 0 image sans `alt` |
| Un seul `h1` par page | 9.1 | ✅ sur 14 écrans sur 15 contrôlés |
| Repères de structure `<nav>`, `<header>`, `<footer>` | 12.6 | ✅ |
| Repère `<main>` | 12.6 | ✅ sur 14 écrans sur 15 |
| Focus clavier visible | 10.7 | ✅ sur 11 écrans sur 15 |
| Navigation au clavier possible | 12.x | ✅ 24 à 25 éléments atteints par écran |

---

## 3 · Non-conformités détectées automatiquement

### 3.1 🟠 Contraste insuffisant — 117 occurrences, 16 écrans

**Critère RGAA 3.2** — *« Dans chaque page web, le contraste entre la couleur du texte et la
couleur de son arrière-plan est-il suffisamment élevé ? »* (WCAG 1.4.3, niveau AA)

**Mesures**

| Premier plan | Arrière-plan | Rapport mesuré | Seuil AA | Verdict |
|---|---|---:|---:|---|
| `#E0533C` orange d'accentuation | `#F4F1EA` crème | **3,40:1** | 4,5:1 | ❌ échec |
| `#E0533C` | `#FFFFFF` blanc | **3,84:1** | 4,5:1 | ❌ échec |
| `#111111` noir d'encre | `#F4F1EA` | 16,74:1 | 4,5:1 | ✅ |
| `#6B6B6B` gris | `#F4F1EA` | 4,72:1 | 4,5:1 | ✅ (de justesse) |

**Où** — le orange est employé pour les intitulés en petites capitales monospace, les numéros de
section, les liens de contact et l'indicateur « MODE ÉDITION ». Exemples relevés :

```html
<h3 class="font-mono text-xs uppercase tracking-[0.2em] font-bold text-[#E0533C]">   <!-- 18× -->
<span class="font-mono text-xs uppercase tracking-[0.2em] text-[#E0533C] font-bold"> <!-- 11× -->
<span class="font-mono text-sm text-[#E0533C]">01.</span>                            <!--  4× -->
<a href="mailto:contact@helpmedraft.fr" class="text-[#E0533C] underline">
```

> **Pourquoi c'est systématiquement en défaut.** Ces éléments sont en `text-xs`, soit 12 px. Le
> seuil de 3:1 réservé au « texte large » ne s'applique qu'à partir de 24 px, ou 18,7 px en gras.
> À 12 px, même en gras, c'est 4,5:1 qui s'impose. Le orange passerait sur un titre de 24 px ; il
> ne passe sur aucun des usages qui en sont faits dans l'application.

**Correctif recommandé** — assombrir la valeur de palette, en conservant la teinte :

| Candidat | Rapport sur `#F4F1EA` | |
|---|---:|---|
| `#C4341C` | **4,83:1** | ✅ marge confortable, écart visuel minime |
| `#B82E17` | 5,41:1 | ✅ plus sûr, teinte sensiblement plus sombre |
| `#AD2A14` | 5,97:1 | ✅ s'éloigne de l'identité visuelle |

**`#C4341C` est le meilleur compromis** : il passe le seuil avec de la marge tout en restant
proche du orange d'origine. La couleur étant écrite en dur dans les classes Tailwind de chaque
composant, le correctif suppose soit un remplacement global, soit — préférable — l'extraction
de la palette en variables CSS, ce qui évitera que le problème se reproduise.

> **Réserve.** Le orange reste acceptable **sur fond noir** (`#E0533C` sur `#111111` : 4,92:1).
> Les usages sur fond sombre n'ont pas besoin d'être modifiés.

### 3.2 🔴 Champ de formulaire sans étiquette — 1 occurrence

**Critère RGAA 11.1** — *« Chaque champ de formulaire a-t-il une étiquette ? »* (WCAG 4.1.2)

**Où** — back-office (E16), champ de modification du quota IA :

```html
<input type="number" min="1" max="1000" class="w-20 h-9 px-2 ...">
```

Aucun `<label>`, aucun `aria-label`. Un lecteur d'écran annonce « zone d'édition numérique »
sans dire de quoi il s'agit. Dans un tableau d'administration listant plusieurs comptes, c'est
inexploitable : rien ne relie le champ à la ligne, donc à l'utilisateur concerné.

**Correctif recommandé** — une étiquette accessible nommant le compte :

```html
<input type="number" min="1" max="1000"
       :aria-label="`Quota IA quotidien de ${utilisateur.email}`">
```

> C'est la seule non-conformité de gravité **critique** du rapport. Elle est aussi la plus
> rapide à corriger.

### 3.3 🟠 Zone d'édition sans nom accessible — 2 occurrences

**Critère RGAA 11.1 / 11.2** (WCAG 4.1.2)

**Où** — l'éditeur Markdown (CodeMirror), sur les écrans Nouveau document (E14) et Éditeur (E15).
Le composant produit un `<div contenteditable>` portant `role="textbox"` mais aucun nom
accessible.

**Pourquoi ça compte ici plus qu'ailleurs** — c'est la zone de travail principale de
l'application. Un utilisateur de lecteur d'écran y arrive sans savoir ce que c'est.

**Correctif recommandé** — passer les attributs à l'instanciation de CodeMirror :

```js
EditorView.contentAttributes.of({
  "aria-label": "Contenu du document, éditeur Markdown",
})
```

---

## 4 · Non-conformités relevées par contrôle manuel

Ces points échappent aux outils automatiques : un titre de page existe, donc axe ne dit rien,
même s'il est identique sur toutes les pages.

### 4.1 🟠 Titre de page identique sur les 16 écrans — ✅ corrigé le 05/10/2026

**Critère RGAA 8.6** — *« Pour chaque page web ayant un titre de page, ce titre est-il
pertinent ? »*

Les 16 écrans portent le même `<title>` : **« Help Me Draft »**.

Conséquences concrètes : un utilisateur de lecteur d'écran qui navigue entre onglets ne peut pas
les distinguer ; l'historique du navigateur devient illisible ; les favoris ne sont pas
identifiables.

**Correctif recommandé** — un titre par route, dérivé des métadonnées du routeur :

```ts
// index.ts, après chaque navigation
router.afterEach((to) => {
  document.title = to.meta.titre ? `${to.meta.titre} — HelpMeDraft` : "HelpMeDraft";
});
```

### 4.2 🟠 Aucun lien d'évitement — 0 écran sur 15 — ✅ corrigé le 05/10/2026

**Critère RGAA 12.7** — *« Dans chaque page web, un lien d'évitement ou d'accès rapide à la zone
de contenu principal est-il présent ? »*

Un utilisateur au clavier doit traverser toute la navigation avant d'atteindre le contenu, **sur
chaque page**. Les mesures montrent 24 à 25 éléments focalisables par écran, dont une large part
en en-tête.

**Correctif recommandé** — dans `App.vue`, en tout premier élément du `<body>` :

```html
<a href="#contenu" class="sr-only focus:not-sr-only focus:absolute focus:z-50 ...">
  Aller au contenu principal
</a>
```

avec `id="contenu"` sur le `<main>`.

### 4.3 🟠 Focus non visible — 22 éléments sur 4 écrans — ✅ corrigé le 05/10/2026

**Critère RGAA 10.7** — *« Pour chaque élément recevant le focus, la prise de focus est-elle
visible ? »*

| Écran | Éléments sans focus visible | Lesquels |
|---|---:|---|
| E04 Modèles | **16 sur 25** | les cartes de modèles (`<a>`) |
| E09 Inscription | 2 sur 25 | boutons « Afficher le mot de passe » et « Afficher la confirmation » |
| E11 Nouveau mot de passe | 2 sur 24 | idem |
| E08 Connexion | 1 sur 24 | bouton « Afficher le mot de passe » |
| E14 Nouveau document | 1 sur 25 | zone d'édition CodeMirror |

> **L'écran Modèles est le cas sérieux** : 16 des 25 éléments focalisables ne montrent aucune
> indication de focus. Un utilisateur au clavier y navigue à l'aveugle. La cause probable est un
> `outline-none` posé sur les cartes sans style de remplacement.

**Correctif recommandé** — ne jamais supprimer le contour sans le remplacer :

```css
:focus-visible { outline: 2px solid #111111; outline-offset: 2px; }
```

> **Ce que la correction a appris.** Les 22 éléments n'avaient pas une cause, mais deux, et la
> seconde est invisible à la lecture du code :
>
> 1. **Les cinq boutons « Afficher le mot de passe »** portaient un `focus:outline-none` **sans
>    style de remplacement**. Une règle globale ne les aurait pas sauvés : en Tailwind, un
>    sélecteur de classe l'emporte sur `:focus-visible`. Il a fallu retirer la classe.
> 2. **Les 16 cartes de l'écran Modèles** avaient bien un contour — `transition-all` le faisait
>    simplement **monter de 0 à 2 px en 150 ms**. La mesure, prise à l'instant du `Tab`, lisait
>    `outline-width: 0px`. Le contour existait donc, mais apparaissait en fondu, ce qui est un
>    vrai défaut pour qui navigue vite au clavier. Les transitions ont été restreintes aux
>    propriétés réellement animées (`transform`, `box-shadow`, `color`), et le script de mesure
>    attend désormais la fin des transitions avant de conclure.

### 4.4 🟡 Sauts de niveau de titre — 6 écrans — ✅ corrigé le 05/10/2026

**Critère RGAA 9.1** — *« Dans chaque page web, l'information est-elle structurée par
l'utilisation appropriée de titres ? »*

| Écran | Saut |
|---|---|
| E08, E09, E10, E11, E16 | `h1 → h3` sur « [ Navigation ] » (pied de page) |
| E04 Modèles | `h1 → h3` sur « Email professionnel » |

Le `h3` du pied de page est la cause de cinq des six cas : un seul correctif à cet endroit en
règle la majorité.

### 4.5 🟡 Deux repères manquants — ✅ corrigé le 05/10/2026

| Écran | Manque | Critère |
|---|---|---|
| E01 Accueil | pas de `<main>` | RGAA 12.6 |
| E14 Nouveau document | pas de `h1` | RGAA 9.1 |

---

## 5 · Anticipation du RGAA 5 (WCAG 2.2)

Le RGAA 5, attendu fin 2026, sera fondé sur **WCAG 2.2** et l'Arcom en deviendra l'autorité de
contrôle — voir le [journal de veille](./veille/journal-de-veille.md) §5. L'audit a été rejoué
avec les règles `wcag22aa` d'axe : **aucune violation détectée**, mais la couverture d'axe sur
WCAG 2.2 est partielle. Le critère **2.5.8 — taille de cible minimale** (24 × 24 px) a donc été
mesuré à la main.

**13 cibles interactives sous 24 px de haut**, toutes en hauteur (14 à 22 px), jamais en largeur :

| Élément | Dimensions | Écrans |
|---|---|---|
| `<a>` « contact@helpmedraft.fr » | 166 × **14** px | mentions légales, CGU |
| `<a>` « ← Retour à la connexion » | 179 × **14** px | mot de passe oublié, nouveau mot de passe |
| `<a>` « rgpd@helpmedraft.fr » | 145 × **14** px | confidentialité |
| `<a>` « Oublié ? », « Créer un compte », « Se connecter » | ~16 px de haut | connexion, inscription |
| `<a>` « ← Retour aux documents » | 172 × **16** px | éditeur |
| `<button>` « Admin » | 57 × **22** px | tableau de bord |
| `<input>` | 14 × **16** px | back-office |

> **Nuance à connaître.** WCAG 2.2 prévoit une exception pour les liens **en ligne dans un bloc
> de texte**. Plusieurs de ces liens en bénéficieraient. Mais les boutons et le champ du
> back-office, eux, n'y échappent pas.

**Correctif recommandé** — augmenter le remplissage vertical plutôt que la taille de police, pour
ne pas toucher à la mise en page : `py-2` sur ces liens porte la hauteur de cible à 28–32 px.

**✅ Corrigé le 05/10/2026**, avec une exception assumée et vérifiable. Dix cibles ont été
agrandies (`inline-block py-2`, ou `h-6 w-6 shrink-0` pour la case de consentement, dont les
classes annonçaient 24 px mais qui rétrécissait dans son conteneur `flex` : 20 × 24 px mesurés).
**Quatre liens de la politique de confidentialité restent sous 24 px** : ils sont au milieu d'une
phrase, et l'exception « lien en ligne dans un bloc de texte » de WCAG 2.5.8 s'y applique — les
rembourrer ferait chevaucher les lignes voisines. Le script de mesure les compte à part, sous
`ciblesEnLigneExemptees`, pour que l'exception reste visible et non oubliée.

Une onzième cible, absente de l'audit du 3 octobre, a été trouvée au contre-audit : le lien
« Créer votre premier document » de l'écran *Mes documents*, qui ne s'affiche que **si la liste
est vide** — le compte de test du premier audit avait des documents.

---

## 6 · Plan de correction priorisé

| # | Correctif | Occurrences levées | Effort | Critère |
|---|---|---:|---|---|
| 1 | Assombrir `#E0533C` en `#C4341C` | **117** | ~1 h | 3.2 |
| 2 | Étiquette sur le champ de quota du back-office | 1 | 5 min | 11.1 |
| 3 | `aria-label` sur la zone CodeMirror | 2 | 15 min | 11.1 |
| 4 | Titre de page par route | 16 écrans | ~30 min | 8.6 |
| 5 | Lien d'évitement dans `App.vue` | 16 écrans | ~20 min | 12.7 |
| 6 | Règle `:focus-visible` globale | 22 éléments | ~30 min | 10.7 |
| 7 | Corriger le `h3` du pied de page | 5 écrans | ~10 min | 9.1 |
| 8 | `<main>` sur l'accueil, `h1` sur Nouveau document | 2 écrans | ~10 min | 12.6, 9.1 |
| 9 | Remplissage vertical des petites cibles | 13 cibles | ~30 min | WCAG 2.2 · 2.5.8 |

**Les neuf correctifs sont faits.** Les trois premiers le 3 octobre, les six suivants le
5 octobre ; le §9 donne le résultat de la mesure qui le vérifie.

---

## 7 · Ce que cet audit ne couvre pas

À énoncer en soutenance plutôt qu'à laisser découvrir :

- **Restitution par lecteur d'écran réel** (NVDA, VoiceOver) — non testée. L'ordre de lecture et
  la pertinence des annonces ne se vérifient pas autrement.
- **Pertinence des alternatives textuelles** — toutes les images ont un `alt`, mais sa qualité
  n'est pas jugeable automatiquement.
- **Contraste des composants d'interface** (bordures, icônes, états de focus) — WCAG 1.4.11,
  partiellement couvert par axe.
- **Comportement au zoom à 200 %** et en orientation portrait — WCAG 1.4.4, 1.3.4.
- **Contenus animés et temporisés** — sans objet ici, l'application n'en comporte pas.
- **Déclaration d'accessibilité** — obligation légale distincte de la conformité technique, non
  rédigée à ce jour.

## 8 · Reproduire cet audit

L'audit est reproductible : application démarrée, puis axe-core piloté par Playwright sur chaque
écran, en deux contextes de navigation (anonyme pour les écrans publics et invité, authentifié
pour le reste), le compte étant promu administrateur en base pour atteindre le back-office.

Les scripts et les résultats bruts sont dans
[`audits/accessibilite-2026-10-03.json`](./audits/accessibilite-2026-10-03.json). Une fois la
conteneurisation faite (`KAN-15`), l'audit a vocation à être rejoué dans la CI pour détecter
toute régression d'accessibilité.

---

## 9 · Contre-audit du 5 octobre 2026

Les six correctifs restants du §6 ont été appliqués, puis **mesurés** : même méthode que l'audit
initial, même script, application réellement démarrée (backend Flask sur SQLite, frontend construit
et servi), connexion par l'interface et compte promu administrateur en base pour atteindre le
back-office.

| | |
|---|---|
| **Date** | 5 octobre 2026 |
| **Écrans** | 15 (E15, l'éditeur d'un document existant, partage son composant avec E14) |
| **Règles axe** | `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa` |
| **Données brutes** | [`audits/accessibilite-2026-10-05.json`](./audits/accessibilite-2026-10-05.json) |
| **Script** | [`audits/audit-accessibilite.mjs`](./audits/audit-accessibilite.mjs) |

### Résultat

| Contrôle | Avant (03/10) | Après (05/10) |
|---|---|---|
| Violations axe-core | 120 → 0 après le lot contraste | **0** sur 15 écrans |
| Titres de page distincts | 1 pour 16 écrans | **15 titres distincts sur 15** |
| Lien d'évitement | 0 écran sur 15 | **15 sur 15**, 235 × 40 px une fois focalisé |
| Repère `<main>` | 14 sur 15 | **15 sur 15** |
| `h1` unique | 14 sur 15 | **15 sur 15** |
| Sauts de niveau de titre | 6 écrans | **0** |
| Éléments sans focus visible | 22 sur 4 écrans | **0** |
| Cibles sous 24 px | 13 | **0**, plus 4 liens en ligne couverts par l'exception 2.5.8 |

### Comment les correctifs ont été posés

- **Titre de page** — `meta.titre` par route et un `router.afterEach` dans `index.ts`, plutôt
  qu'un appel dans chaque vue : une vue qui oublierait de le faire laisserait le titre de la page
  précédente, et l'oubli ne se verrait pas. L'interface `RouteMeta` de `vue-router` est augmentée,
  pour qu'une faute de frappe échoue à la compilation et non à l'exécution.
- **Lien d'évitement** — dans `App.vue`, premier élément focalisable du document, avec la cible
  `#contenu` posée **une seule fois** autour de `<router-view>`. Un `id` par vue aurait rendu le
  lien muet sur l'écran qui l'oublie, sans que rien ne le signale.
- **Focus visible** — règle `:focus-visible` globale dans `style.css`, **et** retrait des cinq
  `focus:outline-none` qui l'auraient emportée sur elle (§4.3).
- **Niveaux de titre** — les trois intitulés du pied de page passent en `h2` : ce sont des frères
  des sections de page, pas leurs enfants. Sur l'écran *Modèles*, le nom de catégorie devient un
  `h2`, ce qui rétablit le chaînage vers le `h3` des cartes.
- **Repères manquants** — la racine de l'accueil devient `<main>`, et l'intitulé de mode de
  l'éditeur (`[ Nouveau Brouillon ]`) devient le `h1` de l'écran : c'est bien le titre de la page.
- **Taille des cibles** — remplissage vertical, jamais de police agrandie, pour ne pas toucher à
  la mise en page (§5).

### Deux faux positifs du script, corrigés dans le script

Ils valent d'être notés : ils montrent que l'outil de mesure se vérifie comme le reste.

1. **Le lien d'évitement était compté comme une cible de 1 × 1 px.** C'est sa taille en `sr-only`,
   état dans lequel il n'est pas une cible. Le script écarte désormais les éléments masqués par
   `clip-path`, et mesure ce lien **à l'état focalisé** — où il fait 235 × 40 px.
2. **Les contours animés étaient lus avant la fin de leur transition** (§4.3). Le script attend
   maintenant 250 ms après chaque `Tab`, et remonte la chaîne des ascendants, parce qu'un contour
   peut être porté par un parent : c'est le cas de CodeMirror, qui focalise `.cm-content` et dessine
   le contour sur `.cm-editor`. L'« absence de focus » relevée sur l'écran *Nouveau document* au
   premier audit était cela, et non un défaut.

### Ce que ce contre-audit ne change pas

Les limites du §7 tiennent toujours : **0 violation automatisée ne vaut pas conformité RGAA**. La
restitution par un lecteur d'écran réel, la pertinence des alternatives textuelles, le zoom à
200 % et la déclaration d'accessibilité restent à faire, et aucun outil ne les remplacera.
