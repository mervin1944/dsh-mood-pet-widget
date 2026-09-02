# dsh-mood-pet-widget 待办问题（TODO）

> 最近一次气泡改版（异议气泡 + 阿里妈妈字体 + 文字旋转/描边/投影）后引入的回归问题。
> 记录时间：2026-09-02

---

## Q1. 气泡和文字要作为整体可以拖动位置

**状态**：未修复

**背景**：
- 气泡从原来的 SVG 椭圆对话泡改成了**逆转裁判气泡背景图**（`bubbles.webp`，`<img class="dshwv-bubble-bg">`），文字层是独立的 `.dshwv-text`。
- 气泡背景图和文字现在是**两个独立元素**，坐标/锚定关系需要重新核对。

**期望行为**：
- 气泡底板 + 内部文字**作为整体**随桌宠拖动、随边缘吸附镜像翻转（左吸附 `scaleX(-1)` 时要能正确镜像文字和底板）。
- 拖拽时气泡不应脱离桌宠主体。

**可能相关**：
- `.dshwv-bubble-bg` 用了 `aspect-ratio: 1700/1248`（对齐原图比例），但文字层 `.dshwv-text` 定位在 `left:50%;top:50%`，两者中心是否真正重合需验证。
- 左吸附的 `scaleX(-1)` 对 `<img>` 和文字各自的 transform 叠加关系。

---

## Q2. 气泡点击后原有的"切换文字展示"功能失效

**状态**：未修复

**背景**：
- 原来点击气泡会**切换随机台词段**（`bubbleRandomActive` + `pickRandomLines` → `applyBubbleLines`），点击气泡本身有 `click` 事件监听（`bubbleBox.addEventListener('click', ...)`）。
- 改版后气泡背景图（`<img class="dshwv-bubble-bg">`）或新增元素可能**挡住了点击**，或 `.dshwv-bubble` 的 `pointer-events` 被 `dshwv-bubble-bg` 的 `pointer-events:none`/层级影响，导致点击不再触发 `bubbleBox` 的 click 监听。

**期望行为**：
- 点击气泡 → 切换随机台词段（峰谷提示/今日已用/卖萌吐槽/gif 动图），再点一次关闭。
- 点击事件不能被背景图或其他新元素吞掉。

**可能相关**：
- `.dshwv-bubble-bg` 的 `pointer-events` 值（当前是 `none`，需确认是否导致整个 bubble box 无法点击）。
- `.dshwv-text` / `.dshwv-gif` 的 `pointer-events` 与点击事件命中。
- `bubbleBox` 的 `z-index` / 层级是否被气泡背景图遮挡。

---

## 备注

- 这两个问题都与"气泡改版"强相关，建议修复时**一起核对**气泡的 DOM 层级、pointer-events、以及点击事件流。
- 相关文件：`lib/index.js`（前端 WIDGET_JS 的气泡/文字/点击逻辑）。
