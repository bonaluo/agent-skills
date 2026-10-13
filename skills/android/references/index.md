# Android 参考文档总索引

本目录下的全部参考文档。按分类组织，每个子目录有自己的 `index.md`。

## 内容索引

- [调试 debugging](#调试-debugging)
- [模拟器 emulator](#模拟器-emulator)
- [构建与安装 build](#构建与安装-build)
- [性能 performance](#性能-performance)

## 调试 debugging

在真机或模拟器上观察画面、注入操作、判断操作是否生效。

- [adb 连接](debugging/adb-connection.md) — 设备列表与状态、多设备选择、无线调试、Windows/Git Bash 路径坑
- [截屏与录屏](debugging/screencap.md) — `exec-out` 与 `shell` 的区别、录屏参数
- [坐标基准](debugging/coordinates.md) — `wm size` / `wm density`、dp 换算、`input` 用的坐标系
- [注入手势](debugging/input-injection.md) — tap / swipe / keyevent / text；fling 阈值；`motionevent` 为什么不可靠
- [定位控件](debugging/ui-inspection.md) — `uiautomator dump`、bounds 解析、Compose 语义树的限制
- [像素量测](debugging/pixel-measure.md) — ffmpeg 裁切放大；导出原始灰度逐像素核对
- [判读操作是否生效](debugging/verify-behavior.md) — 假阳性判据、语义判据、初始状态钉死
- [日志](debugging/logs.md) — 崩溃缓冲区、按级别与 tag 过滤、厂商噪声识别

子索引：[debugging/index.md](debugging/index.md)

## 模拟器 emulator

- [SDK 与系统镜像](emulator/sdk-and-images.md) — cmdline-tools、`sdkmanager`、接受许可、常见目录
- [AVD 管理](emulator/avd-manage.md) — 列出 / 创建 / 删除 AVD，调整内存与磁盘，AVD 存放位置
- [启动与排障](emulator/launch-and-troubleshoot.md) — 启动参数、等待开机完成、启动失败排查
- [与真机的差异](emulator/vs-real-device.md) — 什么该在模拟器上验，什么必须上真机

子索引：[emulator/index.md](emulator/index.md)

## 构建与安装 build

- [构建与安装](build/build-and-install.md) — gradlew 构建、adb 安装、冷启动验证、启动耗时

子索引：[build/index.md](build/index.md)

## 性能 performance

- [帧统计](performance/frame-stats.md) — `dumpsys gfxinfo` 采集与判读，判断瓶颈在主线程、图片上传还是绘制

子索引：[performance/index.md](performance/index.md)
