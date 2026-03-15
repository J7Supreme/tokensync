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
    dimension: 'FLOAT',
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

const COLLECTION_ORDER = ['primitive', 'semantic', 'pattern', 'component'];

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
    if (existingVarMap[displayName]) {
        const existing = existingVarMap[displayName];
        if (existing.resolvedType === figmaType) return existing;
        if (typeof existing.remove === 'function') {
            existing.remove();
            delete existingVarMap[displayName];
        } else {
            throw new Error(`Existing variable "${displayName}" has incompatible type ${existing.resolvedType}`);
        }
    }
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

function titleCaseCollectionName(name) {
    if (!name) return name;
    return name.charAt(0).toUpperCase() + name.slice(1);
}

function normalizeModeName(name) {
    if (!name) return name;
    return name.charAt(0).toUpperCase() + name.slice(1);
}

function getPrimitiveSetKey(data) {
    if (data.Primitive) return 'Primitive';
    if (data.primitive) return 'primitive';
    return null;
}

function analyzePayload(data) {
    const primitiveKey = getPrimitiveSetKey(data);
    const collectionMap = {};
    const topLevelKeys = Object.keys(data).filter(k => !k.startsWith('$'));
    const splitSetKeys = topLevelKeys.filter(k => k.includes('/'));

    if (splitSetKeys.length) {
        for (const key of splitSetKeys) {
            const [collectionName, rawModeName] = key.split('/');
            if (!collectionName || !rawModeName) continue;
            const normalizedCollectionKey = collectionName.toLowerCase();
            if (!collectionMap[normalizedCollectionKey]) {
                collectionMap[normalizedCollectionKey] = {
                    key: normalizedCollectionKey,
                    figmaName: titleCaseCollectionName(collectionName),
                    modes: {}
                };
            }
            collectionMap[normalizedCollectionKey].modes[normalizeModeName(rawModeName)] = data[key];
        }
    } else if (data.Light || data.Dark) {
        for (const modeName of ['Light', 'Dark']) {
            const modeRoot = data[modeName];
            if (!modeRoot || typeof modeRoot !== 'object') continue;
            for (const [collectionName, subtree] of Object.entries(modeRoot)) {
                if (collectionName.startsWith('$')) continue;
                const normalizedCollectionKey = collectionName.toLowerCase();
                if (!collectionMap[normalizedCollectionKey]) {
                    collectionMap[normalizedCollectionKey] = {
                        key: normalizedCollectionKey,
                        figmaName: titleCaseCollectionName(collectionName),
                        modes: {}
                    };
                }
                collectionMap[normalizedCollectionKey].modes[modeName] = subtree;
            }
        }
    }

    const collections = Object.values(collectionMap).sort((a, b) => {
        const aIndex = COLLECTION_ORDER.indexOf(a.key);
        const bIndex = COLLECTION_ORDER.indexOf(b.key);
        if (aIndex === -1 && bIndex === -1) return a.key.localeCompare(b.key);
        if (aIndex === -1) return 1;
        if (bIndex === -1) return -1;
        return aIndex - bIndex;
    });

    return { primitiveKey, collections };
}

function sortModeNames(modeNames) {
    const preferredOrder = ['Light', 'Dark'];
    return [...modeNames].sort((a, b) => {
        const aIndex = preferredOrder.indexOf(a);
        const bIndex = preferredOrder.indexOf(b);
        if (aIndex === -1 && bIndex === -1) return a.localeCompare(b);
        if (aIndex === -1) return 1;
        if (bIndex === -1) return -1;
        return aIndex - bIndex;
    });
}

function safelySetValueForMode(variable, modeId, value, path, addUnsupported) {
    try {
        variable.setValueForMode(modeId, value);
        return true;
    } catch (err) {
        addUnsupported(path, `setValueForMode failed: ${err.message}`);
        return false;
    }
}

// ─── Main import ───────────────────────────────────────────────────────────

async function importVariables(data) {
    const report = {
        unsupported: []
    };

    function addUnsupported(path, reason) {
        report.unsupported.push({ path, reason });
    }

    const payload = analyzePayload(data);
    if (!payload.primitiveKey) {
        throw new Error('Missing primitive token set');
    }

    // ── 1. PRIMITIVE collection (find or create, update in place) ────────────

    const { col: primCol, isNew: primIsNew } = getOrCreateCollection('Primitive');
    const primLightModeId = ensureMode(primCol, 'Light', primIsNew, true);
    const primDarkModeId = ensureMode(primCol, 'Dark', primIsNew, false);

    const primTokens = flattenTokens(data[payload.primitiveKey] || {}, '');

    // Existing variables in this collection (name → Variable)
    const primExistingVars = buildVarNameMap(primCol);

    // Path → Variable map used for alias resolution across collections.
    const aliasVarMap = {};

    function registerPrimitiveAliases(tokenPath, variable) {
        aliasVarMap[tokenPath] = variable;
        aliasVarMap[tokenPath.replace(/^primitive\./, '')] = variable;
    }

    function registerCollectionAliases(collectionKey, modeName, tokenPath, variable) {
        aliasVarMap[`${collectionKey}.${tokenPath}`] = variable;
        aliasVarMap[`${collectionKey}/${modeName.toLowerCase()}.${tokenPath}`] = variable;
        aliasVarMap[`${collectionKey}/${modeName}.${tokenPath}`] = variable;
    }

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
            safelySetValueForMode(variable, primLightModeId, val, token.path, addUnsupported);
            safelySetValueForMode(variable, primDarkModeId, val, token.path, addUnsupported);
        } else {
            addUnsupported(token.path, `Unsupported primitive value for type "${token.type}"`);
        }

        registerPrimitiveAliases(token.path, variable);
    }
    const existingStyleMap = buildStyleNameMap();

    function resolveAlias(rawValue) {
        if (typeof rawValue === 'string' && rawValue.startsWith('{') && rawValue.endsWith('}')) {
            const refPath = rawValue.slice(1, -1);
            const refVar = aliasVarMap[refPath] || aliasVarMap[refPath.replace(/^primitive\./, '')];
            if (refVar) return { type: 'VARIABLE_ALIAS', id: refVar.id };
            return null;
        }
        return null;
    }

    function resolveTokenValue(path, tokenType, rawValue) {
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
                const refPath = hexOrAlias.slice(1, -1);
                const refVar = aliasVarMap[refPath] || aliasVarMap[refPath.replace(/^primitive\./, '')];
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

    for (const collection of payload.collections) {
        const modeNames = sortModeNames(Object.keys(collection.modes));
        if (!modeNames.length) continue;

        const { col, isNew } = getOrCreateCollection(collection.figmaName);
        const modeIds = {};
        for (let index = 0; index < modeNames.length; index += 1) {
            modeIds[modeNames[index]] = ensureMode(col, modeNames[index], isNew, index === 0);
        }
        const existingVars = buildVarNameMap(col);

        const tokensByMode = {};
        const tokenPaths = [];
        const seenPaths = new Set();
        for (const modeName of modeNames) {
            const tokens = flattenTokens(collection.modes[modeName] || {}, '');
            const byPath = {};
            for (const token of tokens) {
                byPath[token.path] = token;
                if (!seenPaths.has(token.path)) {
                    seenPaths.add(token.path);
                    tokenPaths.push(token.path);
                }
            }
            tokensByMode[modeName] = byPath;
        }

        for (const tokenPath of tokenPaths) {
            const seedToken = modeNames.map(modeName => tokensByMode[modeName][tokenPath]).find(Boolean);
            if (!seedToken || isMissingValue(seedToken.value)) continue;

            const displayName = tokenPath.replace(/\./g, '/');
            if (seedToken.type === 'gradient') {
                try {
                    for (const modeName of modeNames) {
                        const modeToken = tokensByMode[modeName][tokenPath];
                        if (!modeToken || isMissingValue(modeToken.value)) continue;
                        upsertGradientStyle(
                            `${collection.key}.${tokenPath}`,
                            `${collection.figmaName}/${modeName}/${displayName}`,
                            modeToken.value,
                            modeToken.description
                        );
                    }
                } catch (e) {
                    addUnsupported(`${collection.key}.${tokenPath}`, `Gradient import failed: ${e.message}`);
                }
                continue;
            }

            const figmaType = TYPE_MAP[seedToken.type] || 'STRING';
            if (!TYPE_MAP[seedToken.type]) {
                addUnsupported(`${collection.key}.${tokenPath}`, `Unsupported token type "${seedToken.type}"`);
                continue;
            }

            const variable = getOrCreateVariable(displayName, col, figmaType, existingVars);
            if (seedToken.description) variable.description = seedToken.description;

            for (const modeName of modeNames) {
                const modeToken = tokensByMode[modeName][tokenPath];
                if (!modeToken || isMissingValue(modeToken.value)) continue;
                if ((TYPE_MAP[modeToken.type] || 'STRING') !== figmaType) {
                    addUnsupported(`${collection.key}.${tokenPath}`, `Mode type mismatch in ${modeName}`);
                    continue;
                }
                const resolvedValue = resolveTokenValue(`${collection.key}.${tokenPath}`, modeToken.type, modeToken.value);
                if (resolvedValue !== null) {
                    safelySetValueForMode(
                        variable,
                        modeIds[modeName],
                        resolvedValue,
                        `${collection.key}/${modeName.toLowerCase()}.${tokenPath}`,
                        addUnsupported
                    );
                }
                registerCollectionAliases(collection.key, modeName, tokenPath, variable);
            }
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
