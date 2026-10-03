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
| IA locale (Ollama) + prompt engineering | `services/ia_service.py` | 3 |
| Quota IA journalier | `ia_route.py` (fenêtre 24 h) | 3 |
| Stats d'usage admin | `admin_route.py` (`/stats`) | 3 |
| Architecture en couches effective | `routes/` → `services/` → `database/` + SPA découplée | 6 |
| Modèle de données (7 entités) + script MySQL | `database/db.py`, `schema_mysql.sql` | 7 |
| ORM SQLAlchemy, requêtes paramétrées, validation des entrées | `db.py`, routes | 8 |
| Protection XSS (DOMPurify) + 13 tests | `MarkdownEditor.vue`, `markdown-sanitization.spec.ts` | 2 |
| Suite de tests automatisés (282 tests) | `backend/tests/`, `frontend/src/**/__tests__/` | 2, 3, 8, 9 |
| Performance de la génération IA : modèle, fenêtre de contexte et maintien en mémoire dimensionnés sur mesures | `config.py`, `ia_service.py` | 3, 11 |
| Annulation d'une génération en cours + temps estimé affiché | `DocumentEditorView.vue`, `utils/iaEstimation.ts` | 2 |
| Tokens hashés, rotation, anti-rejeu, cookie HttpOnly/SameSite | `auth_routes.py`, `test_securite.py` | 3 |
| Consentement RGPD tracé en base | table `consentement` | 5, 7 |
| Maquettes et captures | `docs/maquettes/`, `docs/captures/` | 5 |
| Journal de veille (3 périmètres, avril → octobre 2026) | `docs/veille/journal-de-veille.md` | transversale |
| Suivi de projet sur données Jira réelles | `docs/gestion-de-projet.md` | 4 |
| Git / GitHub, branches, PR | — | 1, 4 |
| `.env.example` | racine | 10 |

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
**282 tests, tous au vert** (228 pytest, 54 Vitest), 95 % de couverture backend.
Voir [`docs/plan-de-tests.md`](./docs/plan-de-tests.md), [`backend/tests/README.md`](./backend/tests/README.md), [`frontend/TESTS.md`](./frontend/TESTS.md).

- [x] **pytest** côté backend : unitaires, intégration, sécurité
- [x] **Vitest** côté frontend
- [x] Tests unitaires par couche : métier (CP3), accès aux données (CP8), interface (CP2)
- [x] **Plan de tests** complet : 7 niveaux, ~90 cas, traçabilité des 10 règles de gestion
- [x] **Environnement de tests** hermétique : base en mémoire, aucun appel réseau
- [x] **Jeu d'essai de la fonctionnalité la plus représentative** : 11 cas exécutés, 0 écart
- [x] **Compte rendu d'exécution** : plan de tests §11
- [ ] **Tests système** TS-01 à TS-10 — manuels, attendent la conteneurisation
- [ ] **Tests d'acceptation** avec le formateur
- [ ] **Tests de charge** — après Docker
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

### 4 · Conteneurisation CP 1, 11
- [ ] `docker-compose.yml` est **vide (0 octet)** — CP1 exige que « les conteneurs implémentent les services requis »
- [ ] `backend/Dockerfile` et `frontend/Dockerfile`
- [ ] Stack composée : backend + frontend + BDD (+ Ollama)

### 5 · CI/CD et qualité de code CP 11
- [ ] Aucun `.github/workflows/` → pipeline GitHub Actions : lint, `vue-tsc`, `pytest`, `npm test`, build — **les deux suites de tests sont prêtes à y être branchées**
- [ ] **Outil de qualité de code** : Ruff côté Python, ESLint côté Vue
- [ ] Savoir **interpréter les rapports de CI** (critère de performance)
- [x] **`npm run build` réparé** : les deux imports inutilisés retirés. Plus rien ne bloque la mise en CI
- [x] Prettier passé sur les 6 fichiers non formatés — `prettier --check src/` est propre

### 6 · Base de données ⭐ CP 7
- [ ] `schema_mysql.sql` existe mais l'app tourne sur SQLite → trancher : migrer vers MySQL (recommandé par le CDC) ou argumenter le choix
- [ ] **Jeu d'essai complet** dans une base de test
- [ ] **Procédure de sauvegarde / restauration**
- [ ] **Utilisateurs SGBD et droits d'accès** (critère de performance : sécurité et confidentialité)
- [ ] Aligner ORM et SQL : `ia.id_document` sans `ondelete` côté ORM alors que le SQL porte `ON DELETE CASCADE`

### 7 · NoSQL ⭐ CP 8
- [ ] L'intitulé de CP8 est « SQL **et** NoSQL » et aucun composant NoSQL n'existe → ajouter un usage justifié (cache Redis des réponses IA, journal des appels IA en Mongo) ou préparer un argumentaire solide pour le jury
- [ ] **Transactions et conflits d'accès** : implémenter ou documenter (critère de performance)

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
- [x] `KAN-98` contrainte SQL du quota alignée sur l'API + script de migration
- [x] `KAN-94` énumération à l'inscription : **risque accepté**, argumenté au §4.1 du rapport
- [x] Test XSS rejoué, et transformé en 13 tests automatisés
- [x] Veille sécurité documentée
- [x] **Ajouter `SECRET_KEY` au `backend/.env`** — fait : `config.py` lève une `RuntimeError` au démarrage sans elle, et l'application démarre
- [x] `KAN-100` **relever la version d'Ollama** — fait : **0.35.1**, au-dessus du seuil de 0.18 fixé au §4.2 du rapport d'audit
- [x] **Clés commitées** : les deux copies de `.env` retirées du dépôt, clés **régénérées**, et `.gitignore` complété (`.env.*`, `!.env.example`, `Claude outputs/`) — les quatre cas d'exclusion vérifiés
- [ ] `KAN-100` Ollama : restreindre l'écoute à `127.0.0.1` (`OLLAMA_HOST=127.0.0.1:11434`)
- [ ] **Chiffrement des données au repos** — 3 options chiffrées au §5.1 du rapport, à arbitrer
- [ ] `KAN-102` épingler les dépendances transitives (Werkzeug non épinglée)

### 9 · Accessibilité RGAA CP 2, 5 — 🔄 le gros du volume est traité
Voir [`docs/audit-accessibilite.md`](./docs/audit-accessibilite.md). Audit réel sur les 16 écrans : **120 occurrences sur 3 règles**, dont 117 dues à une seule couleur.

- [x] **Rapport d'audit d'accessibilité** : axe-core sur l'application démarrée + contrôles manuels
- [x] **Assombrir `#E0533C` en `#C4341C`** — fait, 199 occurrences dans 19 fichiers. Mesuré avec axe-core sur les 10 écrans publics : **64 violations de contraste avant, 0 après**. Les teintes de survol suivent (`#A72C18`), sans quoi le survol serait devenu plus clair que l'état normal
- [ ] **Repasser axe-core sur les écrans authentifiés** (tableau de bord, documents, éditeur, back-office) : non couverts par la mesure ci-dessus, faute de session. C'est ce qui reste de l'écart entre les 64 violations mesurées et les 120 du rapport
- [ ] Étiquette sur le champ de quota du back-office (seul constat *critique*)
- [ ] `aria-label` sur la zone CodeMirror
- [ ] Titre de page distinct par route (les 16 écrans partagent le même)
- [ ] Lien d'évitement (absent des 16 écrans)
- [ ] Règle `:focus-visible` globale (22 éléments sans focus visible, dont 16 sur Modèles)
- [ ] Corriger le `h3` du pied de page (saut de niveau sur 5 écrans)
- [ ] `<main>` sur l'accueil, `h1` sur Nouveau document
- [ ] Remplissage vertical des 13 cibles sous 24 px (WCAG 2.2, anticipation RGAA 5)

**Total estimé : ~3 h 30**, dont 1 h pour 97 % du volume.

### 10 · RGPD
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
- [ ] Supprimer les branches obsolètes : `claude/beautiful-clarke-6znlbn`, `claude/capacites-concretes-y1w66f`, `claude/gracious-goldberg-0o31o8` (tout leur contenu utile est dans `main`)
- [x] Ajouter `Claude outputs/` au `.gitignore` — fait avec le lot sécurité du §8

---

## Priorité suggérée

1. ~~Documents de conception (§1)~~ — ✅ fait
2. ~~Gestion de projet (§3)~~ — ✅ fait, sauf les comptes rendus réels
3. ~~Tests + plan de tests (§2)~~ — ✅ fait, sauf tests système et acceptation
4. ~~Clés commitées, build cassé, contraste AA (§5, §8, §9)~~ — ✅ fait
5. **Docker + CI/CD** (§4, §5) — prochaine étape : rapides, les suites de tests sont prêtes à être branchées, `npm run build` ne bloque plus, et ça nourrit CP1, CP10, CP11 à l'entretien technique
6. **Le reste de l'accessibilité** (§9) — une poignée de corrections courtes, le gros du volume est déjà levé
7. **BDD, NoSQL, sécurité** (§6 à §8)
8. **Dossier de projet et diaporama** (§13) — en dernier, ils agrègent tout le reste. Les §14 et §15 fournissent la démarche de résolution de problème attendue
