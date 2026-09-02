# dsh-whale-widget 开发日志

> 基于 [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget) 的本地迭代记录
> 当前版本：v0.2.10 → v0.3.0（开发中）

---

## 一、目的

将 DSH Web 界面右下角的余额挂件，从静态的「小鲸鱼余额显示」改造为**一个能根据 AI 当前操作状态自动切换表情动画的交互式桌宠**。

### 核心改版方向

| 改版前 | 改版后 |
|---|---|
| 静态 PNG 鲸鱼图（`DSniang1.png`） | 视频主显示（`01_站立说话.webm` 第一帧） |
| 点击播放随机台词气泡 | 点击播放随机动作表情动画 |
| 无状态感知 | 通过 `session/event` hook 追踪 AI 操作状态 |
| 固定外观 | 根据操作自动切换不同动画表情 |

---

## 二、做了什么

### 2.1 图片问题修复

- **黑色底色**：原鲸鱼图 `DSniang1.png` 边缘有半透明黑边（抠像残留），已确认本地文件已修正为正确透明背景。但当前运行中的 dsh web 进程缓存了旧字节，需重启后生效。
- **朝向镜像**：原图已水平翻转（`RotateFlip(FlipX)`），原图备份为 `.orig-bak` 文件。

### 2.2 汉堡菜单修复

- `onDocClickStopper` 全局 click 拦截器缺少菜单/菜单按钮/气泡区域的排除判断，导致汉堡按钮被误判为"鲸鱼命中"而吞掉点击事件。
- 修复后即使图片在按钮位置不透明，点击菜单按钮也能正常打开菜单。

### 2.3 静态图替换为视频第一帧

- 移除 `<img>` 元素和 `.dshwv-img` CSS 规则。
- 新增 `<video>` 主显示元素（`mainVid`），默认加载 `01_站立说话.webm` 并停在第一帧。
- 视频覆盖整个挂件区域（100% × 100%），`object-fit: contain; object-position: bottom center` 底部居中。
- `transform: scaleX(-1)` 镜像翻转，与图片朝向一致。
- 移除了旧的 Canvas 像素级命中检测（`hitCanvas`/`setupHitTest`），改用 widget 边界矩形检测。

### 2.4 点击播放随机表情动画

- **后端**：新增 `/dsh-whale/action/list.json`（返回可用剪辑列表）和 `/dsh-whale/action/data.webm?name=xxx`（服务 WebM 文件）两条路由。
- **前端**：点击鲸鱼（非拖拽）时，从 9 个成步堂表情动画中随机选一个播放，气泡和余额刷新不变。

### 2.5 智能情绪追踪（核心新功能）

**后端**（`lib/index.js` `apply()` 内）：

- 在 `handleSessionEvent` 中扩展情绪追踪逻辑，在所有事件类型上运行，抢在原有的用量统计 early return 前。
- 情绪状态通过 `currentMood` 变量维护，25 秒无事件自动回 `idle`。
- 新增 `GET /dsh-whale/mood.json` 端点，返回 `{ok, mood}`。
- 最短展示时间：每个非 idle 情绪至少展示 3 秒才允许被覆盖，避免快速连续工具调用导致上一个情绪来不及展示。

**前端**（`WIDGET_JS` 内）：

- 新增 `MOOD_CLIPS` 情绪→视频映射表和 `MOOD_SINGLE` 单次播放标记。
- 每 1.5 秒轮询 `/dsh-whale/mood.json`，情绪变化时自动播对应视频。
- 视频播完后的行为：`thinking`/`reading`/`speaking` 循环播放，`writing`/`searching`/`running`/`config` 播一次后恢复静态。

### 2.6 去除 Q 弹按压效果

- 移除了 `body.style.transform = SQUISH`（`scaleY(0.88) scaleX(1.05)`）的视觉挤压效果。
- 音效系统保留不变（按压/松手音效仍在播放）。

### 2.7 表情素材挂载

- 后端新增 `listActionClips()` 和 `readActionClip()` 函数，读取 `D:\Code\bilibili-gb\分割` 目录下的 9 个 WebM 文件。
- 使用 `path.basename` 路径防护，防止路径穿越攻击。

---

## 三、情绪映射表

### 事件 → 情绪（后端 `handleSessionEvent`）

| 事件 | 情绪 |
|---|---|
| `step/start`（开始处理） | `thinking` |
| `tool/call` 且工具名在映射表中 | 按映射表 |
| `tool/call` 但工具名不在映射表中 | `thinking`（fallback） |
| `tool/result`（工具返回结果） | `thinking` |
| `assistant/message`（生成回复） | `speaking` |
| `turn/end`（对话轮结束） | `idle` |
| 25 秒无事件 | `idle`（超时） |

### 工具名 → 情绪映射表（`MOOD_TOOL_MAP`）

| 类别 | 官方工具名 | 情绪 | 视频 | 播放行为 |
|---|---|---|---|---|
| 文件-读 | `read`, `read_image`, `glob`, `grep`, `list_agents` | `reading` | `06_举纸展示一` / `08_举纸展示二` | 🔁 循环 |
| 文件-写 | `edit`, `write`, `todo_write` | `writing` | `03_手指前指控诉` | ▶️ 一次 |
| 搜索 | `web_search` | `searching` | `09_特写反应镜头` | ▶️ 一次 |
| 命令行 | `pwsh`, `bash` | `running` | `04_双手扶腰说话` | ▶️ 一次 |
| 后台任务 | `job_output`, `job_list`, `job_kill` | `running` | `04_双手扶腰说话` | ▶️ 一次 |
| 子代理 | `subagent`, `subagent_fork`, `workflow`, `ralph`, `send_message`, `interrupt_agent` | `thinking` | `05_托腮思考一` / `07_托腮思考二` | 🔁 循环 |
| 交互 | `skill`, `ask_user_question` | `thinking` | `05_托腮思考一` / `07_托腮思考二` | 🔁 循环 |
| 配置/插件 | `plugin_manage`, `plugin_discover`, `config_backup`, `config_restore`, `config_list_snapshots`, `config_sync_pull`, `config_sync_push` | `config` | `02_拍桌喊话` | ▶️ 一次 |
| 目标/表情 | `create_goal`, `get_goal`, `update_goal`, `learn_meme`, `send_meme` | `config` | `02_拍桌喊话` | ▶️ 一次 |

> 注：所有工具名均通过检查 DSH 源码中 `ctx.tools.register({ name: ..., ... })` 的实际注册名确认。

---

## 四、没做什么

### 4.1 未实现的功能

| 功能 | 原因 |
|---|---|
| **视频代替静态图的帧提取** | 当前使用 `<video>` 加载 WebM 文件并停在第一帧代替静态图。理想的方案是用 ffmpeg 提取首帧为 PNG 后混成（避免视频加载延迟），但环境未安装 ffmpeg。 |
| **视频转 GIF/APNG** | 同上，无 ffmpeg 可用。若用户希望用 `<img>` 加载动画而非 `<video>`，需先用 ffmpeg 将 WebM 转 GIF。 |
| **情绪状态持久化** | 重启 dsh web 后 `currentMood` 从 `idle` 开始，需等到首个 `step/start` 事件才更新。短期无影响，因情绪是实时状态。 |
| **自定义情绪→视频映射的菜单 UI** | 当前硬编码在 `MOOD_CLIPS` 中。可在汉堡菜单中加配置页让用户自定义。 |
| **多会话情绪隔离** | 当前 `currentMood` 是全局变量，所有会话共享。多会话并行时最后一个事件覆盖前一个。 |
| **情绪变化动画过渡** | 视频切换是立即的（`src` 替换 + `load()`），没有淡入淡出过渡。 |
| **静态图降级方案** | 如果 WebM 文件加载失败，没有回退到 PNG 鲸鱼图的降级逻辑。 |

### 4.2 未修改的原有功能

| 功能 | 状态 |
|---|---|
| 余额显示与刷新 | ✅ 不变 |
| 今日已用双模式（记账/令牌） | ✅ 不变 |
| 峰谷定价 | ✅ 不变 |
| 每轮对话消耗统计 | ✅ 不变 |
| 随机台词气泡 | ✅ 不变 |
| 音效系统 | ✅ 不变 |
| 拖拽吸附 | ✅ 不变 |
| 汉堡菜单（除点击修复外） | ✅ 不变 |
| 左吸附翻转 | ✅ 不变 |
| 配置持久化 | ✅ 不变 |

---

## 五、问题与待解决

### 5.1 已知问题

| # | 问题 | 优先级 | 状态 |
|---|---|---|---|
| 1 | **dsh web 进程缓存旧图片字节**：`loadImage()` 的 `imageBytes` 变量永久缓存，不检查文件 mtime，本地改了 PNG 不重启不生效 | 🔴 高 | 待修复（需重启） |
| 2 | **测试时情绪被检测工具冲掉**：用 `pwsh` 查 mood.json 时，`pwsh` 的 `tool/call` 覆盖当前情绪。已加 3 秒最短展示保护，但极端情况仍可能被冲 | 🟡 中 | 已部分修复 |
| 3 | **WebM 视频加载延迟**：首次加载或切换 src 时有短暂黑屏/等待，因视频需解码后才显示第一帧 | 🟡 中 | 未修复 |
| 4 | **视频方向与静态图不完全一致**：`mainVid` 加了 `scaleX(-1)` 镜像，但成步堂角色朝向与旧鲸鱼图不同 | 🟢 低 | 可调 |
| 5 | **bilibili-gb 路径硬编码**：`ACTION_CLIPS_DIR = 'D:/Code/bilibili-gb/分割'` 是绝对路径，他人无法使用 | 🟢 低 | 未修复 |

### 5.2 待优化

- **情绪优先级**：某些情绪（如 `config` 拍桌喊话）应该有更高展示优先级，不被普通工具调用覆盖。
- **视频预加载**：在空闲时预加载下一个可能用到的视频，减少切换延迟。
- **多 session 支持**：当前情绪为全局变量，多会话/子代理并行时行为不确定。
- **更细腻的情绪粒度**：目前 6 个情绪 + idle，可以细分更多状态（如 `error` → 拍桌、`success` → 双手扶腰）。

### 5.3 依赖的外部资源

- 表情动画素材源：`D:\Code\bilibili-gb\分割\`（9 个 `.webm` 文件）
- 素材来源：成步堂绿幕抠像，经 `分割` 处理为独立动作片段
- 若需他人使用，需将 WebM 文件打包进 assets 或提供配置路径

---

## 六、改动清单

### `lib/index.js` 的改动记录

| 改动 | 行（约） | 说明 |
|---|---|---|
| 新增 `ACTION_CLIPS_DIR` 常量 | 65 | 指向 `D:/Code/bilibili-gb/分割` |
| 新增 `STATIC_CLIP_NAME` 常量 | 136 | `'01_站立说话.webm'` |
| 移除 `.dshwv-img` CSS 规则 | 143 | 不再需要 |
| 移除 `IMG_URL` 常量 | 133 | 不再使用 |
| 移除 `<img>` 元素创建 | 191-195 | 替换为 `<video>` |
| 新增 `<video>` 主显示元素 + 情绪逻辑 | 405-483 | 完整新逻辑 |
| 新增 `MOOD_URL`/`MOOD_CLIPS`/`MOOD_SINGLE` | 422-431 | 情绪映射 |
| 新增 `pollMood()` / `playMoodClip()` / `showStaticClip()` | 434-481 | 情绪轮询与播放 |
| 修改 `endDrag` 点击分支 | 1240 | `triggerAction` → `playActionClip` |
| 修改 `isWhaleHit` | 1146 | Canvas 像素检测 → 边界矩形 |
| 移除 `hitCanvas`/`setupHitTest`/`triggerAction`/`hideActionVid` | 1147-1181 | 已被替代 |
| 移除 `setupHitTest()` 调用 | 1309 | 不再需要 |
| 移除 SQUISH 常量 + body transform 赋值 | 995 | 去除 Q 弹视觉效果 |
| 新增 `currentMood`/`moodSetAt`/`moodTimer` | 1479 | 情绪追踪变量 |
| 新增 `MOOD_TOOL_MAP`/`moodForTool`/`setMood` | 1482-1507 | 情绪追踪逻辑 |
| 扩展 `handleSessionEvent` 情绪追踪 | 1524-1533 | 在所有事件类型前跑 |
| 新增 `listActionClips()`/`readActionClip()` | 1500-1524 | WebM 文件列表/读取 |
| 新增 `/dsh-whale/action/list.json` 路由 | 1958 | 返回可用剪辑列表 |
| 新增 `/dsh-whale/action/data.webm` 路由 | 1968 | 服务 WebM 文件 |
| 新增 `/dsh-whale/mood.json` 路由 | 2049 | 返回当前情绪 |
| 修改 `onDocClickStopper` 菜单排除 | 1192-1198 | 修复菜单点击穿透 |

### 图片资源改动

| 文件 | 改动 |
|---|---|
| `assets/DSniang1.png` | 水平镜像翻转（`.orig-bak` 为备份） |
| `assets/DSniang02.png` | 水平镜像翻转（`.orig-bak` 为备份） |

---

## 七、v0.3.0 fork 整理（2026-09-02）

### 7.1 决策：从原仓库 fork 自建

- 改动已达"产品方向"级别（静态鲸鱼 → 情绪驱动视频桌宠），且表情素材为 Capcom 角色（成步堂）bilibili 抠像，不适合作为 PR 打回原仓库。
- GitHub 仓库：**https://github.com/mervin1944/dsh-mood-pet-widget**（由原仓库 fork + 改名而来，保留 fork 血缘，`upstream` remote 指向原仓库）。
- npm 包名：`dsh-whale-widget` → **`dsh-mood-pet-widget`**（v0.3.0），`dsh` 名确认未被占用。

### 7.2 清理废弃资源（本次完成）

| 项 | 处理 | 说明 |
|---|---|---|
| `assets/DSniang1.png` | 🗑️ 删除 | 旧鲸鱼本体；v0.3 前端已无任何引用 |
| `assets/DSniang02.png` | 🗑️ 删除 | 备用整图，同上 |
| `*.png.orig-bak` ×2 | 🗑️ 删除 | 本地翻转备份，不应进仓库 |
| `/dsh-whale/image.png` 路由 | 🔧 移除 | 前端无消费者（IMG_URL 早已删除） |
| `loadImage()` + `imageBytes` | 🔧 移除 | 死代码；顺带解决旧 5.1 #1 的 imageBytes 缓存问题 |
| `IMAGE_CANDIDATES` 常量 | 🔧 移除 | 死代码 |
| `assets/rua.gif` | ↩️ 回退 94KB 原版 | 功能在用（13.7% 概率 gif 台词组），3MB 工作区版本来历不明，回退避免仓库膨胀 |

### 7.3 表情素材自包含（解决旧 5.1 #5 硬编码路径）

- 9 个 WebM（共 1.64MB）从 `D:/Code/bilibili-gb/分割` 复制进 **`assets/clips/`**。
- `ACTION_CLIPS_DIR`：绝对路径 → `path.join(PACKAGE_ROOT, 'assets', 'clips')`，clone 即用，他人可安装。

### 7.4 包身份改名

| 文件 | 改动 |
|---|---|
| `package.json` | name/version(0.3.0)/repository/bugs/homepage/keywords → dsh-mood-pet-widget |
| `cordis.patch.yml` | id/name → dsh-mood-pet-widget（cordis 按 name import 包，必须一致） |
| `lib/index.js` | `const name` → `'dsh-mood-pet-widget'` |
| `README.md` | 全面同步：新名/目录结构/安装地址/情绪映射表/FAQ/素材声明 |
| `LICENSE` | 保留 MeteorNOX 版权，追加 mervin1944 版权行 |

### 7.5 遗留待办（自 fork 起）

- 5.1 #2 情绪被检测工具冲掉（3 秒保护已缓解）；#3 WebM 加载延迟；#4 视频朝向
- 5.2 情绪优先级/视频预加载/多 session 隔离/更细粒度情绪（error/success）
- whale-widget-prompt.md 基于 v0.2 静态图版本，已标注过时

---

*文档生成日期：2026-09-02*
*下次更新：情绪追踪效果验证后*
