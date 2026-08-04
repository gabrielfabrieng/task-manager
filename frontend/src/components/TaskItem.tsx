import { useState } from "react";
import { useTaskMutations } from "../hooks/useTasks";
import type { Task } from "../types";
import { ShareDialog } from "./ShareDialog";

export function TaskItem({ task }: { task: Task }) {
  const { toggle, remove } = useTaskMutations();
  const [sharing, setSharing] = useState(false);

  return (
    <li className={`task ${task.is_done ? "done" : ""}`} data-testid="task-item">
      <input
        type="checkbox"
        data-testid="task-toggle"
        checked={task.is_done}
        onChange={(e) => toggle.mutate({ id: task.id, done: e.target.checked })}
      />
      <span className="task-title" data-testid="task-item-title">{task.title}</span>
      {task.shares.length > 0 && (
        <span className="badge" title="Shared">↔ {task.shares.length}</span>
      )}
      <div className="task-actions">
        <button onClick={() => setSharing(true)} data-testid="task-share">Share</button>
        <button onClick={() => remove.mutate(task.id)} data-testid="task-delete">Delete</button>
      </div>
      {sharing && <ShareDialog taskId={task.id} onClose={() => setSharing(false)} />}
    </li>
  );
}
