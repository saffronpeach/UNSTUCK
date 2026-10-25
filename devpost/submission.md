---
doc: submission-preparation
status: awaiting-publication-approval
---

# UNSTUCK — Final Submission Preparation

The original public MVP is at https://github.com/saffronpeach/UNSTUCK. Continuous progression and optional browser voice input are implemented locally. The learner manually tested and approved voice input. The combined update is prepared for publication review; it has not been pushed. No demo video or Devpost submission has been completed. Feature work is frozen.

## Publication Review

Target: **saffronpeach/UNSTUCK**, public, MIT license. Prepare a normal update on top of the clean public history; never push the original development history. The release contains 22 source/document/test files, including the new static/speech.js and tests/speech_browser_check.py. It excludes .env, credentials, the personal learner profile, local tooling, recordings, and development Git metadata.

Implemented release behaviors:
- Typed or optional dictated input, edited and explicitly submitted by the user.
- Real Gemini acknowledgment, concrete action, and suggested duration.
- Focus timer with start/pause/resume/reset and early/expired completion.
- Continue → Next Step with original task context, ordered completed actions in memory, and a completed-step count.
- Retry and Continue failures preserve the current recommendation and progress.
- Browser speech support/permission errors retain typing; browser-native speech processing may use an online service.

Verification: 46 API tests, 7 timer tests, workflow browser tests, and fake-engine speech browser tests. Live generation/continuation evidence and the learner’s manual microphone approval are separate from simulations. Audit the final release tree and all reachable public history before requesting publication approval. Record the exact candidate commit and archive hash in the local dist/ audit report. Do not push until the learner explicitly approves this final update.

## Required Submission Items

Official sources: [overview](https://learn-ai-basics.devpost.com/), [rules](https://learn-ai-basics.devpost.com/rules), [organizer updates](https://learn-ai-basics.devpost.com/updates).

- Public repository with source, setup instructions, an open-source license, and scope.md, prd.md, spec.md. Put its URL in the Devpost “Try it out” field.
- Working screen demo: aim for 1–3 minutes and remain under three minutes. Publish on YouTube or Vimeo and check logged-out access.
- Complete the actual form’s required project fields, Skill Pack explanation, age-of-majority confirmation, and exit survey yourself. The authenticated form is not available to this agent; exact prompts must be checked in your logged-in form.
- Deadline: October 26, 2026, 23:00 Europe/Helsinki (17:00 EDT). No deployment or peer review is required.
- No Devpost submission or video upload has been authorized. Publication approval covers only the reviewed GitHub update.

## Existing Human-Written Project Notes

Project name: **UNSTUCK**.

The following wording was supplied by the learner and is preserved verbatim:

> My project is UNSTUCK, an AI-powered web application that helps overwhelmed people turn their thoughts into one small, actionable next step.

> Target users: Students and people struggling with task initiation or overwhelm.

Use your own words for additions about progression, voice, learning, and the Skill Pack. The official 6-ship skill reserves public narration, submission answers, and personal reflections to the learner; spelling/grammar review is available. Do not invent a personal learning outcome.

## Demo Action Plan — About 2 Minutes 20 Seconds

This is an on-screen action plan; narration remains yours. Record the browser only, without the IDE, .env, terminal, personal notifications, or unrelated windows. Use a generic task, never sensitive personal input.

| Time | Show | Explain in your own words |
| --- | --- | --- |
| 0:00–0:15 | UNSTUCK title and task input. | Intended users and the difficulty beginning an overwhelming task. |
| 0:15–0:40 | Start microphone, dictate a short generic task, stop, and edit if needed. | Voice is optional; text remains editable and nothing submits automatically. |
| 0:40–1:00 | Explicitly submit and show a real Gemini recommendation. | One concrete action and a suggested duration. |
| 1:00–1:30 | Start Focus, pause, resume, then mark complete early. | Short focus controls and completion. |
| 1:30–2:00 | Show the count, select Continue → Next Step, and show the real follow-up action. | Continuity from the original task and completed actions without starting over. |
| 2:00–2:20 | Show the public repository README and planning docs. | How you used the Skill Pack and one thing you actually learned. |

Do not wait through a full focus session on camera. Do not fabricate AI output. If Gemini is overloaded, record later when a real request succeeds; disclose any edited waiting time. Stay under three minutes. Review the recording for private information before uploading it publicly, then verify the link without authentication.

## Remaining Checklist

- [x] Original public repository verified and MIT licensed.
- [x] Progression and voice implemented locally; documentation reflects both.
- [x] Voice manually tested and approved by the learner.
- [ ] Learner approves the final combined update and publication audit.
- [ ] Push only the clean reviewed update; verify public access, all files, and history.
- [ ] Record and publicly upload the demo; verify the link and record it in spec.md.
- [ ] Complete the actual Devpost fields and exit survey in the learner’s own words.
- [ ] Submit personally or explicitly authorize submission after final review.

GitHub URL: https://github.com/saffronpeach/UNSTUCK.
Demo URL: not recorded/uploaded yet.
Devpost: not started/submitted; no submission authorization.
