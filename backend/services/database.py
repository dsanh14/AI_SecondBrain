import os
import uuid
from typing import List, Optional, Any, Dict, Type

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select
from fastapi import Depends

from models.orm import Note, Task, Link
from models.schemas import TaskItem, LinkInfo


# Database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@db:5432/aisecondbrain")

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables():
    """Create database tables if they don't exist"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting async session"""
    async with async_session() as session:
        yield session


# CRUD operations
async def save_note(session: AsyncSession, note_data: Dict[str, Any]) -> Note:
    """Save or update a note"""
    if "id" in note_data and note_data["id"]:
        # Update existing note
        note_id = note_data["id"]
        stmt = select(Note).where(Note.id == note_id)
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        
        if note:
            for key, value in note_data.items():
                setattr(note, key, value)
    else:
        # Create new note
        note = Note(**note_data)
        session.add(note)
    
    await session.commit()
    await session.refresh(note)
    return note


async def get_note(session: AsyncSession, note_id: uuid.UUID) -> Optional[Note]:
    """Get a note by ID"""
    stmt = select(Note).where(Note.id == note_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_notes(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[Note]:
    """List all notes with pagination"""
    stmt = select(Note).order_by(Note.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(stmt)
    return result.scalars().all()


async def save_tasks(session: AsyncSession, tasks: List[TaskItem]) -> List[Task]:
    """Save multiple tasks"""
    db_tasks = []
    
    for task_data in tasks:
        task = Task(**task_data.model_dump())
        session.add(task)
        db_tasks.append(task)
    
    await session.commit()
    
    # Refresh tasks to get their IDs
    for task in db_tasks:
        await session.refresh(task)
    
    return db_tasks


async def update_task(session: AsyncSession, task_id: uuid.UUID, task_data: Dict[str, Any]) -> Optional[Task]:
    """Update a task"""
    stmt = select(Task).where(Task.id == task_id)
    result = await session.execute(stmt)
    task = result.scalar_one_or_none()
    
    if task:
        for key, value in task_data.items():
            setattr(task, key, value)
        
        await session.commit()
        await session.refresh(task)
    
    return task


async def get_tasks_by_note(session: AsyncSession, note_id: uuid.UUID) -> List[Task]:
    """Get all tasks for a note"""
    stmt = select(Task).where(Task.source_note_id == note_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def upsert_links(session: AsyncSession, links: List[LinkInfo]) -> List[Link]:
    """Create or update links between notes"""
    db_links = []
    
    for link_data in links:
        # Check if link already exists
        stmt = select(Link).where(
            Link.source_note_id == link_data.source_note,
            Link.target_note_id == link_data.target_note
        )
        result = await session.execute(stmt)
        link = result.scalar_one_or_none()
        
        if link:
            # Update similarity
            link.similarity = link_data.similarity
        else:
            # Create new link
            link = Link(
                source_note_id=link_data.source_note,
                target_note_id=link_data.target_note,
                similarity=link_data.similarity
            )
            session.add(link)
        
        db_links.append(link)
    
    await session.commit()
    
    # Refresh links to get their IDs
    for link in db_links:
        await session.refresh(link)
    
    return db_links


async def get_note_links(session: AsyncSession, note_id: uuid.UUID, limit: int = 5) -> List[Link]:
    """Get links related to a note (both incoming and outgoing)"""
    # Get outgoing links
    outgoing_stmt = select(Link).where(Link.source_note_id == note_id).order_by(Link.similarity.desc()).limit(limit)
    outgoing_result = await session.execute(outgoing_stmt)
    outgoing_links = outgoing_result.scalars().all()
    
    # Get incoming links
    incoming_stmt = select(Link).where(Link.target_note_id == note_id).order_by(Link.similarity.desc()).limit(limit)
    incoming_result = await session.execute(incoming_stmt)
    incoming_links = incoming_result.scalars().all()
    
    # Combine and deduplicate
    combined_links = list(set(outgoing_links + incoming_links))
    # Sort by similarity
    combined_links.sort(key=lambda x: x.similarity, reverse=True)
    
    return combined_links[:limit]
