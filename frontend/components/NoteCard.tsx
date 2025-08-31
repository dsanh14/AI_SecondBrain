import { FC } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { NoteOut } from '@/lib/types';

interface NoteCardProps {
  note: NoteOut;
  showBody?: boolean;
}

export const NoteCard: FC<NoteCardProps> = ({ note, showBody = false }) => {
  // Generate display title from note (use title or first line of body)
  const displayTitle = note.title || note.body.split('\n')[0] || 'Untitled Note';
  
  // Format date as "X days/minutes ago"
  const formattedDate = formatDistanceToNow(new Date(note.created_at), { addSuffix: true });
  
  return (
    <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-750 transition">
      <Link href={`/notes/${note.id}`} className="block">
        <h3 className="text-lg font-semibold text-white mb-1 truncate">
          {displayTitle}
        </h3>
        <div className="text-xs text-gray-400 mb-2">
          {formattedDate}
        </div>
        
        {showBody && (
          <div className="text-sm text-gray-300 line-clamp-3 mt-2">
            {note.body}
          </div>
        )}
      </Link>
    </div>
  );
};
