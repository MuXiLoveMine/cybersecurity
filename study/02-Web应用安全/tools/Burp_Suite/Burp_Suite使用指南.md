# Burp Suite 使用指南

> Burp Suite 是 Web 安全测试中最核心的工具，被称为"渗透测试神器"。它集成了代理、爬虫、扫描、爆破等多种功能，是 Web 安全从业者的必备工具。

---

## 目录

- [一、Burp Suite 简介](#一burp-suite-简介)
- [二、安装与配置](#二安装与配置)
- [三、核心模块介绍](#三核心模块介绍)
- [四、Proxy 代理模块](#四proxy-代理模块)
- [五、Repeater 重放模块](#五repeater-重放模块)
- [六、Intruder 爆破模块](#六intruder-爆破模块)
- [七、Scanner 扫描模块](#七scanner-扫描模块)
- [八、Decoder 编码解码](#八decoder-编码解码)
- [九、Comparer 对比工具](#九comparer-对比工具)
- [十、Extender 插件](#十extender-插件)
- [十一、常用快捷键](#十一常用快捷键)
- [十二、使用技巧](#十二使用技巧)

---

## 一、Burp Suite 简介

Burp Suite 是 PortSwigger 公司开发的集成化 Web 安全测试工具。

**版本**：
- **Community（社区版）**：免费，功能受限
- **Professional（专业版）**：付费，功能完整（扫描、插件等）
- **Enterprise（企业版）**：企业级自动化扫描

**主要功能**：
- 代理服务器（Proxy）
- Web 爬虫（Spider / Crawler）
- 漏洞扫描（Scanner）
- 重放测试（Repeater）
- 暴力破解（Intruder）
- 编码解码（Decoder）
- 数据对比（Comparer）
- 插件扩展（Extender）

---

## 二、安装与配置

### 2.1 安装

1. 下载：https://portswigger.net/burp
2. 安装 Java 环境（Burp 基于 Java）
3. 运行 Burp Suite

### 2.2 配置浏览器代理

**Burp 默认代理设置**：
- 地址：`127.0.0.1`
- 端口：`8080`

**Firefox 配置**：
1. 设置 → 网络设置 → 手动代理配置
2. HTTP 代理：127.0.0.1  端口：8080
3. 勾选"也将此代理用于 HTTPS"

**Chrome 配置**：
- 使用 SwitchyOmega 等插件管理代理
- 或系统代理设置

### 2.3 安装 HTTPS 证书

1. 配置好代理后，访问 `http://burp`
2. 点击 "CA Certificate" 下载证书
3. 导入证书到浏览器：
   - Firefox：设置 → 隐私与安全 → 查看证书 → 导入 → 勾选"信任此 CA 颁发的网站证书"
   - Chrome：设置 → 隐私和安全 → 安全 → 管理证书 → 导入 → 受信任的根证书颁发机构

---

## 三、核心模块介绍

```
Burp Suite
├── Dashboard     # 仪表板，任务管理、扫描状态
├── Target        # 目标管理，站点地图
├── Proxy         # 代理服务器，拦截请求
├── Repeater      # 重放器，手动修改并重放请求
├── Intruder      # 爆破器，自动化攻击
├── Scanner       # 扫描器，主动/被动漏洞扫描
├── Decoder       # 编解码器，各种编码转换
├── Comparer      # 对比工具，比较两个响应的差异
├── Sequencer     # 序列分析，测试随机性
├── Extender      # 扩展管理，安装插件
└── Settings      # 设置
```

---

## 四、Proxy 代理模块

### 4.1 界面说明

- **Intercept**：拦截开关，查看和修改拦截的请求/响应
- **HTTP history**：HTTP 请求历史记录
- **WebSockets history**：WebSocket 历史
- **Proxy settings**：代理设置

### 4.2 基本操作

| 按钮 | 功能 |
|------|------|
| `Intercept is on/off` | 开启/关闭拦截 |
| `Forward` | 放行当前请求 |
| `Drop` | 丢弃当前请求 |
| `Action` | 操作菜单（发送到其他模块等） |
| `Raw / Headers / Hex / Params` | 不同视图 |

### 4.3 常用操作

1. **拦截请求**：开启 Intercept，浏览器访问页面，Burp 会拦截请求
2. **修改请求**：在 Raw 或 Params 视图中修改参数
3. **发送到 Repeater**：右键 → Send to Repeater（Ctrl+R）
4. **发送到 Intruder**：右键 → Send to Intruder（Ctrl+I）
5. **查看历史**：HTTP history 标签页查看所有请求

### 4.4 代理设置

- **添加/删除监听端口**：Proxy settings → Add
- **SSL Pass Through**：跳过某些 HTTPS 站点的拦截
- **Match and Replace**：自动替换请求/响应内容
- **Response Modification**：自动修改响应（如禁用 JS、移除 CSP 等）

### 4.5 常用选项

```
Proxy settings → Response Modification
  ☑ Unhide hidden form fields       显示隐藏表单字段
  ☑ Enable disabled form fields     启用禁用的表单字段
  ☑ Remove JavaScript validation    移除 JS 验证
  ☑ Remove all JavaScript           移除所有 JS
  ☑ Remove object tags              移除 object 标签
```

---

## 五、Repeater 重放模块

### 5.1 功能

手动修改 HTTP 请求并发送，观察响应变化。用于手工测试漏洞。

### 5.2 基本操作

1. 从 Proxy 右键 Send to Repeater（Ctrl+R）
2. 在左侧请求面板修改请求内容
3. 点击 "Send"（Ctrl+Enter）发送请求
4. 右侧查看响应
5. 多次修改发送，比较响应差异

### 5.3 常用操作

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Enter` | 发送请求 |
| `Ctrl+Shift+R` | 重新发送 |
| `Ctrl+Z` | 撤销修改 |
| `Ctrl+Y` | 重做修改 |
| `Ctrl+Shift+U` | URL 编码选中内容 |
| `Ctrl+Shift+L` | URL 解码选中内容 |

### 5.4 视图切换

- **Pretty**：格式化视图（推荐）
- **Raw**：原始数据
- **Hex**：十六进制
- **Render**：渲染页面（查看页面效果）

---

## 六、Intruder 爆破模块

### 6.1 功能

自动化攻击工具，常用于：
- 密码爆破
- 验证码绕过
- 目录遍历
- SQL 注入 fuzz
- 参数枚举

### 6.2 攻击类型（Attack type）

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| **Sniper** | 狙击手，单 payload 集，逐个替换每个位置 | 单个参数爆破 |
| **Battering ram** | 撞锤，单 payload 集，同时替换所有位置 | 多个相同参数 |
| **Pitchfork** | 叉耙，多 payload 集，一一对应 | 用户名+密码各一个字典，逐行对应 |
| **Cluster bomb** | 集束炸弹，多 payload 集，笛卡尔积 | 用户名+密码组合爆破（所有组合） |

### 6.3 使用步骤

1. 发送请求到 Intruder（Ctrl+I）
2. **Positions 标签**：设置 payload 位置（用 § 包裹）
   - 点击 "Clear §" 清除所有
   - 选中要爆破的参数值，点击 "Add §"
3. **Payloads 标签**：设置 payload 集合
   - Payload type：选择 payload 类型
   - 加载字典：Load... 按钮
4. **Options 标签**：可选设置（线程数、超时、匹配结果等）
5. 点击 "Start attack" 开始攻击
6. 在结果窗口中根据 Length/Status 判断成功

### 6.4 Payload 类型

| 类型 | 说明 |
|------|------|
| **Simple list** | 简单列表（字典） |
| **Runtime file** | 运行时文件（大字典） |
| **Numbers** | 数字序列 |
| **Brute forcer** | 暴力生成字符组合 |
| **Character substitution** | 字符替换 |
| **Recursive grep** | 递归抓取 |
| **Username generator** | 用户名生成 |
| **Illegal Unicode** | 非法 Unicode |
| **Character blocks** | 字符块 |

### 6.5 结果判断

- **Status**：响应状态码（200/302/403 等）
- **Length**：响应长度（长度不同通常意味着结果不同）
- **Time**：响应时间（时间盲注时看这个）

点击列标题可以排序，快速找到异常值。

### 6.6 常用场景

**密码爆破**：
- Attack type: Sniper
- Payload 位置：password 参数
- Payload：密码字典

**用户名枚举**：
- Attack type: Sniper
- Payload 位置：username 参数
- 观察：不同用户名返回不同的错误提示

**验证码绕过**：
- Attack type: Numbers
- 范围：0000-9999
- 位数：4 位

---

## 七、Scanner 扫描模块

> 仅专业版可用

### 7.1 扫描类型

| 类型 | 说明 |
|------|------|
| **Active Scan** | 主动扫描，发送大量 payload 探测漏洞 |
| **Passive Scan** | 被动扫描，分析已有流量发现问题，不发送额外请求 |

### 7.2 扫描方式

1. **全站扫描**：Target → 站点地图 → 右键 → Scan
2. **单 URL 扫描**：Dashboard → New scan → 输入 URL
3. **选中请求扫描**：右键 → Do an active scan

### 7.3 扫描结果

- Dashboard → Issue activity 查看扫描到的问题
- Severity：严重程度（High/Medium/Low/Information）
- Confidence：置信度（Certain/Firm/Tentative）

---

## 八、Decoder 编码解码

### 8.1 功能

各种编码解码转换，处理数据时常用。

### 8.2 支持的编码

| 类别 | 编码方式 |
|------|---------|
| **URL** | URL encode / decode |
| **HTML** | HTML encode / decode |
| **Base64** | Base64 encode / decode |
| **ASCII hex** | 十六进制编解码 |
| **Unicode** | Unicode 编解码 |
| **GZIP** | Gzip 压缩/解压 |
| **Hash** | MD5、SHA1、SHA256 等 |

### 8.3 使用

1. 输入原始数据
2. 选择编码/解码方式
3. 查看结果
4. 可多次编码（Smart decode 智能解码）

---

## 九、Comparer 对比工具

### 9.1 功能

比较两个请求或响应之间的差异，常用于：
- 判断 SQL 注入布尔盲注的真假差异
- 比较正常和异常响应的区别
- 对比两个相似请求

### 9.2 使用

1. 右键请求 → Send to Comparer（request/response）
2. 打开 Comparer 标签
3. 选择两个要比较的项
4. 点击 "Words" 或 "Bytes" 比较
5. 查看差异（高亮显示不同的部分）

---

## 十、Extender 插件

### 10.1 插件管理

- **BApp Store**：官方插件商店，一键安装
- **Extensions**：已安装插件列表
- **Settings**：扩展设置（Python/Java 环境）

### 10.2 常用插件推荐

| 插件 | 功能 |
|------|------|
| **SQLiPy** | SQLMap 集成 |
| **WSDLer** | WSDL 解析 |
| **JsonDecoder** | JSON 格式化 |
| **Hackvertor** | 高级编码转换 |
| **Autorize** | 权限测试（越权检测） |
| **Reflector** | 反射型漏洞检测 |
| **Logger++** | 日志增强 |
| **Burp Suite Crypto** | 加密解密 |
| **Upload Scanner** | 文件上传扫描 |
| **ActiveScan++** | 增强主动扫描 |

### 10.3 安装 Python 插件

1. 下载 Jython：https://www.jython.org/download
2. Extender → Options → Python Environment → 选择 jython.jar
3. 然后即可安装 Python 插件

---

## 十一、常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+P` | 切换代理拦截开关 |
| `Ctrl+R` | 发送到 Repeater |
| `Ctrl+I` | 发送到 Intruder |
| `Ctrl+U` | 发送到 Scanner（主动扫描） |
| `Ctrl+Enter` | Repeater 中发送请求 |
| `Ctrl+D` | 发送到 Decoder |
| `Ctrl+K` | 发送到 Comparer |
| `Ctrl+F` | 查找 |
| `Ctrl+S` | 保存 |
| `Ctrl+Z` | 撤销 |
| `Ctrl+Y` | 重做 |
| `Ctrl+T` | 新建标签页 |
| `Ctrl+W` | 关闭标签页 |
| `Alt+左/右` | 切换标签页 |

---

## 十二、使用技巧

### 12.1 提高效率

1. **范围设置**：在 Target → Scope 设置目标范围，只拦截目标请求
2. **过滤器**：HTTP history 中使用过滤功能，快速找到目标请求
3. **注释标记**：给重要请求加注释和高亮
4. **项目文件**：保存项目文件，下次继续工作

### 12.2 测试流程

```
1. 配置代理，开启拦截
2. 浏览目标网站，收集请求
3. 在 Target 中查看站点地图
4. 对可疑参数发送到 Repeater 手工测试
5. 需要爆破的参数发送到 Intruder
6. 编码问题用 Decoder 处理
7. 差异对比用 Comparer
8. 批量扫描用 Scanner
```

### 12.3 注意事项

1. **合法测试**：只测试授权的目标
2. **备份重要数据**：测试前确认数据可恢复
3. **控制请求频率**：避免对目标造成过大压力
4. **使用专业版**：社区版功能受限，专业版功能更全

---

> **延伸学习**：Burp Suite 是 Web 安全测试的核心工具，需要大量实战才能熟练掌握。建议结合 DVWA、Pikachu 等靶场进行练习，熟悉每个模块的使用场景和技巧。

---

## 十三、Intruder 高级用法

### 13.1 Pitchfork（叉耙）模式详解

Pitchfork 模式使用多个 payload 集，每个 payload 集对应一个位置，按行号一一对应同时替换。

```
场景：撞库攻击，使用已泄露的用户名+密码对

位置1：username=§user1§
位置2：password=§pass1§

Payload set 1（用户名）：Payload set 2（密码）：
  admin                 P@ssw0rd
  root                  toor
  test                  123456

Pitchfork 执行：
  请求1：username=admin&password=P@ssw0rd
  请求2：username=root&password=toor
  请求3：username=test&password=123456

注意：行数以最短的 payload 集为准
```

### 13.2 Cluster Bomb（集束炸弹）模式详解

Cluster Bomb 模式使用多个 payload 集，生成所有可能的组合（笛卡尔积）。

```
场景：用户名+密码全组合爆破

位置1：username=§user§
位置2：password=§pass§

Payload set 1（3个用户名）× Payload set 2（3个密码）= 9 次请求

执行顺序：
  1: user1 + pass1
  2: user1 + pass2
  3: user1 + pass3
  4: user2 + pass1
  5: user2 + pass2
  ...
  9: user3 + pass3
```

### 13.3 Payload 处理规则

在 Payloads 标签页的 Payload Processing 中可以添加处理规则：

```
Add → Add prefix          添加前缀
Add → Add suffix          添加后缀
Add → Match/replace       正则匹配替换
Add → Skip if             条件跳过
Add → Invoke burp extension 调用扩展处理

示例：生成带后缀的密码字典
原始 Payload: password
Add suffix: → 123 → password123
Add suffix: → !  → password123!
```

### 13.4 Grep - Extract 提取响应数据

在 Options 标签页的 Grep - Extract 中可以设置从响应中提取数据：

```
1. 勾选 "Extract the following information from responses"
2. 点击 Add
3. 在弹出的窗口中选择响应内容区域
4. 自动生成正则表达式
5. 结果列表中会显示提取的列

应用场景：
- 提取 CSRF Token 用于后续请求
- 提取响应中的特定字段值
- 检查响应中是否包含特定内容
```

### 13.5 竞态条件测试

```
竞态条件（Race Condition）测试：

1. 将请求发送到 Intruder
2. 设置一个无用的 payload 位置（如空格）
3. Payload 类型选择 Null payload
4. 设置 "Generate" 选项为 "Continue indefinitely"
5. 在 Options → Request Engine 中：
   - 设置线程数（如 20-50）
   - 关闭 "Pause between requests"
6. 发起攻击后立即观察响应

实际案例：优惠券重复使用
- 同一优惠码在并发请求下被多次使用
- 提现接口并发导致多倍提现
- 投票接口并发刷票
```

---

## 十四、Repeater 高级技巧

### 14.1 请求面板操作技巧

```
1. 快捷编辑：
   - 选中文本 → Ctrl+Shift+U（URL编码）
   - 选中文本 → Ctrl+Shift+L（URL解码）
   - 右键 → Paste → Paste file contents（粘贴文件内容）

2. 请求标签页管理：
   - Ctrl+T 新建标签页
   - 右键标签页 → Rename（重命名）
   - 右键标签页 → Pin（固定）

3. 多请求对比：
   - 在不同标签页中发送修改后的请求
   - 使用 Comparer 对比响应差异

4. 响应面板技巧：
   - Render 视图查看页面渲染效果
   - Inspector 面板查看请求/响应组件详情
   - 右键 → Show response in browser（在浏览器中查看）
```

### 14.2 使用 Inspector 面板

Inspector 面板位于 Repeater 底部，提供结构化的请求/响应编辑：

```
Request sections:
  - Request Attributes（请求属性：方法、URL、协议版本）
  - Request Query Parameters（查询参数）
  - Request Body Parameters（请求体参数）
  - Request Headers（请求头）
  - Request Cookies（Cookie）

Response sections:
  - Response Attributes（响应属性）
  - Response Headers（响应头）
  - Response Cookies（Set-Cookie）
  - Response Body（响应体）

优势：结构化编辑，避免手动拼接出错
```

### 14.3 短链接/重定向分析

```
短链接追踪流程：
1. 将短链接请求发送到 Repeater
2. 发送请求，查看响应
3. 查看 Location 头获取重定向目标
4. 将 Update URL on redirect 关闭
5. 手动修改 URL 为重定向目标
6. 重复直到追踪到最终 URL

利用场景：
- 短链接钓鱼分析
- 重定向链追踪
- 开放重定向漏洞测试
```

---

## 十五、主动扫描 vs 被动扫描

### 15.1 被动扫描

被动扫描在流量经过 Burp 代理时自动执行，不发送额外请求。

```
特点：
- 零额外流量，不对目标产生额外请求
- 分析已有请求和响应中的漏洞特征
- 速度取决于浏览速度
- 适合隐蔽测试

检测内容：
- 响应中是否包含敏感信息（邮箱、手机号、密钥）
- 是否设置安全 Cookie 属性
- HTTP 响应头缺失（CSP、HSTS 等）
- 错误信息泄露
- 版本信息泄露
```

### 15.2 主动扫描

主动扫描向目标发送大量探测请求，主动测试漏洞。

```
特点：
- 发送大量请求（可能触发 WAF）
- 测试深度漏洞（SQL 注入、XSS、命令注入等）
- 可能对目标产生影响（修改数据、触发告警）
- 需谨慎使用

扫描配置：
Settings → Scan
  → Crawl strategy（爬取策略）
     - Simple（快速）
     - Comprehensive（全面）
  → Audit strategy（审计策略）
     - Light（轻量，少量请求）
     - Normal（正常）
     - Deep（深入，大量请求）
  → Audit checks（审计项选择）
     - 可选择/取消特定漏洞类型的检测
```

### 15.3 扫描配置优化

```
推荐配置（生产环境）：
- Crawl: Simple（减少爬取时间）
- Audit: Light（减少请求数量）
- 取消选中 Intrusive checks（避免影响业务）
- 设置 Scan speed: Throttled（限制速度）

推荐配置（测试环境/靶场）：
- Crawl: Comprehensive
- Audit: Deep
- 全选所有检查项
- Scan speed: Fast
```

---

## 十六、插件开发（Extender API）

### 16.1 Burp 扩展开发概述

Burp Suite 支持使用 Java、Python、Ruby 开发扩展插件。

```
开发环境搭建：
1. 下载 Burp Extender API（Java）
2. 配置 IDE（IntelliJ IDEA / Eclipse）
3. 添加 Burp 接口 JAR 包到项目

核心接口：
- IBurpExtender：扩展入口接口
- IProxyListener：代理监听器
- IScannerListener：扫描监听器
- IHttpListener：HTTP 监听器
- IMessageEditorTab：自定义编辑器标签
- IContextMenuFactory：右键菜单
```

### 16.2 Python 插件示例

```python
# Burp Suite Python 插件模板
from burp import IBurpExtender
from burp import IProxyListener

class BurpExtender(IBurpExtender, IProxyListener):
    
    def registerExtenderCallbacks(self, callbacks):
        # 注册扩展
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("My Custom Plugin")
        
        # 注册代理监听器
        callbacks.registerProxyListener(self)
        
        print("Plugin loaded successfully!")
    
    def processProxyMessage(self, messageIsRequest, message):
        if messageIsRequest:
            # 获取请求信息
            messageInfo = message.getMessageInfo()
            request = self._helpers.analyzeRequest(messageInfo)
            
            # 获取 URL
            url = request.getUrl()
            print("Request to: " + str(url))
            
            # 修改请求头（示例：添加自定义 Header）
            # ... 修改逻辑
    
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        if not messageIsRequest:
            # 处理响应
            response = messageInfo.getResponse()
            # 分析响应内容
```

### 16.3 Java 插件示例

```java
package com.example.burp;

import burp.IBurpExtender;
import burp.IBurpExtenderCallbacks;
import burp.IContextMenuFactory;
import burp.IContextMenuInvocation;
import javax.swing.*;

public class MyExtension implements IBurpExtender, IContextMenuFactory {
    
    private IBurpExtenderCallbacks callbacks;
    
    @Override
    public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) {
        this.callbacks = callbacks;
        callbacks.setExtensionName("My Extension");
        callbacks.registerContextMenuFactory(this);
        callbacks.printOutput("Extension loaded!");
    }
    
    @Override
    public List<IContextMenuInvocation> createMenuItems(IContextMenuInvocation invocation) {
        List<IContextMenuInvocation> menus = new ArrayList<>();
        JMenuItem item = new JMenuItem("Send to My Tool");
        item.addActionListener(e -> {
            // 处理右键菜单动作
        });
        menus.add(item);
        return menus;
    }
}
```

---

## 十七、BChecks 自定义扫描规则

BChecks 是 Burp Suite 2023+ 引入的自定义扫描规则格式，使用简单的 DSL（领域特定语言）编写。

### 17.1 BChecks 语法

```
# BCheck 基本结构
metadata:
    language: v2-beta
    author: "Your Name"
    description: "Check for sensitive information exposure"

# 定义检查规则
check:
    # 匹配响应中的特定模式
    match:
        response.body: /password\s*[:=]\s*["']?([a-zA-Z0-9]+)/
    
    # 设置漏洞信息
    finding:
        issue:
            name: "Sensitive Password Exposure"
            severity: high
            description: "Password found in response body"
            remediation: "Remove sensitive data from responses"
```

### 17.2 实用 BCheck 示例

```
# 检测 CORS 错误配置
check:
    request:
        method: GET
        path: /
        headers:
            Origin: https://evil.com
    
    match:
        response.headers["Access-Control-Allow-Origin"]: "https://evil.com"
        response.headers["Access-Control-Allow-Credentials"]: "true"
    
    finding:
        issue:
            name: "CORS Misconfiguration"
            severity: high
            description: "Application reflects arbitrary Origin with credentials"

# 检测 .git 目录泄露
check:
    request:
        method: GET
        path: /.git/config
    
    match:
        response.status: 200
        response.body: /\[core\]/
    
    finding:
        issue:
            name: "Git Repository Exposure"
            severity: high
            description: "Git repository files are accessible"

# 检测敏感头缺失
check:
    match:
        response.headers["X-Frame-Options"]: ""
    
    finding:
        issue:
            name: "Missing X-Frame-Options Header"
            severity: low
            description: "X-Frame-Options header is not set"
```

---

## 十八、移动应用测试

### 18.1 移动应用抓包配置

```
Android 抓包：
1. 设置 Burp 代理监听所有接口（0.0.0.0:8080）
2. 手机 WiFi 设置代理：指向电脑 IP:8080
3. 安装证书：
   - 下载 http://burp/cert
   - 安装到设备（Settings → Security → Install certificate）
   - 或使用 Magisk 模块将证书安装为系统证书

iOS 抓包：
1. 同上设置代理
2. 安装证书：
   - 下载证书 → 设置 → 通用 → VPN与设备管理 → 安装
   - 设置 → 通用 → 关于本机 → 证书信任设置 → 启用信任

注意：
- Android 7.0+ 默认不信任用户证书（需 root 或移除 SSL Pinning）
- 使用 Frida + objection 绕过 SSL Pinning
```

### 18.2 SSL Pinning 绕过

```bash
# 使用 Frida + objection
# 安装
pip3 install frida-tools objection

# 绕过 SSL Pinning
objection -g com.example.app explore
# 在 objection 交互终端中：
android sslpinning disable

# 或使用 Frida 脚本
frida -U -f com.example.app -l ssl_pinning_bypass.js --no-pause

# 常用 SSL Pinning 绕过脚本：
# - frida-android-unpinning
# - Universal Android SSL Pinning Bypass
```

---

## 十九、WebSocket 调试

### 19.1 WebSocket 拦截与修改

```
Burp Proxy 支持 WebSocket 拦截：

1. Proxy → WebSockets history：查看 WebSocket 历史
2. Proxy → Intercept → Intercept WebSocket：开启拦截
3. 可以修改 WebSocket 消息内容后转发

操作：
- Forward：放行消息
- Drop：丢弃消息
- 修改消息内容后 Forward
```

### 19.2 WebSocket 安全测试

```
测试要点：
1. 认证检查：WebSocket 连接是否需要认证
2. 授权检查：是否可以访问其他用户的数据
3. 输入验证：WebSocket 消息是否过滤
4. 注入测试：消息内容中的 SQL/XSS 注入
5. 跨域检查：Origin 头验证

Repeater 中的 WebSocket：
- 右键 WebSocket 消息 → Send to Repeater
- 在 Repeater 中可以修改并重新发送
- 支持修改消息内容、opcode
```

---

## 二十、GraphQL 支持

### 20.1 GraphQL 测试

```
1. 识别 GraphQL 端点：
   - 常见路径：/graphql, /api/graphql, /v1/graphql
   - Content-Type: application/json
   - 请求体包含 query 变量

2. 内省查询（获取所有类型和字段）：
   query: "{ __schema { types { name fields { name } } } }"

3. 在 Repeater 中测试：
   - 发送内省查询获取结构
   - 根据结构构造查询/变更
   - 测试注入和权限
```

### 20.2 GraphQL 安全测试要点

```
1. 内省是否开启（信息泄露）
2. 查询深度限制（防止递归查询导致 DoS）
3. 批量查询限制（防止批量请求 DoS）
4. 认证和授权检查
5. 输入验证
6. SQL 注入通过 GraphQL 变量

示例：
POST /graphql HTTP/1.1
Content-Type: application/json

{"query":"query{ user(id:1){ id name email password } }"}
```

---

## 二十一、Burp Suite Enterprise 版

### 21.1 Enterprise 版特点

```
功能：
- 大规模自动化扫描
- 持续监控（CI/CD 集成）
- 团队协作（共享扫描结果）
- API 集成（RESTful API）
- 扫描调度（定时扫描）
- 报告定制

部署方式：
- Docker 部署
- Kubernetes 部署
- 本地部署（企业内网）

典型场景：
- 持续安全监控
- DevSecOps 集成
- 合规扫描
- 资产发现与管理
```

---

## 二十二、实战案例

### 22.1 案例一：越权漏洞发现

```
步骤：
1. 使用两个账号（普通用户A和管理员B）
2. A 账号操作时拦截请求，记录 API
3. B 账号操作时拦截请求，记录 API
4. 将 A 的请求发送到 Repeater
5. 替换 A 的 Cookie/Token 为 B 的
6. 观察是否返回 B 的数据

发现：用户信息接口存在水平越权
  GET /api/user/1001  → 返回用户1001的信息
  修改为 GET /api/user/1002 → 返回其他用户信息
```

### 22.2 案例二：JWT Token 伪造

```
步骤：
1. 拦截请求，发现使用 JWT 认证
2. 将 JWT 复制到 jwt.io 解码
3. 发现算法为 HS256
4. 测试 none 算法绕过：
   - 修改 Header: {"alg":"none","typ":"JWT"}
   - 修改 Payload: {"role":"admin","user":"admin"}
   - 签名部分留空
5. 发送伪造的 JWT
6. 如果服务器不验证算法，成功以管理员身份访问

防护：服务端强制验证算法
```

### 22.3 案例三：文件上传绕过

```
步骤：
1. 拦截上传请求
2. 尝试各种绕过：
   - 后缀名：.php5, .phtml, .phar, .pht
   - 大小写：.PHP, .Php
   - 空字节：shell.php%00.jpg
   - 双写后缀：shell.phphpp
   - MIME 类型伪造
   - 文件头添加 GIF89a（图片马）
3. 在 Repeater 中逐个测试
4. 找到可绕过的方式后上传 WebShell

技巧：
- 使用 Burp 的 Intruder 批量测试后缀名
- Payload 类型：Simple list
- 加载后缀名字典
- 观察不同后缀的响应差异
```
