"use client";

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { format } from 'date-fns';
import { TaskList } from '@/components/TaskList';
import { api } from '@/lib/api';

export default function NoteDetailPage() {
  const params = useParams();
  const noteId = params.id as string;
  
  const { 
    data: note, 
    isLoading,
    error
  } = useQuery({
    queryKey: ['note', noteId],
    queryFn: () => api.getNote(noteId),
    enabled: !!noteId,
  });
  
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'PPP p');
  };
  
  // Handle loading state
  if (isLoading) {
    return <div className="text-gray-400 py-8 text-center">Loading note...</div>;
  }
  
  // Handle error state
  if (error || !note) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-6 text-center">
        <h1 className="text-2xl font-bold text-red-300 mb-4">Error Loading Note</h1>
        <p className="text-red-200 mb-4">
          {error instanceof Error ? error.message : "Failed to load note"}
        </p>
        <Link href="/notes" className="text-blue-400 hover:underline">
          ← Back to Notes
        </Link>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <Link href="/notes" className="text-blue-400 hover:underline">
          ← Back to Notes
        </Link>
        <div className="text-sm text-gray-400">
          {formatDate(note.created_at)}
        </div>
      </div>
      
      <div className="bg-gray-900 rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-6">{note.title || 'Untitled Note'}</h1>
        
        <div className="prose prose-invert max-w-none">
          {note.body.split('\n').map((line, i) => (
            <p key={i}>{line}</p>
          ))}
        </div>
      </div>
      
      {note.tasks.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Tasks</h2>
          <TaskList tasks={note.tasks} onTaskUpdate={() => {}} />
        </div>
      )}
      
      {note.related_links.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Related Notes</h2>
          <div className="space-y-2">
            {note.related_links.map((link) => (
              <Link 
                key={link.target_note} 
                href={`/notes/${link.target_note}`}
                className="block p-3 bg-gray-800 hover:bg-gray-750 rounded-md"
              >
                <div className="flex justify-between items-center">
                  <span>{link.target_note}</span>
                  <span className="text-sm text-gray-400">
                    Similarity: {(link.similarity * 100).toFixed(1)}%
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
