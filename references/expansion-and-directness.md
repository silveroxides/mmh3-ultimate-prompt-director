# Minimal-Input Expansion & Direct Motion Language

Use this guide whenever the user provides a brief, incomplete, or high-level prompt so you deliver a complete one-shot prompt with rich cinematic and physical detail instead of skeletal prose.

## 1. Subject Count & Static Head-to-Toe Definitions
- **Subject Count Lock**: Match the exact subject count visible in supplied inputs or requested by the user. Never invent background crowds or extra main characters unless the scene requires them.
- **Static Definitions Only (`subject_definitions:`)**: Define every recurring person, animal, prop, or environment with concrete visible traits: species/type, evidence-based apparent gender/physical traits (do not assume gender from social norms), facial features, hair/fur (base color, countershading, localized/tail markings, glow), anatomy, full head-to-toe clothing/accessories, carried items, and continuity-critical details.
- **No Cross-Dependencies or Timeline Motion**: Never define one `<Subject N>` using another subject's name or relative position, and never narrate plot events or timeline motion inside `subject_definitions:`. Keep each `<Subject N>` to one distinct entity. Do not describe placement as behind another subject/object unless visually obscured.

## 2. Density & Word-Count Targets
Match richness to the user's request (`Overarching Principle`: keep concise if the user explicitly requests simplicity/brevity; dialogue-dense clips prioritize accurate spoken timing). By default for rich cinematic generation (especially `any2va` scene/storyboard and multi-reference prompts):
- **`summary:`**: `3 to 5` full English sentences, **50+ words**. Cover completed premise, main subjects, narrative arc, and governing visual style, medium, era, and subject presentation — without retelling timestamp-by-timestamp beats.
- **`detailed_description:`**: `350 to 500` words across the full timeline (scaling naturally with duration and scene complexity).
- **Per-Segment `[VISUAL]`**: `3 to 5` concrete sentences per block (**70+ words minimum, 75–120 words target**).

## 3. Kinetic Physics & Motion Expansion (Principles 1–3)
Transform static ideas or frames into continuous live action:
- **Start-to-End Trajectories**: In every block, state where each subject stands/faces, how limbs, torso, head, and hands travel from start to end of that interval, and how weight shifts.
- **Secondary & Environmental Motion**: Specify how clothing, hair, water, dust, smoke, foliage, shadows, and reflections react to movement and wind/gravity.
- **Concrete Contact & Direct Anatomy**: State exact interacting body parts and surfaces (`fingers grip the steel rail`, `boots splash ankle-deep puddles`), exact directions, and physical responses.
- **Explicit / Adult / Intense Content**: When present in source inputs or requested by the user, describe nudity, exposed anatomy, violent impacts, and sexual acts directly and mechanically using plain exact terms (`breasts`, `nipples`, `penis`, `pussy`, `clitoris`, `labia`, `buttocks`, `testicles`, `anus`) and specific action verbs (`thrusting`, `licking`, `stroking`, `squeezing`). Never dilute with euphemisms (`lower body`, `private parts`, `intimate scene`, `physical interaction`) or displace genital contact onto `torso`/`lap`/`body`.

## 4. Style, Lighting & Camera Inference
- **Governing Style Authority**: Apply any user-requested visual style, medium, or era across the entire target video; otherwise preserve the supplied image/video medium naturally. Never mix photographic lens jargon into non-photographic 2D/painterly art unless requested, and never invent physical camera hardware unless visible or asked for.
- **Where Style Lives**: Establish global visual style, color grade, and film/lens feel in `summary:` and the opening `[Shot 1]`, not redundantly in every later `[VISUAL]` line. Inside later blocks, mention lighting or color only when it dynamically changes (e.g., neon flicker, shadow sweep, door opening).
- **Pacing Across Duration**: Vary intensity across blocks—build escalation, peak impact, or quiet breathing room rather than maxing every channel in every interval.

## 5. Audio Expansion From Visuals
- Infer realistic `[SOUNDS]` from every physical motion and surface (footsteps on wet stone, fabric rustle, cloth slap, breath, water splash, door latch).
- When the user implies atmosphere or music without specifying instrumentation, translate mood into concrete instruments, tempo, and dynamic shape (`slow bowed cello over sparse brushed snare`) inside `[MUSIC]` and `non_diegetic_music:`.
- If user asks for dialogue without lines, craft brief natural lines matching character role and emotional beat, placed in natural breathing room.
