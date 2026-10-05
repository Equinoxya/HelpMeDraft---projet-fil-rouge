# Reste à faire — HelpMeDraft

Croisement entre le [cahier des charges LexiCorp](./docs/cahier-des-charges.md), les
[compétences du titre CDA](./docs/competences-cda.md) et l'état du dépôt.

- `CP n` renvoie à la compétence professionnelle du REAC.
- ⭐ = compétence **obligatoirement** mise en œuvre par le projet (REV §3.1).
- Le [plan du dossier de projet](./docs/plan-dossier-projet.md) liste les productions attendues à l'examen.

---

## ✅ Déjà couvert

| Exigence | Où | CP |
|---|---|---|
| Inscription / connexion / déconnexion / reset mot de passe | `auth_routes.py`, 4 vues dédiées | 2, 3 |
| Rôles utilisateur / administrateur | `admin_route.py`, `AdminView.vue` | 3 |
| Éditeur Markdown + commandes IA | `MarkdownEditor.vue`, `DocumentEditorView.vue` | 2 |
| CRUD documents, dossiers, historique IA | `document_route.py`, `dossier_route.py`, `ia_route.py` | 3, 8 |
| Traçabilité des contenus générés par IA (AI Act, art. 50) | `ia_route.py` (`POST …/insertion`), colonnes `insere` / `position_debut` / `insere_at`, `DocumentEditorView.vue` | 2, 3, 7 |
| IA locale (Ollama) + prompt engineering | `services/ia_service.py` | 3 |
| Quota IA journalier | `ia_route.py` (fenêtre 24 h) | 3 |
| Stats d'usage admin | `admin_route.py` (`/stats`) | 3 |
| Architecture en couches effective | `routes/` → `services/` → `database/` + SPA découplée | 6 |
| Modèle de données (7 entités) + script MySQL | `database/db.py`, `schema_mysql.sql` | 7 |
| ORM SQLAlchemy, requêtes paramétrées, validation des entrées | `db.py`, routes | 8 |
| Protection XSS (DOMPurify) + 13 tests | `MarkdownEditor.vue`, `markdown-sanitization.spec.ts` | 2 |
| Suite de tests automatisés (344 tests) | `backend/tests/`, `frontend/src/**/__tests__/` | 2, 3, 8, 9 |
| Performance de la génération IA : modèle, fenêtre de contexte et maintien en mémoire dimensionnés sur mesures | `config.py`, `ia_service.py` | 3, 11 |
| Annulation d'une génération en cours + temps estimé affiché | `DocumentEditorView.vue`, `utils/iaEstimation.ts` | 2 |
| Tokens hashés, rotation, anti-rejeu, révocation contrôlée, cookie HttpOnly/SameSite | `auth_routes.py`, `auth_service.py`, `test_securite.py` | 3 |
| Consentement RGPD tracé en base | table `consentement` | 5, 7 |
| Maquettes et captures | `docs/maquettes/`, `docs/captures/` | 5 |
| Accessibilité RGAA : 15 écrans, 0 violation axe-core, 6 contrôles manuels au vert | `docs/audit-accessibilite.md`, `docs/audits/audit-accessibilite.mjs` | 2, 5 |
| Journal de veille (3 périmètres, avril → octobre 2026) | `docs/veille/journal-de-veille.md` | transversale |
| Suivi de projet sur données Jira réelles | `docs/gestion-de-projet.md` | 4 |
| Git / GitHub, branches, PR | — | 1, 4 |
| `.env.example` | racine | 10 |
| Pile Docker validée sur un démon réel : images, MySQL 8.4, droits, sauvegarde, tests système | `docs/validation-docker.md` | 1, 7, 10, 11 |

---

## ⬜ À faire

### 1 · Documents de conception ⭐ CP 5, 6, 7 — ✅ fait
Voir [`docs/conception/`](./docs/conception/). 11 diagrammes, également exportés en PNG.

- [x] **Expression des besoins** : acteurs, périmètre, 19 besoins fonctionnels et 10 non fonctionnels tracés au cahier des charges, 10 règles de gestion
- [x] **Diagramme de cas d'utilisation** : 18 cas, 5 acteurs, matrice de traçabilité
- [x] **Schéma d'enchaînement des écrans** (critère de performance explicite de CP5) + diagramme d'états de l'éditeur
- [x] **Modèle entités-associations (MCD)** et **modèle physique (MPD)**, cardinalités Merise, règles de passage, conventions de nommage
- [x] **Dossier d'architecture logicielle** : rôle de chaque couche, stratégie de sécurité par couche, analyse DICP, patrons de conception et de sécurité
- [x] **Besoins d'éco-conception** identifiés (8 besoins, ECO-01 à ECO-08)
- [x] **Diagrammes de séquence** : génération IA (nominal + 5 chemins d'erreur), connexion et rotation du refresh token, réinitialisation de mot de passe

Reste à faire sur ce lot :
- [ ] Faire relire le périmètre et les écarts assumés par le formateur
- [ ] Vérifier avec lui si le plan « formation » ou le plan « entreprise » du dossier est attendu

### 2 · Tests automatisés et plan de tests ⭐ CP 2, 3, 8, 9 — 🔄 l'essentiel est fait
**344 tests, tous au vert** (286 pytest, 58 Vitest), **96 % de couverture backend** hors
`database/jeu_essai.py`, script de peuplement non destiné à être couvert (89 % en le comptant).
Chiffres mesurés le 05/10/2026 (`pytest --cov=app --cov=database`, `vitest run`).
Voir [`docs/plan-de-tests.md`](./docs/plan-de-tests.md), [`backend/tests/README.md`](./backend/tests/README.md), [`frontend/TESTS.md`](./frontend/TESTS.md).

- [x] **pytest** côté backend : unitaires, intégration, sécurité
- [x] **Vitest** côté frontend
- [x] Tests unitaires par couche : métier (CP3), accès aux données (CP8), interface (CP2)
- [x] **Plan de tests** complet : 7 niveaux, ~90 cas, traçabilité des 10 règles de gestion
- [x] **Environnement de tests** hermétique : base en mémoire, aucun appel réseau
- [x] **Jeu d'essai de la fonctionnalité la plus représentative** : 11 cas exécutés, 0 écart
- [x] **Compte rendu d'exécution** : plan de tests §11
- [x] **Tests système TS-01 à TS-10 exécutés** sur la pile conteneurisée (05/10/2026) :
      **7 au vert**, 1 en échec (constat SMTP du §8), 2 hors de portée — TS-04 exige un Ollama
      joignable, TS-10 un lecteur d'écran réel. Script versionné
      ([`tests-systeme.mjs`](./docs/audits/tests-systeme.mjs)), résultats bruts dans
      [`tests-systeme-2026-10-05.json`](./docs/audits/tests-systeme-2026-10-05.json)
- [ ] **Tests d'acceptation** avec le formateur
- [ ] **Tests de charge** — la pile est maintenant exécutable, plus rien ne les bloque
- [ ] Brancher les deux suites dans la CI (voir §5)

Trouvé et corrigé pendant la campagne :
- [x] `KAN-93` — `DELETE /documents/<id>` renvoyait un tuple à un élément : erreur 500 au lieu de 204
- [x] Testabilité : `db.py` liait le moteur à un chemin en dur dès l'import. L'URL est désormais lue dans `HELPMEDRAFT_DB_URL` (débloque aussi `KAN-86` et `KAN-15`)

Leçon de méthode, à raconter en soutenance : **les doubles de test mentent.**
Trois bugs de la chaîne IA sont passés sous un faux `requests.post` qui
acceptait `json()` à tout moment et ne libérait jamais de connexion. Il a fallu
un vrai serveur HTTP — `tests/integration/test_ia_flux_ollama.py`, un
`http.server` qui imite `/api/generate` — pour les voir. Les nouveaux tests ont
été vérifiés **par mutation** : on casse volontairement le code pour s'assurer
qu'ils échouent.

### 3 · Gestion de projet ⭐ CP 4 — 🔄 en grande partie fait
Voir [`docs/gestion-de-projet.md`](./docs/gestion-de-projet.md), établi sur les données réelles du Jira `KAN`.

- [x] **Planning** : Gantt des 9 epics, échéances relevées dans Jira
- [x] **Suivi des tâches** rapproché du planning : écart par epic, vélocité mensuelle, incohérences d'état relevées
- [x] **Analyse des causes** du retard et **replanification** priorisée
- [x] **Objectifs et procédures qualité** : définition de « terminé », conventions de code, règles de sécurité non négociables
- [x] **Modèle de compte rendu** structuré + repères de dates pour retrouver les points tenus
- [ ] **Rédiger les comptes rendus réels** dans `docs/comptes-rendus/` — ne peut pas être reconstitué, c'est à faire par la candidate
- [ ] **Porter l'alerte de retard au formateur** et en verser le compte rendu (le critère exige que les acteurs soient alertés)

Hygiène du Jira, relevée au passage :
- [x] Rouvrir `KAN-10` et `KAN-13`, clos alors que des tâches restent ouvertes
- [x] Fermer `KAN-99` (DOMPurify déjà à jour) et `KAN-93` (bug corrigé)
- [ ] Rattacher ou supprimer les 10 tickets hors epic (`KAN-1` à `KAN-6`, `KAN-89` à `KAN-92`)
- [ ] Reporter les échéances des epics (toutes dépassées, de 76 à 129 jours)

### 4 · Conteneurisation CP 1, 11 — ✅ fait **et validée sur un vrai démon Docker**
Voir [`docs/validation-docker.md`](./docs/validation-docker.md) — campagne du 05/10/2026.
- [x] `docker-compose.yml` : MySQL 8.4, backend, frontend. Sonde de santé sur la base, secrets déclarés avec `${VAR:?message}` pour échouer tout de suite plutôt que d'inventer une valeur
- [x] `backend/Dockerfile` : gunicorn, utilisateur non privilégié, `--timeout 600` parce que l'inférence n'impose aucun délai de lecture
- [x] `frontend/Dockerfile` : construction en deux étapes, image finale nginx (**82,9 Mo mesurés**, et non ~50 Mo comme annoncé ici jusqu'au 05/10), repli monopage vérifié (`GET /documents/42` → 200)
- [x] Stack composée : backend + frontend + BDD. **Ollama reste sur l'hôte**, atteint par `host.docker.internal` — son image pèse plusieurs Go et le modèle se télécharge à part
- [x] **`docker compose up --build` exécuté pour de vrai** : composition valide, les deux images se
      construisent, MySQL 8.4.11 passe sa sonde, le backend se connecte sous gunicorn, nginx sert le
      bundle avec le bon `VITE_API_URL`, CORS filtre comme prévu, et la remise à zéro documentée
      (`down -v` puis `up`) rejoue bien `initdb`
- [x] **Deux conteneurs non privilégiés vérifiés** : backend `uid=10001`, frontend `uid=101`, maître
      nginx compris
- [ ] Rejouer la validation sur la machine de développement avec **Ollama démarré** : TS-04
      (reformuler → remplacer) est le seul parcours que la campagne n'a pas pu couvrir, faute de
      modèle joignable depuis l'environnement d'intégration
- [ ] Remplacer le stockage mémoire de Flask-Limiter par Redis. Les seuils comptent **par worker** : avec 2 workers, ceux de `/auth/login` sont doublés

### 5 · CI/CD et qualité de code CP 11 — ✅ en place
- [x] **Pipeline GitHub Actions** (`.github/workflows/ci.yml`) : trois travaux en parallèle — backend (Ruff + pytest), frontend (ESLint, Prettier, types, tests, build), Docker (validation de la composition + construction des deux images). Un échec du frontend ne masque plus l'état du backend
- [x] **Ruff** configuré dans `backend/pyproject.toml` : 20 constats corrigés, dont 10 exceptions levées sans `from` et un `== False` que la suggestion de l'outil aurait rendu FAUX en SQLAlchemy
- [x] **ESLint 9** configuré : 19 constats corrigés, dont les 7 `catch (err: any)`, remplacés par un module typé `utils/erreurs.ts` et ses tests
- [ ] Savoir **interpréter les rapports de CI** (critère de performance) — à exercer sur les premières exécutions réelles
- [ ] Ajouter un seuil de couverture au travail backend (`pytest --cov`, déjà installé)
- [ ] **4 vulnérabilités `high` signalées par `npm audit`**, toutes issues de la même chaîne : `@vue/eslint-config-typescript` → `fast-glob` → `micromatch` → `braces@3.0.3`. L'avis [GHSA-vfj7-8cjw-p6xm](https://github.com/advisories/GHSA-vfj7-8cjw-p6xm) couvre `braces <= 3.0.3` et aucune version corrigée n'existe dans cette branche. **Dépendance de développement uniquement** : elle n'entre pas dans le bundle livré, et le déni de service décrit suppose qu'un attaquant contrôle les motifs de glob passés à ESLint. À revoir quand l'amont publiera un correctif
- [x] **`npm run build` réparé** : les deux imports inutilisés retirés. Plus rien ne bloque la mise en CI
- [x] Prettier passé sur les 6 fichiers non formatés — `prettier --check src/` est propre

### 6 · Base de données ⭐ CP 7 — ✅ l'essentiel est fait
Voir [`docs/exploitation-base-de-donnees.md`](./docs/exploitation-base-de-donnees.md).
**13 contrôles passés contre un vrai serveur MySQL** (MariaDB 10.11, faute de démon Docker ici).

> **Trois défauts réels trouvés et corrigés**, tous invisibles depuis l'interface :
> 1. `create_all()` tournait aussi sur MySQL, donc `schema_mysql.sql` **n'était jamais exécuté** —
>    la base réelle n'avait ni les 5 `CHECK`, ni les 9 index, ni les clés étrangères nommées, alors
>    que le dépôt affichait un script soigné ;
> 2. `ia.id_document` sans `ondelete` côté ORM : tout `DELETE FROM document` exécuté en SQL
>    échouait (`FOREIGN KEY constraint failed`). Seul le passage par l'ORM fonctionnait, grâce à un
>    `cascade` Python qui masquait l'absence de la règle côté base ;
> 3. `cryptography` absente des dépendances : MySQL 8.4 authentifie en `caching_sha2_password`, que
>    PyMySQL ne sait pas honorer sans elle. **La première connexion de la pile échouait** —
>    `docker compose up` ne pouvait pas fonctionner. Invisible parce que les tests tournent sur
>    SQLite, qui n'authentifie rien.

- [x] **MySQL tranché** et argumenté (§2 du document) : MySQL 8.4 en conteneur, SQLite conservé en
      développement et pour les tests. PostgreSQL écarté pour coût et non pour qualité
- [x] **`schema_mysql.sql` est la source de vérité unique** : monté en `initdb` dans la
      composition, `create_all()` ne tourne plus que sur SQLite, et l'application **échoue au
      démarrage** avec la marche à suivre si les tables manquent
- [x] **Parité ORM / SQL vérifiée par 36 tests** (`tests/unit/test_schema_parite.py`) : tables,
      colonnes, longueurs, nullabilité, `CHECK`, index, unicité, clés étrangères et règles
      `ON DELETE`. Modifier un seul des deux endroits fait échouer la CI
- [x] **Jeu d'essai** reproductible (`database/jeu_essai.py`) : 4 comptes, 7 documents, 40 appels
      IA. Couvre les bornes — quota épuisé, quota minimal, les 3 statuts, document sans dossier,
      appels hors fenêtre de 24 h, jetons expiré et consommé. En Python et non en `.sql` parce que
      bcrypt sale ses empreintes
- [x] **Sauvegarde / restauration** : 2 scripts, 3 contrôles d'intégrité, rétention. L'aller-retour
      a été joué pour de vrai — données détruites puis restituées à l'identique
- [x] **Utilisateurs SGBD et droits** : 3 comptes au moindre privilège. Le compte applicatif n'a
      **aucun droit de structure**, vérifié depuis l'application (`CREATE TABLE` et `DROP TABLE`
      refusés)
- [x] Aligner ORM et SQL sur `ia.id_document` — fait, et vérifié sur un vrai InnoDB
- [x] **Les 4 points propres à MySQL 8.4 sont confirmés** sur MySQL 8.4.11 réel (05/10/2026) :
      collation `utf8mb4_0900_ai_ci` sur le schéma et les 7 tables, `mysqldump --set-gtid-purged=OFF`
      accepté (0 instruction `SET GTID_PURGED` dans l'archive), authentification
      `caching_sha2_password` honorée par les 3 comptes — donc l'ajout de `cryptography` était le
      bon correctif — et enchaînement `10-schema.sql` → `20-droits.sh`. Aller-retour
      sauvegarde / restauration rejoué, jeu d'essai chargé, droits éprouvés (`CREATE`, `DROP` et
      `ALTER` refusés à l'applicatif), cascade `DELETE FROM document` vérifiée en SQL brut. Détail
      dans [`docs/validation-docker.md`](./docs/validation-docker.md)
- [ ] Outiller les migrations (Alembic) : les 4 scripts actuels (dont
      `migration_tracabilite_ia.sql`) ne sont ni versionnés ni idempotents, et rien n'enregistre
      ce qui a déjà été appliqué

### 7 · NoSQL ⭐ CP 8
Voir [`docs/argumentaire-nosql.md`](./docs/argumentaire-nosql.md).

- [x] **Argumentaire NoSQL** : décision de ne rien ajouter, argumentée par l'étude des trois usages
      candidats (cache Redis des réponses IA, journal Mongo des appels, Redis pour Flask-Limiter),
      chiffrée là où c'était mesurable, avec les trois conditions de son réexamen.
      **Le critère reste formellement non couvert par un composant** — le document le dit, plutôt
      que de brancher un Redis décoratif
- [x] **Transactions et conflits d'accès** : documenté au §7 du document d'exploitation. Un conflit
      réel y est analysé — le quota IA est un *time-of-check to time-of-use*, deux appels
      simultanés à 19/20 passent tous les deux. Portée chiffrée (2 à 3 appels au-delà du quota, et
      c'est une limite de ressource, pas un contrôle d'accès)
- [ ] Appliquer la correction du quota concurrent (§7.2 : réserver la ligne `ia` dans une
      transaction courte, puis appeler le modèle hors transaction). **Non fait** : un verrou naïf
      serait tenu pendant les 50 s de l'inférence, le remède serait pire que le mal — 2 h

### 8 · Sécurité — 🔄 l'essentiel est fait
Voir [`docs/audit-securite.md`](./docs/audit-securite.md). 0 vulnérabilité critique ou élevée,
17 tests de sécurité.

> **Incident clos.** Deux clés secrètes réelles avaient été commitées dans
> `Claude outputs/env-1`. Elles ont été **régénérées**, ce qui rend sans valeur celles qui
> restent dans l'historique git, et la cause a été corrigée : le `.gitignore` ne contenait que
> la règle `.env`, qui ne couvre que ce nom exact. Un bon sujet pour la démarche de résolution
> de problème du §13 — la leçon est qu'une règle d'exclusion se teste, elle ne se suppose pas.

- [x] **Rapport d'audit de sécurité** complet
- [x] Configurer `SECRET_KEY` Flask, distincte de `JWT_SECRET_KEY`
- [x] `KAN-95` limitation de débit sur `/auth/refresh`
- [x] `KAN-96` purge des sessions expirées
- [x] **Jeton de rafraîchissement révoqué accepté** : `verify_refresh_token()` ne lisait pas le
      drapeau `revoke`. Une session révoquée restant en base jusqu'à expiration — c'est elle qui
      permet la détection de rejeu — un jeton déjà tourné passait le contrôle. Corrigé et
      couvert par un test unitaire dédié
- [x] `KAN-98` contrainte SQL du quota alignée sur l'API + script de migration
- [x] `KAN-94` énumération à l'inscription : **risque accepté**, argumenté au §4.1 du rapport
- [x] Test XSS rejoué, et transformé en 13 tests automatisés
- [x] Veille sécurité documentée
- [x] **Ajouter `SECRET_KEY` au `backend/.env`** — fait : `config.py` lève une `RuntimeError` au démarrage sans elle, et l'application démarre
- [x] `KAN-100` **relever la version d'Ollama** — fait : **0.35.1**, au-dessus du seuil de 0.18 fixé au §4.2 du rapport d'audit
- [x] **Clés commitées** : les deux copies de `.env` retirées du dépôt, clés **régénérées**, et `.gitignore` complété (`.env.*`, `!.env.example`, `Claude outputs/`) — les quatre cas d'exclusion vérifiés
- [ ] **`/auth/forgot-password` immobilise un worker quand le serveur SMTP ne répond pas.**
      Trouvé le 05/10/2026 en validant la pile : le courriel est envoyé **dans le fil de la
      requête**, et Flask-Mail construit son `smtplib.SMTP` sans délai. Mesuré sur la pile réelle —
      requête toujours en cours après 90 s, et avec 2 workers gunicorn synchrones **l'API entière
      cesse de répondre** ; il a fallu redémarrer le conteneur. La route est publique et non
      authentifiée, et la limitation de débit (3/h) compte par IP *et par worker*. Deux corrections,
      à arbitrer, décrites au §4 de
      [`docs/validation-docker.md`](./docs/validation-docker.md) : borner le `send()` par un délai
      de socket (quelques lignes, tout de suite), puis sortir l'envoi du fil de la requête (la vraie
      correction, à rapprocher du §12)
- [ ] `KAN-100` Ollama : restreindre l'écoute à `127.0.0.1` (`OLLAMA_HOST=127.0.0.1:11434`)
- [ ] **Chiffrement des données au repos** — 3 options chiffrées au §5.1 du rapport, à arbitrer
- [ ] `KAN-102` épingler les dépendances transitives (Werkzeug non épinglée)

### 9 · Accessibilité RGAA CP 2, 5 — ✅ les 9 correctifs sont faits et mesurés
Voir [`docs/audit-accessibilite.md`](./docs/audit-accessibilite.md). Audit réel sur les 16 écrans : **120 occurrences sur 3 règles**, dont 117 dues à une seule couleur.

- [x] **Rapport d'audit d'accessibilité** : axe-core sur l'application démarrée + contrôles manuels
- [x] **Assombrir `#E0533C` en `#C4341C`** — fait, 199 occurrences dans 19 fichiers. Mesuré avec axe-core sur les 10 écrans publics : **64 violations de contraste avant, 0 après**. Les teintes de survol suivent (`#A72C18`), sans quoi le survol serait devenu plus clair que l'état normal
- [x] **axe-core repassé sur les écrans authentifiés** (tableau de bord, documents, éditeur, back-office) : application montée dans un conteneur jetable avec un compte de test, connexion par l'interface. **0 violation sur les 5 écrans**
- [x] Étiquette sur le champ de quota du back-office (seul constat *critique*) — `aria-label` citant l'utilisateur concerné, la page affichant autant de champs que de lignes
- [x] `aria-label` sur la zone CodeMirror — via `EditorView.contentAttributes` : aucune `<label>` ne peut désigner un `contenteditable`

> **Bilan axe-core : 15 écrans, 0 violation** (WCAG 2.0 et 2.1, niveaux A et AA).
> Ce qui suit relève du **contrôle manuel**, qu'axe-core ne détecte pas : un
> « 0 violation » automatisé ne vaut pas conformité RGAA.
- [x] **Titre de page distinct par route** — `meta.titre` et un `router.afterEach`, plutôt qu'un
      appel par vue : une vue qui l'oublierait laisserait le titre de la page précédente, et
      l'oubli ne se verrait pas. `RouteMeta` augmentée, pour qu'une faute de frappe échoue à la
      compilation. **15 titres distincts sur 15 écrans**
- [x] **Lien d'évitement** — dans `App.vue`, premier élément focalisable, cible `#contenu` posée
      une seule fois autour de `<router-view>` et non vue par vue. **15 écrans sur 15**,
      235 × 40 px une fois focalisé
- [x] **Règle `:focus-visible` globale** — et surtout **retrait des 5 `focus:outline-none`** qui
      l'auraient emportée sur elle : en Tailwind, un sélecteur de classe bat une pseudo-classe.
      **0 élément sans focus visible**
- [x] **`h3` du pied de page → `h2`**, et nom de catégorie en `h2` sur l'écran Modèles.
      **0 saut de niveau sur les 15 écrans**
- [x] **`<main>` sur l'accueil, `h1` sur Nouveau document** — 15 sur 15 pour les deux
- [x] **Cibles sous 24 px** — 11 agrandies par remplissage vertical, **4 liens en ligne dans une
      phrase laissés tels quels** sous l'exception WCAG 2.5.8, comptés à part par le script pour
      que l'exception reste visible

> **Contre-audit du 05/10/2026**, même méthode et même script que l'audit initial : **15 écrans,
> 0 violation axe-core** (`wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`, `wcag22aa`), et les six
> contrôles manuels au vert. Résultats bruts dans
> [`docs/audits/accessibilite-2026-10-05.json`](./docs/audits/accessibilite-2026-10-05.json), et
> le script est désormais **versionné** ([`audit-accessibilite.mjs`](./docs/audits/audit-accessibilite.mjs)),
> ce qui rend la §8 du rapport vraie et prépare son passage en CI.

Deux défauts trouvés en corrigeant, qu'aucune lecture du code n'aurait donnés :
- [x] Les 16 cartes de l'écran Modèles **avaient** un contour de focus : `transition-all` le
      faisait monter de 0 à 2 px en 150 ms. Il existait donc, mais en fondu — un vrai défaut au
      clavier rapide, et la cause du « focus invisible » relevé à l'audit. Transitions restreintes
      aux propriétés réellement animées
- [x] La case de consentement RGPD **rétrécissait dans son conteneur `flex`** : 20 × 24 px mesurés
      là où ses classes annonçaient 24 × 24. `shrink-0` ajouté
- [x] Une 12ᵉ cible trop petite, absente du premier audit : le lien « Créer votre premier
      document », qui ne s'affiche **que si la liste est vide** — le compte de test d'alors avait
      des documents

Reste à faire sur ce lot, et aucun outil ne le fera :
- [ ] Restitution par un lecteur d'écran réel (NVDA, VoiceOver)
- [ ] Comportement au zoom à 200 % et en orientation portrait
- [ ] **Déclaration d'accessibilité** — obligation légale distincte de la conformité technique
- [ ] Brancher le script d'audit dans la CI, une fois la pile Docker validée

### 10 · RGPD
- [x] **CGU et politique de confidentialité** mises à jour sur les contenus générés : article 5
      dédié, responsabilité éditoriale de l'utilisateur rappelée, et mention explicite qu'aucun
      contenu n'est transmis à un service tiers
- [ ] Consentement **distinct** dédié à l'usage de l'IA
- [ ] Export des données et suppression de compte par l'utilisateur (art. 15 et 17)

### 11 · Éco-conception CP 6
- [x] **Alléger le CSS** : daisyUI retiré (45,6 Ko pour cinq classes utilisées), `legal-style.css` mort supprimé. **79,9 Ko → 34,4 Ko bruts (−57 %)**, 13,7 → 7,0 Ko gzip. Le menu mobile, seule mécanique qui en dépendait, est désormais piloté par l'état du composant — ce qui lui apporte au passage `aria-expanded`, la fermeture par Échap et au clic extérieur
- [ ] Vérifier le chargement différé, alléger les dépendances JavaScript, activer la compression GZIP
- [ ] Le bundle JavaScript dépasse 500 Ko : `vite build` le signale à chaque construction. Découpage en morceaux à envisager

### 12 · Déploiement CP 10
- [ ] **Procédure de déploiement** rédigée (environnements test / acceptation / production)
- [ ] **Scripts de déploiement** écrits et documentés
- [ ] ⚠️ **Délai côté serveur WSGI** : `ia_service.py` n'impose plus aucun délai de lecture à l'inférence, volontairement — un délai coupait des générations qui aboutissaient. Acceptable en local mono-utilisateur, mais en production un Ollama qui se bloque après avoir accepté la connexion occuperait un worker indéfiniment. Prévoir `gunicorn --timeout`

### 13 · Livrables d'examen
- [ ] **Dossier de projet** : 40–60 pages + 40 pages d'annexes max ([plan](./docs/plan-dossier-projet.md))
- [ ] **Diaporama de soutenance**
- [ ] **Documentation utilisateur** (PDF ou web)
- [ ] Préparer le **questionnaire professionnel** : documentation technique en anglais, 2 QCM en français + 2 questions ouvertes en anglais (niveau B1)
- [ ] Préparer une **démarche de résolution de problème** à raconter : un bug réel, le diagnostic, les tests, la correction (critère de performance de CP2, CP3, CP8, CP11)
  → **le matériau existe maintenant** : la campagne de performance IA du §14 est exactement ce format. Un symptôme (« la génération prend 5 minutes »), six hypothèses dont **deux fausses que la mesure a écartées**, et la vraie cause trouvée en dernier. Il y a de quoi montrer qu'on sait mesurer avant de corriger — ce que le jury cherche.

### 14 · Performance de la génération IA — ✅ résolu, documenté

Campagne de diagnostic, PR #5 à #10. Symptôme de départ : une correction de
vingt caractères prenait **plus de cinq minutes**, ou se terminait en `502`.

Les hypothèses, dans l'ordre où elles ont été testées :

| Hypothèse | Verdict |
|---|---|
| Un délai de 60 s coupait des générations valides | ✅ vrai — retiré, compteur de temps estimé affiché à la place |
| `stream: true` envoyé sans lire le flux NDJSON | ✅ vrai — `response.json()` échouait **après** le bloc de gestion d'erreurs, donc `500` opaque au bout de toute l'attente |
| Le mode raisonnement de `qwen3:4b` | ✅ vrai — **1 443 jetons générés** pour corriger 21 caractères |
| `OLLAMA_THINK=false` suffit à le désactiver | ❌ **faux** — sans effet sur Ollama 0.35.1 |
| La consigne `/no_think` suffit | ❌ **faux** — lue comme du texte, puis recopiée dans la réponse |
| La machine de développement est trop lente | ❌ **faux** — 53 à 62 jetons/s, tout à fait normal |
| Le chargement du modèle | ✅ **la vraie cause finale** — 426,9 s sur 427,66 s, soit 99,8 % du temps |

Corrections retenues : `qwen2.5:3b` (sans mode raisonnement), `OLLAMA_NUM_CTX`
ramené de 8192 à **4096** (une fenêtre surdimensionnée alourdit le chargement :
20,5 s contre 426,9 s), et `OLLAMA_KEEP_ALIVE=30m` pour ne pas repayer ce
chargement toutes les cinq minutes.

Deux leçons écrites dans `config.py`, `.env.example` et le `README` pour que
l'erreur ne soit pas refaite : **un modèle à raisonnement est le mauvais outil
pour de la réécriture, quelle que soit sa taille**, et **une fenêtre de contexte
généreuse n'est pas une précaution gratuite** — `OLLAMA_NUM_CTX` et
`IA_MAX_CONTENU_LENGTH` se règlent ensemble.

Reste à faire sur ce lot :
- [ ] **Vérifier le préfixe « Corrigé : »** — en ligne de commande, le modèle préfixe sa réponse. Le gabarit de prompt dit « Réponds uniquement avec le texte corrigé, sans commentaire ni introduction », donc ça devrait aller dans l'application, mais ce n'est pas vérifié. Si le préfixe apparaît, c'est le gabarit qu'il faut durcir (~15 min)
- [ ] **Le temps estimé ne compte pas le chargement du modèle**, seulement l'inférence. Le premier appel après une longue pause dépasse donc l'estimation et bascule sur « plus long que prévu » : correct, mais peu informatif. Distinguer les deux phases demanderait de diffuser la progression réelle au navigateur (SSE), ce qui change le contrat d'API
- [ ] **Journaliser les mesures qu'Ollama renvoie** (durée de chargement, de lecture, de génération, débit, modèle et fenêtre réellement actifs). Le diagnostic ci-dessus a demandé quatre allers-retours de commandes PowerShell alors qu'Ollama donne ces chiffres à chaque appel. Un prototype a été écrit puis abandonné ; il manquait la configuration de journalisation dans `create_app`, Flask n'émettant pas les messages `INFO` hors mode debug. Rejoint « supervision » listé comme reste à faire dans `05-architecture-logicielle.md`

Piège de méthode rencontré, à garder en tête :
- `Claude outputs/env` et `env-1` sont des **copies figées dans le dépôt**, pas le `.env` vivant. Il faut les recopier dans `backend/.env` après chaque modification de configuration, sinon les réglages du poste restent en arrière — c'est ce qui a fait croire à une régression. Et `Claude outputs/env` n'a **pas** de `SECRET_KEY` : l'application ne démarre pas avec celui-là
- La **première** exécution après un `ollama pull` lit les poids depuis le disque *pendant* la génération et donne un débit trompeur : 1,96 jetons/s à froid contre 38,47 à chaud, même machine et même modèle. Toujours mesurer deux fois

### 15 · Hygiène du dépôt
- [ ] Supprimer les 4 branches obsolètes encore sur le dépôt distant :
      `claude/beautiful-clarke-6znlbn`, `claude/capacites-concretes-y1w66f`,
      `claude/clever-maxwell-r7sk09`, `claude/gracious-goldberg-0o31o8` (tout leur contenu utile
      est dans `main`)
- [x] Ajouter `Claude outputs/` au `.gitignore` — fait avec le lot sécurité du §8

### 16 · Traçabilité des contenus générés par IA — ✅ fait

Règlement (UE) 2024/1689 (AI Act), art. 50 : les contenus générés par une IA doivent rester
identifiables. Une ligne de la table `ia` attestait qu'une proposition avait été **produite** ;
rien n'attestait qu'elle avait été **acceptée**. Une proposition rejetée et une proposition versée
au document étaient indiscernables en base — la trace ne valait donc rien.

- [x] **Trois colonnes sur `ia`** : `insere`, `position_debut`, `insere_at`, plus le `CHECK`
      `ck_ia_insertion` qui interdit une insertion sans horodatage. La contrainte est portée par le
      SGBD, pas par l'application : une écriture directe ne peut pas créer l'état incohérent
- [x] **`POST /documents/<id>/ia/<id_ia>/insertion`**, idempotente : un double clic ou un rejeu de
      requête ne réécrit pas l'horodatage d'origine, qui est la donnée que la trace conserve.
      Propriété du document **et** de l'interaction vérifiées dans le `WHERE`, `404` et non `403`
      pour ne pas confirmer l'existence d'un identifiant
- [x] **Aucun marquage dans le Markdown** : des balises seraient détruites à la première réécriture
      et pollueraient l'export. La trace vit à côté du document, et la réconciliation se fait à
      l'ouverture en cherchant `content_after` dans le contenu courant
- [x] **Historique enrichi** : `/historique` expose `insere`, `position_debut` et `insere_at`
- [x] **CGU et politique de confidentialité** complétées (voir §10)
- [x] **10 tests d'intégration** (`test_ia_tracabilite.py`, TI-60 à TI-69) : pose de la trace,
      idempotence, interaction d'un tiers, document d'un autre compte, `position_debut` mal typée
      ou booléenne
- [x] **Migration SQL** livrée (`migration_tracabilite_ia.sql`) et `schema_mysql.sql` aligné

Reste à faire sur ce lot :
- [x] **Migration rejouée contre un vrai MySQL 8.4** (05/10/2026), sur une base dont les colonnes
      avaient été retirées pour simuler l'état d'avant, et avec le compte `helpmedraft_migration` :
      colonnes et types conformes, `ck_ia_insertion` recréée, 0 ligne incohérente. La contrainte
      refuse bien une trace marquée sans horodatage (`ERROR 3819`)
- [ ] Décider si la trace doit être exposée à l'export du document ou rester interne à
      l'application

---

## Priorité suggérée

1. ~~Documents de conception (§1)~~ — ✅ fait
2. ~~Gestion de projet (§3)~~ — ✅ fait, sauf les comptes rendus réels
3. ~~Tests + plan de tests (§2)~~ — ✅ fait, sauf tests système et acceptation
4. ~~Clés commitées, build cassé, contraste AA (§5, §8, §9)~~ — ✅ fait
5. ~~Valider la pile Docker~~ — ✅ fait le 05/10/2026 : tests système (7/10), contrôles MySQL 8.4,
   sauvegarde, droits et migration de traçabilité sont vérifiés d'un coup. Restent les tests de
   charge, et TS-04 à jouer avec Ollama démarré
6. ~~Le reste de l'accessibilité (§9)~~ — ✅ fait et mesuré, ne restent que les contrôles qu'aucun outil ne fait (lecteur d'écran, zoom 200 %, déclaration d'accessibilité)
7. **BDD, NoSQL, sécurité** (§6 à §8)
8. **Dossier de projet et diaporama** (§13) — en dernier, ils agrègent tout le reste. Les §2 et §14 fournissent la démarche de résolution de problème attendue
