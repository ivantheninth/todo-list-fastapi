import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { Index } from "./index";
import {
  authenticatedUser,
  configureAuthenticatedSession,
  renderAuthenticatedIndex,
} from "../test/test-utils";
import { server } from "../test/server";

describe("task management", () => {
  it("fetches and renders the current user's tasks", async () => {
    await renderAuthenticatedIndex([
      { id: 1, title: "Write tests", note: "Use MSW", completed: false },
    ]);

    expect(await screen.findByText("Write tests")).toBeInTheDocument();
    expect(screen.getByText("Use MSW")).toBeInTheDocument();
  });

  it("searches and filters tasks through visible controls", async () => {
    const user = userEvent.setup();
    await renderAuthenticatedIndex([
      { id: 1, title: "Write tests", completed: false },
      { id: 2, title: "Review pull request", completed: true },
    ]);

    await user.type(screen.getByRole("textbox", { name: "Search tasks" }), "review");
    expect(screen.getByText("Review pull request")).toBeInTheDocument();
    expect(screen.queryByText("Write tests")).not.toBeInTheDocument();

    await user.clear(screen.getByRole("textbox", { name: "Search tasks" }));
    await user.click(screen.getByRole("button", { name: "active" }));
    expect(screen.getByText("Write tests")).toBeInTheDocument();
    expect(screen.queryByText("Review pull request")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "completed" }));
    expect(screen.getByText("Review pull request")).toBeInTheDocument();
    expect(screen.queryByText("Write tests")).not.toBeInTheDocument();
  });

  it("shows loading and empty states", async () => {
    server.use(
      http.get("*/auth/me", () => HttpResponse.json(authenticatedUser)),
      http.get("*/tasks", async () => {
        await delay(30);
        return HttpResponse.json([]);
      }),
    );

    render(<Index />);

    expect(await screen.findByText("Loading…")).toBeInTheDocument();
    expect(await screen.findByText("Your list is empty.")).toBeInTheDocument();
  });

  it("creates a task with same-origin credentials and refetches the list", async () => {
    const user = userEvent.setup();
    const tasks: Array<{ id: number; title: string; note?: string; completed: boolean }> = [];
    let credentials: RequestCredentials | undefined;
    let origin: string | null | undefined;

    configureAuthenticatedSession(tasks);
    server.use(
      http.post("*/tasks", async ({ request }) => {
        credentials = request.credentials;
        origin = request.headers.get("origin");
        const body = (await request.json()) as { title: string; note: string; completed: boolean };
        tasks.push({ id: 1, ...body });
        return HttpResponse.json(tasks[0], { status: 201 });
      }),
    );

    render(<Index />);
    await screen.findByRole("heading", { name: "Today's tasks" });
    await user.type(screen.getByPlaceholderText("What needs doing?"), "Ship cookie auth");
    await user.click(screen.getByRole("button", { name: "Add task" }));

    expect(await screen.findByText("Ship cookie auth")).toBeInTheDocument();
    expect(credentials).toBe("same-origin");
    expect(origin).toBeNull();
  });

  it("marks a task as completed", async () => {
    const user = userEvent.setup();
    const tasks = [{ id: 1, title: "Complete me", completed: false }];

    configureAuthenticatedSession(tasks);
    server.use(
      http.patch("*/tasks/1", async ({ request }) => {
        const body = (await request.json()) as { completed: boolean };
        tasks[0].completed = body.completed;
        return HttpResponse.json(tasks[0]);
      }),
    );

    render(<Index />);
    await screen.findByText("Complete me");
    await user.click(screen.getByRole("button", { name: "Mark as done" }));

    expect(await screen.findByRole("button", { name: "Mark as not done" })).toBeInTheDocument();
  });

  it("edits a task", async () => {
    const user = userEvent.setup();
    const tasks = [{ id: 1, title: "Old title", note: "Old note", completed: false }];

    configureAuthenticatedSession(tasks);
    server.use(
      http.patch("*/tasks/1", async ({ request }) => {
        const body = (await request.json()) as { title: string; note: string };
        tasks[0] = { ...tasks[0], ...body };
        return HttpResponse.json(tasks[0]);
      }),
    );

    render(<Index />);
    await screen.findByText("Old title");
    const taskArticle = screen.getByText("Old title").closest("article")!;
    await user.click(within(taskArticle).getByRole("button", { name: "Edit" }));
    const titleInput = within(taskArticle).getByDisplayValue("Old title");
    await user.clear(titleInput);
    await user.type(titleInput, "New title");
    await user.click(screen.getByRole("button", { name: "Save" }));

    expect(await screen.findByText("New title")).toBeInTheDocument();
  });

  it("deletes a task", async () => {
    const user = userEvent.setup();
    const tasks = [{ id: 1, title: "Remove me", completed: false }];

    configureAuthenticatedSession(tasks);
    server.use(
      http.delete("*/tasks/1", () => {
        tasks.splice(0);
        return new HttpResponse(null, { status: 204 });
      }),
    );

    render(<Index />);
    await screen.findByText("Remove me");
    await user.click(screen.getByRole("button", { name: "Delete" }));

    expect(await screen.findByText("Your list is empty.")).toBeInTheDocument();
  });

  it("shows a task API error without losing the current session", async () => {
    const user = userEvent.setup();
    configureAuthenticatedSession();
    server.use(http.post("*/tasks", () => new HttpResponse(null, { status: 500 })));

    render(<Index />);
    await screen.findByRole("heading", { name: "Today's tasks" });
    await user.type(screen.getByPlaceholderText("What needs doing?"), "Will fail");
    await user.click(screen.getByRole("button", { name: "Add task" }));

    expect(await screen.findByText("Failed to create task")).toBeInTheDocument();
    expect(screen.getByText(authenticatedUser.email)).toBeInTheDocument();
  });

  it("returns to login when a task mutation is unauthorized", async () => {
    const user = userEvent.setup();
    configureAuthenticatedSession();
    server.use(http.post("*/tasks", () => new HttpResponse(null, { status: 401 })));

    render(<Index />);
    await screen.findByRole("heading", { name: "Today's tasks" });
    await user.type(screen.getByPlaceholderText("What needs doing?"), "Expired session");
    await user.click(screen.getByRole("button", { name: "Add task" }));

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
  });

  it("returns to login when updating a task is unauthorized", async () => {
    const user = userEvent.setup();
    configureAuthenticatedSession([{ id: 1, title: "Protected task", completed: false }]);
    server.use(http.patch("*/tasks/1", () => new HttpResponse(null, { status: 401 })));

    render(<Index />);
    await screen.findByText("Protected task");
    await user.click(screen.getByRole("button", { name: "Mark as done" }));

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
  });

  it("returns to login when deleting a task is unauthorized", async () => {
    const user = userEvent.setup();
    configureAuthenticatedSession([{ id: 1, title: "Protected task", completed: false }]);
    server.use(http.delete("*/tasks/1", () => new HttpResponse(null, { status: 401 })));

    render(<Index />);
    await screen.findByText("Protected task");
    await user.click(screen.getByRole("button", { name: "Delete" }));

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
  });
});
