# AI Second Brain - Architecture Documentation

## System Overview

AI Second Brain is a knowledge management system that uses AI to process, organize, and retrieve information. The system is designed to help users capture, connect, and query their personal knowledge base.

## Component Architecture

### High-Level Components

```mermaid
graph TB
    User[User]
    FE[Frontend - Next.js]
    BE[Backend - FastAPI]
    DB[(PostgreSQL)]
    VS[(Vector Store)]
    LLM[OpenAI LLM Services]
    Whisper[Whisper API]
    
    User -->|Interacts with| FE
    FE -->|API Requests| BE
    BE -->|Queries/Updates| DB
    BE -->|Semantic Search| VS
    BE -->|LLM Requests| LLM
    BE -->|Audio Transcription| Whisper
    VS -->|Similarity Search| BE
```

### Backend Architecture

```mermaid
graph TD
    Router[API Routers]
    Service[Services Layer]
    Models[Data Models]
    DB[(PostgreSQL)]
    VS[(Vector Store)]
    LLM[LLM Services]
    
    Router -->|Uses| Service
    Service -->|CRUD Operations| Models
    Models -->|ORM| DB
    Service -->|Vector Operations| VS
    Service -->|LLM Chains| LLM
    
    subgraph API Routers
        SummarizeRouter[Summarize Router]
        TaskRouter[Tasks Router]
        NoteRouter[Notes Router]
        SearchRouter[Search Router]
    end
    
    subgraph Services Layer
        LLMService[LLM Service]
        DBService[Database Service]
        EmbeddingService[Embedding Service]
        RetrieverService[Retriever Service]
        GraphService[Graph Service]
        SpeechService[Speech Service]
    end
    
    subgraph Data Models
        Note[Note Model]
        Task[Task Model]
        Link[Link Model]
    end
```

### Frontend Architecture

```mermaid
graph TD
    Pages[Next.js Pages]
    Components[UI Components]
    API[API Client]
    State[State Management]
    
    Pages -->|Renders| Components
    Pages -->|Data Fetching| API
    Components -->|Data Fetching| API
    API -->|State Updates| State
    State -->|Reactivity| Components
    
    subgraph Pages
        Dashboard[Dashboard]
        Notes[Notes List]
        NoteDetail[Note Detail]
        Upload[Upload]
        Search[Search & QA]
        Graph[Graph View]
    end
    
    subgraph UI Components
        NoteCard[Note Card]
        TaskList[Task List]
        GraphView[Graph View]
        UploadForm[Upload Form]
        SearchBox[Search Box]
    end
```

## Data Flow

### Note Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant BE as Backend API
    participant DB as PostgreSQL
    participant VS as Vector Store
    participant LLM as OpenAI LLM
    
    User->>FE: Upload text/audio
    Note right of FE: Audio transcribed if needed
    FE->>BE: Submit text for processing
    BE->>LLM: Request summarization
    LLM-->>BE: Return summary with sections
    BE->>DB: Store note with summary
    BE->>LLM: Extract tasks
    LLM-->>BE: Return structured tasks
    BE->>DB: Store tasks
    BE->>VS: Create and store embeddings
    BE->>VS: Find semantically similar notes
    VS-->>BE: Return similar notes
    BE->>DB: Store links between notes
    BE-->>FE: Return processing results
    FE-->>User: Display summary and relations
```

### Search & Query Pipeline

```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant BE as Backend API
    participant VS as Vector Store
    participant LLM as OpenAI LLM
    participant DB as PostgreSQL
    
    User->>FE: Submit search query
    FE->>BE: POST /search/query
    BE->>VS: Retrieve relevant documents
    VS-->>BE: Return matching documents
    BE->>LLM: Generate answer with context
    LLM-->>BE: Return answer with citations
    BE->>DB: Look up citation details
    DB-->>BE: Return note information
    BE-->>FE: Return formatted answer
    FE-->>User: Display answer with citations
```

## Database Schema

```mermaid
erDiagram
    NOTE {
        uuid id PK
        string title
        text body
        datetime created_at
        datetime updated_at
    }
    
    TASK {
        uuid id PK
        text description
        datetime due_date
        string owner
        uuid source_note_id FK
        boolean completed
        datetime created_at
    }
    
    LINK {
        uuid id PK
        uuid source_note_id FK
        uuid target_note_id FK
        float similarity
        datetime created_at
    }
    
    NOTE ||--o{ TASK : "contains"
    NOTE ||--o{ LINK : "source"
    NOTE ||--o{ LINK : "target"
```

## Vector Storage

The system uses a vector database to store and query embeddings of note content. Two implementations are supported:

1. **Pinecone**: Primary vector store for production use
   - Scalable cloud-based vector database
   - Efficient similarity search
   - Persistence across sessions

2. **FAISS**: Local fallback option
   - In-memory vector store
   - No external API dependencies
   - Suitable for development and testing

The system automatically detects whether Pinecone credentials are available and falls back to FAISS if needed.

## LangChain Integration

LangChain is used as the orchestration layer for all LLM operations. Key components include:

1. **Summarization Chain**: Map-reduce pattern for processing long documents
2. **Task Extraction Chain**: Structured output with JSON schema enforcement
3. **Q&A Chain**: Retrieval augmented generation with citation tracking
4. **Embeddings**: Integration with OpenAI embedding models

## Security Considerations

1. API keys stored in environment variables, not in code
2. Backend handles all LLM API calls, frontend never directly accesses OpenAI
3. Database credentials isolated in containers
4. Rate limiting recommended for production deployments

## Scalability

1. Stateless API design allows horizontal scaling
2. Database can be scaled independently
3. Vector store (Pinecone) handles scaling of embedding storage and retrieval
4. Consider caching for frequently accessed notes and summaries

## Deployment Considerations

1. Ensure sufficient memory for FAISS if used (at least 4GB recommended)
2. Monitor OpenAI API usage to control costs
3. Consider adding Redis for rate limiting and caching in production
4. Set up proper monitoring for API endpoints and LLM service health
