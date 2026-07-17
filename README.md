# video-production-workflow

一站式视频生产 skill，覆盖解释型 / 短纪录片式视频的完整流水线。

## 流程概览

```text
选题 → 脚本 → 分镜 → [确认门禁] → 制图 → 配音 → 渲染成片
```

默认走全流程。用户明确指定某一阶段时，可只执行该阶段。

## 两道确认门禁

1. **选题门禁（不可跳过）**  
   先给出选题建议，用户确认选题并设置目标时长后，才能进入脚本。即使要求「全自动」也必须停在此处。

2. **分镜门禁（默认可确认，可跳过）**  
   分镜生成后，确认分镜稿、画面比例（默认 16:9）、制图风格后再继续。  
   若用户一开始就说「直接执行全流程 / 不要打断 / 全自动」，则跳过本门禁，按默认比例与自动匹配风格继续。

## 目录结构

```text
video-production-workflow/
├── SKILL.md                 # Skill 入口与编排规则
├── agents/
│   └── openai.yaml          # Agent 界面元数据
├── references/              # 各阶段详细规范（按需加载）
│   ├── full-workflow.md
│   ├── topic-selection.md
│   ├── script-writing.md
│   ├── storyboard-generation.md
│   ├── frame-illustration.md
│   ├── voice-generation.md
│   ├── video-rendering.md
│   ├── style-guide.md
│   ├── visual-styles.md
│   └── styles/              # 5 种制图风格
└── scripts/
    ├── generate_voiceover.py  # 逐 shot TTS 配音
    └── render_video.py        # 图片 + 音频 → 30fps MP4
```

## 制图风格

| 风格 | 适合场景 |
| --- | --- |
| 小黑怪诞正文配图 | 方法论、产品、AI、工具、文章转视频 |
| 白底手绘解释图 | 通用科普、心理学、历史机制 |
| 黑底象征性恐惧 | 存在主义、死亡、未知、风险 |
| 高饱和单物图标 | 缩略图、章节封面、概念卡 |
| 漫画大字场景 | 强 hook、冲突场景、短视频开场 |

## 交付物

完整项目包写入工作空间，按话题分目录：

```text
outputs/<topic-slug>/
├── index.md
├── 01-topic.md … 06-evidence-notes.md
├── audio/          # 逐 shot 旁白 + manifest
├── images/         # 帧图与缩略图
└── video/          # final.mp4 + manifest
```

中间草稿可放在 `work/<topic-slug>/`。

## 脚本依赖

配音与渲染阶段需要本机环境：

- **Python 3** + [`edge-tts`](https://pypi.org/project/edge-tts/)（默认配音 provider）
- **ffmpeg / ffprobe**（渲染与音频时长探测）

```bash
pip install edge-tts
# macOS 示例
brew install ffmpeg
```

## 使用方式

将本 skill 目录安装到 Agent 可加载的 skills 路径，然后在对话中触发，例如：

- 「用 video-production-workflow 做一期解释视频」
- 「帮我选题 / 写脚本 / 做分镜 / 配音 / 渲染」
- 「直接执行全流程，一口气跑完」（仍需过选题门禁）

详细编排规则见 [`SKILL.md`](./video-production-workflow/SKILL.md)。

## License

[Apache License 2.0](./LICENSE)
