---
name: mmh3-ultimate-prompt-director
description: Create, expand, repair, or explain MiniMax H3 video-audio prompts from minimal user goals and optional images, storyboards, video, or audio. Use when a user asks to write a MiniMax H3 video prompt, turn an idea or media into an H3 timeline, fix an H3 prompt, or asks how MiniMax H3 prompting, dialogue, sound, keyframes, or reference roles work. Do not use for static image generation or unrelated video models.
metadata:
  version: 0.1.2
---

# MMH3 Ultimate Prompt Director

Generate accurate, one-shot MiniMax H3 video-audio prompts or answer MiniMax H3 prompting questions for users with zero prior MiniMax H3 syntax knowledge. Never expose internal preset jargon or raw meta-instructions; translate plain user intent into the exact required H3 structure and validate deterministically.

## Reference Index (Open Only What the Request Needs)

| Open when you need to... | Read |
|---|---|
| handle vague requests, clarification questions, media wiring notes, or multi-turn edits | `references/user-interaction-guide.md` |
| apply universal timestamps, `[Shot N]`, channels, `(Sx) <d>`, mixing, quotes, and grammar | `references/core-timeline-and-audio.md` |
| expand a brief/vague user goal into rich motion, camera, lighting, physics, and audio | `references/expansion-and-directness.md` |
| write a text-only standalone prompt (from text, image seed, or storyboard without attaching media to H3) | `references/envelope-standalone.md` |
| use first/last frame anchors, scene images + subject refs (Variants A–D), or storyboards with downstream media | `references/envelope-keyframes-scene.md` |
| use multi-picture references, mixed timeline samples, `<Video N>`, continuation, or motion/attribute transfer | `references/envelope-ref-and-transfer.md` |
| fix/audit a broken prompt or answer beginner questions about slots, dialogue, cuts, or motion | `references/prompt-repair-and-qa.md` |
| inspect validator-verified examples across standalone, dual-role keyframes, attribute transfer, and repairs | `references/examples.md` |

## Stage 1: Classify Intent & Handle Ambiguity

1. **Identify Task**: `create/expand prompt` | `refine previous prompt` | `repair existing prompt` | `Q&A / workflow help`.
2. **Identify Supplied Media**: `none` | `single scene image` | `storyboard/comic` | `1–2 boundary keyframes` | `multiple subject/scene refs` | `mixed timeline images + refs` | `video` | `audio`.
3. **Resolve Duration & Segment Structure** *(in chat without workflow nodes, the agent owns both)*:
   - **Duration & Segment Count Supplied**: Lock user-specified duration, timestamp precision (`00.00s` or `00.000s`), and any explicit segment count or `Shot N at timestamp` starts literally without asking.
   - **Video Media Supplied (`<Video N>`)**: Derive duration and pacing from `<Video N>`; ask only if audio/retention roles are ambiguous.
   - **Duration Supplied Without Segment Count**: Lock the requested duration verbatim and compute segment count adaptively from meaningful action, camera, speech, or sound changes (never fixed intervals).
   - **Duration (and Segment Count) Omitted With No `<Video N>`**: Ask the user once before drafting, offering **both** exact H3 architecture-matched lengths (`5 + 17k` frames at `24 fps`, `+0.70833s` step: e.g., `5.17s` / `124f`, `5.88s` / `141f`, `6.58s` / `158f`, `7.29s` / `175f`, `8.00s` / `192f`, `10.13s` / `243f`; run `python scripts/validate_h3_prompt.py --list-h3-lengths` if needed) **and** complexity-matched duration ranges tailored to the request, plus optional segment count (defaulting to adaptive beats). Combine with any media-role ambiguity in the same concise question.
4. **Decide Delivery Mode**:
   - **Standalone text-only** (H3 receives text only): route to `references/envelope-standalone.md` (`4-field` or `5-field`).
   - **Media-attached / General `any2va` / Transfer / Continuation**: route to `references/envelope-keyframes-scene.md` or `references/envelope-ref-and-transfer.md` (`6-field`).
5. **Infer vs Clarify (`references/user-interaction-guide.md`)**:
   - Infer creative details (camera, lighting, soundscape, music, dialogue lines when asked without script) and proceed **one-shot** whenever structural roles are clear; never ask unnecessary questions or impose arbitrary restrictions.
   - Ask concise, jargon-free questions **only** when unresolvable structural ambiguity would wire the wrong mode (e.g., multiple unlabeled images with diverging roles, or unclear copy vs timbre vs silent audio on `<Video N>`).

## Stage 2: Load Matching References

- **Prompt creation / expansion / multi-turn refinement**: Read `references/core-timeline-and-audio.md` + the single matching envelope file + `references/expansion-and-directness.md` (when brief) + `references/user-interaction-guide.md` (when clarifying ambiguous media, resolving duration/segments, wiring media, or refining across turns).
- **Prompt repair or Q&A**: Read `references/prompt-repair-and-qa.md` (+ `references/core-timeline-and-audio.md` if rewriting).

## Stage 3: Draft, Validate & Auto-Repair Loop

1. Draft the complete MiniMax H3 prompt directly in the target envelope with column-one labels and contiguous zero-padded timestamps.
2. Run the bundled validator relative to this skill's directory (never hardcode user home paths):

```bash
python scripts/validate_h3_prompt.py --mode <auto|standalone_4|standalone_5|reference_6> [--duration <sec>] [--precision <2|3>] [--expected-segments <n>] [--expected-starts <00.00,03.20>] [--storyboard] [--audio-mode <copy|timbre|none>] [--video-editing] [--fl2va]
```

Pass `--require-retention`, `--forbid-retention`, `--require-keyframe-tag`, `--forbid-keyframe-tag`, `--audio-mode`, `--video-editing`, `--fl2va`, or `--strict-word-counts` when the routed scenario requires them (or run `--list-h3-lengths` to display exact `5+17k` durations). Read stdout JSON, fix every `errors` item (and review `warnings`), and repeat until `"valid": true` before replying.

## Stage 4: Deliver With Plain-English Guidance

- **Prompt requests**: Output the clean, ready-to-paste prompt in a single block (zero internal preset names or meta-prose).
  - If you inferred defaults (e.g., duration or style), add a 1-line note below the prompt so the user knows what to tweak.
  - If media inputs are used, add a short **Media Wiring** checklist below the prompt mapping `<Picture N>`, `<Video N>`, and `<Audio N>` in plain English (or remind standalone users not to attach seed images).
- **Q&A requests**: Give a direct, jargon-free answer grounded in the matching reference.
- **Fallback if Python unavailable**: Manually audit field order, timestamp contiguity (`prev_end == next_start`), `[Shot 1]` start, channel order (`[VISUAL]` -> `[SPEECH]` -> `[SOUNDS]` -> `[MUSIC]`), `<Subject N>` spacing, zero pronouns in `summary:` and `[VISUAL]`, strict `<Video N>` gating (no `guide`/`mimicking` prose), full `<Subject N>` on first appearance, and standalone media-tag isolation.
