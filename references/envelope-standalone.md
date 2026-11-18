# Standalone Prompts (Text-Only Delivery to MiniMax H3)

Use this reference when MiniMax H3 receives **only the prompt text**, either from a pure text request or when supplied images/storyboards/clips are visual inspiration/seeds used solely while drafting the prompt (never attached to MiniMax H3 downstream).

## 1. Choose the Standalone Envelope

| User Case | Envelope | Fields (Exact Order) |
|---|---|---|
| Pure text goal with recurring multi-subject consistency needed | **5-Field Standalone** | `subject_definitions:` -> `summary:` -> `detailed_description:` (`Timeline:`) -> `overall_soundscape:` -> `non_diegetic_music:` |
| Direct compact text, single scene-image seed, or storyboard-to-text guide (no downstream media) | **4-Field Standalone** | `integrated_multimodal_description:` (`Timeline:`) -> `overall_soundscape:` -> `non_diegetic_music:` |

*(Note: 5-Field Standalone also works whenever explicit static `<Subject N>` definitions clarify multiple characters; omit `retention_analysis:` and omit `[task]` brackets in both standalone envelopes.)*

## 2. Hard Standalone Boundary
- **Zero Media Identifiers or Video Mentions**: Never emit `<Picture N>`, `<Video N>`, `<Audio N>`, `retention_analysis:`, `[reference generation]`, `[keyframe completion]`, or phrases referencing unseen media (`"the supplied image"`, `"first frame image"`, `"the storyboard"`, `source video`, `guide video`, `original video`, `reference video`, `input video`, `story guide`, `the guide`, `in the guide`, `shown in the guide`, `mimicking`).
- **Full Subject Descriptions**: Describe every visual fact (head-to-toe traits, setting, spatial layout, camera angle, lighting, colors) in `subject_definitions:` (5-field) and describe each subject in full on first appearance in `Timeline:` so MiniMax H3 needs no image or video access.

## 3. Single Scene Image as Text-Only Seed
- Treat the image strictly as the opening visual state at `00.00s` (`[Shot 1]`).
- Open `[Shot 1]` with `1–2` concise sentences establishing the governing visual style/medium if using 4-field format, then `3–5` rich sentences (`70+` words minimum) depicting the opening scene and immediate forward physical motion.
- Never mention a camera cut unless the requested story deliberately cuts later.

## 4. Storyboard / Comic Strip / Sequential Guide as Text-Only Prompt
- **Strict Graphic-Strip Stripping**: Never write `storyboard`, `storyboard sequence`, `storyboard video`, `panels`, `comic strip`, `stitched images`, `speech bubbles`, `speech balloons`, `panel borders`, `gutters`, `text boxes`, `speed lines`, or `sound effect lettering`.
- **Continuous Cinematic Translation**: Convert ordered panels or stitched frames into real live-action/cinematic continuous motion across `[00.00s-...]`. Use `[Shot 1]` at `00.00s` and introduce `[Shot N]` only on genuine angle/scene cuts.
- **Mandatory Multi-Channel Extraction**: Never collapse progression segments into visual-only blocks when audio cues exist:
  - `[SPEECH]`: Transcribe speech-bubble text, narration, or sung character vocals verbatim into `[SPEECH]: <Subject N> (Sx) <d>[Language] ... </d>` (mapping each line to the speaking subject, e.g. `<Subject 2> (S1)`; use `voice_desc (Sx)` only if the speaker has no `<Subject N>` alias).
  - `[SOUNDS]`: Translate physical panel actions and comic SFX lettering into realistic physical/ambient sound descriptions (never quote comic onomatopoeia verbatim unless it is a real spoken word or visible sign).
  - `[MUSIC]`: Translate emotional/musical cues into concrete instrumentation and tempo.

## 5. In-Place Character Replacement (Standalone Mode)
When the user supplies a scene image or storyboard **and** asks to replace a character while generating standalone text (no video/image passed to H3):
- **Never write replacement/editing/transfer instructions** ("replace X with Y", "originally A now B").
- Extract **only** setting, composition, framing, pose, limb placement, spatial layout, lighting, and timeline progression from the seed/storyboard.
- Define and depict the replacement character in-place from the user's description or replacement image across `subject_definitions:` (if 5-field), `summary:`, and every `[VISUAL]` / `[SPEECH]` line as if that character was always the sole subject in that role.
- Never name, retain, or describe the replaced subject's face, hair, species, anatomy, clothing, or accessories.
