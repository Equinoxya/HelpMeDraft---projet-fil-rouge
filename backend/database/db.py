from __future__ import annotations

import os
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from utilitaires import utc_now_naive

# Chemin ABSOLU, calculé depuis l'emplacement de ce module et non depuis le
# répertoire courant. Avec `Path("HelpMeDraft.db")`, lancer `python run.py`
# depuis backend/ et `python backend/run.py` depuis la racine ouvraient DEUX
# bases différentes : les comptes créés d'un côté étaient introuvables de
# l'autre, sans que rien ne le signale.
DB_PATH = Path(__file__).resolve().parents[1] / "HelpMeDraft.db"

# L'URL de connexion est configurable par l'environnement, avec le fichier
# SQLite local pour valeur par défaut : lancer l'application sans variable
# d'environnement se comporte exactement comme avant.
#   - tests        : HELPMEDRAFT_DB_URL=sqlite://            (base en mémoire)
#   - conteneur    : HELPMEDRAFT_DB_URL=mysql+pymysql://...  (KAN-86, KAN-15)
# Sans ce point de configuration, le moteur serait lié au fichier dès l'import
# du module : aucun test ne pourrait viser une autre base sans contourner
# l'application elle-même.
DB_URL = os.getenv("HELPMEDRAFT_DB_URL", f"sqlite:///{DB_PATH}")
engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)
# pool_pre_ping : MySQL ferme une connexion inactive au bout de wait_timeout
# (8 h par défaut). Le pool de SQLAlchemy la garde pourtant et la ressort telle
# quelle à la requête suivante, qui échoue avec « MySQL server has gone away ».
# Le ping valide la connexion avant de la prêter, et la remplace si elle est
# morte. Sans effet mesurable sur SQLite, qui n'a pas de connexion réseau.


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    # SQLite n'applique PAS les contraintes de clé étrangère par défaut
    # (contrairement à MySQL/InnoDB, cible de la migration prod KAN-86).
    # Sans ce PRAGMA, le ondelete="SET NULL" déclaré sur
    # Document.id_dossier ne serait jamais exécuté par SQLite : supprimer
    # un dossier laisserait des documents avec un id_dossier pointant vers
    # une ligne inexistante au lieu de repasser proprement à NULL.
    if engine.dialect.name != "sqlite":
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


# ── Modèles ──────────────────────────────────────────────────────────────────
#
# LES CONTRAINTES ET LES INDEX DÉCLARÉS ICI SONT LE MIROIR EXACT DE
# database/schema_mysql.sql, noms compris. Ce n'est pas de la redondance
# décorative : les deux descriptions du même schéma avaient divergé, et la
# divergence ne se voyait nulle part.
#
# Ce qui s'était passé : `Base.metadata.create_all()` tournait sur MySQL comme
# sur SQLite, et créait donc le schéma à partir de ces classes — pas à partir
# de schema_mysql.sql, qui n'était jamais exécuté. Les cinq contraintes CHECK,
# les six index de performance et les clés étrangères nommées du script SQL
# étaient absents de la base réelle, alors que le dépôt affichait un script
# soigné. Le `ON DELETE CASCADE` manquant sur ia.id_document faisait en plus
# échouer tout `DELETE FROM document` exécuté en SQL.
#
# RÈGLE À TENIR : toute modification de structure se fait aux DEUX endroits,
# plus un script de migration. Le test tests/unit/test_schema_parite.py
# compare les deux et échoue si l'un des deux a bougé seul.


class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
        CheckConstraint("role IN ('user','admin')", name="ck_user_role"),
        # Borne basse à 1 et non 0, alignée sur MIN_QUOTA de
        # app/routes/admin_route.py (KAN-98).
        CheckConstraint("quota_daily_limit BETWEEN 1 AND 1000", name="ck_user_quota"),
    )

    user_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    lastname: Mapped[str] = mapped_column(String(50), nullable=False)
    firstname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(326), nullable=False)
    mdp_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user"
    )  # ex: 'user', 'admin'

    # Quotas & Usage IA
    quota_daily_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive
    )

    password_resets: Mapped[list[PasswordReset]] = relationship(
        "PasswordReset", back_populates="user", cascade="all, delete-orphan"
    )
    dossiers: Mapped[list[Dossier]] = relationship(
        "Dossier", back_populates="user", cascade="all, delete-orphan"
    )
    documents: Mapped[list[Document]] = relationship(
        "Document", back_populates="user", cascade="all, delete-orphan"
    )
    consentements: Mapped[list[Consentement]] = relationship(
        "Consentement", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    ias: Mapped[list[IA]] = relationship("IA", back_populates="user", cascade="all, delete-orphan")


class PasswordReset(Base):
    __tablename__ = "password_reset"
    __table_args__ = (
        Index("ix_reset_user", "user_id"),
        Index("ix_reset_expires", "expires_at"),  # purge des demandes expirées
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_reset_user"),
        nullable=False,
    )
    # VARCHAR(128) et non 512 : l'empreinte stockée est un SHA-256 en
    # hexadécimal, soit 64 caractères. 512 était un reste qui faisait diverger
    # l'ORM de schema_mysql.sql, où la colonne vaut 128.
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)

    user: Mapped[User] = relationship("User", back_populates="password_resets")


class UserSession(Base):
    __tablename__ = "user_session"
    __table_args__ = (
        UniqueConstraint("refresh_token_hash", name="uq_session_token"),
        Index("ix_session_user", "user_id"),
    )

    id_session: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    # SÉCURITÉ : on ne stocke JAMAIS le refresh token lui-même, seulement son
    # empreinte SHA-256 (64 caractères hexadécimaux). Une fuite de la base ne
    # permet donc pas de rejouer une session active. Même principe que
    # password_reset.token_hash. VARCHAR(128) pour rester aligné sur
    # schema_mysql.sql et migration_durcissement.sql.
    refresh_token_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_token_exp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoke: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_session_user"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="sessions")


class Dossier(Base):
    __tablename__ = "dossier"
    __table_args__ = (Index("ix_dossier_user", "user_id"),)

    id_dossier: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_dossier_user"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="dossiers")
    documents: Mapped[list[Document]] = relationship("Document", back_populates="dossier")


class Document(Base):
    __tablename__ = "document"
    __table_args__ = (
        Index("ix_document_user_updated", "user_id", "updated_at"),  # liste paginée triée
        Index("ix_document_dossier", "id_dossier"),  # filtrage par dossier
        CheckConstraint("status IN ('brouillon','a_relire','termine')", name="ck_document_status"),
        CheckConstraint("format IN ('markdown','wysiwyg')", name="ck_document_format"),
    )

    id_document: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    titre: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    format: Mapped[str] = mapped_column(
        String(20), nullable=False, default="markdown"
    )  # ex: 'markdown', 'wysiwyg'
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="brouillon"
    )  # 'brouillon', 'a_relire', 'termine'
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive
    )

    id_dossier: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("dossier.id_dossier", ondelete="SET NULL", name="fk_document_dossier"),
        nullable=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_document_user"),
        nullable=False,
    )

    dossier: Mapped[Dossier | None] = relationship("Dossier", back_populates="documents")
    user: Mapped[User] = relationship("User", back_populates="documents")
    ias: Mapped[list[IA]] = relationship(
        "IA", back_populates="document", cascade="all, delete-orphan"
    )


class Consentement(Base):
    __tablename__ = "consentement"
    __table_args__ = (Index("ix_consentement_user", "user_id"),)

    id_consentement: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    type_consentement: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ex: 'traitement_ia_local'
    accepte: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_consentement: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utc_now_naive
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_consentement_user"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="consentements")


class IA(Base):
    __tablename__ = "ia"
    __table_args__ = (
        Index("ix_ia_user_created", "user_id", "created_at"),  # quota 24 h
        Index("ix_ia_document_created", "id_document", "created_at"),  # historique du document
        CheckConstraint(
            "type_action IN ('reformuler','corriger','completer')", name="ck_ia_action"
        ),
        # Une insertion sans horodatage serait une trace inexploitable au regard
        # de l'AI Act. La contrainte est portée par le SGBD plutôt que par
        # l'application : une écriture faite hors de l'application — script
        # d'administration, requête directe — ne peut pas créer l'état
        # incohérent non plus.
        CheckConstraint("insere = 0 OR insere_at IS NOT NULL", name="ck_ia_insertion"),
    )

    id_ia: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_uuid)
    type_action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ex: 'reformuler', 'corriger', 'completer'
    content_before: Mapped[str] = mapped_column(Text, nullable=True)
    content_after: Mapped[str] = mapped_column(Text, nullable=True)
    tokens_used: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )  # Utile pour les métriques de back-office !
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)

    # ── Traçabilité des contenus générés (AI Act, art. 50) ───────────────────
    #
    # Le règlement demande que les contenus générés par IA soient identifiables.
    # Une ligne de cette table atteste qu'une proposition a été PRODUITE ; ces
    # trois colonnes attestent qu'elle a été ACCEPTÉE et versée au document.
    # La distinction compte : une proposition rejetée n'est pas un contenu
    # généré présent dans le document de l'utilisateur.
    #
    # On ne stocke PAS de marquage dans le Markdown lui-même. Des balises ou des
    # commentaires y seraient détruits à la première réécriture manuelle, et
    # pollueraient un contenu que l'utilisateur exporte. La trace vit donc à
    # côté du document, et la réconciliation se fait à l'ouverture
    # (voir DocumentEditorView.vue) : on cherche content_after dans le contenu
    # courant. Si le passage y est, il vient d'une génération ; s'il n'y est
    # plus, il a été réécrit depuis. C'est la seule question à laquelle
    # l'obligation demande de répondre, et elle ne nécessite aucun suivi
    # continu des décalages — lesquels deviendraient faux à la première frappe
    # en amont du passage.
    insere: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Décalage au MOMENT de l'insertion. Volontairement non maintenu ensuite :
    # il ne sert qu'à départager deux passages identiques dans un même
    # document, pas à localiser le texte.
    position_debut: Mapped[int | None] = mapped_column(Integer, nullable=True)
    insere_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", name="fk_ia_user"),
        nullable=False,
    )
    # ondelete="CASCADE" : il manquait, et ce n'était pas qu'une divergence de
    # documentation. Sans lui, la clé étrangère est créée en NO ACTION, et
    # `DELETE FROM document WHERE ...` échoue avec « FOREIGN KEY constraint
    # failed » dès que le document a un appel IA à son historique. Seule la
    # suppression passant par l'ORM fonctionnait, grâce au
    # cascade="all, delete-orphan" déclaré sur Document.ias — un filet côté
    # Python qui masquait l'absence de la règle côté base.
    id_document: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("document.id_document", ondelete="CASCADE", name="fk_ia_document"),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="ias")
    document: Mapped[Document] = relationship("Document", back_populates="ias")


# ── Mise à disposition du schéma ─────────────────────────────────────────────

TABLES_ATTENDUES = frozenset(Base.metadata.tables)


def _verifier_schema_mysql() -> None:
    """
    Vérifie que les sept tables existent, et échoue avec la marche à suivre.

    Sur MySQL, le schéma n'est PAS créé par l'application : il vient de
    database/schema_mysql.sql, que le conteneur `db` exécute au premier
    démarrage (voir docker-compose.yml). Sans ce contrôle, une base vide
    laisserait démarrer l'application, et la première requête échouerait par un
    « Table 'helpmedraft.user' doesn't exist » au fond d'une trace HTTP 500 —
    message vrai mais qui ne dit pas quoi faire.
    """
    manquantes = sorted(TABLES_ATTENDUES - set(inspect(engine).get_table_names()))
    if not manquantes:
        return
    raise RuntimeError(
        "Le schéma de la base MySQL est incomplet : "
        f"{len(manquantes)} table(s) absente(s) ({', '.join(manquantes)}).\n"
        "L'application ne crée PAS le schéma sur MySQL — il est la propriété de "
        "database/schema_mysql.sql, et le compte applicatif n'a volontairement "
        "aucun droit de création de table.\n"
        "Pour y remédier :\n"
        "  • en conteneur : le script est exécuté au PREMIER démarrage du "
        "service db. Un volume déjà initialisé ne le rejoue pas — "
        "`docker compose down -v` puis `docker compose up --build`.\n"
        "  • à la main    : mysql -u root -p < database/schema_mysql.sql"
    )


# SQLite (développement, tests) : l'application crée son schéma elle-même, à
# partir des classes ci-dessus. C'est ce qui permet à la suite de tests de
# travailler sur une base en mémoire, montée et démontée à chaque test.
#
# MySQL (conteneur, production) : elle ne le crée PAS. Deux descriptions
# concurrentes du même schéma, celle-ci et schema_mysql.sql, ne peuvent pas
# faire autorité toutes les deux — et c'est create_all() qui gagnait
# silencieusement, en produisant un schéma sans aucune contrainte CHECK ni
# index de performance. Le script SQL est désormais la source de vérité, et
# l'ORM n'en est que le reflet, vérifié par test_schema_parite.py.
if engine.dialect.name == "sqlite":
    Base.metadata.create_all(engine)
else:
    _verifier_schema_mysql()
