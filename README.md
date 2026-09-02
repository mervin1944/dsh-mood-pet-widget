# DSH 情绪桌宠挂件（dsh-mood-pet-widget）

[![Fork 自 DeepSeek-Balance-Whale-Widget](https://img.shields.io/badge/fork%20of-DeepSeek--Balance--Whale--Widget-2ea44f?logo=github)](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)

> 本仓库 **fork 自** [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)（MIT，作者 [MeteorNOX](https://github.com/MeteorNOX)），并在此之上做了 **v0.3 重构**：主显示从静态鲸鱼 PNG 换成情绪驱动视频动画，表情素材内置打包（自包含，无需外部路径）。核心余额/记账/定价逻辑沿用原项目，感谢原作者的出色工作 🐋

![DSH 情绪桌宠挂件](assets/DSH2.png)

DeepSeek Harness（DSH）Web 界面右下角的**情绪桌宠**：本体为成步堂表情动画（WebM），会根据 AI 当前操作状态**自动切换表情**——思考时托腮、读文件时举纸、写代码时指指控诉、搜索时特写反应……同时保留 DeepSeek 余额、今日已用、峰谷定价与每轮对话消耗统计。每次打开界面自动启用，标准 DSH bundle 插件。

## 特性

- 🎭 **情绪桌宠（v0.3 核心）**：监听 DSH `session/event` 追踪 AI 操作状态，驱动成步堂表情动画自动切换
  - 6 种情绪：`thinking`（托腮）/ `reading`（举纸）/ `writing`（指控）/ `searching`（特写反应）/ `running`（扶腰）/ `config`（拍桌）+ `speaking` / `idle`
  - 每种情绪映射到内置剪辑：思考/阅读/说话**循环播放**，指控/拍桌等**播一次即回**
  - 点击桌宠本体随机播放一段动作表情（覆盖当前情绪）
  - 25 秒无事件自动回 `idle`；非 idle 情绪至少展示 3 秒，避免被快速连续工具调用冲掉
- 🐋 **常驻自启**：随 DSH Web 界面每次打开自动出现（标准 DSH bundle 插件）
- 💰 **余额**：60 秒自动刷新 + 点击桌宠手动刷新；余额变化时数字**滚动动画**；瞬时网络抖动自动沿用最近余额不报错
- 📊 **今日已用**：两种模式任选（见下），显示今日消耗金额
  - **小鲸鱼记账（推荐，免令牌）**：不需要任何会话令牌，每次观测余额后用余额差值自动记账（`.dshw-usage.json`，跨天自动归零归档）
  - **实时·令牌**：填入平台会话令牌后直接调用平台用量接口，按**峰谷定价**（工作日高峰 9:00–12:00 与 14:00–18:00，其余空闲；2026-08-23 起周末全天按谷价）实时换算今日已用
- 💬 **每轮对话消耗统计**：监听本机会话事件，每轮对话结束后弹出本轮消耗金额（精确 usage，非估算）
  - 菜单可开关「每轮对话后自动显示消耗金额」；「自动关闭时间」可自定义秒数（填 0 表示不自动关闭）
  - 消耗金额泡泡显示期间，余额变动不弹普通泡泡
- 🖱️ **拖拽 + 四边四分之一吸附**（左/右/上/下，角落可组合）
- 🔄 左吸附时整体**水平镜像翻转**（文字同步反向、带动画）
- 🧸 **按压回弹**效果（按压时底部坐标不变；v0.3 移除了 Q 弹缩放挤压）
- 🎚️ **汉堡菜单**（悬停右上角出现）：大小滑块（0.6–2.5 倍）、音效切换（小黄鸭 / 音效1）、音量调节、用量模式、峰谷提示文案（默认 / 梁文峰谷 / !?强强?!）、气泡开关、每轮消耗开关与自动关闭时间
- 🔊 **音效**：按压/松手音效（可选包内 mp3，缺失时静默降级）
- 💬 **随机台词**：点击气泡切换随机台词段（加权随机，含峰谷提示/今日已用/gif 动图/卖萌吐槽），再点一次关闭；气泡总显示 5 秒自动收起
- 📐 随浏览器窗口自动缩放；文字位置/字号与视频画面联动

## 目录结构

```text
dsh-mood-pet-widget/
├── package.json          # DSH bundle 插件元数据
├── README.md             # 本文件
├── cordis.patch.yml      # 插件挂载声明
├── lib/
│   └── index.js          # 宿主侧插件本体（含 WIDGET_JS 前端逻辑）
├── assets/
│   ├── DSH2.png          # README 顶部展示图
│   ├── clips/            # 内置表情剪辑（9 个 .webm，情绪/点击动画素材）
│   ├── rua.gif           # 随机台词 gif（气泡动图，可选）
│   ├── Ya1.mp3 / Ya2.mp3 # 小黄鸭音效（可选）
│   └── D1.mp3 / D2.mp3   # 音效1（可选）
└── whale-widget-prompt.md # 完整规格/维护提示词（历史文档）
```

> 表情素材（`assets/clips/*.webm`）已**打包进仓库**，v0.3 起插件完全自包含，不依赖任何本机绝对路径。素材为成步堂（逆转裁判角色）绿幕抠像动作剪辑，仅供个人学习/娱乐，请勿商用。

## 安装

### 方式 A：直接从 GitHub 安装（推荐）

无需本地克隆，一条命令安装：

```powershell
dsh plugin --profile web add github:mervin1944/dsh-mood-pet-widget
```

说明：

- 装完后插件会出现在 DSH 的**插件管理页面**里，之后可以直接在页面里更新，无需再手动执行命令
- 网络环境需要代理时，先设置代理环境变量再执行：
  ```powershell
  $env:http_proxy="http://<ip>:<port>"; $env:https_proxy="http://<ip>:<port>"; $env:all_proxy="socks5://<ip>:<port>"; dsh plugin --profile web add github:mervin1944/dsh-mood-pet-widget
  ```
- 安装完成后重启 `dsh web`，再 F5 刷新浏览器

### 方式 B：本地安装（从当前仓库）

在**仓库根目录**（`dsh-mood-pet-widget`，即 `package.json` 所在目录）执行：

```powershell
dsh plugin --profile web add link:.
```

说明：

- `dsh plugin` 会把参数转发给 pnpm，并在成功后自动把 `dsh-mood-pet-widget` 加入 `dsh.profile.bundles`
- **`link:.` 表示链接当前目录**（仓库根目录本身就是插件包）。如果你复制了仓库到别处，用绝对路径：
  ```powershell
  dsh plugin --profile web add link:D:\你的路径\dsh-mood-pet-widget
  ```
- ⚠️ 不要用 `link:.\dsh-mood-pet-widget`——仓库里**没有** `dsh-mood-pet-widget/` 子目录，这样会安装成普通依赖而非插件，重启后挂件不出现
- 安装完成后重启 `dsh web`，再 F5 刷新浏览器
- **如果之后移动了源码目录**，必须重新执行一次 `dsh plugin --profile web add link:.<新路径>`。若提示已存在/冲突，先 `dsh plugin --profile web remove dsh-mood-pet-widget` 再重新 add

### 方式 C：发布到 npm 后安装

```powershell
dsh plugin --profile web add dsh-mood-pet-widget
```

### 给 AI 的安装说明（用 dsh 辅助安装时，直接复制给 AI）

如果你希望让另一个 DSH / AI 助手帮你安装，把下面这段发给它即可：

```
请帮我安装插件 dsh-mood-pet-widget，来源是 GitHub 仓库 mervin1944/dsh-mood-pet-widget。

步骤：
1. 确保 pnpm 可用（没有就先：npm install -g pnpm）
2. 在 Web profile 安装（任选一种来源）：
   首选，直接从 GitHub 安装（无需本地克隆，装完可在插件管理页面里更新）：
     dsh plugin --profile web add github:mervin1944/dsh-mood-pet-widget
   或从本地仓库链接安装（例如本地克隆的仓库根目录）：
     dsh plugin --profile web add link:.<仓库绝对路径>
   （注意：仓库根目录就是插件包，不要写成 link:.\dsh-mood-pet-widget 这种带子目录的路径）
3. 如果报 pnpm 阻止构建脚本（allowBuilds 相关），在 C:\Users\<用户名>\.dsh\profiles\web\pnpm-workspace.yaml 的 allowBuilds 下加对应的包 key，然后重跑
4. 重启 dsh web，然后 F5 刷新浏览器

安装后验证：
- dsh --profile web --dump-config 应该能看到 dsh-mood-pet-widget 在 bundles 里
- curl http://127.0.0.1:3080/dsh-whale/balance.json 应返回 200 JSON（含 totalBalance）
- curl http://127.0.0.1:3080/dsh-whale/mood.json 应返回 200 JSON（含 mood 字段）
- curl http://127.0.0.1:3080/dsh-whale/action/list.json 应返回 200 JSON（含 9 个 clips）
- curl http://127.0.0.1:3080/dsh-whale/widget.js 应返回 200 JS

另外请检查 DSH 凭据里是否配置了 DEEPSEEK_API_KEY（没有就提示用户配置；DEEPSEEK_PLATFORM_TOKEN 可选，不配也能用默认的记账模式）。
```

### 关于令牌（安装后必读）

> **默认不需要任何令牌。** 安装后只需配置 `DEEPSEEK_API_KEY`（拉取余额必需），「今日已用」会自动使用默认的**小鲸鱼记账**模式（余额差值本地记账），开箱即用。
>
> 「实时·令牌」模式用到的 `DEEPSEEK_PLATFORM_TOKEN`（DeepSeek 平台网页会话令牌）是**可选的**，仅在你想要更精确的实时用量换算时才需要配置。获取方式见下方「用量模式使用教程」。

## 卸载

```powershell
dsh plugin --profile web remove dsh-mood-pet-widget
```

## 情绪映射（v0.3）

| 事件 | 情绪 | 剪辑 | 播放 |
|---|---|---|---|
| `step/start` 开始处理 | `thinking` | `05_托腮思考一` / `07_托腮思考二` | 🔁 循环 |
| `tool/call` 读类工具 | `reading` | `06_举纸展示一` / `08_举纸展示二` | 🔁 循环 |
| `tool/call` 写类工具 | `writing` | `03_手指前指控诉` | ▶️ 一次 |
| `tool/call` web_search | `searching` | `09_特写反应镜头` | ▶️ 一次 |
| `tool/call` 命令行/后台 | `running` | `04_双手扶腰说话` | ▶️ 一次 |
| `tool/call` 配置/插件/目标/表情 | `config` | `02_拍桌喊话` | ▶️ 一次 |
| `tool/call` 子代理/交互 | `thinking` | 托腮组 | 🔁 循环 |
| `tool/result` 返回 | `thinking` | 托腮组 | 🔁 循环 |
| `assistant/message` 生成回复 | `speaking` | `01_站立说话` | 🔁 循环 |
| `turn/end` / 25s 无事件 | `idle` | 站立静止 | — |

完整映射表与实现见 `lib/index.js` 中 `MOOD_TOOL_MAP` / `MOOD_CLIPS` / `MOOD_SINGLE`。

## 从旧手动安装升级

如果你之前按旧方式手动安装过（复制 `whale-balance.mjs` + 改 `cordis.patch.yml`），先清理：

```powershell
$web = "$env:USERPROFILE\.dsh\profiles\web"

Remove-Item "$web\whale-balance.mjs" -ErrorAction SilentlyContinue
Remove-Item "$web\whale-balance.cjs" -ErrorAction SilentlyContinue
Remove-Item "$web\DSniang1.png" -ErrorAction SilentlyContinue
Remove-Item "$web\DSniang02.png" -ErrorAction SilentlyContinue
```

然后编辑 `$web\cordis.patch.yml`，删除这段旧补丁：

```yaml
- insert:
    - id: whale-balance-widget
      name: ./whale-balance.mjs?v=1
```

如果里面只有这段，直接改成：

```yaml
[]
```

清理后再执行上面的安装命令。

> 若旧版 `dsh-whale-widget`（npm 0.2.x）也装在 profile 里，建议先 `dsh plugin --profile web remove dsh-whale-widget` 再安装本 fork，避免两个插件同屏。

## 用量模式使用教程

### 必需的凭据

- **`DEEPSEEK_API_KEY`**（必需）：DeepSeek API 密钥，用于拉取余额（`api.deepseek.com/user/balance`）。在 DSH 凭据服务中配置即可（`dsh` 的凭据管理界面 / `.dsh/.credentials.yaml`）。

### 两种用量模式

挂件的「今日已用」有两种模式，在**菜单 → 用量**中选择：

**① 小鲸鱼记账（推荐，默认）—— 完全不需要额外配置**

每次观测到余额下降就把差值累加到当天用量，跨天自动归零归档（保留 30 天）；观测币种发生变化时只重置基准、不记差值（防止多币种账户切换污染账本）。只要配好了 `DEEPSEEK_API_KEY` 就能用，**开箱即用**。

- 账本文件：`$DSH_HOME/.dshw-usage.json`（自动生成）
- 优点：零配置、免令牌
- 说明：依赖「观测到的余额下降」累计，若 DSH 关闭期间有消耗会漏记；要精确请用令牌模式

**② 实时·令牌（可选）—— 需要 `DEEPSEEK_PLATFORM_TOKEN`**

直接调用 DeepSeek 平台用量接口，按**峰谷定价**实时换算今日已用，**精确到每小时的 token 用量**。

**令牌在哪获取：**
1. 浏览器打开并登录 **https://platform.deepseek.com**
2. 按 **F12** 打开开发者工具 → 切到 **Network（网络）** 标签
3. 在平台页面点击「用量」或刷新页面，找到名为 `usage/by_api_key/amount` 的请求
4. 点开该请求 → **Request Headers（请求标头）** → 复制 `Authorization` 的值（形如 `Bearer eyJ...` 的一长串）
5. 把整段值（含 `Bearer` 前缀或只要后面的 token 部分均可）配置为 DSH 凭据 `DEEPSEEK_PLATFORM_TOKEN`
6. 重启 `dsh web`，在**菜单 → 用量**里选择「实时·令牌」

**说明：**
- ⚠️ **令牌非必需**：不配置时挂件自动使用默认的「小鲸鱼记账」模式，功能不受影响
- 该令牌是 DeepSeek **平台网页的会话令牌**（不是 `sk-` 开头的 API key），仅在登录平台网页时有效；重新登录后可能需要重新获取
- 接口不返回金额，只返回 token 分桶，挂件会按内置峰谷定价表换算成金额；定价表在 `lib/index.js` 顶部 `PRICING` 常量，DeepSeek 调价时可自行修改

### 每轮对话消耗（无需任何凭据）

「每轮对话消耗统计」直接监听 DSH 本机会话事件，按模型真实 usage 换算金额（与今日已用同一套峰谷定价表），**不需要** `DEEPSEEK_PLATFORM_TOKEN`。

## 验证

```powershell
dsh --profile web --dump-config | Select-String -Pattern "mood-pet"

curl http://127.0.0.1:3080/dsh-whale/balance.json
curl http://127.0.0.1:3080/dsh-whale/mood.json
curl http://127.0.0.1:3080/dsh-whale/action/list.json
curl http://127.0.0.1:3080/dsh-whale/size.json
curl http://127.0.0.1:3080/dsh-whale/last-turn.json
```

- `/dsh-whale/balance.json` → 200，含 `{"ok":true,"totalBalance":...,"currency":"CNY","todayUsage":...}`
- `/dsh-whale/mood.json` → 200，含 `{"ok":true,"mood":"idle"}`（AI 干活时会变 `thinking`/`reading`/…）
- `/dsh-whale/action/list.json` → 200，含 9 个内置剪辑名
- `/dsh-whale/size.json` → GET 返回配置；PUT 写入
- `/dsh-whale/last-turn.json` → 200，含最近一轮对话消耗 `{seq, turn, amount, tokens}`
- 浏览器 F5 后右下角出现桌宠

## 常见问题

- **桌宠不出现**：确认 `dsh plugin add` 成功；`dsh --profile web --dump-config` 里能看到 `dsh-mood-pet-widget`；重启 `dsh web` 后 F5。
- **没有表情动画/一片空白**：确认 `assets/clips/` 内 9 个 webm 在插件包内（v0.3 起随包分发，勿删）；`curl /dsh-whale/action/list.json` 应返回剪辑列表。
- **余额报「未配置 DEEPSEEK_API_KEY」**：去 DSH 配置凭据。
- **今日已用显示 --**：记账模式下需要先跑一次余额观测（60 秒内自动完成）；令牌模式需要配置 `DEEPSEEK_PLATFORM_TOKEN`。
- **每轮消耗不显示**：确认菜单「每轮对话后自动显示消耗金额」已勾选；一轮对话必须完整结束（turn/end）才会结算。
- **没有声音**：确认 `assets/*.mp3` 在包内；若不想带音效文件，静默降级为无声音。
- **本地开发改了代码不生效**：使用 `link:` 安装时，修改源码后重启 `dsh web`（ESM 模块缓存）；如果用已发布版本，需要 `npm publish` 新版本后 `dsh plugin --profile web update dsh-mood-pet-widget`。
- **情绪切换太频繁/太快**：非 idle 情绪最短展示 3 秒（`setMood` 内保护）；25 秒无事件自动回 idle，可调 `MOOD_IDLE_MS`。

## 开发与维护

完整规格、视觉参数与历史维护提示词见 `whale-widget-prompt.md`（内容基于 v0.2 静态图版本，v0.3 起主显示已改为视频，部分章节已过时）。开发日志见 `DEVLOG.md`。

## 许可证

本项目基于 **MIT License** 开源，详见 [LICENSE](LICENSE)。fork 自 [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget)（MIT）。表情素材（成步堂动作剪辑）版权归原作者/Capcom 所有，仅作个人学习用途。
