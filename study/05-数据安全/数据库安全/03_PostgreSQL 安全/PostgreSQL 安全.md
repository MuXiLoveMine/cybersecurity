# PostgreSQL 安全

### 3.1 pg_hba.conf 认证配置

```
# TYPE  DATABASE  USER    ADDRESS       METHOD
# 本地连接使用 peer 认证
local   all       all                   peer
# 内网连接使用 scram-sha-256
host    all       all     10.0.0.0/24   scram-sha-256
# 拒绝外部网络连接
host    all       all     0.0.0.0/0     reject
```

### 3.2 角色与权限管理

```sql
-- 创建角色并设置密码
CREATE ROLE app_user LOGIN PASSWORD 'Secure#Pass456';

-- 授予 schema 权限
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO app_user;

-- 设置默认权限（后续新建的表自动授权）
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO app_user;

-- 创建只读角色
CREATE ROLE readonly LOGIN PASSWORD 'Read0nly!';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

### 3.3 行级安全（RLS）

```sql
-- 启用行级安全
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2)
);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 仅允许用户查看自己的订单
CREATE POLICY orders_policy ON orders
    USING (user_id = current_setting('app.current_user_id')::int);

-- 管理员不受 RLS 限制
ALTER TABLE orders FORCE ROW LEVEL SECURITY;
-- 超级用户和 BYPASSRLS 角色不受限
```

### 3.4 审计（pgAudit）

```sql
-- 安装 pgAudit 扩展
CREATE EXTENSION pgaudit;

-- 在 postgresql.conf 中配置
-- pgaudit.log = 'write, ddl, role'
-- pgaudit.log_parameter = on

-- 查看审计日志
SELECT * FROM pg_stat_activity;
```

### 3.5 数据加密（pgcrypto）

```sql
-- 创建扩展
CREATE EXTENSION pgcrypto;

-- 加密存储
INSERT INTO secrets (data) VALUES (pgp_sym_encrypt('机密内容', 'my_secret_key'));

-- 解密读取
SELECT pgp_sym_decrypt(data, 'my_secret_key') FROM secrets;

-- 使用 hash 函数
INSERT INTO users (username, password_hash)
VALUES ('admin', crypt('password123', gen_salt('bf')));
```

---

---

