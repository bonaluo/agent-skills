# AVD 管理

## 内容索引

- [列出](#列出)
- [查看设备型号模板](#查看设备型号模板)
- [创建](#创建)
- [删除](#删除)
- [AVD 存放位置与配置](#avd-存放位置与配置)

## 列出

```bash
emulator -list-avds          # 只列名字，脚本里好用
avdmanager list avd          # 详细信息：路径、镜像、分辨率
```

`emulator -list-avds` 需要 `$ANDROID_HOME/emulator` 在 PATH 中；
只装了 `cmdline-tools` 时用 `avdmanager list avd`。

## 查看设备型号模板

```bash
avdmanager list device
```

输出形如：

```
id: 17 or "pixel_6"
    Name: Pixel 6
    OEM : Google
    ...
```

`-d` 参数接受 **id 数字**或 **带引号的 id 字符串**。不指定就退化成默认机型，
往往分辨率很奇怪，建议显式指定。

## 创建

```bash
avdmanager create avd \
  -n test34 \
  -k "system-images;android-34;google_apis;x86_64" \
  -d pixel_6
```

| 参数 | 说明 |
|------|------|
| `-n` | AVD 名称，之后 `-avd` 用这个名字 |
| `-k` | 系统镜像包名，**必须和 `sdkmanager` 装过的完全一致** |
| `-d` | 设备型号模板 |
| `-c` | SD 卡大小，如 `-c 2048M` |
| `-f` | 同名时强制覆盖 |

创建过程中会问"是否自定义硬件配置"，交互式脚本里可以 `echo no |` 预设：

```bash
echo no | avdmanager create avd -n test34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6
```

**最常见的失败**是 `-k` 指向了一个没装过的镜像，报错形如
`Package 'system-images;...' is not a valid package`。
先 `sdkmanager --list_installed | grep system-images` 确认包名。

## 删除

```bash
avdmanager delete avd -n test34
```

## AVD 存放位置与配置

| 平台 | 位置 |
|------|------|
| Windows | `%USERPROFILE%\.android\avd\<name>.avd\` |
| macOS / Linux | `~/.android/avd/<name>.avd/` |

目录里有 `config.ini`（硬件配置）和 `*.img` / `snapshots/`（磁盘与快照）。

`config.ini` 里常改的几项：

| 键 | 作用 |
|----|------|
| `hw.ramSize` | 内存 MB，默认偏小，2~4GB 更流畅 |
| `vm.heapSize` | JVM 堆上限 |
| `disk.dataPartition.size` | 数据分区，装大应用时调大 |
| `hw.lcd.density` / `hw.lcd.width` / `hw.lcd.height` | 分辨率与密度，**改完要重启才生效** |
| `hw.keyboard` | 设为 `yes` 才能用宿主键盘输入 |

环境变量 `ANDROID_AVD_HOME` 可以整体挪走 AVD 目录（放到 SSD 或大容量盘）。
