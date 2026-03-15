# System Model

Use this reference for source-of-truth decisions, token taxonomy, semantic structure, and adaptive architecture language.

## Core model

- The design system should have one canonical model.
- A common source artifact is `source/tokens.json`, but always confirm the real project structure first.
- Downstream schemas, adapters, and consumer exports are projections of that model, not the design authority.

## Four system views

The base model uses four views:

- `primitive`
- `semantic`
- `pattern`
- `component`

These are parallel ways to organize one system. They are not a mandatory serial pipeline.

## Intended meaning

- `primitive`: foundational visual scales such as color, spacing, radius, size, and shadow.
- `semantic`: UI-role meaning such as text, background, border, icon, or fill usage.
- `pattern`: reusable structure or composition patterns such as surfaces, containers, shells, lists, or layouts.
- `component`: concrete component bindings for variants, states, slots, and final consumable properties.

## Relationship rules

- `semantic` commonly references `primitive`.
- `pattern` and `component` are peers.
- `pattern` and `component` should prefer `semantic.*` for role-based styling.
- `pattern` and `component` may directly reference `primitive.*` for structural values.
- `semantic` answers: "what role does this UI value represent?"
- `component` answers: "what does this component variant or state use?"
- `pattern` answers: "what reusable structure or arrangement is being expressed?"

## Adaptive system rule

Adapting the system means changing how the model is expressed for a consumer, not redefining the model itself.

Examples:

- AI-facing outputs may keep richer guidance, descriptions, and preferred reuse signals.
- Design-facing outputs may prioritize theme parity, naming clarity, and variable grouping.
- Runtime-facing outputs may prioritize deterministic keys, implementation-safe shapes, and code-friendly structure.

## Architecture flow

Preferred direction:

1. Update the canonical model or its governing documentation.
2. Resolve references, validate naming, and preserve mode parity.
3. Build or update consumer-specific projections.
4. Sync projections to design, AI, or runtime consumers as needed.

## Documentation rules

- Keep language aligned with the existing PRD or architecture document.
- Do not describe Figma or any generated export as the source of truth.
- Do not flatten the four-view model into a simpler but inaccurate hierarchy.
- Avoid absolute local links in any publishable markdown.
