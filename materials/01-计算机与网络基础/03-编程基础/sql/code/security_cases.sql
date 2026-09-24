-- ============================================================
-- security_cases.sql —— SQL 安全案例集（防御/学习视角）
--
-- 涵盖 4 个安全案例：
--   1. SQL 注入原理与防御对比 —— 展示不安全拼接 vs 参数化查询
--   2. 数据库权限审计 —— 用户权限、高权限账户、弱口令检查
--   3. 敏感数据审计 —— 明文密码、弱口令、敏感字段检查
--   4. 安全审计日志查询 —— 登录审计、操作审计、异常检测
--
-- 适用数据库：MySQL 5.7+ / 8.0+
-- 依赖：需先执行 basics.sql 导入测试数据
--       权限审计部分需要 MySQL 高权限账号
--
-- 运行方式：
--   mysql -u root -p security_learn < security_cases.sql
--
-- 注意：
--   - 所有案例仅供学习和研究使用
--   - 注入示例仅用于理解原理，请勿用于未授权测试
--   - 生产环境请使用成熟的安全方案（ORM、参数化查询等）
-- ============================================================


USE security_learn;


-- ============================================================
-- 案例 1：SQL 注入原理与防御对比
-- ============================================================
-- 本案例展示 SQL 注入的原理以及正确的防御方法
-- 通过对比危险写法和安全写法，理解注入的本质和防御核心
-- ============================================================

SELECT '============================================================' AS '';
SELECT '  案例 1：SQL 注入原理与防御对比' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '--- 1.1 注入原理演示（仅学习，请勿实际利用） ---';

-- 正常的登录查询（伪代码，演示拼接逻辑）
-- 假设应用代码是这样拼接的：
--   $sql = "SELECT * FROM users WHERE username = '$username' AND password_hash = '$password_hash'";

-- 【正常输入】
-- username = alice
-- password = password123
SELECT '正常输入：username=alice' AS '';
SELECT * FROM users WHERE username = 'alice' AND password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYGyJq2YuH1UOqi';

SELECT '' AS '';

-- 【注入输入 - 万能密码】
-- username = admin' --
-- password = anything
-- 实际执行的 SQL 变成：
--   SELECT * FROM users WHERE username = 'admin' -- ' AND password_hash = 'anything'
-- -- 是 SQL 注释，后面的密码验证被注释掉了！
SELECT '注入演示：username=admin'' -- (万能密码原理)' AS '';
SELECT * FROM users WHERE username = 'admin' -- ' AND password_hash = 'anything';

SELECT '' AS '';

-- 【注入输入 - OR 恒真】
-- username = ' OR '1'='1
-- 实际执行的 SQL 变成：
--   SELECT * FROM users WHERE username = '' OR '1'='1' AND ...
SELECT '注入演示：username='' OR ''1''=''1 (OR恒真原理)' AS '';
SELECT * FROM users WHERE username = '' OR '1'='1';

SELECT '' AS '';

-- 【注入输入 - UNION 联合查询】
-- UNION 可以合并另一个查询的结果
SELECT '注入演示：UNION 联合查询原理' AS '';
SELECT id, username, email, role FROM users WHERE username = 'alice'
UNION ALL
SELECT 999, 'INJECTED', 'hacked@evil.com', 'admin';

SELECT '' AS '';


-- ============================================================
-- 1.2 防御方法：参数化查询
-- ============================================================
SELECT '' AS '--- 1.2 防御方法：参数化查询（核心防御） ---';

SELECT '参数化查询原理：SQL 结构与数据分离' AS '';
SELECT '数据永远被当作数据，不会被解析为 SQL 代码' AS '';
SELECT '' AS '';

-- 参数化查询示例（MySQL 预处理语句）
-- 真实应用中使用语言的 Prepared Statement API
-- 这里演示 MySQL 原生的 PREPARE 语法

SELECT 'MySQL 原生 PREPARE 示例：' AS '';

-- 准备 SQL 模板（结构固定，? 是占位符）
PREPARE stmt_login FROM 'SELECT * FROM users WHERE username = ? AND is_active = 1';

-- 设置参数
SET @username = 'alice';
SET @malicious_input = ''' OR 1=1 --';

-- 执行安全查询（正常输入）
EXECUTE stmt_login USING @username;

-- 执行安全查询（恶意输入也不会注入！）
-- 因为参数被当作纯数据处理，不会改变 SQL 结构
SELECT '恶意输入作为参数时，会被当作纯字符串，不会注入：' AS '';
SET @test = (SELECT COUNT(*) FROM users WHERE username = @malicious_input);
SELECT @test AS '匹配行数(应为0，说明注入无效)';

-- 释放语句
DEALLOCATE PREPARE stmt_login;

SELECT '' AS '';
SELECT '💡 核心结论：' AS '';
SELECT '   - 字符串拼接 SQL = 注入风险根源' AS '';
SELECT '   - 参数化查询（Prepared Statement）= 最佳防御方案' AS '';
SELECT '   - 输入验证、WAF 等都是辅助，不能替代参数化查询' AS '';
SELECT '' AS '';


-- ============================================================
-- 1.3 不同语言的参数化查询写法对比
-- ============================================================
SELECT '' AS '--- 1.3 常见语言参数化查询写法（参考） ---';

-- 创建一个表来存储参考代码
CREATE TEMPORARY TABLE IF NOT EXISTS param_query_ref (
    language VARCHAR(20),
    example TEXT
);

INSERT INTO param_query_ref VALUES
    ('Python',  'cursor.execute("SELECT * FROM users WHERE username = %s", (username,))'),
    ('Java',    'PreparedStatement pstmt = conn.prepareStatement("SELECT * FROM users WHERE username = ?");\n pstmt.setString(1, username);'),
    ('JavaScript (Node.js)', 'db.query("SELECT * FROM users WHERE username = ?", [username])'),
    ('PHP',     '$stmt = $pdo->prepare("SELECT * FROM users WHERE username = ?");\n $stmt->execute([$username]);'),
    ('C#',      'using (var cmd = new SqlCommand("SELECT * FROM Users WHERE Username = @Username", conn)) {\n   cmd.Parameters.AddWithValue("@Username", username); }'),
    ('Go',      'db.Query("SELECT * FROM users WHERE username = ?", username)'),
    ('Ruby',    'User.where("username = ?", username)');

SELECT * FROM param_query_ref;

DROP TEMPORARY TABLE IF EXISTS param_query_ref;

SELECT '' AS '';


-- ============================================================
-- 案例 2：数据库权限审计
-- ============================================================
-- 数据库权限配置是安全基线的重要组成部分
-- 最小权限原则：只给必要的权限
-- 注意：以下查询需要 MySQL root 或高权限账号才能执行
-- ============================================================

SELECT '============================================================' AS '';
SELECT '  案例 2：数据库权限审计' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '--- 2.1 查看所有数据库用户 ---';

-- 列出所有用户及其主机
SELECT user, host, account_locked, password_expired
FROM mysql.user
ORDER BY user, host;

SELECT '' AS '';
SELECT '💡 检查要点：' AS '';
SELECT '   1. 是否有不需要的账户（应删除）' AS '';
SELECT '   2. 是否有允许任意主机连接的账户（user@%，应限制IP）' AS '';
SELECT '   3. 是否有被锁定的账户（应删除或启用）' AS '';
SELECT '' AS '';


-- ============================================================
-- 2.2 高权限账户检查
-- ============================================================
SELECT '' AS '--- 2.2 高权限账户检查 ---';

-- 查看有 SUPER 权限的用户（最高权限之一）
SELECT 'SUPER 权限用户（可执行全局操作）：' AS '';
SELECT user, host FROM mysql.user WHERE Super_priv = 'Y';

-- 查看有 FILE 权限的用户（可读写服务器文件）
SELECT '' AS '';
SELECT 'FILE 权限用户（可读写服务器文件，危险）：' AS '';
SELECT user, host FROM mysql.user WHERE File_priv = 'Y';

-- 查看有 ALL PRIVILEGES 的用户
SELECT '' AS '';
SELECT 'ALL PRIVILEGES 用户（所有权限）：' AS '';
SELECT user, host FROM mysql.user
WHERE Select_priv = 'Y' AND Insert_priv = 'Y' AND Update_priv = 'Y'
  AND Delete_priv = 'Y' AND Create_priv = 'Y' AND Drop_priv = 'Y';

-- 查看有 GRANT 权限的用户（可授权给别人）
SELECT '' AS '';
SELECT 'GRANT 权限用户（可授权给其他用户）：' AS '';
SELECT user, host FROM mysql.user WHERE Grant_priv = 'Y';

SELECT '' AS '';
SELECT '⚠️  安全建议：' AS '';
SELECT '   - 应用账号不要给 SUPER、FILE、GRANT 等全局权限' AS '';
SELECT '   - 应用账号只给具体数据库的必要权限' AS '';
SELECT '   - 管理账号应限制可连接的主机IP' AS '';
SELECT '' AS '';


-- ============================================================
-- 2.3 数据库级权限
-- ============================================================
SELECT '' AS '--- 2.3 数据库级权限（mysql.db） ---';

-- 查看各数据库的权限分配
SELECT db, user, host,
       Select_priv, Insert_priv, Update_priv, Delete_priv,
       Create_priv, Drop_priv, Grant_priv
FROM mysql.db
ORDER BY db, user;

SELECT '' AS '';
SELECT '💡 检查要点：' AS '';
SELECT '   - 应用账号是否只访问需要的数据库' AS '';
SELECT '   - 是否有 DROP/ALTER 等危险权限' AS '';
SELECT '   - 是否有 Grant_priv（应禁止）' AS '';
SELECT '' AS '';


-- ============================================================
-- 2.4 空密码/弱密码检查
-- ============================================================
SELECT '' AS '--- 2.4 空密码检查 ---';

-- MySQL 5.7+ 用 authentication_string
SELECT '空密码账户：' AS '';
SELECT user, host, plugin,
       CASE WHEN authentication_string = '' THEN '空密码'
            WHEN LENGTH(authentication_string) < 20 THEN '可能弱密码'
            ELSE '已设置密码'
       END AS password_status
FROM mysql.user
ORDER BY password_status, user;

SELECT '' AS '';
SELECT '⚠️  安全建议：' AS '';
SELECT '   - 所有账户必须设置强密码' AS '';
SELECT '   - 密码长度建议 ≥ 16 位，含大小写数字特殊字符' AS '';
SELECT '   - 定期更换密码（如 90 天）' AS '';
SELECT '   - 禁用或删除不需要的默认账户' AS '';
SELECT '' AS '';


-- ============================================================
-- 案例 3：敏感数据审计
-- ============================================================
-- 检查数据库中的敏感数据存储是否安全
-- ============================================================

SELECT '============================================================' AS '';
SELECT '  案例 3：敏感数据审计' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '--- 3.1 密码存储安全检查 ---';

-- 检查是否有明文密码字段（危险！）
-- 安全的密码应该是 bcrypt/argon2 哈希值
SELECT '检查 password_hash 字段的存储格式：' AS '';
SELECT
    id,
    username,
    CASE
        WHEN password_hash LIKE '$2b$%' THEN 'bcrypt（安全）'
        WHEN password_hash LIKE '$2a$%' THEN 'bcrypt（安全）'
        WHEN password_hash LIKE '$argon%' THEN 'argon2（安全）'
        WHEN password_hash LIKE '$pbkdf2%' THEN 'PBKDF2（安全）'
        WHEN LENGTH(password_hash) = 32 AND password_hash REGEXP '^[0-9a-f]{32}$' THEN 'MD5（不安全）'
        WHEN LENGTH(password_hash) = 40 AND password_hash REGEXP '^[0-9a-f]{40}$' THEN 'SHA-1（不安全）'
        WHEN LENGTH(password_hash) = 64 AND password_hash REGEXP '^[0-9a-f]{64}$' THEN 'SHA-256（不够安全，缺盐）'
        ELSE '未知格式'
    END AS password_security
FROM users;

SELECT '' AS '';
SELECT '💡 密码存储安全等级：' AS '';
SELECT '   ✅ 推荐：bcrypt / Argon2 / PBKDF2（带盐的慢哈希）' AS '';
SELECT '   ⚠️  一般：SHA-256 + 盐（还可以，但不如慢哈希）' AS '';
SELECT '   ❌ 危险：明文 / MD5 / SHA-1 / 无盐 SHA-256' AS '';
SELECT '' AS '';


-- ============================================================
-- 3.2 敏感字段检查
-- ============================================================
SELECT '' AS '--- 3.2 敏感字段检查 ---';

-- 查找可能的敏感字段（通过字段名模式匹配）
SELECT '通过 information_schema 查找敏感字段：' AS '';
SELECT
    table_name,
    column_name,
    data_type,
    CASE
        WHEN column_name LIKE '%password%' THEN '密码字段（需加密/哈希）'
        WHEN column_name LIKE '%passwd%' THEN '密码字段（需加密/哈希）'
        WHEN column_name LIKE '%secret%' THEN '密钥/机密（需加密）'
        WHEN column_name LIKE '%token%' THEN '令牌（需安全存储）'
        WHEN column_name LIKE '%id_card%' OR column_name LIKE '%idcard%' THEN '身份证号（需加密）'
        WHEN column_name LIKE '%phone%' THEN '手机号（建议脱敏）'
        WHEN column_name LIKE '%email%' THEN '邮箱（建议保护）'
        WHEN column_name LIKE '%address%' THEN '地址（建议保护）'
        WHEN column_name LIKE '%ssn%' OR column_name LIKE '%social%' THEN '社保号（需加密）'
        ELSE '普通字段'
    END AS sensitivity_level
FROM information_schema.columns
WHERE table_schema = 'security_learn'
  AND (
      column_name LIKE '%password%'
      OR column_name LIKE '%secret%'
      OR column_name LIKE '%token%'
      OR column_name LIKE '%phone%'
      OR column_name LIKE '%email%'
      OR column_name LIKE '%id_card%'
      OR column_name LIKE '%address%'
  )
ORDER BY table_name, column_name;

SELECT '' AS '';
SELECT '💡 敏感数据保护建议：' AS '';
SELECT '   1. 密码：使用 bcrypt/Argon2 哈希（不可逆）' AS '';
SELECT '   2. 身份证/手机号：使用 AES 加密（可逆，需密钥管理）' AS '';
SELECT '   3. 展示时脱敏：138****8000、张*三' AS '';
SELECT '   4. 日志中不能出现敏感数据明文' AS '';
SELECT '   5. 遵循最小化原则：不需要的字段不要存储' AS '';
SELECT '' AS '';


-- ============================================================
-- 案例 4：安全审计日志查询
-- ============================================================
-- 审计日志是检测异常行为和溯源的重要依据
-- ============================================================

SELECT '============================================================' AS '';
SELECT '  案例 4：安全审计日志查询' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '--- 4.1 登录审计 ---';

-- 登录成功统计
SELECT '登录成功统计（按用户）：' AS '';
SELECT
    username,
    COUNT(*) AS success_count,
    MAX(created_at) AS last_success
FROM audit_logs
WHERE action = 'login' AND detail LIKE '%"success"%'
GROUP BY username
ORDER BY success_count DESC;

SELECT '' AS '';

-- 登录失败统计
SELECT '登录失败统计（按用户）：' AS '';
SELECT
    username,
    COUNT(*) AS fail_count,
    MAX(created_at) AS last_fail
FROM audit_logs
WHERE action = 'login' AND detail LIKE '%"failed"%'
GROUP BY username
ORDER BY fail_count DESC;

SELECT '' AS '';

-- 登录失败按 IP 统计（暴力破解检测）
SELECT '登录失败按 IP 统计（暴力破解检测）：' AS '';
SELECT
    ip_address,
    COUNT(*) AS fail_count,
    GROUP_CONCAT(DISTINCT username) AS target_users,
    MAX(created_at) AS last_attempt
FROM audit_logs
WHERE action = 'login' AND detail LIKE '%"failed"%'
GROUP BY ip_address
ORDER BY fail_count DESC;

SELECT '' AS '';
SELECT '💡 暴力破解检测规则：' AS '';
SELECT '   - 同一 IP 短时间内大量登录失败' AS '';
SELECT '   - 同一账户大量登录失败（针对特定用户）' AS '';
SELECT '   - 异常时间登录（如凌晨 2-5 点）' AS '';
SELECT '   - 异地登录（非常用地点）' AS '';
SELECT '' AS '';


-- ============================================================
-- 4.2 操作审计
-- ============================================================
SELECT '' AS '--- 4.2 操作审计 ---';

-- 操作类型统计
SELECT '操作类型分布：' AS '';
SELECT
    action AS 操作类型,
    COUNT(*) AS 操作次数,
    COUNT(DISTINCT username) AS 涉及用户数
FROM audit_logs
GROUP BY action
ORDER BY 操作次数 DESC;

SELECT '' AS '';

-- 管理员操作审计
SELECT '管理员操作记录（高危操作关注）：' AS '';
SELECT
    created_at AS 时间,
    username AS 操作用户,
    action AS 操作,
    target_table AS 目标表,
    target_id AS 目标ID,
    ip_address AS IP地址,
    detail AS 详情
FROM audit_logs
WHERE username IN (
    SELECT username FROM users WHERE role = 'admin'
)
ORDER BY created_at DESC;

SELECT '' AS '';


-- ============================================================
-- 4.3 异常检测查询
-- ============================================================
SELECT '' AS '--- 4.3 异常检测 ---';

-- 非工作时间登录（晚上10点到早上6点）
SELECT '非工作时间登录（22:00 - 06:00）：' AS '';
SELECT
    created_at,
    username,
    ip_address,
    detail
FROM audit_logs
WHERE action = 'login'
  AND (HOUR(created_at) >= 22 OR HOUR(created_at) < 6)
ORDER BY created_at DESC;

SELECT '' AS '';

-- 新 IP 登录（之前没出现过的 IP）
SELECT '首次出现的登录 IP（需关注是否为异常登录）：' AS '';
SELECT
    a.ip_address,
    a.username,
    a.created_at AS first_seen,
    (SELECT COUNT(*) FROM audit_logs b
     WHERE b.ip_address = a.ip_address AND b.action = 'login') AS total_logins
FROM audit_logs a
WHERE a.action = 'login'
  AND a.created_at = (
      SELECT MIN(created_at) FROM audit_logs c
      WHERE c.ip_address = a.ip_address AND c.action = 'login'
  )
ORDER BY a.created_at DESC;

SELECT '' AS '';

-- 删除操作审计（高危操作）
SELECT '删除操作记录（高危，需重点审计）：' AS '';
SELECT
    created_at,
    username,
    target_table,
    target_id,
    ip_address,
    detail
FROM audit_logs
WHERE action = 'delete'
ORDER BY created_at DESC;

SELECT '' AS '';


-- ============================================================
-- 4.4 安全加固示例（正确配置示范）
-- ============================================================
SELECT '' AS '--- 4.4 安全加固示例（学习用，请勿在生产直接执行） ---';

SELECT '1. 创建最小权限的应用用户：' AS '';
SELECT '  CREATE USER ''app_reader''@''localhost'' IDENTIFIED BY ''StrongPass123!'';' AS '';
SELECT '  GRANT SELECT ON security_learn.* TO ''app_reader''@''localhost'';' AS '';
SELECT '  FLUSH PRIVILEGES;' AS '';

SELECT '' AS '';
SELECT '2. 禁用远程 root 登录：' AS '';
SELECT '  DELETE FROM mysql.user WHERE User = ''root'' AND Host = ''%'';' AS '';
SELECT '  FLUSH PRIVILEGES;' AS '';

SELECT '' AS '';
SELECT '3. 删除测试数据库和匿名用户：' AS '';
SELECT '  DROP DATABASE IF EXISTS test;' AS '';
SELECT '  DELETE FROM mysql.user WHERE User = '''';' AS '';
SELECT '  FLUSH PRIVILEGES;' AS '';

SELECT '' AS '';
SELECT '4. 开启审计日志（my.cnf 配置）：' AS '';
SELECT '  general_log = ON' AS '';
SELECT '  general_log_file = /var/log/mysql/general.log' AS '';
SELECT '  slow_query_log = ON' AS '';
SELECT '  long_query_time = 2' AS '';

SELECT '' AS '';
SELECT '5. 数据备份策略：' AS '';
SELECT '  mysqldump -u root -p --all-databases > backup_$(date +%Y%m%d).sql' AS '';
SELECT '  # 每日全量备份 + 定期恢复演练' AS '';

SELECT '' AS '';


-- ============================================================
-- 总结
-- ============================================================
SELECT '============================================================' AS '';
SELECT '  SQL 安全要点总结' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '';
SELECT '【防御 SQL 注入】' AS '';
SELECT '  ✅ 核心：使用参数化查询（Prepared Statement）' AS '';
SELECT '  ✅ 辅助：输入验证（白名单）、ORM 框架、WAF' AS '';
SELECT '  ❌ 禁止：字符串拼接 SQL、动态表名/列名不加白名单' AS '';
SELECT '' AS '';

SELECT '【数据库权限】' AS '';
SELECT '  ✅ 原则：最小权限，只给必要的权限' AS '';
SELECT '  ✅ 分离：读写账号分离、应用和管理账号分离' AS '';
SELECT '  ✅ 限制：限制可连接的主机 IP，禁止 % 通配' AS '';
SELECT '' AS '';

SELECT '【数据保护】' AS '';
SELECT '  ✅ 密码：bcrypt/Argon2 慢哈希' AS '';
SELECT '  ✅ 敏感数据：加密存储，展示脱敏' AS '';
SELECT '  ✅ 备份：定期备份并验证恢复能力' AS '';
SELECT '' AS '';

SELECT '【审计监控】' AS '';
SELECT '  ✅ 开启：登录日志、操作日志、慢查询日志' AS '';
SELECT '  ✅ 告警：异常登录、高危操作、权限变更' AS '';
SELECT '  ✅ 定期：权限审计、漏洞扫描、补丁更新' AS '';
SELECT '' AS '';


-- ============================================================
-- 脚本结束
-- ============================================================
SELECT '' AS '';
SELECT '============================================================' AS '';
SELECT '  security_cases.sql 执行完毕' AS '';
SELECT '  涵盖：注入原理对比、权限审计、敏感数据审计、安全审计' AS '';
SELECT '============================================================' AS '';

SELECT '' AS '';
SELECT '⚠️  免责声明：' AS '';
SELECT '  本脚本仅供学习、研究和授权环境下的安全测试使用。' AS '';
SELECT '  任何未经授权的测试或攻击行为均属违法。' AS '';
SELECT '' AS '';
