# JOIN

> **分类**：连接查询
> **说明**：多表连接查询

---

## 语法

```sql
SELECT ... FROM table1 JOIN table2 ON condition;
```

## 连接类型

INNER JOIN / LEFT JOIN / RIGHT JOIN / FULL JOIN / CROSS JOIN

## 区别

INNER: 只返回匹配的行\nLEFT: 返回左表全部+右表匹配的\nRIGHT: 返回右表全部+左表匹配的\nFULL: 返回两表全部

## 示例代码

```sql
-- 准备数据
-- users 表: id, name, email
-- orders 表: id, user_id, amount, status

-- ===== INNER JOIN（内连接，只返回匹配的） =====
SELECT u.name, o.amount, o.status
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 简写 JOIN = INNER JOIN
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;

-- ===== LEFT JOIN（左连接，左表全部返回） =====
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- 没有订单的用户也会显示，amount 为 NULL

-- LEFT JOIN + WHERE 右表为 NULL（找左表中不匹配的）
SELECT u.name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
-- 查询没有下过订单的用户

-- ===== RIGHT JOIN（右连接，右表全部返回） =====
SELECT u.name, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- ===== FULL OUTER JOIN（全连接，两表全部返回） =====
-- MySQL 不直接支持，可用 LEFT JOIN UNION RIGHT JOIN
SELECT u.name, o.amount FROM users u LEFT JOIN orders o ON u.id = o.user_id
UNION
SELECT u.name, o.amount FROM users u RIGHT JOIN orders o ON u.id = o.user_id;

-- ===== 多表连接 =====
SELECT u.name, p.name AS product_name, o.amount
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.status = 'completed';

-- ===== 自连接（表自己连接自己） =====
-- 员工表，有 manager_id 指向自己的 id
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- ===== CROSS JOIN（笛卡尔积） =====
-- 返回两表所有组合，慎用！
SELECT * FROM users CROSS JOIN products;

-- ===== USING 简化（连接列名相同时） =====
SELECT u.name, o.amount
FROM users u
JOIN orders o USING (user_id);  -- 等价于 ON u.user_id = o.user_id

-- ===== NATURAL JOIN（自然连接，自动匹配所有同名列） =====
-- 不推荐，可能有意想不到的结果
SELECT * FROM users NATURAL JOIN orders;
```
