import uuid
from typing import List, Dict, Any, Optional
import logging

from langchain_core.retrievers import BaseRetriever
from sqlalchemy.ext.asyncio import AsyncSession

from services.retriever import make_retriever
from services.database import upsert_links, get_note_links
from models.schemas import LinkInfo

# Configure logger
logger = logging.getLogger(__name__)

# Default parameters
DEFAULT_SIMILARITY_THRESHOLD = 0.7
DEFAULT_TOP_K = 5


async def link_related_notes(
    session: AsyncSession,
    note_id: uuid.UUID,
    retriever: Optional[BaseRetriever] = None,
    k: int = DEFAULT_TOP_K,
    index_name: Optional[str] = None,
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> List[LinkInfo]:
    """
    Find and store links to semantically related notes
    
    Args:
        session: Database session
        note_id: The UUID of the note to find links for
        retriever: Optional pre-configured retriever
        k: Number of related notes to find
        index_name: Name of the vector index
        similarity_threshold: Minimum similarity score to create a link
    
    Returns:
        List of created links
    """
    try:
        # Get or create a retriever
        if retriever is None:
            retriever = make_retriever(index_name=index_name, k=k+1)  # +1 to account for self-match
        
        # Create a simple query from the note ID to find similar content
        # In a real application, you might use the note content as the query
        query = f"note:{note_id}"
        
        # Get relevant documents
        docs = retriever.get_relevant_documents(query)
        
        # Filter out the current note (if present) and collect links
        links = []
        for doc in docs:
            target_note_id = doc.metadata.get("note_id")
            similarity = doc.metadata.get("score", 0.0)  # Some retrievers include score
            
            # Skip self-matches and notes below threshold
            if str(target_note_id) == str(note_id) or similarity < similarity_threshold:
                continue
                
            # Create link
            link = LinkInfo(
                source_note=note_id,
                target_note=uuid.UUID(target_note_id),
                similarity=float(similarity)
            )
            links.append(link)
        
        # Limit to top-k
        links = links[:k]
        
        # Save links to database
        if links:
            await upsert_links(session, links)
        
        return links
    except Exception as e:
        logger.error(f"Error linking related notes: {e}")
        return []


async def get_note_neighborhood(
    session: AsyncSession,
    note_id: uuid.UUID,
    limit: int = DEFAULT_TOP_K
) -> List[LinkInfo]:
    """
    Get a note's neighborhood (incoming and outgoing links)
    
    Args:
        session: Database session
        note_id: Note ID to find neighbors for
        limit: Maximum number of links to return
    
    Returns:
        List of links
    """
    links = await get_note_links(session, note_id, limit)
    
    # Convert to LinkInfo format
    return [
        LinkInfo(
            source_note=link.source_note_id,
            target_note=link.target_note_id,
            similarity=link.similarity
        )
        for link in links
    ]


async def get_graph_data(
    session: AsyncSession,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get graph data for visualization
    
    Args:
        session: Database session
        limit: Maximum number of links to return
    
    Returns:
        Dict with nodes and edges for visualization
    """
    # This would typically query for all notes and links with limits
    # For now we'll return a simplified structure
    links = await get_note_links(session, None, limit)
    
    # Create unique set of nodes
    nodes = set()
    for link in links:
        nodes.add(str(link.source_note_id))
        nodes.add(str(link.target_note_id))
    
    # Format as graph data
    return {
        "nodes": [{"id": node_id} for node_id in nodes],
        "edges": [
            {
                "id": f"{link.source_note_id}-{link.target_note_id}",
                "source": str(link.source_note_id),
                "target": str(link.target_note_id),
                "weight": link.similarity
            }
            for link in links
        ]
    }
