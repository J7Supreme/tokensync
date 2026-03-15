# Adapt Workflow

Use this reference for consumer targeting, output strategy, and common adaptation decisions.

## Common source artifacts

Typical inputs include:

- a canonical token source such as `source/tokens.json`
- a PRD or architecture document
- component contract definitions
- responsive or adaptive rules
- generated consumer outputs in `adapters/`, `exports/`, or similar folders

Do not assume exact paths. Discover the real structure first.

## Common target consumers

### AI or PM-facing schema

Best when the target needs:

- semantic intent
- preferred components or patterns
- guidance for generation
- enough structure to support prompt-driven prototyping

### Design or Figma-facing schema

Best when the target needs:

- variable-friendly naming
- clear modes or collections
- stable grouping for designers
- an output that mirrors reusable patterns and components

### Vercel or runtime-facing schema

Best when the target needs:

- deterministic keys
- implementation-friendly shape
- explicit theme or mode handling
- a clean bridge into frontend code, design tokens tooling, or build pipelines

## Edit policy

- Prefer source-first edits when the system meaning changes.
- Prefer output-first edits only when the request is explicitly consumer-specific.
- Update documentation when the public contract or workflow changes.
- Keep publishable files repo-relative and portable.

## Common task mapping

- Source model issue: confirm the canonical source and architecture doc first.
- Consumer schema issue: confirm the target consumer and what shape it actually needs.
- Publishing issue: remove project-specific naming and path assumptions.
- Workflow issue: clarify which artifacts are authored and which are generated.

## Handoff rule

After adapting a system, make the status explicit:

- what remained the source of truth
- what was adapted for a specific consumer
- whether regeneration or further syncing is still required
