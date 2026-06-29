from __future__ import annotations
from pathlib import Path
from datetime import datetime
import uuid
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text, Table, create_engine, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
)

DB_PATH = Path("db.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass

# ── Modèles ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "user"

    user_id:    Mapped[str]      = mapped_column(String(50),  primary_key=True, default=gen_uuid)
    lastname:   Mapped[str]      = mapped_column(String(50),  nullable=False)
    firstname:  Mapped[str]      = mapped_column(String(50),  nullable=False)
    email:      Mapped[str]      = mapped_column(String(326), nullable=False, unique=True)
    mdp_hash:   Mapped[str]      = mapped_column(String(255), nullable=False)
    role:       Mapped[str]      = mapped_column(String(50),  nullable=False)
    token_ia:   Mapped[int]      = mapped_column(Integer,     nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime,    nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime,    nullable=False, server_default=func.now(), onupdate=func.now())

    token_resets:  Mapped[list[TokenReset]]   = relationship("TokenReset",   back_populates="user")
    dossiers:      Mapped[list[Dossier]]      = relationship("Dossier",      back_populates="user")
    documents:     Mapped[list[Document]]     = relationship("Document",     back_populates="user")
    consentements: Mapped[list[Consentement]] = relationship("Consentement", back_populates="user")
    sessions:      Mapped[list[UserSession]]  = relationship("UserSession",  back_populates="users")
    ias:           Mapped[list[IA]]           = relationship("IA",           back_populates="users")


class TokenReset(Base):
    __tablename__ = "token_reset"

    id:        Mapped[str]      = mapped_column(String(50), primary_key=True, default=gen_uuid)
    token:     Mapped[str]      = mapped_column(String(100), nullable=False, unique=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime,   nullable=False)
    use:       Mapped[bool]     = mapped_column(Boolean,    nullable=False, default=False)
    user_id:   Mapped[str]      = mapped_column(ForeignKey("user.user_id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="token_resets")


class UserSession(Base):
    __tablename__ = "usersession"

    id_session: Mapped[str]      = mapped_column(String(50),  primary_key=True, default=gen_uuid)
    refresh_token:  Mapped[str]      = mapped_column(String(2048), nullable=False, unique = True)
    refresh_token_exp: Mapped[datetime] = mapped_column(DateTime,   nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,    nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime,    nullable=False, server_default=func.now(), onupdate=func.now())

    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'))
    user: Mapped[User] = relationship("User", back_populates='usersessions')
    users: Mapped[list[User]] = relationship("User", back_populates="usersessions")


class Dossier(Base):
    __tablename__ = "dossier"

    id_dossier: Mapped[str | None]      = mapped_column(String(50), primary_key=True, default=gen_uuid)
    name:       Mapped[str]      = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,   nullable=False, server_default=func.now())
    user_id:    Mapped[str]      = mapped_column(ForeignKey("user.user_id"), nullable=False)

    user:      Mapped[User]           = relationship("User",     back_populates="dossiers")
    documents: Mapped[list[Document]] = relationship("Document", back_populates="dossier")


class Document(Base):
    __tablename__ = "document"

    id_document: Mapped[str]      = mapped_column(String(50), primary_key=True, default=gen_uuid)
    titre:       Mapped[str]      = mapped_column(String(50), nullable=False)
    content:     Mapped[str]      = mapped_column(Text)
    format:      Mapped[str]      = mapped_column(String(50))
    created_at:  Mapped[datetime] = mapped_column(DateTime,   nullable=False, server_default=func.now())
    updated_at:  Mapped[datetime] = mapped_column(DateTime,   nullable=False, server_default=func.now(), onupdate=func.now())
    id_dossier:  Mapped[str]      = mapped_column(ForeignKey("dossier.id_dossier"), nullable=False)
    user_id:     Mapped[str]      = mapped_column(ForeignKey("user.user_id"),       nullable=False)

    dossier: Mapped[Dossier] = relationship("Dossier", back_populates="documents")
    user:    Mapped[User]    = relationship("User",    back_populates="documents")
    ias:     Mapped[list[IA]] = relationship("IA",     back_populates="documents")


class Consentement(Base):
    __tablename__ = "consentement"

    id_consentement:   Mapped[str]      = mapped_column(String(50), primary_key=True, default=gen_uuid)
    type_consentement: Mapped[str]      = mapped_column(String(50), nullable=False)
    accepte:           Mapped[bool]     = mapped_column(Boolean,    nullable=False, default=False)
    date_consentement: Mapped[datetime] = mapped_column(DateTime,   nullable=False, server_default=func.now())
    user_id:           Mapped[str]      = mapped_column(ForeignKey("user.user_id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="consentements")


class IA(Base):
    __tablename__ = "ia"

    id_ia:          Mapped[str]      = mapped_column(String(50), primary_key=True, default=gen_uuid)
    type_action:    Mapped[str]      = mapped_column(String(50), nullable=False)
    content_before: Mapped[str]      = mapped_column(Text)
    content_after:  Mapped[str]      = mapped_column(Text)
    created_at:     Mapped[datetime] = mapped_column(DateTime,   nullable=False, server_default=func.now())

    user_id: Mapped[str] = mapped_column(ForeignKey('user.user_id'), nullable=False)
    users:     Mapped[list[User]]     = relationship("User",     back_populates="ias")
    id_document: Mapped[str] = mapped_column(ForeignKey('document.id'))
    documents: Mapped[list[Document]] = relationship("Document", back_populates="ias")


# ── Création des tables ──────────────────────────────────────────────────────
Base.metadata.create_all(engine)