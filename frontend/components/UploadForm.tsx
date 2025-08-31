"use client";

import { FC, useState, useRef, FormEvent, ChangeEvent } from 'react';
import { api } from '@/lib/api';

interface UploadFormProps {
  onSummaryGenerated?: (data: any) => void;
  onTasksExtracted?: (data: any) => void;
  onNoteEmbedded?: (data: any) => void;
}

export const UploadForm: FC<UploadFormProps> = ({
  onSummaryGenerated,
  onTasksExtracted,
  onNoteEmbedded
}) => {
  const [text, setText] = useState('');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [noteId, setNoteId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Handle text input change
  const handleTextChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };
  
  // Handle audio file selection
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setAudioFile(e.target.files[0]);
    }
  };
  
  // Handle audio transcription
  const handleTranscribe = async () => {
    if (!audioFile) return;
    
    try {
      setIsProcessing(true);
      setCurrentStep('transcribing');
      
      const formData = new FormData();
      formData.append('file', audioFile);
      
      // This would typically call the transcription API
      // For demo purposes, we'll simulate a delay and response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Placeholder for real transcription
      const transcription = `Transcribed content from ${audioFile.name}. 
      
This is a sample transcription that would normally come from the Whisper API.
      
Key points:
- We should prioritize the new feature for Q3
- User testing showed positive results for the prototype
- Budget needs to be adjusted by 15% to accommodate changes

Let's schedule a follow-up meeting next week to discuss implementation details.`;
      
      setText(transcription);
      setCurrentStep(null);
    } catch (error) {
      console.error('Transcription error:', error);
      alert('Failed to transcribe audio');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Handle summarization
  const handleSummarize = async () => {
    if (!text.trim()) return;
    
    try {
      setIsProcessing(true);
      setCurrentStep('summarizing');
      
      const result = await api.summarize({ text });
      
      if (onSummaryGenerated) {
        onSummaryGenerated(result);
      }
      
      setCurrentStep(null);
    } catch (error) {
      console.error('Summarization error:', error);
      alert('Failed to summarize text');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Handle task extraction
  const handleExtractTasks = async () => {
    if (!text.trim()) return;
    
    try {
      setIsProcessing(true);
      setCurrentStep('extractingTasks');
      
      const result = await api.extractTasks({ 
        text, 
        source_note_id: noteId || undefined 
      });
      
      if (onTasksExtracted) {
        onTasksExtracted(result);
      }
      
      setCurrentStep(null);
    } catch (error) {
      console.error('Task extraction error:', error);
      alert('Failed to extract tasks');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Handle embedding and linking
  const handleEmbedAndLink = async () => {
    if (!text.trim() || !noteId) return;
    
    try {
      setIsProcessing(true);
      setCurrentStep('embedding');
      
      const result = await api.embedNote({
        note_id: noteId,
        text,
        meta: {}
      });
      
      if (onNoteEmbedded) {
        onNoteEmbedded(result);
      }
      
      setCurrentStep(null);
    } catch (error) {
      console.error('Embedding error:', error);
      alert('Failed to embed and link note');
    } finally {
      setIsProcessing(false);
    }
  };
  
  // Reset form
  const handleReset = () => {
    setText('');
    setAudioFile(null);
    setCurrentStep(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <div className="bg-gray-900 rounded-lg p-6 space-y-6">
      {/* Audio file upload */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Audio File (Optional)
        </label>
        <div className="flex items-center gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="audio/*"
            className="block w-full text-sm text-gray-400
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-gray-700 file:text-white
              hover:file:bg-gray-600"
            disabled={isProcessing}
          />
          {audioFile && (
            <button
              onClick={handleTranscribe}
              disabled={isProcessing}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
            >
              {currentStep === 'transcribing' ? 'Transcribing...' : 'Transcribe'}
            </button>
          )}
        </div>
      </div>
      
      {/* Text content */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Text Content
        </label>
        <textarea
          value={text}
          onChange={handleTextChange}
          rows={8}
          className="w-full p-3 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter or paste text content here, or upload an audio file to transcribe..."
          disabled={isProcessing}
        />
      </div>
      
      {/* Note ID input for embedding */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Note ID (Required for embedding)
        </label>
        <input
          type="text"
          value={noteId || ''}
          onChange={(e) => setNoteId(e.target.value)}
          className="w-full p-3 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter note UUID to use for embedding..."
          disabled={isProcessing}
        />
      </div>
      
      {/* Action buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleSummarize}
          disabled={!text.trim() || isProcessing}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {currentStep === 'summarizing' ? 'Summarizing...' : 'Summarize'}
        </button>
        
        <button
          onClick={handleExtractTasks}
          disabled={!text.trim() || isProcessing}
          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
        >
          {currentStep === 'extractingTasks' ? 'Extracting Tasks...' : 'Extract Tasks'}
        </button>
        
        <button
          onClick={handleEmbedAndLink}
          disabled={!text.trim() || !noteId || isProcessing}
          className="px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 disabled:opacity-50"
        >
          {currentStep === 'embedding' ? 'Embedding...' : 'Embed & Link'}
        </button>
        
        <button
          onClick={handleReset}
          disabled={isProcessing}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
        >
          Reset
        </button>
      </div>
    </div>
  );
};
