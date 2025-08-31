import { FC, useState } from 'react';
import { format } from 'date-fns';
import { TaskItem } from '@/lib/types';
import { api } from '@/lib/api';

interface TaskListProps {
  tasks: TaskItem[];
  onTaskUpdate?: () => void;
}

export const TaskList: FC<TaskListProps> = ({ tasks, onTaskUpdate }) => {
  const [updating, setUpdating] = useState<string | null>(null);
  
  const handleTaskToggle = async (taskId: string, completed: boolean) => {
    try {
      setUpdating(taskId);
      await api.updateTask(taskId, { completed });
      if (onTaskUpdate) {
        onTaskUpdate();
      }
    } catch (error) {
      console.error('Error updating task:', error);
    } finally {
      setUpdating(null);
    }
  };
  
  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <div 
          key={task.source_note_id + task.description} 
          className="flex items-start gap-3 p-3 rounded-md bg-gray-800 hover:bg-gray-750"
        >
          <div className="flex-shrink-0 pt-0.5">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleTaskToggle(task.source_note_id as string, !task.completed)}
              disabled={updating === task.source_note_id}
              className="h-5 w-5 rounded border-gray-600 text-blue-600 focus:ring-blue-600"
            />
          </div>
          
          <div className="flex-1 min-w-0">
            <p className={`text-sm ${task.completed ? 'line-through text-gray-500' : 'text-gray-100'}`}>
              {task.description}
            </p>
            
            <div className="flex gap-3 mt-1 text-xs text-gray-400">
              {task.due_date && (
                <span>
                  Due: {format(new Date(task.due_date), 'MMM d, yyyy')}
                </span>
              )}
              
              {task.owner && (
                <span>
                  Owner: {task.owner}
                </span>
              )}
              
              {task.source_note_id && (
                <span className="truncate">
                  <a href={`/notes/${task.source_note_id}`} className="hover:text-blue-400 hover:underline">
                    Source
                  </a>
                </span>
              )}
            </div>
          </div>
        </div>
      ))}
      
      {tasks.length === 0 && (
        <p className="text-gray-400 text-center py-4">No tasks found</p>
      )}
    </div>
  );
};
