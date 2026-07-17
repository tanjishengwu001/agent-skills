# 按音频渲染视频

## 使用时机

用户已有逐 shot 图片与语音音频，要求生成成片、按音频长度定时、导出 MP4 或固定 30fps 视频时使用。此阶段负责本地合成，不负责生成图片、配音、背景音乐或 AI 动态画面。

## 输入契约

- 音频目录必须含 `voiceover-manifest.json`，由配音阶段生成；音频文件相对该 manifest 路径解析。
- 图片目录中每个有音频的 shot 必须有同名的模型生成栅格图片：`<shot-id>.png`、`.jpg`、`.jpeg` 或 `.webp`。不接受 SVG、动画图片或本地绘图替代物。
- 只渲染 manifest 中状态为 `success` 或 `pending` 且音频文件存在的 shot；`skipped` 不生成画面。

## 尺寸规则

- **默认自动检测**：不传 `--size` 时，脚本从第一张可用图片读取实际宽高作为输出分辨率，并取偶数化以保证 H.264 兼容。
- 所有图片应保持相同尺寸（由绘图阶段保证）；如有不同，以第一张为准，其余等比缩放并补黑边。
- 如需覆盖自动检测值，可手动传 `--size WIDTHxHEIGHT`（如 `--size 1920x1080`、`--size 1080x1920`）。

## 时间与输出规则

- 固定 30fps；不得提供其他帧率选项。
- 使用 `ffprobe` 获取每段音频时长，并按累计音频时间映射到 30fps 的整帧边界；不得按句数、镜头数或估算值定时。镜头边界最多偏离音频边界半帧，必要时用静帧和静音补齐。
- 图片以静帧铺满镜头时长，等比缩放并补黑边，不裁切内容。
- 输出 H.264/AAC 的 MP4，并写入 `video-manifest.json`，其中包含每个 shot 的音频秒数、片段路径、状态、实际输出尺寸、最终成片路径和 `final_qc`。
- 合并完成后必须用 `ffprobe` 检查最终 MP4 的音视频流、帧率、分辨率和总时长。帧率、分辨率或总时长等可修复项不合格时自动重新编码一次并复检；总时长偏差不得超过 1 帧，复检仍失败时不得标记成功。
- 不添加转场；这样每个镜头音频的开始时间保持可预测。后续如增加转场，必须明确其是否覆盖画面而不移动音频时间线。

## 执行

```bash
python scripts/render_video.py \
  --audio-dir outputs/<topic-slug>/audio \
  --image-dir outputs/<topic-slug>/images \
  --output outputs/<topic-slug>/video/final.mp4 \
  --render
```

默认执行 dry run，仅检查镜头对应关系并写入 manifest（含自动检测的尺寸）。添加 `--render` 才调用 `ffmpeg`。要求系统已安装 `ffmpeg` 与 `ffprobe`；缺失时报告前置条件，不能伪造 MP4。

如需指定分辨率而非自动检测：

```bash
python scripts/render_video.py \
  --audio-dir outputs/<topic-slug>/audio \
  --image-dir outputs/<topic-slug>/images \
  --output outputs/<topic-slug>/video/final.mp4 \
  --size 1920x1080 \
  --render
```

## 验收

- 输出为 30fps；最终视频时长等于所有已渲染 shot 音频时长之和，允许封装误差不超过 1 帧（1/30 秒）。
- 输出分辨率与图片实际尺寸一致（或与用户手动指定的 `--size` 一致）。
- 每段有效音频都有同 shot 的图片和视频片段，缺失项在 manifest 中标为 `failed`。
- 最终 MP4 同时含视频和音频流，并能独立播放。
- `video-manifest.json` 中的 `size` 字段反映实际输出分辨率。
- `video-manifest.json` 中必须存在 `final_qc`，且只有 `final_qc.ok == true` 才能将最终状态标记为 `success`。
