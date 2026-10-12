# adb 连接

## 内容索引

- [前提](#前提)
- [列出与选择设备](#列出与选择设备)
- [状态排查](#状态排查)
- [无线调试](#无线调试)
- [Windows / Git Bash 路径坑](#windows--git-bash-路径坑)
- [服务端重启](#服务端重启)

## 前提

- 设备需开启**开发者选项 → USB 调试**，并在首次连接时在设备上确认授权弹窗。
- `platform-tools` 需在 PATH 中；claude 侧无需额外配置。

## 列出与选择设备

```bash
adb devices          # 序列号 + 状态
adb devices -l       # 额外显示 model / product / device
```

多设备时**每条命令都带 `-s`**，避免误操作到别的设备：

```bash
adb -s <serial> shell ...
```

也支持按连接类型选择：

| 参数 | 含义 |
|------|------|
| `-d` | 唯一一台 USB 设备 |
| `-e` | 唯一一台模拟器 |
| `-s <serial>` | 指定序列号（模拟器通常是 `emulator-5554`） |

只在有把握只有一台设备时才省略 `-s`。脚本里更应显式取设备：

```bash
DEVICE="$(adb devices | awk 'NR>1 && $2=="device" {print $1; exit}')"
```

## 状态排查

| 状态 | 含义 | 处理 |
|------|------|------|
| `device` | 正常 | — |
| `unauthorized` | 设备上未授权本机 | 在设备上确认弹窗；不行就撤销 USB 调试授权后重连 |
| `offline` | 掉线 | `adb kill-server` 后重连，或换 USB 口/线 |
| 不出现 | 完全认不到 | 换数据线（很多线只供电）；装厂商 USB 驱动；确认 USB 模式不是"仅充电" |

## 无线调试

**Android 11+（配对方式）**：在「无线调试」页面拿到配对码和配对端口。

```bash
adb pair <ip>:<pairPort> <pairingCode>
adb connect <ip>:<debugPort>
```

**Android 10 及以下**：先用 USB 连一次。

```bash
adb tcpip 5555
adb connect <ip>:5555
```

## Windows / Git Bash 路径坑

MSYS 会把看起来像路径的参数改写成 Windows 路径，`/tmp/x.png`、`/sdcard/ui.xml`
这类设备侧路径会被改坏。**在命令开头关掉路径转换**：

```bash
export MSYS_NO_PATHCONV=1
```

PowerShell / CMD 无此问题。

## 服务端重启

连接异常时优先重启服务端，而不是反复插拔：

```bash
adb kill-server
adb start-server
adb devices
```
