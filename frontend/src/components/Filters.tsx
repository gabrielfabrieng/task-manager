import type { TaskFilters, TaskStatus } from "../types";

interface Props {
  filters: TaskFilters;
  onChange: (patch: Partial<TaskFilters>) => void;
}

export function Filters({ filters, onChange }: Props) {
  return (
    <div className="filters" data-testid="filters">
      <input
        data-testid="filter-search"
        placeholder="Search…"
        value={filters.search ?? ""}
        onChange={(e) => onChange({ search: e.target.value, page: 1 })}
      />
      <select
        data-testid="filter-status"
        value={filters.status ?? ""}
        onChange={(e) => onChange({ status: e.target.value as TaskStatus | "", page: 1 })}
      >
        <option value="">All</option>
        <option value="pending">Pending</option>
        <option value="done">Done</option>
      </select>
      <select
        data-testid="filter-ordering"
        value={filters.ordering ?? "-created_at"}
        onChange={(e) => onChange({ ordering: e.target.value, page: 1 })}
      >
        <option value="-created_at">Newest</option>
        <option value="created_at">Oldest</option>
        <option value="due_date">Due date</option>
        <option value="title">Title</option>
      </select>
    </div>
  );
}
