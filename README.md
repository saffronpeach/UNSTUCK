# UNSTUCK

**One step at a time.** A small, local web application that turns overwhelming thoughts into one concrete action using Gemini, then helps you begin with a short focus timer.

Built with FastAPI, plain HTML/CSS/JavaScript, and server-side Google Gemini. No accounts, database, task history, or persistent browser storage.

## Run locally

Requires Python 3.11+ and internet access for Gemini. Tested with Python 3.14.7. All commands run inside this project; no other project needs to change.

```sh
cd UNSTUCK
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

Open `.env` in your editor and set `GEMINI_API_KEY` locally. The example includes a configurable `GEMINI_MODEL`; choose a model your Gemini account can access if the default is unavailable. Do not paste keys into chat or commit them. `.env`, `.env.*`, and the learner profile are ignored; the blank `.env.example` is safe to commit. Existing shell environment variables take precedence over `.env`.

```sh
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8017
```

Open **http://127.0.0.1:8017**. Port 8017 keeps this app separate from anything already using 8000. Stop with Ctrl+C. Restart after changing `.env`. For another computer, clone the repository, change into its directory, and use the same commands after the first `cd`.

Without a key, the interface still loads and shows a recoverable configuration error on generation. There are no fake AI responses in the app. Gemini quota, model access, and any usage charges depend on your Google account. [API setup](https://ai.google.dev/gemini-api/docs/api-key) · [Models](https://ai.google.dev/gemini-api/docs/models) · [Pricing](https://ai.google.dev/gemini-api/docs/pricing).

The default model is `gemini-3.1-flash-lite`. Upstream high-demand 503 responses receive at most one retry within the 30-second deadline; persistent service failures require trying later. Authentication, quota, model access, and request-configuration failures have distinct safe error messages. A listed model can still be unavailable for inference.

## Try the complete workflow

1. Enter an overwhelming task and select **Help me get unstuck**. Expect a short acknowledgment, one action, and a suggested duration.
2. Select **Try another step**. It should offer a different action for the original input, even if you edit the text field without resubmitting.
3. Choose 5–10 minutes (default 7), select **Start Focus**, and try pause, resume, and reset. New generation is disabled while focus is running or paused; reset unlocks it.
4. Complete early to stop the timer and see a positive message. In a separate session, let the timer finish and check **You did it! Every small step counts.**, then mark complete or retry.
5. Try blank input, a narrow browser window, and keyboard controls. Refresh clears all app state.

Gemini's recommended duration is advisory; change the timer selection yourself if desired. Only the selected duration drives the timer. No notifications or audio are sent. Thoughts are sent to Google for generation; the app does not save them. Provider processing follows Google's policies.

## Automated checks

```sh
source .venv/bin/activate
python -m pytest -q
node --test tests/timer.test.mjs
```

Node 22+ is used only for timer tests; it is not needed to run the app. API tests use explicit test doubles and never prove live Gemini access. Timer tests use an injected clock to check full sessions without waiting in real time.

Optional repeatable browser verification (requires local Google Chrome and a running app on 8017):

```sh
python -m pip install playwright==1.64.1
python tests/browser_check.py
```

The browser check intercepts all AI requests explicitly so it never spends API quota. It checks the UI, retries, validation/errors, loading, a full simulated focus session, early completion, safe text rendering, and 320/390/1280px layouts. Screenshots go to `/tmp/unstuck-desktop.png` and `/tmp/unstuck-mobile.png`. This is test-only tooling, not part of the application or live AI evidence.

## Submission

The MVP and final hands-on review are approved. Real Gemini generation was confirmed; intermittent upstream service availability remains a dependency limitation. The Devpost submission requires a short demo video and public GitHub repository. A local recording can show real generation, another step, focus starting, and early completion. Hosting is optional. Never publish `.env` or personal learner context.

## Planning and license

The required planning documents are [scope](devpost/scope.md), [PRD](devpost/prd.md), and [technical spec](devpost/spec.md). The build and verification record is in [the checklist](devpost/checklist.md). The application was created for Build With AI: Basics using the Devpost Learn Skill Pack and AI coding assistance. Runtime dependencies are listed in requirements.txt; the project uses no RUMI source.

MIT license; see [LICENSE](LICENSE). Third-party dependencies retain their own licenses. No Gemini API credentials are distributed.
