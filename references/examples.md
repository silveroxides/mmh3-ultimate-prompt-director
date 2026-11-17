# Worked Examples (Happy Path, Complex Variants & Repair)

Every example below satisfies `scripts/validate_h3_prompt.py`.

---

## Example 1: Minimal User Input -> Complete 4-Field Standalone Prompt
**User Goal**: *"6s cyberpunk rain chase, add a line of dialogue"* (no media).

```text
integrated_multimodal_description:
Timeline:
[00.00s-03.20s]:
[VISUAL]: [Shot 1] Wide tracking shot glides forward down a rain slick neon alley in gritty live action cinema as a courier in a soaked dark coat sprints over wet asphalt, spraying ankle deep puddles beneath warm storefront light while cyan reflections streak across dark concrete and steam vents curl upward past corrugated shutters.
[SPEECH]: (S1) <d>[English] Keep moving, they sealed the lower gate! </d>
[SOUNDS]: Rapid wet footsteps splashing across puddles, distant thunder rumble, and steady rainfall hiss.
[MUSIC]: Low pulsing analog synthesizer bassline swells quietly beneath the rain.
[03.20s-06.00s]:
[VISUAL]: [Shot 2] Close cut to the courier planting one boot onto a rusted steel barrier and vaulting upward as rain streaks tight across the frame, overhead neon tubes buzzing and snapping sparks into damp air while the coat hem whips backward over wet brick walls.
[SOUNDS]: Sharp metallic clang of boots on steel, strained exhaled breath, and sizzling electric crackle.
overall_soundscape:
Steady heavy rainfall, rapid splashing footsteps, metallic barrier impacts, electrical crackle, and distant thunder fill the alley.
non_diegetic_music:
A pulsing analog synthesizer bassline drives the opening sprint quietly under speech before cutting out for the final barrier vault.
```

---

## Example 2: Dual First-Frame Anchor + Multi-Picture Character Refs + Vocal Timbre (6-Field)
**User Goal**: *"Use Picture 1 as the starting frame of a 5s train departure, Picture 1 and Picture 2 for the woman's look, and Audio 1 just for her voice tone when she speaks."*

```text
subject_definitions:
<Subject 1> is a tall woman with braided black hair, sharp dark eyes, and a long cobalt wool coat over dark boots, referenced from <Picture 1> and <Picture 2>.
<Picture 1> is the fixed first frame anchor at 00.00s.
<Audio 1> is the vocal timbre and delivery reference for <Subject 1> (S1).
summary:
[keyframe completion + reference generation + audio reference] The completed video opens directly from the misty station platform and tracks a composed departure beside idling carriages. <Subject 1> turns toward the sliding train doors and speaks calmly before stepping forward across wet stone under cool overhead station lamps in crisp live action cinema style.
retention_analysis:
<Picture 1>: fully_preserved - fixed first frame anchor at 00.00s
<Subject 1>: partially_preserved - facial identity, braided black hair, and cobalt wool coat from <Picture 1> and <Picture 2> retained across new walking motion
<Audio 1>: reference - vocal timbre and measured cadence guide speech of <Subject 1> (S1) without copying audio signal
detailed_description:
Timeline:
[00.00s-02.80s]:
[VISUAL]: [Shot 1] Medium shot beginning directly from <Picture 1> at 00.00s as <Subject 1> pivots the shoulders of <Subject 1> toward the open carriage door and lifts the left and right hands to smooth the cobalt wool lapels while cool white steam drifts lazily across damp concrete tiles and warm carriage window light catches the braided hair of <Subject 1>.
[SPEECH]: <Subject 1> (S1) <d>[English] Boarding closes in thirty seconds. </d>
[SOUNDS]: Soft leather boot steps on damp concrete, gentle steam release hiss, and muted platform murmur.
[02.80s-05.00s]:
[VISUAL]: Slow Push In tracks behind the right shoulder of <Subject 1> as <Subject 1> steps smoothly across the metal threshold into the lit train vestibule, the hem of the cobalt coat swaying backward while overhead yellow bulbs flicker softly and carriage doors begin gliding inward from left and right.
[SOUNDS]: Crisp metal heel tap on the train threshold, pneumatic door slide hum, and fading platform air.
overall_soundscape:
Light leather footsteps, soft steam hiss, metallic vestibule step, and pneumatic door glide ground the station scene.
non_diegetic_music:
N/A
```

---

## Example 3: Video Motion Transfer With Audio Copy & Non-Replaced Speaker (6-Field)
**User Goal**: *"Replace the person dancing in Video 1 with the character in Picture 1, keep the original soundtrack Audio 1, and keep the DJ in the background talking."*

```text
subject_definitions:
<Subject 1> is a lean dancer in a silver bomber jacket and charcoal cargo pants, defined visually from <Picture 1> and following motion from <Video 1>.
<Subject 2> is a club DJ wearing headphones and a dark hoodie behind the booth in <Video 1>.
<Video 1> supplies choreography, camera movement, timing, and club progression.
<Audio 1> is the full synchronized soundtrack copied from <Video 1>.
summary:
[video editing + reference generation + audio reuse] The target video is an edited version of <Video 1> where the on-screen dancer is replaced by <Subject 1> using visual traits from <Picture 1> and choreography from <Video 1>, retaining the full audio track from <Audio 1> while <Subject 2> speaks from the DJ booth under magenta club beams in live action footage.
retention_analysis:
<Subject 1>: attribute_transfer - visual identity and outfit from <Picture 1> transferred onto dancer choreography of <Video 1>
<Subject 2>: fully_preserved - background DJ identity, placement, and spoken line from <Video 1> retained
<Video 1>: partially_preserved - camera movement, choreography, timing, and club setting retained with dancer replaced by <Subject 1>
<Audio 1>: fully_copy - source audio track is copied entirely
detailed_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Tracking Shot circles clockwise as <Subject 1> executes sharp footwork across the scuffed dance floor, the silver bomber jacket catching sweeping magenta beams while <Subject 2> leans toward the booth microphone behind <Subject 1> and points upward with one raised hand.
[SPEECH]: <Subject 2> (S1) <d>[English] Hands up for the drop! </d>
[SOUNDS]: Sneaker soles pivoting across wood flooring and muffled crowd cheers beneath the booth.
[MUSIC]: <Audio 1>
overall_soundscape:
<Audio 1> provides the complete synchronized club audio landscape of sneaker pivots, crowd cheers, and booth acoustics.
non_diegetic_music:
<Audio 1> serves as the full upbeat electronic club soundtrack throughout the video.
```

---

## Example 4: Anti-Pattern Repair (Before -> After)
**Broken Input**:
- Uses `both hands`, `<Subject 1>'s jacket`, `they`, unpadded `[3.00s-6.00s]`, empty `[SPEECH]: None`, and `<Picture 1>` leaked into a standalone prompt.

**Fixed Rules Applied**:
- Remove `<Picture 1>` everywhere in standalone output.
- Replace `<Subject 1>'s jacket` -> `the jacket of <Subject 1>`.
- Replace `both hands` -> `the left and right hands`; replace `they` -> `<Subject 1> and <Subject 2>`.
- Zero-pad `[03.00s-06.00s]:` and delete `[SPEECH]: None` completely.
