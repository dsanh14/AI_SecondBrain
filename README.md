# AI Second Brain

This repository contains a production-ready AI-powered personal knowledge system that helps summarize meetings, extract tasks, link notes via a semantic graph, and supports semantic search/Q&A.

## Project Structure

The main project is in the `ai-second-brain` directory, which contains the full implementation of:

- **Backend**: FastAPI with LangChain, PostgreSQL, and Pinecone/FAISS vector storage
- **Frontend**: Next.js with TypeScript, Tailwind CSS, and Cytoscape graph visualization
- **Docker**: Configuration for containerized deployment

## Getting Started

To work with this project:

```bash
cd ai-second-brain
```

Then follow the instructions in the project's README.md file.

## Features

- Text summarization using LangChain map-reduce patterns
- Task extraction from notes
- Semantic linking between related content
- Interactive knowledge graph visualization
- Semantic search with citations
- Audio transcription via Whisper API

## Tech Stack

- **Backend**: FastAPI, SQLModel, LangChain, OpenAI GPT-4o
- **Frontend**: Next.js, TypeScript, Tailwind CSS, Cytoscape
- **Database**: PostgreSQL
- **Vector Store**: Pinecone (with FAISS fallback)