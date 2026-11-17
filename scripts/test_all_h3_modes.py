"""Stage 9 comprehensive end-to-end prompt matrix covering all MiniMax H3 modes and edge cases."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_h3_prompt import snap_h3_duration, validate_prompt

RICH_TEXT_BLOCK_A = (
    "[Shot 1] Wide tracking shot glides smoothly across rain slicked cobblestones in crisp live action cinema as <Subject 1> "
    "leans forward into a brisk stride, dark waxed canvas coat rippling behind broad shoulders while warm amber shopfront "
    "lamps shimmer across shallow puddles and mist curls around iron street bollards."
)
RICH_TEXT_BLOCK_B = (
    "Slow Push In tightens toward <Subject 1> pausing beside an arched wooden doorway, right gloved fingers gripping the brass "
    "latch while damp hair clings to the forehead of <Subject 1> and distant headlights sweep soft shadows across wet stone."
)


def test_standalone_modes_and_inplace_replacement():
    # 5-field T2VA multi-subject consistency + colon syntax
    p_5 = f"""subject_definitions:
<Subject 1>: A courier wearing a dark waxed canvas coat, wool scarf, and scuffed leather boots.
<Subject 2>: A watchmaker wearing brass spectacles and an olive twill apron beside a wooden counter.
summary:
<Subject 1> arrives out of evening rain into a lantern lit workshop and passes a sealed brass cylinder to <Subject 2> across a worn oak bench. Shot in textured live action cinema with warm amber practicals and cool street twilight.
detailed_description:
Timeline:
[00.00s-03.50s]:
[VISUAL]: {RICH_TEXT_BLOCK_A}
[SOUNDS]: Wet leather boots splashing softly over puddles and distant city wind.
[MUSIC]: Sparse muted cello sustains a low suspenseful note beneath the rain.
[03.50s-07.00s]:
[VISUAL]: [Shot 2] Hard cut inside the workshop as <Subject 1> steps up to the oak bench and hands the brass cylinder to <Subject 2> while <Subject 2> adjusts brass spectacles with steady fingers under warm tungsten lamp glow and dust motes drift slowly across the timber shelves.
[SPEECH]: <Subject 2> (S1) <d>[English] You made it before midnight. </d>
[SOUNDS]: Wooden door latch clicks shut beside soft clockwork ticking across the shelves.
[MUSIC]: Soft solo piano enters gently after the spoken line fades.
overall_soundscape:
Light street rainfall gives way to a solid wooden door latch and delicate ticking clockwork inside the workshop.
non_diegetic_music:
A low muted cello opens beneath the rain before giving way to sparse solo piano notes inside the workshop."""
    res5 = validate_prompt(p_5, mode="standalone_5", duration=7.0, strict_word_counts=True)
    assert res5.valid, res5.errors

    # Storyboard T2VA standalone (4-field) + --storyboard + in-place replacement (no swap prose)
    p_story_t2va = """integrated_multimodal_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Tracking Shot sweeps sideways along a sunlit wooden rooftop in crisp hand painted anime style as a silver haired swordfighter in a crimson haori sprints across clay tiles, left and right sandals kicking loose moss downward while distant wind chimes sway above green pine ridges and morning light catches steel scabbard edges.
[SPEECH]: (S1) <d>[English] Move! </d>
[SOUNDS]: Crisp sandal slaps across clay roof tiles and rushing morning wind.
[MUSIC]: Fast taiko percussion and shamisen plucks drive forward momentum.
[04.00s-08.00s]:
[VISUAL]: Arc Shot swings upward as the swordfighter plants the right foot against a mossy stone parapet and vaults cleanly across the courtyard gap, crimson haori billowing wide against pale clouds before both sandals drop squarely onto damp flagstones with bent knees absorbing impact.
[SOUNDS]: Stone scrape under sandals, billowing cloth snap, and heavy flagstone landing thud.
[MUSIC]: Taiko drums crest during the leap then drop to a held bamboo flute note.
overall_soundscape:
Rapid sandal footsteps, rushing wind, stone scrapes, billowing cloth snaps, and heavy courtyard landing thuds carry the leap.
non_diegetic_music:
Fast taiko percussion and shamisen plucks accelerate into the rooftop leap before settling onto a sustained bamboo flute."""
    res_st = validate_prompt(p_story_t2va, mode="standalone_4", duration=8.0, storyboard=True)
    assert res_st.valid, res_st.errors


def test_fl2va_one_and_two_keyframes():
    p_fl2va_2 = """subject_definitions:
<Subject 1> is a glazed white ceramic teacup filled with dark amber tea sitting near the edge of a walnut counter.
<Picture 1> is the fixed first frame anchor at 00.00s.
<Picture 2> is the fixed final frame anchor at video endpoint.
summary:
[keyframe completion] Starting from <Picture 1> on the walnut counter edge, <Subject 1> tips forward and plunges downward onto slate floor tiles, shattering cleanly into the exact scattered porcelain layout fixed in <Picture 2> under bright morning window light.
retention_analysis:
<Picture 1>: fully_preserved - fixed first frame anchor at 00.00s
<Picture 2>: fully_preserved - fixed final frame anchor at video endpoint
<Subject 1>: partially_preserved - ceramic glaze and shape from <Picture 1> break into shards matching <Picture 2>
detailed_description:
Timeline:
[00.00s-02.40s]:
[VISUAL]: [Shot 1] Close Up holds directly on <Picture 1> at 00.00s as <Subject 1> trembles slightly from an unseen counter vibration, dark tea sloshing over the porcelain rim before <Subject 1> tilts past the walnut edge and drops vertically while the camera tilts downward along the fall.
[SOUNDS]: Subtle porcelain rattle on wood followed by a sharp air rush and liquid splash.
[02.40s-05.00s]:
[VISUAL]: Tilt Down follows <Subject 1> striking the cool grey slate tile, shattering outward into curved ceramic fragments and splashing amber tea trails that settle precisely into the resting shard geometry locked in <Picture 2> as morning window light glints across wet edges.
[SOUNDS]: Sharp ceramic shatter across slate tile, scattering shard clinks, and settling liquid drips.
overall_soundscape:
Soft porcelain vibration gives way to falling liquid splatter and crisp ceramic shattering across slate floor tiles.
non_diegetic_music:
N/A"""
    res2 = validate_prompt(p_fl2va_2, mode="reference_6", duration=5.0, require_retention=True, fl2va=True)
    assert res2.valid, res2.errors

    p_fl2va_1 = p_fl2va_2.replace("<Picture 2> is the fixed final frame anchor at video endpoint.\n", "").replace(
        "shattering cleanly into the exact scattered porcelain layout fixed in <Picture 2>",
        "shattering across slate tiles cleanly",
    ).replace("<Picture 2>: fully_preserved - fixed final frame anchor at video endpoint\n", "").replace(
        "matching <Picture 2>", "shattering on tile"
    ).replace("locked in <Picture 2> ", "across the tiles ")
    res1 = validate_prompt(p_fl2va_1, mode="reference_6", duration=5.0, require_retention=True, fl2va=True)
    assert res1.valid, res1.errors


def test_scene_image_variants_a_b_c_and_default():
    # Default SCENE_IMAGE_ANY2VA (visual seed only -> no retention_analysis:, no <Picture 1>)
    p_default = """subject_definitions:
<Subject 1> is a botanist wearing a linen field shirt, rolled sleeves, leather satchel, and dusty khaki trousers.
summary:
[reference generation] <Subject 1> kneels beside misted greenhouse glass to examine a blooming night orchid while morning sunbeams cut through humid air and water droplets roll from broad leaves in natural live action cinema.
detailed_description:
Timeline:
[00.000s-05.167s]:
[VISUAL]: [Shot 1] Medium shot slowly Push In behind <Subject 1> kneeling beside dark soil beds as the right hand of <Subject 1> parts broad waxy leaves gently, revealing pale orchid petals glistening under slanted golden sunbeams while humid mist drifts past rusted iron rafters and water drips steadily onto damp stone.
[SOUNDS]: Soft leaf rustle, steady greenhouse water drips, and quiet morning breeze against glass panes.
overall_soundscape:
Gentle foliage rustle, steady condensation drips, and muffled breeze against glass panes fill the quiet greenhouse.
non_diegetic_music:
N/A"""
    res_def = validate_prompt(p_default, mode="reference_6", duration=5.167, precision=3, forbid_retention=True, forbid_keyframe_tag=True)
    assert res_def.valid, res_def.errors
    assert snap_h3_duration(5.167) == (124, 5.167)

    # Variant A (Audio Copy) + Variant C (Turnaround refs) + non-keyframe scene ref
    p_var_ac = """subject_definitions:
<Subject 1> is a street drummer wearing a faded denim vest and red bandana, referenced from <Picture 1> and <Picture 2>.
<Audio 1> is the full synchronized street percussion soundtrack.
summary:
[reference generation + audio reuse] <Subject 1> performs an energetic bucket drum solo beside brick shopfronts while pedestrians pause in warm afternoon sunlight in crisp live action handheld cinema.
retention_analysis:
<Subject 1>: partially_preserved - appearance and denim vest from <Picture 1> and <Picture 2> retained across dynamic drumming motion
<Audio 1>: fully_copy - source audio track is copied entirely
detailed_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Tracking Shot arcs steadily around <Subject 1> seated on an overturned crate as the left and right hands of <Subject 1> drive wooden drumsticks rapidly across plastic buckets while denim fringe bounces and warm brick light glints off spinning stick tips.
[SOUNDS]: Crisp plastic bucket rim clicks and rapid snare-like drum rolls matching stick impacts.
[MUSIC]: <Audio 1>
overall_soundscape:
<Audio 1> supplies the complete street percussion landscape, sharp rim clicks, and muted sidewalk ambience.
non_diegetic_music:
<Audio 1> provides the complete synchronized rhythmic soundtrack throughout the clip."""
    res_ac = validate_prompt(p_var_ac, mode="reference_6", duration=4.0, require_retention=True, forbid_keyframe_tag=True)
    assert res_ac.valid, res_ac.errors


def test_mixed_timeline_samples_and_multi_subject_attr_transfer():
    # MIXED literal timestamps (precision=3, expected_starts, trailing ref Picture)
    p_mixed = """subject_definitions:
<Subject 1> is a mountain cyclist in a matte black helmet, neon windbreaker, and padded gloves, referenced from <Picture 3>.
<Picture 1> is the timeline start frame at 00.000s.
<Picture 2> is the mid-descent turn sample at 02.500s.
summary:
[keyframe completion + reference generation] <Subject 1> carves cleanly down a gravel switchback from <Picture 1> through the banked apex in <Picture 2> and accelerates into pine shadow under crisp overcast daylight.
retention_analysis:
<Picture 1>: fully_preserved - opening trail composition at 00.000s retained
<Picture 2>: fully_preserved - mid-descent turn framing at 02.500s retained
<Subject 1>: partially_preserved - helmet and neon windbreaker from <Picture 3> retained across trail motion
detailed_description:
Timeline:
[00.000s-02.500s]:
[VISUAL]: [Shot 1] Tracking Shot glides behind <Subject 1> starting from <Picture 1> as <Subject 1> pedals hard down loose gravel, tires kicking fine dust outward while the neon windbreaker ripples in headwind toward the banked hairpin.
[SOUNDS]: Crushing gravel beneath knobby tires, freehub ratcheting clicks, and rushing wind.
[02.500s-05.167s]:
[VISUAL]: Tracking Shot leans smoothly through the <Picture 2> apex as <Subject 1> shifts hips inward, braking briefly before accelerating into cool pine shade at the trail bend.
[SOUNDS]: Brief disc brake hiss, sliding gravel spray, and brisk wind rush through pine needles.
overall_soundscape:
Continuous gravel tire crunch, freehub clicks, brief disc brake hiss, and pine forest wind track the descent.
non_diegetic_music:
N/A"""
    res_mix = validate_prompt(
        p_mixed,
        mode="reference_6",
        duration=5.167,
        precision=3,
        expected_segments=2,
        expected_starts=["00.000", "02.500"],
        require_retention=True,
    )
    assert res_mix.valid, res_mix.errors

    # Multi-subject Attribute Transfer (<Subject 1> from <Picture 1>, <Subject 2> from <Picture 2>) + Audio Copy
    p_multi_attr = """subject_definitions:
<Subject 1> is a woman in a tailored emerald blazer and silver earrings, defined visually from <Picture 1> and following motion from <Video 1>.
<Subject 2> is a tall man in a charcoal trench coat, defined visually from <Picture 2> and following motion from <Video 1>.
<Video 1> supplies walking choreography, camera movement, timing, and plaza progression.
<Audio 1> is the full synchronized soundtrack copied from <Video 1>.
summary:
[video editing + reference generation + audio reuse] The target video is an edited version of <Video 1> where two lead walkers are replaced by <Subject 1> from <Picture 1> and <Subject 2> from <Picture 2> while retaining the plaza camera motion and <Audio 1> soundtrack.
retention_analysis:
<Subject 1>: attribute_transfer - visual identity and blazer from <Picture 1> transferred onto <Video 1> motion
<Subject 2>: attribute_transfer - visual identity and trench coat from <Picture 2> transferred onto <Video 1> motion
<Video 1>: partially_preserved - camera movement, choreography, timing, and plaza setting retained with subjects replaced by <Subject 1> and <Subject 2>
<Audio 1>: fully_copy - source audio track is copied entirely
detailed_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Dolly Shot pulls backward steadily ahead of <Subject 1> and <Subject 2> walking side by side across pale stone paving as <Subject 1> turns toward <Subject 2> with raised right hand while the charcoal trench coat of <Subject 2> sways evenly in cool morning breeze.
[SPEECH]: <Subject 1> (S1) <d>[English] Check the north entrance first. </d>
[SOUNDS]: Crisp leather shoe steps on stone paving and light plaza fountain spray.
[MUSIC]: <Audio 1>
overall_soundscape:
<Audio 1> provides the complete plaza acoustic landscape of stone footsteps, distant fountain spray, and ambient murmur.
non_diegetic_music:
<Audio 1> serves as the complete synchronized background score throughout the scene."""
    res_ma = validate_prompt(p_multi_attr, mode="reference_6", duration=4.0, require_retention=True, video_editing=True, audio_mode="copy")
    assert res_ma.valid, res_ma.errors


def test_storyboard_any2va_and_offscreen_voiceover():
    p_story_any = """subject_definitions:
<Subject 1> is a hooded archivist wearing brass goggles and a patched linen cloak, referenced from <Picture 1>.
summary:
[reference generation] <Subject 1> steps carefully into a dusty stone vault holding an iron lantern aloft, scanning carved wall glyphs before lowering the hood quietly as an off-screen narrator warns of the collapsing seal in atmospheric live action cinema.
retention_analysis:
<Subject 1>: partially_preserved - hooded archivist cloak and brass goggles from <Picture 1> retained across vault exploration
detailed_description:
Timeline:
[00.00s-05.00s]:
[VISUAL]: [Shot 1] Push In glides behind <Subject 1> crossing the cracked threshold as the right hand of <Subject 1> raises an iron lantern, warm amber light sweeping across carved limestone glyphs while dust motes swirl around the cloak hem and the lips of <Subject 1> remain closed throughout the quiet inspection.
[SPEECH]: <Subject 1> (S1) says in an off-screen voiceover <d>[English] Nobody opened this seal in three centuries. </d> while the lips of <Subject 1> remain closed.
[SOUNDS]: Soft leather sole scrapes on limestone dust, gentle iron lantern ring creak, and hollow vault air.
overall_soundscape:
Quiet limestone footsteps, faint metal lantern creaks, and hollow stone vault echoes accompany the inspection.
non_diegetic_music:
N/A"""
    res_sa = validate_prompt(p_story_any, mode="reference_6", duration=5.0, storyboard=True, require_retention=True, forbid_keyframe_tag=True)
    assert res_sa.valid, res_sa.errors
