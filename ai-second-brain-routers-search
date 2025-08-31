import re
import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.schemas import SearchIn, SearchOut, CitationInfo
from services.llm import build_qa_chain
from services.retriever import make_retriever
from services.database import get_session

router = APIRouter(prefix="/search", tags=["search"])

# Regex to extract citations in the format [note_id:UUID]
CITATION_PATTERN = r'\[note_id:([0-9a-fA-F-]+)\]'


@router.post("/query", response_model=SearchOut)
async def search_query(
    data: SearchIn,
    session: AsyncSession = Depends(get_session)
):
    """
    Perform semantic search and generate an answer with citations
    """
    try:
        # Validate input
        if not data.query.strip():
            raise HTTPException(status_code=400, detail="Search query is required")
        
        # Set default k if not provided
        k = data.k if data.k is not None else 6
        
        # Get retriever
        retriever = make_retriever(k=k)
        
        # Build QA chain
        qa_chain = build_qa_chain(retriever)
        
        # Get answer
        answer = qa_chain(data.query)
        
        # Extract citations
        citations = extract_citations(answer)
        
        return SearchOut(
            answer=answer,
            citations=citations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing search query: {str(e)}")


def extract_citations(text: str) -> List[CitationInfo]:
    """
    Extract citation references from text in the format [note_id:UUID]
    and convert them to CitationInfo objects
    """
    citations = []
    
    # Find all citation matches
    matches = re.finditer(CITATION_PATTERN, text)
    
    for match in matches:
        try:
            note_id_str = match.group(1)
            note_id = uuid.UUID(note_id_str)
            
            # Extract a snippet of context (up to 100 chars before the citation)
            start_pos = max(0, match.start() - 100)
            end_pos = match.start()
            snippet = text[start_pos:end_pos].strip()
            
            citation = CitationInfo(
                note_id=note_id,
                snippet=snippet
            )
            citations.append(citation)
        except ValueError:
            # Skip invalid UUIDs
            continue
    
    return citations
