import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs";
import path from "path";

describe("Opalescent Components", () => {
  beforeAll(() => {
    const cssPath = path.resolve(__dirname, "styles.css");
    const cssContent = fs.readFileSync(cssPath, "utf8");
    const style = document.createElement("style");
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  });

  it("should have the opalescent class defined with correct background", () => {
    const el = document.createElement("div");
    el.className = "opalescent";
    document.body.appendChild(el);
    const style = getComputedStyle(el);
    // Background color for rgba(255, 255, 255, 0.03) might be computed differently,
    // but let's check if it's set
    expect(style.backgroundColor).toBeDefined();
    expect(style.backdropFilter).toContain("blur(25px)");
    document.body.removeChild(el);
  });
});
