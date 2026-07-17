# 分镜配音生成

## 使用时机

用户已有分镜并要求生成旁白音频、配音、TTS 或 voice-over 时使用。先确认分镜的 `Shot` 与 `Narration` 列完整；不要从画面描述、屏幕文字或绘图提示词推断旁白。

## 输入与输出契约

输入为 Markdown 分镜表，必须含 `Shot` 和 `Narration` 两列。为保持 provider 无关，先将可朗读的行导出为 manifest：

```json
{"version":1,"provider":"edge","voice":"zh-CN-XiaoxiaoNeural","rate":"+0%","shots":[{"id":"01","text":"第一段旁白。"}]}
```

将每个 shot 输出为一个独立音频文件，文件名固定为 `<shot-id>.mp3`；并输出 `voiceover-manifest.json` 记录 provider、voice、rate、原始文本、文件路径和失败项。不要将所有 shot 拼成一个文件，也不要在生成阶段加入背景音乐或音效。

## Provider 选择与扩展

- 默认 `edge`，使用 Python 包 `edge-tts`；若未安装，明确提示安装命令，不能伪造音频。
- 所有调用都通过 `scripts/generate_voiceover.py --provider <name>`。provider 名称、voice、rate 和音频格式写入输出 manifest，并可由命令行参数设置；业务流程不得依赖 Edge 专有文件名或 API。
- 新 provider 只需在脚本中实现同一 adapter 契约：`validate(config)`、`synthesize(text, output_path, config)`、`supported_formats`。保留 manifest schema 和逐 shot 输出不变。
- 未实现的 provider 必须快速失败，并列出已支持的 provider；不要静默回退到 Edge。

## Edge 默认值

- 中文：`zh-CN-XiaoxiaoNeural`
- 英文：`en-US-JennyNeural`
- 日文：`ja-JP-NanamiNeural`
- 未指定 voice 时，根据旁白主要语言选择上述默认值；混合语种要求用户指定 voice 或按语种拆分分镜。

## 执行

```bash
python scripts/generate_voiceover.py --storyboard outputs/<topic-slug>/03-storyboard.md --output-dir outputs/<topic-slug>/audio --provider edge
```

默认不生成音频，只检查表格并写入 manifest；真实合成需显式传 `--synthesize`。首次真实合成前检查 `edge-tts` 是否可导入；如缺失，执行环境允许时安装 `pip install edge-tts`，否则把该前置条件交给用户。

## 验收

- 每个有非空 `Narration` 的 shot 都有对应音频或明确失败记录。
- manifest 中的 `text` 与分镜 `Narration` 一致，shot id 不重复。
- 没有旁白的 shot 写入 `skipped`，不生成空音频。
- 返回音频目录、manifest 路径、provider、voice、成功数、跳过数和失败数。
