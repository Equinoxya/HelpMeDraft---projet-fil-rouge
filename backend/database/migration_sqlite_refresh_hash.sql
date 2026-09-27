-- =============================================================
--  HelpMeDraft — migration de DEV (SQLite : backend/HelpMeDraft.db)
--  Pendant SQLite du point 1 de migration_durcissement.sql (MySQL).
--
--  Pourquoi : la colonne user_session.refresh_token contenait le jeton
--  lui-même. Le code ne stocke désormais que son empreinte SHA-256
--  (colonne refresh_token_hash). SQLAlchemy ne modifie pas une table
--  existante : sans ce script, la base de dev garde l'ancienne colonne
--  et /auth/login échoue avec "no such column: refresh_token_hash".
--
--  Les jetons en clair ne sont pas convertibles en empreintes (SHA-256
--  n'est pas inversible) : les sessions sont purgées. C'est voulu — un
--  jeton qui a été stocké en clair doit être considéré comme compromis.
--  Effet visible : tous les comptes sont déconnectés, il faut se
--  reconnecter. Les comptes, documents et dossiers sont conservés.
--
--  Exécution (depuis backend/) :
--      sqlite3 HelpMeDraft.db < database/migration_sqlite_refresh_hash.sql
--  Sans le binaire sqlite3 :
--      python -c "import sqlite3,pathlib; sqlite3.connect('HelpMeDraft.db').executescript(pathlib.Path('database/migration_sqlite_refresh_hash.sql').read_text(encoding='utf-8'))"
-- =============================================================

DELETE FROM user_session;

ALTER TABLE user_session RENAME COLUMN refresh_token TO refresh_token_hash;

-- Contrôle : la colonne attendue est présente, l'ancienne a disparu.
PRAGMA table_info(user_session);
