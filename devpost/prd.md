---
doc: prd
status: approved
---

# UNSTUCK — Product Requirements

A single-page application helping students and people experiencing overwhelm turn their thoughts into one small action and a short focus session.
Source: `scope.md > The Unique Kernel`, `Who It's For`, and `The POC Boundary`.

## The Core Journey
1. Open the page and describe what is overwhelming you.
2. Select “Help me get unstuck.” See loading feedback, then a short supportive acknowledgment, exactly one concrete next action, and a recommended focus duration.
3. Optionally select “Try another step” to request a different small action for the same original input.
4. Select “Start Focus” to reveal and start the timer. Default to 7 minutes; allow adjustment from 5 to 10 minutes before starting. Pause, resume, or reset as needed.
5. At zero, show “You did it! Every small step counts.” Offer completion or another step. Completing early also stops the timer and shows a short positive message.
Source: `scope.md > The Core Loop` and `What "Working" Looks Like`.

## Screens and Layout
One responsive page, no navigation. Header: UNSTUCK and “One step at a time.” Centered main content: “What's keeping you stuck?”, a large labeled text input with placeholder “I have so much to do and don't know where to start...”, and “Help me get unstuck.” Results and timer appear below in rounded cards. All controls remain usable on narrow screens without horizontal scrolling.

## Look and Feel
Premium, calming, modern minimalism: dark charcoal background, soft lavender and muted violet accents, rounded cards, subtle gradients, spacious layout, clean sans-serif typography, and restrained smooth animation. Supportive, intelligent, reassuring language without excessive enthusiasm. Use readable contrast, visible keyboard focus, and respect reduced-motion preferences.
Source: `scope.md > Inspiration & Identity`, expanded by the learner's visual decisions.

## Features and Behavior

### Thought Input and AI Action
- Accept nonblank text; sensible default limit: 2,000 characters. Show a clear inline message for invalid input without making a request.
- Make a real AI request. Show a short acknowledgment, one specific starting action feasible within a short focus session, and a recommended duration of 5–10 whole minutes.
- Recommendations are advisory; the timer initially remains at the learner-chosen 7-minute default, with manual duration adjustment available.
- While waiting, show calm loading feedback and prevent duplicate requests. Keep the entered text intact.
- “Try another step” uses the original text associated with the current result and the current action to request a different action. Editing the text alone does not change that retry context; submitting the main button creates a new context.
- Replace the current action on successful generation; do not accumulate a list or history.
- If “Try another step” fails, show a calm notice beside that control explaining that only the new request failed and the previous recommendation remains usable. Keep the previous acknowledgment, action, recommended duration, selected timer duration, and completion state; clear the notice when requesting again. First-request errors remain beside the input.
- Acceptance: real input produces the three response elements; retry requests an alternative for the same input; invalid input is blocked; a failed request preserves text and any existing result.
Source: `scope.md > The Unique Kernel`, `The Core Loop`, and `The POC Boundary`.

### Focus Timer
- “Start Focus” reveals and starts the timer at the selected duration, initially 7 minutes. Duration choices are whole minutes from 5 through 10, editable before starting or after reset.
- Display remaining minutes and seconds. Pause freezes the remaining time; resume continues it. Reset stops the countdown and restores the selected duration without discarding the action.
- At zero, stop at 00:00 and show the learner's specified message with “Mark complete” and “Try another step.” No sound, system notifications, or background service.
- Keep one action/session at a time. During a running or paused session, disable new generation and retry; reset makes generation available again. A successful replacement action clears the old timer and completion state.
- Acceptance: each control has its stated effect; the countdown never goes negative; time spent in a background tab is reflected when the tab returns while running, and paused time does not count.
Source: `scope.md > The Core Loop` and `The POC Boundary`.

### Completion and Retry
- “Mark complete” is available after an action is generated, including during focus and at timer expiry. It stops any timer and displays “One small step done. That counts.”
- Completion is distinct from timer expiry; reaching zero alone does not mark the action complete.
- The completion state offers “Try another step”; the original input also remains available for a new submission. No saved completion record or statistics.
- Acceptance: completing early stops the timer; expiry leaves completion as a user choice; a successful retry returns to a fresh action with a 7-minute timer default.
Source: `scope.md > The Core Loop` and `Explicitly Cut`.

## States and Boundaries
- **First use:** show input and primary button; hide result and timer until needed.
- **Loading:** visible progress text, disabled duplicate submission controls; no lost input.
- **AI failure or unusable response:** show a short recoverable inline error and allow manual retry. Preserve the original input and existing valid result. Never substitute a canned response while implying AI succeeded.
- **Active, paused, reset, expired, complete:** reflect the timer and completion behavior above with clear control labels.
- **Refresh/close:** input, action, timer, and completion state are discarded. No persistent browser storage, accounts, or database.
- **Accessibility:** labeled input and controls, keyboard operation, readable status feedback, no reliance on color alone.

## Product Decisions
- Learner chose one page with no navigation to keep the interface minimal.
- Learner chose acknowledgment + one action + duration, real AI retry for the same input, and a 7-minute adjustable timer with start/pause/resume/reset.
- Learner supplied exact welcome, input, expiry copy, and visual direction.
- Learner requested sensible defaults for validation/loading/errors and authorized finalization once these decisions were incorporated. Character limit, timer locking, recommendation handling, reset semantics, and completion copy above are implementation defaults rather than independently volunteered preferences.

## What We're Building
The single-page core journey, real AI generation and retry, responsive calming design, focus controls, completion, and basic recoverable errors. Verification covers the loop, full timer behavior, invalid input, and AI failure. A short demo can show generation and focus starting without waiting seven minutes on camera.

## Non-Goals
Accounts, databases, persistent storage, notifications, task history, dashboards, and optional features remain excluded for the scope's stated reasons. No extra screens, analytics, or gamification. No optional enhancements are committed.
Source: `scope.md > Explicitly Cut` and `Later`.

## Open Questions
No blocking product questions. Stack, AI provider/model, API configuration, and local run instructions belong in `4-spec`. The technical plan requires learner agreement before code.
