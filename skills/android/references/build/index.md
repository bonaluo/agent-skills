# 构建与安装 — 子索引

| 文档 | 内容 |
|------|------|
| [build-and-install](build-and-install.md) | gradlew 构建、adb 安装、多设备、冷启动验证、启动耗时、构建失败排查 |

## 常用速查

```bash
./gradlew assembleDebug                          # 构建 debug APK
adb install -r app/build/outputs/apk/debug/app-debug.apk

adb shell am force-stop <包名>                   # 冷启动前置
adb shell monkey -p <包名> -c android.intent.category.LAUNCHER 1
```

本分类后续会继续扩充：签名配置、多渠道/flavor、AAB、CI 构建等内容按需新增文档。
