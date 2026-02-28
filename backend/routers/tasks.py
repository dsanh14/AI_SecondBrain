from fastapi import APIRouter, HTTPException, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List, Optional

from models.schemas import TaskExtractIn, TaskExtractOut, TaskItem
from services.llm import build_task_chain
from services.database import get_session, save_tasks, update_task

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/extract", response_model=TaskExtractOut)
async def extract_tasks(
    data: TaskExtractIn,
    session: AsyncSession = Depends(get_session)
):
    """
    Extract tasks from text content.
    Optionally associates tasks with a note ID and saves to database.
    
    Returns:
        List of extracted tasks
    """
    try:
        # Validate input
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Get task extraction chain
        task_chain = build_task_chain()
        
        # Extract tasks
        result = task_chain(data.text)
        raw_tasks = result.get("tasks", [])
        
        # Convert dicts to TaskItem instances
        tasks = [
            TaskItem(**t) if isinstance(t, dict) else t
            for t in raw_tasks
        ]
        
        # If source_note_id is provided, save tasks to database
        if data.source_note_id:
            for task in tasks:
                task.source_note_id = data.source_note_id
                
            await save_tasks(session, tasks)
        
        return TaskExtractOut(tasks=tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting tasks: {str(e)}")


@router.get("", response_model=List[TaskItem])
async def list_tasks(
    completed: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
    limit: int = 50,
    offset: int = 0
):
    """
    List tasks with optional filtering by completion status
    """
    from models.orm import Task
    from sqlalchemy import select
    
    try:
        # Build query
        query = select(Task).offset(offset).limit(limit)
        
        # Apply filter if completed status is specified
        if completed is not None:
            query = query.where(Task.completed == completed)
            
        # Execute query
        result = await session.execute(query)
        tasks = result.scalars().all()
        
        # Convert to response models
        return [
            TaskItem(
                description=task.description,
                due_date=task.due_date,
                owner=task.owner,
                source_note_id=task.source_note_id,
                completed=task.completed
            )
            for task in tasks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")


@router.patch("/{task_id}", response_model=TaskItem)
async def update_task_status(
    task_id: uuid.UUID = Path(...),
    completed: Optional[bool] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Update a task's status
    """
    try:
        # Update task
        updated_task = await update_task(session, task_id, {"completed": completed})
        
        if not updated_task:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        # Return updated task
        return TaskItem(
            description=updated_task.description,
            due_date=updated_task.due_date,
            owner=updated_task.owner,
            source_note_id=updated_task.source_note_id,
            completed=updated_task.completed
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")
