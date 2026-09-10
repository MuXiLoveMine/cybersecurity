-- user_manage.sql
-- MySQL 用户与权限管理示例

-- =============================================
-- 一、用户管理
-- =============================================

-- 1. 查看所有用户
SELECT user, host, authentication_string FROM mysql.user;

-- 2. 创建用户（不同登录主机）
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'StrongPass123!';
CREATE USER 'webuser'@'127.0.0.1' IDENTIFIED BY 'StrongPass123!';
CREATE USER 'readonly'@'%' IDENTIFIED BY 'ReadPass123!';
CREATE USER 'appuser'@'192.168.1.%' IDENTIFIED BY 'AppPass123!';

-- 3. 修改密码
ALTER USER 'webuser'@'localhost' IDENTIFIED BY 'NewStrongPass456!';

-- 4. 重命名用户
-- RENAME USER 'olduser'@'localhost' TO 'newuser'@'localhost';

-- 5. 删除用户
-- DROP USER 'readonly'@'%';

-- 6. 查看当前用户
SELECT CURRENT_USER();
SELECT USER();

-- =============================================
-- 二、权限管理
-- =============================================

-- 7. 授予所有数据库的所有权限（不推荐，仅用于测试）
-- GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;

-- 8. 授予指定数据库的所有权限
GRANT ALL PRIVILEGES ON webapp.* TO 'webuser'@'localhost';

-- 9. 授予指定权限
GRANT SELECT, INSERT, UPDATE, DELETE ON webapp.* TO 'appuser'@'192.168.1.%';

-- 10. 只授予查询权限（只读用户）
GRANT SELECT ON webapp.* TO 'readonly'@'%';

-- 11. 授予指定表的权限
GRANT SELECT, INSERT ON webapp.users TO 'webuser'@'localhost';

-- 12. 授予指定列的权限
GRANT SELECT(id, username, email) ON webapp.users TO 'readonly'@'%';

-- 13. 刷新权限（GRANT 后一般不需要，但保险起见）
FLUSH PRIVILEGES;

-- 14. 查看用户权限
SHOW GRANTS FOR 'webuser'@'localhost';
SHOW GRANTS FOR 'readonly'@'%';

-- 15. 收回权限
REVOKE INSERT ON webapp.* FROM 'appuser'@'192.168.1.%';
REVOKE ALL PRIVILEGES ON *.* FROM 'admin'@'localhost';

-- =============================================
-- 三、角色管理（MySQL 8.0+）
-- =============================================

-- 16. 创建角色
-- CREATE ROLE 'readonly_role';
-- CREATE ROLE 'readwrite_role';

-- 17. 给角色授权
-- GRANT SELECT ON webapp.* TO 'readonly_role';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON webapp.* TO 'readwrite_role';

-- 18. 把角色授予用户
-- GRANT 'readonly_role' TO 'readonly'@'%';
-- GRANT 'readwrite_role' TO 'appuser'@'192.168.1.%';

-- =============================================
-- 四、安全配置建议
-- =============================================

-- 1. 删除匿名用户
DELETE FROM mysql.user WHERE user = '';

-- 2. 删除测试数据库
DROP DATABASE IF EXISTS test;

-- 3. 禁止 root 远程登录（删除 root 的非本地登录记录）
-- DELETE FROM mysql.user WHERE user='root' AND host NOT IN ('localhost', '127.0.0.1', '::1');

-- 4. 验证安全配置
SELECT user, host FROM mysql.user ORDER BY user, host;

-- =============================================
-- 五、密码安全
-- =============================================

-- 查看密码策略（需安装 validate_password 插件）
-- SHOW VARIABLES LIKE 'validate_password%';

-- 设置密码过期
-- ALTER USER 'webuser'@'localhost' PASSWORD EXPIRE INTERVAL 90 DAY;

-- 锁定用户
-- ALTER USER 'readonly'@'%' ACCOUNT LOCK;

-- 解锁用户
-- ALTER USER 'readonly'@'%' ACCOUNT UNLOCK;

-- =============================================
-- 清理测试用户（执行完测试后可运行）
-- =============================================
-- DROP USER 'webuser'@'localhost';
-- DROP USER 'webuser'@'127.0.0.1';
-- DROP USER 'readonly'@'%';
-- DROP USER 'appuser'@'192.168.1.%';
-- FLUSH PRIVILEGES;
