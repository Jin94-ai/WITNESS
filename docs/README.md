# docs/ — Witness documentation index

Witness consists of two engines that share the `engine/` + `content/` code
but produce *separate* record/artifact streams. This directory is organised
by engine so that future cross-engine work does not mix the two record
streams.

## Engine split

| | **Person Engine** (v0.5–v1.2) | **World Engine** (v2.0, in progress) |
|---|---|---|
| Code | `engine/` (unchanged) | `world/` |
| Content packs | `content/peter/`, `content/judas/`, ... | `content/worlds/jerusalem_ad30/` |
| Tests | `tests/test_engine/`, `tests/test_peter/` | `tests/test_world/` |
| Written records | [docs/person/](person/) | [docs/world/](world/) |
| Run-time data | [data/person/](../data/person/) | [data/world/](../data/world/) |

## Contents

- **[person/](person/)** — paper artifacts (Cohen's d, POM, counterfactual, etc.)
  produced by the Person Engine v0.5–v1.2.
  - [person/paper_data/](person/paper_data/) — paper figures + `paper_numbers.json`.
- **[world/](world/)** — World Engine design docs, Spike reviews, figures.
  - [world/SPIKE_1_REVIEW.md](world/SPIKE_1_REVIEW.md) — external-LLM review
    packet for Spike 1 (Layers 1 + 2 + 3 + 5 + Sync bridge).
- **[prompts/](prompts/)** — session-prompt snapshots handed to Claude Code
  (baseline, counterfactual, world-spike 1A, world-spike 3 draft,
  world-spike 4 draft, world-spike 5 draft).
- **[archive/](archive/)** — one-off historical review documents.
- **[recipe-cards/](recipe-cards/)** — distilled recipe cards from past
  exploration phases (`CLAUDE.md` Probe & Stitch workflow).
- [ODD_PROTOCOL.md](ODD_PROTOCOL.md) — ODD template notes.
- [session-prompts.md](session-prompts.md) — index of past session prompts.

## Authoritative design docs

These live at the repo root because they are edited often and referenced
from code comments and tests:

| File | Scope |
|------|-------|
| [CLAUDE.md](../CLAUDE.md) | Claude Code behaviour rules |
| [DESIGN.md](../DESIGN.md) | Person Engine v0.7 roadmap |
| [DESIGN_LATENT_DRIVE.md](../DESIGN_LATENT_DRIVE.md) | Person Engine v1.0 latent-drive design |
| [TRACE_SCHEMA.md](../TRACE_SCHEMA.md) | v0.7 trace pipeline schema |
| [ITERATION_CLASSIFICATION.md](../ITERATION_CLASSIFICATION.md) | Iteration tiering |
| [PAPER_DRAFT_V06.md](../PAPER_DRAFT_V06.md) | Person Engine paper working draft |
| [PAPER_OUTLINE_V05.md](../PAPER_OUTLINE_V05.md) | Paper outline (superseded by draft) |
| [PROJECT_DIRECTION_v2.md](../PROJECT_DIRECTION_v2.md) | Paper-writing phase plan |
| [RESEARCH.md](../RESEARCH.md) | Research notes |
| [SCENARIO_TEMPLATE.md](../SCENARIO_TEMPLATE.md) | Adding a new Person-Engine scenario |
| [WORLD_DESIGN.md](../WORLD_DESIGN.md) | World Engine v2.0 design |
| [WORLD_DESIGN_v1.1_amendments.md](../WORLD_DESIGN_v1.1_amendments.md) | v2.0 amendments (sync layer, 3-tier agents, Jesus as agent) |
