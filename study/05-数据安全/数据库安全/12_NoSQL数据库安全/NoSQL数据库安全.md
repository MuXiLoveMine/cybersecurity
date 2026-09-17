# NoSQL数据库安全

### 12.1 MongoDB安全加固

```bash
# MongoDB安全配置

# 1. 启用认证
# /etc/mongod.conf
security:
  authorization: enabled

# 2. 绑定内网IP
net:
  bindIp: 10.0.0.1
  port: 27017
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/server.pem
    CAFile: /etc/mongodb/ca.pem

# 3. 创建管理员用户
use admin
db.createUser({
    user: "admin",
    pwd: passwordPrompt(),
    roles: [
        { role: "userAdminAnyDatabase", db: "admin" },
        { role: "readWriteAnyDatabase", db: "admin" }
    ]
})

# 4. 为应用创建最小权限用户
use appdb
db.createUser({
    user: "appuser",
    pwd: passwordPrompt(),
    roles: [
        { role: "readWrite", db: "appdb" }
    ]
})

# 5. 启用审计日志
auditLog:
    destination: file
    format: JSON
    path: /var/log/mongodb/audit.log

# 6. 限制操作
# 禁用以下操作:
# - eval命令
# - $where操作符(可执行JavaScript)
# - mapReduce (可执行JS)
# - group操作
```

### 12.2 Redis安全加固

```bash
# Redis安全配置

# 1. 设置密码
# redis.conf
requirepass StrongP@ssw0rd123!

# 2. 禁用危险命令
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""

# 3. 绑定内网IP
bind 10.0.0.1

# 4. 禁用远程访问
protected-mode yes

# 5. 更改默认端口
port 6380

# 6. 启用TLS
tls-port 6379
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

# 7. 配置ACL (Redis 6+)
user default off
user appuser on >StrongP@ssw0rd ~app:* +get +set +del -@all

# 8. 限制内存和客户端
maxmemory 2gb
maxmemory-policy allkeys-lru
maxclients 1000
timeout 300
```

### 12.3 Elasticsearch安全加固

```bash
# Elasticsearch安全配置

# 1. 启用安全功能
elasticsearch.yml:
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.key: /etc/elasticsearch/tls/node.key
xpack.security.transport.ssl.certificate: /etc/elasticsearch/tls/node.crt
xpack.security.transport.ssl.certificate_authorities: /etc/elasticsearch/tls/ca.crt

# 2. 设置密码
bin/elasticsearch-setup-passwords auto

# 3. 创建角色和用户
# 使用API创建角色
PUT /_security/role/app_role
{
  "indices": [
    {
      "names": ["app-*"],
      "privileges": ["read", "write"]
    }
  ]
}

# 创建用户
POST /_security/user/appuser
{
  "password": "StrongP@ssw0rd!",
  "roles": ["app_role"],
  "full_name": "Application User"
}

# 4. 配置IP过滤
elasticsearch.yml:
transport.profiles.default.allow_default_headers: false

# 5. 审计日志
xpack.security.audit.enabled: true
xpack.security.audit.logfile.events.include: authentication_success, authentication_failed, access_denied, access_granted
```

---

---

## 📋 内容审核与补充建议

> 针对「NoSQL数据库安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
