# Keyframes, Scene Images & Storyboards (Reference-Aware 6-Field)

Use this reference when the user supplies first/last frame anchors, a scene image (with or without extra subject/audio references), or a storyboard/comic sequence.

All modes below use the **6-field envelope**:
`subject_definitions:` -> `summary:` -> `retention_analysis:` (when reference media tags are active) -> `detailed_description:` (`Timeline:`) -> `overall_soundscape:` -> `non_diegetic_music:`

---

## 1. First-Frame & Last-Frame Keyframe Bridges (1 or 2 Anchors)
Use when `<Picture 1>` locks frame `00.00s` and optional `<Picture 2>` locks the exact final frame at total duration.
- **Definitions**: Define recurring `<Subject N>` entities statically, plus `<Picture 1> is the fixed first frame anchor at 00.00s.` and (only if 2nd image exists) `<Picture 2> is the fixed final frame anchor at video endpoint.` Never invent `<Picture 2>` when only 1 image exists.
- **`summary:`**: Begin with `[keyframe completion]`. State the subjects, the progression from `<Picture 1>` to `<Picture 2>` (or forward from `<Picture 1>`), and governing visual style.
- **`retention_analysis:`**: Emit `<Picture 1>: fully_preserved - first frame anchor at 00.00s` (plus `<Picture 2>: fully_preserved - final frame anchor at video endpoint` when present), and track `<Subject N>: fully_preserved` or `partially_preserved` as applicable.
- **`Timeline:`**:
  - Segment 1 (`[Shot 1]` at `00.00s`) begins directly from the exact composition and pose of `<Picture 1>`, then develops immediate physical motion.
  - Final segment directs subject motion, spatial relationships, and camera movement smoothly into the exact composition and pose of `<Picture 2>` (when present) without abrupt snaps.
  - Do not exhaustively re-describe static fine pixel details already locked by the anchor frames; focus prose on motion, physics, camera travel, and audio.

---

## 2. Single Scene Image + Optional Subject/Audio References
Route carefully by how the user treats the supplied images/audio:

### Critical Distinction: Keyframe Anchor vs Scene/Subject Reference
- **Keyframe Reference (`keyframe completion`)**: `<Picture N>` is explicitly assigned as a concrete first frame, final frame, or keyframe locking exact frame-0/endpoint pose and framing -> emit `[keyframe completion + ...]` in `summary:`, standalone `<Picture N> is ...` in `subject_definitions:`, `<Picture N>: fully_preserved - ...` in `retention_analysis:`, and start `[Shot 1]` directly from `<Picture 1>` at `00.00s`.
- **Non-Keyframe Scene Reference (`reference generation` only)**: `<Picture N>` is a non-keyframe scene reference without a fixed boundary guiding setting, lighting, or subject appearance without locking frame 0 -> keep `[reference generation]` (do **not** add `keyframe completion` or `<Picture 1>: fully_preserved`), leave camera framing flexible, and cite `, referenced from <Picture N>.` on the `<Subject N>` line.

### Scene-Image Intent Variants
- **Default (single unannotated image, no downstream tags requested)**: Treat as visual seed only. Omit `retention_analysis:` and omit `<Picture N>` tags; begin `summary:` with `[reference generation]`, describe opening `[Shot 1]` from that visual state, and extrapolate dynamic action forward.
- **Variant A (Full Soundtrack Copy)**: Add `+ audio reuse` to `summary:`, define `<Audio 1> is the full synchronized soundtrack...`, add `<Audio 1>: fully_copy - source audio track is copied entirely`, emit `[MUSIC]: <Audio 1>`, transcribe any audible lyrics/dialogue into `[SPEECH]`, and open `non_diegetic_music:` with `<Audio 1>`.
- **Variant B (Vocal Timbre Reference)**: Add `+ audio reference` to `summary:`, define `<Audio 1> is the vocal-timbre reference for <Subject N> (Sx)...`, add `<Audio 1>: reference - vocal timbre and delivery guide speech without copying audio signal`. Never copy raw source wording/audio.
- **Variant C (Subject Visual Reference, 1 or multiple turnaround images)**: Append `, referenced from <Picture N>.` (or `, referenced from <Picture A> and <Picture B>.`) on the `<Subject N>` line. Track on `<Subject N>: partially_preserved - ...` (or `fully_preserved`); omit standalone `<Picture N>` lines unless also assigned a frame role.
- **Variant D (Dual First-Frame Anchor + Multi-Picture Subject Refs)**: When `<Picture 1>` is the fixed first frame **and** also supplies `<Subject N>` alongside turnaround images (`<Picture 2>`, `<Picture 3>`):
  - Define `<Subject 1> is ..., referenced from <Picture 1> and <Picture 2>.` (and `<Subject 2>` with `<Picture 1> and <Picture 3>` as applicable) **and** `<Picture 1> is the fixed first frame anchor at 00.00s.`
  - `summary:` starts with `[keyframe completion + reference generation]` (+ audio tag if present).
  - `retention_analysis:` emits **both** `<Picture 1>: fully_preserved - fixed first frame anchor at 00.00s` **and** `<Subject N>: partially_preserved - ... from <Picture 1> and <Picture 2> retained across new motion`.
  - `[Shot 1]` starts directly from `<Picture 1>` at `00.00s`.

### In-Place Character Replacement (Scene Image / Storyboard)
When the user wants to replace a character seen in a scene image or storyboard (and MiniMax H3 is not editing a source `<Video N>`):
- Never write replacement/swap instructions or mention the replaced character.
- Use the image/storyboard only for pose, composition, camera, and action; define `<Subject N>` exclusively from the replacement identity (citing `, referenced from <Picture N>.` only if `<Picture N>` is attached downstream) and depict that character across all fields as always occupying the scene.

---

## 3. Storyboard / Comic Sheet / Story Guide Video (VLM-Only Progression)
- **Strict `<Video N>` Gating & Zero Vague/Meta Guide Mentions**: Only when a video is provided AND the user explicitly requests `<Video 1>` (or `<Video N>`) downstream is the prompt allowed to use that strict `<Video N>` tag. Otherwise MiniMax H3 sees **zero** guide media—never write vague or meta references (`the guide`, `in the guide`, `from the guide`, `shown in the guide`, `mimicking`, `source video`, `guide video`, `original video`, `reference video`, `pre-existing video`, `story guide`, `input video`, `the footage`, `the clip`) anywhere in `subject_definitions:`, `summary:`, `retention_analysis:`, or `Timeline:`. Write directly as a firsthand scene.
- **Self-Contained Subject Anchors**: Describe every `<Subject N>` in full head-to-toe detail in `subject_definitions:` and anchor each `<Subject N>` completely upon first introduction in `Timeline:` so MiniMax H3 has complete self-contained visual anchors across every beat.
- **Zero Graphic-Strip Leakage**: Never write `storyboard`, `panels`, `comic strip`, `stitched images`, `progression images`, `speech bubbles`, `borders`, `gutters`, `halftone`, or `sfx lettering`.
- **Chronological Cinematic Flow**: Group ordered panels or progression frames into cohesive multi-second movement phrases (never uniform single-frame micro-slices; `70+` words `[VISUAL]`). Keep one unbroken `[Shot 1]` if the progression is a single continuous camera take without cuts.
- **Channel Extraction**: Transcribe bubble dialogue or sung character vocals into `[SPEECH]`; never place non-diegetic song lyrics into `[SPEECH]`. Translate panel actions/onomatopoeia into realistic `[SOUNDS]` (no music/drums in `[SOUNDS]`).
- Apply Variants A–C and Conditional User-Instructed References identically to Section 2 (`[reference generation]` default, omit `retention_analysis:` unless downstream media tags are assigned).
