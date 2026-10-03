-- =============================================================================
-- HelpMeDraft — alignement de la borne minimale du quota IA (KAN-98)
-- -----------------------------------------------------------------------------
-- Constat : schema_mysql.sql autorisait `quota_daily_limit BETWEEN 0 AND 1000`,
-- alors que l'API (MIN_QUOTA dans app/routes/admin_route.py) refuse toute
-- valeur inférieure à 1. Une valeur de 0 était donc acceptée par le SGBD mais
-- inatteignable par le back-office : une divergence silencieuse entre les deux
-- gardiens de la même règle.
--
-- Décision : la base s'aligne sur l'API. Un quota de 0 serait un compte bridé
-- sans que rien ne le signale ; couper l'accès à l'IA relève d'un champ
-- explicite, pas de la valeur nulle d'un compteur.
--
-- Exécution (MySQL 8) :
--     mysql -u <user> -p helpmedraft < database/migration_quota_min.sql
--
-- Idempotence : le script remonte d'abord les lignes à 0, pour qu'aucune ne
-- viole la nouvelle contrainte au moment de sa création.
-- =============================================================================

START TRANSACTION;

-- 1. Aucune ligne existante ne doit violer la contrainte à venir.
UPDATE user
   SET quota_daily_limit = 1
 WHERE quota_daily_limit < 1;

-- 2. Remplacement de la contrainte.
ALTER TABLE user DROP CONSTRAINT ck_user_quota;
ALTER TABLE user
    ADD CONSTRAINT ck_user_quota CHECK (quota_daily_limit BETWEEN 1 AND 1000);

COMMIT;

-- Vérification :
--   SELECT MIN(quota_daily_limit), MAX(quota_daily_limit) FROM user;
--   SHOW CREATE TABLE user;
