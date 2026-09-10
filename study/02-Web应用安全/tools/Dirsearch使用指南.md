# Dirsearch 使用指南

> Dirsearch 是一款高效的 Web 目录/文件扫描工具，用于发现网站上的隐藏目录、文件和敏感路径。

---

## 目录

- [一、Dirsearch 简介](#一dirsearch-简介)
- [二、安装](#二安装)
- [三、基本使用](#三基本使用)
- [四、目标与字典](#四目标与字典)
- [五、扫描选项](#五扫描选项)
- [六、过滤与匹配](#六过滤与匹配)
- [七、请求配置](#七请求配置)
- [八、输出与报告](#八输出与报告)
- [九、高级用法](#九高级用法)
- [十、常用字典推荐](#十常用字典推荐)
- [十一、使用技巧](#十一使用技巧)

---

## 一、Dirsearch 简介

Dirsearch 是一款用 Python 编写的 Web 目录爆破工具。

**特点**：
- 速度快，多线程支持
- 支持多种 HTTP 方法
- 支持代理、Cookie、自定义 Header
- 支持多种状态码过滤
- 支持递归扫描
- 支持子目录爆破
- 支持多种格式报告输出
- 内置大量字典

**同类工具**：
- DirBuster（Java，图形化）
- gobuster（Go 语言，快）
- wfuzz（Web 应用模糊测试）
- dirb（C 语言，经典）

**官方仓库**：https://github.com/maurosoria/dirsearch

---

## 二、安装

### 2.1 方式一：克隆仓库

```bash
git clone https://github.com/maurosoria/dirsearch.git
cd dirsearch
pip3 install -r requirements.txt

# 运行
python3 dirsearch.py -u http://example.com
```

### 2.2 方式二：pip 安装

```bash
pip3 install dirsearch

# 运行
dirsearch -u http://example.com
```

### 2.3 Kali Linux

```bash
sudo apt-get install dirsearch
dirsearch -u http://example.com
```

### 2.4 Windows

1. 安装 Python 3
2. 下载源码或 pip 安装
3. 命令行运行

### 2.5 验证安装

```bash
dirsearch --version
dirsearch -h
```

---

## 三、基本使用

### 3.1 最简单的扫描

```bash
# 扫描单个 URL
dirsearch -u http://example.com

# 完整 URL（带路径）
dirsearch -u http://example.com/admin/
```

### 3.2 输出结果解读

```
[10:00:00] Starting:
[10:00:01] 200 -  1234B - /index.html
[10:00:01] 301 -   324B - /admin  ->  http://example.com/admin/
[10:00:01] 403 -   289B - /.htaccess
[10:00:02] 200 -  5678B - /login.php
[10:00:02] 404 -  1024B - /test
```

| 列 | 说明 |
|----|------|
| 时间 | 发现时间 |
| 状态码 | HTTP 状态码 |
| 大小 | 响应内容长度（字节） |
| 路径 | 发现的路径 |
| `->` | 重定向目标 |

---

## 四、目标与字典

### 4.1 指定目标

```bash
# 单个 URL
dirsearch -u http://example.com
dirsearch --url http://example.com

# 多个 URL（逗号分隔）
dirsearch -u http://example.com,http://test.com

# 从文件读取 URL 列表
dirsearch -l urls.txt
dirsearch --url-list=urls.txt
```

### 4.2 指定字典

```bash
# 指定字典文件
dirsearch -u http://example.com -w wordlist.txt
dirsearch -u http://example.com --wordlist=wordlist.txt

# 多个字典（逗号分隔）
dirsearch -u http://example.com -w dict1.txt,dict2.txt

# 不使用默认字典扩展名（只用字典原样）
dirsearch -u http://example.com --no-extension
```

### 4.3 字典扩展名

dirsearch 会自动为字典添加常见后缀（如 .php、.html 等）

```bash
# 指定扩展名
dirsearch -u http://example.com -e php
dirsearch -u http://example.com --extensions=php

# 多个扩展名
dirsearch -u http://example.com -e php,html,asp,aspx,jsp

# 指定扩展名列表文件
dirsearch -u http://example.com -E extensions.txt

# 不添加任何扩展名
dirsearch -u http://example.com -e ""
```

### 4.4 前缀/后缀

```bash
# 添加前缀
dirsearch -u http://example.com --prefixes=admin_,test_

# 添加后缀
dirsearch -u http://example.com --suffixes=.bak,.old,.swp
```

---

## 五、扫描选项

### 5.1 线程与速度

```bash
# 线程数（默认 25）
dirsearch -u http://example.com -t 50
dirsearch -u http://example.com --threads=100

# 延迟（秒，每个请求之间的间隔）
dirsearch -u http://example.com --delay=0.5

# 最大速率（每秒请求数）
dirsearch -u http://example.com --max-rate=100
```

### 5.2 递归扫描

```bash
# 递归扫描子目录
dirsearch -u http://example.com -r
dirsearch -u http://example.com --recursive

# 递归深度（默认 0 = 无限）
dirsearch -u http://example.com -r --recursion-depth=2

# 只递归指定状态码的目录
dirsearch -u http://example.com -r --recursion-status=200,301,403

# 强制递归（即使目录返回 403 也递归）
dirsearch -u http://example.com -r --force-recursive
```

### 5.3 子目录扫描

```bash
# 从指定子目录开始扫描
dirsearch -u http://example.com --subdirs=/admin,/backup

# 子目录列表文件
dirsearch -u http://example.com -S subdirs.txt
```

### 5.4 HTTP 方法

```bash
# GET 方法（默认）
dirsearch -u http://example.com -m GET

# HEAD 方法（更快，只看响应头）
dirsearch -u http://example.com -m HEAD

# POST 方法
dirsearch -u http://example.com -m POST
```

---

## 六、过滤与匹配

### 6.1 状态码过滤

```bash
# 包含指定状态码（只显示这些）
dirsearch -u http://example.com -i 200,301
dirsearch -u http://example.com --include-status=200,301

# 排除指定状态码
dirsearch -u http://example.com -x 404,403
dirsearch -u http://example.com --exclude-status=404,400,500

# 排除状态码 + 大小
dirsearch -u http://example.com --exclude-sizes=1234B,5678B

# 排除响应文本
dirsearch -u http://example.com --exclude-texts="Not Found"
```

### 6.2 响应大小过滤

```bash
# 只显示指定大小的响应
dirsearch -u http://example.com --include-sizes=1KB,2KB

# 排除指定大小
dirsearch -u http://example.com --exclude-sizes=1024B,2048B
```

### 6.3 响应内容匹配

```bash
# 包含指定文本
dirsearch -u http://example.com --include-text="admin"

# 排除指定文本
dirsearch -u http://example.com --exclude-text="404 Not Found"

# 正则匹配
dirsearch -u http://example.com --include-regex="admin|login"
dirsearch -u http://example.com --exclude-regex="error|not found"
```

### 6.4 响应长度对比

```bash
# 排除与 404 页面长度相同的响应
dirsearch -u http://example.com --exclude-response=notfound.html

# 采样 404 页面进行对比
dirsearch -u http://example.com --no-404-detector  # 禁用自动检测
```

---

## 七、请求配置

### 7.1 Cookie

```bash
# 设置 Cookie
dirsearch -u http://example.com --cookie="PHPSESSID=abc123; user=admin"
```

### 7.2 自定义 Header

```bash
# 单个 Header
dirsearch -u http://example.com -H "User-Agent: Mozilla/5.0"

# 多个 Header
dirsearch -u http://example.com -H "User-Agent: Mozilla/5.0" -H "X-Custom: test"

# 从文件读取 Header
dirsearch -u http://example.com --headers-file=headers.txt
```

### 7.3 User-Agent

```bash
# 自定义 UA
dirsearch -u http://example.com --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."

# 随机 UA
dirsearch -u http://example.com --random-user-agents
```

### 7.4 代理

```bash
# HTTP 代理
dirsearch -u http://example.com -p http://127.0.0.1:8080
dirsearch -u http://example.com --proxy=http://127.0.0.1:8080

# SOCKS 代理
dirsearch -u http://example.com --proxy=socks5://127.0.0.1:1080

# 代理认证
dirsearch -u http://example.com --proxy=user:pass@127.0.0.1:8080
```

### 7.5 认证

```bash
# HTTP Basic 认证
dirsearch -u http://example.com -q admin:password
dirsearch -u http://example.com --auth-type=basic --auth=admin:password

# Digest 认证
dirsearch -u http://example.com --auth-type=digest --auth=user:pass
```

### 7.6 超时与重试

```bash
# 连接超时（秒，默认 7.5）
dirsearch -u http://example.com --timeout=10

# 重试次数
dirsearch -u http://example.com --retries=3

# 重试间隔
dirsearch -u http://example.com --delay=1
```

### 7.7 跟随重定向

```bash
# 跟随重定向
dirsearch -u http://example.com -F
dirsearch -u http://example.com --follow-redirects

# 最大重定向次数
dirsearch -u http://example.com --max-redirects=5
```

### 7.8 SSL 配置

```bash
# 跳过 SSL 证书验证
dirsearch -u https://example.com -k
dirsearch -u https://example.com --no-cert-check
```

---

## 八、输出与报告

### 8.1 输出格式

```bash
# 简单文本报告
dirsearch -u http://example.com --simple-report=result.txt

# 纯文本报告
dirsearch -u http://example.com --plain-text-report=result.txt

# JSON 报告
dirsearch -u http://example.com --json-report=result.json

# XML 报告
dirsearch -u http://example.com --xml-report=result.xml

# CSV 报告
dirsearch -u http://example.com --csv-report=result.csv

# Markdown 报告
dirsearch -u http://example.com --markdown-report=result.md

# HTML 报告
dirsearch -u http://example.com --html-report=result.html

# 所有格式
dirsearch -u http://example.com --format=all -o result
```

### 8.2 输出目录

```bash
# 指定输出目录
dirsearch -u http://example.com -o ./output/
dirsearch -u http://example.com --output=./output/

# 自动生成报告（默认在 reports 目录）
dirsearch -u http://example.com
```

### 8.3 输出样式

```bash
# 无颜色输出
dirsearch -u http://example.com --no-color

# 安静模式（只显示结果）
dirsearch -u http://example.com -q
dirsearch -u http://example.com --quiet-mode

# 完整输出
dirsearch -u http://example.com --full-url
```

---

## 九、高级用法

### 9.1 自定义 404 检测

```bash
# 禁用 404 自动检测
dirsearch -u http://example.com --no-404-detector

# 自定义 404 页面样本
dirsearch -u http://example.com --exclude-response=/path/to/404.html
```

### 9.2 跳过某些路径

```bash
# 跳过指定路径
dirsearch -u http://example.com --skip-on-status=401,403

# 跳过已扫描的 URL
dirsearch -u http://example.com --skip-urls=skip.txt
```

### 9.3 扫描优化

```bash
# 仅扫描指定扩展名的路径
dirsearch -u http://example.com -e php --only-selected

# 不使用默认字典（只用自定义字典）
dirsearch -u http://example.com -w mydict.txt --no-default-wordlist
```

### 9.4 从 Burp 日志导入

```bash
# 使用 Burp 日志中的请求
dirsearch -u http://example.com --burp-log=burp.log
```

---

## 十、常用字典推荐

### 10.1 dirsearch 内置字典

dirsearch 自带的字典在 `db/` 目录下：

```
db/
├── dicc.txt              # 默认字典
├── directories.txt       # 目录字典
├── files.txt             # 文件字典
├── extensions.txt        # 常见扩展名
├── subdomains.txt        # 子域名字典
└── user-agents.txt       # User-Agent 列表
```

### 10.2 常用字典资源

| 字典 | 说明 | 地址 |
|------|------|------|
| **SecLists** | 最全面的安全字典集合 | https://github.com/danielmiessler/SecLists |
| **fuzzdb** | 模糊测试数据库 | https://github.com/fuzzdb-project/fuzzdb |
| **dirbuster wordlists** | DirBuster 自带字典 | OWASP 项目 |
| **robots disallow** | robots.txt 收集 | - |

**SecLists 目录字典**：
```
SecLists/Discovery/Web-Content/
├── common.txt                 # 通用目录
├── common.php.txt             # PHP 专用
├── common-api-security.txt    # API 安全
├── CGI.txt                    # CGI 相关
├── apache.txt                 # Apache
├── nginx.txt                  # Nginx
├── iis.txt                    # IIS
├── wordpress.fuzz.txt         # WordPress
├── phpMyAdmin.fuzz.txt        # phpMyAdmin
├── backup.txt                 # 备份文件
└── ...
```

### 10.3 字典选择建议

- **初步探测**：用小字典（common.txt，几千条）
- **深入扫描**：用大字典（directory-list-2.3-medium.txt）
- **特定 CMS**：用对应 CMS 的字典（WordPress、Dedecms 等）
- **备份文件**：专门的备份文件字典（.bak、.swp、.zip、.sql 等）

---

## 十一、使用技巧

### 11.1 常用扫描命令

```bash
# 1. 基础扫描（默认字典 + php 扩展）
dirsearch -u http://example.com -e php

# 2. 快速扫描（大线程）
dirsearch -u http://example.com -e php,html,js -t 100

# 3. 递归扫描
dirsearch -u http://example.com -e php -r --recursion-depth=2

# 4. 只看 200 和 301
dirsearch -u http://example.com -i 200,301

# 5. 排除 404 和 403
dirsearch -u http://example.com -x 404,403,500

# 6. 带 Cookie 扫描（登录后）
dirsearch -u http://example.com --cookie="session=abc123"

# 7. 指定字典
dirsearch -u http://example.com -w /path/to/bigdict.txt -e php

# 8. 使用代理（通过 Burp）
dirsearch -u http://example.com -p http://127.0.0.1:8080

# 9. 批量扫描
dirsearch -l urls.txt -e php -t 50

# 10. 导出报告
dirsearch -u http://example.com -e php --json-report=result.json
```

### 11.2 扫描策略

**第一层：快速探测**
```bash
dirsearch -u http://example.com -e php,html -t 100 --random-user-agents
```
目的：快速发现明显的目录和文件

**第二层：深入扫描**
```bash
dirsearch -u http://example.com -w bigdict.txt -e php,html,bak,zip,sql -t 50 -r
```
目的：使用大字典 + 多种扩展名 + 递归扫描

**第三层：针对性扫描**
```bash
# CMS 扫描
dirsearch -u http://example.com -w wordpress.txt

# 备份文件扫描
dirsearch -u http://example.com -w backup.txt -e bak,swp,zip,rar,sql

# API 扫描
dirsearch -u http://example.com/api/ -w api.txt -e json
```

### 11.3 注意事项

1. **合法授权**：只扫描授权的目标
2. **控制速度**：生产环境降低线程，避免影响服务
3. **配合代理**：使用 Burp 代理查看和分析请求
4. **多次扫描**：不同字典、不同时间扫描，结果可能不同
5. **验证结果**：扫描结果需要人工验证，排除误报
6. **关注特殊文件**：
   - 备份文件：.bak、.swp、.zip、.rar、.tar.gz
   - 配置文件：.env、config.php、web.config
   - 管理后台：admin、manager、login
   - 编辑器残留：~、.swo、.swn
   - 版本控制：.git、.svn、.hg

### 11.4 常见问题

**Q: 扫描结果都是 404？**
- 检查 URL 是否正确
- 检查是否需要登录（加 Cookie）
- 检查是否被 WAF 拦截（用代理看看响应）
- 尝试更换 User-Agent

**Q: 扫描太慢？**
- 增加线程数（-t 100）
- 使用更小的字典
- 减少扩展名
- 使用 HEAD 方法（更快，但可能不准）

**Q: 误报太多？**
- 使用 `-x` 排除常见误报状态码
- 使用 `--exclude-sizes` 排除相同大小的响应
- 使用 `--exclude-texts` 排除特定内容

---

> **延伸学习**：目录扫描是信息收集的重要环节。建议多准备几套字典，针对不同类型的站点使用不同的字典和策略。配合 Burp Suite 的爬虫功能，可以更全面地发现网站内容。
