# Design System — imToken Webapp

## 1. Visual Theme & Atmosphere

imToken Webapp is a lightweight, cross-platform portal to the tokenized world, accessible anywhere a user has a browser and internet connection. Rather than behaving like just another crypto wallet, it is designed as an explorer interface to tokens, token functions, and blockchain-based value on top of the open internet. Its positioning is broad by intent: from newcomers discovering tokens for the first time to everyday users sharing, claiming, and using digital value without platform lock-in or pre-install barriers. The experience is guided by a clear product philosophy: tokens before wallets, access before setup, openness before dependency, and human empowerment over institutional gatekeeping. Every design decision should make token journeys feel more natural, more legible, and more immediate, so anyone can enter the token economy just in time, on any screen, from anywhere.

The visual identity is built on a clean, high-contrast aesthetic. Light surfaces (`#FFFFFF`) dominate the canvas, providing maximum contrast and visual clarity for dense financial data. A single brand blue (`#007FFF`) serves as the primary interactive accent, applied consistently to links, focus rings, active states, and a tightly controlled set of brand gradient moments. The palette is deliberately restrained — one accent color for every interactive element, avoiding chromatic competition.

Typography is anchored in **Noto Sans** — a clean, humanist sans-serif with broad multilingual coverage. Three weights are used: Regular (400) for body and supporting text, Medium (500) for emphasis and section titles, and Bold (700) for headings and financial numbers. The type scale ranges from 10px (`tabLabel`) to 32px (`heroTitle`), with all styles sharing a uniform 0.04em letter spacing and either 140% or 130% line height. Japanese content uses **Noto Sans JP** and Simplified Chinese uses **Noto Sans SC** as locale-specific fallbacks.

Dark mode is a first-class citizen. The dark palette uses iOS-system-aligned grays (`#1C1C1E` background, `#2C2C2E` modal sections) with adapted text colors (`#D6D7E0` primary, `#8B8B91` secondary) for comfortable low-light sessions. Brand blue shifts to `#066BD2` for dark-surface actions, maintaining perceived emphasis without alpha-blending dependencies.

**Key Characteristics:**
- Cross-platform: one design system serving mobile, pad, and web — responsive from 320px to 1200px+
- Noto Sans with three weights (400, 500, 700) — hierarchy through size and weight, not font-family changes
- Type scale: 10px → 12px → 14px → 16px → 20px → 24px → 32px with two line-height modes (140% normal, 130% tight)
- Pure white `#FFFFFF` for light-mode page and card surfaces
- Single brand accent: Blue `#007FFF` reserved for all interactive and brand elements
- Token-centric data display — financial information presented in clean, scannable layouts
- Border radius scale: 4px (sm), 8px (xs), 10px (md), 16px (lg), 9999px (full/pill)
- Dark mode as equal citizen — near-black `#1C1C1E` with elevated sections at `#2C2C2E`
- Semantic color categories: success (green `#4BCE71`), error (red `#F3636F`), warning (orange `#FC8C4D`)
- All alpha-channel tokens pre-composited to solid equivalents for cross-surface stability

## 2. Color Palette & Roles

### Primitive Colors

#### White

| Token | Value | Description |
|-------|-------|-------------|
| `white` | `#FFFFFF` | Pure white — light mode surfaces, text on dark backgrounds |
| `white.0` | `#FFFFFF00` | Fully transparent white — gradient feathered edge start |
| `white.80` | `#FFFFFFCC` | White at 80% — frosted glass / backdrop blur in light mode |

#### Black

| Token | Value | Description |
|-------|-------|-------------|
| `black` | `#000000` | Pure black — OLED-optimized dark mode gradient base |
| `black.80` | `#000000CC` | Black at 80% — dark mode backdrop scrim for modal overlays |

#### Gray

| Token | Value | Description |
|-------|-------|-------------|
| `gray.0` | `#01030600` | Transparent near-black — dark mode tab bar gradient start |
| `gray.50` | `#F9FAFB` | Lightest gray — modal surface in light mode |
| `gray.100` | `#F0F1F3` | Light gray — secondary surfaces, chip backgrounds |
| `gray.300` | `#D6D7E0` | Mid-light gray — primary body text in dark mode |
| `gray.350` | `#8B8B91` | Dark-mode mid gray — secondary text in dark mode |
| `gray.450` | `#B4B4BC` | Dark-mode light gray — primary icon stroke in dark mode |
| `gray.500` | `#B6B7C1` | Dark-surface medium gray — secondary fill in dark mode |
| `gray.700` | `#49494C` | Dark-mode dark gray — placeholder text in dark mode |
| `gray.800` | `#2C2C2E` | Deep dark gray — modal section surface in dark mode |
| `gray.850` | `#1F1F1F` | Deeper dark gray — dark mode gradient stop |
| `gray.880` | `#2C2C30` | Near-surface gray — border/divider in dark mode |
| `gray.900` | `#1C1C1E` | Near-black gray — primary dark mode surface (iOS system black) |
| `gray.950` | `#010306` | Darkest near-black — OLED tab bar gradient end |

#### Navy

| Token | Value | Description |
|-------|-------|-------------|
| `navy.50` | `#ECEDF0` | Near-white navy tint — border/divider in light mode |
| `navy.200` | `#D0D2DB` | Pale navy tint — placeholder text in light mode |
| `navy.700` | `#A0A5B7` | Muted navy — secondary text and icons in light mode |
| `navy.800` | `#003160` | Deep navy — dark mode hero gradient end stop |
| `navy.900` | `#111D4A` | Darkest navy — primary text, icons, fills in light mode |

#### Blue

| Token | Value | Description |
|-------|-------|-------------|
| `blue.50` | `#F9FDFF` | Near-white blue tint — light mode gradient start |
| `blue.100` | `#D6EBFF` | Very light blue — hero gradient end in light mode |
| `blue.200` | `#EEF7FF` | Pale blue — XAUT card gradient accent |
| `blue.500` | `#007FFF` | Brand blue — primary action color, links, interactive affordance |
| `blue.600` | `#066BD2` | Dark-adapted brand blue — action color in dark mode |
| `blue.800` | `#004C99` | Dark blue shade — pressed states, deep branded emphasis |
| `blue.500_a8` | `rgba(0, 127, 255, 0.08)` | 8% blue — selected surfaces, decorative accents |
| `blue.500_a20` | `rgba(0, 127, 255, 0.2)` | 20% blue — soft fills, badges, informational backgrounds |
| `blue.500_a40` | `rgba(0, 127, 255, 0.4)` | 40% blue — medium-emphasis fills and overlay states |
| `blue.500_a60` | `rgba(0, 127, 255, 0.6)` | 60% blue — stronger tinted fills and transitional states |

#### Green

| Token | Value | Description |
|-------|-------|-------------|
| `green.500` | `#4BCE71` | Success green — connected, positive, completed states |
| `green.800` | `#2D7C44` | Dark green shade — pressed success states |
| `green.500_a20` | `rgba(75, 206, 113, 0.2)` | 20% green — soft success backgrounds |
| `green.500_a40` | `rgba(75, 206, 113, 0.4)` | 40% green — medium success fills |
| `green.500_a60` | `rgba(75, 206, 113, 0.6)` | 60% green — stronger success surfaces |

#### Red

| Token | Value | Description |
|-------|-------|-------------|
| `red.500` | `#F3636F` | Error red — destructive, failed, critical states |
| `red.800` | `#923B43` | Dark red shade — pressed destructive states |
| `red.500_a20` | `rgba(243, 99, 111, 0.2)` | 20% red — subtle destructive backgrounds |
| `red.500_a40` | `rgba(243, 99, 111, 0.4)` | 40% red — medium alert fills |
| `red.500_a60` | `rgba(243, 99, 111, 0.6)` | 60% red — stronger destructive fills |

#### Orange

| Token | Value | Description |
|-------|-------|-------------|
| `orange.500` | `#FC8C4D` | Warning orange — caution, offline, attention states |
| `orange.800` | `#97542E` | Dark orange shade — pressed warning states |
| `orange.500_a20` | `rgba(252, 140, 77, 0.2)` | 20% orange — subtle warning backgrounds |
| `orange.500_a40` | `rgba(252, 140, 77, 0.4)` | 40% orange — medium warning fills |

---

### Semantic Roles — Light

#### Background

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `background.general` | `#FFFFFF` | Base page surface under the default page gradient |
| `background.card` | `#FFFFFF` | Card surface background |
| `background.modal` | `#F9FAFB` | Modal container background — slightly off-white |
| `background.modal_section` | `#FFFFFF` | Modal section panel background |
| `background.modal_section_inner` | `#F0F1F3` | Inner modal subsection — light gray grouping |
| `background.backdrop` | `#FFFFFFCC` | Backdrop blur overlay — frosted glass |

#### Page Background Semantics

| Semantic Use | Light | Dark | Application |
|------|-------|------|-------------|
| General page background | `gradient.general` = `#F9FDFF` → `#F0F1F3` (180°) | `gradient.general` = `#000000` → `#1F1F1F` (180°) | Default for most pages |
| Token main / promo background | `gradient.main` = `#F9FDFF` → `#D6EBFF` (180°) | `gradient.main` = `#000000` → `#003160` (180°) | Token main page, claim page, and other promotional pages |

#### Text

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `text.core` | `#111D4A` | Core information — balances, amounts, page headings |
| `text.primary` | `#111D4A` | Primary titles — subheadings, labels |
| `text.secondary` | `#A0A5B7` | Supporting and secondary text |
| `text.action` | `#007FFF` | Interactive text — links, CTAs, affordance |
| `text.inverse` | `#FFFFFF` | Text on branded/dark surfaces |
| `text.placeholder` | `#D0D2DB` | Placeholder and empty state hints |
| `text.success` | `#4BCE71` | Positive inline messaging |
| `text.error` | `#F3636F` | Destructive and validation messaging |
| `text.warning` | `#FC8C4D` | Caution and offline messaging |

#### Stroke

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `stroke.icon_primary` | `#111D4A` | Primary icon stroke — full navy |
| `stroke.icon_secondary` | `#A0A5B7` | Secondary icon stroke — muted navy |
| `stroke.logo` | `#111D4A` | Brand/token-logo stroke |
| `stroke.icon_inverse` | `#FFFFFF` | Icons on branded/dark surfaces |

#### Border

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `border.default` | `#ECEDF0` | Default border and divider |

#### Fill

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `fill.action` | `#007FFF` | Primary action fill — interactive chips, badges, icons |
| `fill.action_subtle` | `rgba(0, 127, 255, 0.2)` | Subtle action fill — low-emphasis pills, chips |
| `fill.icon_chip` | `#F0F1F3` | Icon chip background — gray pill |
| `fill.secondary` | `#111D4A` | Secondary solid fill — secondary buttons, badges |
| `fill.tertiary` | `#FFFFFF` | Tertiary fill — ghost buttons, outlined backgrounds |
| `fill.logo` | `#111D4A` | Logo fill color |
| `fill.success` | `#4BCE71` | Filled success surface |
| `fill.success_subtle` | `rgba(75, 206, 113, 0.2)` | Soft success fill — chips, secondary positive |
| `fill.error` | `#F3636F` | Filled error surface |
| `fill.error_subtle` | `rgba(243, 99, 111, 0.2)` | Soft error fill — alert chips |
| `fill.warning` | `#FC8C4D` | Filled warning surface |
| `fill.warning_subtle` | `rgba(252, 140, 77, 0.2)` | Soft warning fill — caution chips |

#### Gradient

| Role | Stops | Description |
|------|-------|-------------|
| `gradient.general` | `#F9FDFF` → `#F0F1F3` (180°) | General page background gradient — default for most pages |
| `gradient.main` | `#F9FDFF` → `#D6EBFF` (180°) | Token main / promo page background gradient |
| `gradient.xaut_card` | `#FFFFFF99` → `#EEF7FF` (180°) | XAUT card — glassmorphism to pale blue |
| `gradient.bar_backdrop` | `#FFFFFF00` → `#FFFFFF` (180°) | Tab bar backdrop — transparent to solid white |
| `gradient.button_primary_fill` | Radial `#0CC5FF` → `#007FFF` (opacity 0.7) | Primary CTA fill gradient — reserved for the primary button surface only |

#### Status

| Role | Resolved Value | Subtle Variant |
|------|----------------|----------------|
| `status.success` | `#4BCE71` | `rgba(75, 206, 113, 0.2)` |
| `status.error` | `#F3636F` | `rgba(243, 99, 111, 0.2)` |
| `status.warning` | `#FC8C4D` | `rgba(252, 140, 77, 0.2)` |

---

### Semantic Roles — Dark

#### Background

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `background.general` | `#1C1C1E` | Base page surface under the default page gradient — near-black (iOS system) |
| `background.card` | `#1C1C1E` | Card surface — blends with page background |
| `background.modal` | `#1C1C1E` | Modal container background |
| `background.modal_section` | `#2C2C2E` | Modal section panel — slightly elevated |
| `background.modal_section_inner` | `#1C1C1E` | Inner modal subsection — matches card surface |
| `background.backdrop` | `#000000CC` | Backdrop scrim — 80% black |

#### Text

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `text.core` | `#FFFFFF` | Core information — balances, amounts, page headings |
| `text.primary` | `#D6D7E0` | Primary titles — mid-light gray |
| `text.secondary` | `#8B8B91` | Supporting and secondary text |
| `text.action` | `#066BD2` | Interactive text — dark-adapted brand blue |
| `text.inverse` | `#FFFFFF` | Text on branded surfaces |
| `text.placeholder` | `#49494C` | Placeholder and hints |
| `text.success` | `#4BCE71` | Positive messaging |
| `text.error` | `#F3636F` | Destructive messaging |
| `text.warning` | `#FC8C4D` | Caution messaging |

#### Stroke

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `stroke.icon_primary` | `#B4B4BC` | Primary icon stroke |
| `stroke.icon_secondary` | `#8B8B91` | Secondary icon stroke |
| `stroke.logo` | `#FFFFFF` | Logo stroke |
| `stroke.icon_inverse` | `#FFFFFF` | Icons on branded surfaces |

#### Border

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `border.default` | `#2C2C30` | Default border and divider |

#### Fill

| Role | Resolved Value | Description |
|------|----------------|-------------|
| `fill.action` | `#066BD2` | Primary action fill — dark-adapted brand blue |
| `fill.action_subtle` | `rgba(0, 127, 255, 0.2)` | Subtle action fill |
| `fill.icon_chip` | `#2C2C2E` | Icon chip background — deep dark gray |
| `fill.secondary` | `#B6B7C1` | Secondary solid fill — adapted gray |
| `fill.tertiary` | `#1C1C1E` | Tertiary fill — near-black |
| `fill.logo` | `#FFFFFF` | Logo fill — pure white |
| `fill.success` | `#4BCE71` | Filled success surface |
| `fill.success_subtle` | `rgba(75, 206, 113, 0.2)` | Soft success fill |
| `fill.error` | `#F3636F` | Filled error surface |
| `fill.error_subtle` | `rgba(243, 99, 111, 0.2)` | Soft error fill |
| `fill.warning` | `#FC8C4D` | Filled warning surface |
| `fill.warning_subtle` | `rgba(252, 140, 77, 0.2)` | Soft warning fill |

#### Gradient

| Role | Stops | Description |
|------|-------|-------------|
| `gradient.general` | `#000000` → `#1F1F1F` (180°) | General page background gradient — black to deep gray for OLED |
| `gradient.main` | `#000000` → `#003160` (180°) | Token main / promo page background gradient — black to deep navy |
| `gradient.xaut_card` | `#151417B3` → `#2C2C2E` (180°) | XAUT card — warm undertone to elevated gray |
| `gradient.bar_backdrop` | `#01030600` → `#010306` (180°) | Tab bar backdrop — transparent to near-black |
| `gradient.button_primary_fill` | Radial `#0CC5FF` → `#007FFF` (opacity 0.7) | Primary CTA fill gradient — reserved for the primary button surface only |

#### Status

| Role | Resolved Value | Subtle Variant |
|------|----------------|----------------|
| `status.success` | `#4BCE71` | `rgba(75, 206, 113, 0.2)` |
| `status.error` | `#F3636F` | `rgba(243, 99, 111, 0.2)` |
| `status.warning` | `#FC8C4D` | `rgba(252, 140, 77, 0.2)` |

## 3. Typography Rules

### Font Family

- **Primary (Latin)**: `"Noto Sans"` — `--font-sans`
- **Japanese**: `"Noto Sans JP"` — `--font-jp`
- **Simplified Chinese**: `"Noto Sans SC"` — `--font-sc`

### Rendering

- `text-rendering: optimizeLegibility`
- `-webkit-font-smoothing: antialiased`
- `-moz-osx-font-smoothing: grayscale`

### Hierarchy

| Role | Token | Size | Weight | Line Height | Letter Spacing |
|------|-------|------|--------|-------------|----------------|
| Hero Title | `heroTitle` | 32px (2rem) | 700 Bold | 140% | 0.04em |
| Hero Amount | `heroAmount` | 24px (1.5rem) | 700 Bold | 140% | 0.04em |
| Section Lead | `sectionLead` | 20px (1.25rem) | 500 Medium | 140% | 0.04em |
| Nav Title | `navTitle` | 16px (1rem) | 700 Bold | 140% | 0.04em |
| Body Primary | `bodyPrimary` | 16px (1rem) | 500 Medium | 140% | 0.04em |
| Action Label | `actionLabel` | 16px (1rem) | 400 Regular | 140% | 0.04em |
| Body Secondary | `bodySecondary` | 14px (0.875rem) | 400 Regular | 140% | 0.04em |
| Section Title | `sectionTitle` | 14px (0.875rem) | 500 Medium | 140% | 0.04em |
| Supporting Text | `supportingText` | 12px (0.75rem) | 400 Regular | 130% | 0.04em |
| Tab Label | `tabLabel` | 10px (0.625rem) | 400 Regular | 140% | 0.04em |

### Font Size Scale

| Token | Value | Use |
|-------|-------|-----|
| `size.xs` | 10px | Tab labels, bottom navigation text |
| `size.sm` | 12px | Auxiliary info, annotations, supporting text |
| `size.md` | 14px | Secondary content, section titles, body secondary |
| `size.lg` | 16px | Navigation titles, body primary, button labels |
| `size.xl` | 20px | Guide titles, section leads |
| `size.2xl` | 24px | Large amount emphasis, hero amounts |
| `size.3xl` | 32px | Article titles, hero titles |

### Principles

- **Single family, three weights**: Noto Sans covers all text with weights 400 (regular), 500 (medium), and 700 (bold). No other weights appear in components.
- **Size creates hierarchy, not font swapping**: All text uses the same typeface family. Hierarchy is established through size differences (10px to 32px), weight contrasts (400 vs 700), and color role shifts (text.core vs text.secondary).
- **Two line-height modes**: Body and heading text uses 140% (normal) for comfortable reading. Supporting text tightens to 130% for compact annotation layouts.
- **Uniform letter spacing**: All roles use 0.04em (4%) letter spacing for consistent rhythm across the interface.

## 4. Component Stylings

### Button

The Button component (`Button/DS-v2`) is defined in Figma as a Component Set with 42 variants across 7 hierarchies × 3 sizes × 2 states. All dimensions, colors, and typography are bound to design-system variables. The component exposes a single `Label` TEXT property.

#### Layout & Structure

- **Layout mode**: Horizontal auto-layout, both axes centered (`CENTER / CENTER`)
- **Sizing**: Width HUGs label content; height is FIXED per size token
- **Shape**: `radius/full` → `9999px` (pill) — applied to all four corners via variable binding
- **Disabled state**: Entire component at `40%` opacity (`opacity: 0.4`)
- **Component property**: `Label` (TEXT) — controls the button label string

#### Size Scale

| Size | Height token | Height | Padding token | PaddingX | Text style | Font |
|------|-------------|--------|--------------|----------|------------|------|
| `lg` | `size/52` | 52px | `spacing/16` | 16px | `actionLabel` | Noto Sans 16px Regular (400) |
| `default` | `size/48` | 48px | `spacing/16` | 16px | `actionLabel` | Noto Sans 16px Regular (400) |
| `sm` | `size/44` | 44px | `spacing/12` | 12px | `sectionTitle` | Noto Sans 14px Medium (500) |

#### Hierarchy Styles

**Primary** — reserved exclusively for the primary CTA surface
- Fill: `component/button/primary/fill` paint style — radial gradient `#0CC5FF → #007FFF` at 70% opacity
- Stroke: `component/button/primary/stroke` paint style — linear gradient `rgba(255,255,255,0.5) → rgba(12,197,255,0.07)`, 1px inside
- Text color: `text/inverse` (`#FFFFFF` light / `#FFFFFF` dark)
- Do not apply this gradient to cards, chips, icon buttons, or secondary actions

**Secondary**
- Fill: `fill/secondary` → `#111D4A` light / `#B6B7C1` dark (SOLID, variable-bound)
- Stroke: none
- Text color: `text/inverse` (`#FFFFFF` light / `#FFFFFF` dark)

**Outline**
- Fill: transparent (no fill)
- Stroke: `border/default` → `#ECEDF0` light / `#2C2C30` dark (SOLID, 1px inside, variable-bound)
- Text color: `text/primary` → `#111D4A` light / `#D6D7E0` dark

**Ghost**
- Fill: transparent (no fill)
- Stroke: none
- Text color: `text/secondary` → `#A0A5B7` light / `#8B8B91` dark
- Hover: `fill/icon_chip` background tint (`#F0F1F3` light / `#2C2C2E` dark)

**Foreground**
- Fill: `fill/secondary` → `#111D4A` light / `#B6B7C1` dark (SOLID, variable-bound)
- Stroke: none
- Text color: `text/inverse` (`#FFFFFF` light / `#FFFFFF` dark)

**Destructive**
- Fill: transparent (no fill)
- Stroke: none
- Text color: `text/error` → `#F3636F` (same light and dark)

**Link**
- Fill: transparent (no fill)
- Stroke: none
- Text color: `text/action` → `#007FFF` light / `#066BD2` dark
- Hover: underline, offset 4px

#### Variable Binding Map

| Node | Property | Variable | Scope |
|------|----------|----------|-------|
| Frame | `cornerRadius` (all corners) | `radius/full` | `CORNER_RADIUS` |
| Frame (lg, default) | `paddingLeft`, `paddingRight` | `spacing/16` | `GAP` |
| Frame (sm) | `paddingLeft`, `paddingRight` | `spacing/12` | `GAP` |
| Frame (lg) | `minHeight` | `size/52` | `WIDTH_HEIGHT` |
| Frame (default) | `minHeight` | `size/48` | `WIDTH_HEIGHT` |
| Frame (sm) | `minHeight` | `size/44` | `WIDTH_HEIGHT` |
| Frame (Secondary, Foreground) | `fills[0].color` | `fill/secondary` | `FRAME_FILL` |
| Frame (Outline) | `strokes[0].color` | `border/default` | `STROKE_COLOR` |
| Text (Primary, Secondary, Foreground) | `fills[0].color` | `text/inverse` | `TEXT_FILL` |
| Text (Outline) | `fills[0].color` | `text/primary` | `TEXT_FILL` |
| Text (Ghost) | `fills[0].color` | `text/secondary` | `TEXT_FILL` |
| Text (Destructive) | `fills[0].color` | `text/error` | `TEXT_FILL` |
| Text (Link) | `fills[0].color` | `text/action` | `TEXT_FILL` |
| Text (lg, default) | `textStyleId` | `actionLabel` style | 16px Regular |
| Text (sm) | `textStyleId` | `sectionTitle` style | 14px Medium |

#### Figma Component Reference

- **Component Set**: `Button/DS-v2` — page `原子组件/Button`
- **Variant naming**: `Hierarchy={value}, State={Active|Disabled}, Size={lg|default|sm}`
- **Paint styles used**: `component/button/primary/fill`, `component/button/primary/stroke`

### IconButton

Circular icon-only buttons for toolbar and nav actions.

| Variant | Background | Icon Color |
|---------|------------|------------|
| `ghost` | transparent → `fill.icon_chip` on hover | `stroke.icon_secondary` (`#A0A5B7` / `#8B8B91`) |
| `muted` | `fill.icon_chip` (`#F0F1F3` / `#2C2C2E`) | `stroke.icon_primary` (`#111D4A` / `#B4B4BC`) |
| `foreground` | `fill.secondary` (`#111D4A` / `#B6B7C1`) | `stroke.icon_inverse` (`#FFFFFF`) |

| Size | Dimensions | Icon Size |
|------|------------|-----------|
| `sm` | 36×36px | 16px |
| `md` | 40×40px | 20px |
| `lg` | 48×48px | 20px |

### ActionButton & ActionBar

Full-width action buttons arranged in a responsive grid.

- **Primary**: `fill.action` (`#007FFF` / `#066BD2`) background, `text.inverse` (`#FFFFFF`) text
- **Secondary**: `fill.icon_chip` (`#F0F1F3` / `#2C2C2E`) background, `text.primary` (`#111D4A` / `#D6D7E0`) text
- Height: 48px, `radius.full` (9999px), `sectionTitle` — 14px, medium (500)
- Icon: 16px with stroke-width 2.5
- Grid: 2-column or 4-column, gap 12px

### Badge

Status pills with icon support and semantic color variants.

| Variant | Background | Text |
|---------|------------|------|
| `action` | `fill.action_subtle` (`rgba(0,127,255,0.2)`) | `text.action` (`#007FFF` / `#066BD2`) |
| `success` | `fill.success_subtle` (`rgba(75,206,113,0.2)`) | `text.success` (`#4BCE71`) |
| `neutral` | `fill.icon_chip` (`#F0F1F3` / `#2C2C2E`) | `text.primary` (`#111D4A` / `#D6D7E0`) |
| `error` | `fill.error_subtle` (`rgba(243,99,111,0.2)`) | `text.error` (`#F3636F`) |
| `warning` | `fill.warning_subtle` (`rgba(252,140,77,0.2)`) | `text.warning` (`#FC8C4D`) |

| Size | Padding | Font |
|------|---------|------|
| `sm` | px-8, py-2 | 10px (`tabLabel`) |
| `md` | px-12, py-4 | 12px (`supportingText`) |
| `lg` | px-16, py-8 | 12px (`supportingText`) |

Shape: `radius.full` (9999px), medium (500) weight. Optional leading icon at 16px.

### Avatar

Token and user avatars with image or letter fallback.

| Size | Dimensions | Image Size |
|------|------------|------------|
| `xs` | 28×28px | 16px |
| `sm` | 32×32px | 20px |
| `md` | 40×40px | 24px |
| `lg` | 48×48px | 32px |

- Shape: `radius.full` (9999px)
- Custom `bgColor` prop for token-branded backgrounds
- Fallback: bold letter in the token's brand color

### Card

Multi-slot card component with flexible composition. Token v5 pattern defines: background `background.card`, title `sectionTitle`, body `bodySecondary`, padding 16px, radius `radius.md` (10px).

- Background: `background.card` (`#FFFFFF` / `#1C1C1E`)
- Text: `text.primary` (`#111D4A` / `#D6D7E0`)
- Shape: `radius.md` (10px)
- Border: 1px solid `border.default` (`#ECEDF0` / `#2C2C30`)
- Padding: 16px (default), 12px (`size="sm"`)
- Gap: 16px between slots (12px for small)
- Slots: `CardHeader`, `CardTitle`, `CardDescription`, `CardAction`, `CardContent`, `CardFooter`
- Footer: `border.default` top border, `fill.icon_chip` at 50% opacity background

### SectionPanel

Section-level container for dashboard content.

| Variant | Shadow |
|---------|--------|
| `default` | `--shadow-card` |
| `elevated` | `--shadow-card-md` |
| `flat` | none |

| Padding | Value |
|---------|-------|
| `sm` | 16px |
| `md` | 20px |
| `lg` | 24px |
| `xl` | 24px → 32px at `sm:` breakpoint |

- Shape: `radius.md` (10px), `border.default`, `background.card`

### IconBox

Large icon containers for onboarding, hero, and feature sections.

| Variant | Background | Icon Color |
|---------|------------|------------|
| `action` | `fill.action` (`#007FFF` / `#066BD2`) | `stroke.icon_inverse` (`#FFFFFF`) |
| `action-soft` | `fill.action_subtle` (`rgba(0,127,255,0.2)`) | `text.action` (`#007FFF` / `#066BD2`) |
| `success` | `fill.success` (`#4BCE71`) | `stroke.icon_inverse` (`#FFFFFF`) |
| `neutral` | `fill.icon_chip` (`#F0F1F3` / `#2C2C2E`) | `stroke.icon_primary` (`#111D4A` / `#B4B4BC`) |
| `foreground` | `fill.secondary` (`#111D4A` / `#B6B7C1`) | `stroke.icon_inverse` (`#FFFFFF`) |

| Size | Dimensions | Corner Radius | Icon Size |
|------|------------|---------------|-----------|
| `xs` | 32×32px | `radius.xs` (8px) | 16px |
| `sm` | 40×40px | `radius.md` (10px) | 20px |
| `md` | 64×64px | `radius.lg` (16px) | 32px |
| `lg` | 88×88px | `radius.lg` (16px) | 44px |
| `xl` | 96×96px | `radius.lg` (16px) | 48px |
| `2xl` | 122×122px | `radius.lg` (16px) | 64px |

### Chip

Selectable pill chips for filters and suggestions.

- Default: `border.default` (`#ECEDF0` / `#2C2C30`), `background.card` (`#FFFFFF` / `#1C1C1E`), `text.primary`
- Selected: `fill.action` border, `blue.500_a8` background, `text.action`
- Height: 32px (sm), 36px (md)
- Shape: `radius.full` (9999px)
- Font: 14px (`sectionTitle`), medium (500) weight

### ChatBubble

Agent chat message bubbles.

- **Incoming**: `fill.icon_chip` (`#F0F1F3` / `#2C2C2E`) background, `text.secondary` text
- **Outgoing**: `fill.action` (`#007FFF` / `#066BD2`) background, `text.inverse` (`#FFFFFF`) text
- Shape: `radius.lg` (16px)
- Padding: 16px
- Font: 14px (`bodySecondary`), regular (400)

### Input

Standard text input field.

- Height: 48px (from token v5 `fieldHeight`)
- Shape: `radius.xs` (8px)
- Border: 1px solid `border.default` (`#ECEDF0` / `#2C2C30`)
- Background: transparent
- Placeholder: `text.placeholder` (`#D0D2DB` / `#49494C`)
- Focus: `fill.action` (`#007FFF`) border, ring
- Font: 16px (`bodyPrimary`)
- Padding: 12px horizontal (from token v5 `fieldPaddingX`)

### Progress

Linear progress bar with animated fill.

| Variant | Track | Bar |
|---------|-------|-----|
| `action` | `blue.500_a8` | `fill.action` (`#007FFF` / `#066BD2`) |
| `success` | `green.500_a20` | `fill.success` (`#4BCE71`) |

| Size | Height |
|------|--------|
| `sm` | 4px |
| `md` | 8px |

- Shape: `radius.full` (9999px)
- Animation: 420ms with `--ease-emphasis` timing function

### NavItem

Sidebar navigation items.

- Active: `fill.action` (`#007FFF` / `#066BD2`) background, `text.inverse` (`#FFFFFF`) text
- Inactive: `text.secondary` (`#A0A5B7` / `#8B8B91`), hover: `fill.icon_chip` background
- Destructive: `text.error` (`#F3636F`), hover: `fill.error_subtle` background
- Height: 44px
- Shape: `radius.xs` (8px)
- Icon: 16px, leading
- Font: 14px (`sectionTitle`), medium (500) weight
- Spacing: mb-4 between items

### StepCard

Onboarding step indicators with tri-state visuals.

| State | Border | Background | Icon Container |
|-------|--------|------------|----------------|
| `completed` | `green.500_a40` | `green.500_a20` | `fill.success` bg, `stroke.icon_inverse` icon |
| `active` | `fill.action_subtle` | `blue.500_a8` | `fill.action_subtle` bg, `text.action` icon |
| `pending` | `border.default` | `background.card` | `fill.action_subtle` bg, `text.action` icon |

- Shape: `radius.md` (10px)
- Icon container: 40×40px, `radius.full`
- Completed icon overrides to checkmark
- Title: 16px (`bodyPrimary`), bold (700)
- Detail: 14px (`bodySecondary`), `text.secondary`

### AssetRow

Token display row for portfolio views.

- Layout: flex, `justify-between`, `items-center`
- Padding: px-12, py-12
- Shape: `radius.xs` (8px)
- Left: Avatar + symbol (16px `bodyPrimary` medium) + amount (14px `bodySecondary` `text.secondary`)
- Right: value (16px `bodyPrimary` medium) + detail (14px `bodySecondary`, custom token color)

### HoldingCard

Dashboard stat card for holdings.

- Shape: `radius.lg` (16px), border `border.default`, `background.card`
- Shadow: `--shadow-card`
- Padding: 20px
- Label: 14px `bodySecondary`, `text.secondary`
- Amount: 24px (`heroAmount`), bold (700), `text.core`
- Suffix: 12px (`supportingText`), regular (400), `text.secondary`
- Value: 14px (`sectionTitle`), medium (500), `text.primary`
- Change: 12px (`supportingText`), regular (400), `text.success`
- P&L: 12px `supportingText`, `text.secondary`

### TaskCard

Trading agent task cards with stats and progress.

- Shape: `radius.lg` (16px), border `border.default`
- Padding: 16px
- Title: 14px `sectionTitle`, medium (500)
- Subtitle: 12px `supportingText`, `text.secondary`
- Stats grid: 3-column (default) or 2-column (compact), gap 12px
- Progress: `sm` (4px) track, `blue.500_a8` → `fill.action` fill
- Actions: `border.default` top border, pt-16, flex with gap-8

### StatCell

Minimal label-value pair for data grids.

- Label: 12px (`supportingText`), `text.secondary`
- Value: 14px (`sectionTitle`), medium (500), `text.primary`
- Gap: mt-4 (4px) between label and value

### FeatureItem

Feature highlight rows for onboarding screens.

- Shape: `radius.lg` (16px)
- Background: `blue.500_a8`
- Padding: px-16, py-12
- Icon container: 32×32px, `radius.full`, `background.card`, `stroke.icon_primary` icon
- Text: 14px (`sectionTitle`), medium (500), `text.primary`

### ChecklistCard

Task checklist items.

- Shape: `radius.xs` (8px), border `border.default`
- Padding: 16px
- Title: 14px `sectionTitle`, medium (500)
- Description: 12px `supportingText`, `text.secondary`
- Optional `tone` background color prop
- Optional action slot (mt-12)

### WebNav

Web navigation bar from token v5 component definitions.

- Height: 68px (signed-out and signed-in)
- Background: `background.general` (`#FFFFFF` / `#1C1C1E`)
- Title: `navTitle` (16px bold)
- Icon: `stroke.icon_primary` (`#111D4A` / `#B4B4BC`)
- Border: `border.default` (`#ECEDF0` / `#2C2C30`) bottom border
- Padding: 16px horizontal

### Modal

Modal component from token v5 component definitions.

- Background: `background.modal` (`#F9FAFB` / `#1C1C1E`)
- Title: `sectionTitle` (14px medium)
- Body: `bodySecondary` (14px regular)
- Padding: 16px horizontal, 8px top
- Content top gap: 72px
- Close button: 32×32px
- Drag handle: 36×4px
- Shape: `radius.lg` (16px)

**Modal Form (pattern)**
- Field background: `background.modal_section` (`#FFFFFF` / `#2C2C2E`)
- Field padding: 12px horizontal
- Field height: 48px
- Section gap: 32px
- Action gap: 32px

### MobileNav

Mobile navigation from token v5 component definitions.

**Primary**
- Height: 90px
- Padding: 16px horizontal
- Title: `navTitle` (16px bold)
- Icon: `stroke.icon_primary`

**Secondary**
- Height: 56px
- Padding: 16px horizontal
- Title: `navTitle` (16px bold)
- Icon: `stroke.icon_primary`

### TokenList

Token list control from token v5 component definitions.

**Default / Expand**
- Control height: 32px
- Text: `bodyPrimary` (16px medium)
- Icon: `stroke.icon_primary`

**Token Item (pattern)**
- Primary text: `bodyPrimary` (16px medium)
- Secondary text: `bodySecondary` (14px regular)
- Icon size: 40px
- Internal gap: 12px
- Row height: 62px

### Menu

Menu component from token v5 component definitions.

- Background (signed-out): `background.card`
- Background (signed-in): `background.card`
- Title: `sectionTitle` (14px medium)
- Body: `bodySecondary` (14px regular)
- Padding: 16px

## 5. Layout Principles

### Spacing System

- **Base unit**: 8px
- **Grid**: Strict 4pt sub-grid — all spacing, padding, margins, and sizes must be multiples of 2px minimum
- **Scale** (from token v5 primitives): 2, 4, 8, 10, 12, 14, 15, 16, 20, 24, 32, 40, 42, 48, 62, 72px

| Token | Use |
|-------|-----|
| 2–4px | Micro spacing (badge padding, label gaps, drag handle height) |
| 8px | Icon gaps, tight element spacing, row gaps |
| 10px | Component internal gaps (compact) |
| 12px | Field padding, compact list gaps, component internal gaps |
| 14–15px | Info-card content spacing, card row spacing |
| 16px | Standard container padding (cards, panels, sections, nav) |
| 20px | Elevated panel padding, medium content separation |
| 24px | Large panel padding, intra-section gaps |
| 32px | Section-level separation, action groups, modal form gaps |
| 40–42px | Large content separation, layout offsets |
| 48px | Major section separation, modal tour layouts |
| 62px | Token list row height, info-card list spacing |
| 72px | Modal content top gap, large vertical offsets |

### Size Tokens

| Token | Value | Use |
|-------|-------|-----|
| `size.4` | 4px | Drag handle height |
| `size.16` | 16px | Compact icons, small square affordances |
| `size.20` | 20px | Small status-row icons |
| `size.24` | 24px | Standard compact controls and icons |
| `size.32` | 32px | Compact control heights, close buttons, token list height |
| `size.36` | 36px | Drag handle width, compact action elements |
| `size.40` | 40px | Large list icons, icon containers |
| `size.44` | 44px | Touch-friendly heights |
| `size.48` | 48px | Field heights, medium touch controls |
| `size.52` | 52px | Primary button height |
| `size.56` | 56px | Secondary mobile nav height |
| `size.62` | 62px | Token list row height |
| `size.64` | 64px | Tall compact containers |
| `size.68` | 68px | Web navigation height |
| `size.90` | 90px | Primary mobile navigation height |
| `size.343` | 343px | Compact container width |
| `size.356` | 356px | Standard container width |
| `size.375` | 375px | Mobile frame width |
| `size.1200` | 1200px | Wide web container width |

### Grid & Container

- Max content width: 1200px (token v5 `size.1200`) for main webapp content
- Max form/card width: 375px (token v5 `size.375`) for mobile-equivalent views
- Max compact container: 343px (token v5 `size.343`) for compact card content
- Page horizontal padding: 24px (`spacing.24`)
- Content vertical padding: 32px (`spacing.32`)
- Section vertical gap: 48px (`spacing.48`)

### Border Radius Scale

| Token | Value | Use |
|-------|-------|-----|
| `radius.sm` | 4px | Micro elements, progress bars |
| `radius.xs` | 8px | Inputs, small buttons, checklist cards, nav items |
| `radius.md` | 10px | Cards, section panels, buttons, icon box sm |
| `radius.lg` | 16px | Modals, chat bubbles, holding cards, task cards, icon box md+ |
| `radius.full` | 9999px | Pill buttons, badges, avatars, chips, icon buttons, progress bars |

### Whitespace Philosophy

- **Breathing room through card stacking**: Cards (`background.card`) sit on top of the page background system. Most pages use `gradient.general` over `background.general`, while token-led and promotional pages use `gradient.main`. In light mode cards still resolve to `#FFFFFF`, so borders (`border.default`) and shadows define separation. In dark mode cards resolve to `#1C1C1E`, and borders at `#2C2C30` provide subtle edge definition against both dark gradients.
- **Tight within, generous between**: Components have compact internal spacing (12–16px padding) while section-to-section spacing is generous (48px). This creates dense, scannable information blocks separated by clear visual breaks.
- **Financial data density**: Portfolio views, stat grids, and trading cards pack data tightly (4–8px gaps between label/value pairs) while maintaining readability through the text.core / text.secondary color hierarchy.

## 6. Depth & Elevation

| Level | Token | Value | Use |
|-------|-------|-------|-----|
| Flat (Level 0) | — | No shadow | Page background, flat panels |
| Card (Level 1) | `--shadow-card` | `0 1px 3px rgba(17, 29, 74, 0.04), 0 1px 2px rgba(17, 29, 74, 0.06)` | Default section panels, list cards |
| Card Medium (Level 2) | `--shadow-card-md` | `0 2px 8px rgba(17, 29, 74, 0.06)` | Elevated panels, page headers |
| Card Large (Level 3) | `--shadow-card-lg` | `0 8px 24px rgba(17, 29, 74, 0.05)` | Prominent feature cards |
| Icon | `--shadow-icon` | `0 6px 20px rgba(17, 29, 74, 0.08)` | Feature item icon containers |
| CTA Small | `--shadow-cta-sm` | `0 4px 14px rgba(0, 127, 255, 0.22)` | Default primary buttons, outgoing chat bubbles |
| CTA | `--shadow-cta` | `0 8px 28px rgba(0, 127, 255, 0.28)` | Hero buttons, large icon boxes |
| CTA Large | `--shadow-cta-lg` | `0 16px 40px rgba(0, 127, 255, 0.32)` | Maximum emphasis CTAs |
| Nav Active | `--shadow-nav-active` | `0 10px 15px rgba(0, 127, 255, 0.25)` | Active sidebar navigation item |
| Dialog | `--shadow-dialog` | `0 24px 60px rgba(17, 29, 74, 0.18)` | Modal dialogs, overlays |

### Shadow Philosophy

Shadows serve two distinct purposes — structural elevation and brand emphasis. Structural shadows use `navy.900` (`rgba(17, 29, 74, *)`) at very low opacities (0.04–0.08), creating barely perceptible lift. Brand shadows use `blue.500` (`rgba(0, 127, 255, *)`) at higher opacities (0.22–0.32), creating a colored glow beneath interactive elements that draws attention and reinforces the brand palette.

The CTA shadow scale (sm → default → lg) allows progressive emphasis: a standard button gets a subtle blue underglow, a hero-sized button gets a dramatic one. Active navigation items share this blue shadow language.

## 7. Motion

| Token | Value | Use |
|-------|-------|-----|
| `--ease-emphasis` | `cubic-bezier(0.22, 1, 0.36, 1)` | Emphasized transitions — progress bars, hero animations |
| `--duration-fast` | 150ms | Micro-interactions — hover, focus |
| `--duration-normal` | 220ms | Standard transitions — color changes, opacity |
| `--duration-soft` | 420ms | Smooth transitions — progress fills, panel entries |
| `--duration-hero` | 560ms | Hero animations — page transitions, large element entries |

### Identity Gradient

The brand identity gradient animates through the brand palette for emphasis moments:

- Colors: `#007FFF` → `#004C99` → `#066BD2` → `#007FFF`
- Background size: 280% for smooth looping
- Duration: 3.6s, `ease-in-out`, infinite
- Applied via `-webkit-background-clip: text` for gradient text effect
- Respects `prefers-reduced-motion`: falls back to static `fill.action` color

## 8. Do's and Don'ts

### Do

- Use `fill.action` (`#007FFF`) for links, focus rings, active states, chips, and other non-primary interactive accents
- Use `gradient.button_primary_fill` only on the primary CTA surface
- Use `gradient.general` as the default page background for most pages, and reserve `gradient.main` for token main, claim, and promotional pages
- Use `background.general` / `background.card` as the underlying surfaces beneath those page gradients
- Use `radius.full` (9999px, pill) shape for badges, avatars, chips — the signature pill shape for status elements
- Use `radius.md` (10px) for cards and buttons — the standard container shape
- Apply `--shadow-cta-sm` to primary buttons — the blue underglow is the brand's tactile signal
- Use `text.secondary` (`#A0A5B7`) for secondary text — never raw opacity on text.core
- Use `Noto Sans` for all text — hierarchy comes from size (10–32px) and weight (400/500/700), not font families
- Support both light and dark themes — test every component in both modes
- Use the spacing scale from token v5 — 2, 4, 8, 10, 12, 14, 15, 16, 20, 24, 32, 40, 42, 48, 62, 72
- Use `data-slot` attributes on component root elements for testing and styling hooks
- Use semantic token roles (`text.core`, `fill.action`, `border.default`) instead of raw primitives in components

### Don't

- Don't use raw hex values in components — always reference semantic roles or design tokens
- Don't introduce additional accent colors beyond `blue.500` — the single blue palette is the complete chromatic budget
- Don't use weight 600 (semibold) — the system uses only 400 (regular), 500 (medium), and 700 (bold)
- Don't use radii outside the token v5 scale — only `sm` (4px), `xs` (8px), `md` (10px), `lg` (16px), `full` (9999px)
- Don't use alpha-based color values for cross-surface elements — use pre-composited solid tokens
- Don't use `radius.full` on cards — cards use `radius.md` (10px) or `radius.lg` (16px)
- Don't reuse `gradient.button_primary_fill` outside the primary CTA — no cards, page shells, bars, tags, icon buttons, or decorative backgrounds
- Don't add business logic, API calls, or signing logic to UI components — strictly presentational
- Don't use arbitrary spacing values outside the token v5 spacing scale
- Don't place font imports in components — fonts are loaded globally
- Don't use alpha design's colors (`#fafaf9`, `#0a0b0d`, `#282b31`, `#0cc5ff`, `#10b981`, `#d4183d`) — these are superseded by token v5 values

## 9. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|------|-------|-------------|
| Default (Mobile) | <640px | Single column, compact spacing |
| `sm:` | ≥640px | 2-column grids begin, panel padding expands |
| `md:` | ≥1024px | Full desktop layout |
| `xl:` | ≥1280px | 4-column action grids |

### Touch Targets

- Primary buttons: 48–56px height with generous horizontal padding — exceeds 48px minimum at lg/hero sizes
- Icon buttons: 32–48px square — sm (36px) meets minimum, md/lg (40–48px) exceed
- Navigation items: 44px height with full-width hit area
- Web navigation: 68px height (token v5)
- Chips: 32–36px height — adequate for thumb interaction
- Action buttons: 48px height — comfortable touch target
- Input fields: 48px height (token v5) — comfortable for text entry

### Collapsing Strategy

- **Mobile-first**: All default styles target mobile viewport
- **ActionBar**: 2-column at mobile, optionally 4-column at `xl:` breakpoint
- **Card grids**: single column → 2-column at `sm:` → up to 4-column at `xl:`
- **Section panels**: padding scales from 16px (sm) → 24px (md/lg) → 32px (xl) at `sm:` breakpoint
- **Typography**: hero title text (32px) should scale down proportionally on mobile while maintaining 140% line-height
- **Web nav**: shows full horizontal item layout at `md:`, collapses to hamburger below

### Utility Classes

- `.no-scrollbar`: hides scrollbars for horizontal scroll containers (WebKit + Firefox + IE)
- `.identity-gradient`: brand gradient text effect with motion-safe animation

## 10. Agent Prompt Guide

### Quick Color Reference

| Role | Light | Dark |
|------|-------|------|
| Action (CTA) | `#007FFF` | `#066BD2` |
| Page background (general) | `#F9FDFF → #F0F1F3` | `#000000 → #1F1F1F` |
| Page background (token main / promo) | `#F9FDFF → #D6EBFF` | `#000000 → #003160` |
| Base page surface | `#FFFFFF` | `#1C1C1E` |
| Card surface | `#FFFFFF` | `#1C1C1E` |
| Modal surface | `#F9FAFB` | `#1C1C1E` |
| Core text | `#111D4A` | `#FFFFFF` |
| Primary text | `#111D4A` | `#D6D7E0` |
| Secondary text | `#A0A5B7` | `#8B8B91` |
| Placeholder | `#D0D2DB` | `#49494C` |
| Border | `#ECEDF0` | `#2C2C30` |
| Success | `#4BCE71` | `#4BCE71` |
| Error | `#F3636F` | `#F3636F` |
| Warning | `#FC8C4D` | `#FC8C4D` |
| Secondary fill | `#111D4A` | `#B6B7C1` |
| Icon chip | `#F0F1F3` | `#2C2C2E` |
| CTA shadow | `0 4px 14px rgba(0,127,255,0.22)` | same |
| Card shadow | `0 1px 3px rgba(17,29,74,0.04), 0 1px 2px rgba(17,29,74,0.06)` | same |

### Quick Typography Reference

| Style | Size / Weight |
|-------|---------------|
| Hero Title | 32px / Bold (700) |
| Hero Amount | 24px / Bold (700) |
| Section Lead | 20px / Medium (500) |
| Nav Title | 16px / Bold (700) |
| Body Primary | 16px / Medium (500) |
| Action Label | 16px / Regular (400) |
| Body Secondary | 14px / Regular (400) |
| Section Title | 14px / Medium (500) |
| Supporting Text | 12px / Regular (400) |
| Tab Label | 10px / Regular (400) |

All styles: Noto Sans, 0.04em letter spacing, 140% line height (130% for supportingText).

### Example Component Prompts

- "Create a primary CTA button: `radius.md` (10px), `gradient.button_primary_fill` (radial `#0CC5FF` → `#007FFF`, opacity 0.7), `text.inverse` (white), 52px height, px-16 padding, 16px Noto Sans regular weight (actionLabel), `shadow-cta-sm` blue underglow. Reserve this gradient for the primary CTA only."

- "Design a portfolio asset row: flex row with `justify-between`. Left side: 40px round Avatar with token color background and bold letter fallback, then symbol at 16px `bodyPrimary` medium (500) and amount at 14px `text.secondary` (#A0A5B7). Right side: value at 16px medium and percentage in token brand color. Padding px-12 py-12, `radius.xs` (8px)."

- "Build a balance card: `SectionPanel` with `padding='xl'`. Label at 12px `supportingText` in `text.secondary` (#A0A5B7). Balance number at 24px `heroAmount` bold, `text.core` (#111D4A). Below: `Badge variant='success'` with green icon showing percentage, then secondary dollar change. Action bar below with 4-column grid: Send (action), Receive, Swap, Buy (all icon_chip)."

- "Create a trading agent task card: `radius.lg` (16px) border container, 16px padding. Header: title at 14px `sectionTitle` medium + `Badge variant='success' size='sm'` status. Stats grid below with 3 columns showing label (12px supportingText, text.secondary) and value (14px sectionTitle, text.primary). Progress bar: sm (4px) track, blue.500_a8 → fill.action fill. Footer actions separated by border.default."

- "Design an onboarding step card sequence: vertical stack of `StepCard` components with 12px gap. First two: `state='completed'` (green.500_a20 bg, green.500_a40 border, green check icon). Third: `state='active'` (blue.500_a8 bg, fill.action_subtle border). Fourth: `state='pending'` (background.card, border.default). Each has 40px round icon container, 16px bodyPrimary bold label, 14px bodySecondary text.secondary description."

- "Build a dark mode dashboard section: use `gradient.general` (`#000000 → #1F1F1F`) as the page background over `background.general` (`#1C1C1E`). Cards use `background.card` (`#1C1C1E`) with `border.default` (`#2C2C30`) edges. Text: `text.core` (`#FFFFFF`) for headings, `text.secondary` (`#8B8B91`) for labels. Reserve `gradient.main` (`#000000 → #003160`) for token main, claim, or promotional variants."

### Iteration Guide

1. Every interactive element uses `fill.action` (`#007FFF` / `#066BD2`) — no other accent colors for CTAs or focus
2. Page surface is pure white (`#FFFFFF`), cards are also pure white — borders and shadows provide separation in light mode
3. Button shape uses `radius.md` (10px) per token v5 component definition; badges/avatars/chips use `radius.full` (9999px) pill shape
4. Financial numbers use bold (700) weight at large sizes; secondary data uses medium (500) at smaller sizes
5. Shadows bifurcate: structural shadows use navy tint (`rgba(17,29,74,*)`), interactive shadows use blue tint (`rgba(0,127,255,*)`)
6. Dark mode inverts surfaces but keeps `fill.action` (`#007FFF` → `#066BD2`) as adapted brand blue — not identical across themes
7. Three weights only: 400 (regular), 500 (medium), 700 (bold) — no semibold (600) or black (800/900)
8. Use the token v5 spacing scale — if a spacing value is not in the scale (2,4,8,10,12,14,15,16,20,24,32,40,42,48,62,72), question it
9. Noto Sans is the only typeface — hierarchy through size (10–32px) and weight (400–700), never through font-family changes
10. Use semantic roles (`text.core`, `fill.action`, `border.default`) instead of raw primitives — the semantic layer handles theme switching
