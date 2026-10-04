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

# ── Contrôle des trois mots de passe ─────────────────────────────────────────
#
# Deux exigences, vérifiées dans une seule boucle :
#
#   PRÉSENCE — les trois sont EXIGÉS, sans valeur de repli. Un défaut ici
#     créerait trois comptes au mot de passe connu de quiconque lit le dépôt, et
#     la pile démarrerait sans rien signaler : le pire des deux mondes. On
#     préfère un échec bruyant (« fail fast, fail loud », comme app/config.py).
#
#   CONTENU — une apostrophe ou un antislash terminerait la chaîne SQL dans
#     laquelle le mot de passe est inséré, cassant le script voire changeant son
#     sens. Plutôt que d'échapper, on refuse : ces deux caractères n'apportent
#     rien à une chaîne tirée au hasard.
#
# POURQUOI UNE BOUCLE et non trois « : "${VAR:?message}" », qui étaient plus
# courts : ce raccourci produit le motif « MYSQL_PASSWORD:?texte », que le
# détecteur « Generic Password » de GitGuardian lit comme une affectation de
# mot de passe en dur. Trois faux positifs, et une analyse de sécurité en échec
# sur la pull request. Un outil qui crie au loup sur du code sain finit par
# n'être plus lu : mieux vaut écrire le contrôle d'une façon qui ne lui donne
# rien à mordre. La boucle a l'avantage accessoire de ne plus énumérer les trois
# variables deux fois.
for nom in MYSQL_PASSWORD MYSQL_BACKUP_PASSWORD MYSQL_MIGRATION_PASSWORD; do
    case "$nom" in
        MYSQL_PASSWORD) usage="compte applicatif" ;;
        MYSQL_BACKUP_PASSWORD) usage="compte de sauvegarde" ;;
        MYSQL_MIGRATION_PASSWORD) usage="compte de migration" ;;
    esac

    # ${!nom-} et non ${!nom} : « set -u » est actif, et une indirection vers
    # une variable non définie interromprait le script sur « unbound variable »
    # au lieu du message explicite voulu juste en dessous.
    valeur="${!nom-}"

    if [ -z "$valeur" ]; then
        echo "[droits] ERREUR : $nom est requis ($usage)." >&2
        echo "[droits] Les quatre mots de passe de la pile sont décrits dans .env.example." >&2
        exit 1
    fi

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
