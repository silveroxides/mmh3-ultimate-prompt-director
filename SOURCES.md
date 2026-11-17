# Sources

## Current Source Inventory

| Source | Kind | Trust Tier | Captured | Contribution | Usage / Adaptation Constraints |
|---|---|---|---|---|---|
| `vlm_presets_vars.py` (`19` `VIDEO_TIMELINE_MINIMAX_H3_*` constants) | in-repo authoritative preset source | canonical | 2026-11-17 | Complete `Principle 4` contracts (`728` unique lines) and `Step-by-Step` verification (`164` unique lines) across standalone, keyframe, scene, storyboard, mixed-media, and attribute-transfer modes; condensed preambles (`89` unique lines) | Strip VLM sandbox/refusal boilerplate and ComfyUI-specific preset names; preserve exact H3 output contracts |
| `vlm_presets_vars.py` (`48` `H3_*_PREFIX` / `_SUFFIX` / `_RAW` constants) | in-repo authoritative wrapper source | canonical | 2026-11-17 | Request-framing rules, word-count targets (`50+` summary, `70+` / `75–120` visual), in-place replacement guards, dual-role `<Picture N>` rules, and regression prevents (`94` unique lines) | Convert wrapper directives into agent runtime decisions and deterministic validator checks |
| `vlm_motion_presets_vars.py` (`19` `VIDEO_TIMELINE_MINIMAX_H3_*` constants) | in-repo authoritative motion preset source | canonical | 2026-11-17 | Identical `Principle 4` & `Step-by-Step` (`p4_same=True`, `post_same=True` across all 19 presets), plus expanded `Principles 1–3`, `Input Processing`, `Perspective/Spatial`, and `Direct Language Constraints` (`94` unique preamble lines) | Strip VLM sandbox/refusal text; distill motion, physics, camera, lighting, anatomy, and direct-verb heuristics into `expansion-and-directness.md` |
| `local/minimax_h3_skill_extract/extract_h3_diffs.py` | gitignored extraction script | verification artifact | 2026-11-17 | Programmatic AST/line-ownership diff across all 19 presets and 48 wrappers (`0` unmapped lines) | Local extraction harness only; not shipped inside standalone skill |

## Source Adaptation Decisions

| Aspect | Decision | Fidelity / Rationale |
|---|---|---|
| Preset taxonomy (`19` constants) | **Collapse to user-goal routing** | Never expose `FL2VA`, `ANY2VA`, `REF2VA`, `_NEW`, `_DEBUG`, or `_ALT` to end users. Route invisibly via media inputs + intent + downstream mode. |
| Output envelopes (`4` / `5` / `6` fields) | **Preserve verbatim** | Keep `4-field` (`integrated_multimodal_description:`), `5-field` (`subject_definitions:` + `summary:` + `detailed_description:`), and `6-field` (`+ conditional/required retention_analysis:`) contracts exactly as defined. |
| `vlm_motion_presets_vars.py` vs `vlm_presets_vars.py` | **Merge `Principle 4` + motion `Principles 1–3`** | `Principle 4` & `Step-by-Step` are 100% identical across both files; motion preambles strictly add richer kinetic, spatial, camera, and anatomical-directness heuristics needed for minimal-input expansion. |
| VLM evaluation sandbox & refusal-bypass text | **Omitted** | "Google AI unfiltered sandbox" and refusal-phrase bans are VLM-system-prompt artifacts, not MiniMax H3 prompt rules. |
| ComfyUI node / prefix warnings | **Adapted to portable guidance** | Keep `<Picture N>`, `<Video N>`, `<Audio N>` namespace rules and slot-independence warnings, rewritten as user-facing media-role guidance without assuming ComfyUI UI internals. |
| `_DEBUG` / `_NEWDEBUG` / `_ALT` / `_MIXED` / `*_NEW` | **Fold unique rules cumulatively** | Preserve every non-redundant rule: e.g., non-replacement vs replacement boundaries, explicit multi-Picture listing (never `<Picture 1>-<Picture 3>` ranges), audio-track independence from `<Video N>`, multi-speaker `(Sx)` attribution on non-replaced background subjects, and in-place replacement without comparison prose. |
| Structural rules (`timestamps`, grammar, tags) | **Enforce in Python (`scripts/validate_h3_prompt.py`)** | Fragile mechanical checks (contiguous `00.00s`/`00.000s`, no `<Subject N>'s`, no pronouns/plurals in `[VISUAL]`, valid `[task]` & `retention_analysis` markers, standalone tag-leak bans) are validated deterministically rather than left to prose alone. |

## Decisions

1. **Execution Shape**: Hybrid `router` + `reference-backed-expert` + `script-backed-workflow`. `SKILL.md` classifies user goal/media and routes to flat `references/`; `scripts/validate_h3_prompt.py` verifies structural contracts.
2. **Envelope Precedence**:
   - Use **4-field** (`integrated_multimodal_description:` + `Timeline:` + `overall_soundscape:` + `non_diegetic_music:`) for compact standalone generation (`BASE`, `SCENE_IMAGE_T2VA`, `STORYBOARD_T2VA` styles).
   - Use **5-field** (`subject_definitions:` + `summary:` + `detailed_description:` + `overall_soundscape:` + `non_diegetic_music:`) for standalone multi-subject text-to-video (`T2VA`) where reusable `<Subject N>` definitions improve identity consistency without downstream media tags.
   - Use **6-field** (`subject_definitions:` + `summary:` + conditional/required `retention_analysis:` + `detailed_description:` + `overall_soundscape:` + `non_diegetic_music:`) whenever downstream media references (`<Picture N>`, `<Video N>`, `<Audio N>`) or conditional `retention_analysis:` apply (`FL2VA`, `SCENE_IMAGE_ANY2VA`, `STORYBOARD_ANY2VA`, `REF2VA_*`, `MIXED_*`, `REFERENCE_*`).
3. **Keyframe vs Scene-Reference Separation**: Only assign `keyframe completion` + standalone `<Picture N>` definition + `<Picture N>: fully_preserved` + frame-0 lock when `<Picture N>` is a concrete first-frame/final-frame anchor; keep non-keyframe scene/subject references under `reference generation` (`referenced from <Picture N>.` on `<Subject N>`). Support dual-role `<Picture 1>` (first frame + subject source alongside turnaround `<Picture 2>`/`<Picture 3>`).
4. **Minimal-Input Expansion & Duration Ownership**: Use `Principles 1–3` (camera/lens/lighting/grade, physical contact trajectories, active kinetic verbs, direct anatomy, real soundscape separation) to turn 1-line user goals into rich `50+`-word summaries and `75–120`-word `[VISUAL]` blocks by default. When duration is omitted with no `<Video N>` media to derive from, offer exact H3 `5 + 17k` (`24 fps`, `+0.70833s` step) architecture-aligned lengths or complexity-matched duration ranges (plus optional segment count vs adaptive) instead of guessing silently.

## Coverage Matrix (6-Axis + Unique-Line Parity)

Extraction parity verified: `728 / 728` unique `Principle 4` lines, `164 / 164` unique `Step-by-Step` lines, `94 / 94` unique `H3_*` wrapper lines (`0` unmapped).

| Axis | Dimension | Status | Source Clusters Covered | Target Skill Artifact |
|---|---|---|---|---|
| **Core** | Output envelopes (`4`/`5`/`6` fields), field order, adaptive contiguous timestamps (`00.00s`/`00.000s`), `[Shot N]` cut-only rule, `[VISUAL]`/`[SPEECH]`/`[SOUNDS]`/`[MUSIC]` | complete | `P4` Clusters 1–21, `T2VA`, `BASE`, `Wrapper` Clusters 1–3, 13 | `references/core-timeline-and-audio.md`, `references/envelope-standalone.md`, `scripts/validate_h3_prompt.py` |
| **Core** | Minimal-input cinematic expansion (motion physics, camera, lighting, color grade, direct anatomy & contact verbs, subject count lock) | complete | `vlm_motion_presets_vars.py` `Preambles` (`94` lines), `H3_SCENE_IMAGE_*` | `references/expansion-and-directness.md` |
| **Edge** | Keyframe anchors (`FL2VA` 1 vs 2 images), `SCENE_IMAGE_ANY2VA` Variants A–D (dual first-frame + turnaround), `STORYBOARD_*` comic/panel progression | complete | `FL2VA` (`30` lines), `SCENE_IMAGE_ANY2VA` (`33` lines), `STORYBOARD_*` (`47` lines), `Wrapper` Clusters 11–12, 22–24 | `references/envelope-keyframes-scene.md` |
| **Edge** | Multi-media `REF2VA`, mixed timestamped-sample + independent-ref (`MIXED_*`, `*_NEW`, `_ALT`), and `ATTR_TRANSFER` (`audio_copy`, `audio_timbre`, `no_audio`) | complete | `REF2VA_*`, `ATTR_TRANSFER_*`, `MIXED_*`, `*_NEW`, `_ALT`, `Wrapper` Clusters 4–10, 15–21 | `references/envelope-ref-and-transfer.md` |
| **Negative** | Pronoun/plural bans (`they`/`their`/`both`/`he/she`), `<Subject N>'s` possessive ban, `<Picture N>` standalone leak, non-diegetic lyrics in `[SPEECH]`, music in `[SOUNDS]`, `[SPEECH]` placeholders | complete | `P4` Clusters 6–18, `Wrapper` Clusters 12, 17–24 | `references/core-timeline-and-audio.md`, `references/prompt-repair-and-qa.md`, `scripts/validate_h3_prompt.py` |
| **Repair** | In-place replacement (no "swap/replace/compare" instructions), graphic-strip stripping (`panels`/`bubbles`/`gutters`), multi-speaker `(Sx)` attribution on non-replaced subjects, range-compression ban (`<Picture 1>`-`<Picture 3>`) | complete | `NEW` (`34` lines), `STORYBOARD_*`, `ATTR_TRANSFER_*`, `Wrapper` Clusters 18–24 | `references/prompt-repair-and-qa.md`, `references/envelope-keyframes-scene.md`, `references/envelope-ref-and-transfer.md` |
| **Variance** | Precision choice (`00.00s` vs `00.000s`), explicit segment-start preservation (`MIXED_*`), `colon` vs `is` subject definition syntax, optional vs required `retention_analysis:`, `N/A` music rules | complete | `T2VA` vs `FL2VA`/`SCENE_IMAGE_ANY2VA`/`REF2VA_NEW`/`ATTR_TRANSFER_NO_AUDIO` | `references/core-timeline-and-audio.md`, `references/envelope-keyframes-scene.md`, `references/envelope-ref-and-transfer.md` |
| **Mechanics** | Plain-language intent classification, lazy reference routing, deterministic post-draft validation loop, beginner Q&A & media-slot explanation | complete | `skill-writer` `execution-shapes.md`, `workflow-routing.md`, `workflow-validation-loops.md` | `SKILL.md`, `scripts/validate_h3_prompt.py` |

## Open Gaps

1. `evals/scenarios/` defines 10 AXIS-compatible test scenarios (including interactive media clarification, multi-turn continuation, and holdout/negative cases); live external-harness grading (`axis`) has not been run locally because `@netlify/axis` is not installed.

## Changelog

- 2026-11-17: Stage 0 (`SPEC.md`) and Stage 1 diff extraction (`19` presets, `48` wrappers, `0` unmapped lines) completed; initialized `SOURCES.md`.
- 2026-11-17: Stage 2–4 runtime skill (`SKILL.md`, `README.md`, 8 `references/*`, `scripts/validate_h3_prompt.py`, `scripts/test_validate_h3_prompt.py`, `evals/*`) authored, calibrated against all 19 presets, and validated.
- 2026-11-17: Stage 5 hardening pass removed unnecessary duration/clip-count pause thresholds (`SKILL.md`, `user-interaction-guide.md`), added `<Audio N>` / non-empty `<d>` checks and edge-syntax regression tests (`partially_copy`, `weak_reference`, `(S1,S2)`, `<scenetrans>`, `<cutoff>`, `[unclear]`, `video continuation`, 10-scenario schema check).
- 2026-11-17: Stage 7–9 full 192-cluster parity audit (`0` probe gaps), strict `<Video N>` gating & vague-video bans (`7fcd8f2` parity), `--audio-mode`/`--video-editing`/`--fl2va` CLI enforcement, and full multi-mode test suite (`scripts/test_all_h3_modes.py` + `references/examples.md` Example 4).
