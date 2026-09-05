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
  const [filter, setFilter] = useState<
    "all" | "active" | "completed"
  >("all");

  const [showChat, setShowChat] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [authMode, setAuthMode] = useState<
    "login" | "register"
  >("login");

  const [authLoading, setAuthLoading] = useState(false);

  const [token, setToken] = useState<string | null>(() => {
    if (typeof window === "undefined") {
      return null;
    }

    return localStorage.getItem("access_token");
  });


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

    localStorage.setItem(
      "access_token",
      data.access_token,
    );

    setToken(data.access_token);
    setPassword("");
  }


  async function login(e: FormEvent) {
    e.preventDefault();

    setError(null);
    setAuthLoading(true);

    try {
      await performLogin();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Login failed",
      );
    } finally {
      setAuthLoading(false);
    }
  }


  async function register(e: FormEvent) {
    e.preventDefault();

    setError(null);
    setAuthLoading(true);

    try {
      const res = await fetch("/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
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
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Registration failed",
      );
    } finally {
      setAuthLoading(false);
    }
  }


  function switchAuthMode(
    mode: "login" | "register",
  ) {
    setAuthMode(mode);
    setError(null);
    setPassword("");
  }


  function logout() {
    localStorage.removeItem("access_token");

    setToken(null);
    setTasks([]);
    setEmail("");
    setPassword("");
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

        throw new Error(
          "Your session has expired. Please log in again.",
        );
      }

      if (!res.ok) {
        throw new Error("Failed to load tasks");
      }

      const data: Task[] = await res.json();

      setTasks(data);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Something went wrong",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    if (token) {
      loadTasks();
    }
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


  const remaining = tasks.filter(
    (task) => !task.completed,
  ).length;


  const query = search.trim().toLowerCase();


  const filteredTasks = tasks.filter((task) => {
    const matchesFilter =
      filter === "all"
        ? true
        : filter === "active"
          ? !task.completed
          : task.completed;

    if (!matchesFilter) {
      return false;
    }

    if (!query) {
      return true;
    }

    return (
      task.title.toLowerCase().includes(query) ||
      (task.note &&
        task.note.toLowerCase().includes(query))
    );
  });


  if (!token) {
    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="mx-auto max-w-md px-6 py-16">

          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
            ToDo List
          </p>

          <h1 className="mt-2 text-4xl font-semibold tracking-tight">
            {authMode === "login"
              ? "Login"
              : "Create account"}
          </h1>

          <p className="mt-2 text-muted-foreground">
            {authMode === "login"
              ? "Sign in to access your tasks."
              : "Create an account to start using your task list."}
          </p>


          <div className="mt-8 flex gap-1 rounded-xl border border-border bg-card p-1">

            <button
              type="button"
              onClick={() =>
                switchAuthMode("login")
              }
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
              onClick={() =>
                switchAuthMode("register")
              }
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
            onSubmit={
              authMode === "login"
                ? login
                : register
            }
            className="mt-3 flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-warm)]"
          >

            <input
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              placeholder="Email"
              autoComplete="email"
              required
              className="rounded-lg border border-border bg-background px-4 py-3 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="Password"
              autoComplete={
                authMode === "login"
                  ? "current-password"
                  : "new-password"
              }
              required
              className="rounded-lg border border-border bg-background px-4 py-3 outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <button
              type="submit"
              disabled={authLoading}
              className="rounded-lg bg-primary px-5 py-3 font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {authLoading
                ? "Please wait..."
                : authMode === "login"
                  ? "Login"
                  : "Create account"}
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
              <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
                ToDo List
              </p>

              <h1 className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
                Today's tasks
              </h1>
            </div>

            <button
              type="button"
              onClick={logout}
              className="rounded-lg border border-border px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              Logout
            </button>

          </div>

          <p className="mt-2 text-muted-foreground">
            {tasks.length === 0
              ? "Nothing here yet — add your first task below."
              : `${remaining} of ${tasks.length} still to do.`}
          </p>

          <button
            type="button"
            onClick={() =>
              setShowChat((previous) => !previous)
            }
            className="mt-5 rounded-xl bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            {showChat
              ? "Hide AI Assistant"
              : "✨ Open AI Assistant"}
          </button>

        </header>


        <form
          onSubmit={createTask}
          className="rounded-2xl border border-border bg-card p-5 shadow-[var(--shadow-warm)]"
        >
          <div className="flex flex-col gap-3">

            <input
              value={title}
              onChange={(e) =>
                setTitle(e.target.value)
              }
              placeholder="What needs doing?"
              className="w-full rounded-lg border border-border bg-background px-4 py-3 text-base outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
            />

            <textarea
              value={note}
              onChange={(e) =>
                setNote(e.target.value)
              }
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
            onChange={(e) =>
              setSearch(e.target.value)
            }
            placeholder="Search tasks by title or note…"
            aria-label="Search tasks"
            className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base shadow-[var(--shadow-warm)] outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/30"
          />

          <div
            role="group"
            aria-label="Filter tasks"
            className="flex gap-1 rounded-xl border border-border bg-card p-1 shadow-[var(--shadow-warm)]"
          >
            {(
              [
                "all",
                "active",
                "completed",
              ] as const
            ).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() =>
                  setFilter(f)
                }
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

            <p className="text-sm text-muted-foreground">
              Loading…
            </p>

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
                      onChange={(e) =>
                        setEditTitle(
                          e.target.value,
                        )
                      }
                      className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />

                    <textarea
                      value={editNote}
                      onChange={(e) =>
                        setEditNote(
                          e.target.value,
                        )
                      }
                      rows={2}
                      className="w-full resize-none rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-ring focus:ring-2 focus:ring-ring/30"
                    />

                    <div className="flex justify-end gap-2">

                      <button
                        type="button"
                        onClick={() =>
                          setEditingId(null)
                        }
                        className="rounded-lg px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
                      >
                        Cancel
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          saveEdit(task)
                        }
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
                      onClick={() =>
                        toggleCompleted(task)
                      }
                      aria-label={
                        task.completed
                          ? "Mark as not done"
                          : "Mark as done"
                      }
                      className={`mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 transition-colors ${
                        task.completed
                          ? "border-primary bg-primary text-primary-foreground"
                          : "border-border hover:border-primary"
                      }`}
                    >
                      {task.completed
                        ? "✓"
                        : ""}
                    </button>


                    <div className="min-w-0 flex-1">

                      <h2
                        className={`text-base font-medium leading-snug ${
                          task.completed
                            ? "text-muted-foreground line-through"
                            : ""
                        }`}
                      >
                        {task.title}
                      </h2>

                      {task.note && (
                        <p className="mt-1 text-sm text-muted-foreground">
                          {task.note}
                        </p>
                      )}

                    </div>


                    <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100">

                      <button
                        type="button"
                        onClick={() =>
                          startEdit(task)
                        }
                        className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          deleteTask(task.id)
                        }
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