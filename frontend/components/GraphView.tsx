"use client";

import { FC, useEffect, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import Cytoscape from 'cytoscape';
import { useRouter } from 'next/navigation';

// Define types for graph data
interface Node {
  id: string;
  label?: string;
  data?: any;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  weight?: number;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface GraphViewProps {
  data: GraphData;
  height?: string | number;
  onNodeClick?: (nodeId: string) => void;
}

export const GraphView: FC<GraphViewProps> = ({ 
  data, 
  height = '600px',
  onNodeClick
}) => {
  const router = useRouter();
  const cyRef = useRef<Cytoscape.Core | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [elements, setElements] = useState<any[]>([]);
  
  useEffect(() => {
    // Format data for Cytoscape
    const formattedElements = [
      // Nodes
      ...data.nodes.map(node => ({
        data: { 
          id: node.id, 
          label: node.label || `Note ${node.id.substring(0, 6)}...`,
          ...node.data
        }
      })),
      // Edges
      ...data.edges.map(edge => ({
        data: { 
          id: edge.id, 
          source: edge.source, 
          target: edge.target,
          weight: edge.weight || 1
        }
      }))
    ];
    
    setElements(formattedElements);
  }, [data]);
  
  const handleNodeClick = (event: Cytoscape.EventObject) => {
    const nodeId = event.target.id();
    if (onNodeClick) {
      onNodeClick(nodeId);
    } else {
      // Default behavior: navigate to note detail
      router.push(`/notes/${nodeId}`);
    }
  };
  
  return (
    <div ref={containerRef} style={{ height, width: '100%' }}>
      {elements.length > 0 && (
        <CytoscapeComponent
          elements={elements}
          style={{ width: '100%', height: '100%' }}
          cy={(cy) => {
            cyRef.current = cy;
            
            // Set up event handlers
            cy.on('tap', 'node', handleNodeClick);
            
            // Apply layout
            cy.layout({
              name: 'cose',
              idealEdgeLength: 100,
              nodeOverlap: 20,
              refresh: 20,
              fit: true,
              padding: 30,
              randomize: false,
              componentSpacing: 100,
              nodeRepulsion: 400000,
              edgeElasticity: 100,
              nestingFactor: 5,
              gravity: 80,
              numIter: 1000,
              initialTemp: 200,
              coolingFactor: 0.95,
              minTemp: 1.0
            }).run();
          }}
          stylesheet={[
            {
              selector: 'node',
              style: {
                'background-color': '#4299e1',
                'label': 'data(label)',
                'color': '#fff',
                'text-outline-color': '#2b6cb0',
                'text-outline-width': '1px',
                'font-size': '12px'
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 'data(weight)',
                'line-color': '#2d3748',
                'target-arrow-color': '#2d3748',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'opacity': 0.7
              }
            },
            {
              selector: ':selected',
              style: {
                'background-color': '#ed8936',
                'line-color': '#ed8936',
                'target-arrow-color': '#ed8936',
                'source-arrow-color': '#ed8936'
              }
            }
          ]}
        />
      )}
    </div>
  );
};
