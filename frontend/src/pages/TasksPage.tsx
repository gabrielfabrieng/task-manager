import { useState } from "react";
import { Filters } from "../components/Filters";
import { TaskForm } from "../components/TaskForm";
import { TaskItem } from "../components/TaskItem";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import type { TaskFilters } from "../types";

const PAGE_SIZE = 20;

export function TasksPage() {
  const { user, logout } = useAuth();
  const [filters, setFilters] = useState<TaskFilters>({ page: 1, ordering: "-created_at" });
  const { data, isLoading } = useTasks(filters);

  const patch = (p: Partial<TaskFilters>) => setFilters((f) => ({ ...f, ...p }));
  const totalPages = data ? Math.max(1, Math.ceil(data.count / PAGE_SIZE)) : 1;
  const page = filters.page ?? 1;

  return (
    <div className="container">
      <header className="topbar">
        <h1>Tasks</h1>
        <div>
          <span data-testid="current-user">{user?.username}</span>
          <button onClick={logout} data-testid="logout">Logout</button>
        </div>
      </header>

      <TaskForm />
      <Filters filters={filters} onChange={patch} />

      {isLoading ? (
        <p>Loading…</p>
      ) : (
        <ul className="task-list" data-testid="task-list">
          {data?.results.map((t) => <TaskItem key={t.id} task={t} />)}
          {data?.results.length === 0 && <li data-testid="empty">No tasks yet.</li>}
        </ul>
      )}

      <footer className="pagination" data-testid="pagination">
        <button disabled={page <= 1} onClick={() => patch({ page: page - 1 })} data-testid="prev-page">
          Prev
        </button>
        <span data-testid="page-info">
          Page {page} / {totalPages} · {data?.count ?? 0} total
        </span>
        <button
          disabled={page >= totalPages}
          onClick={() => patch({ page: page + 1 })}
          data-testid="next-page"
        >
          Next
        </button>
      </footer>
    </div>
  );
}
