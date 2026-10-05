"""
Tests du script d'attribution du rôle administrateur (database/promouvoir.py).

Ce script est le SEUL moyen de désigner le premier administrateur d'une base
neuve : le back-office sait changer un rôle, mais il faut déjà être
administrateur pour y entrer. Un défaut ici laisse une installation sans aucune
porte d'entrée, ou — pire — ouvre le back-office à un compte qu'on n'a pas visé.

Les codes de retour sont vérifiés autant que les effets en base : le script est
appelé en ligne de commande, parfois dans un script de déploiement, où le code
de retour est tout ce qui est lu.
"""

from sqlalchemy import select

from database.db import SessionLocal, User
from database.promouvoir import lister, promouvoir


def _role(email: str) -> str:
    with SessionLocal() as session:
        return session.execute(select(User.role).where(User.email == email)).scalar_one()


def test_tu_promo01_promeut_un_compte_existant(utilisateur):
    assert _role("camille@exemple.fr") == "user"

    code = promouvoir("camille@exemple.fr", "admin", forcer=False)

    assert code == 0
    assert _role("camille@exemple.fr") == "admin"


def test_tu_promo02_email_inconnu_echoue_sans_rien_changer(utilisateur):
    """Une promotion qui ne promeut rien est pire qu'une erreur : on croit l'avoir faite."""
    code = promouvoir("camile@exemple.fr", "admin", forcer=False)

    assert code == 1
    assert _role("camille@exemple.fr") == "user"


def test_tu_promo03_relance_idempotente(administrateur):
    """Relancer sur un compte déjà administrateur ne doit pas être une erreur."""
    code = promouvoir("admin@exemple.fr", "admin", forcer=False)

    assert code == 0
    assert _role("admin@exemple.fr") == "admin"


def test_tu_promo04_retrograde_quand_il_reste_un_autre_administrateur(
    administrateur, creer_utilisateur
):
    creer_utilisateur("seconde.admin@exemple.fr", role="admin")

    code = promouvoir("admin@exemple.fr", "user", forcer=False)

    assert code == 0
    assert _role("admin@exemple.fr") == "user"
    assert _role("seconde.admin@exemple.fr") == "admin"


def test_tu_promo05_refuse_de_retirer_le_dernier_administrateur(administrateur):
    """Sans ce garde-fou, le back-office devient inaccessible à tout le monde."""
    code = promouvoir("admin@exemple.fr", "user", forcer=False)

    assert code == 1
    assert _role("admin@exemple.fr") == "admin"


def test_tu_promo06_forcer_lève_le_garde_fou(administrateur):
    """Le refus doit rester contournable : sinon, impossible de vider une base de test."""
    code = promouvoir("admin@exemple.fr", "user", forcer=True)

    assert code == 0
    assert _role("admin@exemple.fr") == "user"


def test_tu_promo07_lister_ne_modifie_rien(administrateur, utilisateur, capsys):
    code = lister()

    assert code == 0
    sortie = capsys.readouterr().out
    assert "admin@exemple.fr" in sortie
    assert "camille@exemple.fr" not in sortie, "un compte sans le rôle ne doit pas être listé"
    assert _role("admin@exemple.fr") == "admin"
    assert _role("camille@exemple.fr") == "user"


def test_tu_promo08_lister_signale_une_base_sans_administrateur(utilisateur, capsys):
    """Le cas d'une installation neuve : le message doit dire quoi faire."""
    assert lister() == 0

    sortie = capsys.readouterr().out
    assert "aucun" in sortie.lower()
    assert "promouvoir.py" in sortie
