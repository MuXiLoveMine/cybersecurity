-- init.sql
-- 数据库初始化脚本
-- 用法: mysql -u root -p < init.sql

-- 创建数据库
CREATE DATABASE IF NOT EXISTS webapp DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE webapp;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(100) NOT NULL COMMENT '密码',
    email VARCHAR(100) COMMENT '邮箱',
    age INT DEFAULT 0 COMMENT '年龄',
    gender ENUM('male', 'female', 'unknown') DEFAULT 'unknown' COMMENT '性别',
    city VARCHAR(50) DEFAULT '' COMMENT '城市',
    status TINYINT DEFAULT 1 COMMENT '状态: 1正常 0禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '订单ID',
    order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
    user_id INT NOT NULL COMMENT '用户ID',
    total_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT '总金额',
    status TINYINT DEFAULT 0 COMMENT '状态: 0待付款 1已付款 2已发货 3已完成 4已取消',
    address VARCHAR(255) DEFAULT '' COMMENT '收货地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '商品ID',
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    price DECIMAL(10,2) DEFAULT 0.00 COMMENT '价格',
    stock INT DEFAULT 0 COMMENT '库存',
    category_id INT DEFAULT 0 COMMENT '分类ID',
    description TEXT COMMENT '商品描述',
    status TINYINT DEFAULT 1 COMMENT '状态: 1上架 0下架',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_name (name),
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 订单商品表
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '商品ID',
    quantity INT DEFAULT 1 COMMENT '数量',
    price DECIMAL(10,2) DEFAULT 0.00 COMMENT '单价',
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单商品表';

-- 插入测试数据 - 用户表
INSERT INTO users (username, password, email, age, gender, city) VALUES
    ('admin', 'admin123', 'admin@example.com', 30, 'male', '北京'),
    ('zhangsan', '123456', 'zhangsan@example.com', 25, 'male', '北京'),
    ('lisi', '123456', 'lisi@example.com', 28, 'female', '上海'),
    ('wangwu', '123456', 'wangwu@example.com', 22, 'male', '广州'),
    ('zhaoliu', '123456', 'zhaoliu@example.com', 35, 'female', '深圳'),
    ('qianqi', '123456', 'qianqi@example.com', 27, 'male', '杭州'),
    ('sunba', '123456', 'sunba@example.com', 31, 'female', '成都'),
    ('zhoujiu', '123456', 'zhoujiu@example.com', 24, 'male', '武汉'),
    ('wu_shi', '123456', 'wushi@example.com', 29, 'female', '南京'),
    ('zheng_shi', '123456', 'zhengshi@example.com', 26, 'male', '西安');

-- 插入测试数据 - 商品表
INSERT INTO products (name, price, stock, category_id, description) VALUES
    ('iPhone 15 Pro', 7999.00, 100, 1, 'Apple 最新款手机，钛金属设计'),
    ('MacBook Pro 14', 14999.00, 50, 1, 'M3 芯片，专业级笔记本'),
    ('AirPods Pro 2', 1899.00, 200, 2, '主动降噪无线耳机'),
    ('iPad Air', 4799.00, 80, 3, '轻薄平板电脑，M1 芯片'),
    ('Apple Watch S9', 2999.00, 150, 4, '智能手表，健康监测'),
    ('Magic Keyboard', 899.00, 300, 5, '无线蓝牙键盘'),
    ('Magic Mouse', 699.00, 250, 5, '无线触控鼠标'),
    ('HomePod mini', 749.00, 120, 6, '智能音箱，家庭中枢'),
    ('Apple TV 4K', 1499.00, 60, 7, '4K 高清机顶盒'),
    ('iPhone 15', 5999.00, 180, 1, 'iPhone 15 标准版，灵动岛设计');

-- 插入测试数据 - 订单表
INSERT INTO orders (order_no, user_id, total_amount, status, address) VALUES
    ('ORD202401010001', 2, 7999.00, 3, '北京市朝阳区xxx路1号'),
    ('ORD202401020001', 3, 2598.00, 3, '上海市浦东新区xxx路2号'),
    ('ORD202401030001', 2, 14999.00, 2, '北京市海淀区xxx路3号'),
    ('ORD202401040001', 4, 4799.00, 1, '广州市天河区xxx路4号'),
    ('ORD202401050001', 5, 2999.00, 0, '深圳市南山区xxx路5号'),
    ('ORD202401060001', 6, 1598.00, 3, '杭州市西湖区xxx路6号'),
    ('ORD202401070001', 7, 899.00, 3, '成都市武侯区xxx路7号'),
    ('ORD202401080001', 8, 5999.00, 2, '武汉市洪山区xxx路8号');

-- 插入测试数据 - 订单商品表
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
    (1, 1, 1, 7999.00),
    (2, 3, 1, 1899.00),
    (2, 7, 1, 699.00),
    (3, 2, 1, 14999.00),
    (4, 4, 1, 4799.00),
    (5, 5, 1, 2999.00),
    (6, 3, 1, 1899.00),
    (6, 8, 1, 749.00),
    (7, 6, 1, 899.00),
    (8, 10, 1, 5999.00);

-- 查看数据统计
SELECT '用户表: ' AS '', COUNT(*) AS num FROM users
UNION ALL
SELECT '商品表: ', COUNT(*) FROM products
UNION ALL
SELECT '订单表: ', COUNT(*) FROM orders
UNION ALL
SELECT '订单商品表: ', COUNT(*) FROM order_items;
