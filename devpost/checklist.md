---
doc: checklist
status: approved
build_status: complete
---

# Build Checklist

Build mode: fast — explicitly approved along with build order and local Git initialization.

## Slices

- [x] **1. Turn overwhelm into a real AI action and complete a focus session**
  Becomes usable: The complete minimal single-page UNSTUCK experience: submit thoughts, receive a real Gemini acknowledgment/action/duration, request another step, focus with a 5–10 minute timer, and mark complete.
  Why now: This small product has one core loop. One integrated slice proves its real AI kernel immediately and avoids separate scaffolding, backend, and frontend stages. One hands-on session can supply initial feedback and final review without repeated pauses.
  PRD ref: `prd.md > The Core Journey`, `Thought Input and AI Action`, `Focus Timer`, `Completion and Retry`, `Look and Feel`, `States and Boundaries`.
  Spec ref: `spec.md > Page and Result View`, `Step Endpoint`, `Gemini Adapter`, `Browser Timer and Completion`, `File Structure`, `Verification`, `Where It Runs and How Someone Tries It`.
  Build: Create the FastAPI app, Gemini adapter, validated request/response contracts, secret-free .env.example, ignored local configuration, responsive single-page UI, retry flow, browser timer controller, completion states, recoverable errors, and concise setup instructions. Install and record tested dependencies. No optional framework, storage, or deployment. Do not create or request a real key in chat.
  Verify (mechanical): Run API tests for valid requests, validation boundaries, retries, missing configuration, malformed/blocked model output, and provider failures using clearly labeled test doubles. Run deterministic timer tests for start, pause/resume, reset, delayed expiry, and early completion. Start the actual server, check page/assets and credential-file exclusion, and inspect the responsive browser workflow using available browser tools. Perform a genuine Gemini generation and retry only after a local key is configured; never treat test doubles as live verification. Check the full focus-session behavior. Fix failures and repeat affected checks before completion.
  Learner check: Configure GEMINI_API_KEY in the ignored .env locally, open http://127.0.0.1:8017, submit an overwhelming task, try another step, run the timer controls, and complete an action early. Inspect the page at a narrow width and try blank input. Report anything broken or confusing and confirm when ready to ship. A real request and a full timer session must be verified before declaring the prototype complete.
  Commit: `Build UNSTUCK AI action and focus workflow`

## Hands-on Checkpoints

- [x] Early usable behavior explored — learner reports successful real Gemini recommendation, focus interface, and completion state; requested clearer failed-retry feedback.
- [x] Final kick-the-tires exploration and feedback completed — learner explicitly approves the completed MVP and hands-on review.

## Final Review

- [x] Failed-retry refinement accepted in the learner’s explicit approval of the completed MVP and hands-on review.

Implementation is mechanically verified and the learner has approved the final hands-on review. The learner reports successful real Gemini generation, focus, and completion. Automated browser tests verify retry behavior and the full timer lifecycle with explicitly simulated responses; intermittent upstream Gemini 503 errors remain an external dependency limitation, handled without discarding valid results. No claim is made that the automated browser test called Gemini.

Implementation checkpoint: `862656d` (`Build UNSTUCK AI action and focus workflow`). Automated checks and screenshot review completed; temporary UNSTUCK test server stopped so the learner can launch with the documented command. The existing service on port 8000 was left untouched.

Automated evidence: 37 passing API tests; 7 passing timer tests; isolated Chrome browser checks for input validation, loading, preserved retry context, recoverable errors, full simulated focus session, early completion, inert model text, refresh reset, and layouts at 320/390/1280px. Desktop and mobile screenshots inspected. Python compilation, JavaScript syntax checks, and dependency compatibility checks pass. Current automated generated-response test data is explicitly simulated; genuine generation was separately confirmed by live diagnosis and the learner. Deterministic session checks do not claim seven minutes of real-time learner testing.

- [x] Final review complete — feedback resolved and learner explicitly confirms ready to ship.

## Code Tour and App Map

- [x] Learning activity complete — brief source-grounded recap supplied after final approval; no extra exercise or claim of mastery.
- [x] Optional edit and transfer reflection addressed — omitted per learner instruction.
- [x] Required wrap-up addressed here in Markdown; no HTML map per learner’s explicit instruction.

Activity and evidence: Brief recap connects one next-action request to the server endpoint, Gemini validation, and the browser timer. Regression evidence: tests/test_api.py, tests/browser_check.py, and tests/timer.test.mjs. Reusable practice: separate AI availability checks from deterministic UI/timer checks; model output test doubles do not prove live API access.
Route and stops: Reference route: static/app.js requestStep → app/main.py step → app/ai.py generate_step; static/timer.js FocusTimer manages the local countdown. To change copy/layout, start at static/index.html and static/styles.css; to change retry feedback, start at requestStep. This is a recap/reference route, not a claim of an interactive code tour.
Edit outcome: Optional edit omitted per learner's request to avoid optional work.
Reflection: Optional reflection omitted per learner's concise-curriculum preference.
Activity mode: Brief recap after final revisions; build complete by learner approval. Next: 6-ship, pending publication and submission approvals.

## Revisions

- On learner feedback, failed “Try another step” requests now show a neutral result-local notice that the previous recommendation remains usable. Preserve existing result, timer selection, and expiry/completion state; clear the notice on a new request. Browser regressions cover 503/429 failure, result preservation, successful responses, all timer controls, and completion before/after expiry. No new live API calls were needed; learner already confirmed a successful real recommendation. Credential checks confirm the local key is absent from served page/assets and .env is not served or tracked.

- Live diagnosis confirmed the local key loads correctly and the configured model is listed. Gemini rejected `additional_properties` generated from Pydantic `extra="forbid"` with HTTP 400; the previous generic handler masked it as 503. Use an explicit Gemini-compatible schema while retaining strict local validation. Add regression tests and distinguish request configuration, credential/access, quota, model availability, and upstream service failures with sanitized messages. The automated suite now has 37 API tests and 7 timer tests passing.
- A real structured-output probe succeeded on `gemini-3.1-flash-lite`; set that model in the ignored local .env and public default/example, preserving the key unchanged. Subsequent real application calls still received upstream 503 high-demand errors or 504 timeouts. No authentication or quota rejection was observed. Add at most one retry for 503 only within the existing 30-second total deadline; complete live generation/retry and hands-on review remain pending stable provider availability. Never mark live end-to-end verification complete based on the single successful probe.

- Local run port changed from 8000 to 8017 because 8000 was already occupied. No existing process or other project was changed; spec, checks, and run instructions use 8017.
- No HTML app map or extra document will be generated, following the learner's explicit Markdown-only/no-extra-documentation instruction. Required short wrap-up remains in this checklist after hands-on revisions.
- Python 3.14.7 and compatible dependency releases are installed in this project's .venv; tested direct versions are pinned. Playwright is optional verification tooling only and uses an isolated Chrome profile.
