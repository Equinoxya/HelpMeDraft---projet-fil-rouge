<div align="center">

# ✍️ HelpMeDraft

### Rédigez vos documents professionnels avec une IA qui ne sort jamais de chez vous.

Emails, notes de service, rapports — un éditeur Markdown augmenté par un modèle de langage **exécuté en local**, sans qu'une ligne de vos contenus ne parte chez un tiers.

<br>

![Statut](https://img.shields.io/badge/statut-en%20développement-f59e0b?style=for-the-badge)
![Vue](https://img.shields.io/badge/Vue-3-42b883?style=for-the-badge&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-6-3178c6?style=for-the-badge&logo=typescript&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/IA-100%25%20locale-7c3aed?style=for-the-badge)

<br>

<img src="docs/captures/C-01-accueil.png" alt="Page d'accueil de HelpMeDraft" width="820">

</div>

---

> [!NOTE]
> **Projet en cours.** HelpMeDraft est le projet fil rouge du titre professionnel **Concepteur Développeur d'Applications (CDA)** — CD2IA 2025/2026, Metz Numeric School. Commanditaire fictif : **LexiCorp**, éditeur d'outils de gestion documentaire pour les PME.
> Le cœur fonctionnel, la suite de tests (344 tests), la conteneurisation et la CI/CD sont en place. Restent les livrables d'examen, une poignée de corrections RGAA et la validation de la pile Docker sur une machine disposant d'un démon — voir [l'état d'avancement](#-état-davancement).

<details>
<summary><b>📑 Sommaire</b></summary>

- [Pourquoi ce projet](#-pourquoi-ce-projet)
- [Fonctionnalités](#-fonctionnalités)
- [Stack technique](#%EF%B8%8F-stack-technique)
- [Architecture du dépôt](#-architecture-du-dépôt)
- [Démarrage rapide](#-démarrage-rapide)
- [Variables d'environnement](#-variables-denvironnement)
- [API](#-api)
- [Modèle de données](#%EF%B8%8F-modèle-de-données)
- [Tests](#-tests)
- [Sécurité](#-sécurité)
- [RGPD et accessibilité](#%EF%B8%8F-rgpd-et-accessibilité)
- [État d'avancement](#-état-davancement)
- [Auteur](#-auteur)

</details>

---

## 💡 Pourquoi ce projet

Les assistants de rédaction existants envoient le texte de l'utilisateur à une API distante. Pour une PME qui rédige des courriers RH, des comptes rendus ou des réponses clients, cela signifie confier des données personnelles à un tiers.

**HelpMeDraft prend le problème à l'envers** : le modèle tourne sur la machine de l'entreprise via [Ollama](https://ollama.com). Aucune clé API, aucune facture au token, aucun transfert hors infrastructure — et une conformité RGPD obtenue par l'architecture plutôt que par une clause contractuelle.

---

## ✨ Fonctionnalités

<table>
<tr>
<td width="50%" valign="top">

### 🔐 Comptes & sessions
- Inscription avec consentement RGPD explicite et tracé
- Connexion / déconnexion, rôles `user` et `admin`
- Réinitialisation du mot de passe par email (token à usage unique, 1 h)
- Refresh token en cookie `httpOnly` avec rotation

</td>
<td width="50%" valign="top">

### 🧠 Éditeur intelligent
- Markdown live (CodeMirror 6) + prévisualisation assainie
- Enregistrement automatique
- 3 actions IA : **reformuler**, **corriger**, **compléter**
- Portée au choix : sélection ou document entier
- Consigne libre transmise au modèle, insertion ou remplacement du résultat
- Annulation d'une génération en cours, temps restant estimé
- **Traçabilité AI Act** : les passages acceptés sont tracés et rappelés à l'ouverture du document

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 📁 Gestion documentaire
- CRUD documents, organisation en dossiers, filtrage
- Statuts `brouillon` · `a_relire` · `termine`
- Historique complet de chaque appel IA (avant / après, tokens, insertion effective)
- Statistiques personnelles

</td>
<td width="50%" valign="top">

### 🛠️ Back-office admin
- Liste paginée des utilisateurs avec compteurs d'usage
- Modification du rôle et du quota IA quotidien
- Suppression de compte, avec garde-fous
- Statistiques globales : comptes, documents par statut, appels IA sur 24 h et 7 jours

</td>
</tr>
</table>

Côté vitrine : pages publiques **Accueil**, **Fonctionnalités**, **Modèles**, **Tarifs**, ainsi que **Mentions légales**, **CGU** et **Politique de confidentialité**.

---

## ⚙️ Stack technique

| Domaine | Technologie |
|---|---|
| 🎨 Front-end | Vue 3 · TypeScript · Vite · Tailwind CSS 4 · Pinia · Vue Router |
| 📝 Éditeur | CodeMirror 6 (`@codemirror/lang-markdown`) + `marked` + `DOMPurify` |
| 🐍 Back-end | Python 3.11+ · Flask 3 · SQLAlchemy 2 |
| 🗄️ Base de données | MySQL 8.4 en conteneur (schéma, droits et sauvegarde : [documentation](docs/exploitation-base-de-donnees.md)) — SQLite en développement et pour les tests |
| 🤖 IA | **Ollama en local** (`qwen2.5:3b`) — aucune donnée envoyée à un service tiers |
| 🔑 Authentification | JWT HS256 (access 15 min) + refresh token `httpOnly` haché, avec rotation |
| ✉️ Emailing | Flask-Mail, sandbox Mailtrap en développement |
| 🧪 Tests | pytest (+ pytest-cov) côté backend, Vitest côté frontend |
| 🔁 CI / CD | GitHub Actions — Ruff, ESLint, Prettier, types, tests, build des deux images |
| 🐳 Conteneurisation | Docker Compose : MySQL 8.4, gunicorn, nginx |

> [!TIP]
> **Choix technique — IA locale.** Le cahier des charges autorisait OpenAI *ou* un LLM local. Ollama a été retenu : les contenus rédigés ne quittent jamais l'infrastructure, ce qui répond directement à l'exigence RGPD « aucune donnée personnelle envoyée à un tiers sans anonymisation ». Aucune clé API n'est donc nécessaire.

---

## 🧱 Architecture du dépôt

```
HelpMeDraft/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # factory create_app(), CORS, blueprints, handler 429
│   │   ├── config.py            # configuration lue depuis .env (fail fast si clé absente)
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
│   │   ├── db.py                # modèles SQLAlchemy et moteur
│   │   ├── schema_mysql.sql     # source de vérité du schéma (monté en initdb)
│   │   ├── migration_*.sql      # 4 migrations, appliquées à la main
│   │   ├── jeu_essai.py         # jeu d'essai reproductible
│   │   └── sauvegarde.sh / restauration.sh
│   ├── tests/                   # 286 tests : unit/, integration/, security/
│   ├── Dockerfile               # gunicorn, utilisateur non privilégié
│   ├── run.py                   # point d'entrée de développement
│   └── requirements.txt         # versions figées (reproductibilité CI)
├── frontend/
│   ├── src/
│   │   ├── index.ts             # routeur et guards (auth / guest / admin)
│   │   ├── views/               # une vue par route
│   │   ├── components/          # MarkdownEditor, Nav, Footer
│   │   ├── services/            # clients HTTP (axios) par domaine
│   │   ├── stores/auth.ts       # état d'authentification (Pinia)
│   │   ├── types/               # types partagés front/API
│   │   └── **/__tests__/        # 58 tests Vitest
│   └── Dockerfile               # build en deux étapes, image finale nginx
├── docs/                        # conception, plan de tests, audits, veille, captures
├── .github/workflows/ci.yml     # backend · frontend · images Docker
├── .env.example
└── docker-compose.yml           # MySQL 8.4 + backend + frontend
```

Le backend suit une séparation stricte en trois couches :

```
routes  →  services  →  database
(HTTP)     (métier)     (persistance)
```

C'est cette séparation qui rend les composants métier testables **sans serveur Flask**.

---

## 🚀 Démarrage rapide

### Prérequis

| | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 20+, avec **pnpm** |
| [Ollama](https://ollama.com) | installé et lancé localement |
| [Mailtrap](https://mailtrap.io) | sandbox gratuite, pour tester les emails |

### 1 · Cloner

```bash
git clone <url-du-depot>
cd HelpMeDraft---projet-fil-rouge
```

### 2 · Backend

```bash
cd backend
python -m venv .venv

source .venv/bin/activate     # macOS / Linux
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
cp ../.env.example .env        # puis renseigner les valeurs (voir ci-dessous)
```

> [!IMPORTANT]
> **Pour un poste de développement, seules `JWT_SECRET_KEY` et `SECRET_KEY` sont à renseigner.**
> Tout le reste a un défaut qui convient. Le même fichier d'exemple sert aux deux modes de
> lancement — en local et en conteneur — et les variables dont la bonne valeur dépend du mode y
> sont **laissées commentées exprès** : `CORS_ORIGINS` et `FRONTEND_URL`. Les décommenter avec la
> valeur du conteneur (`http://localhost:8080`) fait refuser par le navigateur toutes les requêtes
> du serveur Vite, qui tourne sur le port 5173 :
>
> ```
> Access to XMLHttpRequest at 'http://localhost:5000/auth/register'
> from origin 'http://localhost:5173' has been blocked by CORS policy
> ```
>
> Inscription et connexion deviennent alors impossibles. Depuis, le backend **journalise** chaque
> origine refusée au démarrage et à chaque requête, au lieu de laisser chercher.

Les tables SQLite sont créées automatiquement au premier import de `database/db.py` — aucune migration à lancer en développement.

> [!NOTE]
> **Cette création automatique ne vaut QUE pour SQLite.** Sur MySQL, le schéma est la propriété de
> [`backend/database/schema_mysql.sql`](backend/database/schema_mysql.sql), exécuté au premier
> démarrage du conteneur, et l'application n'y crée rien — elle refuse même de démarrer si les
> tables manquent. Deux descriptions concurrentes du même schéma ne peuvent pas faire autorité
> toutes les deux ; voir [l'exploitation de la base](docs/exploitation-base-de-donnees.md).

Pour charger un **jeu d'essai** (4 comptes, 7 documents, 40 appels IA, et les cas limites) :

```bash
python database/jeu_essai.py          # mot de passe commun affiché en fin d'exécution
python database/jeu_essai.py --vider  # purge d'abord les 7 tables
```

### 3 · Frontend

```bash
cd frontend
pnpm install
```

### 4 · Modèle IA

```bash
ollama pull qwen2.5:3b
ollama serve                   # écoute sur http://localhost:11434
```

### 5 · Lancer

Deux terminaux, plus Ollama en arrière-plan.

```bash
# Terminal 1 — backend (depuis backend/, venv activé)
python run.py          # → http://localhost:5000
```

```bash
# Terminal 2 — frontend (depuis frontend/)
pnpm dev               # → http://localhost:5173
```

> [!IMPORTANT]
> Le backend doit être lancé **depuis le dossier `backend/`** : les imports (`utilitaires`) sont relatifs au répertoire courant. Le chemin de la base SQLite, lui, ne l'est plus — il est calculé depuis l'emplacement de `database/db.py` et vaut toujours `backend/HelpMeDraft.db`. Avant, lancer l'application depuis la racine ouvrait une **seconde** base, et les comptes créés d'un côté étaient introuvables de l'autre.

Pour promouvoir le premier compte en administrateur, passer son champ `role` à `admin` directement en base (`backend/HelpMeDraft.db`).

---

## 🐳 Avec Docker

La pile complète — MySQL, API, interface — en une commande :

```bash
cp .env.example .env     # puis renseigner les mots de passe et les deux clés
docker compose up --build
```

> [!NOTE]
> **Pile validée sur un démon Docker réel** le 5 octobre 2026 : MySQL 8.4.11, schéma et droits
> appliqués au premier démarrage, sauvegarde et restauration jouées, 7 des 10 tests système au vert.
> Compte rendu complet, défauts trouvés compris :
> [`docs/validation-docker.md`](docs/validation-docker.md).

| Service | Adresse |
|---|---|
| Interface | http://localhost:8080 |
| API | http://localhost:5000 |
| MySQL | interne à la pile, données dans le volume `db-data` |

### Ce que la pile ne contient pas, et pourquoi

**Ollama reste sur la machine hôte.** Son image pèse plusieurs gigaoctets et le modèle se télécharge séparément : l'embarquer rendrait `docker compose up` inutilisable sur une connexion ordinaire. Le backend l'atteint via `host.docker.internal`. Lancer `ollama serve` sur l'hôte avant la pile.

### Deux points à connaître

> [!IMPORTANT]
> **`VITE_API_URL` est figée à la construction.** Vite remplace `import.meta.env.VITE_*` par des littéraux dans le bundle : changer cette valeur impose de **reconstruire** l'image du frontend, pas seulement de redémarrer le conteneur.
>
> **`CORS_ORIGINS` doit désigner le port du frontend conteneurisé** (8080 par défaut, et non 5173). Si les deux ne concordent pas, le navigateur refuse chaque requête sans qu'aucune erreur n'apparaisse côté serveur — la panne est silencieuse et difficile à diagnostiquer.

### Choix d'implémentation

- **Gunicorn** remplace le serveur de développement de Flask, avec `--timeout 600`. Ce n'est pas du confort : l'appel à Ollama n'impose aucun délai de lecture, et le défaut de gunicorn (30 s) tuerait le worker en pleine inférence.
- **Deux workers**, pas davantage : la limitation de débit de Flask-Limiter compte en mémoire, donc **par worker**. Avec N workers, les seuils de `/auth/login` sont multipliés par N. Un stockage Redis partagé est la vraie correction — elle figure dans la TODO.
- **Image frontend en deux étapes** et **non privilégiée** : Node ne sert qu'à produire les fichiers statiques ; l'image finale (**82,9 Mo mesurés**) ne contient que nginx et le résultat du build, et tourne sous l'uid 101 — le maître nginx compris, ce qui a été vérifié dans le conteneur. L'image nginx officielle lance son maître en root pour se lier au port 80 — la variante *unprivileged* écoute sur 8080 et s'en passe.
- **Repli monopage dans nginx** (`try_files`) : sans lui, recharger `/documents/42` renvoie une 404, l'application ne fonctionnant qu'en navigation interne.

---

## 🔧 Variables d'environnement

Copier `.env.example` en `backend/.env`, puis renseigner :

| Variable | Rôle | Obligatoire |
|---|---|:---:|
| `JWT_SECRET_KEY` | Clé de signature des access tokens | ✅ |
| `APP_ENV` | `development` → cookie sans `Secure` ; toute autre valeur → `Secure` activé | ➖ (`development`) |
| `MAIL_SERVER`, `MAIL_PORT` | Serveur SMTP | ✅ |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | Identifiants SMTP | ✅ |
| `MAIL_DEFAULT_SENDER` | Expéditeur des emails | ✅ |
| `MAIL_USE_TLS`, `MAIL_USE_SSL` | Chiffrement SMTP | ➖ (défauts fournis) |
| `OLLAMA_URL` | URL du serveur Ollama | ➖ (`http://localhost:11434`) |
| `OLLAMA_MODEL` | Modèle utilisé | ➖ (`qwen2.5:3b`) |
| `OLLAMA_THINK` | Mode raisonnement du modèle. **À laisser à `false`** — voir l'avertissement ci-dessous | ➖ (`false`) |
| `OLLAMA_NUM_CTX` | Fenêtre de contexte, en jetons. **Dimensionnée, pas généreuse** — voir l'avertissement ci-dessous | ➖ (`4096`) |
| `OLLAMA_KEEP_ALIVE` | Durée de maintien du modèle en mémoire. Le défaut d'Ollama (5 min) est trop court | ➖ (`30m`) |
| `OLLAMA_CONNECT_TIMEOUT` | Délai pour établir la connexion à Ollama, en secondes. Aucun délai ne borne la génération elle-même | ➖ (`10`) |
| `IA_MAX_CONTENU_LENGTH` | Taille maximale du texte soumis à l'IA, en caractères | ➖ (`3000`) |
| `FRONTEND_URL` | Base du lien de réinitialisation | ➖ (`http://localhost:5173`) |

Générer une clé JWT robuste :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

> [!WARNING]
> `config.py` ne définit **aucune valeur de repli** pour `JWT_SECRET_KEY` : l'application refuse de démarrer sans elle. Le fichier `.env` est exclu par `.gitignore` et ne doit jamais être commité.

> [!IMPORTANT]
> **Ne pas remplacer `OLLAMA_MODEL` par un modèle à raisonnement** (`qwen3`, `deepseek-r1`), même plus petit. Un tel modèle produit un monologue d'analyse avant de répondre, de taille à peu près **constante** : il « réfléchit » autant pour une faute d'orthographe que pour trois pages.
>
> Mesuré sur la même machine, pour corriger `BJR je serai en retar` :
>
> | Modèle | Jetons générés | Débit | Durée |
> |---|---|---|---|
> | `qwen3:4b` | 1 443 | 11,9 j/s | **2 min 01 s** |
> | `qwen2.5:3b` | 9 | 38,5 j/s | **0,27 s** |
>
> Le facteur 440 ne vient pas du matériel mais du travail demandé. Et ce comportement **ne se désactive pas de façon fiable** : sur Ollama 0.35.1, ni `OLLAMA_THINK=false` ni la consigne `/no_think` (depuis retirée du projet, car recopiée dans la réponse) n'ont arrêté le monologue de `qwen3:4b`. Le seul levier qui fonctionne est le choix du modèle.
>
> `OLLAMA_THINK` reste donc à `false` et sans effet sur le modèle par défaut ; `_nettoyer_raisonnement` dans `ia_service.py` garde le filet de sécurité qui empêche un tel monologue d'être proposé pour insertion dans un document.

> [!IMPORTANT]
> **Le chargement du modèle domine le temps de réponse, pas la génération.** Sur une machine de développement, même modèle et même prompt :
>
> | Appel | Total | dont chargement | Inférence |
> |---|---|---|---|
> | à froid | 427,66 s | **426,9 s** | 0,76 s |
> | à chaud | 0,19 s | 0 s | 0,19 s |
>
> Deux réglages en découlent, et ils comptent plus que le reste :
>
> - **`OLLAMA_NUM_CTX` ne doit pas être gonflé « au cas où ».** La fenêtre détermine la taille du cache d'attention alloué au chargement : passer de 4096 à 8192 faisait grimper ce chargement de 20,5 s à 426,9 s sur une machine dont la RAM est juste. Le besoin réel avec `IA_MAX_CONTENU_LENGTH=3000` est d'environ 1 700 jetons, soit une marge de 2,4 à 4096. Les deux valeurs se règlent **ensemble**.
> - **`OLLAMA_KEEP_ALIVE` garde le modèle en mémoire** entre deux appels. Le défaut d'Ollama est de 5 minutes, trop court pour un usage par intermittence. Contrepartie : environ 2 Gio de RAM occupés pendant cette durée.
>
> Conséquence pour l'estimation affichée pendant la génération : elle ne compte **que** l'inférence. Le premier appel après une longue pause dépassera donc l'estimation, et le compteur basculera sur « plus long que prévu » — comportement correct, mais garder la cause en tête.

---

## 🔌 API

Base : `http://localhost:5000`. Toutes les routes hors `/auth` exigent l'en-tête `Authorization: Bearer <access_token>`.

<details open>
<summary><b>🔐 Authentification</b></summary>

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/auth/register` | Inscription (consentement RGPD requis) — 3 req./h |
| `POST` | `/auth/login` | Connexion — 5 req./min |
| `POST` | `/auth/refresh` | Renouvellement de l'access token (cookie `refresh_token`) |
| `POST` | `/auth/logout` | Déconnexion et révocation de la session |
| `GET` | `/auth/me` | Profil de l'utilisateur courant |
| `POST` | `/auth/forgot-password` | Envoi du lien de réinitialisation — 3 req./h |
| `POST` | `/auth/reset-password` | Définition du nouveau mot de passe |

</details>

<details>
<summary><b>📄 Documents et dossiers</b></summary>

| Méthode | Route | Description |
|---|---|---|
| `GET` / `POST` | `/documents` | Liste paginée (filtrable par dossier) / création |
| `GET` / `PUT` / `DELETE` | `/documents/<id>` | Lecture / mise à jour / suppression |
| `GET` | `/documents/stats` | Statistiques personnelles |
| `GET` / `POST` | `/dossiers` | Liste avec compteurs / création |
| `DELETE` | `/dossiers/<id>` | Suppression (les documents repassent à `id_dossier` nul) |

</details>

<details>
<summary><b>🤖 IA</b></summary>

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/documents/<id>/ia/generer` | Génération. Corps : `type_action` (`reformuler` \| `corriger` \| `completer`), `scope` (`selection` \| `document`), `contenu`, `instructions` (facultatif). Renvoie `429` si le quota 24 h est atteint, `502` si Ollama est injoignable |
| `GET` | `/documents/<id>/ia/historique` | Historique des interactions du document, état d'insertion compris |
| `POST` | `/documents/<id>/ia/<id_ia>/insertion` | Marque une proposition comme versée au document (AI Act, art. 50). Corps : `position_debut` (entier). Idempotente : un second appel renvoie `200` sans réécrire l'horodatage d'origine |

</details>

<details>
<summary><b>🛡️ Administration — rôle <code>admin</code> requis</b></summary>

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/admin/users` | Liste paginée avec compteurs d'usage |
| `PATCH` | `/admin/users/<id>` | Modification de `role` et `quota_daily_limit` |
| `DELETE` | `/admin/users/<id>` | Suppression d'un compte |
| `GET` | `/admin/stats` | Statistiques globales |

</details>

---

## 🗃️ Modèle de données

Sept entités, identifiants UUID, suppression en cascade depuis `user`.

| Table | Rôle |
|---|---|
| `user` | Compte, rôle, quota IA quotidien (20 par défaut) |
| `document` | Titre, contenu, format, statut, rattachement à un dossier |
| `dossier` | Regroupement de documents d'un utilisateur |
| `ia` | Journal des appels IA : action, contenu avant/après, tokens consommés, et trace d'insertion (`insere`, `position_debut`, `insere_at`) |
| `consentement` | Traçabilité des consentements RGPD (type, acceptation, date) |
| `user_session` | Refresh tokens hachés, expiration, drapeau de révocation |
| `password_reset` | Tokens de réinitialisation hachés, expiration, usage unique |

> `PRAGMA foreign_keys=ON` est activé à chaque connexion : SQLite n'applique pas les contraintes de clé étrangère par défaut, et sans lui le `ondelete="SET NULL"` de `document.id_dossier` ne serait jamais exécuté.

---

## 🧪 Tests

**344 tests, tous au vert** — 286 pytest, 58 Vitest. Couverture backend **96 %** hors
`database/jeu_essai.py`, script de peuplement non destiné à être couvert (89 % en le comptant).

```bash
# Backend — depuis backend/, venv activé
pytest                                   # toute la suite
pytest -m securite                       # la campagne de sécurité seule
pytest --cov=app --cov=database --cov-report=term-missing

# Frontend — depuis frontend/
npm test                                 # vitest run
npm run test:coverage
```

| Niveau | Où |
|---|---|
| Unitaires (métier, accès aux données) | `backend/tests/unit/` |
| Intégration (routes HTTP, flux Ollama, traçabilité IA) | `backend/tests/integration/` |
| Sécurité (17 non-régressions, `-m securite`) | `backend/tests/security/` |
| Parité ORM / `schema_mysql.sql` (36 contrôles) | `backend/tests/unit/test_schema_parite.py` |
| Interface et utilitaires | `frontend/src/**/__tests__/` |

L'environnement de test est hermétique : base en mémoire, aucun appel réseau. Le
[plan de tests](docs/plan-de-tests.md) détaille les 7 niveaux, la traçabilité des règles de gestion
et le compte rendu d'exécution.

> [!TIP]
> **Les doubles de test mentent.** Trois bugs de la chaîne IA sont passés sous un faux
> `requests.post` qui acceptait `json()` à tout moment. Il a fallu un vrai serveur HTTP —
> `tests/integration/test_ia_flux_ollama.py` — pour les voir.

---

## 🔒 Sécurité

### ✅ En place

| | Mesure |
|---|---|
| 🔑 | **Mots de passe** hachés avec bcrypt (sel automatique) — 8 caractères min., majuscule, minuscule, chiffre |
| ⏱️ | **Access token** JWT HS256, durée de vie 15 minutes, en-tête `Authorization` |
| 🔄 | **Refresh token** en cookie `httpOnly`, `SameSite=Strict`, limité au chemin `/auth`, **stocké haché** et **tourné à chaque usage** — la réutilisation d'un token consommé est traitée comme un vol et révoque toutes les sessions |
| 🧼 | **XSS** : la prévisualisation Markdown passe par `DOMPurify.sanitize()` entre `marked.parse()` et `v-html` ([détail du correctif](docs/securite-correctifs-2026-09-27.md)) |
| 🚨 | **Fail fast** : absence de `JWT_SECRET_KEY` ou de `SECRET_KEY` → `RuntimeError` au démarrage, aucune clé de repli dans le code |
| 🚫 | **Jetons révoqués** : une session révoquée reste en base jusqu'à expiration pour la détection de rejeu — `verify_refresh_token()` contrôle le drapeau `revoke` et la refuse |
| 🔐 | **Cookie `Secure`** piloté par `APP_ENV` : désactivé en dev (localhost HTTP), obligatoire ailleurs |
| 📧 | **Réinitialisation** : seul le hash SHA-256 du token est stocké, expiration 1 h, usage unique, révocation de toutes les sessions après changement |
| 🕵️ | **Anti-énumération** : `/auth/forgot-password` répond à l'identique que l'email existe ou non |
| 🚦 | **Rate-limiting** sur les routes sensibles, réponse `429` normalisée |
| 👤 | **Contrôle d'accès** : appartenance vérifiée sur chaque document/dossier ; le rôle admin est relu **en base** à chaque appel, jamais depuis le JWT |
| 🧯 | **Garde-fous back-office** : un admin ne peut ni se retirer ses droits ni supprimer son propre compte |
| 💉 | **Injections SQL** : aucune requête par concaténation, paramétrage systématique par SQLAlchemy |
| 🌐 | **CORS** restreint à l'origine du frontend |
| ✔️ | **Validation d'entrée** systématique : types, longueurs, valeurs autorisées, bornes de quota et de pagination |

### 🚧 Points ouverts avant une mise en production

L'[audit de sécurité](docs/audit-securite.md) est rédigé : **0 vulnérabilité critique ou élevée**,
17 tests de non-régression. Restent :

- [ ] Chiffrement des données sensibles au repos (3 options chiffrées au § 5.1 de l'audit)
- [ ] Restreindre l'écoute d'Ollama à `127.0.0.1` (`OLLAMA_HOST=127.0.0.1:11434`)
- [ ] Épingler les dépendances transitives (Werkzeug non épinglée)
- [ ] **`/auth/forgot-password` sans délai sur le serveur de courriel** : le courriel part dans le
      fil de la requête, et Flask-Mail n'impose aucun délai. SMTP injoignable → la requête ne se
      termine jamais, et avec deux workers synchrones **l'API entière cesse de répondre**. Route
      publique et non authentifiée. Mesuré le 05/10/2026, analyse au §4 de
      [`docs/validation-docker.md`](docs/validation-docker.md)
- [ ] Remplacer le stockage mémoire de Flask-Limiter par Redis — les seuils comptent **par worker**,
      ce que la campagne de tests système a vérifié à ses dépens
- [ ] Corriger le quota IA concurrent : contrôle et usage ne sont pas atomiques (§ 7.2 de
      [l'exploitation de la base](docs/exploitation-base-de-donnees.md))

---

## ⚖️ RGPD et accessibilité

**RGPD et AI Act**

- ✅ Consentement explicite recueilli à l'inscription et tracé en base (table `consentement`)
- ✅ Inférence IA entièrement locale : aucun contenu utilisateur transmis à un tiers
- ✅ Pages Mentions légales, CGU et Politique de confidentialité intégrées, article dédié aux
  contenus générés et à la responsabilité éditoriale de l'utilisateur
- ✅ **Traçabilité des contenus générés** (règlement UE 2024/1689, art. 50) : la table `ia`
  distingue une proposition *produite* d'une proposition *acceptée*, et l'éditeur rappelle à
  l'ouverture les passages issus d'une génération
- 🚧 Consentement distinct dédié à l'usage de l'IA
- 🚧 Export des données et suppression de compte à l'initiative de l'utilisateur

**Accessibilité (RGAA)**

[Audit réel sur les 16 écrans](docs/audit-accessibilite.md), axe-core sur l'application démarrée
(écrans publics **et** authentifiés) complété par des contrôles manuels.

- ✅ **15 écrans, 0 violation axe-core** (WCAG 2.0, 2.1 et 2.2, niveaux A et AA)
- ✅ Contrastes corrigés : `#E0533C` assombri en `#C4341C` — 64 violations avant, 0 après
- ✅ Étiquettes sur les champs de quota du back-office et sur la zone CodeMirror
- ✅ **Titre de page distinct par route** (15 titres sur 15 écrans) et **lien d'évitement** sur
  chaque écran
- ✅ **Focus visible partout** : règle `:focus-visible` globale, et retrait des `focus:outline-none`
  qui l'emportaient sur elle
- ✅ **Structure de titres sans saut de niveau**, `<main>` et `h1` sur les 15 écrans
- ✅ **Cibles de 24 px minimum** (WCAG 2.2 · 2.5.8), hors liens en ligne dans une phrase, couverts
  par l'exception du critère
- ✅ Chargement différé des routes, navigation cohérente
- 🚧 Ce qu'aucun outil ne fait : lecteur d'écran réel, zoom à 200 %, déclaration d'accessibilité

> Un « 0 violation » automatisé ne vaut pas conformité RGAA : l'audit le dit, et liste ce qu'axe-core
> ne détecte pas. Le script de mesure est versionné
> ([`audit-accessibilite.mjs`](docs/audits/audit-accessibilite.mjs)), l'audit est donc rejouable.

---

## 📊 État d'avancement

| Lot | État |
|---|:---:|
| Authentification et gestion de compte | ✅ Terminé |
| CRUD documents et dossiers | ✅ Terminé |
| Intégration IA (Ollama), quotas et performance | ✅ Terminé |
| Traçabilité des contenus générés (AI Act) | ✅ Terminé |
| Back-office administrateur | ✅ Terminé |
| Pages légales et vitrine | ✅ Terminé |
| Correctifs de sécurité (XSS, tokens, CSRF) | ✅ Terminé |
| Maquettes, captures et veille | ✅ Terminé |
| Documents de conception (11 diagrammes) | ✅ Terminé |
| Tests automatisés (344) et plan de tests | ✅ Terminé |
| Migration vers MySQL, droits, sauvegarde et jeu d'essai | ✅ Terminé |
| Conteneurisation Docker | ✅ Terminée et validée sur un démon réel |
| Pipeline CI/CD (GitHub Actions, Ruff, ESLint) | ✅ Terminé |
| Audit de sécurité | ✅ Terminé |
| Audit d'accessibilité et correctifs RGAA | ✅ Terminé |
| Tests système TS-01 à TS-10 | 🔄 7 au vert, 1 défaut trouvé, 2 hors de portée (Ollama, lecteur d'écran) |
| Tests de charge et d'acceptation | ⬜ À faire |
| Procédure et scripts de déploiement | ⬜ À faire |
| Dossier de projet, diaporama, documentation utilisateur | ⬜ À faire |

Le détail, lot par lot, est dans [`TODO.md`](TODO.md).

---

## 👩‍💻 Auteur

<div align="center">

**Ophélie Bellissens** — CDA / CD2IA, Metz Numeric School

[![Portfolio](https://img.shields.io/badge/Portfolio-opheliebellissens.netlify.app-0ea5e9?style=for-the-badge)](https://opheliebellissens.netlify.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-ophelie--bellissens--dev-0a66c2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/ophelie-bellissens-dev)

<sub>Projet pédagogique, non destiné à un usage commercial.</sub>

</div>
