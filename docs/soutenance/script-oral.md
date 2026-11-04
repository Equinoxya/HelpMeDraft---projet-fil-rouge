# Script oral — soutenance HelpMeDraft

Support : `docs/Soutenance-HelpMeDraft.pptx` (31 diapos) · PDF de secours : `docs/Soutenance-HelpMeDraft.pdf`
Durée : **40 min** d'exposé, questions après.

> Mode d'emploi : les notes du .pptx sont rédigées en phrases complètes (à lire si tu bloques).
> Ce fichier-ci est l'inverse : des mots-clés à dire, pas à lire. Apprends les **phrases-clés en gras** mot pour mot, le reste s'improvise autour.

---

## Le plan en une page

| # | Temps | Partie | Diapos | Dossier | Message unique à faire passer |
|---|---|---|---|---|---|
| 1 | 0:00 → 4:10 | Contexte et besoin | 1 → 5 | § 2, § 3 | La confidentialité est **dans** le cahier des charges, pas en option |
| 2 | 4:10 → 8:35 | Gestion de projet | 6 → 8 | § 4 | Lots verticaux + 3 arbitrages + 1 erreur assumée |
| 3 | 8:35 → 20:30 | Conception | 9 → 17 | § 5 | Le navigateur ne parle **jamais** au modèle |
| 4 | 20:30 → 27:55 | Réalisation | 18 → 23 | § 6, § 7 | Du code, 3 décisions par extrait |
| 5 | 27:55 → 32:20 | Sécurité | 24 → 26 | § 8 | La sécurité est une contrainte de **structure** |
| 6 | 32:20 → 40:00 | Tests, veille, bilan | 27 → 31 | § 9-11 | Je vérifie, je me tiens à jour, j'assume ce qui reste |

**Les 3 phrases de fin** (à savoir par cœur, elles closent l'oral) :
1. Un prompt est du code.
2. Une mesure de sécurité est un composant comme un autre.
3. Un jeu de données, c'est le choix des valeurs qui font échouer les mauvaises implémentations.

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
- Planning repris du cahier des charges. Tout terminé **sauf trois choses, écrites dans le dossier** : déploiement, bascule MySQL (schéma exécuté et vérifié, il manque un démon Docker), mention AI Act.
- Versions : une branche par fonctionnalité, commits conventionnés, `.env` ignoré.
- `package-lock.json` commité : **pas un détail d'organisation, une mesure de sécurité** — la compromission d'axios le montrera.
- Seule → point hebdo avec mon référent + revues croisées avec la promo sur l'authentification.

### Diapo 8 · Trois arbitrages, et une erreur `[6:20 — 8:35]`
- **1 — Un JWT seul ne se révoque pas.** → table `user_session` + rotation des refresh tokens. Un jeton déjà consommé qui revient = vol → toutes les sessions révoquées.
- **2 — Le quota par agrégation**, pas par compteur. Un compteur se désynchronise, une agrégation non. Bonus : historique auditable (RGPD).
- **3 — La confidentialité.** Plutôt qu'anonymiser du texte libre → modèle en local, Ollama. **L'exigence est satisfaite par construction.**
  - Contreparties assumées : latence, qualité < GPT-4, prérequis d'installation, un service de plus à maintenir.
  - Ma veille l'a confirmé : CVE critique sur Ollama en avril.
- **L'erreur, que j'ai gardée dans le dossier** : mes textes avaient dérivé vers un positionnement « juridique » absent du cahier des charges. 20 libellés, 9 fichiers.
  - Le dernier résidu n'était pas dans l'interface : **dans les gabarits de prompt du backend** — « Tu es un assistant de rédaction juridique ».
  - Invisible, mais envoyé au modèle à chaque appel → effet réel sur les sorties.
  - **Règle : un prompt est du code, il se teste comme du code.** Cas TU-04.

---

## 4. Conception — 8:35 → 20:30

### Diapo 9 · Section `[8:35 — 8:45]`
> « Troisième temps, le plus long : la conception. »

### Diapo 10 · Le navigateur ne parle jamais au moteur `[8:45 — 11:00]`
- Client/serveur découplé, trois niveaux, service d'inférence en périphérie.
- **Le navigateur ne dialogue jamais directement avec le moteur.** Tout passe par l'API : authentification → propriété → quota → journalisation.
- Si le front appelait Ollama : **un utilisateur contournerait le quota en appelant le port 11434 lui-même.**
- **L'intermédiaire n'est pas une commodité : il rend les contraintes opposables.**
- Le moteur n'écoute que sur l'interface de bouclage. Habitude implicite → consigne écrite après la CVE Ollama.
- Deux écarts au cahier des charges, argumentés : **Vue 3 plutôt que React** (recommandé, pas imposé ; la maîtrise réduit le risque en solo) et **Ollama plutôt qu'OpenAI** (les deux autorisés ; c'est le RGPD qui tranche).

### Diapo 11 · Aucun import Flask dans services/ `[11:00 — 13:00]`
- Trois couches. **La règle qui compte est la colonne de droite : ce que chaque couche ne contient jamais.**
- **Aucun import Flask dans `services/`.** Pas esthétique — fonctionnel.
- C'est elle qui rend le métier testable **sans démarrer de serveur ni ouvrir de base**.
- Sans elle, tout test d'`auth_service` ou `ia_service` devient un test d'intégration : plus lent, plus fragile. **C'est le socle du plan de tests.**
- Honnêteté : la lecture de la configuration passe par `current_app`, objet Flask. **Seul point où la règle fléchit** — expliqué § 7.2.
- Cinq blueprints : auth, documents, dossiers, IA, admin.
- Front, même logique : **aucune vue n'appelle axios.** Donc l'intercepteur qui rejoue après un 401 est écrit une seule fois.

### Diapo 12 · Neuf planches, une intention par écran `[13:00 — 14:30]`
- Neuf planches, une par écran. Trois temps : recensement → charte et composants → planches.
- Celle-ci : l'éditeur, **l'écran le plus représentatif du produit**.
- Chaque planche porte sa route, sa garde de routeur, et une colonne « intentions » numérotée.
- Intention 4 : enregistrement auto 2,5 s après la dernière frappe + bouton explicite — je montrerai le code.
- Intention 5 : historique IA — action, avant, après, tokens. **Pas un confort : la traçabilité exigée.**
- Le maquettage a servi à deux choses : vérifier la couverture du périmètre, fixer les intentions **avant d'écrire une ligne de Vue**.

### Diapo 13 · Trois zones, trois gardes `[14:30 — 15:30]`
- Trois zones : public, espace authentifié, back-office.
- Trois gardes correspondantes : `guest`, `auth`, `admin`.
- **Je le précise tout de suite parce que c'est la question qu'on pose : ces gardes sont du confort d'usage.**
- Elles évitent un écran vide et masquent le menu d'admin.
- **Le contrôle qui compte est côté serveur** — partie sécurité.

### Diapo 14 · Huit entités, UUID, cascades SGBD `[15:30 — 16:45]`
- Le modèle conceptuel. **Huit entités**, les cardinalités sur les associations.
- Trois choix à défendre.
- **UUID v4, pas d'auto-incrément** → les identifiants ne sont pas énumérables. On ne balaie pas `/documents/1`, `/documents/2`.
- **Cascades déclarées au niveau du SGBD**, pas seulement dans l'ORM. Suppression via un client SQL → l'intégrité tient. **Une contrainte qui n'existe que dans le code applicatif n'est pas une contrainte.**
- **La table `ia` journalise avant/après.** Elle sert trois choses : historique affiché, calcul du quota, traçabilité RGPD. **La même donnée rend les trois possibles.**
- Si on te pointe « Contient » : **0,1 côté document** — un document peut n'appartenir à aucun dossier. C'est ce que le `ON DELETE SET NULL` produit.

### Diapo 15 · Les associations deviennent des clés étrangères `[16:45 — 17:45]`
- Le modèle logique : le même modèle, **associations résolues en clés étrangères** (en bleu).
- **Toutes les clés étrangères convergent vers `user`** — c'est le cloisonnement par compte, écrit dans le schéma.
- Sessions, documents, dossiers, appels IA, consentements, réinitialisations : **chaque ligne appartient à quelqu'un, et c'est la base qui le sait**, pas seulement le code.
- `ia` porte **deux** clés : `id_document` et `user_id`. Le document aurait suffi pour remonter au propriétaire, mais **le quota s'agrège sur l'utilisateur** : redondance assumée, elle évite une jointure à chaque appel. L'index `(user_id, created_at)` est là pour ça.
- MPD en § 5.4, script MySQL § 5.5 — **exécuté et vérifié sur un serveur réel**.

### Diapo 16 · Trois acteurs `[17:45 — 18:45]`
- Visiteur, utilisateur authentifié, administrateur.
- Utilisateur : strictement ses documents, ses dossiers, ses 3 actions IA dans son quota, son historique.
- Admin : hérite de tout le périmètre utilisateur + back-office.
- Le moteur apparaît comme **système externe sollicité par l'API, jamais par le navigateur** — cohérence avec l'architecture.
- Cas le plus significatif : **la génération d'une assistance IA** → diagramme de séquence + jeu d'essai.

### Diapo 17 · Cinq contrôles avant le modèle `[18:45 — 20:30]`
- Séquence du cas le plus significatif.
- **Suivez l'ordre des contrôles, il n'est pas arbitraire** : authentification → propriété → validation des entrées → quota → **et seulement ensuite l'appel au modèle**.
- **Chaque contrôle est placé avant celui qui coûte plus cher.**
- Vérifier le quota après l'inférence = consommer le moteur sans être compté.
- Journalisation après la réponse, avec avant/après.
- Cas d'erreur traité : Ollama muet → `ia_service` traduit l'exception réseau en message lisible, **et aucune ligne n'est écrite** — sinon un échec consommerait du quota.
- **La décision finale reste à l'utilisateur.** Ergonomie **et** sécurité : ne jamais appliquer automatiquement la sortie d'un modèle.

---

## 5. Réalisation — 20:30 → 27:55

### Diapo 18 · Section `[20:30 — 20:40]`
> « Quatrième temps : la réalisation, avec les écrans et le code. »

### Diapo 19 · Supprimer la page blanche `[20:40 — 21:40]`
- Tableau de bord. **Capture réelle de l'application en fonctionnement.**
- Trois compteurs, puis trois portes d'entrée vers la rédaction.
- Constat d'usage : **devant un éditeur vide, l'utilisateur sans structure en tête abandonne.** Un modèle ou un document existant supprime la page blanche.
- Deux points techniques : les compteurs viennent de l'API, pas d'un calcul client. La recherche filtre la page courante côté client **parce que la pagination est serveur** — la liste n'est jamais chargée entièrement.
- Huit captures en annexe § 12.2, avec le code.

### Diapo 20 · Enregistrer 2,5 s après la frappe `[21:40 — 23:25]`
- L'éditeur, écran central. Je m'arrête sur l'enregistrement automatique : **quatre décisions en quelques lignes**.
- 2,5 s n'est pas arbitraire : à chaque caractère → API saturée, écritures multipliées. Trop long → sauvegarde invisible, travail perdu.
- **Le minuteur précédent est systématiquement annulé** — sinon une frappe rapide empile les requêtes.
- Doublé d'un bouton explicite : l'utilisateur doit pouvoir forcer.
- Rien n'est enregistré tant que le titre est vide.
- Remarque de méthode, écrite dans le dossier : sur la capture C-07 l'indicateur n'apparaît pas, **parce qu'aucune frappe n'a eu lieu**.
- **Une capture atteste d'un état, pas d'un comportement.** Vérifier une fonctionnalité demande de lire le code ou d'exécuter un scénario. → **C'est la raison d'être du jeu d'essai.**

### Diapo 21 · Compter les appels, jamais les stocker `[23:25 — 25:25]`
- Composant métier : le quota IA. **Dix lignes, trois décisions.**
- **1 — C'est une agrégation** sur le journal des 24 dernières heures, pas un compteur sur l'utilisateur. Un compteur se désynchronise — il suffit d'un échec entre l'appel et l'incrément. **Une agrégation est juste par construction.**
- **2 — Fenêtre glissante, pas compteur journalier.** Le cahier des charges dit « 20 requêtes par 24 heures », pas « par jour calendaire ». Remise à zéro à minuit → **40 appels entre 23 h et 1 h**.
- **3 — Le code de retour est 429, pas 403.** 403 = « vous n'avez pas le droit ». 429 = « réessayez plus tard ». **Pas la même information pour le client.**
- Contrôle entièrement serveur. Le front affiche le quota restant — **c'est de l'affichage**.
- Test JE-07. **Mes données contiennent une ligne datée de 25 heures précisément pour vérifier la fenêtre glissante.**

### Diapo 22 · La propriété est dans le WHERE `[25:25 — 26:25]`
- Accès aux données. **Le motif le plus répété du projet.**
- **La propriété est dans la clause WHERE.** Je ne charge pas le document pour comparer ensuite son propriétaire : je demande un document qui a cet identifiant **ET** qui appartient à l'utilisateur courant.
- **Pas stylistique** : avec un contrôle a posteriori, un `if` oublié dans une route ouvre une faille. Ici, oublier la condition **fait échouer le test de propriété**, qui existe pour chaque ressource.
- Conséquence voulue : **404, pas 403.** Un 403 confirmerait que la ressource existe. Le 404 est indiscernable d'un identifiant inexistant.
- Tout passe par l'ORM, paramétré, **aucune concaténation de chaîne** — objectif de qualité tenu sans exception.

### Diapo 23 · Conteneurisée, intégrée, pas déployée `[26:25 — 27:55]`
- **Je préfère l'amener moi-même** : conteneurisée et intégrée en continu depuis le 4 octobre, **mais pas déployée**.
- Trois services :
  - MySQL 8.4, volume persistant, **sonde de santé** — sans elle le backend démarre avant que la base accepte les connexions.
  - Backend sous **Gunicorn**, pas le serveur de dev de Flask, utilisateur non privilégié.
  - Frontend : build Vite en deux étapes, servi par Nginx → **~50 Mo**, parce que l'image ne contient que du statique, pas la chaîne de construction.
- Détail qui compte : secrets en `${VAR:?message}` → **la composition échoue si la variable manque, au lieu de démarrer avec une valeur inventée**.
- Ollama hors composition, sur l'hôte, via `host.docker.internal` : image de plusieurs Go, modèle téléchargé à part.
- CI à chaque push et chaque PR, **trois travaux parallèles**. Le parallélisme n'est pas de la performance : **enchaînés, un échec du frontend masquait l'état du backend** — il fallait deux exécutions.
- Troisième carte, à montrer : ce sont **des changements de configuration, pas de code — c'est pour ça qu'ils s'oublient**.
- Le plus traître : **`SameSite=Strict` raisonne en sites, pas en origines.** En dev, front et API sur localhost → le cookie passe. En prod, deux domaines distincts **casseraient le rafraîchissement sans qu'aucun test local ne le voie**.
- **Ce qui manque pour déployer est une machine avec un démon Docker, pas une étape de conception.**

---

## 6. Sécurité — 27:55 → 32:20

### Diapo 24 · Section `[27:55 — 28:05]`
> « Cinquième temps : la sécurité. **C'est le fil rouge du projet, pas un chapitre.** »

### Diapo 25 · La sécurité comme contrainte de conception `[28:05 — 30:05]`
- Grille : **OWASP Top 10 2021**, croisée avec le cahier des charges et l'ANSSI. Le dossier traite les dix ; j'en montre six.
- Point de méthode : **pas traitée en fin de projet — et pas par vertu, par nécessité pratique.**
- Filtrage par propriétaire dans le WHERE, stockage d'empreintes, refus de démarrer sans clé : **des choix de structure. Les ajouter après aurait demandé de réécrire les couches.**
- **A01** : la propriété est dans le WHERE, **et le rôle est relu en base, pas lu dans le jeton**.
- **A02** : bcrypt + sel pour les mots de passe, SHA-256 pour les jetons. **Aucun secret en clair en base** → une fuite ne permet pas de rejouer une session.
- **A05** : l'application **refuse de démarrer sans `JWT_SECRET_KEY`**. Pas de défaut, pas de repli silencieux. **Une clé de secours en dur est une clé en production.**
- **A10** : la seule URL sortante est `OLLAMA_URL`, une valeur de configuration. **Aucune entrée utilisateur ne devient une destination HTTP.**
- Transparence, c'est dans le dossier : **A09, la journalisation applicative est incomplète.** Le journal IA existe, mais pas de journalisation systématique des événements de sécurité.

### Diapo 26 · Deux jetons `[30:05 — 32:20]`
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

### Diapo 27 · Section `[32:20 — 32:30]`
> « Dernier temps : comment je vérifie, comment je me tiens à jour, et ce que je retiens. »

### Diapo 28 · 195 cas au vert `[32:30 — 34:30]`
- Quatre niveaux, **du moins coûteux au plus coûteux** → ce classement détermine ce qui tourne à chaque push et ce qui reste manuel.
- Campagne du 3 octobre : **195 cas, tous au vert, 59 secondes. 95 % de couverture backend** — 100 % sur `services/` et la persistance, 89-96 % sur les routes.
- Mon objectif était 80 % sur `services/` et les routes, **sans objectif chiffré ailleurs. C'est volontaire : viser un pourcentage global pousse à écrire des tests faciles sur du code sans risque.**
- Les 62 % du front : tirés vers le bas par cinq modules qui sont des enveloppes d'une ligne autour d'axios — **les tester reviendrait à tester axios**.
- Trois zones concentrent l'effort : authentification, propriété, quota. **Les trois endroits où une régression coûte cher.**
- La leçon : **les doubles de test mentent.** Trois défauts de la chaîne IA sont passés sous un faux `requests.post` qui acceptait `json()` à tout moment et ne fermait jamais de connexion. **Il a fallu un vrai serveur HTTP local pour les voir.**
- Tests ajoutés ensuite **vérifiés par mutation** : on casse le code exprès pour s'assurer que le test échoue. **Un test qu'on n'a jamais vu échouer ne prouve rien.**
- Reste : tests système (démon Docker), tests de charge après.

### Diapo 29 · La ligne datée de 25 heures `[34:30 — 36:30]`
- Jeu d'essai : la génération d'une assistance IA. **Trois raisons :**
  1. il traverse les trois couches et sollicite un système externe ;
  2. il concentre cinq contrôles de nature différente ;
  3. il porte les deux exigences les plus délicates : **quota et traçabilité**.
- **Et c'est la seule fonctionnalité qu'aucune capture ne peut attester** — elle se manifeste par un enchaînement, pas par un état.
- Données construites par script, **reproductibles à l'identique**. Quatre comptes : l'utilisatrice principale, un tiers pour les accès croisés, un admin, **un compte au quota abaissé à 1** pour atteindre la limite en un appel.
- La donnée la plus utile : dans le journal de U1, **19 lignes de moins de 24 h, et une ligne de 25 heures**.
- **Cette ligne unique est le seul moyen de distinguer une fenêtre glissante d'un compteur journalier.** Sans elle, JE-07 passerait quelle que soit l'implémentation.
- **Ce que j'ai appris : un jeu de données, ce n'est pas remplir des tables — c'est choisir les valeurs qui font échouer les mauvaises implémentations.**

### Diapo 30 · La sévérité ne prédit pas l'impact `[36:30 — 38:30]`
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

### Diapo 31 · Ce que je retiens `[38:30 — 40:00]`
- Trois colonnes.
- **Livré** : l'application complète sur les cinq lots, 195 tests au vert, conteneurisation et pipeline, audits accessibilité et sécurité, journal de veille.
- **Reste, et je ne le cache pas** : déploiement effectif ; bascule MySQL (schéma exécuté et vérifié, il manque un démon Docker) ; trois compléments AI Act ; journalisation applicative à compléter.
- **Ce que je retiens — trois phrases que ce projet m'a apprises, pas un cours :**
  1. **Un prompt est du code** : il part en production, il oriente le comportement, il se teste.
  2. **Une mesure de sécurité est un composant comme un autre** : ajouter DOMPurify n'a pas clos le sujet XSS, ça l'a déplacé vers sa maintenance.
  3. **Un jeu de données, c'est le choix des valeurs qui font échouer les mauvaises implémentations.**
- Je vous remercie, je suis à votre disposition pour vos questions.

---

## Antisèche — à relire 5 minutes avant

**Chiffres**
`195` tests au vert · `59 s` · `95 %` couverture backend (100 % services) · `62 %` front · `8` tables · `5` blueprints · `9` planches · `20` requêtes / `24 h` · `429` · `404` pas 403 · `15 min` access · `7 jours` refresh · `2,5 s` autosave · `~50 Mo` image front · `8` entrées de veille, `3` actions · CVE `9,1` Ollama / `5,1` DOMPurify · AI Act `2 août 2026` · `13` lots

**Si tu perds le fil** → reviens à la question « pourquoi ce choix ? ». Chaque diapo a une raison, pas une liste.

**Si tu es en retard** → coupe dans les diapos 12, 13, 16 et 19 (descriptives). Ne coupe jamais 8, 10, 21, 22, 26, 31.

**Les quatre « je ne le cache pas »** — à sortir toi-même, jamais à laisser venir :
1. Pas déployé (il manque un démon Docker, pas une conception).
2. A09 journalisation incomplète.
3. `current_app` dans `services/` : seul point où la règle fléchit.
4. La dérive éditoriale « juridique », corrigée, cas TU-04.

**Posture** → une respiration à chaque diapo de section. Les trois phrases finales : lentement, en regardant le jury.
