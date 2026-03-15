# 基于设计文件的 Design System 评估框架

作者：Codex  
状态：Draft  
适用范围：仅基于 Figma / 设计文件内容进行评估

---

## 1. 背景

如果评估对象是“整体设计系统”，那么 `token` 只是其中一个能力域，而不是全部。

但如果评估证据来源被限制为“设计文件本身”，那么评分体系就不应该覆盖所有设计系统成熟度维度，因为有一部分能力并不在设计文件中完整呈现。

因此，需要先明确：

1. 哪些维度适合仅基于设计文件评估
2. 哪些维度不适合纳入设计文件评分
3. 这些设计文件维度与现有 R2D2 report 维度之间如何对应

本文档用于定义这一边界。

---

## 2. 核心结论

从设计文件角度，最适合评估的不是“完整设计系统成熟度”，而是：

`设计资产成熟度（Design Asset Maturity）`

它关注的是：

- 基础设计资产是否完整
- 组件是否结构化、可复用
- 设计师是否易于理解和使用
- 资产是否完成变量化 / token 化
- 是否具备可访问性准备度

而以下能力不应直接纳入“仅基于设计文件”的评分主表：

- 工程集成能力
- 治理与发布机制
- 实际 adoption / 使用率
- 代码实现质量
- Source Token / SSOT 合规性

原因不是这些维度不重要，而是它们需要设计文件之外的外部证据。

---

## 3. 最适合基于设计文件评估的五个维度

### 3.1 Foundation

评估目标：判断基础设计资产是否存在且成体系。

建议观察项：

- Color
- Typography
- Spacing
- Radius
- Elevation / Shadow
- Iconography
- Motion principles
- Grid / Breakpoints

为什么适合：

- 这些内容通常直接存在于 Figma 页面、Variables、Styles、规范说明页、示例组件中。
- 可以较准确判断“是否存在”“是否成系统”“是否一致”。

边界：

- 能看出是否定义了圆角体系、字号体系、颜色体系。
- 看不出代码实现是否真实遵守这些体系。

---

### 3.2 Component System

评估目标：判断组件是否已经形成可复用系统，而不是零散页面素材。

建议观察项：

- 核心组件覆盖度
- Variant / State 完整性
- Component Set 使用情况
- 命名一致性
- 组件结构组织质量
- 响应式差异覆盖
- 复杂组件与 Pattern 抽象能力

为什么适合：

- 这些信息直接存在于 Figma 组件、页面结构、实例和变体里。
- 设计文件是观察组件复用能力和结构成熟度的第一现场。

边界：

- 能看出组件设计是否完整。
- 看不出前端组件 API 是否稳定、一致。

---

### 3.3 Designer Experience

评估目标：判断设计师是否真的能高效使用这套系统。

建议观察项：

- 页面组织结构
- 命名清晰度
- 搜索与发现成本
- Usage guideline
- Do / Don't
- 组件说明
- Description 字段
- 示例覆盖度
- Library 发布状态

为什么适合：

- 这些都直接发生在设计文件和 Figma library 层。
- 它们直接影响设计协作质量和系统使用门槛。

边界：

- 能看出文档是否存在、是否清晰。
- 看不出团队是否在实际协作中真正遵循这些规范。

---

### 3.4 Tokenization

评估目标：判断设计资产是否已经从视觉稿进化为变量化、可系统消费的资产。

建议观察项：

- 是否使用 Variables / Styles
- Color / Number / String 等变量覆盖度
- Light / Dark modes
- 命名路径语义化程度
- 基础属性是否去硬编码
- 组件是否绑定变量而不是写死值

为什么适合：

- 变量化程度是设计文件中最能反映“系统化成熟度”的指标之一。
- 可以直接判断资产是否具备机器可读和结构化消费的基础。

边界：

- 能看出 Figma 中是否使用 variable / style。
- 看不出 Git 中的 source token、alias 规则、adapter 输出是否正确。

---

### 3.5 Accessibility Readiness

评估目标：判断设计文件是否已经把可访问性要求表达为系统规则，而不是留给落地阶段补救。

建议观察项：

- 对比度
- Focus / Hover / Disabled / Error 状态
- Touch target 尺寸
- 文本层级
- 表单状态定义
- 响应式适配
- Light / Dark 下的可读性

为什么适合：

- 这些很多可以从颜色、组件状态、尺寸和规范说明中直接判断。
- 适合评估“设计是否为无障碍落地做好准备”。

边界：

- 能看出设计意图。
- 看不到真实 DOM、键盘导航、ARIA、屏幕阅读器支持。

---

## 4. 不适合仅基于设计文件评估的维度

### 4.1 Engineering Integration

不适合原因：

- 设计文件看不到 token compiler、runtime adapter、CSS / Tailwind / React 消费情况。
- 看不到设计组件和代码组件是否真正一一对应。
- 即使存在 Code Connect，也不代表运行时一定可用。

外部依赖：

- 代码仓库
- 组件实现
- 构建脚本
- Runtime token 输出

---

### 4.2 Governance & Operations

不适合原因：

- Figma 中可以看到更新时间、版本字样、页面结构，但这不等于治理能力。
- 看不到 owner、review 流程、发布机制、变更审批、弃用策略。

外部依赖：

- 团队流程文档
- 仓库历史
- 发布记录
- Owner 信息

---

### 4.3 Adoption / 实际使用率

不适合原因：

- 一个组件存在于设计库中，不等于业务团队真实在使用。
- 设计文件无法准确反映覆盖率、替换率、遗留使用情况。

外部依赖：

- 代码扫描
- 产品使用统计
- 文件引用关系
- 团队访谈

---

### 4.4 Implementation Quality

不适合原因：

- 设计文件只能展示设计意图，无法反映最终实现质量。
- 看不到性能、HTML 语义、真实交互、浏览器兼容性等问题。

外部依赖：

- 前端代码
- 线上产品
- 浏览器审计
- 性能与 A11y 检测工具

---

### 4.5 Source Token / SSOT Compliance

不适合原因：

- Figma 可以看到 variable，但看不到它是否来自真实 `source/tokens.json`。
- 也看不到 alias 是否合规、adapter 是否保形、source 是否满足 PRD。

外部依赖：

- `source/tokens.json`
- PRD / schema
- build pipeline
- adapters 输出文件

---

## 5. 设计文件评估的推荐主模型

如果评估证据源限定为设计文件，推荐主模型如下：

| 维度 | 核心问题 |
|---|---|
| Foundation | 基础设计资产是否完整、成体系、一致 |
| Component System | 组件是否结构化、可复用、可扩展 |
| Designer Experience | 设计师是否易于理解、查找、正确使用 |
| Tokenization | 设计资产是否变量化、语义化、去硬编码 |
| Accessibility Readiness | 可访问性要求是否已经在设计侧被系统表达 |

一句话概括：

`资产是否完整 + 是否结构化 + 是否可复用 + 是否易用 + 是否具备可访问性准备度`

---

## 6. 与 R2D2 六维的关系

R2D2 当前使用的是更接近“整体设计系统成熟度”的语言，包含：

- 完善度
- 设计师可用性
- AI Friendly
- 开发衔接
- 可访问性
- 治理与贡献

这套语言适合做高层成熟度报告，但如果证据源仅限设计文件，需要重新划清边界。

### 6.1 对比原则

1. 保留 R2D2 中适合设计文件观察的部分
2. 将设计文件无法可靠验证的部分降级为“外部验证项”
3. 避免把工程、治理、采用率混入设计文件总分，导致失真

---

## 7. 设计文件五维与 R2D2 六维对比表

| 设计文件评估维度 | 定义 | 对应的 R2D2 维度 | 是否适合仅基于设计文件评分 | 说明 |
|---|---|---|---|---|
| Foundation | 基础设计资产是否完整、成体系 | 主要对应 `完善度` | 是 | R2D2 中的 Color、Typography、Spacing、Radius、Motion、Icon、Shadow 等都可归入此维度 |
| Component System | 组件是否具备复用和变体系统 | 主要对应 `完善度`，部分对应 `设计师可用性` | 是 | 组件覆盖度、变体完整性、Component Set 化程度都适合从 Figma 直接观察 |
| Designer Experience | 设计师能否高效理解和使用系统 | 主要对应 `设计师可用性` | 是 | 命名、说明、示例、Library 组织、页面可发现性都属于设计文件内证据 |
| Tokenization | 是否完成变量化、语义化、模式化表达 | 部分对应 `完善度`，部分对应 `AI Friendly` | 是 | 适合评估 Variables、Styles、Modes、命名语义化；但不等于 source token 合规 |
| Accessibility Readiness | 可访问性要求是否已经在设计中显式表达 | 对应 `可访问性` | 是 | 对比度、focus、state、尺寸、断点等可在设计文件中检查，但仅是“准备度” |
| AI Friendly | 设计资产是否足够便于 AI 读取和理解 | 对应 `AI Friendly` | 部分适合 | 命名、description、结构语义可在设计文件中评估；但 Code Connect、真实生成效果需要外部验证 |
| 开发衔接 | 设计系统是否可被工程侧稳定消费 | 对应 `开发衔接` | 不适合直接纳入主评分 | 可在设计文件中看到一些线索，但关键证据在代码、runtime、adapter、组件实现 |
| 治理与贡献 | 是否具备版本、发布、owner、变更管理机制 | 对应 `治理与贡献` | 不适合直接纳入主评分 | Figma 中看到的更新时间和页面组织只是表象，不能替代真实治理能力 |

---

## 8. 推荐的使用方式

建议将后续评估拆成两层：

### 8.1 Layer A：Design File Audit

仅基于设计文件评分，使用以下五维：

- Foundation
- Component System
- Designer Experience
- Tokenization
- Accessibility Readiness

用途：

- 评估设计资产本身的成熟度
- 对 Figma 文件、Library、组件库做相对客观的审计
- 发现设计系统在“资产层”上的短板

---

### 8.2 Layer B：System Validation

不纳入设计文件主评分，单列为外部验证项：

- Engineering Integration
- Governance & Operations
- Adoption
- Implementation Quality
- Source Token / SSOT Compliance

用途：

- 与代码仓库、PRD、构建链路、发布机制联合审计
- 判断系统是否真的完成设计到工程的闭环

---

## 9. 最终建议

如果目标是“从设计文件视角”建立更成熟的 Design System 评分体系，推荐做法是：

1. 主评分只评估设计文件可直接举证的五个维度
2. 将工程、治理、采用等维度列为外部验证项，而非混入总分
3. 将 R2D2 的六维语言保留为高层沟通框架，但在执行层重新定义边界

这样可以避免两种常见失真：

- Figma 看起来完整，但工程上根本不可消费
- Git / token 很规范，但设计资产本身极不成熟

更稳妥的结论应该是：

`设计文件评分 = 设计资产成熟度`

而不是：

`设计文件评分 = 完整设计系统成熟度`

---

## 10. 后续可扩展方向

这份框架后续可以继续扩展为三类产物：

1. `Design File Scorecard`
   - 将五个维度细化为二级指标和权重

2. `R2D2 Audit v3`
   - 将现有六维报告拆分为“设计文件评分 + 外部验证项”

3. `Full Design System Maturity Model`
   - 联合 Figma、Token Repo、Runtime、Governance 一起评分

