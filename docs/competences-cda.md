# Compétences CDA — couverture par HelpMeDraft

Titre professionnel **Concepteur développeur d'applications** (TP-01281, millésime 04, 02/07/2024), niveau 6.
Référentiels de référence : [`REAC-CDA-V04.pdf`](./REAC-CDA-V04.pdf) · [`REV-CDA-V04.pdf`](./REV-CDA-V04.pdf)

## Les 11 compétences, réparties en 3 blocs

| Bloc (activité type) | CP | Compétence | Obligatoire dans le projet ? |
|---|---|---|:---:|
| **AT1** — Développer une application sécurisée | 1 | Installer et configurer son environnement de travail en fonction du projet | — |
| | 2 | Développer des interfaces utilisateur | ✅ |
| | 3 | Développer des composants métier | ✅ |
| | 4 | Contribuer à la gestion d'un projet informatique | ✅ |
| **AT2** — Concevoir et développer une application sécurisée organisée en couches | 5 | Analyser les besoins et maquetter une application | ✅ |
| | 6 | Définir l'architecture logicielle d'une application | ✅ |
| | 7 | Concevoir et mettre en place une base de données relationnelle | ✅ |
| | 8 | Développer des composants d'accès aux données SQL et NoSQL | ✅ |
| **AT3** — Préparer le déploiement d'une application sécurisée | 9 | Préparer et exécuter les plans de tests d'une application | ✅ |
| | 10 | Préparer et documenter le déploiement d'une application | — |
| | 11 | Contribuer à la mise en production dans une démarche DevOps | — |

> **8 compétences doivent obligatoirement être mises en œuvre par le projet** (REV §3.1).
> CP 1, 10 et 11 sont évaluées par l'entretien technique et le questionnaire professionnel — mais les traiter
> dans le projet donne de la matière pour l'entretien.

---

## Couverture détaillée

### CP 1 — Installer et configurer son environnement de travail
*Critères : outils de développement installés · gestion de versions installée · **les conteneurs implémentent les services requis** · documentation technique comprise (FR/EN, B1).*

| État | Élément |
|:---:|---|
| ✅ | Git + GitHub, branches, pull requests |
| ✅ | Environnement Python/venv + Vite documenté dans le README |
| ❌ | **Conteneurs** : `docker-compose.yml` vide, aucun Dockerfile → critère de performance non satisfait |

### CP 2 — Développer des interfaces utilisateur
*Critères : conforme au dossier de conception · responsive · charte graphique · réglementation · **code documenté** · **tests unitaires** · **jeu d'essai fonctionnel complet** · **tests de sécurité** · démarche de résolution de problème · **veille**.*

| État | Élément |
|:---:|---|
| ✅ | 15 vues Vue 3 + Tailwind/daisyUI, routing avec chargement différé |
| ✅ | Éditeur Markdown (CodeMirror) avec commandes IA |
| ✅ | Mentions légales / CGU / Politique de confidentialité (RGPD) |
| ✅ | Test de sécurité XSS (`frontend/test_xss.mjs`) |
| ✅ | Veille (`docs/veille-helpmedraft.html`) |
| ❌ | **Tests unitaires front** : Vitest absent de `package.json` |
| ❌ | **Jeu d'essai fonctionnel** documenté |
| 🔄 | **RGAA** : couverture ARIA, contrastes, navigation clavier incomplètes |

### CP 3 — Développer des composants métier
*Critères : **bonnes pratiques POO** · composants sécurisés · règles de nommage · **code documenté** · **tests unitaires** · **tests de sécurité** · démarche de résolution de problème · **veille**.*

| État | Élément |
|:---:|---|
| ✅ | Services `auth_service`, `ia_service`, `email_service` |
| ✅ | Sécurité serveur : hash mots de passe, JWT, permissions, quota IA |
| ✅ | Tests de sécurité (`backend/test_securite.py`) |
| ❌ | **Tests unitaires** : pas de pytest, seulement des scripts lancés à la main |
| 🔄 | **POO** : les services sont des modules de fonctions, pas des classes — à argumenter ou à refactorer |

### CP 4 — Contribuer à la gestion d'un projet informatique
*Critères : **tâches planifiées** · **suivi des tâches rapproché de la planification, retards identifiés** · procédures qualité · environnement de développement adéquat · **outils collaboratifs** · **comptes rendus de réunion structurés**.*

| État | Élément |
|:---:|---|
| ✅ | GitHub comme outil collaboratif, historique de commits |
| ❌ | **Planning** (Gantt ou backlog agile avec itérations) |
| ❌ | **Suivi des tâches** et identification des écarts |
| ❌ | **Comptes rendus de réunion** |
| ❌ | **Procédures qualité** formalisées (conventions de code, définition de « terminé ») |

> ⚠️ C'est aujourd'hui la compétence obligatoire la moins couverte, et elle est intégralement
> documentaire — donc rapide à rattraper.

### CP 5 — Analyser les besoins et maquetter une application
*Critères : besoins couvrant l'ensemble du cahier des charges · **maquettes conformes** · **enchaînement formalisé par un schéma** · **dossier de conception structuré**.*

| État | Élément |
|:---:|---|
| ✅ | Maquettes (`docs/maquettes/`) et captures (`docs/captures/`) |
| ❌ | **Schéma d'enchaînement des écrans** (critère explicite) |
| ❌ | **Dossier de conception** structuré |
| ❌ | Formalisation des besoins : cas d'utilisation ou user stories tracés au cahier des charges |

### CP 6 — Définir l'architecture logicielle d'une application
*Critères : **architecture multicouche répartie sécurisée** conforme aux bonnes pratiques · **rôle de chaque couche défini en tenant compte de la stratégie de sécurité** · **besoins d'éco-conception identifiés**.*

| État | Élément |
|:---:|---|
| ✅ | Découpage en couches effectif : `routes/` → `services/` → `database/` ; SPA découplée via API REST |
| ❌ | **Dossier technique d'architecture** : rôle de chaque couche, stratégie de sécurité par couche (DICP), design patterns et security patterns retenus |
| ❌ | **Besoins d'éco-conception identifiés** et documentés |

### CP 7 — Concevoir et mettre en place une base de données relationnelle
*Critères : **schéma conceptuel respectant le relationnel** · schéma physique conforme · règles de nommage · **intégrité, sécurité et confidentialité** · **base de test avec jeu d'essai complet, restaurable**.*

| État | Élément |
|:---:|---|
| ✅ | 7 entités (`User`, `PasswordReset`, `UserSession`, `Dossier`, `Document`, `Consentement`, `IA`) |
| ✅ | `schema_mysql.sql` + scripts de migration |
| ❌ | **Modèle entités-associations (MCD)** et **modèle physique (MPD)** — exigés aussi par le dossier de projet |
| ❌ | **Jeu d'essai complet** dans une base de test |
| ❌ | **Procédure de sauvegarde / restauration** |
| ❌ | **Utilisateurs SGBD et droits d'accès** (l'app tourne sur SQLite, pas de gestion de comptes) |

### CP 8 — Développer des composants d'accès aux données SQL et NoSQL
*Critères : traitements conformes au dossier de conception · **cas d'exception pris en compte** · intégrité et confidentialité · **conflits d'accès gérés** · **toutes les entrées contrôlées et validées** · **tests unitaires et de sécurité associés à chaque composant** · **veille**.*

| État | Élément |
|:---:|---|
| ✅ | ORM SQLAlchemy 2.0 (`DeclarativeBase`), requêtes paramétrées → pas d'injection SQL |
| ✅ | Validation des entrées côté serveur (ex. `_validate_update_payload`) |
| ❌ | **Tests unitaires** sur les composants d'accès |
| ❌ | **Transactions et conflits d'accès** : à implémenter ou à documenter |
| ❌ | **NoSQL** : aucun composant (l'intitulé dit « SQL **et** NoSQL ») → prévoir au minimum un usage (cache Redis, journal Mongo) ou argumenter le choix devant le jury |

### CP 9 — Préparer et exécuter les plans de tests d'une application
*Critères : **plan de tests couvrant l'ensemble des fonctionnalités** · **environnement de tests créé** · tests exécutés conformes au plan · **résultats cohérents avec l'attendu** · prise en compte des évolutions et problèmes de sécurité.*

| État | Élément |
|:---:|---|
| ✅ | Deux scripts de test de sécurité existants (XSS, tokens) |
| ❌ | **Plan de tests** (intégration, non-régression, système, sécurité, charge) |
| ❌ | **Environnement de tests** dédié |
| ❌ | **Dossier de compte rendu de tests** |
| ❌ | Tests de charge, tests d'acceptation utilisateur |

### CP 10 — Préparer et documenter le déploiement
*Critères : **procédure de déploiement rédigée** · **scripts de déploiement écrits et documentés** · **environnements de tests définis et procédure d'exécution des tests rédigée** · veille.*

| État | Élément |
|:---:|---|
| ✅ | Démarrage rapide dans le README, `.env.example` |
| ❌ | **Procédure de déploiement** (environnements SIT / UAT / production) |
| ❌ | **Scripts de déploiement** documentés |

### CP 11 — Contribuer à la mise en production dans une démarche DevOps
*Critères : **outils de qualité de code utilisés** · **outils d'automatisation de tests utilisés** · **scripts d'intégration continue s'exécutant sans erreur** · **serveur d'automatisation paramétré** · **rapports de CI interprétés** · veille.*

| État | Élément |
|:---:|---|
| ❌ | **Aucun `.github/workflows/`** |
| ❌ | **Conteneurs** et stack `docker compose` |
| ❌ | **Outil de qualité de code** (ESLint, Ruff, SonarQube…) |
| ❌ | **Interprétation des rapports de CI** |

### Compétences transversales
- **Communiquer en français et en anglais** (B1 écrit/compréhension, A2 oral) → le questionnaire professionnel comporte **2 questions ouvertes en anglais** sur une documentation technique anglaise. Documenter du code en anglais est un savoir-faire listé en CP2, CP3 et CP8.
- **Mettre en œuvre une démarche de résolution de problème** → critère de performance de CP2, CP3, CP8 et CP11. À tracer : un bug réel, le diagnostic, les tests, la correction.
- **Apprendre en continu** → le journal de veille existe ; il doit couvrir **sécurité, technologies et accessibilité** et être exploité (vulnérabilités trouvées, failles corrigées).
