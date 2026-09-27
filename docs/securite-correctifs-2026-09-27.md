# Correctifs de sécurité — HelpMeDraft

Session du 27/09/2026. Matière pour les sections 8 (sécurité) et 11 (veille sur les vulnérabilités) du dossier projet CDA.

Six correctifs appliqués (1, 2, 3, 4, 5, 6) et une reformulation (7).

---

## 1. XSS stocké dans l'aperçu Markdown 🔴

**Fichiers** : `frontend/src/components/MarkdownEditor.vue`, `frontend/package.json`, `frontend/test_xss.mjs` (nouveau)

**Pourquoi c'était une faille.** `marked` fait une seule chose : convertir la syntaxe Markdown en HTML. Ce n'est pas un assainisseur. Le HTML brut rencontré dans la source est recopié tel quel dans la sortie — c'est même un comportement documenté et voulu, puisque le Markdown autorise l'HTML inline. Le résultat était ensuite injecté avec `v-html`, qui contourne délibérément l'échappement de Vue. Saisir `<img src=x onerror="alert(1)">` dans un document produisait donc cette balise dans le DOM, et le navigateur exécutait `onerror`.

Le point aggravant est l'enregistrement automatique : la charge n'est pas seulement réfléchie le temps d'une frappe, elle est écrite en base et rejouée à chaque réouverture du document. C'est un XSS **stocké** (OWASP A03:2021 – Injection). Conséquences concrètes sur HelpMeDraft : vol du contenu des documents affichés, actions à la place de l'utilisateur via l'access token présent en mémoire du front, et — si une fonction de partage de document arrive un jour — propagation à d'autres comptes.

**Correctif.** `DOMPurify.sanitize()` entre `marked.parse()` et `v-html`. L'ordre compte : assainir avant la conversion Markdown laisserait passer des charges reconstruites par `marked`.

Avant :

```ts
const previewHtml = computed(() => {
  try {
    return marked.parse(internalValue.value || "", markedOptions);
  } catch {
    return "<p>Erreur de rendu</p>";
  }
});
```

Après :

```ts
import DOMPurify from "dompurify";

const previewHtml = computed(() => {
  try {
    const rawHtml = marked.parse(
      internalValue.value || "",
      markedOptions,
    ) as string;
    return DOMPurify.sanitize(rawHtml, { USE_PROFILES: { html: true } });
  } catch {
    return "<p>Erreur de rendu</p>";
  }
});
```

Le profil `html` autorise les balises de mise en forme dont l'éditeur a besoin, y compris le `<u>` posé par le bouton « Souligné » de la barre d'outils, et refuse tout le reste.

**Test** — `node frontend/test_xss.mjs` rejoue la chaîne `marked` → `DOMPurify` sur six entrées :

| Entrée | Avant assainissement | Après |
|---|---|---|
| `<img src=x onerror="alert(1)">` | `<img src=x onerror="alert(1)">` | `<img src="x">` |
| `<script>alert(1)</script>` | `<script>alert(1)</script>` | *(vide)* |
| `<a href="javascript:alert(1)">clic</a>` | `<a href="javascript:alert(1)">clic</a>` | `<a>clic</a>` |
| `<iframe src="https://evil.tld">` | `<iframe src="https://evil.tld">` | *(vide)* |
| Markdown légitime (titres, gras, `<u>`, liste, lien https, code) | — | **inchangé** |

Le dernier cas est le plus important : il prouve qu'on a corrigé la faille sans casser le rendu.

---

## 2. Refresh token stocké en clair 🔴

**Fichiers** : `backend/database/db.py`, `backend/app/services/auth_service.py`, `backend/app/routes/auth_routes.py`, `backend/database/migration_sqlite_refresh_hash.sql` (nouveau)

**Pourquoi c'était une faille.** Un refresh token est un secret à longue durée de vie (7 jours ici, cookie posé pour 30) : le présenter suffit à obtenir un access token, donc à prendre la place de l'utilisateur, sans mot de passe et sans déclencher de tentative de connexion visible. Le stocker en clair revient à stocker un mot de passe en clair.

L'incohérence interne rendait le défaut évident : la table `password_reset` ne gardait que `token_hash`, une empreinte SHA-256, alors que `user_session` gardait `refresh_token`, le jeton lui-même. Deux secrets de même nature, deux traitements. Un dump de base, une sauvegarde mal protégée ou une injection SQL en lecture permettait de rejouer toutes les sessions actives.

SHA-256 sans sel convient ici, contrairement à un mot de passe : le jeton est un aléa de 64 octets produit par `secrets.token_urlsafe`, il n'est attaquable ni par dictionnaire ni par table précalculée. L'empreinte reste vérifiable (on hache ce que présente le client et on compare) sans être inversible.

**Correctif.** Colonne renommée en `refresh_token_hash` (`VARCHAR(128)`, aligné sur `schema_mysql.sql` et `migration_durcissement.sql`), et empreinte calculée à l'émission comme à la vérification.

Avant — `db.py` :

```python
refresh_token:     Mapped[str]      = mapped_column(String(512), nullable=False, unique=True)
```

Après :

```python
refresh_token_hash: Mapped[str]     = mapped_column(String(128), nullable=False, unique=True)
```

Avant — `auth_service.py` :

```python
def create_session(user_id: str) -> str:
    refresh_token = generate_refresh_token()
    with SessionLocal() as db_session:
        user_session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            ...
        )
```

Après :

```python
def hash_refresh_token(plain_token: str) -> str:
    return hashlib.sha256(plain_token.encode()).hexdigest()


def create_session(user_id: str) -> str:
    refresh_token = generate_refresh_token()
    with SessionLocal() as db_session:
        user_session = UserSession(
            user_id=user_id,
            refresh_token_hash=hash_refresh_token(refresh_token),
            ...
        )
    # Seul l'appelant (la route) reçoit le jeton en clair, pour le cookie.
    return refresh_token
```

Même transformation sur les trois autres points de contact : `verify_refresh_token`, `rotate_refresh_token` (lecture de l'ancien jeton **et** écriture du nouveau), et la route `/auth/logout` qui cherchait la session par `UserSession.refresh_token == token`. Le jeton en clair ne vit plus qu'en mémoire, le temps d'aller dans le cookie.

**Migration.** `migration_durcissement.sql` fait déjà le travail côté MySQL. Côté SQLite, SQLAlchemy ne modifie pas une table existante : `migration_sqlite_refresh_hash.sql` est le pendant exact du point 1 de ce script. Les sessions sont purgées dans les deux cas — une empreinte ne se déduit pas d'un jeton, et de toute façon un jeton qui a été stocké en clair doit être considéré comme compromis.

**Test** — `python backend/test_securite.py`, qui vérifie sur une base neuve :

- après connexion, la valeur en base est l'empreinte SHA-256 du cookie (64 caractères hex), et **pas** le jeton ;
- `/auth/refresh` pose un nouveau jeton et enregistre une nouvelle empreinte ;
- rejouer l'ancien jeton renvoie 401 **et** révoque toutes les sessions de l'utilisateur (détection de réutilisation déjà présente, préservée) ;
- `/auth/logout` retrouve bien la session par empreinte et la supprime.

Le chemin de migration a été vérifié séparément : base créée avec l'ancien code → nouveau code sans migration → `login` en 500 (`no such column: refresh_token_hash`) → migration → `login` en 200, comptes et documents conservés.

---

## 3. `JWT_SECRET_KEY` avec valeur de repli 🔴

**Fichier** : `backend/app/config.py`, `.env.example`

**Pourquoi c'était une faille.** `os.environ.get("JWT_SECRET_KEY", "change_moi_en_prod")` fait démarrer l'application sans `.env`, avec une clé écrite en clair dans un dépôt public. Or cette clé est le seul élément qui distingue un access token légitime d'un token forgé : en HS256, qui connaît la clé signe le payload de son choix, donc `{"sub": "<n'importe quel user_id>"}`. Tous les comptes deviennent accessibles, admin compris.

C'est un défaut de configuration sécurisée (OWASP A05:2021) doublé d'un secret en dur (A02:2021 – Cryptographic Failures). Le nom même de la valeur (« change_moi_en_prod ») suppose que quelqu'un y pensera au bon moment ; un correctif fiable ne repose pas sur cette hypothèse.

**Correctif** — échec bruyant au démarrage plutôt que démarrage silencieusement vulnérable :

```python
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY est absente de l'environnement. "
        "Copier .env.example en backend/.env puis générer une clé : "
        'python -c "import secrets; print(secrets.token_urlsafe(64))"'
    )
```

Le message d'erreur porte la marche à suivre : un garde-fou qu'on ne sait pas lever finit par être retiré.

**Test** — dans `test_securite.py` : un sous-processus importe `app.config` sans la variable d'environnement, on vérifie code de retour non nul et présence du message. Avec la variable, `create_app()` passe.

---

## 4. Cookie de refresh en `secure=False` 🔴

**Fichiers** : `backend/app/routes/auth_routes.py`, `backend/app/config.py`, `.env.example`

**Pourquoi c'était une faille.** Sans l'attribut `Secure`, le navigateur joint le cookie aux requêtes HTTP en clair. Le refresh token peut alors être capté sur un réseau non maîtrisé, ou par un attaquant capable de forcer une requête vers `http://` (SSL stripping). `httponly` protège du vol par JavaScript, pas de l'interception réseau : les deux attributs répondent à deux menaces différentes et ne se remplacent pas.

`secure=True` en dur n'était pas jouable non plus : le front tourne en `http://localhost:5173`, le cookie ne serait jamais envoyé et la connexion casserait. D'où le pilotage par environnement.

**Correctif.** `config.py` expose une valeur dérivée de l'environnement :

```python
APP_ENV = os.getenv("APP_ENV", "development")
COOKIE_SECURE = APP_ENV != "development"
```

Le défaut est le cas sûr : toute valeur autre que `development` — y compris une variable oubliée mais renseignée — active `Secure`.

`auth_routes.py` : les deux `set_cookie` dupliqués de `/auth/login` et `/auth/refresh` sont remplacés par un helper unique, `set_refresh_cookie()`. Un seul endroit à relire pour auditer la politique de cookie, et plus de risque que les deux routes divergent. `httponly` et `path="/auth"` sont conservés ; `samesite` passe à `Strict` au point 6.

**Test** — dans `test_securite.py`, l'en-tête `Set-Cookie` de `/auth/login` est inspecté :

- `APP_ENV=development` → `HttpOnly; Path=/auth; SameSite=Lax`, **sans** `Secure` ;
- `APP_ENV=production` → `Secure; HttpOnly; Path=/auth; SameSite=Lax`.

---

## 5. Cascades déclarées côté ORM seulement 🟠

**Fichier** : `backend/database/db.py`

**Pourquoi c'était un défaut.** Les `cascade="all, delete-orphan"` de SQLAlchemy ne sont appliqués que par SQLAlchemy : ils décrivent le comportement de l'application, pas une garantie du SGBD. Toute suppression qui ne passe pas par l'ORM — script de maintenance, requête manuelle, purge d'un lot de comptes, `DELETE` dans un client MySQL — laissait des lignes orphelines dans `document`, `dossier`, `ia`, `consentement`, `user_session`, `password_reset`.

Ce n'est pas seulement un problème d'intégrité référentielle. Le droit à l'effacement (RGPD art. 17) doit être garanti par le schéma, pas par la bonne tenue du code applicatif : « les documents de ce compte ont été supprimés parce que l'ORM le fait normalement » n'est pas une preuve. Les six clés étrangères vers `user.user_id` n'avaient aucun `ondelete`, alors que `schema_mysql.sql`, déjà livré, portait bien `ON DELETE CASCADE` sur les six. Le modèle Python et le schéma cible divergeaient.

**Correctif** — `ondelete="CASCADE"` sur les six FK vers `user.user_id` (`password_reset`, `user_session`, `dossier`, `document`, `consentement`, `ia`). Le `PRAGMA foreign_keys=ON` déjà présent dans `db.py` fait que SQLite les applique réellement en dev.

**Test** — dans `test_securite.py` : lecture du DDL généré (`sqlite_master`) pour confirmer la présence de `ON DELETE CASCADE`, puis un `DELETE FROM user` **en SQL pur**, hors SQLAlchemy — le seul test qui prouve que la cascade vit dans le SGBD. Documents et consentements du compte passent de 1 à 0.

---

## 6. Protection CSRF 🟠

**Fichier** : `backend/app/routes/auth_routes.py`

**Pourquoi c'était un défaut.** Le refresh token étant dans un cookie, le navigateur le joint automatiquement. `POST /auth/refresh` est donc déclenchable depuis un site tiers : l'attaquant ne lit pas la réponse (le CORS ne l'autorise pas, seul `http://localhost:5173` est admis), mais l'effet de bord se produit quand même.

Ici il est particulier, et c'est ce qui rend le cas intéressant à documenter : la route applique une **rotation**. Une requête forgée invalide le jeton légitime de la victime, et le rejeu suivant par le vrai front est interprété par la détection de réutilisation comme une fraude → toutes ses sessions sont révoquées. L'impact est donc un **déni de service sur le compte**, pas une usurpation.

Les autres routes ne sont pas concernées : elles s'authentifient par en-tête `Authorization: Bearer`, que le navigateur n'ajoute jamais de lui-même. Un formulaire tiers ne peut pas les appeler au nom du client. Le CSRF est structurellement limité aux routes qui s'authentifient par cookie — ici la seule `/auth/refresh`, déjà restreinte par `path=/auth`.

**Options étudiées.**

| | Coût front | Apport | Limite |
|---|---|---|---|
| **A** — `SameSite=Strict` | aucun | ferme aussi les navigations top-level que `Lax` laisse passer | front et API doivent être sur le même site (eTLD+1) ; défense déléguée au navigateur |
| **B** — double-submit token (`Lax` + cookie `csrf_token` lisible + en-tête `X-CSRF-Token`) | `api.ts` à modifier | ne dépend pas du navigateur | **neutralisée par un XSS**, qui peut lire le cookie et forger l'en-tête — suppose donc le point 1 corrigé |
| **C** — A + B | coût de B | défense en profondeur | cumule les deux contraintes |

**Décision : option A.** Le refresh est la seule route sensible en cookie, `path=/auth` limite déjà la surface, et le pire cas est un déni de service sur un compte. L'option B se justifierait s'il y avait d'autres routes mutatives authentifiées par cookie ; elle reste notée ici parce qu'elle illustre un point de raisonnement utile — **une protection CSRF par double-submit ne tient que si le XSS est fermé** : les deux failles sont liées, et corriger le point 1 était le préalable.

**Correctif** — dans `set_refresh_cookie()` :

```python
response.set_cookie(
    "refresh_token", refresh_token,
    httponly=True,
    secure=current_app.config["COOKIE_SECURE"],
    samesite="Strict",          # était "Lax"
    max_age=REFRESH_COOKIE_MAX_AGE,
    path="/auth",
)
```

**Contrainte de déploiement à retenir.** `SameSite` raisonne en *sites* (eTLD+1), pas en origines. En dev, front (`:5173`) et API (`:5000`) sont tous deux sur `localhost` : même site, le cookie passe malgré les ports différents. En production il faudra deux sous-domaines d'un même domaine, ou l'API derrière un reverse proxy sur le domaine du front. Un front et une API sur deux domaines distincts casseraient le refresh.

**Test** — dans `test_securite.py` : l'en-tête `Set-Cookie` de `/auth/login` contient `SameSite=Strict`, en dev comme en `APP_ENV=production` (`Secure; HttpOnly; Path=/auth; SameSite=Strict`). Le parcours complet inscription → connexion → refresh → création de document → déconnexion reste vert, ce qui confirme que `Strict` ne casse pas le refresh en dev.

---

## 7. Affirmation non fondée sur la page d'accueil 🟠

**Fichier** : `frontend/src/views/HomeView.vue`

La carte « Souveraineté des Données » promettait un « Hébergement européen ». Rien n'est déployé : la promesse n'est pas vérifiable, et sur un sujet RGPD une affirmation non tenue est un risque de conformité, pas une maladresse de rédaction. L'argument réel est plus fort : l'inférence tourne sur Ollama en local, donc aucun document ne quitte la machine.

Avant : *« Vos écrits restent les vôtres. Hébergement européen, aucun entraînement public sur vos données confidentielles. »*

Après : *« Vos écrits restent les vôtres : traitement local, aucune donnée transmise à un tiers, aucun entraînement sur vos documents confidentiels. »*

À rapprocher du point 2 de `migration_durcissement.sql`, qui renomme le consentement `openai_data_processing` en `traitement_ia_local` : même mise en cohérence du discours avec l'architecture réelle.

---

## Ce qui reste ouvert

**À faire avant de relancer l'application**

1. `cd frontend && pnpm add dompurify` — la dépendance est déclarée dans `package.json` (`^3.2.7`) mais **pas installée** : l'installation n'a pas pu être lancée à distance, le front ne compilera pas avant.
2. Migration de la base de dev, depuis `backend/` :
   `sqlite3 HelpMeDraft.db < database/migration_sqlite_refresh_hash.sql`
   Sans cette étape, `/auth/login` répond 500 (`no such column: refresh_token_hash`). Tous les comptes sont déconnectés, les données sont conservées.

**Vérifications non effectuées**

- Démarrage réel sur la machine (`python run.py`, `pnpm dev`) et parcours dans le navigateur : pas d'accès à un shell distant pendant la session. Le backend a été rejoué intégralement en conteneur avec `test_securite.py` (inscription → connexion → refresh → création de document → déconnexion, tous verts), et la chaîne d'assainissement du front a été testée hors Vue avec `test_xss.mjs`. Restent à confirmer en local : le typage `vue-tsc` (`pnpm build`) et le rendu visuel de l'aperçu.
- Le test XSS de bout en bout demandé — saisir `<img src=x onerror="alert(1)">` dans un document, recharger, vérifier qu'aucune alerte ne se déclenche — est à faire manuellement. C'est une capture utile pour la section 8.

**Constats hors périmètre, non modifiés**

- `ia.id_document` n'a pas de `ondelete` côté ORM alors que `schema_mysql.sql` porte `ON DELETE CASCADE`. Même écart que le point 5, sur une FK qui ne pointe pas vers `user` : hors périmètre demandé, mais à aligner pour que modèle et schéma coïncident vraiment.
- Les cascades ajoutées au point 5 n'apparaissent dans la base SQLite existante **que** sur les tables recréées : `ALTER TABLE` ne sait pas ajouter une clause `ON DELETE` en SQLite. Pour obtenir les six cascades en dev, supprimer `HelpMeDraft.db` et laisser SQLAlchemy la recréer. MySQL est correct dès `schema_mysql.sql`.
- `SECRET_KEY` de Flask n'est pas configurée. Pas exploitable en l'état — aucune session côté serveur, aucun `flash()` — mais à poser avant d'utiliser quoi que ce soit qui signe des cookies de session.
