# Design System Status & Workflow

- **Current Status:** The design system has a solid core structure with an optimized workflow foundation. It is usable today — components are live and functional — but the system is still expanding toward completeness, with new components being filled in progressively as needs arise.

- **Proposed Workflow:** Three roles are served — designers, developers, and product managers. For designers, Figma acts as the discussion canvas: visual, organized, and easy to iterate on. The single source of truth lives in two artifacts: a design markdown file and a token JSON, together capturing everything authoritatively. Component schemas and pattern schemas are the ideal next layer, but are deferred — they will be added file-by-file only when a component's complexity demands it.

- **Key Strength:** The design system is AI-native, well-scoped, and well-structured — purpose-built so that any part of it can be cleanly translated into a structured design markdown file. This makes it inherently machine-readable and directly usable as input for downstream tooling and code generation.

## How I Got Here

After trying multiple official Figma skills, I identified them falling into distinct categories by use case:

**1. Set Up a Design System**
Starting point can be from scratch, from an existing but messy design system, or from code. Under this umbrella, two supporting skills apply:
- *Audit & Apply Design System* — focused on component building. Must be used only after foundations are already established (variables, styles, typography, etc.).
- *Sync Design Token* — intended for when you're building on a visual canvas like Figma and want to generate a code schema from it. Backwards sync is not the primary use case for this skill, but it is useful in our context.

**2. Figma Generate Library**
The key skill. It follows a strict set of rules (covered in detail later). This is the backbone of building out the design system library.

**3. Figma Generate Design**
Used for producing actual screen designs. Most generated designs come with components, variables, and styles already bound — but not always. Unbound components and unbound variables still appear and require manual cleanup.

## Highlights: Working Patterns

Two primary working patterns define how the design system is used in practice:

**Pattern 1 — Code-First (Figma as Canvas)**
When starting from code, Figma serves as a visualization and discussion canvas. In this mode, the design system in Figma is second-class. The first-class objects are the design markdown file and the token schema. Code and schema drive everything; Figma reflects it.

**Pattern 2 — Figma as Proprietary Design Tool**
When a designer is working heavily in Figma as the primary tool, the design system must be fully bound — especially at the component level. Code is generated not only from schema but also from Figma map pages. In this mode, all available skills need to be leveraged so that a design can start from raw data or complete scratch and eventually reach a fully bound, production-ready state.

**Pattern 3 — AI-First**
Two sub-cases:

- *Exploration:* No strict requirement for all components or bindings to be ready in Figma. Input can be a prompt, a file, or natural language — the goal is fast generation all the way to code. Bindings and structure are best-effort, not mandatory.

- *Active Production:* Production-level output requires design components to be well-bound. Page generation follows strict semantic rules explicitly stated in the design markdown file. When complexity exceeds what the markdown covers, a component schema becomes necessary to drive accurate generation.
