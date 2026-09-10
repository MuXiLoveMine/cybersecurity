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
