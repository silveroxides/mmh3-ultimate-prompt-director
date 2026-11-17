# Prompt Repair Checklist & Beginner Q&A Guide

Use this reference when auditing/fixing an existing prompt or answering a user's MiniMax H3 workflow/prompting question.

---

## 1. Repair Checklist (Fixing Broken Prompts)
Run `scripts/validate_h3_prompt.py` first to locate exact structural/grammar errors, then fix any semantic issues below:

| Failure Mode | Symptom | Fix |
|---|---|---|
| **Wrong envelope** | `retention_analysis:` or `[reference generation]` in text-only prompt; or `integrated_multimodal_description:` when `<Subject N>`/`<Picture N>` definitions are needed | Switch to `5-field` (standalone with `<Subject N>`) or `6-field` (downstream media attached). |
| **Media tag leak** | `<Picture 1>` appears in standalone prompt or inside `summary:` | Remove all media tags in standalone mode; move `<Picture N>` provenance out of `summary:` into `subject_definitions:`/`retention_analysis:`. |
| **False keyframe lock** | `keyframe completion` or `<Picture 1>: fully_preserved` used for a general character/scene style reference | Use `reference generation` and cite `, referenced from <Picture 1>.` on `<Subject 1>` unless `<Picture 1>` actually locks frame `0`. |
| **Timestamp math break** | Gap/overlap (`02.50s` -> `03.00s`), unpadded `2.50s`, mixed `00.00s`/`00.000s`, or `Part 1:` headers | Zero-pad (`02.50s`), touch adjacent endpoints (`02.50s` -> `02.50s`), match decimal precision, remove `Part N:`. |
| **Over-cut `[Shot N]`** | `[Shot 2]`, `[Shot 3]` placed on every timestamp block during a continuous camera move | Remove `[Shot N]` from continuous-camera blocks; use `[Shot N]` only on hard cuts/scene jumps. |
| **Subject grammar errors** | `<Subject 1>'s hand`, `he`/`they`/`both` in `[VISUAL]`, or `both hands` | Replace with `the hand of <Subject 1>`, repeat literal `<Subject 1>`/`<Subject 2>`, write `the left and right hands`. |
| **Speech/Lyrics/Music mixup** | `[SPEECH]: None`, background song lyrics in `[SPEECH]`, drums/beats in `[SOUNDS]`, or `[MUSIC]` before `[SOUNDS]` | Delete silent `[SPEECH]` lines; keep background lyrics out of `[SPEECH]`; move music/beats to `[MUSIC]` after `[SOUNDS]`. |
| **Replacement prose leak** | "Replace the woman in Video 1 with <Subject 1>" or defining the old replaced character | Delete superseded identity everywhere; describe one completed video with `<Subject 1>` already in place. |
| **Graphic-strip leak** | Mentions `storyboard`, `panels`, `comic strip`, `speech bubbles`, `gutters`, `borders` | Rewrite as live camera shots, transcribing bubble words into `[SPEECH]` and action/SFX into `[SOUNDS]`. |
| **Dashes & placeholders** | Contains `—`, `–`, hyphenated adjectives, `{...}`, or vague `physical interaction` | Replace dashes/hyphens with clean spaced prose; replace placeholders with exact mechanical actions and body parts. |

---

## 2. Zero-Knowledge Beginner Q&A Reference
Answer user questions in plain, practical language without internal preset jargon:

- **"Should I attach my image to MiniMax H3 or just use text?"**
  - *Pure inspiration / no strict pixel lock needed*: Keep MiniMax H3 text-only (standalone prompt) and describe every detail in full prose so the prompt carries 100% of the visual spec.
  - *Exact character face/outfit or exact opening/ending frame needed*: Attach the image(s) downstream and use a reference-aware prompt (`<Picture 1>`, `<Picture 2>`, ...) specifying which image locks frame 0 / final frame vs which image only supplies character appearance.
- **"Can one image be both my opening frame AND a character reference alongside turnaround sheets?"**
  - Yes. Assign `<Picture 1>` as the fixed first frame at `00.00s` **and** cite `<Picture 1>` plus turnaround `<Picture 2>`/`<Picture 3>` in `<Subject N>` (`referenced from <Picture 1> and <Picture 2>.`), with `[keyframe completion + reference generation]` and standalone `<Picture 1>: fully_preserved`.
- **"What's the difference between copying video audio vs voice-timbre reference?"**
  - *Audio copy (`audio reuse`)* keeps the original audio track verbatim (dialogue, ambient, music).
  - *Voice timbre (`audio reference`)* uses the audio clip only to match a speaker's pitch, tone, and delivery for **new** spoken lines without copying original audio.
- **"Why did my character stop moving or look robotic?"**
  - Prompts with short static descriptions or cuts on every beat break continuity. Keep `3–5` motion-focused sentences per `[VISUAL]` block (`75–120` words), track limbs and camera continuously, and omit `[Shot N]` unless cutting.
- **"How do I handle voiceovers or dialogue crossing a cut?"**
  - For voiceover: write `<Subject 1> (S1) says in an off-screen voiceover <d>[English] ... </d>` and state right after `</d>` that the on-screen character's lips remain closed.
  - Across a cut: place `<scenetrans>` at both connecting points and state that the audio continues across the cut.
