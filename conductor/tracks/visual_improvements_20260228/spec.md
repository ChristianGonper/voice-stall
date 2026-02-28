@
# Specification - Track visual_improvements_20260228

## Overview
This track focuses on resolving UI inconsistencies in the Tauri application. Specifically, it addresses an issue where the background appears white instead of black and improves the visual hierarchy by enhancing section contrast and divider visibility.

## Scope
- Fix the main window background color to be explicitly dark.
- Improve the visual distinction between the titlebar, app content, and mini-widget sections.
- Enhance the visibility of borders and dividers throughout the UI.

## Functional Requirements
- Modify tauri-app/src/styles.css to enforce --bg-deep: #07090C across all main containers.
- Update section background variables or styles to create a clear "layered" effect (e.g., slightly lighter interior against deep background).
- Brighten border colors (--border-dim) to make section dividers more apparent.
- Ensure the React App.tsx layout correctly applies these solid, opaque styles.

## Acceptance Criteria
- [ ] Window background is consistently #07090C (no white flashes or fallback).
- [ ] Titlebar, content panels, and footer have distinct, readable contrast.
- [ ] Section dividers and borders are clearly visible.
- [ ] The UI remains 100% opaque as per the "Deep Night Minimalist" guide.
@
