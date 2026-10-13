# 模拟器 — 子索引

创建 AVD、启动、排查启动失败，以及真机与模拟器的取舍。

## 内容索引

- [文档一览](#文档一览)
- [推荐流程](#推荐流程)
- [环境变量](#环境变量)

## 文档一览

| 文档 | 内容 |
|------|------|
| [sdk-and-images](sdk-and-images.md) | 安装 cmdline-tools、下载 system-image、接受许可；SDK 目录结构 |
| [avd-manage](avd-manage.md) | 列出 / 创建 / 删除 AVD；设备型号模板；调整内存与磁盘；AVD 存放位置 |
| [launch-and-troubleshoot](launch-and-troubleshoot.md) | 启动参数（无界面、GPU、快照、临时写入）；等待开机完成；常见失败 |
| [vs-real-device](vs-real-device.md) | 模拟器缺什么；什么该在模拟器上验，什么必须上真机 |

## 推荐流程

```bash
# 1. 装命令行工具并接受许可
sdkmanager --licenses

# 2. 装系统镜像（按需要选 API 与架构）
sdkmanager "platform-tools" "emulator" "system-images;android-34;google_apis;x86_64"

# 3. 建 AVD
avdmanager create avd -n test34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6

# 4. 启动（无界面）
emulator -avd test34 -no-window -no-audio -no-boot-anim -gpu swiftshader_indirect &

# 5. 等开机完成（光 wait-for-device 不够，要等 boot_completed）
adb wait-for-device
until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1" ]; do sleep 2; done

# 6. 装包并启动
adb install -r app-debug.apk
```

## 环境变量

SDK 根目录的两种常见位置：

| 平台 | 默认路径 |
|------|----------|
| Windows | `%LOCALAPPDATA%\Android\Sdk` |
| macOS / Linux | `~/Library/Android/sdk` / `~/Android/Sdk` |

```bash
export ANDROID_HOME="$LOCALAPPDATA/Android/Sdk"      # Git Bash
export ANDROID_HOME="$HOME/Library/Android/sdk"      # macOS
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
```

Gradle 工程里更常见的是 `local.properties`：

```properties
sdk.dir=C\:\\Users\\<user>\\AppData\\Local\\Android\\Sdk
```

**`sdkmanager` / `avdmanager` 在 `cmdline-tools/latest/bin/` 下**，不在 `tools/`。
只装了 Android Studio 没装 cmdline-tools 时，这两个命令不存在。
