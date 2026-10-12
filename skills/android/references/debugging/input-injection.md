# 注入手势

## 内容索引

- [tap 与 swipe](#tap-与-swipe)
- [原理：和真手指等价](#原理和真手指等价)
- [惯性会污染结果](#惯性会污染结果)
- [长按](#长按)
- [不要用 motionevent 拼手势](#不要用-motionevent-拼手势)
- [按键与文本](#按键与文本)
- [前置条件](#前置条件)

## tap 与 swipe

```bash
adb shell input tap 240 908                          # 点 (240,908)
adb shell input swipe 540 1700 540 600 3000          # 从 (540,1700) 拖到 (540,600)，历时 3000ms
```

`duration` 可省略，省略时几乎是瞬移（不会触发惯性，但也不像真实手势）。
坐标是屏幕物理像素，见 [coordinates](coordinates.md)。

## 原理：和真手指等价

系统先在起点注入一个 DOWN，然后按 `duration` 把 MOVE 事件**线性插值**铺到终点，最后发 UP。
这些事件走的是 Android 正常的输入分发管线，所以被注入的控件收到的
和真手指摸上去**没有任何区别**——Compose 里 `awaitFirstDown`、
`awaitVerticalTouchSlopOrCancellation`、`drag()` 拿到的东西完全一样。

**推论：不能用"注入的是假的"来解释失败。** 手势没生效，就是真的没生效，
该去查判据、坐标或前置条件（比如控件根本没挂载手势节点）。

## 惯性会污染结果

`input swipe` 在抬手那一刻仍然带着速度，超过系统阈值就会触发 fling
（惯性滚动），列表**会多滑一段不可预测的距离**。阈值来自
`ViewConfiguration.getMinimumFlingVelocity()`，默认 **50 dp/s**。

- **想让净位移可预测**：把速度压到阈值以下。速度 ≈ 位移 ÷ 时长。
  例：300px / 2500ms = 120px/s ≈ 44dp/s（density 440），不会甩出去。
- **反过来**，想触发滚动（比如只想让滚动条/悬浮按钮现身）就用**快速滑动**。

判断是否越界时，先自己算一遍 `位移 / 时长 / (density/160)`，再决定这个手势能不能用来做定量结论。

## 长按

`input` 没有独立的长按命令，用**起终点相同 + 足够长的 duration** 实现：

```bash
adb shell input swipe 540 1200 540 1200 800    # 在 (540,1200) 按住 800ms
```

## 不要用 motionevent 拼手势

```bash
input motionevent DOWN 540 1400
input motionevent MOVE 540 1200
input motionevent UP   540 1200
```

看着能拼出任意轨迹，**实际不可用**：每次 `input` 调用都是独立进程，
系统未必把它们识别成同一个手势流。典型症状是结果和预期**相反**
（向下拖，列表反而回退），而且不可复现，排查时极容易误判成应用 bug。

**结论：注入手势一律用单条 `input swipe`（或 `input tap`）。**

## 按键与文本

```bash
adb shell input keyevent 4              # KEYCODE_BACK
adb shell input keyevent KEYCODE_HOME
adb shell input keyevent --longpress 26 # 长按电源键
adb shell input text "abc"              # 只支持 ASCII
```

常用 keycode：

| 值 | 常量 | 含义 |
|----|------|------|
| 3 | HOME | 回桌面 |
| 4 | BACK | 返回 |
| 26 | POWER | 电源 |
| 66 | ENTER | 回车 |
| 82 | MENU | 菜单 |
| 187 | APP_SWITCH | 最近任务 |
| 224 | WAKEUP | 点亮屏幕 |

`input text` **输入不了中文**，只支持 ASCII；空格要写成 `%s`。
中文输入需要用 ADBKeyboard 之类的输入法，或用应用内的测试入口绕过。

## 前置条件

- **屏幕必须亮着且已解锁**，否则注入的事件会被锁屏吞掉。先 `keyevent 224`（WAKEUP）再 `keyevent 82`（MENU）通常是解锁手势机最快的方式。
- **`input` 命令本身有进程启动开销**（约 200~500ms）。两个手势连发时，间隔比 `duration` 显示的要长，涉及"1.5 秒内必须完成"这类时序假设时要把它算进去。
  需要严格连续时，把多条命令放在同一个 `adb shell "a; b"` 里执行。
