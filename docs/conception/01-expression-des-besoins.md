# 1 · Expression des besoins

> **CP 5** — Analyser les besoins et maquetter une application
> *Critère de performance : « Les besoins recensés couvrent l'ensemble des exigences utilisateur exprimées dans le cahier des charges ».*

Source : [cahier des charges LexiCorp](../cahier-des-charges.md).

## 1.1 Objectif et limites du système

**Objectif.** Permettre aux collaborateurs d'une PME de rédiger des documents professionnels
(emails, notes, rapports) et de les améliorer à l'aide d'un modèle de langage génératif, dans un
espace personnel sécurisé.

**Dans le périmètre**

- Comptes utilisateurs avec authentification et récupération de mot de passe
- Rédaction, stockage, classement et suppression de documents
- Trois actions d'assistance par IA : compléter, reformuler, corriger
- Historique des interactions avec l'IA
- Back-office d'administration : utilisateurs, statistiques, quotas
- Conformité RGPD, RGAA et recommandations ANSSI

**Hors périmètre** (choix assumés, à énoncer devant le jury)

- Édition collaborative simultanée de documents
- Partage de documents entre utilisateurs
- Export bureautique (`.docx`, `.pdf`)
- Facturation et gestion d'abonnements — la page Tarifs est purement vitrine
- Application mobile native

**Écart assumé par rapport au cahier des charges.** Le cahier des charges propose « OpenAI GPT-4
via API REST **ou LLM local (Ollama)** ». Le choix retenu est **Ollama en local**. Motif : la
contrainte RGPD du cahier des charges impose qu'« aucune donnée personnelle ne doit être envoyée
à OpenAI sans anonymisation ». Une inférence locale supprime le transfert à un tiers, donc le
besoin d'anonymisation, et la base juridique associée. C'est la réponse la plus forte à la
contrainte, pas un contournement.

## 1.2 Acteurs

| Acteur | Nature | Rôle |
|---|---|---|
| **Visiteur** | humain, non authentifié | consulte les pages vitrine et légales, s'inscrit, se connecte |
| **Utilisateur** | humain, authentifié (`role = "user"`) | rédige et gère ses documents, déclenche les actions IA |
| **Administrateur** | humain, authentifié (`role = "admin"`) | hérite de l'utilisateur, plus la gestion des comptes, des quotas et des statistiques |
| **Service d'inférence** | système externe | Ollama en local — génère les suggestions de texte |
| **Service de messagerie** | système externe | SMTP — achemine le mail de réinitialisation de mot de passe |

## 1.3 Besoins fonctionnels

Chaque besoin est tracé à la section du cahier des charges qui l'exige.

| # | Besoin | CDC | Cas d'utilisation |
|---|---|---|---|
| BF-01 | Créer un compte avec consentement explicite | a | UC-01 |
| BF-02 | Se connecter et se déconnecter | a | UC-02, UC-03 |
| BF-03 | Réinitialiser un mot de passe oublié par mail | a | UC-04 |
| BF-04 | Distinguer utilisateur standard et administrateur | a | UC-15 |
| BF-05 | Rédiger un document dans un éditeur Markdown | b | UC-06 |
| BF-06 | Compléter un paragraphe par IA | b | UC-10 |
| BF-07 | Reformuler pour un ton professionnel par IA | b | UC-10 |
| BF-08 | Corriger l'orthographe et la grammaire par IA | b | UC-10 |
| BF-09 | Insérer ou remplacer la suggestion dans l'éditeur | b | UC-11 |
| BF-10 | Créer, modifier, supprimer un document | c | UC-05, UC-07, UC-09 |
| BF-11 | Enregistrement automatique | c | UC-08 |
| BF-12 | Consulter l'historique des interactions IA | c | UC-12 |
| BF-13 | Organiser les documents en dossiers | c | UC-13 |
| BF-14 | Appeler le service d'inférence de façon sécurisée | d | UC-10 |
| BF-15 | Construire le prompt dynamiquement selon l'action | d | UC-10 |
| BF-16 | Afficher le résultat IA de façon différenciée | d | UC-11 |
| BF-17 | Gérer les comptes utilisateurs (back-office) | e | UC-15 |
| BF-18 | Consulter les statistiques d'usage | e | UC-16 |
| BF-19 | Appliquer un quota de requêtes IA par jour | e | UC-17 |

## 1.4 Besoins non fonctionnels

| # | Besoin | Exigence du CDC | Mise en œuvre |
|---|---|---|---|
| BNF-01 | Authentification sécurisée | hash + JWT ou sessions | bcrypt (coût par défaut) + JWT HS256, access token 15 min, refresh token 7 jours |
| BNF-02 | Protection XSS | Sécurité | rendu Markdown assaini par DOMPurify avant insertion |
| BNF-03 | Protection CSRF | Sécurité | refresh token en cookie `HttpOnly`, `SameSite=Strict`, `Path=/auth` |
| BNF-04 | Protection contre les injections | Sécurité | ORM SQLAlchemy, requêtes paramétrées exclusivement |
| BNF-05 | Chiffrement des données sensibles | Sécurité | **non réalisé** — voir [TODO](../../TODO.md) §8 |
| BNF-06 | Accessibilité RGAA | Accessibilité | **partiel** — contrastes, ARIA et navigation clavier à auditer |
| BNF-07 | Consentement explicite à l'usage de l'IA | RGPD | consentement recueilli à l'inscription, tracé en table `consentement` ; consentement IA **distinct** restant à ajouter |
| BNF-08 | Aucune donnée personnelle envoyée à un tiers | RGPD | inférence locale : la contrainte est satisfaite par construction |
| BNF-09 | Éco-conception | Éco-conception | chargement différé des 16 routes ; compression GZIP et allègement des dépendances à faire |
| BNF-10 | Résistance au bourrage d'identifiants | ANSSI | Flask-Limiter : 5 connexions/min, 3 demandes de réinitialisation/heure |

## 1.5 Règles de gestion

| # | Règle | Implémentation |
|---|---|---|
| RG-01 | Un utilisateur n'accède qu'à ses propres documents, dossiers et historiques IA | filtrage par `user_id` sur **chaque** requête, jamais sur l'identifiant seul |
| RG-02 | Un document appartient à zéro ou un dossier | `document.id_dossier` nullable, `ON DELETE SET NULL` |
| RG-03 | Supprimer un dossier ne supprime pas ses documents | `ON DELETE SET NULL` : les documents sont déclassés |
| RG-04 | Supprimer un compte supprime toutes ses données | `ON DELETE CASCADE` sur les 6 tables liées (RGPD art. 17) |
| RG-05 | Un document a un statut parmi brouillon, à relire, terminé | validation serveur sur liste blanche |
| RG-06 | Une action IA est l'une des trois : compléter, reformuler, corriger | liste blanche `ALLOWED_TYPE_ACTIONS` |
| RG-07 | Le quota IA est glissant sur 24 h, par utilisateur, 20 requêtes par défaut | `COUNT` des lignes `ia` depuis `now − 24 h` comparé à `user.quota_daily_limit` ; `HTTP 429` au-delà |
| RG-08 | Le contenu soumis à l'IA est limité à 20 000 caractères, les instructions à 500 | validation serveur avant appel |
| RG-09 | Le refresh token est tourné à chaque usage ; un jeton rejoué invalide la session | rotation + détection de rejeu (`test_securite.py`) |
| RG-10 | La base ne contient jamais un jeton en clair, seulement son empreinte SHA-256 | `user_session.refresh_token_hash`, `password_reset.token_hash` |
