# UPDATE

> **分类**：更新
> **说明**：更新表中的数据

---

## 语法

```sql
UPDATE table SET col1 = val1, col2 = val2 WHERE condition;
```

## 注意

一定要加 WHERE 条件，否则会更新所有行！

## 安全

先 SELECT 确认条件，再 UPDATE / 使用事务回滚

## 示例代码

```sql
-- 更新单条记录
UPDATE users
SET age = 26
WHERE id = 1;

-- 更新多个字段
UPDATE users
SET name = 'Alice Smith',
    email = 'alice.smith@example.com',
    age = age + 1
WHERE id = 1;

-- 批量更新
UPDATE users
SET city = 'Beijing'
WHERE city = 'beijing';

-- 使用表达式更新
UPDATE products
SET price = price * 1.1  -- 涨价10%
WHERE category = 'electronics';

-- 关联更新（多表更新）
UPDATE users u
JOIN orders o ON u.id = o.user_id
SET u.total_spent = u.total_spent + o.amount
WHERE o.status = 'completed';

-- CASE WHEN 条件更新
UPDATE users
SET level = CASE
    WHEN score >= 1000 THEN 'gold'
    WHEN score >= 500 THEN 'silver'
    ELSE 'bronze'
END;

-- 递增/递减
UPDATE counters SET count = count + 1 WHERE id = 1;
UPDATE inventory SET stock = stock - 1 WHERE product_id = 100;

-- ===== 安全提醒 =====
-- 1. 永远先 SELECT 确认条件
SELECT * FROM users WHERE age > 60;
-- 确认无误后再执行 UPDATE
-- UPDATE users SET status = 'retired' WHERE age > 60;

-- 2. 使用事务（可以回滚）
-- START TRANSACTION;
-- UPDATE users SET salary = salary * 1.1;
-- 检查影响行数和结果
-- COMMIT;  -- 或 ROLLBACK;

-- 3. 使用 LIMIT 限制更新数量（MySQL）
UPDATE users SET status = 'inactive'
WHERE last_login < '2023-01-01'
LIMIT 100;
```
