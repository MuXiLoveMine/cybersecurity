# SQL 编程基础与安全学习资源

> 本文系统介绍 SQL 编程基础与数据库安全领域应用：SQL 在安全中的定位、SQL 编程基础（安全视角）、SQL 注入原理与防御、常用命令与工具、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的 SQL 示例脚本（basics.sql 和 security_cases.sql）。面向 Web 安全工程师与数据库管理员，全部内容从防御、授权测试和安全研究的正向角度出发。

---

## 目录

- [一、SQL 在网络安全中的定位](#一sql-在网络安全中的定位)
- [二、SQL 编程基础（安全视角）](#二sql-编程基础安全视角)
- [三、SQL 注入原理与防御](#三sql-注入原理与防御)
- [四、常用命令与安全审计](#四常用命令与安全审计)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、SQL 在网络安全中的定位

### 1.1 为什么安全从业者必须掌握 SQL

**SQL（Structured Query Language，结构化查询语言）** 是关系型数据库的标准操作语言。对于网络安全从业者来说，SQL 是理解数据库安全、SQL 注入漏洞原理与防御的**核心基础**。

| 优势 / 特点 | 说明 |
|------------|------|
| **数据的核心入口** | 几乎所有 Web 应用的数据都存在数据库中，SQL 是操作数据的语言 |
| **注入之王** | SQL 注入是 OWASP Top 10 常客，危害大、利用广 |
| **权限控制关键** | 数据库权限配置直接影响数据安全 |
| **审计溯源基础** | 日志审计、权限审计、数据泄露溯源都需要 SQL 能力 |
| **数据保护核心** | 加密、脱敏、备份恢复等数据安全措施都围绕数据库 |

> **安全视角的重要性**：
> - 作为**防御者**：必须理解 SQL 注入的原理，才能写出安全的代码、设计合理的权限、配置有效的 WAF 规则
> - 作为**渗透测试人员**：需要识别注入点、构造 Payload、掌握不同数据库的注入技巧
> - 作为**数据库管理员**：需要配置最小权限、审计用户行为、加固数据库安全

### 1.2 常见数据库类型对比

| 数据库 | 类型 | 默认端口 | 典型场景 | 安全关注点 |
|--------|------|---------|---------|-----------|
| **MySQL** | 开源关系型 | 3306 | Web 应用、电商、LAMP | UDF 提权、information_schema |
| **PostgreSQL** | 开源关系型 | 5432 | 企业应用、GIS | 功能强大、自定义函数多 |
| **SQL Server** | 商业关系型 | 1433 | 微软生态、企业级 | xp_cmdshell、CLR 集成 |
| **Oracle** | 商业关系型 | 1521 | 大型企业、金融 | 权限体系复杂、UTL_HTTP 等 |
| **SQLite** | 文件型数据库 | 无（文件） | 移动端、嵌入式、小型应用 | 文件权限、无用户管理 |
| **MongoDB** | NoSQL 文档型 | 27017 | 大数据、灵活结构 | NoSQL 注入、默认无认证 |
| **Redis** | NoSQL 键值型 | 6379 | 缓存、队列 | 未授权访问、主从复制 RCE |

> **安全提示**：不同数据库的 SQL 方言和注入技巧各有差异。掌握通用 SQL 语法后，需要了解目标数据库的特性函数、系统表、提权方法等。

### 1.3 安全领域的应用方向

| 方向 | SQL 的作用 | 典型场景 |
|------|-----------|---------|
| **Web 渗透测试** | 识别和利用 SQL 注入漏洞 | 联合查询注入、盲注、报错注入 |
| **数据库审计** | 检查配置和权限 | 用户权限审计、弱口令检查、日志审计 |
| **数据安全防护** | 设计安全的数据库架构 | 最小权限、数据加密、访问控制 |
| **应急响应** | 溯源和取证 | 日志分析、数据篡改溯源、权限变更审计 |
| **安全开发** | 编写安全的数据库操作代码 | 参数化查询、ORM 正确使用、输入验证 |
| **合规与审计** | 满足等保、GDPR 等合规要求 | 数据分级、操作审计、备份恢复验证 |

---

## 二、SQL 编程基础（安全视角）

### 2.1 SQL 语句分类

| 类别 | 全称 | 作用 | 代表命令 |
|------|------|------|---------|
| **DDL** | Data Definition Language | 数据定义：定义数据库结构 | CREATE、ALTER、DROP、TRUNCATE |
| **DML** | Data Manipulation Language | 数据操作：增删改查 | SELECT、INSERT、UPDATE、DELETE |
| **DCL** | Data Control Language | 数据控制：权限管理 | GRANT、REVOKE |
| **TCL** | Transaction Control Language | 事务控制 | COMMIT、ROLLBACK、SAVEPOINT |
| **DQL** | Data Query Language | 数据查询（有时单独分类） | SELECT |

### 2.2 DDL：数据定义语言

#### CREATE（创建）

```sql
-- 创建数据库
CREATE DATABASE myapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建索引（提升查询性能，注意安全：不要索引敏感字段）
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

> **安全提示**：
> - 密码必须存储哈希值，不能明文存储（`password_hash` 字段）
> - 合理使用索引提升性能，但不要过度索引（影响写入性能）
> - 敏感字段（如身份证、手机号）考虑加密存储

#### ALTER（修改）

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;

-- 修改列
ALTER TABLE users MODIFY COLUMN email VARCHAR(150) NOT NULL;

-- 删除列
ALTER TABLE users DROP COLUMN phone;

-- 添加约束
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE(email);
```

> **⚠️ 高风险警告**：ALTER TABLE 在大表上可能锁表，生产环境需谨慎操作，建议在维护窗口执行，并做好备份。

#### DROP（删除）

```sql
-- 删除表（结构和数据一起删）
DROP TABLE IF EXISTS temp_data;

-- 删除数据库
DROP DATABASE IF EXISTS old_database;

-- 删除索引
DROP INDEX idx_users_email ON users;
```

> **⚠️ 极高风险警告**：DROP 操作不可逆！执行前务必备份，建议先确认再确认。生产环境可以通过权限控制禁止 DROP 操作。

### 2.3 DML：数据操作语言

#### SELECT（查询）

```sql
-- 基本查询
SELECT id, username, email FROM users;

-- 所有列（不推荐生产环境使用，明确列名更安全高效）
SELECT * FROM users;

-- 条件查询
SELECT * FROM users WHERE role = 'admin';
SELECT * FROM users WHERE created_at > '2026-01-01';
SELECT * FROM users WHERE is_active = 1 AND role = 'user';
SELECT * FROM users WHERE role IN ('admin', 'editor');
SELECT * FROM users WHERE username LIKE '%test%';

-- 排序
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY role ASC, created_at DESC;

-- 限制数量（分页）
SELECT * FROM users ORDER BY id LIMIT 10;           -- 前 10 条
SELECT * FROM users ORDER BY id LIMIT 20, 10;       -- 第 21-30 条（MySQL）

-- 去重
SELECT DISTINCT role FROM users;
```

> **安全提示**：`SELECT *` 可能意外返回敏感字段（如 `password_hash`），生产环境应明确指定需要的列名，遵循最小化原则。

#### INSERT（插入）

```sql
-- 插入单行
INSERT INTO users (username, email, password_hash, role)
VALUES ('alice', 'alice@example.com', '$2b$12$...', 'admin');

-- 插入多行
INSERT INTO users (username, email, password_hash, role) VALUES
    ('bob', 'bob@example.com', '$2b$12$...', 'user'),
    ('charlie', 'charlie@example.com', '$2b$12$...', 'editor');

-- 从其他表插入
INSERT INTO users_backup SELECT * FROM users WHERE is_active = 0;
```

#### UPDATE（更新）

```sql
-- 更新数据（务必加 WHERE 条件！）
UPDATE users SET email = 'new_alice@example.com' WHERE id = 1;

-- 多列更新
UPDATE users SET role = 'editor', is_active = 1 WHERE username = 'bob';

-- 递增/递减
UPDATE users SET login_count = login_count + 1 WHERE id = 1;
```

> **⚠️ 极高风险警告**：UPDATE 语句如果忘记写 WHERE 条件，会更新全表！建议先 SELECT 确认条件，再执行 UPDATE。生产环境开启事务，确认无误后再 COMMIT。

#### DELETE（删除）

```sql
-- 删除数据（务必加 WHERE 条件！）
DELETE FROM users WHERE id = 100;

-- 删除多行
DELETE FROM users WHERE is_active = 0 AND created_at < '2025-01-01';

-- 清空表（快速，不记日志，不可恢复！）
TRUNCATE TABLE temp_data;
```

> **⚠️ 极高风险警告**：DELETE 无 WHERE 会删除全部数据！TRUNCATE 更危险，速度极快且通常无法回滚。删除操作前务必：1) 备份数据；2) 用 SELECT 验证 WHERE 条件；3) 开启事务确认后再提交。

### 2.4 聚合与分组

```sql
-- 聚合函数
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(DISTINCT role) AS role_count FROM users;
SELECT AVG(login_count) AS avg_logins FROM users;
SELECT SUM(login_count) AS total_logins FROM users;
SELECT MAX(created_at) AS latest_user FROM users;
SELECT MIN(created_at) AS earliest_user FROM users;

-- GROUP BY 分组
SELECT role, COUNT(*) AS user_count
FROM users
GROUP BY role
ORDER BY user_count DESC;

-- HAVING：分组后筛选（WHERE 是分组前筛选）
SELECT role, COUNT(*) AS cnt
FROM users
WHERE is_active = 1
GROUP BY role
HAVING COUNT(*) > 10
ORDER BY cnt DESC;
```

### 2.5 JOIN（连接查询）

假设有两张表：`users`（用户表）和 `orders`（订单表），`orders.user_id` 关联 `users.id`。

| 连接类型 | 说明 | 图示 |
|---------|------|------|
| **INNER JOIN** | 只返回两边都匹配的行 | 交集 |
| **LEFT JOIN** | 返回左表全部 + 右表匹配的行 | 左集 + 交集 |
| **RIGHT JOIN** | 返回右表全部 + 左表匹配的行 | 右集 + 交集 |
| **FULL OUTER JOIN** | 返回两边全部行（MySQL 不直接支持） | 并集 |

```sql
-- INNER JOIN：查询有订单的用户及其订单
SELECT u.username, o.order_no, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
ORDER BY o.amount DESC;

-- LEFT JOIN：查询所有用户，没有订单的也显示
SELECT u.username, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username
ORDER BY order_count DESC;

-- 自连接：连接同一张表
-- 假设有 employees 表，有 manager_id 字段
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### 2.6 子查询

```sql
-- WHERE 子查询：找出金额最高的订单的用户
SELECT username FROM users
WHERE id = (
    SELECT user_id FROM orders
    ORDER BY amount DESC LIMIT 1
);

-- IN 子查询：找出有订单的用户
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders);

-- EXISTS 子查询：存在性检查（通常比 IN 高效）
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- FROM 子查询（派生表）
SELECT avg_amount FROM (
    SELECT user_id, AVG(amount) AS avg_amount
    FROM orders GROUP BY user_id
) AS user_avg
WHERE avg_amount > 1000;
```

### 2.7 视图与索引

#### 视图（View）

```sql
-- 创建视图（虚拟表，基于查询结果）
CREATE VIEW active_users AS
SELECT id, username, email, role, created_at
FROM users
WHERE is_active = 1;

-- 使用视图（像表一样查询）
SELECT * FROM active_users WHERE role = 'admin';

-- 视图的安全意义：限制可见字段和行
-- 比如只让某个用户看活跃用户的非敏感字段
```

> **安全意义**：视图可以实现行级和列级的访问控制，隐藏敏感数据，是数据库安全的重要手段之一。

#### 索引（Index）

```sql
-- 普通索引
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 复合索引（最左前缀原则）
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- 查看索引
SHOW INDEX FROM orders;

-- 删除索引
DROP INDEX idx_orders_user_id ON orders;
```

> **性能与安全**：索引提升查询性能，但也会增加写入开销。安全角度，不要对加密字段或敏感字段建普通索引（可能泄露信息）。

---

## 三、SQL 注入原理与防御

### 3.1 SQL 注入是什么

**SQL 注入（SQL Injection）** 是一种代码注入攻击，攻击者通过在应用程序的输入中插入恶意 SQL 代码，从而操纵后端数据库执行非预期的操作。

#### 注入原理示例

```php
// 危险代码：直接拼接 SQL
$username = $_GET['username'];
$sql = "SELECT * FROM users WHERE username = '$username'";
$result = mysqli_query($conn, $sql);
```

正常输入：`alice`
```sql
SELECT * FROM users WHERE username = 'alice'
```

恶意输入：`' OR '1'='1`
```sql
SELECT * FROM users WHERE username = '' OR '1'='1'
-- 结果：返回所有用户数据！
```

更危险的输入：`'; DROP TABLE users; --`
```sql
SELECT * FROM users WHERE username = ''; DROP TABLE users; --'
-- 结果：users 表被删除！
```

### 3.2 SQL 注入类型

| 类型 | 说明 | 典型场景 | 利用难度 |
|------|------|---------|---------|
| **联合注入**（UNION） | 使用 UNION SELECT 合并查询结果获取数据 | 页面显示查询结果 | 低 |
| **报错注入** | 利用数据库错误信息获取数据 | 页面显示 SQL 错误 | 中 |
| **布尔盲注** | 根据页面真假判断数据（无显示无报错） | 页面只有两种状态 | 高 |
| **时间盲注** | 根据响应时间延迟判断数据 | 页面完全无差异 | 很高 |
| **堆叠注入** | 一次执行多条 SQL 语句 | 数据库支持多语句 | 中 |
| **带外注入**（OOB） | 通过 DNS/HTTP 请求带出数据 | 有出站连接权限 | 高 |
| **二次注入** | 数据存入数据库后在别处被取出执行 | 数据被其他功能使用 | 高 |

### 3.3 注入点识别

| 注入类型 | 特征 | 测试方法 |
|---------|------|---------|
| **数字型** | 参数是数字，如 `?id=1` | `?id=1'` 报错、`?id=1 and 1=1` 正常、`?id=1 and 1=2` 异常 |
| **字符型** | 参数是字符串，如 `?name=alice` | `?name=alice'` 报错、`?name=alice' and '1'='1` 正常 |
| **搜索型** | LIKE 查询，如搜索框 | 输入 `%` 返回全部、输入 `'` 报错 |
| **POST 注入** | 参数在请求体中 | Burp 抓包修改参数测试 |
| **Cookie 注入** | 参数在 Cookie 中 | 修改 Cookie 值测试 |
| **Header 注入** | 参数在 HTTP 头中 | 修改 User-Agent、Referer、X-Forwarded-For 等 |
| **ORDER BY 注入** | 排序参数可控 | `?sort=id desc` 看排序变化 |

### 3.4 SQL 注入防御方法

| 防御方法 | 说明 | 有效性 | 推荐度 |
|---------|------|--------|--------|
| **参数化查询（预编译）** | 使用 Prepared Statement，SQL 结构与数据分离 | ✅ 最佳 | ⭐⭐⭐⭐⭐ |
| **ORM 框架** | 使用成熟的 ORM（避免写原生 SQL） | ✅ 好 | ⭐⭐⭐⭐ |
| **输入验证** | 白名单验证输入格式（类型、长度、范围） | ⚠️ 辅助 | ⭐⭐⭐ |
| **输出编码** | 数据展示时编码转义 | ⚠️ 辅助 | ⭐⭐ |
| **最小权限** | 数据库账号只给必要权限 | ✅ 纵深防御 | ⭐⭐⭐⭐ |
| **WAF** | Web 应用防火墙 | ⚠️ 可绕过 | ⭐⭐⭐ |
| **存储过程** | 使用预定义的存储过程 | ⚠️ 写得不好也会有注入 | ⭐⭐ |
| **数据库防火墙** | 数据库层面的安全防护 | ✅ 企业级 | ⭐⭐⭐⭐ |

#### 参数化查询示例（核心防御）

```python
# 危险：字符串拼接
# cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")

# 安全：参数化查询
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

```java
// 危险：Statement
// Statement stmt = conn.createStatement();
// ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE username = '" + username + "'");

// 安全：PreparedStatement
PreparedStatement pstmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?"
);
pstmt.setString(1, username);
ResultSet rs = pstmt.executeQuery();
```

```javascript
// 危险：字符串拼接
// db.query(`SELECT * FROM users WHERE username = '${username}'`);

// 安全：参数化
db.query("SELECT * FROM users WHERE username = ?", [username]);
```

> **核心原则**：数据和 SQL 结构必须分离！参数化查询是防御 SQL 注入的最佳方法，因为数据库会把参数值永远当作数据处理，不会被解析为 SQL 代码。

### 3.5 安全编码最佳实践

1. **永远使用参数化查询**，不要拼接 SQL
2. **使用 ORM 框架**（如 SQLAlchemy、Hibernate、Prisma），减少手写 SQL
3. **最小权限原则**：应用数据库账号只给 SELECT/INSERT/UPDATE，不给 DROP/ALTER 权限
4. **禁止多语句执行**：配置数据库驱动不允许多语句执行，防堆叠注入
5. **输入验证**：使用白名单验证输入的类型、格式、长度
6. **错误信息不暴露**：生产环境不返回 SQL 错误详情给前端
7. **使用数据库账户分离**：读操作和写操作用不同账号
8. **敏感数据加密**：密码、身份证等敏感字段加密存储
9. **定期审计**：检查数据库权限、慢查询日志、错误日志
10. **WAF 辅助**：部署 WAF 作为额外防御层（但不能替代参数化查询）

---

## 四、常用命令与安全审计

### 4.1 MySQL 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `mysql` | 连接数据库 | `mysql -u root -p -h localhost` |
| `mysqldump` | 备份数据库 | `mysqldump -u root -p mydb > backup.sql` |
| `mysqladmin` | 管理工具 | `mysqladmin -u root -p status` |
| `SHOW DATABASES` | 列出数据库 | `SHOW DATABASES;` |
| `SHOW TABLES` | 列出表 | `SHOW TABLES;` |
| `DESCRIBE` | 查看表结构 | `DESCRIBE users;` |
| `SHOW GRANTS` | 查看权限 | `SHOW GRANTS FOR 'appuser'@'localhost';` |
| `CREATE USER` | 创建用户 | `CREATE USER 'app'@'localhost' IDENTIFIED BY 'StrongPass123!';` |
| `GRANT` | 授权 | `GRANT SELECT, INSERT ON mydb.* TO 'app'@'localhost';` |
| `REVOKE` | 撤销权限 | `REVOKE DROP ON mydb.* FROM 'app'@'localhost';` |
| `FLUSH PRIVILEGES` | 刷新权限 | `FLUSH PRIVILEGES;` |
| `SHOW PROCESSLIST` | 查看连接 | `SHOW PROCESSLIST;` |
| `information_schema` | 元数据数据库 | `SELECT table_name FROM information_schema.tables WHERE table_schema = 'mydb';` |

### 4.2 PostgreSQL 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `psql` | 连接数据库 | `psql -U postgres -d mydb` |
| `pg_dump` | 备份 | `pg_dump -U postgres mydb > backup.sql` |
| `\l` | 列出数据库 | psql 命令行内 |
| `\dt` | 列出表 | psql 命令行内 |
| `\d+ table` | 查看表结构 | psql 命令行内 |
| `\du` | 列出用户/角色 | psql 命令行内 |
| `\dp` | 查看权限 | psql 命令行内 |
| `CREATE ROLE` | 创建角色 | `CREATE ROLE appuser WITH LOGIN PASSWORD 'pass';` |
| `GRANT` | 授权 | `GRANT SELECT ON ALL TABLES IN SCHEMA public TO appuser;` |

### 4.3 SQLite 常用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `sqlite3` | 打开数据库 | `sqlite3 mydb.db` |
| `.tables` | 列出表 | sqlite3 命令行内 |
| `.schema` | 查看建表语句 | sqlite3 命令行内 |
| `.dump` | 导出数据库 | sqlite3 命令行内 |
| `.read` | 执行 SQL 文件 | sqlite3 命令行内 |
| `.quit` | 退出 | sqlite3 命令行内 |

> **安全提示**：SQLite 是文件型数据库，没有用户权限系统。安全依赖文件系统权限。确保 .db 文件不可通过 Web 直接下载，设置正确的文件权限。

### 4.4 数据库安全审计常用查询

```sql
-- MySQL：查看所有用户及其主机
SELECT user, host FROM mysql.user;

-- MySQL：查看用户权限
SHOW GRANTS FOR 'username'@'localhost';

-- MySQL：查看所有数据库的权限
SELECT * FROM mysql.db;

-- MySQL：查看有 SUPER 权限的用户（高权限）
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';

-- MySQL：查看有 FILE 权限的用户（可读写文件）
SELECT user, host FROM mysql.user WHERE File_priv = 'Y';

-- 查看当前用户
SELECT current_user();
SELECT user();

-- 查看数据库版本
SELECT version();

-- 查看数据库名
SELECT database();

-- information_schema 查询（MySQL）
-- 列出所有表
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_schema NOT IN ('information_schema', 'mysql', 'performance_schema');

-- 列出某表的列
SELECT column_name, data_type FROM information_schema.columns
WHERE table_schema = 'mydb' AND table_name = 'users';
```

### 4.5 数据库安全基线检查清单

| 检查项 | 说明 | 标准 |
|--------|------|------|
| **密码策略** | 强密码、定期更换 | 长度≥12，含大小写数字特殊字符 |
| **默认账户** | 禁用/删除默认账户 | root/admin 等默认账户应改密或禁用 |
| **最小权限** | 应用账号只给必要权限 | 不给 FILE、SUPER、PROCESS 等权限 |
| **网络访问** | 限制 IP 访问 | 不要 0.0.0.0 监听，用防火墙限制 |
| **加密传输** | SSL/TLS 连接 | 启用 SSL，禁止明文传输 |
| **数据加密** | 敏感字段加密 | 密码哈希、敏感字段加密 |
| **审计日志** | 开启审计 | 记录登录、查询、变更等操作 |
| **备份策略** | 定期备份并验证 | 定期备份，定期演练恢复 |
| **版本补丁** | 保持最新版本 | 及时安装安全补丁 |
| **删除测试库** | 删除 test 等测试库 | test、sample 等默认库应删除 |

---

## 五、2026 年免费学习资源

| 资源 | 类型 | 说明 | 链接/获取方式 |
|------|------|------|--------------|
| **SQLBolt** | 交互式教程 | 20 课左右，每课有讲解和在线练习，2-3 小时可入门 | [sqlbolt.com](https://sqlbolt.com/) |
| **sql-mother（SQL 母题）** | 闯关式教程 | 程序员鱼皮原创，30+ 关卡，闯关式 SQL 自学教程，带在线编辑器 | [github.com/liyupi/sql-mother](https://github.com/liyupi/sql-mother) |
| **PortSwigger Web Security Academy** | 实验室 | 免费 SQL 注入实验（15+ labs），涵盖联合注入、盲注、时间盲注、带外注入等 | [portswigger.net/web-security/sql-injection](https://portswigger.net/web-security/sql-injection) |
| **SQLZoo** | 交互式练习 | 经典的 SQL 交互式教程，从基础到进阶 | [sqlzoo.net](https://sqlzoo.net/) |
| **Mode SQL Tutorial** | 教程 | 面向数据分析的 SQL 教程，含大量实例 | [mode.com/sql-tutorial](https://mode.com/sql-tutorial/) |
| **W3Schools SQL** | 参考/教程 | 经典的 SQL 入门教程，简明扼要 | [w3schools.com/sql](https://www.w3schools.com/sql/) |
| **Hack The Box - SQL Injection** | 实验室 | HTB 平台有大量 SQL 注入相关的靶机和挑战 | [hackthebox.com](https://www.hackthebox.com/) |

> **2026 年时效性标注**：以上资源均为长期维护的官方或社区知名资源。PortSwigger 学院持续更新实验，SQLBolt 和 SQLZoo 是经典的入门学习资源，sql-mother 是国内热门的中文闯关式 SQL 学习项目。

---

## 六、2026 年推荐 GitHub 项目

| 项目 | Stars（约） | 说明 | 适用场景 |
|------|------------|------|---------|
| **liyupi/sql-mother** | 数千+ | 程序员鱼皮原创，免费的闯关式 SQL 自学教程网站，30+ 关卡，在线 SQL 编辑器 | SQL 入门，闯关练习 |
| **NeaByteLab/SQL-Injection-Manual** | 数百+ | 22 章 SQL 注入完整指南，覆盖 MySQL、PostgreSQL、MSSQL、Oracle、SQLite | SQL 注入系统学习 |
| **Yanyan-dd/TAT-web-securiey-lab** | 数百+ | 面向高校教学的 Web 安全实验平台，涵盖 SQL 注入、XSS、CSRF 等 | 教学实验平台 |
| **sqlmapproject/sqlmap** | 3万+ | 自动化 SQL 注入工具，支持多种数据库和注入技术 | 授权测试，自动化检测 |
| **OWASP/CheatSheetSeries** | 数万+ | OWASP 安全速查表，含 SQL 注入防御速查表 | 防御参考，开发规范 |
| **payloadbox/sql-injection-payload-list** | 数千+ | SQL 注入 Payload 列表，按数据库分类 | 安全研究，测试用例 |
| **shielder-io/whatwaf** | 数千+ | 检测和绕过 WAF 的工具 | WAF 检测与绕过研究 |

> **⚠️ 免责声明**：以上 GitHub 项目仅供学习研究使用。sqlmap 等自动化注入工具**仅限在完全授权的测试环境中使用**。未经授权对任何系统进行 SQL 注入测试可能违反法律。学习者应重点关注漏洞原理和防御方法。防御者可以使用这些工具在授权环境下验证自己的防护措施。

---

## 七、示例代码文件

`code/` 目录下包含两个 SQL 示例脚本（以 MySQL 语法为主，兼容大部分标准 SQL）：

| 文件 | 内容 | 运行方式 |
|------|------|---------|
| `basics.sql` | SQL 基础语法示例：DDL、DML、查询、聚合、连接、子查询 | MySQL: `mysql -u user -p < basics.sql`；SQLite: `sqlite3 test.db < basics.sql` |
| `security_cases.sql` | 安全案例集：注入点检测查询、参数化查询示例、数据库权限审计、安全审计查询 | 同上，或在数据库客户端中执行 |

### 7.1 basics.sql 内容概览

- DDL：数据库创建、表创建、索引
- DML：INSERT、SELECT、UPDATE、DELETE
- 查询进阶：WHERE、ORDER BY、LIMIT、DISTINCT
- 聚合函数：COUNT、SUM、AVG、MAX、MIN、GROUP BY、HAVING
- 连接查询：INNER JOIN、LEFT JOIN、RIGHT JOIN、自连接
- 子查询：WHERE 子查询、IN 子查询、EXISTS 子查询、FROM 子查询
- 视图与索引

### 7.2 security_cases.sql 内容概览

| 案例 | 功能 | 说明 |
|------|------|------|
| **SQL 注入点识别查询** | 展示不安全的拼接 SQL 与安全的参数化查询对比 | 理解注入原理与防御方法 |
| **数据库权限审计** | 查询用户权限、高权限账户、空密码账户 | 安全基线检查 |
| **敏感数据审计** | 查找明文密码、弱口令、敏感字段 | 数据安全检查 |
| **安全审计日志查询** | 登录审计、操作审计、异常查询检测 | 运维审计 |
| **数据库安全加固示例** | 安全用户创建、权限配置、视图隔离 | 防御实践 |

> **运行注意**：
> - 脚本使用标准 SQL 语法（MySQL 方言为主）
> - 建议在本地测试环境（如 Docker MySQL、SQLite）中运行
> - 权限审计相关查询需要高权限账户
> - 所有注入示例仅用于理解原理，请勿用于未授权的测试

---

## 附：优化后的提示词模板

```
# 角色
你是一名资深数据库安全与 SQL 注入专家，精通 SQL 注入原理、防御技术和数据库安全加固。

# 任务
请针对以下 SQL / 数据库安全任务给出完整方案：
【在此处填入具体任务，如"分析某应用的 SQL 注入风险并给出加固方案"】

# 输出要求
- 漏洞原理说明（攻击 + 防御双视角）
- SQL 代码示例（漏洞代码 + 修复代码对比）
- 检测方法（如何发现此类问题）
- 修复方案（多层次防御建议）
- 相关 CWE / OWASP 编号

# 约束
- 仅限防御、安全研究和授权测试场景
- 攻击代码仅用于原理说明，需做脱敏处理
- 必须给出对应的防御和修复方案
- 强调伦理与法律边界
- 注明适用的数据库类型（MySQL/PostgreSQL/MSSQL 等）
```

---

> **免责声明**：本文档所有内容仅用于学习、研究和授权环境下的安全测试与防御实践。任何未经授权的测试或攻击行为均属违法。读者应遵守所在地区法律法规，对自己的行为负责。
