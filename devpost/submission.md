---
doc: submission-preparation
status: draft
---

# UNSTUCK — Submission Preparation

5-build is complete by the learner's explicit final approval. 6-ship is in progress. Nothing has been published, uploaded, or submitted.

## Verified Requirements

Checked against the official [overview](https://learn-ai-basics.devpost.com/), [rules](https://learn-ai-basics.devpost.com/rules), and [organizer updates](https://learn-ai-basics.devpost.com/updates).

- Submit a new working project built with the Devpost Learn Skill Pack; include scope.md, prd.md, and spec.md in its public repository.
- Provide the public repository URL. The rules also call for an open-source license; a proposed MIT LICENSE is prepared locally for publication approval.
- Record a working screen demo. Target 1–3 minutes per the overview and stay under three minutes per the rules. Upload to publicly visible YouTube or Vimeo and verify logged-out access.
- Complete the project name, description, other required submission fields, and exit survey. Organizer updates specifically identify a required Skill Pack explanation and age-of-majority checkbox; place the public repository link in “Try it out.”
- Deadline: October 26, 2026, 23:00 Europe/Helsinki (17:00 EDT).
- Deployment and peer feedback are optional and are not planned.

The authenticated submission form was not accessible from this session. Exact remaining field prompts and the exit survey must be checked in the learner's logged-in form, not invented here. The learner must confirm their own eligibility; no age or personal survey answer is inferred.

## Project Name and Existing Human-Written Description

Project name, already chosen by the learner: **UNSTUCK**.

The following is copied verbatim from the learner's original message; it is not newly drafted submission prose:

> My project is UNSTUCK, an AI-powered web application that helps overwhelmed people turn their thoughts into one small, actionable next step.

Additional human-supplied source notes, preserved without rewriting:

> Target users: Students and people struggling with task initiation or overwhelm.

> Core workflow: User describes what is overwhelming them → AI identifies one small, concrete next action → user starts a 5–10 minute focus timer → user marks the action complete or retries.

The learner chooses what to paste and writes any additional description, personal learning reflection, Skill Pack explanation, and exit-survey responses. The official 6-ship skill reserves public narration and submission writing to the learner; spelling and grammar review is available. These notes are not marked as a completed submission form.

## Demo Run of Show — Approximately 2 Minutes

This is a technical action script, not authored narration. Explain each beat in your own words. Record only the browser, without the IDE, .env tab, terminal, personal notifications, or unrelated windows. Use a generic example rather than sensitive personal input.

| Time | On-screen action | What to explain in your own words |
| --- | --- | --- |
| 0:00–0:15 | Show the clean UNSTUCK page and tagline. | Who you built it for and the difficulty starting an overwhelming task. |
| 0:15–0:45 | Type a generic overwhelmed-student example, click Help me get unstuck, and wait for a real Gemini result. | The text becomes one concrete next action, with a short acknowledgment and suggested duration. |
| 0:45–1:05 | Briefly show the recommendation and select a 5–10 minute focus duration. | The difference between the suggested duration and the user's chosen timer. |
| 1:05–1:35 | Start Focus, pause, resume, reset, and start again. | The browser-only focus controls. |
| 1:35–1:50 | Mark the action complete early. | The completion state and the end of the core loop. |
| 1:50–2:10 | Show the planning docs and run instructions in the prepared public repository or safe source-file view. | How you used the Skill Pack and one thing you actually learned. |

You do not need to wait five minutes on camera. The early-completion path shows the complete loop; timer expiry was checked separately. Another AI request is not necessary in the recording. If you choose to demonstrate retry, leave room under three minutes. Do not fabricate a live response or provoke failures just for the video. If Gemini is overloaded, retry later and record a successful real run. Disclose any edited waiting time instead of implying generation was instant.

Upload the finished recording yourself after reviewing it for private content. Verify that a logged-out viewer can play it. No face camera, hosting deployment, music, or extra feature is needed.

## Repository Preparation

Proposed public repository name: **UNSTUCK**. Owner: **saffronpeach**. Target: **https://github.com/saffronpeach/UNSTUCK** (not created or published by this agent). Proposed license: MIT. GitHub repository creation, visibility changes, and upload/push all require explicit approval; code and included history become publicly readable.

README setup instructions now use a portable project path, and all three planning documents are present. Runtime configuration uses an ignored .env; .env.example has a blank key. The original local Git history remains intact.

A read-only audit of all four existing development commits and 32 unique blobs found no credential patterns, the current local Gemini key, .env files, learner profile, or unrelated curriculum source. It did identify a personal absolute home path in historical README versions and a local-machine email in commit metadata. Current README paths are portable. Do not publish the original history without discussing those metadata findings.

Prepare the public source from the clean snapshot archive in dist/UNSTUCK-public.zip. It contains the intended current source, tests, technical documentation, planning artifacts, and license, without .git, credentials, personal learner profile, or local tooling. A new repository created from that snapshot gets a fresh GitHub-authored history and leaves the local development repository untouched. This is an export, not a rewrite of local history. Publication of the snapshot still requires explicit approval.

## Remaining Actions

- [x] MVP and hands-on review approved; brief build wrap-up recorded in checklist.md.
- [x] Automated checks: 37 API tests and 7 timer tests pass; browser regression passed during final build verification.
- [x] Portable README, planning documents, blank .env.example, and proposed MIT license prepared locally.
- [x] Development history audited; credential and learner-profile checks pass. Personal path/author metadata findings are documented above.
- [x] Learner specifies GitHub owner saffronpeach and repository name UNSTUCK.
- [ ] Learner explicitly approves the public repository, MIT license, and clean-snapshot publication; approval has not been given.
- [ ] Public GitHub URL created and verified without authentication; add it to spec.md and the Devpost “Try it out” field.
- [ ] Learner records, reviews, and publicly uploads the demo to YouTube/Vimeo; verify access and add URL to spec.md.
- [ ] Learner completes submission text, Skill Pack explanation, age eligibility confirmation, and required exit survey using the actual form.
- [ ] Learner explicitly authorizes final submission, or submits personally and confirms completion.

GitHub target: https://github.com/saffronpeach/UNSTUCK — pending explicit publication approval; public availability not confirmed.
Demo URL: not recorded yet, confirmed by learner.
Devpost form: not started yet, confirmed by learner.
Devpost submission URL/status: pending; not submitted.

## Final Publication Review

Publish only the audited clean source snapshot, not the development Git history or the local project directory wholesale. Target owner/name: saffronpeach/UNSTUCK. Visibility: public. License: MIT. Root contents: FastAPI source, static frontend, tests, requirements, portable README, LICENSE, blank .env.example, .gitignore, and devpost planning/build/shipping documents. No app hosting or Devpost submission is included in this authorization request.

Final content checks cover all archive entries for the actual local key and credential patterns, excluded private files, home-directory paths, and required source/planning/license files. No remote repository creation, visibility change, push, or upload has occurred.
