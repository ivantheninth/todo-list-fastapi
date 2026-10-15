import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { delay, http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";

import Chat from "./Chat";
import { server } from "../test/server";

describe("Chat", () => {
  it("sends a message with same-origin credentials and renders the assistant response", async () => {
    const user = userEvent.setup();
    let credentials: RequestCredentials | undefined;
    let origin: string | null | undefined;

    server.use(
      http.post("*/chat", ({ request }) => {
        credentials = request.credentials;
        origin = request.headers.get("origin");
        return HttpResponse.json({ answer: "Try one task at a time.", tasks: [] });
      }),
    );

    render(<Chat />);
    await user.type(screen.getByPlaceholderText("Ask AI..."), "How should I plan?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("Try one task at a time.")).toBeInTheDocument();
    expect(credentials).toBe("same-origin");
    expect(origin).toBeNull();
  });

  it("shows a loading state while waiting for the assistant", async () => {
    const user = userEvent.setup();
    server.use(
      http.post("*/chat", async () => {
        await delay(30);
        return HttpResponse.json({ answer: "Finished", tasks: [] });
      }),
    );

    render(<Chat />);
    await user.type(screen.getByPlaceholderText("Ask AI..."), "Wait for it");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(screen.getByText("Thinking...")).toBeInTheDocument();
    expect(await screen.findByText("Finished")).toBeInTheDocument();
  });

  it("shows an error response when chat fails", async () => {
    const user = userEvent.setup();
    server.use(http.post("*/chat", () => new HttpResponse(null, { status: 500 })));

    render(<Chat />);
    await user.type(screen.getByPlaceholderText("Ask AI..."), "Will this fail?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("Sorry, something went wrong.")).toBeInTheDocument();
  });

  it("notifies its parent when the chat session is unauthorized", async () => {
    const user = userEvent.setup();
    const onAuthenticationExpired = vi.fn();
    server.use(http.post("*/chat", () => new HttpResponse(null, { status: 401 })));

    render(<Chat onAuthenticationExpired={onAuthenticationExpired} />);
    await user.type(screen.getByPlaceholderText("Ask AI..."), "Expired?");
    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(onAuthenticationExpired).toHaveBeenCalledOnce();
    expect(await screen.findByText("Sorry, something went wrong.")).toBeInTheDocument();
  });

  it("creates suggested tasks through the bulk endpoint", async () => {
    const user = userEvent.setup();
    const onTasksCreated = vi.fn();
    let bulkCredentials: RequestCredentials | undefined;
    let bulkOrigin: string | null | undefined;
    let bulkPayload: unknown;

    server.use(
      http.post("*/chat", () =>
        HttpResponse.json({
          answer: "Here is a plan.",
          tasks: [
            { title: "Plan", note: "Break down the work" },
            { title: "Build", note: null },
          ],
        }),
      ),
      http.post("*/tasks/bulk", async ({ request }) => {
        bulkCredentials = request.credentials;
        bulkOrigin = request.headers.get("origin");
        bulkPayload = await request.json();
        return HttpResponse.json([], { status: 201 });
      }),
    );

    render(<Chat onTasksCreated={onTasksCreated} />);
    await user.type(screen.getByPlaceholderText("Ask AI..."), "Create a plan");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await screen.findByText("Plan");
    await user.click(screen.getByRole("button", { name: "Create 2 tasks" }));

    expect(await screen.findByText("2 tasks created successfully.")).toBeInTheDocument();
    expect(onTasksCreated).toHaveBeenCalledOnce();
    expect(bulkPayload).toEqual({
      tasks: [
        { title: "Plan", note: "Break down the work", completed: false },
        { title: "Build", note: null, completed: false },
      ],
    });
    expect(bulkCredentials).toBe("same-origin");
    expect(bulkOrigin).toBeNull();
  });

  it("sends a message when Enter is pressed", async () => {
    const user = userEvent.setup();
    const requestReceived = vi.fn();
    server.use(
      http.post("*/chat", () => {
        requestReceived();
        return HttpResponse.json({ answer: "Sent", tasks: [] });
      }),
    );

    render(<Chat />);
    const input = screen.getByPlaceholderText("Ask AI...");
    await user.type(input, "Send with Enter");
    await user.keyboard("{Enter}");

    expect(await screen.findByText("Sent")).toBeInTheDocument();
    expect(requestReceived).toHaveBeenCalledOnce();
  });

  it("keeps a newline and does not send when Shift+Enter is pressed", async () => {
    const user = userEvent.setup();
    const requestReceived = vi.fn();
    server.use(
      http.post("*/chat", () => {
        requestReceived();
        return HttpResponse.json({ answer: "Unexpected", tasks: [] });
      }),
    );

    render(<Chat />);
    const input = screen.getByPlaceholderText("Ask AI...");
    await user.type(input, "First line");
    await user.keyboard("{Shift>}{Enter}{/Shift}");
    await user.type(input, "Second line");

    expect(input).toHaveValue("First line\nSecond line");
    expect(requestReceived).not.toHaveBeenCalled();
  });
});
