# Specification: Fix UI Accents and Encoding

## Overview
This track addresses character encoding issues (mojibake) found in UI text for buttons, sections, and notifications. It also introduces an automated test to prevent similar issues in the future.

## Functional Requirements
- **Fix UI Text**: Correct incorrect characters (mojibake) in Spanish strings across the application UI (specifically in `App.tsx` and `HistoryItem.tsx`).
- **Automated Encoding Check**: Include a new test file `tauri-app/src/encoding.test.ts` that recursively scans source files for common mojibake patterns (like `Ã³`, `Ã±`, `Ã¡`, etc.).
- **Configuration Support**: Update `package.json` and `tsconfig.json` to support Node.js types and Vitest globals required for the new encoding test.

## Non-Functional Requirements
- **Build Integrity**: The application must build without errors after these changes.
- **Test Stability**: Existing tests must continue to pass, and the new encoding test must pass cleanly.

## Acceptance Criteria
- [ ] No mojibake characters are visible in the application UI (checked manually or via the new test).
- [ ] `tauri-app/src/encoding.test.ts` is present and its tests pass.
- [ ] `npm test` runs successfully in the `tauri-app` directory.
- [ ] All changes (source, tests, config) are staged and committed.

## Out of Scope
- Adding new features or modifying application logic beyond text fixes.
- Refactoring UI components unrelated to encoding issues.
