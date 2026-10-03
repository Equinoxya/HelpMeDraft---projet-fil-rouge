# 3 · Enchaînement des écrans

> **CP 5** — Analyser les besoins et maquetter une application
> *Critère de performance : « **L'enchainement des maquettes est formalisé par un schéma** ».*

Maquettes associées : [`docs/maquettes/`](../maquettes/) · captures de l'application réalisée : [`docs/captures/`](../captures/)

## 3.1 Schéma d'enchaînement

```mermaid
flowchart TD
    Start(["Arrivée sur le site"]) --> Home["<b>/</b><br/>Accueil"]

    subgraph PUB["Zone publique — accès libre"]
        Home
        Fonc["<b>/fonctionnalites</b>"]
        Tarifs["<b>/tarifs</b>"]
        Modeles["<b>/modeles</b>"]
        Legal["<b>/mentions-legales</b><br/><b>/cgu</b><br/><b>/confidentialite</b>"]
    end

    subgraph GUEST["Zone invité — meta: guestOnly"]
        Login["<b>/login</b><br/>Connexion"]
        Register["<b>/register</b><br/>Inscription"]
        Forgot["<b>/forgot-password</b><br/>Mot de passe oublié"]
        Reset["<b>/reset-password</b><br/>Nouveau mot de passe"]
    end

    subgraph AUTH["Zone authentifiée — meta: requiresAuth"]
        Dash["<b>/dashboard</b><br/>Tableau de bord"]
        List["<b>/documents</b><br/>Mes documents"]
        New["<b>/documents/nouveau</b><br/>Nouveau document"]
        Editor["<b>/documents/:id</b><br/>Éditeur"]
    end

    subgraph ADM["Zone admin — requiresAuth + requiresAdmin"]
        AdminV["<b>/admin</b><br/>Back-office"]
    end

    Home --> Fonc & Tarifs & Modeles
    Home --> Login
    Home --> Register
    Home -.-> Legal
    Fonc --> Register
    Tarifs --> Register

    Register -->|compte créé| Login
    Login -->|identifiants valides| Dash
    Login --> Forgot
    Forgot -->|mail envoyé<br/>lien reçu| Reset
    Reset -->|mot de passe changé| Login

    Dash --> List
    Dash --> New
    List --> New
    List -->|ouvrir| Editor
    New -->|premier enregistrement| Editor
    Editor -->|retour| List

    Dash -->|si role = admin| AdminV
    AdminV --> Dash

    Dash -->|déconnexion| Home
    List -->|déconnexion| Home
    Editor -->|déconnexion| Home

    Login -.->|déjà connecté<br/>guestOnly| Dash
    Dash -.->|non authentifié<br/>ou refresh échoué| Login
    AdminV -.->|role ≠ admin| Dash
```

**Légende**

- Trait plein : navigation déclenchée par l'utilisateur
- Trait pointillé : redirection automatique du garde de navigation, ou lien de pied de page
- Les libellés en gras sont les chemins réels déclarés dans `frontend/src/index.ts`

## 3.2 Zones d'accès

Quatre zones, matérialisées par les métadonnées de route et contrôlées par un garde de navigation.

| Zone | Métadonnée | Écrans | Comportement du garde |
|---|---|---|---|
| Publique | *aucune* | `/`, `/fonctionnalites`, `/tarifs`, `/modeles`, `/mentions-legales`, `/cgu`, `/confidentialite` | accès libre |
| Invité | `guestOnly: true` | `/login`, `/register`, `/forgot-password`, `/reset-password` | un utilisateur déjà connecté est renvoyé vers `/dashboard` |
| Authentifiée | `requiresAuth: true` | `/dashboard`, `/documents`, `/documents/nouveau`, `/documents/:id` | sans session valide, redirection vers `/login` |
| Administration | `requiresAuth` + `requiresAdmin` | `/admin` | sans `role = "admin"`, redirection vers `/dashboard` |

> **Point de sécurité à souligner en soutenance.** Ce garde de navigation est un **confort
> d'interface**, pas un mécanisme de sécurité : il est entièrement contournable depuis la console
> du navigateur. L'autorisation réelle est serveur — `token_required` sur chaque route protégée,
> et `require_admin` en `before_request` du blueprint d'administration. Les deux niveaux sont
> nécessaires : le client pour l'ergonomie, le serveur pour la sécurité.

## 3.3 Écran central : l'éditeur

`/documents/:id` est l'écran qui porte la fonctionnalité la plus représentative du projet.

```mermaid
stateDiagram-v2
    [*] --> Chargement
    Chargement --> Edition : document chargé
    Chargement --> Erreur404 : document absent ou non possédé

    Edition --> Enregistrement : modification (différée)
    Enregistrement --> Edition : PUT 200

    Edition --> SelectionTexte : l'utilisateur sélectionne
    SelectionTexte --> AttenteIA : action IA choisie
    Edition --> AttenteIA : action IA sur tout le document

    AttenteIA --> Suggestion : 201 — suggestion reçue
    AttenteIA --> QuotaAtteint : 429
    AttenteIA --> ServiceIndisponible : 502 Ollama injoignable
    AttenteIA --> Edition : 400 — entrée invalide

    Suggestion --> Edition : insérer ou remplacer
    Suggestion --> Edition : ignorer
    QuotaAtteint --> Edition : message, réessai sous 24 h
    ServiceIndisponible --> Edition : message d'erreur

    Erreur404 --> [*]
```

La suggestion est un **état distinct** de l'édition : elle est présentée à l'utilisateur sans
jamais écraser son texte. L'insertion ou le remplacement est une action explicite de sa part —
c'est l'exigence « intégration des suggestions dans l'éditeur (insertion ou remplacement) » et
« résultat affiché de manière différenciée » du cahier des charges.
