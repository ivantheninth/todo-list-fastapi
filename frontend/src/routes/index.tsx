import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type FormEvent } from "react";

export const Route = createFileRoute("/")({
  component: Index,
});

type Task = {
  id: number | string;
  title: string;
  note?: string;
  completed: boolean;
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

  async function loadTasks() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_URL);
      if (!res.ok) throw new Error("Failed to load tasks");
      setTasks(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  async function createTask(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) {
      setError("Title is required");
      return;
    }
    setError(null);
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: title.trim(), note: note.trim(), completed: false }),
    });
    if (!res.ok) {
      setError("Failed to create task");
      return;
    }
    setTitle("");
    setNote("");
    loadTasks();
  }

  async function toggleCompleted(task: Task) {
    const res = await fetch(`${API_URL}/${task.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...task, completed: !task.completed }),
    });
    if (!res.ok) {
      setError("Failed to update task");
      return;
    }
    loadTasks();
  }

  function startEdit(task: Task) {
    setEditingId(task.id);
    setEditTitle(task.title);
    setEditNote(task.note ?? "");
  }

  async function saveEdit(task: Task) {
    if (!editTitle.trim()) {
      setError("Title is required");
      return;
    }
    const res = await fetch(`${API_URL}/${task.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: editTitle.trim(),
        note: editNote.trim(),
        completed: task.completed,
      }),
    });
    if (!res.ok) {
      setError("Failed to update task");
      return;
    }
    setEditingId(null);
    loadTasks();
  }

  async function deleteTask(id: Task["id"]) {
    const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    if (!res.ok) {
      setError("Failed to delete task");
      return;
    }
    loadTasks();
  }

  const remaining = tasks.filter((t) => !t.completed).length;

  const query = search.trim().toLowerCase();
  const filteredTasks = tasks.filter((t) => {
    const matchesFilter =
      filter === "all" ? true : filter === "active" ? !t.completed : t.completed;
    if (!matchesFilter) return false;
    if (!query) return true;
    return (
      t.title.toLowerCase().includes(query) ||
      (t.note && t.note.toLowerCase().includes(query))
    );
  });

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-2xl px-6 py-12 sm:py-16">
        <header className="mb-10">
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
            Warm Todo
          </p>
          <h1 className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">
            Today's tasks
          </h1>
          <p className="mt-2 text-muted-foreground">
            {tasks.length === 0
              ? "Nothing here yet — add your first task below."
              : `${remaining} of ${tasks.length} still to do.`}
          </p>
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
                        onClick={() => setEditingId(null)}
                        className="rounded-lg px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground"
                      >
                        Cancel
                      </button>
                      <button
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
                        onClick={() => startEdit(task)}
                        className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
                      >
                        Edit
                      </button>
                      <button
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
      </div>
    </div>
  );
}
