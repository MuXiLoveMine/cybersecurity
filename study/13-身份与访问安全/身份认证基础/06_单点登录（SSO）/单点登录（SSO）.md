# 单点登录（SSO）

### 6.1 SSO 基础概念

**定义**：单点登录（Single Sign-On）允许用户**一次登录**，即可访问**多个相互信任的应用系统**，无需重复认证。

**SSO 的核心价值**：

| 价值 | 说明 |
|------|------|
| 用户体验 | 只需记住一个密码，减少登录次数 |
| 安全提升 | 减少密码数量，降低泄露风险；集中管理认证策略 |
| 管理效率 | 统一身份管理，降低IT支持成本 |
| 合规审计 | 集中审计所有访问行为 |

### 6.2 SSO 架构模型

#### 集中式认证架构
```
┌─────────┐     ┌──────────────┐     ┌─────────┐
│ 应用A   │     │  认证中心     │     │ 应用B   │
│ (SP)    │<───>│  (IdP)       │<───>│ (SP)    │
└─────────┘     └──────────────┘     └─────────┘
                       │
                       v
                  ┌─────────┐
                  │ 应用C   │
                  │ (SP)    │
                  └─────────┘

IdP: Identity Provider（身份提供者）
SP: Service Provider（服务提供者）
```

### 6.3 SSO 主要协议对比

| 协议 | 发布时间 | 数据格式 | 主要用途 | 适用场景 |
|------|----------|----------|----------|----------|
| SAML | 2005 | XML | 企业级SSO | 企业内部、B2B |
| OAuth 2.0 | 2012 | JSON | 授权框架 | API授权、第三方登录 |
| OIDC | 2014 | JSON/JWT | 身份层（基于OAuth） | 现代Web/移动应用 |
| CAS | 2004 | XML/JSON | 高校SSO | 教育行业 |
| Kerberos | 1980s | 二进制 | 域环境SSO | Windows AD、企业内网 |

### 6.4 SAML 协议详解

**SAML 简介**：
- Security Assertion Markup Language
- 基于 XML 的开放标准
- OASIS 组织制定
- 企业级 SSO 的事实标准

**SAML 核心角色**：
- **主体（Principal）**：最终用户
- **身份提供者（IdP）**：负责认证和断言用户身份
- **服务提供者（SP）**：提供服务的应用，信任IdP的断言

**SAML 断言（Assertion）**：
- IdP 签发的 XML 文档
- 包含用户身份信息
- 包含认证信息（何时、如何认证）
- 数字签名保证真实性

**SAML 工作流程（SP 发起）**：

```
1. 用户访问 SP 受保护资源
   ↓
2. SP 生成 SAML AuthnRequest
   ↓
3. 用户浏览器重定向到 IdP
   ↓
4. 用户在 IdP 完成认证（如用户名密码）
   ↓
5. IdP 生成 SAML Assertion（签名）
   ↓
6. 用户浏览器 POST 到 SP 的 ACS URL
   ↓
7. SP 验证 SAML Assertion 签名
   ↓
8. SP 创建用户会话，授权访问
```

**SAML 安全风险**：
- XML 签名包装攻击（Signature Wrapping）
- 断言伪造
- 重放攻击
- 属性注入
- 未加密的断言内容

### 6.5 OAuth 2.0 简介

**OAuth 2.0 是什么**：
- 授权框架（Authorization Framework）
- **不是认证协议**
- 允许第三方应用在用户授权下访问其资源
- 使用令牌而非凭证

**OAuth 2.0 四个角色**：

| 角色 | 说明 | 示例 |
|------|------|------|
| 资源所有者 | 用户 | 你 |
| 客户端 | 第三方应用 | 某网站想用微信登录 |
| 授权服务器 | 颁发令牌的服务器 | 微信授权服务器 |
| 资源服务器 | 存储用户资源的服务器 | 微信用户信息服务器 |

**OAuth 2.0 授权码模式流程**：
```
1. 用户点击"用XX登录"
   ↓
2. 重定向到授权服务器
   ?response_type=code
   &client_id=xxx
   &redirect_uri=xxx
   &scope=xxx
   ↓
3. 用户授权（登录并确认）
   ↓
4. 重定向回客户端，携带授权码
   redirect_uri?code=xxx
   ↓
5. 客户端用授权码换取令牌
   POST /token
   grant_type=authorization_code
   &code=xxx
   &redirect_uri=xxx
   &client_id=xxx
   &client_secret=xxx
   ↓
6. 返回 Access Token
```

### 6.6 OpenID Connect (OIDC)

**OIDC 简介**：
- OpenID Connect
- 基于 OAuth 2.0 的身份层
- 提供用户认证信息
- 使用 JWT 格式的 ID Token

**OIDC 在 OAuth 2.0 基础上增加了什么**：
- **ID Token**：身份令牌，包含用户身份信息（JWT格式）
- **UserInfo 端点**：获取更多用户信息的API
- **标准化的用户信息**：sub（用户ID）、name、email等

**OIDC 三种 Token**：

| Token | 作用 | 格式 |
|-------|------|------|
| ID Token | 证明用户身份 | JWT |
| Access Token | 访问资源服务器 | 任意（通常JWT） |
| Refresh Token | 刷新Access Token | 字符串 |

---

---

## 📋 内容审核与补充建议

> 针对「单点登录（SSO）」部分的内容审核结果：

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
