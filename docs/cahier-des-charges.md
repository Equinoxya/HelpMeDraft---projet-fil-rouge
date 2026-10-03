# Cahier des charges — HelpMeDraft by LexiCorp

> Transcription du cahier des charges officiel (CD2IA 2025/2026, avril 2025).
> PDF de référence : [`cahier-des-charges-helpmedraft.pdf`](./cahier-des-charges-helpmedraft.pdf)
> Les livrables marqués d'un `*` sont **obligatoires pour le passage du titre**.

## Contexte

LexiCorp est une jeune entreprise spécialisée dans les outils de gestion documentaire
pour les PME. Elle souhaite offrir un nouveau service : une application web permettant
aux collaborateurs de rédiger et améliorer leurs documents professionnels (emails,
notes, rapports) grâce à une intelligence artificielle générative.

## Objectifs

Développer une application web sécurisée et accessible permettant aux utilisateurs de :

- Rédiger et stocker des documents professionnels.
- Bénéficier de suggestions et de reformulations via l'API OpenAI (GPT-4 ou GPT-3.5) ou autre modèle de langage.
- Gérer un espace personnel sécurisé (authentification, historique).
- Respecter les exigences de sécurité, accessibilité et confidentialité des données (RGPD, ANSSI, RGAA).

## Fonctionnalités attendues

### a. Gestion utilisateur
- Inscription / Connexion / Déconnexion
- Récupération de mot de passe
- Rôles : utilisateur standard, administrateur

### b. Éditeur de texte intelligent
- Zone de rédaction (éditeur Markdown ou WYSIWYG)
- Boutons de commande IA : compléter un paragraphe, reformuler pour un ton professionnel, corriger fautes grammaticales et orthographiques
- Intégration des suggestions dans l'éditeur (insertion ou remplacement)

### c. Gestion documentaire
- Création / modification / suppression de documents
- Enregistrement automatique
- Historique des interactions avec l'IA
- Organisation en dossiers ou catégories

### d. Intégration IA
- Appels sécurisés vers l'API de complétion automatique
- Prompt engineering dynamique
- Résultat affiché de manière différenciée (highlight / modal)

### e. Back-office (Admin)
- Gestion des utilisateurs
- Statistiques d'usage : nombre de documents, appels API
- Système de quota (ex : 20 requêtes IA / jour)

## Contraintes techniques & fonctionnelles

**Sécurité**
- Authentification sécurisée (hash + JWT ou sessions)
- Stockage des données sensibles chiffré
- Protection contre XSS / CSRF / injections

**Accessibilité**
- Respect du RGAA : contraste, navigation clavier, balises ARIA
- Tests via Google Lighthouse ou WAVE

**RGPD**
- Consentement explicite pour l'usage des services IA
- Aucune donnée personnelle ne doit être envoyée à OpenAI sans anonymisation

**Éco-conception**
- Chargement différé, poids optimisé des dépendances, compression GZIP

## Environnement technique recommandé

| Domaine | Technologie |
|---|---|
| Front-end | React + Tailwind ou Bootstrap |
| Back-end | Python / Flask |
| BDD | MySQL ou MongoDB |
| IA | OpenAI GPT-4 via API REST (chat/completions) ou LLM local (Ollama) |
| Authentification | JWT ou Passport.js |
| CI/CD | GitHub Actions ou GitLab CI |
| Conteneurisation | Docker + docker-compose |

## Livrables attendus

**a. Techniques**
- Code source structuré, documenté
- Dossier projet (architecture, BDD, diagrammes) `*`
- Scripts d'installation / déploiement (Docker, CI/CD)
- Fichier `.env.example` avec variables nécessaires
- Journal de veille (IA, sécurité, accessibilité) `*`

**b. Fonctionnels**
- Documentation utilisateur (PDF ou web)
- Présentation orale avec diaporama `*`
- Jeu de tests automatisés + plan de test manuel `*`
- Rapport d'audit d'accessibilité et de sécurité

## Plan de développement indicatif

| Étape | Durée estimée | Résultat attendu |
|---|---|---|
| Expression des besoins & maquettes | 2 semaines | Dossier de conception |
| Mise en place de l'architecture (front, back, BDD) | 3 semaines | Projet fonctionnel sans logique métier |
| Intégration IA | 1 semaine | Fonctions « Compléter / Corriger / Reformuler » opérationnelles |
| Tests unitaires, validation RGPD & accessibilité | 1 semaine | Fonctionnalités stables, sécurisées |
| CI/CD, Dockerisation, déploiement (VM locale) | 1 semaine | Application accessible en ligne ou en réseau local |
| Documentation, soutenance, préparation examen | 1 semaine | Dossier + support de présentation prêts |
