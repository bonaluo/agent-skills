# 定位控件

## 内容索引

- [dump 控件树](#dump-控件树)
- [解析 bounds](#解析-bounds)
- [Compose 语义树的限制](#compose-语义树的限制)
- [拿不到坐标时](#拿不到坐标时)

## dump 控件树

```bash
adb shell "uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; cat /sdcard/ui.xml"
```

`uiautomator dump` 会把当前窗口的**无障碍语义树**写到文件。
它输出的是语义节点，不是 View 层级——对 Compose、Flutter 这类自绘框架同样有效。

加 `--compressed` 可去掉冗余节点：

```bash
adb shell uiautomator dump --compressed /sdcard/ui.xml
```

节点属性里最有用的几个：

| 属性 | 用途 |
|------|------|
| `bounds` | 屏幕绝对坐标，形如 `[22,255][132,365]` |
| `text` | 文本内容 |
| `content-desc` | 无障碍描述（Compose 的 `contentDescription`） |
| `resource-id` | View 体系中是 `包名:id/xxx` |
| `clickable` / `long-clickable` | 是否可点/可长按 |
| `scrollable` | 是否是可滚动容器 |
| `selected` / `checked` | 状态 |

一次性过滤出"可点且有描述"的节点：

```bash
adb shell "uiautomator dump /sdcard/ui.xml >/dev/null 2>&1; cat /sdcard/ui.xml" \
  | tr '>' '\n' \
  | grep -o 'text="[^"]*" resource-id="[^"]*"[^/]*bounds="[^"]*"'
```

## 解析 bounds

```
bounds="[22,255][132,365]"
```

左上角 `(22,255)`，右下角 `(132,365)`。点击中心点：

```
x = (22 + 132) / 2 = 77
y = (255 + 365) / 2 = 310
```

注意 bounds 常常**比视觉元素大**——Compose 的 `IconButton` 会强制 48dp 的最小触摸区，
图标本身可能只有 24dp。这反而有利：按中心点注入总能命中。

## Compose 语义树的限制

Compose 默认**合并语义**，一个可点击的行会把内部所有文本合并到父节点，
因此：

- 大量节点 `text=""`、`resource-id=""`，只有 `content-desc` 有值
  （对应代码里显式写的 `contentDescription`）。
- 没写 `contentDescription` 的图标按钮在 dump 里基本定位不到。
- 同一个可点击区域内的文字会合并成一长串，不能用 `text` 精确匹配单个标签。

**应对**：

1. 优先按 `content-desc` 找——代码里给交互元素写 `contentDescription` 的收益是双份的。
2. 找不到就退回**截图 + 目视估坐标**，点一次再截图验证。
3. 需要真正看清布局时用 Android Studio 的 **Layout Inspector**（可附着到运行中的进程），
   它能显示 Compose 的组合层级，比 dump 详细得多。命令行下没有等价物。

## 拿不到坐标时

按代价从低到高：

1. `uiautomator dump` 找 `content-desc` / `text`。
2. 从截图目视估算，按 [coordinates](coordinates.md) 换算。
3. **用已知确定的元素做参照**：先点一个能确认的按钮，观察画面变化，
   借机标定一个参考点，再推其他坐标。
4. 给应用加临时的调试入口 / 日志，用日志确认走到了哪一步，
   而不是继续猜坐标。
