---
doc: prd
status: approved
---

# UNSTUCK — Product Requirements

A single-page application helping students and people experiencing overwhelm turn typed or spoken thoughts into one small action, focus, and continue to a logical next action after completion.
Source: `scope.md > The Unique Kernel`, `Who It's For`, and `The POC Boundary`.

## The Core Journey
1. Open the page and type what is overwhelming you, or start the optional microphone, dictate, stop, and edit the text. Nothing submits automatically.
2. Select “Help me get unstuck.” See loading feedback, then a short supportive acknowledgment, exactly one concrete next action, and a recommended focus duration.
3. Optionally select “Try another step” to request a different small action for the same original input.
4. Select “Start Focus” to reveal and start the timer. Default to 7 minutes; allow adjustment from 5 to 10 minutes before starting. Pause, resume, or reset as needed.
5. At zero, show “You did it! Every small step counts.” Offer completion or another step. Completing early also stops the timer and shows a short positive message.
6. Mark complete, then select “Continue → Next Step” to build on completed work without re-entering the task. Repeat for the current task; display the completed count.
Source: `scope.md > The Core Loop` and `What "Working" Looks Like`.

## Screens and Layout
One responsive page, no navigation. Header: UNSTUCK and “One step at a time.” Centered main content: “What's keeping you stuck?”, a large labeled text input with placeholder “I have so much to do and don't know where to start...”, and “Help me get unstuck.” The microphone button and listening/help status sit beside the existing textarea. Results and timer appear below in rounded cards; a completed-step count and prominent Continue button appear with completion. All controls remain usable on narrow screens without horizontal scrolling.

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
- Replace the displayed action on successful generation. Keep an ordered in-memory list of completed actions for the current task only; no history screen or persistent records.
- If “Try another step” fails, show a calm notice beside that control explaining that only the new request failed and the previous recommendation remains usable. Keep the previous acknowledgment, action, recommended duration, selected timer duration, and completion state; clear the notice when requesting again. First-request errors remain beside the input.
- Acceptance: real input produces the three response elements; retry requests an alternative for the same input; invalid input is blocked; a failed request preserves text and any existing result.
Source: `scope.md > The Unique Kernel`, `The Core Loop`, and `The POC Boundary`.

### Speech-to-Text Input
- Add a keyboard-accessible microphone button beside the existing input, using browser SpeechRecognition or webkitSpeechRecognition only. No transcription API, audio backend endpoint, or new account/key.
- First click starts recognition after browser permission. Show a textual listening state and pressed state; click again to stop. Starting focus also stops recognition. Do not auto-restart recognition after the browser ends it.
- Final recognized phrases append once to the existing editable textarea, preserving typed edits and respecting its 2,000-character limit. Update the character count. Never auto-submit; generation controls remain disabled while recognition starts/listens/stops, and become available again afterward.
- Use navigator.language, then navigator.languages[0], then en-US. Recognition support varies; show an explanatory disabled control and retain manual typing if unsupported.
- Permission denial, unavailable microphone/service, no speech, unsupported language, network errors, and start failures show safe actionable messages without discarding text. A stale callback after a session has ended or errored must not change the input; final phrases delivered while stopping are retained. Bound cancellation if an engine never fires end.
- Explain that the browser may use an online speech service. UNSTUCK has no audio endpoint and sends text to Gemini only on explicit user submission; unsent speech edits do not change the original progression task.
- Acceptance: start/stop by mouse and keyboard; see editable recognized text without an AI request; recover from errors; submit manually; Continue/retry and timer controls still behave as specified. Automated fake-engine tests cover browser/error states; the learner has manually tested and approved the microphone feature.
Source: explicit learner request and manual approval of the voice feature; publication approval remains separate.

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
- The completion state prominently offers “Continue → Next Step,” alongside the existing retry control. Keep an ordered completed-action list in memory only; increment it exactly once per completed action and show “1 step completed” or “3 steps completed.” No persisted record or statistics dashboard.
- Acceptance: completing early stops the timer; expiry leaves completion as a user choice; a successful retry returns to a fresh action with a 7-minute timer default.
Source: `scope.md > The Core Loop` and `Explicitly Cut`.

### Continue and Session Progress
- Continue is available only after explicitly marking the current action complete, including completion after expiry. Reaching zero alone does not add an action or reveal Continue.
- Send the original successful task input, ordered completed actions, and current action as task context. Ask Gemini for one logically subsequent action that builds on progress and does not repeat completed work.
- Successful continuation preserves the completed list/count, replaces the current result, and resets the focus timer to its 7-minute default. The Continue button hides until the new action is completed.
- Retry keeps the same original task and completed list, asking for an alternative unfinished action; it does not count the rejected action as complete.
- Failed continuation preserves the current result, completed list/count, timer/completion state, and original input. Show a result-local notice and re-enable Continue for another attempt; disable duplicate requests while loading.
- Editing the text alone does not change the task context. A successful main-form submission starts a fresh task and clears completed actions; failed submissions do not clear progress. Refresh/close discards all state.
- Acceptance: complete three distinct actions and see “3 steps completed”; inspect ordered progress in subsequent requests; failures preserve that count and allow the same request again. No dashboard, accounts, database, or persistent storage.
Source: `scope.md > The Core Loop` and `The POC Boundary`; explicitly requested progression extension; implemented and tested locally, with publication approval pending.

## States and Boundaries
- **First use:** show input and primary button; hide result and timer until needed.
- **Loading:** visible progress text, disabled duplicate submission controls; no lost input.
- **AI failure or unusable response:** show a short recoverable inline error and allow manual retry. Preserve the original input and existing valid result. Never substitute a canned response while implying AI succeeded.
- **Active, paused, reset, expired, complete:** reflect the timer and completion behavior above with clear control labels.
- **Refresh/close:** input, action, completed-action list/count, timer, and completion state are discarded. No persistent browser storage, accounts, or database.
- **Accessibility:** labeled input and controls, keyboard operation, readable status feedback, no reliance on color alone.

## Product Decisions
- Learner chose one page with no navigation to keep the interface minimal.
- Learner chose acknowledgment + one action + duration, real AI retry for the same input, and a 7-minute adjustable timer with start/pause/resume/reset.
- Learner supplied exact welcome, input, expiry copy, and visual direction.
- Learner requested sensible defaults for validation/loading/errors and authorized finalization once these decisions were incorporated. Character limit, timer locking, recommendation handling, reset semantics, and completion copy above are implementation defaults rather than independently volunteered preferences.

## What We're Building
The single-page core journey, optional browser dictation, real AI generation and retry, context-aware Continue progression with an in-memory completed count, responsive calming design, focus controls, completion, and recoverable errors. Verification covers the loop, full timer behavior, invalid input, and AI failure. A short demo can show generation and focus starting without waiting seven minutes on camera.

## Non-Goals
Accounts, databases, persistent storage, notifications, persistent task history, dashboards, and optional features remain excluded for the scope's stated reasons. No extra screens, analytics, or gamification. No optional enhancements are committed.
Source: `scope.md > Explicitly Cut` and `Later`.

## Open Questions
No blocking implementation decisions. Browser speech support and Gemini availability remain external limitations with typing/manual-retry fallbacks. Feature work is frozen; publication requires explicit approval of the audited update, followed by demo recording and submission review.
