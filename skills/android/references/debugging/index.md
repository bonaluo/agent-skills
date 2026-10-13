# 调试 — 子索引

在真机或模拟器上观察画面、注入操作、判断操作是否生效。

## 内容索引

- [adb 连接](#adb-连接)
- [截屏与录屏](#截屏与录屏)
- [坐标基准](#坐标基准)
- [注入手势](#注入手势)
- [定位控件](#定位控件)
- [像素量测](#像素量测)
- [判读操作是否生效](#判读操作是否生效)
- [日志](#日志)
- [推荐工作流](#推荐工作流)

## 文档一览

| 文档 | 解决什么问题 | 何时读 |
|------|--------------|--------|
| [adb-connection](adb-connection.md) | 设备认不到、多设备、无线调试、路径坑 | 开始任何操作之前 |
| [screencap](screencap.md) | 稳定拿到一手画面 | 需要看屏幕时 |
| [coordinates](coordinates.md) | dp 与像素换算、坐标系 | 要把设计稿坐标变成 `input` 参数时 |
| [input-injection](input-injection.md) | tap / swipe / keyevent、惯性、motionevent 坑 | 要点或拖的时候 |
| [ui-inspection](ui-inspection.md) | `uiautomator dump`、Compose 语义树 | 不知道控件坐标时 |
| [pixel-measure](pixel-measure.md) | 从截图量精确尺寸 | 要核对布局尺寸时 |
| [verify-behavior](verify-behavior.md) | 假阳性判据、语义判据 | 判断"操作到底生效没有"时 |
| [logs](logs.md) | 崩溃、异常、厂商噪声 | 排查失败原因时 |

## 推荐工作流

1. **连接**：`adb devices` 确认状态为 `device`；多设备一律带 `-s`。
2. **摸清规格**：`wm size` + `wm density`，把 dp 换算成像素。
3. **截图看现状**：`exec-out screencap -p`，先确认目标位置。
4. **定位控件**：优先 `uiautomator dump` 拿 bounds；定位不到再靠截图目视估坐标。
5. **注入单个手势**：一条 `input swipe` / `input tap`，不要拼接。
6. **判读结果**：选只有该操作能造成的差异，不要用"截图变了"。
7. **需要精确尺寸时**：用 ffmpeg 裁切放大，或导出灰度值逐像素核对。
