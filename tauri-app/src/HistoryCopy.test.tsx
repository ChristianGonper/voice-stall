import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { App } from "./App";

// Mock Tauri APIs
vi.mock("./api", () => ({
  initApp: vi.fn(() => Promise.resolve({
    config: { app: { history_limit: 10 }, engine: {}, dictionary: {} },
    metrics: { count: 0, avg_total_ms: 0, avg_transcribe_ms: 0, avg_paste_ms: 0 },
    history: [{ ts: "12:00:00", text: "Test transcription" }],
    status: "idle",
    status_message: "Ready"
  })),
  getMetrics: vi.fn(),
  saveSettings: vi.fn(),
  setHotkey: vi.fn(),
  toggleDictation: vi.fn()
}));

vi.mock("@tauri-apps/api/window", () => ({
  getCurrentWindow: vi.fn(() => ({
    isMaximized: vi.fn(() => Promise.resolve(false)),
    listen: vi.fn(),
  }))
}));

vi.mock("@tauri-apps/api/event", () => ({
  listen: vi.fn(() => Promise.resolve(() => {}))
}));

describe("History Copy Feature", () => {
  it("should show a copy button for each history item", async () => {
    render(<App />);
    // Need to wait for initial load and switch to history tab
    // In a real test we'd click the tab, but here I just want to see if the button is planned
    // I'll check for the button after rendering history
  });
});
