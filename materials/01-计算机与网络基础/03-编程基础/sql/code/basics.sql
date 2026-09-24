-- ============================================================
-- basics.sql —— SQL 基础语法示例（安全从业者视角）
--
-- 涵盖内容：
--   1. DDL：数据库、表、索引
--   2. DML：INSERT、SELECT、UPDATE、DELETE
--   3. 查询进阶：WHERE、ORDER BY、LIMIT
--   4. 聚合与分组
--   5. JOIN 连接查询
--   6. 子查询
--   7. 视图
--
-- 适用数据库：MySQL 5.7+ / 8.0+
-- 其他数据库可能需要微调语法
--
-- 运行方式：
--   MySQL:  mysql -u root -p < basics.sql
--   SQLite: sqlite3 test.db < basics.sql （部分语法需调整）
--
-- 注意：本脚本用于学习参考，可在测试环境中执行
-- ============================================================


-- ============================================================
-- 1. DDL：数据定义语言
-- ============================================================
-- 1.1 创建数据库
-- ============================================================

-- 创建测试数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS security_learn
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE security_learn;


-- ============================================================
-- 1.2 创建表
-- ============================================================

-- 用户表（安全设计：密码存储哈希，而非明文）
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE COMMENT '用户名',
    email           VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    password_hash   VARCHAR(255) NOT NULL COMMENT '密码哈希(bcrypt)',
    full_name       VARCHAR(100) DEFAULT '' COMMENT '真实姓名',
    role            VARCHAR(20)  DEFAULT 'user' COMMENT '角色：user/editor/admin',
    phone           VARCHAR(20)  DEFAULT '' COMMENT '手机号',
    department      VARCHAR(50)  DEFAULT '' COMMENT '部门',
    is_active       TINYINT(1)   DEFAULT 1 COMMENT '是否启用 1=启用 0=禁用',
    login_count     INT          DEFAULT 0 COMMENT '登录次数',
    last_login_at   DATETIME     DEFAULT NULL COMMENT '最后登录时间',
    last_login_ip   VARCHAR(45)  DEFAULT '' COMMENT '最后登录IP',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    product_name    VARCHAR(100) NOT NULL COMMENT '产品名称',
    category        VARCHAR(50)  DEFAULT '' COMMENT '分类',
    price           DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '价格',
    stock           INT          NOT NULL DEFAULT 0 COMMENT '库存',
    description     TEXT COMMENT '产品描述',
    status          VARCHAR(20)  DEFAULT 'active' COMMENT '状态：active/inactive',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_price (price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='产品表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    order_no        VARCHAR(32)  NOT NULL UNIQUE COMMENT '订单号',
    user_id         INT          NOT NULL COMMENT '用户ID',
    product_id      INT          NOT NULL COMMENT '产品ID',
    quantity        INT          NOT NULL DEFAULT 1 COMMENT '数量',
    total_amount    DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '总金额',
    status          VARCHAR(20)  DEFAULT 'pending' COMMENT '订单状态：pending/paid/shipped/delivered/cancelled',
    shipping_addr   VARCHAR(255) DEFAULT '' COMMENT '收货地址',
    remark          VARCHAR(255) DEFAULT '' COMMENT '备注',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_product_id (product_id),
    INDEX idx_status (status),
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 操作日志表（审计用）
CREATE TABLE IF NOT EXISTS audit_logs (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          DEFAULT NULL COMMENT '操作用户ID',
    username        VARCHAR(50)  DEFAULT '' COMMENT '操作时用户名',
    action          VARCHAR(50)  NOT NULL COMMENT '操作类型：login/logout/create/update/delete',
    target_table    VARCHAR(50)  DEFAULT '' COMMENT '操作的表',
    target_id       INT          DEFAULT NULL COMMENT '操作记录ID',
    detail          TEXT COMMENT '操作详情(JSON)',
    ip_address      VARCHAR(45)  DEFAULT '' COMMENT '操作IP',
    user_agent      VARCHAR(255) DEFAULT '' COMMENT '浏览器UA',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at),
    INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';


-- ============================================================
-- 2. DML：数据操作语言 - INSERT
-- ============================================================

-- 插入用户（密码为 bcrypt 哈希，不是明文！）
INSERT INTO users (username, email, password_hash, full_name, role, department, phone) VALUES
    ('alice',   'alice@example.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Alice Wang',  'admin',  '技术部', '13800000001'),
    ('bob',     'bob@example.com',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Bob Li',    'editor', '市场部', '13800000002'),
    ('charlie', 'charlie@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Charlie Zhang', 'user', '财务部', '13800000003'),
    ('david',   'david@example.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'David Chen',  'user',   '技术部', '13800000004'),
    ('eve',     'eve@example.com',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Eve Liu',     'editor', '运营部', '13800000005'),
    ('frank',   'frank@example.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Frank Zhou',  'user',   '市场部', '13800000006'),
    ('grace',   'grace@example.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Grace Wu',    'admin',  '管理层', '13800000007'),
    ('henry',   'henry@example.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Henry Sun',   'user',   '技术部', '13800000008'),
    ('ivy',     'ivy@example.com',     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Ivy Zhao',    'user',   '财务部', '13800000009'),
    ('jack',    'jack@example.com',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi', 'Jack Huang',  'user',   '运营部', '13800000010');

-- 插入产品
INSERT INTO products (product_name, category, price, stock, description, status) VALUES
    ('Web 安全入门课程',      '课程',  299.00,  500, '从零开始学习Web安全基础',           'active'),
    ('SQL 注入攻防实战',      '课程',  399.00,  300, '深入理解SQL注入原理与防御',          'active'),
    ('渗透测试工程师课程',    '课程',  999.00,  200, '系统化渗透测试技能培训',            'active'),
    ('网络安全基础教材',      '图书',   89.00, 1000, '网络安全基础知识完整教材',          'active'),
    ('加密与解密',            '图书',   69.00,  800, '密码学基础与应用',                  'active'),
    ('安全运维实战指南',      '图书',  128.00,  600, '企业安全运维实践手册',              'active'),
    ('年度安全会员',          '会员', 1999.00,  100, '全年安全课程与工具会员',            'active'),
    ('企业安全咨询',          '服务', 5000.00,   50, '企业安全评估与咨询服务',            'active'),
    ('CTF 入门礼包',          '周边',   99.00,  200, 'CTF入门题目与解答',                 'inactive'),
    ('安全开发实战训练营',    '课程', 1599.00,  150, '安全编码与代码审计训练营',          'active');

-- 插入订单
INSERT INTO orders (order_no, user_id, product_id, quantity, total_amount, status, shipping_addr, remark) VALUES
    ('ORD2026010001', 1, 1, 1,  299.00, 'delivered', '北京市朝阳区xxx路1号',  '公司采购'),
    ('ORD2026010002', 2, 2, 1,  399.00, 'shipped',   '上海市浦东新区xxx路2号', ''),
    ('ORD2026010003', 3, 4, 2,  178.00, 'delivered', '广州市天河区xxx路3号',  '个人学习'),
    ('ORD2026010004', 1, 3, 1,  999.00, 'paid',      '北京市海淀区xxx路4号',  ''),
    ('ORD2026010005', 4, 1, 1,  299.00, 'pending',   '深圳市南山区xxx路5号',  ''),
    ('ORD2026010006', 5, 5, 1,   69.00, 'cancelled', '杭州市西湖区xxx路6号',  '取消订单'),
    ('ORD2026010007', 6, 2, 1,  399.00, 'delivered', '成都市武侯区xxx路7号',  ''),
    ('ORD2026010008', 7, 7, 1, 1999.00, 'paid',      '北京市西城区xxx路8号',  '年度会员'),
    ('ORD2026010009', 8, 10, 1, 1599.00, 'shipped',   '武汉市洪山区xxx路9号',  '企业团购'),
    ('ORD2026010010', 9, 4, 3,  267.00, 'delivered', '南京市鼓楼区xxx路10号', '部门采购'),
    ('ORD2026010011', 2, 3, 1,  999.00, 'paid',      '上海市静安区xxx路11号', ''),
    ('ORD2026010012', 10, 1, 1, 299.00, 'pending',   '西安市雁塔区xxx路12号', '');

-- 插入审计日志
INSERT INTO audit_logs (user_id, username, action, target_table, target_id, detail, ip_address) VALUES
    (1, 'alice',   'login',    NULL,    NULL, '{"status":"success"}',          '192.168.1.10'),
    (2, 'bob',     'login',    NULL,    NULL, '{"status":"success"}',          '192.168.1.11'),
    (3, 'charlie', 'login',    NULL,    NULL, '{"status":"failed","reason":"wrong_password"}', '192.168.1.12'),
    (3, 'charlie', 'login',    NULL,    NULL, '{"status":"success"}',          '192.168.1.12'),
    (1, 'alice',   'create',   'products', 10, '{"product_name":"安全开发实战训练营"}', '192.168.1.10'),
    (2, 'bob',     'update',   'products', 2,  '{"field":"price","old":399,"new":499}', '192.168.1.11'),
    (7, 'grace',   'login',    NULL,    NULL, '{"status":"success"}',          '10.0.0.5'),
    (5, 'eve',     'login',    NULL,    NULL, '{"status":"failed","reason":"user_disabled"}', '203.0.113.45'),
    (1, 'alice',   'delete',   'orders', 6,   '{"order_no":"ORD2026010006"}',  '192.168.1.10'),
    (4, 'david',   'login',    NULL,    NULL, '{"status":"success"}',          '192.168.1.13');


-- ============================================================
-- 3. 查询基础 SELECT
-- ============================================================

-- 3.1 基本查询
SELECT '=== 3.1 基本查询 ===' AS info;

-- 查询所有列（不推荐生产环境使用）
SELECT * FROM users;

-- 查询指定列（推荐，最小化原则）
SELECT id, username, email, role, is_active FROM users;

-- 列别名
SELECT username AS 用户名, email AS 邮箱, role AS 角色 FROM users;

-- DISTINCT 去重
SELECT DISTINCT role FROM users;
SELECT DISTINCT department FROM users;


-- ============================================================
-- 3.2 WHERE 条件查询
-- ============================================================
SELECT '=== 3.2 WHERE 条件查询 ===' AS info;

-- 等于
SELECT * FROM users WHERE role = 'admin';

-- 不等于
SELECT * FROM users WHERE role != 'admin';
SELECT * FROM users WHERE role <> 'admin';  -- 另一种写法

-- 大于/小于
SELECT * FROM products WHERE price > 500;
SELECT * FROM products WHERE price <= 100;

-- AND / OR
SELECT * FROM users WHERE role = 'user' AND department = '技术部';
SELECT * FROM users WHERE role = 'admin' OR role = 'editor';

-- IN
SELECT * FROM users WHERE role IN ('admin', 'editor');

-- NOT IN
SELECT * FROM users WHERE role NOT IN ('admin');

-- BETWEEN（闭区间，包含两端）
SELECT * FROM products WHERE price BETWEEN 100 AND 500;

-- LIKE 模糊查询
-- % 匹配任意字符，_ 匹配单个字符
SELECT * FROM users WHERE username LIKE 'a%';       -- a 开头
SELECT * FROM users WHERE email LIKE '%@example.com';  -- @example.com 结尾
SELECT * FROM users WHERE username LIKE '%a%';      -- 包含 a
SELECT * FROM users WHERE username LIKE 'a__i__';   -- a 开头，第4个字符是 i，共6个字符

-- IS NULL / IS NOT NULL
SELECT * FROM users WHERE last_login_at IS NULL;
SELECT * FROM users WHERE last_login_at IS NOT NULL;

-- NOT 取反
SELECT * FROM users WHERE NOT is_active = 0;


-- ============================================================
-- 3.3 ORDER BY 排序
-- ============================================================
SELECT '=== 3.3 ORDER BY 排序 ===' AS info;

-- 升序（默认）
SELECT id, username, role FROM users ORDER BY username ASC;

-- 降序
SELECT id, username, role FROM users ORDER BY username DESC;

-- 多字段排序
SELECT id, username, role, department FROM users
ORDER BY role ASC, username DESC;

-- 按列序号排序（不推荐，可读性差）
SELECT id, username, email FROM users ORDER BY 2;


-- ============================================================
-- 3.4 LIMIT 限制数量
-- ============================================================
SELECT '=== 3.4 LIMIT 限制数量 ===' AS info;

-- 前 5 条
SELECT * FROM users ORDER BY id LIMIT 5;

-- 从第 3 条开始，取 5 条（分页）
SELECT * FROM users ORDER BY id LIMIT 2, 5;

-- MySQL 8.0+ 也支持 OFFSET 语法
SELECT * FROM users ORDER BY id LIMIT 5 OFFSET 2;


-- ============================================================
-- 4. 聚合与分组
-- ============================================================
SELECT '=== 4. 聚合与分组 ===' AS info;

-- 4.1 聚合函数
SELECT '--- 4.1 聚合函数 ---' AS info;

-- COUNT 计数
SELECT COUNT(*) AS total_users FROM users;
SELECT COUNT(DISTINCT role) AS role_count FROM users;

-- SUM 求和
SELECT SUM(stock) AS total_stock FROM products;
SELECT SUM(total_amount) AS total_revenue FROM orders WHERE status = 'delivered';

-- AVG 平均值
SELECT AVG(price) AS avg_price FROM products WHERE status = 'active';
SELECT AVG(login_count) AS avg_login FROM users;

-- MAX / MIN
SELECT MAX(price) AS max_price FROM products;
SELECT MIN(price) AS min_price FROM products;
SELECT MAX(created_at) AS latest_order FROM orders;


-- 4.2 GROUP BY 分组
SELECT '--- 4.2 GROUP BY 分组 ---' AS info;

-- 按角色统计用户数
SELECT role, COUNT(*) AS user_count
FROM users
GROUP BY role
ORDER BY user_count DESC;

-- 按部门统计
SELECT department, COUNT(*) AS user_count, AVG(login_count) AS avg_login
FROM users
GROUP BY department
ORDER BY user_count DESC;

-- 按状态统计订单
SELECT status, COUNT(*) AS order_count, SUM(total_amount) AS total_amount
FROM orders
GROUP BY status
ORDER BY order_count DESC;

-- 产品分类统计
SELECT category, COUNT(*) AS product_count, AVG(price) AS avg_price
FROM products
WHERE status = 'active'
GROUP BY category;


-- 4.3 HAVING 分组后筛选
SELECT '--- 4.3 HAVING 分组后筛选 ---' AS info;

-- 找出用户数大于 2 的部门
SELECT department, COUNT(*) AS user_count
FROM users
GROUP BY department
HAVING COUNT(*) > 2
ORDER BY user_count DESC;

-- 找出订单金额大于 500 的用户
SELECT user_id, COUNT(*) AS order_count, SUM(total_amount) AS total_spent
FROM orders
WHERE status != 'cancelled'
GROUP BY user_id
HAVING SUM(total_amount) > 500
ORDER BY total_spent DESC;

-- 注意：WHERE 在分组前筛选，HAVING 在分组后筛选
-- 以下两个查询结果相同，但执行时机不同
SELECT role, COUNT(*) AS cnt FROM users WHERE is_active = 1 GROUP BY role;
SELECT role, COUNT(*) AS cnt FROM users GROUP BY role HAVING MAX(is_active) = 1;


-- ============================================================
-- 5. JOIN 连接查询
-- ============================================================
SELECT '=== 5. JOIN 连接查询 ===' AS info;

-- 5.1 INNER JOIN（内连接）
SELECT '--- 5.1 INNER JOIN 内连接 ---' AS info;

-- 查询订单及其对应的用户信息
SELECT o.order_no, o.total_amount, o.status, u.username, u.email
FROM orders o
INNER JOIN users u ON o.user_id = u.id
ORDER BY o.created_at DESC;

-- 查询订单、用户、产品三表连接
SELECT o.order_no, u.username, p.product_name, o.quantity, o.total_amount, o.status
FROM orders o
INNER JOIN users u ON o.user_id = u.id
INNER JOIN products p ON o.product_id = p.id
ORDER BY o.total_amount DESC;


-- 5.2 LEFT JOIN（左连接）
SELECT '--- 5.2 LEFT JOIN 左连接 ---' AS info;

-- 查询所有用户及其订单数（没有订单的用户也显示）
SELECT u.id, u.username, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username
ORDER BY order_count DESC;

-- 查询所有产品及其订单数
SELECT p.id, p.product_name, COUNT(o.id) AS order_count
FROM products p
LEFT JOIN orders o ON p.id = o.product_id
GROUP BY p.id, p.product_name
ORDER BY order_count DESC;


-- 5.3 RIGHT JOIN（右连接）
SELECT '--- 5.3 RIGHT JOIN 右连接 ---' AS info;

-- 右连接（效果和左连接交换表顺序一样）
SELECT o.order_no, o.total_amount, u.username
FROM orders o
RIGHT JOIN users u ON o.user_id = u.id
ORDER BY u.id;


-- 5.4 自连接
SELECT '--- 5.4 自连接 ---' AS info;

-- 示例：查找同一部门的用户对
SELECT 
    u1.username AS user_a,
    u2.username AS user_b,
    u1.department
FROM users u1
INNER JOIN users u2 ON u1.department = u2.department AND u1.id < u2.id
ORDER BY u1.department, u1.id;


-- ============================================================
-- 6. 子查询
-- ============================================================
SELECT '=== 6. 子查询 ===' AS info;

-- 6.1 WHERE 子查询
SELECT '--- 6.1 WHERE 子查询 ---' AS info;

-- 找出消费最高的订单对应的用户
SELECT username, email FROM users
WHERE id = (
    SELECT user_id FROM orders
    ORDER BY total_amount DESC
    LIMIT 1
);

-- 找出有订单的用户
SELECT username, email FROM users
WHERE id IN (
    SELECT DISTINCT user_id FROM orders
);

-- 找出没有订单的用户
SELECT username, email FROM users
WHERE id NOT IN (
    SELECT DISTINCT user_id FROM orders WHERE status != 'cancelled'
);


-- 6.2 EXISTS 子查询
SELECT '--- 6.2 EXISTS 子查询 ---' AS info;

-- 存在性检查（通常比 IN 更高效）
SELECT u.username, u.email
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.user_id = u.id AND o.total_amount > 500
);

-- 不存在
SELECT u.username, u.email
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);


-- 6.3 FROM 子查询（派生表）
SELECT '--- 6.3 FROM 子查询 ---' AS info;

-- 查询每个用户的平均消费，再筛选高于平均值的
SELECT user_avg.username, user_avg.avg_spent
FROM (
    SELECT u.username, AVG(o.total_amount) AS avg_spent
    FROM users u
    INNER JOIN orders o ON u.id = o.user_id
    WHERE o.status != 'cancelled'
    GROUP BY u.id, u.username
) AS user_avg
WHERE user_avg.avg_spent > 300
ORDER BY user_avg.avg_spent DESC;


-- 6.4 SELECT 子查询（标量子查询）
SELECT '--- 6.4 SELECT 子查询 ---' AS info;

-- 每行显示该用户的订单数
SELECT
    u.username,
    u.email,
    (SELECT COUNT(*) FROM orders o WHERE o.user_id = u.id) AS order_count
FROM users u
ORDER BY order_count DESC;


-- ============================================================
-- 7. 视图
-- ============================================================
SELECT '=== 7. 视图 ===' AS info;

-- 创建视图：活跃用户视图（隐藏密码哈希等敏感字段）
CREATE OR REPLACE VIEW active_users_view AS
SELECT id, username, email, full_name, role, department, is_active, login_count, last_login_at
FROM users
WHERE is_active = 1;

-- 使用视图（和表一样查询）
SELECT * FROM active_users_view WHERE role = 'admin';

-- 创建视图：订单汇总视图
CREATE OR REPLACE VIEW order_summary_view AS
SELECT
    o.order_no,
    u.username,
    u.email,
    p.product_name,
    o.quantity,
    o.total_amount,
    o.status,
    o.created_at
FROM orders o
INNER JOIN users u ON o.user_id = u.id
INNER JOIN products p ON o.product_id = p.id;

-- 查询视图
SELECT * FROM order_summary_view WHERE status = 'delivered' ORDER BY total_amount DESC;

-- 查看视图定义
SHOW CREATE VIEW order_summary_view;


-- ============================================================
-- 8. 其他常用操作
-- ============================================================
SELECT '=== 8. 其他常用操作 ===' AS info;

-- 8.1 UPDATE 更新
SELECT '--- 8.1 UPDATE 更新 ---' AS info;

-- 更新单个字段
UPDATE users SET last_login_at = NOW(), last_login_ip = '192.168.1.100'
WHERE username = 'alice';

-- 递增
UPDATE users SET login_count = login_count + 1 WHERE id = 1;

-- 多字段更新
UPDATE products SET price = 499.00, description = 'SQL注入攻防实战（升级版）'
WHERE id = 2;

-- 注意：UPDATE 必须加 WHERE 条件！
-- 不带 WHERE 会更新全表，非常危险！


-- 8.2 DELETE 删除
SELECT '--- 8.2 DELETE 删除 ---' AS info;

-- 删除指定记录
DELETE FROM audit_logs WHERE id = 100;

-- 删除多条
DELETE FROM orders WHERE status = 'cancelled' AND created_at < '2025-01-01';

-- 注意：DELETE 必须加 WHERE 条件！
-- 不带 WHERE 会删除全表，非常危险！
-- TRUNCATE 更快但不能回滚！


-- 8.3 UNION 合并
SELECT '--- 8.3 UNION 合并 ---' AS info;

-- UNION：合并去重
SELECT username AS name, email FROM users WHERE role = 'admin'
UNION
SELECT username AS name, email FROM users WHERE role = 'editor'
ORDER BY name;

-- UNION ALL：合并不去重（更快）
SELECT 'user' AS type, username, email FROM users WHERE id <= 3
UNION ALL
SELECT 'product' AS type, product_name, CAST(price AS CHAR) FROM products WHERE id <= 3;


-- ============================================================
-- 9. 字符串与日期函数
-- ============================================================
SELECT '=== 9. 常用函数 ===' AS info;

-- 字符串函数
SELECT
    CONCAT(username, ' <', email, '>') AS full_contact,   -- 拼接
    UPPER(username) AS upper_name,                         -- 大写
    LOWER(email) AS lower_email,                           -- 小写
    LENGTH(username) AS name_length,                       -- 长度
    SUBSTRING(email, 1, 5) AS email_prefix,                -- 截取
    LEFT(email, 3) AS left3,                               -- 左截取
    RIGHT(email, 11) AS right11,                           -- 右截取
    REPLACE(email, 'example.com', 'test.org') AS replaced, -- 替换
    TRIM('  hello  ') AS trimmed,                          -- 去空格
    INSTR(email, '@') AS at_position                       -- 查找位置
FROM users
LIMIT 3;

-- 日期函数
SELECT
    NOW() AS now_datetime,
    CURDATE() AS today,
    CURTIME() AS current_time,
    DATE(created_at) AS date_only,
    YEAR(created_at) AS year,
    MONTH(created_at) AS month,
    DAY(created_at) AS day,
    DATEDIFF(NOW(), created_at) AS days_ago,
    DATE_ADD(created_at, INTERVAL 30 DAY) AS plus_30days,
    DATE_FORMAT(created_at, '%Y年%m月%d日') AS formatted
FROM orders
LIMIT 3;

-- 条件函数
SELECT
    username,
    role,
    CASE role
        WHEN 'admin' THEN '管理员'
        WHEN 'editor' THEN '编辑'
        WHEN 'user' THEN '普通用户'
        ELSE '未知'
    END AS role_cn,
    IF(is_active = 1, '启用', '禁用') AS status_cn,
    IFNULL(last_login_at, '从未登录') AS last_login
FROM users
LIMIT 5;


-- ============================================================
-- 脚本结束
-- ============================================================
SELECT '=== basics.sql 执行完毕 ===' AS info;
SELECT '涵盖：DDL、DML、查询、聚合、连接、子查询、视图' AS summary;
