# Key Figma Skill Explanation

## Structure

This document consolidates the full on-disk `SKILL.md` content for the key Figma-related global skills requested for this workspace.

Included source files:

1. `/Users/jameshou/.agents/skills/figma-generate-design/SKILL.md`
2. `/Users/jameshou/.agents/skills/figma-generate-library/SKILL.md`
3. `/Users/jameshou/.agents/skills/audit-design-system/SKILL.md`
4. `/Users/jameshou/.agents/skills/apply-design-system/SKILL.md`
5. `/Users/jameshou/.agents/skills/rad-spacing/SKILL.md`
6. `/Users/jameshou/.agents/skills/sync-figma-token/SKILL.md`
7. `/Users/jameshou/.agents/skills/edit-figma-design/SKILL.md`

## Current Condition

All seven requested global skill files were located successfully and merged into this root-level reference.

## Recommended Next Move

Use this file as the single local briefing document when planning Figma generation, library-building, design-system auditing, design-system application, spacing normalization, token sync, or direct Figma authoring work in this repo.

---

## figma-generate-design

Source: `/Users/jameshou/.agents/skills/figma-generate-design/SKILL.md`

```md
---
name: figma-generate-design
description: "Use this skill alongside figma-use when the task involves translating an application page, view, or multi-section layout into Figma. Triggers: 'write to Figma', 'create in Figma from code', 'push page to Figma', 'take this app/page and build it in Figma', 'create a screen', 'build a landing page in Figma', 'update the Figma screen to match code'. This is the preferred workflow skill whenever the user wants to build or update a full page, screen, or view in Figma from code or a description. Discovers design system components, variables, and styles via search_design_system, imports them, and assembles screens incrementally section-by-section using design system tokens instead of hardcoded values."
disable-model-invocation: false
---

# Build / Update Screens from Design System

Use this skill to create or update full-page screens in Figma by **reusing the published design system** — components, variables, and styles — rather than drawing primitives with hardcoded values. The key insight: the Figma file likely has a published design system with components, color/spacing variables, and text/effect styles that correspond to the codebase's UI components and tokens. Find and use those instead of drawing boxes with hex colors.

**MANDATORY**: You MUST also load [figma-use](../figma-use/SKILL.md) before any `use_figma` call. That skill contains critical rules (color ranges, font loading, etc.) that apply to every script you write.

**Always pass `skillNames: "figma-generate-design"` when calling `use_figma` as part of this skill.** This is a logging parameter — it does not affect execution.

## Skill Boundaries

- Use this skill when the deliverable is a **Figma screen** (new or updated) composed of design system component instances.
- If the user wants to generate **code from a Figma design**, switch to [figma-implement-design](../figma-implement-design/SKILL.md).
- If the user wants to create **new reusable components or variants**, use [figma-use](../figma-use/SKILL.md) directly.
- If the user wants to write **Code Connect mappings**, switch to [figma-code-connect-components](../figma-code-connect-components/SKILL.md).

## Prerequisites

- Figma MCP server must be connected
- The target Figma file must have a published design system with components (or access to a team library)
- User should provide either:
  - A Figma file URL / file key to work in
  - Or context about which file to target (the agent can discover pages)
- Source code or description of the screen to build/update

## Parallel Workflow with generate_figma_design (Web Apps Only)

When building a screen from a **web app** that can be rendered in a browser, the best results come from running both approaches in parallel:

1. **In parallel:**
   - Start building the screen using this skill's workflow (use_figma + design system components)
   - Run `generate_figma_design` to capture a pixel-perfect screenshot of the running web app
2. **Once both complete:** Update the use_figma output to match the pixel-perfect layout from the `generate_figma_design` capture. The capture provides the exact spacing, sizing, and visual treatment to aim for, while your use_figma output has proper component instances linked to the design system.
3. **Once confirmed looking good:** Delete the `generate_figma_design` output — it was only used as a visual reference.

This combines the best of both: `generate_figma_design` gives pixel-perfect layout accuracy, while use_figma gives proper design system component instances that stay linked and updatable.

**This workflow only applies to web apps** where `generate_figma_design` can capture the running page. For non-web apps (iOS, Android, etc.) or when updating existing screens, use the standard workflow below.

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 1: Understand the Screen

Before touching Figma, understand what you're building:

1. If building from code, read the relevant source files to understand the page structure, sections, and which components are used.
2. Identify the major sections of the screen (e.g., Header, Hero, Content Panels, Pricing Grid, FAQ Accordion, Footer).
3. For each section, list the UI components involved (buttons, inputs, cards, navigation pills, accordions, etc.).

### Step 2: Discover Design System — Components, Variables, and Styles

You need three things from the design system: **components** (buttons, cards, etc.), **variables** (colors, spacing, radii), and **styles** (text styles, effect styles like shadows). Don't hardcode hex colors or pixel values when design system tokens exist.

#### 2a: Discover components

**Preferred: inspect existing screens first.** If the target file already contains screens using the same design system, skip `search_design_system` and inspect existing instances directly. A single `use_figma` call that walks an existing frame's instances gives you an exact, authoritative component map:

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const uniqueSets = new Map();
frame.findAll(n => n.type === "INSTANCE").forEach(inst => {
  const mc = inst.mainComponent;
  const cs = mc?.parent?.type === "COMPONENT_SET" ? mc.parent : null;
  const key = cs ? cs.key : mc?.key;
  const name = cs ? cs.name : mc?.name;
  if (key && !uniqueSets.has(key)) {
    uniqueSets.set(key, { name, key, isSet: !!cs, sampleVariant: mc.name });
  }
});
return [...uniqueSets.values()];
```

Only fall back to `search_design_system` when the file has no existing screens to reference. When using it, **search broadly** — try multiple terms and synonyms (e.g., "button", "input", "nav", "card", "accordion", "header", "footer", "tag", "avatar", "toggle", "icon", etc.). Use `includeComponents: true` to focus on components.

**Include component properties** in your map — you need to know which TEXT properties each component exposes for text overrides. Create a temporary instance, read its `componentProperties` (and those of nested instances), then remove the temp instance.

Example component map with property info:

```text
Component Map:
- Button → key: "abc123", type: COMPONENT_SET
  Properties: { "Label#2:0": TEXT, "Has Icon#4:64": BOOLEAN }
- PricingCard → key: "ghi789", type: COMPONENT_SET
  Properties: { "Device": VARIANT, "Variant": VARIANT }
  Nested "Text Heading" has: { "Text#2104:5": TEXT }
  Nested "Button" has: { "Label#2:0": TEXT }
```

#### 2b: Discover variables (colors, spacing, radii)

**Inspect existing screens first** (same as components). Or use `search_design_system` with `includeVariables: true`.

> **WARNING: Two different variable discovery methods — do not confuse them.**
>
> - `use_figma` with `figma.variables.getLocalVariableCollectionsAsync()` — returns **only local variables defined in the current file**. If this returns empty, it does **not** mean no variables exist. Remote/published library variables are invisible to this API.
> - `search_design_system` with `includeVariables: true` — searches across **all linked libraries**, including remote and published ones. This is the correct tool for discovering design system variables.
>
> **Never conclude "no variables exist" based solely on `getLocalVariableCollectionsAsync()` returning empty.** Always also run `search_design_system` with `includeVariables: true` to check for library variables before deciding to create your own.

**Query strategy:** `search_design_system` matches against **variable names** (e.g., "Gray/gray-9", "core/gray/100", "space/400"), not categories. Run multiple short, simple queries in parallel rather than one compound query:

- **Primitive colors:** "gray", "red", "blue", "green", "white", "brand"
- **Semantic colors:** "background", "foreground", "border", "surface", "text"
- **Spacing/sizing:** "space", "radius", "gap", "padding"

If initial searches return empty, try shorter fragments or different naming conventions — libraries vary widely ("grey" vs "gray", "spacing" vs "space", "color/bg" vs "background").

Inspect an existing screen's bound variables for the most authoritative results:

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const varMap = new Map();
frame.findAll(() => true).forEach(node => {
  const bv = node.boundVariables;
  if (!bv) return;
  for (const [prop, binding] of Object.entries(bv)) {
    const bindings = Array.isArray(binding) ? binding : [binding];
    for (const b of bindings) {
      if (b?.id && !varMap.has(b.id)) {
        const v = await figma.variables.getVariableByIdAsync(b.id);
        if (v) varMap.set(b.id, { name: v.name, id: v.id, key: v.key, type: v.resolvedType, remote: v.remote });
      }
    }
  }
});
return [...varMap.values()];
```

For library variables (remote = true), import them by key with `figma.variables.importVariableByKeyAsync(key)`. For local variables, use `figma.variables.getVariableByIdAsync(id)` directly.

See [variable-patterns.md](../figma-use/references/variable-patterns.md) for binding patterns.

#### 2c: Discover styles (text styles, effect styles)

Search for styles using `search_design_system` with `includeStyles: true` and terms like "heading", "body", "shadow", "elevation". Or inspect what an existing screen uses:

```js
const frame = figma.currentPage.findOne(n => n.name === "Existing Screen");
const styles = { text: new Map(), effect: new Map() };
frame.findAll(() => true).forEach(node => {
  if ('textStyleId' in node && node.textStyleId) {
    const s = figma.getStyleById(node.textStyleId);
    if (s) styles.text.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
  if ('effectStyleId' in node && node.effectStyleId) {
    const s = figma.getStyleById(node.effectStyleId);
    if (s) styles.effect.set(s.id, { name: s.name, id: s.id, key: s.key });
  }
});
return {
  textStyles: [...styles.text.values()],
  effectStyles: [...styles.effect.values()]
};
```

Import library styles with `figma.importStyleByKeyAsync(key)`, then apply with `node.textStyleId = style.id` or `node.effectStyleId = style.id`.

See [text-style-patterns.md](../figma-use/references/text-style-patterns.md) and [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md) for details.

### Step 3: Create the Page Wrapper Frame First

**Do NOT build sections as top-level page children and reparent them later** — moving nodes across `use_figma` calls with `appendChild()` silently fails and produces orphaned frames. Instead, create the wrapper first, then build each section directly inside it.

Create the page wrapper in its own `use_figma` call. Position it away from existing content and return its ID:

```js
// Find clear space
let maxX = 0;
for (const child of figma.currentPage.children) {
  maxX = Math.max(maxX, child.x + child.width);
}

const wrapper = figma.createFrame();
wrapper.name = "Homepage";
wrapper.layoutMode = "VERTICAL";
wrapper.primaryAxisAlignItems = "CENTER";
wrapper.counterAxisAlignItems = "CENTER";
wrapper.resize(1440, 100);
wrapper.layoutSizingHorizontal = "FIXED";
wrapper.layoutSizingVertical = "HUG";
wrapper.x = maxX + 200;
wrapper.y = 0;

return { success: true, wrapperId: wrapper.id };
```

### Step 4: Build Each Section Inside the Wrapper

**This is the most important step.** Build one section at a time, each in its own `use_figma` call. At the start of each script, fetch the wrapper by ID and append new content directly to it.

```js
const createdNodeIds = [];
const wrapper = await figma.getNodeByIdAsync("WRAPPER_ID_FROM_STEP_3");

// Import design system components by key
const buttonSet = await figma.importComponentSetByKeyAsync("BUTTON_SET_KEY");
const primaryButton = buttonSet.children.find(c =>
  c.type === "COMPONENT" && c.name.includes("variant=primary")
) || buttonSet.defaultVariant;

// Import design system variables for colors and spacing
const bgColorVar = await figma.variables.importVariableByKeyAsync("BG_COLOR_VAR_KEY");
const spacingVar = await figma.variables.importVariableByKeyAsync("SPACING_VAR_KEY");

// Build section frame with variable bindings (not hardcoded values)
const section = figma.createFrame();
section.name = "Header";
section.layoutMode = "HORIZONTAL";
section.setBoundVariable("paddingLeft", spacingVar);
section.setBoundVariable("paddingRight", spacingVar);
const bgPaint = figma.variables.setBoundVariableForPaint(
  { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }, 'color', bgColorVar
);
section.fills = [bgPaint];

// Import and apply text/effect styles
const shadowStyle = await figma.importStyleByKeyAsync("SHADOW_STYLE_KEY");
section.effectStyleId = shadowStyle.id;

// Create component instances inside the section
const btnInstance = primaryButton.createInstance();
section.appendChild(btnInstance);
createdNodeIds.push(btnInstance.id);

// Append section to wrapper
wrapper.appendChild(section);
section.layoutSizingHorizontal = "FILL"; // AFTER appending

createdNodeIds.push(section.id);
return { success: true, createdNodeIds };
```

After each section, validate with `get_screenshot` before moving on. Look closely for cropped/clipped text (line heights cutting off content) and overlapping elements — these are the most common issues and easy to miss at a glance.

#### Override instance text with setProperties()

Component instances ship with placeholder text ("Title", "Heading", "Button"). Use the component property keys you discovered in Step 2 to override them with `setProperties()` — this is more reliable than direct `node.characters` manipulation. See [component-patterns.md](../figma-use/references/component-patterns.md#overriding-text-in-a-component-instance) for the full pattern.

For nested instances that expose their own TEXT properties, call `setProperties()` on the nested instance:

```js
const nestedHeading = cardInstance.findOne(n => n.type === "INSTANCE" && n.name === "Text Heading");
if (nestedHeading) {
  nestedHeading.setProperties({ "Text#2104:5": "Actual heading from source code" });
}
```

Only fall back to direct `node.characters` for text that is NOT managed by any component property.

#### Read source code defaults carefully

When translating code components to Figma instances, check the component's default prop values in the source code, not just what's explicitly passed. For example, `<Button size="small">Register</Button>` with no variant prop — check the component definition to find `variant = "primary"` as the default. Selecting the wrong variant (e.g., Neutral instead of Primary) produces a visually incorrect result that's easy to miss.

#### What to build manually vs. import from design system

| Build manually | Import from design system |
|----------------|--------------------------|
| Page wrapper frame | **Components**: buttons, cards, inputs, nav, etc. |
| Section container frames | **Variables**: colors (fills, strokes), spacing (padding, gap), radii |
| Layout grids (rows, columns) | **Text styles**: heading, body, caption, etc. |
| | **Effect styles**: shadows, blurs, etc. |

**Never hardcode hex colors or pixel spacing** when a design system variable exists. Use `setBoundVariable` for spacing/radii and `setBoundVariableForPaint` for colors. Apply text styles with `node.textStyleId` and effect styles with `node.effectStyleId`.

### Step 5: Validate the Full Screen

After composing all sections, call `get_screenshot` on the full page frame and compare against the source. Fix any issues with targeted `use_figma` calls — don't rebuild the entire screen.

**Screenshot individual sections, not just the full page.** A full-page screenshot at reduced resolution hides text truncation, wrong colors, and placeholder text that hasn't been overridden. Take a screenshot of each section by node ID to catch:
- **Cropped/clipped text** — line heights or frame sizing cutting off descenders, ascenders, or entire lines
- **Overlapping content** — elements stacking on top of each other due to incorrect sizing or missing auto-layout
- Placeholder text still showing ("Title", "Heading", "Button")
- Truncated content from layout sizing bugs
- Wrong component variants (e.g., Neutral vs Primary button)

### Step 6: Updating an Existing Screen

When updating rather than creating from scratch:

1. Use `get_metadata` to inspect the existing screen structure.
2. Identify which sections need updating and which can stay.
3. For each section that needs changes:
   - Locate the existing nodes by ID or name
   - Swap component instances if the design system component changed
   - Update text content, variant properties, or layout as needed
   - Remove deprecated sections
   - Add new sections
4. Validate with `get_screenshot` after each modification.

```js
// Example: Swap a button variant in an existing screen
const existingButton = await figma.getNodeByIdAsync("EXISTING_BUTTON_INSTANCE_ID");
if (existingButton && existingButton.type === "INSTANCE") {
  // Import the updated component
  const buttonSet = await figma.importComponentSetByKeyAsync("BUTTON_SET_KEY");
  const newVariant = buttonSet.children.find(c =>
    c.name.includes("variant=primary") && c.name.includes("size=lg")
  ) || buttonSet.defaultVariant;
  existingButton.swapComponent(newVariant);
}
return { success: true, mutatedNodeIds: [existingButton.id] };
```

## Reference Docs

For detailed API patterns and gotchas, load these from the [figma-use](../figma-use/SKILL.md) references as needed:

- [component-patterns.md](../figma-use/references/component-patterns.md) — importing by key, finding variants, setProperties, text overrides, working with instances
- [variable-patterns.md](../figma-use/references/variable-patterns.md) — creating/binding variables, importing library variables, scopes, aliasing, discovering existing variables
- [text-style-patterns.md](../figma-use/references/text-style-patterns.md) — creating/applying text styles, importing library text styles, type ramps
- [effect-style-patterns.md](../figma-use/references/effect-style-patterns.md) — creating/applying effect styles (shadows), importing library effect styles
- [gotchas.md](../figma-use/references/gotchas.md) — layout pitfalls (HUG/FILL interactions, counterAxisAlignItems, sizing order), paint/color issues, page context resets

## Error Recovery

Follow the error recovery process from [figma-use](../figma-use/SKILL.md#6-error-recovery--self-correction):

1. **STOP** on error — do not retry immediately.
2. **Read the error message carefully** to understand what went wrong.
3. If the error is unclear, call `get_metadata` or `get_screenshot` to inspect the current file state.
4. **Fix the script** based on the error message.
5. **Retry** the corrected script — this is safe because failed scripts are atomic (nothing is created if a script errors).

Because this skill works incrementally (one section per call), errors are naturally scoped to a single section. Previous sections from successful calls remain intact.

## Best Practices

- **Always search before building.** The design system likely has the component, variable, or style you need. Manual construction and hardcoded values should be the exception, not the rule.
- **Search broadly.** Try synonyms and partial terms. A "NavigationPill" might be found under "pill", "nav", "tab", or "chip". For variables, search "color", "spacing", "radius", etc.
- **Prefer design system tokens over hardcoded values.** Use variable bindings for colors, spacing, and radii. Use text styles for typography. Use effect styles for shadows. This keeps the screen linked to the design system.
- **Prefer component instances over manual builds.** Instances stay linked to the source component and update automatically when the design system evolves.
- **Work section by section.** Never build more than one major section per `use_figma` call.
- **Return node IDs from every call.** You'll need them to compose sections and for error recovery.
- **Validate visually after each section.** Use `get_screenshot` to catch issues early.
- **Match existing conventions.** If the file already has screens, match their naming, sizing, and layout patterns.
```

---

## figma-generate-library

Source: `/Users/jameshou/.agents/skills/figma-generate-library/SKILL.md`

```md
---
name: figma-generate-library
description: "Build or update a professional-grade design system in Figma from a codebase. Use when the user wants to create variables/tokens, build component libraries, set up theming (light/dark modes), document foundations, or reconcile gaps between code and Figma. This skill teaches WHAT to build and in WHAT ORDER — it complements the `figma-use` skill which teaches HOW to call the Plugin API. Both skills should be loaded together."
disable-model-invocation: false
---

# Design System Builder — Figma MCP Skill

Build professional-grade design systems in Figma that match code. This skill orchestrates multi-phase workflows across 20–100+ `use_figma` calls, enforcing quality patterns from real-world design systems (Material 3, Polaris, Figma UI3, Simple DS).

**Prerequisites**: The `figma-use` skill MUST also be loaded for every `use_figma` call. It provides Plugin API syntax rules (return pattern, page reset, ID return, font loading, color range). This skill provides design system domain knowledge and workflow orchestration.

**Always pass `skillNames: "figma-generate-library"` when calling `use_figma` as part of this skill.** This is a logging parameter — it does not affect execution.

---

## 1. The One Rule That Matters Most

**This is NEVER a one-shot task.** Building a design system requires 20–100+ `use_figma` calls across multiple phases, with mandatory user checkpoints between them. Any attempt to create everything in one call WILL produce broken, incomplete, or unrecoverable results. Break every operation to the smallest useful unit, validate, get feedback, proceed.

---

## 2. Mandatory Workflow

Every design system build follows this phase order. Skipping or reordering phases causes structural failures that are expensive to undo.

```text
Phase 0: DISCOVERY (always first — no use_figma writes yet)
  0a. Analyze codebase → extract tokens, components, naming conventions
  0b. Inspect Figma file → pages, variables, components, styles, existing conventions
  0c. Search subscribed libraries → use search_design_system for reusable assets
  0d. Lock v1 scope → agree on exact token set + component list before any creation
  0e. Map code → Figma → resolve conflicts (code and Figma disagree = ask user)
  ✋ USER CHECKPOINT: present full plan, await explicit approval

Phase 1: FOUNDATIONS (tokens first — always before components)
  1a. Create variable collections and modes
  1b. Create primitive variables (raw values, 1 mode)
  1c. Create semantic variables (aliased to primitives, mode-aware)
  1d. Set scopes on ALL variables
  1e. Set code syntax on ALL variables
  1f. Create effect styles (shadows) and text styles (typography)
  → Exit criteria: every token from the agreed plan exists, all scopes set, all code syntax set
  ✋ USER CHECKPOINT: show variable summary, await approval

Phase 2: FILE STRUCTURE (before components)
  2a. Create page skeleton: Cover → Getting Started → Foundations → --- → Components → --- → Utilities
  2b. Create foundations documentation pages (color swatches, type specimens, spacing bars)
  → Exit criteria: all planned pages exist, foundations docs are navigable
  ✋ USER CHECKPOINT: show page list + screenshot, await approval

Phase 3: COMPONENTS (one at a time — never batch)
  For EACH component (in dependency order: atoms before molecules):
    3a. Create dedicated page
    3b. Build base component with auto-layout + full variable bindings
    3c. Create all variant combinations (combineAsVariants + grid layout)
    3d. Add component properties (TEXT, BOOLEAN, INSTANCE_SWAP)
    3e. Link properties to child nodes
    3f. Add page documentation (title, description, usage notes)
    3g. Validate: get_metadata (structure) + get_screenshot (visual)
    3h. Optional: lightweight Code Connect mapping while context is fresh
    → Exit criteria: variant count correct, all bindings verified, screenshot looks right
    ✋ USER CHECKPOINT per component: show screenshot, await approval before next component

Phase 4: INTEGRATION + QA (final pass)
  4a. Finalize all Code Connect mappings
  4b. Accessibility audit (contrast, min touch targets, focus visibility)
  4c. Naming audit (no duplicates, no unnamed nodes, consistent casing)
  4d. Unresolved bindings audit (no hardcoded fills/strokes remaining)
  4e. Final review screenshots of every page
  ✋ USER CHECKPOINT: complete sign-off
```

---

## 3. Critical Rules

**Plugin API basics** (from use_figma skill — enforced here too):
- Use `return` to send data back (auto-serialized). Do NOT wrap in IIFE or call closePlugin.
- Return ALL created/mutated node IDs in every return value
- Page context resets each call — always `await figma.setCurrentPageAsync(page)` at start
- `figma.notify()` throws — never use it
- Colors are 0–1 range, not 0–255
- Font MUST be loaded before any text write: `await figma.loadFontAsync({family, style})`

**Design system rules**:
1. **Variables BEFORE components** — components bind to variables. No token = no component.
2. **Inspect before creating** — run read-only `use_figma` to discover existing conventions. Match them.
3. **One page per component** *(default)* — exception: tightly related families (e.g., Input + helpers) may share a page with clear section separation.
4. **Bind visual properties to variables** *(default)* — fills, strokes, padding, radius, gap. Exceptions: intentionally fixed geometry (icon pixel-grid sizes, static dividers).
5. **Scopes on every variable** — NEVER leave as `ALL_SCOPES`. Background: `FRAME_FILL, SHAPE_FILL`. Text: `TEXT_FILL`. Border: `STROKE_COLOR`. Spacing: `GAP`. Radii: `CORNER_RADIUS`. Primitives: `[]` (hidden).
6. **Code syntax on every variable** — WEB syntax MUST use the `var()` wrapper: `var(--color-bg-primary)`, not `--color-bg-primary`. Use the actual CSS variable name from the codebase. ANDROID/iOS do NOT use a wrapper.
7. **Alias semantics to primitives** — `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`. Never duplicate raw values in semantic layer.
8. **Position variants after combineAsVariants** — they stack at (0,0). Manually grid-layout + resize.
9. **INSTANCE_SWAP for icons** — never create a variant per icon. Cap variant matrices: if Size × Style × State > 30 combinations, split into sub-component.
10. **Deterministic naming** — use consistent, unique node names for idempotent cleanup and resumability. Track created node IDs via return values and the state ledger.
11. **No destructive cleanup** — cleanup scripts identify nodes by name convention or returned IDs, not by guessing.
12. **Validate before proceeding** — never build on unvalidated work. `get_metadata` after every create, `get_screenshot` after each component.
13. **NEVER parallelize `use_figma` calls** — Figma state mutations must be strictly sequential. Even if your tool supports parallel calls, never run two use_figma calls simultaneously.
14. **Never hallucinate Node IDs** — always read IDs from the state ledger returned by previous calls. Never reconstruct or guess an ID from memory.
15. **Use the helper scripts** — embed scripts from `scripts/` into your use_figma calls. Don't write 200-line inline scripts from scratch.
16. **Explicit phase approval** — at each checkpoint, name the next phase explicitly. "looks good" is not approval to proceed to Phase 3 if you asked about Phase 1.

---

## 4. State Management (Required for Long Workflows)

> **`getPluginData()` / `setPluginData()` are NOT supported in `use_figma`.** Use `getSharedPluginData()` / `setSharedPluginData()` instead (these ARE supported), or use name-based lookups and the state ledger (returned IDs).

| Entity type | Idempotency key | How to check existence |
|-------------|----------------|----------------------|
| Scene nodes (pages, frames, components) | `setSharedPluginData('dsb', 'key', value)` or unique name | `node.getSharedPluginData('dsb', 'key')` or `page.findOne(n => n.name === 'Button')` |
| Variables | Name within collection | `(await figma.variables.getLocalVariablesAsync()).find(v => v.name === name && v.variableCollectionId === collId)` |
| Styles | Name | `getLocalTextStyles().find(s => s.name === name)` |

Tag every created **scene node** immediately after creation:
```javascript
node.setSharedPluginData('dsb', 'run_id', RUN_ID);        // identifies this build run
node.setSharedPluginData('dsb', 'phase', 'phase3');        // which phase created it
node.setSharedPluginData('dsb', 'key', 'component/button');// unique logical key
```

**State persistence**: Do NOT rely solely on conversation context for the state ledger. Write it to disk:
```text
/tmp/dsb-state-{RUN_ID}.json
```
Re-read this file at the start of every turn. In long workflows, conversation context will be truncated — the file is the source of truth.

Maintain a state ledger tracking:
```json
{
  "runId": "ds-build-2024-001",
  "phase": "phase3",
  "step": "component-button",
  "entities": {
    "collections": { "primitives": "id:...", "color": "id:..." },
    "variables": { "color/bg/primary": "id:...", "spacing/sm": "id:..." },
    "pages": { "Cover": "id:...", "Button": "id:..." },
    "components": { "Button": "id:..." }
  },
  "pendingValidations": ["Button:screenshot"],
  "completedSteps": ["phase0", "phase1", "phase2", "component-avatar"]
}
```

**Idempotency check** before every create: query by name + state ledger ID. If exists, skip or update — never duplicate.

**Resume protocol**: at session start or after context truncation, run a read-only `use_figma` to scan all pages, components, variables, and styles by name to reconstruct the `{key → id}` map. Then re-read the state file from disk if available.

**Continuation prompt** (give this to the user when resuming in a new chat):
> "I'm continuing a design system build. Run ID: {RUN_ID}. Load the figma-generate-library skill and resume from the last completed step."

---

## 5. search_design_system — Reuse Decision Matrix

Search FIRST in Phase 0, then again immediately before each component creation.

```text
search_design_system({ query, fileKey, includeComponents: true, includeVariables: true, includeStyles: true })
```

**Reuse if** all of these are true:
- Component property API matches your needs (same variant axes, compatible types)
- Token binding model is compatible (uses same or aliasable variables)
- Naming conventions match the target file
- Component is editable (not locked in a remote library you don't own)

**Rebuild if** any of these:
- API incompatibility (different property names, wrong variant model)
- Token model incompatible (hardcoded values, different variable schema)
- Ownership issue (can't modify the library)

**Wrap if** visual match but API incompatible:
- Import the library component as a nested instance inside a new wrapper component
- Expose a clean API on the wrapper

**Three-way priority**: local existing → subscribed library import → create new.

---

## 6. User Checkpoints

Mandatory. Design decisions require human judgment.

| After | Required artifacts | Ask |
|-------|-------------------|-----|
| Discovery + scope lock | Token list, component list, gap analysis | "Here's my plan. Approve before I create anything?" |
| Foundations | Variable summary (N collections, M vars, K modes), style list | "All tokens created. Review before file structure?" |
| File structure | Page list + screenshot | "Pages set up. Review before components?" |
| Each component | get_screenshot of component page | "Here's [Component] with N variants. Correct?" |
| Each conflict (code ≠ Figma) | Show both versions | "Code says X, Figma has Y. Which wins?" |
| Final QA | Per-page screenshots + audit report | "Complete. Sign off?" |

**If user rejects**: fix before moving on. Never build on rejected work.

---

## 7. Naming Conventions

Match existing file conventions. If starting fresh:

**Variables** (slash-separated):
```text
color/bg/primary     color/text/secondary    color/border/default
spacing/xs  spacing/sm  spacing/md  spacing/lg  spacing/xl  spacing/2xl
radius/none  radius/sm  radius/md  radius/lg  radius/full
typography/body/font-size    typography/heading/line-height
```

**Primitives**: `blue/50` → `blue/900`, `gray/50` → `gray/900`

**Component names**: `Button`, `Input`, `Card`, `Avatar`, `Badge`, `Checkbox`, `Toggle`

**Variant names**: `Property=Value, Property=Value` — e.g., `Size=Medium, Style=Primary, State=Default`

**Page separators**: `---` (most common) or `——— COMPONENTS ———`

> Full naming reference: [naming-conventions.md](references/naming-conventions.md)

---

## 8. Token Architecture

| Complexity | Pattern |
|-----------|---------|
| < 50 tokens | Single collection, 2 modes (Light/Dark) |
| 50–200 tokens | **Standard**: Primitives (1 mode) + Color semantic (Light/Dark) + Spacing (1 mode) + Typography (1 mode) |
| 200+ tokens | **Advanced**: Multiple semantic collections, 4–8 modes (Light/Dark × Contrast × Brand). See M3 pattern in [token-creation.md](references/token-creation.md) |

Standard pattern (recommended starting point):
```text
Collection: "Primitives"    modes: ["Value"]
  blue/500 = #3B82F6, gray/900 = #111827, ...

Collection: "Color"         modes: ["Light", "Dark"]
  color/bg/primary → Light: alias Primitives/white, Dark: alias Primitives/gray-900
  color/text/primary → Light: alias Primitives/gray-900, Dark: alias Primitives/white

Collection: "Spacing"       modes: ["Value"]
  spacing/xs = 4, spacing/sm = 8, spacing/md = 16, ...
```

---

## 9. Per-Phase Anti-Patterns

**Phase 0 anti-patterns:**
- ❌ Starting to create anything before scope is locked with user
- ❌ Ignoring existing file conventions and imposing new ones
- ❌ Skipping `search_design_system` before planning component creation

**Phase 1 anti-patterns:**
- ❌ Using `ALL_SCOPES` on any variable
- ❌ Duplicating raw values in semantic layer instead of aliasing
- ❌ Not setting code syntax (breaks Dev Mode and round-tripping)
- ❌ Creating component tokens before agreeing on token taxonomy

**Phase 2 anti-patterns:**
- ❌ Skipping the cover page or foundations docs
- ❌ Putting multiple unrelated components on one page

**Phase 3 anti-patterns:**
- ❌ Creating components before foundations exist
- ❌ Hardcoding any fill/stroke/spacing/radius value in a component
- ❌ Creating a variant per icon (use INSTANCE_SWAP instead)
- ❌ Not positioning variants after combineAsVariants (they all stack at 0,0)
- ❌ Building variant matrix > 30 without splitting (variant explosion)
- ❌ Importing remote components then immediately detaching them

**General anti-patterns:**
- ❌ Retrying a failed script without understanding the error first
- ❌ Using name-prefix matching for cleanup (deletes user-owned nodes)
- ❌ Building on unvalidated work from the previous step
- ❌ Skipping user checkpoints to "save time"
- ❌ Parallelizing use_figma calls (always sequential)
- ❌ Guessing/hallucinating node IDs from memory (always read from state ledger)
- ❌ Writing massive inline scripts instead of using the provided helper scripts
- ❌ Starting Phase 3 because the user said "build the button" without completing Phases 0-2

---

## 10. Reference Docs

Load on demand — each reference is authoritative for its phase:

Use your file reading tool to read these docs when needed. Do not assume their contents from the filename.

| Doc | Phase | Required / Optional | Load when |
|-----|-------|---------------------|-----------|
| [discovery-phase.md](references/discovery-phase.md) | 0 | **Required** | Starting any build — codebase analysis + Figma inspection |
| [token-creation.md](references/token-creation.md) | 1 | **Required** | Creating variables, collections, modes, styles |
| [documentation-creation.md](references/documentation-creation.md) | 2 | Required | Creating cover page, foundations docs, swatches |
| [component-creation.md](references/component-creation.md) | 3 | **Required** | Creating any component or variant |
| [code-connect-setup.md](references/code-connect-setup.md) | 3–4 | Required | Setting up Code Connect or variable code syntax |
| [naming-conventions.md](references/naming-conventions.md) | Any | Optional | Naming anything — variables, pages, variants, styles |
| [error-recovery.md](references/error-recovery.md) | Any | **Required on error** | Script fails, multi-step workflow recovery, cleanup of abandoned workflow state |

---

## 11. Scripts

Reusable Plugin API helper functions. Embed in `use_figma` calls:

| Script | Purpose |
|--------|---------|
| [inspectFileStructure.js](scripts/inspectFileStructure.js) | Discover all pages, components, variables, styles; returns full inventory |
| [createVariableCollection.js](scripts/createVariableCollection.js) | Create a named collection with modes; returns `{collectionId, modeIds}` |
| [createSemanticTokens.js](scripts/createSemanticTokens.js) | Create aliased semantic variables from a token map |
| [createComponentWithVariants.js](scripts/createComponentWithVariants.js) | Build a component set from a variant matrix; handles grid layout |
| [bindVariablesToComponent.js](scripts/bindVariablesToComponent.js) | Bind design tokens to all component visual properties |
| [createDocumentationPage.js](scripts/createDocumentationPage.js) | Create a page with title + description + section structure |
| [validateCreation.js](scripts/validateCreation.js) | Verify created nodes match expected counts, names, structure |
| [cleanupOrphans.js](scripts/cleanupOrphans.js) | Remove orphaned nodes by name convention or state ledger IDs |
| [rehydrateState.js](scripts/rehydrateState.js) | Scan file for all pages, components, variables by name; returns full `{key → nodeId}` map for state reconstruction |
```

---

## audit-design-system

Source: `/Users/jameshou/.agents/skills/audit-design-system/SKILL.md`

```md
---
name: audit-design-system
description: Audit a Figma screen or component for design-system integration drift, including missing shared components, local overrides, and unbound tokens.
---

# Audit Design System

Review a Figma node for evidence that the design is not properly integrated with the design system.

This skill is read-only. When the user wants a write action afterward, downstream skills should use `use_figma` through a `figma-use`-style helper when the host environment requires one.

## Output Format Selection

- **Explicit user request wins**:
  - If the user asks for `--json` or JSON, output raw JSON (no markdown fences, no prose).
  - If the user asks for `--markdown`, markdown, or a specific human-readable format, output the human-readable markdown report.
- **Codex Desktop app**: Output raw JSON by default.
- **Codex CLI and other chat-style environments**: Output the human-readable markdown report by default.
- **Machine-consumed review surfaces**: Output raw JSON by default.
- **Ambiguous environment**: If the environment is unclear, output markdown by default.

## Workflow

1. Parse the Figma input.
   Accept a full Figma URL, or a `fileKey` and `nodeId`.
   Normalize node IDs from `72-293` to `72:293` when needed.

2. Pull the minimum required evidence with Figma MCP read tools.
   Call `get_design_context` for the exact node under review.
   Call `get_screenshot` for visual confirmation.
   Call `get_variable_defs` to see which variables are actually bound.
   Call `get_code_connect_map` when relevant.
   Call `get_metadata` when the reviewed node is large, repeated, or board-like and you need to map nested instances before drilling in.
   Call `search_design_system` when you have identified a likely non-systemized primitive and there is a realistic chance of suggesting a concrete replacement from the audited design system.

3. Review for systemization failures, not visual taste.
   Look for places where the design should probably inherit from the design system but is locally constructed instead.
   Base every finding on structure visible in Figma: instances, duplicated frames, raw values, variant drift, or missing token bindings.
   Prefer omissions over weak findings.

4. When the evidence is strong enough, suggest a replacement candidate.
   After identifying a likely custom primitive, use `search_design_system` to find the closest matching component family from the audited design system.
   Include a candidate only when the match is credible from structure and naming, not just screenshot similarity.
   If search results are noisy or ambiguous, omit the candidate instead of guessing.

5. Present findings in the appropriate format based on the environment.
   Use JSON for Codex Desktop and machine-consumed review surfaces, markdown for Claude Code CLI and other chat-style environments (see Output Format Selection above).

6. When the user wants a fix, route to the right downstream skill.
   Prefer [fix-design-system-finding](../fix-design-system-finding/SKILL.md) when one specific offending node should be repaired.
   Prefer [apply-design-system](../apply-design-system/SKILL.md) when the user wants a broader screen-wide pass, multiple sections need coordinated remediation, or the review is being used to define scope before writing.

## What To Flag

- Shared UI primitives recreated as ad-hoc frames instead of component instances.
  Common targets: buttons, icon buttons, cards, alerts, pills, chips, avatars, stat tiles, tab bars, nav bars, FABs, list rows.

- Repeated sibling structures that should clearly collapse into one reusable primitive.
  Example: three nearly identical stat tiles with different content.

- Hard-coded visual values where the rest of the design system uses variables.
  Common targets: fills, strokes, text colors, radius, spacing, typography, shadows.
  Only flag this when the evidence is concrete, such as a raw hex value or bespoke geometry sitting beside tokenized peers.

- Global navigation or other high-leverage patterns built from custom frames instead of system components.
  Flag these aggressively because drift there scales across many screens.

- Variant drift inside a nominal component.
  Example: a local edit button with unusual size, stroke width, or radius that does not match the expected icon-button primitive.

## What Not To Flag

- Purely aesthetic preferences.
- Copywriting or product decisions.
- Layout choices that can reasonably remain screen-specific.
- One-off compositions when the underlying primitives are already componentized and tokenized.
- Claims that require undocumented assumptions about a design library.

## Evidence Standard

Every finding must answer both questions:

1. What concrete Figma evidence shows this is not systemized correctly?
2. Why does that matter for propagation, consistency, theming, or maintenance?

Good evidence includes:

- a node is a plain frame when it should be an instance
- several siblings duplicate the same structure
- raw color or geometry values appear where variables or standard primitives should apply
- a global pattern is custom-built

Weak evidence includes:

- "this looks custom"
- "I would normally make this a component"
- any statement based only on screenshot aesthetics without structural support

## Replacement Suggestion Rule

When a finding is about a missing shared primitive, try to attach one likely replacement suggestion.

Use `search_design_system` after you already know what category of thing is missing, for example:
- custom avatar cluster
- bespoke stat tile
- local alert card
- hand-built navigation item

Only suggest a replacement when:
- the node's role is clear
- the search result belongs to the relevant library or audited file context
- the candidate is structurally plausible for the finding

Good suggestion language:
- `This custom avatar frame could likely be replaced with Avatar from library X.`
- `These repeated stat tiles appear to map to Metric item from library X.`

Do not overstate:
- do not claim the suggested component is definitely correct unless the evidence is explicit
- do not force a replacement candidate into every finding
- do not recommend a component from an unrelated library just because search returned it first

## Output Format

### JSON Output

When the selected output format is JSON, return this exact JSON shape with no markdown fences and no extra prose:

```json
{
  "findings": [
    {
      "title": "<= 80 chars, imperative>",
      "body": "<valid Markdown explaining why this is a problem>",
      "confidence_score": 0.0,
      "priority": 0,
      "code_location": {
        "absolute_file_path": "/figma/<fileKey>/nodes/<nodeId>",
        "line_range": {
          "start": 1,
          "end": 1
        }
      }
    }
  ],
  "overall_correctness": "patch is correct" | "patch is incorrect",
  "overall_explanation": "<1-3 sentence summary>",
  "overall_confidence_score": 0.0
}
```

Schema notes:

- Use `overall_correctness: "patch is incorrect"` whenever you found one or more design-system integration issues.
- Use `overall_correctness: "patch is correct"` only when there are no findings.
- For each finding, set `code_location.absolute_file_path` to `/figma/<fileKey>/nodes/<nodeId>` using the most specific offending node.
- Always set `line_range.start` and `line_range.end` to `1`.

### Human-Readable Markdown Report

When the selected output format is markdown, present a formatted markdown report with:

1. **Header section:**
   - File name and node being reviewed
   - Overall verdict: ✅ Passes / ⚠️ Needs Work / ❌ Significant Issues
   - Confidence percentage

2. **Summary:** 2-3 sentences explaining the overall state

3. **Findings table:** Quick overview with priority indicators
   - 🔴 Critical (priority 3): severe library-level or navigation-level issues
   - 🟠 High (priority 2): important reusable primitive or tokenization issues
   - 🟡 Medium (priority 1): moderate system drift
   - ⚪ Low (priority 0): nits or low-impact consistency issues

4. **Details section:** Expand each finding with:
   - What's wrong (concrete evidence from Figma structure)
   - Why it matters (maintenance, consistency, theming impact)
   - Likely replacement, when supported by `search_design_system`
   - Affected node IDs for reference

5. **Recommendations:** Prioritized action items

### Output Rules

- Keep findings focused on the highest-signal issues. Usually 0-6 findings.
- Keep titles imperative and under 80 characters.
- Always anchor each finding to a specific node ID so users can locate it in Figma.
- For JSON output, do not invent filesystem paths. Use `/figma/<fileKey>/nodes/<nodeId>` exactly.
- When a replacement suggestion is credible, include it in the finding body.

## Review Heuristics

Use `priority` like this:

- `0`: nit or low-impact consistency issue
- `1`: moderate system drift
- `2`: important reusable primitive or tokenization issue
- `3`: severe library-level or navigation-level issue likely to propagate widely

Use `confidence_score` like this:

- `0.9-1.0`: direct structural evidence
- `0.7-0.89`: strong inference from repetition and nearby token usage
- `0.5-0.69`: plausible but incomplete evidence; prefer omitting instead

## Board And Screen Scope

For a single screen:

- inspect the root node
- drill into repeated or high-leverage children
- anchor findings to the most specific offending node

For a board or larger page:

- use `get_metadata` first to identify candidate screens or repeated modules
- review only the most relevant nodes instead of trying to audit everything
- keep findings scoped and evidence-backed

## Example Trigger Phrases

- "Review this Figma screen for design-system integration"
- "Audit this board for missing component usage"
- "Check whether this design uses tokens correctly"
- "/audit-design-system https://figma.com/design/..."
- "/audit-design-system --json https://figma.com/design/..." (for JSON output)

## Handoff Guidance

Use this routing rule after the review:
- one concrete finding with a narrow write scope: use [fix-design-system-finding](../fix-design-system-finding/SKILL.md)
- several findings that collapse into a broader screen or section reconciliation pass: use [apply-design-system](../apply-design-system/SKILL.md)

Do not force every review result through the single-finding fix skill. Some reviews are better used as scope discovery for a broader apply pass.
```

---

## apply-design-system

Source: `/Users/jameshou/.agents/skills/apply-design-system/SKILL.md`

```md
---
name: apply-design-system
description: Review an existing design and connect it to design system components.
---

# Connect A Design To A Design System

Use this skill for an existing Figma design that should reuse a published design system instead of detached layers, local wrappers, or one-off components.

This skill supports two entry modes:
- `review-then-apply`: the user wants a broad pass, but the exact offending sections are not yet identified
- `apply-known-scope`: the user already knows which sections or clusters should be brought onto the design system

Load these capabilities first:
- Figma MCP read access for tools such as `get_metadata`, `get_screenshot`, and `search_design_system`
- a `figma-use`-style helper before any `use_figma` call, when your environment requires one
- a screen-building companion workflow, when available, if you are reconnecting a full screen or page

Do not use this skill as the default follow-up to a single `audit-design-system` finding. For one targeted issue, use [fix-design-system-finding](../fix-design-system-finding/SKILL.md) so the write scope stays narrow.

## Core Rule

Do not treat a section as "connected" just because it contains a few design-system buttons or icons.

This skill is for multi-section reconciliation. If the task can be satisfied by fixing one specific reviewed node, the narrower finding-fix skill is the better choice.

Classify each section into exactly one bucket:
- `already-connected`: the section itself is a library instance or a composition the user explicitly accepts as already canonical
- `exact-swap`: a published library component or variant can replace the section directly
- `compose-from-primitives`: no single library component exists, but the section can be rebuilt from published library primitives
- `blocked`: the library does not expose the needed components, imports fail, or the section is intentionally bespoke

## Required Workflow

### 1. Determine Scope First

Before gathering replacement candidates, decide whether the screen needs an initial audit.

If scope is not already identified:
1. Run [audit-design-system](../audit-design-system/SKILL.md) or perform an equivalent internal audit pass.
2. Collapse the review output into section-sized work packages instead of treating every micro-finding as a separate rewrite task.
3. If the review produces only one narrow finding, switch to [fix-design-system-finding](../fix-design-system-finding/SKILL.md) instead of continuing here.

If scope is already identified, continue directly.

Do not skip component discovery just because a review already exists. Review identifies drift; this skill still has to choose the actual replacement primitives and variants.

### 2. Capture the Current State

Before writing:
1. Get the target frame metadata with `get_metadata`.
2. Get a screenshot with `get_screenshot`.
3. If you need `get_design_context` and Figma asks the Code Connect question, ask the user exactly as instructed by the tool before proceeding.

For this skill, prefer `get_metadata` plus `use_figma` for structure discovery. `get_design_context` is optional unless it unlocks missing context.

### 3. Back Up the Target Screen

Before destructive edits, duplicate the frame or page and place the backup to the right.

Name it clearly, for example:
- `Backup - Start`
- `Backup - Mobile dashboard`

Do this in its own `use_figma` call and return the created node ID.

### 4. Inventory the Existing Screen

Inspect the target frame before searching the library.

Use `use_figma` to gather:
- top-level section instances
- each section's `mainComponent`
- whether that component is local, remote, or missing
- nested published components already used inside each local wrapper
- exposed text and variant properties when present

Prefer exact keys over names. Names are only hints.

Useful read-only inventory pattern:

```js
(async () => {
  try {
    await figma.setCurrentPageAsync(figma.root.children.find(p => p.id === "PAGE_ID"));
    const frame = await figma.getNodeByIdAsync("FRAME_ID");
    const sections = frame.findAll(n => n.type === "INSTANCE").map(inst => {
      const mc = inst.mainComponent;
      const cs = mc?.parent?.type === "COMPONENT_SET" ? mc.parent : null;
      return {
        instanceId: inst.id,
        instanceName: inst.name,
        componentName: mc?.name ?? null,
        componentKey: mc?.key ?? null,
        componentSetName: cs?.name ?? null,
        componentSetKey: cs?.key ?? null,
      };
    });
    figma.closePlugin(JSON.stringify({ createdNodeIds: [], mutatedNodeIds: [], sections }));
  } catch (e) {
    figma.closePluginWithFailure(e.message);
  }
})()
```

### 5. Build a Component Map From the Design System

Prefer authoritative sources in this order:
1. Existing screens in the same library or workfile that already use the system
2. Known library pages inspected directly with `use_figma`
3. `search_design_system` as a fallback only

When using `search_design_system`, remember:
- results may include unrelated team or community libraries
- broad queries are useful for discovery, but do not trust them without verifying the actual file or page
- once the right library is known, prefer direct inspection of that file over repeated search calls

For each candidate, capture:
- component or component-set key
- exact variant name
- whether the section is a one-to-one swap or a composition
- text property keys or nested instance properties needed for overrides

Do not default blindly to the library's primary or default variant.

Before choosing a variant, inspect the original node for:
- semantic cues from the name, copy, and usage context
- visual cues such as fills, strokes, effects, corner radius, and typography treatment
- existing variant-like traits already visible in the screen, such as primary vs secondary button treatment

Then compare those cues against the available component-set variants and choose the closest match. If the family is correct but the variant match is ambiguous, call that out instead of silently using the default variant.

### 6. Decide Section Strategy

Use these heuristics:

- `exact-swap` if a library component matches the section's job and structure closely enough that `swapComponent()` or a direct replacement preserves intent.
- `compose-from-primitives` if the section is really a container around library pieces such as avatar, badge, buttons, metrics, or nav items.
- `blocked` if the design system lacks the composite, the library is not published, imports fail, or the section should remain bespoke.

Common patterns:
- Header summary blocks are often `compose-from-primitives`, not one component.
- Alerts and metrics often have strong `exact-swap` candidates.
- Appointment or patient cards often require composition unless the system explicitly ships those domain cards.
- Bottom nav bars are frequently custom containers built from nav-item primitives.

### 7. Update One Section At A Time

Never rewrite the entire screen in one script.

For each section:
1. Read the current node IDs.
2. Import or locate the library component.
3. Match the closest variant to the original section before swapping or rebuilding.
4. Detect whether the parent uses auto-layout.
5. Create or swap only that section.
6. Return all mutated node IDs.
7. Validate with `get_screenshot`.

Prefer `swapComponent()` when the existing node is already an instance of a compatible family and you want to preserve overrides.

Prefer rebuilding beside the original when:
- the old section is a local wrapper around mixed content
- you need to compare the result visually before replacing the original
- you are composing from multiple primitives

When the parent is not auto-layout, treat replacement as a layout-risk operation.

For non-auto-layout parents:
- preserve `x` and `y` explicitly
- preserve width and height explicitly when the replacement should occupy the same footprint
- do not assume the new instance will inherit the old node's position or size
- warn the user that absolute-positioned or grouped parents can cause drift after swaps or rebuilds
- suggest converting the parent to auto-layout only when the user wants structural cleanup, not as the default move

### 8. Handle Import Failures Explicitly

If `importComponentSetByKeyAsync()` or `importComponentByKeyAsync()` fails or times out:
1. Stop.
2. Do not continue making unrelated edits and pretend the section is connected.
3. Check whether exact component keys already exist elsewhere in the target file.
4. If the library file is accessible, verify the exact component key there.
5. Try importing the exact component key instead of the component-set key.
6. If imports still fail, mark the section `blocked` and report the blocker clearly.

Treat these as real blockers:
- published key exists in the library but import times out
- `search_design_system` finds the family, but the target file cannot import it
- only nested primitives can be imported, not the intended composite

### 9. Validate What Actually Changed

After each section:
- screenshot the changed section, not only the full frame
- confirm placeholder text is gone
- confirm the instance is really linked to a library component
- confirm spacing did not regress

At the end, validate the full screen screenshot as well.

## Writing Rules

- Work incrementally and preserve a backup.
- Prefer direct library inspection over noisy search results.
- Prefer exact component keys over names.
- Match the variant to the original visual treatment, not just the correct component family.
- Preserve position and size explicitly when replacing content inside non-auto-layout parents.
- Use imperative evidence in the report: node names, keys, component families, and whether the final node is local or library-backed.
- Do not claim full reconnection when the result is still a local shell around a few shared children.
- If a section must remain bespoke, say so and explain why.

## Deliverable Format

When closing the task, report:
- `Swapped`: sections replaced directly with library instances
- `Composed`: sections rebuilt from library primitives
- `Already connected`: sections that were already valid
- `Blocked`: sections that could not be connected, with the concrete reason

If everything is blocked, say that plainly and include the exact failure mode instead of a vague summary.
```

---

## rad-spacing

Source: `/Users/jameshou/.agents/skills/rad-spacing/SKILL.md`

```md
---
name: rad-spacing
description: Use for Figma layout work when creating new screens, refactoring spacing, standardizing hierarchy, or spacing nested components. Apply hierarchical spacing using the Gestalt principle of proximity so outer containers get proportionally more spacing than inner elements, using 8px/4px increments from the file's library variables.
---

# Rad Spacing

## When to use
- You're creating new screens or layouts and need intentional, consistent spacing that communicates visual hierarchy.
- You're refactoring spacing in an existing Figma design to improve readability and grouping.
- You're building components that will nest inside larger containers and need spacing that scales with depth.
- You're standardizing spacing across a file to align with the Gestalt principle of proximity: related items close together, separate groups further apart.

## Instructions
1. Identify the nesting depth of the design. Map out the hierarchy levels from outermost to innermost (for example: page -> section -> card -> card content -> inline elements).
2. Check the Figma file's library for existing spacing variables:
   - Look for number variables in 4px or 8px increments (for example: `spacing/4`, `spacing/8`, `spacing/16`, `spacing/24`).
   - If the library already has spacing variables, use them. Adapt to whatever naming convention is in place.
3. If no spacing variables exist, create semantic number variables using this default convention:
   - `spacing/xs` -> 4px
   - `spacing/sm` -> 8px
   - `spacing/md` -> 12px
   - `spacing/lg` -> 16px
   - `spacing/xl` -> 24px
   - `spacing/2xl` -> 32px
   - `spacing/3xl` -> 48px
   - Adapt the naming if the library already has a pattern for other variable types.
4. Calculate spacing per hierarchy level using the ~40% rule:
   - Each parent level gets approximately 1.4x the spacing of its child level.
   - Snap the result to the nearest 8px increment. If the 0.6 ratio (child = parent x 0.6) lands closer to a 4px increment than an 8px increment, use the 4px value instead.
   - Work from the innermost elements outward, or from a known base value (commonly 8px for the tightest grouping).
5. Apply spacing using the `use_figma` MCP tool:
   - Use padding on auto-layout frames for container-level spacing (pages, sections, cards).
   - Use gap (`itemSpacing`) on auto-layout frames for spacing between sibling elements.
   - Bind spacing values to the library's number variables wherever possible.
6. Validate the visual hierarchy:
   - Outer groups should feel clearly separated from one another.
   - Inner items within a group should feel cohesive and related.
   - Check that the spacing progression is perceptible at each level. If two adjacent levels look the same, increase the ratio or adjust the snap.
7. Summarize what was applied:
   - List the spacing values used at each hierarchy level.
   - Note any new variables created and any exceptions or deviations from the 40% rule.

## Examples

**Input request:** "Create a settings page with a sidebar and content area containing form sections."

**Hierarchy and spacing calculation (base = 8px, working outward):**

| Level | Element | Spacing | Calculation |
|-------|---------|---------|-------------|
| 4 (innermost) | Form field labels and inputs | 8px gap | Base value |
| 3 | Fields within a form section | 12px gap | 8 x 1.4 = 11.2 -> snaps to 12px (4px increment) |
| 2 | Form sections within content area | 16px gap | 12 x 1.4 = 16.8 -> snaps to 16px |
| 1 | Content area padding | 24px padding | 16 x 1.4 = 22.4 -> snaps to 24px |
| 0 (outermost) | Page padding | 32px padding | 24 x 1.4 = 33.6 -> snaps to 32px |

**Result:** A settings page where the tightest spacing (8px) groups labels with their inputs, slightly wider spacing (12px) separates fields, wider still (16px) distinguishes form sections, and the largest spacing (24-32px) frames the overall page and content area. The eye naturally parses the groupings without explicit dividers.

## Common edge cases
- **No library variables exist:** Create the semantic spacing variables as described in step 3. Confirm the naming convention with the designer or adapt to any existing variable patterns in the file.
- **Deeply nested structures (4+ levels):** The 40% rule may push the outermost spacing very large. Cap the maximum at a reasonable value (for example: 48px or 64px) and compress the inner levels to fit, maintaining the relative progression.
- **Hitting the 4px minimum:** If the innermost level calculates below 4px, floor it at 4px and recalculate outward from there.
- **Ambiguous nesting depth:** When it's unclear whether elements are siblings or parent-child, default to treating visually distinct groups as separate hierarchy levels.
- **Mixed component reuse:** A component used at different nesting depths may need spacing overrides via instance properties. Apply the spacing appropriate to its context, not its definition.
- **Existing designs with inconsistent spacing:** Audit the current values first, then remap systematically from the innermost level outward rather than adjusting individual values in isolation.
```

---

## sync-figma-token

Source: `/Users/jameshou/.agents/skills/sync-figma-token/SKILL.md`

```md
---
name: sync-figma-token
description: "Sync design tokens between code and Figma variables with strict drift reporting, mandatory approval gate, safe delta apply, and persisted reports."
disable-model-invocation: true
metadata:
  mcp-server: figma, figma-staging
---

# sync-figma-token

Use this skill for token parity workflows (code tokens vs Figma variables).

**MANDATORY prerequisite**: load `figma-use` before every `use_figma` call.

## Non-negotiable safety rule

After producing dry-run output, you MUST STOP and ask for approval.

- Do NOT run any write `use_figma` calls in the same turn as dry-run output.
- Ask a normal confirmation question (example: "Apply these changes? (yes/no)").
- Only proceed on explicit affirmative approval.
- If the response is unclear or negative, do not apply writes.

## Standard source formats (required)

Prefer real token sources in this order:
1. Design Tokens JSON (`tokens.json`, `tokens/*.json`, DTCG-style)
2. Style Dictionary input JSON
3. Platform theme sources (Compose/Kotlin/TS) only when JSON source is unavailable

If source format is non-standard, explicitly state assumptions in dry-run output.

## Required policies before writes

- `direction`: `code_to_figma` (default), `figma_to_code`, `bidirectional`
- `deletePolicy`: default `archive_only` (NOT delete)
- `conflictPolicy`: `prefer_code`, `prefer_figma`, `manual_review`
- `namingPolicy`: token key normalization strategy
- `modePolicy`: code mode <-> Figma mode mapping

Never delete by default. Deletion requires explicit user instruction.

## Normalization rules

Normalize both sides to canonical rows:
- `key` (canonical token name)
- `type` (`COLOR`, `FLOAT`, `STRING`, `BOOLEAN`)
- `modeValues` (light/dark/etc.)
- `aliasTarget`
- `scopes`
- `codeSyntax`

Name normalization examples:
- `color.bg.primary` <-> `color/bg/primary`
- `Neutral10` <-> `Neutral/10` only if explicitly mapped by naming policy

## Value validation (required)

Dry-run must validate values, not only presence/type.

- COLOR: compare RGBA with tolerance `epsilon = 0.0001`
- FLOAT: strict numeric comparison unless tolerance is configured
- STRING/BOOLEAN: strict equality
- Aliases: compare canonical alias targets

## Drift categories

Each drift item must include one of:
- `missing_in_figma`
- `missing_in_code`
- `value_mismatch`
- `alias_mismatch`
- `type_mismatch`
- `mode_mismatch`
- `scope_mismatch`
- `code_syntax_mismatch`
- `broken_alias`

## Dry-run output format

Always return:

1) Headline summary:
```json
{
  "create": 0,
  "update": 0,
  "aliasFix": 0,
  "scopeFix": 0,
  "syntaxFix": 0,
  "archive": 0,
  "delete": 0
}
```

2) Detailed drift list with token keys and before/after values.

Then ask:

`Dry-run complete. Apply these changes? (yes/no)`

## Report persistence (required)

Persist report JSON every run:
- `/tmp/sync-figma-token-dry-run-{runId}.json`
- `/tmp/sync-figma-token-final-{runId}.json`

If file persistence fails, mention that explicitly in output.

## Conflict handling

When conflicting data is found (type/mode/alias ambiguity):
- If `conflictPolicy=manual_review`, list conflicts and STOP.
- If `conflictPolicy=prefer_code`, update Figma to source values/types.
- If `conflictPolicy=prefer_figma`, keep Figma and emit drift as informational.

## Apply order

Apply deltas in this order:
1. Ensure collections/modes
2. Create missing primitives
3. Create/update semantic aliases
4. Apply value updates
5. Apply scopes and code syntax
6. Archive stale tokens per `deletePolicy`

Never parallelize write `use_figma` calls.

## Success condition

After apply, run a fresh diff.
Success = unresolved drift is zero, or only explicitly approved exceptions remain.
```

---

## edit-figma-design

Source: `/Users/jameshou/.agents/skills/edit-figma-design/SKILL.md`

```md
---
name: edit-figma-design
description: Create or update Figma designs directly from a written product or UI description using the Figma MCP authoring tools. Use when the user wants a mockup, wireframe, screen, component, flow, or concept designed in Figma from text, or wants to iterate on an existing Figma file from textual feedback. Despite the name, this skill can start from a new blank file or edit an existing one. Do not use for capture-based workflows that turn a running page into Figma; use `figma-generate-design` for those, and use `implement-design` for code implementation requests. Requires Figma MCP server connection.
metadata:
  mcp-server: figma
---

# Edit Figma Design

## Overview

This skill creates or updates Figma designs directly from a natural-language description. It combines Figma library search with direct file authoring, and uses Warp's broader agent capabilities only when they are needed to make the design more product-aware or codebase-aware.

## When to use this skill

Use this skill when the user wants you to:

- design a new screen, flow, component, or mockup in Figma from a written description
- refine or extend an existing Figma file from text feedback
- create a first-pass wireframe or higher-fidelity design directly in Figma
- align a Figma design to an existing design system or product vocabulary

Do not use this skill when:

- the user wants production code from a design — use `implement-design`
- the user wants to capture a running page or app into Figma — use `figma-generate-design`
- the user only wants to inspect or pull existing Figma context — use `pull-figma-content`

## Prerequisites

- Figma MCP server must be connected and accessible.
  - Verify that `search_design_system`, `create_new_file`, and `use_figma` are available.
- Gather the minimum information needed to proceed:
  - what should be designed
  - whether to use an existing Figma file or create a new one
  - whether the result should align to an existing design system or codebase
- Ask clarifying questions only when the user has not already given enough detail to start. Keep them short and batch them into one message when possible.

## Required Workflow

**Follow these steps in order. Do not skip steps.**

### Step 1: Confirm this is a Figma-authoring request

If the user is actually asking for implementation, stop and consult `implement-design`.

If the user wants a screenshot-to-Figma or webpage capture flow, stop and consult `figma-generate-design`. That skill is for capture-based workflows; this skill is for text-to-design authoring.

### Step 2: Resolve the destination file first

Both `search_design_system` and `use_figma` need a `fileKey`, so determine the destination before searching or editing.

**If the user provided an existing Figma URL or file key:**

- Extract and use that `fileKey`.
- Reuse the provided URL when you respond.

**If the user wants a new file:**

1. Decide on a clear file name from the request.
2. If the user already provided a `planKey`, use it.
3. Otherwise call the Figma MCP `whoami` tool to inspect the authenticated Figma user and available plans. This is not the shell `whoami` command.
4. If there is exactly one plan, use its `key`.
5. If there are multiple plans, ask the user which team or organization to use.
6. Call `create_new_file(editorType="design", fileName=..., planKey=...)`.
7. Save the returned `fileKey` and URL. Share the URL once the first usable draft is ready.

### Step 3: Gather the right context, but only when it is needed

Decide how much non-Figma context is actually necessary.

**Stay inside Figma MCP only** when the user wants an exploratory concept, wireframe, or mockup and does not ask for codebase alignment.

**Use Warp agent context selectively** when the user wants the design to match an existing product or design system:

- read project rules from `AGENTS.md` and/or `WARP.md` if they exist
- use semantic codebase search, grep, and file reads to find relevant components, product vocabulary, layout patterns, and design-token sources
- use other MCP sources or web search only when the prompt directly depends on them, such as product requirements in another system or explicit inspiration requests
- do not edit code, run REPL commands, or use computer use as part of this skill's normal workflow

### Step 4: Search the design system before authoring

Call `search_design_system` with the resolved `fileKey` before creating new components or styles.

Search for the most reusable assets first:

- components and component sets
- variables and token-like values
- styles for color, typography, spacing, or effects

Start with the user's domain terms and any names discovered from project rules or codebase search.

If needed, narrow follow-up searches with returned library keys rather than immediately broadening the search.

Prefer reusing and importing matches over recreating them from scratch.

### Step 5: Prepare `use_figma` safely

Before the first `use_figma` call, plan the edit sequence and follow the tool's required Plugin API constraints.

Keep the authoring plan incremental:

1. create page and frame structure
2. establish layout and major sections
3. reuse or import design-system assets
4. apply variables, styles, and typography
5. add content and polish
6. make targeted revisions based on what the file now contains

### Step 6: Edit the design in small `use_figma` steps

Use multiple small `use_figma` calls instead of one giant script.

Good step boundaries:

- create a page and top-level frames
- lay out a header, sidebar, hero, or content region
- import or place one family of reusable components
- bind colors, text styles, or spacing variables
- update copy, states, or alignment for a specific section

After each step, inspect the result and only continue once the previous step succeeded.

When creating anything component-like, prefer imported library assets discovered in Step 4.

### Step 7: Hand back the design and next options

When the first usable draft is ready:

- return the Figma URL if you have it
- summarize what you created or updated at a high level
- ask whether the user wants revisions in Figma

If the user asks to implement the approved design in code, stop using this skill and consult `implement-design`.

## Warp-agent guidance

Use Warp's broader capabilities to reduce manual prompting, not to add unnecessary work.

**Good uses of Warp agent capabilities in this skill:**

- finding existing component names or design tokens in the repo
- reading project rules that constrain layout, naming, or branding
- pulling product requirements from other connected systems when the user explicitly relies on them

**Usually unnecessary for this skill:**

- shell commands or REPL access
- code edits
- computer-use validation
- broad web research without a specific user request

## Examples

### Example 1: New file from a product description

User says: "Design a billing overview screen in Figma for our desktop app. Use our existing design system and create a new file."

**Actions:**

1. Confirm this is Figma authoring, not code implementation.
2. Resolve the destination by calling `whoami` if needed, then `create_new_file`.
3. Read `AGENTS.md` or `WARP.md`, or search the codebase only if needed to understand billing terminology and existing components.
4. Call `search_design_system` with billing-related queries.
5. Build the screen in small `use_figma` steps.
6. Return the new Figma file URL and offer to revise.

### Example 2: Update an existing Figma file

User says: "Add an onboarding checklist to this Figma file: https://figma.com/design/FILEKEY/Product?node-id=1-2"

**Actions:**

1. Extract the `fileKey` from the existing URL.
2. Search the design system for checklist, card, badge, and progress assets before creating anything new.
3. Use incremental `use_figma` calls to add the new section.
4. Return the same Figma URL and summarize the change.

### Example 3: Pure exploratory concept

User says: "Create a first-pass mobile workout planner mockup in Figma. It doesn't need to match my codebase yet."

**Actions:**

1. Create a new file if needed.
2. Skip codebase search and project-rule inspection.
3. Use `search_design_system` only to reuse any relevant Figma library assets.
4. Build the concept directly in Figma with small `use_figma` steps.
5. Share the file link and ask what to refine next.

## Common issues and responses

### Issue: The user hasn't said whether to use an existing file or a new one

Ask one direct question that resolves the destination. Do not start `search_design_system` or `use_figma` until you have a `fileKey`.

### Issue: Multiple Figma plans are available for `create_new_file`

Ask the user which team or organization to use. Do not guess.

### Issue: The user wants the design to match existing product conventions, but the request is vague

Read the project's rules first. Then use targeted codebase search to gather only the components and conventions relevant to the requested surface.

### Issue: The user asks for both a Figma design and implementation

Create or update the Figma design first only if the user's request is primarily about authoring in Figma. If the request is primarily about implementation, consult `implement-design` instead. After the design is approved, implementation can follow in a separate step.

### Issue: `use_figma` fails or the script is getting large

Break the task into smaller `use_figma` calls. Prefer structure first, then styling, then targeted revisions.

## Additional resources

- [Figma MCP Server Documentation](https://developers.figma.com/docs/figma-mcp-server/)
- [Figma MCP Server Tools and Prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
```
