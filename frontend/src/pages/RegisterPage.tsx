import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";
import { register } from "../api/endpoints";
import { useAuth } from "../hooks/useAuth";
import { registerSchema } from "../lib/validation";

export function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = registerSchema.safeParse({ username, email, password });
    if (!parsed.success) {
      setError(parsed.error.errors[0].message);
      return;
    }
    try {
      await register(username, email, password);
      await login(username, password);
      navigate("/");
    } catch (err) {
      const detail = (err as AxiosError<Record<string, string[]>>).response?.data;
      setError(detail ? Object.values(detail).flat()[0] : "Registration failed");
    }
  }

  return (
    <div className="card auth-card">
      <h1>Create account</h1>
      <form onSubmit={onSubmit} data-testid="register-form">
        <input
          data-testid="register-username"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          data-testid="register-email"
          placeholder="E-mail"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          data-testid="register-password"
          type="password"
          placeholder="Password (min 10 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="error" data-testid="register-error">{error}</p>}
        <button type="submit" data-testid="register-submit">Register</button>
      </form>
      <p>
        Have an account? <Link to="/login">Sign in</Link>
      </p>
    </div>
  );
}
