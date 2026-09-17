# MySQL 安全

### 2.1 安全加固清单

```sql
-- 1. 设置强 root 密码
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Str0ng!Pass#2024';

-- 2. 删除匿名账户
DELETE FROM mysql.user WHERE User='';
FLUSH PRIVILEGES;

-- 3. 禁止 root 远程登录，仅允许本地
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost','127.0.0.1');
FLUSH PRIVILEGES;

-- 4. 删除测试数据库
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%';

-- 5. 修改默认端口（在 my.cnf 中配置）
-- [mysqld]
-- port=33060

-- 6. 限制文件导入导出
-- 在 my.cnf 中添加
-- secure_file_priv=/var/lib/mysql-files
```

### 2.2 权限管理

```sql
-- 创建应用专用账户，遵循最小权限原则
CREATE USER 'webapp'@'10.0.0.%' IDENTIFIED BY 'App$ecret123';

-- 仅授予业务所需的 SELECT/INSERT/UPDATE 权限
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'webapp'@'10.0.0.%';

-- 授予特定表权限（更细粒度）
GRANT SELECT ON mydb.user_info TO 'webapp'@'10.0.0.%';

-- 查看用户权限
SHOW GRANTS FOR 'webapp'@'10.0.0.%';

-- 撤销权限
REVOKE UPDATE ON mydb.* FROM 'webapp'@'10.0.0.%';

-- 删除用户
DROP USER 'webapp'@'10.0.0.%';
```

### 2.3 审计日志

```sql
-- General Query Log（记录所有查询，生产环境慎用）
SET GLOBAL general_log = 'ON';
SET GLOBAL general_log_file = '/var/log/mysql/general.log';

-- Slow Query Log（记录慢查询）
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;

-- MySQL Enterprise Audit Plugin（企业版）
-- 安装审计插件
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
-- 在 my.cnf 中配置
-- plugin_audit_log=FORCE_PLUS_PERMANENT
-- audit_log_format=JSON
```

### 2.4 数据加密（TDE）

```sql
-- MySQL 透明数据加密（企业版 InnoDB 加密）
-- 安装 keyring 插件
INSTALL PLUGIN keyring_file SONAME 'keyring_file.so';

-- 创建加密表空间
CREATE TABLESPACE encrypted_ts ADD DATAFILE 'encrypted.ibd' ENCRYPTION='Y';

-- 创建表时指定加密
CREATE TABLE sensitive_data (
    id INT PRIMARY KEY,
    ssn VARCHAR(20)
) TABLESPACE encrypted_ts ENCRYPTION='Y';
```

### 2.5 备份与恢复安全

```bash
# 加密逻辑备份
mysqldump -u root -p mydb | openssl enc -aes-256-cbc -salt -pbkdf2 -out backup.sql.enc

# 恢复
openssl enc -d -aes-256-cbc -pbkdf2 -in backup.sql.enc | mysql -u root -p mydb

# 物理备份（Percona XtraBackup，支持加密）
xtrabackup --backup --target-dir=/backup --encrypt=AES256 \
  --encrypt-key-file=/etc/mysql/encrypt.key
```

### 2.6 MySQL 常见漏洞

- **SQL 注入**：未参数化拼接 SQL 导致数据泄露
- **CVE-2021-2154**：MySQL Server Optimizer 组件越权漏洞
- **CVE-2022-21427**：Server: Replication 组件提权漏洞
- **UDF 提权**：通过加载恶意 `.so` 文件执行系统命令

---

---

## 📋 内容审核与补充建议

> 针对「MySQL 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
