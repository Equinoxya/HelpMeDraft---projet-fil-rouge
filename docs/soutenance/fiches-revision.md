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

## ▣ Fiche 27 — Les définitions à savoir dire

Le jury demande souvent « qu'est-ce que c'est, exactement ? ». Une phrase de
définition, puis **un ancrage dans ton projet** : c'est l'ancrage qui montre que
tu l'as compris et pas récité.

### Architecture et web

| Terme | À dire |
|---|---|
| **API REST** | Une interface où chaque ressource a son adresse et où le verbe HTTP dit l'action — GET pour lire, POST pour créer, PUT/PATCH pour modifier, DELETE pour supprimer. **Chez moi** : `GET /documents`, `POST /documents/:id/ia/generer`. |
| **SPA** (application monopage) | Le serveur envoie une seule page ; ensuite c'est le JavaScript qui change l'affichage sans recharger. **Chez moi** : Vue Router change de vue, le navigateur ne recharge jamais. |
| **Architecture en couches** | Chaque couche ne parle qu'à la suivante et ignore celle du dessus. **Chez moi** : routes → services → persistance, et **aucun import Flask dans `services/`**. |
| **Endpoint** | Un point d'entrée de l'API : une URL plus un verbe. |
| **Blueprint** (Flask) | Un groupe de routes qu'on enregistre d'un bloc. **Chez moi** : cinq — auth, documents, dossiers, IA, admin. |
| **CORS** | La règle qui décide quelles origines ont le droit d'appeler l'API depuis un navigateur. **Chez moi** : restreint à l'origine du front, et rien d'autre. |
| **Proxy inverse** | Un serveur placé devant l'application, qui reçoit les requêtes et les distribue. **Chez moi** : Nginx sert le front et relaie `/api` vers le back. |
| **Conteneur / image** | L'**image** est le modèle figé, le **conteneur** est une instance qui tourne. On part toujours de la même image, donc du même état. |

### Conception logicielle

C'est le vocabulaire du REAC : « composants **métier** », « composants d'**accès aux
données** ». Le jury s'en sert pour vérifier que tu sais *où* vit quoi.

| Terme | À dire |
|---|---|
| **Logique métier** | Les règles propres au domaine, indépendantes de la façon dont on y accède. **Chez moi** : « un quota vaut 20 appels par 24 heures », « un jeton rejoué révoque la session ». Elles resteraient vraies si je remplaçais l'API REST par une ligne de commande. |
| **Composant métier** | Le code qui porte ces règles. **Chez moi** : `auth_service`, `ia_service`, `email_service` — dans `app/services/`. |
| **Couche de présentation** | La frontière avec l'extérieur : elle désérialise, valide, autorise, choisit le code de statut. **Chez moi** : `app/routes/`. **C'est la seule couche qui parle HTTP.** |
| **Couche d'accès aux données** | Celle qui sait parler au SGBD, et la seule. **Chez moi** : `database/db.py` — modèles, relations, requêtes. |
| **Séparation des responsabilités** | Chaque morceau de code a une raison de changer, et une seule. **Chez moi** : la règle vérifiable est **« aucun import Flask dans `services/` »**. |
| **Couplage / cohésion** | Le **couplage** est ce qui lie deux modules — on le veut faible. La **cohésion** est ce qui lie l'intérieur d'un module — on la veut forte. Un service qui ne connaît pas `request` est faiblement couplé au transport. |
| **Patron de conception** | Une solution éprouvée à un problème qui revient. On ne les invente pas, on les reconnaît. |
| **Fabrique** (factory) | Une fonction qui construit l'objet au lieu de le créer au chargement. **Chez moi** : `create_app()` — c'est ce qui permet d'instancier l'application avec une configuration de test. |
| **Décorateur** | Enrober une fonction pour lui ajouter un comportement sans la modifier. **Chez moi** : `@token_required`, `@limiter.limit` — la préoccupation transversale est écrite une fois. |
| **Intercepteur** | Le même principe côté client, sur les requêtes. **Chez moi** : l'intercepteur axios injecte le jeton et rejoue l'appel après un 401. |
| **Préoccupation transversale** | Ce qui concerne toutes les routes sans appartenir à aucune : authentification, journalisation, limitation de débit. D'où décorateurs et intercepteurs. |
| **Magasin centralisé** (store) | Une source de vérité unique partagée par toutes les vues. **Chez moi** : le store Pinia `auth`. |
| **Injection de dépendances** | Fournir à un composant ce dont il a besoin, au lieu qu'il aille le chercher. **Chez moi** : les services reçoivent leur session de base en paramètre — c'est ce qui les rend testables. |
| **Idempotence** | Rejouer l'appel ne change pas le résultat. **Chez moi** : `POST .../insertion` — un second appel renvoie `200` sans réécrire l'horodatage d'origine. |
| **Transaction** | Un ensemble d'écritures qui réussit ou échoue d'un bloc. |
| **Échec sécurisé** | En cas de doute, refuser plutôt que continuer dégradé. **Chez moi** : l'application **refuse de démarrer** sans `JWT_SECRET_KEY`. |
| **Liste blanche** | N'accepter que des valeurs explicitement autorisées, au lieu d'interdire les mauvaises. **Chez moi** : `type_action`, `scope`, `status`, `format`. |
| **Refactorisation** | Changer la structure du code sans changer son comportement. Les tests sont ce qui rend l'opération sûre. |
| **Dette technique** | Un raccourci qu'on devra payer plus tard. **Chez moi** : je l'invoque pour refuser un composant NoSQL qui n'aurait servi qu'à remplir une grille. |

> **La question POO.** Elle tombe souvent, parce que le CP 3 évalue « les bonnes pratiques
> de la POO ». **Dis-le avant qu'on te le trouve.**
>
> Ce qui est objet chez toi : les **huit modèles** de `database/db.py` sont des classes qui
> héritent toutes d'une base commune `Base(DeclarativeBase)` — héritage, encapsulation des
> colonnes, correspondance classe ↔ table.
>
> Ce qui ne l'est pas : **tes services sont des modules de fonctions**. Un choix idiomatique
> en Python pour des services **sans état** — une classe sans attribut d'instance n'est
> qu'un espace de noms, et le module en est déjà un. C'est écrit dans ton dossier (§ 5.2),
> donc assume-le plutôt que de le découvrir à l'oral.

### Base de données

| Terme | À dire |
|---|---|
| **SGBD relationnel** | Un système qui range les données en tables liées entre elles et qui garantit lui-même la cohérence. **Chez moi** : MySQL 8.4. |
| **ORM** | Une couche qui fait correspondre des classes du langage à des tables. **Chez moi** : SQLAlchemy — et c'est lui qui **paramètre toutes les requêtes**, donc qui rend l'injection SQL impossible. |
| **Clé primaire / clé étrangère** | La primaire identifie une ligne de façon unique ; l'étrangère pointe vers la primaire d'une autre table. **Chez moi** : 8 primaires, 9 étrangères. |
| **UUID** | Un identifiant de 36 caractères tiré au hasard, pas un compteur. **Chez moi** : on ne peut pas deviner `/documents/43` à partir de `/documents/42`. |
| **Cardinalité** | Combien d'éléments de A peuvent correspondre à un élément de B. **Chez moi** : lecture Merise, `(0,n)` côté utilisateur, `(1,1)` côté dépendant. |
| **MCD / MLD / MPD** | Le **conceptuel** dit *quoi* (entités, associations) ; le **logique** traduit les associations en clés étrangères ; le **physique** ajoute les types SQL, les index et les règles de suppression. |
| **Dénormalisation** | Accepter une redondance pour éviter une jointure coûteuse. **Chez moi** : `ia` porte `user_id` *et* `id_document`, parce que le quota se compte par utilisateur. |
| **Index** | Une structure qui évite de parcourir toute la table. **Chez moi** : `(user_id, created_at)` sert le calcul du quota. |
| **ON DELETE CASCADE** | Supprimer la ligne parente supprime les filles. **Chez moi** : c'est **le droit à l'effacement du RGPD en une instruction**. |
| **ON DELETE SET NULL** | La fille survit, son lien passe à nul. **Chez moi** : supprimer un dossier ne supprime pas ses documents. |
| **Requête paramétrée** | La valeur est transmise à part de la requête, donc jamais interprétée comme du SQL. C'est **la** parade à l'injection. |
| **NoSQL** | Des bases sans schéma fixe ni jointures, faites pour le volume distribué. **Chez moi** : écarté, et c'est argumenté — mes données ont un schéma stable et sont fortement reliées. |

### Sécurité

| Terme | À dire |
|---|---|
| **Authentification / autorisation** | L'authentification répond à « qui êtes-vous », l'autorisation à « avez-vous le droit ». **Deux choses distinctes** : un utilisateur authentifié n'a pas pour autant accès au document d'un autre. |
| **Hachage** | Une transformation **à sens unique** : on ne revient pas en arrière. À ne pas confondre avec le chiffrement, qui est réversible. |
| **Sel** | Une valeur aléatoire ajoutée avant le hachage, pour que deux mots de passe identiques ne donnent pas la même empreinte. **Chez moi** : bcrypt le gère lui-même. |
| **bcrypt** | Une fonction de hachage **lente exprès**, à coût réglable. C'est sa lenteur qui protège de la force brute. |
| **JWT** | Un jeton qui contient ses propres informations et une signature. Le serveur le vérifie **sans rien stocker** — ce qui est son avantage, et sa limite : **on ne peut pas le révoquer**. |
| **Access / refresh token** | L'**access** sert à chaque appel, court (15 min). Le **refresh** sert seulement à obtenir un nouvel access, long (7 jours) et **révocable côté serveur**. |
| **Rotation des jetons** | Chaque usage du refresh en émet un nouveau et invalide l'ancien. **Chez moi** : un jeton déjà consommé qui revient est traité comme un vol. |
| **httpOnly** | Un cookie que le JavaScript ne peut pas lire. **Chez moi** : même une faille XSS ne donne pas le refresh token. |
| **SameSite=Strict** | Le cookie n'est envoyé que si la requête part du même site. C'est la parade CSRF. **Attention** : il raisonne en *sites*, pas en *origines*. |
| **XSS** | Faire exécuter du JavaScript étranger dans le navigateur d'un autre utilisateur. **Chez moi** : l'aperçu Markdown est assaini par DOMPurify, et je stocke du Markdown brut, jamais du HTML. |
| **Injection SQL** | Faire interpréter une entrée comme du code SQL. **Chez moi** : impossible, l'ORM paramètre tout. |
| **CSRF** | Faire exécuter une action à un utilisateur connecté depuis un autre site, à son insu. |
| **Défense en profondeur** | Ne jamais dépendre d'une seule barrière. **Chez moi** : DOMPurify assainit l'affichage, **et** la base ne contient que du Markdown non exécutable. |
| **Moindre privilège** | Chacun n'a que les droits dont il a besoin. **Chez moi** : trois comptes MySQL — l'applicatif n'a aucun droit de structure. |
| **Limitation de débit** | Plafonner le nombre d'appels par période. **Chez moi** : sur connexion, inscription et mot de passe oublié. |
| **Énumération de comptes** | Déduire qu'une adresse existe à partir de la réponse du serveur. **Chez moi** : réponse identique que le compte existe ou non — « Email ou mot de passe incorrect » à la connexion, et le même message au mot de passe oublié. **Si on insiste** : le temps de réponse, lui, n'est pas égalisé, puisque l'envoi du mail prend un instant de plus. Je le sais ; la parade serait de différer l'envoi. |
| **OWASP Top 10** | La liste de référence des dix risques applicatifs les plus courants. **Chez moi** : édition **2021**, et aussi le **Top 10 for LLM Applications**, édition 2026. |

### Intelligence artificielle

| Terme | À dire |
|---|---|
| **LLM** (modèle de langage) | Un modèle entraîné à prédire le mot suivant ; c'est de cette prédiction répétée que sort un texte. |
| **Inférence** | L'exécution du modèle pour produire une réponse — par opposition à l'entraînement. **Je n'entraîne rien, je fais de l'inférence.** |
| **Inférence locale** | Le modèle tourne sur la machine de l'entreprise. **Chez moi** : Ollama, et c'est ce qui satisfait l'exigence RGPD **par construction**. |
| **Jeton** (token) | L'unité que manipule le modèle : un mot court, ou un morceau de mot. **Chez moi** : journalisé à chaque appel. |
| **Prompt** | Le texte envoyé au modèle. **Chez moi** : un message `system` qui porte les règles, un message `user` qui porte le contenu. |
| **Prompt engineering** | Écrire ce texte de façon à obtenir un résultat régulier. **Et un prompt se teste comme du code** : c'est le cas TU-04. |
| **Fenêtre de contexte** | Le nombre de jetons que le modèle peut lire d'un coup. **Chez moi** : 4 096 — au-delà, Ollama tronque **silencieusement**, et par l'avant, donc ce sont les consignes qui disparaissent. |
| **Température** | Le réglage du hasard dans la génération. **Chez moi** : 0,1 pour corriger, 0,7 pour compléter — on veut peu d'imagination pour corriger. |
| **Hallucination** | Une sortie fausse énoncée avec assurance. **Chez moi** : c'est pourquoi **rien n'est appliqué automatiquement** et que l'interface prévient. |

### Tests et qualité

| Terme | À dire |
|---|---|
| **Test unitaire** | Vérifie une fonction isolée, sans base ni réseau. |
| **Test d'intégration** | Vérifie que plusieurs composants fonctionnent ensemble — chez moi, route + service + base. |
| **Test fonctionnel** | Rejoue un parcours utilisateur complet. |
| **Couverture de code** | La part du code exécutée par les tests. **Ce n'est pas une preuve de qualité** : du code couvert peut être mal testé. |
| **Double de test** (mock) | Un faux composant qui remplace un vrai. **Chez moi** : la leçon de la campagne — **les doubles mentent**, trois défauts sont passés sous un faux `requests.post`. |
| **Test de mutation** | On casse volontairement le code pour vérifier qu'un test échoue. **Un test qu'on n'a jamais vu échouer ne prouve rien.** |
| **Régression** | Une fonctionnalité qui remarchait et qui casse. Les tests de non-régression existent pour ça. |
| **Jeu d'essai** | Un jeu de données construit pour la recette. **Ce n'est pas remplir des tables : c'est choisir les valeurs qui font échouer les mauvaises implémentations.** |

### Exploitation

| Terme | À dire |
|---|---|
| **Intégration continue (CI)** | À chaque envoi de code, une machine rejoue analyse, tests et construction. **Chez moi** : GitHub Actions, trois travaux parallèles. |
| **Déploiement continu (CD)** | Le prolongement : la mise en ligne automatique après succès. **Chez moi** : non mis en place, l'hébergement reste à faire. |
| **Pipeline** | L'enchaînement de ces étapes. |
| **Lint** | L'analyse statique qui repère erreurs et écarts de style **sans exécuter** le code. |
| **Fichier de verrouillage** | Fige la version exacte de chaque dépendance, directes et indirectes. **Chez moi** : `package-lock.json` commité — **une mesure de sécurité**, l'incident axios l'a montré. |

### Conformité

| Terme | À dire |
|---|---|
| **RGPD** | Le règlement européen sur les données personnelles. **Chez moi** : consentement tracé, export (art. 15 et 20), effacement par cascade. |
| **Droit à l'effacement** | Le droit d'obtenir la suppression de ses données. **Chez moi** : porté par les `ON DELETE CASCADE`. |
| **Portabilité** | Le droit de récupérer ses données dans un format réutilisable. **Chez moi** : export en archive ZIP. |
| **RGAA 4.1.2** | Le référentiel français d'accessibilité, fondé sur **WCAG 2.1 niveau AA**. **Chez moi** : 15 écrans audités, 0 violation axe-core. |
| **ANSSI** | L'agence française de cybersécurité ; ses recommandations ont servi de référence à l'audit. |
| **AI Act** | Le règlement européen **UE 2024/1689**. Son **article 50** impose d'informer l'utilisateur qu'un contenu est généré — applicable depuis le **2 août 2026**, soit après la rédaction du cahier des charges. |

---

## ▣ Fiche 28 — Gestion du temps

| Si tu es en retard | Coupe les diapos **14, 15, 18, 22** (descriptives). La **21** se survole en 20 s. |
|---|---|
| **Ne coupe jamais** | **8** (arbitrages) · **11** (choix techno) · **12** (archi) · **24** (quota) · **25** (WHERE) · **29** (jetons) · **34** (clôture) |

**Si tu perds le fil** → reviens à la question « pourquoi ce choix ? ». Chaque diapo a une
raison, pas une liste.

**Posture** → une respiration à chaque diapo de section. La clôture : lentement, en
regardant le jury.
