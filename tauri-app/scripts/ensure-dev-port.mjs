import { execSync } from "node:child_process";

function getListeningPidsWindows(port) {
  try {
    const output = execSync(`netstat -ano -p tcp | findstr :${port}`, {
      stdio: ["ignore", "pipe", "ignore"],
      encoding: "utf8",
    });

    return output
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .filter((line) => line.includes("LISTENING"))
      .map((line) => line.split(/\s+/).at(-1))
      .filter((pid) => pid && /^\d+$/.test(pid));
  } catch {
    return [];
  }
}

function killPidWindows(pid) {
  execSync(`taskkill /PID ${pid} /F`, {
    stdio: ["ignore", "ignore", "ignore"],
  });
}

const port = Number(process.argv[2] ?? "1430");

if (!Number.isInteger(port) || port <= 0) {
  console.error(`[dev:prepare] Invalid port: ${process.argv[2] ?? ""}`);
  process.exit(1);
}

if (process.platform !== "win32") {
  process.exit(0);
}

const pids = [...new Set(getListeningPidsWindows(port))];

if (pids.length === 0) {
  console.log(`[dev:prepare] Port ${port} is free.`);
  process.exit(0);
}

for (const pid of pids) {
  try {
    killPidWindows(pid);
    console.log(`[dev:prepare] Closed process ${pid} on port ${port}.`);
  } catch (error) {
    console.error(`[dev:prepare] Failed to close process ${pid} on port ${port}.`);
    if (error instanceof Error) {
      console.error(error.message);
    }
    process.exit(1);
  }
}
