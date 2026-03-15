---
name: design-system-adapt
description: Adapt one canonical design-system model into consumer-specific outputs for AI, design, and runtime workflows. Use this skill when the task involves translating source tokens, semantic layers, patterns, component contracts, or responsive system rules into PM-facing, UX-facing, developer-facing, Figma-facing, or runtime-facing schemas. This version is adapt-first and keeps clear boundaries for future audit and normalize extensions.
metadata:
  short-description: Adapt a design system into consumer-specific schemas
---

# Design System Adapt

Use this skill when a design system has one canonical model and the task is to reshape that model for a specific consumer without turning the consumer output into the new source of truth.

## Quick Rules

- Find the canonical source first. Typical inputs are a source token file, system schema, component contract document, or PRD.
- Adapt the representation for the target consumer; do not silently redefine system meaning.
- Treat Figma files, runtime exports, and AI-facing schemas as downstream projections unless the user explicitly asks for an output-only patch.
- Preserve the distinction between `primitive`, `semantic`, `pattern`, and `component`.
- Use repo-relative references only. Do not introduce absolute filesystem paths into the skill or generated docs.
- When the output contract is explicit, use the bundled scripts instead of regenerating adapter logic ad hoc.

## Default Workflow

1. Identify the source-of-truth artifact and the target consumer.
2. Read only the reference that matches the task:
   - Read [references/system-model.md](references/system-model.md) for token architecture, naming, and layer semantics.
   - Read [references/adapt-workflow.md](references/adapt-workflow.md) for role-based outputs, adapter strategy, and handoff flow.
   - Read [references/module-boundaries.md](references/module-boundaries.md) only when the task touches future `audit` or `normalize` expansion.
3. If the output shape is deterministic, run the matching script:
   - `scripts/build_ai_adapter.py`
   - `scripts/build_figma_adapter.py`
   - `scripts/build_runtime_adapter.py`
   - `scripts/validate_adapters.py`
4. Decide whether the request is source-first, output-first, or documentation-first.
5. Make the smallest change that keeps the canonical model and its projections coherent.
6. State what remains authoritative, what is derived, and whether any regeneration or follow-up is still needed.

## Task Routing

### Source-first adaptation

Use this path when the user asks to change token structure, semantic meaning, component contracts, or adaptive rules.

- Update the canonical source or governing doc first.
- Preserve aliases, mode parity, and naming intent where possible.
- Keep responsive or adaptive logic explicit rather than hiding it inside consumer-specific hacks.

### Consumer-specific adaptation

Use this path when the user asks for AI-facing, Figma-facing, Vercel-facing, or runtime-facing outputs.

- Keep the consumer schema optimized for how that consumer works.
- Prefer stable naming, explicit structure, and derived metadata over lossy flattening.
- Use the script-generated contract when the consumer requires strict import shape, such as Figma plugin import or runtime pipeline ingestion.
- If a consumer-only patch creates drift risk, say so clearly.

### Documentation and publishing

Use this path when the user asks to package, describe, publish, or hand off the skill.

- Keep the skill self-contained and portable.
- Remove project-specific branding unless it is intentionally part of the public contract.
- Avoid assumptions about repository name, local directory layout, or a fixed install location.

## Output Priorities By Consumer

### PM or AI prototyping

- Preserve intent, allowed usage, and preferred component or pattern choices.
- Make semantic meaning obvious enough for prompt-based generation.
- Favor reusable structures over raw visual values.

### UX or Figma workflows

- Preserve naming clarity, theme parity, and variable-friendly grouping.
- Keep pattern and component boundaries legible.
- Avoid adding AI-only metadata that makes the design-facing output hard to use.

### Developers or runtime systems

- Prefer stable keys, deterministic modes, and implementation-friendly shape.
- Keep token references traceable back to the canonical model.
- Make adaptive rules explicit enough to map cleanly into code or build tooling.

## Default Constraints

- One canonical model should remain clearly identifiable.
- `pattern` and `component` are parallel views, not a forced serial chain.
- `pattern` and `component` should usually consume `semantic.*`, and may directly consume `primitive.*` for structural values.
- Consumer outputs should stay derivable from the source model.
- The current public surface is `adapt`; future `audit` and `normalize` additions should extend, not blur, this contract.

## When To Read More Context

- Read [references/system-model.md](references/system-model.md) before changing taxonomy, naming, layer semantics, or adaptive architecture language.
- Read [references/adapt-workflow.md](references/adapt-workflow.md) before creating or editing consumer-facing projections.
- Read [references/module-boundaries.md](references/module-boundaries.md) before adding `audit` or `normalize` behavior to this skill package.
- Use the scripts in `scripts/` before hand-authoring deterministic adapter JSON.
