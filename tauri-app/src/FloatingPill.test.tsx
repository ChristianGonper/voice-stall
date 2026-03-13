import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FloatingPill } from "./FloatingPill"; // I will extract it or create it

describe("FloatingPill Component", () => {
  it("should render correctly with transcription text", () => {
    render(
      <FloatingPill 
        status="recording" 
        statusTone={(s) => "recording"} 
        statusMessage="Test transcription" 
        onToggle={() => {}} 
        onExpand={() => {}} 
      />
    );
    expect(screen.getByText("Test transcription")).toBeDefined();
  });

  it("should show recording status dot", () => {
    const { container } = render(
      <FloatingPill 
        status="recording" 
        statusTone={(s) => "recording"} 
        statusMessage="Test" 
        onToggle={() => {}} 
        onExpand={() => {}} 
      />
    );
    const dot = container.querySelector(".dot.bg-recording");
    expect(dot).toBeDefined();
  });
});
