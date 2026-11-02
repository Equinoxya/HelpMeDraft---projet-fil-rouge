"""
Parité entre les deux descriptions du schéma.

POURQUOI CE FICHIER EXISTE — le projet décrit son schéma DEUX fois :

  • database/schema_mysql.sql  → la source de vérité, exécutée par le
    conteneur MySQL au premier démarrage ;
  • database/db.py             → les classes de l'ORM, dont la suite de tests
    se sert pour monter une base SQLite en mémoire.

Deux descriptions concurrentes du même schéma divergent toujours, et c'est
arrivé : pendant plusieurs semaines l'ORM ignorait les cinq contraintes CHECK,
les six index de performance et le `ON DELETE CASCADE` de ia.id_document, et
rien ne le signalait — `create_all()` tournait aussi sur MySQL, créant donc un
schéma sans rien de tout cela à partir des classes. Le dépôt affichait un
script SQL soigné que personne n'exécutait.

CE QUE CE TEST COMPARE, et pourquoi pas plus : les noms de tables, les
colonnes, les longueurs déclarées, les contraintes CHECK, les index, les
contraintes d'unicité et les règles ON DELETE des clés étrangères. Autrement
dit le contrat structurel.

CE QU'IL NE COMPARE PAS : le nom exact des types SQL. schema_mysql.sql écrit
CHAR(36) pour les identifiants, là où l'ORM produit VARCHAR(36) — un choix
délibéré du script (longueur fixe pour un UUID), sans conséquence
fonctionnelle, et que l'ORM n'a plus de raison de reproduire puisqu'il ne crée
plus le schéma MySQL. Le test vérifie donc la FAMILLE du type (texte, entier,
date, booléen) et la longueur, pas son orthographe.
"""

import pathlib
import re

import pytest
from sqlalchemy import Boolean, DateTime, Integer, String, Text

from database.db import Base

SCHEMA_SQL = pathlib.Path(__file__).resolve().parents[2] / "database" / "schema_mysql.sql"


# ── Lecture du script SQL ────────────────────────────────────────────────────

_FAMILLE_SQL = {
    "CHAR": "texte",
    "VARCHAR": "texte",
    "TEXT": "texte",
    "INT": "entier",
    "DATETIME": "date",
    "BOOLEAN": "booleen",
}

_FAMILLE_ORM = {String: "texte", Text: "texte", Integer: "entier", DateTime: "date"}

_RE_CREATE = re.compile(r"CREATE TABLE `?(\w+)`?\s*\(", re.IGNORECASE)
_RE_COLONNE = re.compile(
    # Le \b se place APRÈS le nom du type et AVANT la longueur : placé après
    # le groupe optionnel, il ne peut pas se satisfaire entre « ) » et
    # l'espace qui suit — deux caractères non alphanumériques. L'expression
    # abandonnait alors la longueur et renvoyait None pour chaque colonne.
    r"^\s+`?(\w+)`?\s+(CHAR|VARCHAR|TEXT|INT|DATETIME|BOOLEAN)\b(?:\((\d+)\))?(.*)$",
    re.IGNORECASE,
)
_RE_CHECK = re.compile(r"CONSTRAINT\s+(\w+)\s+CHECK", re.IGNORECASE)
_RE_FK = re.compile(
    r"CONSTRAINT\s+(\w+)\s+FOREIGN KEY\s+\(`?(\w+)`?\)\s*"
    r"REFERENCES\s+`?(\w+)`?\s*\(`?(\w+)`?\)\s*"
    r"(?:ON DELETE\s+(CASCADE|SET NULL|RESTRICT|NO ACTION))?",
    re.IGNORECASE | re.DOTALL,
)
_RE_KEY = re.compile(r"^\s+KEY\s+(\w+)\s+\(([^)]*)\)", re.IGNORECASE)
_RE_UNIQUE = re.compile(r"^\s+UNIQUE KEY\s+(\w+)\s+\(([^)]*)\)", re.IGNORECASE)


def _decouper_en_tables(sql: str) -> dict[str, str]:
    """Rend {nom_de_table: corps du CREATE TABLE}."""
    tables = {}
    for depart in _RE_CREATE.finditer(sql):
        # Les parenthèses sont comptées plutôt que cherchées à l'aveugle : un
        # CHECK (role IN ('user','admin')) en contient, et s'arrêter à la
        # première fermante tronquerait la table à sa première contrainte.
        profondeur = 0
        debut = sql.index("(", depart.start())
        for position in range(debut, len(sql)):
            if sql[position] == "(":
                profondeur += 1
            elif sql[position] == ")":
                profondeur -= 1
                if profondeur == 0:
                    tables[depart.group(1)] = sql[debut + 1 : position]
                    break
    return tables


def _colonnes_sql(corps: str) -> dict[str, tuple[str, int | None, bool]]:
    """Rend {colonne: (famille, longueur, nullable)}."""
    colonnes = {}
    for ligne in corps.splitlines():
        trouve = _RE_COLONNE.match(ligne)
        if not trouve:
            continue
        nom, type_sql, longueur, reste = trouve.groups()
        if nom.upper() in {"PRIMARY", "UNIQUE", "KEY", "CONSTRAINT", "FOREIGN"}:
            continue
        colonnes[nom] = (
            _FAMILLE_SQL[type_sql.upper()],
            int(longueur) if longueur else None,
            "NOT NULL" not in reste.upper(),
        )
    return colonnes


def _lignes_multi(corps: str, motif: re.Pattern) -> dict[str, tuple[str, ...]]:
    """Rend {nom_index: (colonnes...)} pour KEY et UNIQUE KEY."""
    return {
        trouve.group(1): tuple(c.strip().strip("`") for c in trouve.group(2).split(","))
        for ligne in corps.splitlines()
        if (trouve := motif.match(ligne))
    }


SQL_TABLES = _decouper_en_tables(SCHEMA_SQL.read_text(encoding="utf-8"))


# ── Lecture de l'ORM ─────────────────────────────────────────────────────────


def _famille_orm(colonne) -> str:
    for classe, famille in _FAMILLE_ORM.items():
        if isinstance(colonne.type, Boolean):
            return "booleen"
        if isinstance(colonne.type, classe):
            return famille
    raise AssertionError(f"type ORM non cartographié : {colonne.type!r}")


# ── Tests ────────────────────────────────────────────────────────────────────


def test_tu80_les_deux_descriptions_portent_les_memes_tables():
    assert set(Base.metadata.tables) == set(SQL_TABLES)


@pytest.mark.parametrize("nom_table", sorted(Base.metadata.tables))
def test_tu81_memes_colonnes_memes_longueurs_meme_nullabilite(nom_table):
    attendu = _colonnes_sql(SQL_TABLES[nom_table])
    obtenu = {
        colonne.name: (
            _famille_orm(colonne),
            getattr(colonne.type, "length", None),
            colonne.nullable,
        )
        for colonne in Base.metadata.tables[nom_table].columns
    }
    assert obtenu == attendu, (
        f"table « {nom_table} » : l'ORM et schema_mysql.sql ne décrivent pas "
        "les mêmes colonnes. Toute modification de structure se fait aux DEUX "
        "endroits, plus un script de migration."
    )


@pytest.mark.parametrize("nom_table", sorted(Base.metadata.tables))
def test_tu82_memes_contraintes_check(nom_table):
    attendu = set(_RE_CHECK.findall(SQL_TABLES[nom_table]))
    obtenu = {
        contrainte.name
        for contrainte in Base.metadata.tables[nom_table].constraints
        if type(contrainte).__name__ == "CheckConstraint"
    }
    assert obtenu == attendu, (
        f"table « {nom_table} » : contraintes CHECK divergentes. Une règle "
        "présente dans un seul des deux endroits n'est pas appliquée partout — "
        "c'était le cas des cinq CHECK du script, absents de la base réelle."
    )


@pytest.mark.parametrize("nom_table", sorted(Base.metadata.tables))
def test_tu83_memes_index_de_performance(nom_table):
    attendu = _lignes_multi(SQL_TABLES[nom_table], _RE_KEY)
    obtenu = {
        index.name: tuple(colonne.name for colonne in index.columns)
        for index in Base.metadata.tables[nom_table].indexes
        if not index.unique
    }
    assert obtenu == attendu, (
        f"table « {nom_table} » : index divergents. Un index absent ne casse "
        "rien, il rend lent — et c'est précisément ce qui ne se voit pas."
    )


@pytest.mark.parametrize("nom_table", sorted(Base.metadata.tables))
def test_tu84_memes_contraintes_d_unicite(nom_table):
    attendu = _lignes_multi(SQL_TABLES[nom_table], _RE_UNIQUE)
    obtenu = {
        contrainte.name: tuple(colonne.name for colonne in contrainte.columns)
        for contrainte in Base.metadata.tables[nom_table].constraints
        if type(contrainte).__name__ == "UniqueConstraint"
    }
    assert obtenu == attendu


@pytest.mark.parametrize("nom_table", sorted(Base.metadata.tables))
def test_tu85_memes_cles_etrangeres_et_memes_regles_on_delete(nom_table):
    attendu = {
        nom: (colonne, table_cible, colonne_cible, (regle or "NO ACTION").upper())
        for nom, colonne, table_cible, colonne_cible, regle in _RE_FK.findall(SQL_TABLES[nom_table])
    }
    obtenu = {}
    for contrainte in Base.metadata.tables[nom_table].foreign_key_constraints:
        cle = next(iter(contrainte.elements))
        obtenu[contrainte.name] = (
            cle.parent.name,
            cle.column.table.name,
            cle.column.name,
            (contrainte.ondelete or "NO ACTION").upper(),
        )
    assert obtenu == attendu, (
        f"table « {nom_table} » : clés étrangères divergentes. C'est la "
        "divergence la plus coûteuse : il manquait ON DELETE CASCADE sur "
        "ia.id_document, et tout DELETE FROM document exécuté en SQL échouait."
    )
