# Figma DS Review Proposal

Date: 2026-03-14

Figma scope: `Webapp-design-system` page node `321:9714` (`📦 设计组件和定义`)

Source of truth checked:

- `source/tokens.json`
- `adapters/figma/figma_tokens_adaptive.json`
- `prd_v1.md`

## 1. Current repository gap

The repository token source is structurally incomplete relative to the PRD.

- `Primitive` currently contains only `primitive.color.*`
- `Light` and `Dark` currently contain only `semantic.*`
- `pattern.*` is missing entirely
- `component.*` is missing entirely

This means the current source cannot represent the component contracts already implied by the Figma DS page.

## 2. Non-compliant definitions found in Figma

The Figma page already contains stable component examples, but many are not normalized into a token-friendly component contract.

### 2.1 Naming issues

- Variant axes are inconsistent and too generic: `Property 1=Default`, `Property 1=Expand`, `Property 1=Signed in`, `Property 1=Not signed in`, `Property 1=Token main scroll`, `Level=Default`, `Level=2nd nav`, `Status=Unsigned in`, `Status=Signed in`
- Internal layers use non-semantic names: `Frame 2087326813`, `Group 1321319297`, `Rectangle 24593`, `Rectangle 24115`, `Rectangle 24117`
- Some example containers are mixed into component naming: `Token main`, `Web Token Main`, `Header cover`

These names do not map cleanly to the PRD path rules:

- `pattern.<patternGroup>.<patternName>.<property>`
- `component.<component>.<variant>.<state>.<property>`

### 2.2 Stable components/patterns already visible

The following are stable enough to normalize:

- `Mobile nav`
- `Web nav`
- `Nav`
- `Token list`
- `Menu`
- `Modal`
- `Button`
- card-like surfaces used in `Info cards`, `Price card`, `Collection card`, `Market info`, `Recent activity`

### 2.3 Evidence from geometry

Observed repeated structural values on the Figma page:

- container widths: `343`, `356`, `375`, `1200`
- heights: `24`, `32`, `44`, `48`, `52`, `56`, `64`, `68`, `90`
- offsets / padding / gaps: `4`, `8`, `12`, `16`, `20`, `24`, `32`, `40`, `42`, `72`
- icon sizes: `16`, `20`, `24`, `32`, `40`

Safe conclusion: the DS already has an implicit scale, but it has not been formalized into primitive tokens.

## 3. Primitive proposal

Per PRD, primitives should contain foundational scales. The following groups should be added.

### 3.1 Safe to add now from visible geometry

These values are directly evidenced by node sizes or offsets and can be proposed without guessing intent.

```text
primitive.spacing.4
primitive.spacing.8
primitive.spacing.12
primitive.spacing.16
primitive.spacing.20
primitive.spacing.24
primitive.spacing.32
primitive.spacing.40
primitive.spacing.42
primitive.spacing.72

primitive.size.4
primitive.size.16
primitive.size.20
primitive.size.24
primitive.size.32
primitive.size.36
primitive.size.40
primitive.size.44
primitive.size.48
primitive.size.52
primitive.size.56
primitive.size.62
primitive.size.64
primitive.size.68
primitive.size.90
primitive.size.343
primitive.size.356
primitive.size.375
primitive.size.1200
```

Recommendation:

- keep `spacing.*` only for actual layout spacing
- keep `size.*` for control height, icon size, and canonical container width
- do not overload `spacing` with component heights

### 3.2 Must be added, but values are not safe to infer from metadata alone

These groups are required by your stated goal and the PRD, but current Figma metadata access did not expose the exact values.

```text
primitive.radius.sm = [MISSING]
primitive.radius.md = [MISSING]
primitive.radius.lg = [MISSING]
primitive.radius.full = [MISSING]

primitive.typography.family.sans = [MISSING]
primitive.typography.weight.regular = [MISSING]
primitive.typography.weight.medium = [MISSING]
primitive.typography.weight.semibold = [MISSING]
primitive.typography.weight.bold = [MISSING]

primitive.typography.size.xs = [MISSING]
primitive.typography.size.sm = [MISSING]
primitive.typography.size.md = [MISSING]
primitive.typography.size.lg = [MISSING]
primitive.typography.size.xl = [MISSING]
primitive.typography.lineHeight.xs = [MISSING]
primitive.typography.lineHeight.sm = [MISSING]
primitive.typography.lineHeight.md = [MISSING]
primitive.typography.lineHeight.lg = [MISSING]
primitive.typography.lineHeight.xl = [MISSING]
```

Reason:

- `get_metadata` returns bounds and hierarchy, but not font family, font weight, letter spacing, or corner radius values
- current `get_design_context` / `get_variable_defs` access was blocked by Figma selection state, so these values should not be guessed into SSOT

### 3.3 Other primitive groups worth adding

These appear structurally useful given the page content and PRD, but should be confirmed before writing values:

```text
primitive.border.width.sm = [MISSING]
primitive.shadow.sm = [MISSING]
primitive.shadow.md = [MISSING]
```

## 4. Proposed pattern layer

These are the clearest reusable content/composition patterns visible from the DS page.

### 4.1 Surface card pattern

```text
pattern.surface.card.background -> {semantic.background.card}
pattern.surface.card.title -> {semantic.text.primary}
pattern.surface.card.body -> {semantic.text.secondary}
pattern.surface.card.padding -> {primitive.spacing.16}
pattern.surface.card.radius -> {primitive.radius.md}
```

Why:

- repeated across `Info cards`, `Price card`, `Collection card`, `Market info`, `Recent activity`

### 4.2 Modal content pattern

```text
pattern.modal.form.title -> {semantic.text.primary}
pattern.modal.form.body -> {semantic.text.secondary}
pattern.modal.form.fieldBackground -> {semantic.background.modal_section}
pattern.modal.form.fieldPaddingX -> {primitive.spacing.12}
pattern.modal.form.fieldHeight -> {primitive.size.48}
pattern.modal.form.sectionGap -> {primitive.spacing.32}
pattern.modal.form.actionGap -> {primitive.spacing.32}
```

Why:

- repeated in modal examples with title, content area, field, CTA

### 4.3 Token/list item pattern

```text
pattern.list.tokenItem.text -> {semantic.text.primary}
pattern.list.tokenItem.subtext -> {semantic.text.secondary}
pattern.list.tokenItem.iconSize -> {primitive.size.40}
pattern.list.tokenItem.gap -> {primitive.spacing.12}
pattern.list.tokenItem.height -> {primitive.size.62} [REVIEW]
```

Note:

- item height is visually implied on web token list, but the exact canonical token should be reviewed before writing because `62` was observed only in example rows

### 4.4 Status row pattern

```text
pattern.list.statusRow.title -> {semantic.text.primary}
pattern.list.statusRow.meta -> {semantic.text.secondary}
pattern.list.statusRow.iconSize -> {primitive.size.20}
pattern.list.statusRow.rowGap -> {primitive.spacing.8}
pattern.list.statusRow.paddingY -> {primitive.spacing.16}
```

Why:

- repeated in `Menu` examples and status/info rows

## 5. Proposed component layer

These should be created as the first batch of normalized component contracts.

### 5.1 Mobile nav

```text
component.mobileNav.primary.default.height -> {primitive.size.90}
component.mobileNav.primary.default.paddingX -> {primitive.spacing.16}
component.mobileNav.primary.default.title -> {semantic.text.primary}
component.mobileNav.primary.default.icon -> {semantic.stroke.icon_primary}

component.mobileNav.secondary.default.height -> {primitive.size.56}
component.mobileNav.secondary.default.paddingX -> {primitive.spacing.16}
component.mobileNav.secondary.default.title -> {semantic.text.primary}
component.mobileNav.secondary.default.icon -> {semantic.stroke.icon_primary}
```

Source evidence:

- `Level=Default` width `375` height `90`
- `Level=2nd nav` width `375` height `56`

### 5.2 Web nav

```text
component.webNav.default.signedOut.height -> {primitive.size.68}
component.webNav.default.signedIn.height -> {primitive.size.68}
component.webNav.default.default.background -> {semantic.background.general}
component.webNav.default.default.title -> {semantic.text.primary}
component.webNav.default.default.icon -> {semantic.stroke.icon_primary}
component.webNav.default.default.border -> {semantic.border.default}
```

Review note:

- state naming should be normalized from `Unsigned in` to `signedOut`

### 5.3 Modal

```text
component.modal.default.default.background -> {semantic.background.modal}
component.modal.default.default.title -> {semantic.text.primary}
component.modal.default.default.body -> {semantic.text.secondary}
component.modal.default.default.paddingX -> {primitive.spacing.16}
component.modal.default.default.paddingTop -> {primitive.spacing.8}
component.modal.default.default.contentTopGap -> {primitive.spacing.72}
component.modal.default.default.closeButtonSize -> {primitive.size.32}
component.modal.default.default.dragHandleWidth -> {primitive.size.36} [REVIEW]
component.modal.default.default.dragHandleHeight -> {primitive.size.4}
component.modal.default.default.radius -> {primitive.radius.lg}
```

Source evidence:

- modal frame width `375`
- top block width `343` height `44`
- drag handle width `36` height `4`
- close control `32`
- content begins at `y=72`

### 5.4 Button

```text
component.button.primary.default.height -> {primitive.size.52}
component.button.primary.default.paddingX -> {primitive.spacing.16}
component.button.primary.default.background -> {semantic.fill.secondary}
component.button.primary.default.text -> {semantic.text.action} [REVIEW]
component.button.primary.default.radius -> {primitive.radius.md}
```

Review note:

- text color alias is not safe yet; this depends on whether the button is filled dark or brand-blue in the real component master

### 5.5 Menu

```text
component.menu.default.signedOut.background -> {semantic.background.card}
component.menu.default.signedIn.background -> {semantic.background.card}
component.menu.default.default.title -> {semantic.text.primary}
component.menu.default.default.body -> {semantic.text.secondary}
component.menu.default.default.padding -> {primitive.spacing.16}
```

### 5.6 Token list

```text
component.tokenList.default.default.height -> {primitive.size.32}
component.tokenList.default.default.text -> {semantic.text.primary}
component.tokenList.default.default.icon -> {semantic.stroke.icon_primary}

component.tokenList.expand.default.height -> {primitive.size.32}
component.tokenList.expand.default.text -> {semantic.text.primary}
component.tokenList.expand.default.icon -> {semantic.stroke.icon_primary}
```

Review note:

- rename variant axis from `Property 1` to `variant`
- rename `Expand` to `expanded`

## 6. Renaming normalization proposal

Before writing any token back, the following Figma naming normalization is recommended.

```text
Property 1=Default           -> variant=default
Property 1=Expand            -> variant=expanded
Property 1=Signed in         -> state=signedIn
Property 1=Not signed in     -> state=signedOut
Property 1=Token main scroll -> state=scrolled
Level=Default                -> variant=primary
Level=2nd nav                -> variant=secondary
Status=Unsigned in           -> state=signedOut
Status=Signed in             -> state=signedIn
```

Internal anonymous layers should also be renamed if they are meant to remain part of the authored component structure:

```text
Frame 2087326813 -> modal.header
Frame 2087326815 -> modal.headerTitle
Group 1321319297 -> modal.closeButton
Rectangle 24593  -> modal.dragHandle
Rectangle 24115  -> nav.centerAction
Rectangle 24117  -> nav.iconButtonBackground
```

## 7. Review gates before write-back

I recommend reviewing these decisions before I touch `source/tokens.json`:

1. Whether `primitive.size.*` should include canonical container widths such as `343`, `356`, `375`, `1200`, or whether those should live under `primitive.container.*`
2. Whether button text should alias `semantic.text.action`, `semantic.text.primary`, or a new semantic token such as `semantic.text.onFill`
3. Whether modal and button radii should use shared radius tokens or component-specific values
4. Whether typography should be added now as `[MISSING]` placeholders in source, or postponed until exact Figma font values can be extracted
5. Whether `Menu` should be treated as a first-class component or as a pattern built from card/list primitives

### Review resolution

The review decisions are resolved as follows:

1. Keep canonical container widths under `primitive.size.*`; do not introduce `primitive.container.*`
2. Use `semantic.text.action` for button text
3. Treat radius as a shared primitive scale via `primitive.radius.*`
4. Keep unverifiable typography values as `[MISSING]` in the review process and do not infer write-back values
5. Treat `Menu` as a first-class `component`

## 8. Recommended next action

After review approval, the safest implementation order is:

1. Add missing primitive groups and mark uncertain values as `[MISSING]` or hold them back
2. Add `pattern.*` paths with alias-only values
3. Add `component.*` paths with alias-only values
4. Generate a diff for your review before syncing to Figma adapters
