# 截屏与录屏

## 内容索引

- [截屏：必须用 exec-out](#截屏必须用-exec-out)
- [多屏设备](#多屏设备)
- [录屏](#录屏)
- [输出到管道](#输出到管道)

## 截屏：必须用 exec-out

```bash
adb -s <serial> exec-out screencap -p > shot.png
```

**不要用 `adb shell screencap -p > shot.png`。**
`shell` 会把输出交给伪终端，`\n` 被翻译成 `\r\n`，PNG 二进制会损坏——
文件能存下来，但打开报损坏，或者图像内容错位。`exec-out` 直传二进制、不经过转换。

如果确实要落盘到设备再取回，用设备侧的绝对路径 + `pull`：

```bash
adb shell screencap -p /sdcard/shot.png
adb pull /sdcard/shot.png
```

**每次截屏都是一帧静态画面。**需要观察动画过程时，连续截屏会有几百毫秒的空隙，
改用录屏。

## 多屏设备

```bash
adb shell screencap -p -d <displayId>   # 指定 display
adb shell dumpsys display | grep -i "displayDeviceInfo"   # 查看有哪些 display
```

折叠屏、外接屏会出现多个 display，默认截的是主屏。

## 录屏

```bash
adb shell screenrecord --time-limit 10 --size 720x1280 --bit-rate 4M /sdcard/x.mp4
adb pull /sdcard/x.mp4
```

| 参数 | 说明 |
|------|------|
| `--time-limit N` | 最长录制秒数，默认 180，上限也是 180 |
| `--size WxH` | 降低分辨率可显著减小体积 |
| `--bit-rate` | 默认 4Mbps，文字密集界面可调高 |
| `--rotate` | 旋转 90 度 |
| `--bugreport` | 叠加时间戳等信息，用于对帧 |

`screenrecord` 在设备上以后台进程运行，`Ctrl+C` 或超时后才会写入 moov atom——
**中途强杀进程会得到无法播放的文件**，务必等它自然结束或让超出 `--time-limit`。

## 输出到管道

```bash
# 直接取 H.264 裸流，交给本地 ffmpeg 处理，不占设备存储
adb exec-out screenrecord --output-format=h264 --time-limit 5 - > cap.h264
```

用 `ffmpeg -i cap.h264` 即可转码或抽帧。抽帧对"动画是否卡顿"的分析比逐张截图靠谱得多：

```bash
ffmpeg -i x.mp4 -vf fps=10 frame_%03d.png
```
