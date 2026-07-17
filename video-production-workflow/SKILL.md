---
name: video-production-workflow
description: 视频生产一体化 skill。用于选题策划、选题评分、纪录片式或解释型视频脚本、细粒度分镜、分镜绘图提示词、根据分镜生成配音、根据图片与音频渲染 30fps 视频、缩略图方向，或从想法到最终视频项目包的端到端工作流；适合用户提到 YouTube、短纪录片、解释视频、视频选题、脚本、分镜、配音、旁白音频、视频渲染、音频驱动视频、帧图提示词、缩略图或完整视频生产包时使用。skill 说明使用中文，但输出语言应跟随用户需求。
---

# Video Production Workflow

## 核心原则

默认触发全流程（选题 → 脚本 → 分镜 → 绘图 → 配音 → 渲染）。除非用户明确指定只做某个阶段，否则一律走完整工作流。

制图时默认禁止把分镜生产标签画进图片，包括 `Shot 01`、`SHOT_01`、`shot-01`、`镜头01` 等 shot 名称或编号。shot 标签只用于文件命名和生产管理；除非用户明确要求它作为画面文字出现，否则提示词必须将其列入负面约束，并在成图验收时检查。

全流程包含两道确认门禁：

1. **选题门禁（不可跳过）**：先给选题建议，等用户确认选题并设置目标视频时长后，才能进入脚本写作。即使用户说"不要打断""全自动"等，也必须停在选题阶段等待用户主动选择选题和设置时长。
2. **分镜门禁**：分镜生成后，必须停下等用户确认以下三项后，才能进入绘图及后续阶段：
   - 分镜稿内容（镜头拆分是否合理、旁白是否准确）
   - 画面比例（默认 16:9，用户可指定其他）
   - 制图风格（根据脚本内容按 `visual-styles.md` 选择规则给出推荐风格，列出全部5种风格供用户选择，或用户自定义）

**分镜门禁例外**：如果用户在触发 skill 时明确说"直接执行全流程""不要打断""全自动""一口气跑完"等，则跳过分镜门禁，从分镜直接跑到渲染，中途不停。此时按以下默认值自动决策：
- 分镜比例：16:9
- 制图风格：根据 `visual-styles.md` 的选择规则自动匹配

## 全流程默认行为

调用本 skill 时，默认读取 `references/full-workflow.md` 并按其定义的7个阶段顺序执行。每进入一个新阶段时，再按需加载该阶段对应的 reference 文件：

1. 选题阶段 → 读取 `references/topic-selection.md` + `references/style-guide.md`
2. 脚本阶段 → 读取 `references/script-writing.md` + `references/style-guide.md`
3. 分镜阶段 → 读取 `references/storyboard-generation.md` + `references/style-guide.md`
4. 分镜确认门禁 → 停下等用户确认分镜稿、画面比例、制图风格
5. 绘图阶段 → 读取 `references/frame-illustration.md` + `references/style-guide.md`；如需选择风格，读取 `references/visual-styles.md`，再只读取选中的 `references/styles/*.md`；生成提示词后必须实际调用制图模型生成每张图片，保留模型返回的正常栅格格式
6. 配音阶段 → 读取 `references/voice-generation.md`，使用 `scripts/generate_voiceover.py`（默认 provider 为 Edge）
7. 渲染阶段 → 读取 `references/video-rendering.md`，使用 `scripts/render_video.py`（固定 30fps）

## 单阶段入口

当用户明确指定只做某个阶段时，直接加载对应 reference：

- "帮我选个题" / "选题" / "评分" → `references/topic-selection.md`
- "写脚本" / 用户已确认题目 → `references/script-writing.md`
- "分镜" / "shot list" / 用户给出脚本 → `references/storyboard-generation.md`
- "绘图提示词" / "帧图" / "制图" / 用户给出分镜 → `references/frame-illustration.md`（生成提示词 + 调用制图模型实际生成图片）
- "配音" / "TTS" / "旁白" / 用户给出分镜 → `references/voice-generation.md` + `scripts/generate_voiceover.py`
- "渲染" / "合成视频" / "导出MP4" / 用户给出图片+音频 → `references/video-rendering.md` + `scripts/render_video.py`

## 输出边界

- 按用户指定语言输出；若未指定，使用用户输入的主要语言。
- 不要把一种语言的表达腔调生硬直译到另一种语言。
- 不要把一个阶段的交付混成另一个阶段：选题阶段不要提前写完整脚本；脚本阶段不要默认生成几十行分镜；分镜阶段不要改写旁白；绘图阶段不要改变脚本含义；语音阶段不要擅自改写、合并或删减分镜旁白；渲染阶段不要改变音频速度或用固定时长替代音频时长。
- 对证据、引用、事实不确定时，写入 `证据备注` 或提示需要检索，不要伪造来源。
- 最终产物必须保存到当前工作空间目录；优先按话题写入 `outputs/<topic-slug>/`，中间草稿或临时材料按话题写入 `work/<topic-slug>/`。不要把所有内容塞进一个巨型 package 文件；按功能拆成独立文件，并提供一个入口索引文件。最终回复必须给出工作空间内的交付目录和关键文件路径。

## 质量标准

每次交付都必须能直接交给下一阶段继续生产：选题要能确认，脚本要能朗读，分镜要能拆图，提示词要能生成同一视觉系统的画面，语音要能按 shot 对齐剪辑，视频要能逐镜头与音频同步播放。
