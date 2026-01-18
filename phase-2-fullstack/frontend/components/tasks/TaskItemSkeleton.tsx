// components/tasks/TaskItemSkeleton.tsx
import React from 'react';

export const TaskItemSkeleton: React.FC = () => {
  return (
    <div className="p-4 border rounded-md shadow-sm bg-white">
      <div className="flex items-start justify-between animate-pulse">
        <div className="flex-grow">
          <div className="h-6 bg-gray-200 rounded w-3/4"></div>
          <div className="mt-2 h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="ml-4 h-5 w-5 bg-gray-200 rounded"></div>
      </div>
      <div className="flex justify-between text-xs text-gray-400 mt-4 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        <div className="h-4 bg-gray-200 rounded w-1/4"></div>
      </div>
    </div>
  );
};
