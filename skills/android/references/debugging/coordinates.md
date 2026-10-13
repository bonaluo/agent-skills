# 坐标基准

## 内容索引

- [先问设备规格](#先问设备规格)
- [dp 与像素换算](#dp-与像素换算)
- [input 用的是物理像素](#input-用的是物理像素)
- [override 尺寸](#override-尺寸)
- [状态栏与导航栏](#状态栏与导航栏)

## 先问设备规格

```bash
adb shell wm size        # 例如 Physical size: 1080x2400
adb shell wm density     # 例如 Physical density: 440
```

**这两个值是一切坐标的基准，先拿到再动手。**

## dp 与像素换算

```
1dp = density / 160 px
```

| density | 1dp 等于 |
|---------|----------|
| 160 | 1.0 px |
| 240 | 1.5 px |
| 320 | 2.0 px |
| 420 | 2.625 px |
| 440 | 2.75 px |
| 480 | 3.0 px |

设计稿上的 dp 值、代码里的 `.dp` 字面量都要过这道换算，否则按 1:1 取坐标会整体偏出去。
反查时用除法：`px / (density / 160)`。

## input 用的是物理像素

```bash
adb shell input tap <x> <y>
```

`x` / `y` 是**屏幕绝对像素坐标**，原点在左上角，与 dp、与控件层级都无关。
不写 `-s` 时 `input` 生效在最上层可获得焦点的窗口——如果弹了对话框，
坐标要按对话框重新算。

## override 尺寸

如果 `wm size` 输出里多了一行 `Override size`，说明分辨率被改过，实际生效的是 override 值：

```bash
adb shell wm size                             # 查看
adb shell wm size reset                       # 还原
adb shell wm size 1080x2400                   # 临时改成指定值
adb shell wm density 440                      # 同理，改密度
adb shell wm density reset
```

改过之后**所有坐标都要按新尺寸重新算**，包括截图本身的像素尺寸。

## 状态栏与导航栏

`input` 的坐标系包含状态栏和导航栏区域。截图里量出来的 y 值可以直接用，
不需要减去状态栏高度——除非你量的是某个 Android View 内部的相对坐标，
那需要先加上它在屏幕上的偏移。

顶部状态栏高度、底部导航栏/手势条高度可以用：

```bash
adb shell dumpsys window | grep -i "stableInsets\|cutout"
```

更省事的办法：直接从截图上看——状态栏和内容区之间通常有明显分界。
