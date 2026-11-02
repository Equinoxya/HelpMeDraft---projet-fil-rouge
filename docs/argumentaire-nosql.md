# Argumentaire — pourquoi aucun composant NoSQL dans HelpMeDraft

> **CP 8** : « développer des composants d'accès aux données SQL et NoSQL ».
>
> Ce document est l'argumentaire demandé pour un critère que le projet **ne couvre pas par un
> composant**. Il expose la décision, son raisonnement, et ce qu'il faudrait faire pour la changer.
> Il ne prétend pas que le critère est satisfait.

| | |
|---|---|
| **Date** | 4 octobre 2026 |
| **Décision** | aucun composant NoSQL ajouté |
| **Qui décide** | la propriétaire du projet, après étude des trois usages candidats ci-dessous |
| **Réexamen** | au déploiement, ou si l'un des seuils du §4 est franchi |

---

## 1 · La décision, et ce qu'elle coûte

**Aucun composant NoSQL n'est ajouté à HelpMeDraft.** Le volet « NoSQL » du CP 8 n'est donc pas
couvert par du code.

Ce choix est assumé, pas subi. Son coût est connu : le jury peut considérer le critère comme non
satisfait, et c'est son droit. Le raisonnement qui suit est ce qui est opposé à cette lecture.

L'argument principal n'est pas qu'il serait difficile d'ajouter du NoSQL. C'est l'inverse : il
serait **facile**, et c'est précisément ce qui rend l'ajout suspect. Brancher un Redis et y écrire
trois clés produirait une ligne de plus dans le `docker-compose.yml`, un service à exploiter, et
aucune réponse à un besoin réel. Un composant dont la seule justification est de figurer dans une
grille d'évaluation est une dette technique déguisée en compétence.

---

## 2 · Pourquoi le besoin est relationnel

Les sept entités du modèle — `user`, `dossier`, `document`, `ia`, `consentement`, `user_session`,
`password_reset` — ont trois propriétés qui désignent un SGBD relationnel, et aucune qui plaide
pour autre chose.

| Propriété des données | Conséquence |
|---|---|
| **Schéma stable et connu** : 7 entités, pas de champ libre, pas de structure variable d'une ligne à l'autre | la souplesse de schéma du document est sans objet — et son revers, l'absence de contrainte, serait une perte |
| **Fortement reliées** : tout part de `user`, et les 8 clés étrangères portent des règles de suppression qui mettent en œuvre le droit à l'effacement du RGPD | un `ON DELETE CASCADE` depuis `user` efface en une instruction toutes les données d'une personne. En base documentaire, ce serait du code applicatif à écrire, à tester et à maintenir — pour une obligation légale |
| **Volume modeste** : quelques milliers de lignes par utilisateur | le partitionnement horizontal, qui est la raison d'être des bases NoSQL distribuées, ne répond à aucun problème ici |

Les contraintes `CHECK`, l'unicité de l'adresse et les règles `ON DELETE` sont des **règles
métier appliquées par le SGBD**. Déplacer une partie des données vers un magasin sans contrainte
reviendrait à les redescendre dans le code applicatif, où elles seraient appliquées par du code
qu'il faut écrire et tester, au lieu d'être garanties.

---

## 3 · Les trois usages candidats, et pourquoi chacun est écarté

Trois pistes ont été étudiées. Elles sont présentées avec ce qu'elles auraient apporté, parce
qu'aucune n'est absurde — et c'est leur coût d'exploitation qui tranche.

### 3.1 Redis pour mettre en cache les réponses de l'IA

**L'idée.** Une inférence coûte jusqu'à 50 secondes sur processeur seul. Mettre en cache le
couple (action, contenu) → résultat éviterait de régénérer deux fois la même chose.

**Pourquoi c'est écarté — le taux de réussite serait proche de zéro.** La clé du cache serait
l'empreinte du texte soumis. Or l'usage de l'application est la réécriture d'un texte que
l'utilisateur vient de taper, et qu'il modifie entre deux appels : deux soumissions identiques au
caractère près sont un cas marginal. Un cache dont on n'attend presque aucun succès n'est pas une
optimisation, c'est un service de plus à exploiter.

**Ce qui répondait vraiment au problème a déjà été fait**, et par un réglage et non par un
composant : `OLLAMA_KEEP_ALIVE=30m` garde le modèle en mémoire entre deux appels. Le gain mesuré
est sans comparaison avec ce qu'un cache aurait donné.

| | chargement | génération |
|---|---|---|
| modèle déchargé (défaut Ollama : 5 min) | 20,5 s | 0,2 s |
| modèle maintenu (`OLLAMA_KEEP_ALIVE=30m`) | — | 0,2 s |

C'était le chargement qui dominait le temps de réponse, pas la génération. Le cache aurait traité
le petit terme en laissant le grand.

> **Confidentialité, accessoirement.** Mettre en cache les réponses de l'IA, c'est dupliquer hors
> de la base des extraits de documents — qui peuvent être des contrats ou des courriers RH — dans
> un magasin sans chiffrement au repos et sans règle de purge. Le chiffrement au repos est déjà un
> point ouvert de l'[audit de sécurité](./audit-securite.md) ; en ajouter une copie n'irait pas
> dans le bon sens.

### 3.2 MongoDB pour journaliser les appels à l'IA

**L'idée.** Stocker l'historique des interactions IA en documents : `type_action`,
`content_before`, `content_after`, `tokens_used`.

**Pourquoi c'est écarté — ce serait un doublon.** La table `ia` fait déjà exactement cela, avec
deux propriétés qu'une collection documentaire perdrait :

- `ON DELETE CASCADE` depuis `user` et depuis `document` : l'effacement d'un compte emporte son
  historique IA. En Mongo, il faudrait l'écrire, le tester, et ne jamais l'oublier — pour une
  obligation RGPD ;
- `ck_ia_action` garantit que `type_action` est l'une des trois valeurs admises. La même garantie
  côté Mongo serait un contrôle applicatif de plus.

Et le besoin qui justifierait une base documentaire — des structures hétérogènes d'un
enregistrement à l'autre — n'existe pas : les quatre champs sont les mêmes pour les trois actions.

### 3.3 Redis comme stockage de Flask-Limiter

**L'idée, et elle est différente des deux précédentes : celle-là corrige un défaut réel.**
Flask-Limiter compte en mémoire, donc **par *worker***. Avec les 2 *workers* gunicorn configurés,
les seuils de `/auth/login` sont effectivement doublés : 5 tentatives par minute annoncées, 10 en
pratique. Un stockage partagé est la vraie correction, et elle figure déjà dans la
[TODO](../TODO.md).

**Pourquoi ce n'est pas la réponse au CP 8.** Redis servirait ici de compteur partagé entre
processus, c'est-à-dire d'**infrastructure**, pas de magasin de données métier. Le CP 8 demande des
« composants d'accès aux données » : un `INCR` sur une clé de limitation de débit n'est pas un
accès aux données de l'application, et le présenter comme tel serait un habillage.

**Le défaut reste à corriger, mais pour sa propre raison.** Il est inscrit comme tel dans la TODO,
au titre de la sécurité — pas du CP 8. Le confondre avec une couverture du critère affaiblirait les
deux.

---

## 4 · À quelles conditions la décision changerait

Elle n'est pas définitive. Trois seuils la rouvriraient, et ils sont écrits pour être vérifiables
plutôt que rhétoriques.

| Si… | Alors |
|---|---|
| L'application passe à **plus de 2 *workers*** ou à plusieurs instances | Redis devient nécessaire pour la limitation de débit **et** pour les sessions. L'argument « infrastructure » du §3.3 tient toujours, mais le composant devient inévitable |
| L'IA passe à un **modèle distant facturé au jeton** | le cache du §3.1 change de nature : il n'économise plus de l'attente mais de l'argent, et un taux de réussite faible devient acceptable |
| Un **journal d'audit** est exigé (RGPD, traçabilité des accès) | des écritures nombreuses, jamais modifiées, à durée de vie bornée : c'est le profil pour lequel une base documentaire ou un stockage par séries temporelles est réellement meilleur qu'une table |

---

## 5 · Ce que la propriétaire du projet peut démontrer sans composant NoSQL

Le CP 8 porte sur l'accès aux données. Le volet SQL est, lui, couvert — et c'est la part sur
laquelle il y a matière à discuter :

| Sujet | Où |
|---|---|
| Requêtes paramétrées, ORM SQLAlchemy, aucune concaténation de SQL | `app/routes/`, et l'[audit de sécurité](./audit-securite.md) |
| Index posés en fonction des requêtes réelles (`ix_ia_user_created` pour le quota glissant, `ix_document_user_updated` pour la liste paginée triée) | [`schema_mysql.sql`](../backend/database/schema_mysql.sql) |
| Contraintes `CHECK` alignées sur la validation applicative, et le travail de les y aligner (KAN-98) | `migration_quota_min.sql` |
| Transactions, et un conflit d'accès réel analysé et chiffré | §7 de l'[exploitation de la base](./exploitation-base-de-donnees.md) |
| Moindre privilège : 3 comptes SGBD, l'applicatif sans aucun droit de structure | [`droits_mysql.sql`](../backend/database/droits_mysql.sql) |
| Deux descriptions du schéma maintenues en parité par 36 tests, après une divergence réelle | `tests/unit/test_schema_parite.py` |

**La position à tenir** : le choix de ne rien ajouter est argumenté par l'étude de trois usages
candidats, chiffrée là où c'était mesurable, et accompagnée des conditions de son réexamen. Le
critère reste formellement non couvert par un composant. Ce qui est démontré, c'est la capacité à
juger de la pertinence d'une technologie plutôt qu'à la convoquer pour remplir une case.
