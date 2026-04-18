---
name: scriptcat-skill
description: 这是一个关于ScriptCat浏览器脚本开发的skill，专门用于处理浏览器扩展脚本开发中的常见问题，如跨域请求、GM函数使用等。
metadata:
  version: 20260417.0000
  update-url: https://github.com/bonaluo/agent-skills@scriptcat-skill
---

# scriptcat-skill

这是一个关于ScriptCat浏览器脚本开发的skill，专门用于处理浏览器扩展脚本开发中的常见问题，如跨域请求、GM函数使用等。

## When to use

当你需要开发浏览器用户脚本（UserScript）并遇到以下情况时，可以使用此技能：
- 需要绕过跨域限制进行HTTP请求
- 需要使用ScriptCat或Tampermonkey提供的GM函数
- 需要操作DOM元素或注入脚本到网页中
- 需要存储用户数据或设置选项
- 需要监听页面事件或内容变化

## Instructions

### 处理跨域请求问题

当脚本需要向不同域名的服务器发起请求时，会遇到跨域限制(CORS)。在这种情况下，应使用ScriptCat提供的GM_xmlhttpRequest函数替代标准的XMLHttpRequest或fetch：

```javascript
// 错误方式：直接使用fetch可能遇到跨域限制
// fetch('https://api.example.com/data')

// 正确方式：使用GM_xmlhttpRequest绕过跨域限制
GM_xmlhttpRequest({
  method: "GET",
  url: "https://api.example.com/data",
  headers: {
    "Content-Type": "application/json",
  },
  onload: function(response) {
    // 请求成功时的回调
    const data = JSON.parse(response.responseText);
    console.log(data);
  },
  onerror: function(error) {
    // 请求失败时的回调
    console.error("Request failed:", error);
  }
});
```

### GM_xmlhttpRequest详细用法

GM_xmlhttpRequest是ScriptCat/Tampermonkey提供的增强版XMLHttpRequest，支持跨域请求：

```javascript
GM_xmlhttpRequest({
  method: "POST",           // HTTP方法: GET, POST, PUT, DELETE等
  url: "https://api.example.com/endpoint",
  headers: {                // 可选：请求头
    "Content-Type": "application/json",
    "Authorization": "Bearer token"
  },
  data: JSON.stringify({    // 可选：POST/PUT请求的数据
    key: "value"
  }),
  timeout: 10000,          // 可选：超时时间(毫秒)
  onload: function(response) {
    // 成功响应的回调
    if (response.status === 200) {
      const result = JSON.parse(response.responseText);
      // 处理返回的数据
    }
  },
  onerror: function(error) {
    // 网络错误或其他异常的回调
    console.error("Network error:", error);
  },
  ontimeout: function() {
    // 请求超时的回调
    console.warn("Request timed out");
  }
});
```

### 其他常用的GM函数

- **GM_setValue/GM_getValue**: 存储和读取用户数据
- **GM_addStyle**: 为页面添加CSS样式
- **GM_registerMenuCommand**: 注册菜单命令
- **GM_notification**: 显示桌面通知

```javascript
// 存储数据
GM_setValue("username", "john_doe");

// 读取数据
const username = GM_getValue("username", "default_user");

// 添加自定义样式
GM_addStyle(`
  .custom-highlight {
    background-color: yellow;
  }
`);

// 注册右键菜单项
GM_registerMenuCommand("我的脚本功能", function() {
  alert("脚本功能被触发！");
});

// 显示通知
GM_notification("任务已完成！", "提示");
```

### 脚本头部元数据

编写ScriptCat脚本时，需要在脚本开头包含适当的元数据：

```javascript
// ==UserScript==
// @name         我的ScriptCat脚本
// @namespace    http://tampermonkey.net/
// @version      1.0.0
// @description  脚本描述
// @author       你的名字
// @match        https://www.example.com/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_addStyle
// @grant        GM_registerMenuCommand
// @grant        GM_notification
// @grant        unsafeWindow
// ==/UserScript==
```

注意：
- @match指定脚本运行的页面URL规则
- @grant声明所需的权限，必须明确声明每个GM函数的权限

### DOM操作最佳实践

由于脚本在页面加载完成后执行，建议使用以下方式确保DOM已准备就绪：

```javascript
function main() {
  // 主要逻辑
  console.log("脚本开始执行");
}

// 确保DOM完全加载后执行
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
```

### 页面内容变化监听

对于单页应用(SPA)或动态加载的内容，使用MutationObserver监听DOM变化：

```javascript
const observer = new MutationObserver(function(mutations) {
  mutations.forEach(function(mutation) {
    // 处理DOM变化
    if (mutation.type === 'childList') {
      // 检查新增的节点
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // 对新节点执行脚本逻辑
        }
      });
    }
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});
```

## 注意事项

- 始终在脚本头部声明@grant权限，未声明的GM函数无法使用
- GM_xmlhttpRequest是解决跨域问题的主要手段，但仅限于HTTP请求
- 避免直接操作unsafeWindow，除非确实需要与页面JS交互
- 脚本应考虑性能，避免不必要的重复操作
- 尊重网站的robots.txt和服务条款，不要滥用自动化功能