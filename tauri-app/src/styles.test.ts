import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs";
import path from "path";

describe("Enhanced Deep Night+ Palette", () => {
  beforeAll(() => {
    const cssPath = path.resolve(__dirname, "styles.css");
    const cssContent = fs.readFileSync(cssPath, "utf8");
    const style = document.createElement("style");
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  });

  it("should have the correct value for --bg-deep", () => {
    const bgDeep = getComputedStyle(document.documentElement).getPropertyValue("--bg-deep").trim();
    expect(bgDeep).toBe("#04080f");
  });

  it("should have the correct value for --bg-surface", () => {
    const bgSurface = getComputedStyle(document.documentElement).getPropertyValue("--bg-surface").trim();
    expect(bgSurface).toBe("#09111d");
  });

  it("should have the correct value for --bg-alt", () => {
    const bgAlt = getComputedStyle(document.documentElement).getPropertyValue("--bg-alt").trim();
    expect(bgAlt).toBe("#111b2d");
  });

  it("should have the correct value for --border-dim", () => {
    const borderDim = getComputedStyle(document.documentElement).getPropertyValue("--border-dim").trim();
    expect(borderDim).toBe("#1a263a");
  });

  it("should have the new --accent-glow variable", () => {
    const accentGlow = getComputedStyle(document.documentElement).getPropertyValue("--accent-glow").trim();
    expect(accentGlow).toBe("rgba(74, 144, 226, 0.4)");
  });

  it("should have the new --opalescent-bg variable", () => {
    const opalescentBg = getComputedStyle(document.documentElement).getPropertyValue("--opalescent-bg").trim();
    expect(opalescentBg).toBe("rgba(255, 255, 255, 0.03)");
  });

  it("should have the new --opalescent-border variable", () => {
    const opalescentBorder = getComputedStyle(document.documentElement).getPropertyValue("--opalescent-border").trim();
    expect(opalescentBorder).toBe("rgba(255, 255, 255, 0.08)");
  });
});
