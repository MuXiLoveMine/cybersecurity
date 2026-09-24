# 移动 API 安全概述

### 4.1 REST API 安全

移动应用后端通常采用 REST API 进行通信，API 安全是移动安全的重要组成部分。

**REST API 安全要素**：

| 要素 | 说明 | 示例 |
|------|------|------|
| 传输安全 | HTTPS 强制，TLS 1.2+ | HSTS 头 |
| 认证 | Token/Session 认证 | OAuth 2.0 / JWT |
| 授权 | 资源级访问控制 | RBAC / ABAC |
| 输入验证 | 防注入攻击 | 参数白名单 |
| 速率限制 | 防暴力破解 | 5次/分钟 |
| 审计日志 | 操作可追溯 | 全量请求日志 |

### 4.2 GraphQL API 安全

GraphQL 作为灵活的查询语言，引入了新的安全挑战：

```graphql
# GraphQL 查询 - 可能导致信息过度暴露
query {
  user(id: 1) {
    id
    name
    email
    phone
    passwordHash    # 敏感字段不应暴露
    creditCard      # 敏感字段不应暴露
    orders {
      id
      amount
      billingAddress  # 敏感字段
    }
  }
}

# 深度嵌套查询 - 可能导致 DoS
query {
  user {
    friends {
      friends {
        friends {
          friends {
            # 无限嵌套导致资源耗尽
          }
        }
      }
    }
  }
}
```

**GraphQL 安全防护**：

- 查询深度限制（Max Depth）
- 查询复杂度分析（Cost Analysis）
- 字段级权限控制
- 查询白名单（Persisted Queries）
- 速率限制

### 4.3 API 认证授权机制

**常见 API 认证方式对比**：

| 方式 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| Basic Auth | Base64 编码用户名密码 | 简单 | 不安全，明文传输 |
| Session Cookie | 服务端 Session + Cookie | 成熟可靠 | 不适合移动端/分布式 |
| Bearer Token | 携带 Token 访问 | 无状态，适合移动端 | Token 泄露风险 |
| OAuth 2.0 | 授权码流程 | 标准化，安全性高 | 实现复杂 |
| JWT | 自包含 Token | 无状态，可验证 | 无法主动失效 |

---

---

