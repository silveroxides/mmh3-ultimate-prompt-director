"""Unit tests for validate_h3_prompt.py."""

import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_h3_prompt import snap_h3_duration, validate_prompt

VALID_STANDALONE_4 = """integrated_multimodal_description:
Timeline:
[00.00s-03.00s]:
[VISUAL]: [Shot 1] Wide tracking shot glides forward down a rain slick neon alley as a runner sprints past puddles, water spraying off boots with slow dolly acceleration while steam vents drift across warm storefront light.
[SPEECH]: (S1) <d>[English] Keep moving, they locked the lower gate! </d>
[SOUNDS]: Rapid wet footsteps splashing across asphalt, distant thunder rumble, and steady rain hiss.
[MUSIC]: Low pulsing analog synth bass swells quietly beneath the rainfall.
[03.00s-06.00s]:
[VISUAL]: [Shot 2] Close cut to the runner vaulting a steel railing while rain streaks across a tight lens, sparks flaring from an overhead sign above dark wet concrete.
[SOUNDS]: Metallic clang of boots against steel, sharp exhaled breath, and sizzling electric crackle.
overall_soundscape:
Steady heavy rainfall, rapid splashing footsteps, metallic impacts, and distant thunder echo across the alley.
non_diegetic_music:
A pulsing analog synthesizer bassline drives the opening chase before cutting out for the final vault.
"""

VALID_STANDALONE_5 = """subject_definitions:
<Subject 1>: A courier wearing a dark waxed jacket and scuffed boots.
summary:
A courier sprints across a flooded street to deliver a sealed metal tube before dawn. Shot in gritty live action photography with cool sodium streetlights and wet reflections.
detailed_description:
Timeline:
[00.000s-04.500s]:
[VISUAL]: [Shot 1] Medium tracking shot follows <Subject 1> sprinting across wet cobblestones as rainwater sprays from the boots of <Subject 1> and cold wind whips the dark jacket collar backward.
[SOUNDS]: Heavy splashing footsteps, wind gusts, and rattling metal clasp.
overall_soundscape:
Brisk rain, heavy wet footsteps, and wind rushing past stone walls fill the street.
non_diegetic_music:
N/A
"""

VALID_REFERENCE_6_VARIANT_D = """subject_definitions:
<Subject 1> is a tall woman with braided black hair and a cobalt coat, referenced from <Picture 1> and <Picture 2>.
<Picture 1> is the fixed first frame anchor at 00.00s.
<Audio 1> is the voice-timbre reference for <Subject 1> (S1).
summary:
[keyframe completion + reference generation + audio reference] The completed video opens directly from the rainy station platform and tracks a brisk departure through drifting steam. <Subject 1> steps toward the train door while speaking calmly under cool fluorescent lights in crisp live action cinema style.
retention_analysis:
<Picture 1>: fully_preserved - fixed first frame anchor at 00.00s
<Subject 1>: partially_preserved - facial identity, braided hair, and cobalt coat from <Picture 1> and <Picture 2> retained across new walking motion
<Audio 1>: reference - vocal timbre and measured cadence guide speech of <Subject 1> (S1) without copying signal
detailed_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Medium shot beginning directly from <Picture 1> at 00.00s as <Subject 1> turns the shoulders of <Subject 1> toward the platform edge and raises the left and right hands to adjust the cobalt coat collar while steam drifts across cool overhead light.
[SPEECH]: <Subject 1> (S1) <d>[English] Boarding closes in thirty seconds. </d>
[SOUNDS]: Distant train brake hiss, soft leather boot steps on wet concrete, and faint platform murmur.
overall_soundscape:
Soft wet footsteps, escaping steam hiss, and distant rail rumble ground the station platform.
non_diegetic_music:
N/A
"""


def test_valid_envelopes_pass():
    r4 = validate_prompt(VALID_STANDALONE_4, duration=6.0)
    assert r4.valid, r4.errors
    assert r4.detected_mode == "standalone_4"
    assert r4.precision == 2
    assert r4.shot_count == 2

    r5 = validate_prompt(VALID_STANDALONE_5, duration=4.5)
    assert r5.valid, r5.errors
    assert r5.detected_mode == "standalone_5"
    assert r5.precision == 3

    r6 = validate_prompt(VALID_REFERENCE_6_VARIANT_D, duration=4.0, require_retention=True, require_keyframe_tag=True)
    assert r6.valid, r6.errors
    assert r6.detected_mode == "reference_6"


def test_rejects_timestamp_gap_and_unpadded_seconds():
    bad = VALID_STANDALONE_4.replace("[03.00s-06.00s]:", "[3.50s-06.00s]:")
    res = validate_prompt(bad, duration=6.0)
    assert not res.valid
    assert any("zero-pad" in e for e in res.errors)
    assert any("gap or overlap" in e for e in res.errors)


def test_rejects_possessive_pronouns_and_both_on_subjects():
    bad = VALID_STANDALONE_5.replace("the boots of <Subject 1>", "<Subject 1>'s boots").replace("the dark jacket collar", "both hands on their collar")
    res = validate_prompt(bad)
    assert not res.valid
    assert any("possessive" in e for e in res.errors)
    assert any("both" in e and "their" in e for e in res.errors)


def test_rejects_media_leak_in_standalone_and_range_shorthand():
    bad_standalone = VALID_STANDALONE_5.replace("scuffed boots.", "scuffed boots, referenced from <Picture 1>.")
    res = validate_prompt(bad_standalone, mode="standalone_5")
    assert not res.valid
    assert any("Standalone mode" in e for e in res.errors)

    bad_range = VALID_REFERENCE_6_VARIANT_D.replace("<Picture 1> and <Picture 2>", "<Picture 1>-<Picture 3>")
    res2 = validate_prompt(bad_range)
    assert not res2.valid
    assert any("ranges" in e for e in res2.errors)


def test_rejects_speech_placeholder_storyboard_leak_and_bad_retention():
    bad_speech = VALID_STANDALONE_4.replace(
        "[SPEECH]: (S1) <d>[English] Keep moving, they locked the lower gate! </d>",
        "[SPEECH]: None",
    )
    res = validate_prompt(bad_speech)
    assert not res.valid
    assert any("placeholder" in e for e in res.errors)

    bad_story = VALID_STANDALONE_4.replace("neon alley", "comic strip panel borders")
    res2 = validate_prompt(bad_story, storyboard=True)
    assert not res2.valid
    assert any("Storyboard" in e for e in res2.errors)

    bad_ret = VALID_REFERENCE_6_VARIANT_D.replace(
        "<Audio 1>: reference - vocal timbre",
        "<Audio 1>: partially_preserved - vocal timbre (S1)",
    )
    res3 = validate_prompt(bad_ret)
    assert not res3.valid
    assert any("Speaker ID" in e for e in res3.errors)
    assert any("Invalid audio retention marker" in e for e in res3.errors)


def test_cli_stdin_exit_codes():
    script = Path(__file__).resolve().parent / "validate_h3_prompt.py"
    proc = subprocess.run([sys.executable, str(script), "--duration", "6.0"], input=VALID_STANDALONE_4, text=True, capture_output=True)
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["valid"] is True


def test_documented_examples_validate():
    import re

    examples_path = Path(__file__).resolve().parents[1] / "references" / "examples.md"
    blocks = re.findall(r"```text\r?\n(.*?)\r?\n```", examples_path.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 4

    ex1 = validate_prompt(blocks[0], mode="standalone_4", duration=6.0)
    assert ex1.valid, ex1.errors

    ex2 = validate_prompt(blocks[1], mode="reference_6", duration=5.0, require_retention=True, require_keyframe_tag=True)
    assert ex2.valid, ex2.errors

    ex3 = validate_prompt(blocks[2], mode="reference_6", duration=4.0, require_retention=True, forbid_keyframe_tag=True)
    assert ex3.valid, ex3.errors

    ex4 = validate_prompt(blocks[3], mode="reference_6", duration=5.0, require_retention=True, forbid_keyframe_tag=True)
    assert ex4.valid, ex4.errors


def test_expected_segments_and_literal_starts():
    ok = validate_prompt(VALID_STANDALONE_4, duration=6.0, expected_segments=2, expected_starts=["00.00", "03.00"])
    assert ok.valid, ok.errors

    bad_count = validate_prompt(VALID_STANDALONE_4, expected_segments=3)
    assert not bad_count.valid
    assert any("expected 3" in e for e in bad_count.errors)

    bad_starts = validate_prompt(VALID_STANDALONE_4, expected_starts=["00.00", "02.50"])
    assert not bad_starts.valid
    assert any("do not match expected" in e for e in bad_starts.errors)


def test_edge_syntax_continuation_transfer_and_speech_variants():
    continuation_and_edge = """subject_definitions:
<Subject 1> is a street courier wearing a dark waterproof jacket and boots.
<Video 1> is the prior rainy chase clip whose ending momentum, camera velocity, and neon reflections continue directly.
<Audio 1> is the rhythmic synth percussion track used as style reference.
summary:
[video continuation + audio reference] <Subject 1> continues sprinting across the wet rooftop directly out of the prior ending pose while rain lashes the skyline.
retention_analysis:
<Video 1>: partially_preserved - ending pose, camera tracking momentum, and wet rooftop environment continue directly into the opening beat
<Subject 1>: fully_preserved - courier appearance and jacket continuity remain intact across the continued sprint
<Audio 1>: weak_reference - driving industrial percussion tempo guides score feel without copying source audio
detailed_description:
Timeline:
[00.00s-02.50s]:
[VISUAL]: [Shot 1] Continuing directly from the forward lean at the end of <Video 1>, <Subject 1> drives hard off wet concrete toward the stairwell door as the camera tracks low behind the boots while rain sheets catch neon glare <scenetrans>.
[SPEECH]: (S1,S2) <d>[English] [unclear] Keep moving across the roof! </d> <scenetrans>
[SOUNDS]: Wet boot slaps echo sharply against puddles as heavy rain hammers steel vents.
[MUSIC]: Pulsing industrial snare and low analog bass swell steadily behind the sprint.
[02.50s-05.00s]:
[VISUAL]: <Subject 1> shoulders through the metal door onto the landing, boots skidding slightly across gritty tile as overhead fluorescent light flickers over damp shoulders while the camera pushes forward steadily.
[SPEECH]: <Audio 1> <d>[English] Move now before the hatch locks <cutoff> </d>
[SOUNDS]: Steel latch clangs shut beside heavy uneven breathing inside the stairwell.
[MUSIC]: Industrial drums tighten into a sharp rising pulse at the end of the climb.
overall_soundscape:
Driving rooftop rainfall, sharp wet boot impacts, metallic door clangs, and labored breathing carry cleanly across the stairwell transition.
non_diegetic_music:
Driving industrial percussion and low analog bass mirror the sprint energy from <Audio 1> without copying raw stems."""

    res = validate_prompt(continuation_and_edge, mode="reference_6", duration=5.0, require_retention=True)
    assert res.valid, res.errors

    partial_copy_prompt = continuation_and_edge.replace(
        "<Audio 1>: weak_reference - driving industrial percussion tempo guides score feel without copying source audio",
        "<Audio 1>: partially_copy - selected ambient rain and rhythmic stems mix beneath new dialogue",
    ).replace(
        "[video continuation + audio reference]",
        "[video continuation + audio reuse]",
    )
    res_partial = validate_prompt(partial_copy_prompt, mode="reference_6", duration=5.0, require_retention=True)
    assert res_partial.valid, res_partial.errors

    empty_d = continuation_and_edge.replace("<d>[English] [unclear] Keep moving across the roof! </d>", "<d>   </d>")
    res_empty_d = validate_prompt(empty_d, mode="reference_6", duration=5.0)
    assert not res_empty_d.valid
    assert any("empty '<d></d>'" in e for e in res_empty_d.errors)


def test_eval_scenarios_manifest_valid():
    scenarios_dir = Path(__file__).resolve().parents[1] / "evals" / "scenarios"
    files = sorted(scenarios_dir.glob("*.json"))
    assert len(files) == 10
    for f in files:
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data.get("name") and data.get("prompt")
        assert isinstance(data.get("judge"), list) and len(data["judge"]) >= 1


def test_h3_architecture_length_grid_and_cli():
    assert snap_h3_duration(5.167) == (124, 5.167)
    assert snap_h3_duration(8.0) == (192, 8.0)
    assert snap_h3_duration(0.21) == (5, 0.208)

    script = Path(__file__).resolve().parent / "validate_h3_prompt.py"
    proc = subprocess.run([sys.executable, str(script), "--list-h3-lengths"], text=True, capture_output=True)
    assert proc.returncode == 0
    rows = json.loads(proc.stdout)
    assert any(r["frames"] == 124 and r["seconds_3dp"] == 5.167 for r in rows)
    assert any(r["frames"] == 192 and r["seconds_3dp"] == 8.0 for r in rows)


def test_attribute_transfer_audio_timbre_and_no_audio():
    timbre_prompt = """subject_definitions:
<Subject 1> is a street poet wearing a wool coat and scarf, defined visually from <Picture 1> and following motion from <Video 1>.
<Subject 2> is a cafe barista in a canvas apron standing beside the espresso machine in <Video 1>.
<Video 1> supplies walking motion, camera movement, timing, and street cafe setting.
<Audio 1> is the vocal-timbre reference for <Subject 1> (S1).
summary:
[video editing + reference generation + audio reference] The target video is an edited version of <Video 1> where the main speaker is replaced by <Subject 1> using visual traits from <Picture 1> and motion from <Video 1>, referencing vocal timbre from <Audio 1> while <Subject 2> responds beside the counter.
retention_analysis:
<Subject 1>: attribute_transfer - visual identity and appearance from <Picture 1> transferred onto <Video 1> motion
<Subject 2>: fully_preserved - non-replaced barista appearance, placement, and spoken response from <Video 1> retained
<Video 1>: partially_preserved - camera movement, pacing, and cafe progression retained with speaker replaced by <Subject 1>
<Audio 1>: reference - vocal timbre and delivery guide speech of <Subject 1> (S1) without copying audio signal
detailed_description:
Timeline:
[00.00s-04.00s]:
[VISUAL]: [Shot 1] Dolly Shot glides past steamed glass as <Subject 1> steps up to the wooden counter with gloved hands tucked into the wool coat while <Subject 2> turns from the brass espresso machine.
[SPEECH]: <Subject 1> (S1) <d>[English] Two dark roasts when you have a moment. </d>
[SOUNDS]: Door chime rings softly above porcelain cup clinks and espresso steam hiss.
overall_soundscape:
Soft cafe door chimes, porcelain cup clinks, and steady espresso steam fill the counter space without copying <Audio 1>.
non_diegetic_music:
N/A"""

    res_timbre = validate_prompt(timbre_prompt, mode="reference_6", duration=4.0, require_retention=True, audio_mode="timbre", video_editing=True)
    assert res_timbre.valid, res_timbre.errors

    no_audio_prompt = timbre_prompt.replace(
        "<Audio 1> is the vocal-timbre reference for <Subject 1> (S1).\n", ""
    ).replace(
        "[video editing + reference generation + audio reference]", "[video editing + reference generation]"
    ).replace(
        ", referencing vocal timbre from <Audio 1>", ""
    ).replace(
        "<Audio 1>: reference - vocal timbre and delivery guide speech of <Subject 1> (S1) without copying audio signal\n", ""
    ).replace(
        "[SPEECH]: <Subject 1> (S1) <d>[English] Two dark roasts when you have a moment. </d>\n", ""
    ).replace(
        " without copying <Audio 1>", ""
    )

    res_no_audio = validate_prompt(no_audio_prompt, mode="reference_6", duration=4.0, require_retention=True, audio_mode="none", video_editing=True)
    assert res_no_audio.valid, res_no_audio.errors


def test_stage8_mode_flags_vague_video_ban_and_audio_consistency():
    # Reject vague video/guide references when no <Video N> tag exists + pronouns in summary
    vague_leak = VALID_STANDALONE_4.replace("neon alley", "guide video alley")
    res_vague = validate_prompt(vague_leak, mode="standalone_4")
    assert not res_vague.valid
    assert any("vague video reference" in e for e in res_vague.errors)

    bare_guide_leak = VALID_STANDALONE_5.replace("to deliver a sealed metal tube", "mimicking the routine shown in the guide")
    res_bare_guide = validate_prompt(bare_guide_leak, mode="standalone_5")
    assert not res_bare_guide.valid
    assert any("vague video reference" in e for e in res_bare_guide.errors)

    mimic_leak = VALID_STANDALONE_5.replace("to deliver a sealed metal tube", "while mimicking someone off camera")
    res_mimic = validate_prompt(mimic_leak, mode="standalone_5")
    assert not res_mimic.valid
    assert any("vague video reference" in e for e in res_mimic.errors)

    sum_pronoun_leak = VALID_STANDALONE_5.replace("before dawn.", "as they greet the dawn.")
    res_sum_p = validate_prompt(sum_pronoun_leak, mode="standalone_5")
    assert not res_sum_p.valid
    assert any("'summary:' uses banned pronoun" in e for e in res_sum_p.errors)

    # Reject <d> inside overall_soundscape and warn on missing [SPEECH] / [MUSIC]
    bad_soundscape = VALID_STANDALONE_4.replace(
        "Steady heavy rainfall, rapid splashing footsteps, metallic impacts, and distant thunder echo across the alley.",
        "Steady heavy rainfall while (S1) says <d>[English] Go! </d>.",
    )
    res_d = validate_prompt(bad_soundscape)
    assert not res_d.valid
    assert any("overall_soundscape:" in e and "<d>" in e for e in res_d.errors)

    no_speech_warn = VALID_STANDALONE_4.replace(
        "[SPEECH]: (S1) <d>[English] Keep moving, they locked the lower gate! </d>\n", ""
    ).replace(
        "sprints past puddles", "shouting while sprinting past puddles"
    )
    res_warn = validate_prompt(no_speech_warn)
    assert res_warn.valid
    assert any("without a [SPEECH] line" in w for w in res_warn.warnings)

    # Verify --fl2va and --audio-mode copy on documented examples
    examples_path = Path(__file__).resolve().parents[1] / "references" / "examples.md"
    import re

    blocks = re.findall(r"```text\r?\n(.*?)\r?\n```", examples_path.read_text(encoding="utf-8"), re.S)
    assert len(blocks) == 4
    ex2 = validate_prompt(blocks[1], mode="reference_6", duration=5.0, require_retention=True, fl2va=True)
    assert ex2.valid, ex2.errors
    ex3 = validate_prompt(blocks[2], mode="reference_6", duration=4.0, require_retention=True, audio_mode="copy", video_editing=True)
    assert ex3.valid, ex3.errors

    # Negative check for --audio-mode copy missing [MUSIC]: <Audio 1>
    bad_copy = blocks[2].replace("[MUSIC]: <Audio 1>\n", "")
    res_bad_copy = validate_prompt(bad_copy, mode="reference_6", audio_mode="copy", video_editing=True)
    assert not res_bad_copy.valid
    assert any("[MUSIC]: <Audio 1>" in e for e in res_bad_copy.errors)

    placeholder_d = VALID_REFERENCE_6_VARIANT_D.replace(
        "[SPEECH]: <Subject 1> (S1) <d>[English] Boarding closes in thirty seconds. </d>",
        "[SPEECH]: <Subject 1> (S1) <d>[English] (No dialogue, silent focus) </d>",
    )
    res_placeholder_d = validate_prompt(placeholder_d, mode="reference_6", duration=4.0, require_retention=True)
    assert not res_placeholder_d.valid
    assert any("non-spoken placeholder/stage note" in e for e in res_placeholder_d.errors)

    bare_speaker_prompt = VALID_REFERENCE_6_VARIANT_D.replace(
        "[SPEECH]: <Subject 1> (S1) <d>[English] Boarding closes in thirty seconds. </d>",
        "[SPEECH]: (S1) <d>I can't anymore...</d>",
    )
    res_bare = validate_prompt(bare_speaker_prompt, mode="reference_6", duration=4.0, require_retention=True)
    assert res_bare.valid
    assert any("bare speaker ID without subject tag" in w for w in res_bare.warnings)
    assert any("missing leading language tag" in w for w in res_bare.warnings)
