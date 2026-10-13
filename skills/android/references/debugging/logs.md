# 日志

## 内容索引

- [最常用的几条](#最常用的几条)
- [按进程与 tag 过滤](#按进程与-tag-过滤)
- [识别厂商噪声](#识别厂商噪声)
- [崩溃缓冲区](#崩溃缓冲区)

## 最常用的几条

```bash
adb logcat -c                          # 清空，便于只看新日志（排查前先执行）
adb logcat -d                          # dump 当前缓冲区后退出
adb logcat -d -b crash                 # 崩溃缓冲区
adb logcat -d *:E                      # 只看 Error 及以上
adb logcat -d -v time                  # 带时间戳
adb logcat -d -v threadtime            # 带时间戳 + pid/tid
```

`-d` 是"打印完就退出"，不加会一直跟随输出。自动化场景一律加 `-d`。

**排查前先 `logcat -c`**，否则会捞到上一次运行留下的无关日志，
把归因带偏。

## 按进程与 tag 过滤

```bash
PID="$(adb shell pidof <包名> | tr -d '\r')"
adb logcat -d --pid="${PID}"

adb logcat -d -s TagName:V             # 只保留指定 tag
adb logcat -d "ActivityManager:I" "*:S"  # 白名单：只放行指定 tag，其余静音
```

`*:S`（Silent）是白名单写法的关键：先把全部静音，再单独放行需要的 tag。

按 **tag 和 pid** 过滤是最有效的手段，比按级别过滤有用得多——
厂商 rom 会把大量正常信息打成 `E` 级。

## 识别厂商噪声

这些看着像报错，其实与应用无关，**不要据此判定崩溃**：

| 典型 tag | 实际是什么 |
|----------|-----------|
| `perf-hal-service` / `ExtendedPerfBoost` | 厂商性能调度，正常输出 |
| `HyperSentinel` | 厂商内存/进程守护，RSS 变化的常规记录 |
| `dex2oat64` abort | 系统在编译应用（AOT），不是你的应用崩了 |
| `chatty` | logcat 自己说"日志被限流丢掉了"，只是提示 |

判断方法：看 `pid` 是不是应用的进程。不是自己进程的 `E` 日志一律先忽略。

## 崩溃缓冲区

```bash
adb logcat -d -b crash
```

`crash` 缓冲区里是崩溃、ANR 和 native tombstone。
Java 异常的堆栈会以 `FATAL EXCEPTION: main` 开头，
native 崩溃是 `F/DEBUG` 开头的寄存器转储。

排查应用是否崩溃，**先看这个缓冲区**，而不是在 `main` 缓冲区里翻 `E`。
