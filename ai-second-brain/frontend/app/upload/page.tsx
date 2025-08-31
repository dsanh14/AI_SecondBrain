"use client";

import { useState } from 'react';
import { UploadForm } from '@/components/UploadForm';
import { SummarizeOut, TaskExtractOut, NoteEmbedResponse } from '@/lib/types';

export default function UploadPage() {
  const [summary, setSummary] = useState<SummarizeOut | null>(null);
  const [tasks, setTasks] = useState<TaskExtractOut | null>(null);
  const [embedResult, setEmbedResult] = useState<NoteEmbedResponse | null>(null);
  
  const handleSummaryGenerated = (data: SummarizeOut) => {
    setSummary(data);
  };
  
  const handleTasksExtracted = (data: TaskExtractOut) => {
    setTasks(data);
  };
  
  const handleNoteEmbedded = (data: NoteEmbedResponse) => {
    setEmbedResult(data);
  };
  
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Upload & Process</h1>
      
      <UploadForm 
        onSummaryGenerated={handleSummaryGenerated}
        onTasksExtracted={handleTasksExtracted}
        onNoteEmbedded={handleNoteEmbedded}
      />
      
      {summary && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Summary</h2>
          <div className="prose prose-invert max-w-none">
            <p className="mb-4">{summary.summary}</p>
            
            {summary.highlights.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Highlights</h3>
                <ul>
                  {summary.highlights.map((highlight, index) => (
                    <li key={index}>{highlight}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {summary.decisions.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Decisions</h3>
                <ul>
                  {summary.decisions.map((decision, index) => (
                    <li key={index}>{decision}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {summary.action_items.length > 0 && (
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Action Items</h3>
                <ul>
                  {summary.action_items.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
      
      {tasks && tasks.tasks.length > 0 && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Extracted Tasks</h2>
          <div className="space-y-2">
            {tasks.tasks.map((task, index) => (
              <div key={index} className="p-3 bg-gray-800 rounded-md">
                <div className="font-medium">{task.description}</div>
                <div className="flex gap-4 mt-1 text-sm text-gray-400">
                  {task.due_date && <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>}
                  {task.owner && <span>Owner: {task.owner}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {embedResult && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Embedding Results</h2>
          <p className="mb-2">Chunks indexed: {embedResult.chunks_indexed}</p>
          <p className="mb-2">Semantic links created: {embedResult.links.length}</p>
          
          {embedResult.links.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2">Links</h3>
              <div className="space-y-2">
                {embedResult.links.map((link, index) => (
                  <div key={index} className="p-2 bg-gray-800 rounded-md text-sm">
                    <div>Source: {link.source_note}</div>
                    <div>Target: {link.target_note}</div>
                    <div>Similarity: {(link.similarity * 100).toFixed(1)}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
