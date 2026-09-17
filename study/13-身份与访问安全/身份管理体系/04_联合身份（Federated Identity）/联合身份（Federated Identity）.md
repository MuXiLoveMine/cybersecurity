# 联合身份（Federated Identity）

### 4.1 什么是身份联邦

**身份联邦（Identity Federation）**：在不同的安全域（组织、系统）之间建立信任关系，使得一个域中的身份可以被另一个域信任和使用。

**核心价值**：
- 跨组织访问无需创建新账号
- 用户体验好（一次登录多处访问）
- 减少身份管理成本
- 企业间合作更便捷

**联邦模型**：

```
模型1：一对多（一个IdP，多个SP）
┌──────┐
│ IdP  │ ←── 统一身份源
└──┬───┘
   ├──→ SP1 (应用A)
   ├──→ SP2 (应用B)
   └──→ SP3 (应用C)

模型2：多对多（联邦枢纽）
┌──────┐        ┌──────┐
│ IdP1 │ ←────→ │      │
├──────┤        │ 联邦  │ ←────→ SP1
│ IdP2 │ ←────→ │ 枢纽  │ ←────→ SP2
├──────┤        │      │ ←────→ SP3
│ IdP3 │ ←────→ │      │
└──────┘        └──────┘
```

### 4.2 联邦身份标准协议

#### SAML 2.0

**SAML（Security Assertion Markup Language）**：基于 XML 的联邦身份标准，企业级 SSO 的主流协议。

**核心组件**：
- **断言（Assertion）**：IdP 签发的身份声明（XML格式）
- **协议（Protocol）**：请求和响应的格式
- **绑定（Binding）**：如何传输消息（HTTP重定向、POST等）
- **配置文件（Profile）**：特定场景的使用方式

**SAML 断言内容**：
```xml
<saml:Assertion>
  <!-- 断言签发者 -->
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  
  <!-- 主体（用户） -->
  <saml:Subject>
    <saml:NameID>user@example.com</saml:NameID>
  </saml:Subject>
  
  <!-- 认证声明 -->
  <saml:AuthnStatement AuthnInstant="2024-01-15T10:00:00Z">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>PasswordProtectedTransport</saml:AuthnContextClassRef>
    </saml:AuthnContext>
  </saml:AuthnStatement>
  
  <!-- 属性声明 -->
  <saml:AttributeStatement>
    <saml:Attribute Name="cn">
      <saml:AttributeValue>张三</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="email">
      <saml:AttributeValue>zhangsan@example.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="department">
      <saml:AttributeValue>IT部门</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

#### OAuth 2.0

**OAuth 2.0**：授权框架，用于第三方应用授权，也是现代联邦身份的基础。

**四种授权模式**：

| 模式 | 适用场景 | 安全性 |
|------|----------|--------|
| 授权码模式 | 服务端Web应用 | 高 |
| 隐式模式 | 纯前端应用（已不推荐） | 中 |
| 密码模式 | 高度信任的客户端 | 低 |
| 客户端模式 | 服务间调用（无用户） | 中 |

**授权码模式流程详解**：
```
┌──────────┐          ┌──────────┐          ┌──────────┐
│  用户浏览器 │          │  客户端   │          │ 授权服务器 │
└────┬─────┘          └────┬─────┘          └────┬─────┘
     │                     │                     │
     │ 1. 点击登录按钮      │                     │
     │────────────────────→│                     │
     │                     │                     │
     │ 2. 重定向到授权页面  │                     │
     │←────────────────────│                     │
     │                     │                     │
     │ 3. 用户授权          │                     │
     │─────────────────────────────────────────→│
     │                     │                     │
     │ 4. 返回授权码        │                     │
     │←─────────────────────────────────────────│
     │                     │                     │
     │ 5. 携带授权码回调    │                     │
     │────────────────────→│                     │
     │                     │                     │
     │ 6. 用授权码换令牌    │                     │
     │                     │────────────────────→│
     │                     │                     │
     │                     │ 7. 返回令牌         │
     │                     │←────────────────────│
     │                     │                     │
     │ 8. 登录成功          │                     │
     │←────────────────────│                     │
```

#### OpenID Connect (OIDC)

**OIDC**：在 OAuth 2.0 之上构建的身份层，提供认证功能。

**OIDC 新增内容**：
- **ID Token**：身份令牌（JWT格式），包含用户身份信息
- **UserInfo 端点**：获取更多用户信息的API
- **标准的用户声明**：sub、name、email、picture等

**ID Token 示例（JWT Payload）**：
```json
{
  "iss": "https://idp.example.com",      // 签发者
  "sub": "user-12345",                   // 用户唯一标识
  "aud": "client-app-1",                 // 受众
  "exp": 1705312800,                     // 过期时间
  "iat": 1705309200,                     // 签发时间
  "name": "张三",                        // 姓名
  "email": "zhangsan@example.com",       // 邮箱
  "email_verified": true,                // 邮箱是否验证
  "picture": "https://.../avatar.jpg",   // 头像
  "amr": ["pwd", "mfa"]                  // 认证方法
}
```

### 4.3 SCIM

**SCIM（System for Cross-domain Identity Management）**：跨域身份管理系统，用于身份信息的自动化同步。

**SCIM 的作用**：
- 自动化用户和组的创建、更新、删除
- 标准化的 REST API
- 减少手工操作和配置错误

**SCIM 资源模型**：
```
/User          用户资源
/Group         组资源
/Schemas       模式定义
/ResourceTypes 资源类型
```

**SCIM API 示例**：
```
# 创建用户
POST /scim/v2/Users
Content-Type: application/scim+json

{
  "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
  "userName": "zhangsan",
  "name": {
    "givenName": "三",
    "familyName": "张"
  },
  "emails": [
    { "value": "zhangsan@example.com", "primary": true }
  ],
  "active": true
}
```

---

---

## 📋 内容审核与补充建议

> 针对「联合身份（Federated Identity）」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
