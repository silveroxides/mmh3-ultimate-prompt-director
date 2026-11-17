# MMH3 Ultimate Prompt Director

Portable Agent Skill for generating, expanding, repairing, and explaining **MiniMax H3** adaptive timeline audio-visual prompts from minimal plain-language user goals and optional media inputs.

## Structure

- `SKILL.md` — Intent classifier, lazy reference router, and validation workflow
- `SPEC.md` — Maintenance contract, scope boundaries, and acceptance gates
- `SOURCES.md` — Source provenance and 6-axis coverage matrix
- `references/` — Modular MiniMax H3 timeline, audio, expansion, standalone, keyframe/scene/storyboard, multi-reference/transfer, repair/Q&A, and worked examples
- `scripts/validate_h3_prompt.py` — Zero-dependency deterministic Python validator (`--help` for CLI options)
- `scripts/test_validate_h3_prompt.py` — Pytest suite for validator contracts
- `scripts/test_all_h3_modes.py` — Full MiniMax H3 mode-matrix regression tests
- `evals/` — Scenario fixtures covering all H3 prompt variations and negative cases

## Install

```bash
npx skills add silveroxides/mmh3-ultimate-prompt-director -g
```

## Validate Locally

```bash
python scripts/validate_h3_prompt.py --help
pytest scripts/
```
