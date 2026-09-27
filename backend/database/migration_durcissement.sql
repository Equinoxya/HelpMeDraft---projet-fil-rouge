-- =============================================================
--  HelpMeDraft — script de modification : durcissement du schéma
--  Cible : MySQL 8.0, base helpmedraft déjà en service
--  Auteur : Ophélie Bellissens — CDA / CD2IA, Metz Numeric School
--
--  AVERTISSEMENT : ce script déconnecte tous les utilisateurs.
--  Les refresh tokens stockés en clair ne peuvent pas être convertis
--  en empreintes sans connaître le jeton ; ils sont donc purgés.
--  C'est le comportement voulu — un jeton stocké en clair doit être
--  considéré comme compromis.
--
--  Sauvegarder la base avant exécution :
--      mysqldump -u root -p helpmedraft > helpmedraft_avant_durcissement.sql
-- =============================================================

USE helpmedraft;

-- 1) Sessions : passer du jeton en clair à son empreinte ---------------------
DELETE FROM user_session;

ALTER TABLE user_session
    DROP INDEX uq_session_token,
    CHANGE COLUMN refresh_token refresh_token_hash VARCHAR(128) NOT NULL,
    ADD UNIQUE KEY uq_session_token (refresh_token_hash);

-- 2) Normalisation des libellés de consentement -----------------------------
--    L'inférence est locale : aucune donnée n'est transmise à OpenAI.
--    Exécuté AVANT les CHECK, pour qu'aucune ligne existante ne les viole.
UPDATE consentement
   SET type_consentement = 'traitement_ia_local'
 WHERE type_consentement = 'openai_data_processing';

-- 3) Contraintes de valeur --------------------------------------------------
ALTER TABLE `user`
    ADD CONSTRAINT ck_user_role  CHECK (role IN ('user','admin')),
    ADD CONSTRAINT ck_user_quota CHECK (quota_daily_limit BETWEEN 0 AND 1000);

ALTER TABLE document
    ADD CONSTRAINT ck_document_status CHECK (status IN ('brouillon','a_relire','termine')),
    ADD CONSTRAINT ck_document_format CHECK (format IN ('markdown','wysiwyg'));

ALTER TABLE ia
    ADD CONSTRAINT ck_ia_action CHECK (type_action IN ('reformuler','corriger','completer'));

-- 4) Index de performance ---------------------------------------------------
CREATE INDEX ix_ia_user_created       ON ia (user_id, created_at);
CREATE INDEX ix_ia_document_created   ON ia (id_document, created_at);
CREATE INDEX ix_document_user_updated ON document (user_id, updated_at);
CREATE INDEX ix_document_dossier      ON document (id_dossier);

-- =============================================================
--  Contrôles post-exécution
-- =============================================================

-- Les sept tables sont présentes, en InnoDB et utf8mb4
SELECT table_name, engine, table_collation
  FROM information_schema.tables
 WHERE table_schema = 'helpmedraft'
 ORDER BY table_name;

-- Chaque clé étrangère porte CASCADE ou SET NULL, jamais RESTRICT
SELECT constraint_name, table_name, referenced_table_name, delete_rule
  FROM information_schema.referential_constraints
 WHERE constraint_schema = 'helpmedraft';

-- Les index de performance sont en place
SELECT table_name, index_name,
       GROUP_CONCAT(column_name ORDER BY seq_in_index) AS colonnes
  FROM information_schema.statistics
 WHERE table_schema = 'helpmedraft'
 GROUP BY table_name, index_name;
