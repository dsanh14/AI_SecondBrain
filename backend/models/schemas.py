import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, UUID4


# Input models
class SummarizeIn(BaseModel):
    text: str


class TaskExtractIn(BaseModel):
    text: str
    source_note_id: Optional[UUID4] = None


class NoteIn(BaseModel):
    note_id: UUID4
    text: str
    meta: Optional[Dict[str, Any]] = None


class SearchIn(BaseModel):
    query: str
    k: Optional[int] = 6


# Output models
class SummarizeOut(BaseModel):
    summary: str
    highlights: List[str]
    decisions: List[str]
    action_items: List[str]


class TaskItem(BaseModel):
    description: str
    due_date: Optional[datetime] = None
    owner: Optional[str] = None
    source_note_id: Optional[UUID4] = None
    completed: bool = False


class TaskExtractOut(BaseModel):
    tasks: List[TaskItem]


class NoteOut(BaseModel):
    id: UUID4
    title: Optional[str] = None
    body: str
    created_at: datetime
    updated_at: datetime


class CitationInfo(BaseModel):
    note_id: UUID4
    snippet: str


class SearchOut(BaseModel):
    answer: str
    citations: List[CitationInfo]


class LinkInfo(BaseModel):
    source_note: UUID4
    target_note: UUID4
    similarity: float


class LinksOut(BaseModel):
    links: List[LinkInfo]


class NoteEmbedResponse(BaseModel):
    chunks_indexed: int
    links: List[LinkInfo]


# Extended output model for note detail
class NoteDetailOut(NoteOut):
    tasks: List[TaskItem] = []
    related_links: List[LinkInfo] = []
