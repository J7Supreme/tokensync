# AI, Figma, and Design System Workflow

## Core recommendation

The most effective setup is not to choose between the Figma design file and adapter-generated JSON schemas. They should work as three coordinated layers:

1. `Figma design file`
2. `source tokens / source design-system schema`
3. `adapter outputs`

Each layer serves a different stage of design, AI generation, and handoff.

## Positioning

This workflow describes DSSkillV2 as a source-first design-system operating model.

It is designed to keep one canonical schema aligned across:

- AI prototype generation
- Figma-based design workflows
- runtime implementation

In practice, it is not just a token repository. It is a shared translation layer between product intent, design artifacts, and engineering outputs.

## Recommended layering

### 1. Figma design file

This is the visual source of truth for the design working session.

It should contain:

- components
- variables
- styles
- layout
- interaction details
- design notes when needed

Its main use is:

- design work
- visual review
- developer handoff
- validating actual visual output

### 2. Source tokens / source design-system schema

This should be the system source of truth.

It should contain:

- complete tokens
- component contracts
- structured semantics
- usage rules
- AI-oriented metadata

Its main use is:

- generating adapters
- AI consumption
- code generation
- linting and governance
- keeping all downstream outputs aligned

This is the layer that should be treated as the real Single Source of Truth.

### 3. Adapter outputs

Adapters are consumer-specific projections of the source schema.

Examples:

- `figma adapter`: for Figma import
- `ai-native adapter`: for agents and prompt pipelines
- `runtime adapter`: for code and theme systems

Adapters should be generated, not manually edited.

## Primary users

### PM

PMs primarily use the AI-friendly schema as structured input for prototype generation.

Typical use:

- define goals in product language
- generate prototypes from natural-language requirements
- explore feature directions without rebuilding token and component assumptions each time

What PMs get:

- faster prototype generation
- more consistent AI outputs
- less ambiguity between PRD language and UI structure

### UX

UX uses the workflow in two main ways:

1. maintain and evolve the design system
2. apply the same system to Figma designs and AI-generated prototypes

Typical use:

- update token definitions, naming, and structure
- map design intent into Figma-compatible and AI-compatible forms
- validate token changes against design files and prototype outputs
- audit Figma files for design-system and quality issues

What UX gets:

- a better DS maintenance workflow
- a clearer bridge between token definitions and design artifacts
- more reliable reuse of system rules in Figma and AI-assisted design work

### DEV

Developers use the workflow to translate the shared system into runtime-friendly outputs.

Typical use:

- consume or generate schemas that are easier to use in application code and pipelines
- adapt the same token source into runtime-safe formats
- keep implementation aligned with the canonical token source instead of hand-maintaining parallel definitions

What DEV gets:

- a cleaner integration path from design tokens to runtime
- reduced schema drift
- better consistency between source, adapters, and shipped UI

## Core principle

- The `Figma file` should not carry the full AI-native semantic system.
- The `adapter` should not become the source of truth.
- The actual source of truth should live in the `source` layer.
- Both Figma and AI should consume different projections of that same source.

## Best fit by scenario

### 1. Designer uses a tokenized Figma file and asks AI to generate high-fidelity demo designs

Best input combination:

- `Figma file` as visual context
- `AI-native adapter` as semantic and system context
- optional `figma token adapter` for variable mapping validation

Why:

- Figma tells the AI what the current system looks like
- the AI-native adapter tells the AI why tokens and components exist and how they should be used
- Figma variable names alone are not enough
- JSON alone does not provide the full visual situation

Recommended workflow:

1. AI reads Figma nodes or design context
2. AI reads the AI-native schema
3. AI generates by preferring reusable components and patterns first, semantic tokens second, and primitive values last

### 2. Designer hands off the same Figma file to developers

Best input combination:

- `Figma file` as the primary handoff artifact
- `runtime/code adapter` as the implementation artifact
- `source tokens` for auditability and traceability

Why:

- handoff is still centered on the Figma file
- developers need an implementation-friendly token and component mapping
- adapters should prevent engineers from manually copying visual values

Recommended workflow:

1. Designer completes the Figma handoff file
2. Developer uses Figma for visual and structural confirmation
3. Developer uses the runtime adapter for stable token paths, component mappings, and theme logic

### 3. Designer uses natural language during exploration to ask AI for prototypes

Best input combination:

- `AI-native adapter` as the primary input
- Figma is optional, or used only as a reference library

Why:

- the goal is not to reproduce an existing design file
- the goal is to explore within design-system boundaries
- the most important inputs are token intent, component contract, pattern usage, and brand rules

Recommended workflow:

1. Feed the AI-native schema first
2. Provide task goals, page type, and user scenario
3. Generate the prototype
4. Align the result back to Figma variables and components if needed

### 4. Product uses natural language during exploration to ask AI for prototypes

Best input combination:

- `AI-native adapter` as the primary system input
- an additional product-facing schema or prompt layer
- Figma is usually not the first input

Why:

- product users usually do not think in token or component language
- AI has to translate business intent into system-compliant design decisions
- this is where structured semantics become especially valuable

Recommended workflow:

1. Product provides goals, user type, content blocks, and rough intent
2. AI reads the AI-native schema
3. AI outputs low- to mid-fidelity prototypes or constrained high-fidelity drafts
4. Designers refine the result in Figma afterward

## Recommended file responsibilities

### Figma design file

Use for:

- visual design
- variables
- component instances
- layouts
- handoff context

Do not use it as the only storage for full AI semantics.

### `source/tokens.json`

Use for:

- primitive
- semantic
- pattern
- component
- `$description`
- structured metadata such as `intent`, `usage`, `forbiddenUsage`, `state`, `preferredComponent`, and `contentType`

This should be the root source.

### Figma adapter

Goal:

- stable import into Figma

Keep:

- name
- description
- modes
- collection grouping
- publish and hide behavior

Do not force it to carry every AI-only metadata field.

### AI-native adapter

Goal:

- help models make design-system decisions

Keep:

- full structured semantics
- reusable component relationships
- slot, prop, and state information
- page and pattern rules
- guidance that encourages reuse over inventing new UI

### Runtime/code adapter

Goal:

- support implementation

Keep:

- token paths
- theme modes
- component mappings
- engineering-friendly naming and structure

## Most important design decision

If only one layer can be the true source of truth, it should be the `source schema`, not the Figma file and not an adapter.

Why:

- Figma is strong at editing and presentation, but not as a full machine-readable semantic store
- adapters are projections, not sources
- both AI systems and code generation need more stable structure than Figma alone provides

## Practical summary

- Use Figma for the design working surface
- Use the source schema as the system truth
- Use adapters as tailored outputs for Figma, AI, and runtime consumers

## Suggested workflow by role

### PM workflow

1. Start from product intent, feature requirements, or prototype goals.
2. Use the AI-friendly schema as the primary structured input.
3. Generate prototype concepts from that schema.
4. Hand off the result to UX for design-system alignment and refinement.

### UX workflow

1. Maintain the source token model and design-system structure.
2. Refine or complete token definitions in the source layer.
3. Generate the adapter outputs needed for Figma or AI usage.
4. Audit Figma files for design-system consistency and design quality.
5. Feed improvements back into the source model.

### DEV workflow

1. Start from the canonical source and generated schema outputs.
2. Use the runtime-oriented adapter as the implementation input.
3. Integrate the output into application or platform code.
4. Keep implementation aligned with source-of-truth updates rather than patching downstream outputs by hand.

## Collaboration model

The intended collaboration model is:

- PM defines intent and uses the AI-friendly schema for prototyping
- UX governs and evolves the design system while applying it to design artifacts and prototypes
- DEV converts the same system into runtime-friendly schema and implementation outputs

This keeps product, design, and engineering working from the same source model, with different adapters for different jobs.

## One-line workflow summary

Design work happens in Figma, system truth lives in the source schema, and every downstream consumer should receive the adapter best suited to its job.
