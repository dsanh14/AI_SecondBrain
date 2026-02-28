import os
from typing import Optional, List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "ai-second-brain")
USE_FAISS_FALLBACK = os.getenv("USE_FAISS_FALLBACK", "true").lower() == "true"

# Configure logger
logger = logging.getLogger(__name__)


def get_embeddings_model() -> OpenAIEmbeddings:
    """Get the embeddings model with environment defaults"""
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )


def get_vector_store(index_name: Optional[str] = None) -> Any:
    """
    Get vector store based on environment configuration
    Falls back to FAISS if Pinecone config is missing
    """
    embeddings = get_embeddings_model()
    index = index_name or PINECONE_INDEX
    
    # Check if Pinecone configuration is available
    if PINECONE_API_KEY and PINECONE_ENV and not USE_FAISS_FALLBACK:
        try:
            # Initialize Pinecone vector store
            vector_store = PineconeVectorStore(
                index_name=index,
                embedding=embeddings,
            )
            logger.info(f"Using Pinecone vector store with index: {index}")
            return vector_store
        except Exception as e:
            logger.warning(f"Failed to initialize Pinecone: {e}")
            if not USE_FAISS_FALLBACK:
                raise
    
    # Fallback to FAISS
    logger.info("Using FAISS vector store (local)")
    # For FAISS, we'll return a function that creates a new store since
    # it needs documents to initialize
    return lambda documents: FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )


def create_chunks_from_text(text: str, note_id: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
    """Create document chunks from text with metadata"""
    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    
    # Create base metadata
    meta = {"note_id": note_id}
    if metadata:
        meta.update(metadata)
    
    # Create documents
    documents = text_splitter.create_documents(
        texts=[text],
        metadatas=[meta]
    )
    
    return documents


async def index_note(vector_store, text: str, note_id: str, metadata: Optional[Dict[str, Any]] = None) -> int:
    """Index a note text into the vector store"""
    # Create chunks
    chunks = create_chunks_from_text(text, note_id, metadata)
    
    # Add to vector store
    if isinstance(vector_store, PineconeVectorStore):
        # For Pinecone
        vector_store.add_documents(chunks)
    else:
        # For FAISS (or other stores requiring initialization with documents)
        if not hasattr(vector_store, 'add_documents'):
            vector_store = vector_store(chunks)
        else:
            vector_store.add_documents(chunks)
    
    return len(chunks)
