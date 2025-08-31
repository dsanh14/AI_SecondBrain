"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { NoteCard } from "@/components/NoteCard";
import { TaskList } from "@/components/TaskList";
import { api } from "@/lib/api";

export default function Home() {
  const [text, setText] = useState("");
  
  // Fetch recent notes
  const { 
    data: notes = [], 
    isLoading: notesLoading 
  } = useQuery({
    queryKey: ["notes", { limit: 5 }],
    queryFn: () => api.getNotes({ limit: 5 }),
  });
  
  // Fetch open tasks
  const { 
    data: tasks = [], 
    isLoading: tasksLoading,
    refetch: refetchTasks
  } = useQuery({
    queryKey: ["tasks", { completed: false }],
    queryFn: () => api.getTasks({ completed: false }),
  });
  
  // Quick summarize handler
  const handleQuickSummarize = async () => {
    if (!text.trim()) return;
    
    try {
      const result = await api.summarize({ text });
      console.log("Summary:", result);
      // In a real app, you would save this as a note or display it
      alert(`Summarized! ${result.summary.substring(0, 50)}...`);
    } catch (error) {
      console.error("Error summarizing:", error);
    }
  };
  
  return (
    <div className="space-y-8">
      <section className="bg-gray-900 p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">Quick Upload</h2>
        <div className="space-y-4">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="w-full h-32 p-3 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter or paste text here..."
          />
          <div className="flex gap-2">
            <button
              onClick={handleQuickSummarize}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md"
            >
              Summarize
            </button>
            <Link
              href="/upload"
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md"
            >
              Advanced Upload
            </Link>
          </div>
        </div>
      </section>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <section>
          <h2 className="text-2xl font-bold mb-4">Recent Notes</h2>
          {notesLoading ? (
            <div className="text-gray-400">Loading notes...</div>
          ) : notes.length > 0 ? (
            <div className="space-y-4">
              {notes.map((note) => (
                <NoteCard key={note.id} note={note} />
              ))}
            </div>
          ) : (
            <div className="text-gray-400">No notes found</div>
          )}
        </section>
        
        <section>
          <h2 className="text-2xl font-bold mb-4">Open Tasks</h2>
          {tasksLoading ? (
            <div className="text-gray-400">Loading tasks...</div>
          ) : tasks.length > 0 ? (
            <TaskList tasks={tasks} onTaskUpdate={() => refetchTasks()} />
          ) : (
            <div className="text-gray-400">No open tasks</div>
          )}
        </section>
      </div>
    </div>
  );
}
