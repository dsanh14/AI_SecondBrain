from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from models.schemas import SummarizeIn, SummarizeOut
from services.llm import build_summarization_chain

router = APIRouter(prefix="/summarize", tags=["summarization"])


@router.post("", response_model=SummarizeOut)
async def summarize_text(data: SummarizeIn):
    """
    Summarize text content using map-reduce summarization.
    
    Returns:
        - Summary text
        - Key highlights
        - Decisions
        - Action items
    """
    try:
        # Validate input
        if not data.text.strip():
            raise HTTPException(status_code=400, detail="Text content is required")
        
        # Get summarization chain
        summarize_chain = build_summarization_chain()
        
        # Process the text
        result = summarize_chain(data.text)
        
        # Return formatted output
        return SummarizeOut(
            summary=result.get("summary", ""),
            highlights=result.get("highlights", []),
            decisions=result.get("decisions", []),
            action_items=result.get("action_items", [])
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing summarization: {str(e)}")
