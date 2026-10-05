"""
HelpMeDraft — attribuer ou retirer le rôle administrateur à un compte.

POURQUOI CE SCRIPT EXISTE
-------------------------
Le back-office sait déjà changer le rôle d'un compte (`PATCH /admin/users/<id>`),
mais il faut être administrateur pour y entrer. Sur une base neuve, personne ne
l'est : le premier administrateur ne peut donc venir que de l'extérieur de
l'application. Jusqu'ici, la seule marche à suivre était « modifier le champ
`role` à la main dans la base », ce que le README disait en une ligne. Un UPDATE
tapé à la main sur une base réelle est exactement le genre d'opération qui part
de travers : faute de frappe dans l'email, WHERE oublié, et tous les comptes
deviennent administrateurs sans que rien ne le signale.

EXÉCUTION (depuis backend/) :

    python database/promouvoir.py ophelie@exemple.fr
    python database/promouvoir.py ophelie@exemple.fr --role user     # rétrograder
    python database/promouvoir.py --lister                           # qui est admin ?

Sur la pile conteneurisée, la base n'est pas publiée sur l'hôte : il faut passer
par le conteneur, et avec le compte APPLICATIF, qui a le droit d'UPDATE sans
aucun droit de structure.

    set -a && . ./.env && set +a
    URL="mysql+pymysql://helpmedraft_app"
    URL="$URL:$MYSQL_PASSWORD@db:3306/helpmedraft"
    docker compose run --rm --no-deps -e HELPMEDRAFT_DB_URL="$URL" \
        backend python database/promouvoir.py ophelie@exemple.fr

GARDE-FOUS, et ils ne sont pas décoratifs :

  • le compte doit EXISTER. Un email inconnu fait échouer le script avec la
    liste des comptes proches, au lieu de ne rien faire en silence — une
    promotion qui ne promeut rien est pire qu'une erreur, on croit l'avoir
    faite ;
  • un seul compte à la fois, désigné par son email exact. Pas de motif, pas
    de `--tous` ;
  • retirer le dernier rôle administrateur est REFUSÉ sans --forcer : plus
    aucun administrateur, c'est le back-office inaccessible et ce script à
    relancer pour en sortir ;
  • le rôle est vérifié contre les deux mêmes valeurs que l'API et que la
    contrainte `ck_user_role` de la base. Les trois endroits doivent dire la
    même chose, sans quoi la base refuserait ce que le script accepte.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

# Le script est lancé depuis backend/ (« python database/promouvoir.py »), donc
# son répertoire — database/ — est en tête du chemin d'import, et non backend/.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select  # noqa: E402

from database.db import SessionLocal, User  # noqa: E402

# Mêmes valeurs que ALLOWED_ROLES de app/routes/admin_route.py et que la
# contrainte ck_user_role de la base.
ROLES = ("user", "admin")


def lister() -> int:
    """Affiche qui est administrateur. Sans rien modifier."""
    with SessionLocal() as session:
        admins = session.execute(
            select(User.email, User.firstname, User.lastname)
            .where(User.role == "admin")
            .order_by(User.email)
        ).all()
        total = session.execute(select(func.count()).select_from(User)).scalar_one()

    print(f"{total} compte(s) en base, dont {len(admins)} administrateur(s) :")
    for email, prenom, nom in admins:
        print(f"  • {email}  ({prenom} {nom})")
    if not admins:
        print("  (aucun — le back-office est donc inaccessible)")
        print("\n  Pour en désigner un :")
        print("      python database/promouvoir.py <email>")
    return 0


def promouvoir(email: str, role: str, forcer: bool) -> int:
    with SessionLocal() as session:
        compte = session.execute(select(User).where(User.email == email)).scalar_one_or_none()

        if compte is None:
            print(f"ÉCHEC : aucun compte avec l'email « {email} ».", file=sys.stderr)
            # L'email est le plus souvent mal tapé, pas inexistant : on aide à
            # trouver le bon plutôt que de laisser chercher.
            debut = email.split("@")[0][:3]
            proches = (
                session.execute(select(User.email).where(User.email.like(f"%{debut}%")).limit(5))
                .scalars()
                .all()
            )
            if proches:
                print("Comptes dont l'email ressemble :", file=sys.stderr)
                for autre in proches:
                    print(f"  • {autre}", file=sys.stderr)
            else:
                print(
                    "Aucun email approchant. « --lister » affiche les administrateurs existants.",
                    file=sys.stderr,
                )
            return 1

        if compte.role == role:
            print(f"Rien à faire : {email} a déjà le rôle « {role} ».")
            return 0

        # Retirer le dernier administrateur ferme le back-office à tout le monde.
        if compte.role == "admin" and role != "admin" and not forcer:
            restants = session.execute(
                select(func.count()).select_from(User).where(User.role == "admin")
            ).scalar_one()
            if restants <= 1:
                print(
                    f"REFUSÉ : {email} est le dernier administrateur. Le rétrograder "
                    "rendrait le back-office inaccessible, et il faudrait relancer ce "
                    "script pour en sortir.\n"
                    "Désigner d'abord un autre administrateur, ou passer --forcer en "
                    "connaissance de cause.",
                    file=sys.stderr,
                )
                return 1

        ancien = compte.role
        compte.role = role
        session.commit()

    print(f"{email} : « {ancien} » → « {role} ».")
    if role == "admin":
        print(
            "Se reconnecter pour que le changement prenne effet : le rôle est relu en "
            "base à chaque appel, mais l'interface ne révèle le menu Administration "
            "qu'au chargement du profil."
        )
    return 0


if __name__ == "__main__":
    analyseur = argparse.ArgumentParser(
        description="Attribue ou retire le rôle administrateur à un compte de "
        "HelpMeDraft, dans la base désignée par HELPMEDRAFT_DB_URL.",
    )
    analyseur.add_argument("email", nargs="?", help="Email exact du compte à modifier.")
    analyseur.add_argument(
        "--role",
        choices=ROLES,
        default="admin",
        help="Rôle à attribuer (défaut : admin).",
    )
    analyseur.add_argument(
        "--lister",
        action="store_true",
        help="Affiche les administrateurs existants, sans rien modifier.",
    )
    analyseur.add_argument(
        "--forcer",
        action="store_true",
        help="Autorise le retrait du DERNIER rôle administrateur.",
    )
    arguments = analyseur.parse_args()

    if arguments.lister:
        sys.exit(lister())
    if not arguments.email:
        analyseur.error("l'email du compte est requis, ou bien --lister.")
    sys.exit(promouvoir(arguments.email, arguments.role, arguments.forcer))
