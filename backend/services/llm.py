import os
from typing import Dict, List, Any, Optional

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

from models.schemas import TaskItem


# Environment variables for OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_llm(model_name: Optional[str] = None, temperature: float = 0.0) -> ChatOpenAI:
    """Get LLM instance with environment defaults"""
    model = model_name or OPENAI_MODEL
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
    )


# Constants for prompts
SUMMARIZE_MAP_PROMPT = """You are an expert at summarizing content.
Create a concise summary of this content chunk. Include:
- 3-5 bullet points of key information
- Any important decisions mentioned
- Any action items or tasks mentioned

Content to summarize:
{text}
"""

SUMMARIZE_REDUCE_PROMPT = """You are an expert at summarizing and organizing information.
Combine these summaries into a cohesive executive summary. Structure your response as:

## Summary
- 5-8 bullet points covering the most important information

## Decisions
- List all decisions mentioned

## Action Items
- List all action items or tasks mentioned

Previous summaries:
{summaries}
"""

TASK_EXTRACT_PROMPT = """Extract tasks from the following text. 
For each task provide:
1. A clear description of what needs to be done
2. Due date (if mentioned)
3. Owner/assignee (if mentioned)

Return the results as a JSON array with fields:
- description: string (required)
- due_date: ISO date string or null
- owner: string or null
- completed: always false for new tasks

Text to extract tasks from:
{text}
"""

QA_CONTEXT_PROMPT = """You are a helpful AI assistant that answers questions based solely on the provided context.

When answering:
1. Use ONLY information from the provided context
2. If you don't know or the context doesn't contain the answer, say "I don't have enough information to answer this question."
3. Cite the source of your information using the format [note_id:UUID] where UUID is the note ID
4. Be concise and direct
5. Format your answer in markdown when appropriate

Context:
{context}

Question:
{question}
"""


class TaskListSchema(BaseModel):
    """Schema for task list output"""
    tasks: List[TaskItem] = Field(description="List of extracted tasks")


def build_summarization_chain():
    """Build a LangChain for document summarization"""
    # Text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    
    # Map chain
    map_prompt = PromptTemplate.from_template(SUMMARIZE_MAP_PROMPT)
    map_chain = map_prompt | get_llm() | StrOutputParser()
    
    # Reduce chain
    reduce_prompt = PromptTemplate.from_template(SUMMARIZE_REDUCE_PROMPT)
    reduce_chain = reduce_prompt | get_llm() | StrOutputParser()
    
    # Function to process and format output
    def format_output(result: str) -> Dict[str, Any]:
        # Split sections based on markdown headers
        sections = result.split("##")
        
        summary = ""
        highlights = []
        decisions = []
        action_items = []
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split("\n")
            header = lines[0].strip().lower()
            content = [line.strip()[2:] for line in lines[1:] if line.strip().startswith("- ")]
            
            if "summary" in header:
                summary = " ".join(content)
                highlights = content
            elif "decision" in header:
                decisions = content
            elif "action" in header:
                action_items = content
        
        return {
            "summary": summary,
            "highlights": highlights,
            "decisions": decisions,
            "action_items": action_items,
        }
    
    # Build the full chain
    def run_chain(text: str) -> Dict[str, Any]:
        # Split text
        docs = text_splitter.create_documents([text])
        texts = [doc.page_content for doc in docs]
        
        # Map step
        summaries = []
        for doc_text in texts:
            summary = map_chain.invoke({"text": doc_text})
            summaries.append(summary)
        
        # Reduce step
        combined = reduce_chain.invoke({"summaries": "\n\n".join(summaries)})
        
        # Format output
        return format_output(combined)
    
    return run_chain


def build_task_chain():
    """Build a LangChain for task extraction"""
    # Output parser
    parser = JsonOutputParser(pydantic_object=TaskListSchema)
    
    # Create prompt (use tuple format so {text} is treated as a template variable)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a task extraction assistant that creates structured JSON output."),
        ("human", TASK_EXTRACT_PROMPT),
    ])
    
    # Build chain
    chain = prompt | get_llm() | parser
    
    # Define function to run chain
    def run_chain(text: str) -> Dict[str, List[TaskItem]]:
        result = chain.invoke({"text": text})
        return result
    
    return run_chain


def build_qa_chain(retriever):
    """Build a LangChain for question answering"""
    # Create prompt
    prompt = ChatPromptTemplate.from_template(QA_CONTEXT_PROMPT)
    
    # Format documents for context
    def format_docs(docs: List[Document]) -> str:
        formatted_docs = []
        for doc in docs:
            note_id = doc.metadata.get("note_id", "unknown")
            formatted_docs.append(f"[NOTE ID: {note_id}]\n{doc.page_content}\n")
        return "\n".join(formatted_docs)
    
    # Build retrieval chain
    retrieval_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | get_llm(temperature=0.1)
        | StrOutputParser()
    )
    
    # Define function to run chain
    def run_chain(query: str) -> str:
        return retrieval_chain.invoke(query)
    
    return run_chain
