# Script oral — soutenance HelpMeDraft

Support : `docs/Soutenance-HelpMeDraft.pptx` (34 diapos) · PDF de secours : `docs/Soutenance-HelpMeDraft.pdf`
Durée : **40 min** d'exposé, questions après.

> Mode d'emploi : les notes du .pptx sont rédigées en phrases complètes (à lire si tu bloques).
> Ce fichier-ci est l'inverse : des mots-clés à dire, pas à lire. Apprends les **phrases-clés en gras** mot pour mot, le reste s'improvise autour.

---

## Le plan en une page

| # | Temps | Partie | Diapos | Dossier | Message unique à faire passer |
|---|---|---|---|---|---|
| 1 | 0:00 → 4:10 | Contexte et besoin | 1 → 5 | § 2, § 3 | La confidentialité est **dans** le cahier des charges, pas en option |
| 2 | 4:10 → 8:35 | Gestion de projet | 6 → 8 | § 4 | Lots verticaux + 3 arbitrages + 1 erreur assumée |
| 3 | 8:35 → 20:30 | Conception | 9 → 19 | § 5 | Le navigateur ne parle **jamais** au modèle |
| 4 | 20:30 → 27:55 | Réalisation | 20 → 26 | § 6, § 7 | Du code, 3 décisions par extrait |
| 5 | 27:55 → 32:20 | Sécurité | 27 → 29 | § 8 | La sécurité est une contrainte de **structure** |
| 6 | 32:20 → 40:00 | Tests, veille, clôture | 30 → 34 | § 9-11 | Je vérifie, je me tiens à jour, et je réponds à la commande |

**La clôture** : les quatre objectifs du cahier des charges, repris dans les termes de l'ouverture, et les six mesures de sécurité qui les tiennent. **Tu réponds à la commande, tu ne récites pas un bilan.**

**Les 4 points restants** (les dire avant qu'on te les demande) : déploiement effectif · bascule MySQL complète · 3 compléments AI Act · journalisation applicative.

---

## 1. Ouverture — 0:00 → 1:00

### Diapo 1 · HelpMeDraft `[0:00 — 0:30]`
- Bonjour. Ophélie Bellissens, candidate au titre CDA.
- HelpMeDraft : rédaction assistée par IA.
- **Conçue et développée seule, du cahier des charges au déploiement.**
- Commanditaire fictif : LexiCorp.
- La présentation suit le fil du dossier.
- 40 minutes. Questions à la fin.

### Diapo 2 · Déroulé `[0:30 — 1:00]`
- Six temps.
- Je commence par le besoin — **toutes les décisions techniques en découlent**.
- Puis : projet, conception, réalisation avec du code, sécurité, tests/veille/bilan.
- Les numéros renvoient aux sections du dossier.

---

## 2. Contexte et besoin — 1:00 → 4:10

### Diapo 3 · Section `[1:00 — 1:10]`
> « Premier temps : d'où vient la demande. »

### Diapo 4 · Aider à écrire, pas seulement à classer `[1:10 — 2:40]`
- LexiCorp : outils de gestion documentaire pour PME.
- **Son catalogue sait classer et retrouver. Il ne sait pas aider à écrire.**
- Le constat : courriels, notes, comptes rendus — rédigés par des gens dont ce n'est pas le métier.
- Temps réel, qualité inégale, reprises multiples.
- La commande : une appli web qui assiste la rédaction, espace personnel sécurisé.
- Pour LexiCorp : déplacement de positionnement — de l'organisation à la production.
- Quatre objectifs. **Retenez le quatrième : sécurité, accessibilité, confidentialité sont dans les objectifs, pas en fin de projet.**
- Mon rôle : seule sur toute la chaîne → deux conséquences : architecture lisible, documentation au fil de l'eau.

### Diapo 5 · Périmètre et exigences `[2:40 — 4:10]`
- Cinq blocs fonctionnels.
- **Trois commandes IA, et trois seulement** : reformuler, corriger, compléter.
- Sélection ou document entier. **C'est toujours l'utilisateur qui insère.**
- Quota 20/24 h : vient du cahier des charges, implémenté côté serveur — j'y reviens.
- À droite, le non fonctionnel. La ligne qui a tout pesé : *« aucune donnée personnelle transmise à OpenAI sans anonymisation ».*
- **Sur des textes libres, l'anonymisation n'est jamais exhaustive.** → point de départ de l'inférence locale.
- En bas : le hors périmètre. **Un périmètre qu'on ne borne pas est un périmètre qui dérive.**
- Important pour la suite : AI Act applicable **2 août 2026**, après le cahier des charges. C'est ma veille qui l'a remonté.

---

## 3. Gestion de projet — 4:10 → 8:35

### Diapo 6 · Section `[4:10 — 4:20]`
> « Deuxième temps : comment j'ai conduit le projet. »

### Diapo 7 · Des lots verticaux `[4:20 — 6:20]`
- Itérations d'une semaine, chacune close par un lot utilisable de bout en bout.
- Le point de méthode : **lots verticaux — front + API + base — plutôt que couches horizontales.**
- Horizontal : on ne valide rien avant l'assemblage. Vertical : chaque fin d'itération est démontrable.
- Planning repris du cahier des charges. Six étapes engagées, **13 lots terminés**.
- **La pile conteneurisée a été exécutée pour de vrai** : campagne complète sur un démon Docker réel le 5 octobre, MySQL 8.4 comprise, puis relancée sur mon poste.
- Restent **deux compléments, écrits dans le dossier** : la mention AI Act, et la journalisation applicative à étoffer.
- Versions : une branche par fonctionnalité, commits conventionnés, `.env` ignoré.
- `package-lock.json` commité : **pas un détail d'organisation, une mesure de sécurité** — la compromission d'axios le montrera.
- Seule → point hebdo avec mon référent + revues croisées avec la promo sur l'authentification.

### Diapo 8 · Trois arbitrages `[6:20 — 8:35]`
- **1 — Un JWT seul ne se révoque pas.** → table `user_session` + rotation des refresh tokens. Un jeton déjà consommé qui revient = vol → toutes les sessions révoquées.
- **2 — Le quota par agrégation**, pas par compteur. Un compteur se désynchronise, une agrégation non. Bonus : historique auditable (RGPD).
- **3 — La confidentialité.** Plutôt qu'anonymiser du texte libre → modèle en local, Ollama. **L'exigence est satisfaite par construction.**
  - Contreparties assumées : latence, qualité < GPT-4, prérequis d'installation, un service de plus à maintenir.
  - Ma veille l'a confirmé : CVE critique sur Ollama en avril.
- **Le fil commun** : les trois tiennent une exigence du cahier des charges **par la structure du code**, pas par une vérification ajoutée après coup.

## 4. Conception — 8:35 → 20:30

### Diapo 9 · Section `[8:35 — 8:45]`
> « Troisième temps, le plus long : la conception. »

### Diapo 10 · La pile technique `[8:45 — 9:40]`
- La pile domaine par domaine, **mise en regard de l'environnement recommandé au § 4 du cahier des charges**.
- **Sur sept domaines, six sont conformes** : Python/Flask, JWT, GitHub Actions, Docker — aucune raison de m'en écarter.
- **Deux lignes sont des choix dans une alternative ouverte** par le cahier des charges lui-même : « MySQL ou MongoDB », « OpenAI ou un modèle local ». **Choisir dans une alternative, ce n'est pas s'écarter.**
- **Un seul véritable écart : le front.** React recommandé, Vue 3 retenu. Je l'argumente juste après.
- **Deux ajouts** hors cahier des charges : CodeMirror 6 (un éditeur Markdown ne s'écrit pas à la main dans un `textarea`) et DOMPurify (la prévisualisation rend du HTML issu du texte utilisateur — c'est **le seul `v-html` du projet**, et il est assaini).
- SQLite : **pas un second SGBD**, le même code SQLAlchemy sur un moteur de développement. Les tests tournent dessus en mémoire, en quelques secondes, sans serveur.

### Diapo 11 · Trois choix de technologie `[9:40 — 10:50]`
- **1 — Vue 3 plutôt que React.** Le seul écart. **Il recommande, il n'impose pas.**
  - Même modèle de composants avec la Composition API ; ma maîtrise y était meilleure — **seule sur un projet, la maîtrise est ce qui réduit le risque**.
  - Intégration directe de CodeMirror 6. Le découpage vues / services / store **reste transposable à React** : le choix n'enferme personne.
- **2 — Ollama plutôt qu'OpenAI.** Les deux sont autorisés : **c'est le RGPD qui tranche.**
  - « Aucune donnée transmise sans anonymisation » est **intenable sur du texte libre**.
  - En local, les contenus ne sortent pas : **satisfait par construction, pas par une clause de contrat**.
  - Contreparties assumées. `ia_service` isole l'appel : **basculer vers un fournisseur distant ne toucherait pas les routes**.
- **3 — MySQL plutôt que MongoDB**, et c'est la question CP 8 (« composants SQL **et NoSQL** »).
  - Schéma stable, données fortement reliées, volume modeste.
  - **`ON DELETE CASCADE` met en œuvre le droit à l'effacement en une instruction.** En base documentaire, ce serait du code à écrire, tester et maintenir — **pour une obligation légale**.
  - **Je n'ai pas ajouté de NoSQL, et ce n'est pas par difficulté : ce serait facile, et c'est ce qui rend l'ajout suspect.** Un composant qui ne sert qu'à remplir une grille est une dette déguisée en compétence.
  - **Je l'assume, et le jury est libre de considérer le critère comme non couvert.** L'argumentaire est un livrable à part : `docs/argumentaire-nosql.md`.

### Diapo 12 · Le navigateur ne parle jamais au moteur `[10:50 — 12:40]`
- Client/serveur découplé, trois niveaux, service d'inférence en périphérie.
- **Le navigateur ne dialogue jamais directement avec le moteur.** Tout passe par l'API : authentification → propriété → quota → journalisation.
- Si le front appelait Ollama : **un utilisateur contournerait le quota en appelant le port 11434 lui-même.**
- **L'intermédiaire n'est pas une commodité : il rend les contraintes opposables.**
- Le moteur n'écoute que sur l'interface de bouclage. Habitude implicite → consigne écrite après la CVE Ollama.

### Diapo 13 · Aucun import Flask dans services/ `[12:40 — 14:20]`
- Trois couches. **La règle qui compte est la colonne de droite : ce que chaque couche ne contient jamais.**
- **Aucun import Flask dans `services/`.** Pas esthétique — fonctionnel.
- C'est elle qui rend le métier testable **sans démarrer de serveur ni ouvrir de base**.
- Sans elle, tout test d'`auth_service` ou `ia_service` devient un test d'intégration : plus lent, plus fragile. **C'est le socle du plan de tests.**
- Honnêteté : la lecture de la configuration passe par `current_app`, objet Flask. **Seul point où la règle fléchit** — expliqué § 7.2.
- Cinq blueprints : auth, documents, dossiers, IA, admin.
- Front, même logique : **aucune vue n'appelle axios.** Donc l'intercepteur qui rejoue après un 401 est écrit une seule fois.

### Diapo 14 · L'éditeur de document `[14:20 — 15:25]`
- Le maquettage a produit **neuf planches**, une par écran. Trois temps : recensement → charte et composants → planches.
- Chaque planche porte sa route, sa garde de routeur, et une colonne « intentions » numérotée.
- **Je montre l'écran livré plutôt que la planche — c'est lui qui prouve que l'intention a été tenue.**
- Trois choses à relever : la barre d'outils Markdown ; les **trois modes d'affichage** (écrire, partagé, lire) ; la mention « enregistré automatiquement » sous le titre.
- Le maquettage a servi à deux choses : vérifier la couverture du périmètre, et fixer les intentions **avant d'écrire une ligne de Vue**.
- Planches en annexe § 12.1, captures en § 12.2.

### Diapo 15 · Trois zones, trois gardes `[15:25 — 16:20]`
- **Seize routes**, déclarées dans `frontend/src/index.ts`. Un seul `beforeEach` pour les trois gardes.
- Bande 1 — **Public, aucune garde** : accueil, vitrine, pages légales.
- Bande 2 — **Public mais visiteur seul**, garde `guestOnly` : connexion, inscription, mot de passe oublié. **Déjà connecté → renvoyé au tableau de bord** — sinon on pourrait rouvrir le formulaire de connexion en étant connecté.
- Bande 3 — **Espace personnel**, garde `requiresAuth` : sans jeton → retour à `/login`.
- Bande 4 — **Back-office**, les deux gardes cumulées. **Le rôle est relu dans le store, qui le tient de l'API — pas du jeton.**
- **Je le précise tout de suite parce que c'est la question qu'on pose : ces gardes sont du confort d'usage.**
- Elles évitent un écran vide et masquent le menu d'admin.
- **Le contrôle qui compte est côté serveur** — partie sécurité.

### Diapo 16 · Huit entités, UUID, cascades SGBD `[16:20 — 17:20]`
- Le modèle conceptuel. **Huit entités**, les cardinalités sur les associations.
- Trois choix à défendre.
- **UUID v4, pas d'auto-incrément** → les identifiants ne sont pas énumérables. On ne balaie pas `/documents/1`, `/documents/2`.
- **Cascades déclarées au niveau du SGBD**, pas seulement dans l'ORM. Suppression via un client SQL → l'intégrité tient. **Une contrainte qui n'existe que dans le code applicatif n'est pas une contrainte.**
- **La table `ia` journalise avant/après.** Elle sert trois choses : historique affiché, calcul du quota, traçabilité RGPD. **La même donnée rend les trois possibles.**
- Si on te pointe « Contient » : **0,1 côté document** — un document peut n'appartenir à aucun dossier. C'est ce que le `ON DELETE SET NULL` produit.

### Diapo 17 · Les associations deviennent des clés étrangères `[17:20 — 18:15]`
- Le modèle logique : le même modèle, **associations résolues en clés étrangères** (en bleu).
- **Toutes les clés étrangères convergent vers `user`** — c'est le cloisonnement par compte, écrit dans le schéma.
- Sessions, documents, dossiers, appels IA, consentements, réinitialisations : **chaque ligne appartient à quelqu'un, et c'est la base qui le sait**, pas seulement le code.
- `ia` porte **deux** clés : `id_document` et `user_id`. Le document aurait suffi pour remonter au propriétaire, mais **le quota s'agrège sur l'utilisateur** : redondance assumée, elle évite une jointure à chaque appel. L'index `(user_id, created_at)` est là pour ça.
- MPD en § 5.4, script MySQL § 5.5 — **exécuté et vérifié sur un serveur réel**.

### Diapo 18 · Trois acteurs `[18:15 — 19:00]`
- Visiteur, utilisateur authentifié, administrateur.
- Utilisateur : strictement ses documents, ses dossiers, ses 3 actions IA dans son quota, son historique.
- Admin : hérite de tout le périmètre utilisateur + back-office.
- Le moteur apparaît comme **système externe sollicité par l'API, jamais par le navigateur** — cohérence avec l'architecture.
- Cas le plus significatif : **la génération d'une assistance IA** → diagramme de séquence + jeu d'essai.

### Diapo 19 · Cinq contrôles avant le modèle `[19:00 — 20:30]`
- Séquence du cas le plus significatif.
- **Suivez l'ordre des contrôles, il n'est pas arbitraire** : authentification → propriété → validation des entrées → quota → **et seulement ensuite l'appel au modèle**.
- **Chaque contrôle est placé avant celui qui coûte plus cher.**
- Vérifier le quota après l'inférence = consommer le moteur sans être compté.
- Journalisation après la réponse, avec avant/après.
- Cas d'erreur traité : Ollama muet → `ia_service` traduit l'exception réseau en message lisible, **et aucune ligne n'est écrite** — sinon un échec consommerait du quota.
- **La décision finale reste à l'utilisateur.** Ergonomie **et** sécurité : ne jamais appliquer automatiquement la sortie d'un modèle.

---

## 5. Réalisation — 20:30 → 27:55

### Diapo 20 · Section `[20:30 — 20:40]`
> « Quatrième temps : la réalisation, avec les écrans et le code. »

### Diapo 21 · Onze écrans, douze captures `[20:40 — 21:30]`
- Avant le code, **la série complète des écrans livrés**. Onze écrans, douze captures.
- L'accueil figure deux fois : **version large et version mobile** — l'adaptation aux petits écrans est une exigence du cahier des charges.
- **Ligne 1** : zone publique et pages réservées au visiteur — accueil, mobile, connexion, inscription, mot de passe oublié, réinitialisation.
- **Ligne 2** : espace authentifié puis back-office — tableau de bord, mes documents, nouveau document, éditeur, assistant IA, administration.
- **C'est le découpage que je vous ai montré sur les gardes du routeur.**
- Les douze sont en annexe § 12.2, **chacune accompagnée du code qui la produit**.
- « Je m'arrête maintenant sur trois d'entre elles, et sur leur code. »

### Diapo 22 · Le tableau de bord `[21:30 — 22:25]`
- Tableau de bord. **Capture réelle de l'application en fonctionnement.**
- Trois compteurs, puis trois portes d'entrée vers la rédaction.
- Constat d'usage : **devant un éditeur vide, l'utilisateur sans structure en tête abandonne.** Un modèle ou un document existant supprime la page blanche.
- Deux points techniques : les compteurs viennent de l'API, pas d'un calcul client. La recherche filtre la page courante côté client **parce que la pagination est serveur** — la liste n'est jamais chargée entièrement.
- Huit captures en annexe § 12.2, avec le code.

### Diapo 23 · Enregistrer 2,5 s après la frappe `[22:25 — 24:00]`
- L'éditeur, écran central. Je m'arrête sur l'enregistrement automatique : **quatre décisions en quelques lignes**.
- 2,5 s n'est pas arbitraire : à chaque caractère → API saturée, écritures multipliées. Trop long → sauvegarde invisible, travail perdu.
- **Le minuteur précédent est systématiquement annulé** — sinon une frappe rapide empile les requêtes.
- Doublé d'un bouton explicite : l'utilisateur doit pouvoir forcer.
- Rien n'est enregistré tant que le titre est vide.
- Remarque de méthode, écrite dans le dossier : sur la capture C-07 l'indicateur n'apparaît pas, **parce qu'aucune frappe n'a eu lieu**.
- **Une capture atteste d'un état, pas d'un comportement.** Vérifier une fonctionnalité demande de lire le code ou d'exécuter un scénario. → **C'est la raison d'être du jeu d'essai.**

### Diapo 24 · Compter les appels, jamais les stocker `[24:00 — 25:50]`
- Composant métier : le quota IA. **Dix lignes, trois décisions.**
- **1 — C'est une agrégation** sur le journal des 24 dernières heures, pas un compteur sur l'utilisateur. Un compteur se désynchronise — il suffit d'un échec entre l'appel et l'incrément. **Une agrégation est juste par construction.**
- **2 — Fenêtre glissante, pas compteur journalier.** Le cahier des charges dit « 20 requêtes par 24 heures », pas « par jour calendaire ». Remise à zéro à minuit → **40 appels entre 23 h et 1 h**.
- **3 — Le code de retour est 429, pas 403.** 403 = « vous n'avez pas le droit ». 429 = « réessayez plus tard ». **Pas la même information pour le client.**
- Contrôle entièrement serveur. Le front affiche le quota restant — **c'est de l'affichage**.
- Test JE-07. **Mes données contiennent une ligne datée de 25 heures précisément pour vérifier la fenêtre glissante.**

### Diapo 25 · La propriété est dans le WHERE `[25:50 — 26:45]`
- Accès aux données. **Le motif le plus répété du projet.**
- **La propriété est dans la clause WHERE.** Je ne charge pas le document pour comparer ensuite son propriétaire : je demande un document qui a cet identifiant **ET** qui appartient à l'utilisateur courant.
- **Pas stylistique** : avec un contrôle a posteriori, un `if` oublié dans une route ouvre une faille. Ici, oublier la condition **fait échouer le test de propriété**, qui existe pour chaque ressource.
- Conséquence voulue : **404, pas 403.** Un 403 confirmerait que la ressource existe. Le 404 est indiscernable d'un identifiant inexistant.
- Tout passe par l'ORM, paramétré, **aucune concaténation de chaîne** — objectif de qualité tenu sans exception.

### Diapo 26 · Conteneurisée, intégrée, exécutée `[26:45 — 27:55]`
- Conteneurisée, intégrée en continu depuis le 4 octobre, **et la pile a été exécutée**.
- **Pas seulement décrite — jouée** : le 5 octobre sur un démon Docker réel, et de nouveau depuis sur mon poste.
- Trois services :
  - MySQL 8.4, volume persistant, **sonde de santé** — sans elle le backend démarre avant que la base accepte les connexions.
  - Backend sous **Gunicorn**, pas le serveur de dev de Flask, utilisateur non privilégié.
  - Frontend : build Vite en deux étapes, servi par Nginx → **82,9 Mo mesurés**, parce que l'image ne contient que du statique, pas la chaîne de construction.
- Détail qui compte : secrets en `${VAR:?message}` → **la composition échoue si la variable manque, au lieu de démarrer avec une valeur inventée**.
- Ollama hors composition, sur l'hôte, via `host.docker.internal`.
- CI à chaque push et chaque PR, **trois travaux parallèles**. **Enchaînés, un échec du frontend masquait l'état du backend** — il fallait deux exécutions.
- Troisième carte, la liste de contrôle d'une mise en ligne : ce sont **des valeurs de configuration, pas des développements**.
- **L'application est prête à être hébergée le jour où on lui donne un domaine.**

### Diapo 27 · Section `[27:55 — 28:05]`
> « Cinquième temps : la sécurité. **C'est le fil rouge du projet, pas un chapitre.** »

### Diapo 28 · La sécurité comme contrainte de conception `[28:05 — 30:05]`
- Grille : **OWASP Top 10 2021**, croisée avec le cahier des charges et l'ANSSI. Le dossier traite les dix ; j'en montre six.
- Point de méthode : **pas traitée en fin de projet — et pas par vertu, par nécessité pratique.**
- Filtrage par propriétaire dans le WHERE, stockage d'empreintes, refus de démarrer sans clé : **des choix de structure. Les ajouter après aurait demandé de réécrire les couches.**
- **A01** : la propriété est dans le WHERE, **et le rôle est relu en base, pas lu dans le jeton**.
- **A02** : bcrypt + sel pour les mots de passe, SHA-256 pour les jetons. **Aucun secret en clair en base** → une fuite ne permet pas de rejouer une session.
- **A05** : l'application **refuse de démarrer sans `JWT_SECRET_KEY`**. Pas de défaut, pas de repli silencieux. **Une clé de secours en dur est une clé en production.**
- **A10** : la seule URL sortante est `OLLAMA_URL`, une valeur de configuration. **Aucune entrée utilisateur ne devient une destination HTTP.**
- Transparence, c'est dans le dossier : **A09, la journalisation applicative est incomplète.** Le journal IA existe, mais pas de journalisation systématique des événements de sécurité.

### Diapo 29 · Deux jetons `[30:05 — 32:20]`
- Cycle de vie des sessions : **la partie qui m'a demandé le plus de réflexion**.
- Deux besoins contradictoires : court = sûr mais pénible ; long = confortable mais dangereux.
- **La combinaison donne les deux propriétés** : access token 15 min, non révocable mais fenêtre courte ; refresh token 7 jours, révocable côté serveur.
- Refresh : cookie **httpOnly, SameSite Strict, chemin `/auth`**. Inaccessible au JavaScript → **même une faille XSS ne permet pas de le lire**.
- **Je ne stocke pas le jeton, je stocke son empreinte SHA-256.**
- Le cœur du mécanisme (code à droite) : à chaque usage, le jeton présenté est marqué consommé, un nouveau est émis.
- Un jeton consommé qui se représente → deux explications : vieille requête rejouée, ou vol. **Dans le doute, je révoque toutes les sessions du compte.**
- **Volontairement brutal : la gêne est une reconnexion, le risque évité est un compte compromis.**
- Le point qu'on oublie : **à la réinitialisation du mot de passe, toutes les sessions sont supprimées.** Changer son mot de passe ne sert à rien si les sessions de l'attaquant survivent.
- Purge : `purge_expired_sessions` filtre sur **l'expiration**, pas sur le drapeau de révocation. Une session révoquée doit survivre jusqu'au terme de son jeton — **sinon la détection de rejeu tombe**.

---

## 7. Tests, veille et bilan — 32:20 → 40:00

### Diapo 30 · Section `[32:20 — 32:30]`
> « Dernier temps : comment je vérifie, comment je me tiens à jour, et ce que je retiens. »

### Diapo 31 · 461 cas au vert `[32:30 — 34:30]`
- Quatre niveaux, **du moins coûteux au plus coûteux** → ce classement détermine ce qui tourne à chaque push et ce qui reste manuel.
- Campagne rejouée le 4 novembre : **461 cas automatisés, tous au vert — 403 backend, 58 frontend.**
- **95 % de couverture backend**, 100 % sur `auth_service` et `email_service`, 93 à 97 % sur les routes.
- Si on te demande comment c'est calculé : **hors `jeu_essai.py`**, qui est un script de peuplement, pas du code applicatif. En l'incluant, on tombe à 90 % — dis-le toi-même, c'est plus solide.
- Objectif fixé : 80 % sur `services/` et les routes, **sans objectif chiffré ailleurs. Viser un pourcentage global pousse à écrire des tests faciles sur du code sans risque.**
- Les **55 %** du front : tirés vers le bas par six modules qui sont des enveloppes d'une ligne autour d'axios — **les tester reviendrait à tester axios**.
- Trois zones concentrent l'effort : authentification, propriété, quota. **Les trois endroits où une régression coûte cher.**
- Le quatrième niveau, **les tests système, joué le 5 octobre sur la pile conteneurisée : 7 au vert sur 10.** Un échec réel sur la réinitialisation (TS-02), deux cas hors de portée dont celui qui demande un Ollama joignable.
- Restent les **tests de charge**.

### Diapo 32 · La ligne datée de 25 heures `[34:30 — 36:30]`
- Jeu d'essai : la génération d'une assistance IA. **Trois raisons :**
  1. il traverse les trois couches et sollicite un système externe ;
  2. il concentre cinq contrôles de nature différente ;
  3. il porte les deux exigences les plus délicates : **quota et traçabilité**.
- **Et c'est la seule fonctionnalité qu'aucune capture ne peut attester** — elle se manifeste par un enchaînement, pas par un état.
- Données construites par script, **reproductibles à l'identique**. Quatre comptes : l'utilisatrice principale, un tiers pour les accès croisés, un admin, **un compte au quota abaissé à 1** pour atteindre la limite en un appel.
- La donnée la plus utile : dans le journal de U1, **19 lignes de moins de 24 h, et une ligne de 25 heures**.
- **Cette ligne unique est le seul moyen de distinguer une fenêtre glissante d'un compteur journalier.** Sans elle, JE-07 passerait quelle que soit l'implémentation.
- **Ce que j'ai appris : un jeu de données, ce n'est pas remplir des tables — c'est choisir les valeurs qui font échouer les mauvaises implémentations.**

### Diapo 33 · La veille technologique `[36:30 — 38:30]`
- Trois périmètres : dépendances, sécurité applicative, réglementaire.
- Principe : **surveiller ce que le projet utilise réellement. Une alerte sur une bibliothèque absente du projet n'est pas une information.**
- Huit entrées sur six mois, **trois ont appelé une action** — c'est la mesure de l'utilité de l'exercice.
- Le constat du titre : **la sévérité publiée ne prédit pas l'impact réel.**
  - La plus sévère — **9,1 sur Ollama** — atténuée par ma configuration : écoute sur localhost seulement.
  - La plus modérée — **5,1 sur DOMPurify** — affectait directement ma version.
- DOMPurify, l'entrée la plus instructive : **c'est la bibliothèque que j'avais ajoutée pour corriger une faille XSS.**
- **Principe : une mesure de sécurité est un composant comme un autre, avec sa propre surface d'attaque.** Ajouter une bibliothèque d'assainissement ne clôt pas le sujet XSS, **ça le déplace vers la maintenance de cette bibliothèque**.
- D'où la défense en profondeur : **je stocke du Markdown brut, pas du HTML.** Si DOMPurify échoue, la donnée stockée n'est toujours pas exécutable.
- Ollama éclaire mon architecture : **héberger soi-même, c'est aussi maintenir soi-même.** La décision reste la bonne au regard du RGPD, **mais elle se paie en maintenance — et le dire est plus honnête que de la présenter comme un choix sans contrepartie**.
- L'AI Act justifie la veille comme livrable : le cahier des charges, rédigé avant l'entrée en application, ne mentionne que le RGPD. **Sans ce suivi, j'aurais livré une application non conforme à une obligation entrée en vigueur trois semaines avant la fin du développement.**

### Diapo 34 · Ce qui était demandé, ce qui le tient `[38:30 — 40:00]`
- « Pour conclure, **je reprends les quatre objectifs du cahier des charges, dans les termes mêmes de l'ouverture**, et je dis pour chacun ce qui le tient. »
- **Rédiger et stocker** → éditeur Markdown, CRUD, dossiers, enregistrement automatique à 2,5 s.
- **Suggérer et reformuler** → trois commandes, quota 20 / 24 h par agrégation, chaque interaction journalisée avec l'avant et l'après.
- **Un espace sécurisé** → deux jetons, sessions révocables, cloisonnement par compte dans la clause `WHERE`.
- **Se conformer** → RGPD par l'architecture (les contenus ne sortent pas), RGAA vérifié sur 15 écrans, 0 violation axe-core, AI Act tracé en base.
- « À droite, **les six mesures qui tiennent tout cela**. Je les reprends vite, chacune a déjà été montrée. »
  1. La propriété est dans le `WHERE` — **404, jamais 403** : un 403 confirmerait que la ressource existe.
  2. **Le rôle est relu en base** à chaque requête, jamais lu dans le jeton.
  3. **bcrypt salé** pour les mots de passe, **empreinte SHA-256** pour les jetons — une fuite de la base ne rejoue pas une session.
  4. **Refus de démarrer sans `JWT_SECRET_KEY`** : pas de clé de secours en dur.
  5. Refresh dans un cookie **httpOnly** ; **rejouer un jeton consommé révoque tout le compte**.
  6. **Markdown brut stocké, jamais de HTML** : si DOMPurify échoue, la donnée n'est toujours pas exécutable.
- **Si on te demande ce qui manque** : la journalisation des événements de sécurité est incomplète — **A09 de l'OWASP**, et c'est écrit dans le dossier. Dis-le toi-même si la question vient.
- Je vous remercie, je suis à votre disposition pour vos questions.

## Antisèche — à relire 5 minutes avant

**Chiffres**
`461` tests au vert (403 back + 58 front) · `95 %` couverture backend (90 % brut, `jeu_essai.py` inclus) · `55 %` front · `8` tables · `5` blueprints · `9` planches · `20` requêtes / `24 h` · `429` · `404` pas 403 · `15 min` access · `7 jours` refresh · `2,5 s` autosave · `82,9 Mo` image front · `8` entrées de veille, `3` actions · CVE `9,1` Ollama / `5,1` DOMPurify · AI Act `2 août 2026` · `13` lots

**Si tu perds le fil** → reviens à la question « pourquoi ce choix ? ». Chaque diapo a une raison, pas une liste.

**Si tu es en retard** → coupe dans les diapos 14, 15, 18 et 22 (descriptives). La 21, la planche des écrans, se survole en 20 s. Ne coupe jamais 8, 11, 12, 23, 24, 29, 34.

**Les quatre « je ne le cache pas »** — à sortir toi-même, jamais à laisser venir :
1. Pas encore mise en ligne : la pile tourne en conteneurs, il manque un domaine et des valeurs de configuration.
2. A09 journalisation incomplète.
3. `current_app` dans `services/` : seul point où la règle fléchit.
4. La couverture backend est de 95 % hors `jeu_essai.py` ; 90 % en l'incluant.

**Posture** → une respiration à chaque diapo de section. Les trois phrases finales : lentement, en regardant le jury.
