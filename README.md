# HelpMeDraft

Application web de rédaction assistée par IA pour les documents professionnels (emails, notes, rapports).

Projet fil rouge réalisé dans le cadre du titre professionnel **Concepteur Développeur d'Applications (CDA)** — CD2IA 2025/2026, Metz Numeric School. Commanditaire fictif : **LexiCorp**, éditeur d'outils de gestion documentaire pour les PME.

---

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Architecture du dépôt](#architecture-du-dépôt)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Variables d'environnement](#variables-denvironnement)
- [Lancement](#lancement)
- [API](#api)
- [Modèle de données](#modèle-de-données)
- [Sécurité](#sécurité)
- [RGPD et accessibilité](#rgpd-et-accessibilité)
- [État d'avancement](#état-davancement)
- [Auteur](#auteur)

---

## Fonctionnalités

**Gestion utilisateur**
- Inscription avec consentement RGPD explicite, connexion, déconnexion
- Réinitialisation de mot de passe par email (token à usage unique, valable 1 h)
- Deux rôles : `user` et `admin`

**Éditeur intelligent**
- Éditeur Markdown (CodeMirror 6) avec prévisualisation
- Enregistrement automatique
- Trois actions IA : **reformuler**, **corriger**, **compléter**
- Portée au choix : sélection de texte ou document entier
- Consigne libre transmise au modèle, insertion ou remplacement du résultat dans l'éditeur

**Gestion documentaire**
- CRUD documents, organisation en dossiers, filtrage par dossier
- Statuts : `brouillon`, `a_relire`, `termine`
- Historique de chaque interaction IA (contenu avant/après, tokens consommés)

**Back-office administrateur**
- Liste paginée des utilisateurs avec nombre de documents et d'appels IA
- Modification du rôle et du quota IA quotidien, suppression de compte
- Statistiques globales : utilisateurs, documents par statut, appels IA sur 24 h et 7 jours

---

## Stack technique

| Domaine | Technologie |
|---|---|
| Front-end | Vue 3, TypeScript, Vite, Tailwind CSS 4, daisyUI, Pinia, Vue Router |
| Éditeur | CodeMirror 6 (`@codemirror/lang-markdown`) + `marked` |
| Back-end | Python 3.11+, Flask 3, SQLAlchemy 2 |
| Base de données | SQLite en développement (cible MySQL en production) |
| IA | **Ollama en local** (`llama3.1`) — aucune donnée n'est envoyée à un service tiers |
| Authentification | JWT HS256 (access token 15 min) + refresh token en cookie `httpOnly` avec rotation |
| Emailing | Flask-Mail, sandbox Mailtrap en développement |

> **Choix technique — IA locale.** Le cahier des charges autorise OpenAI *ou* un LLM local. Ollama a été retenu : les contenus rédigés par les utilisateurs ne quittent jamais l'infrastructure, ce qui répond directement à l'exigence RGPD « aucune donnée personnelle envoyée à un tiers sans anonymisation ». Aucune clé API n'est donc nécessaire.

---

## Architecture du dépôt

```
HelpMeDraft/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # factory create_app(), CORS, blueprints, handler 429
│   │   ├── config.py            # configuration lue depuis .env
│   │   ├── extension.py         # instances Mail et Limiter
│   │   ├── routes/              # couche HTTP (validation + codes de retour)
│   │   │   ├── auth_routes.py   # inscription, login, refresh, logout, reset password
│   │   │   ├── document_route.py
│   │   │   ├── dossier_route.py
│   │   │   ├── ia_route.py      # génération IA + quota + historique
│   │   │   └── admin_route.py   # back-office, réservé au rôle admin
│   │   └── services/            # logique métier, sans dépendance à Flask/HTTP
│   │       ├── auth_service.py  # hachage, JWT, rotation des refresh tokens
│   │       ├── email_service.py
│   │       └── ia_service.py    # prompt engineering + appel Ollama
│   ├── database/
│   │   └── db.py                # modèles SQLAlchemy et moteur
│   ├── utilitaires.py
│   ├── run.py                   # point d'entrée de développement
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── index.ts             # routeur et guards (auth / guest / admin)
│       ├── views/               # une vue par route
│       ├── components/          # MarkdownEditor, Nav, Footer
│       ├── services/            # clients HTTP (axios) par domaine
│       ├── stores/auth.ts       # état d'authentification (Pinia)
│       └── types/               # types partagés front/API
├── .env.example
└── docker-compose.yml
```

Le backend suit une séparation en trois couches : **routes** (validation des entrées et réponses HTTP) → **services** (métier, testables isolément) → **database** (persistance). Cette séparation est ce qui rend les composants métier testables sans serveur Flask.

---

## Prérequis

- **Python** 3.11 ou supérieur
- **Node.js** 20 ou supérieur, avec **pnpm**
- **[Ollama](https://ollama.com)** installé et lancé localement
- Un compte [Mailtrap](https://mailtrap.io) (sandbox gratuite) pour tester les emails

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <url-du-depot>
cd HelpMeDraft---projet-fil-rouge
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Les tables SQLite sont créées automatiquement au premier import de `database/db.py` ; aucune migration à lancer en développement.

### 3. Frontend

```bash
cd frontend
pnpm install
```

### 4. Modèle IA

```bash
ollama pull llama3.1
ollama serve        # écoute sur http://localhost:11434
```

---

## Variables d'environnement

Copier `.env.example` en `backend/.env` puis renseigner les valeurs.

| Variable | Rôle | Obligatoire |
|---|---|---|
| `JWT_SECRET_KEY` | Clé de signature des access tokens | **Oui** |
| `MAIL_SERVER`, `MAIL_PORT` | Serveur SMTP | Oui |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | Identifiants SMTP | Oui |
| `MAIL_USE_TLS`, `MAIL_USE_SSL` | Chiffrement SMTP | Non (défauts fournis) |
| `MAIL_DEFAULT_SENDER` | Expéditeur des emails | Oui |
| `OLLAMA_URL` | URL du serveur Ollama | Non (`http://localhost:11434`) |
| `OLLAMA_MODEL` | Modèle utilisé | Non (`llama3.1`) |
| `FRONTEND_URL` | Base du lien de réinitialisation | Non (`http://localhost:5173`) |

Générer une clé JWT robuste :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

> Le fichier `.env` est exclu par `.gitignore` et ne doit jamais être commité.

---

## Lancement

Deux terminaux, plus Ollama en arrière-plan.

```bash
# Terminal 1 — backend (depuis backend/, l'environnement virtuel activé)
python run.py
# → http://localhost:5000
```

```bash
# Terminal 2 — frontend (depuis frontend/)
pnpm dev
# → http://localhost:5173
```

> Le backend doit être lancé **depuis le dossier `backend/`** : les imports (`utilitaires`) et le chemin de la base SQLite sont relatifs au répertoire courant.

Pour promouvoir le premier compte en administrateur, passer son champ `role` à `admin` directement en base (`backend/HelpMeDraft.db`).

---

## API

Base : `http://localhost:5000`. Toutes les routes hors `/auth` exigent l'en-tête `Authorization: Bearer <access_token>`.

### Authentification

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/auth/register` | Inscription (consentement RGPD requis) — 3 requêtes/heure |
| `POST` | `/auth/login` | Connexion — 5 requêtes/minute |
| `POST` | `/auth/refresh` | Renouvellement de l'access token (cookie `refresh_token`) |
| `POST` | `/auth/logout` | Déconnexion et révocation de la session |
| `GET` | `/auth/me` | Profil de l'utilisateur courant |
| `POST` | `/auth/forgot-password` | Envoi du lien de réinitialisation — 3 requêtes/heure |
| `POST` | `/auth/reset-password` | Définition du nouveau mot de passe |

### Documents et dossiers

| Méthode | Route | Description |
|---|---|---|
| `GET` / `POST` | `/documents` | Liste paginée (filtrable par dossier) / création |
| `GET` / `PUT` / `DELETE` | `/documents/<id>` | Lecture / mise à jour / suppression |
| `GET` | `/documents/stats` | Statistiques personnelles |
| `GET` / `POST` | `/dossiers` | Liste avec compteurs / création |
| `DELETE` | `/dossiers/<id>` | Suppression (les documents repassent à `id_dossier` nul) |

### IA

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/documents/<id>/ia/generer` | Génération. Corps : `type_action` (`reformuler` \| `corriger` \| `completer`), `scope` (`selection` \| `document`), `contenu`, `instructions` (facultatif). Renvoie `429` si le quota de 24 h est atteint, `502` si Ollama est injoignable |
| `GET` | `/documents/<id>/ia/historique` | Historique des interactions du document |

### Administration — rôle `admin` requis

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/admin/users` | Liste paginée avec compteurs d'usage |
| `PATCH` | `/admin/users/<id>` | Modification de `role` et `quota_daily_limit` |
| `DELETE` | `/admin/users/<id>` | Suppression d'un compte |
| `GET` | `/admin/stats` | Statistiques globales |

---

## Modèle de données

Sept entités, identifiants UUID, suppression en cascade depuis `user`.

| Table | Rôle |
|---|---|
| `user` | Compte, rôle, quota IA quotidien (20 par défaut) |
| `document` | Titre, contenu, format, statut, rattachement à un dossier |
| `dossier` | Regroupement de documents d'un utilisateur |
| `ia` | Journal des appels IA : action, contenu avant/après, tokens consommés |
| `consentement` | Traçabilité des consentements RGPD (type, acceptation, date) |
| `user_session` | Refresh tokens, expiration, drapeau de révocation |
| `password_reset` | Tokens de réinitialisation hachés, expiration, usage unique |

Le `PRAGMA foreign_keys=ON` est activé à chaque connexion : SQLite n'applique pas les contraintes de clé étrangère par défaut, et sans lui le `ondelete="SET NULL"` de `document.id_dossier` ne serait jamais exécuté.

---

## Sécurité

Mesures en place :

- **Mots de passe** hachés avec bcrypt (sel automatique). Politique : 8 caractères minimum, une majuscule, une minuscule, un chiffre.
- **Access token** JWT HS256, durée de vie 15 minutes, transmis en en-tête `Authorization`.
- **Refresh token** en cookie `httpOnly` limité au chemin `/auth`, avec **rotation à chaque usage** : la réutilisation d'un token déjà consommé est interprétée comme un vol et révoque toutes les sessions de l'utilisateur.
- **Réinitialisation de mot de passe** : seul le hash SHA-256 du token est stocké, expiration à 1 h, usage unique, révocation de toutes les sessions après changement.
- **Anti-énumération de comptes** : `/auth/forgot-password` répond de façon identique que l'email existe ou non.
- **Rate-limiting** sur les routes sensibles, réponse `429` normalisée.
- **Contrôle d'accès** : chaque requête sur un document ou un dossier vérifie l'appartenance à l'utilisateur courant ; les routes `/admin` vérifient le rôle en base à chaque appel, pas dans le JWT.
- **Garde-fous back-office** : un administrateur ne peut ni se retirer ses droits ni supprimer son propre compte.
- **Injections SQL** : aucune requête construite par concaténation, l'ORM SQLAlchemy paramètre systématiquement.
- **CORS** restreint à l'origine du frontend.
- **Validation d'entrée** systématique : types, longueurs, valeurs autorisées (`type_action`, `scope`, `status`, `format`, `role`, bornes de quota et de pagination).

Points ouverts, à traiter avant toute mise en production :

- [ ] `JWT_SECRET_KEY` a une valeur de repli dans `config.py` — doit lever une erreur au démarrage si absente
- [ ] Cookie du refresh token en `secure=False` — à conditionner à l'environnement
- [ ] Prévisualisation Markdown injectée via `v-html` sans assainissement (`marked` ne filtre pas le HTML) — ajouter DOMPurify
- [ ] Protection CSRF à formaliser
- [ ] Chiffrement des données sensibles au repos

---

## RGPD et accessibilité

**RGPD**
- Consentement explicite recueilli à l'inscription et tracé en base (table `consentement`)
- Inférence IA entièrement locale : aucun contenu utilisateur transmis à un service tiers
- Pages Mentions légales, CGU et Politique de confidentialité intégrées à l'application
- Reste à faire : consentement distinct dédié à l'usage de l'IA, export des données et suppression de compte à l'initiative de l'utilisateur

**Accessibilité (RGAA)**
- Chargement différé des routes, navigation cohérente
- Reste à faire : couverture ARIA complète, vérification des contrastes et de la navigation clavier, audit Lighthouse / WAVE et rapport associé

---

## État d'avancement

| Lot | État |
|---|---|
| Authentification et gestion de compte | Terminé |
| CRUD documents et dossiers | Terminé |
| Intégration IA (Ollama) et quotas | Terminé |
| Back-office administrateur | Terminé |
| Pages légales | Terminé |
| Tests automatisés (pytest, Vitest) et plan de test | À faire |
| Conteneurisation Docker | À faire (`docker-compose.yml` vide) |
| Pipeline CI/CD | À faire |
| Migration vers MySQL et scripts SQL | À faire |
| Audit accessibilité et sécurité | À faire |
| Documentation utilisateur et journal de veille | À faire |

---

## Auteur

**Ophélie Bellissens** — CDA / CD2IA, Metz Numeric School

- Portfolio : [opheliebellissens.netlify.app](https://opheliebellissens.netlify.app)
- LinkedIn : [ophelie-bellissens-dev](https://linkedin.com/in/ophelie-bellissens-dev)

Projet pédagogique, non destiné à un usage commercial.
