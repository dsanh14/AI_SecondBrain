"use client";

import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { GraphView } from '@/components/GraphView';
import { api } from '@/lib/api';

interface GraphData {
  nodes: { id: string; label?: string }[];
  edges: { id: string; source: string; target: string; weight?: number }[];
}

export default function GraphPage() {
  const [graphData, setGraphData] = useState<GraphData>({
    nodes: [],
    edges: []
  });
  
  // Fetch notes to build graph data
  const { data: notes = [], isLoading } = useQuery({
    queryKey: ['notes'],
    queryFn: () => api.getNotes({ limit: 100 }),
  });
  
  // Convert notes and their links to graph data format
  useEffect(() => {
    if (notes.length > 0) {
      // This is simulating what would normally come from a backend endpoint
      // In a real application, you might have a dedicated API for graph data
      
      // Create set of all node IDs to avoid duplicates
      const nodeIds = new Set<string>();
      const edges: { id: string; source: string; target: string; weight: number }[] = [];
      
      // For this demo, we'll create a simple graph structure
      // In a real app, this would come from the actual note relationships
      notes.forEach((note) => {
        nodeIds.add(note.id);
        
        // In a real app, we'd get actual links data from the API
        // Here we're just creating some dummy links between consecutive notes
        if (notes.length > 1) {
          const targetIndex = Math.floor(Math.random() * notes.length);
          const targetNote = notes[targetIndex];
          
          if (targetNote && targetNote.id !== note.id) {
            edges.push({
              id: `${note.id}-${targetNote.id}`,
              source: note.id,
              target: targetNote.id,
              weight: 0.5 + Math.random() * 0.5
            });
          }
        }
      });
      
      // Convert node IDs to graph nodes with labels
      const nodes = Array.from(nodeIds).map(id => {
        const note = notes.find(n => n.id === id);
        return {
          id,
          label: note?.title || `Note ${id.substring(0, 6)}...`
        };
      });
      
      setGraphData({ nodes, edges });
    }
  }, [notes]);
  
  if (isLoading) {
    return <div className="text-gray-400 py-8 text-center">Loading graph data...</div>;
  }
  
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Knowledge Graph</h1>
      
      <p className="text-gray-300">
        Visual representation of semantic connections between your notes.
      </p>
      
      <div className="bg-gray-900 rounded-lg p-4 h-[calc(100vh-250px)] min-h-[500px]">
        <GraphView data={graphData} />
      </div>
      
      <div className="text-sm text-gray-400">
        <p>Click on any node to open the corresponding note.</p>
      </div>
    </div>
  );
}
