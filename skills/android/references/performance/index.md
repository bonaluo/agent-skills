# 性能 — 子索引

| 文档 | 内容 |
|------|------|
| [frame-stats](frame-stats.md) | `dumpsys gfxinfo` 采集与判读，判断瓶颈在主线程、图片上传还是绘制 |

## 采集三步

```bash
adb shell dumpsys gfxinfo <包名> reset     # 1. 清零
# 2. 在设备上执行固定的操作序列（例如滚动 10 秒）
adb shell dumpsys gfxinfo <包名>           # 3. 读数
```

**不要跳过 `reset`**，也不要在模拟器上取性能数据（见
[vs-real-device](../emulator/vs-real-device.md)）。

## 关键原则

- **操作序列必须固定**，两次采集要跑同一套动作，否则数据不可比。
- **单次数据无意义**，要的是改动前后的对比。
- **先定位瓶颈在哪一层，再谈优化**。盲目改代码只会引入噪声。

本分类后续会继续扩充：内存占用、启动耗时分解、Perfetto 系统 trace、
包体积分析等内容按需新增文档。
