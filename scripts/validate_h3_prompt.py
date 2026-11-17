#!/usr/bin/env python3
"""Deterministic validator for MiniMax H3 adaptive timeline prompts."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import re
import sys

ALLOWED_TASK_TAGS = {
    "keyframe completion",
    "reference generation",
    "video editing",
    "video continuation",
    "audio reuse",
    "audio reference",
}

VISIBLE_MARKERS = {"fully_preserved", "partially_preserved", "attribute_transfer", "weak_reference"}
AUDIO_MARKERS = {"fully_copy", "partially_copy", "reference", "weak_reference"}

ENVELOPES = {
    "standalone_4": ["integrated_multimodal_description:", "overall_soundscape:", "non_diegetic_music:"],
    "standalone_5": ["subject_definitions:", "summary:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"],
    "reference_6_with_ret": ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"],
    "reference_6_no_ret": ["subject_definitions:", "summary:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"],
}

TOP_FIELDS_SET = {
    "integrated_multimodal_description:",
    "subject_definitions:",
    "summary:",
    "retention_analysis:",
    "detailed_description:",
    "overall_soundscape:",
    "non_diegetic_music:",
}

TS_LINE_RE = re.compile(r"^\[(\d+\.\d{2,3})s-(\d+\.\d{2,3})s\]:(.*)$")
SHOT_RE = re.compile(r"\[Shot\s+(\d+)\]")
SPEECH_SYNTAX_RE = re.compile(r"(?:(?:<Subject\s+\d+>\s+)?\(S\d+(?:,S\d+)*\)|<Audio\s+\d+>)")
D_TAG_RE = re.compile(r"<d>(.*?)</d>", re.S)
SPEECH_EMPTY_RE = re.compile(r"^(?:none|n/a|no speech|no dialogue|silence|silent|\{.*\})\.?$", re.I)
MEDIA_TAG_RE = re.compile(r"<(?:Picture|Video|Audio)\s+\d+>")
MEDIA_RANGE_RE = re.compile(r"<(Picture|Video|Audio)\s+\d+>\s*(?:-|to|through|–|—)\s*<\1\s+\d+>", re.I)
SUBJECT_TAG_RE = re.compile(r"<Subject\s+\d+>")
BAD_SUBJECT_SUFFIX_RE = re.compile(r"<Subject\s+\d+>(?:'s|’s|[a-zA-Z]|-)")
PRONOUN_BANS_RE = re.compile(r"\b(?:he|she|him|her|his|their|theirs|they|them|both)\b", re.I)
STORYBOARD_LEAK_RE = re.compile(
    r"\b(?:storyboard(?:\s+sequence|\s+video)?|comic\s+strip|manga\s+page|stitched\s+images?|speech\s+bubbles?|speech\s+balloons?|panel\s+borders?|gutters?)\b",
    re.I,
)
VAGUE_VIDEO_RE = re.compile(
    r"\b(?:source\s+video|guide\s+video|original\s+video|reference\s+video|pre-existing\s+video|story\s+guide|input\s+video|the\s+footage)\b",
    re.I,
)
VIDEO_TAG_RE = re.compile(r"<Video\s+\d+>")
AUDIO_TAG_RE = re.compile(r"<Audio\s+\d+>")
VISUAL_SPEECH_WARN_RE = re.compile(r"\b(?:sings|singing|speaks|speaking|shouts|shouting|whispers|whispering)\b", re.I)
TEMPLATE_LEAK_RE = re.compile(r"\{[^{}\n]{2,60}\}")


@dataclass
class ValidationReport:
    valid: bool
    detected_mode: str
    precision: int | None
    duration_seconds: float | None
    segment_count: int
    shot_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def h3_video_length_from_seconds(seconds: float) -> int:
    """Return frame count rounded up onto MiniMax H3's 24 fps 5 + 17k grid."""
    if seconds < 0:
        raise ValueError("Duration must be non-negative.")
    frames = max(5, round(seconds * 24))
    return frames + (5 - frames % 17) % 17


def snap_h3_duration(seconds: float) -> tuple[int, float]:
    frames = h3_video_length_from_seconds(seconds)
    return frames, round(frames / 24.0, 3)


def h3_length_grid(min_k: int = 4, max_k: int = 22) -> list[dict[str, object]]:
    rows = []
    for k in range(min_k, max_k + 1):
        frames = 5 + 17 * k
        sec = frames / 24.0
        rows.append({"k": k, "frames": frames, "seconds_3dp": round(sec, 3), "seconds_2dp": round(sec, 2)})
    return rows


def _ms(ts: str) -> int:
    whole, frac = ts.split(".")
    frac_padded = frac.ljust(3, "0")
    return int(whole) * 1000 + int(frac_padded)


def _check_ts_format(ts: str, expected_prec: int | None, errors: list[str], label: str) -> int | None:
    whole, frac = ts.split(".")
    if len(whole) < 2:
        errors.append(f"{label} timestamp '{ts}s' must zero-pad single-digit seconds (e.g. 02.50s).")
    if len(frac) not in (2, 3):
        errors.append(f"{label} timestamp '{ts}s' must use 2 or 3 decimal places.")
        return expected_prec
    if expected_prec is None:
        return len(frac)
    if len(frac) != expected_prec:
        errors.append(f"{label} timestamp '{ts}s' uses {len(frac)} decimals; expected {expected_prec}.")
    return expected_prec


def _parse_sections(text: str, errors: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    order: list[str] = []
    sections: dict[str, list[str]] = {}
    current: str | None = None
    in_fence = False
    for idx, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            errors.append(f"Line {idx}: markdown code fences are forbidden in generated prompts.")
            continue
        if stripped in TOP_FIELDS_SET:
            if raw != stripped:
                errors.append(f"Line {idx}: field '{stripped}' must start in column one with no indentation or prefix.")
            if stripped in sections:
                errors.append(f"Line {idx}: duplicate top-level field '{stripped}'.")
            current = stripped
            order.append(stripped)
            sections[current] = []
            continue
        # Handle inline single-line `field: value` if user pasted on same line
        matched_inline = None
        for f in TOP_FIELDS_SET:
            if stripped.startswith(f + " "):
                matched_inline = f
                break
        if matched_inline:
            if not raw.startswith(matched_inline):
                errors.append(f"Line {idx}: field '{matched_inline}' must start in column one.")
            if matched_inline in sections:
                errors.append(f"Line {idx}: duplicate top-level field '{matched_inline}'.")
            current = matched_inline
            order.append(matched_inline)
            rest = stripped[len(matched_inline) :].strip()
            sections[current] = [rest] if rest else []
            continue
        if current is None:
            if stripped:
                errors.append(f"Line {idx}: unexpected text before first top-level field: '{stripped[:60]}'.")
        else:
            sections[current].append(raw)
    return order, sections


def validate_prompt(
    text: str,
    *,
    mode: str = "auto",
    duration: float | None = None,
    precision: int | None = None,
    require_retention: bool = False,
    forbid_retention: bool = False,
    forbid_media_tags: bool = False,
    require_keyframe_tag: bool = False,
    forbid_keyframe_tag: bool = False,
    storyboard: bool = False,
    strict_word_counts: bool = False,
    expected_segments: int | None = None,
    expected_starts: list[str] | None = None,
    audio_mode: str | None = None,
    video_editing: bool = False,
    fl2va: bool = False,
) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    order, sections = _parse_sections(text, errors)

    detected_mode = mode
    if mode == "auto":
        if "integrated_multimodal_description:" in sections:
            detected_mode = "standalone_4"
        elif "retention_analysis:" in sections:
            detected_mode = "reference_6"
        elif "subject_definitions:" in sections:
            has_media = bool(MEDIA_TAG_RE.search(text))
            has_task_bracket = bool(
                sections.get("summary:")
                and re.match(r"^\s*\[[^\]]+\]", "\n".join(sections["summary:"]).strip())
            )
            detected_mode = "reference_6" if (has_media or has_task_bracket) else "standalone_5"
        else:
            detected_mode = "unknown"

    if detected_mode == "standalone_4":
        expected_order = ENVELOPES["standalone_4"]
        forbid_media_tags = True
    elif detected_mode == "standalone_5":
        expected_order = ENVELOPES["standalone_5"]
        forbid_media_tags = True
    elif detected_mode == "reference_6":
        expected_order = ENVELOPES["reference_6_with_ret"] if "retention_analysis:" in sections else ENVELOPES["reference_6_no_ret"]
    else:
        errors.append("Could not detect a valid MiniMax H3 top-level field envelope.")
        return ValidationReport(False, detected_mode, precision, None, 0, 0, errors, warnings)

    if order != expected_order:
        errors.append(f"Top-level field order mismatch: got {order}, expected {expected_order}.")

    if require_retention and "retention_analysis:" not in sections:
        errors.append("Missing required 'retention_analysis:' section.")
    if forbid_retention and "retention_analysis:" in sections:
        errors.append("'retention_analysis:' must be omitted for this mode.")

    # Check global leaks
    if TEMPLATE_LEAK_RE.search(text):
        errors.append("Unreplaced template placeholder '{...}' found in output.")
    if MEDIA_RANGE_RE.search(text):
        errors.append("Media identifier ranges (e.g. '<Picture 1>-<Picture 3>') are forbidden; list every tag individually.")
    if forbid_media_tags and MEDIA_TAG_RE.search(text):
        errors.append("Standalone mode must not emit <Picture N>, <Video N>, or <Audio N> tags.")
    if storyboard and STORYBOARD_LEAK_RE.search(text):
        errors.append("Storyboard/comic-convention terminology leaked into prompt output.")
    if BAD_SUBJECT_SUFFIX_RE.search(text):
        errors.append("Forbidden suffix or possessive attached directly to '<Subject N>' (e.g. `<Subject 1>'s`).")
    if "—" in text or "–" in text:
        errors.append("Em-dashes (—) and en-dashes (–) are forbidden in prompt prose.")
    vague_vid = VAGUE_VIDEO_RE.findall(text)
    if vague_vid and not VIDEO_TAG_RE.search(text):
        errors.append(f"Forbidden vague video reference(s) {sorted(set(v.lower() for v in vague_vid))} when no <Video N> tag is active.")
    elif vague_vid:
        warnings.append(f"Use strict <Video N> tags instead of vague prose {sorted(set(v.lower() for v in vague_vid))}.")

    # Validate subject_definitions
    defined_subjects: set[str] = set()
    if "subject_definitions:" in sections:
        subj_lines = [l for l in sections["subject_definitions:"] if l.strip()]
        if not subj_lines:
            errors.append("'subject_definitions:' cannot be empty.")
        for sl in subj_lines:
            if re.match(r"^\s*(?:[-*]|\d+\.)\s+", sl):
                errors.append(f"Bullet or numbering prefix forbidden in subject_definitions: '{sl.strip()[:50]}'.")
            if sl != sl.lstrip():
                errors.append(f"Indentation forbidden in subject_definitions: '{sl[:50]}'.")
            for m in SUBJECT_TAG_RE.finditer(sl):
                defined_subjects.add(m.group(0))

    # Validate summary
    summary_tags: list[str] = []
    sum_text = ""
    if "summary:" in sections:
        sum_text = " ".join(l.strip() for l in sections["summary:"] if l.strip())
        if not sum_text:
            errors.append("'summary:' cannot be empty.")
        else:
            if detected_mode == "reference_6":
                bm = re.match(r"^\[([^\]]+)\]\s*(.+)$", sum_text)
                if not bm:
                    errors.append("Reference-aware 'summary:' must begin with bracketed task prefix like '[reference generation]'.")
                else:
                    summary_tags = [t.strip() for t in bm.group(1).split("+")]
                    if len(summary_tags) != len(set(summary_tags)):
                        errors.append(f"Duplicate task tags in summary prefix: '{bm.group(1)}'.")
                    unknown = [t for t in summary_tags if t not in ALLOWED_TASK_TAGS]
                    if unknown:
                        errors.append(f"Unknown task tag(s) in summary prefix: {unknown}.")
                    if require_keyframe_tag and "keyframe completion" not in summary_tags:
                        errors.append("Summary prefix must include 'keyframe completion' for concrete keyframe anchors.")
                    if forbid_keyframe_tag and "keyframe completion" in summary_tags:
                        errors.append("Summary prefix must not include 'keyframe completion' without a concrete keyframe anchor.")
            if MEDIA_TAG_RE.search(sum_text):
                warnings.append("Media tag (<Picture/Video/Audio N>) appears in 'summary:'; keep media provenance in subject_definitions/retention_analysis unless explicitly requested.")
            words = len(sum_text.split())
            if strict_word_counts and words < 50:
                warnings.append(f"'summary:' has {words} words (target >= 50 words for full 3-5 sentence summary).")

    # Validate retention_analysis
    ret_entries: dict[str, str] = {}
    if "retention_analysis:" in sections:
        ret_lines = [l.strip() for l in sections["retention_analysis:"] if l.strip()]
        if not ret_lines:
            errors.append("'retention_analysis:' is present but empty.")
        for rl in ret_lines:
            m = re.match(r"^([^:]+):\s*([a-z_]+)\s+-\s+(.+)$", rl)
            if not m:
                if re.search(r"\(S\d+\)", rl):
                    errors.append(f"Speaker ID '(Sx)' forbidden inside retention_analysis: '{rl}'.")
                errors.append(f"Malformed retention_analysis line (expected '<label>: <marker> - <descriptor>'): '{rl}'.")
                continue
            label, marker, desc = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            ret_entries[label] = marker
            if not desc:
                errors.append(f"Empty retention descriptor in '{rl}'.")
            if re.search(r"\(S\d+\)", rl) and not (label.startswith("<Audio") and marker == "reference"):
                errors.append(f"Speaker ID '(Sx)' forbidden inside retention_analysis: '{rl}'.")
            if label.startswith("<Audio"):
                if marker not in AUDIO_MARKERS:
                    errors.append(f"Invalid audio retention marker '{marker}' in '{rl}'.")
            else:
                if marker not in VISIBLE_MARKERS:
                    errors.append(f"Invalid visible retention marker '{marker}' in '{rl}'.")

    # Extract Timeline lines from integrated_multimodal_description or detailed_description
    timeline_host = "integrated_multimodal_description:" if detected_mode == "standalone_4" else "detailed_description:"
    host_lines = sections.get(timeline_host, [])
    tl_idx = next((i for i, l in enumerate(host_lines) if l.strip() == "Timeline:"), None)
    if tl_idx is None:
        errors.append(f"Missing 'Timeline:' line inside '{timeline_host}'.")
        return ValidationReport(False, detected_mode, precision, None, 0, 0, errors, warnings)

    tl_lines = host_lines[tl_idx + 1 :]
    blocks: list[dict] = []
    cur_block: dict | None = None

    for raw in tl_lines:
        s = raw.strip()
        if not s:
            continue
        if re.match(r"^Part\s+\d+\s*:", s, re.I):
            errors.append(f"Forbidden fixed heading '{s}' inside Timeline.")
            continue
        ts_m = TS_LINE_RE.match(s)
        if ts_m:
            if cur_block is not None:
                blocks.append(cur_block)
            cur_block = {
                "start": ts_m.group(1),
                "end": ts_m.group(2),
                "inline": ts_m.group(3).strip(),
                "channels": [],
            }
            if cur_block["inline"]:
                errors.append(f"Timestamp line '[{cur_block['start']}s-{cur_block['end']}s]:' should place channels on subsequent lines, not inline.")
            continue
        if cur_block is None:
            errors.append(f"Timeline content before first timestamp range: '{s[:60]}'.")
            continue
        ch_m = re.match(r"^\[(VISUAL|SPEECH|SOUNDS|MUSIC)\]:(.*)$", s)
        if ch_m:
            cur_block["channels"].append((ch_m.group(1), ch_m.group(2).strip()))
        else:
            errors.append(f"Unexpected non-channel line inside timestamp block '[{cur_block['start']}s-{cur_block['end']}s]': '{s[:60]}'.")

    if cur_block is not None:
        blocks.append(cur_block)

    if not blocks:
        errors.append("Timeline contains zero timestamp blocks.")
        return ValidationReport(False, detected_mode, precision, None, 0, 0, errors, warnings)

    # Validate timestamps & block contents
    active_prec = precision
    prev_end_ms: int | None = None
    expected_shot = 1
    total_shots = 0

    for b_idx, blk in enumerate(blocks):
        st, en = blk["start"], blk["end"]
        active_prec = _check_ts_format(st, active_prec, errors, f"Block {b_idx + 1} start")
        active_prec = _check_ts_format(en, active_prec, errors, f"Block {b_idx + 1} end")
        st_ms, en_ms = _ms(st), _ms(en)
        if b_idx == 0 and st_ms != 0:
            errors.append(f"First timestamp block must start at 00.00s/00.000s, got '{st}s'.")
        if en_ms <= st_ms:
            errors.append(f"Block {b_idx + 1} end '{en}s' must be strictly greater than start '{st}s'.")
        if prev_end_ms is not None and st_ms != prev_end_ms:
            errors.append(f"Timestamp gap or overlap before block {b_idx + 1}: previous ended at {prev_end_ms / 1000:.3f}s, next starts at '{st}s'.")
        prev_end_ms = en_ms

        ch_names = [c[0] for c in blk["channels"]]
        if not ch_names or ch_names[0] != "VISUAL":
            errors.append(f"Block [{st}s-{en}s] must begin with '[VISUAL]:'.")
        if ch_names.count("VISUAL") > 1:
            errors.append(f"Block [{st}s-{en}s] has multiple '[VISUAL]:' lines.")
        if "SOUNDS" in ch_names and "MUSIC" in ch_names:
            if ch_names.index("MUSIC") < ch_names.index("SOUNDS"):
                errors.append(f"Block [{st}s-{en}s] places '[MUSIC]' before '[SOUNDS]'.")
        if "SPEECH" in ch_names and "SOUNDS" in ch_names:
            if ch_names.index("SOUNDS") < ch_names.index("SPEECH"):
                errors.append(f"Block [{st}s-{en}s] places '[SOUNDS]' before '[SPEECH]'.")

        for ch_name, body in blk["channels"]:
            if not body:
                errors.append(f"Block [{st}s-{en}s] has empty '[{ch_name}]:' line.")
                continue
            if ch_name == "VISUAL":
                shots = [int(x) for x in SHOT_RE.findall(body)]
                if b_idx == 0 and (not shots or shots[0] != 1):
                    errors.append(f"First block [{st}s-{en}s] [VISUAL] must open with '[Shot 1]'.")
                for s_num in shots:
                    if s_num != expected_shot:
                        errors.append(f"Block [{st}s-{en}s] has '[Shot {s_num}]', expected '[Shot {expected_shot}]'.")
                    expected_shot = s_num + 1
                    total_shots += 1
                if defined_subjects:
                    pm = PRONOUN_BANS_RE.findall(body)
                    if pm:
                        errors.append(f"Block [{st}s-{en}s] [VISUAL] uses banned pronoun/group word(s) {sorted(set(x.lower() for x in pm))} with defined <Subject N> tags.")
                if "SPEECH" not in ch_names and VISUAL_SPEECH_WARN_RE.search(body) and not re.search(r"lips\s+remain\s+closed|silent|without\s+speaking", body, re.I):
                    warnings.append(f"Block [{st}s-{en}s] [VISUAL] describes speaking/singing without a [SPEECH] line.")
                if strict_word_counts and len(body.split()) < 70:
                    warnings.append(f"Block [{st}s-{en}s] [VISUAL] has {len(body.split())} words (rich target >= 70 words).")
            elif ch_name == "SPEECH":
                if SPEECH_EMPTY_RE.match(body):
                    errors.append(f"Block [{st}s-{en}s] emits placeholder [SPEECH]; omit the line when no speech occurs.")
                else:
                    d_matches = D_TAG_RE.findall(body)
                    if not d_matches:
                        errors.append(f"Block [{st}s-{en}s] [SPEECH] must wrap spoken words in '<d>...</d>'.")
                    elif any(not m.strip() for m in d_matches):
                        errors.append(f"Block [{st}s-{en}s] [SPEECH] has empty '<d></d>' dialogue tag.")
                    elif not SPEECH_SYNTAX_RE.search(body):
                        errors.append(f"Block [{st}s-{en}s] [SPEECH] missing speaker ID '(Sx)' or '<Audio N>' source.")
            elif ch_name == "SOUNDS":
                if re.search(r"\b(?:background music|soundtrack|orchestral score|synth beat|bassline|drumbeat)\b", body, re.I):
                    warnings.append(f"Block [{st}s-{en}s] [SOUNDS] appears to include music/score cues; move music to [MUSIC].")

    final_dur = prev_end_ms / 1000.0 if prev_end_ms is not None else None
    if duration is not None and prev_end_ms is not None:
        if abs(prev_end_ms - round(duration * 1000)) > 1:
            errors.append(f"Timeline ends at {final_dur:.3f}s, expected requested duration {duration:.3f}s.")
    if expected_segments is not None and len(blocks) != expected_segments:
        errors.append(f"Timeline has {len(blocks)} segment(s), expected {expected_segments}.")
    if expected_starts is not None:
        norm_expected = [s.strip().removesuffix("s") for s in expected_starts if s.strip()]
        actual_starts = [blk["start"] for blk in blocks]
        if actual_starts != norm_expected:
            errors.append(f"Segment start timestamps {actual_starts} do not match expected {norm_expected}.")

    # Whole-video audio summaries
    soundscape_val = " ".join(l.strip() for l in sections.get("overall_soundscape:", []) if l.strip())
    music_val = " ".join(l.strip() for l in sections.get("non_diegetic_music:", []) if l.strip())
    for wf, val in (("overall_soundscape:", soundscape_val), ("non_diegetic_music:", music_val)):
        if not val:
            errors.append(f"'{wf}' cannot be empty (use 'N/A' for non_diegetic_music when absent).")
    if "<d>" in soundscape_val or "</d>" in soundscape_val:
        errors.append("Dialogue tags '<d>...</d>' are forbidden inside 'overall_soundscape:'.")

    all_music_bodies = [body for blk in blocks for ch_name, body in blk["channels"] if ch_name == "MUSIC"]
    if music_val and music_val.upper() != "N/A" and not all_music_bodies and not AUDIO_TAG_RE.search(music_val):
        warnings.append("'non_diegetic_music:' describes music while Timeline: has no [MUSIC] cue.")

    # Mode-contract enforcement flags
    if video_editing:
        if detected_mode != "reference_6":
            errors.append("--video-editing requires the 6-field reference-aware envelope.")
        if not summary_tags or summary_tags[0] != "video editing":
            errors.append("--video-editing requires 'video editing' first in summary prefix.")
        if "The target video is an edited version of <Video 1>" not in sum_text:
            errors.append("--video-editing summary must open with 'The target video is an edited version of <Video 1>'.")
        if "<Video 1>" not in ret_entries:
            errors.append("--video-editing requires '<Video 1>' entry in retention_analysis:.")

    if fl2va:
        if detected_mode != "reference_6":
            errors.append("--fl2va requires the 6-field reference-aware envelope.")
        if "keyframe completion" not in summary_tags:
            errors.append("--fl2va requires 'keyframe completion' in summary prefix.")
        if ret_entries.get("<Picture 1>") != "fully_preserved":
            errors.append("--fl2va requires '<Picture 1>: fully_preserved - ...' in retention_analysis:.")
        if re.search(r"^<Picture\s+2>\s+is\b", "\n".join(sections.get("subject_definitions:", [])), re.M) and ret_entries.get("<Picture 2>") != "fully_preserved":
            errors.append("--fl2va requires '<Picture 2>: fully_preserved - ...' when <Picture 2> is a standalone frame anchor.")
        first_visual = next((body for ch_name, body in blocks[0]["channels"] if ch_name == "VISUAL"), "")
        if "<Picture 1>" not in first_visual:
            errors.append("--fl2va first segment [VISUAL] must open from '<Picture 1>'.")

    if audio_mode == "copy":
        if "audio reuse" not in summary_tags:
            errors.append("--audio-mode copy requires 'audio reuse' in summary prefix.")
        if ret_entries.get("<Audio 1>") not in ("fully_copy", "partially_copy"):
            errors.append("--audio-mode copy requires '<Audio 1>: fully_copy' or 'partially_copy' in retention_analysis:.")
        if not any(b == "<Audio 1>" for b in all_music_bodies):
            errors.append("--audio-mode copy requires '[MUSIC]: <Audio 1>' in Timeline.")
        if not soundscape_val.startswith("<Audio 1>"):
            errors.append("--audio-mode copy requires 'overall_soundscape:' to begin with '<Audio 1>'.")
        if not music_val.startswith("<Audio 1>"):
            errors.append("--audio-mode copy requires 'non_diegetic_music:' to begin with '<Audio 1>'.")
    elif audio_mode == "timbre":
        if "audio reference" not in summary_tags:
            errors.append("--audio-mode timbre requires 'audio reference' in summary prefix.")
        if ret_entries.get("<Audio 1>") != "reference":
            errors.append("--audio-mode timbre requires '<Audio 1>: reference' in retention_analysis:.")
        if any("<Audio 1>" in b for b in all_music_bodies):
            errors.append("--audio-mode timbre must not emit '[MUSIC]: <Audio 1>' (signal is not copied).")
        if music_val.startswith("<Audio 1>"):
            errors.append("--audio-mode timbre must not begin 'non_diegetic_music:' with copied '<Audio 1>'.")
    elif audio_mode == "none":
        if AUDIO_TAG_RE.search(text):
            errors.append("--audio-mode none forbids '<Audio N>' tags anywhere in the prompt.")
        if music_val.strip().upper() != "N/A":
            errors.append("--audio-mode none requires 'non_diegetic_music: N/A'.")

    return ValidationReport(
        valid=len(errors) == 0,
        detected_mode=detected_mode,
        precision=active_prec,
        duration_seconds=final_dur,
        segment_count=len(blocks),
        shot_count=total_shots,
        errors=errors,
        warnings=warnings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a MiniMax H3 adaptive timeline prompt.")
    parser.add_argument("prompt_file", nargs="?", type=Path, help="Path to prompt text file (reads stdin if omitted).")
    parser.add_argument("--mode", choices=("auto", "standalone_4", "standalone_5", "reference_6"), default="auto")
    parser.add_argument("--duration", type=float, help="Expected exact total duration in seconds.")
    parser.add_argument("--precision", type=int, choices=(2, 3), help="Required decimal precision (2 or 3).")
    parser.add_argument("--require-retention", action="store_true")
    parser.add_argument("--forbid-retention", action="store_true")
    parser.add_argument("--forbid-media-tags", action="store_true")
    parser.add_argument("--require-keyframe-tag", action="store_true")
    parser.add_argument("--forbid-keyframe-tag", action="store_true")
    parser.add_argument("--storyboard", action="store_true", help="Enforce storyboard/comic-convention leak bans.")
    parser.add_argument("--strict-word-counts", action="store_true", help="Warn when summary < 50 words or [VISUAL] < 70 words.")
    parser.add_argument("--expected-segments", type=int, help="Exact required number of timeline segments when user/workflow specifies one.")
    parser.add_argument("--expected-starts", help="Comma-separated exact start timestamps (e.g. '00.00,03.20') to preserve literally.")
    parser.add_argument("--audio-mode", choices=("copy", "timbre", "none"), help="Enforce audio-copy, vocal-timbre, or no-audio contract.")
    parser.add_argument("--video-editing", action="store_true", help="Enforce video editing summary opening and <Video 1> retention.")
    parser.add_argument("--fl2va", action="store_true", help="Enforce first/last frame anchor contract.")
    parser.add_argument("--list-h3-lengths", action="store_true", help="Print MiniMax H3 24 fps 5+17k supported frame/second lengths as JSON and exit.")
    args = parser.parse_args()

    if args.list_h3_lengths:
        print(json.dumps(h3_length_grid(), indent=2))
        return 0

    text = args.prompt_file.read_text(encoding="utf-8") if args.prompt_file else sys.stdin.read()
    starts_list = args.expected_starts.split(",") if args.expected_starts else None
    report = validate_prompt(
        text,
        mode=args.mode,
        duration=args.duration,
        precision=args.precision,
        require_retention=args.require_retention,
        forbid_retention=args.forbid_retention,
        forbid_media_tags=args.forbid_media_tags,
        require_keyframe_tag=args.require_keyframe_tag,
        forbid_keyframe_tag=args.forbid_keyframe_tag,
        storyboard=args.storyboard,
        strict_word_counts=args.strict_word_counts,
        expected_segments=args.expected_segments,
        expected_starts=starts_list,
        audio_mode=args.audio_mode,
        video_editing=args.video_editing,
        fl2va=args.fl2va,
    )
    print(json.dumps(asdict(report), indent=2))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
