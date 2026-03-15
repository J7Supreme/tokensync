// ds skill v2 Variable Importer — code.js
// Runs inside Figma's plugin sandbox. Uses figma.variables API (free on all plans).

figma.showUI(__html__, { width: 480, height: 560, title: 'ds skill v2' });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'cancel') {
        figma.closePlugin();
        return;
    }

    if (msg.type === 'import') {
        try {
            const data = JSON.parse(msg.json);
            const report = await importVariables(data);
            const warningCount = report.unsupported.length;
            const summary = warningCount
                ? `✅ Variables synced with ${warningCount} unsupported token issue${warningCount === 1 ? '' : 's'}.`
                : '✅ Variables synced successfully.';
            figma.notify(summary, { timeout: 5000 });
            figma.ui.postMessage({ type: 'import-result', report });
            if (!warningCount) {
                figma.closePlugin();
            }
        } catch (err) {
            figma.ui.postMessage({ type: 'error', message: err.message });
        }
    }
};

// ─── Color helpers ─────────────────────────────────────────────────────────

function hexToFigmaColor(hex) {
    const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!r) return null;
    return { r: parseInt(r[1], 16) / 255, g: parseInt(r[2], 16) / 255, b: parseInt(r[3], 16) / 255, a: 1 };
}

function rgbaToFigmaColor(str) {
    const m = str.match(/rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)/i);
    if (!m) return null;
    return {
        r: parseFloat(m[1]) / 255,
        g: parseFloat(m[2]) / 255,
        b: parseFloat(m[3]) / 255,
        a: m[4] !== undefined ? parseFloat(m[4]) : 1
    };
}

function parseFigmaColor(value) {
    if (!value || typeof value !== 'string') return null;
    if (value.startsWith('#')) return hexToFigmaColor(value);
    if (/^rgba?\(/i.test(value)) return rgbaToFigmaColor(value);
    return null;
}

function isMissingValue(value) {
    return value === '[MISSING]';
}

// Maps W3C / Tokens Studio $type → Figma variable resolvedType
const TYPE_MAP = {
    color: 'COLOR',
    string: 'STRING',
    number: 'FLOAT',
    float: 'FLOAT',
    boolean: 'BOOLEAN',
    gradient: 'GRADIENT', // Special marker — handled as Paint Styles
    // Tokens Studio aliases
    fontFamilies: 'STRING',
    fontWeights: 'STRING',
    fontSizes: 'FLOAT',
    lineHeights: 'FLOAT',
    letterSpacing: 'FLOAT',
    spacing: 'FLOAT',
    sizing: 'FLOAT',
    borderRadius: 'FLOAT',
    borderWidth: 'FLOAT',
    opacity: 'FLOAT',
};

/**
 * Recursively flatten a token object into { path, type, value, description }.
 */
function flattenTokens(obj, prefix) {
    const out = [];
    for (const [key, val] of Object.entries(obj)) {
        if (key.startsWith('$')) continue;
        const path = prefix ? `${prefix}.${key}` : key;
        if (val && val.$type && TYPE_MAP[val.$type]) {
            out.push({ path, type: val.$type, value: val.$value, description: val.$description || '' });
        } else if (val && typeof val === 'object' && !Array.isArray(val)) {
            out.push(...flattenTokens(val, path));
        }
    }
    return out;
}

// ─── Collection / Mode / Variable upsert helpers ────────────────────────────

/**
 * Find an existing collection by name, or create a new one.
 * Returns { col, isNew }.
 */
function getOrCreateCollection(name) {
    const existing = figma.variables.getLocalVariableCollections()
        .find(c => c.name === name);
    if (existing) return { col: existing, isNew: false };
    return { col: figma.variables.createVariableCollection(name), isNew: true };
}

/**
 * Find a mode by name inside a collection, or add it.
 * For brand-new collections, the first mode is the default — rename it instead of adding.
 */
function ensureMode(col, modeName, isNewCol, isFirstMode) {
    // Always check first: mode might already exist with the right name
    const existing = col.modes.find(m => m.name === modeName);
    if (existing) return existing.modeId;

    // New collection: rename the default mode instead of adding
    if (isNewCol && isFirstMode) {
        col.renameMode(col.defaultModeId, modeName);
        return col.defaultModeId;
    }

    return col.addMode(modeName);
}

/**
 * Build a name → Variable map for all variables in a collection.
 * Used to look up existing variables for in-place updates.
 */
function buildVarNameMap(col) {
    const map = {};
    for (const varId of col.variableIds) {
        const v = figma.variables.getVariableById(varId);
        if (v) map[v.name] = v;
    }
    return map;
}

/**
 * Find an existing variable by display name in a collection, or create one.
 * Mutates existingVarMap to register newly created variables for later lookups.
 */
function getOrCreateVariable(displayName, col, figmaType, existingVarMap) {
    if (existingVarMap[displayName]) return existingVarMap[displayName];
    const v = figma.variables.createVariable(displayName, col, figmaType);
    existingVarMap[displayName] = v;
    return v;
}

/**
 * Build a name → PaintStyle map for all local paint styles.
 */
function buildStyleNameMap() {
    const map = {};
    for (const style of figma.getLocalPaintStyles()) {
        map[style.name] = style;
    }
    return map;
}

/**
 * Find an existing paint style by name, or create one.
 */
function getOrCreatePaintStyle(name, existingStyleMap) {
    if (existingStyleMap[name]) return existingStyleMap[name];
    const style = figma.createPaintStyle();
    style.name = name;
    existingStyleMap[name] = style;
    return style;
}

// ─── Main import ───────────────────────────────────────────────────────────

async function importVariables(data) {
    const report = {
        unsupported: []
    };

    function addUnsupported(path, reason) {
        report.unsupported.push({ path, reason });
    }

    // ── 1. PRIMITIVE collection (find or create, update in place) ────────────

    const { col: primCol, isNew: primIsNew } = getOrCreateCollection('Primitive');
    const primLightModeId = ensureMode(primCol, 'Light', primIsNew, true);
    const primDarkModeId = ensureMode(primCol, 'Dark', primIsNew, false);

    const primTokens = flattenTokens(data['Primitive'] || {}, '');

    // Existing variables in this collection (name → Variable)
    const primExistingVars = buildVarNameMap(primCol);

    // Path → Variable map used for alias resolution during semantic import
    const primVarMap = {};

    for (const token of primTokens) {
        if (isMissingValue(token.value)) continue;
        const displayName = token.path.replace(/^primitive\./, '').replace(/\./g, '/');
        const figmaType = TYPE_MAP[token.type] || 'STRING';
        if (!TYPE_MAP[token.type]) {
            addUnsupported(token.path, `Unsupported primitive token type "${token.type}"`);
            continue;
        }

        const variable = getOrCreateVariable(displayName, primCol, figmaType, primExistingVars);
        if (token.description) variable.description = token.description;

        // Hide primitives: not visible in publish panel or inspector
        variable.hiddenFromPublishing = true;
        variable.scopes = [];

        const val = resolvePrimitiveValue(token.type, token.value);
        if (val !== null) {
            variable.setValueForMode(primLightModeId, val);
            variable.setValueForMode(primDarkModeId, val);
        } else {
            addUnsupported(token.path, `Unsupported primitive value for type "${token.type}"`);
        }

        // Register under both full path and path without "primitive." prefix
        primVarMap[token.path] = variable;
        primVarMap[token.path.replace(/^primitive\./, '')] = variable;
    }

    // ── 2. SEMANTIC collection (find or create, update in place) ─────────────

    const { col: semCol, isNew: semIsNew } = getOrCreateCollection('Semantic');
    const lightModeId = ensureMode(semCol, 'Light', semIsNew, true);
    const darkModeId = ensureMode(semCol, 'Dark', semIsNew, false);

    const lightTokens = flattenTokens(data['Light'] || {}, '');
    const darkTokens = flattenTokens(data['Dark'] || {}, '');

    // Build dark token lookup by path for O(1) access
    const darkByPath = {};
    for (const t of darkTokens) darkByPath[t.path] = t;

    const semExistingVars = buildVarNameMap(semCol);
    const existingStyleMap = buildStyleNameMap();

    function resolveAlias(rawValue) {
        if (typeof rawValue === 'string' && rawValue.startsWith('{') && rawValue.endsWith('}')) {
            const refPath = rawValue.slice(1, -1);
            const refVar = primVarMap[refPath] || primVarMap[refPath.replace(/^primitive\./, '')];
            if (refVar) return { type: 'VARIABLE_ALIAS', id: refVar.id };
            return null;
        }
        return null;
    }

    function resolveSemanticValue(path, tokenType, rawValue) {
        if (isMissingValue(rawValue)) return null;
        const alias = resolveAlias(rawValue);
        if (alias) return alias;
        const resolved = resolvePrimitiveValue(tokenType, rawValue);
        if (resolved === null && isAliasLike(rawValue)) {
            addUnsupported(path, `Unresolved alias ${rawValue}`);
        }
        return resolved;
    }

    function upsertGradientStyle(path, name, tokenValue, description) {
        if (!tokenValue || !Array.isArray(tokenValue.stops)) {
            addUnsupported(path, 'Gradient token is missing stops');
            return;
        }
        const style = getOrCreatePaintStyle(name, existingStyleMap);
        if (description) style.description = description;

        const stops = tokenValue.stops.map(s => {
            const hexOrAlias = s.color;
            let rgb = { r: 0, g: 0, b: 0, a: 1 };
            let colorBinding = null;

            if (typeof hexOrAlias === 'string' && hexOrAlias.startsWith('{')) {
                const refPath = hexOrAlias.slice(1, -1).replace(/^primitive\./, '');
                const refVar = primVarMap[refPath];
                if (refVar) {
                    const val = refVar.valuesByMode[Object.keys(refVar.valuesByMode)[0]];
                    if (val) rgb = { r: val.r, g: val.g, b: val.b, a: val.a !== undefined ? val.a : 1 };
                    colorBinding = { type: 'VARIABLE_ALIAS', id: refVar.id };
                } else {
                    addUnsupported(path, `Unresolved gradient alias ${hexOrAlias}`);
                }
            } else {
                const parsed = parseFigmaColor(hexOrAlias);
                if (parsed) rgb = parsed;
                else addUnsupported(path, `Unsupported gradient stop color ${hexOrAlias}`);
            }
            const stop = { position: s.position, color: rgb };
            if (colorBinding) {
                stop.boundVariables = { color: colorBinding };
            }
            return stop;
        });

        const gradientPaint = {
            type: 'GRADIENT_LINEAR',
            gradientTransform: [
                [0, 1, 0],
                [-1, 0, 1]
            ],
            gradientStops: stops
        };

        try {
            style.paints = [gradientPaint];
        } catch (err) {
            // Fallback for runtimes that reject variable-bound gradient stops.
            const fallbackPaint = {
                type: 'GRADIENT_LINEAR',
                gradientTransform: gradientPaint.gradientTransform,
                gradientStops: stops.map(({ position, color }) => ({ position, color }))
            };
            style.paints = [fallbackPaint];
            addUnsupported(path, `Gradient stop variable binding not applied: ${err.message}`);
        }
    }

    for (const lightToken of lightTokens) {
        if (isMissingValue(lightToken.value)) continue;
        const displayName = lightToken.path.replace(/\./g, '/');

        // Gradient tokens → Paint Styles (Figma Variables don't support gradients natively)
        if (lightToken.type === 'gradient') {
            try {
                upsertGradientStyle(lightToken.path, `Semantic/Light/${displayName}`, lightToken.value, lightToken.description);
                const darkToken = darkByPath[lightToken.path];
                if (darkToken && !isMissingValue(darkToken.value)) {
                    upsertGradientStyle(darkToken.path, `Semantic/Dark/${displayName}`, darkToken.value, darkToken.description);
                }
            } catch (e) {
                addUnsupported(lightToken.path, `Gradient import failed: ${e.message}`);
            }
            continue;
        }

        // Standard tokens → Variables
        const figmaType = TYPE_MAP[lightToken.type] || 'STRING';
        if (!TYPE_MAP[lightToken.type]) {
            addUnsupported(lightToken.path, `Unsupported token type "${lightToken.type}"`);
            continue;
        }
        const variable = getOrCreateVariable(displayName, semCol, figmaType, semExistingVars);
        if (lightToken.description) variable.description = lightToken.description;

        const lightVal = resolveSemanticValue(lightToken.path, lightToken.type, lightToken.value);
        if (lightVal !== null) variable.setValueForMode(lightModeId, lightVal);

        const darkToken = darkByPath[lightToken.path];
        if (darkToken && !isMissingValue(darkToken.value)) {
            if (!TYPE_MAP[darkToken.type]) {
                addUnsupported(darkToken.path, `Unsupported token type "${darkToken.type}"`);
                continue;
            }
            const darkVal = resolveSemanticValue(darkToken.path, darkToken.type, darkToken.value);
            if (darkVal !== null) variable.setValueForMode(darkModeId, darkVal);
        }
    }

    return report;
}

// ─── Primitive value resolver ────────────────────────────────────────────────

function isAliasLike(rawValue) {
    return typeof rawValue === 'string' && rawValue.startsWith('{') && rawValue.endsWith('}');
}

function resolvePrimitiveValue(tokenType, rawValue) {
    const figmaType = TYPE_MAP[tokenType] || 'STRING';
    if (figmaType === 'COLOR') return parseFigmaColor(rawValue);
    if (figmaType === 'FLOAT') {
        const n = parseFloat(rawValue);
        return isNaN(n) ? null : n;
    }
    if (figmaType === 'BOOLEAN') {
        if (typeof rawValue === 'boolean') return rawValue;
        return rawValue === 'true' || rawValue === true;
    }
    // STRING — return as-is
    return rawValue !== undefined ? String(rawValue) : null;
}
