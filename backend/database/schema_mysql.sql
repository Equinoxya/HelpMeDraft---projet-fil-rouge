-- =============================================================
--  HelpMeDraft — création du schéma
--  Cible : MySQL 8.0 / InnoDB / utf8mb4
--  Auteur : Ophélie Bellissens — CDA / CD2IA, Metz Numeric School
--
--  Ordre de création imposé par les dépendances de clés étrangères :
--  user → dossier → document → ia, et les tables satellites de user.
--
--  Note : `revoke` et `user` sont entourés d'accents graves car ce
--  sont des mots-clés MySQL. `REVOKE` est un mot RÉSERVÉ : sans les
--  accents graves, la création de user_session échoue.
-- =============================================================

CREATE DATABASE IF NOT EXISTS helpmedraft
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE helpmedraft;

-- ---------- Comptes --------------------------------------------------------
CREATE TABLE `user` (
    user_id           CHAR(36)     NOT NULL,
    lastname          VARCHAR(50)  NOT NULL,
    firstname         VARCHAR(50)  NOT NULL,
    email             VARCHAR(326) NOT NULL,   -- longueur max RFC 5321
    mdp_hash          VARCHAR(255) NOT NULL,   -- empreinte bcrypt
    role              VARCHAR(20)  NOT NULL DEFAULT 'user',
    quota_daily_limit INT          NOT NULL DEFAULT 20,
    created_at        DATETIME     NOT NULL,
    updated_at        DATETIME     NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_user_email (email),
    CONSTRAINT ck_user_role  CHECK (role IN ('user','admin')),
    -- Borne basse à 1 et non 0, alignée sur MIN_QUOTA de app/routes/admin_route.py.
    -- Un quota de 0 serait un compte bridé sans que rien ne le dise : couper
    -- l'accès à l'IA relève d'un champ explicite, pas de la valeur nulle d'un
    -- compteur (KAN-98).
    CONSTRAINT ck_user_quota CHECK (quota_daily_limit BETWEEN 1 AND 1000)
) ENGINE=InnoDB;

-- ---------- Dossiers -------------------------------------------------------
CREATE TABLE dossier (
    id_dossier CHAR(36)     NOT NULL,
    name       VARCHAR(100) NOT NULL,
    created_at DATETIME     NOT NULL,
    user_id    CHAR(36)     NOT NULL,
    PRIMARY KEY (id_dossier),
    KEY ix_dossier_user (user_id),
    CONSTRAINT fk_dossier_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------- Documents ------------------------------------------------------
CREATE TABLE document (
    id_document CHAR(36)     NOT NULL,
    titre       VARCHAR(255) NOT NULL,
    content     TEXT         NULL,
    format      VARCHAR(20)  NOT NULL DEFAULT 'markdown',
    status      VARCHAR(20)  NOT NULL DEFAULT 'brouillon',
    created_at  DATETIME     NOT NULL,
    updated_at  DATETIME     NOT NULL,
    id_dossier  CHAR(36)     NULL,
    user_id     CHAR(36)     NOT NULL,
    PRIMARY KEY (id_document),
    KEY ix_document_user_updated (user_id, updated_at),  -- liste paginée triée
    KEY ix_document_dossier (id_dossier),                -- filtrage par dossier
    CONSTRAINT fk_document_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_document_dossier FOREIGN KEY (id_dossier)
        REFERENCES dossier (id_dossier) ON DELETE SET NULL,
    CONSTRAINT ck_document_status CHECK (status IN ('brouillon','a_relire','termine')),
    CONSTRAINT ck_document_format CHECK (format IN ('markdown','wysiwyg'))
) ENGINE=InnoDB;

-- ---------- Journal des interactions IA ------------------------------------
CREATE TABLE ia (
    id_ia          CHAR(36)    NOT NULL,
    type_action    VARCHAR(50) NOT NULL,
    content_before TEXT        NULL,
    content_after  TEXT        NULL,
    tokens_used    INT         NOT NULL DEFAULT 0,
    created_at     DATETIME    NOT NULL,
    user_id        CHAR(36)    NOT NULL,
    id_document    CHAR(36)    NOT NULL,
    PRIMARY KEY (id_ia),
    KEY ix_ia_user_created (user_id, created_at),          -- quota 24 h
    KEY ix_ia_document_created (id_document, created_at),  -- historique du document
    CONSTRAINT fk_ia_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ia_document FOREIGN KEY (id_document)
        REFERENCES document (id_document) ON DELETE CASCADE,
    CONSTRAINT ck_ia_action CHECK (type_action IN ('reformuler','corriger','completer'))
) ENGINE=InnoDB;

-- ---------- Consentements RGPD ---------------------------------------------
CREATE TABLE consentement (
    id_consentement   CHAR(36)    NOT NULL,
    type_consentement VARCHAR(50) NOT NULL,
    accepte           BOOLEAN     NOT NULL DEFAULT FALSE,
    date_consentement DATETIME    NOT NULL,
    user_id           CHAR(36)    NOT NULL,
    PRIMARY KEY (id_consentement),
    KEY ix_consentement_user (user_id),
    CONSTRAINT fk_consentement_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------- Sessions -------------------------------------------------------
CREATE TABLE user_session (
    id_session         CHAR(36)     NOT NULL,
    refresh_token_hash VARCHAR(128) NOT NULL,  -- empreinte SHA-256, jamais le jeton
    refresh_token_exp  DATETIME     NOT NULL,
    `revoke`           BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at         DATETIME     NOT NULL,
    user_id            CHAR(36)     NOT NULL,
    PRIMARY KEY (id_session),
    UNIQUE KEY uq_session_token (refresh_token_hash),
    KEY ix_session_user (user_id),
    CONSTRAINT fk_session_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------- Réinitialisations de mot de passe ------------------------------
CREATE TABLE password_reset (
    id         CHAR(36)     NOT NULL,
    token_hash VARCHAR(128) NOT NULL,  -- empreinte SHA-256 du jeton envoyé
    expires_at DATETIME     NOT NULL,
    used       BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at DATETIME     NOT NULL,
    user_id    CHAR(36)     NOT NULL,
    PRIMARY KEY (id),
    KEY ix_reset_user (user_id),
    KEY ix_reset_expires (expires_at),  -- purge des demandes expirées
    CONSTRAINT fk_reset_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE
) ENGINE=InnoDB;
