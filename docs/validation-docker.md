# Validation de la pile conteneurisée — HelpMeDraft

> Livrable attendu par les critères de performance **CP 1** (mettre en place son environnement de
> travail), **CP 10** (préparer et documenter le déploiement) et **CP 11** (contribuer à la mise en
> production dans une démarche DevOps).

| | |
|---|---|
| **Date** | 5 octobre 2026 |
| **Pile** | `docker compose up --build` — MySQL 8.4.11, backend gunicorn, frontend nginx non privilégié |
| **Docker** | Engine 29.6.2, storage driver `overlayfs`, buildkit |
| **Résultats bruts** | [`audits/tests-systeme-2026-10-05.json`](./audits/tests-systeme-2026-10-05.json) |
| **Script des tests système** | [`audits/tests-systeme.mjs`](./audits/tests-systeme.mjs) |

Jusqu'ici, la composition et les deux `Dockerfile` étaient **écrits mais jamais exécutés** : le
poste de développement n'avait pas de démon Docker, et la TODO le disait. Les quatre points propres
à MySQL 8.4 — collation `utf8mb4_0900_ai_ci`, `--set-gtid-purged=OFF`, authentification
`caching_sha2_password`, enchaînement des montages `initdb` — ne pouvaient pas être confirmés sur le
MariaDB 10.11 qui avait servi de substitut.

**Ils le sont maintenant, sur un vrai MySQL 8.4.** Ce document consigne ce qui a été vérifié, et les
deux défauts que l'exécution a révélés.

---

## 1 · Synthèse

| Lot | Résultat |
|---|---|
| `docker compose config` | ✅ composition valide |
| Construction des deux images | ✅ `docker compose build` aboutit |
| Démarrage de la pile | ✅ db saine, backend et frontend servis |
| Schéma MySQL 8.4 | ✅ 7 tables, 6 `CHECK`, 8 clés étrangères nommées, 18 index |
| Collation `utf8mb4_0900_ai_ci` | ✅ sur le schéma et les 7 tables |
| Authentification `caching_sha2_password` | ✅ les 3 comptes, et l'application se connecte |
| Enchaînement des montages `initdb` | ✅ `10-schema.sql` puis `20-droits.sh` |
| Droits au moindre privilège | ✅ `CREATE`, `DROP` et `ALTER` refusés à l'applicatif |
| Sauvegarde / restauration | ✅ aller-retour joué, données restituées à l'identique |
| Migration de traçabilité IA | ✅ appliquée sur un vrai MySQL 8.4 |
| Jeu d'essai | ✅ chargé en base MySQL (4 comptes, 7 documents, 40 appels IA) |
| Parcours applicatif de bout en bout | ✅ inscription, connexion, documents, dossiers, back-office |
| Remise à zéro documentée (`down -v`) | ✅ `initdb` est bien rejoué |
| Tests système TS-01 à TS-10 | 🔄 **7 au vert**, 1 en échec (constat n° 2), 2 hors de portée |

**Deux défauts trouvés, qu'aucune relecture de la composition n'aurait donnés.** Le premier est
corrigé ; le second est un constat de production, décrit au §4.

---

## 2 · Les quatre points propres à MySQL 8.4

Ce sont ceux que MariaDB ne permettait pas de confirmer.

```
Version du serveur                       8.4.11
Collation du schéma                      utf8mb4 / utf8mb4_0900_ai_ci
Collation des 7 tables                   utf8mb4_0900_ai_ci (toutes)
Plugin d'authentification des 3 comptes   caching_sha2_password
Ordre des scripts initdb                 10-schema.sql → 20-droits.sh
mysqldump --set-gtid-purged=OFF          accepté, 0 instruction SET GTID_PURGED dans l'archive
```

L'authentification mérite un mot : MySQL 8.4 utilise `caching_sha2_password`, que PyMySQL ne sait
pas honorer sans le paquet `cryptography`. Son absence des dépendances avait été corrigée **par
raisonnement** lors du lot base de données, sans pouvoir être vérifiée. C'est fait : le backend se
connecte, donc le correctif était le bon.

### Schéma réellement en base

```
Tables (7)        user, document, dossier, ia, consentement, user_session, password_reset
CHECK (6)         ck_user_role, ck_user_quota, ck_document_status, ck_document_format,
                  ck_ia_action, ck_ia_insertion
Clés étrangères   fk_consentement_user (CASCADE)   fk_document_dossier (SET NULL)
(8, nommées)      fk_document_user (CASCADE)       fk_dossier_user (CASCADE)
                  fk_ia_document (CASCADE)         fk_ia_user (CASCADE)
                  fk_reset_user (CASCADE)          fk_session_user (CASCADE)
Index             18
```

Deux garanties portées par la base, et non par l'application, ont été éprouvées depuis SQL brut :

- `DELETE FROM document` **réussit** et propage la suppression aux lignes `ia`. C'est le défaut
  corrigé au lot base de données : l'ORM masquait l'absence de `ON DELETE` côté base par un
  `cascade` Python, et tout `DELETE` fait en SQL échouait sur une violation de clé étrangère.
- `INSERT` d'une trace marquée insérée **sans horodatage** est refusé (`ERROR 3819`, violation de
  `ck_ia_insertion`). Une écriture faite hors de l'application ne peut pas créer l'état incohérent.

### Droits des trois comptes

```
helpmedraft_app          SELECT, INSERT, UPDATE, DELETE
helpmedraft_sauvegarde   SELECT, LOCK TABLES, SHOW VIEW, TRIGGER
helpmedraft_migration    + CREATE, DROP, ALTER, INDEX, REFERENCES, EXECUTE, ROUTINE, TRIGGER
```

Le compte `helpmedraft` créé par l'image, qui a tous les droits sur la base, **a bien été
supprimé** : `SELECT COUNT(*) FROM mysql.user WHERE user='helpmedraft'` renvoie 0. Et depuis le
compte applicatif :

```
CREATE TABLE zzz_test (id INT);        -> ERROR 1142 (42000)
DROP TABLE user;                       -> ERROR 1142 (42000)
ALTER TABLE user ADD COLUMN zzz INT;   -> ERROR 1142 (42000)
SELECT COUNT(*) FROM user;             -> autorisé
```

### Sauvegarde et restauration

L'aller-retour a été joué pour de vrai contre MySQL 8.4 : archive produite (7 tables, marqueur de
fin présent, collation et contraintes dans le dump), **données détruites volontairement**
(`DELETE FROM user`, qui vide aussi les tables filles par cascade), puis restaurées. L'utilisateur
et le document d'essai sont revenus à l'identique.

À savoir, et le script le dit lui-même : le tableau de contrôle qu'il affiche en fin de
restauration lit `information_schema.table_rows`, qui est une **estimation** de l'optimiseur sur
InnoDB et peut afficher 0 sur une table pleine. Le vrai contrôle est un `COUNT(*)`, ou le test de
restauration du §6.4 de [l'exploitation de la base](./exploitation-base-de-donnees.md).

### Migration de traçabilité IA

Testée comme elle le sera en vrai, c'est-à-dire sur une base qui ne contient pas encore les
colonnes : les trois colonnes et la contrainte ont été retirées, puis
`migration_tracabilite_ia.sql` a été appliqué **avec le compte `helpmedraft_migration`**, celui qui
a les droits de structure. Résultat : `insere tinyint(1) NOT NULL DEFAULT 0`,
`position_debut int NULL`, `insere_at datetime NULL`, contrainte `ck_ia_insertion` recréée, 0 ligne
incohérente, et les colonnes à la bonne place dans l'ordre de la table.

---

## 3 · Constat n° 1 — `.env.example` cassait l'IA dans la pile · ✅ corrigé

`OLLAMA_URL=http://localhost:11434` était **renseignée** dans `.env.example`. Or la composition lit
le `.env` de la racine : la valeur se retrouvait donc poussée dans le conteneur backend, où
`localhost` désigne le conteneur lui-même. Tout appel au modèle échouait.

Vérifié sur la pile réelle, avant correction :

```
$ docker compose exec backend env | grep OLLAMA_URL
OLLAMA_URL=http://localhost:11434

$ curl -X POST .../ia/generer
502  « Impossible de joindre Ollama sur http://localhost:11434. »
```

C'est exactement la panne déjà corrigée pour `CORS_ORIGINS` et `FRONTEND_URL` : les deux valeurs par
défaut sont justes chacune dans son contexte — `http://localhost:11434` dans `app/config.py` pour un
lancement local, `http://host.docker.internal:11434` dans `docker-compose.yml` pour la pile — et
écrire la valeur dans `.env.example` en casse une des deux. `OLLAMA_URL` avait été oubliée.

La ligne est désormais commentée, avec la raison. Après correction, sur la même pile :

```
$ docker compose exec backend env | grep OLLAMA_URL
OLLAMA_URL=http://host.docker.internal:11434

502  « Impossible de joindre Ollama sur http://host.docker.internal:11434. »
```

L'échec subsiste — aucun Ollama ne tourne sur l'hôte de ce conteneur d'intégration — mais **la cible
est la bonne**, et c'est ce que le message prouve. `host.docker.internal` est bien résolu depuis le
backend (`172.17.0.1`), donc `extra_hosts` fait son travail sous Linux.

---

## 4 · Constat n° 2 — `/auth/forgot-password` sans délai sur le serveur de courriel · ⬜ à corriger

**C'est le constat sérieux de cette campagne, et il n'a rien à voir avec Docker : la
conteneurisation l'a seulement rendu visible.**

`POST /auth/forgot-password` envoie le courriel **dans le fil de la requête**, par `mail.send()`.
Flask-Mail construit son `smtplib.SMTP` sans délai, et `smtplib` sans délai attend indéfiniment. Si
le serveur SMTP accepte la connexion TCP puis ne répond pas — ou si le port est filtré — la requête
ne se termine jamais.

Mesuré sur la pile :

| Observation | Valeur |
|---|---|
| Durée de la requête | **> 90 s**, abandonnée par le client, le serveur tient toujours |
| Effet sur le service | `GET /auth/me` ne répond plus du tout |
| Rétablissement | `docker compose restart backend` |

Le backend tourne avec **2 workers gunicorn synchrones** : un worker bloqué, c'est la moitié de la
capacité ; deux, c'est l'API entière. Et la route est **publique et non authentifiée**. La
limitation de débit (3 requêtes par heure) compte par adresse IP *et par worker* : elle ne protège
pas de deux requêtes venues de deux adresses.

> La campagne l'a prouvé deux fois sans le vouloir : placé en tête, le test TS-02 rendait tous les
> tests suivants rouges, le service entier étant devenu injoignable. Il est désormais exécuté en
> dernier, et le script le documente à cet endroit.

Correction proposée, à arbitrer — elle touche l'authentification, donc elle n'a pas été appliquée
dans le même lot que cette validation :

1. **Un délai, tout de suite** (quelques lignes) : borner le `mail.send()` par un délai de socket et
   répondre malgré l'échec d'envoi, la route répondant déjà à l'identique que l'adresse existe ou
   non (anti-énumération). Un worker ne peut plus être immobilisé.
2. **Sortir l'envoi du fil de la requête** (la vraie correction) : file d'attente ou fil
   d'exécution, pour que la réponse HTTP ne dépende pas d'un tiers. À rapprocher du point déjà
   ouvert sur le délai côté WSGI dans [la TODO](../TODO.md) §12.

---

## 5 · Tests système TS-01 à TS-10

Exécutés sur la pile conteneurisée avec le jeu d'essai chargé en MySQL, par Playwright pour les
parcours navigateur et en direct sur l'API pour le reste.

| ID | Parcours | Verdict | Observation |
|---|---|:---:|---|
| TS-01 | inscription → connexion → tableau de bord | ✅ | compte créé, session ouverte, titre de page correct |
| TS-02 | mot de passe oublié → mail → réinitialisation | ❌ | aucune réponse : constat n° 2 |
| TS-03 | rédaction → enregistrement automatique → rechargement | ✅ | contenu conservé après rechargement |
| TS-04 | sélection → reformuler → remplacer | — | exige un Ollama joignable ; couvert par les tests d'intégration (vrai serveur HTTP de substitution) |
| TS-05 | dossier : créer → classer → supprimer le dossier | ✅ | document conservé, `id_dossier` à `null` (`ON DELETE SET NULL`) |
| TS-06 | épuiser le quota IA | ✅ | `429` et message explicite, refus **avant** tout appel au modèle |
| TS-07 | Ollama injoignable → message explicite | ✅ | `502` nommant la cible, éditeur encore utilisable |
| TS-08 | administrateur → back-office | ✅ | comptes et statistiques affichés |
| TS-09 | navigation au clavier seul | ✅ | 3 écrans, 89 prises de focus, **0 sans indication visible** |
| TS-10 | restitution par lecteur d'écran | — | exige NVDA ou VoiceOver sur une machine graphique |

**7 au vert, 1 en échec, 2 hors de portée de cet environnement.** Les deux derniers ne sont pas des
oublis : ils demandent respectivement un modèle chargé et un lecteur d'écran réel, et le dire vaut
mieux que les cocher.

Un effet de bord instructif de la campagne : `/auth/login` étant limité à **5 requêtes par minute et
par worker**, une suite de tests épuise le seuil et se voit refuser la connexion. Le script attend
la fenêtre suivante plutôt que de conclure à un échec. C'est la démonstration vécue du point déjà
ouvert sur le stockage mémoire de Flask-Limiter : les seuils ne sont pas ceux qu'on croit tant qu'ils
ne sont pas partagés entre workers.

---

## 6 · Ce qui a été mesuré, et non repris de la documentation

| Élément | Valeur mesurée |
|---|---|
| Image backend | 280 Mo |
| Image frontend | 82,9 Mo |
| Utilisateur du conteneur backend | `uid=10001(helpmedraft)` |
| Utilisateur du conteneur frontend | `uid=101(nginx)`, maître nginx compris |
| Repli monopage | `GET /documents/42` → `200` |
| `VITE_API_URL` dans le bundle livré | `http://localhost:5000/` |
| CORS | `http://localhost:8080` autorisé ; `:5173` et une origine tierce refusés |

La TODO annonçait une image frontend « ~50 Mo » : c'est **82,9 Mo**, et la valeur a été corrigée.
Le README annonçait « ~83 Mo », qui était juste.

---

## 7 · Limite de cette validation

L'environnement d'intégration qui a servi à cette campagne a deux particularités, à connaître pour
rejouer la validation :

1. **Son trafic sortant est intercepté en TLS.** Les deux images de base ont donc dû être
   complétées avec l'autorité de certification du mandataire pour que `pip` et `npm` acceptent de
   télécharger. **Les `Dockerfile` du dépôt ne sont pas modifiés** : seule l'étiquette locale des
   images de base l'était, le temps de la construction. Sur une machine à sortie directe,
   `docker compose up --build` fonctionne sans cet aménagement.
2. **Aucun Ollama ne tourne sur son hôte.** TS-04 reste donc à jouer sur la machine de
   développement, Ollama démarré — c'est le seul parcours que cette campagne ne couvre pas et qui
   ne demande pas de matériel particulier.
