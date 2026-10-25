---
doc: spec
status: approved
---

# UNSTUCK — Technical Spec

## How This Works, In Plain Language
FastAPI serves one HTML page and its CSS and JavaScript. Users type or optionally dictate into the same textarea; dictation never submits automatically. On explicit submission, the browser sends the user’s thoughts to our Python endpoint, which calls Gemini with a private API key and returns a validated priority selection with source evidence, a server-built explanation, a supportive acknowledgment, one action, and a duration. After completion, Continue sends the original task, ordered completed actions, current action, and prior priority to get a logical follow-up while reassessing priorities when progress warrants it. The browser displays the result and runs the timer itself. Nothing is saved between visits. One local process serves the entire app, without a frontend build system or database.

## The Core Journey Through the System
Implements `prd.md > The Core Journey`.
1. Browser loads `/` and assets under `/static/`.
2. Optional browser recognition appends editable final phrases; explicit submission validates the text and posts JSON to `/api/step`.
3. FastAPI validates it again, calls Gemini, validates the structured response, and returns JSON.
4. Retry and Continue send the original thoughts, ordered completed actions, and current action. Retry asks for an alternative unfinished action; Continue asks for a logical next action after completion. Input edits alone do not replace the original task.
5. The browser replaces the result only on success and runs focus/completion controls locally. Refresh clears all state.

## Stack
- Python 3.11+; FastAPI for routing and validation; Uvicorn to serve locally. Learner accepted this familiar stack. [FastAPI](https://fastapi.tiangolo.com/) · [Uvicorn](https://www.uvicorn.org/).
- Plain HTML/CSS/JavaScript; no frontend framework, bundler, or external font dependency. [Browser APIs](https://developer.mozilla.org/en-US/docs/Web/API).
- Official `google-genai` Python SDK for Gemini; Pydantic response validation. [SDK](https://googleapis.github.io/python-genai/) · [Pydantic](https://docs.pydantic.dev/latest/).
- `python-dotenv` to load local configuration without overriding existing environment variables. [Documentation](https://bbc2.github.io/python-dotenv/).
- Runtime and test dependencies are installed and tested in an isolated virtual environment; direct versions are pinned in requirements.txt. Browser voice input adds no Python/JavaScript package or external transcription API.

## Where It Runs and How Someone Tries It
Local-only app. From the repository root:
```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
# Edit .env locally to set GEMINI_API_KEY.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8017
```
Open `http://127.0.0.1:8017`. Local environment needs internet access to Gemini and an API key with model access/quota. Never paste credentials into chat. `.env.example` contains only a blank key and model configuration. `.env` remains ignored and is never served.

Record the real input (typed or dictated) → generated action → focus → completion → Continue flow for the required short demo video. The public GitHub repository must include setup instructions and the secret-free example. Deployment is deferred and does not replace either submission artifact.

## Look and Feel
Implements `prd.md > Look and Feel` and `Screens and Layout`.
Use charcoal near `#141319`, lavender near `#C4B5FD`, muted violet near `#8B78B8`, warm light text, and slightly lighter rounded card surfaces. Use a system sans-serif stack, generous spacing, subtle gradient accents and short opacity/position transitions disabled under reduced motion. A centered column expands comfortably on desktop and fits a 320px viewport. Visible keyboard focus, readable contrast, labeled controls, and polite status announcements. No dashboard, navigation, external fonts, or illustration assets.

## Components

### Page and Result View
`static/index.html`, `static/styles.css`, `static/app.js` implement `prd.md > Screens and Layout`, `Thought Input and AI Action`, and `States and Boundaries`. Use the exact learner-supplied copy. Render model output as text with `textContent`, never HTML. Validate before requests, prevent duplicate submissions, and preserve input/result on failure. Disable generation while focus is running or paused. Keep entered text separate from the last successfully submitted original input.

Failed retries show a neutral `role="status"` notice below the result controls, explicitly preserving the existing recommendation's validity. Keep first-request/input errors in their existing location. Clear stale notices before another request; never reset the timer or result on failure.

### Step Endpoint
`app/main.py` implements `prd.md > Thought Input and AI Action`. Serve `/` with a file response and mount only the `static/` directory. Do not expose repository files. Same-origin fetch needs no CORS configuration. `POST /api/step` accepts:
```json
{"thoughts":"I have three assignments and don't know where to start", "previous_action":null,"completed_actions":[],"mode":"suggest","priority_context":null}
```
Trim and require 1–2,000 characters; optional previous action is limited to 500 characters. Request mode is suggest, retry, or continue (default suggest for compatibility). completed_actions is an ordered list of at most 100 nonempty strings, each at most 500 characters, to bound request size. Continue requires at least one completed action and previous_action equal to its last item. Invalid context returns 422 before Gemini is called. Optional priority_context has task (1–180 chars), basis (deadline/urgency/importance/dependency/unspecified), and evidence (up to 300 chars). Stated bases require evidence; unspecified requires empty evidence. Incoming task/evidence must occur in the original thoughts. Return HTTP 200 with:
```json
{"acknowledgment":"That sounds like a lot to hold at once.","action":"Open the nearest-deadline assignment and read its first instruction.","recommended_minutes":7,"priority":{"task":"assignments","basis":"unspecified","evidence":""},"priority_reason":"A manageable starting point; no unstated deadline or urgency is assumed."}
```
This is an illustrative contract, not a fallback AI response. Require nonempty acknowledgment (max 300 characters), nonempty action (max 500), and strict integer minutes 5–10. Do not return unvalidated model text. Use one concise `{ "detail": "..." }` error message; normalize FastAPI validation messages in the browser.

### Gemini Adapter
`app/ai.py` implements `prd.md > Thought Input and AI Action`. Load `GEMINI_API_KEY` server-side; make one asynchronous `client.aio.models.generate_content` call per request, with a Gemini-compatible explicit `types.Schema` and concise output. Keep strict Pydantic validation locally; do not send its `additionalProperties: false` field through Gemini's subset response schema. Use a separate system instruction for one feasible, supportive action; treat submitted thoughts and previous action as user data, not instructions. Include previous_action for retry and continuation as current task context. Include ordered completed_actions and mode; instruct Gemini to build on finished work and choose a materially different unfinished action. Reject repeated completed actions after whitespace/case/trailing-punctuation normalization. Reject an identical returned action with a recoverable error; do not retry content rejection automatically. No tools, chat session, streaming, agents, or stored conversation.

### Browser Timer and Completion
`static/timer.js` implements `prd.md > Focus Timer` and `Completion and Retry`. Export a small timer controller usable by the page and deterministic tests. Keep selected duration, remaining milliseconds, running deadline, and phase (`ready`, `running`, `paused`, `expired`, `complete`) in memory. Default to 7 minutes; whole-minute select 5–10. The recommendation is displayed separately and does not overwrite the selected duration.

Start sets a deadline using the browser clock; render remaining time from that deadline rather than decrementing a counter. Reconcile on visibility change, so delayed background callbacks do not extend focus. Pause captures remaining time, resume creates a new deadline, reset restores selected duration, completion stops callbacks. Clamp at zero, use ceiling seconds for display, and fire expiry once. No service worker, notification, storage, or requirement to survive closing the page. A successful new result resets timer selection to 7 and clears completion; failure leaves the existing result/session intact. Duration selection is locked until reset after a session starts. Generation is allowed again after expiry, reset, or completion.

## Data Model
Browser memory: editable thoughts, original submitted thoughts associated with the current result, current result, loading/error message, selected duration, and timer phase/time fields. Update the result and its original input atomically on successful requests. There is no persistent history collection. The browser keeps the last valid priority object in current.priority, sent as priority_context for retry/continue and replaced only on valid success. A successful fresh input or refresh clears it with progress. The browser keeps an ordered completedActions array for the current task, appended exactly once on explicit completion and sent with retry/continue requests; only its length is displayed. main.py validates it, and ai.py includes it with mode, thoughts, and previous_action in the Gemini prompt. Strict local comparison rejects normalized repeats of completed actions; semantic continuity is instructed by the AI prompt. A successful main submission or refresh clears this array. There is no server-side session store. FastAPI holds only transient request data; Gemini credentials are environment configuration. Do not log thoughts, model text, keys, or raw provider errors. App data disappears on refresh; processing by the external provider follows its own policies.

## File Structure
```text
app/
  __init__.py       # Python package
  main.py           # Routes, contracts, local configuration
  ai.py             # Gemini call and output validation
static/
  index.html        # Single page and accessible controls
  styles.css        # Responsive calming visual treatment
  app.js            # Request flow, rendering, control wiring
  timer.js          # Browser countdown logic
  speech.js         # Optional browser-native dictation controller
tests/
  test_api.py       # Validation, provider errors, response contract
  timer.test.mjs    # Deterministic timer lifecycle checks
  browser_check.py  # Progression, timer and error browser checks
  speech_browser_check.py # Fake-engine dictation/browser integration checks
  priority_browser_check.py # Priority/context/reassessment browser checks
requirements.txt   # Tested runtime and small test dependencies
.env.example       # Blank GEMINI_API_KEY and configurable GEMINI_MODEL
.gitignore         # Secrets, learner profile, venv and caches
README.md          # Required setup, verification, demo guidance
LICENSE            # MIT license
devpost/           # Required curriculum planning artifacts
```

## External Services and Dependencies
Gemini is the only external service called by FastAPI. Optional native browser recognition may use the browser’s own online speech service; no separate transcription API is integrated by UNSTUCK. Default `GEMINI_MODEL=gemini-3.1-flash-lite`, configurable so an account-supported model can be selected without changing code. Real generation was confirmed by the learner and a live continuation check produced a logical writing action after the supplied completed steps. Intermittent upstream high-demand 503 errors remain possible and preserve the previous result/progress. Model listing alone does not prove inference availability. [Models](https://ai.google.dev/gemini-api/docs/models).

SDK call maps to `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`, authenticating with the API key in a header. Payload contains `systemInstruction`, `contents` with the serialized thoughts/previous action, and `generationConfig` with `responseMimeType: application/json` and the output JSON schema. The SDK extracts JSON text from candidate content; validate with Pydantic before returning our response. Missing/blocked/empty output is an error. [GenerateContent](https://ai.google.dev/api/generate-content) · [Structured output](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en).

Timeout: 30 seconds server-side for the entire operation, 35 seconds browser-side. Allow at most one SDK retry after one second for HTTP 503 only, within the same total server deadline, following observed transient provider overload. Do not retry authentication, configuration, or quota failures automatically. Use a bounded output budget of 2,048 tokens. Cost and quota depend on model and account tier; do not assume free access or enable billing automatically. No polling or unbounded retries. [Pricing](https://ai.google.dev/gemini-api/docs/pricing) · [Project-specific rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

## Important Failure Modes
- Invalid input → inline validation; server returns 422 if bypassed; no provider call.
- Missing key/model access, quota, or upstream timeout → sanitized 503/429/504 response as appropriate; preserve input and current result, offer manual retry. Never expose raw provider details.
- Blocked, malformed, empty, or identical retry output → sanitized 502 error; retain prior valid state and allow retry. Never simulate successful AI output.

## Verification
Trace every behavior to the PRD: API tests cover invalid/blank/oversized input, valid schema, malformed output, missing configuration, and provider failures using explicit test doubles. Timer tests cover start, pause/resume, reset, expiry after delayed callbacks, and early completion with an injected clock. Workflow browser checks cover initial state, responsive layout, loading/errors, three-step progression, ordered context, failed Continue/retry recovery, progress reset, and completion before/after expiry. Speech browser checks use a fake recognition engine for start/stop, text editing, no auto-submit, language/prefix fallback, permission/service errors, cancellation, and timer/progression integration. Real generation and continuation have separate live evidence, and the learner manually tested and approved microphone input. Test doubles never count as real audio or live Gemini evidence. No frontend toolchain is required.

## What Was Simplified and Why
One FastAPI process serves the page and API, avoiding a separate frontend service. Browser-only ephemeral timer/state removes storage and background infrastructure. Local recording avoids deployment work. Real Gemini generation remains essential; no mocks in the product.

## Decisions and Open Issues
- Learner accepted FastAPI + plain HTML/CSS/JavaScript, server-side AI calls, and local demo.
- Learner chose Gemini and a local ignored `.env`, with a committed secret-free `.env.example`.
- No unresolved technical design decisions; provider availability remains an external operational dependency.
- Model default, contracts, timeouts, and file layout are implemented and mechanically verified. Provider service availability and browser speech support remain runtime dependencies.
- Original MVP, speech, and all three prioritization manual scenarios are approved. Progression is implemented with live and automated evidence. The public repository exists, while the combined prioritization/progression/voice update awaits separate publication approval. No demo video or Devpost submission has been completed.

## Submission Links
- Public GitHub repository: https://github.com/saffronpeach/UNSTUCK — published with explicit approval and verified without authentication. Exactly 20 files match the approved snapshot; one clean initial commit 2888b9da5b4f3f4c5aeeecba94e1776acb6e7838. Original development history was not published.
- Public demo video: learner confirms no recording yet. Record and upload after publication preparation; no URL exists.
- Devpost submission: learner confirms the form has not been started; final submission requires explicit approval.

## Implemented Session Progression
Implements `prd.md > Continue and Session Progress` in the existing endpoint, Gemini adapter, and page controller. Completion records an action exactly once in browser memory and updates the count. Continue preserves the original task and ordered progress; failures retain the completed state and permit another attempt. A successful new task or refresh clears progress. No new route, account, database, storage, or runtime dependency. Publication of this update requires a new explicit approval.

## Implemented Optional Browser Speech Input
Implements `prd.md > Speech-to-Text Input`. static/speech.js configures native SpeechRecognition/webkitSpeechRecognition with continuous=true, interimResults=false, maxAlternatives=1, and navigator.language → navigator.languages[0] → en-US. Final phrases append once per result index to the current textarea value; input events update the existing counter. No audio blobs, recording files, server route, transcription API, or runtime dependency.

The controller tracks idle/starting/listening/stopping states; render locks AI generation while active, disables microphone initiation during requests/focus, and permits stop/cancel. Stop accepts final results until end, with a two-second abort fallback if the browser fails to end. Errors use fixed messages, preserve text, release the active state, and ignore stale callbacks; pagehide aborts recognition. Browser-native processing may use an external speech service, disclosed beside the control. Browser feature detection, not a fixed compatibility list, determines availability. [Reference](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition).

Tests use a fake engine in isolated Chrome to exercise transcript events, duplicate results, editing, permissions, constructor/start failure, unsupported/prefixed APIs, language fallback, stop-before-start, late callbacks, final-on-stop, limit handling, cancellation timeout, original progression context, timer compatibility, and narrow layouts. These fake-engine tests do not claim real audio recognition. The learner separately reports manual microphone testing and approves the feature. A final audited GitHub update is prepared for publication approval; no push is authorized yet.

## Implemented Lightweight Priority Selection
Architecture check: this is an extension to the existing Step/StepRequest models, Gemini schema/prompt, and result rendering. No new endpoint, service, runtime dependency, persistent store, task dashboard, or clock-based scheduling engine.

app/ai.py defines PriorityContext(task, basis, evidence). The explicit Gemini schema requests this nested object plus the existing acknowledgment/action/duration. Step validation generates priority_reason from the basis label and quoted evidence, overriding any model-supplied free-form reason. For unspecified ranking, use a fixed neutral reason. Validate normalized task/evidence as source excerpts; reject unsupported excerpts and common English negations that contradict a claimed factor. Other linguistic/semantic interpretation remains AI judgment guided by the no-invention prompt. Do not imply that string grounding proves all semantic ranking decisions.

app/main.py validates optional priority_context before the provider call. static/app.js sends the original thoughts, ordered completed actions, mode, current action, and current.priority on Continue/retry; fresh submissions send null context. Only valid responses replace the priority display. The existing error path preserves prior priority/progress/timer state on failure. Render the task/reason with textContent in a small section within the existing result card.

Tests cover all stated factor contracts, missing information, source grounding, rejected invented evidence, common negations, safe explanation construction, continuation/reassessment context, preserved failures, and minimal priority rendering. Live generic-task checks passed for an essay due tomorrow, continued essay work, and a neutral no-ranking case. The learner manually tested and approved all three prioritization scenarios. The final 23-file combined update is prepared for audit and publication approval; the public initial repository remains unchanged.
