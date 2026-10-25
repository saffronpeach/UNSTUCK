---
doc: scope
status: approved
---

# UNSTUCK

A minimal AI-powered web application that helps users identify a current priority from their stated constraints, start one small action, focus, and continue making progress. Input can be typed or optionally dictated.

## The Unique Kernel
Reduce the decision of what matters and where to start to one grounded priority and one immediately actionable step, then help the user begin it with a 5–10 minute timer. The central proof is the transition from overwhelm to action, followed by continued progress without re-entering the task.

## Who It's For
Students and people struggling with task initiation or overwhelm, who have something to do but need help identifying a manageable starting point.

## The Core Loop
Open UNSTUCK → type what is overwhelming you, or dictate and stop voice input before submitting → see one priority and its stated basis, plus one small, concrete action from a real AI API → start a 5–10 minute focus timer → mark the action complete or retry. After completion, Continue → Next Step uses the original input, prior priority, and completed actions to keep progressing on the same task. Only the current session remembers these actions; a new submission or refresh starts fresh.

## Inspiration & Identity
A calm, responsive single page: charcoal background, lavender/violet accents, rounded cards, clean sans-serif typography, spacious layout, and restrained motion. Optional voice input shares the same input surface; progress is a simple completed-step count.

## Why This Matters to the Learner
Demonstrate a small working thought-to-action-to-focus loop and prepare the required hackathon submission without expanding the proof-of-concept boundary.

## What "Working" Looks Like
A person opens the app on a phone or desktop, types or optionally dictates an overwhelming task, explicitly submits it, and sees one concrete action from a real AI request. They can focus, complete the action, and Continue to a logical follow-up using the original task and session-only completed actions. The count increases once per completed action. Failed requests preserve progress. A short demo can show this loop using early completion without waiting through a full focus session.

Basic error handling lets the user recover from empty input or a failed AI request without losing their entered text. The timer and completion flow can be checked separately through a full session during verification.

Submission preparation includes the required short demo video and public GitHub repository. Deployment is optional. Keep the project sized for the curriculum's target of 2–4 hours of active work; this is a planning target, not a delivery guarantee.

## The POC Boundary
- Simple responsive interface for the core loop, with optional browser-native speech-to-text entry where supported; typing always remains available.
- Real AI API integration that weighs stated deadlines, urgency, importance, and dependencies; shows one priority with a short grounded explanation; and recommends exactly one small next action. No invented deadlines or assumed urgency when information is missing.
- Short focus timer within the requested 5–10 minute range.
- Mark the action complete, retry, or continue to a logically subsequent step; show a session-only completed-step count.
- Basic validation, loading feedback, and recoverable errors.
- No persistence requirement; the proof of concept works within the current session.

The PRD defines the implemented screen, voice controls, retry/progression semantics, and errors; the technical spec defines the FastAPI/Gemini/browser implementation. This release is limited to those implemented features.

## Later
The only authorized addition to the previous release scope is lightweight prioritization in the existing result and request flow. No further features are planned. Remaining work is publication approval, demo recording, and the Devpost form; no further features are planned.

## Explicitly Cut
- Accounts: unnecessary to demonstrate the core loop.
- Databases: no saved records are needed for this proof of concept.
- Notifications: the focus session can remain on screen.
- Persistent task history: excluded. An in-memory completed-action list for the current task is explicitly included for continuation, with only a count displayed.
- Complex dashboards: they do not help prove the transition to one action.
- Other optional features: protect the smallest functioning proof of concept and submission timeline.
