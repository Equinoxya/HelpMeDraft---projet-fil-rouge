# Plan de tests — HelpMeDraft

> **CP 9** — Préparer et exécuter les plans de tests d'une application
> *Critères de performance : **le plan couvre l'ensemble des fonctionnalités** · **un environnement de tests est créé** · l'intégralité des tests exécutés est conforme au plan · **les résultats obtenus sont cohérents avec les résultats attendus** · le plan tient compte des évolutions technologiques et des problèmes de sécurité.*

Version 1 — 3 octobre 2026
Terminologie : CFTL / ISTQB.

---

## 1 · Objectif et périmètre

Vérifier que HelpMeDraft remplit les fonctionnalités du [cahier des charges](./cahier-des-charges.md)
et respecte les règles de gestion du [dossier de conception](./conception/01-expression-des-besoins.md#15--règles-de-gestion),
sans régression de sécurité.

**Dans le périmètre** — les 19 besoins fonctionnels (BF-01 à BF-19) et les 10 règles de gestion
(RG-01 à RG-10).

**Hors périmètre** — la qualité linguistique des suggestions produites par le modèle. Elle n'est
pas déterministe et ne peut pas faire l'objet d'une assertion. Ce qui est testé, c'est la
**mécanique** autour du modèle : validation, autorisation, quota, trace, gestion d'erreur. Le
modèle lui-même est remplacé par un double de test.

---

## 2 · Niveaux de tests

| Niveau | Objet | Outil | Automatisé |
|---|---|---|:---:|
| **Unitaire** | une fonction ou un composant isolé | pytest, Vitest | ✅ |
| **Intégration** | une route complète, du HTTP à la base | pytest + client de test Flask | ✅ |
| **Système** | un parcours utilisateur de bout en bout | manuel (v1), Playwright (cible) | ⬜ |
| **Sécurité** | les parades aux vulnérabilités identifiées | pytest, Vitest | ✅ |
| **Non-régression** | l'ensemble des suites rejouées à chaque modification | CI GitHub Actions | ✅ |
| **Acceptation** | conformité au cahier des charges, validée par le commanditaire | manuel, avec le formateur | ⬜ |
| **Charge** | tenue sous sollicitation de la route d'inférence | Locust (ciblé, hors v1) | ⬜ |

> **Pourquoi les tests système restent manuels en v1.** Playwright demande une application
> démarrée, un modèle chargé et une base peuplée. L'investissement se justifie une fois la
> conteneurisation faite (`KAN-15`), pas avant. En attendant, les parcours sont exécutés
> manuellement et consignés au §7.

---

## 3 · Environnement de tests

> *Critère de performance : « Un environnement de tests est créé ».*

| | Développement | **Tests** | Production (cible) |
|---|---|---|---|
| Base | SQLite, fichier `HelpMeDraft.db` | **SQLite en mémoire, recréée à chaque test** | MySQL 8 |
| Inférence | Ollama local | **double de test** — aucun appel réseau | Ollama sur l'hôte |
| Messagerie | SMTP de test | **envoi supprimé**, messages capturés | Brevo |
| Limitation de débit | active | **désactivée** | active |
| Secrets | `.env` | valeurs fixes injectées par les fixtures | secrets d'environnement |

**Propriétés exigées de l'environnement de tests**

1. **Isolation** — un test ne voit jamais les données d'un autre. Base recréée par test.
2. **Hermétisme** — aucun appel réseau sortant. Ni Ollama, ni SMTP.
3. **Reproductibilité** — même résultat sur le poste et dans la CI, horodatages maîtrisés.
4. **Rapidité** — la suite complète doit rester sous la minute, sinon elle ne sera pas lancée.

---

## 4 · Obstacles de testabilité à lever

> Ces points sont relevés avant l'écriture des tests, parce qu'ils **conditionnent** la possibilité
> d'en écrire. Les ignorer conduirait à des tests fragiles qui se contournent les uns les autres.

### 4.1 · La base est liée au moment de l'import — bloquant

`backend/database/db.py` construit le moteur SQLAlchemy **au chargement du module**, sur un chemin
de fichier en dur, et crée les tables dans la foulée :

```python
DB_PATH = Path("HelpMeDraft.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
...
Base.metadata.create_all(engine)      # exécuté à l'import
```

`SessionLocal` est un singleton de module, importé directement par les routes
(`from database.db import SessionLocal`). **Conséquence : il n'existe aucun point d'entrée pour
diriger l'application vers une autre base.** Dès qu'un test importe une route, le fichier
`HelpMeDraft.db` du poste est créé et utilisé — c'est d'ailleurs ce que fait `test_securite.py`,
qui crée et détruit sa propre base et prévient de ne pas la lancer sur des données à conserver.

Deux issues possibles :

| | **A — Détournement en fixture** | **B — URL configurable** |
|---|---|---|
| Principe | la fixture remplace `SessionLocal` et le moteur par un double pointant sur `sqlite:///:memory:` | `db.py` lit `HELPMEDRAFT_DB_URL` dans l'environnement, avec le fichier actuel par défaut |
| Code de production modifié | **aucun** | 3 lignes dans `db.py` |
| Robustesse | fragile : dépend de l'ordre des imports, à refaire à chaque nouveau module | solide : un seul point de configuration |
| Effet de bord utile | aucun | **débloque aussi `KAN-86`** (migration MySQL) et la conteneurisation (`KAN-15`) |
| Risque | un import oublié écrit dans la vraie base | aucun si la valeur par défaut est inchangée |

> **Recommandation : B.** Trois lignes, aucun changement de comportement par défaut, et c'est de
> toute façon nécessaire pour MySQL et pour Docker. L'option A fait porter aux tests une
> complexité qui appartient au code.

### 4.2 · Points secondaires

| Obstacle | Effet sur les tests | Traitement |
|---|---|---|
| `Config` lève une exception sans `JWT_SECRET_KEY` | la suite ne démarre pas | la fixture injecte une clé de test |
| Limitation de débit active (5 connexions/min) | le 6ᵉ test d'authentification échoue en `429` | `RATELIMIT_ENABLED = False` en configuration de test |
| `ia_service.call_ollama` appelle le réseau | tests lents, non déterministes, échouent sans Ollama | double de test sur `call_ollama` |
| `email_service` envoie réellement | mails parasites | `MAIL_SUPPRESS_SEND = True`, messages capturés |
| Fenêtre de quota de 24 h | impossible de tester le dépassement sans 20 appels | insérer directement les lignes `ia` avec des horodatages choisis |
| `create_app()` ne prend pas de configuration | impossible de surcharger proprement | ajouter un paramètre optionnel `config_object` |

---

## 5 · Outillage

| | Backend | Frontend |
|---|---|---|
| Lanceur | **pytest** | **Vitest** |
| Client HTTP | client de test Flask | — |
| Composants | — | **@vue/test-utils** + **jsdom** |
| Doubles | `pytest-monkeypatch` | `vi.mock` |
| Couverture | `pytest-cov` | `@vitest/coverage-v8` |

**Pourquoi pytest** plutôt que `unittest` : les fixtures composables correspondent exactement au
besoin (base, application, client, utilisateur authentifié s'empilent), et c'est l'outil attendu
dans l'écosystème Flask.

**Pourquoi Vitest** plutôt que Jest : Vitest réutilise la configuration Vite déjà en place —
alias, TypeScript, plugin Vue. Jest demanderait une seconde chaîne de transformation.

---

## 6 · Arborescence

```
backend/
├── pytest.ini                  # configuration et chemins
└── tests/
    ├── conftest.py             # fixtures : app, client, base, utilisateur, admin
    ├── unit/
    │   ├── test_auth_service.py        # hachage, JWT, rotation des jetons
    │   └── test_ia_service.py          # construction des prompts, erreurs Ollama
    ├── integration/
    │   ├── test_auth_routes.py         # inscription, connexion, rafraîchissement, déconnexion
    │   ├── test_document_routes.py     # CRUD et cloisonnement
    │   ├── test_dossier_routes.py      # CRUD et déclassement
    │   ├── test_ia_routes.py           # génération, quota, historique
    │   └── test_admin_routes.py        # autorisation, gestion des comptes, statistiques
    └── security/
        └── test_securite.py            # suite existante, reprise en pytest

frontend/
├── vitest.config.ts
└── src/
    ├── utils/__tests__/documentStatus.spec.ts
    ├── components/__tests__/MarkdownEditor.spec.ts   # assainissement XSS
    ├── services/__tests__/api.spec.ts                # intercepteurs, mutualisation du 401
    └── stores/__tests__/auth.spec.ts                 # cycle de session
```

> `backend/test_securite.py` et `frontend/test_xss.mjs` existent déjà mais sont des **scripts**
> lancés à la main, qui impriment des traces sans assertion. Ils sont **repris en tests**, pas
> jetés : leur contenu est pertinent, c'est le harnais qui manque.

---

## 7 · Campagne de tests

### 7.1 · Tests unitaires — backend

| ID | Objet | Entrée | Résultat attendu |
|---|---|---|---|
| TU-01 | `hash_password` | mot de passe en clair | empreinte bcrypt, ≠ clair, préfixe `$2b$` |
| TU-02 | `verify_password` | bon mot de passe | `True` |
| TU-03 | `verify_password` | mauvais mot de passe | `False` |
| TU-04 | `hash_password` | même mot de passe, deux appels | empreintes **différentes** (sel aléatoire) |
| TU-05 | `generate_access_token` | `user_id` | JWT HS256 décodable, `sub` correct |
| TU-06 | `decode_access_token` | jeton expiré | `ValueError("Token expiré")` |
| TU-07 | `decode_access_token` | jeton signé avec une autre clé | `ValueError` |
| TU-08 | `hash_refresh_token` | un jeton | SHA-256 de 64 caractères hexadécimaux, déterministe |
| TU-09 | `build_prompt` | `reformuler` + contenu | contient le gabarit et le contenu |
| TU-10 | `build_prompt` | action inconnue | `ValueError` |
| TU-11 | `build_prompt` | avec instructions | la consigne est concaténée |
| TU-12 | `call_ollama` | connexion refusée | `RuntimeError` mentionnant l'URL |
| TU-13 | `call_ollama` | délai dépassé | `RuntimeError("trop de temps")` |
| TU-14 | `call_ollama` | réponse nominale | `(texte, jetons)`, jetons = somme des deux compteurs |

### 7.2 · Tests d'intégration — authentification

| ID | Objet | Entrée | Attendu |
|---|---|---|---|
| TI-01 | `POST /auth/register` | données valides | `201`, utilisateur en base, mot de passe haché |
| TI-02 | `POST /auth/register` | adresse déjà prise | erreur, **pas de création** |
| TI-03 | `POST /auth/register` | champ manquant | `400` |
| TI-04 | `POST /auth/login` | identifiants valides | `200`, `access_token`, cookie de rafraîchissement posé |
| TI-05 | `POST /auth/login` | mot de passe erroné | `401`, message **indifférencié** |
| TI-06 | `POST /auth/login` | compte inexistant | `401`, **message identique à TI-05** |
| TI-07 | cookie de rafraîchissement | après connexion | `HttpOnly`, `SameSite=Strict`, `Path=/auth` |
| TI-08 | `POST /auth/refresh` | cookie valide | `200`, nouveau jeton, **ancien invalidé** |
| TI-09 | `POST /auth/refresh` | cookie rejoué | `401`, session supprimée |
| TI-10 | `POST /auth/refresh` | sans cookie | `401` |
| TI-11 | `POST /auth/logout` | session active | `200`, ligne `user_session` supprimée |
| TI-12 | `GET /auth/me` | sans en-tête | `401` |
| TI-13 | `GET /auth/me` | jeton valide | `200`, identité correcte, **jamais `mdp_hash`** |
| TI-14 | `POST /auth/forgot-password` | adresse inconnue | `200` — **réponse identique** à une adresse connue |

### 7.3 · Tests d'intégration — documents et dossiers

| ID | Objet | Entrée | Attendu |
|---|---|---|---|
| TI-20 | `POST /documents` | titre valide | `201`, document rattaché à l'utilisateur |
| TI-21 | `POST /documents` | statut hors liste blanche | `400` (RG-05) |
| TI-22 | `GET /documents` | deux utilisateurs, un document chacun | **chacun ne voit que le sien** (RG-01) |
| TI-23 | `GET /documents/<id>` | document d'autrui | **`404`**, pas `403` |
| TI-24 | `PUT /documents/<id>` | document d'autrui | `404`, **contenu inchangé en base** |
| TI-25 | `DELETE /documents/<id>` | son propre document | `204`, supprimé |
| TI-26 | `DELETE /documents/<id>` | document d'autrui | `404`, **toujours présent en base** |
| TI-27 | `POST /dossiers` | nom valide | `201` |
| TI-28 | `DELETE /dossiers/<id>` | dossier contenant 2 documents | `204`, **documents conservés**, `id_dossier` à `NULL` (RG-03) |
| TI-29 | suppression d'un utilisateur | compte avec documents, dossiers, IA | **toutes** les lignes liées supprimées (RG-04, RGPD art. 17) |
| TI-30 | `GET /documents/stats` | 3 documents de statuts différents | compte correct par statut |

### 7.4 · Tests d'intégration — IA

| ID | Objet | Entrée | Attendu |
|---|---|---|---|
| TI-40 | `POST …/ia/generer` | nominal, modèle doublé | `201`, suggestion, **ligne `ia` créée** |
| TI-41 | — | `type_action` hors liste | `400` (RG-06) |
| TI-42 | — | `scope` hors liste | `400` |
| TI-43 | — | contenu vide | `400` |
| TI-44 | — | contenu de la borne + 1 caractère | `400` (RG-08) |
| TI-45 | — | contenu au-delà de la borne configurée | `201` — **borne incluse** |
| TI-46 | — | instructions de 501 caractères | `400` |
| TI-47 | — | document d'autrui | `404` |
| TI-48 | — | 20 appels déjà dans les 24 h | `429` (RG-07) |
| TI-49 | — | 20 appels dont 1 **au-delà de 24 h** | `201` — **fenêtre glissante** |
| TI-50 | — | Ollama injoignable | `502`, **aucune ligne `ia` créée** |
| TI-51 | — | sans authentification | `401` |
| TI-52 | `GET …/ia/historique` | 3 appels | 3 entrées, **ordre antichronologique** |
| TI-53 | `GET …/ia/historique` | document d'autrui | `404` |

> **TI-45, TI-49 et TI-50 sont les trois cas qui comptent.** TI-45 vérifie que la borne est
> inclusive et pas exclusive. TI-49 vérifie que le quota est bien **glissant** et non remis à zéro.
> TI-50 vérifie qu'un appel échoué ne consomme pas de quota — sinon une panne d'Ollama épuiserait
> le quota de l'utilisateur sans lui rendre aucun service.

### 7.5 · Tests d'intégration — administration

| ID | Objet | Entrée | Attendu |
|---|---|---|---|
| TI-60 | `GET /admin/users` | utilisateur standard | **`403`** |
| TI-61 | `GET /admin/users` | administrateur | `200`, liste avec compteurs |
| TI-62 | `PATCH /admin/users/<id>` | rôle invalide | `400` |
| TI-63 | `PATCH /admin/users/<id>` | quota négatif | `400` |
| TI-64 | `DELETE /admin/users/<id>` | utilisateur standard appelant | `403` |
| TI-65 | `GET /admin/stats` | administrateur | `200`, totaux cohérents |

### 7.6 · Tests de sécurité

| ID | Vulnérabilité | Scénario | Attendu |
|---|---|---|---|
| TSEC-01 | XSS stocké | `<img src=x onerror=alert(1)>` dans un document | attribut `onerror` supprimé au rendu |
| TSEC-02 | XSS stocké | `<script>alert(1)</script>` | balise supprimée |
| TSEC-03 | XSS | `<a href="javascript:alert(1)">` | protocole neutralisé |
| TSEC-04 | XSS | `<svg/onload=alert(1)>` | gestionnaire supprimé |
| TSEC-05 | non-régression | Markdown légitime (gras, listes, liens, code) | **rendu préservé** |
| TSEC-06 | injection SQL | `' OR '1'='1` dans un titre | traité comme du texte, stocké tel quel |
| TSEC-07 | fuite de secret | base après connexion | **aucun jeton en clair** (RG-10) |
| TSEC-08 | rejeu de session | rotation puis réutilisation | session invalidée (TI-09) |
| TSEC-09 | échec sécurisé | démarrage sans `JWT_SECRET_KEY` | **refus de démarrer** |
| TSEC-10 | CSRF | attribut `SameSite` du cookie | `Strict` |
| TSEC-11 | accès horizontal | parcours des identifiants d'autrui | `404` systématique |
| TSEC-12 | escalade de privilèges | jeton d'un utilisateur standard sur `/admin` | `403` |
| TSEC-13 | intégrité référentielle | suppression d'un utilisateur | aucune ligne orpheline (TI-29) |
| TSEC-14 | limitation de débit | 35 appels sur `/auth/refresh` | `429` déclenché, mais pas avant le 26ᵉ appel |
| TSEC-15 | échec sécurisé | démarrage sans `SECRET_KEY` | **refus de démarrer**, et clé distincte de `JWT_SECRET_KEY` |

### 7.7 · Tests unitaires — frontend

| ID | Objet | Entrée | Attendu |
|---|---|---|---|
| TU-F01 | `getStatusStyle` | les 3 statuts | une classe non vide par statut |
| TU-F02 | `statusLabels` | les 3 statuts | libellés français corrects |
| TU-F03 | rendu Markdown | les 6 cas de `test_xss.mjs` | reprise de TSEC-01 à TSEC-05 **avec assertions** |
| TU-F04 | intercepteur de requête | jeton présent dans le magasin | en-tête `Authorization` ajouté |
| TU-F05 | intercepteur de réponse | `401` | un seul appel à `/auth/refresh`, requête rejouée |
| TU-F06 | intercepteur de réponse | deux `401` simultanés | **un seul** rafraîchissement, les deux requêtes rejouées |
| TU-F07 | intercepteur de réponse | `401` sur `/auth/refresh` | pas de boucle, redirection vers la connexion |
| TU-F08 | magasin `auth` | `clearAuth` | jeton et identité remis à zéro |

> **TU-F06 est le test qui justifie l'existence du fichier.** La mutualisation des `401`
> concurrents est le mécanisme le plus subtil du frontend : sans elle, dix requêtes simultanées
> déclenchent dix rotations de jeton, et la détection de rejeu déconnecte l'utilisateur. C'est
> typiquement le genre de régression qu'une relecture ne rattrape pas.

### 7.8 · Tests système — manuels

| ID | Parcours | Résultat attendu |
|---|---|---|
| TS-01 | inscription → connexion → tableau de bord | compte créé, session ouverte |
| TS-02 | mot de passe oublié → mail → réinitialisation → connexion | nouveau mot de passe actif, ancien refusé |
| TS-03 | créer un document → rédiger → enregistrement automatique → recharger | contenu conservé |
| TS-04 | sélectionner du texte → reformuler → remplacer | texte remplacé, entrée visible dans l'historique |
| TS-05 | créer un dossier → y classer un document → supprimer le dossier | document conservé, déclassé |
| TS-06 | épuiser le quota IA | message explicite, pas d'erreur technique |
| TS-07 | arrêter Ollama → demander une suggestion | message explicite, éditeur utilisable |
| TS-08 | connexion en administrateur → back-office | comptes et statistiques affichés |
| TS-09 | navigation **au clavier seul** sur un parcours complet | tout atteignable, focus visible |
| TS-10 | restitution par lecteur d'écran de l'éditeur | zones et boutons annoncés |

### 7.9 · Tests d'acceptation

Exécutés avec le formateur dans son rôle de commanditaire. Un cas par besoin fonctionnel,
BF-01 à BF-19, tracé dans la [matrice de traçabilité](./conception/02-cas-utilisation.md#23--matrice-de-traçabilité).

---

## 8 · Jeu d'essai de la fonctionnalité la plus représentative

> Production exigée du dossier de projet : *« la présentation d'un jeu d'essai élaboré par le
> candidat de la fonctionnalité la plus représentative (données en entrée, données attendues,
> données obtenues) et analyse des écarts éventuels »*.

**Fonctionnalité : génération IA sur un document** (UC-10).

### État initial

| Table | Contenu |
|---|---|
| `user` | `U1` (standard, quota 20), `U2` (standard) |
| `document` | `D1` appartenant à `U1`, `D2` appartenant à `U2` |
| `ia` | vide |

### Cas d'essai

Exécuté le **3 octobre 2026**, modèle d'inférence remplacé par un double.

| # | Entrée | Attendu | Obtenu | Écart | Test |
|---|---|---|---|---|---|
| JE-01 | `U1`, `D1`, `reformuler` | `201`, suggestion non vide, 1 ligne `ia` | `201`, suggestion rendue, 1 ligne `ia` portant action, contenu avant et après, jetons | aucun | TI-40 |
| JE-02 | `U1`, `D1`, `corriger` puis `completer` | `201`, 3 lignes `ia` au total | `201`, 3 lignes, ordre antichronologique à la relecture | aucun | TI-52 |
| JE-03 | `U1`, `D1`, `traduire` *(hors liste)* | `400` | `400`, aucune ligne `ia` | aucun | TI-41 |
| JE-04 | `U1`, **`D2`**, `reformuler` | `404` | `404`, aucune ligne `ia` | aucun | TI-47 |
| JE-05 | `U1`, `D1`, contenu de la borne + 1 caractère | `400` | `400` | aucun | TI-44 |
| JE-05b | `U1`, `D1`, contenu au-delà de la borne configurée | `201` | `201` — borne inclusive confirmée | aucun | TI-45 |
| JE-06 | `U1`, `D1`, 20 lignes `ia` sur 24 h | `429` | `429`, compteur figé à 20 | aucun | TI-48 |
| JE-07 | 19 lignes récentes + 1 datée de 25 h | `201` | `201` — fenêtre bien glissante | aucun | TI-49 |
| JE-08 | `U1`, `D1`, service d'inférence en panne | `502`, **0 nouvelle ligne `ia`** | `502`, 0 ligne : le quota n'est pas consommé | aucun | TI-50 |
| JE-09 | historique de `D1` par `U1` | ordre antichronologique | conforme | aucun | TI-52 |
| JE-10 | historique de `D1` par **`U2`** | `404` | `404` | aucun | TI-53 |

**Analyse des écarts.** Aucun écart sur les onze cas. Deux résultats méritent d'être relevés
parce qu'ils n'allaient pas de soi :

- **JE-05 / JE-05b** — tester seulement la borne + 1 caractère ne distinguerait pas un `>` d'un `>=`.
  Les deux côtés de la borne sont nécessaires pour prouver qu'elle est inclusive.
- **JE-08** — un appel échoué n'écrit aucune ligne `ia`, donc ne consomme pas de quota. Sans
  cette propriété, une panne du service d'inférence épuiserait le quota de l'utilisateur sans
  lui rendre le moindre service.

> **Limite assumée.** Le service d'inférence est remplacé par un double : ce jeu d'essai valide
> la mécanique, pas la qualité linguistique des suggestions, qui n'est pas déterministe et ne
> peut pas faire l'objet d'une assertion. L'exécution avec Ollama réel reste à faire, en test
> système (TS-04).

---

## 9 · Critères d'entrée et de sortie

**Entrée** — l'obstacle de testabilité du §4.1 est levé, et l'environnement du §3 est en place.

**Sortie de la v1**

| Critère | Seuil |
|---|---|
| Tests unitaires et d'intégration | **100 % exécutés, 100 % au vert** |
| Tests de sécurité TSEC-01 à TSEC-13 | **100 % au vert — bloquant** |
| Couverture des routes | ≥ 80 % |
| Couverture de `services/` | ≥ 90 % |
| Tests système TS-01 à TS-10 | exécutés et consignés |
| Jeu d'essai JE-01 à JE-10 | exécuté, écarts analysés |
| Durée de la suite automatisée | < 60 s |

> Un seuil de couverture ne vaut rien seul : 100 % de couverture avec des assertions creuses ne
> prouve rien. Les seuils ci-dessus sont des garde-fous, la vraie exigence est que **chaque règle
> de gestion RG-01 à RG-10 ait au moins un test qui échoue si on la retire**.

### Traçabilité règles de gestion → tests

| Règle | Tests |
|---|---|
| RG-01 cloisonnement par utilisateur | TI-22, TI-23, TI-24, TI-26, TI-47, TI-53, TSEC-11 |
| RG-02 document dans au plus un dossier | TI-28 |
| RG-03 supprimer un dossier déclasse | TI-28 |
| RG-04 suppression en cascade | TI-29, TSEC-13 |
| RG-05 statuts en liste blanche | TI-21 |
| RG-06 actions IA en liste blanche | TI-41 |
| RG-07 quota glissant sur 24 h | TI-48, TI-49, JE-06, JE-07 |
| RG-08 bornes de taille | TI-44, TI-45, TI-46 |
| RG-09 rotation et rejeu | TI-08, TI-09, TSEC-08 |
| RG-10 aucun jeton en clair | TU-08, TSEC-07 |

---

## 10 · Qui fait quoi, quand, sur quel environnement

| Phase | Qui | Quand | Environnement |
|---|---|---|---|
| Tests unitaires et d'intégration | candidate | à chaque commit, en local | poste, SQLite en mémoire |
| Non-régression | CI GitHub Actions | à chaque poussée et pull request | conteneur Ubuntu |
| Tests de sécurité | candidate | à chaque commit, et avant chaque livraison | poste et CI |
| Tests système | candidate | avant chaque jalon | poste, pile complète |
| Audit d'accessibilité | candidate | une fois avant la soutenance | Lighthouse, WAVE |
| Tests d'acceptation | formateur | au point d'étape de validation | poste, pile complète |
| Tests de charge | candidate | après la conteneurisation | pile en conteneurs |

---

## 11 · Suivi d'exécution

### Campagne v1 — 3 octobre 2026

| Suite | Exécutés | Succès | Échecs | Durée |
|---|---:|---:|---:|---:|
| pytest — unitaires | 50 | 50 | 0 | — |
| pytest — intégration | 79 | 79 | 0 | — |
| pytest — sécurité | 17 | 17 | 0 | — |
| **Total backend** | **146** | **146** | **0** | **57 s** |
| Vitest — frontend | 42 | 42 | 0 | 2 s |
| **Total** | **188** | **188** | **0** | **59 s** |

*Mise à jour du 3 octobre, seconde campagne : +7 tests couvrant les correctifs de sécurité
(purge des sessions, limitation de débit sur le rafraîchissement, clé de session Flask).*

### Couverture

| Module | Couverture | Seuil | |
|---|---:|---:|:---:|
| `app/routes/` | 89 – 96 % | ≥ 80 % | ✅ |
| `app/services/` | 100 % | ≥ 90 % | ✅ |
| `database/db.py` | 100 % | — | ✅ |
| **Backend, total** | **95 %** | — | ✅ |
| Frontend (`utils`, `stores`, `services`) | 62 % | *non fixé* | — |

> La couverture frontend est tirée vers le bas par les cinq modules de service
> (`authService`, `documentService`, `dossierService`, `iaService`, `adminService`), qui sont
> des enveloppes d'une ligne autour d'`api`. Les tester reviendrait à tester axios. Ce qui
> porte de la logique — intercepteurs, magasin de session, assainissement, utilitaires — est
> couvert.

### Critères de sortie

| Critère | Seuil | Résultat | |
|---|---|---|:---:|
| Tests unitaires et d'intégration | 100 % au vert | 181 / 181 | ✅ |
| Tests de sécurité (bloquant) | 100 % au vert | 17 / 17 + 13 côté frontend | ✅ |
| Couverture des routes | ≥ 80 % | 89 – 96 % | ✅ |
| Couverture de `services/` | ≥ 90 % | 100 % | ✅ |
| Durée de la suite | < 60 s | 57 s | ✅ |
| Jeu d'essai JE-01 à JE-10 | exécuté, écarts analysés | 11 cas, 0 écart | ✅ |
| Tests système TS-01 à TS-10 | exécutés et consignés | **non exécutés** | ⬜ |
| Tests d'acceptation | avec le commanditaire | **non exécutés** | ⬜ |
| Tests de charge | après conteneurisation | **non exécutés** | ⬜ |

### Défaut trouvé et corrigé pendant la campagne

| Ticket | Défaut | Correction |
|---|---|---|
| `KAN-93` | `DELETE /documents/<id>` renvoyait `return "",` — un tuple à un seul élément, que Flask refuse. La route produisait une **erreur 500** au lieu d'un `204`, et le document était pourtant bien supprimé. | `return "", 204`. Le test TI-25 échoue si la régression revient. |

### Point de testabilité levé

`database/db.py` liait le moteur SQLAlchemy à un chemin de fichier en dur dès l'import, sans
aucun point de configuration : aucun test ne pouvait viser une autre base. L'URL est désormais
lue dans `HELPMEDRAFT_DB_URL`, avec le fichier actuel pour valeur par défaut — le comportement
hors tests est inchangé. Le même point de configuration servira pour la migration MySQL
(`KAN-86`) et la conteneurisation (`KAN-15`).

Vérification de l'hermétisme : après exécution complète de la suite, aucun fichier
`HelpMeDraft.db` n'est créé sur le disque, et aucun appel réseau n'est émis.

### Campagnes suivantes

| Campagne | Date | Exécutés | Succès | Échecs | Observations |
|---|---|---|---|---|---|
| v2 — correctifs de sécurité | 03/10/2026 | 188 | 188 | 0 | +7 tests ; voir [rapport d'audit de sécurité](./audit-securite.md) |
| | | | | | |
