import { z } from 'zod';
import {
  NoteOut,
  NoteDetailOut,
  TaskItem,
  SearchOut,
  SummarizeOut,
  NoteEmbedResponse
} from './types';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Zod schemas for runtime validation
const taskItemSchema = z.object({
  description: z.string(),
  due_date: z.string().nullable().optional(),
  owner: z.string().nullable().optional(),
  source_note_id: z.string().uuid().nullable().optional(),
  completed: z.boolean().default(false),
});

const noteOutSchema = z.object({
  id: z.string().uuid(),
  title: z.string().nullable().optional(),
  body: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
});

const linkInfoSchema = z.object({
  source_note: z.string().uuid(),
  target_note: z.string().uuid(),
  similarity: z.number(),
});

const citationInfoSchema = z.object({
  note_id: z.string().uuid(),
  snippet: z.string(),
});

const searchOutSchema = z.object({
  answer: z.string(),
  citations: z.array(citationInfoSchema),
});

const summarizeOutSchema = z.object({
  summary: z.string(),
  highlights: z.array(z.string()),
  decisions: z.array(z.string()),
  action_items: z.array(z.string()),
});

const noteEmbedResponseSchema = z.object({
  chunks_indexed: z.number(),
  links: z.array(linkInfoSchema),
});

const noteDetailOutSchema = noteOutSchema.extend({
  tasks: z.array(taskItemSchema),
  related_links: z.array(linkInfoSchema),
});

// Helper function to make API calls
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  schema?: z.ZodType<T>
): Promise<T> {
  const url = `${BACKEND_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }
  
  const data = await response.json();
  
  // Validate response if schema is provided
  if (schema) {
    try {
      return schema.parse(data);
    } catch (error) {
      console.error('Response validation error:', error);
      throw new Error('Invalid response from API');
    }
  }
  
  return data as T;
}

// API client functions
export const api = {
  // Notes
  getNotes: async ({ skip = 0, limit = 20 } = {}) => {
    return apiFetch<NoteOut[]>(
      `/notes?skip=${skip}&limit=${limit}`,
      { method: 'GET' },
      z.array(noteOutSchema)
    );
  },
  
  getNote: async (noteId: string) => {
    return apiFetch<NoteDetailOut>(
      `/notes/${noteId}`,
      { method: 'GET' },
      noteDetailOutSchema
    );
  },
  
  createNote: async (data: { title?: string; body: string }) => {
    return apiFetch<NoteOut>(
      '/notes',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      noteOutSchema
    );
  },
  
  embedNote: async (data: { note_id: string; text: string; meta?: Record<string, any> }) => {
    return apiFetch<NoteEmbedResponse>(
      '/notes/embed',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      noteEmbedResponseSchema
    );
  },
  
  // Tasks
  getTasks: async ({ completed, limit = 50, offset = 0 } = {}) => {
    let url = `/tasks?limit=${limit}&offset=${offset}`;
    if (completed !== undefined) {
      url += `&completed=${completed}`;
    }
    
    return apiFetch<TaskItem[]>(
      url,
      { method: 'GET' },
      z.array(taskItemSchema)
    );
  },
  
  extractTasks: async (data: { text: string; source_note_id?: string }) => {
    return apiFetch<{ tasks: TaskItem[] }>(
      '/tasks/extract',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      z.object({ tasks: z.array(taskItemSchema) })
    );
  },
  
  updateTask: async (taskId: string, data: { completed?: boolean }) => {
    return apiFetch<TaskItem>(
      `/tasks/${taskId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      },
      taskItemSchema
    );
  },
  
  // Search
  search: async (data: { query: string; k?: number }) => {
    return apiFetch<SearchOut>(
      '/search/query',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      searchOutSchema
    );
  },
  
  // Summarize
  summarize: async (data: { text: string }) => {
    return apiFetch<SummarizeOut>(
      '/summarize',
      {
        method: 'POST',
        body: JSON.stringify(data),
      },
      summarizeOutSchema
    );
  },
};
