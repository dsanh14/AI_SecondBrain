import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import summarize, tasks, search, notes

app = FastAPI(title="AI Second Brain API", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarize.router)
app.include_router(tasks.router)
app.include_router(search.router)
app.include_router(notes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Second Brain API", "status": "active"}

@app.get("/health")
def health_check():
    # Check if services are available
    services = {
        "api": "ok",
        "db": "ok",  # This would typically check database connection
        "openai": "ok" if os.getenv("OPENAI_API_KEY") else "missing key",
        "vector_store": "pinecone" if os.getenv("PINECONE_API_KEY") and os.getenv("PINECONE_ENV") else "faiss"
    }
    return services
