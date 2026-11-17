# minimax-h3-prompting Specification

## Intent

Enable any AI agent to produce accurate, one-shot MiniMax H3 video-audio prompts and answer MiniMax H3 prompting questions for users with zero prior knowledge of MiniMax H3 syntax, presets, or workflows. From minimal user input (plain goal plus optional media descriptions or files), the skill infers sound defaults, resolves media roles, structures adaptive timelines and audio channels, and validates the finished prompt deterministically.

## Scope

In scope:
- Prompt generation, expansion from minimal user briefs, prompt repair/rewriting, and workflow/prompting Q&A grounded exclusively in the MiniMax H3 presets and query wrappers from `vlm_presets_vars.py` and `vlm_motion_presets_vars.py` (anchored in Principle 4 and supplemented by Principles 1–3 and `H3_*` wrappers).
- All MiniMax H3 prompt shapes: standalone text-to-video (`4-field` and `5-field`), single scene image or storyboard seeds (standalone or reference-aware), first/last keyframe bridges, multi-picture character/scene/style references (including dual first-frame + turnaround roles), video reference / motion & attribute transfer (audio copy, vocal timbre, or no audio), and video continuation/editing.
- Cross-runtime portable execution (`SKILL.md`, flat `references/`, and Python `scripts/`).

Out of scope:
- Exposing internal preset names, VLM sandbox directives, or preset-selection menus to end users.
- Non-MiniMax-H3 VLM presets or `minimax_h3_vlm_presets_vars.py` templates outside the stated source pair.
- Calling external generation APIs, rendering video, or running ComfyUI workflows directly.
- Provider-locked mechanics (Claude-Code-only hooks, `context: fork`, `$ARGUMENTS` assumptions, or mandatory subagent spawning).

## Users And Trigger Context

- Primary users: Zero-knowledge users or practitioners wanting ready-to-paste MiniMax H3 prompts or answers from minimal descriptions, media assets, or broken prompt drafts.
- Common user requests:
  - Plain-English video ideas with duration or minimal detail ("make an 8s rain chase prompt for MiniMax H3").
  - Image/storyboard/video/audio-backed goals ("use picture 1 as first frame and picture 2 for the character", "keep the dance motion from this video but swap the person").
  - Broken prompt cleanup or H3 questions ("fix my MiniMax H3 timeline", "how do I format dialogue and music in MiniMax H3?").
- Should not trigger for:
  - Static image prompt enhancement (e.g. MOSS-Image), unrelated video models, or general code editing in a host repository.

## Runtime Contract

- Required first actions:
  1. Classify user request along four plain axes: user goal (create, expand, repair, Q&A), available media (none, scene image, storyboard, first/last keyframes, character/scene refs, video, audio), downstream delivery (standalone text vs media-attached H3), and audio/dialogue intent.
  2. Read `references/core-timeline-and-audio.md` plus only the matching envelope/mode reference(s) (and `references/expansion-and-directness.md` when user input is minimal).
- Required outputs:
  - Ready-to-use MiniMax H3 prompt in the exact required top-level field envelope (`4-field`, `5-field`, or `6-field`), plus plain-language media-slot mapping only when media inputs are involved, or clear direct answers for Q&A requests.
- Non-negotiable constraints:
  - Never leak internal preset identifiers, VLM meta-instructions, or forbidden syntax (`<Picture N>` in standalone prompts, `<Subject N>'s` possessives, pronouns/group plurals replacing defined subjects, `[SPEECH]` placeholders, non-contiguous timestamps, or `Part N:` headers).
  - Never impose arbitrary restrictions or ask unnecessary questions when creative details can be inferred; when duration/segment scale is omitted and no `<Video N>` is supplied, ask once offering exact H3 `5 + 17k` (`24 fps`) lengths or complexity-matched duration ranges (plus optional segment count vs adaptive).
- Expected bundled files loaded at runtime:
  - Always: `SKILL.md` (and `references/core-timeline-and-audio.md` for prompt tasks).
  - Conditionally: 1 matching envelope reference + `references/expansion-and-directness.md` (minimal input) + `references/prompt-repair-and-qa.md` (repair/Q&A) + `scripts/validate_h3_prompt.py` (deterministic verification).

## Source And Evidence Model

Authoritative sources:
- `vlm_presets_vars.py`: `19` `VIDEO_TIMELINE_MINIMAX_H3_*` presets (`Principle 4`, condensed preambles, `Step-by-Step`) and `48` `H3_*` query wrappers (`_PREFIX`, `_SUFFIX`, `_RAW`).
- `vlm_motion_presets_vars.py`: `19` `VIDEO_TIMELINE_MINIMAX_H3_*` presets (expanded cinematic motion `Principles 1–3`, `Input Processing`, `Perspective/Spatial`, `Direct Language Constraints`, plus identical `Principle 4` & `Step-by-Step`).

Useful improvement sources:
- Positive examples: compliant outputs spanning all envelopes and Variants A–D.
- Negative examples: regression patterns guarded by presets and wrapper suffixes (e.g. comic-bubble leakage, `[SPEECH]` on non-diegetic lyrics, keyframe vs non-keyframe scene-ref confusion, pronoun/possessive regressions).
- Validation results: `scripts/validate_h3_prompt.py` and `scripts/test_validate_h3_prompt.py`.

Data that must not be stored:
- Secrets, private local paths, or unadapted raw VLM sandbox/refusal boilerplate.

## Reference Architecture

- `SKILL.md` contains: plain-language intent classifier, envelope/mode routing table, flat `references/` open-when index, execution & validation workflow.
- `references/` contains: flat focused domain modules (`user-interaction-guide.md`, `core-timeline-and-audio.md`, `expansion-and-directness.md`, `envelope-standalone.md`, `envelope-keyframes-scene.md`, `envelope-ref-and-transfer.md`, `prompt-repair-and-qa.md`, `examples.md`).
- `scripts/` contains: deterministic prompt validator (`validate_h3_prompt.py`) and its pytest suite (`test_validate_h3_prompt.py`).
- `evals/` contains: `axis.config.json` and zero-knowledge user test scenarios.

## Validation

- Lightweight validation: `python quick_validate.py <skill-root>` (`skill-writer` structural/frontmatter/reference check).
- Deeper validation: `pytest scripts/test_validate_h3_prompt.py` + extraction-coverage parity check + scenario evals across all H3 modes.
- Acceptance gates: zero `quick_validate.py` errors, 100% unit tests passing, 100% extracted unique Principle 4 / wrapper rules accounted for in `SOURCES.md` coverage matrix, and clean cross-repo portability for standalone GitHub publication.

## Known Limitations

- The skill validates prompt structure, syntax, timeline math, tag grammar, and mode-boundary rules deterministically; subjective creative quality still relies on adherence to the distilled Principles 1–4 guidance.

## Maintenance Notes

- When to update `SKILL.md`: routing table, workflow steps, validator CLI flags, or bundled `references/` index changes.
- When to update `SOURCES.md`: upstream `vlm_presets_vars.py` / `vlm_motion_presets_vars.py` preset diffs change or new regressions are captured.
- When to update `evals/`: new H3 failure modes or edge variants appear.
