import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HistoryItem } from "./HistoryItem";

const writeTextMock = vi.fn(async (_text: string) => {});

vi.mock("@tauri-apps/plugin-clipboard-manager", () => ({
  writeText: (text: string) => writeTextMock(text),
}));

describe("History copy feature", () => {
  it("copies the transcription and shows copied feedback", async () => {
    const user = userEvent.setup();
    render(<HistoryItem ts="12:00:00" text="Texto dictado" />);

    const button = screen.getByTitle("Copiar al portapapeles");
    await user.click(button);

    expect(writeTextMock).toHaveBeenCalledWith("Texto dictado");
    expect(screen.getByTitle("¡Copiado!")).toHaveClass("copied");
  });
});
