# Journal de veille — HelpMeDraft

> **Compétence transversale « Apprendre en continu »** — *« Le système de veille mis en place
> permet de suivre l'actualité de la profession, les évolutions technologiques et les
> problématiques de sécurité en lien avec le métier ».*
> Également critère de performance de **CP 2, CP 3, CP 8, CP 9, CP 10 et CP 11**, et production
> exigée du dossier de projet : *« la description de la veille, effectuée par le candidat durant
> le projet, sur les vulnérabilités de sécurité, description des vulnérabilités éventuellement
> trouvées et des failles potentiellement corrigées »*.

**Période couverte** : avril 2026 → 3 octobre 2026
**Dernière revue** : 3 octobre 2026
**Versions confrontées** : `backend/requirements.txt`, `frontend/package-lock.json` (versions résolues, pas les plages déclarées)

> `docs/veille-helpmedraft.html` est la mise en page de la version de septembre. **Ce fichier-ci
> est désormais la source de référence** : l'HTML est à régénérer à partir de lui avant la remise
> du dossier. Deux verdicts de la version HTML sont corrigés ici (DOMPurify, Ollama).

---

## 1 · Méthode

Trois périmètres, chacun avec ses sources et sa fréquence. Principe directeur : **surveiller ce
que le projet utilise réellement**, pas l'actualité de la sécurité en général.

| Périmètre | Sources suivies | Fréquence |
|---|---|---|
| **Sécurité et dépendances** | GitHub Advisory Database, NVD / CVE.org, `pip-audit` et `npm audit`, bulletins CERT-FR (ANSSI), OWASP | hebdomadaire, et à chaque installation |
| **Technologies IA** | notes de version Ollama, OWASP GenAI Security Project, publications sur les modèles ouverts | mensuelle |
| **Réglementaire et accessibilité** | CNIL, Commission européenne (AI Act), DINUM et Arcom (RGAA), W3C (WCAG) | mensuelle |

**Critère de rétention.** Une entrée n'est retenue que si le composant concerné figure dans
`requirements.txt`, `package.json`, ou dans l'environnement d'exécution (Ollama, SGBD, serveur de
développement). Chaque entrée se termine par un **verdict d'applicabilité** : la version utilisée
est-elle dans la plage affectée, et les conditions d'exploitation sont-elles réunies *ici* ?

> Une vulnérabilité publiée n'est pas une vulnérabilité exploitable. La colonne « Impact ici » est
> le résultat de l'analyse, pas la sévérité publiée.

---

## 2 · Tableau de synthèse

| Date | Composant | Référence | Nature | Version ici | **Impact ici** | Action |
|---|---|---|---|---|---|---|
| 31/03/2026 | axios | *pas de CVE* | compromission de la chaîne d'approvisionnement npm | 1.20.0 | **Non affecté** | vérification du fichier de verrouillage |
| 04/2026 | Ollama | CVE-2026-7482 | lecture hors limites dans le chargeur GGUF | à relever | **À vérifier** | relever la version installée |
| 29/04/2026 | Ollama (Windows) | CVE-2026-42248, CVE-2026-42249 | mise à jour automatique détournée en exécution de code persistante | à relever | **À vérifier** | poste de développement Windows |
| 2026 | DOMPurify | CVE-2026-0540 | contournement XSS, 5 éléments manquants dans `SAFE_FOR_XML` | 3.4.16 | **Non affecté** ✅ *corrigé* | aucune — `KAN-99` à fermer |
| 2026 | DOMPurify | CVE-2026-41238, CVE-2026-47423, CVE-2026-49978, CVE-2026-66010 | quatre contournements du nettoyage | 3.4.16 | **Non affecté** | aucune |
| 2026 | PyJWT | CVE-2026-48526 | clé publique de l'émetteur utilisable comme secret HMAC | 2.15.0 | **Non affecté** | aucune |
| 2026 | Flask | CVE-2026-27205 | divulgation d'information, en-tête `Vary: Cookie` absent | 3.1.3 | **Non affecté** | aucune |
| 2026 | Werkzeug | CVE-2026-102598 | correctif en 3.1.9 | **non épinglée** | **Indéterminé** ⚠️ | épingler Werkzeug |
| 08/2026 | Vite | CVE-2026-39363, CVE-2026-39364 | contournement de `server.fs.deny`, lecture de fichiers arbitraires | 8.3.1 | **Non affecté** | ne jamais exposer le serveur de développement |
| 04/08/2026 | OWASP | LLM Top 10 — édition 2026 | refonte du classement des risques des applications à LLM | — | **Concerné** | relire l'intégration IA |
| 02/08/2026 | AI Act | UE 2024/1689 art. 50 | obligations de transparence applicables | — | **Concerné** ⚠️ | `KAN-101` — échéance 02/12/2026 |
| 01/2026 | CNIL | recommandation-cadre IA | cadre actualisé après l'entrée en application de l'AI Act | — | **Concerné** | confronter à la liste de vérification |
| 2026 | RGAA | RGAA 5 | version fondée sur WCAG 2.2, Arcom autorité de contrôle | — | **À anticiper** | auditer sur RGAA 4.1.2 |
| 08/2026 | Ollama | v0.33.x | sorties structurées, temps au premier jeton réduit | — | **Opportunité** | fiabiliserait l'intégration IA |

---

## 3 · Sécurité — fiches détaillées

### 3.1 · DOMPurify — cinq CVE, et une correction de verdict

**Nature.** DOMPurify est le composant qui assainit le Markdown rendu dans l'éditeur. C'est
**la** défense du projet contre le XSS stocké : un document contenant une charge utile ne doit
pas s'exécuter au rendu. Cinq contournements ont été publiés en 2026.

| Référence | Plage affectée | Mécanisme | Correctif |
|---|---|---|---|
| CVE-2026-0540 | 3.1.3 → 3.3.1, 2.5.3 → 2.5.8 | cinq éléments *rawtext* (`noscript`, `xmp`, `noembed`, `noframes`, `iframe`) manquants dans l'expression `SAFE_FOR_XML` | 3.3.2 |
| CVE-2026-41238 | 3.0.1 → 3.3.3 | pollution de prototype injectant des `tagNameCheck` permissifs | 3.3.4 |
| CVE-2026-47423 | 3.4.4 | le navigateur re-clone le contenu de `selectedcontent` **après** l'assainissement | 3.4.5 |
| CVE-2026-49978 | — | contournement via une racine d'ombre attachée dans `<template>.content` | — |
| CVE-2026-66010 | < 3.4.12 | contournement de crochet via `CUSTOM_ELEMENT_HANDLING` | 3.4.12 |

**Verdict pour HelpMeDraft — correction du journal précédent.**
La version résolue dans `package-lock.json` est **3.4.16**, supérieure à tous les correctifs
ci-dessus. Le projet n'est affecté par **aucune** des cinq vulnérabilités.

> ⚠️ **Le journal de septembre indiquait « Affecté — mise à jour ≥ 3.3.2 », et le ticket `KAN-99`
> demande encore cette mise à jour.** Les deux sont obsolètes : la mise à jour des dépendances
> faite depuis a porté DOMPurify bien au-delà. **`KAN-99` est à fermer.** C'est l'illustration
> d'un piège de la veille : une entrée n'est utile que si son verdict est rejoué contre l'état
> courant du projet, pas contre celui du jour où elle a été écrite.

### 3.2 · Vite — serveur de développement exposé

**Nature.** CVE-2026-39364 (CVSS 8.2) : les fichiers normalement bloqués par `server.fs.deny`
(`.env`, `*.crt`) sont servis avec un code 200 si la requête ajoute `?raw`, `?import&raw` ou
`?import&url&inline`. CVE-2026-39363 : le `fetchModule` exposé par le WebSocket du serveur de
développement n'applique pas le contrôle `server.fs`, ce qui permet la lecture de fichiers
arbitraires sans en-tête `Origin`.

**Plages affectées.** Vite 7.1.0 → 7.3.2, et Vite 8 avant 8.0.5.

**Exploitation observée.** Vite écoute sur `localhost` par défaut ; l'exposition vient de l'ajout
de `--host` par confort, ou d'une redirection de port Docker qui publie le 5173. F5 Labs a
relevé **plus de 32 000 événements d'attaque sur le seul mois d'août 2026**, dix-neuf fois plus
que sur les trois mois précédents, les attaquants cherchant des identifiants cloud dans les
fichiers `.env`.

**Verdict pour HelpMeDraft.** La version résolue est **8.3.1**, postérieure au correctif 8.0.5 :
non affecté. Mais la leçon dépasse la CVE et vaut **consigne de projet** : ne jamais lancer le
serveur de développement avec `--host`, et ne pas publier le port 5173 dans la future
configuration `docker-compose`. Le `.env` du backend contient `JWT_SECRET_KEY` et les
identifiants SMTP.

### 3.3 · Flask et Werkzeug — un trou dans l'épinglage

**Flask — CVE-2026-27205.** Divulgation d'information affectant Flask ≤ 3.1.2 : lorsque l'objet
session est consulté par certaines opérations (l'opérateur `in` notamment), Flask n'ajoute pas
l'en-tête `Vary: Cookie`, ce qui peut conduire un cache à servir à un utilisateur une réponse
calculée pour un autre.
**Verdict.** `requirements.txt` épingle `Flask==3.1.3`, postérieure à la plage affectée : non affecté.

**Werkzeug — CVE-2026-102598.** Vulnérabilité de sévérité moyenne, corrigée en 3.1.9.
**Verdict : indéterminé, et c'est un problème en soi.** Werkzeug est une dépendance de Flask,
mais **elle n'est pas épinglée** dans `requirements.txt`. Or ce fichier porte en commentaire
« Versions figées volontairement (reproductibilité des builds et de la CI) » : l'intention n'est
pas tenue pour les dépendances transitives. Deux installations à deux dates différentes peuvent
donc embarquer deux versions de Werkzeug, dont une vulnérable, sans que rien ne le signale.

> **Action.** Geler l'arbre complet des dépendances (`pip freeze > requirements.lock`, ou passer à
> `pip-tools`), et activer `pip-audit` et `npm audit` dans la CI — c'est l'objet du ticket
> `KAN-102`. Tant que les dépendances transitives ne sont pas épinglées, aucun verdict de veille
> sur le backend n'est réellement vérifiable.

### 3.4 · Ollama — chaîne de mise à jour sur Windows

**CVE-2026-42248** — la routine de vérification des mises à jour de la version Windows renvoie
systématiquement un succès : **aucune signature n'est vérifiée** avant de préparer et d'exécuter
la charge de mise à jour.
**CVE-2026-42249** — traversée de répertoires dans le mécanisme de mise à jour : les chemins
locaux sont construits à partir d'en-têtes HTTP non validés, ce qui permet d'écrire un exécutable
hors du répertoire prévu, y compris dans le dossier de démarrage de Windows.

Les deux ont été publiées le **29 avril 2026**. Versions testées vulnérables : **0.12.10 à
0.17.5**. Enchaînées, elles donnent une exécution de code **automatique et persistante**, sans
interaction, puisque Ollama se met à jour silencieusement.

**Verdict pour HelpMeDraft.** À vérifier : la version d'Ollama installée sur le poste de
développement n'est pas relevée. Si elle est ≥ 0.18, le défaut est corrigé ; la version courante
de l'outil est la 0.33.x. **Deux actions**, portées par `KAN-100` :
relever et mettre à jour la version, et **restreindre l'écoute d'Ollama à `127.0.0.1`** — l'API
d'inférence n'a aucune raison d'être jointe depuis le réseau, et elle n'a pas d'authentification.

### 3.5 · OWASP Top 10 for LLM Applications — édition 2026

Publiée le **4 août 2026**. Pour la première fois, le classement est établi à partir d'incidents
réels : un vote de praticiens pour trois quarts, et pour un quart l'analyse de **7 714 incidents**
issus de bases de vulnérabilités publiques et d'une base de dommages liés à l'IA.

**Mouvements principaux**

| Risque | 2025 | 2026 |
|---|:---:|:---:|
| Injection de prompt | 1 | 1 |
| Divulgation d'informations sensibles | 2 | 2 |
| **Agentivité excessive** | 6 | **3** |
| Empoisonnement des données et du modèle | — | 5 |
| Désinformation | — | 6 |
| Consommation non bornée | — | 7 |
| **Traitement inadéquat des sorties** | 5 | **10** |

« System Prompt Leakage » est renommé et élargi en **« Hidden Context Exposure »**. L'injection de
prompt couvre désormais les attaques multimodales dissimulées dans des images ou du son.

**Analyse pour HelpMeDraft**

| Risque | Exposition du projet |
|---|---|
| **Injection de prompt** (1) | **Réelle.** Le contenu du document est concaténé au gabarit de prompt. Un document contenant « ignore les instructions précédentes… » influence la génération. **Portée limitée** : le modèle ne dispose d'aucun outil, l'effet se borne à une suggestion de texte que l'utilisateur voit avant de l'accepter. |
| **Divulgation d'informations sensibles** (2) | **Faible.** Inférence locale : rien ne sort de l'infrastructure. Pas d'apprentissage sur les données utilisateur. |
| **Agentivité excessive** (3) | **Nulle, par conception.** Le modèle renvoie du texte, point. Aucun appel d'outil, aucune écriture en base déclenchée par sa sortie. C'est un argument fort à porter en soutenance, maintenant que ce risque est 3ᵉ. |
| **Consommation non bornée** (7) | **Traitée.** Quota glissant de 20 requêtes par 24 h, contenu plafonné à une borne configurable par machine (3 000 caractères par défaut), délai court sur la connexion à Ollama. Le délai de lecture a été retiré après constat : sur une machine sans carte graphique, il coupait des générations en cours et affichait une erreur là où rien n'avait échoué. Ce qui borne le coût d'un appel, c'est la taille du texte accepté en entrée — le chronomètre ne faisait que rendre l'échec visible plus tôt. |
| **Traitement inadéquat des sorties** (10) | **Traité.** La sortie du modèle est du Markdown rendu via DOMPurify, et elle n'est jamais écrite dans le document sans action explicite de l'utilisateur. |
| **Hidden Context Exposure** | **À vérifier.** Les gabarits de prompt sont en clair dans `ia_service.py`. Ils ne contiennent aucun secret — mais la question mérite d'être posée explicitement plutôt que supposée. |

> **Ce que cette édition change pour le projet.** Les deux risques qui montent — agentivité
> excessive et consommation non bornée — sont précisément ceux que l'architecture traite déjà,
> l'un par conception, l'autre par le quota. Le risque qui reste ouvert est l'injection de prompt,
> et il est structurellement difficile à éliminer : séparer instructions et données dans un prompt
> textuel est un problème non résolu. La parade retenue est la **limitation de l'impact** plutôt
> que la prévention : pas d'outils, pas d'écriture automatique, validation humaine systématique.

---

## 4 · Réglementaire

### 4.1 · AI Act — obligations de transparence applicables depuis le 2 août 2026

**Ce qui s'applique.** L'article 50 du règlement UE 2024/1689 est entré en application le
**2 août 2026**. Les systèmes conversationnels et génératifs doivent signaler clairement à
l'utilisateur qu'il interagit avec une IA, sauf lorsque c'est manifeste. Les contenus générés ou
substantiellement modifiés par une IA doivent être identifiables comme tels, par marquage
technique ou mention visible selon le cas.

**Sanctions.** Jusqu'à **15 millions d'euros ou 3 % du chiffre d'affaires annuel mondial** pour
un manquement aux obligations de transparence.

**Délais.** Pour les outils déjà commercialisés avant le 2 août 2026, un délai court jusqu'au
**2 décembre 2026** pour intégrer le marquage technique. **L'obligation d'information visible,
elle, est d'application immédiate.**

**Verdict pour HelpMeDraft — concerné.** L'application génère du texte à destination de documents
professionnels. Trois actions, portées par `KAN-101` :

1. **Mention visible au premier usage** d'une fonction IA dans l'éditeur — l'obligation
   immédiate, à traiter en priorité.
2. **Clause dédiée dans les CGU et la politique de confidentialité**, distincte du consentement
   RGPD actuel.
3. **Marquage du contenu généré** — échéance du 2 décembre 2026. Le projet a un atout ici : la
   table `ia` conserve déjà `content_before` et `content_after` pour chaque appel. La traçabilité
   de ce qui a été généré existe en base ; il reste à la rendre visible côté utilisateur.

### 4.2 · CNIL — recommandation-cadre IA actualisée

La CNIL a publié en **janvier 2026** une recommandation-cadre actualisée sur l'intelligence
artificielle, en réponse à l'entrée en application de l'AI Act. Elle rappelle que lorsque des
données personnelles sont utilisées dans un système d'IA, **le RGPD et l'AI Act s'appliquent tous
les deux** — l'un ne dispense pas de l'autre. La conformité IA figure au programme des contrôles
de la CNIL pour 2026.

Les principes fondamentaux restent applicables : finalité, minimisation, transparence, droits des
personnes. La CNIL met l'accent sur la minimisation des données dans l'IA générative et sur la
notion d'intervention humaine.

**Verdict pour HelpMeDraft.** Position favorable sur deux points, à faire valoir :
l'**inférence locale** satisfait la minimisation par construction (aucune transmission à un
tiers), et l'**intervention humaine** est structurelle (la suggestion n'est jamais appliquée
sans action de l'utilisateur). Restent ouverts, et déjà au backlog :

- la **durée de conservation du journal IA** (`content_before` / `content_after` sont des données
  personnelles conservées sans limite) — `KAN-84` ;
- l'**export et la suppression de compte** à l'initiative de l'utilisateur (art. 15 et 17) ;
- un **consentement distinct** pour l'usage de l'IA, aujourd'hui fondu dans celui de l'inscription.

> **À faire.** Confronter le projet à la liste de vérification « Développement des systèmes d'IA »
> publiée par la CNIL, et en verser le résultat au dossier.

---

## 5 · Accessibilité

### RGAA 5 — la version qui arrive

**Annonce.** La DINUM prépare le **RGAA 5**, attendu pour **fin 2026**.

**Ce qui change**

| Évolution | Conséquence |
|---|---|
| Fondé sur **WCAG 2.2** | neuf nouveaux critères de succès, orientés handicap moteur et cognitif |
| **Arcom autorité de contrôle** | pouvoir de sanction financière, portail unique de déclaration d'accessibilité |
| **Périmètre élargi** | applications mobiles et documents bureautiques téléchargeables, en plus des sites web |

Parmi les nouveaux critères WCAG 2.2, celui qui touche le plus directement une application de
rédaction : **2.5.8 — taille de cible minimale**, qui impose à toute zone interactive de mesurer
au moins **24 × 24 pixels CSS**. Les boutons de commande IA de l'éditeur sont concernés.
S'ajoutent la visibilité du focus, les alternatives au glisser-déposer, et la cohérence de
l'emplacement de l'aide.

**Verdict pour HelpMeDraft — à anticiper, sans changer de référentiel.** Le RGAA 5 n'est pas
publié : l'audit du projet doit se faire sur **RGAA 4.1.2**, qui reste le référentiel en vigueur.
Mais trois points de WCAG 2.2 sont peu coûteux à traiter maintenant et éviteront une reprise :

1. vérifier la taille des cibles interactives, en particulier les boutons IA de l'éditeur ;
2. soigner la visibilité du focus clavier — c'est de toute façon un critère RGAA 4.1.2 ;
3. garder l'aide et la navigation au même endroit sur toutes les pages.

> **L'argument de soutenance.** Un audit RGAA 4.1.2 conforme qui anticipe trois critères de
> WCAG 2.2 montre une veille réglementaire active, pas seulement une conformité subie. Le lot
> accessibilité (`KAN-14`) est le moins avancé du projet : 0 tâche terminée sur 6.

---

## 6 · Veille technologique — IA

### Ollama v0.33.x — sorties structurées

**Évolution.** Ollama atteint la version **0.33.1** le **26 août 2026**. Deux apports intéressent
directement le projet :

- les **sorties structurées** (`format` avec un schéma JSON) permettent de contraindre la réponse
  du modèle à une structure donnée, au lieu de recevoir du texte libre ;
- le **temps au premier jeton réduit de moitié** environ sur la série 0.33.

**Ce que le projet fait aujourd'hui.** `call_ollama` appelle `/api/generate` sans contrainte de
format et lit `data["response"]` comme du texte brut. Les gabarits de prompt compensent en
demandant au modèle de « répondre uniquement avec le texte reformulé, sans commentaire ni
introduction ». C'est une consigne, pas une garantie : rien n'empêche le modèle de préfixer sa
réponse par « Voici le texte reformulé : », qui se retrouverait alors inséré dans le document de
l'utilisateur.

**Opportunité identifiée.** Une sortie structurée (`{"texte": "..."}`) rendrait l'extraction
déterministe et supprimerait cette classe de défaut. Le gain est réel mais le coût n'est pas nul
— il faut vérifier que le modèle retenu prend en charge la contrainte de schéma.

> **Décision : à arbitrer, pas à faire maintenant.** Le lot tests et le lot documentation
> conditionnent le passage du titre ; cette amélioration non. À inscrire au backlog comme piste
> d'évolution, et à mentionner en soutenance comme veille exploitée — savoir qu'une solution
> existe et avoir arbitré de ne pas la faire *tout de suite* est une décision de gestion de
> projet, pas un oubli.

---

## 7 · Ce que la veille a produit

> *Le dossier de projet demande « description des vulnérabilités éventuellement trouvées et des
> failles potentiellement corrigées ». Voici le lien entre la veille et le backlog.*

| Entrée de veille | Ticket | État |
|---|---|---|
| DOMPurify CVE-2026-0540 | `KAN-99` | **à fermer** — version déjà supérieure au correctif |
| Ollama CVE-2026-42248 / 42249, écoute réseau | `KAN-100` | à faire |
| AI Act art. 50 — transparence | `KAN-101` | à faire — **échéance réglementaire au 02/12/2026** |
| Épinglage des dépendances, audit en CI | `KAN-102` | à faire |
| Conservation du journal IA (CNIL) | `KAN-84` | à faire |
| RGAA — audit et mise en conformité | `KAN-64`, `KAN-67` | à faire |

Relecture de sécurité du 2 octobre, issue de la veille sur les pratiques (OWASP, ANSSI) :

| Constat | Ticket |
|---|---|
| `DELETE /documents/<id>` renvoie une réponse mal construite | `KAN-93` |
| Énumération de comptes possible sur `/auth/register` | `KAN-94` |
| Pas de limitation de débit sur `/auth/refresh` | `KAN-95` |
| Sessions révoquées ou expirées jamais purgées | `KAN-96` |

---

## 8 · Sources

**Sécurité**
- [CVE-2026-0540 — DOMPurify, GitLab Advisories](https://advisories.gitlab.com/npm/dompurify/CVE-2026-0540/)
- [CVE-2026-41238 — DOMPurify, GitHub Advisory Database](https://github.com/advisories/GHSA-v9jr-rg53-9pgp)
- [CVE-2026-47423 — DOMPurify, Miggo](https://www.miggo.io/vulnerability-database/cve/CVE-2026-47423)
- [CVE-2026-49978 — DOMPurify, GitLab Advisories](https://advisories.gitlab.com/npm/dompurify/CVE-2026-49978/)
- [CVE-2026-66010 — DOMPurify, cvefeed.io](https://cvefeed.io/vuln/detail/CVE-2026-66010)
- [CVE-2026-39364 — Vite, GitHub Advisory Database](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [CVE-2026-39363 — Vite, GitLab Advisories](https://advisories.gitlab.com/npm/vite/CVE-2026-39363/)
- [Exposition massive des serveurs de développement Vite — securityonline.info](https://securityonline.info/vite-vulnerabilities-cve-2026-39364-arbitrary-file-read/)
- [CVE-2026-27205 — Flask, SentinelOne](https://www.sentinelone.com/vulnerability-database/cve-2026-27205/)
- [CVE-2026-42249 — Ollama, NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-42249)
- [CVE-2026-42248 — Ollama, CERT Polska](https://cert.pl/en/posts/2026/04/CVE-2026-42248/)
- [Mise à jour automatique d'Ollama détournée — Help Net Security](https://www.helpnetsecurity.com/2026/05/05/ollama-windows-vulnerabilities-cve-2026-42248-cve-2026-42249/)

**IA**
- [OWASP Top 10 for LLM Applications — projet officiel](https://owasp.github.io/www-project-top-10-for-large-language-model-applications/)
- [Édition 2026 du Top 10 LLM — Help Net Security, 6 août 2026](https://www.helpnetsecurity.com/2026/08/06/owasp-2026-llm-top-10-released/)
- [Ce qui change dans le Top 10 LLM 2026 — Aembit](https://aembit.io/blog/the-owasp-top-10-for-llm-applications-2026-what-changed-and-why-it-matters/)
- [Versions et nouveautés d'Ollama en 2026 — PromptQuorum](https://www.promptquorum.com/local-llms/local-llm-model-updates-2026)

**Réglementaire**
- [AI Act : ce qui change le 2 août 2026 — Blog du Modérateur](https://www.blogdumoderateur.com/ia-act-2-aout-2026/)
- [Nouvelles obligations depuis le 2 août 2026 — Pôle d'excellence cyber](https://www.pole-excellence-cyber.org/europe/ai-act-obligations-2-aout-2026/)
- [Ce qui a vraiment changé le 2 août 2026 — Toute l'Europe](https://www.touteleurope.eu/economie-et-social/intelligence-artificielle-ce-qui-change-vraiment-le-2-aout-2026-avec-le-reglement-europeen/)
- [Développement des systèmes d'IA : les recommandations de la CNIL](https://www.cnil.fr/fr/developpement-des-systemes-dia-les-recommandations-de-la-cnil-pour-respecter-le-rgpd)
- [Liste de vérification « Développement des systèmes d'IA » — CNIL (PDF)](https://www.cnil.fr/sites/default/files/2025-07/ia_liste_de_verification.pdf)
- [Questions-réponses sur l'utilisation d'un système d'IA générative — CNIL](https://www.cnil.fr/fr/les-questions-reponses-de-la-cnil-sur-lutilisation-dun-systeme-dia-generative)

**Accessibilité**
- [Évolution du RGAA — blog Ippon, avril 2026](https://blog.ippon.fr/2026/04/13/accessibilite-numerique-evolution-du-rgaa/)
- [RGAA 5 : ce qui change réellement — Binclusive](https://binclusive.io/en/blog/rgaa-5-france-digital-accessibility-standard)
- [Où en est le RGAA 5 — Accessibility Sentinel](https://accessibility-sentinel.com/en/rgaa-5/)
