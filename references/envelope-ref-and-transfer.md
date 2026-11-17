# Multi-Reference, Mixed Media & Attribute/Motion Transfer (6-Field)

Use this reference whenever the user supplies multiple reference pictures, mixed timeline samples + references, reference video (`<Video N>`), video editing/continuation, or subject motion/attribute transfer.

Envelope: `subject_definitions:` -> `summary:` -> `retention_analysis:` -> `detailed_description:` (`Timeline:`) -> `overall_soundscape:` -> `non_diegetic_music:`

---

## 1. Media Identifiers & Namespace Rules
- **Existing IDs Only**: Refer only to `<Picture N>`, `<Video N>`, `<Audio N>` identifiers that actually exist in the user's attached inputs. Never renumber, restart numbering per subset, invent unsupplied IDs, or output upstream media-prefix headers.
- **No Range Shorthand**: List every Picture individually (`<Picture 1>, <Picture 2>, and <Picture 3>`), never `<Picture 1>-<Picture 3>` or `through`.
- **Independent Namespaces**: `<Picture N>`, `<Video N>`, and `<Audio N>` indices are independent; matching numbers do not imply shared origin. A `<Video N>` with audio does **not** create `<Audio N>` unless an audio input/track is actually attached/exposed.
- **Keep Meaning Stable**: Never change what a `<Subject N>`, `<Picture N>`, `<Video N>`, or `<Audio N>` represents across the 6 fields.
- **Where Citations Live**: Cite `<Picture N>` provenance in `subject_definitions:` (and standalone `<Picture N>` only if it holds a concrete frame/planning role) and track in `retention_analysis:`. Never cite `<Picture N>`/`<Video N>`/`<Audio N>` inside `summary:` unless explicitly requested.

---

## 2. Closed Task-Prefix Allowlist (`summary:`)
Begin `summary:` with `[tag]` or `[tag1 + tag2 + ...]` from **only** these 6 values (no duplicates, no invented tags):

| Tag | Activate ONLY When |
|---|---|
| `keyframe completion` | An attached `<Picture N>` is a concrete target first frame, keyframe, or last frame. |
| `reference generation` | Attached `<Picture N>`, `<Video N>`, or `<Audio N>` guides subject, scene, style, motion, or audio without being a concrete frame or direct edit/continuation. |
| `video editing` | An actual `<Video N>` is directly modified OR a subject/object/visual transfer replaces content onto `<Video N>`. (Place `video editing` **first** when combined.) |
| `video continuation` | New content continues, resumes, or extends an actual `<Video N>`. (Timeline Pictures alone never activate this.) |
| `audio reuse` | Full or partial `<Audio N>` signal is copied into the target track. |
| `audio reference` | Audible traits (vocal timbre, cadence, music style, texture) of `<Audio N>` are followed without copying audio. |

- When direct `<Video N>` editing applies, open the prose right after `[...]` with: `The target video is an edited version of <Video 1>.`

---

## 3. `retention_analysis:` Relationship Markers
One line per tracked `<Subject N>` or standalone media label, literal ` - ` separator, nonempty descriptor:
- **Visible (`<Subject N>`, `<Picture N>`, `<Video N>`)**:
  - `fully_preserved` — every defined trait and applicable role remains intact (never assume merely from input presence).
  - `partially_preserved` — some traits/roles are retained while others change, or only source motion/camera/scene progression remains (`use partially_preserved on <Video N> when source video motion/camera/setting stays visible`).
  - `attribute_transfer` — source identity/appearance (`<Picture N>`) or source motion/choreography/camera (`<Video N>`) is transferred onto a different target `<Subject N>`.
  - `weak_reference` — only broad style, category, composition, or mood remains.
- **Audio (`<Audio N>`)**:
  - `fully_copy` — complete signal copied as final track.
  - `partially_copy` — selected layers/segments copied or mixed.
  - `reference` — characteristics (timbre/delivery/style) followed without copying signal.
  - `weak_reference` — broad audible category/atmosphere only.
- **Prohibited Inside `retention_analysis:`**: Detailed choreography, event timelines, production methods, repeated definitions, or `(Sx)` speaker IDs (except `<Audio N>: reference - ... of <Subject N> (Sx) ...` in vocal-timbre transfer).

---

## 4. Mixed Timestamped Samples + Independent References
When the user supplies ordered timeline images (e.g., `Shot N at timestamp` or `M` leading timeline Pictures) plus later reference Pictures:
1. Partition strictly by the user's explicit timestamp/segment count—never guess partition from order alone.
2. Preserve supplied start timestamps literally (next start = previous end; final end = total duration). Do not replace them with equal slices.
3. Map later reference Pictures strictly by user instructions and visible evidence—never assume later Picture order maps 1-to-1 to subject order, and never assume replacement unless requested.
4. Keep timeline governing style global; treat a reference image's rendering style as local unless the user requests a global style override.

---

## 5. Video Attribute / Motion Transfer (3 Audio Modes)
Use when transferring identity/appearance from `<Picture N>` (`<Picture 1>`, or multiple `<Picture N>` for multi-subject replacement) onto a subject's motion, choreography, camera, and timing from `<Video 1>`:

- **Replacement & Retention Rules (All Modes)**:
  - Define each replaced `<Subject N>` statically using `<Picture N>` appearance + `<Video 1>` motion role. **Never** define, name, or describe replaced original `<Video 1>` subject(s) anywhere in `subject_definitions:`, `retention_analysis:`, or `Timeline:`, and never narrate an on-screen swap unless requested.
  - Define every **non-replaced** background/secondary person in `<Video 1>` as their own `<Subject N>` (`<Subject 2>`, ...) and attribute any dialogue they speak strictly to their own `<Subject N> (Sx)` tag (never to a replaced `<Subject 1>`).
  - Emit both retention lines cleanly: `<Subject N>: attribute_transfer - visual identity and appearance from <Picture N> transferred onto <Video 1> motion` and `<Video 1>: partially_preserved - camera movement, choreography, timing, and scene progression retained with subject replaced by <Subject N>` (or `<Video 1>: attribute_transfer` when only motion/camera transfers without source scene retention).
  - Do **not** invent `[SOUNDS]` not verifiably produced by a subject/action (`[SOUNDS]` is never for music or instruments). Never place theme-music or uncertain/nonsensical lyrics in `[SPEECH]` (`[SPEECH]` is only for an active `<Subject N>` speaking/singing; omit uncertain spans or mark `[unclear]` on verbatim copied audio).

| Audio Mode | `summary:` Prefix | `subject_definitions:` `<Audio 1>` | `retention_analysis:` `<Audio 1>` | `Timeline:` & `non_diegetic_music:` |
|---|---|---|---|---|
| **1. Audio Copy** | `[video editing + reference generation + audio reuse]` | `<Audio 1> is the full synchronized soundtrack copied from <Video 1>.` | `<Audio 1>: fully_copy - source audio track is copied entirely` (or `partially_copy` if selected segments/layers) | Emit `[MUSIC]: <Audio 1>`. Transcribe verbatim spoken/sung lyrics by active `<Subject N>` from `<Audio 1>` into `[SPEECH]` (omit uncertain lyrics; never emit theme-music lyrics). Start `non_diegetic_music:` with `<Audio 1>`. |
| **2. Audio Timbre** | `[video editing + reference generation + audio reference]` | `<Audio 1> is the vocal-timbre reference for <Subject 1> (S1).` | `<Audio 1>: reference - vocal timbre and delivery guide speech of <Subject 1> (S1) without copying audio signal` | `<Subject 1> (S1)` follows `<Audio 1>` voice traits without copying audio wording/signal. Target music described normally or `N/A`. |
| **3. No Audio** | `[video editing + reference generation]` | Omit `<Audio N>` completely. | Omit `<Audio N>` completely. | Omit `[SPEECH]` unless silent-video subjects are given new/non-replaced speaker lines; `non_diegetic_music: N/A`. |

---

## 6. Video Continuation (`video continuation`)
Use when new generated action continues, resumes, or extends directly from an actual attached `<Video N>`:
- **Activation**: Only an actual `<Video N>` activates `video continuation` (ordered timeline `<Picture N>` images alone never activate it).
- **Audio Pairing**:
  - Combine with `audio reuse` if source `<Audio N>` audio continues/copies directly.
  - Combine with `audio reference` if the continuation follows audible voice timbre, rhythm, or music characteristics without copying the raw source audio signal.
- **`subject_definitions:` & `retention_analysis:`**: Define recurring subjects retained from `<Video N>` (plus any new subjects/props introduced), define `<Video 1>` as the continuation source, and track `<Video 1>: partially_preserved` (or `fully_preserved` if complete continuity) and each `<Subject N>` cleanly.
- **`Timeline:`**: Open `[Shot 1]` at `00.00s` seamlessly matching `<Video 1>`'s ending pose, momentum, camera direction, lighting, and acoustic space before progressing forward.
