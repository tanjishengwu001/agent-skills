# 风格：小黑怪诞正文配图

适合：方法论、产品、AI、工具、工作流、复杂概念解释、文章转视频、需要清爽但有怪诞隐喻的帧图。

## 风格 DNA

- 16:9 横版。
- 纯白背景，不要米色、纸纹、阴影、渐变、噪点。
- 黑色手绘线稿为主，线条轻微抖动，不机械、不矢量、不厚重。
- 大量留白，主体约占画面 40%-60%，至少 35% 空白。
- 少量红色、橙色、蓝色手写批注，最多 5-8 处，每处尽量 2-8 个字。
- 一张图只讲一个核心动作、结构、状态或隐喻。
- 结构要自然表达，不要在图上写“流程图 / 系统架构 / 路线图”等结构类型名称。

## 小黑 IP

小黑是黑色实心小怪物，有白色圆点眼睛、细腿、空表情，认真参与一个荒诞但成立的系统动作。

小黑必须承担核心动作，不能只是站在旁边当装饰。如果去掉小黑，画面的核心隐喻仍完全成立，说明提示词失败，要重写。

小黑可以：

- 搬、拉、塞、捞、压、称、缝、剪、拧、守、推、接、拆、标记、回收。
- 卡在机器里、守门、拉线、搭桥、分拣、修补、记录、操作奇怪装置。

小黑不要：

- 变成可爱吉祥物、表情包、儿童卡通。
- 穿复杂服装、露出闪亮眼睛、做夸张卖萌表情。
- 抢走结构表达。

## 构图模式

只选一种结构：

- `Workflow 流程`：左输入，中间小黑或怪机器处理，右输出，橙色箭头表达主流向。
- `系统局部`：只画 3-5 个核心模块，小黑参与其中一个关键动作。
- `前后对比`：左混乱，右稳定，中间橙色箭头。
- `角色状态`：2-4 个小状态，每个状态一个短标注。
- `概念隐喻`：一个大的怪物件或机器，少量输入，一个输出。
- `方法分层`：一层层盒子，不要正式金字塔，小黑在旁边搬砖或搭建。
- `地图路线`：一条弯曲路径，少量节点，小黑牵线或走路。
- `小漫画分镜`：2-4 个小场景，每格只表达一个动作。

## 原创隐喻法

1. 把抽象概念换成物理动作：卡住、漏掉、变重、分拣、沉淀、发酵、开门、折叠、拆包、回流。
2. 把系统结构换成低科技物件：坏机器、纸箱、抽屉、水管、邮筒、怪表盘、秤、井、梯子、怪工位。
3. 让小黑承担动作：卡在机器里、拉错线、守门、搬运、修补、称重、扶梯子、记录。

不要复刻旧案例构图。每次都从当前脚本或分镜重新发明一个奇怪但成立的隐喻。

## 提示词骨架

```text
Generate one standalone 16:9 horizontal illustration.

Style:
小黑怪诞正文配图。Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten annotations in the target language. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring IP character required:
小黑, a small solid-black absurd character with white dot eyes, tiny thin legs, blank serious expression, slightly uneven hand-drawn body shape. 小黑 must perform the core conceptual action, not decorate the scene. Make 小黑 serious, deadpan, and slightly bizarre, not cute.

Theme:
{画面主题}

Structure type:
{Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图要表达的核心意思}

Composition:
{小黑在哪里、正在做什么、主要物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {元素4}

Handwritten labels:
{短标注1} / {短标注2} / {短标注3} / {短标注4}

Color use:
Black for main line art and 小黑. Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Invent a fresh visual metaphor for this specific script. Clear but not instructional, interesting but not childish, strange but clean.
```

## QA

必过：

- 16:9 横版。
- 干净白底。
- 小黑出现并承担核心动作。
- 画面怪诞、有创意，但 1 秒内能看懂结构。
- 主体不超过画面约 60%。
- 标注少、短、能读。
- 橙色只用于主路径或箭头；红色只用于重点、问题、提醒或结果；蓝色只用于补充说明、反馈或系统状态。

失败则重写或重生成：

- 小黑只是装饰。
- 画面像 PPT、课程课件、正式流程图。
- 元素、箭头、节点太多。
- 背景有纸纹、阴影、渐变、米色、噪点。
- 真实 UI 截图或科技感界面。
- 文字变成大段解释或错字严重。
- 左上角出现“常见坑 / Workflow / 系统架构图 / 路线图”等标题。
