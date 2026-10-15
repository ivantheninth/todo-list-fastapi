import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const server = setupServer(
  http.get("*/auth/me", () => new HttpResponse(null, { status: 401 })),
  http.get("*/tasks", () => HttpResponse.json([])),
);
