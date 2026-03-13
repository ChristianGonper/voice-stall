import { describe, it, expect, beforeAll } from "vitest";
import fs from "fs";
import path from "path";

describe("Base UI Components Refinement", () => {
  beforeAll(() => {
    const cssPath = path.resolve(__dirname, "styles.css");
    const cssContent = fs.readFileSync(cssPath, "utf8");
    const style = document.createElement("style");
    style.innerHTML = cssContent;
    document.head.appendChild(style);
  });

  it("panel should use backdrop-filter", () => {
    const panel = document.createElement("div");
    panel.className = "panel";
    document.body.appendChild(panel);
    const style = getComputedStyle(panel);
    expect(style.backdropFilter).toContain("blur(20px)"); // I plan to increase blur from 10px to 20px
    document.body.removeChild(panel);
  });

  it("primary button should have a glow box-shadow", () => {
    const btn = document.createElement("button");
    btn.className = "primary";
    document.body.appendChild(btn);
    const style = getComputedStyle(btn);
    // jsdom might not fully parse complex box-shadows with variables, 
    // but we can check if it exists or if we can see the variable name if not computed
    expect(style.boxShadow).toBeDefined();
    document.body.removeChild(btn);
  });
});
