import { render, screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";

import { Index } from "../routes/index";
import { server } from "./server";

export const authenticatedUser = {
  id: 1,
  username: "Ada",
  email: "ada@example.com",
};

export type TestTask = {
  id: number;
  title: string;
  note?: string;
  completed: boolean;
};

export function configureAuthenticatedSession(tasks: TestTask[] = []) {
  server.use(
    http.get("*/auth/me", () => HttpResponse.json(authenticatedUser)),
    http.get("*/tasks", () => HttpResponse.json(tasks)),
  );
}

export async function renderAuthenticatedIndex(tasks: TestTask[] = []) {
  configureAuthenticatedSession(tasks);
  render(<Index />);

  await screen.findByRole("heading", { name: "Today's tasks" });
}
