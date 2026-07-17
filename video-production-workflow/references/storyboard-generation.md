# 分镜阶段

## 使用时机

用户已有完整脚本，需要分镜表、shot list、视觉拆解或后续绘图输入时使用本文件。

开始前读取 `style-guide.md`。不要改写脚本，除非用户明确要求。

## 工作流

1. 读取完整脚本。
2. 激进拆分为独立 shots。默认每个 shot 覆盖 1-2 句旁白。
3. 每个 shot 定义：
   - shot id
   - exact narration
   - visual concept
   - main subject
   - background
   - emotion
   - suggested camera/framing
   - on-screen text if needed
   - image prompt seed for drawing stage
4. 保持简单。一帧只讲一个核心想法。

## 拆分规则

- 旁白切换论点、例子、时间、地点、情绪或机制时拆分。
- 一个句子含两个视觉概念时也拆分。
- 不要为了减少行数合并多个证据节拍。
- 8 分钟脚本通常 20-45 个 shots，视旁白密度调整。

## 输出格式

```markdown
| Shot | Narration | Visual Concept | Subject | Background | Emotion | Framing | On-screen Text | Drawing Notes |
|---|---|---|---|---|---|---|---|---|
| 01 | ... | ... | ... | ... | ... | ... | ... | ... |
```

随后添加：

```markdown
## Continuity Notes
- recurring character:
- recurring color:
- repeated symbols:
- thumbnail-style candidates:
```

## 验收

每一行都必须能交给绘图阶段独立生成图片。不要出现只有人类剪辑师才懂的含糊描述。
