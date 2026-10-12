# 构建与安装

## 内容索引

- [构建](#构建)
- [SDK 路径](#sdk-路径)
- [安装](#安装)
- [冷启动与重启](#冷启动与重启)
- [启动耗时](#启动耗时)
- [构建失败排查](#构建失败排查)

## 构建

```bash
./gradlew assembleDebug          # macOS / Linux / Git Bash
gradlew.bat assembleDebug        # Windows CMD / PowerShell
```

产物路径是**固定的**，不必每次去 `find`：

```
app/build/outputs/apk/debug/app-debug.apk
app/build/outputs/apk/release/app-release.apk
```

常用变体：

| 命令 | 作用 |
|------|------|
| `assembleDebug` | 构建，不安装 |
| `installDebug` | 构建并装到**当前唯一**设备 |
| `assembleRelease` | Release（需签名配置） |
| `clean` | 清理产物 |
| `--offline` | 离线构建 |
| `-q` | 静默，只输出错误 |

`installDebug` 在多设备下会失败；此时**先 `assembleDebug` 再用 `adb -s <serial> install`**。

## SDK 路径

Gradle 按以下顺序找 SDK：

1. `local.properties` 里的 `sdk.dir`
2. 环境变量 `ANDROID_HOME`
3. 环境变量 `ANDROID_SDK_ROOT`（已废弃但仍被识别）

`local.properties` 是**本机私有配置，不应提交到版本库**（通常已在 `.gitignore` 中）：

```properties
sdk.dir=C\:\\Users\\<user>\\AppData\\Local\\Android\\Sdk
```

报 `SDK location not found` 时就是这三处都没配。

## 安装

```bash
adb -s <serial> install -r app/build/outputs/apk/debug/app-debug.apk
```

| 参数 | 作用 |
|------|------|
| `-r` | 覆盖安装保留数据（最常用） |
| `-d` | 允许版本号降级 |
| `-g` | 安装时授予全部运行时权限，省去手点弹窗 |
| `-t` | 允许 test-only 包 |
| `-s` | 装到 SD 卡 |

```bash
adb uninstall <包名>             # 卸载（清数据）
adb shell pm clear <包名>        # 只清数据，不卸载
```

**包名和 APK 里的 applicationId 必须一致**，否则包名写错会静默装成"另一个应用"。

## 冷启动与重启

```bash
adb shell am force-stop <包名>

# 方式一：模拟桌面点击（不需要知道 Activity 名）
adb shell monkey -p <包名> -c android.intent.category.LAUNCHER 1

# 方式二：直接指定 Activity
adb shell am start -n <包名>/.MainActivity
```

`force-stop` 后再启动是**干净起点**：内存态全部丢失，可以用来验证
"状态是否真的被持久化"——重启后位置/设置还在，说明写进了存储。

`monkey` 不需要知道 Activity 名，更适合包名已知但入口类名不确定的情况；
输出里的杂讯可以用 `>/dev/null 2>&1` 丢掉。

## 启动耗时

```bash
adb shell am start -W -n <包名>/.MainActivity
```

`-W` 会等待启动完成并打印：

```
ThisTime:  1234    # 最后一个 Activity 的启动耗时
TotalTime: 1234    # 所有 Activity 累计
WaitTime:  1310    # 含系统调度，最接近用户感知
```

对比数值前先 `force-stop`，否则命中的是热启动，数字会小得离谱。

## 构建失败排查

| 现象 | 处理 |
|------|------|
| 只有一行 `FAILURE: Build failed` | 去掉 `-q`，或加 `--stacktrace` 看完整堆栈 |
| 想看清执行了哪些任务 | `--info`；更详细用 `--debug`（输出极大） |
| 依赖解析失败 | `--refresh-dependencies`；确认仓库配置与网络 |
| 疑似增量缓存出错 | `./gradlew clean` 后重建；仍不行删 `~/.gradle/caches/` |
| Gradle daemon 卡死 | `./gradlew --stop` 后重试 |

**构建前先 `--stop` 停掉 daemon** 是排查"文件被占用""改代码不生效"的常用起手式，
Windows 上尤其明显。

改动仓库级配置（`settings.gradle.kts`、`init.gradle`）后如果报仓库/插件解析冲突，
先怀疑本机的全局 `~/.gradle/init.gradle`——它会注入额外仓库与 `FAIL_ON_PROJECT_REPOS`
之类的策略，和工程自身配置打架。临时改名移走后构建、构建完再改回来，
是定位这类冲突最快的办法。
