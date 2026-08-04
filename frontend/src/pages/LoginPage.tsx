import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { loginSchema } from "../lib/validation";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const parsed = loginSchema.safeParse({ username, password });
    if (!parsed.success) {
      setError(parsed.error.errors[0].message);
      return;
    }
    try {
      await login(username, password);
      navigate("/");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <div className="card auth-card">
      <h1>Sign in</h1>
      <form onSubmit={onSubmit} data-testid="login-form">
        <input
          data-testid="login-username"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          data-testid="login-password"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="error" data-testid="login-error">{error}</p>}
        <button type="submit" data-testid="login-submit">Sign in</button>
      </form>
      <p>
        No account? <Link to="/register">Register</Link>
      </p>
    </div>
  );
}
