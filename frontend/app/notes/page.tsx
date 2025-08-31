"use client";

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { NoteCard } from '@/components/NoteCard';
import { api } from '@/lib/api';

export default function NotesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  
  const { 
    data: notes = [], 
    isLoading
  } = useQuery({
    queryKey: ['notes'],
    queryFn: () => api.getNotes(),
  });
  
  // Filter notes based on search query (client-side)
  const filteredNotes = searchQuery
    ? notes.filter(note => 
        note.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.body.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : notes;
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Notes</h1>
      
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search notes..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full p-3 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      {isLoading ? (
        <div className="text-gray-400">Loading notes...</div>
      ) : filteredNotes.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredNotes.map(note => (
            <NoteCard key={note.id} note={note} showBody />
          ))}
        </div>
      ) : (
        <div className="text-gray-400 text-center py-8">
          {searchQuery ? 'No notes match your search' : 'No notes found'}
        </div>
      )}
    </div>
  );
}
