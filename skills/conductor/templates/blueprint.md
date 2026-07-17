---
module: "{{MODULE_NAME}}"
slug: "{{MODULE_SLUG}}"
created: "{{DATE}}"
mode: "{{new|adopt}}"
gate_level: "{{run-ahead|gate-every-phase}}"
approved_by_divya: "{{DATE or PENDING}}"
sweep_paths: ["{{CODE_GLOB_1}}", "{{CODE_GLOB_2}}"]
sweep_keywords: ["{{KEYWORD_1}}", "{{KEYWORD_2}}"]
---

# {{MODULE_NAME}} — Module Blueprint

> Writer: Conductor only, after Divya approves.

## The job sentence

> When I {{REAL_SITUATION}}, I want to {{GOAL}}, so that {{OUTCOME}}.

## Scope

**In:** {{WHAT_THIS_MODULE_COVERS}}

**Out (named, not implied):** {{WHAT_IT_DELIBERATELY_DOES_NOT_COVER}}

## What "finished" means

{{3_TO_6_PLAIN_ENGLISH_BULLETS — the module-level definition of done, including Divya's human items (device smoke tests, sign-offs)}}

## Phases & waves

| Phase | Name | One-line promise | Depends on | Wave |
|---|---|---|---|---|
| 01 | {{NAME}} | {{PROMISE}} | — | 1 |
| 02 | {{NAME}} | {{PROMISE}} | 01 | 2 |

Rules baked into this table:
- A phase's wave = 1 + (highest wave among its dependencies). Phases sharing a wave MAY run in parallel windows.
- Two phases that touch the same files MUST NOT share a wave — sequence them and note why here.

## Cross-module integration (CLAUDE.md blocking principle)

- Signals this module generates: {{LIST}}
- Existing modules that could consume them: {{LIST}}
- Existing module data this module consumes: {{LIST}}
- Cross-module AI opportunity: {{LIST_OR_NONE_STATED}}
