# Reste à faire — HelpMeDraft

Croisement entre le [cahier des charges](./docs/cahier-des-charges.md) et l'état du dépôt.
`*` = livrable **obligatoire pour le passage du titre**.

---

## ✅ Déjà couvert

| Exigence du CDC | Où |
|---|---|
| Inscription / connexion / déconnexion / reset mot de passe | `backend/app/routes/auth_routes.py`, vues `LoginView` · `RegisterView` · `ForgotPasswordView` · `ResetPasswordView` |
| Rôles utilisateur / administrateur | `admin_route.py` (`require_admin`), `AdminView.vue` |
| Éditeur Markdown + commandes IA | `MarkdownEditor.vue`, `DocumentEditorView.vue` |
| CRUD documents, dossiers, historique IA | `document_route.py`, `dossier_route.py`, `ia_route.py` |
| IA locale (Ollama) + prompt engineering | `services/ia_service.py` |
| Quota IA journalier | `ia_route.py` (`quota_daily_limit`, fenêtre 24 h) |
| Stats d'usage admin | `admin_route.py` (`/stats`) |
| Protection XSS (DOMPurify) + tests | `MarkdownEditor.vue`, `frontend/test_xss.mjs` |
| Tokens : hash SHA-256 en base, rotation, anti-rejeu, cookie HttpOnly/SameSite | `auth_routes.py`, `backend/test_securite.py` |
| Consentement RGPD tracé en base | table `consentement` |
| `.env.example` | racine du dépôt |
| Maquettes + captures | `docs/maquettes/`, `docs/captures/` |
| Journal de veille `*` | `docs/veille-helpmedraft.html` |

---

## ⬜ À faire

### 1 · Tests automatisés `*`
- [ ] Mettre en place **pytest** côté backend (les tests actuels sont des scripts `python test_*.py`, pas une suite).
- [ ] Mettre en place **Vitest** côté frontend (absent de `frontend/package.json`).
- [ ] Couvrir : auth, CRUD documents/dossiers, quota IA, garde-fous admin.
- [ ] Rédiger le **plan de test manuel** (scénarios, résultats attendus, traçabilité).

### 2 · Conteneurisation
- [ ] `docker-compose.yml` est **vide (0 octet)**.
- [ ] Écrire `backend/Dockerfile` et `frontend/Dockerfile`.
- [ ] Composer : backend + frontend + BDD (+ Ollama).

### 3 · CI/CD
- [ ] Aucun `.github/workflows/`. Ajouter un pipeline GitHub Actions : lint, `vue-tsc`, tests back, tests front, build.

### 4 · Base de données
- [ ] `schema_mysql.sql` existe mais l'app tourne sur SQLite. Trancher : migrer vers MySQL (recommandé par le CDC) ou documenter le choix SQLite.
- [ ] Aligner l'ORM et le SQL : `ia.id_document` sans `ondelete` côté ORM alors que le SQL porte `ON DELETE CASCADE`.

### 5 · Accessibilité (RGAA)
- [ ] Passe complète : contrastes, navigation clavier, balises ARIA, focus visible.
- [ ] Audit **Lighthouse / WAVE** + **rapport d'audit d'accessibilité**.

### 6 · Sécurité
- [ ] Chiffrement des données sensibles au repos (exigence explicite du CDC).
- [ ] Configurer `SECRET_KEY` Flask.
- [ ] **Rapport d'audit de sécurité** (le CDC le demande comme livrable).
- [ ] Rejouer le test XSS de bout en bout dans le navigateur.

### 7 · RGPD
- [ ] Consentement **distinct** dédié à l'usage de l'IA.
- [ ] Export des données et suppression de compte à l'initiative de l'utilisateur (art. 15 et 17).

### 8 · Éco-conception
- [ ] Vérifier le chargement différé des routes, alléger les dépendances, activer la compression GZIP.

### 9 · Documentation & soutenance
- [ ] **Dossier projet** `*` : architecture, modèle de données, diagrammes (cas d'usage, séquence, MCD).
- [ ] **Documentation utilisateur** (PDF ou web).
- [ ] **Diaporama de soutenance** `*`.

---

## Priorité suggérée

1. Tests automatisés + plan de test `*` — livrable titre, et bloque le reste.
2. Dossier projet + diaporama `*` — livrables titre.
3. Docker + CI/CD — rapides, débloquent le déploiement.
4. Audits accessibilité et sécurité.
5. RGPD (export/suppression), chiffrement au repos, éco-conception.
