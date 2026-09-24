# MongoDB 安全

### 4.1 认证配置

```yaml
# mongod.conf - 启用认证
security:
  authorization: enabled

# 使用 SCRAM 认证（默认）
# 使用 X.509 证书认证
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/server.pem
    CAFile: /etc/mongodb/ca.pem
```

```javascript
// 创建管理员用户
use admin
db.createUser({
  user: "admin",
  pwd: passwordPrompt(),  // 交互式输入密码
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})

// 创建业务库专用用户
use mydb
db.createUser({
  user: "appUser",
  pwd: "App@secure789",
  roles: [{ role: "readWrite", db: "mydb" }]
})
```

### 4.2 授权（内置角色）

| 角色 | 权限范围 |
|------|----------|
| `read` | 只读 |
| `readWrite` | 读写 |
| `dbAdmin` | 数据库管理 |
| `userAdmin` | 用户管理 |
| `readWriteAnyDatabase` | 所有库读写 |
| `root` | 超级管理员 |

```javascript
// 自定义角色
use admin
db.createRole({
  role: "customReadWrite",
  privileges: [
    { resource: { db: "mydb", collection: "" }, actions: ["find", "insert", "update", "remove"] }
  ],
  roles: []
})
```

### 4.3 网络安全

```yaml
# mongod.conf - 绑定内网地址
net:
  bindIp: 10.0.0.10
  port: 27017
  tls:
    mode: requireTLS
```

### 4.4 加密

- **传输加密**：TLS/SSL 配置（如上）
- **静态加密**：MongoDB Enterprise 的 WiredTiger 加密引擎

```yaml
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb/encryption-key
```

### 4.5 常见安全问题

- **未授权访问**：默认配置不启用认证，导致数据库暴露
- **默认端口 27017 暴露**：大量 MongoDB 实例因绑定 0.0.0.0 而被公开访问
- **检查命令**：`mongosh --eval "db.adminCommand('listDatabases')"` 无认证即返回数据说明存在风险

---

---

