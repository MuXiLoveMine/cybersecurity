# 第4章 BeEF核心功能模块

BeEF的功能以模块（Module）的形式组织，每个模块实现特定的功能。截至最新版本，BeEF内置了超过200个模块，按功能分为多个大类。

### 4.1 模块体系概述

#### 模块分类

在BeEF管理界面的右栏"Module Tree"中，模块按树状结构分类组织：

```
Module Tree
├── Browser（浏览器相关）
│   ├── Fingerprint（指纹识别）
│   ├── Hooked Domain（Hook所在域操作）
│   ├── Debug（调试）
│   └── ...
├── Network（网络侦察）
│   ├── Host（主机发现）
│   ├── Port Scan（端口扫描）
│   ├── DNS（DNS探测）
│   └── ...
├── Social Engineering（社会工程）
│   ├── Pretty Theft
│   ├── Clippy
│   ├── Fake Notification Bar
│   └── ...
├── Persistence（持久化）
│   ├── Confirm Close Tab
│   ├── Create Foreground Iframe
│   └── ...
├── Metasploit
├── IPEC（浏览器内命令执行）
├── Mobile（移动设备）
└── WebRTC
```

#### 模块执行状态

每个模块执行后会返回不同的状态结果：

| 状态 | 颜色 | 含义 |
|------|------|------|
| 0 - 未定义 | 灰色 | 模块执行结果未定义 |
| 1 - 成功 | 绿色 | 模块执行成功，达到预期效果 |
| 2 - 执行但不确定 | 橙色 | 模块已执行，但无法确认是否成功 |
| 3 - 执行失败 | 红色 | 模块执行失败 |
| 4 - 不适用 | 蓝色 | 该模块不适用于当前浏览器环境 |

> **截图位置说明**：在BeEF管理界面的"Commands"标签页中，每条已执行的命令前面都有一个颜色标识的状态图标。绿色对勾表示成功，红色叉号表示失败，橙色感叹号表示不确定。

### 4.2 浏览器信息收集

信息收集是渗透测试的第一步，BeEF提供了丰富的浏览器指纹和系统信息收集模块。

#### 4.2.1 浏览器指纹

浏览器指纹是通过收集浏览器的各种特征信息来唯一标识用户的技术。BeEF的指纹信息非常详细。

**User-Agent信息：**
- 浏览器名称和版本（Chrome、Firefox、Safari、Edge、IE等）
- 浏览器渲染引擎（Blink、Gecko、WebKit、Trident）
- 操作系统信息

**插件检测：**
BeEF可以检测浏览器安装的所有插件，包括：
- Adobe Flash Player
- Java Plugin
- Adobe Reader
- Silverlight
- QuickTime
- Windows Media Player
- 各种自定义插件

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Browser" -> "Fingerprint" -> "Browser Fingerprint"
3. 点击"Execute"执行
4. 在"Commands"或"Details"标签页查看结果

> **截图位置说明**：在浏览器详情的"Details"标签页中，可以看到完整的浏览器指纹信息，包括Browser Name、Browser Version、Browser Language、Platform、User-Agent等字段。

**Canvas指纹：**
Canvas指纹利用不同浏览器和系统对Canvas绘图的细微差异来生成唯一标识。

```javascript
// Canvas指纹原理示例
var canvas = document.createElement('canvas');
var ctx = canvas.getContext('2d');
ctx.textBaseline = 'top';
ctx.font = '14px Arial';
ctx.fillText('canvas_fingerprint', 2, 2);
var fingerprint = canvas.toDataURL();
```

**字体检测：**
BeEF可以检测系统中安装的字体列表，这也是重要的指纹特征。

**WebGL指纹：**
通过WebGL API获取显卡信息和渲染特征。

#### 4.2.2 系统信息

BeEF可以收集到的系统信息包括：

| 信息类型 | 具体内容 | 获取方式 |
|---------|---------|---------|
| 操作系统 | Windows/macOS/Linux/Android/iOS | User-Agent、平台检测 |
| 操作系统版本 | Windows 10/11、macOS版本等 | User-Agent解析 |
| 系统架构 | x86/x64/ARM | 平台检测 |
| CPU核心数 | 处理器核心数量 | navigator.hardwareConcurrency |
| 内存大小 | 设备内存 | navigator.deviceMemory |
| 屏幕分辨率 | 屏幕宽高 | screen.width/height |
| 颜色深度 | 屏幕色深 | screen.colorDepth |
| 时区 | 系统时区 | Intl.DateTimeFormat |
| 语言 | 系统语言 | navigator.language |
| 在线状态 | 是否联网 | navigator.onLine |
| 电池状态 | 电量、充电状态 | Battery API |
| 触摸支持 | 是否支持触摸 | Touch事件检测 |

**获取系统信息的模块：**
- Browser Fingerprint：综合浏览器和系统信息
- Get Screen Dimensions：屏幕尺寸
- Get Timezone Offset：时区偏移
- Battery Status：电池状态（移动设备常用）

#### 4.2.3 网络信息

**公网IP地址：**
BeEF可以通过第三方API或自身服务器获取目标的公网IP地址。

> **截图位置说明**：在"Details"标签页的"Network"部分，可以看到Public IP地址和大致的地理位置信息（基于IP数据库）。

**内网IP探测：**
这是BeEF的一项强大功能，利用WebRTC或其他手段探测目标的内网IP地址。

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Network" -> "Host" -> "Get Internal IP"（WebRTC方式）
3. 点击"Execute"执行

**原理说明：**
WebRTC在建立P2P连接时，会向STUN服务器发送请求，请求中包含本地IP地址。通过捕获这些请求，可以获取用户的内网IP。

```javascript
// WebRTC获取内网IP原理
var pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
pc.createDataChannel('');
pc.createOffer().then(pc.setLocalDescription.bind(pc));
pc.onicecandidate = function(e) {
    if (e.candidate) {
        var ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3})/;
        var match = e.candidate.candidate.match(ipRegex);
        if (match) console.log('内网IP:', match[1]);
    }
};
```

**端口扫描：**
BeEF可以利用被Hook的浏览器作为跳板，对内网或特定目标进行端口扫描。

**操作步骤：**
1. 选中目标浏览器
2. 展开 "Network" -> "Port Scanner"
3. 配置参数：
   - **ip**：目标IP地址（如 `192.168.1.1`）
   - **ports**：端口范围（如 `1-1000`）
   - **timeout**：超时时间
4. 点击"Execute"执行

> **截图位置说明**：在"Module Tree" -> "Network" -> "Port Scanner"模块的参数配置区，可以看到ip、ports、timeout等输入框。执行后结果会显示每个端口的状态（开放/关闭/过滤）。

**扫描原理：**
通过创建Image对象，根据图片加载的时间和成功/失败状态来判断端口是否开放。由于同源策略限制，无法读取响应内容，但可以通过加载时间推断端口状态。

#### 4.2.4 历史记录与Cookie获取

**Cookie获取：**
对于Hook所在域的Cookie，BeEF可以直接通过 `document.cookie` 获取。

> **截图位置说明**：在"Details"标签页的"Cookies"部分，列出了当前页面域下的所有Cookie键值对。

**获取Cookie模块：**
1. 展开 "Browser" -> "Hooked Domain" -> "Get Cookie"
2. 输入Cookie名称，或留空获取所有
3. 点击"Execute"

**历史记录探测：**
BeEF可以通过CSS历史记录嗅探技术（已被现代浏览器修复）或其他方式探测用户的浏览历史。

**LocalStorage/SessionStorage获取：**
对于Hook所在域，可以直接读取LocalStorage和SessionStorage的内容。

### 4.3 社会工程模块

社会工程模块是BeEF最具特色也最强大的功能之一，利用人的心理弱点而非技术漏洞来达到攻击目的。

#### 4.3.1 弹窗欺骗

弹窗欺骗通过伪造各种系统或应用程序弹窗，诱导用户进行特定操作。

**Fake Notification Bar（假通知栏）：**
模拟浏览器的通知栏，提示用户需要安装插件或更新软件。

**操作步骤：**
1. 展开 "Social Engineering" -> "Fake Notification Bar"
2. 选择通知类型：
   - **WebRTC**：假的WebRTC权限请求
   - **Java**：假的Java插件更新
   - **Flash**：假的Flash Player更新
   - **Custom**：自定义通知内容
3. 配置通知文本和下载链接
4. 点击"Execute"

> **截图位置说明**：目标浏览器顶部会出现一个仿真的通知栏，外观与浏览器的真实通知栏非常相似。用户点击后会跳转到预设的恶意链接。

**Clippy（助手动画）：**
模拟经典的Office助手（大眼夹），用可爱的动画形象吸引用户注意并诱导操作。

**操作步骤：**
1. 展开 "Social Engineering" -> "Clippy"
2. 配置参数：
   - **message**：显示的消息内容
   - **executable**：用户点击后的下载链接
   - **clippy_id**：助手形象（Clippy/Dot/F1/Genie/Links/Merlin/Rover）
3. 点击"Execute"

**Pretty Theft（精美钓鱼弹窗）：**
一个制作精美的登录弹窗，仿冒各种知名网站的登录界面。

**操作步骤：**
1. 展开 "Social Engineering" -> "Pretty Theft"
2. 选择钓鱼类型：
   - Facebook
   - LinkedIn
   - YouTube
   - Windows
   - 自定义
3. 配置回调URL（用于接收凭证）
4. 点击"Execute"

> **截图位置说明**：目标浏览器页面中央会弹出一个半透明遮罩的登录对话框，外观与对应网站的登录界面高度相似。用户输入用户名和密码后，凭证会被发送到BeEF服务器。

#### 4.3.2 页面注入与替换

**Replace Content（内容替换）：**
替换页面中的指定内容，可用于修改页面信息、插入恶意链接等。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Replace Content"
2. 配置参数：
   - **old_text**：要替换的旧文本
   - **new_text**：替换后的新文本
3. 点击"Execute"

**Redirect Browser（页面重定向）：**
将当前页面重定向到指定URL。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Redirect Browser"
2. 输入目标URL
3. 点击"Execute"

**TabNabbing（标签页劫持）：**
当检测到用户切换到其他标签页时，悄悄将当前页面替换为钓鱼页面。用户切回来时往往不会注意到页面已被替换。

**操作步骤：**
1. 展开 "Social Engineering" -> "TabNabbing"
2. 配置钓鱼页面URL
3. 点击"Execute"

#### 4.3.3 点击劫持（Clickjacking）

点击劫持是一种通过在可见页面上覆盖不可见的恶意页面，诱导用户点击的攻击方式。

**BeEF中的点击劫持模块：**

1. **Clickjacking**：基础点击劫持模块
2. **Cursor Spoofing**：伪造鼠标光标位置
3. **Invisible Iframe**：创建透明iframe覆盖层

**Clickjacking模块操作：**
1. 展开 "Social Engineering" -> "Clickjacking"
2. 配置参数：
   - **target_url**：要嵌入的目标页面URL（如设置页面）
   - **button_text**：诱使用户点击的按钮文字
3. 点击"Execute"

**攻击原理：**
```
┌─────────────────────────────────┐
│     诱骗页面（可见）             │
│  ┌─────────────────────────┐    │
│  │  点击这里赢取大奖！     │    │
│  │  [ 立即领取 ]           │    │
│  └─────────────────────────┘    │
│                                 │
│  ┌─────────────────────────┐    │
│  │  透明iframe（不可见）   │    │  ← 实际点击的是这里
│  │  [ 删除账户 ]           │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

#### 4.3.4 剪贴板劫持

剪贴板劫持可以修改用户剪贴板中的内容，常用于将恶意内容注入到用户的复制操作中。

**操作步骤：**
1. 展开 "Browser" -> "Hooked Domain" -> "Clipboard Event"
2. 配置要注入的内容
3. 点击"Execute"

**攻击场景示例：**
- 用户复制一个命令，粘贴后变成了恶意命令
- 用户复制一个网址，粘贴后变成了钓鱼网站地址
- 用户复制钱包地址，粘贴后变成了攻击者的地址

### 4.4 网络侦察模块

BeEF可以利用被Hook的浏览器作为内网侦察的跳板，因为浏览器处于目标的内网环境中，可以访问内网资源。

#### 4.4.1 内网主机发现

**Ping Sweep（Ping扫描）：**
通过Image对象加载探测内网网段中的存活主机。

**操作步骤：**
1. 展开 "Network" -> "Host" -> "Ping Sweep"
2. 配置参数：
   - **cidr**：目标网段，如 `192.168.1.0/24`
   - **timeout**：超时时间（毫秒）
   - **delay**：每个请求之间的延迟
3. 点击"Execute"

> **截图位置说明**：执行后，在结果中可以看到扫描到的存活主机IP列表。每个IP后面标注了响应状态。

**DNS枚举：**
通过尝试解析常见的内网主机名来发现内网设备。

**操作步骤：**
1. 展开 "Network" -> "DNS" -> "Enumerate Hostnames"
2. 配置域后缀（如 `corp.local`）
3. 点击"Execute"

#### 4.4.2 端口扫描

**Port Scanner模块：**
对指定IP进行端口扫描，发现开放的服务。

**常用端口扫描选项：**
- 快速扫描：扫描常用端口（21, 22, 23, 25, 53, 80, 110, 143, 443, 3306, 3389, 8080等）
- 全端口扫描：扫描1-65535（耗时较长）
- 自定义端口范围

**扫描结果解读：**
- **Open**：端口开放，可建立连接
- **Closed**：端口关闭，有响应但拒绝连接
- **Filtered**：端口被过滤，无响应

#### 4.4.3 跨域资源探测

**Cross-Origin Resource Scanner：**
探测其他域上的资源是否存在，利用的是资源加载的成功/失败状态。

**应用场景：**
- 探测内网网站是否存在（如 `http://192.168.1.1/admin`）
- 检测用户是否登录了某个网站
- 探测内部服务的版本信息

#### 4.4.4 DNS探测

**DNS Enumeration模块：**
通过创建指向不同子域名的资源请求，触发DNS解析，从而判断哪些子域名真实存在。

**常用的DNS探测模块：**
- **DNS Enumerate Hostnames**：枚举主机名
- **DNS Local Domain**：探测本地域名
- **DNS Rebinding**：DNS重绑定攻击

### 4.5 命令执行模块

#### 4.5.1 浏览器内命令执行

**IPEC（Inter-Process Exploitation Channel）：**
BeEF的浏览器内命令执行技术，利用Java、Flash等插件在浏览器沙箱外执行命令。

**Java Applet命令执行：**
如果目标浏览器安装了Java插件且安全设置较低，可以通过签名的Java Applet执行系统命令。

**操作步骤：**
1. 确保目标浏览器安装了Java插件
2. 展开 "IPEC" -> "Java Payload"
3. 配置Payload参数
4. 点击"Execute"

> **注意**：现代浏览器大多已默认禁用Java插件，此方法成功率较低。

#### 4.5.2 配合Metasploit获取Shell

BeEF可以与Metasploit无缝集成，通过浏览器投递Metasploit的Payload，获取系统级Shell。

**集成方式（详见第5章）：**
1. 配置BeEF的Metasploit扩展
2. 启动Metasploit的RPC服务
3. 在BeEF中选择对应的Exploit模块
4. 针对目标浏览器执行

#### 4.5.3 Java/Flash利用

**Java利用模块：**
- Java Payload：执行Java Payload
- Java Applet Reverse TCP：反向TCP连接
- Java 0-day（历史漏洞）

**Flash利用模块：**
- Flash ActionScript注入
- Flash参数注入
- Flash XSS利用

> **注意**：随着Flash的退役和Java插件的禁用，这类模块在现代环境中的适用性越来越低，但在老旧系统中仍可能有效。

---

---

## 📋 内容审核与补充建议

> 针对「第4章 BeEF核心功能模块」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
