---
doc: spec
status: approved
---

# UNSTUCK — Technical Spec

## How This Works, In Plain Language
FastAPI serves one HTML page and its CSS and JavaScript. The browser sends the user's thoughts to our Python endpoint, which calls Gemini with a private API key and returns a validated acknowledgment, one action, and a duration. The browser displays the result and runs the timer itself. Nothing is saved between visits. One local process serves the entire app, without a frontend build system or database.

## The Core Journey Through the System
Implements `prd.md > The Core Journey`.
1. Browser loads `/` and assets under `/static/`.
2. JavaScript validates the text and posts JSON to `/api/step`.
3. FastAPI validates it again, calls Gemini, validates the structured response, and returns JSON.
4. Retry sends the original submitted thoughts and the current action; Gemini is instructed to choose a different starting action.
5. The browser replaces the result only on success and runs focus/completion controls locally. Refresh clears all state.

## Stack
- Python 3.11+; FastAPI for routing and validation; Uvicorn to serve locally. Learner accepted this familiar stack. [FastAPI](https://fastapi.tiangolo.com/) · [Uvicorn](https://www.uvicorn.org/).
- Plain HTML/CSS/JavaScript; no frontend framework, bundler, or external font dependency. [Browser APIs](https://developer.mozilla.org/en-US/docs/Web/API).
- Official `google-genai` Python SDK for Gemini; Pydantic response validation. [SDK](https://googleapis.github.io/python-genai/) · [Pydantic](https://docs.pydantic.dev/latest/).
- `python-dotenv` to load local configuration without overriding existing environment variables. [Documentation](https://bbc2.github.io/python-dotenv/).
- Install compatible current releases in an isolated virtual environment, verify together, and record tested versions in `requirements.txt` during build. No versions have been installed or tested yet.

## Where It Runs and How Someone Tries It
Local-only app. From the repository root:
```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Edit .env locally to set GEMINI_API_KEY.
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8017
```
Open `http://127.0.0.1:8017`. Local environment needs internet access to Gemini and an API key with model access/quota. Never paste credentials into chat. `.env.example` contains only a blank key and model configuration. `.env` remains ignored and is never served.

Record the real input → generated action → focus-start flow for the required short demo video. The public GitHub repository must include setup instructions and the secret-free example. Deployment is deferred and does not replace either submission artifact.

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
{"thoughts":"I have three assignments and don't know where to start", "previous_action":null}
```
Trim and require 1–2,000 characters; optional previous action is limited to 500 characters. Return HTTP 200 with:
```json
{"acknowledgment":"That sounds like a lot to hold at once.","action":"Open the nearest-deadline assignment and read its first instruction.","recommended_minutes":7}
```
This is an illustrative contract, not a fallback AI response. Require nonempty acknowledgment (max 300 characters), nonempty action (max 500), and strict integer minutes 5–10. Do not return unvalidated model text. Use one concise `{ "detail": "..." }` error message; normalize FastAPI validation messages in the browser.

### Gemini Adapter
`app/ai.py` implements `prd.md > Thought Input and AI Action`. Load `GEMINI_API_KEY` server-side; make one asynchronous `client.aio.models.generate_content` call per request, with a Gemini-compatible explicit `types.Schema` and concise output. Keep strict Pydantic validation locally; do not send its `additionalProperties: false` field through Gemini's subset response schema. Use a separate system instruction for one feasible, supportive action; treat submitted thoughts and previous action as user data, not instructions. Include previous action only for retries and ask for a materially different step. Reject an identical returned action with a recoverable error; do not loop automatically. No tools, chat session, streaming, agents, or stored conversation.

### Browser Timer and Completion
`static/timer.js` implements `prd.md > Focus Timer` and `Completion and Retry`. Export a small timer controller usable by the page and deterministic tests. Keep selected duration, remaining milliseconds, running deadline, and phase (`ready`, `running`, `paused`, `expired`, `complete`) in memory. Default to 7 minutes; whole-minute select 5–10. The recommendation is displayed separately and does not overwrite the selected duration.

Start sets a deadline using the browser clock; render remaining time from that deadline rather than decrementing a counter. Reconcile on visibility change, so delayed background callbacks do not extend focus. Pause captures remaining time, resume creates a new deadline, reset restores selected duration, completion stops callbacks. Clamp at zero, use ceiling seconds for display, and fire expiry once. No service worker, notification, storage, or requirement to survive closing the page. A successful new result resets timer selection to 7 and clears completion; failure leaves the existing result/session intact. Duration selection is locked until reset after a session starts. Generation is allowed again after expiry, reset, or completion.

## Data Model
Browser memory: editable thoughts, original submitted thoughts associated with the current result, current result, loading/error message, selected duration, and timer phase/time fields. Update the result and its original input atomically on successful requests. There is no history collection. FastAPI holds only transient request data; Gemini credentials are environment configuration. Do not log thoughts, model text, keys, or raw provider errors. App data disappears on refresh; processing by the external provider follows its own policies.

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
tests/
  test_api.py       # Validation, provider errors, response contract
  timer.test.mjs    # Deterministic timer lifecycle checks
requirements.txt   # Tested runtime and small test dependencies
.env.example       # Blank GEMINI_API_KEY and configurable GEMINI_MODEL
.gitignore         # Secrets, learner profile, venv and caches
README.md          # Required setup, verification, demo guidance
devpost/           # Required curriculum planning artifacts
```

## External Services and Dependencies
Gemini is the only external runtime service. Default `GEMINI_MODEL=gemini-3.1-flash-lite`, configurable so an account-supported model can be selected without changing code. A real structured-output probe succeeded with the local key. Subsequent inference calls returned upstream high-demand 503 errors, so complete live generation/retry verification remains pending provider recovery. Model listing alone does not prove inference availability. [Models](https://ai.google.dev/gemini-api/docs/models).

SDK call maps to `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`, authenticating with the API key in a header. Payload contains `systemInstruction`, `contents` with the serialized thoughts/previous action, and `generationConfig` with `responseMimeType: application/json` and the output JSON schema. The SDK extracts JSON text from candidate content; validate with Pydantic before returning our response. Missing/blocked/empty output is an error. [GenerateContent](https://ai.google.dev/api/generate-content) · [Structured output](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en).

Timeout: 30 seconds server-side for the entire operation, 35 seconds browser-side. Allow at most one SDK retry after one second for HTTP 503 only, within the same total server deadline, following observed transient provider overload. Do not retry authentication, configuration, or quota failures automatically. Use a bounded output budget of 2,048 tokens. Cost and quota depend on model and account tier; do not assume free access or enable billing automatically. No polling or unbounded retries. [Pricing](https://ai.google.dev/gemini-api/docs/pricing) · [Project-specific rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

## Important Failure Modes
- Invalid input → inline validation; server returns 422 if bypassed; no provider call.
- Missing key/model access, quota, or upstream timeout → sanitized 503/429/504 response as appropriate; preserve input and current result, offer manual retry. Never expose raw provider details.
- Blocked, malformed, empty, or identical retry output → sanitized 502 error; retain prior valid state and allow retry. Never simulate successful AI output.

## Verification
Trace every behavior to the PRD: API tests cover invalid/blank/oversized input, valid schema, malformed output, missing configuration, and provider failures using explicit test doubles. Timer tests cover start, pause/resume, reset, expiry after delayed callbacks, and early completion with an injected clock. Browser review covers initial state, exact copy, responsive layout, keyboard controls, loading/errors, same-input retry, and completion. Perform at least one genuine Gemini request and a full timer-session check before claiming the prototype works. Test doubles never count as live AI evidence. Test tooling is selected at build time based on available local tools; avoid adding a frontend toolchain.

## What Was Simplified and Why
One FastAPI process serves the page and API, avoiding a separate frontend service. Browser-only ephemeral timer/state removes storage and background infrastructure. Local recording avoids deployment work. Real Gemini generation remains essential; no mocks in the product.

## Decisions and Open Issues
- Learner accepted FastAPI + plain HTML/CSS/JavaScript, server-side AI calls, and local demo.
- Learner chose Gemini and a local ignored `.env`, with a committed secret-free `.env.example`.
- No unresolved technical design decisions; provider availability remains an external operational dependency.
- Model default, contracts, timeouts, and file layout are implementation choices derived from those decisions. Provider access, dependency compatibility, browser testing capability, and the live request must be verified during build.
- Implementation and final hands-on review are approved. Shipping preparation is underway; no remote repository, video URL, or Devpost submission is confirmed yet.

## Submission Links
- Public GitHub repository target: https://github.com/saffronpeach/UNSTUCK — publication not authorized yet; no public URL verified.
- Public demo video: learner confirms no recording yet. Record and upload after publication preparation; no URL exists.
- Devpost submission: learner confirms the form has not been started; final submission requires explicit approval.
