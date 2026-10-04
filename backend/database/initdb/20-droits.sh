#!/bin/bash
# =============================================================================
#  HelpMeDraft — application des droits SGBD au premier démarrage du conteneur
#
#  POURQUOI UN SCRIPT SHELL et pas seulement un .sql monté dans
#  /docker-entrypoint-initdb.d : un fichier .sql est passé tel quel à MySQL,
#  qui ne sait pas lire les variables d'environnement. Or les mots de passe des
#  trois comptes viennent de l'environnement — les écrire dans un fichier
#  versionné reviendrait à les publier (c'est exactement l'incident déjà
#  survenu sur ce projet avec deux clés commitées).
#
#  Ce script est donc un simple adaptateur : il prend database/droits_mysql.sql,
#  qui reste la SOURCE DE VÉRITÉ et la seule description des droits, y substitue
#  les trois mots de passe, et passe le résultat à MySQL. Rien d'autre.
#
#  Exécuté par l'entrypoint de l'image mysql, au PREMIER démarrage seulement
#  (un volume db-data déjà initialisé ne rejoue aucun fichier de
#  /docker-entrypoint-initdb.d). Les fichiers y sont traités par ordre
#  alphabétique : 10-schema.sql crée les tables, puis 20-droits.sh ferme les
#  droits.
# =============================================================================

set -euo pipefail

SOURCE_SQL=/opt/helpmedraft/droits_mysql.sql

if [ ! -r "$SOURCE_SQL" ]; then
    echo "[droits] ERREUR : $SOURCE_SQL est absent ou illisible." >&2
    echo "[droits] Vérifier le montage du service db dans docker-compose.yml." >&2
    exit 1
fi

# Les trois mots de passe sont EXIGÉS, sans valeur de repli. Un défaut ici
# créerait trois comptes au mot de passe connu de quiconque lit le dépôt, et la
# pile démarrerait sans rien signaler — le pire des deux mondes. On préfère un
# échec bruyant (« fail fast, fail loud », comme app/config.py).
: "${MYSQL_PASSWORD:?[droits] MYSQL_PASSWORD est requis (compte applicatif)}"
: "${MYSQL_BACKUP_PASSWORD:?[droits] MYSQL_BACKUP_PASSWORD est requis (compte de sauvegarde)}"
: "${MYSQL_MIGRATION_PASSWORD:?[droits] MYSQL_MIGRATION_PASSWORD est requis (compte de migration)}"

# Un apostrophe ou un antislash dans un mot de passe terminerait la chaîne SQL
# et casserait le script, voire changerait son sens. Plutôt que d'échapper, on
# refuse : ces deux caractères n'apportent rien à une chaîne tirée au hasard.
for nom in MYSQL_PASSWORD MYSQL_BACKUP_PASSWORD MYSQL_MIGRATION_PASSWORD; do
    valeur="${!nom}"
    case "$valeur" in
        *\'* | *\\*)
            echo "[droits] ERREUR : $nom contient une apostrophe ou un antislash." >&2
            echo "[droits] Générer les mots de passe ainsi :" >&2
            echo "[droits]   python -c \"import secrets; print(secrets.token_urlsafe(32))\"" >&2
            exit 1
            ;;
    esac
done

echo "[droits] Application de $SOURCE_SQL (moindre privilège, 3 comptes)…"

# La substitution se fait dans un tube, jamais dans un fichier temporaire : un
# fichier contiendrait les trois mots de passe en clair sur le disque du
# conteneur, et survivrait à l'échec du script.
#
# L'ordre des expressions compte : le marqueur de l'applicatif est remplacé en
# premier, mais chaque marqueur est distinct, donc aucune substitution n'écrase
# le résultat d'une autre.
sed -e "s|__MDP_APP__|${MYSQL_PASSWORD}|g" \
    -e "s|__MDP_SAUVEGARDE__|${MYSQL_BACKUP_PASSWORD}|g" \
    -e "s|__MDP_MIGRATION__|${MYSQL_MIGRATION_PASSWORD}|g" \
    "$SOURCE_SQL" \
  | mysql --protocol=socket -u root -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE:-helpmedraft}"

echo "[droits] Terminé. Le compte applicatif n'a plus aucun droit de structure."
