# Design System Adapt

Publishable skill package for adapting one canonical design-system model into AI, Figma, and runtime-facing outputs.

## Visual architecture

Open [docs/token-visual-architecture.html](docs/token-visual-architecture.html) for a visual explanation of the token structure defined in [prd_v1.md](prd_v1.md) and [source/tokens.json](source/tokens.json).

## Skill package

- Skill folder: `design-system-adapt/`
- Install guide: [docs/INSTALL_DESIGN_SYSTEM_ADAPT.md](docs/INSTALL_DESIGN_SYSTEM_ADAPT.md)
- Packaged zip: `docs/design-system-adapt-skill-package.zip`
- Invocation: `$design-system-adapt`

## Scope

The current public module is `adapt`.

- It translates a canonical design-system source into deterministic AI, Figma, and runtime adapter outputs.
- It includes bundled builder scripts for strict output contracts and plugin-facing import shapes.
- It keeps `audit` and `normalize` as explicit future extensions rather than mixing them into the current public contract.
