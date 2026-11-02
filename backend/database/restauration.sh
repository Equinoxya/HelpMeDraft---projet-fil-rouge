#!/usr/bin/env bash
# =============================================================================
#  HelpMeDraft — restauration de la base MySQL depuis une archive
#
#  Usage (depuis la racine du dépôt) :
#      ./backend/database/restauration.sh sauvegardes/helpmedraft-20261004-143000.sql.gz
#      BASE=helpmedraft_recette ./backend/database/restauration.sh <archive>
#
#  CETTE OPÉRATION ÉCRASE LA BASE CIBLE. Le script demande donc une
#  confirmation tapée à la main, et affiche la cible avant de la détruire.
#  Pour une exécution automatisée (test de restauration périodique) :
#      CONFIRMER=oui ./backend/database/restauration.sh <archive>
#
#  Le compte utilisé est helpmedraft_migration et non helpmedraft_app : une
#  restauration crée des tables, donc exige des droits de structure que le
#  compte applicatif n'a volontairement pas (voir droits_mysql.sql).
#
#  UNE SAUVEGARDE NON RESTAURÉE N'EST PAS UNE SAUVEGARDE. La procédure complète,
#  dont le test de restauration sur une base jetable, est dans
#  docs/exploitation-base-de-donnees.md.
# =============================================================================

set -euo pipefail

archive="${1:-}"

if [ -z "$archive" ]; then
    echo "Usage : $0 <archive.sql.gz>" >&2
    echo "Archives disponibles :" >&2
    find "${DESTINATION:-./sauvegardes}" -maxdepth 1 -name 'helpmedraft-*.sql.gz' \
        -type f 2>/dev/null | sort >&2 || echo "  (aucune)" >&2
    exit 1
fi

if [ ! -r "$archive" ]; then
    echo "[restauration] ERREUR : « $archive » est absente ou illisible." >&2
    exit 1
fi

BASE="${BASE:-helpmedraft}"
UTILISATEUR="${UTILISATEUR:-helpmedraft_migration}"
HOTE="${HOTE:-127.0.0.1}"
PORT="${PORT:-3306}"
EXEC="${EXEC-docker compose exec -T db}"

: "${MYSQL_MIGRATION_PASSWORD:?MYSQL_MIGRATION_PASSWORD est requis. \
Il est dans le .env à la racine : export \$(grep MYSQL_MIGRATION_PASSWORD .env | xargs)}"

# L'archive est vérifiée AVANT de toucher à la base. Dans l'autre ordre, une
# archive corrompue laisserait une base à moitié écrasée : plus de données
# d'origine, et pas de restauration — le scénario à ne jamais produire.
echo "[restauration] vérification de l'archive…"
if ! gzip -t "$archive" 2>/dev/null; then
    echo "[restauration] ÉCHEC : archive illisible. La base n'a pas été touchée." >&2
    exit 1
fi
if ! gzip -dc "$archive" | tail -5 | grep -q "Dump completed"; then
    echo "[restauration] ÉCHEC : marqueur de fin absent, archive partielle." >&2
    echo "[restauration] La base n'a pas été touchée." >&2
    exit 1
fi
tables="$(gzip -dc "$archive" | grep -c '^CREATE TABLE' || true)"
echo "[restauration] archive valide : ${tables} table(s)."

echo
echo "  ┌──────────────────────────────────────────────────────────────────┐"
echo "  │  LA BASE « ${BASE} » VA ÊTRE ÉCRASÉE.                            "
echo "  │  Toutes ses données actuelles seront définitivement perdues.     │"
echo "  └──────────────────────────────────────────────────────────────────┘"
echo "  source : ${archive}"
echo

if [ "${CONFIRMER:-}" != "oui" ]; then
    # read -r sur /dev/tty et non sur l'entrée standard : le script peut être
    # appelé dans un tube, où stdin n'est pas le clavier et où la lecture
    # renverrait immédiatement une chaîne vide — c'est-à-dire un refus, mais
    # pour la mauvaise raison.
    printf "  Taper « oui » pour confirmer : "
    read -r reponse < /dev/tty || reponse=""
    if [ "$reponse" != "oui" ]; then
        echo "[restauration] annulée. Rien n'a été modifié."
        exit 1
    fi
fi

echo "[restauration] la base « ${BASE} » existe-t-elle ?…"

# AUCUN « DROP DATABASE » ICI, ET C'EST UNE CORRECTION.
#
# La première version du script faisait DROP DATABASE puis CREATE DATABASE dans
# la même instruction, en croyant qu'un dump ne pouvait pas se charger par-dessus
# des tables existantes. Essai fait : c'est faux, et la construction était
# dangereuse.
#
#   • Faux, parce que mysqldump produit un « DROP TABLE IF EXISTS » devant
#     chaque « CREATE TABLE » (--add-drop-table est actif par défaut), et pose
#     FOREIGN_KEY_CHECKS=0 en tête de fichier. Le dump sait donc se substituer
#     aux sept tables, dans n'importe quel ordre, sans aide.
#   • Dangereux, parce que si le CREATE échoue après un DROP réussi, la base est
#     détruite et non restaurée. Le cas s'est produit en essai : une collation
#     refusée par le serveur, et il ne restait rien. Exactement ce que l'ordre
#     des vérifications plus haut cherchait à éviter — annulé par la ligne
#     suivante.
#
# La base est donc seulement créée si elle manque, et le chargement du dump fait
# le reste. Aucun moment où les données d'avant sont parties sans que celles
# d'après soient arrivées.
#
# Contrepartie assumée : une table qui existerait dans la base mais pas dans le
# dump survit. Elle est signalée par le contrôle de fin, plutôt que supprimée en
# silence.
#
# La collation est celle de schema_mysql.sql. Elle est portée par une variable
# parce qu'elle est propre à MySQL 8 : sur un autre serveur de la famille, la
# surcharger plutôt que de modifier le script.
COLLATION="${COLLATION:-utf8mb4_0900_ai_ci}"

$EXEC env MYSQL_PWD="$MYSQL_MIGRATION_PASSWORD" mysql \
    --host="$HOTE" --port="$PORT" --user="$UTILISATEUR" \
    --execute="CREATE DATABASE IF NOT EXISTS \`${BASE}\`
                   CHARACTER SET utf8mb4 COLLATE ${COLLATION};"

echo "[restauration] chargement des données…"
gzip -dc "$archive" \
  | $EXEC env MYSQL_PWD="$MYSQL_MIGRATION_PASSWORD" mysql \
        --host="$HOTE" --port="$PORT" --user="$UTILISATEUR" \
        --default-character-set=utf8mb4 \
        "$BASE"

# Contrôle de bonne fin : compter ce qui est réellement arrivé en base, et pas
# se fier au code de retour de mysql, qui vaut 0 dès que la dernière instruction
# a passé.
#
# table_rows est APPROXIMATIF sur InnoDB — c'est une estimation de l'optimiseur,
# pas un comptage. Suffisant pour voir qu'une table n'est pas vide, inutilisable
# pour affirmer qu'elle est complète. Le vrai contrôle est le test de
# restauration décrit dans docs/exploitation-base-de-donnees.md §6.4.
echo "[restauration] contrôle…"
$EXEC env MYSQL_PWD="$MYSQL_MIGRATION_PASSWORD" mysql \
    --host="$HOTE" --port="$PORT" --user="$UTILISATEUR" --table \
    --execute="SELECT table_name AS 'table', table_rows AS 'lignes (approx.)'
                 FROM information_schema.tables
                WHERE table_schema = '${BASE}'
                ORDER BY table_name;"

# Une table présente en base mais absente du dump n'a pas été écrasée : elle est
# restée telle quelle. Ce n'est pas forcément une erreur (une table de travail,
# une migration en cours), mais c'est à savoir — c'est la contrepartie de ne plus
# détruire la base.
tables_en_base="$($EXEC env MYSQL_PWD="$MYSQL_MIGRATION_PASSWORD" mysql \
    --host="$HOTE" --port="$PORT" --user="$UTILISATEUR" --skip-column-names \
    --execute="SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = '${BASE}';" | tr -d '[:space:]')"
if [ "${tables_en_base:-0}" -gt "$tables" ]; then
    echo "[restauration] ATTENTION : ${tables_en_base} tables en base, ${tables} dans l'archive."
    echo "               Les tables surnuméraires n'ont pas été touchées par la restauration."
fi

echo "[restauration] OK — base « ${BASE} » restaurée depuis ${archive}"
echo "[restauration] Les comptes SGBD ne sont PAS dans le dump : ils vivent dans"
echo "               la base mysql. Sur une instance neuve, rejouer droits_mysql.sql."
