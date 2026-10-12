# SDK 与系统镜像

## 内容索引

- [SDK 目录结构](#sdk-目录结构)
- [sdkmanager 常用命令](#sdkmanager-常用命令)
- [系统镜像怎么选](#系统镜像怎么选)
- [接受许可](#接受许可)

## SDK 目录结构

```
$ANDROID_HOME/
├── cmdline-tools/latest/bin/    # sdkmanager / avdmanager
├── platform-tools/              # adb、fastboot
├── emulator/                    # emulator 可执行文件
├── platforms/android-34/        # 编译用的 android.jar
├── build-tools/34.0.0/          # aapt2、d8 等
└── system-images/
    └── android-34/
        └── google_apis/
            └── x86_64/          # AVD 从这里取镜像
```

**`platform-tools`、`emulator`、`platforms`、`build-tools` 是四件不同的东西。**
装了 Android Studio 不等于命令行下可用——`adb` 在 `platform-tools`，
`emulator` 是独立包。

## sdkmanager 常用命令

```bash
sdkmanager --list                       # 列出已装 + 可装
sdkmanager --list_installed             # 只列已装
sdkmanager --install "pkg;name;..."     # 安装
sdkmanager --uninstall "pkg"            # 卸载
sdkmanager --update                     # 更新全部
```

也可以用 `--sdk_root=` 指定 SDK 位置（多 SDK 并存时）：

```bash
sdkmanager --sdk_root="$ANDROID_HOME" --install "emulator"
```

包名用分号分层，**含分号时必须加引号**，否则 shell 会截断：

```bash
sdkmanager "platform-tools" "emulator" "platforms;android-34" "build-tools;34.0.0"
```

## 系统镜像怎么选

包名格式：

```
system-images;<API 级别>;<变体>;<ABI>
```

| 变体 | 是否带 Google 应用 | 可否 `adb root` |
|------|-------------------|----------------|
| `default` | 否，纯 AOSP | 是 |
| `google_apis` | 部分（无 Play 商店） | 是 |
| `google_apis_playstore` | 完整 Play 商店 | **否**（且不可 `-writable-system`） |

| ABI | 适用 |
|-----|------|
| `x86_64` | Intel/AMD 宿主机，最快，首选 |
| `arm64-v8a` | Apple Silicon 宿主机 |
| `x86` | 老镜像，兼容性差，不推荐 |

需要 `adb root` / `adb remount` / `-writable-system` 做系统级调试时，
**必须选 `google_apis` 或 `default`，不能用 playstore 变体**。

示例：

```bash
sdkmanager "system-images;android-34;google_apis;x86_64"
```

## 接受许可

镜像装不下、或报 "license not accepted"，先跑：

```bash
sdkmanager --licenses
```

它会逐条询问，全选 `y`。非交互环境（脚本/CI）可以：

```bash
yes | sdkmanager --licenses
```

许可状态记录在 `$ANDROID_HOME/licenses/` 下。清空该目录会恢复未接受状态。
