# Core Timeline, Audio, Shot & Grammar Contract

Apply these invariants across every MiniMax H3 prompt regardless of mode.

## 1. Formatting & Column-One Rules
- Write every top-level field name, `Timeline:`, timestamp range, and channel tag (`[VISUAL]:`, `[SPEECH]:`, `[SOUNDS]:`, `[MUSIC]:`) starting in **column one**.
- Never use markdown bullets (`-`, `*`), numbering prefixes, indentation, quotation marks, backticks, or code fences around field headers, definitions, or retention lines.
- Use `<Subject N> is a ...` for reference-aware definitions (or `<Subject N>: ...` in 5-field standalone); never output backtick syntax guides.
- Write all field labels and prose in English. Preserve original language **only** inside `<d>...</d>` dialogue/lyrics and inside double quotes for visible scene text.
- Output nothing outside the selected field envelope.

## 2. Adaptive Timestamps & Duration
- **Zero-padding & Precision**: Start at `00.00s` (default 2 decimals) or `00.000s` (3 decimals when requested or matching user-supplied millisecond timestamps). Zero-pad single-digit seconds (`02.50s`, `02.500s`). Keep precision uniform through the final endpoint.
- **Contiguous Coverage**: Format every block header as `[STARTs-ENDs]:` on its own line. Adjacent ranges must touch (`prev_end == next_start`) with zero gaps or overlaps. Final `END` equals the exact requested total duration.
- **Adaptive Boundaries**: Never force a fixed section count, equal intervals, or `Part N:` headings. Place boundaries only at meaningful changes in action, camera cut/shift, speech, sound peak, foreground priority, scene state, or media role. (If user provides explicit `Shot N at timestamp` starts, preserve those exact starts literally.)

## 3. Shots & Camera Motion
- **Opening & Cuts**: Put `[Shot 1]` immediately after `[VISUAL]:` in the first segment. Add sequential `[Shot 2]`, `[Shot 3]` **only** when an instantaneous hard camera cut or discontinuous scene/perspective jump occurs. On a single unbroken take, use only `[Shot 1]` at `00.00s` and omit `[Shot N]` from later segments.
- **Natural Transitions**: Prefer continuous camera motion over cuts for slight angle or distance changes. Use cross-dissolve, fade, or wipe only when explicitly needed.
- **Camera Motion & Framing Vocabulary**: Describe camera motion naturally inside `[VISUAL]`. Pair framing/angle geometry (`wide shot`, `close up`, `low angle`, `overhead`, `crane shot`, etc.) with standard motion types:
  - `Static Shot`: camera position and lens remain still.
  - `Zoom In` / `Zoom Out`: focal length changes while camera stays stationary.
  - `Push In` / `Pull Out`: camera body moves forward or backward.
  - `Pan Left` / `Pan Right`: camera stays fixed, pivots horizontally.
  - `Tilt Up` / `Tilt Down`: camera stays fixed, pivots vertically.
  - `Truck Left` / `Truck Right`: complete camera translates horizontally.
  - `Pedestal Up` / `Pedestal Down`: complete camera moves vertically.
  - `Tracking Shot`: camera moves alongside a moving subject.
  - `Dolly Shot`: camera moves toward, away from, or alongside subject for depth.
  - `Arc Shot`: camera moves in an arc around the subject.
  - `Shake Slightly` / `Shake Strongly`: slight or strong handheld/impact shake.
  - `Roll Clockwise` / `Roll Counterclockwise`: camera rolls around lens axis.
  - `POV`: camera presents a subject's first-person viewpoint (state whose viewpoint it is only when established by input or request; never assign first-person perspective to an external viewpoint).
- Add `slow` or `fast` only when speed materially affects the shot; omit normal speed.

## 4. Channels, Foreground Priority & Mixing
Each timestamp block follows this exact channel order:
1. `[VISUAL]:` (required): concrete visual action, subject positioning, start-to-end trajectories, environment reaction, lighting shifts, and camera movement. Never lapse into static frame description or repeat global style specs in every block.
2. `[SPEECH]:` (conditional): omit the entire line whenever no speech or character-sung vocal occurs in that block. Never write placeholders (`None`, `N/A`, `No speech`).
3. `[SOUNDS]:` (recommended whenever physical/ambient sound exists): non-musical physical sound effects, environmental ambience, and animal/creature/nonverbal human sounds.
4. `[MUSIC]:` (conditional): segment-specific diegetic or score cue. Omit when no music is specific to that segment. Always place after `[SOUNDS]`.

**Mixing Rules**:
- Assign one primary foreground event per block (intelligible dialogue, sung lyric phrase, major impact/action, or major musical transition). Keep competing channels subordinate and quieter.
- During `[SPEECH]`, keep visual action readable, limit loud impacts, and duck music. Place loud impacts, rapid action, and musical peaks before or after spoken lines. Do not overlap dialogue with foreground sung lyrics unless explicitly requested.
- **Music vs Sounds Boundary**: Never put music, beats, basslines, drums, or rhythm inside `[SOUNDS]`. In `[MUSIC]`, name `<Subject N>` only if that subject is actively playing the music.
- **Lyrics vs Dialogue Boundary**: Put vocals actually spoken or sung by an on-screen/off-screen subject or narrator into `[SPEECH]`. Never emit `[SPEECH]` for non-diegetic background song lyrics not sung by any subject, and never describe singing or speaking in `[VISUAL]` unless `[SPEECH]` is present in that block.

## 5. Speaker IDs & Speech Tags
- Syntax: `[SPEECH]: <Subject N> (Sx) <d>[Language] spoken words </d>` (or `applicable_voice_desc (Sx)` when speaker has no `<Subject N>` definition; use `<Audio N>` only when verbal content exists solely inside directly reused soundtrack/music without a defined `(Sx)` speaker).
- **Spoken-Aloud `<d>` Boundary**: Everything inside `<d>...</d>` is literally spoken aloud by the model in the speaker's voice. Place voice, emotion, action, or delivery descriptors **before** `<d>`, never inside `<d>...</d>`. Never write stage notes, parenthetical remarks, silence labels, or placeholders such as `(No dialogue, silent focus)`, `(silent)`, or `N/A` inside `<d>...</d>`; omit the entire `[SPEECH]` line when no speech occurs.
- Assign `(S1)`, `(S2)`, ... in actual vocal-event order; keep IDs stable across every shot. Never assign an ID to a non-speaking subject.
- **Multiple Simultaneous Speakers**: Use compound ID `(S1,S2)`.
- **Off-Screen Voiceover**: Write `<Subject N> (Sx) says in an off-screen voiceover <d>[Lang] ... </d>` and state immediately after `</d>` that the on-screen subject's lips remain closed (keep delivery/action outside `<d>`).
- **Speech Crossing a Cut**: Place `<scenetrans>` at both connecting points and explicitly state that audio continues across the cut.
- **Truncated Speech**: Append `<cutoff>` when speech is cut off by the end of the video.
- **Unintelligible Reused Audio**: Write `[unclear]` for unintelligible spans in verbatim reference-audio transcription.
- **Implicit Dialogue Requests**: If user asks to "add dialogue" without exact words, write concise, context-fitting lines at natural pauses (never force dialogue into every block). Preserve user-supplied wording verbatim.

## 6. Whole-Video Audio Fields
- `overall_soundscape:`: one continuous English paragraph (1–4 sentences) summarizing ambient, physical, and nonverbal sounds across the full clip. Do not repeat dialogue or lyrics.
- `non_diegetic_music:`: 1–3 English sentences describing audience-only background music (real instruments, tempo, rhythm, dynamic arc, not vague mood labels), or `N/A` when absent or complete silence is requested. Never introduce music absent from the Timeline. When the same `<Audio N>` genuinely supplies both physical sound and audience-only score, state the applicable relationship in both whole-video fields.

## 7. Grammar, Quotes & Direct-Language Bans
- **Summary Chronology**: If `summary:` mentions more than one temporally related occurrence, preserve their order and relationship exactly as in the Timeline; never reorder, duplicate, or retell timestamp-by-timestamp beats.
- **Fixed Subject Labels**: Emit `<Subject N>` as plain text with whitespace separation. Never attach `'s`, plural `s`, hyphens, or punctuation directly to `>` (write `the red coat worn by <Subject 1>`, never `<Subject 1>'s red coat`).
- **Zero Pronouns / Plurals in `summary:` & `[VISUAL]`**: Whenever `<Subject N>` tags are defined, repeat literal `<Subject N>` tags for every action, target, giver, receiver, and body part (`<Subject 1> hands the key to <Subject 2>`). Never use `he`, `she`, `him`, `her`, `his`, `their`, `theirs`, `they`, `them`, `both`, `Both` (even `both hands` -> `the left and right hands`), `the subjects`, `the couple`, or `the pair` inside `summary:` or `[VISUAL]`.
- **Double Quotes & Unwanted Overlays**: Use English double quotes `""` **only** around meaningful text visibly present in the scene (signs, neon, labels, subtitles), preserving original wording verbatim. Omit watermarks, signatures, logos, or overlaid graphics unless explicitly requested.
- **No Em/En Dashes or Ambiguous Hyphen Compounds**: Never use em-dashes (`—`) or en-dashes (`–`), and avoid hyphenated compound adjectives in visual/motion prose (keep established structural phrases like `off-screen` only where specified). Write direct, literal, visually renderable wording.
