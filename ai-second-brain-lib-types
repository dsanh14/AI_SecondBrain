// Shared types for frontend

export interface TaskItem {
  description: string;
  due_date?: string; // ISO date string
  owner?: string;
  source_note_id?: string; // UUID
  completed: boolean;
}

export interface NoteOut {
  id: string; // UUID
  title?: string;
  body: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

export interface NoteDetailOut extends NoteOut {
  tasks: TaskItem[];
  related_links: LinkInfo[];
}

export interface LinkInfo {
  source_note: string; // UUID
  target_note: string; // UUID
  similarity: number;
}

export interface CitationInfo {
  note_id: string; // UUID
  snippet: string;
}

export interface SearchOut {
  answer: string;
  citations: CitationInfo[];
}

export interface SummarizeOut {
  summary: string;
  highlights: string[];
  decisions: string[];
  action_items: string[];
}

export interface NoteEmbedResponse {
  chunks_indexed: number;
  links: LinkInfo[];
}

// Input types
export interface SearchIn {
  query: string;
  k?: number;
}

export interface SummarizeIn {
  text: string;
}

export interface TaskExtractIn {
  text: string;
  source_note_id?: string; // UUID
}

export interface NoteIn {
  note_id: string; // UUID
  text: string;
  meta?: Record<string, any>;
}
