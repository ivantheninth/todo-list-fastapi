import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { Index } from "./index";
import { authenticatedUser, configureAuthenticatedSession } from "../test/test-utils";
import { server } from "../test/server";

describe("Google OAuth login", () => {
  it("provides browser navigation to the Google OAuth initiation endpoint", async () => {
    render(<Index />);
    await screen.findByRole("heading", { name: "Login" });

    expect(screen.getByRole("link", { name: "Continue with Google" })).toHaveAttribute(
      "href",
      "/auth/google/login",
    );
  });

  it("restores the Google-authenticated user after the backend redirect", async () => {
    let meCredentials: RequestCredentials | undefined;
    configureAuthenticatedSession();
    server.use(
      http.get("*/auth/me", ({ request }) => {
        meCredentials = request.credentials;
        return HttpResponse.json(authenticatedUser);
      }),
    );

    render(<Index />);

    expect(await screen.findByText(authenticatedUser.email)).toBeInTheDocument();
    expect(meCredentials).toBe("same-origin");
    expect(localStorage.getItem("access_token")).toBeNull();
  });

  it("handles a failed Google return as an unauthenticated session", async () => {
    render(<Index />);

    expect(await screen.findByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Continue with Google" })).toBeInTheDocument();
  });
});
