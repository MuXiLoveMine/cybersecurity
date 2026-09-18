# MongoDB Atlas安全加固

### 13.1 Atlas网络与访问控制

```bash
# 配置IP白名单(仅允许应用服务器IP)
mongocli atlas accessLists create \
    --projectId <project-id> \
    --ipAddress 10.0.1.100 \
    --comment "App Server 1"

# 配置VPC Peering(私有网络连接)
mongocli atlas privateEndpoints create \
    --projectId <project-id> \
    --provider GCP \
    --region us-east1 \
    --privateEndpointsId <endpoint-id>

# 配置网络对等连接
mongocli atlas networking peering create \
    --projectId <project-id> \
    --provider AWS \
    --awsAccountId <aws-account-id> \
    --routeTableCidr 10.0.0.0/24 \
    --vpcId <vpc-id> \
    --region us-east-1
```

### 13.2 MongoDB角色与权限管理

```javascript
// 创建自定义角色(最小权限原则)
db.createRole({
    role: "appReadUser",
    privileges: [
        {
            resource: { db: "myapp", collection: "users" },
            actions: ["find", "listCollections"]
        },
        {
            resource: { db: "myapp", collection: "orders" },
            actions: ["find", "insert", "update"]
        }
    ],
    roles: []
});

// 创建用户并分配角色
db.createUser({
    user: "app_service",
    pwd: passwordPrompt(),
    roles: [
        { role: "appReadUser", db: "myapp" }
    ]
});

// 启用审计日志
// 在mongod.conf中配置
/*
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.log
  filter: '{atype: {$in: ["authenticate","createCollection","dropCollection","createUser","dropUser","grantRole","revokeRole","renameCollection"]}}'
*/

// 查看当前用户权限
db.runCommand({usersInfo: "app_service", showPrivileges: true});

// 启用字段级加密(Client-Side Field Level Encryption)
// CSFLE配置
const fs = require('fs');
const dataKey = fs.readFileSync('./master-key.txt');

const encryptionOptions = {
  keyVaultNamespace: 'admin.datakeys',
  kmsProviders: {
    local: { key: dataKey }
  },
  schemaMap: {
    'myapp.users': {
      bsonType: 'object',
      properties: {
        ssn: {
          encrypt: {
            keyId: '/dataKeyId',
            bsonType: 'string',
            algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic'
          }
        },
        creditCard: {
          encrypt: {
            keyId: '/dataKeyId',
            bsonType: 'string',
            algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Random'
          }
        }
      }
    }
  }
};
```

---

---

## 📋 内容审核与补充建议

> 针对「MongoDB Atlas安全加固」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
