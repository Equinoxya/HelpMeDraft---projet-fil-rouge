-- =============================================================================
-- HelpMeDraft — traçabilité des contenus générés par IA (AI Act, art. 50)
-- -----------------------------------------------------------------------------
-- Contexte : depuis le 2 août 2026, le règlement européen sur l'intelligence
-- artificielle impose que les contenus générés par IA soient identifiables.
-- La table `ia` conservait déjà content_before et content_after, donc la trace
-- de ce que le modèle a PRODUIT. Elle ne disait rien de ce que l'utilisateur a
-- ACCEPTÉ : une proposition rejetée et une proposition insérée dans le document
-- y étaient indiscernables.
--
-- Trois colonnes comblent l'écart :
--
--     insere          la proposition a-t-elle été appliquée au document
--     position_debut  décalage AU MOMENT de l'insertion
--     insere_at       horodatage de l'insertion
--
-- Pourquoi aucun marquage dans le Markdown lui-même : des balises ou des
-- commentaires y seraient détruits à la première réécriture manuelle, et
-- pollueraient un contenu que l'utilisateur exporte. La trace vit donc à côté
-- du document, et la réconciliation se fait à l'ouverture, en cherchant
-- content_after dans le contenu courant.
--
-- Pourquoi position_debut n'est pas maintenue : le décalage devient faux à la
-- première frappe en amont du passage. Le maintenir demanderait de suivre
-- chaque édition ; il ne sert donc qu'à départager deux passages identiques
-- dans un même document, pas à localiser le texte.
--
-- Exécution (MySQL 8) :
--     mysql -u <user> -p helpmedraft < database/migration_tracabilite_ia.sql
--
-- Sauvegarde préalable :
--     mysqldump -u root -p helpmedraft > helpmedraft_avant_tracabilite_ia.sql
--
-- Effet sur les données : aucune perte. Les lignes existantes passent à
-- insere = FALSE — ce qui est le constat honnête et non une approximation :
-- pour les interactions antérieures à cette migration, l'information n'a jamais
-- été collectée. Les présenter comme non insérées serait faux ; elles sont
-- simplement hors du périmètre de la trace, et le § 11.4 du dossier le dit.
-- =============================================================================

START TRANSACTION;

-- 1. Les trois colonnes ------------------------------------------------------
ALTER TABLE ia
    ADD COLUMN insere         BOOLEAN  NOT NULL DEFAULT FALSE AFTER created_at,
    ADD COLUMN position_debut INT      NULL                   AFTER insere,
    ADD COLUMN insere_at      DATETIME NULL                   AFTER position_debut;

-- 2. Contrainte de cohérence -------------------------------------------------
--    Une insertion sans horodatage serait une trace inexploitable. La règle est
--    portée par le SGBD et non par l'application, pour qu'une écriture faite
--    hors de l'application — script d'administration, requête directe — ne
--    puisse pas créer l'état incohérent non plus.
--
--    Placée APRÈS l'ajout des colonnes : une contrainte CHECK est vérifiée sur
--    les lignes existantes au moment de sa création, et toutes portent
--    insere = FALSE, qui la satisfait.
ALTER TABLE ia
    ADD CONSTRAINT ck_ia_insertion CHECK (insere = FALSE OR insere_at IS NOT NULL);

COMMIT;

-- =============================================================================
-- Contrôles post-exécution
-- =============================================================================

-- Les trois colonnes sont présentes, avec les bons types et la bonne nullabilité
SELECT column_name, column_type, is_nullable, column_default
  FROM information_schema.columns
 WHERE table_schema = 'helpmedraft'
   AND table_name   = 'ia'
   AND column_name IN ('insere', 'position_debut', 'insere_at')
 ORDER BY ordinal_position;

-- La contrainte est en place
SELECT constraint_name, check_clause
  FROM information_schema.check_constraints
 WHERE constraint_schema = 'helpmedraft'
   AND constraint_name   = 'ck_ia_insertion';

-- Aucune ligne incohérente (doit renvoyer 0)
SELECT COUNT(*) AS lignes_incoherentes
  FROM ia
 WHERE insere = TRUE AND insere_at IS NULL;
