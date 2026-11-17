# User Interaction, Clarification & Multi-Turn Refinement

Use this guide to handle zero-knowledge user requests smoothly: resolving duration and segment structure when no upstream node supplies them, delivering one-shot results whenever intent is clear, asking plain-English questions only when structural choices diverge, explaining media wiring, and supporting multi-turn edits.

## 0. Duration & Segment Count Ownership (Outside Node Workflows)
In automated node workflows, total duration and optional segment timestamps are handed in upfront. With a zero-knowledge user in chat, **you** must resolve both cleanly without inventing arbitrary constraints:
- **When Duration & Segment Count Are Supplied**: Use them verbatim (`00.00s` or `00.000s`; preserve exact segment count and `Shot N at timestamp` starts literally).
- **When `<Video N>` Media Is Supplied**: Derive duration and visual pacing directly from `<Video N>` (ask only if audio/retention roles are unclear).
- **When Duration Is Supplied Without Segment Count**: Use that duration verbatim and compute segment count adaptively from real changes in action, camera, speech, sound, or foreground priority (never fixed equal slices). Note in 1 line below the prompt that they can specify an exact segment count or `Shot N at timestamp` starts if needed.
- **When Duration (and Segment Count) Is Omitted With No `<Video N>`**: Ask the user once before drafting, offering:
  1. **Exact H3 Architecture Lengths (`24 fps`, `5 + 17k` frames, `+17f ≈ +0.70833s` per step)** (e.g.):
     - `73f = 3.042s` (`3.04s`) · `90f = 3.750s` (`3.75s`) · `107f = 4.458s` (`4.46s`)
     - `124f = 5.167s` (`5.17s`, H3 single-chunk default) · `141f = 5.875s` (`5.88s`) · `158f = 6.583s` (`6.58s`)
     - `175f = 7.292s` (`7.29s`) · `192f = 8.000s` (`8.00s`) · `209f = 8.708s` (`8.71s`)
     - `226f = 9.417s` (`9.42s`) · `243f = 10.125s` (`10.13s`) · `294f = 12.250s` (`12.25s`) · `362f = 15.083s` (`15.08s`)
     *(Run `python scripts/validate_h3_prompt.py --list-h3-lengths` for full values; use `00.000s` precision when aligning to exact fractional H3 lengths like `5.167s`.)*
  2. **Complexity-Matched Range Options** tailored to their prompt's story beats (e.g., short single-beat `~5.17s–6.58s`, medium multi-beat `~7.29s–10.13s`, extended arc `~10.83s–15.08s+`).
  3. **Optional Segment Count / Timestamps**: Ask if they want a specific segment count or timestamps, or adaptive beat-based segments by default.

## 1. One-Shot Inference vs Clarification Decision Matrix

Never interrogate a user over creative details you can infer well, and never impose arbitrary caps or thresholds. Ask only when duration/segment scale is unspecified without `<Video N>` or when an unresolved structural choice would produce the wrong mode or media wiring.

| User Input Situation | Action | Plain-English Handling |
|---|---|---|
| Brief text idea with **no duration**, no segment count, and no `<Video N>` (*"cat knocks over coffee mug"*) | **Ask once for length/range (+ segments)** | Present 2–3 complexity-matched duration ranges **plus** exact H3 `5 + 17k` (`24 fps`) length options, and note adaptive beat-based segments as default unless they want a specific segment count. Infer style, camera, and soundscape automatically once they pick length. |
| User supplies duration (`"6s"`, `"8.000s"`, `"124 frames"`) without segment count | **Proceed one-shot (adaptive segments)** | Use exact duration (snapping frame count only if user asks for H3-aligned seconds). Divide into adaptive beat-based segments at real action/camera/speech/sound shifts, never fixed intervals. |
| User supplies explicit segment count or `Shot N at timestamp` starts (with duration) | **Preserve literally** | Keep the user's exact segment count and start timestamps literally (`prev_end == next_start`; final `END` = total duration). |
| User requests any explicit duration for one prompt, or asks for chained clips | **Honor user scope directly** | Generate a single timeline at the exact requested duration without inventing duration caps; use `video continuation` when the user asks for chained clips or continuing from a prior `<Video N>`. |
| User says *"add dialogue"* without providing lines | **Infer & deliver one-shot** | Write concise, context-fitting lines placed at natural pauses; keep `(Sx) <d>[Lang] ... </d>` syntax clean. |
| Single unannotated image + plain goal (duration given, *"8s, make this character walk into a cafe"*) | **Infer & deliver one-shot** | Default to visual-seed generation (`[reference generation]`, no `retention_analysis:`), and mention in 1 line below the prompt that they can ask to lock frame 0 if desired. *(If duration is also missing, ask length + frame-0 vs visual-seed in one combined question.)* |
| Multiple unlabeled images (*"here are 3 images, make an H3 video"*) | **Ask 1 concise plain question** | Combine missing duration (exact H3 lengths / complexity ranges) and role clarity in plain words (no preset jargon): e.g., *"How long should the clip be (e.g., exact H3 `5.17s` / `6.58s` / `8.00s`, or a short/medium range)? Also, should Image 1 lock the exact starting frame or serve as a character/scene reference?"* |
| User supplies `<Video N>` (or video + audio) without saying what to keep | **Ask targeted audio/retention question** | Ask plainly: *"Should the new video keep the original audio track verbatim, match only the speaker's voice tone for new lines, or have no audio? And should we keep the original background or replace only the main subject?"* |
| User supplies conflicting instructions (e.g., *"completely silent"* + *"background pop music"*) | **Surface conflict briefly** | Note the conflict in 1 sentence and ask which should win before locking `non_diegetic_music:`. |

## 2. Plain-English Media-Slot Onboarding (Post-Prompt Output)
Whenever the generated prompt uses `<Picture N>`, `<Video N>`, or `<Audio N>` tags, append a short **Media Wiring** block right below the prompt (outside the prompt text) so beginners know exactly what to attach and in what order:

```markdown
Media Wiring:
- Picture 1 -> Fixed opening frame + visual appearance for Subject 1
- Picture 2 -> Extra turnaround/appearance reference for Subject 1
- Audio 1 -> Voice tone reference only (audio signal is not copied)
```

If the user asked for a **standalone text-only prompt** derived from a seed image or storyboard, explicitly state below the prompt: *"Do not attach the seed image/storyboard to MiniMax H3; paste the prompt text alone."*

## 3. Multi-Turn Refinement & Follow-Up Edits
When the user iterates on an already-generated prompt:
1. **Timing / Duration Change** (*"make it 10s instead"*, *"stretch the reveal"*): Re-proportion affected timestamp segments while keeping `[00.00s-...]` contiguous through the new endpoint; never leave gaps or drop precision.
2. **Audio / Dialogue / Music Edit** (*"remove dialogue"*, *"switch to upbeat jazz"*, *"add a voiceover"*): Delete `[SPEECH]` completely if removed (never leave placeholders), update `(Sx)` numbering in actual vocal order if speakers shift, and keep `[MUSIC]` + `non_diegetic_music:` synchronized.
3. **Style Override** (*"make it 2D anime instead"*): Update governing style in `summary:` (or `[Shot 1]` for 4-field) while preserving subject identity and physical continuity.
4. **Standalone <-> Reference Conversion** (*"now I want to attach Image 1 as the starting frame"*): Upgrade envelope cleanly (`4/5-field` -> `6-field` with `subject_definitions:`, `[keyframe completion]`/`[reference generation]`, `retention_analysis:`, and `<Picture 1>` anchoring), or strip all media tags and `retention_analysis:` when converting to text-only.
5. **Continue Into Next Clip** (*"write the next 6s clip continuing right after this one"*): Either draft a fresh standalone/first-frame continuation starting from the final state of clip 1, or, when continuing from `<Video 1>`, switch to `video continuation` in `envelope-ref-and-transfer.md`.
6. **Always Re-Validate**: Run `scripts/validate_h3_prompt.py` after every follow-up edit before replying.
