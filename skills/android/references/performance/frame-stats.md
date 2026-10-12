# 帧统计

用 `dumpsys gfxinfo` 采集渲染帧数据，判断卡顿出在哪一层。

## 内容索引

- [采集](#采集)
- [关键字段](#关键字段)
- [判读](#判读)
- [只看关心的行](#只看关心的行)
- [逐帧数据](#逐帧数据)
- [注意事项](#注意事项)

## 采集

```bash
# 1. 清零
adb shell dumpsys gfxinfo <包名> reset

# 2. 在设备上执行固定的操作序列（例如快速滚动 10 秒）

# 3. 读数
adb shell dumpsys gfxinfo <包名>
```

`reset` 不清的话，读到的是**进程自启动以来**的累计值，
会把启动、首页加载等无关阶段的帧混进来。

## 关键字段

```
Total frames rendered: 470
Janky frames: 71 (15.11%)
50th percentile: 14ms
90th percentile: 32ms
95th percentile: 40ms
99th percentile: 80ms
Number Missed Vsync: 20
Number High input latency: 0
Number Slow UI thread: 63
Number Slow bitmap uploads: 4
Number Slow issue draw commands: 12
Number Frame deadline missed: 55
GPU 50th percentile: 3ms
```

| 字段 | 含义 |
|------|------|
| `Total frames rendered` | 采集窗口内的总帧数，**样本量太少（<100）不要下结论** |
| `Janky frames` | 超过该设备帧预算的帧数与占比 |
| `Nth percentile` | 帧耗时分布。中位数是否超过帧预算，决定"持续掉帧"还是"偶发卡顿" |
| `Number Missed Vsync` | 错过垂直同步的次数 |
| `Number Slow UI thread` | 主线程计算超时的帧数 |
| `Number Slow bitmap uploads` | 位图上传（解码/纹理上传）超时的帧数 |
| `Number Slow issue draw commands` | 绘制指令下发超时的帧数 |
| `GPU percentile` | GPU 侧耗时；很低说明瓶颈不在渲染 |

## 判读

**看 `Slow *` 三兄弟的相对占比**，谁最接近 `Janky frames` 总数，瓶颈就在谁身上：

| 现象 | 瓶颈位置 | 优化方向 |
|------|----------|----------|
| `Slow UI thread` 接近 Janky 总数 | **主线程计算** | 减少组合/布局工作量、避免在组合阶段读会触发重组的 state、拆分重组范围 |
| `Slow bitmap uploads` 偏高 | **图片解码 / 纹理上传** | 缩小解码尺寸、改用磁盘缓存的小图、避免每次滚动重新解码原图 |
| `Slow issue draw commands` 偏高 | **绘制指令过多** | 减少层级与过度绘制、去掉不必要的阴影/裁剪/离屏层 |
| `GPU percentile` 偏高 | **GPU 绘制** | 减少过度绘制、简化效果；软件渲染或弱 GPU 设备上尤其明显 |
| 三者都很低，但 Janky 很高 | 主线程在做**与渲染无关**的事 | 查主线程上的 IO、锁等待、频繁 GC |

**中位数 vs 90th percentile**：

- 中位数就超过帧预算 → 持续掉帧，是结构性问题；
- 中位数正常、90th 很高 → 偶发卡顿，通常是某个操作（图片解码、数据库查询）引起。

## 只看关心的行

完整输出很长，过滤一下：

```bash
adb shell dumpsys gfxinfo <包名> | grep -E \
  "Total frames rendered|Janky frames|^ *[0-9]+th percentile|Number Missed Vsync|Number Slow UI thread|Number Slow bitmap uploads|Number Slow issue draw commands|GPU.*percentile"
```

## 逐帧数据

需要精确到每一帧时（哪些帧卡、卡多少纳秒）：

```bash
adb shell dumpsys gfxinfo <包名> framestats
```

输出是一张 CSV 表，每行一帧，列含 `INTENDED_VSYNC` / `VSYNC` /
`FRAME_COMPLETED` / `HANDLE_INPUT_START` 等纳秒时间戳。
把 `FRAME_COMPLETED - INTENDED_VSYNC` 算出来就是这一帧的总耗时，
可以直接定位到"第几帧开始卡的"。

## 注意事项

- **必须在真机上采集**。模拟器的 GPU 是软件渲染或宿主模拟，数值没有参考价值。
- **刷新率影响判定标准**。120Hz 设备的帧预算只有 8.3ms，同样的代码在 60Hz 上不卡、
  在 120Hz 上会被判为 janky。
- **固定操作序列**。两次采集之间只改代码，不改动作，否则数据不可比。
- **样本量要够**。总帧数低于一百时百分比波动极大，先跑久一点。
- **`reset` 之后要等采集窗口结束再读**，中途读会把未完成的窗口算进去。

更进一步的工具：Android Studio 的 Profiler（CPU / Memory / GPU）、
Perfetto（系统级 trace，能看跨进程与渲染管线）、
开发者选项里的"GPU 呈现模式分析"（屏幕上直接画柱状图，看实时手感最直观）。
