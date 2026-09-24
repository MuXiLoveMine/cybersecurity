# INSERT

> **分类**：插入
> **说明**：向表中插入数据

---

## 语法

```sql
INSERT INTO table (col1, col2) VALUES (val1, val2);
```

## 方式

VALUES 单条/多条 / SELECT 插入查询结果 / ON DUPLICATE KEY UPDATE

## 示例代码

```sql
-- 插入单条数据
INSERT INTO users (name, email, age)
VALUES ('Alice', 'alice@example.com', 25);

-- 插入多条数据
INSERT INTO users (name, email, age)
VALUES 
    ('Bob', 'bob@example.com', 30),
    ('Charlie', 'charlie@example.com', 35),
    ('Diana', 'diana@example.com', 28);

-- 插入所有列（不指定列名，但不推荐）
INSERT INTO users
VALUES (1, 'Eve', 'eve@example.com', 22, 'Beijing');

-- 从另一个表插入数据
INSERT INTO users_backup (name, email, age)
SELECT name, email, age FROM users WHERE age > 30;

-- 插入时忽略重复（MySQL）
INSERT IGNORE INTO users (email, name)
VALUES ('alice@example.com', 'Alice2');

-- 插入或更新（MySQL，存在则更新）
INSERT INTO users (email, name, age)
VALUES ('alice@example.com', 'Alice', 26)
ON DUPLICATE KEY UPDATE name = VALUES(name), age = VALUES(age);

-- PostgreSQL 写法
-- INSERT INTO users (email, name, age)
-- VALUES ('alice@example.com', 'Alice', 26)
-- ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name, age = EXCLUDED.age;

-- 获取刚插入的自增ID
INSERT INTO users (name, email) VALUES ('test', 'test@example.com');
SELECT LAST_INSERT_ID();  -- MySQL
-- SELECT SCOPE_IDENTITY();  -- SQL Server
-- RETURNING id;  -- PostgreSQL

-- 批量插入性能优化
-- 尽量使用多值 INSERT，而不是循环单条 INSERT
```
