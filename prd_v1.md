# Design Token 管理架构 PRD

**Single Source of Truth + Adaptive Token Pipeline**

作者：James Hou
版本：v1.3
状态：Active

---

# 1. 概述

本文档定义了产品设计系统中的 **Design Token 管理架构**。

目标是在 Git 中建立一个 **Single Source of Truth（SSOT）** 的 Design Token 源文件，并通过自动化流程生成适配不同环境的 Token 格式，包括：

* Figma
* Runtime（Web / CSS / Tailwind / App）
* AI Native 系统

该架构确保：

* 所有设计决策来自统一 Token Source
* 设计与代码保持一致
* AI 能够理解并生成符合 Design System 的 UI

---

# 2. 核心原则

## 2.1 Single Source of Truth

所有 Design Token 存储在 Git 中的唯一源文件：

```
source/tokens.json
```

该文件是 **唯一允许手动编辑 Token 的地方**。

其他 Token 文件均为 **自动生成产物**。

---

## 2.2 单向同步

Token 只允许单向流动：

```
Git Source
    ↓
Token Compiler
    ↓
Adapters
    ↓
Consumers
```

消费者包括：

* Figma
* Runtime
* AI 系统

Figma **不是 Token Source**。

---

## 2.3 Adapter 架构

不同系统需要不同 Token 格式，因此通过 Adapter 生成：

```
figma.tokens.json
runtime.tokens.json
ai.tokens.json
```

---

# 3. Token 架构

Canonical Token Schema 使用四层结构：

```
primitive
semantic
pattern
component
```

---

## 3.1 Primitive Tokens

Primitive Token 表示基础视觉数值。

例如：

```
primitive.color.blue.500
primitive.spacing.8
primitive.radius.md
primitive.shadow.sm
```

特点：

* 表示视觉 scale
* 不包含 UI 语义
* 可复用

---

## 3.2 Semantic Tokens

Semantic Token 表示设计语义。

例如：

```
semantic.text.primary
semantic.background.card
semantic.border.default
semantic.icon.primary
```

Semantic Token 通常引用 Primitive Token。

例如：

```
semantic.text.primary → primitive.color.navy.900
```

---

## 3.3 Pattern Tokens

Pattern Token 表示 UI Pattern。

例如：

```
pattern.surface.card
pattern.surface.modal
pattern.layout.container
```

---

## 3.4 Component Tokens

Component Token 表示组件级设计规则。

例如：

```
component.button.primary.background
component.button.primary.padding
component.button.primary.radius
component.card.shadow
```

这些 Token 允许 Runtime 与 AI 系统重建组件。

---

# 4. Design Token System Architecture

本章节描述 **Design Token 系统整体架构**，展示 Token 从 Source 到各系统消费端的完整流程。

---

## 4.1 高层系统架构

```
                 ┌─────────────────────┐
                 │   Design Token      │
                 │   Source of Truth   │
                 │                     │
                 │   source/tokens.json│
                 │   (Git Repository)  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Token Compiler   │
                 │                     │
                 │  - Resolve tokens  │
                 │  - Validate schema │
                 │  - Expand alias    │
                 │  - Build adapters  │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼

         Figma Adapter   Runtime Adapter   AI Adapter

              │             │               │
              ▼             ▼               ▼

      figma.tokens.json  runtime.tokens.json  ai.tokens.json

              │             │               │
              ▼             ▼               ▼

       Figma Variables     CSS / Tailwind     AI UI Generation
       Tokens Studio       React / App        AI Reasoning
```

---

## 4.2 架构组件说明

### Token Source

Token Source 是整个系统的 **唯一设计数据源**。

```
source/tokens.json
```

特点：

* 存储在 Git
* 所有 Token 修改必须通过 PR
* 不依赖任何工具

---

### Token Compiler

Token Compiler 负责：

* 解析 Token 引用
* 校验 Schema
* 构建 Token 层级
* 生成适配不同系统的 Token

核心流程：

```
load tokens
   ↓
resolve references
   ↓
validate schema
   ↓
generate adapters
```

---

### Adapter Layer

Adapter Layer 负责生成不同系统需要的 Token。

#### Figma Adapter

生成：

```
adapters/figma/figma_tokens_adaptive.json   ← Tokens Studio 导入格式
adapters/figma/figma_variables_api.json     ← Figma REST API 格式（Enterprise）
```

通过 **Token importer by imToken** Figma Plugin 导入，生成带 Light / Dark 双 Mode 的 Figma Variables，无需付费计划。

---

#### Runtime Adapter

生成：

```
runtime.tokens.json
```

用于：

* CSS Variables
* Tailwind
* React
* Mobile

---

#### AI Adapter

生成：

```
ai.tokens.json
```

用于：

* AI UI generation
* AI reasoning
* AI design validation

---

# 5. Repository 结构

推荐结构：

```
design-tokens
│
├── source
│   └── tokens.json
│
├── adapters
│   ├── figma
│   │   └── tokens.figmatokens.json
│   │
│   ├── runtime
│   │   └── tokens.runtime.json
│   │
│   └── ai
│       └── tokens.ai.json
│
├── schema
│   ├── dtcg.schema.json
│   ├── figma.schema.json
│   ├── tokenstudio.schema.json
│   └── runtime.schema.json
│
└── scripts
    └── build-tokens.ts
```

---

# 6. Token Schema 设计

Source Token Schema 需要兼容：

* Figma Native Variables
* Tokens Studio
* Runtime Token
* W3C DTCG
* AI Native Token

Schema 以 **Reference 文档形式独立维护**。

Token Compiler 会根据 schema 自动生成 Token。

---

# 7. Figma 集成

Figma Token 通过 Adapter 自动生成。

流程：

```
Git tokens
      ↓
generate figma.tokens.json
      ↓
Tokens Studio import
      ↓
Apply to Figma Variables
```

规则：

* Figma Token **只读**
* 不允许在 Figma 修改 Token
* Token 只允许 **从 Git 同步**

---

# 8. Runtime 集成

Runtime Token 用于：

* CSS Variables
* Tailwind
* React Theme
* Mobile Design Token

示例：

```
--color-text-primary
--spacing-sm
--radius-md
```

---

# 9. AI Native Token Layer

AI Adapter 生成：

```
ai.tokens.json
```

AI 可以通过这些 Token：

* 理解 UI
* 生成组件
* 保持设计一致性

---

# 10. Token Flow 示例

```
primitive.color.blue.500
        ↓
semantic.text.primary
        ↓
component.button.primary.background
```

消费者：

```
Figma
Runtime
AI
```

---

# 11. Design Governance

Token 修改流程：

```
token change
     ↓
pull request
     ↓
design review
     ↓
merge
     ↓
token rebuild
```

保证：

* 设计治理
* 版本可追溯

---

# 12. AI Token Consumption Model

AI 在生成 UI 时 **不直接生成视觉数值**。

AI 必须引用 Token。

例如：

```
background: semantic.background.primary
padding: primitive.spacing.8
radius: primitive.radius.md
```

而不是：

```
background: #007FFF
padding: 8px
```

---

# 13. AI UI Generation Flow

AI UI 生成流程：

```
User prompt
     ↓
AI reasoning
     ↓
Token lookup
     ↓
Component resolution
     ↓
Generate UI
```

---

# 14. AI Component Reconstruction

AI 可以通过 Token 层级重建组件：

```
component.button.primary
```

AI 可以解析：

```
layout
background
typography
spacing
```

---

# 15. AI Design Consistency

AI 生成 UI 必须遵守：

1. 不生成未定义设计值
2. 不直接写 hex color
3. spacing 必须来自 token scale

错误：

```
padding: 7px
```

正确：

```
padding: primitive.spacing.8
```

---

# 16. AI Token Pipeline

```
source tokens
      ↓
token compiler
      ↓
ai.tokens.json
      ↓
AI system
      ↓
UI generation
```

---

# 17. Token Naming Convention

Token 命名结构：

```
layer.category.element.variant.property
```

示例：

```
primitive.color.blue.500
semantic.text.primary
component.button.primary.background
```

---

---

# 19. Figma Adaptive Token 输出规则

本章节定义 **Figma Adaptive Token JSON** 的严格输出格式规则。

---

## 19.1 文件结构

`figma_tokens_adaptive.json` 必须严格遵守以下结构：

```
{
  "Primitive": {
    "primitive": {
      "color": { ... }   ← 原始视觉值，无 alias
    }
  },
  "Light": {
    "semantic": { ... } ← 仅包含 alias，引用 {primitive.color.*}
  },
  "Dark": {
    "semantic": { ... } ← 仅包含 alias，引用 {primitive.color.*}
  },
  "$themes": [...],
  "$metadata": { "tokenSetOrder": ["Primitive", "Light", "Dark"] }
}
```

---

## 19.2 Primitive Token 规则

* `$type` 必须为 `color`（或 `string` / `number` / `boolean` / `gradient`）
* `$value` 必须为直接视觉值（hex / rgba），`gradient` 除外
* **禁止** 在 Primitive 层使用 alias 引用
* 命名路径格式：`primitive.color.<palette>.<scale>`
  * 示例：`primitive.color.gray.50`、`primitive.color.navy.900_a40`

---

## 19.3 Semantic Token 规则（Light & Dark）

* Light 和 Dark 的 **token 路径必须完全一一对应**
* 每个 semantic token 必须：
  * 包含 `$type`
  * 包含 `$value`
  * 包含 `$description`（AI Native 语义描述，不得为空）
* **禁止** 在 semantic 层使用硬编码色值（除 gradient 外）
* **普通 Alias 格式**：`{primitive.color.<palette>.<scale>}`
  * 正确：`{primitive.color.navy.900}`
  * 错误：`{Primitive.color.navy.900}` / `#111D4A`
* **Gradient 格式**：当 `$type` 为 `gradient` 时，`$value` 必须是包含 `type`、`angle` 和 `stops` 数组的对象。`stops` 数组中的 `color` 必须使用 `{primitive.color.*}` alias。

---

## 19.4 Multi Mode 规则

* `$themes` 必须定义 `Light` 和 `Dark` 两个 theme
* Light theme：启用 `Primitive` + `Light`，禁用 `Dark`
* Dark theme：启用 `Primitive` + `Dark`，禁用 `Light`
* Token set 顺序：`["Primitive", "Light", "Dark"]`
* 扩展新 Mode（如 `HighContrast`）时，必须与 Light / Dark 保持相同的 semantic token 路径集合

---

## 19.5 Figma Plugin 导入规则

* 使用 **Token importer by imToken** Figma Plugin 导入
* Plugin 使用 `figma.variables` API（无需 Enterprise 或付费计划）结合 `figma.createPaintStyle()`
* 导入行为：
  * `Primitive`：生成为 **Figma Variables**（包含 `Light` + `Dark` 两个 mode，两者的实际 primitive 值输入完全相同，这是由于 Figma 原生 Paint Style 目前不支持自身响应模式的主题切换，必须依赖底层 Variable 的双模属性。）。并且被设置为 `hiddenFromPublishing = true` 和 `scopes = []`，完全在设计师选色面板中隐藏。
  * `Semantic`（非 gradient）：生成为 **Figma Variables**（Light + Dark 两个 mode）。
  * `Semantic`（gradient）：生成为 **Figma Paint Styles**（分 `Light/` 和 `Dark/` 目录结构），因为 Figma Variables 原生暂不支持渐变。
* 每次导入会完整清除并重建旧 Variables 集合与 Semantic Styles，支持安全重复执行

---

# 20. Source Token 保留规则

`source/tokens.json` 是系统的 **Single Source of Truth**，任何时候都必须完整保留以下特性。

---

## 20.1 必须保留的完整结构

| 结构 | 说明 |
|---|---|
| 多层结构（Multi-layer） | Primitive / Light / Dark 三层完整存在 |
| Light / Dark 双主题 | 两套 semantic token，路径完全对应 |
| AI Semantic 描述 | 每个 semantic token 的 `$description` 字段不得删除 |
| `$themes` 定义 | Light / Dark theme 配置完整保留 |
| `$metadata.tokenSetOrder` | token set 顺序字段完整保留 |
| AI native 语义命名 | 命名遵循 `category.role.state` 语义格式 |

---

## 20.2 禁止操作

* **禁止** 将 source token 的 semantic 层替换为硬编码值
* **禁止** 删除 `$description` 字段
* **禁止** 合并 Light 和 Dark 为单一 token set
* **禁止** 删除 `$themes` 或 `$metadata` 字段
* **禁止** 在 Primitive 层写入 alias

---

## 20.3 Source 与 Adapter 关系

```
source/tokens.json
    ↓ 编译 / 转换
adapters/figma/figma_tokens_adaptive.json   ← 仅变更 path 分隔符等格式
adapters/figma/figma_variables_api.json     ← RGB 归一化 + REST API 结构
```

Source 是 **语义层**，Adapter 是 **格式层**。两者都不得丢失信息。

---

# 21. Token 优化规则

当对现有 token JSON 进行优化、审计、重构时，必须严格遵守以下规则。

---

## 21.1 优化原则

* **保形优化（Structure-preserving）**：优化只改变 token 的值或描述，不得改变 token 的路径结构
* **不得无故删除 token**：即使 token 值在 Light / Dark 中相同，也必须在两套中分别定义
* **缺失值允许补充，不允许假设**：如某 token 在源文件中不存在，可补充；但不得为不存在的 token 填入推测值

---

## 21.2 优化允许的操作

| 操作 | 条件 |
|---|---|
| 修改 `$value` | 必须仍为 `{primitive.*}` alias，不得改为硬编码 |
| 修改 `$description` | 必须保留 AI 语义属性，描述更准确即可 |
| 新增 token | 路径必须符合 `semantic.category.role` 格式 |
| 修改 Primitive 值 | 允许，但不得影响现有 alias 引用 |
| 补充缺失的 `$description` | 必须写 AI native 语义描述 |

---

## 21.3 优化禁止的操作

* **禁止** 修改 token 路径（除非明确重命名需求并同步所有引用）
* **禁止** 将 alias 替换为硬编码值（即使两者当前等价）
* **禁止** 删除某 Light token 而在 Dark 中保留同路径 token
* **禁止** 将 semantic 层直接指向另一个 semantic token（跨层引用）
* **禁止** 在没有对应 Primitive token 的情况下在 semantic 中使用该 alias

---

## 21.4 缺失值处理规则

如发现 token 值确实缺失（如源文件中某 token 根本不存在）：

1. 记录为 `missing`，不得填入随机值
2. 优化报告中标记为 `[MISSING]`
3. 由设计师确认后再补充
4. 补充时必须同时在 `Light` 和 `Dark` 中定义

---

# 18. 总结

该架构建立了一套 **AI Native Design Token Infrastructure**。

核心特点：

* Git Single Source of Truth
* Adapter Token Pipeline
* Schema Reference Architecture
* AI Native Token Consumption
* Scalable Design System

Design Token 成为：

```
Design System
Runtime
AI UI Generation
```

之间的统一语义层。
