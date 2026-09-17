-- query_examples.sql
-- MySQL 查询示例汇总
-- 使用前先导入 init.sql: mysql -u root -p < init.sql
-- 执行: mysql -u root -p webapp < query_examples.sql

USE webapp;

-- =============================================
-- 一、基础查询
-- =============================================

-- 1. 查询所有用户
SELECT * FROM users;

-- 2. 查询指定列
SELECT id, username, email FROM users;

-- 3. 使用别名
SELECT username AS '用户名', email AS '邮箱', age AS '年龄' FROM users;

-- 4. 去重
SELECT DISTINCT city FROM users;
SELECT DISTINCT gender FROM users;

-- =============================================
-- 二、条件查询（WHERE）
-- =============================================

-- 5. 精确匹配
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE username = 'admin';

-- 6. 比较运算符
SELECT * FROM users WHERE age > 25;
SELECT * FROM users WHERE age >= 25;
SELECT * FROM users WHERE age < 30;
SELECT * FROM users WHERE age <= 30;
SELECT * FROM users WHERE age != 25;

-- 7. 逻辑运算符
SELECT * FROM users WHERE age > 20 AND gender = 'male';
SELECT * FROM users WHERE city = '北京' OR city = '上海';
SELECT * FROM users WHERE NOT status = 0;

-- 8. BETWEEN AND（范围查询）
SELECT * FROM users WHERE age BETWEEN 25 AND 30;
SELECT * FROM users WHERE age NOT BETWEEN 20 AND 30;

-- 9. IN（指定集合）
SELECT * FROM users WHERE city IN ('北京', '上海', '广州');
SELECT * FROM users WHERE age IN (25, 28, 30);
SELECT * FROM users WHERE city NOT IN ('北京', '上海');

-- 10. LIKE（模糊查询）
-- % 匹配任意多个字符，_ 匹配单个字符
SELECT * FROM users WHERE username LIKE 'a%';       -- 以 a 开头
SELECT * FROM users WHERE username LIKE '%a%';      -- 包含 a
SELECT * FROM users WHERE email LIKE '%@example.com';  -- 以 @example.com 结尾
SELECT * FROM users WHERE username LIKE '___';      -- 恰好 3 个字符

-- 11. NULL 判断
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;

-- =============================================
-- 三、排序（ORDER BY）
-- =============================================

-- 12. 升序排序（默认 ASC）
SELECT * FROM users ORDER BY age ASC;
SELECT * FROM users ORDER BY age;

-- 13. 降序排序
SELECT * FROM users ORDER BY age DESC;

-- 14. 多字段排序
SELECT * FROM users ORDER BY gender ASC, age DESC;
SELECT * FROM users ORDER BY city ASC, age ASC;

-- =============================================
-- 四、限制数量（LIMIT）
-- =============================================

-- 15. 前 N 条
SELECT * FROM users LIMIT 5;

-- 16. 分页：从第 M 条开始，取 N 条
SELECT * FROM users LIMIT 0, 5;   -- 第 1 页，每页 5 条
SELECT * FROM users LIMIT 5, 5;   -- 第 2 页，每页 5 条
SELECT * FROM users LIMIT 10, 5;  -- 第 3 页，每页 5 条

-- 17. LIMIT ... OFFSET 写法
SELECT * FROM users LIMIT 5 OFFSET 5;  -- 同上第 2 页

-- =============================================
-- 五、聚合函数
-- =============================================

-- 18. COUNT 统计数量
SELECT COUNT(*) AS '总用户数' FROM users;
SELECT COUNT(email) AS '有邮箱的用户数' FROM users;

-- 19. SUM 求和
SELECT SUM(total_amount) AS '订单总金额' FROM orders;

-- 20. AVG 平均值
SELECT AVG(age) AS '平均年龄' FROM users;

-- 21. MAX / MIN 最大最小
SELECT MAX(age) AS '最大年龄', MIN(age) AS '最小年龄' FROM users;
SELECT MAX(price) AS '最贵商品价格' FROM products;
SELECT MIN(price) AS '最便宜商品价格' FROM products;

-- =============================================
-- 六、分组查询（GROUP BY）
-- =============================================

-- 22. 按性别分组统计
SELECT gender, COUNT(*) AS '人数'
FROM users
GROUP BY gender;

-- 23. 按城市分组，统计人数和平均年龄
SELECT city, COUNT(*) AS '人数', AVG(age) AS '平均年龄'
FROM users
GROUP BY city
ORDER BY 人数 DESC;

-- 24. 按用户分组，统计订单数和消费总额
SELECT u.username, COUNT(o.id) AS '订单数', SUM(o.total_amount) AS '消费总额'
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY 消费总额 DESC;

-- 25. HAVING 过滤分组结果
-- 统计人数大于1的城市
SELECT city, COUNT(*) AS num
FROM users
GROUP BY city
HAVING num > 1
ORDER BY num DESC;

-- =============================================
-- 七、联表查询（JOIN）
-- =============================================

-- 26. 内连接：查询有订单的用户及其订单
SELECT u.username, o.order_no, o.total_amount, o.status
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 27. 左连接：所有用户及其订单（没有订单的用户也显示）
SELECT u.username, o.order_no, o.total_amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- 28. 右连接：所有订单及其用户
SELECT u.username, o.order_no, o.total_amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- 29. 三表连接：查询订单详情（用户 + 订单 + 商品）
SELECT 
    o.order_no,
    u.username,
    p.name AS product_name,
    oi.quantity,
    oi.price,
    o.total_amount
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;

-- =============================================
-- 八、子查询
-- =============================================

-- 30. 查询年龄大于平均年龄的用户
SELECT username, age
FROM users
WHERE age > (SELECT AVG(age) FROM users);

-- 31. 查询有订单的用户
SELECT * FROM users
WHERE id IN (SELECT DISTINCT user_id FROM orders);

-- 32. 查询最贵的商品
SELECT * FROM products
WHERE price = (SELECT MAX(price) FROM products);

-- 33. EXISTS 子查询
SELECT * FROM users
WHERE EXISTS (SELECT 1 FROM orders WHERE orders.user_id = users.id);

-- =============================================
-- 九、常用函数
-- =============================================

-- 34. 字符串函数
SELECT 
    username,
    UPPER(username) AS upper_name,
    LOWER(username) AS lower_name,
    LENGTH(username) AS len,
    CONCAT(username, ' - ', email) AS user_info
FROM users;

-- 35. 数值函数
SELECT 
    price,
    ROUND(price, 0) AS rounded,
    CEIL(price) AS ceil_price,
    FLOOR(price) AS floor_price
FROM products;

-- 36. 日期函数
SELECT 
    created_at,
    DATE(created_at) AS date_only,
    YEAR(created_at) AS year,
    MONTH(created_at) AS month,
    DAY(created_at) AS day,
    DATEDIFF(NOW(), created_at) AS days_ago
FROM orders;

-- 37. 条件函数
SELECT 
    username,
    age,
    IF(age >= 30, '中年', '青年') AS age_group,
    IFNULL(email, '未填写邮箱') AS email_status,
    CASE gender
        WHEN 'male' THEN '男'
        WHEN 'female' THEN '女'
        ELSE '未知'
    END AS gender_text
FROM users;

-- =============================================
-- 十、综合查询练习
-- =============================================

-- 38. 查询消费金额最高的前 3 名用户
SELECT 
    u.username,
    COUNT(o.id) AS order_count,
    SUM(o.total_amount) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
ORDER BY total_spent DESC
LIMIT 3;

-- 39. 查询每个城市的平均年龄和人数
SELECT 
    city,
    COUNT(*) AS total,
    AVG(age) AS avg_age,
    SUM(CASE WHEN gender = 'male' THEN 1 ELSE 0 END) AS male_count,
    SUM(CASE WHEN gender = 'female' THEN 1 ELSE 0 END) AS female_count
FROM users
GROUP BY city
ORDER BY total DESC;

-- 40. 查询每个订单的商品数量
SELECT 
    o.order_no,
    COUNT(oi.id) AS item_count,
    SUM(oi.quantity) AS total_quantity,
    o.total_amount
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id;
