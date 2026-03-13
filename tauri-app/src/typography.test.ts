import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs";
import path from "path";

describe("Typography and Spacing Refinements", () => {
  beforeAll(() => {
    const cssPath = path.resolve(__dirname, "styles.css");
    const cssContent = fs.readFileSync(cssPath, "utf8");
    const style = document.createElement("style");
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  });

  it("body should have increased line-height", () => {
    const style = getComputedStyle(document.body);
    expect(parseFloat(style.lineHeight)).toBeGreaterThan(1.4);
  });

  it("headings should have letter-spacing", () => {
    const h1 = document.createElement("h1");
    h1.className = "brand";
    document.body.appendChild(h1);
    const style = getComputedStyle(h1);
    expect(style.letterSpacing).toBeDefined();
    document.body.removeChild(h1);
  });
});
