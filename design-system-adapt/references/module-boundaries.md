# Module Boundaries

Use this reference only when extending the skill beyond `adapt`.

## Current public contract

- `adapt` is the active module.
- Its job is translation: convert one canonical design-system model into consumer-specific outputs without changing what the system means.

## Reserved future modules

### `audit`

Use `audit` for evaluation, not transformation.

- Inspect design assets, source schemas, or consumer outputs.
- Report gaps, inconsistencies, and risks.
- Do not silently fix issues while auditing unless the user asks for remediation.

### `normalize`

Use `normalize` for alignment, not translation.

- Make naming, structure, and shape more consistent.
- Reduce schema drift across source and outputs.
- Keep normalization rules explicit so they can be reviewed and repeated.

## Packaging rule

If future versions add `audit` or `normalize`, keep the boundaries visible in `SKILL.md` and in any references:

- `adapt` answers: "How should this system be expressed for a target consumer?"
- `audit` answers: "What is wrong or risky in the current system or artifact?"
- `normalize` answers: "How should the current structure be made consistent?"
