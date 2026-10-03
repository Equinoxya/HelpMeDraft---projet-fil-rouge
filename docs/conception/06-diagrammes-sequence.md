# 6 · Diagrammes de séquence

> **CP 5 / CP 6** — Production exigée par le dossier de projet : « le diagramme du détail des cas d'utilisations les plus significatifs de type diagramme de séquence ».

## 6.1 UC-10 · Demander une suggestion IA

**Le cas d'utilisation le plus représentatif du projet** : il traverse les quatre couches,
mobilise l'authentification, l'autorisation, la validation des entrées, une règle de gestion
(le quota), un service externe et l'écriture d'une trace.

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant ED as MarkdownEditor.vue
    participant SV as iaService.ts
    participant AX as axios · intercepteurs
    participant RT as ia_route.py<br/>(contrôleur)
    participant AU as auth_service<br/>(métier)
    participant IS as ia_service<br/>(métier)
    participant DB as SQLAlchemy<br/>(accès données)
    participant OL as Ollama

    U->>ED: sélectionne du texte
    U->>ED: clique « Reformuler »
    ED->>SV: generer(idDocument, payload)
    SV->>AX: POST /documents/:id/ia/generer
    AX->>AX: injecte Authorization: Bearer
    AX->>RT: requête HTTP

    rect rgb(232, 240, 254)
        note over RT,AU: Authentification
        RT->>AU: decode_access_token(token)
        AU-->>RT: user_id
    end

    rect rgb(252, 232, 230)
        note over RT: Validation des entrées — liste blanche
        RT->>RT: type_action ∈ {reformuler, corriger, completer} ?
        RT->>RT: scope ∈ {selection, document} ?
        RT->>RT: contenu non vide, ≤ la borne configurée ?
        RT->>RT: instructions ≤ 500 caractères ?
    end

    rect rgb(230, 244, 234)
        note over RT,DB: Autorisation — filtre conjoint
        RT->>DB: SELECT document WHERE id = :id AND user_id = :user
        DB-->>RT: document ou None
        note right of RT: None → 404 (jamais 403)
    end

    rect rgb(254, 247, 224)
        note over RT,DB: Règle RG-07 — quota glissant 24 h
        RT->>DB: SELECT quota_daily_limit FROM user
        DB-->>RT: 20
        RT->>DB: COUNT(ia) WHERE user_id = :user<br/>AND created_at ≥ now − 24h
        DB-->>RT: 7
        note right of RT: 7 < 20 → on continue
    end

    RT->>IS: build_prompt(type_action, contenu, instructions)
    IS->>IS: applique le gabarit de l'action
    IS->>IS: concatène la consigne particulière
    IS-->>RT: prompt

    RT->>IS: call_ollama(prompt)
    IS->>OL: POST /api/generate<br/>(modèle, temperature 0.7, délai max 60 s)
    OL-->>IS: réponse + compteurs de jetons
    IS-->>RT: (content_after, tokens_used)

    rect rgb(240, 240, 240)
        note over RT,DB: Trace — exigence « historique » et preuve
        RT->>DB: INSERT ia (action, avant, après, jetons, user, document)
        DB-->>RT: id_ia
    end

    RT-->>AX: 201 {id_ia, content_after, tokens_used}
    AX-->>SV: réponse
    SV-->>ED: suggestion
    ED->>U: affiche la suggestion de façon différenciée
    note over ED: Le texte de l'utilisateur n'est pas modifié.
    U->>ED: « Remplacer » ou « Insérer » ou « Ignorer »
    ED->>ED: applique le choix dans CodeMirror
```

### Chemins d'erreur

```mermaid
sequenceDiagram
    autonumber
    participant RT as ia_route.py
    participant DB as Base
    participant OL as Ollama
    participant CL as Client

    alt Jeton absent ou expiré
        RT-->>CL: 401 « Token invalide ou expiré »
        CL->>CL: intercepteur → POST /auth/refresh puis rejoue
    else Entrée invalide
        RT-->>CL: 400 (message précisant le champ)
    else Document absent ou appartenant à autrui
        RT->>DB: SELECT ... AND user_id = :user
        DB-->>RT: None
        RT-->>CL: 404 « Document introuvable »
        note right of RT: Volontairement 404 et non 403 :<br/>un 403 confirmerait l'existence du document
    else Quota atteint
        RT-->>CL: 429 « Quota IA quotidien atteint (20 / 24h) »
    else Ollama injoignable ou délai dépassé
        RT->>OL: POST /api/generate
        OL--xRT: ConnectionError / Timeout
        RT-->>CL: 502 (message explicite)
        note right of RT: Aucune ligne ia écrite :<br/>le quota n'est pas consommé<br/>pour un appel qui a échoué
    end
```

> **Point à souligner en soutenance.** L'ordre des contrôles n'est pas arbitraire :
> authentification, puis validation des entrées, puis autorisation, puis quota, puis seulement
> l'appel coûteux au modèle. Chaque contrôle est placé avant celui qui coûte plus cher. Valider
> le quota avant de vérifier la propriété du document reviendrait à faire payer un appel de
> quota à quelqu'un qui n'a pas accès au document.

## 6.2 UC-02 · Se connecter, puis renouveler la session

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant LV as LoginView.vue
    participant ST as store auth (Pinia)
    participant AX as axios
    participant RT as auth_routes.py
    participant AU as auth_service
    participant DB as Base

    U->>LV: adresse mail + mot de passe
    LV->>AX: POST /auth/login
    AX->>RT: requête
    RT->>RT: Flask-Limiter — 5 par minute
    RT->>DB: SELECT user WHERE email = :email
    DB-->>RT: user
    RT->>AU: verify_password(saisie, user.mdp_hash)
    AU-->>RT: vrai

    RT->>AU: generate_access_token(user_id)
    AU-->>RT: JWT HS256, 15 min
    RT->>AU: create_session(user_id)
    AU->>AU: secrets.token_urlsafe(64)
    AU->>DB: INSERT user_session (SHA-256 du jeton, exp +7 j)
    AU-->>RT: refresh token en clair

    RT-->>AX: 200 {access_token, user}<br/>+ Set-Cookie: refresh_token<br/>HttpOnly, SameSite=Strict, Path=/auth
    AX-->>ST: stocke l'access token **en mémoire**
    note over ST: Jamais en localStorage :<br/>un XSS le lirait
    ST->>U: redirection vers /dashboard

    note over U,DB: ⏱ 15 minutes plus tard — l'access token a expiré

    U->>AX: action quelconque
    AX->>RT: requête avec un jeton expiré
    RT-->>AX: 401
    AX->>AX: un seul refresh à la fois,<br/>les requêtes concurrentes attendent
    AX->>RT: POST /auth/refresh (le cookie part automatiquement)
    RT->>AU: rotate_refresh_token(ancien)
    AU->>DB: SELECT user_session WHERE hash = SHA-256(ancien)

    alt Jeton valide
        AU->>DB: DELETE l'ancienne session
        AU->>DB: INSERT la nouvelle session
        AU-->>RT: (user_id, nouveau refresh token)
        RT-->>AX: 200 {access_token} + nouveau cookie
        AX->>AX: rejoue la requête initiale<br/>et celles mises en attente
    else Jeton inconnu — rejeu détecté
        AU-->>RT: ValueError
        RT-->>AX: 401 + suppression du cookie
        AX->>ST: clearAuth()
        ST->>U: redirection vers /login
        note over AU: Un jeton déjà tourné qui revient<br/>signale un vol : la session tombe
    end
```

### Pourquoi deux jetons

| | Access token | Refresh token |
|---|---|---|
| **Durée** | 15 minutes | 7 jours |
| **Stockage** | mémoire JavaScript | cookie `HttpOnly` |
| **Lisible par JavaScript** | oui | **non** |
| **Transmis** | en-tête `Authorization` | automatiquement, aux seules routes `/auth` |
| **En base** | rien (JWT auto-porteur) | empreinte SHA-256 |
| **Si volé** | 15 minutes d'exposition | détecté à la première rotation, session invalidée |

> **Le compromis, formulé simplement.** Un jeton long en mémoire serait perdu à chaque
> rechargement de page. Un jeton long en `localStorage` serait exfiltrable par XSS. La
> combinaison retenue — jeton court en mémoire, jeton long en cookie `HttpOnly` avec rotation —
> donne une session persistante dont le secret durable n'est jamais exposé à JavaScript.
> `SameSite=Strict` et `Path=/auth` ferment la surface CSRF que le cookie ouvrirait sinon.

## 6.3 UC-04 · Réinitialiser son mot de passe

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant FV as ForgotPasswordView
    participant RT as auth_routes.py
    participant DB as Base
    participant ML as email_service
    participant MB as Boîte mail

    U->>FV: saisit son adresse mail
    FV->>RT: POST /auth/forgot-password
    RT->>RT: Flask-Limiter — 3 par heure
    RT->>DB: SELECT user WHERE email = :email

    alt Compte existant
        RT->>RT: génère un jeton aléatoire
        RT->>DB: INSERT password_reset<br/>(empreinte, expiration, used = faux)
        RT->>ML: envoie le lien de réinitialisation
        ML->>MB: mail
    else Compte inexistant
        RT->>RT: ne fait rien
    end

    RT-->>FV: 200 — réponse **identique** dans les deux cas
    note over RT,FV: Énumération de comptes impossible :<br/>la réponse ne dit pas si l'adresse existe

    U->>MB: ouvre le mail
    MB->>U: lien vers /reset-password?token=...
    U->>RT: POST /auth/reset-password (jeton + nouveau mot de passe)
    RT->>DB: SELECT password_reset WHERE token_hash = SHA-256(jeton)

    alt Jeton valide, non expiré, non utilisé
        RT->>DB: UPDATE user SET mdp_hash = bcrypt(nouveau)
        RT->>DB: UPDATE password_reset SET used = vrai
        RT-->>U: 200 — redirection vers /login
    else Jeton invalide, expiré ou déjà utilisé
        RT-->>U: 400
    end
```

> **Trois propriétés à défendre.** La réponse est identique que le compte existe ou non — sinon
> le formulaire devient un oracle d'existence de comptes. Le jeton n'est stocké qu'en empreinte —
> une fuite de la base ne permet pas de réinitialiser les mots de passe. Le drapeau `used`
> garantit l'usage unique — un lien intercepté dans un historique de navigation ne resservira pas.
