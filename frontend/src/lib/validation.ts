import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
});

export const registerSchema = z.object({
  username: z.string().min(3, "At least 3 characters"),
  email: z.string().email("Invalid e-mail"),
  password: z.string().min(10, "At least 10 characters"),
});

export const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(2000).optional(),
  category: z.number().nullable().optional(),
  due_date: z.string().nullable().optional(),
});

export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type TaskInput = z.infer<typeof taskSchema>;
