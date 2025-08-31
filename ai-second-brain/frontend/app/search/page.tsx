"use client";

import { useState } from 'react';
import { SearchBox } from '@/components/SearchBox';
import { SearchOut } from '@/lib/types';

export default function SearchPage() {
  const [searchResults, setSearchResults] = useState<SearchOut | null>(null);
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Semantic Search & Q&A</h1>
      
      <p className="text-gray-300">
        Ask questions about your knowledge base and get answers with citations from your notes.
      </p>
      
      <SearchBox 
        onResultsChange={setSearchResults}
      />
    </div>
  );
}
