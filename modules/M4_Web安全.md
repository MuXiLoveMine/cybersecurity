# M4 Web 安全 · 详细补充

> **模块编号**：M4
> **所属阶段**：阶段二 · 实战进阶
> **建议学习时机**：第 6-9 个月（基础筑基完成后）
> **前置知识**：M1 编程（Python/JS/SQL）+ M2 Linux + M3 网络（HTTP/HTTPS）
> **每日投入**：2 小时（其中靶场实操 ≥ 1.5 小时）
> **信息时效**：2026 年 9 月版

---

## 1. 模块定位与前置知识

### 模块定位
Web 安全是网络安全领域**入门最友好、就业需求最大、实战资源最多**的方向。几乎所有企业都有 Web 应用，Web 漏洞也是最常见的入侵入口。

本模块从 **OWASP Top 10** 出发，系统覆盖所有常见 Web 漏洞的原理、利用、检测与防御。学完本模块，你将具备独立进行 Web 渗透测试的能力。

### 前置知识
- **必选前置**：M1（Python/JS/SQL 基础）+ M2（Linux 基础）+ M3（HTTP/HTTPS 协议）
- **推荐环境**：Kali Linux + Burp Suite + 本地靶场（DVWA / WebGoat 等）
- **工具基础**：会用 Burp Suite 抓包、改包、重放

### Web 安全能力分级

| 级别 | 能力描述 | 对应阶段 |
|------|---------|---------|
| **L1 入门** | 理解 OWASP Top 10 原理，能用工具扫描出漏洞 | 阶段二初 |
| **L2 实用** | 能手工检测和利用常见漏洞，理解绕过技巧 | 阶段二中 |
| **L3 熟练** | 能挖掘复杂漏洞（逻辑漏洞、组合漏洞），编写自动化工具 | 阶段二末 |
| **L4 精通** | 能挖 0day、做代码审计、研究新型攻击技术 | 阶段三及以后 |

---

## 2. 知识图谱

```
Web 安全知识体系
├── Web 安全基础
│   ├── HTTP/HTTPS 协议深度
│   │   ├── 请求方法（GET/POST/PUT/DELETE/OPTIONS/PATCH/HEAD）
│   │   ├── 请求头 / 响应头（重点：Cookie/Authorization/Content-Type/Referer/Origin 等）
│   │   ├── 状态码（2xx/3xx/4xx/5xx 常见含义）
│   │   ├── Cookie 机制（属性：Domain/Path/Expires/HttpOnly/Secure/SameSite）
│   │   ├── Session 与 Token 认证
│   │   ├── CORS 跨域资源共享
│   │   ├── HTTPS 与 TLS 握手
│   │   └── HTTP/2 / HTTP/3 基础认知
│   ├── Web 技术栈
│   │   ├── 前端：HTML/CSS/JavaScript / DOM / AJAX / JSONP / WebSocket
│   │   ├── 后端：PHP / Java (Spring) / Python (Django/Flask) / Node.js / .NET
│   │   ├── 数据库：MySQL / PostgreSQL / SQL Server / MongoDB / Redis
│   │   ├── 中间件：Nginx / Apache / Tomcat / IIS / WebLogic / JBoss
│   │   └── CMS：WordPress / Drupal / Joomla / Discuz / 织梦 / 帝国
│   └── Web 安全方法论
│       ├── OWASP Top 10（2021 版）
│       ├── 渗透测试执行标准（PTES）Web 部分
│       └── 漏洞评级标准（CVSS 3.1）
│
├── 注入类漏洞（Injection）
│   ├── SQL 注入 ⭐⭐⭐ 重点
│   │   ├── 注入点：GET/POST/Cookie/HTTP头/UA/Referer
│   │   ├── 注入类型：联合注入 / 报错注入 / 布尔盲注 / 时间盲注
│   │   ├── 高阶注入：堆叠注入 / 二次注入 / 宽字节注入 / 编码注入
│   │   ├── 各数据库差异：MySQL / SQL Server / Oracle / PostgreSQL / SQLite
│   │   ├── 读写文件与提权
│   │   ├── WAF 绕过
│   │   └── sqlmap 使用与进阶（tamper 脚本、自定义注入）
│   ├── NoSQL 注入（MongoDB / Redis）
│   ├── 命令注入（OS Command Injection）
│   ├── 代码注入（PHP eval / Python exec / Node.js vm）
│   ├── XPath 注入
│   ├── LDAP 注入
│   └── SSTI 模板注入（Jinja2 / Twig / Freemarker / Velocity）
│
├── 认证与授权漏洞
│   ├── 身份认证失效（Broken Authentication）
│   │   ├── 弱密码 / 默认密码 / 密码爆破
│   │   ├── 会话固定攻击
│   │   ├── 会话劫持
│   │   ├── 凭据 stuffing（凭证填充）
│   │   ├── MFA 绕过
│   │   └── JWT 攻击（未验签 / 算法混淆 / 密钥爆破 / kid 注入）
│   ├── 访问控制失效（Broken Access Control）⭐⭐⭐ 重点
│   │   ├── 水平越权（IDOR）
│   │   ├── 垂直越权
│   │   ├── 未授权访问
│   │   ├── 功能级访问控制缺失
│   │   └── 不安全的直接对象引用
│   └── OAuth / SSO 安全
│
├── 客户端攻击
│   ├── XSS 跨站脚本攻击 ⭐⭐⭐ 重点
│   │   ├── 反射型 XSS
│   │   ├── 存储型 XSS
│   │   ├── DOM 型 XSS
│   │   ├── XSS 利用：Cookie 窃取 / 会话劫持 / 钓鱼 / 内网探测
│   │   ├── XSS 绕过（标签过滤 / 事件过滤 / 长度限制 / WAF）
│   │   ├── CSP 内容安全策略与绕过
│   │   └── XSS Platform / BeEF 框架
│   ├── CSRF 跨站请求伪造
│   │   ├── CSRF 原理与利用条件
│   │   ├── CSRF 攻击场景（改密 / 转账 / 管理员操作）
│   │   └── CSRF 防御与绕过
│   ├── 点击劫持（Clickjacking）
│   ├── CORS 配置错误
│   ├── JSONP 安全
│   └── WebSocket 安全
│
├── 服务端典型漏洞
│   ├── 文件上传漏洞 ⭐⭐⭐ 重点
│   │   ├── 前端校验绕过（JS 校验）
│   │   ├── MIME 类型绕过
│   │   ├── 后缀名绕过（黑名单 / 白名单 / .php3 / .phtml / .htaccess）
│   │   ├── %00 截断
│   │   ├── 解析漏洞（Apache / Nginx / IIS）
│   │   ├── 条件竞争
│   │   └── 图片马 + 文件包含组合利用
│   ├── 文件包含漏洞
│   │   ├── 本地文件包含（LFI）
│   │   ├── 远程文件包含（RFI）
│   │   ├── PHP 伪协议（php:// / file:// / data:// / zip://）
│   │   ├── 日志包含 / Session 包含
│   │   └── LFI → RCE 的各种姿势
│   ├── SSRF 服务端请求伪造 ⭐⭐⭐ 重点
│   │   ├── SSRF 原理与危害
│   │   ├── 利用场景：内网探测 / 云服务元数据 / Redis 攻击
│   │   ├── 绕过：DNS Rebinding / 短地址 / 进制转换 / @ 符号
│   │   ├── Gopher 协议扩展利用
│   │   └── SSRF 防御（白名单 / 内网限制 / 禁用协议）
│   ├── XXE XML 外部实体注入
│   │   ├── XXE 原理（DTD / ENTITY）
│   │   ├── 有回显 XXE / 无回显 XXE（OOB）
│   │   ├── XXE 利用：读文件 / SSRF / DOS
│   │   └── 各语言 XXE 默认情况与修复
│   ├── 反序列化漏洞 ⭐⭐⭐ 重点
│   │   ├── PHP 反序列化（POP 链 / Phar 反序列化）
│   │   ├── Java 反序列化（Shiro / Fastjson / Jackson / Commons Collections）
│   │   ├── Python 反序列化（pickle / PyYAML）
│   │   ├── .NET 反序列化
│   │   └── 反序列化防御
│   └── 逻辑漏洞 / 业务安全漏洞 ⭐⭐⭐ 重点
│       ├── 支付逻辑漏洞（金额篡改 / 数量篡改 / 优惠券滥用）
│       ├── 密码找回逻辑漏洞
│       ├── 验证码绕过（重放 / 爆破 / 客户端验证）
│       ├── 注册逻辑漏洞（用户名占用 / 邀请码绕过）
│       ├── 越权操作（水平 / 垂直 / 未授权）
│       ├── 接口滥用（短信轰炸 / 邮件轰炸 / 刷票）
│       └── 竞争条件（并发 / 条件竞争）
│
├── 配置与基础设施漏洞
│   ├── 安全配置错误（Security Misconfiguration）
│   │   ├── 默认密码 / 默认配置
│   │   ├── 不必要的功能开启
│   │   ├── 错误的 HTTP 安全头
│   │   ├── 目录遍历 / 目录列出
│   │   ├── 备份文件 / 敏感文件泄露
│   │   └── 错误信息泄露（栈追踪 / 详细报错）
│   ├── 敏感数据泄露（Sensitive Data Exposure）
│   │   ├── 明文传输 / 弱加密
│   │   ├── 密码弱哈希（MD5 / SHA1 无盐）
│   │   ├── API 密钥泄露（GitHub / JS 文件 / 注释）
│   │   ├── Swagger / API 文档泄露
│   │   └── .git / .svn 源码泄露
│   ├── 中间件 / CMS 漏洞
│   │   ├── Nginx / Apache / IIS 解析漏洞
│   │   ├── Tomcat / WebLogic / JBoss / Jenkins 漏洞
│   │   ├── WordPress / Drupal / 常见 CMS 漏洞
│   │   ├── Redis 未授权访问
│   │   ├── MongoDB / Elasticsearch 未授权
│   │   └── Docker API 未授权
│   ├── 使用含有已知漏洞的组件
│   │   ├── 第三方组件漏洞（Struts2 / Log4j / Spring）
│   │   ├── 前端库漏洞
│   │   └── SCA 软件成分分析
│   └── 重定向与转发漏洞（Open Redirect）
│
├── Web 安全工具链
│   ├── 抓包与代理：Burp Suite / OWASP ZAP / Fiddler
│   ├── 信息收集：Nmap / Gobuster / ffuf / dirsearch / Amass / subfinder
│   ├── 漏洞扫描：Nuclei / AWVS / Nessus / AppScan / Xray
│   ├── SQL 注入：sqlmap
│   ├── XSS：XSS Platform / BeEF / XSStrike
│   ├── CMS 扫描：Wappalyzer / CMSeeK / Droopescan / WPScan
│   ├── 指纹识别：whatweb / wappalyzer / Ehole
│   └── 模糊测试：wfuzz / ffuf / Burp Intruder
│
└── Web 安全防御
    ├── 输入验证与输出编码
    ├── WAF Web 应用防火墙
    ├── 安全开发规范
    ├── 安全头配置（CSP / HSTS / X-Frame-Options / X-XSS-Protection）
    ├── Cookie 安全属性
    ├── CSRF Token
    ├── 权限控制最佳实践
    └── HTTPS 与 TLS 安全配置
```

---

## 3. 学习顺序与时间表

### 总时长：约 4 个月（240 小时）

| 周次 | 学习内容 | 重点漏洞 | PortSwigger 进度 |
|------|---------|---------|-----------------|
| **第 1-2 周** | Web 基础回顾 + 信息收集 | HTTP 深解、指纹识别、目录爆破 | 完成 Introduction 模块 |
| **第 3-4 周** | SQL 注入 | 联合/报错/盲注/二阶注入、sqlmap | 完成 SQL Injection 全部实验 |
| **第 5-6 周** | XSS 跨站脚本 | 反射/存储/DOM 型、CSP 绕过 | 完成 XSS 全部实验 |
| **第 7-8 周** | 认证与授权 | 会话安全、JWT 攻击、越权（IDOR） | 完成 Authentication + Access Control |
| **第 9-10 周** | 文件上传 + 文件包含 + SSRF | 各种上传绕过、伪协议、SSRF 利用 | 完成 File upload + SSRF 实验 |
| **第 11-12 周** | XXE + 反序列化 + 逻辑漏洞 | XXE、PHP/Java 反序列化、业务逻辑 | 完成 XXE + Deserialization + Business logic |
| **第 13-14 周** | 配置错误 + 信息泄露 + CORS 等 | 各种配置漏洞、信息泄露、CORS | 完成剩余服务端专题 |
| **第 15-16 周** | 综合实战 + 自动化工具 | Burp 高级用法、Python 脚本、靶场实战 | 完成 Client-side 路径 + 复习 |

### 学习方法论

```
每个漏洞的学习五步法：
  1. 理解原理 → 为什么会产生这个漏洞？（代码层面）
  2. 简单利用 → 在靶场上复现最基础的 Payload
  3. 进阶绕过 → 学习各种绕过技巧（WAF / 过滤 / 编码）
  4. 实战综合 → 组合漏洞、复杂场景利用
  5. 防御修复 → 如何修复？代码层面怎么写？
```

---

## 4. 工具链与版本建议

### 4.1 核心工具

| 工具 | 版本 / 类型 | 用途 | 优先级 | 费用 |
|------|------------|------|--------|------|
| **Burp Suite Pro** | 最新版 | Web 渗透测试综合平台（代理/爬虫/扫描/ Intruder/插件） | ⭐⭐⭐ 必用 | 付费（约 $449/年） |
| **Burp Suite Community** | 最新版 | Burp 免费版，功能受限，入门够用 | ⭐⭐⭐ 必装 | 免费 |
| **OWASP ZAP** | 最新版 | 开源 Web 安全扫描器（Burp 免费替代） | ⭐⭐ 推荐 | 免费 |
| **sqlmap** | 最新版（GitHub dev 分支） | 自动化 SQL 注入检测与利用 | ⭐⭐⭐ 必装 | 免费 |
| **Nuclei** | 最新版 | 基于模板的快速漏洞扫描器 | ⭐⭐⭐ 必装 | 免费 |
| **Xray** | 社区版 / 高级版 | 国产 Web 漏洞扫描器 | ⭐⭐ 推荐 | 免费 + 付费 |
| **AWVS** | 最新版 | 商业 Web 漏洞扫描器 | ⭐⭐ 推荐 | 付费（贵） |
| **Nessus Essentials** | 最新版 | 漏洞扫描器（家庭/学习免费） | ⭐⭐ 推荐 | 免费版（限 16 IP） |

### 4.2 信息收集工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Gobuster / ffuf / dirsearch** | Web 目录 / 文件 / DNS 爆破 | ⭐⭐⭐ 必装 |
| **Amass / subfinder / Sublist3r** | 子域名枚举 | ⭐⭐⭐ 必装 |
| **WhatWeb / Wappalyzer / Ehole** | CMS / 技术栈指纹识别 | ⭐⭐⭐ 必装 |
| **WPScan / CMSeeK / Droopescan** | CMS 专用扫描器 | ⭐⭐ 推荐 |
| **httpx** | HTTP 存活探测 | ⭐⭐⭐ 必装 |
| **nuclei-templates** | Nuclei 漏洞模板库（社区持续更新） | ⭐⭐⭐ 必装 |
| **Shodan / Fofa / ZoomEye** | 网络空间搜索引擎 | ⭐⭐ 推荐 |
| **Wayback Machine / gau** | 历史 URL 抓取 | ⭐⭐ 推荐 |

### 4.3 Burp Suite 必备插件

| 插件 | 用途 | 优先级 |
|------|------|--------|
| **Repeater / Intruder / Decoder / Comparer** | Burp 自带核心功能 | ⭐⭐⭐ 必用 |
| **Hackvertor** | 强大的编码转换与 Payload 生成 | ⭐⭐⭐ 强烈推荐 |
| **Autorize** | 自动检测越权漏洞（水平/垂直） | ⭐⭐⭐ 强烈推荐 |
| **Active Scan++** | 增强 Burp 主动扫描能力 | ⭐⭐ 推荐 |
| **WSDLer** | WSDL/SOAP Web Service 解析 | ⭐⭐ 推荐 |
| **JSON Web Tokens** | JWT 解析与攻击 | ⭐⭐ 推荐 |
| **Param Miner** | 隐藏参数发现 | ⭐⭐ 推荐 |
| **Retire.js** | 前端 JS 库漏洞检测 | ⭐⭐ 推荐 |
| **Logger++** | 高级日志记录 | ⭐⭐ 推荐 |
| **Upload Scanner** | 文件上传漏洞检测 | ⭐⭐ 推荐 |

---

## 5. 编程 / 脚本练习

### 5.1 Python 安全脚本

```python
# 练习 1：Web 目录爆破器（多线程版）
import requests
import threading
from queue import Queue

def dir_brute(url, wordlist):
    q = Queue()
    for word in wordlist:
        q.put(word.strip())
    
    def worker():
        while not q.empty():
            path = q.get()
            try:
                resp = requests.get(f"{url}/{path}", timeout=5, allow_redirects=False)
                if resp.status_code in [200, 301, 403, 401]:
                    print(f"[{resp.status_code}] /{path}")
            except:
                pass
            q.task_done()
    
    for _ in range(20):
        threading.Thread(target=worker, daemon=True).start()
    q.join()

# 练习 2：简单 SQL 注入检测脚本（基于错误消息）
# 练习 3：XSS 扫描器（基于反射检测）
# 练习 4：子域名爆破工具（基于字典 + HTTP 探测 + DNS 查询）
# 练习 5：CMS 指纹识别工具（匹配 favicon hash / 特征路径 / 特征字符串）
# 练习 6：JWT 破解脚本（HS256 密钥爆破 / 算法混淆测试）
# 练习 7：批量 URL 存活检测 + 指纹识别（整合 httpx + whatweb 思路）
# 练习 8：基于 requests 的 SSRF 检测脚本
# 练习 9：文件上传漏洞检测脚本
# 练习 10：Burp Suite 插件开发（Python / Java）
```

### 5.2 JavaScript 安全练习

```javascript
// 练习 1：构造各种 XSS Payload
// - 绕过 script 标签过滤
// - 绕过引号过滤
// - 绕过空格过滤
// - DOM XSS 利用

// 练习 2：CSP 绕过 Payload 收集
// 练习 3：CSRF PoC 页面构造
// 练习 4：简单的 XSS 平台（接收 Cookie、记录访问者）
// 练习 5：Node.js 原型链污染漏洞理解与利用
```

### 5.3 sqlmap 高级用法

```bash
# 练习 1：基础使用 — 检测注入点 + 获取数据库
sqlmap -u "http://target.com/page?id=1" --dbs

# 练习 2：POST 数据注入
sqlmap -u "http://target.com/login" --data "user=admin&pass=123"

# 练习 3：Cookie 注入 + 指定数据库类型
sqlmap -u "http://target.com/" --cookie "id=1" --dbms mysql

# 练习 4：tamper 脚本绕过 WAF
sqlmap -u "http://target.com/page?id=1" --tamper=space2comment,bypassesqlinjection

# 练习 5：获取 Shell / 读写文件
sqlmap -u "http://target.com/page?id=1" --os-shell
sqlmap -u "http://target.com/page?id=1" --file-read "/etc/passwd"

# 练习 6：自定义注入点（指定参数 + 位置）
# 练习 7：二阶注入
# 练习 8：写自己的 tamper 脚本
```

---

## 6. 靶场与实验环境

### 6.1 在线靶场（推荐优先级从高到低）

| 靶场 | 特点 | 费用 | 适合阶段 |
|------|------|------|---------|
| **PortSwigger Web Security Academy** | 最系统的 Web 安全实验室，每个漏洞都有配套讲解和练习 | 免费 | 全程 |
| **HackTheBox** | 大量 Web 靶机，从简单到困难 | 免费 + 付费 | 阶段二起 |
| **TryHackMe** | Web 安全专项房间，引导式学习 | 免费 + 付费 | 入门到进阶 |
| **OWASP Juice Shop** | OWASP 官方靶场，包含所有 Top 10 漏洞 | 免费（Docker 部署） | 入门到进阶 |
| **WebGoat** | OWASP 经典 Web 安全教学应用 | 免费 | 入门 |
| **DVWA** | Damn Vulnerable Web App，入门经典 | 免费 | 入门 |
| **BWAPP** | 包含 100+ 个漏洞的 PHP 靶场 | 免费 | 入门到进阶 |
| **VulnHub** | 下载虚拟机靶机本地运行 | 免费 | 全阶段 |
| **Root-Me** | 法国平台，Web 类挑战丰富 | 免费 + 付费 | 进阶 |
| **CTFtime** | CTF 比赛日历，有很多 Web 题 | 免费 | 进阶 |
| **攻防世界** | 国内 CTF 平台，有 Web 专区 | 免费 | 进阶 |
| **Bugku** | 国内 CTF 平台 | 免费 | 入门到进阶 |

### 6.2 本地靶场搭建（Docker 一键部署）

```bash
# 1. DVWA（入门必装）
docker run -d -p 8080:80 vulnerables/web-dvwa

# 2. OWASP Juice Shop（现代化靶场，体验好）
docker run -d -p 3000:3000 bkimminich/juice-shop

# 3. WebGoat + WebWolf
docker run -d -p 8080:8080 -p 9090:9090 webgoat/goatandwolf

# 4. BWAPP
docker run -d -p 8081:80 hackersquad/bwapp

# 5. Pikachu（国产靶场，中文友好）
# GitHub 搜索 "pikachu 靶场"

# 6. Vulhub（预编译的漏洞环境集合，强烈推荐！）
# https://github.com/vulhub/vulhub
git clone https://github.com/vulhub/vulhub.git
cd vulhub/漏洞名/
docker-compose up -d
```

### 6.3 CMS 漏洞环境

| CMS | 漏洞环境 | 获取方式 |
|-----|---------|---------|
| **WordPress** | 各种插件漏洞 | Vulhub / 自己搭建旧版本 |
| **Drupal** | Drupalgeddon 系列 | Vulhub |
| **Joomla** | 各种组件漏洞 | Vulhub |
| **Discuz!** | 国内论坛，经典漏洞 | 网上搜索旧版本 |
| **织梦 CMS（DedeCMS）** | 国内 CMS，漏洞较多 | 官网历史版本 |
| **ThinkPHP** | 国内框架，RCE 漏洞经典 | Vulhub |
| **Shiro** | Java 反序列化经典 | Vulhub |
| **Log4j / Struts2 / Spring** | Java 三大经典漏洞 | Vulhub |

### 6.4 学习路径建议

```
第 1 月：PortSwigger Academy 为主（系统学习原理）
  → 每个实验都自己做一遍，不看答案
  → 做完后看官方 Solution，对比自己的思路

第 2 月：本地靶场 + Vulhub 结合
  → DVWA / BWAPP / Juice Shop 通关
  → Vulhub 选 10-15 个经典漏洞复现

第 3 月：HTB / THM 靶机实战
  → 独立完成 15+ 台 Web 方向 Easy 靶机
  → 每台靶机写 Writeup

第 4 月：CTF + 综合实战
  → 参加 2-3 次 CTF 比赛的 Web 题
  → 做 2-3 个综合项目（见实战项目部分）
```

---

## 7. 推荐资料

### 📚 书籍

| 书名 | 难度 | 备注 |
|------|------|------|
| **《白帽子讲 Web 安全》**第 2 版 | ⭐⭐ 入门 | 吴翰清著，建立 Web 安全思维框架，必读 |
| **《Web 安全深度剖析》** | ⭐⭐⭐ 进阶 | 张炳帅著，系统深入，实战性强 |
| **《Web 前端黑客技术揭秘》** | ⭐⭐⭐ 进阶 | 钟晨鸣著，前端安全必读 |
| **《SQL 注入攻击与防御》**第 2 版 | ⭐⭐⭐ 专题 | SQL 注入圣经 |
| **《The Web Application Hacker's Handbook》**第 2 版 | ⭐⭐⭐⭐ 进阶 | Web 黑客手册，英文经典 |
| **《OWASP Top 10 官方文档》** | ⭐⭐ 入门 | 官方标准，必读 |
| **《Burp Suite 实战指南》** | ⭐⭐ 入门 | Burp 工具使用 |
| **《XSS 跨站脚本攻击剖析与防御》** | ⭐⭐⭐ 专题 | XSS 深入学习 |
| **《代码审计：企业级 Web 安全架构》** | ⭐⭐⭐⭐ 进阶 | 代码审计方向 |

### 🌐 在线文档与教程

| 资源 | 关键词 | 特点 |
|------|--------|------|
| **PortSwigger Web Security Academy** | portswigger.net/web-security | 最系统的 Web 安全免费课程，必学 |
| **OWASP 官方网站** | owasp.org | OWASP Top 10 / 各种指南 / Cheat Sheet |
| **OWASP Cheat Sheet Series** | cheatsheetseries.owasp.org | 各种安全主题速查表 |
| **MDN Web 安全** | developer.mozilla.org/docs/Web/Security | Web 安全参考 |
| **PayloadsAllTheThings** | GitHub - swisskyrepo/PayloadsAllTheThings | Payload 大全，必备 |
| **HackTricks** | book.hacktricks.xyz | 黑客技巧百科全书，持续更新 |
| **CTF Wiki** | ctf-wiki.org | CTF 知识百科，中文 |

### 🎥 视频课程

| 课程 | 平台 | 适合人群 |
|------|------|---------|
| **i 春秋 Web 安全系列** | B 站 / i 春秋 | 系统课程，中文 |
| **合天智汇 Web 安全** | B 站 / 合天网安实验室 | 实操课程 |
| **PortSwigger Academy 配套视频** | YouTube | 官方讲解，英文 |
| **IppSec HTB Walkthrough** | YouTube | HTB 靶机讲解，学习思路 |
| **STÖK** | YouTube | Bug Bounty / Web 安全技巧 |
| **Nahamsec** | YouTube | Bug Bounty 思路与技巧 |
| **LiveOverflow** | YouTube | 深入的安全技术分析 |
| **P牛 / phith0n** | 博客 / B 站 | 国内 Web 安全大牛，技术深度高 |

### 📝 社区与博客

| 平台 | 用途 |
|------|------|
| **先知社区** | 国内顶级安全社区，Web 安全文章质量高 |
| **FreeBuf** | 国内安全资讯与技术社区 |
| **安全客** | 360 安全团队运营 |
| **Paper.seebug.org** | 知道创宇安全知识库 |
| **Phith0n's Blog** | 离别歌博客，PHP/Java 安全深度 |
| **P 牛的博客** | 专注 Java 安全和中间件安全 |
| **Reddit r/websecurity** | 国际 Web 安全社区 |
| **HackerOne Hacktivity** | 漏洞披露平台，学习真实漏洞 |

### 🎯 Bug Bounty 平台（实战进阶）

| 平台 | 特点 | 适合阶段 |
|------|------|---------|
| **补天 SRC** | 国内最大漏洞响应平台 | 阶段二末起 |
| **漏洞盒子** | 国内 SRC 平台 | 阶段二末起 |
| **HackerOne** | 国际最大漏洞赏金平台 | 阶段三 |
| **Bugcrowd** | 国际漏洞赏金平台 | 阶段三 |
| **Intigriti** | 欧洲漏洞赏金平台 | 阶段三 |

---

## 8. 实战项目

### 项目一：个人 Web 漏洞扫描器

**目标**：用 Python 实现一个功能完整的 Web 漏洞扫描器，整合信息收集 + 常见漏洞检测。

**功能模块**：
1. **信息收集模块**
   - 子域名枚举（字典爆破 + 证书透明度）
   - 端口扫描（调用 Nmap 或自研）
   - Web 指纹识别（CMS / 中间件 / 语言 / 框架）
   - 目录 / 文件扫描（多线程）
   - 爬虫（爬取全站链接与参数）
2. **漏洞检测模块**
   - SQL 注入检测（基于错误 + 布尔盲注 + 时间盲注）
   - XSS 检测（反射型 + DOM 型基础检测）
   - 命令注入检测
   - 文件包含检测
   - 敏感文件 / 备份文件检测
   - 弱口令检测（后台登录口）
   - CORS 配置错误检测
3. **报告模块**
   - 生成 HTML 格式报告
   - 漏洞分级（严重/高危/中危/低危/信息）
   - 漏洞详情 + 修复建议

**参考代码量**：1500-2500 行
**预计耗时**：40-50 小时
**对标工具**：简化版 Xray / AWVS

---

### 项目二：CMS 漏洞分析与复现报告集

**目标**：深入分析 10 个经典 CMS / 框架漏洞，从原理到利用到防御全部掌握。

**漏洞清单（参考）**：
1. ThinkPHP 5.x RCE（多版本）
2. Shiro 反序列化 RCE（Cookie  RememberMe）
3. Fastjson 反序列化 RCE
4. Log4j2 JNDI 注入（Log4Shell）
5. WordPress 某插件 SQL 注入
6. Drupal Drupalgeddon 2 RCE
7. Nginx 解析漏洞 + 目录穿越
8. S2-061 / S2-045 等 Struts2 经典漏洞
9. Spring Cloud Function SpEL 注入
10. Redis 未授权访问 → GetShell

**每个漏洞的分析报告包含**：
- 漏洞简介与影响范围
- 漏洞原理分析（代码层面）
- 环境搭建步骤（Docker / 本地）
- 复现过程与 Payload
- 进阶利用技巧
- 修复方案与补丁分析
- 参考链接

**预计耗时**：40 小时
**产出物**：10 份漏洞分析报告 + 可复现的环境配置

---

### 项目三：Web 安全加固方案

**目标**：搭建一个有漏洞的 Web 应用，然后从各个层面进行安全加固。

**任务清单**：
1. **搭建靶标环境**
   - 部署一个有漏洞的 Web 应用（如 DVWA / 自己写的有漏洞的博客）
   - 环境：Nginx + PHP-FPM + MySQL + WordPress
2. **代码层加固**
   - 修复 SQL 注入：使用预编译语句
   - 修复 XSS：输出编码 + CSP
   - 修复 CSRF：添加 Token
   - 修复文件上传：白名单 + 重命名 + 存储隔离
   - 修复越权：完善权限校验
3. **服务器层加固**
   - Nginx 安全配置（隐藏版本、安全头、限制方法）
   - PHP 安全配置（禁用危险函数、open_basedir）
   - MySQL 安全配置（删默认库、禁远程、降权运行）
   - 系统层加固（防火墙、SSH 安全、文件权限）
4. **WAF 部署**
   - 部署 ModSecurity + OWASP CRS 规则
   - 调优规则，降低误报
5. **渗透测试验证**
   - 加固前后分别用扫描器扫描，对比结果
   - 手工验证漏洞是否修复
6. 输出《Web 应用安全加固方案》

**预计耗时**：30 小时
**产出物**：加固后的环境 + 加固方案文档

---

### 项目四：CTF Web 解题集 + 自动化脚本

**目标**：刷 30 道 Web CTF 题，总结题型并编写自动化工具。

**题型覆盖**：
- SQL 注入（5 道）
- XSS（3 道）
- 文件上传 / 包含（4 道）
- SSRF（3 道）
- 反序列化（4 道）
- 逻辑漏洞（3 道）
- XXE（2 道）
- SSTI（2 道）
- 信息泄露 / 源码泄露（2 道）
- 综合题（2 道）

**要求**：
- 每道题写详细 Writeup（原理 + 思路 + Payload + Flag）
- 总结题型套路和解题技巧
- 针对常见题型写自动化脚本

**预计耗时**：40 小时
**产出物**：30 道题 Writeup + 解题工具集

---

## 9. 常见误区

### ❌ 误区 1：沉迷工具，不理解原理
**现象**：sqlmap 一把梭，Burp Scanner 扫完直接交报告，问原理全不会。
**纠正**：工具只是提高效率的手段，原理才是核心。每个漏洞都先手工利用一遍，再用工具加速。面试的时候不会有人让你用 sqlmap，都是手写 Payload。

### ❌ 误区 2：只学攻击，不学防御
**现象**：只会打洞，问怎么修、怎么防就懵了。
**纠正**：攻击和防御是一体两面。不懂防御就不懂绕过，也做不了深度渗透。学每个漏洞的时候都要想：怎么修？为什么这么修能防住？有没有绕过的可能？

### ❌ 误区 3：背 Payload，不理解本质
**现象**：收藏了一大堆 Payload 大全，换个场景就不会用了。
**纠正**：理解漏洞产生的根本原因，Payload 只是利用的形式。理解了原理，你自己就能写出无数 Payload，也能根据环境进行变形和绕过。

### ❌ 误区 4：只打 CTF，不碰真实环境
**现象**：CTF 打得很溜，真实渗透测试一塌糊涂。
**纠正**：CTF 题是精心设计的，真实环境要复杂得多（有 WAF、有防护、有业务逻辑）。阶段二末要开始接触真实目标（合法授权的 SRC 项目）。

### ❌ 误区 5：忽视逻辑漏洞和业务安全
**现象**：只关注技术型漏洞（SQL 注入、XSS），觉得逻辑漏洞"不够技术"。
**纠正**：真实业务中，逻辑漏洞的危害往往更大（直接涉及钱、用户数据），而且更难被自动化扫描器发现。高水平的 Web 安全工程师，逻辑漏洞挖掘能力是核心竞争力。

### ❌ 误区 6：不做笔记，不复盘
**现象**：做了很多靶机，过两个月就忘了。
**纠正**：每做一个漏洞、一台靶机，都写详细的笔记和 Writeup。写的过程就是梳理思路的过程，而且以后遇到类似问题可以快速回顾。

### ❌ 误区 7：追新猎奇，基础不牢
**现象**：天天追新漏洞（今天 Log4j，明天 Spring），基础的 SQL 注入绕过都不熟练。
**纠正**：新漏洞本质上都是老漏洞类型的变体。基础打牢了，新漏洞看一眼原理就能复现。基础不牢，每个新漏洞都得从头学。

---

## 10. 自测题与产出物

### 10.1 原理题（SQL 注入）

1. SQL 注入有哪些类型？分别适用于什么场景？
2. 什么是布尔盲注？什么是时间盲注？两者的区别和适用场景？
3. MySQL 注入中，如何获取当前数据库名、表名、列名？（写出 Payload）
4. SQL Server 注入和 MySQL 注入有哪些主要差异？
5. 宽字节注入的原理是什么？什么条件下会产生？
6. 二阶注入的原理是什么？如何检测和利用？
7. sqlmap 的 --tamper 参数有什么用？列举 5 个常用 tamper 及其作用。
8. 如何防御 SQL 注入？预编译为什么能防注入？

### 10.2 原理题（XSS）

1. XSS 有哪三种类型？区别是什么？
2. 反射型 XSS 和 CSRF 有什么区别和联系？
3. DOM 型 XSS 和其他两种有什么不同？挖掘思路有什么区别？
4. CSP 是什么？有哪些常见指令？如何绕过 CSP？
5. XSS 的 HttpOnly Cookie 能不能偷？为什么？XSS 还能做什么？
6. XSS 的 SameSite Cookie 属性有什么作用？Strict 和 Lax 的区别？
7. 如何防御 XSS？输入过滤和输出编码的区别是什么？

### 10.3 原理题（其他常见漏洞）

1. 文件上传漏洞有哪些绕过方式？（至少说 8 种）
2. 什么是文件包含？LFI 和 RFI 的区别？PHP 有哪些伪协议可以利用？
3. SSRF 的原理是什么？能用来做什么？如何绕过内网 IP 限制？
4. XXE 的原理是什么？有回显和无回显分别怎么利用？
5. 反序列化漏洞的原理是什么？PHP 和 Java 反序列化的区别？
6. 什么是 IDOR？如何挖掘和测试？
7. JWT 的结构是什么？常见的 JWT 攻击方式有哪些？
8. 逻辑漏洞有哪些常见类型？举 5 个实际场景。
9. CSRF 的原理是什么？防御方式有哪些？如何绕过？
10. SSRF 和 CSRF 有什么区别？

### 10.4 实操题

1. 不借助 sqlmap，手工完成一次布尔盲注，获取数据库名（用 Burp Intruder 或 Python 脚本）。
2. 在有 CSP 的环境下，构造一个能弹 Cookie 的 XSS Payload。
3. 利用 SSRF 读取云服务器的元数据（169.254.169.254）。
4. 复现 Shiro 反序列化漏洞，获取服务器权限。
5. 找到一个逻辑漏洞并利用（比如密码重置漏洞或支付漏洞）。
6. 独立完成一台 HTB Medium 级别的 Web 靶机。

### 10.5 阶段产出物清单

完成本模块后，你应该拥有以下产出物：

- [ ] **漏洞知识库**
  - [ ] OWASP Top 10 每类漏洞的原理 + 利用 + 防御笔记
  - [ ] 20+ 个经典漏洞的详细分析报告
  - [ ] Payload 集合（SQL/XSS/SSRF/反序列化等，按场景分类）
  - [ ] WAF 绕过技巧总结
- [ ] **工具与脚本**
  - [ ] 个人 Web 漏洞扫描器
  - [ ] 20+ 个安全小脚本（子域名爆破、指纹识别、JWT 工具等）
  - [ ] Burp Suite 插件（至少 1 个自己写的）
  - [ ] sqlmap 自定义 tamper 脚本
- [ ] **靶场战绩**
  - [ ] PortSwigger Academy 完成 100%（或至少 80%）
  - [ ] DVWA / BWAPP / Juice Shop 全部通关
  - [ ] Vulhub 复现 20+ 个漏洞
  - [ ] HTB / THM Web 方向靶机 20+ 台（独立完成）
  - [ ] CTF Web 题 30+ 道
- [ ] **实战经验**
  - [ ] SRC 平台提交 3+ 个有效漏洞（合法授权）
  - [ ] 参与 2+ 次 CTF 比赛
- [ ] **技术输出**
  - [ ] Web 安全技术博客 20+ 篇
  - [ ] 漏洞复现 / Writeup 文章 15+ 篇
  - [ ] GitHub 安全项目获得一定 Star

---

> **下一步建议**：Web 安全是网络安全的入口，学完 M4 你已经具备了核心安全能力。接下来根据你的目标方向选择：
> - 想做渗透测试 / 红队 → 进入 **M5 渗透测试与红队**
> - 想做蓝队 / SOC / 应急响应 → 进入 **M6 蓝队与 SOC**
> - 想做云安全 → 进入 **M8 云原生安全**
> - 想做安全开发 → 进入 **M9 安全开发与 DevSecOps**
