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

---

## 十二、自定义字典制作

### 12.1 字典制作工具

```bash
# 1. cewl - 从网站内容生成字典
cewl http://target.com -w target_words.txt -m 5
# -m 5: 最小单词长度 5

# 2. TIDOS-Framework - 综合字典生成
python3 tidos.py -u http://target.com

# 3. 自定义字典合并与去重
cat dict1.txt dict2.txt dict3.txt | sort -u > merged.txt

# 4. 基于规则生成变体字典
# 使用 hashcat 规则生成密码/目录变体
hashcat --stdout base.txt -r /usr/share/hashcat/rules/best64.rule

# 5. 自定义字典脚本
python3 -c "
import itertools
# 生成常见后台路径变体
base = ['admin', 'manage', 'system', 'config', 'backup', 'test', 'debug', 'api']
exts = ['.php', '.html', '.jsp', '.asp', '.aspx', '.bak', '.old', '.zip', '.txt']
for b in base:
    for e in exts:
        print(f'/{b}{e}')
    print(f'/{b}/')
" > custom_dict.txt
```

### 12.2 针对性字典制作

```bash
# 1. CMS 专属字典
# WordPress
dirsearch -u http://target.com -w /usr/share/SecLists/Discovery/Web-Content/wordpress.txt

# 2. 基于技术栈的字典
# PHP 项目
dirsearch -u http://target.com -e php,inc,bak,old,swp -w php_dirs.txt

# Java 项目
dirsearch -u http://target.com -e jsp,jspx,war,xml,properties -w java_dirs.txt

# 3. 备份文件专用字典
# 生成备份文件字典
python3 -c "
import datetime
year = datetime.date.today().year
for y in range(year-5, year+1):
    for m in range(1, 13):
        for ext in ['zip','rar','tar.gz','bak','sql','sql.gz']:
            print(f'/backup_{y}{m:02d}.{ext}')
            print(f'/db_{y}{m:02d}.{ext}')
" > backup_dict.txt

# 4. API 端点字典
cat > api_dict.txt << 'EOF'
/api/v1/
/api/v2/
/api/users
/api/admin
/api/config
/swagger-ui.html
/swagger-resources
/v2/api-docs
/graphql
/api/auth
/api/upload
/api/download
EOF
```

### 12.3 字典优化策略

```
字典优化原则：
1. 长度优先：短字典先行，长字典后行
2. 频率排序：常用路径排在前面
3. 去重处理：合并多字典时去除重复
4. 针对性过滤：根据技术栈过滤无关路径
5. 动态扩展：从已发现路径推导新路径

优化脚本示例：
# 根据已发现的目录推测隐藏路径
# 发现 /admin/login.php → 猜测 /admin/config.php, /admin/users.php
# 发现 /api/v1/users → 猜测 /api/v2/users, /api/v1/admin
```

---

## 十三、过滤器配置详解

### 13.1 extensions（扩展名配置）

```bash
# 根据目标技术栈选择扩展名

# PHP 站点
dirsearch -u http://target.com -e php,php5,php7,php8,inc,phtml,phar

# Java 站点
dirsearch -u http://target.com -e jsp,jspx,war,do,action,properties,xml

# ASP.NET 站点
dirsearch -u http://target.com -e aspx,asp,ashx,asmx,config,bak

# 静态站点
dirsearch -u http://target.com -e html,htm,js,css,json,xml,txt

# 备份文件
dirsearch -u http://target.com -e bak,old,swp,swo,swn,zip,rar,tar.gz,7z,sql

# 配置文件
dirsearch -u http://target.com -e env,ini,conf,cfg,xml,yml,yaml,toml,properties

# 通用多扩展名
dirsearch -u http://target.com -e php,html,js,json,bak,zip,txt,old
```

### 13.2 threads/retries 配置

```bash
# 线程数调整策略
# 低并发（避免 WAF）：5-10 线程
dirsearch -u http://target.com -t 5 --delay=0.5

# 中等并发（常规测试）：25-50 线程
dirsearch -u http://target.com -t 25

# 高并发（无防护目标）：100-200 线程
dirsearch -u http://target.com -t 100

# 重试次数配置
# 增加重试次数以提高准确性
dirsearch -u http://target.com --retries=3 --timeout=10

# 配合延迟使用
dirsearch -u http://target.com -t 10 --delay=0.2 --retries=2
```

---

## 十四、递归扫描深度配置

```bash
# 递归扫描深度控制

# 深度1（推荐，平衡速度和覆盖）
dirsearch -u http://target.com -r --recursion-depth=1

# 深度2（更全面但更慢）
dirsearch -u http://target.com -r --recursion-depth=2

# 深度3+（非常慢，需长时间运行）
dirsearch -u http://target.com -r --recursion-depth=3

# 指定递归状态码
dirsearch -u http://target.com -r --recursion-status=200,301,302,403

# 强制递归（403 也递归）
dirsearch -u http://target.com -r --force-recursive

# 子目录扫描组合
dirsearch -u http://target.com \
  --subdirs=/admin,/backup,/api,/config,/test,/dev,/old \
  -r --recursion-depth=2 \
  -e php,bak,zip
```

---

## 十五、子域名枚举

### 15.1 使用 dirsearch 进行子域名爆破

```bash
# 子域名爆破（使用 - 子域名格式字典）
dirsearch -u http://target.com --subdomains -w subdomains.txt

# 常见子域名字典
# SecLists 子域名字典位置：
# /usr/share/SecLists/Discovery/DNS/

dirsearch -u http://target.com \
  --subdomains \
  -w /usr/share/SecLists/Discovery/DNS/subdomains-top1million-20000.txt
```

### 15.2 其他子域名收集工具

```bash
# Sublist3r - 搜索引擎枚举
python3 sublist3r.py -d target.com -o subdomains.txt

# Amass - 深度子域名收集
amass enum -d target.com -o amass_results.txt

# Subfinder - 快速被动收集
subfinder -d target.com -o subfinder_results.txt

# DNS 字典爆破
python3 dnspop.py -d target.com

# 组合收集后合并去重
cat sublist3r.txt amass.txt subfinder.txt | sort -u > all_subdomains.txt

# 验证子域名存活
cat all_subdomains.txt | while read sub; do
    if curl -s -o /dev/null -w "%{http_code}" "http://$sub" | grep -q "200\|301\|302\|403"; then
        echo "$sub" >> alive_subs.txt
    fi
done
```

---

## 十六、CDN/WAF 绕过技巧

### 16.1 WAF 检测与绕过

```bash
# 1. 检测 WAF
wafw00f http://target.com

# 2. 降低扫描速度绕过 WAF
dirsearch -u http://target.com -t 5 --delay=2 --random-user-agents

# 3. 使用随机 User-Agent
dirsearch -u http://target.com --random-user-agents -t 10

# 4. 使用多个代理轮换
# 配置代理池文件
cat > proxy_list.txt << 'EOF'
http://proxy1:8080
http://proxy2:8080
socks5://proxy3:1080
EOF

# 5. 自定义 Header 绕过
dirsearch -u http://target.com \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
  -H "Accept: text/html,application/xhtml+xml" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  -H "X-Forwarded-For: 127.0.0.1" \
  --delay=0.5 -t 10

# 6. 使用 HEAD 方法（减少流量）
dirsearch -u http://target.com -m HEAD -t 10

# 7. 使用 Cookie 绕过认证检查
dirsearch -u http://target.com \
  --cookie="session=abc123; token=xyz789; auth=true" \
  -e php -t 25
```

### 16.2 CDN 绕过（直连真实 IP）

```bash
# 1. 通过子域名找真实 IP
# 很多子域名未配置 CDN
dig dev.target.com
dig test.target.com
dig internal.target.com

# 2. 通过历史 DNS 记录
# 使用 SecurityTrails、ViewDNS 等
# https://viewdns.info/iphistory/?domain=target.com

# 3. 通过 SSL 证书
# https://crt.sh/?q=target.com
# 查看 SSL 证书关联的 IP

# 4. 邮件服务 IP
# 注册账户接收邮件，查看邮件头中的源 IP

# 5. 全网扫描
# 使用 fscan 或 zmap 对 IP 段进行反查
# 确认哪个 IP 上运行了目标网站

# 6. 直连扫描
# 获取真实 IP 后直接扫描
dirsearch -u http://真实IP -H "Host: target.com" -e php
```

---

## 十七、结果导出与分析

### 17.1 结果导出

```bash
# JSON 报告（便于程序解析）
dirsearch -u http://target.com -e php --json-report=result.json

# 分析 JSON 结果
python3 -c "
import json
with open('result.json') as f:
    data = json.load(f)
for item in data:
    if item['status'] == 200:
        print(f\"[200] {item['url']} - {item['length']}B\")
"

# CSV 报告（便于表格分析）
dirsearch -u http://target.com -e php --csv-report=result.csv

# Markdown 报告
dirsearch -u http://target.com -e php --markdown-report=result.md
```

### 17.2 结果自动化分析

```bash
# 1. 提取所有 200 状态码路径
grep "200" result.txt | awk '{print $NF}'

# 2. 提取可能有趣的文件
grep -E "\.(env|config|backup|sql|bak|swp|zip|rar|git|svn)" result.txt

# 3. 按状态码分组统计
grep -oP '\d{3}' result.txt | sort | uniq -c | sort -rn

# 4. 提取重定向目标
grep "301\|302" result.txt | grep -oP 'http[s]?://\S+'

# 5. 提取大文件（可能是备份）
grep -E "^\[.*\] \d{3} -\s+\d{5,}B" result.txt

# 6. 自动验证结果
cat result.txt | while read line; do
    url=$(echo $line | grep -oP 'http\S+')
    if [ ! -z "$url" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
        echo "[$status] $url"
    fi
done
```

---

## 十八、与其他工具联动

### 18.1 与 ffuf 联动

```bash
# 使用 dirsearch 快速扫描后用 ffuf 深入
# 1. dirsearch 快速发现目录
dirsearch -u http://target.com -e php -t 100 -o results/

# 2. 对发现的目录用 ffuf 深入扫描
for dir in $(grep "200\|301" results/*.txt | grep -oP '/\w+/'); do
    ffuf -u http://target.com${dir}FUZZ -w big_dict.txt -mc 200,301,302,403
done

# ffuf 优势：
# - 支持更灵活的模糊位置
# - 可以从 stdout 实时过滤
# - 支持递归
# - 支持多种匹配模式
```

### 18.2 与 gobuster 联动

```bash
# gobuster 目录扫描
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt -t 50

# gobuster 子域名扫描
gobuster dns -d target.com -w subdomains.txt -i

# gobuster vhost 虚拟主机扫描
gobuster vhost -u http://target.com -w vhosts.txt

# 联动策略：
# 1. gobuster 快速子域名发现
gobuster dns -d target.com -w subdomains.txt -i -o subs.txt
# 2. 对每个子域名运行 dirsearch
for sub in $(cat subs.txt); do
    dirsearch -u http://$sub -e php,html -t 25
done
```

### 18.3 与 Nmap 联动

```bash
# 1. Nmap 发现 Web 服务
nmap -sV -p 80,443,8080,8443 10.0.0.0/24 -oG web_hosts.gnmap

# 2. 提取 Web 服务地址
grep "80/open\|443/open\|8080/open" web_hosts.gnmap | awk '{print $2}'

# 3. 对每个 Web 服务运行 dirsearch
for host in $(grep "80/open\|443/open" web_hosts.gnmap | awk '{print $2}'); do
    dirsearch -u http://$host -e php -t 25 -o /results/$host/
done
```

---

## 十九、真实渗透测试与 CTF 案例

### 19.1 案例一：发现备份文件导致数据泄露

```
场景：对某企业网站进行授权渗透测试

步骤：
1. 基础扫描发现网站使用 PHP
   dirsearch -u http://target.com -e php -t 50

2. 发现 /backup/ 目录返回 403
3. 针对备份目录使用备份字典
   dirsearch -u http://target.com/backup/ -e zip,rar,tar.gz,sql,bak -t 25

4. 发现 /backup/site_2024.zip 返回 200
5. 下载备份文件，发现：
   - config.php（数据库凭据）
   - .env 文件（API 密钥）
   - 数据库导出文件（用户数据）

教训：备份文件不应存放在 Web 可访问目录
```

### 19.2 案例二：通过 .git 泄露获取源码

```
场景：CTF 竞赛

步骤：
1. 目录扫描发现 /.git/ 目录
   dirsearch -u http://target.com -e "" --no-extension

2. 使用 GitHack 恢复源码
   python3 GitHack.py http://target.com/.git/

3. 查看源码发现：
   - 硬编码的数据库密码
   - 内部 API 接口
   - 隐藏的管理后台路径

4. 进一步利用：
   - 访问管理后台
   - 使用泄露的凭据登录数据库
   - 获取 flag

教训：版本控制目录不应暴露在 Web 目录
```

### 19.3 案例三：API 端点发现

```
场景：对 REST API 进行安全测试

步骤：
1. 使用 API 字典扫描
   dirsearch -u http://target.com/api/ -e json -w api_dict.txt -t 25

2. 发现以下端点：
   /api/v1/users     → 200（用户列表）
   /api/v1/admin     → 401（需认证）
   /api/v1/debug     → 200（调试信息）
   /api/v2/          → 200（新版本 API）

3. 测试越权：
   /api/v1/users/1   → 返回用户1的信息
   /api/v1/users/2   → 返回用户2的信息（水平越权）

4. 发现 /api/v1/debug 泄露：
   - 服务器内部路径
   - 环境变量
   - 数据库连接信息

教训：API 端点需要严格的认证和授权控制
```

### 19.4 案例四：WAF 绕过扫描

```
场景：目标部署了 WAF，常规扫描被拦截

步骤：
1. 常规扫描被 WAF 拦截
   dirsearch -u http://target.com -e php -t 50
   → 大量 403 响应

2. 降低速度 + 随机 UA
   dirsearch -u http://target.com -e php -t 5 --delay=2 --random-user-agents

3. 添加伪造 Header
   dirsearch -u http://target.com -e php -t 5 \
     -H "X-Forwarded-For: 127.0.0.1" \
     -H "X-Real-IP: 127.0.0.1" \
     --delay=1

4. 使用代理池轮换 IP
   dirsearch -u http://target.com -e php -t 10 \
     --proxy=http://proxy1:8080 --delay=1

5. 成功发现隐藏路径：
   /admin_panel/  → 301
   /secret_api/   → 200

教训：WAF 绕过需要耐心，低速扫描是关键
```
