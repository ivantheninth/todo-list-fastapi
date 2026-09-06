import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type FormEvent } from "react";

import Chat from "../components/Chat";

export const Route = createFileRoute("/")({
  component: Index,
});

type Task = {
  id: number | string;
  title: string;
  note?: string;
  completed: boolean;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
};

type User = {
  id: number;
  username: string;
  email: string;
};

const API_URL = "/tasks";

function Index() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [editingId, setEditingId] = useState<Task["id"] | null>(null);

  const [editTitle, setEditTitle] = useState("");
  const [editNote, setEditNote] = useState("");

  const [search, setSearch] = useState("");

  const [filter, setFilter] = useState<"all" | "active" | "completed">("all");

  const [showChat, setShowChat] = useState(false);

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);

  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const [authMode, setAuthMode] = useState<"login" | "register">("login");

  const [authLoading, setAuthLoading] = useState(false);

  const [token, setToken] = useState<string | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    return localStorage.getItem("access_token");
  });

  async function loadCurrentUser(accessToken: string) {
    const res = await fetch("/auth/me", {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (res.status === 401 || res.status === 403) {
      throw new Error("Your session has expired.");
    }

    if (!res.ok) {
      throw new Error("Failed to load user");
    }

    const user: User = await res.json();

    setCurrentUser(user);
  }

  async function performLogin() {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });

    if (!res.ok) {
      throw new Error("Incorrect email or password");
    }

    const data: TokenResponse = await res.json();

    localStorage.setItem("access_token", data.access_token);

    await loadCurrentUser(data.access_token);

    setToken(data.access_token);
    setPassword("");
    setRepeatPassword("");
  }

  async function login(e: FormEvent) {
    e.preventDefault();

    setError(null);
    setAuthLoading(true);

    try {
      await performLogin();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    } finally {
      setAuthLoading(false);
    }
  }

  async function register(e: FormEvent) {
    e.preventDefault();

    setError(null);

    if (!username.trim()) {
      setError("Username is required");
      return;
    }

    if (password !== repeatPassword) {
      setError("Passwords do not match");
      return;
    }

    setAuthLoading(true);

    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username.trim(),
          email,
          password,
        }),
      });

      if (res.status === 409) {
        throw new Error("Email already registered");
      }

      if (!res.ok) {
        throw new Error("Registration failed");
      }

      await performLogin();

      setUsername("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Registration failed");
    } finally {
      setAuthLoading(false);
    }
  }

  function switchAuthMode(mode: "login" | "register") {
    setAuthMode(mode);
    setError(null);

    setUsername("");
    setPassword("");
    setRepeatPassword("");

    setShowPassword(false);
    setShowRepeatPassword(false);
  }

  function logout() {
    localStorage.removeItem("access_token");

    setToken(null);
    setCurrentUser(null);
    setTasks([]);

    setUsername("");
    setEmail("");
    setPassword("");
    setRepeatPassword("");

    setShowPassword(false);
    setShowRepeatPassword(false);

    setError(null);
    setShowChat(false);
    setAuthMode("login");
  }

  async function loadTasks() {
    if (!token) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.status === 401 || res.status === 403) {
        logout();

        throw new Error("Your session has expired. Please log in again.");
      }

      if (!res.ok) {
        throw new Error("Failed to load tasks");
      }

      const data: Task[] = await res.json();

      setTasks(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) {
      return;
    }

    async function initializeUser() {
      try {
        await loadCurrentUser(token);
      } catch {
        logout();
        return;
      }

      await loadTasks();
    }

    initializeUser();
  }, [token]);

  async function createTask(e: FormEvent) {
    e.preventDefault();

    if (!token) {
      return;
    }

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setError(null);

    const res = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: title.trim(),
        note: note.trim(),
        completed: false,
      }),
    });

    if (res.status === 401 || res.status === 403) {
      logout();
      return;
    }

    if (!res.ok) {
      setError("Failed to create task");
      return;
    }

    setTitle("");
    setNote("");

    await loadTasks();
  }

  async function toggleCompleted(task: Task) {
    if (!token) {
      return;
    }

    setError(null);

    const res = await fetch(`${API_URL}/${task.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        completed: !task.completed,
      }),
    });

    if (res.status === 401 || res.status === 403) {
      logout();
      return;
    }

    if (!res.ok) {
      setError("Failed to update task");
      return;
    }

    await loadTasks();
  }

  function startEdit(task: Task) {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditNote(task.note ?? "");
  }

  async function saveEdit(task: Task) {
    if (!token) {
      return;
    }

    if (!editTitle.trim()) {
      setError("Title is required");
      return;
    }

    setError(null);

    const res = await fetch(`${API_URL}/${task.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: editTitle.trim(),
        note: editNote.trim(),
      }),
    });

    if (res.status === 401 || res.status === 403) {
      logout();
      return;
    }

    if (!res.ok) {
      setError("Failed to update task");
      return;
    }

    setEditingId(null);

    await loadTasks();
  }

  async function deleteTask(id: Task["id"]) {
    if (!token) {
      return;
    }

    setError(null);

    const res = await fetch(`${API_URL}/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.status === 401 || res.status === 403) {
      logout();
      return;
    }

    if (!res.ok) {
      setError("Failed to delete task");
      return;
    }

    await loadTasks();
  }

  const remaining = tasks.filter((task) => !task.completed).length;

  const query = search.trim().toLowerCase();

  const filteredTasks = tasks.filter((task) => {
    const matchesFilter =
      filter === "all" ? true : filter === "active" ? !task.completed : task.completed;

    if (!matchesFilter) {
      return false;
    }

    if (!query) {
      return true;
    }

    return (
      task.title.toLowerCase().includes(query) ||
      (task.note && task.note.toLowerCase().includes(query))
    );
  });

  if (!token) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="mx-auto max-w-md px-6 py-16">
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">ToDo List</p>

          <h1 className="mt-2 text-4xl font-semibold tracking-tight">
            {authMode === "login" ? "Login" : "Create account"}
          </h1>

          <p className="mt-2 text-muted-foreground">
            {authMode === "login"
              ? "Sign in to access your tasks."
              : "Create an account to start using your task list."}
          </p>

          <div className="mt-8 flex gap-1 rounded-xl border border-border bg-card p-1">
            <button
              type="button"
              onClick={() => switchAuthMode("login")}
              className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                authMode === "login"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              Login
            </button>

            <button
              type="button"
              onClick={() => switchAuthMode("register")}
              className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                authMode === "register"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              Register
            </button>
          </div>

          <form
            onSubmit={authMode === "login" ? login : register}
            className="mt-3 flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-warm)]"
          >
            {authMode === "register" && (
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
                autoComplete="username"
                required
                className="rounded-lg border border-border bg-background px-4 py-3 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
              />
            )}

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              autoComplete="email"
              required
              className="rounded-lg border border-border bg-background px-4 py-3 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                autoComplete={authMode === "login" ? "current-password" : "new-password"}
                required
                className="w-full rounded-lg border border-border bg-background px-4 py-3 pr-12 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
              />

              <button
                type="button"
                onClick={() => setShowPassword((previous) => !previous)}
                aria-label={showPassword ? "Hide password" : "Show password"}
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
              >
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>

            {authMode === "register" && (
              <div className="relative">
                <input
                  type={showRepeatPassword ? "text" : "password"}
                  value={repeatPassword}
                  onChange={(e) => setRepeatPassword(e.target.value)}
                  placeholder="Repeat password"
                  autoComplete="new-password"
                  required
                  className="w-full rounded-lg border border-border bg-background px-4 py-3 pr-12 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
                />

                <button
                  type="button"
                  onClick={() => setShowRepeatPassword((previous) => !previous)}
                  aria-label={showRepeatPassword ? "Hide password" : "Show password"}
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-muted-foreground transition-colors hover:text-foreground"
                >
                  {showRepeatPassword ? <EyeOffIcon /> : <EyeIcon />}
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={authLoading}
              className="rounded-lg bg-primary px-5 py-3 font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {authLoading ? "Please wait..." : authMode === "login" ? "Login" : "Create account"}
            </button>

            {error && (
              <div className="rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                {error}
              </div>
            )}
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-2xl px-6 py-12 sm:py-16">
        <header className="mb-10">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">ToDo List</p>

              <h1 className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                Today's tasks
              </h1>
            </div>

            <div className="flex flex-col items-end gap-2">
              {currentUser && (
                <div className="text-right">
                  <p className="text-sm font-medium">{currentUser.username}</p>

                  <p className="text-xs text-muted-foreground">{currentUser.email}</p>
                </div>
              )}

              <button
                type="button"
                onClick={logout}
                className="rounded-lg border border-border px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                Logout
              </button>
            </div>
          </div>

          <p className="mt-2 text-muted-foreground">
            {tasks.length === 0
              ? "Nothing here yet — add your first task below."
              : `${remaining} of ${tasks.length} still to do.`}
          </p>

          <button
            type="button"
            onClick={() => setShowChat((previous) => !previous)}
            className="mt-5 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            {showChat ? "Hide AI Assistant" : "✨ Open AI Assistant"}
          </button>
        </header>

        <form
          onSubmit={createTask}
          className="rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-warm)]"
        >
          <div className="flex flex-col gap-3">
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What needs doing?"
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-base outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Add a note (optional)"
              rows={2}
              className="w-full resize-none rounded-lg border border-border bg-background px-4 py-3 text-sm outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={loadTasks}
                className="rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                Refresh
              </button>

              <button
                type="submit"
                className="rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground transition-transform hover:-translate-y-0.5 hover:bg-primary/90"
              >
                Add task
              </button>
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-4 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="mt-8 space-y-3">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tasks by title or note…"
            aria-label="Search tasks"
            className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base shadow-[var(--shadow-warm)] outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
          />

          <div
            role="group"
            aria-label="Filter tasks"
            className="flex gap-1 rounded-xl border border-border bg-card p-1 shadow-[var(--shadow-warm)]"
          >
            {(["all", "active", "completed"] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                aria-pressed={filter === f}
                className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium capitalize transition-colors ${
                  filter === f
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <section className="mt-5 space-y-3">
          {loading && tasks.length === 0 ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : tasks.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-card/60 p-10 text-center text-muted-foreground">
              Your list is empty.
            </div>
          ) : filteredTasks.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-card/60 p-10 text-center text-muted-foreground">
              No tasks match your search.
            </div>
          ) : (
            filteredTasks.map((task) => (
              <article
                key={task.id}
                className="group rounded-2xl border border-border bg-card p-4 transition-shadow hover:shadow-[var(--shadow-warm)]"
              >
                {editingId === task.id ? (
                  <div className="flex flex-col gap-2">
                    <input
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />

                    <textarea
                      value={editNote}
                      onChange={(e) => setEditNote(e.target.value)}
                      rows={2}
                      className="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />

                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setEditingId(null)}
                        className="rounded-lg px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
                      >
                        Cancel
                      </button>

                      <button
                        type="button"
                        onClick={() => saveEdit(task)}
                        className="rounded-lg bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={() => toggleCompleted(task)}
                      aria-label={task.completed ? "Mark as not done" : "Mark as done"}
                      className={`mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                        task.completed
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-border hover:border-primary"
                      }`}
                    >
                      {task.completed ? "✓" : ""}
                    </button>

                    <div className="min-w-0 flex-1">
                      <h2
                        className={`text-base font-medium leading-snug ${
                          task.completed ? "text-muted-foreground line-through" : ""
                        }`}
                      >
                        {task.title}
                      </h2>

                      {task.note && (
                        <p className="mt-1 text-sm text-muted-foreground">{task.note}</p>
                      )}
                    </div>

                    <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                      <button
                        type="button"
                        onClick={() => startEdit(task)}
                        className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        onClick={() => deleteTask(task.id)}
                        className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                )}
              </article>
            ))
          )}
        </section>

        {showChat && (
          <section className="mt-10 overflow-hidden rounded-2xl border border-border bg-card shadow-[var(--shadow-warm)]">
            <Chat onTasksCreated={loadTasks} />
          </section>
        )}
      </div>
    </div>
  );
}

function EyeIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m2 2 20 20" />
      <path d="M6.71 6.71C4.99 7.9 3.61 9.6 2.94 11.65a1 1 0 0 0 0 .7C4.42 16.87 7.92 19 12 19c1.49 0 2.88-.28 4.12-.8" />
      <path d="M10.73 5.08A9.8 9.8 0 0 1 12 5c4.08 0 7.58 2.13 9.06 6.65a1 1 0 0 1 0 .7 11 11 0 0 1-1.55 3.02" />
      <path d="M14.12 14.12A3 3 0 0 1 9.88 9.88" />
    </svg>
  );
}
