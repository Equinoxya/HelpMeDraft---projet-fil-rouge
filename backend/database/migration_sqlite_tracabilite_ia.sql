-- =============================================================
--  HelpMeDraft — migration de DEV (SQLite : backend/HelpMeDraft.db)
--  Pendant SQLite de migration_tracabilite_ia.sql (MySQL).
--
--  Pourquoi : la table `ia` a reçu trois colonnes de traçabilité
--  (insere, position_debut, insere_at — AI Act art. 50). SQLAlchemy
--  ne modifie PAS une table existante : `Base.metadata.create_all()`
--  crée les tables manquantes, jamais les colonnes manquantes. La
--  base de dev gardait donc l'ancien schéma, et POST
--  /documents/<id>/ia/generer échouait à l'INSERT avec
--  « table ia has no column named insere ». L'exception n'étant pas
--  rattrapée, Flask répondait 500 SANS passer par after_request,
--  donc sans en-tête Access-Control-Allow-Origin : le navigateur
--  affichait une erreur CORS qui masquait la véritable cause.
--
--  Effet sur les données : aucune perte. Les lignes existantes
--  passent à insere = 0 (l'information n'a jamais été collectée pour
--  elles — cf. § 11.4 du dossier).
--
--  Différence avec la version MySQL : la contrainte CHECK
--  ck_ia_insertion n'est pas ajoutée. SQLite ne sait pas ajouter une
--  contrainte à une table existante (il faudrait reconstruire la
--  table). Elle reste portée par MySQL en conteneur et par l'ORM sur
--  une base SQLite créée de zéro.
--
--  Exécution (depuis backend/) :
--      sqlite3 HelpMeDraft.db < database/migration_sqlite_tracabilite_ia.sql
--  Sans le binaire sqlite3 :
--      python -c "import sqlite3,pathlib; sqlite3.connect('HelpMeDraft.db').executescript(pathlib.Path('database/migration_sqlite_tracabilite_ia.sql').read_text(encoding='utf-8'))"
-- =============================================================

ALTER TABLE ia ADD COLUMN insere         BOOLEAN  NOT NULL DEFAULT 0;
ALTER TABLE ia ADD COLUMN position_debut INTEGER  NULL;
ALTER TABLE ia ADD COLUMN insere_at      DATETIME NULL;

-- Contrôle : les trois colonnes sont présentes.
PRAGMA table_info(ia);
