"use client";

import { FC, useState } from 'react';
import { api } from '@/lib/api';
import { SearchOut, CitationInfo } from '@/lib/types';
import Link from 'next/link';

interface SearchBoxProps {
  initialQuery?: string;
  onResultsChange?: (results: SearchOut | null) => void;
}

export const SearchBox: FC<SearchBoxProps> = ({
  initialQuery = '',
  onResultsChange
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<SearchOut | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleSearch = async () => {
    if (!query.trim()) return;
    
    try {
      setIsSearching(true);
      setError(null);
      
      const searchResults = await api.search({ query });
      
      setResults(searchResults);
      if (onResultsChange) {
        onResultsChange(searchResults);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to perform search. Please try again.');
      setResults(null);
      if (onResultsChange) {
        onResultsChange(null);
      }
    } finally {
      setIsSearching(false);
    }
  };
  
  // Replace citations in text with links
  const renderAnswerWithCitations = (answer: string, citations: CitationInfo[]) => {
    if (!citations || citations.length === 0) {
      return <p>{answer}</p>;
    }
    
    let result = answer;
    const segments = [];
    let lastIndex = 0;
    
    // Sort citations by their position in the text
    const citationRegex = /\[note_id:([0-9a-fA-F-]+)\]/g;
    let match;
    
    while ((match = citationRegex.exec(answer)) !== null) {
      const noteId = match[1];
      const startIndex = match.index;
      const endIndex = startIndex + match[0].length;
      
      // Add text before the citation
      if (startIndex > lastIndex) {
        segments.push(
          <span key={`text-${lastIndex}`}>
            {answer.substring(lastIndex, startIndex)}
          </span>
        );
      }
      
      // Add the citation as a link
      segments.push(
        <Link
          href={`/notes/${noteId}`}
          key={`citation-${startIndex}`}
          className="inline-block bg-blue-900 text-blue-200 px-1.5 py-0.5 rounded text-xs mx-1 hover:bg-blue-800"
        >
          [{noteId.substring(0, 8)}]
        </Link>
      );
      
      lastIndex = endIndex;
    }
    
    // Add any remaining text
    if (lastIndex < answer.length) {
      segments.push(
        <span key={`text-${lastIndex}`}>
          {answer.substring(lastIndex)}
        </span>
      );
    }
    
    return <div className="space-y-4">{segments}</div>;
  };
  
  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Ask any question about your knowledge base..."
          className="flex-1 p-3 bg-gray-800 text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
          disabled={isSearching}
        />
        <button
          onClick={handleSearch}
          disabled={!query.trim() || isSearching}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>
      
      {error && (
        <div className="p-4 bg-red-900/40 border border-red-700 rounded-lg text-red-200">
          {error}
        </div>
      )}
      
      {results && (
        <div className="bg-gray-900 rounded-lg p-6">
          <h3 className="font-semibold text-xl mb-4">Answer</h3>
          <div className="prose prose-invert max-w-none">
            {renderAnswerWithCitations(results.answer, results.citations)}
          </div>
          
          {results.citations.length > 0 && (
            <div className="mt-6 pt-4 border-t border-gray-700">
              <h4 className="font-medium text-gray-300 mb-2">Citations</h4>
              <div className="space-y-2">
                {results.citations.map((citation, index) => (
                  <div key={`${citation.note_id}-${index}`} className="p-3 bg-gray-800 rounded-md">
                    <Link
                      href={`/notes/${citation.note_id}`}
                      className="font-mono text-xs text-blue-400 hover:underline"
                    >
                      {citation.note_id}
                    </Link>
                    <p className="mt-1 text-sm text-gray-400">
                      {citation.snippet}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
