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
| Protection XSS (DOMPurify) + test | `MarkdownEditor.vue`, `test_xss.mjs` | 2 |
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

### 2 · Tests automatisés et plan de tests ⭐ CP 2, 3, 8, 9
- [ ] **pytest** côté backend (les tests actuels sont des scripts lancés à la main, pas une suite)
- [ ] **Vitest** côté frontend (absent de `package.json`)
- [ ] Tests unitaires par couche : composants métier (CP3), composants d'accès aux données (CP8), composants d'interface (CP2)
- [ ] **Plan de tests** : intégration, non-régression, système, sécurité, charge
- [ ] **Environnement de tests** dédié (critère de performance de CP9)
- [ ] **Jeu d'essai de la fonctionnalité la plus représentative** : entrée / attendu / obtenu + analyse des écarts
- [ ] **Dossier de compte rendu de tests**

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
- [ ] Rattacher ou supprimer les 10 tickets hors epic (`KAN-1` à `KAN-6`, `KAN-89` à `KAN-92`)
- [ ] Rouvrir `KAN-10` et `KAN-13`, clos alors que des tâches restent ouvertes
- [ ] Fermer `KAN-99` : DOMPurify 3.4.16 dépasse déjà le correctif demandé
- [ ] Reporter les échéances des epics (toutes dépassées, de 76 à 129 jours)

### 4 · Conteneurisation CP 1, 11
- [ ] `docker-compose.yml` est **vide (0 octet)** — CP1 exige que « les conteneurs implémentent les services requis »
- [ ] `backend/Dockerfile` et `frontend/Dockerfile`
- [ ] Stack composée : backend + frontend + BDD (+ Ollama)

### 5 · CI/CD et qualité de code CP 11
- [ ] Aucun `.github/workflows/` → pipeline GitHub Actions : lint, `vue-tsc`, tests back, tests front, build
- [ ] **Outil de qualité de code** : Ruff côté Python, ESLint côté Vue
- [ ] Savoir **interpréter les rapports de CI** (critère de performance)

### 6 · Base de données ⭐ CP 7
- [ ] `schema_mysql.sql` existe mais l'app tourne sur SQLite → trancher : migrer vers MySQL (recommandé par le CDC) ou argumenter le choix
- [ ] **Jeu d'essai complet** dans une base de test
- [ ] **Procédure de sauvegarde / restauration**
- [ ] **Utilisateurs SGBD et droits d'accès** (critère de performance : sécurité et confidentialité)
- [ ] Aligner ORM et SQL : `ia.id_document` sans `ondelete` côté ORM alors que le SQL porte `ON DELETE CASCADE`

### 7 · NoSQL ⭐ CP 8
- [ ] L'intitulé de CP8 est « SQL **et** NoSQL » et aucun composant NoSQL n'existe → ajouter un usage justifié (cache Redis des réponses IA, journal des appels IA en Mongo) ou préparer un argumentaire solide pour le jury
- [ ] **Transactions et conflits d'accès** : implémenter ou documenter (critère de performance)

### 8 · Sécurité
- [ ] **Chiffrement des données sensibles au repos** (exigé par le CDC)
- [ ] Configurer `SECRET_KEY` Flask
- [ ] **Rapport d'audit de sécurité**
- [ ] Rejouer le test XSS de bout en bout dans le navigateur
- [ ] Documenter la **veille sécurité** : vulnérabilités trouvées, failles corrigées (attendu explicite du dossier de projet)

### 9 · Accessibilité RGAA CP 2, 5
- [ ] Passe complète : contrastes, navigation clavier, balises ARIA, focus visible
- [ ] Audit **Lighthouse / WAVE** + **rapport d'audit d'accessibilité**

### 10 · RGPD
- [ ] Consentement **distinct** dédié à l'usage de l'IA
- [ ] Export des données et suppression de compte par l'utilisateur (art. 15 et 17)

### 11 · Éco-conception CP 6
- [ ] Vérifier le chargement différé, alléger les dépendances, activer la compression GZIP

### 12 · Déploiement CP 10
- [ ] **Procédure de déploiement** rédigée (environnements test / acceptation / production)
- [ ] **Scripts de déploiement** écrits et documentés

### 13 · Livrables d'examen
- [ ] **Dossier de projet** : 40–60 pages + 40 pages d'annexes max ([plan](./docs/plan-dossier-projet.md))
- [ ] **Diaporama de soutenance**
- [ ] **Documentation utilisateur** (PDF ou web)
- [ ] Préparer le **questionnaire professionnel** : documentation technique en anglais, 2 QCM en français + 2 questions ouvertes en anglais (niveau B1)
- [ ] Préparer une **démarche de résolution de problème** à raconter : un bug réel, le diagnostic, les tests, la correction (critère de performance de CP2, CP3, CP8, CP11)

---

## Priorité suggérée

1. **Documents de conception** (§1) — le jury les lit avant tout, et ils couvrent trois compétences obligatoires.
2. **Tests + plan de tests** (§2) — compétence obligatoire, et verrou pour la CI.
3. **Gestion de projet** (§3) — peu de travail, compétence obligatoire quasi vide aujourd'hui.
4. **Docker + CI/CD** (§4, §5) — rapides, nourrissent l'entretien technique sur CP1, 10, 11.
5. **BDD, NoSQL, sécurité, accessibilité** (§6 à §9).
6. **Dossier de projet et diaporama** (§13) — en dernier, ils agrègent tout le reste.
