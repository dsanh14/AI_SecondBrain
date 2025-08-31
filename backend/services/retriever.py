import os
from typing import Any, Dict, List, Optional

from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
import logging

from services.embeddings import get_vector_store, index_note

# Configure logger
logger = logging.getLogger(__name__)

# Default retrieval parameters
DEFAULT_K = 6


def make_retriever(index_name: Optional[str] = None, k: int = DEFAULT_K) -> BaseRetriever:
    """
    Create a retriever for the specified vector store
    
    Args:
        index_name: Name of the vector index
        k: Number of documents to retrieve
    
    Returns:
        A configured retriever
    """
    vector_store = get_vector_store(index_name)
    
    # For FAISS which might return a factory function
    if callable(vector_store) and not isinstance(vector_store, BaseRetriever):
        # Initialize with empty documents as needed
        try:
            # Create an empty document to initialize the store
            empty_doc = Document(page_content="", metadata={"note_id": "init"})
            vector_store = vector_store([empty_doc])
        except Exception as e:
            logger.warning(f"Could not initialize empty vector store: {e}")
            # Return a simple retriever that returns no results
            return EmptyRetriever()
    
    # Create and return the retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": k}
    )
    
    return retriever


class EmptyRetriever(BaseRetriever):
    """A fallback retriever that returns no documents"""
    
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Return no documents"""
        logger.warning("Using EmptyRetriever - no documents will be returned")
        return []


async def process_and_index_note(
    text: str,
    note_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    index_name: Optional[str] = None
) -> int:
    """
    Process a note text and index it in the vector store
    
    Args:
        text: The note text
        note_id: The UUID of the note
        metadata: Additional metadata to store with the embeddings
        index_name: Name of the vector index
    
    Returns:
        Number of chunks indexed
    """
    vector_store = get_vector_store(index_name)
    return await index_note(vector_store, text, str(note_id), metadata)
