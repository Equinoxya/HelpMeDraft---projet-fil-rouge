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
    -- Traçabilité AI Act (art. 50) : la ligne atteste que la proposition a été
    -- PRODUITE, ces trois colonnes qu'elle a été ACCEPTÉE et versée au document.
    -- position_debut n'est pas maintenue après l'insertion : elle départage
    -- deux passages identiques, elle ne localise pas le texte.
    insere         BOOLEAN     NOT NULL DEFAULT FALSE,
    position_debut INT         NULL,
    insere_at      DATETIME    NULL,
    user_id        CHAR(36)    NOT NULL,
    id_document    CHAR(36)    NOT NULL,
    PRIMARY KEY (id_ia),
    KEY ix_ia_user_created (user_id, created_at),          -- quota 24 h
    KEY ix_ia_document_created (id_document, created_at),  -- historique du document
    CONSTRAINT fk_ia_user FOREIGN KEY (user_id)
        REFERENCES `user` (user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ia_document FOREIGN KEY (id_document)
        REFERENCES document (id_document) ON DELETE CASCADE,
    CONSTRAINT ck_ia_action CHECK (type_action IN ('reformuler','corriger','completer')),
    -- Une insertion sans horodatage serait une trace inexploitable : le
    -- SGBD refuse l'état incohérent plutôt que de compter sur l'application.
    CONSTRAINT ck_ia_insertion CHECK (insere = FALSE OR insere_at IS NOT NULL)
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

-- ---------- Journal des actions d'administration ---------------------------
--
-- Qui a changé quoi, sur qui, et quand. Les deux emails sont COPIÉS et non
-- seulement référencés : l'action la plus importante à tracer est la
-- suppression d'un compte, et une clé étrangère disparaîtrait au moment même où
-- la trace devient utile.
--
-- acteur_id en ON DELETE SET NULL, et cible_id SANS clé étrangère : supprimer
-- un administrateur ne doit pas effacer ses actions, et la cible peut ne plus
-- exister. Les identifiants ne servent qu'à relier au compte quand il est là.
--
-- Rétention : un an, appliquée par purge_journal_admin() côté application. Le
-- journal contient des données personnelles, il n'a pas à grossir sans fin.
CREATE TABLE journal_admin (
    id_action    CHAR(36)     NOT NULL,
    acteur_id    CHAR(36)     NULL,
    acteur_email VARCHAR(326) NOT NULL,  -- même longueur que user.email
    cible_id     CHAR(36)     NULL,      -- volontairement sans clé étrangère
    cible_email  VARCHAR(326) NOT NULL,
    action       VARCHAR(32)  NOT NULL,
    avant        VARCHAR(255) NULL,
    apres        VARCHAR(255) NULL,
    created_at   DATETIME     NOT NULL,
    PRIMARY KEY (id_action),
    KEY ix_journal_date (created_at),  -- lecture décroissante et purge
    KEY ix_journal_acteur (acteur_id),
    KEY ix_journal_cible (cible_id),
    CONSTRAINT fk_journal_acteur FOREIGN KEY (acteur_id)
        REFERENCES `user` (user_id) ON DELETE SET NULL,
    CONSTRAINT ck_journal_action CHECK (action IN ('role','quota','suppression'))
) ENGINE=InnoDB;
