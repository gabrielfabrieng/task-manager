import { api, tokenStore } from "./client";
import type {
  Category,
  Paginated,
  SharePermission,
  Task,
  TaskFilters,
  User,
} from "../types";

// ---- Auth ----
export async function login(username: string, password: string): Promise<void> {
  const { data } = await api.post("/auth/login/", { username, password });
  tokenStore.set(data.access, data.refresh);
}

export async function register(
  username: string,
  email: string,
  password: string,
): Promise<User> {
  const { data } = await api.post<User>("/auth/register/", { username, email, password });
  return data;
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/auth/me/");
  return data;
}

// ---- Tasks ----
export async function fetchTasks(filters: TaskFilters): Promise<Paginated<Task>> {
  const params: Record<string, string | number> = {};
  if (filters.status) params.status = filters.status;
  if (filters.category) params.category = filters.category;
  if (filters.search) params.search = filters.search;
  if (filters.ordering) params.ordering = filters.ordering;
  params.page = filters.page ?? 1;
  const { data } = await api.get<Paginated<Task>>("/tasks/", { params });
  return data;
}

export async function createTask(payload: Partial<Task>): Promise<Task> {
  const { data } = await api.post<Task>("/tasks/", payload);
  return data;
}

export async function updateTask(id: number, payload: Partial<Task>): Promise<Task> {
  const { data } = await api.patch<Task>(`/tasks/${id}/`, payload);
  return data;
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`/tasks/${id}/`);
}

export async function setTaskStatus(id: number, done: boolean): Promise<Task> {
  const { data } = await api.patch<Task>(`/tasks/${id}/status/`, { done });
  return data;
}

export async function shareTask(
  id: number,
  email: string,
  permission: SharePermission,
): Promise<void> {
  await api.post(`/tasks/${id}/share/`, { email, permission });
}

// ---- Categories ----
export async function fetchCategories(): Promise<Category[]> {
  const { data } = await api.get<Paginated<Category>>("/categories/");
  return data.results;
}

export async function createCategory(name: string, color: string): Promise<Category> {
  const { data } = await api.post<Category>("/categories/", { name, color });
  return data;
}
