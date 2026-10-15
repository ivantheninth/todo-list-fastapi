import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { Index } from "./index";
import { authenticatedUser, configureAuthenticatedSession } from "../test/test-utils";
import { server } from "../test/server";

describe("authentication", () => {
  it("restores an authenticated user with a same-origin /auth/me request", async () => {
    let requestCredentials: RequestCredentials | undefined;

    server.use(
      http.get("*/auth/me", ({ request }) => {
        requestCredentials = request.credentials;
        return HttpResponse.json(authenticatedUser);
      }),
    );

    render(<Index />);

    expect(screen.getByText("Restoring your session…")).toBeInTheDocument();
    expect(await screen.findByText(authenticatedUser.email)).toBeInTheDocument();
    expect(requestCredentials).toBe("same-origin");
  });

  it("shows the unauthenticated application when session restoration returns 401", async () => {
    localStorage.setItem("access_token", "legacy-token");

    render(<Index />);

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(localStorage.getItem("access_token")).toBe("legacy-token");
  });

  it("logs in without storing or reading a JWT in frontend storage", async () => {
    const user = userEvent.setup();
    let isLoggedIn = false;
    let loginCredentials: RequestCredentials | undefined;
    let loginOrigin: string | null | undefined;

    server.use(
      http.get("*/auth/me", () =>
        isLoggedIn ? HttpResponse.json(authenticatedUser) : new HttpResponse(null, { status: 401 }),
      ),
      http.post("*/auth/login", ({ request }) => {
        isLoggedIn = true;
        loginCredentials = request.credentials;
        loginOrigin = request.headers.get("origin");
        return HttpResponse.json({ access_token: "backend-only-token", token_type: "bearer" });
      }),
    );

    render(<Index />);
    await screen.findByRole("heading", { name: "Login" });

    await user.type(screen.getByPlaceholderText("Email"), authenticatedUser.email);
    await user.type(screen.getByPlaceholderText("Password"), "Testpassword123!");
    await user.click(
      screen
        .getAllByRole("button", { name: "Login" })
        .find((button) => button.getAttribute("type") === "submit")!,
    );

    expect(await screen.findByText(authenticatedUser.email)).toBeInTheDocument();
    expect(loginCredentials).toBe("same-origin");
    expect(loginOrigin).toBeNull();
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("shows an error for invalid login credentials", async () => {
    const user = userEvent.setup();
    server.use(http.post("*/auth/login", () => new HttpResponse(null, { status: 401 })));

    render(<Index />);
    await screen.findByRole("heading", { name: "Login" });

    await user.type(screen.getByPlaceholderText("Email"), "wrong@example.com");
    await user.type(screen.getByPlaceholderText("Password"), "wrong-password");
    await user.click(
      screen
        .getAllByRole("button", { name: "Login" })
        .find((button) => button.getAttribute("type") === "submit")!,
    );

    expect(await screen.findByText("Incorrect email or password")).toBeInTheDocument();
  });

  it("registers a user, then restores the cookie-authenticated session", async () => {
    const user = userEvent.setup();
    let isLoggedIn = false;
    let registerCredentials: RequestCredentials | undefined;
    let registerOrigin: string | null | undefined;
    let registration: unknown;

    server.use(
      http.get("*/auth/me", () =>
        isLoggedIn ? HttpResponse.json(authenticatedUser) : new HttpResponse(null, { status: 401 }),
      ),
      http.post("*/auth/register", async ({ request }) => {
        registerCredentials = request.credentials;
        registerOrigin = request.headers.get("origin");
        registration = await request.json();
        return HttpResponse.json(authenticatedUser, { status: 201 });
      }),
      http.post("*/auth/login", () => {
        isLoggedIn = true;
        return HttpResponse.json({ access_token: "backend-only-token", token_type: "bearer" });
      }),
    );

    render(<Index />);
    await screen.findByRole("heading", { name: "Login" });
    await user.click(screen.getByRole("button", { name: "Register" }));

    await user.type(screen.getByPlaceholderText("Username"), "Ada");
    await user.type(screen.getByPlaceholderText("Email"), authenticatedUser.email);
    await user.type(screen.getByPlaceholderText("Password"), "Testpassword123!");
    await user.type(screen.getByPlaceholderText("Repeat password"), "Testpassword123!");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText(authenticatedUser.email)).toBeInTheDocument();
    expect(registration).toEqual({
      username: "Ada",
      email: authenticatedUser.email,
      password: "Testpassword123!",
    });
    expect(registerCredentials).toBe("same-origin");
    expect(registerOrigin).toBeNull();
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("validates matching registration passwords before making a request", async () => {
    const user = userEvent.setup();
    let registrationAttempts = 0;
    server.use(
      http.post("*/auth/register", () => {
        registrationAttempts += 1;
        return HttpResponse.json(authenticatedUser, { status: 201 });
      }),
    );

    render(<Index />);
    await screen.findByRole("heading", { name: "Login" });
    await user.click(screen.getByRole("button", { name: "Register" }));

    await user.type(screen.getByPlaceholderText("Username"), "Ada");
    await user.type(screen.getByPlaceholderText("Email"), authenticatedUser.email);
    await user.type(screen.getByPlaceholderText("Password"), "Testpassword123!");
    await user.type(screen.getByPlaceholderText("Repeat password"), "Differentpassword123!");
    await user.click(screen.getByRole("button", { name: "Create account" }));

    expect(await screen.findByText("Passwords do not match")).toBeInTheDocument();
    expect(registrationAttempts).toBe(0);
  });

  it("clears the backend session and frontend state on logout", async () => {
    const user = userEvent.setup();
    let logoutCredentials: RequestCredentials | undefined;
    let logoutOrigin: string | null | undefined;

    configureAuthenticatedSession();
    server.use(
      http.post("*/auth/logout", ({ request }) => {
        logoutCredentials = request.credentials;
        logoutOrigin = request.headers.get("origin");
        return new HttpResponse(null, { status: 204 });
      }),
    );

    render(<Index />);
    await screen.findByRole("button", { name: "Logout" });
    await user.click(screen.getByRole("button", { name: "Logout" }));

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(logoutCredentials).toBe("same-origin");
    expect(logoutOrigin).toBeNull();
  });

  it("returns to the login screen when a later task request is unauthorized", async () => {
    const user = userEvent.setup();
    let shouldExpire = false;

    server.use(
      http.get("*/auth/me", () => HttpResponse.json(authenticatedUser)),
      http.get("*/tasks", () =>
        shouldExpire ? new HttpResponse(null, { status: 401 }) : HttpResponse.json([]),
      ),
    );

    render(<Index />);
    await screen.findByRole("heading", { name: "Today's tasks" });
    shouldExpire = true;

    await user.click(screen.getByRole("button", { name: "Refresh" }));

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
  });

  it("restores authentication after a page refresh", async () => {
    configureAuthenticatedSession();
    const firstRender = render(<Index />);
    await screen.findByText(authenticatedUser.email);

    firstRender.unmount();
    render(<Index />);

    expect(await screen.findByText(authenticatedUser.email)).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.queryByText("Restoring your session…")).not.toBeInTheDocument(),
    );
  });
});
