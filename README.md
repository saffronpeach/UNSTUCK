# UNSTUCK

**One step at a time.** A small, local web application that uses Gemini to identify a priority from your stated constraints, recommend one concrete action, help you focus, and offer a logical next step after completion. Type your thoughts or use optional browser voice input.

Built with FastAPI, plain HTML/CSS/JavaScript, and server-side Google Gemini. No accounts, database, persistent task history, or persistent browser storage. Completed actions stay in memory only for the current task, enabling Continue → Next Step.

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

1. Type an overwhelming task, or use the microphone and stop dictation, then select **Help me get unstuck**. Expect “Your priority right now,” a short evidence-based explanation, a supportive acknowledgment, one action, and a suggested duration.
2. Select **Try another step**. It should offer a different action for the original input, even if you edit the text field without resubmitting.
3. Choose 5–10 minutes (default 7), select **Start Focus**, and try pause, resume, and reset. New generation is disabled while focus is running or paused; reset unlocks it.
4. Complete early to stop the timer and see a positive message. In a separate session, let the timer finish and check **You did it! Every small step counts.**, then mark complete or retry.
5. After completing an action, select **Continue → Next Step**. The next action uses your original input, prior priority, and completed steps. Gemini reassesses when completed work finishes a task or unblocks another; one small completion does not automatically finish the whole task. Complete more actions to increase the progress count. Retry preserves that progress; a failed next-step request keeps your state and lets you try Continue again. A successful new main-form submission starts a fresh task.
6. Try blank input, a narrow browser window, and keyboard controls. Refresh clears all app state.

Gemini's recommended duration is advisory; change the timer selection yourself if desired. Only the selected duration drives the timer. UNSTUCK does not send notifications or upload audio to its backend. On explicit generation, retry, or Continue requests, task text and relevant completed actions are sent to Gemini; the app keeps them only in the current browser session. Optional voice input may use the browser’s own speech service. Provider processing follows the respective providers’ policies.

## Lightweight prioritization

Mention deadlines, urgency, importance, and prerequisites in your input when you know them. UNSTUCK selects one current priority and one manageable action, not a ranked task list. Its priority label and evidence must come from the original text. The server builds the explanation from the quoted evidence; it rejects unsupported priority claims and common explicit negations such as “not urgent.” If ranking information is missing, it uses a neutral manageable-start explanation rather than assuming urgency or inventing a deadline. Relative deadlines remain as stated, without an assumed calendar date.

Continue and retry carry the previous priority plus completed actions in browser memory. Priorities can change when that progress warrants it; failed requests preserve the previous priority and progress. AI selection still needs your judgment, especially with ambiguous or competing constraints. Submit revised input to start a fresh task context.

## Voice input

Select **Use microphone** beside the task input, allow microphone access, and speak. The button changes to **Stop dictation** and a visible listening message appears. Click again to stop, edit the recognized text if needed, and explicitly select **Help me get unstuck** to submit. Final recognized phrases append to your current text without replacing manual edits; nothing is submitted automatically.

Voice input uses browser-native SpeechRecognition or webkitSpeechRecognition, with the browser language and an en-US fallback. Support and microphone permissions depend on the browser; unsupported browsers keep manual typing available. No transcription API key, audio upload endpoint, or new backend service is added. Your browser may use its own online speech service; recognition is not guaranteed to be offline. [Web Speech API reference](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition).

If permission is denied, allow microphone access in the browser's site settings and try again. Device, network, language, or no-speech errors preserve your text. Starting focus stops dictation; generation controls are disabled until dictation stops. Use the local app on http://127.0.0.1:8017 for manual testing.

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
python tests/speech_browser_check.py
python tests/priority_browser_check.py
```

The workflow browser check intercepts all AI requests explicitly so it never spends API quota. It checks three-step progression, ordered original-task context, retry and Continue failures, progress reset, validation/loading, a full simulated focus session, early/late completion, safe text rendering, and 320/390/1280px layouts. Screenshots go to `/tmp/unstuck-desktop.png` and `/tmp/unstuck-mobile.png`. This is test-only tooling, not part of the application or live AI evidence.

## Submission

The MVP and final hands-on review are approved. Real Gemini generation was confirmed; intermittent upstream service availability remains a dependency limitation. The Devpost submission requires a short demo video and public GitHub repository. A local recording can show optional dictation, real generation, focus starting, completion, and Continue returning the next action. Hosting is optional. Never publish `.env` or personal learner context.

## Planning and license

The required planning documents are [scope](devpost/scope.md), [PRD](devpost/prd.md), and [technical spec](devpost/spec.md). The build and verification record is in [the checklist](devpost/checklist.md). The application was created for Build With AI: Basics using the Devpost Learn Skill Pack and AI coding assistance. Runtime dependencies are listed in requirements.txt.

MIT license; see [LICENSE](LICENSE). Third-party dependencies retain their own licenses. No Gemini API credentials are distributed.

The speech regression uses a simulated recognition engine to verify start/stop, editable text, no auto-submit, language fallback, permission/service failures, cancellation, input length, and timer/progression compatibility. The microphone feature has also been manually tested and approved; support and recognition accuracy can still vary by browser and language.

The priority browser regression verifies visible priority/reason, continuation and retry context, reassessment rendering, failure preservation, new-task reset, and safe text rendering with simulated responses. Separate live Gemini checks verified a stated essay deadline, essay continuation, and neutral handling when ranking information was missing. The learner manually tested and approved all three prioritization scenarios. The combined update awaits publication approval.
