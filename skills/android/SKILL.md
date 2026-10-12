---
name: android
description: Operate and debug Android apps on real devices and emulators through adb — capture the screen, inject taps and swipes, locate UI nodes, measure pixels, read logs, manage AVDs, build and install, and read frame statistics. Use when an Android app must be driven, verified, or diagnosed from the command line. / 通过 adb 在真机与模拟器上操控和调试 Android 应用 —— 截屏、注入点击与滑动、定位控件、量测像素、读取日志、管理模拟器、构建安装、读取帧统计。需要从命令行驱动、验证或诊断 Android 应用时使用。
tags: [android, adb, emulator, device, debugging, gradle, performance]
metadata:
  version: 20261013.0015
  update-url: https://github.com/bonaluo/agent-skills@android
---

# Android

从命令行操控和验证 Android 应用。通道只有一条：**adb**。
它的能力上限是——注入输入事件、截屏录屏、安装卸载、读日志、dump 控件树。
不需要 root，也因此拿不到应用内部状态，只能从外部观察行为。

## 通用原则

1. **先确认设备规格**（`wm size` / `wm density`），再谈坐标。按 dp 直接取像素坐标一定偏。
2. **手势一律用单条 `input swipe` 或 `input tap`**。用 `input motionevent` 拼接多段手势会得到不可复现的结果。
3. **判据要选「只有目标操作才能造成」的差异**。截图变了不等于操作生效——异步内容本来就会改画面。
4. **不要假设注入的事件是"假的"**。注入走的是正常输入分发管线，控件收到的和真手指完全一样；手势没生效就是真的没生效。
5. **改一个变量，观察一次**。多变量同时变，结论一定不可靠。
6. **厂商模拟器/真机的日志噪声很大**。按 tag 和 pid 过滤，别只看日志级别。

## 分类索引

### 调试 debugging

在真机或模拟器上观察画面、注入操作、判断操作是否生效。

| 文档 | 解决什么问题 |
|------|--------------|
| [adb-connection](references/debugging/adb-connection.md) | 设备认不到、多设备选择、无线调试、Windows 路径坑 |
| [screencap](references/debugging/screencap.md) | 稳定拿到一手画面；录屏 |
| [coordinates](references/debugging/coordinates.md) | dp 与物理像素换算，`input` 坐标从哪来 |
| [input-injection](references/debugging/input-injection.md) | tap / swipe / keyevent；惯性阈值；motionevent 为什么不能用 |
| [ui-inspection](references/debugging/ui-inspection.md) | uiautomator dump；Compose 语义树的限制 |
| [pixel-measure](references/debugging/pixel-measure.md) | 从截图里量出精确到像素的尺寸 |
| [verify-behavior](references/debugging/verify-behavior.md) | 避开假阳性判据 |
| [logs](references/debugging/logs.md) | 崩溃、异常、厂商噪声过滤 |

→ 子索引：[references/debugging/index.md](references/debugging/index.md)

### 模拟器 emulator

创建 AVD、启动、排查启动失败，以及真机与模拟器的取舍。

| 文档 | 解决什么问题 |
|------|--------------|
| [sdk-and-images](references/emulator/sdk-and-images.md) | 装 cmdline-tools / system-image，接受许可 |
| [avd-manage](references/emulator/avd-manage.md) | 列出、创建、删除 AVD，调整内存与磁盘 |
| [launch-and-troubleshoot](references/emulator/launch-and-troubleshoot.md) | 启动参数、等待开机完成、常见失败 |
| [vs-real-device](references/emulator/vs-real-device.md) | 什么该在模拟器上验，什么必须上真机 |

→ 子索引：[references/emulator/index.md](references/emulator/index.md)

### 构建与安装 build

| 文档 | 解决什么问题 |
|------|--------------|
| [build-and-install](references/build/build-and-install.md) | gradlew 构建、adb 安装、冷启动验证、启动耗时 |

→ 子索引：[references/build/index.md](references/build/index.md)

### 性能 performance

| 文档 | 解决什么问题 |
|------|--------------|
| [frame-stats](references/performance/frame-stats.md) | dumpsys gfxinfo 采集与判读，找瓶颈在哪一层 |

→ 子索引：[references/performance/index.md](references/performance/index.md)

## 目录结构

```
android/
├── SKILL.md                      # 本文件：总索引
└── references/
    ├── index.md                  # 全部参考文档总索引
    ├── debugging/                # 调试
    ├── emulator/                 # 模拟器
    ├── build/                    # 构建与安装
    └── performance/              # 性能
```

每个子目录都有自己的 `index.md`；新增文档时同步更新所在目录的 `index.md` 与本文件的分类表。

## 关联技能

- `skill-user-habits`：修改本技能后必须更新 `metadata.version`；不要自动打包。
