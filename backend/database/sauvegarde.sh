#!/usr/bin/env bash
# =============================================================================
#  HelpMeDraft — sauvegarde de la base MySQL
#
#  Produit une archive compressée, horodatée et VÉRIFIÉE dans le répertoire de
#  destination, et purge les archives au-delà de la durée de rétention.
#
#  Usage (depuis la racine du dépôt) :
#      ./backend/database/sauvegarde.sh
#      DESTINATION=/mnt/sauvegardes RETENTION_JOURS=30 ./backend/database/sauvegarde.sh
#
#  La base n'est PAS publiée sur l'hôte (le service db de docker-compose.yml n'a
#  pas de section ports : l'exposer sans raison serait une surface d'attaque de
#  plus). Les commandes passent donc par le conteneur. Pour une base hors
#  conteneur, surcharger EXEC :
#      EXEC="" HOTE=db.exemple.fr ./backend/database/sauvegarde.sh
#
#  Le compte utilisé est helpmedraft_sauvegarde, qui n'a que SELECT, LOCK
#  TABLES, SHOW VIEW et TRIGGER (voir droits_mysql.sql). Un script de
#  sauvegarde n'a aucune raison de pouvoir écrire dans la base qu'il sauvegarde :
#  s'il se trompe de sens, MySQL refuse.
# =============================================================================

set -euo pipefail

BASE="${BASE:-helpmedraft}"
UTILISATEUR="${UTILISATEUR:-helpmedraft_sauvegarde}"
DESTINATION="${DESTINATION:-./sauvegardes}"
RETENTION_JOURS="${RETENTION_JOURS:-14}"
HOTE="${HOTE:-127.0.0.1}"
PORT="${PORT:-3306}"
EXEC="${EXEC-docker compose exec -T db}"

: "${MYSQL_BACKUP_PASSWORD:?MYSQL_BACKUP_PASSWORD est requis. \
Il est dans le .env à la racine : export \$(grep MYSQL_BACKUP_PASSWORD .env | xargs)}"

horodatage="$(date +%Y%m%d-%H%M%S)"
archive="${DESTINATION}/helpmedraft-${horodatage}.sql.gz"

mkdir -p "$DESTINATION"

# L'horodatage est à la seconde : deux lancements dans la même seconde
# viseraient le même nom. Le second écraserait la première archive, et s'il
# échouait ensuite, le nettoyage supprimerait une sauvegarde valide — une perte
# causée par le garde-fou lui-même. On refuse plutôt que d'écraser.
if [ -e "$archive" ]; then
    echo "[sauvegarde] ERREUR : ${archive} existe déjà." >&2
    echo "[sauvegarde] Attendre une seconde et relancer." >&2
    exit 1
fi

echo "[sauvegarde] base « ${BASE} » -> ${archive}"

# Les options ne sont pas décoratives, chacune corrige un défaut du dump par
# défaut :
#
#   --single-transaction  prend un instantané cohérent SANS verrouiller les
#                         tables (InnoDB). Sans elle, mysqldump pose un verrou
#                         global : l'application se bloque pendant toute la
#                         durée de la sauvegarde.
#   --routines
#   --triggers            le schéma ne s'arrête pas aux tables. Les oublier
#                         produit une sauvegarde qui restaure des données dans
#                         une base amputée, et ça ne se voit qu'à la
#                         restauration.
#   --default-character-set=utf8mb4
#                         la base est en utf8mb4. Sans cette option, les
#                         accents et les emojis reviennent en « ?? » — une perte
#                         SILENCIEUSE, que seule une relecture du contenu
#                         révèle.
#   --no-tablespaces      évite d'exiger le privilège PROCESS, que le compte de
#                         sauvegarde n'a volontairement pas.
#   --set-gtid-purged=OFF n'inscrit pas d'état de réplication dans le dump : il
#                         empêcherait de restaurer sur une autre instance.
#
# Le mot de passe passe par MYSQL_PWD et non par -p : un mot de passe en
# argument est visible de tout le système dans la liste des processus (ps aux).
#
# Le préfixe « env MYSQL_PWD=… » est posé à l'INTÉRIEUR de $EXEC, et pas devant :
# en mode conteneur, une variable exportée sur l'hôte n'atteint pas le processus
# lancé dans le conteneur. Cette forme marche dans les deux modes, EXEC vide
# compris.
if ! $EXEC env MYSQL_PWD="$MYSQL_BACKUP_PASSWORD" mysqldump \
        --host="$HOTE" \
        --port="$PORT" \
        --user="$UTILISATEUR" \
        --single-transaction \
        --routines \
        --triggers \
        --default-character-set=utf8mb4 \
        --no-tablespaces \
        --set-gtid-purged=OFF \
        "$BASE" \
     | gzip -9 > "$archive"
then
    echo "[sauvegarde] ÉCHEC du dump. Archive incomplète supprimée." >&2
    rm -f "$archive"
    exit 1
fi

# TROIS CONTRÔLES, parce qu'une sauvegarde non vérifiée n'est pas une
# sauvegarde. Les trois échecs ci-dessous produisent tous un fichier d'allure
# normale, et ne se découvrent qu'au moment où on en a besoin.

# 1) L'archive est lisible de bout en bout. Un dump coupé en cours d'écriture
#    (disque plein, conteneur arrêté) donne un .gz tronqué.
if ! gzip -t "$archive" 2>/dev/null; then
    echo "[sauvegarde] ÉCHEC : archive illisible (gzip -t). Supprimée." >&2
    rm -f "$archive"
    exit 1
fi

# 2) mysqldump écrit « -- Dump completed on … » en DERNIÈRE ligne, et seulement
#    s'il est allé au bout. C'est le seul témoin fiable de complétude : le code
#    de retour, lui, est celui de gzip à cause du tube.
if ! gzip -dc "$archive" | tail -5 | grep -q "Dump completed"; then
    echo "[sauvegarde] ÉCHEC : marqueur de fin absent, le dump est partiel." >&2
    echo "[sauvegarde] Archive supprimée pour ne pas laisser croire à une sauvegarde valide." >&2
    rm -f "$archive"
    exit 1
fi

# 3) Les sept tables sont présentes. Une erreur de droits en cours de dump peut
#    n'en sauvegarder qu'une partie sans interrompre le reste.
tables_trouvees="$(gzip -dc "$archive" | grep -c '^CREATE TABLE' || true)"
if [ "$tables_trouvees" -lt 7 ]; then
    echo "[sauvegarde] ÉCHEC : ${tables_trouvees} table(s) dans l'archive, 7 attendues." >&2
    rm -f "$archive"
    exit 1
fi

taille="$(du -h "$archive" | cut -f1)"
echo "[sauvegarde] OK — ${archive} (${taille}, ${tables_trouvees} tables)"

# Rétention : les archives plus vieilles que RETENTION_JOURS sont supprimées.
# Sans purge, le disque se remplit et c'est la sauvegarde SUIVANTE qui échoue —
# au pire moment, puisque le disque plein est souvent déjà le symptôme.
supprimees="$(find "$DESTINATION" -maxdepth 1 -name 'helpmedraft-*.sql.gz' \
                -type f -mtime "+${RETENTION_JOURS}" -print -delete | wc -l)"
echo "[sauvegarde] rétention ${RETENTION_JOURS} j : ${supprimees} archive(s) purgée(s)," \
     "$(find "$DESTINATION" -maxdepth 1 -name 'helpmedraft-*.sql.gz' -type f | wc -l) conservée(s)"
