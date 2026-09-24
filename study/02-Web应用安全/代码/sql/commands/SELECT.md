# SELECT

> **分类**：查询
> **说明**：从数据库中查询数据

---

## 语法

```sql
SELECT column1, column2 FROM table WHERE condition ORDER BY col LIMIT n;
```

## 子句顺序

SELECT / FROM / WHERE / GROUP BY / HAVING / ORDER BY / LIMIT

## 常用函数

COUNT / SUM / AVG / MAX / MIN / CONCAT / LENGTH / UPPER / LOWER

## 示例代码

```sql
-- 基本查询
SELECT * FROM users;
SELECT name, email FROM users;

-- 去重
SELECT DISTINCT city FROM users;

-- WHERE 条件
SELECT * FROM users WHERE age >= 18;
SELECT * FROM users WHERE city = 'Beijing' AND age < 30;
SELECT * FROM users WHERE city IN ('Beijing', 'Shanghai', 'Guangzhou');
SELECT * FROM users WHERE age BETWEEN 18 AND 30;

-- 模糊查询
SELECT * FROM users WHERE name LIKE '张%';   -- 以张开头
SELECT * FROM users WHERE name LIKE '%明%';  -- 包含明
SELECT * FROM users WHERE name LIKE '_伟%';  -- 第二个字是伟

-- ORDER BY 排序
SELECT * FROM users ORDER BY age ASC;        -- 升序（默认）
SELECT * FROM users ORDER BY age DESC;       -- 降序
SELECT * FROM users ORDER BY city, age DESC; -- 多字段排序

-- LIMIT 限制数量
SELECT * FROM users LIMIT 10;                 -- 前10条
SELECT * FROM users LIMIT 10 OFFSET 20;      -- 第21-30条（分页）
SELECT * FROM users LIMIT 20, 10;            -- MySQL 写法，同上面

-- 别名
SELECT name AS 姓名, age AS 年龄 FROM users;
SELECT u.name, u.email FROM users u;          -- 表别名

-- 聚合函数
SELECT COUNT(*) AS total FROM users;
SELECT SUM(score) AS total_score FROM students;
SELECT AVG(age) AS avg_age FROM users;
SELECT MAX(age) AS max_age, MIN(age) AS min_age FROM users;

-- GROUP BY 分组
SELECT city, COUNT(*) AS count FROM users GROUP BY city;
SELECT department, AVG(salary) AS avg_salary FROM employees GROUP BY department;

-- HAVING 分组后过滤
SELECT city, COUNT(*) AS cnt 
FROM users 
GROUP BY city 
HAVING cnt > 100;

-- 字符串函数
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;
SELECT UPPER(name), LOWER(email) FROM users;
SELECT LENGTH(name), SUBSTRING(name, 1, 3) FROM users;

-- 时间函数
SELECT NOW();                  -- 当前日期时间
SELECT CURDATE();              -- 当前日期
SELECT YEAR(birthday), MONTH(birthday), DAY(birthday) FROM users;
SELECT DATEDIFF(NOW(), birthday) AS days FROM users;
SELECT DATE_FORMAT(created_at, '%Y-%m-%d') FROM users;

-- CASE WHEN
SELECT name, age,
    CASE
        WHEN age < 18 THEN '未成年'
        WHEN age < 60 THEN '成年'
        ELSE '老年'
    END AS age_group
FROM users;

-- JOIN 连接
SELECT u.name, o.order_id, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN（左连接，左表全部，右表匹配）
SELECT u.name, o.order_id
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- RIGHT JOIN / FULL JOIN
-- 子查询
SELECT name FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- UNION（合并两个查询，自动去重）
SELECT name FROM table1
UNION
SELECT name FROM table2;
```
