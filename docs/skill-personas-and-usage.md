# DSSkillV2 Personas And Usage

This document explains who DSSkillV2 is for, how each role uses it, and what its core capabilities are.

## Positioning

DSSkillV2 is a design-token and schema workflow centered on one canonical source of truth. It helps teams translate the same system into outputs that are friendly to:

- AI prototype generation
- Figma-based design workflows
- Runtime implementation

In practice, the skill can be used as an AI-friendly schema layer that keeps product, design, and engineering aligned around the same token model and adapter logic.

## Primary Users

### PM

PMs primarily use DSSkillV2 as a structured input for prototype generation.

Typical usage:

- Use the skill, or more precisely the AI-friendly schema it produces, to generate product prototypes from natural-language requirements.
- Define intent in product language while relying on the schema to keep outputs aligned with the design system.
- Explore feature directions quickly without manually rebuilding the same token and component assumptions each time.

What PMs get from it:

- Faster prototype generation
- More consistent AI outputs
- Less ambiguity between PRD language and UI structure

### UX

UX uses DSSkillV2 in two main ways:

1. Maintain and evolve the design system.
2. Apply the skill to Figma designs and AI-generated prototypes.

Typical usage:

- Update token definitions, naming, and structure so the design system stays coherent.
- Use the skill to map design intent into Figma-compatible and AI-compatible structures.
- Apply or validate token changes against design files and prototype outputs.
- Use the audit capability to evaluate Figma files from a design-quality perspective.

What UX gets from it:

- Better DS maintenance workflow
- A clearer bridge between token definitions and design artifacts
- More reliable reuse of system rules in Figma and AI-assisted design work

### DEV

Developers use DSSkillV2 to translate the shared system into runtime-friendly schema and implementation-facing outputs.

Typical usage:

- Consume or generate schemas that are easier to use in application code and pipelines.
- Adapt the same token source into runtime-safe formats for frontend or platform integration.
- Keep implementation outputs aligned with the canonical token source instead of hand-maintaining multiple parallel definitions.

What DEV gets from it:

- Cleaner integration path from design tokens to runtime
- Reduced schema drift
- Better consistency between source, adapters, and shipped UI

## Core Capabilities

### optimize

`optimize` updates or completes token definitions based on:

- Natural-language input
- Figma design files

Use it when token coverage is incomplete, naming is inconsistent, or the system needs refinement based on new requirements or design changes.

### adapt

`adapt` generates the schema shape needed by a specific role or consumer.

Examples:

- PM-facing AI-friendly schema for prototype generation
- UX-facing schema for design-system and Figma workflows
- DEV-facing runtime-friendly schema for implementation

Use it when the same source model needs to be expressed differently for different collaborators or systems.

### audit

`audit` evaluates a Figma file from a design perspective only.

Use it when UX or design-system owners need to review:

- token consistency
- design-system alignment
- structural gaps in the design
- overall design quality signals visible in the Figma file

This capability is intentionally Figma-based and design-oriented, rather than runtime- or code-oriented.

## Suggested Workflow By Role

### PM workflow

1. Start from product intent, feature requirements, or prototype goals.
2. Use DSSkillV2 to generate or adapt an AI-friendly schema.
3. Generate prototype concepts from that schema.
4. Hand off the result to UX for design-system alignment and refinement.

### UX workflow

1. Maintain the source token model and DS structure.
2. Use `optimize` to refine or fill token definitions.
3. Use `adapt` to prepare schema outputs for Figma or AI prototype usage.
4. Use `audit` on Figma files to identify design-system or quality issues.
5. Feed improvements back into the source model.

### DEV workflow

1. Start from the canonical source and existing schema outputs.
2. Use `adapt` to produce runtime-friendly schema.
3. Integrate the output into application or platform code.
4. Keep implementation aligned with source-of-truth updates rather than patching downstream outputs by hand.

## Collaboration Model

The intended collaboration model is:

- PM defines intent and uses AI-friendly schema for prototyping.
- UX governs and evolves the design system, while applying the skill to design artifacts and prototypes.
- DEV converts the same system into runtime-friendly schema and implementation outputs.

This makes DSSkillV2 not just a token repository workflow, but a shared translation layer across product, design, and engineering.
