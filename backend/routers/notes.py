import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from models.schemas import NoteIn, NoteOut, NoteDetailOut, NoteEmbedResponse, LinkInfo, TaskItem
from services.database import get_session, save_note, get_note, list_notes, get_tasks_by_note
from services.retriever import process_and_index_note
from services.graph import link_related_notes

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/embed", response_model=NoteEmbedResponse)
async def embed_note(
    data: NoteIn,
    session: AsyncSession = Depends(get_session)
):
    """
    Embed note text into vector store and create semantic links
    """
    try:
        # Index the note in the vector store
        chunks_indexed = await process_and_index_note(
            text=data.text,
            note_id=str(data.note_id),
            metadata=data.meta
        )
        
        # Generate links to related notes
        links = await link_related_notes(
            session=session,
            note_id=data.note_id,
            k=5
        )
        
        return NoteEmbedResponse(
            chunks_indexed=chunks_indexed,
            links=links
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error embedding note: {str(e)}")


@router.get("", response_model=List[NoteOut])
async def get_notes(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 20
):
    """
    Get a list of notes with pagination
    """
    try:
        notes = await list_notes(session, skip, limit)
        
        return [
            NoteOut(
                id=note.id,
                title=note.title,
                body=note.body,
                created_at=note.created_at,
                updated_at=note.updated_at
            )
            for note in notes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notes: {str(e)}")


@router.get("/{note_id}", response_model=NoteDetailOut)
async def get_note_detail(
    note_id: uuid.UUID = Path(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed information about a note, including tasks and links
    """
    try:
        # Get the note
        note = await get_note(session, note_id)
        
        if not note:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found")
        
        # Get tasks for this note
        tasks = await get_tasks_by_note(session, note_id)
        
        # Get related links
        links = await link_related_notes(session, note_id)
        
        # Create response
        return NoteDetailOut(
            id=note.id,
            title=note.title,
            body=note.body,
            created_at=note.created_at,
            updated_at=note.updated_at,
            tasks=[
                TaskItem(
                    description=task.description,
                    due_date=task.due_date,
                    owner=task.owner,
                    source_note_id=task.source_note_id,
                    completed=task.completed
                )
                for task in tasks
            ],
            related_links=links
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting note detail: {str(e)}")


@router.post("", response_model=NoteOut)
async def create_note(
    note_data: dict,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new note
    """
    try:
        # Save the note
        note = await save_note(session, note_data)
        
        return NoteOut(
            id=note.id,
            title=note.title,
            body=note.body,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")
