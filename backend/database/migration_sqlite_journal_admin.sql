-- =============================================================================
-- HelpMeDraft — journal des actions d'administration (variante SQLite)
-- -----------------------------------------------------------------------------
-- Même table que database/migration_journal_admin.sql, écrite pour SQLite, qui
-- sert en développement et pour les tests. Les raisons de conception sont dans
-- la version MySQL ; seule la syntaxe change ici.
--
-- Utile uniquement sur une base SQLite EXISTANTE : sur une base neuve,
-- l'application crée le schéma elle-même à partir des classes de l'ORM (voir la
-- fin de database/db.py).
--
-- Exécution (depuis backend/) :
--     sqlite3 HelpMeDraft.db < database/migration_sqlite_journal_admin.sql
-- =============================================================================

CREATE TABLE IF NOT EXISTS journal_admin (
    id_action    VARCHAR(36)  NOT NULL PRIMARY KEY,
    acteur_id    VARCHAR(36)  NULL REFERENCES user (user_id) ON DELETE SET NULL,
    acteur_email VARCHAR(326) NOT NULL,
    cible_id     VARCHAR(36)  NULL,
    cible_email  VARCHAR(326) NOT NULL,
    action       VARCHAR(32)  NOT NULL
                 CONSTRAINT ck_journal_action
                 CHECK (action IN ('role','quota','suppression')),
    avant        VARCHAR(255) NULL,
    apres        VARCHAR(255) NULL,
    created_at   DATETIME     NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_journal_date   ON journal_admin (created_at);
CREATE INDEX IF NOT EXISTS ix_journal_acteur ON journal_admin (acteur_id);
CREATE INDEX IF NOT EXISTS ix_journal_cible  ON journal_admin (cible_id);
