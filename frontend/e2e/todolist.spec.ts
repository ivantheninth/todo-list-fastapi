import { expect, test, type Page } from "@playwright/test";

const password = "E2ePassword1!";

function uniqueIdentity() {
  const suffix = `${Date.now()}-${Math.random().toString(36).slice(2)}`;

  return {
    username: `e2e-${suffix}`,
    email: `e2e-${suffix}@example.com`,
  };
}

async function expectLoginInterface(page: Page) {
  await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();
  await expect(page.locator("form").getByRole("button", { name: "Login" })).toBeVisible();
}

async function registerThroughBrowser(page: Page) {
  const identity = uniqueIdentity();

  await page.goto("/");
  await expectLoginInterface(page);
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByPlaceholder("Username").fill(identity.username);
  await page.getByPlaceholder("Email").fill(identity.email);
  await page.getByPlaceholder("Password", { exact: true }).fill(password);
  await page.getByPlaceholder("Repeat password").fill(password);
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page.getByRole("heading", { name: "Today's tasks" })).toBeVisible();

  return identity;
}

async function addTask(page: Page, title: string, note = "") {
  await page.getByPlaceholder("What needs doing?").fill(title);

  if (note) {
    await page.getByPlaceholder("Add a note (optional)").fill(note);
  }

  await page.getByRole("button", { name: "Add task" }).click();
  await expect(page.getByRole("heading", { name: title })).toBeVisible();
}

test.describe("ToDoList through Nginx", () => {
  test("shows the login interface to an unauthenticated visitor", async ({ page }) => {
    await page.goto("/");

    await expectLoginInterface(page);
  });

  test("rejects invalid email/password credentials", async ({ page }) => {
    await page.goto("/");
    await page.getByPlaceholder("Email").fill("missing@example.test");
    await page.getByPlaceholder("Password").fill(password);
    await page.locator("form").getByRole("button", { name: "Login" }).click();

    await expect(page.getByText("Incorrect email or password")).toBeVisible();
    await expectLoginInterface(page);
  });

  test("registers, logs in, restores the cookie session after refresh, and logs out", async ({
    page,
    context,
  }) => {
    const identity = await registerThroughBrowser(page);

    const cookie = (await context.cookies()).find((item) => item.name === "access_token");
    expect(cookie).toMatchObject({
      httpOnly: true,
      secure: true,
      sameSite: "Lax",
      path: "/",
    });

    await page.reload();
    await expect(page.getByText(identity.username, { exact: true })).toBeVisible();

    await page.getByRole("button", { name: "Logout" }).click();
    await expectLoginInterface(page);
    await expect(context.cookies()).resolves.not.toContainEqual(
      expect.objectContaining({ name: "access_token" }),
    );

    await page.getByPlaceholder("Email").fill(identity.email);
    await page.getByPlaceholder("Password").fill(password);
    await page.locator("form").getByRole("button", { name: "Login" }).click();
    await expect(page.getByText(identity.username, { exact: true })).toBeVisible();
  });

  test("creates, edits, completes, searches, filters, and deletes tasks", async ({ page }) => {
    await registerThroughBrowser(page);
    await addTask(page, "Write E2E coverage", "Verify Nginx routing");
    await addTask(page, "Completed E2E task");

    const editableTask = page.locator("article").filter({
      has: page.getByRole("heading", { name: "Write E2E coverage" }),
    });
    await editableTask.getByRole("button", { name: "Edit" }).click();
    const editForm = page.locator("article").filter({
      has: page.getByRole("button", { name: "Save" }),
    });
    await editForm.getByRole("textbox").first().fill("Review E2E coverage");
    await editForm.getByRole("button", { name: "Save" }).click();
    await expect(page.getByRole("heading", { name: "Review E2E coverage" })).toBeVisible();

    const updatedTask = page.locator("article").filter({
      has: page.getByRole("heading", { name: "Review E2E coverage" }),
    });

    const completedTask = page.locator("article").filter({
      has: page.getByRole("heading", { name: "Completed E2E task" }),
    });
    await completedTask.getByRole("button", { name: "Mark as done" }).click();
    await expect(completedTask.getByRole("button", { name: "Mark as not done" })).toBeVisible();

    await page.getByRole("button", { name: "Completed" }).click();
    await expect(page.getByRole("heading", { name: "Completed E2E task" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Review E2E coverage" })).not.toBeVisible();

    await page.getByRole("button", { name: "All" }).click();
    await page.getByRole("textbox", { name: "Search tasks" }).fill("Nginx routing");
    await expect(page.getByRole("heading", { name: "Review E2E coverage" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Completed E2E task" })).not.toBeVisible();

    await page.getByRole("textbox", { name: "Search tasks" }).fill("");
    await updatedTask.getByRole("button", { name: "Delete" }).click();
    await expect(page.getByRole("heading", { name: "Review E2E coverage" })).not.toBeVisible();
  });

  test("rejects an unauthenticated API request", async ({ browser }) => {
    const unauthenticatedContext = await browser.newContext({ ignoreHTTPSErrors: true });
    const response = await unauthenticatedContext.request.get("https://localhost:8443/tasks");

    expect(response.status()).toBe(401);
    await unauthenticatedContext.close();
  });
});
