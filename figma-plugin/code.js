// TokenSync Variable Importer — code.js
// Runs inside Figma's plugin sandbox. Uses figma.variables API (free on all plans).

figma.showUI(__html__, { width: 480, height: 560, title: 'Design token importer by imToken' });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'cancel') {
        figma.closePlugin();
        return;
    }

    if (msg.type === 'import') {
        try {
            const data = JSON.parse(msg.json);
            await importVariables(data);
            figma.notify('✅ Variables imported! Primitive + Semantic (Light & Dark) collections created. Colors, strings, numbers & booleans all supported.', { timeout: 5000 });
            figma.closePlugin();
        } catch (err) {
            figma.ui.postMessage({ type: 'error', message: err.message });
        }
    }
};

// ─── Helpers ───────────────────────────────────────────────────────────────

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

// Maps W3C / Tokens Studio $type → Figma variable resolvedType
const TYPE_MAP = {
    color: 'COLOR',
    string: 'STRING',
    number: 'FLOAT',
    float: 'FLOAT',
    boolean: 'BOOLEAN',
    gradient: 'GRADIENT', // Special marker for Paint Styles
    // common Tokens Studio aliases
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
 * Collects ALL $type tokens (color, string, number, boolean, …).
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

// ─── Main import ───────────────────────────────────────────────────────────

async function importVariables(data) {
    // ── 0. Wipe existing collections and styles ──────────────────────────────
    const existingCols = figma.variables.getLocalVariableCollections();
    for (const col of existingCols) {
        if (col.name === 'Primitive' || col.name === 'Semantic') col.remove();
    }
    const existingStyles = figma.getLocalPaintStyles();
    for (const style of existingStyles) {
        if (style.name.startsWith('Semantic/')) style.remove();
    }

    const primCol = figma.variables.createVariableCollection('Primitive');
    const primModeId = primCol.defaultModeId;
    primCol.renameMode(primModeId, 'Default');

    // Flatten: paths like "primitive.color.gray.50"
    const primTokens = flattenTokens(data['Primitive'] || {}, '');

    // map: full dot-path → Figma Variable
    const primVarMap = {};

    for (const token of primTokens) {
        const displayName = token.path.replace(/^primitive\./, '').replace(/\./g, '/');
        const figmaType = TYPE_MAP[token.type] || 'STRING';
        const variable = figma.variables.createVariable(displayName, primCol, figmaType);
        if (token.description) variable.description = token.description;

        // Hide primitives from sharing and inspector
        variable.hiddenFromPublishing = true;
        variable.scopes = [];

        const val = resolvePrimitiveValue(token.type, token.value);
        if (val !== null) variable.setValueForMode(primModeId, val);

        primVarMap[token.path] = variable;
        primVarMap[token.path.replace(/^primitive\./, '')] = variable;
    }

    // ── 2. SEMANTIC collection (Light + Dark modes) ──────────────────────────
    const semCol = figma.variables.createVariableCollection('Semantic');
    const lightModeId = semCol.defaultModeId;
    semCol.renameMode(lightModeId, 'Light');
    const darkModeId = semCol.addMode('Dark');

    const lightTokens = flattenTokens(data['Light'] || {}, '');
    const darkTokens = flattenTokens(data['Dark'] || {}, '');

    // Build dark lookup by path
    const darkByPath = {};
    for (const t of darkTokens) darkByPath[t.path] = t;

    function resolveAlias(rawValue) {
        if (typeof rawValue === 'string' && rawValue.startsWith('{') && rawValue.endsWith('}')) {
            const refPath = rawValue.slice(1, -1);
            const refVar = primVarMap[refPath] || primVarMap[refPath.replace(/^primitive\./, '')];
            if (refVar) return { type: 'VARIABLE_ALIAS', id: refVar.id };
            console.warn(`[TokenSync] Unresolved alias: ${rawValue}`);
            return null;
        }
        return null; // not an alias
    }

    function resolveSemanticValue(tokenType, rawValue) {
        const alias = resolveAlias(rawValue);
        if (alias) return alias;
        return resolvePrimitiveValue(tokenType, rawValue);
    }

    function createGradientStyle(name, tokenValue, description) {
        const style = figma.createPaintStyle();
        style.name = `Semantic/${name}`;
        if (description) style.description = description;

        // Parse the stops
        const stops = tokenValue.stops.map(s => {
            const hexOrAlias = s.color;
            let rgb = { r: 0, g: 0, b: 0, a: 1 };

            // Resolve alias if needed
            if (hexOrAlias.startsWith('{')) {
                const refPath = hexOrAlias.slice(1, -1).replace(/^primitive\./, '');
                const refVar = primVarMap[refPath];
                if (refVar) {
                    const val = refVar.valuesByMode[Object.keys(refVar.valuesByMode)[0]];
                    if (val) rgb = { r: val.r, g: val.g, b: val.b, a: val.a !== undefined ? val.a : 1 };
                }
            } else {
                const parsed = parseFigmaColor(hexOrAlias);
                if (parsed) rgb = parsed;
            }
            return { position: s.position, color: rgb };
        });

        // Simple vertical linear gradient (90 deg in Figma space)
        style.paints = [{
            type: 'GRADIENT_LINEAR',
            gradientTransform: [
                [0, 1, 0],
                [-1, 0, 1]
            ],
            gradientStops: stops
        }];
    }

    for (const lightToken of lightTokens) {
        const displayName = lightToken.path.replace(/\./g, '/');

        // Handle Gradient Styles separately
        if (lightToken.type === 'gradient') {
            createGradientStyle(`Light/${displayName}`, lightToken.value, lightToken.description);

            const darkToken = darkByPath[lightToken.path];
            if (darkToken) {
                createGradientStyle(`Dark/${displayName}`, darkToken.value, darkToken.description);
            }
            continue;
        }

        // Standard Variables
        const figmaType = TYPE_MAP[lightToken.type] || 'STRING';
        const variable = figma.variables.createVariable(displayName, semCol, figmaType);
        if (lightToken.description) variable.description = lightToken.description;

        const lightVal = resolveSemanticValue(lightToken.type, lightToken.value);
        if (lightVal !== null) variable.setValueForMode(lightModeId, lightVal);

        const darkToken = darkByPath[lightToken.path];
        if (darkToken) {
            const darkVal = resolveSemanticValue(darkToken.type, darkToken.value);
            if (darkVal !== null) variable.setValueForMode(darkModeId, darkVal);
        }
    }
}

// ─── Primitive value resolver (no alias lookup) ─────────────────────────────

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
