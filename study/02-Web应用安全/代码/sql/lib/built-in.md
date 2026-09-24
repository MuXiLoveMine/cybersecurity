# 内置函数 - SQL 常用函数

> SQL 标准和常用数据库的内置函数，包括字符串、数值、日期、聚合等。

---

## 一、字符串函数

### 1.1 基本操作

```sql
-- 字符串拼接
-- MySQL
SELECT CONCAT('Hello', ' ', 'World');    -- 'Hello World'
SELECT CONCAT_WS(',', 'a', 'b', 'c');    -- 'a,b,c'（带分隔符，跳过 NULL）

-- PostgreSQL
SELECT 'Hello' || ' ' || 'World';        -- 'Hello World'
SELECT CONCAT('Hello', ' ', 'World');

-- SQL Server
SELECT 'Hello' + ' ' + 'World';          -- 'Hello World'
SELECT CONCAT('Hello', ' ', 'World');

-- Oracle
SELECT 'Hello' || ' ' || 'World' FROM dual;
SELECT CONCAT('Hello', 'World') FROM dual;  -- 只接受两个参数
```

### 1.2 长度与截取

```sql
-- 字符串长度
-- MySQL: CHAR_LENGTH（字符数）, LENGTH（字节数）
SELECT CHAR_LENGTH('Hello World');       -- 11
SELECT LENGTH('Hello World');            -- 11

-- PostgreSQL
SELECT CHAR_LENGTH('Hello World');       -- 11
SELECT LENGTH('Hello World');            -- 11

-- SQL Server
SELECT LEN('Hello World');               -- 11
SELECT DATALENGTH('Hello World');        -- 11（字节数）

-- Oracle
SELECT LENGTH('Hello World') FROM dual;  -- 11

-- 子串截取
-- SUBSTRING(str, start, length)  - 标准 SQL
SELECT SUBSTRING('Hello World', 1, 5);   -- 'Hello'（注意：SQL 从 1 开始）
SELECT SUBSTRING('Hello World', 7);      -- 'World'

-- MySQL
SELECT SUBSTRING('Hello World', 1, 5);
SELECT SUBSTR('Hello World', 1, 5);      -- 简写
SELECT LEFT('Hello World', 5);           -- 'Hello'（左 N 个字符）
SELECT RIGHT('Hello World', 5);          -- 'World'（右 N 个字符）
SELECT MID('Hello World', 7, 5);         -- 'World'
```

### 1.3 查找与替换

```sql
-- 查找位置（从 1 开始，0 表示未找到）
-- MySQL: LOCATE
SELECT LOCATE('World', 'Hello World');    -- 7
SELECT LOCATE('l', 'Hello World', 5);     -- 10（从位置 5 开始找）

-- PostgreSQL: POSITION
SELECT POSITION('World' IN 'Hello World');  -- 7

-- SQL Server: CHARINDEX
SELECT CHARINDEX('World', 'Hello World');   -- 7

-- Oracle: INSTR
SELECT INSTR('Hello World', 'World') FROM dual;  -- 7

-- 替换
SELECT REPLACE('Hello World', 'World', 'SQL');  -- 'Hello SQL'

-- 大小写转换
SELECT UPPER('hello');       -- 'HELLO'
SELECT LOWER('WORLD');       -- 'world'
SELECT UCASE('hello');       -- 'HELLO'（MySQL）
SELECT LCASE('WORLD');       -- 'world'（MySQL）

-- 去除空格
SELECT TRIM('  hello  ');         -- 'hello'（两端）
SELECT LTRIM('  hello');          -- 'hello'（左端）
SELECT RTRIM('hello  ');          -- 'hello'（右端）

-- 填充
SELECT LPAD('42', 5, '0');        -- '00042'（左填充）
SELECT RPAD('42', 5, '*');        -- '42***'（右填充）

-- 重复
SELECT REPEAT('ab', 3);           -- 'ababab'

-- 反转
SELECT REVERSE('hello');          -- 'olleh'
```

---

## 二、数值函数

### 2.1 数学运算

```sql
-- 基本运算
SELECT 10 + 5;    -- 15
SELECT 10 - 5;    -- 5
SELECT 10 * 5;    -- 50
SELECT 10 / 5;    -- 2.0
SELECT 10 % 3;    -- 1（取模）
SELECT MOD(10, 3);  -- 1

-- 绝对值
SELECT ABS(-10);        -- 10

-- 四舍五入
SELECT ROUND(3.14159);      -- 3
SELECT ROUND(3.14159, 2);   -- 3.14
SELECT ROUND(123.45, -1);   -- 120（十位）

-- 向上/向下取整
SELECT CEIL(3.1);     -- 4
SELECT CEILING(3.1);  -- 4（SQL Server）
SELECT FLOOR(3.9);    -- 3

-- 截断小数
SELECT TRUNCATE(3.14159, 2);  -- 3.14（MySQL）
SELECT TRUNC(3.14159, 2);     -- 3.14（Oracle/PG）

-- 幂运算
SELECT POWER(2, 10);    -- 1024
SELECT POW(2, 10);      -- 1024（MySQL）

-- 平方根
SELECT SQRT(16);        -- 4

-- 随机数
-- MySQL
SELECT RAND();               -- 0-1 之间的随机浮点数
SELECT FLOOR(RAND() * 100);  -- 0-99 随机整数

-- PostgreSQL
SELECT RANDOM();             -- 0-1 之间

-- SQL Server
SELECT RAND();               -- 0-1 之间

-- Oracle
SELECT DBMS_RANDOM.VALUE FROM dual;
```

### 2.2 类型转换

```sql
-- 字符串转数字
SELECT CAST('123' AS INT);           -- 123
SELECT CAST('3.14' AS DECIMAL(5,2)); -- 3.14

-- 数字转字符串
SELECT CAST(123 AS CHAR(10));        -- '123'

-- MySQL 简写
SELECT CONVERT('123', SIGNED);       -- 123
SELECT CONVERT(123, CHAR);           -- '123'

-- 字符串转日期
SELECT CAST('2024-01-15' AS DATE);
SELECT CAST('2024-01-15 14:30:00' AS DATETIME);

-- PostgreSQL
SELECT '123'::INTEGER;               -- 123（类型转换简写）
```

---

## 三、日期时间函数

### 3.1 获取当前时间

```sql
-- 当前日期时间
-- MySQL
SELECT NOW();                  -- '2024-01-15 14:30:00'
SELECT CURRENT_TIMESTAMP;      -- 同上
SELECT CURDATE();              -- '2024-01-15'
SELECT CURTIME();              -- '14:30:00'
SELECT SYSDATE();              -- 执行时的时间（NOW() 是语句开始时）

-- PostgreSQL
SELECT NOW();
SELECT CURRENT_TIMESTAMP;
SELECT CURRENT_DATE;
SELECT CURRENT_TIME;

-- SQL Server
SELECT GETDATE();
SELECT CURRENT_TIMESTAMP;
SELECT GETUTCDATE();

-- Oracle
SELECT SYSDATE FROM dual;
SELECT CURRENT_TIMESTAMP FROM dual;
SELECT SYSTIMESTAMP FROM dual;
```

### 3.2 日期运算

```sql
-- 日期加减
-- MySQL
SELECT DATE_ADD('2024-01-15', INTERVAL 7 DAY);       -- 加 7 天
SELECT DATE_SUB('2024-01-15', INTERVAL 1 MONTH);     -- 减 1 月
SELECT DATE_ADD(NOW(), INTERVAL 1 HOUR);             -- 加 1 小时
SELECT '2024-01-15' + INTERVAL 7 DAY;                -- 简写

-- PostgreSQL
SELECT '2024-01-15'::DATE + INTERVAL '7 days';
SELECT NOW() + INTERVAL '1 month';
SELECT NOW() - INTERVAL '3 hours';

-- 日期差
-- MySQL
SELECT DATEDIFF('2024-01-20', '2024-01-15');         -- 5（天）
SELECT TIMESTAMPDIFF(HOUR, '2024-01-01', '2024-01-02');  -- 24（小时）

-- PostgreSQL
SELECT '2024-01-20'::DATE - '2024-01-15'::DATE;      -- 5
SELECT EXTRACT(EPOCH FROM ('2024-01-02' - '2024-01-01')) / 3600;  -- 小时差

-- Oracle
SELECT TO_DATE('2024-01-20', 'YYYY-MM-DD') - TO_DATE('2024-01-15', 'YYYY-MM-DD') 
FROM dual;  -- 5
```

### 3.3 日期提取

```sql
-- 提取日期各部分
-- MySQL
SELECT YEAR('2024-01-15');      -- 2024
SELECT MONTH('2024-01-15');     -- 1
SELECT DAY('2024-01-15');       -- 15
SELECT HOUR('14:30:00');        -- 14
SELECT MINUTE('14:30:00');      -- 30
SELECT SECOND('14:30:45');      -- 45
SELECT DAYOFWEEK('2024-01-15'); -- 2 (1=周日, 2=周一...)
SELECT WEEK('2024-01-15');      -- 第几周

-- EXTRACT（标准 SQL）
SELECT EXTRACT(YEAR FROM '2024-01-15');   -- 2024
SELECT EXTRACT(MONTH FROM '2024-01-15');  -- 1
SELECT EXTRACT(DAY FROM '2024-01-15');    -- 15
SELECT EXTRACT(HOUR FROM '14:30:00');     -- 14

-- 日期格式化
-- MySQL: DATE_FORMAT
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d');           -- '2024-01-15'
SELECT DATE_FORMAT(NOW(), '%Y年%m月%d日');
SELECT DATE_FORMAT(NOW(), '%H:%i:%s');           -- '14:30:00'

-- PostgreSQL: TO_CHAR
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD');
SELECT TO_CHAR(NOW(), 'HH24:MI:SS');

-- Oracle: TO_CHAR
SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') FROM dual;
```

---

## 四、聚合函数

```sql
-- COUNT - 计数
SELECT COUNT(*) FROM users;              -- 总行数
SELECT COUNT(column_name) FROM users;    -- 非 NULL 值的数量
SELECT COUNT(DISTINCT city) FROM users;  -- 不同城市的数量

-- SUM - 求和
SELECT SUM(amount) FROM orders;
SELECT SUM(price * quantity) FROM order_items;

-- AVG - 平均值
SELECT AVG(price) FROM products;

-- MAX / MIN - 最大/最小值
SELECT MAX(price) FROM products;
SELECT MIN(created_at) FROM users;

-- GROUP_CONCAT - 分组拼接字符串（MySQL）
SELECT department, GROUP_CONCAT(name SEPARATOR ', ') 
FROM employees 
GROUP BY department;
-- 结果: 每个部门的员工名用逗号分隔

-- STRING_AGG（PostgreSQL / SQL Server）
SELECT department, STRING_AGG(name, ', ')
FROM employees
GROUP BY department;

-- LISTAGG（Oracle）
SELECT department, LISTAGG(name, ', ') WITHIN GROUP (ORDER BY name)
FROM employees
GROUP BY department;

-- 聚合 + 条件
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) AS active_count,
    AVG(CASE WHEN age > 18 THEN age END) AS adult_avg_age
FROM users;
```

---

## 五、条件函数

### 5.1 IF / CASE

```sql
-- IF（MySQL）
SELECT name, IF(score >= 60, '及格', '不及格') AS result
FROM students;

-- CASE 表达式（标准 SQL）
SELECT 
    name,
    score,
    CASE 
        WHEN score >= 90 THEN '优秀'
        WHEN score >= 80 THEN '良好'
        WHEN score >= 60 THEN '及格'
        ELSE '不及格'
    END AS grade
FROM students;

-- CASE 简单形式
SELECT 
    status,
    CASE status
        WHEN 0 THEN '禁用'
        WHEN 1 THEN '启用'
        WHEN 2 THEN '待审核'
        ELSE '未知'
    END AS status_text
FROM users;

-- COALESCE - 返回第一个非 NULL 值
SELECT COALESCE(phone, email, '无联系方式') AS contact
FROM users;

-- NULLIF - 如果两值相等返回 NULL，否则返回第一个
SELECT NULLIF(price, 0)  -- price 为 0 时返回 NULL
FROM products;

-- IFNULL（MySQL）/ ISNULL（SQL Server）/ NVL（Oracle）
SELECT IFNULL(phone, '无') FROM users;    -- MySQL
SELECT ISNULL(phone, '无') FROM users;    -- SQL Server
SELECT NVL(phone, '无') FROM dual;        -- Oracle
```

---

## 六、安全相关内容

### 6.1 SQL 注入

```sql
-- ===== 危险：字符串拼接导致 SQL 注入 =====
-- 假设应用中这样拼接：
-- sql = "SELECT * FROM users WHERE username = '" + username + "'"
-- 攻击者输入：' OR '1'='1
-- 实际执行的 SQL：
SELECT * FROM users WHERE username = '' OR '1'='1';
-- 结果：返回所有用户

-- ===== 更严重的注入 =====
-- 输入：'; DROP TABLE users; --
SELECT * FROM users WHERE username = ''; DROP TABLE users; --';

-- ===== 防御：参数化查询 =====
-- 在应用代码中使用预处理语句/参数绑定
-- 例如在 Python 中：
-- cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
-- SQL 中用 ? 或 :name 等占位符

-- ===== 不能参数化的部分（白名单验证）=====
-- 表名、列名、ORDER BY 方向等不能参数化
-- 必须在应用层做白名单验证

-- 例如：排序字段必须是白名单中的列
-- 允许的列: id, name, created_at
-- 不在白名单中则使用默认值
```

### 6.2 密码存储

```sql
-- ===== 错误的密码存储方式 =====
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL  -- ❌ 明文存储
);

INSERT INTO users (username, password) VALUES ('admin', 'admin123');

-- ===== 不推荐：MD5 =====
INSERT INTO users (username, password) 
VALUES ('admin', MD5('admin123'));  -- ❌ 太快，易彩虹表攻击

-- ===== 也不推荐：SHA1 + 盐 =====
INSERT INTO users (username, password, salt) 
VALUES ('admin', SHA1(CONCAT(salt, 'admin123')), 'randomsalt');

-- ===== 推荐：bcrypt =====
-- 注意：SQL 中通常不直接计算 bcrypt
-- 在应用层计算后存储哈希
-- bcrypt 自动包含盐和成本因子

-- 存储格式示例: $2y$10$...
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL  -- 存储 bcrypt 哈希
);

-- 验证时：取出哈希，在应用层用 password_verify() 等函数验证
-- 不要在 SQL 中比较密码哈希
-- 正确的做法：
-- 1. SELECT password_hash FROM users WHERE username = ?
-- 2. 在应用层用 password_verify(input_password, stored_hash) 验证
```

### 6.3 权限与安全函数

```sql
-- ===== MySQL =====
-- 创建用户
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'strong_password';

-- 授予权限（最小权限原则）
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'appuser'@'localhost';
-- 不要给 ALL PRIVILEGES

-- 撤销权限
REVOKE DELETE ON mydb.* FROM 'appuser'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- ===== PostgreSQL =====
CREATE USER appuser WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE mydb TO appuser;
GRANT USAGE ON SCHEMA public TO appuser;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO appuser;

-- ===== 防止 SQL 注入的数据库层措施 =====
-- 1. 最小权限原则：应用账号只有必要的权限
-- 2. 禁止应用账号执行 DROP, ALTER, CREATE 等
-- 3. 禁用 FILE 权限（防止读写文件）
-- 4. 存储过程不能完全防止注入
```

### 6.4 注入攻击常见类型

```sql
-- ===== 1. 基于 UNION 的注入 =====
-- 原查询: SELECT id, name FROM products WHERE category = 'input'
-- 攻击: ' UNION SELECT username, password FROM users -- 
SELECT id, name FROM products WHERE category = '' UNION SELECT username, password FROM users -- ';

-- 防御：列数、类型要匹配

-- ===== 2. 布尔盲注 =====
-- 攻击: 通过页面差异判断条件真假
-- AND 1=1  -> 正常
-- AND 1=2  -> 错误/无结果
SELECT * FROM products WHERE id = 1 AND 1=1;  -- 有结果
SELECT * FROM products WHERE id = 1 AND 1=2;  -- 无结果

-- 可用于逐字符猜解数据
-- AND ASCII(SUBSTRING(database(),1,1)) > 97  -> 猜第一个字符的 ASCII 码

-- ===== 3. 时间盲注 =====
-- 攻击: 通过响应时间判断
-- AND SLEEP(5)  -> 响应延迟 5 秒
SELECT * FROM products WHERE id = 1 AND SLEEP(5);

-- ===== 4. 报错注入 =====
-- 攻击: 触发数据库错误，错误信息中包含数据
-- MySQL 中使用 AND extractvalue(1, concat(0x7e, version(), 0x7e))
-- 错误信息会返回数据库版本

-- ===== 5. 堆叠查询 =====
-- 攻击: 用分号分隔执行多条语句
-- ; DROP TABLE users; -- 
-- 注意：PHP 的 mysql_query 不支持，但 mysqli_multi_query 支持
```

---

## 七、常用函数速查

| 功能 | MySQL | PostgreSQL | SQL Server | Oracle |
|------|-------|-----------|------------|--------|
| 字符串拼接 | `CONCAT()` | `\|\|` / `CONCAT()` | `+` / `CONCAT()` | `\|\|` |
| 子串 | `SUBSTRING()` | `SUBSTRING()` | `SUBSTRING()` | `SUBSTR()` |
| 字符串长度 | `CHAR_LENGTH()` | `CHAR_LENGTH()` | `LEN()` | `LENGTH()` |
| 查找位置 | `LOCATE()` | `POSITION()` | `CHARINDEX()` | `INSTR()` |
| 替换 | `REPLACE()` | `REPLACE()` | `REPLACE()` | `REPLACE()` |
| 当前时间 | `NOW()` | `NOW()` | `GETDATE()` | `SYSDATE` |
| 日期格式化 | `DATE_FORMAT()` | `TO_CHAR()` | `FORMAT()` | `TO_CHAR()` |
| 转数字 | `CAST()` | `CAST()` | `CAST()` | `TO_NUMBER()` |
| 空值处理 | `IFNULL()` | `COALESCE()` | `ISNULL()` | `NVL()` |
| 条件判断 | `IF()` / `CASE` | `CASE` | `CASE` | `CASE` |
