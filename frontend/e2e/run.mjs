import { spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, rmSync, unlinkSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDirectory = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const projectDirectory = resolve(frontendDirectory, "..");
const certificatesDirectory = resolve(frontendDirectory, "e2e/.certs");
const lockFile = resolve(frontendDirectory, "e2e/.runner.lock");
const composeFile = resolve(projectDirectory, "docker-compose.e2e.yml");
const compose = ["compose", "-f", composeFile];
const runnerArguments = process.argv.slice(2);
const reuseImages = runnerArguments.includes("--reuse-images");
const playwrightArguments = runnerArguments.filter((argument) => argument !== "--reuse-images");

let activeChild;
let interruptedSignal;
let ownsLock = false;

function isProcessRunning(processId) {
  try {
    process.kill(processId, 0);
    return true;
  } catch (error) {
    return error.code === "EPERM";
  }
}

function acquireLock() {
  try {
    writeFileSync(lockFile, `${process.pid}\n`, { flag: "wx" });
    return false;
  } catch (error) {
    if (error.code !== "EEXIST") {
      throw error;
    }

    const processId = Number.parseInt(readFileSync(lockFile, "utf8"), 10);

    if (Number.isInteger(processId) && isProcessRunning(processId)) {
      throw new Error(`An E2E runner is already active (PID ${processId}).`);
    }

    unlinkSync(lockFile);
    writeFileSync(lockFile, `${process.pid}\n`, { flag: "wx" });
    return true;
  }
}

function releaseLock() {
  if (existsSync(lockFile)) {
    unlinkSync(lockFile);
  }
}

function run(command, arguments_, options = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(command, arguments_, {
      cwd: frontendDirectory,
      stdio: "inherit",
      ...options,
    });

    activeChild = child;

    child.once("error", rejectPromise);
    child.once("exit", (code, signal) => {
      if (activeChild === child) {
        activeChild = undefined;
      }

      if (code === 0) {
        resolvePromise();
        return;
      }

      const reason = signal ? `terminated by ${signal}` : `exited with code ${code}`;
      const error = new Error(`${command} ${arguments_.join(" ")} ${reason}`);
      error.exitCode = code ?? 1;
      rejectPromise(error);
    });
  });
}

function delay(milliseconds) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, milliseconds));
}

async function createCertificate() {
  const certificate = resolve(certificatesDirectory, "localhost.crt");
  const privateKey = resolve(certificatesDirectory, "localhost.key");

  if (existsSync(certificate) && existsSync(privateKey)) {
    return;
  }

  mkdirSync(certificatesDirectory, { recursive: true });
  await run("openssl", [
    "req",
    "-x509",
    "-newkey",
    "rsa:2048",
    "-nodes",
    "-keyout",
    privateKey,
    "-out",
    certificate,
    "-days",
    "1",
    "-subj",
    "/CN=localhost",
    "-addext",
    "subjectAltName=DNS:localhost,IP:127.0.0.1",
  ]);
}

async function waitForApplication() {
  const deadline = Date.now() + 120_000;

  while (Date.now() < deadline) {
    try {
      await run(
        "curl",
        ["--fail", "--silent", "--show-error", "--insecure", "https://localhost:8443/health"],
        { stdio: "ignore" },
      );
      return;
    } catch {
      await delay(1_000);
    }
  }

  throw new Error("The E2E application did not become ready within two minutes.");
}

async function verifyReusableImages() {
  const images = [
    "todolist-e2e-frontend:latest",
    "todolist-e2e-backend:latest",
    "todolist-e2e-migrate:latest",
  ];

  try {
    await run("docker", ["image", "inspect", ...images], { stdio: "ignore" });
  } catch {
    throw new Error(
      "E2E fast mode requires existing images. Run `npm run test:e2e` first to build them.",
    );
  }
}

async function cleanUp() {
  try {
    await run("docker", [...compose, "down", "--volumes", "--remove-orphans"]);
  } finally {
    rmSync(certificatesDirectory, { recursive: true, force: true });
  }
}

function handleInterrupt(signal) {
  interruptedSignal = signal;
  activeChild?.kill(signal);
}

process.once("SIGINT", () => handleInterrupt("SIGINT"));
process.once("SIGTERM", () => handleInterrupt("SIGTERM"));

let exitCode = 0;

try {
  const staleRun = acquireLock();
  ownsLock = true;

  if (staleRun) {
    await cleanUp();
  }

  await createCertificate();
  if (reuseImages) {
    await verifyReusableImages();
    await run("docker", [...compose, "up", "--detach", "--no-build"]);
  } else {
    await run("docker", [...compose, "build"], { stdio: "ignore" });
    await run("docker", [...compose, "up", "--detach", "--no-build"]);
  }
  await waitForApplication();
  await run("npx", ["playwright", "test", ...playwrightArguments]);
} catch (error) {
  console.error(error.message);
  exitCode = error.exitCode ?? 1;
} finally {
  try {
    await cleanUp();
  } catch (error) {
    console.error(`E2E cleanup failed: ${error.message}`);
    exitCode ||= 1;
  } finally {
    if (ownsLock) {
      releaseLock();
    }
  }
}

if (interruptedSignal) {
  exitCode = 128 + (interruptedSignal === "SIGINT" ? 2 : 15);
}

process.exitCode = exitCode;
