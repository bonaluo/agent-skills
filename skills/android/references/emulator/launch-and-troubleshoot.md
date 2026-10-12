# 启动与排障

## 内容索引

- [启动](#启动)
- [常用参数](#常用参数)
- [等待开机完成](#等待开机完成)
- [系统级写入](#系统级写入)
- [常见失败](#常见失败)

## 启动

```bash
emulator -avd test34 &
```

AVD 与 adb 的对应关系是固定的端口约定：

| AVD 实例 | 控制台端口 | adb 端口 | adb 序列号 |
|----------|-----------|----------|-----------|
| 第 1 台 | 5554 | 5555 | `emulator-5554` |
| 第 2 台 | 5556 | 5557 | `emulator-5556` |

多台同时跑时，用 `adb -s emulator-5554 ...` 区分。

## 常用参数

**无界面运行**（CI / 只能看截图时）：

```bash
emulator -avd test34 -no-window -no-audio -no-boot-anim
```

| 参数 | 作用 |
|------|------|
| `-no-window` | 不显示窗口，但仍可 `screencap` 截屏 |
| `-no-audio` | 关音频，避免宿主音频设备冲突 |
| `-no-boot-anim` | 跳过开机动画，启动更快 |
| `-gpu swiftshader_indirect` | 纯软件渲染，最稳，适合无显卡/远程环境 |
| `-gpu host` | 用宿主 GPU，最快，但驱动不兼容时会黑屏 |
| `-no-snapshot-load` | 本次冷启动，不加载快照 |
| `-no-snapshot-save` | 退出时不保存快照（**调试系统改动时用它，避免污染下次启动**） |
| `-wipe-data` | 恢复出厂状态，等价删除用户数据 |
| `-writable-system` | 允许 `adb remount` 写入 system 分区 |
| `-memory 4096` | 内存 MB |
| `-port 5556` | 指定端口（多实例时） |
| `-read-only` | 以只读方式启动多份同一 AVD |

**GPU 模式选择**：远程桌面/无独显环境优先 `swiftshader_indirect`；
出现黑屏、花屏、渲染异常时第一步就是换成它重试。

## 等待开机完成

`adb wait-for-device` **只等到 adb 可见，不代表系统启动完成**，
此时装包或点击都会失败。必须再等 `sys.boot_completed`：

```bash
adb wait-for-device
until [ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ]; do
  sleep 2
done
```

`tr -d '\r'` 不可省——Windows 上 `adb shell` 的输出带 `\r`，
字符串比较会永远不相等，脚本看起来像卡死。

更严格还可以等 `init.svc.bootanim` 变成 `stopped`。

## 系统级写入

要改系统分区（推 so、改 hosts、装系统证书）：

```bash
emulator -avd test34 -writable-system -no-snapshot-save &
adb root
adb remount
adb push libfoo.so /system/lib64/
```

必须用 `default` 或 `google_apis` 镜像；**`google_apis_playstore` 镜像不允许 root**。

`-no-snapshot-save` 很重要：否则改动会被写进快照，
下次启动时系统分区状态和你以为的不一样。

## 常见失败

| 现象 | 原因 | 处理 |
|------|------|------|
| `Cannot find AVD system path` / 启动即退 | system-image 缺失 | `sdkmanager --list_installed` 核对；缺了就装 |
| 启动卡在黑屏或无限开机动画 | GPU 模式不兼容 | 换 `-gpu swiftshader_indirect` 重试 |
| `emulator: ERROR: x86 emulation currently requires hardware acceleration` | 未开虚拟化 | BIOS 打开 VT-x/AMD-V；Windows 关闭 Hyper-V 冲突；Linux 装 KVM |
| 端口被占用 | 上次实例没退干净 | `adb -s emulator-5554 emu kill`，或删 `~/.android/avd/<name>.avd/*.lock` |
| `adb devices` 只有 `offline` | 模拟器还没起完 | 等 boot_completed，不要提前操作 |
| 磁盘空间不足 | `disk.dataPartition.size` 太小 | 改 `config.ini` 后 `-wipe-data` 重建 |
| 启动极慢 | 每次都冷启动 | 启用快照（不加 `-no-snapshot-load`），或用 `-no-boot-anim` |

需要彻底重置时：`avdmanager delete avd -n test34` 后重建，比手工清文件可靠。
