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
