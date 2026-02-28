import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, ForeignKey, String, Boolean, Float, Text, DateTime
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import UUID


class Note(SQLModel, table=True):
    __tablename__ = "notes"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    title: Optional[str] = Field(sa_column=Column(Text))
    body: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime))
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime))
    
    # Relationships
    tasks: List["Task"] = Relationship(back_populates="source_note")
    outgoing_links: List["Link"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Link.source_note_id]"},
        back_populates="source"
    )
    incoming_links: List["Link"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Link.target_note_id]"},
        back_populates="target"
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    description: str = Field(sa_column=Column(Text))
    due_date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
    owner: Optional[str] = Field(default=None, sa_column=Column(String(255)))
    source_note_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="notes.id",
        sa_column=Column(UUID(as_uuid=True), ForeignKey("notes.id"))
    )
    completed: bool = Field(default=False, sa_column=Column(Boolean))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime))
    
    # Relationship
    source_note: Optional[Note] = Relationship(back_populates="tasks")


class Link(SQLModel, table=True):
    __tablename__ = "links"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        sa_column=Column(UUID(as_uuid=True), primary_key=True)
    )
    source_note_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("notes.id"), index=True)
    )
    target_note_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("notes.id"), index=True)
    )
    similarity: float = Field(sa_column=Column(Float))
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime))
    
    # Relationships
    source: Note = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Link.source_note_id"},
        back_populates="outgoing_links"
    )
    target: Note = Relationship(
        sa_relationship_kwargs={"foreign_keys": "Link.target_note_id"},
        back_populates="incoming_links"
    )
