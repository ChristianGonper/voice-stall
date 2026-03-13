# Specification: Frontend UI/UX Enhancement & History Copy Feature

## Overview
This track focuses on elevating the "Voice Stall" frontend to a more premium, high-quality visual experience. We will refine the "Deep Night Minimalist" theme into an "Enhanced Deep Night+" aesthetic, implement a "Floating Pill" minimized mode, and add a direct "Copy" button to every history entry.

## Functional Requirements
1.  **Enhanced Deep Night+ Aesthetic**
    -   Refine UI components with deeper gradients, subtle glow effects, and higher-quality semi-transparent "opalescent" surfaces.
    -   Improve typography and spacing for a more polished, professional feel.
2.  **Floating Pill Minimized Mode**
    -   Implement a compact, pill-shaped interface for minimal distraction.
    -   The pill will display the record/stop button and the most recently transcribed text segment.
    -   The app will support switching between this Floating Pill and the full Main Window.
3.  **Always-Visible History "Copy" Button**
    -   Add a dedicated "Copy to Clipboard" icon button to every entry in the dictation history list.
    -   The button will be **always visible** (not just on hover) for immediate accessibility.
    -   Include a "Copied!" visual confirmation when the button is clicked.

## Non-Functional Requirements
-   **Visual Fidelity:** Maintain high legibility while using semi-transparent backgrounds.
-   **Performance:** UI enhancements must not introduce lag in the transcription display or window switching.
-   **Consistency:** The design language must remain cohesive across both minimized and maximized modes.

## Acceptance Criteria
-   [ ] The application can toggle between "Floating Pill" (minimized) and "Full" (maximized) views.
-   [ ] The UI consistently uses the refined "Enhanced Deep Night+" visual style.
-   [ ] Each history entry displays a working copy button that copies the correct text to the clipboard.
-   [ ] Transcription text is clearly legible in the minimized pill mode.

## Out of Scope
-   Changes to the Python backend transcription logic or `faster-whisper` settings.
-   New features outside of UI/UX and history management.
