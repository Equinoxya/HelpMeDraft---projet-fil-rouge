from __future__ import annotations
from pathlib import Path
from datetime import datetime
import uuid
from sqlalchemy import (
    Boolean, DateTime, ForeignKey,
    Integer, String, Text, create_engine, func
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
)
from utilitaires import utc_now_naive

DB_PATH = Path("HelpMeDraft.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def gen_uuid() -> str:
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass

# ── Modèles ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "user"

    user_id:    Mapped[str]      = mapped_column(String(36),  primary_key=True, default=gen_uuid)
    lastname:   Mapped[str]      = mapped_column(String(50),  nullable=False)
    firstname:  Mapped[str]      = mapped_column(String(50),  nullable=False)
    email:      Mapped[str]      = mapped_column(String(326), nullable=False, unique=True)
    mdp_hash:   Mapped[str]      = mapped_column(String(255), nullable=False)
    role:       Mapped[str]      = mapped_column(String(20),  nullable=False, default="user") # ex: 'user', 'admin'
    
    # Quotas & Usage IA
    quota_daily_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utc_now_naive, onupdate=utc_now_naive)

    password_resets: Mapped[list[PasswordReset]] = relationship("PasswordReset", back_populates="user", cascade="all, delete-orphan")
    dossiers:        Mapped[list[Dossier]]       = relationship("Dossier",       back_populates="user", cascade="all, delete-orphan")
    documents:       Mapped[list[Document]]      = relationship("Document",      back_populates="user", cascade="all, delete-orphan")
    consentements:   Mapped[list[Consentement]]  = relationship("Consentement",  back_populates="user", cascade="all, delete-orphan")
    sessions:        Mapped[list[UserSession]]   = relationship("UserSession",   back_populates="user", cascade="all, delete-orphan")
    ias:             Mapped[list[IA]]            = relationship("IA",            back_populates="user", cascade="all, delete-orphan")


class PasswordReset(Base):
    __tablename__ = "password_reset"
    
    id:          Mapped[str]      = mapped_column(String(36),  primary_key=True, default=gen_uuid)
    user_id:     Mapped[str]      = mapped_column(String(36),  ForeignKey("user.user_id"), nullable=False)
    token_hash:  Mapped[str]      = mapped_column(String(512), nullable=False)
    expires_at:  Mapped[datetime] = mapped_column(DateTime,    nullable=False)
    used:        Mapped[bool]     = mapped_column(Boolean,     nullable=False, default=False)
    created_at:  Mapped[datetime] = mapped_column(DateTime,    nullable=False, default=utc_now_naive)

    user: Mapped[User] = relationship("User", back_populates="password_resets")


class UserSession(Base):
    __tablename__ = "user_session"

    id_session:        Mapped[str]      = mapped_column(String(36),  primary_key=True, default=gen_uuid)
    refresh_token:     Mapped[str]      = mapped_column(String(512), nullable=False, unique=True)
    refresh_token_exp: Mapped[datetime] = mapped_column(DateTime,    nullable=False)
    revoke:            Mapped[bool] = mapped_column(Boolean, nullable= False, default=False)
    created_at:        Mapped[datetime] = mapped_column(DateTime,    nullable=False, default=utc_now_naive)
    user_id:           Mapped[str]      = mapped_column(String(36),  ForeignKey("user.user_id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="sessions")


class Dossier(Base):
    __tablename__ = "dossier"

    id_dossier: Mapped[str]      = mapped_column(String(36),  primary_key=True, default=gen_uuid)
    name:       Mapped[str]      = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,    nullable=False, default=utc_now_naive)
    user_id:    Mapped[str]      = mapped_column(String(36),  ForeignKey("user.user_id"), nullable=False)

    user:      Mapped[User]           = relationship("User",     back_populates="dossiers")
    documents: Mapped[list[Document]] = relationship("Document", back_populates="dossier")


class Document(Base):
    __tablename__ = "document"

    id_document: Mapped[str]      = mapped_column(String(36),  primary_key=True, default=gen_uuid)
    titre:       Mapped[str]      = mapped_column(String(255), nullable=False)
    content:     Mapped[str]      = mapped_column(Text,        nullable=True)
    format:      Mapped[str]      = mapped_column(String(20),  default="markdown") # ex: 'markdown', 'wysiwyg'
    created_at:  Mapped[datetime] = mapped_column(DateTime,    nullable=False, default=utc_now_naive)
    updated_at:  Mapped[datetime] = mapped_column(DateTime,    nullable=False, default=utc_now_naive, onupdate=utc_now_naive)
    
    id_dossier:  Mapped[str | None] = mapped_column(String(36), ForeignKey("dossier.id_dossier", ondelete="SET NULL"), nullable=True)
    user_id:     Mapped[str]        = mapped_column(String(36), ForeignKey("user.user_id"), nullable=False)

    dossier: Mapped[Dossier | None] = relationship("Dossier", back_populates="documents")
    user:    Mapped[User]           = relationship("User",    back_populates="documents")
    ias:     Mapped[list[IA]]       = relationship("IA",      back_populates="document", cascade="all, delete-orphan")


class Consentement(Base):
    __tablename__ = "consentement"

    id_consentement:   Mapped[str]      = mapped_column(String(36), primary_key=True, default=gen_uuid)
    type_consentement: Mapped[str]      = mapped_column(String(50), nullable=False) # ex: 'openai_data_processing'
    accepte:           Mapped[bool]     = mapped_column(Boolean,    nullable=False, default=False)
    date_consentement: Mapped[datetime] = mapped_column(DateTime,   nullable=False, default=utc_now_naive)
    user_id:           Mapped[str]      = mapped_column(String(36), ForeignKey("user.user_id"), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="consentements")


class IA(Base):
    __tablename__ = "ia"

    id_ia:          Mapped[str]      = mapped_column(String(36), primary_key=True, default=gen_uuid)
    type_action:    Mapped[str]      = mapped_column(String(50), nullable=False) # ex: 'reformuler', 'corriger', 'completer'
    content_before: Mapped[str]      = mapped_column(Text, nullable=True)
    content_after:  Mapped[str]      = mapped_column(Text, nullable=True)
    tokens_used:    Mapped[int]      = mapped_column(Integer, default=0) # Utile pour les métriques de back-office !
    created_at:     Mapped[datetime] = mapped_column(DateTime,   nullable=False, default=utc_now_naive)
    
    user_id:        Mapped[str]      = mapped_column(String(36), ForeignKey("user.user_id"), nullable=False)
    id_document:    Mapped[str]      = mapped_column(String(36), ForeignKey("document.id_document"), nullable=False)

    user:     Mapped[User]     = relationship("User",     back_populates="ias")
    document: Mapped[Document] = relationship("Document", back_populates="ias")

# ── Création des tables ──────────────────────────────────────────────────────
Base.metadata.create_all(engine)