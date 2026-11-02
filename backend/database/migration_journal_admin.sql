-- =============================================================================
-- HelpMeDraft — journal des actions d'administration
-- -----------------------------------------------------------------------------
-- Le back-office permet de changer un rôle, un quota, et de supprimer un
-- compte. Rien n'en gardait trace : impossible de savoir qui avait promu qui,
-- ni qui avait supprimé quel compte. Pour un écran qui touche aux droits et
-- détruit des données, c'est le manque le plus gênant — et un attendu du RGPD,
-- qui demande de pouvoir rendre compte des traitements.
--
-- CHOIX DE CONCEPTION, à lire avant de modifier cette table :
--
--   • les deux emails sont COPIÉS, pas seulement référencés. L'action la plus
--     importante à tracer est la suppression : une clé étrangère disparaîtrait
--     au moment même où la trace devient utile, et le journal dirait
--     « quelqu'un a supprimé quelqu'un » ;
--   • acteur_id est en ON DELETE SET NULL : supprimer un administrateur ne doit
--     pas effacer les actions qu'il a faites ;
--   • cible_id n'a AUCUNE clé étrangère, volontairement : la cible peut ne plus
--     exister, c'est même le cas normal après une suppression ;
--   • avant/apres sont du texte. Des colonnes typées par action laisseraient
--     trois colonnes vides sur quatre à chaque ligne.
--
-- RÉTENTION : un an, appliquée par purge_journal_admin() côté application, sur
-- le modèle de la purge des sessions expirées. Ce journal contient des données
-- personnelles ; il n'a pas à grossir indéfiniment.
--
-- Exécution (MySQL 8) :
--     mysql -u <user> -p helpmedraft < database/migration_journal_admin.sql
--
-- Sauvegarde préalable :
--     ./backend/database/sauvegarde.sh
--
-- Effet sur les données : aucun. La table est créée vide. Les actions
-- d'administration antérieures à cette migration n'ont jamais été collectées,
-- et aucune reconstitution n'est possible — le journal commence ici.
-- =============================================================================

CREATE TABLE IF NOT EXISTS journal_admin (
    id_action    CHAR(36)     NOT NULL,
    acteur_id    CHAR(36)     NULL,
    acteur_email VARCHAR(326) NOT NULL,
    cible_id     CHAR(36)     NULL,
    cible_email  VARCHAR(326) NOT NULL,
    action       VARCHAR(32)  NOT NULL,
    avant        VARCHAR(255) NULL,
    apres        VARCHAR(255) NULL,
    created_at   DATETIME     NOT NULL,
    PRIMARY KEY (id_action),
    KEY ix_journal_date (created_at),
    KEY ix_journal_acteur (acteur_id),
    KEY ix_journal_cible (cible_id),
    CONSTRAINT fk_journal_acteur FOREIGN KEY (acteur_id)
        REFERENCES `user` (user_id) ON DELETE SET NULL,
    CONSTRAINT ck_journal_action CHECK (action IN ('role','quota','suppression'))
) ENGINE=InnoDB;

-- ── Contrôles ───────────────────────────────────────────────────────────────
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
  FROM information_schema.COLUMNS
 WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'journal_admin'
 ORDER BY ORDINAL_POSITION;

SELECT CONSTRAINT_NAME, CHECK_CLAUSE
  FROM information_schema.CHECK_CONSTRAINTS
 WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = 'ck_journal_action';

SELECT CONSTRAINT_NAME, DELETE_RULE
  FROM information_schema.REFERENTIAL_CONSTRAINTS
 WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = 'fk_journal_acteur';
