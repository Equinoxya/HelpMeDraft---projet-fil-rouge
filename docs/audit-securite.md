# Rapport d'audit de sécurité — HelpMeDraft

> Livrable fonctionnel exigé par le [cahier des charges](./cahier-des-charges.md) : *« Rapport
> d'audit d'accessibilité et de sécurité »*.
> Critères de performance **CP 2**, **CP 3** et **CP 8** (« les tests de sécurité sont réalisés »,
> « les composants métier sont sécurisés », « toutes les entrées sont contrôlées et validées »).

| | |
|---|---|
| **Date** | 3 octobre 2026 |
| **Référentiels** | OWASP Top 10 (2021), OWASP Top 10 for LLM Applications (édition 2026), recommandations ANSSI, RGPD |
| **Périmètre** | code applicatif, modèle de données, dépendances, configuration |
| **Hors périmètre** | infrastructure d'hébergement, réseau, poste de développement (non déployé à ce jour) |
| **Méthode** | relecture de code ciblée, tests de sécurité automatisés, confrontation aux entrées du [journal de veille](./veille/journal-de-veille.md) |

---

## 1 · Synthèse

| Gravité | Nombre | État |
|---|---:|---|
| 🔴 Critique | 0 | — |
| 🟠 Élevée | 0 | — |
| 🟡 Moyenne | 3 | **3 corrigées** le 3 octobre |
| 🔵 Faible | 2 | 1 risque **accepté et argumenté**, 1 à traiter |
| ⬜ Recommandation | 2 | non traitées, chiffrées ci-dessous |

**Aucune vulnérabilité critique ou élevée.** Les parades aux grandes familles d'attaque — XSS,
CSRF, injection SQL, accès horizontal, escalade de privilèges — sont en place et **couvertes par
17 tests de non-régression** qui échouent si on les retire.

Le point faible restant est le **chiffrement des données au repos**, exigé par le cahier des
charges et non réalisé. Il fait l'objet d'une proposition chiffrée au §5.

---

## 2 · Ce qui est en place

| Mesure | Mise en œuvre | Test |
|---|---|---|
| Hachage des mots de passe | bcrypt avec sel aléatoire par mot de passe | TU-01 à TU-04 |
| Politique de mot de passe | 8 caractères, majuscule, minuscule, chiffre | TU unitaires |
| Jetons d'accès | JWT HS256, durée 15 min | TU-05 à TU-07 |
| Jetons de rafraîchissement | 64 octets de `secrets.token_urlsafe`, **empreinte SHA-256 seule en base** | TU-08, TSEC-07 |
| Rotation et détection de rejeu | un jeton rejoué invalide **toutes** les sessions du compte | TI-09, TSEC-08 |
| Protection XSS | DOMPurify sur le rendu Markdown avant injection dans le DOM | 13 tests frontend |
| Protection CSRF | cookie `HttpOnly`, `SameSite=Strict`, `Path=/auth` | TI-07, TSEC-10 |
| Protection injection SQL | ORM SQLAlchemy 2.0, requêtes paramétrées exclusivement | TSEC-06 |
| Cloisonnement par utilisateur | filtrage conjoint `(identifiant, user_id)` sur chaque requête | TSEC-11, 7 tests |
| Contrôle d'accès administrateur | `require_admin` en `before_request`, vérifié serveur | TSEC-12 |
| Validation des entrées | listes blanches fermées, bornes de taille | 15 tests |
| Échec sécurisé au démarrage | refus de démarrer sans clé de signature | TSEC-09, TSEC-15 |
| Limitation de débit | `/register` 3/h, `/login` 5/min, `/forgot-password` 3/h, `/refresh` 30/min | TSEC-14 |
| Intégrité référentielle | `ON DELETE CASCADE`, PRAGMA `foreign_keys` activé | TSEC-13, TI-29 |
| Confidentialité vis-à-vis des tiers | **inférence locale : aucun contenu utilisateur ne sort de l'infrastructure** | — |

### Deux choix qui méritent d'être soulignés

**Le jeton d'accès reste en mémoire JavaScript, jamais en `localStorage`.** Un XSS exfiltrerait
immédiatement un jeton rangé dans `localStorage`. La session persiste malgré tout, parce que le
secret durable — le jeton de rafraîchissement — vit dans un cookie `HttpOnly` inaccessible à
JavaScript. C'est le bon compromis, et il est testé.

**L'application refuse de démarrer sans clé de signature.** `app/config.py` ne prévoit aucune
valeur de repli. Une clé en dur dans le dépôt permettrait à quiconque le lit de forger un jeton
valide pour n'importe quel compte. Un échec bruyant au démarrage vaut mieux qu'un démarrage
silencieusement vulnérable.

---

## 3 · Constats corrigés le 3 octobre 2026

### 3.1 🟡 `/auth/refresh` sans limitation de débit — **corrigé**

| | |
|---|---|
| **Ticket** | `KAN-95` |
| **OWASP** | A04:2021 — Insecure Design |
| **Gravité** | moyenne |

**Constat.** Trois routes d'authentification étaient protégées par Flask-Limiter — `/register`,
`/login`, `/forgot-password` — mais **pas `/auth/refresh`**, alors qu'elle émet des jetons
d'accès.

**Analyse.** Le jeton de rafraîchissement fait 64 octets tirés au hasard : le deviner par force
brute est hors de portée, la limite ne protège donc pas le secret. Le risque réel est
l'**épuisement de ressources** — chaque appel déclenche une lecture, une écriture et une
suppression en base — et le **martèlement automatisé** si un cookie fuit.

**Correctif.** `@limiter.limit("30 per minute")`. Ce plafond laisse largement passer un usage
normal : un rafraîchissement toutes les 15 minutes par session, même avec plusieurs onglets ou
appareils derrière une même adresse IP.

**Vérification.** `TSEC-14` réactive la limitation, émet 35 appels, et vérifie à la fois qu'un
`429` survient et qu'il ne survient **pas avant le 26ᵉ** — une limite trop basse casserait
l'usage multi-onglets.

### 3.2 🟡 Accumulation des sessions mortes — **corrigé**

| | |
|---|---|
| **Ticket** | `KAN-96` |
| **OWASP** | A04:2021 — Insecure Design |
| **Gravité** | moyenne |

**Constat.** La table `user_session` n'était **jamais purgée**. Deux sources d'accumulation : les
sessions jamais fermées dont le jeton expire au bout de 7 jours, et les sessions marquées
révoquées par la rotation — c'est-à-dire **une ligne par rafraîchissement**, soit potentiellement
une toutes les 15 minutes et par session.

**Analyse.** Le risque n'est pas une fuite mais une dérive : croissance non bornée d'une table
contenant des empreintes de jetons, et dégradation progressive des requêtes de session, qui sont
sur le chemin critique de chaque requête authentifiée.

**Correctif.** `purge_expired_sessions(user_id=None)`, appelée à chaque connexion pour le compte
concerné, et utilisable sans argument par une tâche planifiée.

> **Le point délicat.** Le critère de purge est **l'expiration**, pas le drapeau `revoke`. Une
> session révoquée doit survivre jusqu'au terme de son jeton : sinon un jeton volé puis rejoué
> ne serait plus reconnu comme un rejeu — il serait simplement « inconnu » — et la détection de
> vol tomberait **silencieusement**. Purger sur `revoke` aurait donc introduit une faille en
> croyant faire du ménage. Un test dédié verrouille ce comportement.

**Vérification.** 4 tests, dont `test_purge_conserve_une_session_revoquee_non_expiree`, qui
échoue si le critère de purge est changé.

### 3.3 🟡 Divergence entre la contrainte SQL et la validation applicative — **corrigé**

| | |
|---|---|
| **Ticket** | `KAN-98` |
| **OWASP** | A04:2021 — Insecure Design |
| **Gravité** | moyenne |

**Constat.** `schema_mysql.sql` autorisait `quota_daily_limit BETWEEN 0 AND 1000`, tandis que
l'API refuse toute valeur inférieure à 1 (`MIN_QUOTA`). Deux gardiens de la même règle, en
désaccord.

**Analyse.** Une divergence de ce type est toujours un défaut, même quand le gardien le plus
strict est devant : elle signale que les deux niveaux ont été écrits séparément, et le jour où
une écriture contourne l'API — script de migration, reprise de données — la base accepte une
valeur que l'application considère invalide.

**Décision.** La base s'aligne sur l'API, borne basse à 1. Un quota de 0 serait un compte bridé
sans que rien ne le signale : couper l'accès à l'IA relève d'un champ explicite, pas de la valeur
nulle d'un compteur.

**Correctif.** Contrainte `CHECK` modifiée dans `schema_mysql.sql` et
`migration_durcissement.sql`, plus un script de migration dédié
[`migration_quota_min.sql`](../backend/database/migration_quota_min.sql) qui remonte d'abord les
lignes existantes à 0 pour qu'aucune ne viole la nouvelle contrainte.

### 3.4 🔵 `SECRET_KEY` Flask non configurée — **corrigé**

| | |
|---|---|
| **OWASP** | A02:2021 — Cryptographic Failures |
| **Gravité** | faible (aucun impact actuel) |

**Constat.** `SECRET_KEY` n'était pas définie. Flask s'en sert pour signer les cookies de session
et les messages flash — aucun des deux n'est utilisé aujourd'hui, d'où la gravité faible.

**Analyse.** Le risque est différé : le premier usage ajouté de `session` ou de `flash()`
échouerait, ou pire, fonctionnerait avec une clé nulle.

**Correctif.** `SECRET_KEY` exigée au démarrage, selon le même principe d'échec bruyant que
`JWT_SECRET_KEY`, et **distincte de celle-ci** : réutiliser une même clé pour deux usages
cryptographiques différents fait qu'une fuite sur l'un compromet l'autre.

**Vérification.** `TSEC-15` vérifie le refus de démarrer, `TSEC-15b` que les deux clés diffèrent.

> ⚠️ **Action requise côté développement.** Ajouter `SECRET_KEY` à votre `backend/.env` avant de
> relancer l'application. `.env.example` documente la variable et la commande de génération.

---

## 4 · Constats non corrigés

### 4.1 🔵 Énumération de comptes à l'inscription — **risque accepté**

| | |
|---|---|
| **Ticket** | `KAN-94` |
| **OWASP** | A07:2021 — Identification and Authentication Failures |
| **Gravité** | faible |
| **Décision** | **risque accepté**, 3 octobre 2026 |

**Constat.** `POST /auth/register` répond `409` avec « Cet email est déjà utilisé » quand
l'adresse existe. Un attaquant peut donc déterminer si une adresse est enregistrée.

**Analyse du risque.** La route est **déjà limitée à 3 requêtes par heure et par adresse IP**,
soit **72 adresses testables par jour**. Énumérer un annuaire à ce rythme n'est pas une attaque
praticable. Par contraste, `/auth/forgot-password` et `/auth/login` répondent, eux, de façon
strictement indifférenciée — vérifié par les tests `TI-05`, `TI-06` et `TI-14` — donc les deux
routes réellement exposées à l'énumération de masse sont couvertes.

**Options examinées.**

| Option | Sécurité | Coût |
|---|---|---|
| Réponse uniforme + courriel (recommandation OWASP) | élevée | l'inscription devient muette à l'écran ; dépend du SMTP ; si le mail ne part pas, l'utilisateur ne sait plus rien |
| **Conserver le `409`** | suffisante au vu du plafond de débit | aucun |

**Décision retenue : conserver le comportement actuel.** Le gain de sécurité ne compense pas la
perte d'ergonomie à l'inscription, étant donné le plafond de 3 requêtes par heure. La décision
est tracée ici plutôt que le ticket fermé en silence.

> Un test, `test_ti02b_inscription_revele_l_existence_du_compte`, **fige ce comportement** et
> porte en commentaire l'instruction de l'inverser le jour où la décision changera. L'écart est
> ainsi visible dans la suite de tests, pas seulement dans ce rapport.

**Réexamen** — si le plafond de débit est relevé, ou si l'application sort du cadre pédagogique
pour un usage réel, la décision doit être rejouée.

### 4.2 🔵 Chaîne de mise à jour d'Ollama sur Windows

| | |
|---|---|
| **Ticket** | `KAN-100` |
| **Références** | CVE-2026-42248, CVE-2026-42249, publiées le 29 avril 2026 |
| **Gravité** | élevée **sur le poste de développement**, hors périmètre applicatif |

**Constat.** La version Windows d'Ollama ne vérifie aucune signature avant d'exécuter une mise à
jour, et construit les chemins de fichiers à partir d'en-têtes HTTP non validés. Enchaînées, ces
deux failles donnent une exécution de code **automatique et persistante**. Versions testées
vulnérables : **0.12.10 à 0.17.5**.

**Pourquoi ce n'est pas un défaut du code de HelpMeDraft** — il s'agit d'un composant tiers
installé sur le poste. L'application ne peut ni le corriger ni le détecter.

**Actions requises, hors code :**

1. Relever la version installée : `ollama --version`. Si elle est inférieure à 0.18, mettre à
   jour — la version courante de l'outil est la 0.33.x.
2. **Restreindre l'écoute d'Ollama à la boucle locale** : `OLLAMA_HOST=127.0.0.1:11434`. L'API
   d'inférence n'a aucune authentification ; exposée sur le réseau, n'importe qui peut
   l'interroger, charger un modèle, ou saturer la machine.
3. Lors de la conteneurisation (`KAN-15`), **ne pas publier le port 11434** hors du réseau du
   compose.

---

## 5 · Recommandations non traitées

### 5.1 ⬜ Chiffrement des données sensibles au repos

| | |
|---|---|
| **Exigence** | cahier des charges, « Sécurité » : *« Stockage des données sensibles chiffré »* |
| **OWASP** | A02:2021 — Cryptographic Failures |
| **État** | **non réalisé** |

**Constat.** Le contenu des documents (`document.content`) et l'historique IA
(`ia.content_before`, `ia.content_after`) sont stockés en clair. Ce sont les données les plus
personnelles de l'application : des courriers et notes professionnels.

**Ce qui est déjà protégé** — mots de passe (bcrypt), jetons de session et de réinitialisation
(empreintes SHA-256 seules). Aucun secret d'authentification n'est en clair, ce que vérifie
`TSEC-07`.

**Pourquoi ce n'est pas corrigé dans ce lot.** Le chiffrement applicatif n'est pas une ligne de
code, c'est une décision d'architecture avec trois conséquences :

1. **Gestion de la clé** — une clé en variable d'environnement protège d'une fuite de sauvegarde,
   pas d'une compromission du serveur, puisque l'application doit pouvoir déchiffrer. La vraie
   protection demande un coffre (KMS, Vault), hors périmètre du projet.
2. **Perte de la recherche** — un champ chiffré n'est ni filtrable ni triable en SQL. Toute
   recherche future dans le contenu devrait se faire en mémoire, après déchiffrement.
3. **Réversibilité** — chiffrer suppose une migration des données existantes et une procédure de
   rotation de clé.

**Proposition chiffrée**

| Option | Protège de | Ne protège pas de | Effort |
|---|---|---|---|
| **A** — chiffrement applicatif par champ (`cryptography`, Fernet), clé en variable d'environnement | fuite de sauvegarde, vol de fichier de base | compromission du serveur applicatif | ~1 j + migration |
| **B** — chiffrement au niveau du SGBD (MySQL `TDE` ou chiffrement du volume) | vol du disque ou du fichier | tout accès via le SGBD | ~2 h, dépend de `KAN-86` |
| **C** — les deux | les deux surfaces | — | ~1,5 j |

**Recommandation : option A sur les trois champs de contenu**, avec la clé en variable
d'environnement distincte des deux autres, et une mention explicite en soutenance de ce qu'elle
ne protège pas. C'est proportionné au contexte du projet et honnête sur ses limites.

### 5.2 ⬜ Épinglage des dépendances transitives

| | |
|---|---|
| **Ticket** | `KAN-102` |
| **OWASP** | A06:2021 — Vulnerable and Outdated Components |

**Constat.** `backend/requirements.txt` porte en commentaire « Versions figées volontairement
(reproductibilité des builds et de la CI) », mais n'épingle que les dépendances directes.
Werkzeug, dépendance de Flask, n'est pas épinglée — or CVE-2026-102598 l'affecte en 3.1.8,
corrigée en 3.1.9.

**Conséquence.** Deux installations à deux dates différentes peuvent embarquer deux versions
différentes, dont une vulnérable, sans que rien ne le signale. **Tant que l'arbre complet n'est
pas gelé, aucun verdict de veille sur le backend n'est réellement vérifiable.**

**Correctif recommandé** — `pip-compile` (pip-tools) pour produire un `requirements.lock`
exhaustif, puis `pip-audit` et `npm audit` dans la CI, plus Dependabot sur le dépôt.

---

## 6 · État des dépendances

Relevé le 3 octobre 2026 sur les **versions résolues** (`package-lock.json`,
`requirements.txt`), et non sur les plages déclarées. Détail et sources dans le
[journal de veille](./veille/journal-de-veille.md).

| Composant | Version | CVE 2026 examinées | Verdict |
|---|---|---|---|
| DOMPurify | 3.4.16 | CVE-2026-0540, -41238, -47423, -49978, -66010 | ✅ non affecté |
| Vite | 8.3.1 | CVE-2026-39363, -39364 | ✅ non affecté |
| Flask | 3.1.3 | CVE-2026-27205 | ✅ non affecté |
| PyJWT | 2.15.0 | CVE-2026-48526 | ✅ non affecté |
| axios | 1.20.0 | compromission npm du 31/03/2026 | ✅ non affecté |
| **Werkzeug** | **non épinglée** | CVE-2026-102598 | ⚠️ **indéterminé** |
| Ollama | à relever | CVE-2026-42248, -42249, -7482 | ⚠️ à vérifier (§4.2) |

> **Consigne permanente issue de la veille** — ne jamais lancer le serveur de développement Vite
> avec `--host`, et ne pas publier le port 5173 dans la configuration Docker. F5 Labs a relevé
> plus de 32 000 attaques en août 2026 ciblant des serveurs Vite exposés, à la recherche de
> fichiers `.env`. Le nôtre contient `JWT_SECRET_KEY`, `SECRET_KEY` et les identifiants SMTP.

---

## 7 · Exposition aux risques OWASP Top 10 for LLM Applications 2026

L'édition 2026, publiée le 4 août, place l'**agentivité excessive** en 3ᵉ position (contre 6ᵉ en
2025). Analyse détaillée dans le [journal de veille](./veille/journal-de-veille.md) §3.5.

| Risque | Exposition | Pourquoi |
|---|---|---|
| 1 · Injection de prompt | 🟡 **réelle, impact borné** | le contenu du document est concaténé au gabarit ; mais le modèle n'a aucun outil, et l'utilisateur valide chaque suggestion |
| 2 · Divulgation d'informations sensibles | 🟢 faible | inférence locale, aucun apprentissage sur les données |
| 3 · Agentivité excessive | 🟢 **nulle par conception** | le modèle renvoie du texte, rien d'autre ; aucun appel d'outil, aucune écriture déclenchée par sa sortie |
| 7 · Consommation non bornée | 🟢 traitée | quota glissant 20/24 h, contenu plafonné par une borne configurable, délai maximum de 60 s |
| 10 · Traitement inadéquat des sorties | 🟢 traitée | la sortie passe par DOMPurify et n'est jamais écrite sans action de l'utilisateur |

> **L'argument à porter en soutenance.** Les deux risques qui montent dans l'édition 2026 sont
> précisément ceux que l'architecture traite déjà — l'un par conception, l'autre par le quota.
> Le risque qui reste ouvert est l'injection de prompt, structurellement difficile à éliminer :
> séparer instructions et données dans un prompt textuel est un problème non résolu. La parade
> retenue est donc la **limitation de l'impact** plutôt que la prévention.

---

## 8 · Conformité RGPD — points de sécurité

| Exigence | État |
|---|---|
| Consentement explicite tracé | ✅ table `consentement`, horodatée |
| Droit à l'effacement (art. 17) | ✅ `ON DELETE CASCADE` sur les 6 tables liées, vérifié par `TI-29` |
| Minimisation vis-à-vis des tiers | ✅ inférence locale, aucun transfert |
| Consentement **distinct** pour l'IA | ⬜ fondu dans celui de l'inscription |
| Droit d'accès et portabilité (art. 15, 20) | ⬜ pas d'export |
| Suppression de compte par l'utilisateur | ⬜ réservée à l'administrateur |
| Durée de conservation du journal IA | ⬜ `KAN-84` — conservation illimitée aujourd'hui |
| Chiffrement au repos | ⬜ §5.1 |

---

## 9 · Preuves

Les constats de ce rapport sont adossés à **17 tests de sécurité automatisés**, rejouables par
`pytest -m securite` côté backend et `npm test` côté frontend.

| Référence | Objet |
|---|---|
| TSEC-01 à TSEC-05 | XSS : gestionnaires d'événements, `<script>`, protocole `javascript:`, SVG, non-régression du Markdown légitime |
| TSEC-06 | injection SQL : quatre charges traitées comme du texte |
| TSEC-07 | aucun mot de passe ni jeton en clair en base |
| TSEC-08 | rejeu d'un jeton de rafraîchissement |
| TSEC-09 | refus de démarrer sans `JWT_SECRET_KEY` |
| TSEC-10 | attributs du cookie : `SameSite`, `HttpOnly`, `Path`, `Secure` |
| TSEC-11 | accès horizontal : 7 routes parcourues avec l'identifiant d'un tiers |
| TSEC-12 | escalade de privilèges vers le back-office |
| TSEC-13 | intégrité référentielle appliquée par le SGBD |
| **TSEC-14** | limitation de débit sur `/auth/refresh` *(nouveau)* |
| **TSEC-15** | refus de démarrer sans `SECRET_KEY`, et clés distinctes *(nouveau)* |

> **Le choix méthodologique à défendre.** Les tests d'assainissement portent sur le **DOM** et non
> sur la chaîne HTML. Chercher « onload » dans le texte de sortie échouerait sur une charge que
> `marked` a échappée en `&lt;svg/onload=…&gt;` : la sous-chaîne est toujours présente, mais
> c'est devenu du texte inerte. Ce qui compte n'est pas l'absence du mot, c'est l'absence
> d'élément exécutable.

---

## 10 · Suites à donner

| Priorité | Action | Ticket |
|---|---|---|
| 1 | Ajouter `SECRET_KEY` au `.env` de développement | — |
| 2 | Relever et mettre à jour Ollama, restreindre son écoute à `127.0.0.1` | `KAN-100` |
| 3 | Épingler l'arbre complet des dépendances, `pip-audit` et `npm audit` en CI | `KAN-102` |
| 4 | Chiffrement au repos — arbitrer entre les options A, B et C du §5.1 | — |
| 5 | Durée de conservation du journal IA | `KAN-84` |
| 6 | Consentement IA distinct, export et suppression de compte | — |
| 7 | Rejouer cet audit après la conteneurisation, périmètre infrastructure inclus | `KAN-15` |
