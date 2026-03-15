# Roadmap

## Source Token Semantic Metadata

### Status

Deferred for now.

### Why it matters

The current `source/tokens.json` already carries naming structure and `$description`, which is enough to support the current Figma adapter, runtime adapter, and initial AI adapter workflow.

However, richer structured semantics in the source layer would improve AI reasoning and design-system application quality, especially for:

- token intent understanding
- correct token selection in generation workflows
- avoiding misuse across components and UI contexts
- component reconstruction and reuse decisions

### Candidate future fields

Possible future additions to non-primitive layers:

- `intent`
- `usage`
- `forbiddenUsage`
- `preferredComponent`
- `contentType`
- `hierarchy`

These should be evaluated carefully before adoption to avoid creating maintenance overhead without enough practical value.

### Recommended rollout approach

If this work starts later, the preferred order is:

1. Add a minimal field set first.
2. Start with `semantic` and `component`, not `primitive`.
3. Validate whether AI output quality actually improves.
4. Only then expand to broader structured metadata coverage.

### Constraint

The source token file should remain the single source of truth. Any future semantic metadata should be authored in `source/tokens.json` first, then propagated into AI-facing adapters as needed, rather than being invented separately in downstream adapter files.

## Figma Export Normalization

### Status

Planned as a future `dsskillv2` capability, not part of the current default workflow.

### Positioning

`dsskillv2` itself remains a usable standalone capability for working with the token source-of-truth system.

Over time, it is expected to include and package three adjacent abilities together:

- `audit`
- `normalize`
- `adapt`

Within that direction, Figma export normalization belongs primarily to the `normalize` capability, and can later be bundled with `audit` for migration review and quality checks.

### Summary

The current repository is source-first:

- `source/tokens.json` is the canonical source.
- Figma-oriented files are adapters or import payloads.
- The supported sync direction is source to adapters to consumers.

There is currently no formal, general-purpose workflow that converts an existing Figma-exported JSON back into the canonical `source/tokens.json` structure.

What exists today is only a limited precedent:

- a one-off refactor path for older token JSON shapes
- manual mapping from legacy group names into canonical semantic paths
- heuristic reconstruction of primitive aliases from hard-coded exported values

That means reverse generation is currently better understood as a normalization or migration task, not as a stable part of the normal token pipeline.

### Why this should live under `normalize`

A Figma export usually reflects consumer-side structure and raw resolved values, but the canonical source model requires stronger design-system intent:

- canonical primitive naming
- semantic alias preservation
- Light and Dark path parity
- pattern and component layer structure
- retained descriptions and governance metadata

Those requirements are not reliably recoverable from exported Figma JSON without normalization rules and human review.

### Recommended future scope

If this is implemented later, the feature should be framed as:

- input: existing Figma-exported token JSON
- output: a best-effort canonical source token draft
- guarantees: structure normalization, path remapping, alias reconstruction where possible, and explicit flags for anything that still needs manual review

It should not be positioned as a lossless round-trip compiler from Figma back into source.

### Packaging recommendation

Recommended future packaging inside `dsskillv2`:

1. `normalize`: convert legacy or exported token JSON into canonical source structure
2. `audit`: detect drift, missing descriptions, broken parity, unresolved aliases, and schema gaps after normalization
3. `adapt`: help reshape the normalized source for downstream consumer formats and future usage contexts without breaking the source-first model

### Constraint

Even after this capability is added, the governance rule should remain unchanged:

- Figma is not the source of truth.
- Reverse import should be treated as bootstrap, recovery, or migration support.
- Ongoing design-token maintenance should still happen in `source/tokens.json` first.
