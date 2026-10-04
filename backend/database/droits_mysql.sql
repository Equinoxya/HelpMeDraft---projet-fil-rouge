-- =============================================================================
--  HelpMeDraft — utilisateurs du SGBD et droits d'accès
--  Cible : MySQL 8.0 / 8.4, base helpmedraft créée par schema_mysql.sql
--  Auteur : Ophélie Bellissens — CDA / CD2IA, Metz Numeric School
-- -----------------------------------------------------------------------------
--  PRINCIPE : moindre privilège. Trois besoins distincts, trois comptes
--  distincts, chacun avec le strict nécessaire. Un seul compte « bon à tout
--  faire » signifie qu'une injection SQL réussie, un identifiant qui fuit ou
--  une erreur de manipulation disposent immédiatement de TOUS les droits,
--  jusqu'au DROP TABLE.
--
--  Ce que chaque compte peut faire, et surtout ce qu'il ne peut pas :
--
--    helpmedraft_app         l'application Flask. Lit et écrit les données.
--                            AUCUN droit de structure : pas de CREATE, pas
--                            d'ALTER, pas de DROP. C'est ce qui rend la
--                            séparation réelle — une injection SQL qui
--                            aboutirait ne peut pas supprimer une table ni
--                            créer un compte.
--
--    helpmedraft_sauvegarde  mysqldump. SELECT seulement, plus les trois
--                            droits techniques qu'un dump cohérent exige
--                            (LOCK TABLES, SHOW VIEW, TRIGGER). Ne peut rien
--                            modifier : un script de sauvegarde mal écrit ne
--                            peut pas abîmer la base qu'il sauvegarde.
--
--    helpmedraft_migration   l'application des scripts de migration. Droits
--                            de structure, utilisé À LA MAIN et jamais par un
--                            service qui tourne. Séparé de l'applicatif
--                            exprès : une migration est une opération
--                            exceptionnelle, elle n'a pas à être permise en
--                            permanence.
--
--  Aucun des trois n'a de droit sur `mysql`, `information_schema` ni sur une
--  autre base : les GRANT sont tous portés sur `helpmedraft`.*
--
--  Les comptes sont déclarés en @'%' et non @'localhost' : dans la pile
--  Docker, l'application se connecte depuis un AUTRE conteneur, donc depuis
--  une adresse IP du réseau de la composition. Un compte @'localhost' serait
--  refusé avec « Access denied », et la cause est difficile à voir.
--  En déploiement hors conteneur, restreindre ces hôtes à l'adresse réelle
--  des clients.
--
--  PIÈGE RENCONTRÉ EN ESSAI, sur une installation manuelle du SGBD : certains
--  paquets (MariaDB sous Debian et Ubuntu, notamment) créent des comptes
--  ANONYMES ''@'localhost'. Pour une connexion venant de localhost, ils sont
--  plus spécifiques que 'helpmedraft_app'@'%' et l'emportent donc : la
--  connexion échoue avec « Access denied for user 'helpmedraft_app'@'localhost'
--  », ce qui désigne un compte qui existe et des droits qui sont corrects.
--  Les repérer et les retirer :
--      SELECT user, host FROM mysql.user WHERE user = '';
--  L'image MySQL officielle, celle de la composition Docker, n'en crée aucun :
--  le piège ne concerne qu'une installation à la main.
-- -----------------------------------------------------------------------------
--  EXÉCUTION
--
--  Les trois mots de passe ne sont PAS écrits dans ce fichier : il est
--  versionné. Ils sont portés par les marqueurs __MDP_*__ ci-dessous, que
--  initdb/20-droits.sh remplace par les valeurs de l'environnement avant de
--  passer le script à MySQL.
--
--    • en conteneur : automatique, au premier démarrage du service db.
--    • à la main    : remplacer les trois marqueurs puis
--                     mysql -u root -p < database/droits_mysql.sql
--                     (ne pas enregistrer le fichier ainsi complété)
-- =============================================================================

-- Le compte créé par l'image Docker à partir de MYSQL_USER reçoit ALL
-- PRIVILEGES sur toute la base, ce qui inclut DROP. On le retire : ce script
-- est la référence des droits, pas un ajout par-dessus un état plus large.
-- IF EXISTS parce que le compte n'existe pas lors d'une exécution manuelle sur
-- une base montée sans l'image Docker.
DROP USER IF EXISTS 'helpmedraft'@'%';

-- ---------- Compte applicatif ----------------------------------------------
CREATE USER IF NOT EXISTS 'helpmedraft_app'@'%' IDENTIFIED BY '__MDP_APP__';
ALTER USER 'helpmedraft_app'@'%' IDENTIFIED BY '__MDP_APP__';

GRANT SELECT, INSERT, UPDATE, DELETE
    ON helpmedraft.* TO 'helpmedraft_app'@'%';

-- ---------- Compte de sauvegarde -------------------------------------------
CREATE USER IF NOT EXISTS 'helpmedraft_sauvegarde'@'%' IDENTIFIED BY '__MDP_SAUVEGARDE__';
ALTER USER 'helpmedraft_sauvegarde'@'%' IDENTIFIED BY '__MDP_SAUVEGARDE__';

-- LOCK TABLES, SHOW VIEW et TRIGGER ne sont pas du luxe : sans eux, mysqldump
-- s'interrompt sur une erreur de droits au lieu de produire une sauvegarde
-- incomplète en silence. Ils restent en lecture seule sur les données.
GRANT SELECT, LOCK TABLES, SHOW VIEW, TRIGGER
    ON helpmedraft.* TO 'helpmedraft_sauvegarde'@'%';

-- ---------- Compte de migration --------------------------------------------
CREATE USER IF NOT EXISTS 'helpmedraft_migration'@'%' IDENTIFIED BY '__MDP_MIGRATION__';
ALTER USER 'helpmedraft_migration'@'%' IDENTIFIED BY '__MDP_MIGRATION__';

-- Les droits de ce compte sont dictés par ce qu'il doit RÉELLEMENT exécuter :
-- les scripts migration_*.sql, et le contenu d'un dump produit par
-- sauvegarde.sh. La première version s'arrêtait aux droits de structure, et la
-- restauration échouait à sa quarante-deuxième ligne :
--
--     LOCK TABLES `consentement` WRITE
--     ERROR 1044: Access denied for user 'helpmedraft_migration'@'%'
--
-- mysqldump encadre en effet chaque table de LOCK TABLES / UNLOCK TABLES
-- (--add-locks est actif par défaut, et accélère nettement le chargement).
-- Un compte de restauration incapable de restaurer n'est pas du moindre
-- privilège, c'est une sauvegarde inutilisable — et on ne l'aurait découvert
-- qu'en essayant de s'en servir.
--
-- Les droits sur les routines et les déclencheurs suivent le même
-- raisonnement : le dump est produit avec --routines --triggers. Le schéma n'en
-- comporte aucun aujourd'hui, mais le jour où il en comportera, la restauration
-- ne doit pas échouer pour un droit manquant.
GRANT SELECT, INSERT, UPDATE, DELETE,
      CREATE, ALTER, DROP, INDEX, REFERENCES,
      LOCK TABLES,
      CREATE ROUTINE, ALTER ROUTINE, EXECUTE, TRIGGER
    ON helpmedraft.* TO 'helpmedraft_migration'@'%';

FLUSH PRIVILEGES;

-- =============================================================================
--  Contrôles post-exécution
-- =============================================================================

-- Les droits effectifs de chaque compte, à lire ligne par ligne.
-- ATTENDU — aucune ligne « ON *.* » autre que « GRANT USAGE », qui ne donne
-- aucun droit sur aucune donnée et sert seulement à exister.
SHOW GRANTS FOR 'helpmedraft_app'@'%';
SHOW GRANTS FOR 'helpmedraft_sauvegarde'@'%';
SHOW GRANTS FOR 'helpmedraft_migration'@'%';

-- Contrôle de non-régression du moindre privilège : le compte applicatif ne
-- doit posséder AUCUN droit de structure.
-- ATTENDU : jeu de résultats vide.
SELECT grantee, privilege_type
  FROM information_schema.schema_privileges
 WHERE grantee LIKE '''helpmedraft_app''%'
   AND privilege_type IN ('CREATE', 'ALTER', 'DROP', 'INDEX', 'REFERENCES',
                          'CREATE USER', 'GRANT OPTION');
