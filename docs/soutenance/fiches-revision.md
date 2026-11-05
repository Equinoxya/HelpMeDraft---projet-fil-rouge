# Fiches de révision — ce que je dois dire

Exposé de 40 min, 34 diapositives. Le détail est dans [`script-oral.md`](./script-oral.md) ;
ici, c'est la version à réviser : une fiche par temps fort, trois à cinq puces, et la
phrase à placer.

> **Méthode.** Apprends par cœur les deux fiches encadrées — l'ouverture et la clôture.
> Pour le reste, retiens **la phrase en gras** de chaque fiche : le reste se raconte tout
> seul autour. Ne récite pas les puces.

---

## ▣ Fiche 0 — Les chiffres

À réviser en dernier, cinq minutes avant d'entrer.

| | |
|---|---|
| Tests | **461** au vert — 403 backend, 58 frontend |
| Couverture | **95 %** backend (90 % avec `jeu_essai.py`) · **55 %** front |
| Base | **8** tables · **9** clés étrangères · **7** contraintes CHECK |
| API | **5** blueprints |
| Écrans | **11** écrans, **12** captures · **9** planches de maquettage |
| Quota | **20** requêtes / **24 h** · code **429** |
| Cloisonnement | **404**, jamais 403 |
| Jetons | access **15 min** · refresh **7 jours** |
| Éditeur | enregistrement **2,5 s** après la dernière frappe |
| Docker | image front **82,9 Mo** · **3** services · **3** travaux de CI |
| Veille | **8** entrées, **3** actions · CVE **9,1** Ollama / **5,1** DOMPurify |
| Dates | AI Act **2 août 2026** · pile validée **5 octobre** |
| Projet | **13** lots · itérations d'**1 semaine** |

---

## ▣ Fiche 1 — L'ouverture *(à savoir mot à mot)*

> Bonjour, je m'appelle Ophélie Bellissens, je suis candidate au titre Concepteur
> Développeur d'Applications.
>
> Je vais vous présenter **HelpMeDraft**, une application web de rédaction assistée par IA
> que j'ai **conçue et développée seule**, du cahier des charges au déploiement, pour un
> commanditaire fictif : LexiCorp.
>
> Je vous propose quarante minutes, et je garde les questions pour la fin.

Puis le déroulé : **six temps**. « Je commence par le besoin, parce que toutes les
décisions techniques qui suivent en découlent. »

---

## Temps 1 — Le contexte et le besoin `1:00 → 4:10`

### Fiche 2 · Le besoin
- LexiCorp sait **classer** les documents, pas **aider à les écrire**.
- Dans une PME, les écrits courants sont rédigés par des gens dont ce n'est pas le métier.
- Quatre objectifs au cahier des charges.
- **« Retenez le quatrième : sécurité, accessibilité et confidentialité sont dans les objectifs, pas en fin de projet. »**

### Fiche 3 · Le périmètre
- **Trois commandes IA, et trois seulement** : reformuler, corriger, compléter.
- C'est toujours l'utilisateur qui insère ou remplace.
- La ligne qui a tout pesé : *« aucune donnée personnelle transmise sans anonymisation »*.
- **« Sur des textes libres, l'anonymisation n'est jamais exhaustive. »** → point de départ de l'inférence locale.
- Hors périmètre assumé. **« Un périmètre qu'on ne borne pas est un périmètre qui dérive. »**
- AI Act applicable le **2 août 2026**, après le cahier des charges. C'est la veille qui l'a remonté.

---

## Temps 2 — La gestion de projet `4:10 → 8:35`

### Fiche 4 · La méthode
- Itérations d'une semaine, chacune close par un lot utilisable de bout en bout.
- **« Des lots verticaux — front, API, base — plutôt que des couches horizontales. »**
- Horizontal : on ne valide rien avant l'assemblage. Vertical : chaque fin d'itération est démontrable.
- `package-lock.json` commité : **pas de l'organisation, une mesure de sécurité** (cf. axios).

### Fiche 5 · Les trois arbitrages
1. **Un JWT seul ne se révoque pas** → table `user_session` + rotation. Jeton rejoué = vol → tout tombe.
2. **Le quota par agrégation**, pas par compteur. Un compteur se désynchronise, une agrégation non.
3. **La confidentialité** → modèle en local. **« L'exigence est satisfaite par construction. »**
- Le fil : **les trois tiennent une exigence par la structure du code, pas par une vérification ajoutée.**

---

## Temps 3 — La conception `8:35 → 20:30`

### Fiche 6 · La pile technique
- **Sur sept domaines, six sont conformes** à la recommandation du cahier des charges.
- Deux lignes sont des **choix dans une alternative ouverte** : « MySQL ou MongoDB », « OpenAI ou local ».
- **« Choisir dans une alternative, ce n'est pas s'écarter. »**
- **Un seul vrai écart : le front.** Deux ajouts : CodeMirror 6 et DOMPurify.

### Fiche 7 · Les trois choix de techno
- **Vue 3 / React** — il recommande, il n'impose pas. Maîtrise = moins de risque en solo. Transposable.
- **Ollama / OpenAI** — les deux autorisés, **c'est le RGPD qui tranche**. `ia_service` isole l'appel.
- **MySQL / MongoDB** — schéma stable, données reliées. **`ON DELETE CASCADE` met en œuvre le droit à l'effacement en une instruction.**
- Sur le NoSQL : **« ce serait facile, et c'est précisément ce qui rend l'ajout suspect. »**

### Fiche 8 · L'architecture
- **« Le navigateur ne parle jamais au moteur d'inférence. »**
- Sinon : on contourne le quota en appelant le port 11434 soi-même.
- **« L'intermédiaire n'est pas une commodité : il rend les contraintes opposables. »**

### Fiche 9 · Les couches
- **« Aucun import Flask dans `services/`. »** Pas esthétique — fonctionnel.
- C'est elle qui rend le métier testable **sans serveur ni base**. **Socle du plan de tests.**
- Honnêteté : `current_app` pour la configuration, **seul point où la règle fléchit** (§ 7.2).
- Front : **aucune vue n'appelle axios** → l'intercepteur 401 est écrit une seule fois.

### Fiche 10 · Les écrans et le routeur
- Neuf planches de maquettage, une intention par écran, **avant d'écrire une ligne de Vue**.
- Seize routes, trois gardes : `guestOnly`, `requiresAuth`, `requiresAdmin`.
- **« Je le précise tout de suite parce que c'est la question qu'on pose : ces gardes sont du confort d'usage. »**
- **Le contrôle qui compte est côté serveur.**

### Fiche 11 · Le modèle de données
- **Huit entités, neuf associations.**
- **UUID v4** → les identifiants ne sont pas énumérables.
- **Cascades au niveau du SGBD** : *« une contrainte qui n'existe que dans le code applicatif n'est pas une contrainte. »*
- **La table `ia` sert trois choses** : historique, quota, traçabilité. **La même donnée rend les trois possibles.**
- MLD : **toutes les clés étrangères convergent vers `user`** — le cloisonnement écrit dans le schéma.

### Fiche 12 · La séquence IA
- **« Suivez l'ordre des contrôles, il n'est pas arbitraire. »** Auth → propriété → validation → quota → **puis** le modèle.
- **« Chaque contrôle est placé avant celui qui coûte plus cher. »**
- Ollama muet → message lisible, **et aucune ligne écrite** (sinon un échec consommerait du quota).
- **« La décision finale reste à l'utilisateur. »** Ergonomie **et** sécurité.

---

## Temps 4 — La réalisation `20:30 → 27:55`

### Fiche 13 · Les écrans livrés
- Onze écrans, douze captures. Ligne 1 = zone publique, ligne 2 = authentifié + back-office.
- **« C'est le découpage que je vous ai montré sur les gardes du routeur. »**

### Fiche 14 · L'enregistrement automatique
- 2,5 s : à chaque caractère → API saturée ; trop long → travail perdu.
- **Le minuteur précédent est systématiquement annulé.**
- **« Une capture atteste d'un état, pas d'un comportement. »** → raison d'être du jeu d'essai.

### Fiche 15 · Le quota
- **Agrégation**, pas compteur — un échec entre l'appel et l'incrément suffit à désynchroniser.
- **Fenêtre glissante**, pas jour calendaire : sinon **40 appels entre 23 h et 1 h**.
- **429, pas 403** : « réessayez plus tard » ≠ « vous n'avez pas le droit ».

### Fiche 16 · La propriété
- **« La propriété est dans la clause WHERE. »** Le motif le plus répété du projet.
- Contrôle a posteriori : un `if` oublié ouvre une faille. Ici, **oublier la condition fait échouer le test**.
- **404, pas 403** : un 403 confirmerait que la ressource existe.

### Fiche 17 · Docker et CI
- **« La pile a été exécutée. Pas seulement décrite — jouée »**, le 5 octobre sur un démon réel.
- Sonde de santé, Gunicorn non privilégié, image front 82,9 Mo.
- Secrets en `${VAR:?}` → **échoue plutôt que de démarrer avec une valeur inventée**.
- CI en trois travaux **parallèles** : enchaînés, un échec du front masquait l'état du back.
- **« Prête à être hébergée le jour où on lui donne un domaine. »**

---

## Temps 5 — La sécurité `27:55 → 32:20`

### Fiche 18 · La méthode
- Grille **OWASP Top 10 2021** + cahier des charges + ANSSI.
- **« Pas traitée en fin de projet — et pas par vertu, par nécessité pratique. »**
- WHERE, empreintes, refus de démarrer : **des choix de structure**. Les ajouter après aurait demandé de réécrire.
- **A05** : *« une clé de secours en dur est une clé en production. »*
- **A09, la faiblesse** : journalisation des événements de sécurité incomplète. **Dis-le toi-même.**

### Fiche 19 · Les deux jetons
- Court = sûr mais pénible ; long = confortable mais dangereux. **La combinaison donne les deux.**
- **Je ne stocke pas le jeton, je stocke son empreinte SHA-256.**
- Jeton consommé qui revient → vieille requête **ou** vol. **Dans le doute, je révoque tout.**
- **« La gêne est une reconnexion, le risque évité est un compte compromis. »**
- Le point qu'on oublie : **à la réinitialisation, toutes les sessions sont supprimées.**
- Purge : filtre sur **l'expiration**, pas sur la révocation — sinon la détection de rejeu tombe.

---

## Temps 6 — Tests, veille, clôture `32:20 → 40:00`

### Fiche 20 · Les tests
- **461 au vert.** 95 % backend — **et précise : hors `jeu_essai.py`, 90 % en l'incluant.**
- **« Viser un pourcentage global pousse à écrire des tests faciles sur du code sans risque. »**
- 55 % front : six enveloppes d'une ligne autour d'axios — **les tester reviendrait à tester axios**.
- Trois zones d'effort : authentification, propriété, quota.
- Campagne système jouée le 5 octobre : **7 au vert sur 10**.

### Fiche 21 · Le jeu d'essai
- Choisi parce qu'il traverse les trois couches, concentre cinq contrôles, porte quota **et** traçabilité.
- **« La seule fonctionnalité qu'aucune capture ne peut attester. »**
- **La ligne datée de 25 heures** : seul moyen de distinguer une fenêtre glissante d'un compteur journalier.
- **« Un jeu de données, c'est choisir les valeurs qui font échouer les mauvaises implémentations. »**

### Fiche 22 · La veille
- Trois périmètres. **« Une alerte sur une bibliothèque absente du projet n'est pas une information. »**
- **« La sévérité publiée ne prédit pas l'impact réel »** : 9,1 Ollama atténuée, 5,1 DOMPurify subie.
- DOMPurify : la bibliothèque **ajoutée pour corriger le XSS** portait sa propre faille.
- → **« Une mesure de sécurité est un composant comme un autre. »** D'où le Markdown brut stocké.
- Ollama : **héberger soi-même, c'est maintenir soi-même.**
- AI Act : **sans cette veille, j'aurais livré une application non conforme.**

---

## ▣ Fiche 23 — La clôture *(à savoir mot à mot)*

> Pour conclure, **je reprends les quatre objectifs du cahier des charges, dans les termes
> mêmes de l'ouverture**, et je dis pour chacun ce qui le tient.

| Objectif | Ce qui le tient |
|---|---|
| Rédiger et stocker | Éditeur Markdown, CRUD, dossiers, enregistrement automatique |
| Suggérer et reformuler | Trois commandes, quota 20/24 h, chaque appel journalisé |
| Un espace sécurisé | Deux jetons, sessions révocables, cloisonnement par compte |
| Se conformer | RGPD par l'architecture, RGAA 0 violation, AI Act tracé en base |

Puis les six mesures : **WHERE/404 · rôle relu en base · bcrypt + SHA-256 · refus sans clé ·
refresh httpOnly et rejeu = révocation · Markdown brut.**

> Je vous remercie, je suis à votre disposition pour vos questions.

---

## ▣ Fiche 24 — Les quatre « je ne le cache pas »

À sortir **toi-même**, jamais à laisser venir.

1. **Pas encore mise en ligne.** La pile tourne en conteneurs ; il manque un domaine et des valeurs de configuration.
2. **A09** — la journalisation des événements de sécurité est incomplète.
3. **`current_app` dans `services/`** — seul point où la règle d'architecture fléchit.
4. **Les 95 % de couverture excluent `jeu_essai.py`** ; 90 % en l'incluant.

Et si on te pousse sur le NoSQL : **« je l'assume, et le jury est libre de considérer le
critère comme non couvert. »**

---

## ▣ Fiche 26 — À quoi sert chaque brique

Pour la question « pourquoi avoir utilisé ça ? ». Une ligne par outil : **ce que
c'est**, **ce qu'il fait chez toi**, et la phrase qui justifie sa présence.

> **La règle qui répond à tout** : *« je ne l'ai pas ajouté parce que ça existe,
> je l'ai ajouté parce que sans lui j'aurais dû l'écrire moi-même — et moins
> bien. »* Si on te demande pour une bibliothèque que tu ne saurais pas
> défendre, c'est qu'elle n'a rien à faire là.

### Les deux langages

| | |
|---|---|
| **TypeScript** 6 | JavaScript **plus les types**. Le navigateur ne comprend que JavaScript : TypeScript est vérifié à la compilation, puis effacé. **Chez moi** : tout le front. **Pourquoi** — une faute de frappe sur un champ (`titre` / `title`) devient une erreur avant l'exécution, au lieu d'un `undefined` affiché à l'utilisateur. Sur un projet mené seule, c'est le relecteur que je n'avais pas. |
| **Python** 3.13 | Le langage du back. **Pourquoi** — recommandé par le cahier des charges, et c'est l'écosystème où SQLAlchemy, bcrypt et PyJWT sont les références. |

Et les trois autres langages du projet, qu'on oublie de citer : **SQL** (le schéma
et les requêtes), **HTML/CSS** (les gabarits Vue et Tailwind), **Markdown** (le
format de stockage des documents).

### Le front

| Outil | Ce que c'est | Ce qu'il fait chez moi |
|---|---|---|
| **Vue 3** | Framework de composants | Les 15 vues et les composants `MarkdownEditor`, `Nav`, `Footer`. L'interface se redessine quand la donnée change, sans que je touche au DOM. |
| **Vite** | Serveur de développement et empaqueteur | Recharge l'écran à chaque sauvegarde, et produit le paquet optimisé servi par Nginx. Il porte aussi le **proxy `/api`** vers le back. |
| **Vue Router** | Routeur de la SPA | Les 16 routes et les **trois gardes** (`guestOnly`, `requiresAuth`, `requiresAdmin`). |
| **Pinia** | Magasin d'état | Tient la session en mémoire — **l'access token n'est jamais dans `localStorage`**, et c'est voulu : une faille XSS ne peut pas le lire. |
| **axios** | Client HTTP | Les appels à l'API. Son **intercepteur** rafraîchit le jeton après un 401 et rejoue la requête — écrit une seule fois pour toute l'application. |
| **Tailwind CSS 4** | Styles par classes utilitaires | La charte. **Pourquoi** — pas de fichier CSS qui grossit sans qu'on sache ce qui sert encore ; le style est là où il s'applique. Recommandé par le cahier des charges. |
| **CodeMirror 6** | Composant d'édition de texte | L'éditeur Markdown : coloration, raccourcis, annulation. **Pourquoi** — un `<textarea>` n'a rien de tout ça, et le réécrire aurait été plusieurs semaines pour un résultat inférieur. |
| **marked** | Markdown → HTML | Produit l'aperçu à droite de l'éditeur, et le HTML envoyé au moteur PDF. |
| **DOMPurify** | Nettoyeur de HTML | **Le point de sécurité du front.** L'aperçu est le seul `v-html` du projet : il affiche du HTML fabriqué à partir du texte de l'utilisateur. DOMPurify en retire tout ce qui peut s'exécuter. **17 tests de non-régression.** |

### Le back

| Outil | Ce que c'est | Ce qu'il fait chez moi |
|---|---|---|
| **Flask 3** | Micro-framework web | Les 5 blueprints et les routes de l'API. **Pourquoi** — recommandé, et **micro** : il n'impose ni structure ni ORM, ce qui m'a laissée découper en trois couches comme je le voulais. |
| **SQLAlchemy 2** | ORM | Les 8 modèles, les relations, et **toutes les requêtes paramétrées**. **Pourquoi** — c'est lui qui rend l'injection SQL impossible par construction, et qui permet de développer sur SQLite en visant MySQL. |
| **bcrypt** | Fonction de hachage à coût réglable | Les mots de passe. **Pourquoi pas SHA-256** — SHA-256 est *rapide*, donc facile à attaquer par force brute. bcrypt est **lent exprès** et sale chaque empreinte. |
| **PyJWT** | Jetons signés | Émet et vérifie les access tokens (HS256, 15 min). |
| **requests** | Client HTTP | Le seul appel sortant du projet : vers Ollama, en **flux** (`/api/chat`). |
| **Flask-Limiter** | Limitation de débit | Freine `/register`, `/login`, `/forgot-password`. **Pourquoi** — sans lui, rien n'empêche d'essayer des mots de passe en boucle. |
| **Flask-Mail** | Envoi de courriels | Le lien de réinitialisation. Mailtrap en développement : **aucun mail ne part vraiment**. |
| **Flask-CORS** | Politique d'origine croisée | Autorise le front à appeler l'API, **et lui seul**. |
| **python-dotenv** | Lecture du `.env` | Charge la configuration. **Aucun secret dans le code.** |
| **markdown** + **WeasyPrint** | Markdown → HTML → PDF | L'export des documents terminés. **Pourquoi ce détour par HTML** — le PDF ressemble alors exactement à l'aperçu que l'utilisateur a relu ; composer le PDF autrement aurait voulu dire réimplémenter titres, listes et tableaux, et les maintenir en double. |
| **gunicorn** | Serveur d'application | Sert Flask en conteneur. **Pourquoi** — le serveur intégré de Flask est un outil de développement, mono-processus et non durci ; il l'écrit lui-même au démarrage. |
| **PyMySQL** | Pilote MySQL | Le dialogue avec MySQL 8.4. `cryptography` l'accompagne pour l'authentification `caching_sha2_password`. |

### Données, exécution, qualité

| Outil | À quoi il sert |
|---|---|
| **MySQL 8.4** | La base de production, en conteneur. |
| **SQLite** | **Pas un second SGBD** : le même code SQLAlchemy sur un moteur de développement. Les tests tournent dessus **en mémoire**, en quelques secondes, sans serveur. |
| **Ollama** + **qwen2.5:3b** | Le moteur d'inférence, **sur la machine**. Le modèle est choisi pour son **absence de mode raisonnement** — mesuré, qwen3 produisait 1 443 jetons là où qwen2.5 en produit 9. |
| **Docker / Compose** | Trois services — MySQL, backend, frontend — qui démarrent ensemble et à l'identique sur n'importe quelle machine. |
| **Nginx** | Sert les fichiers statiques du front dans le conteneur, et relaie `/api` vers le back. |
| **GitHub Actions** | L'intégration continue : 3 travaux **parallèles** à chaque push. |
| **pytest** + **pytest-cov** | Les 403 tests backend et la mesure de couverture. |
| **Vitest** + **@vue/test-utils** + **jsdom** | Les 58 tests frontend. jsdom simule un navigateur pour monter les composants sans en ouvrir un. |
| **Ruff** | Analyse et formatage Python, en une seule passe. |
| **ESLint** + **Prettier** | Analyse et formatage côté front. **Deux rôles distincts** : ESLint cherche les erreurs, Prettier impose la forme. |
| **vue-tsc** | Vérifie les types **dans les fichiers `.vue`**, ce que `tsc` seul ne sait pas faire. |

### Les trois pièges de cette question

1. **« Pourquoi pas du JavaScript simple ? »** → Je l'ai écrit en TypeScript parce que le projet est seul de son espèce : personne pour relire mes appels d'API. Les types sont ce relecteur.
2. **« Vous avez beaucoup de dépendances. »** → Douze côté front, quatorze côté back — plus les outils de développement, qui ne partent pas en production. **Toutes à version figée** et `package-lock.json` commité. Chacune remplace du code que j'aurais écrit moins bien — et la compromission d'axios m'a appris que les figer est une mesure de sécurité.
3. **« DOMPurify suffit-il ? »** → Non, et c'est pour ça que **je stocke du Markdown brut, jamais du HTML**. Si DOMPurify échoue un jour, la donnée en base n'est toujours pas exécutable.

---

## ▣ Fiche 27 — Gestion du temps

| Si tu es en retard | Coupe les diapos **14, 15, 18, 22** (descriptives). La **21** se survole en 20 s. |
|---|---|
| **Ne coupe jamais** | **8** (arbitrages) · **11** (choix techno) · **12** (archi) · **24** (quota) · **25** (WHERE) · **29** (jetons) · **34** (clôture) |

**Si tu perds le fil** → reviens à la question « pourquoi ce choix ? ». Chaque diapo a une
raison, pas une liste.

**Posture** → une respiration à chaque diapo de section. La clôture : lentement, en
regardant le jury.
