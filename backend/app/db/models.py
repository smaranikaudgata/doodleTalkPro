from sqlalchemy import DateTime, Integer, String, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import UTC, datetime
from pgvector.sqlalchemy import Vector
from app.db.session import Base
from app.utils.constants import DocumentStatus, ChatRole

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    #relationships
    documents: Mapped[list["Document"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(50))
    file_path: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(default=DocumentStatus.processing)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    #relationships
    owner: Mapped["User"] = relationship(back_populates="documents")
    document_chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    text_content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(768))
    __table_args__ = (
    Index('hnsw_index_for_embedding', 'embedding',
          postgresql_using='hnsw',
          postgresql_with={'m': 16, 'ef_construction': 64},
          postgresql_ops={'embedding': 'vector_cosine_ops'},
        ),
    )

    #relationships
    document: Mapped["Document"] = relationship(back_populates="document_chunks")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    #relationships
    owner: Mapped["User"] = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(back_populates="chat_session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[ChatRole] = mapped_column(default=ChatRole.user)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    #relationships
    chat_session: Mapped["ChatSession"] = relationship(back_populates="messages")