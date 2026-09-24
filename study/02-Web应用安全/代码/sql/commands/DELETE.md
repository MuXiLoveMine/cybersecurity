# DELETE

> **分类**：删除
> **说明**：删除表中的数据

---

## 语法

```sql
DELETE FROM table WHERE condition;
```

## 注意

一定要加 WHERE 条件，否则会删除所有数据！

## 相关

TRUNCATE TABLE - 清空表（更快，不可恢复）\nDROP TABLE - 删除表

## 示例代码

```sql
-- 删除指定行
DELETE FROM users WHERE id = 1;

-- 按条件删除
DELETE FROM users WHERE age < 18;
DELETE FROM users WHERE status = 'inactive' AND last_login < '2023-01-01';

-- 删除重复数据（保留最小 ID）
DELETE u1 FROM users u1
JOIN users u2 ON u1.email = u2.email AND u1.id > u2.id;

-- LIMIT 限制删除数量（MySQL）
DELETE FROM logs
WHERE created_at < '2023-01-01'
ORDER BY id
LIMIT 1000;

-- ===== 安全提醒 =====
-- 1. 永远先 SELECT 确认条件
SELECT * FROM users WHERE age > 100;
-- 确认无误后再删除
-- DELETE FROM users WHERE age > 100;

-- 2. 使用事务（可以回滚）
-- START TRANSACTION;
-- DELETE FROM orders WHERE status = 'cancelled';
-- SELECT ROW_COUNT();  -- 检查删除行数
-- COMMIT;  -- 或 ROLLBACK;

-- 3. 软删除（更安全，用标记字段）
-- 不物理删除，而是标记为已删除
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL;
UPDATE users SET deleted_at = NOW() WHERE id = 1;
-- 查询时过滤
SELECT * FROM users WHERE deleted_at IS NULL;

-- ===== TRUNCATE =====
-- 清空整个表（不可恢复，更快）
-- TRUNCATE TABLE logs;
-- 注意：TRUNCATE 是 DDL，不是 DML，无法回滚，会重置自增ID

-- ===== DROP =====
-- 删除整个表（结构和数据都没了）
-- DROP TABLE users;
-- DROP TABLE IF EXISTS users;  -- 存在才删

-- 对比：
-- DELETE: DML，可回滚，可加 WHERE，不会重置自增，触发表行级触发器
-- TRUNCATE: DDL，不可回滚，清空整表，重置自增，不触发行级触发器
-- DROP: DDL，删除整个表结构和数据
```
