# MSSQL 安全

### 6.1 身份验证模式

```
-- Windows 身份验证模式（推荐）
-- 仅允许 Windows 账户登录

-- 混合模式（Windows + SQL Server 认证）
-- 在 SSMS 中设置：服务器属性 -> 安全性 -> SQL Server 和 Windows 身份验证模式
```

```sql
-- 创建 SQL Server 登录名
CREATE LOGIN app_login WITH PASSWORD = 'Str0ng!MSSQL#2024',
    CHECK_POLICY = ON,        -- 启用密码策略
    CHECK_EXPIRATION = ON;     -- 启用密码过期

-- 创建数据库用户
USE MyDatabase;
CREATE USER app_user FOR LOGIN app_login;
```

### 6.2 权限管理

```sql
-- 固定服务器角色
ALTER SERVER ROLE sysadmin ADD MEMBER app_login;  -- 危险！仅限管理员

-- 固定数据库角色
ALTER ROLE db_datareader ADD MEMBER app_user;     -- 只读
ALTER ROLE db_datawriter ADD MEMBER app_user;     -- 读写

-- 自定义数据库角色
CREATE ROLE app_executor;
GRANT EXECUTE ON SCHEMA::dbo TO app_executor;
ALTER ROLE app_executor ADD MEMBER app_user;
```

### 6.3 TDE 加密

```sql
-- 创建主密钥
USE master;
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'MasterKey!2024';

-- 创建证书
CREATE CERTIFICATE TDECert WITH SUBJECT = 'TDE Certificate';

-- 在目标库创建数据库加密密钥
USE MyDatabase;
CREATE DATABASE ENCRYPTION KEY
WITH ALGORITHM = AES_256
ENCRYPTION BY SERVER CERTIFICATE TDECert;

-- 启用 TDE
ALTER DATABASE MyDatabase SET ENCRYPTION ON;

-- 查看加密状态
SELECT db_name(database_id), encryption_state, encryption_state_desc
FROM sys.dm_database_encryption_keys;
```

### 6.4 审计（SQL Server Audit）

```sql
-- 创建服务器审计
USE master;
CREATE SERVER AUDIT ServerAudit
TO FILE (FILEPATH = 'C:\Audit\', MAXSIZE = 100 MB);

-- 创建服务器审计规范
CREATE SERVER AUDIT SPECIFICATION LoginAudit
FOR SERVER AUDIT ServerAudit
ADD (SUCCESSFUL_LOGIN_GROUP),
ADD (FAILED_LOGIN_GROUP);

-- 创建数据库审计规范
USE MyDatabase;
CREATE DATABASE AUDIT SPECIFICATION DboAudit
FOR SERVER AUDIT ServerAudit
ADD (INSERT, UPDATE, DELETE ON DATABASE::MyDatabase BY public);

-- 启用审计
ALTER SERVER AUDIT ServerAudit WITH (STATE = ON);
```

### 6.5 常见漏洞

- **xp_cmdshell**：可执行系统命令，默认禁用但常被重新开启
```sql
-- 禁用 xp_cmdshell
EXEC sp_configure 'xp_cmdshell', 0;
RECONFIGURE;
```
- **链接服务器滥用**：通过链接服务器横向移动
- **混合模式弱口令**：sa 账户使用弱密码

---

---

