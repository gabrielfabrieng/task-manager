import { FormEvent, useState } from "react";
import { useCategories, useTaskMutations } from "../hooks/useTasks";
import { taskSchema } from "../lib/validation";

export function TaskForm() {
  const { create } = useTaskMutations();
  const { data: categories } = useCategories();
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<number | "">("");
  const [error, setError] = useState<string | null>(null);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const parsed = taskSchema.safeParse({ title, category: category || null });
    if (!parsed.success) {
      setError(parsed.error.errors[0].message);
      return;
    }
    create.mutate(
      { title, category: category === "" ? null : category },
      { onSuccess: () => setTitle("") },
    );
    setError(null);
  }

  return (
    <form onSubmit={onSubmit} className="task-form" data-testid="task-form">
      <input
        data-testid="task-title"
        placeholder="New task…"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <select
        data-testid="task-category"
        value={category}
        onChange={(e) => setCategory(e.target.value ? Number(e.target.value) : "")}
      >
        <option value="">No category</option>
        {categories?.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name}
          </option>
        ))}
      </select>
      <button type="submit" data-testid="task-add" disabled={create.isPending}>
        Add
      </button>
      {error && <span className="error">{error}</span>}
    </form>
  );
}
