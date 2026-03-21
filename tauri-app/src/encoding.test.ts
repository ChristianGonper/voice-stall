import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";

const SRC_DIR = path.resolve(__dirname);
const BAD_PATTERNS = [0xc3, 0xc2, 0xfffd].map((codePoint) =>
  String.fromCodePoint(codePoint),
);
const INCLUDED_EXTENSIONS = new Set([".ts", ".tsx", ".css", ".html", ".json"]);
const IGNORED_DIRS = new Set(["dist", "node_modules", "target"]);

function collectFiles(dir: string): string[] {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    if (entry.isDirectory()) {
      if (!IGNORED_DIRS.has(entry.name)) {
        files.push(...collectFiles(path.join(dir, entry.name)));
      }
      continue;
    }

    if (INCLUDED_EXTENSIONS.has(path.extname(entry.name))) {
      files.push(path.join(dir, entry.name));
    }
  }

  return files;
}

describe("source text encoding", () => {
  it("does not contain mojibake markers in src", () => {
    const offenders: string[] = [];

    for (const file of collectFiles(SRC_DIR)) {
      const contents = fs.readFileSync(file, "utf8");
      const matches = BAD_PATTERNS.filter((pattern) => contents.includes(pattern));

      if (matches.length > 0) {
        offenders.push(`${path.relative(SRC_DIR, file)} -> ${matches.join(", ")}`);
      }
    }

    expect(offenders).toEqual([]);
  });
});
