export type TaskStatus = "pending" | "done";
export type SharePermission = "view" | "edit";

export interface User {
  id: number;
  username: string;
  email: string;
  date_joined: string;
}

export interface Category {
  id: number;
  name: string;
  color: string;
  created_at: string;
}

export interface TaskShare {
  id: number;
  user: string;
  permission: SharePermission;
  created_at: string;
}

export interface Task {
  id: number;
  owner: string;
  title: string;
  description: string;
  status: TaskStatus;
  is_done: boolean;
  category: number | null;
  due_date: string | null;
  shares: TaskShare[];
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface TaskFilters {
  status?: TaskStatus | "";
  category?: number | "";
  search?: string;
  page?: number;
  ordering?: string;
}
