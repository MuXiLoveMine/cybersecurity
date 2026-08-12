# Web 应用安全学习指南

> Web 应用安全是网络安全中最热门、就业岗位最多的方向，聚焦 Web 应用的漏洞挖掘、利用与防御。

---

## 一、方向概述

Web 应用安全是网络安全领域最热门、从业人员最多的方向。随着互联网的发展，Web 应用承载了越来越多的业务，也成为了攻击的主要目标。Web 安全研究的是 Web 应用中的各种安全漏洞、攻击技术以及防御方案。

**核心防护对象**：Web 服务器、Web 应用、浏览器、Web API、中间件、CMS、Web 框架

**关键威胁**：SQL 注入、XSS 跨站脚本、CSRF 跨站请求伪造、文件上传漏洞、命令执行、代码执行、SSRF 服务端请求伪造、XXE XML 外部实体注入、反序列化漏洞、业务逻辑漏洞

**职业方向**：Web 安全工程师、渗透测试工程师、漏洞挖掘工程师、安全研究员、WAF 安全工程师、安全开发工程师

---

## 二、详细子方向

### 2.1 客户端安全

#### 2.1.1 XSS 跨站脚本攻击
**核心知识点**
- XSS 原理与分类：反射型、存储型、DOM 型
- XSS 攻击场景与危害
- XSS 绕过技术
- XSS 利用平台（BeEF 等）

**常见绕过**
- 标签绕过：大小写、双写、编码
- 过滤绕过：事件处理器、特殊标签
- WAF 绕过：分块、编码、混淆

**防御方法**
- 输入过滤与输出编码
- CSP（内容安全策略）
- HttpOnly Cookie
- XSS 防护头
- 安全的编码规范

#### 2.1.2 CSRF 跨站请求伪造
**核心知识点**
- CSRF 原理与攻击条件
- CSRF 攻击场景
- CSRF 与 XSS 的区别
- CSRF 利用方式

**防御方法**
- Token 验证
- SameSite Cookie
- Referer 验证
- 验证码
- 二次确认

#### 2.1.3 客户端安全其他
**核心知识点**
- Clickjacking（点击劫持）
- CORS 跨域资源共享
- JSONP 安全
- WebSocket 安全
- HTML5 安全
- 浏览器安全策略
- 同源策略
- 沙箱机制

---

### 2.2 服务端安全

#### 2.2.1 SQL 注入
**核心知识点**
- SQL 注入原理与分类
- 联合查询注入
- 报错注入
- 布尔盲注
- 时间盲注
- 堆叠查询
- 二次注入
- 宽字节注入
- 编码注入

**数据库特性**
- MySQL：information_schema、load_file、into outfile
- MSSQL：xp_cmdshell、存储过程
- Oracle：utl_http、dbms_xmldom
- PostgreSQL：COPY、自定义函数
- Access：偏移注入、暴力猜解

**注入技巧**
- 绕过过滤：大小写、双写、编码、注释
- WAF 绕过：分块传输、HTTP 参数污染
- 无列名注入
- 绕过 addslashes、mysql_real_escape_string

**防御方法**
- 预编译（Prepared Statement）
- 参数化查询
- ORM 框架正确使用
- 输入验证与过滤
- 最小权限原则
- WAF

#### 2.2.2 命令执行漏洞
**核心知识点**
- 命令执行原理
- 系统命令执行
- 管道符与连接符
- 命令执行绕过
- 无回显命令执行

**危险函数**
- PHP：system()、exec()、shell_exec()、passthru()、popen()、反引号
- Java：Runtime.getRuntime().exec()、ProcessBuilder
- Python：os.system()、os.popen()、subprocess

**绕过技巧**
- 空格绕过：${IFS}、$IFS$9、<、>、%09
- 关键字绕过：拼接、编码、通配符
- 长度限制绕过
- 禁用函数绕过

#### 2.2.3 代码执行漏洞
**核心知识点**
- 代码执行原理
- 动态代码执行
- 模板注入
- 表达式注入

**危险函数**
- PHP：eval()、assert()、preg_replace /e、call_user_func()、array_map()
- Python：eval()、exec()、pickle
- Java：反射、表达式引擎（OGNL、SpEL、MVEL）
- JavaScript：eval()、Function()

#### 2.2.4 文件上传漏洞
**核心知识点**
- 文件上传原理
- 前端验证绕过
- MIME 类型验证绕过
- 后缀名验证绕过
- 内容验证绕过
- 解析漏洞
- .htaccess 利用
- 竞争条件上传

**常见解析漏洞**
- Apache：多后缀解析、AddHandler
- Nginx：文件名解析漏洞、PHP CGI 解析漏洞
- IIS：6.0 解析漏洞、PUT 上传
- Tomcat：JSP 上传、PUT 上传

**防御方法**
- 文件重命名
- 文件内容检测
- 文件后缀白名单
- 上传目录权限控制
- 单独域名存储
- WAF

#### 2.2.5 文件包含漏洞
**核心知识点**
- 文件包含原理
- 本地文件包含（LFI）
- 远程文件包含（RFI）
- PHP 伪协议
- 文件包含利用
- 包含日志 getshell
- 包含 session getshell
- 包含上传文件 getshell

**PHP 伪协议**
- php://filter（读文件）
- php://input（POST 数据）
- php://zip（压缩包）
- data://（数据）
- expect://（命令执行）
- phar://（PHP 归档）

#### 2.2.6 SSRF 服务端请求伪造
**核心知识点**
- SSRF 原理
- SSRF 危害
- SSRF 利用场景
- 内网探测
- 端口扫描
- 攻击内网服务
- 读取本地文件
- Gopher 协议利用

**常见协议**
- http/https
- file
- gopher
- dict
- ftp
- sftp

**绕过技巧**
- IP 地址转换（十进制、八进制、十六进制）
- DNS 重绑定
- URL 解析差异
- 短链接
- 302 跳转
- @ 符号绕过

**防御方法**
- 禁用不必要的协议
- 限制内网 IP
- URL 白名单
- 统一错误信息
- 禁止跳转

#### 2.2.7 XXE XML 外部实体注入
**核心知识点**
- XXE 原理
- XML 基础
- DTD 基础
- 外部实体
- XXE 危害
- 读取文件
- SSRF
- 命令执行（特定环境）
- 盲 XXE

**利用方式**
- 有回显：直接读取文件
- 无回显：外带数据（OOB）
- 报错 XXE
- 基于 XInclude

**防御方法**
- 禁用外部实体
- 禁用 DTD
- 升级 XML 解析库
- 输入过滤

#### 2.2.8 反序列化漏洞
**核心知识点**
- 反序列化原理
- 序列化与反序列化
- 魔术方法
- 反序列化漏洞成因
- POP 链构造
- 反序列化利用

**PHP 反序列化**
- 魔术方法：__wakeup()、__destruct()、__toString()、__call() 等
- 常见 POP 链
- PHP 原生类利用
- Phar 反序列化

**Java 反序列化**
- 序列化机制
- 常见 gadget：Commons Collections、Fastjson、Jackson、Shiro、Log4j
- ysoserial 工具
- JRMP 利用

**Python 反序列化**
- pickle 反序列化
- 魔术方法：__reduce__()
- 构造 payload

---

### 2.3 业务逻辑安全

#### 2.3.1 常见业务逻辑漏洞
**核心知识点**
- 业务逻辑漏洞概述
- 越权访问（水平越权、垂直越权）
- 密码找回漏洞
- 验证码绕过
- 短信轰炸
- 邮件轰炸
- 支付漏洞
- 订单篡改
- 数量篡改
- 价格篡改
- 积分篡改
- 优惠券漏洞
- 注册逻辑漏洞
- 登录逻辑漏洞

#### 2.3.2 越权漏洞
**水平越权**
- 用户 A 可以访问用户 B 的数据
- 常见于：查看个人信息、查看订单、修改信息
- 检测方法：修改用户 ID、订单 ID 等参数

**垂直越权**
- 普通用户可以访问管理员功能
- 常见于：后台管理、权限管理
- 检测方法：直接访问管理员页面、修改权限参数

**未授权访问**
- 不需要登录就能访问需要登录的功能
- 常见于：后台页面、API 接口
- 检测方法：直接访问 URL、去掉 Cookie

#### 2.3.3 支付漏洞
**常见类型**
- 价格修改：修改商品价格
- 数量修改：修改购买数量为负数
- 优惠券重复使用
- 积分无限使用
- 支付状态篡改
- 订单金额篡改

**检测方法**
- 抓包修改价格参数
- 修改数量为负数
- 重复提交支付请求
- 修改支付状态
- 篡改订单信息

#### 2.3.4 验证码漏洞
**常见类型**
- 验证码不刷新
- 验证码可预测
- 验证码可绕过
- 验证码识别
- 短信验证码无限制
- 验证码复用

---

### 2.4 API 安全

#### 2.4.1 API 安全概述
**核心知识点**
- API 安全的重要性
- REST API 安全
- GraphQL 安全
- SOAP API 安全
- API 安全风险

**OWASP API Security Top 10**
1. API1:2023 - 失效的对象级授权（BOLA）
2. API2:2023 - 失效的身份认证
3. API3:2023 - 失效的对象属性级授权（BOPLA）
4. API4:2023 - 不受限制的资源消耗
5. API5:2023 - 失效的功能级授权
6. API6:2023 - 不受限制的访问敏感业务流
7. API7:2023 - 服务器端请求伪造（SSRF）
8. API8:2023 - 安全配置错误
9. API9:2023 - 不当的资产管理
10. API10:2023 - 不安全的 API 使用

#### 2.4.2 REST API 安全
**常见漏洞**
- 越权访问
- 注入攻击
- 敏感信息泄露
- 认证绕过
- 速率限制缺失
- CORS 配置错误

**安全措施**
- 认证与授权
- 输入验证
- 输出编码
- 速率限制
- HTTPS
- API 版本控制
- 日志与监控

#### 2.4.3 GraphQL 安全
**常见漏洞**
- 深度嵌套攻击（DoS）
- 批量查询攻击
- 内省查询泄露
- 认证绕过
- 注入攻击
- 敏感信息泄露

**安全措施**
- 查询深度限制
- 查询复杂度限制
- 禁用内省（生产环境）
- 速率限制
- 认证与授权

---

### 2.5 代码审计

#### 2.5.1 代码审计概述
**核心知识点**
- 代码审计的目的
- 代码审计方法
- 自动化审计 vs 人工审计
- 代码审计流程
- 危险函数定位
- 变量追踪
- 数据流分析

#### 2.5.2 PHP 代码审计
**审计要点**
- 危险函数：eval、system、exec、assert 等
- SQL 注入：数据库查询语句
- XSS：输出点
- 文件上传：上传处理
- 文件包含：include、require
- 命令执行：系统命令函数
- 反序列化：unserialize
- XXE：XML 解析

**常见 CMS 审计**
- WordPress
- Drupal
- Joomla
- Discuz
- Dedecms
- ThinkPHP
- Laravel

#### 2.5.3 Java 代码审计
**审计要点**
- SQL 注入：MyBatis、JDBC
- 命令执行：Runtime、ProcessBuilder
- 反序列化：readObject
- XXE：XML 解析
- SSTI：模板引擎
- 表达式注入：OGNL、SpEL
- 文件上传：MultipartFile

**常见框架审计**
- Spring
- Spring Boot
- Struts2
- MyBatis
- Shiro

#### 2.5.4 Python 代码审计
**审计要点**
- 命令执行：os.system、subprocess
- 代码执行：eval、exec
- 反序列化：pickle
- SSTI：Jinja2、Mako
- SQL 注入：SQL 查询
- 文件操作：open、文件上传

**常见框架审计**
- Django
- Flask
- Tornado

#### 2.5.5 自动化代码审计
**工具介绍**
- CodeQL
- Semgrep
- SonarQube
- RIPS
- Fortify
- Checkmarx

**审计流程**
1. 工具初筛
2. 人工验证
3. 漏洞确认
4. 报告编写

---

### 2.6 框架与中间件安全

#### 2.6.1 Web 框架安全
**PHP 框架**
- ThinkPHP：RCE、SQL 注入、文件包含
- Laravel：反序列化、SSTI
- CodeIgniter：SQL 注入、XSS
- Yii：SQL 注入、RCE

**Java 框架**
- Spring：SpEL 注入、RCE
- Spring Boot：Actuator 泄露、RCE
- Struts2：OGNL 注入（S2-001 到 S2-061 等）
- MyBatis：SQL 注入
- Shiro：反序列化、认证绕过

**Python 框架**
- Django：SQL 注入、SSTI
- Flask：SSTI、CSRF
- Tornado：各种漏洞

**JavaScript 框架**
- Node.js：原型链污染、RCE
- Express：各种漏洞
- React：XSS

#### 2.6.2 Web 服务器安全
**Apache**
- 多后缀解析漏洞
- .htaccess 利用
- 目录遍历
- 状态页泄露
- mod_ssl 漏洞

**Nginx**
- 文件名解析漏洞
- 目录遍历
- 配置错误
- 缓冲区溢出
- HTTP/2 漏洞

**IIS**
- IIS 6.0 解析漏洞
- PUT 上传
- WebDAV 漏洞
- 短文件名泄露
- ASP.NET 漏洞

**Tomcat**
- WAR 包部署 getshell
- PUT 上传
- 弱口令
- 反序列化
- JSP 上传

#### 2.6.3 中间件安全
**Redis**
- 未授权访问
- 写 webshell
- 写计划任务
- 写 SSH 公钥
- 主从复制 RCE
- Lua 脚本 RCE

**MySQL**
- 弱口令
- 提权
- UDF 提权
- MOF 提权
- 写 webshell
- 数据泄露

**MongoDB**
- 未授权访问
- NoSQL 注入
- 数据泄露
- 命令执行

**Memcached**
- 未授权访问
- 数据泄露
- DDoS 放大攻击

**Elasticsearch**
- 未授权访问
- 数据泄露
- 命令执行
- Groovy 脚本执行

**JBoss / WildFly**
- 未授权访问
- 部署 war 包 getshell
- JMX 控制台
- 反序列化

**WebLogic**
- 反序列化漏洞（CVE-2015-4852、CVE-2016-3510 等）
- SSRF
- 弱口令
- 部署 war 包

---

### 2.7 WAF 绕过

#### 2.7.1 WAF 概述
**WAF 类型**
- 硬件 WAF
- 软件 WAF
- 云 WAF
- 代码级 WAF

**检测原理**
- 特征匹配
- 正则匹配
- 行为分析
- 机器学习

#### 2.7.2 SQL 注入绕过
**常见绕过技巧**
- 大小写绕过
- 双写绕过
- 编码绕过（URL 编码、Unicode、Hex）
- 注释绕过
- 空格绕过（/**/、%09、%0a、%0d）
- 等价函数替换
- HTTP 参数污染（HPP）
- HTTP 参数污染（HPF）
- 分块传输
- 协议层绕过

#### 2.7.3 XSS 绕过
**常见绕过技巧**
- 大小写混合
- 标签嵌套
- 事件处理器
- 特殊标签
- 编码绕过
- WAF 规则绕过
- DOM XSS 绕过

#### 2.7.4 其他绕过
**文件上传绕过**
- 文件名绕过
- 内容绕过
- 特殊后缀
- 解析漏洞

**命令执行绕过**
- 通配符
- 变量拼接
- 编码
- 内置函数

---

### 2.8 渗透测试

#### 2.8.1 渗透测试概述
**渗透测试类型**
- 黑盒测试
- 白盒测试
- 灰盒测试

**渗透测试标准**
- PTES（渗透测试执行标准）
- OWASP Testing Guide
- NIST SP 800-115

**渗透测试流程**
1. 前期交互
2. 情报收集
3. 威胁建模
4. 漏洞分析
5. 漏洞利用
6. 后渗透
7. 报告编写

#### 2.8.2 信息收集
**主动信息收集**
- 端口扫描
- 服务识别
- 版本探测
- 漏洞扫描
- 目录扫描
- 指纹识别

**被动信息收集**
- WHOIS 查询
- DNS 查询
- 子域名收集
- 搜索引擎
- 社交媒体
- 代码托管平台
- 历史漏洞
- 员工信息

**常用工具**
- Nmap
- Masscan
- Subfinder / Amass / OneForAll
- Dirsearch / Gobuster
- WhatWeb / Wappalyzer
- FOFA / ZoomEye / Shodan
- theHarvester

#### 2.8.3 漏洞扫描与验证
**扫描工具**
- AWVS
- AppScan
- Nessus
- Xray
- Burp Suite Scanner

**漏洞验证**
- 手工验证
- PoC 编写
- 漏洞复现
- 危害评估

#### 2.8.4 Web Shell 与权限维持
**Web Shell**
- 一句话木马
- 大马
- 小马
- 内存马
- 免杀 webshell

**管理工具**
- 中国蚁剑
- 冰蝎
- 菜刀
- Weevely
- Godzilla

**权限维持**
- 隐藏 webshell
- 不死马
- 内存马
- 计划任务
- 服务后门
- 启动项

#### 2.8.5 渗透测试报告
**报告结构**
- 执行摘要
- 测试范围
- 测试方法
- 漏洞详情
- 风险评估
- 修复建议
- 附录

**漏洞详情**
- 漏洞名称
- 漏洞等级
- 漏洞描述
- 复现步骤
- 漏洞危害
- 修复建议
- 参考链接

---

## 三、学习路线

### 阶段 1：Web 基础（1-2 个月）
**学习目标**：掌握 Web 基础知识，理解 Web 工作原理

**学习内容**
- HTTP/HTTPS 协议
- HTML/CSS/JavaScript 基础
- 前端开发基础
- 后端开发基础（PHP 或 Python）
- 数据库基础（MySQL）
- Web 服务器配置（Apache/Nginx）

**实践任务**
- 搭建 LAMP/LNMP 环境
- 开发简单的 Web 应用
- 用 Burp Suite 抓包分析
- 学习 HTTP 请求和响应

### 阶段 2：Web 安全入门（2-3 个月）
**学习目标**：掌握常见 Web 漏洞原理和基本利用

**学习内容**
- SQL 注入（联合查询、报错、盲注）
- XSS 跨站脚本（反射型、存储型、DOM 型）
- CSRF 跨站请求伪造
- 文件上传漏洞
- 文件包含漏洞
- 命令执行漏洞
- 代码执行漏洞
- SSRF 漏洞
- XXE 漏洞
- 信息泄露

**实践任务**
- 打 DVWA 全部关卡
- 打 SQLi-Labs 全部关卡
- 打 Upload-labs 全部关卡
- 打皮卡丘靶场
- 用 Burp Suite 进行渗透测试

### 阶段 3：Web 安全进阶（3-4 个月）
**学习目标**：深入理解高级漏洞，掌握绕过技巧

**学习内容**
- SQL 注入进阶（绕过、WAF 绕过、各种数据库）
- XSS 进阶（绕过、CSP 绕过、利用技巧）
- 反序列化漏洞（PHP、Java、Python）
- 模板注入（SSTI）
- 业务逻辑漏洞
- 越权漏洞
- 支付漏洞
- 验证码漏洞
- 中间件漏洞
- CMS 漏洞
- WAF 绕过

**实践任务**
- 打 CTF Web 题目
- 打 Vulhub 漏洞环境
- 打 PortSwigger Web Security Academy
- 代码审计练习
- 挖 SRC（合法授权）

### 阶段 4：渗透测试实战（2-3 个月）
**学习目标**：掌握完整的渗透测试流程，具备实战能力

**学习内容**
- 渗透测试方法论
- 信息收集技巧
- 漏洞扫描与验证
- Web Shell 使用
- 权限维持
- 内网渗透基础
- 渗透测试报告编写

**实践任务**
- 完成完整的渗透测试项目
- 打综合靶场（如 VulnHub 的靶机）
- 参与 CTF 比赛
- 挖 SRC 漏洞
- 写渗透测试报告

### 阶段 5：深入研究（持续）
**学习目标**：深入研究某个方向，成为专家

**研究方向**
- 代码审计
- 漏洞挖掘
- WAF 绕过
- 浏览器安全
- API 安全
- 云原生安全
- 安全开发
- 安全研究

---

## 四、推荐工具

### 4.1 抓包代理工具
| 工具 | 用途 | 类型 |
|------|------|------|
| Burp Suite | Web 渗透测试必备工具 | 商业（社区版免费） |
| Fiddler | HTTP 抓包调试工具 | 免费 |
| Charles | HTTP 代理抓包工具 | 商业 |
| mitmproxy | 命令行 HTTP 代理 | 开源免费 |
| Wireshark | 网络抓包分析 | 开源免费 |

### 4.2 信息收集工具
| 工具 | 用途 | 类型 |
|------|------|------|
| Nmap | 端口扫描与服务识别 | 开源免费 |
| Masscan | 高速端口扫描 | 开源免费 |
| Subfinder | 子域名收集 | 开源免费 |
| Amass | 子域名枚举 | 开源免费 |
| OneForAll | 子域名收集工具集 | 开源免费 |
| Dirsearch | 目录扫描 | 开源免费 |
| Gobuster | 目录/子域名爆破 | 开源免费 |
| WhatWeb | Web 指纹识别 | 开源免费 |
| Wappalyzer | 技术栈识别 | 浏览器插件 |

### 4.3 漏洞扫描工具
| 工具 | 用途 | 类型 |
|------|------|------|
| AWVS | Web 漏洞扫描器 | 商业 |
| AppScan | Web 漏洞扫描器 | 商业 |
| Nessus | 综合漏洞扫描器 | 商业（家庭版免费） |
| Xray | 长亭科技漏洞扫描器 | 商业（基础版免费） |
| Nikto | Web 服务器扫描器 | 开源免费 |
| Wfuzz | Web 应用模糊测试 | 开源免费 |
| SQLMap | SQL 注入工具 | 开源免费 |
| XSStrike | XSS 扫描与利用 | 开源免费 |

### 4.4 Web Shell 管理工具
| 工具 | 用途 | 类型 |
|------|------|------|
| 中国蚁剑 | Web Shell 管理工具 | 开源免费 |
| 冰蝎 | 动态二进制加密 webshell 管理 | 开源免费 |
| 菜刀 | 经典 webshell 管理工具 | 免费 |
| Weevely | PHP 网页后门 | 开源免费 |
| Godzilla | 哥斯拉 webshell 管理 | 开源免费 |

### 4.5 代码审计工具
| 工具 | 用途 | 类型 |
|------|------|------|
| CodeQL | 语义代码分析引擎 | 开源免费（研究版） |
| Semgrep | 静态代码分析 | 开源免费 |
| SonarQube | 代码质量与安全 | 开源免费 |
| Seay | PHP 代码审计工具 | 免费 |
| RIPS | PHP 代码审计 | 商业 |
| Fortify | 静态代码分析 | 商业 |
| Checkmarx | 静态代码分析 | 商业 |

### 4.6 浏览器插件
| 工具 | 用途 | 类型 |
|------|------|------|
| HackBar | SQL/XSS 测试工具 | 浏览器插件 |
| Max HackBar | HackBar 增强版 | 浏览器插件 |
| Wappalyzer | 技术栈识别 | 浏览器插件 |
| Cookie-Editor | Cookie 编辑 | 浏览器插件 |
| FoxyProxy | 代理切换 | 浏览器插件 |
| SwitchyOmega | 代理管理 | 浏览器插件 |

### 4.7 其他工具
| 工具 | 用途 | 类型 |
|------|------|------|
| Postman | API 测试工具 | 免费 |
| Apifox | API 设计/测试/文档 | 免费 |
| curl | 命令行 HTTP 工具 | 开源免费 |
| httpie | 命令行 HTTP 客户端 | 开源免费 |
| jq | JSON 处理工具 | 开源免费 |
| CyberChef | 网络瑞士军刀 | 开源免费 |

---

## 五、学习资源

### 📚 推荐书籍

#### 基础入门
- 《Web 安全深度剖析》- 适合入门，内容全面
- 《白帽子讲 Web 安全》- 经典 Web 安全书籍，吴翰清著
- 《Web 前端黑客技术揭秘》- 前端安全深入
- 《黑客攻防技术宝典：Web 实战篇》- Web 渗透实战

#### 深入进阶
- 《SQL 注入攻击与防御》- SQL 注入权威指南
- 《XSS 跨站脚本攻击剖析与防御》- XSS 专题
- 《代码审计：企业级 Web 代码安全架构》- 代码审计
- 《Web 渗透测试实战指南》- 渗透测试实战
- 《Metasploit 渗透测试指南》- Metasploit 工具

#### 高级提升
- 《漏洞战争：软件漏洞分析精要》- 漏洞分析
- 《0day 安全：软件漏洞分析技术》- 漏洞挖掘经典
- 《加密与解密》- 逆向工程经典
- 《灰帽黑客》- 黑客技术进阶

#### 业务安全
- 《互联网企业安全高级指南》- 企业安全建设
- 《业务安全实战指南》- 业务安全
- 《数据安全架构设计与实战》- 数据安全

### 🎥 视频课程

#### B 站课程
- 小迪安全 6 个月全套 - 系统全面的 Web 安全课程
- Web 渗透测试 139 集 - 渗透测试入门到进阶
- Burp Suite 从入门到精通 - Burp 工具详解
- SQL 注入从入门到精通 - SQL 注入专题
- XSS 跨站脚本攻击 - XSS 专题
- 红日安全团队教程 - 内网渗透等
- 掌控安全学院 - Web 安全入门
- 合天智汇 - 各种安全课程

#### 国外课程
- PortSwigger Web Security Academy - 免费 Web 安全学习平台
- Udemy：Complete Web Penetration Testing Bootcamp
- Coursera：Web Security Fundamentals
- Cybrary：各种安全课程

#### 国内平台
- 合天网安实验室 - 在线实验平台
- i 春秋 - 安全培训平台
- 实验吧 - 安全实验平台
- 攻防世界 - CTF 练习平台

### 🌐 在线资源

#### 漏洞库与参考
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Web 安全 Top 10
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/) - Web 安全测试指南
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) - 安全速查表
- [CVE Details](https://www.cvedetails.com/) - CVE 漏洞详情
- [Exploit-DB](https://www.exploit-db.com/) - 漏洞利用数据库
- [NVD](https://nvd.nist.gov/) - 国家漏洞数据库

#### Payload 与技巧
- [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) - Payload 大全
- [HackTricks](https://book.hacktricks.xyz/) - 渗透测试技巧百科
- [GTFOBins](https://gtfobins.github.io/) - Linux 提权
- [LOLBAS](https://lolbas-project.github.io/) - Windows 提权
- [XSS Payload 列表](https://github.com/payloadbox/xss-payload-list) - XSS Payload

#### 技术社区
- [FreeBuf](https://www.freebuf.com/) - 安全资讯与技术文章
- [安全客](https://www.anquanke.com/) - 安全资讯平台
- [先知社区](https://xz.aliyun.com/) - 阿里安全技术社区
- [看雪论坛](https://bbs.pediy.com/) - 安全技术论坛
- [T00ls](https://www.t00ls.net/) - 安全社区
- [Seebug](https://www.seebug.org/) - 漏洞平台

#### 博客与文章
- [Phithon 的博客](https://www.leavesongs.com/) - PHP 安全大神
- [P 牛的博客](https://www.leavesongs.com/) - 同上
- [米斯特安全团队](https://www.mi1k7ea.com/) - 安全技术文章
- [国光的博客](https://www.sqlsec.com/) - 安全教程
- [EvilOctopus 的博客](https://eviloctopus.github.io/) - 安全研究

### 🎯 练习平台

#### Web 靶场
- [DVWA](https://dvwa.co.uk/) - Web 漏洞练习平台，入门必打
- [SQLi-Labs](https://github.com/Audi-1/sqli-labs) - SQL 注入练习
- [Upload-labs](https://github.com/c0ny1/upload-labs) - 文件上传练习
- [皮卡丘靶场](https://github.com/zhuifengshaonianhanlu/pikachu) - 综合 Web 漏洞靶场
- [Vulhub](https://vulhub.org/) - 漏洞环境集合，一键搭建
- [VulApps](https://github.com/Medicean/VulApps) - 各种漏洞环境
- [bWAPP](http://www.itsecgames.com/) - 漏洞 Web 应用
- [WebGoat](https://owasp.org/www-project-webgoat/) - OWASP 官方靶场

#### 在线练习
- [PortSwigger Web Security Academy](https://portswigger.net/web-security) - 最佳 Web 安全学习平台，免费
- [Hack The Box](https://www.hackthebox.com/) - 综合渗透练习
- [TryHackMe](https://tryhackme.com/) - 入门友好，有学习路径
- [OverTheWire](https://overthewire.org/wargames/) - 安全练习
- [Root Me](https://www.root-me.org/) - 各种安全挑战
- [PentesterLab](https://pentesterlab.com/) - Web 安全练习

#### CTF 平台
- [攻防世界](https://adworld.xctf.org/) - 国内 CTF 平台
- [CTFHub](https://www.ctfhub.com/) - CTF 练习平台
- [BUUCTF](https://buuoj.cn/) - CTF 练习平台
- [NSSCTF](https://www.nssctf.cn/) - CTF 练习平台
- [Bugku](https://ctf.bugku.com/) - CTF 练习平台
- [CTFtime](https://ctftime.org/) - 全球 CTF 赛事

#### SRC 平台
- [补天漏洞响应平台](https://www.butian.net/) - 漏洞平台
- [漏洞盒子](https://www.vulbox.com/) - 漏洞平台
- [阿里云 SRC](https://security.aliyun.com/) - 阿里 SRC
- [腾讯安全应急响应中心](https://security.tencent.com/) - 腾讯 SRC
- [字节跳动 SRC](https://security.bytedance.com/) - 字节 SRC
- [百度 SRC](https://security.baidu.com/) - 百度 SRC

---

## 六、常见面试题

### 基础概念
1. **OWASP Top 10 有哪些？**
   - 注入、失效的身份认证、敏感数据暴露、XML 外部实体（XXE）、失效的访问控制、安全配置错误、跨站脚本（XSS）、不安全的反序列化、使用含有已知漏洞的组件、不足的日志记录和监控

2. **SQL 注入的类型有哪些？如何防御？**
   - 类型：联合查询、报错注入、布尔盲注、时间盲注、堆叠查询、二次注入、宽字节注入
   - 防御：预编译、参数化查询、输入验证、最小权限、WAF

3. **XSS 的类型有哪些？如何防御？**
   - 类型：反射型、存储型、DOM 型
   - 防御：输入过滤、输出编码、CSP、HttpOnly、安全头

4. **CSRF 的原理是什么？如何防御？**
   - 原理：利用用户已登录的身份，在用户不知情的情况下，以用户的名义完成非法操作
   - 防御：Token 验证、SameSite Cookie、Referer 验证、验证码

### 漏洞原理
5. **SSRF 的原理和利用方式？**
   - 原理：服务端请求伪造，由攻击者构造请求，由服务端发起请求
   - 利用：内网探测、端口扫描、攻击内网服务、读取本地文件、Gopher 协议利用

6. **文件上传漏洞的绕过方式？**
   - 前端验证绕过：抓包修改
   - MIME 类型绕过：修改 Content-Type
   - 后缀名绕过：大小写、特殊后缀、解析漏洞
   - 内容绕过：图片马、文件头
   - .htaccess 利用
   - 竞争条件上传

7. **反序列化漏洞的原理？**
   - 原理：应用程序在反序列化用户可控的数据时，攻击者可以构造恶意的序列化数据，触发魔术方法，执行恶意代码
   - 关键：魔术方法、POP 链、gadget

8. **XXE 的原理和利用？**
   - 原理：XML 解析器解析包含外部实体的 XML 文档
   - 利用：读取文件、SSRF、命令执行（特定环境）、盲 XXE 外带数据

### 实战相关
9. **渗透测试的流程？**
   - 前期交互、情报收集、威胁建模、漏洞分析、漏洞利用、后渗透、报告编写

10. **如何进行信息收集？**
    - 被动：WHOIS、DNS、子域名、搜索引擎、社交媒体、代码托管
    - 主动：端口扫描、服务识别、目录扫描、指纹识别、漏洞扫描

11. **SQL 注入如何绕 WAF？**
    - 大小写、双写、编码、注释、空格绕过、等价函数、HPP、分块传输、协议层绕过

12. **常见的中间件漏洞有哪些？**
    - Apache：解析漏洞、.htaccess
    - Nginx：解析漏洞、目录遍历
    - Tomcat：war 部署、PUT 上传、弱口令
    - JBoss：未授权访问、部署 war
    - WebLogic：反序列化、SSRF
    - Redis：未授权访问、写 webshell、写计划任务

---

## 七、学习建议

### 7.1 学习方法
1. **先开发后安全**：先学会 Web 开发，再学 Web 安全。不懂开发做安全，只会用工具，理解不了原理。

2. **原理 + 实践**：每个漏洞都要理解原理，然后动手实践。打靶场是最好的学习方式。

3. **从易到难**：先打 DVWA、皮卡丘等入门靶场，再打 CTF 题目，最后挖 SRC。

4. **多做笔记**：每个漏洞都要整理笔记，包括原理、利用方式、绕过技巧、防御方法。

5. **写 Writeup**：每做完一个题目或靶场，都写一篇 Writeup，既能巩固知识，又能积累作品集。

### 7.2 学习重点
- **漏洞原理**：深入理解每个漏洞的成因，而不只是会用工具
- **利用技巧**：掌握各种绕过技巧和利用方式
- **防御方法**：理解漏洞的防御方案，不能只懂攻击
- **工具使用**：熟练掌握 Burp Suite、SQLMap 等核心工具
- **代码审计**：具备一定的代码审计能力
- **业务逻辑**：关注业务逻辑漏洞，这是现在的重点

### 7.3 常见误区
- ❌ 只会用工具，不懂原理：工具只是辅助，原理才是根本
- ❌ 只学攻击，不学防御：攻击和防御是一体两面
- ❌ 只打 CTF，不关注实战：CTF 和实战有差距，都要接触
- ❌ 贪多嚼不烂：先把基础打牢，再学高级内容
- ❌ 不做笔记：好记性不如烂笔头
- ❌ 不写 Writeup：写 Writeup 是最好的巩固方式

### 7.4 职业发展
- **初级**：Web 安全工程师、渗透测试工程师、安全运维
- **中级**：高级渗透测试工程师、代码审计工程师、安全研究员
- **高级**：安全专家、安全架构师、技术负责人
- **专家**：首席安全官、安全研究员、漏洞挖掘专家

### 7.5 关注趋势
- 云原生安全
- API 安全
- 业务安全
- 移动安全
- IoT 安全
- AI 安全
- 零信任
- DevSecOps

---

> 💡 **Web 安全是入门最快、岗位最多的方向，但也是竞争最激烈的方向。打好基础，深入研究，才能脱颖而出！**
