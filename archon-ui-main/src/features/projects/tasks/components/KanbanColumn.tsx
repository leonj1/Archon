import { useRef } from "react";
import { useDrop } from "react-dnd";
import { cn } from "../../../ui/primitives/styles";
import type { Task } from "../types";
import { getColumnColor, getColumnGlow, ItemTypes } from "../utils/task-styles";
import { TaskCard } from "./TaskCard";

interface KanbanColumnProps {
  status: Task["status"];
  title: string;
  tasks: Task[];
  projectId: string;
  onTaskMove: (taskId: string, newStatus: Task["status"]) => void;
  onTaskReorder: (taskId: string, targetIndex: number, status: Task["status"]) => void;
  onTaskEdit?: (task: Task) => void;
  onTaskDelete?: (task: Task) => void;
  hoveredTaskId: string | null;
  onTaskHover: (taskId: string | null) => void;
}

export const KanbanColumn = ({
  status,
  title,
  tasks,
  projectId,
  onTaskMove,
  onTaskReorder,
  onTaskEdit,
  onTaskDelete,
  hoveredTaskId,
  onTaskHover,
}: KanbanColumnProps) => {
  const ref = useRef<HTMLDivElement>(null);

  const [, drop] = useDrop({
    accept: ItemTypes.TASK,
    drop: (item: { id: string; status: Task["status"] }) => {
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
  });

  drop(ref);

  return (
    <div ref={ref} className="flex flex-col h-full">
      {/* Column Header - transparent with colored underline */}
      <div className="text-center py-3 relative">
        <h3 className={cn("font-mono text-sm font-medium", getColumnColor(status))}>{title}</h3>
        <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">{tasks.length}</div>
        {/* Colored underline */}
        <div
          className={cn(
            "absolute bottom-0 left-[15%] right-[15%] w-[70%] mx-auto h-[1px]",
            getColumnGlow(status),
            "shadow-md",
          )}
        />
      </div>

      {/* Tasks Container */}
      <div className="px-2 flex-1 overflow-y-auto space-y-2 py-3 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
        {tasks.map((task, index) => (
          <TaskCard
            key={task.id}
            task={task}
            index={index}
            projectId={projectId}
            onTaskReorder={onTaskReorder}
            onEdit={onTaskEdit}
            onTaskDelete={onTaskDelete}
            hoveredTaskId={hoveredTaskId}
            onTaskHover={onTaskHover}
          />
        ))}
      </div>
    </div>
  );
};
