import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTask,
  deleteTask,
  fetchCategories,
  fetchTasks,
  setTaskStatus,
  shareTask,
  updateTask,
} from "../api/endpoints";
import type { SharePermission, Task, TaskFilters } from "../types";

const TASKS_KEY = "tasks";

export function useTasks(filters: TaskFilters) {
  return useQuery({
    queryKey: [TASKS_KEY, filters],
    queryFn: () => fetchTasks(filters),
    placeholderData: (prev) => prev, // keep page visible while refetching
  });
}

export function useCategories() {
  return useQuery({ queryKey: ["categories"], queryFn: fetchCategories });
}

/** All task mutations invalidate the task list so the UI stays consistent. */
export function useTaskMutations() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: [TASKS_KEY] });

  return {
    create: useMutation({ mutationFn: (p: Partial<Task>) => createTask(p), onSuccess: invalidate }),
    update: useMutation({
      mutationFn: ({ id, patch }: { id: number; patch: Partial<Task> }) => updateTask(id, patch),
      onSuccess: invalidate,
    }),
    remove: useMutation({ mutationFn: (id: number) => deleteTask(id), onSuccess: invalidate }),
    toggle: useMutation({
      mutationFn: ({ id, done }: { id: number; done: boolean }) => setTaskStatus(id, done),
      onSuccess: invalidate,
    }),
    share: useMutation({
      mutationFn: ({ id, email, permission }: { id: number; email: string; permission: SharePermission }) =>
        shareTask(id, email, permission),
      onSuccess: invalidate,
    }),
  };
}
