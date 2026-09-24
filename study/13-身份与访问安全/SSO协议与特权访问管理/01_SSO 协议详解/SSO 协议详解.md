# SSO 协议详解

### 1.1 SAML 2.0

#### SAML 架构

**SAML（Security Assertion Markup Language）** 是基于 XML 的联邦身份标准，广泛用于企业 SSO。

```
┌──────────┐                    ┌──────────┐               ┌──────────┐
│          │  ① 访问受保护资源   │          │  ② 重定向到   │          │
│   SP     │ <───────────────── │  浏览器  │ ────────────> │   IdP    │
│ (服务    │                    │ (用户)   │               │ (身份    │
│  提供方) │  ⑤ 接受 SAML断言    │          │  ③ 用户认证   │  提供方) │
│          │ <───────────────── │          │ <─────────── │          │
└──────────┘                    └──────────┘               └──────────┘
                                      │
                                      │  ④ POST SAMLResponse
                                      └──────────────────────────> SP
```

**三要素**：
- **SP（Service Provider）**：服务提供方，依赖 IdP 的断言进行授权
- **IdP（Identity Provider）**：身份提供方，认证用户并签发断言
- **Assertion（断言）**：包含用户身份和属性的 XML 文档，由 IdP 签名

**SAML 断言结构**：

```xml
<saml:Assertion Version="2.0" ID="_abc123">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <ds:Signature>  <!-- XML 数字签名 -->
    <!-- 签名覆盖整个断言 -->
  </ds:Signature>
  <saml:Subject>
    <saml:NameID Format="...:transient">user123</saml:NameID>
  </saml:Subject>
  <saml:Conditions NotBefore="2026-09-12T10:00:00Z" NotOnOrAfter="2026-09-12T10:05:00Z">
    <saml:AudienceRestriction>https://sp.example.com</saml:AudienceRestriction>
  </saml:Conditions>
  <saml:AuthnStatement AuthnInstant="2026-09-12T10:00:00Z" SessionIndex="_xyz">
    <saml:AuthnContext>
      <saml:AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport</saml:AuthnContextClassRef>
    </saml:AuthnContext>
  </saml:AuthnStatement>
  <saml:AttributeStatement>
    <saml:Attribute Name="email"><saml:AttributeValue>user@example.com</saml:AttributeValue></saml:Attribute>
    <saml:Attribute Name="role"><saml:AttributeValue>admin</saml:AttributeValue></saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

#### SAML 认证流程

```
① 用户访问 SP 的受保护资源
② SP 发现用户未登录，生成 SAMLRequest，通过浏览器重定向到 IdP
③ IdP 展示登录页面，用户输入凭证
④ IdP 验证凭证后，生成 SAMLResponse（包含签名的断言）
⑤ 浏览器通过 POST 将 SAMLResponse 发送到 SP 的 ACS（Assertion Consumer Service）端点
⑥ SP 验证断言签名、时间窗口、受众约束后，创建会话
```

#### SAML 安全攻击

**1. XML 签名包装（XSW）**

攻击者修改断言结构但保留有效签名，使 SP 验证签名通过但解析到不同的断言内容：

```xml
<!-- 原始断言（已签名） -->
<Response>
  <Assertion ID="_signed">
    <Subject>user123</Subject>
    <Signature>...</Signature>
  </Assertion>
</Response>

<!-- XSW 攻击后（签名仍覆盖原始断言，但 SP 解析了注入的断言） -->
<Response>
  <Assertion ID="_injected">
    <Subject>admin</Subject>  <!-- 注入的断言 -->
  </Assertion>
  <Assertion ID="_signed">
    <Subject>user123</Subject>
    <Signature>...</Signature>  <!-- 签名验证通过 -->
  </Assertion>
</Response>
```

**防御**：严格验证签名引用（`Reference URI`）指向唯一断言，使用安全的 XML 解析库。

**2. XXE 注入**

SAML 基于 XML，若解析器未禁用外部实体，可导致 XXE：

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<saml:Assertion>
  <saml:AttributeStatement>
    <saml:Attribute Name="email">&xxe;</saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

**防御**：禁用 DTD 处理和外部实体解析（`disallow-doctype-decl=true`）。

**3. SSRF（服务端请求伪造）**

`AssertionConsumerServiceURL` 或 `Destination` 属性若被 SP 服务端发起请求，可被利用为 SSRF。

**防御**：预注册 ACS URL，忽略断言中的动态 URL。

#### SAML 配置安全清单

| 配置项 | 安全要求 |
|--------|---------|
| 签名验证 | 验证整个 Response 或 Assertion 的签名 |
| 时间窗口 | NotBefore/NotOnOrAfter 验证，窗口不超过5分钟 |
| 受众限制 | 严格校验 AudienceRestriction |
| 证书轮换 | 使用 IdP 元数据自动更新证书 |
| DTD 处理 | 禁用 |
| 重放保护 | 验证 Assertion ID 唯一性（防重放） |
| 加密传输 | SAML Response 中的断言加密 |

---

### 1.2 OAuth 2.0

#### OAuth 四种授权模式

**OAuth 2.0** 是授权框架（注意：OAuth 不是认证协议），定义四种授权流程：

```
┌──────────────┬──────────────────────────────┬──────────────────────┐
│ 授权模式      │ 适用场景                      │ 安全性               │
├──────────────┼──────────────────────────────┼──────────────────────┤
│ 授权码模式    │ Web应用（有后端）              │ 高（推荐）           │
│ (Auth Code)  │                              │                      │
├──────────────┼──────────────────────────────┼──────────────────────┤
│ 简化模式      │ SPA/前端单页应用（无后端）     │ 中                   │
│ (Implicit)   │                              │                      │
├──────────────┼──────────────────────────────┼──────────────────────┤
│ 密码模式      │ 高度信任的第一方应用           │ 低（已废弃）         │
│ (Password)   │                              │                      │
├──────────────┼──────────────────────────────┼──────────────────────┤
│ 客户端凭证    │ 服务间调用（M2M）             │ 中                   │
│ (Client Cred)│                              │                      │
└──────────────┴──────────────────────────────┴──────────────────────┘
```

**授权码模式流程**：

```
┌────────┐          ┌──────────┐          ┌──────────┐
│ 用户   │          │  客户端   │          │ 授权服务器│
│ 浏览器 │          │ (应用)   │          │ (Auth)   │
└───┬────┘          └────┬─────┘          └────┬─────┘
    │  ① 点击登录        │                      │
    │ ──────────────────> │                      │
    │                    │  ② 重定向到授权页      │
    │ <───────────────── │                      │
    │  ③ 用户授权          │                      │
    │ ──────────────────────────────────────────> │
    │                    │  ④ 返回授权码(code)    │
    │ <──────────────────────────────────────── │
    │  ⑤ 传递code给客户端  │                      │
    │ ──────────────────> │                      │
    │                    │  ⑥ code换token        │
    │                    │ ────────────────────> │
    │                    │  ⑦ 返回access_token   │
    │                    │ <──────────────────── │
    │                    │  ⑧ 用token访问API     │
    │                    │ ────────────────────> │ Resource Server
```

#### 授权码模式 PKCE

**PKCE（Proof Key for Code Exchange）** 防止授权码截获攻击（尤其针对移动应用和 SPA）。

```
# PKCE 流程
1. 客户端生成 code_verifier（随机字符串，43-128字符）
2. 计算 code_challenge = BASE64URL(SHA256(code_verifier))
3. 发起授权请求时携带 code_challenge 和 code_challenge_method=S256
4. 授权服务器保存 code_challenge
5. 用 code 换 token 时携带 code_verifier
6. 授权服务器验证 SHA256(code_verifier) == code_challenge
```

```bash
# PKCE 授权请求示例
GET /authorize?
  response_type=code&
  client_id=myapp&
  redirect_uri=https://app.example.com/callback&
  scope=openid profile&
  code_challenge=E9Melhoa2OwvFrEMTJguCHaoeM1Zz4U&
  code_challenge_method=S256&
  state=xyz123

# Token 请求（携带 code_verifier）
POST /token
  grant_type=authorization_code&
  client_id=myapp&
  code=AUTH_CODE_HERE&
  redirect_uri=https://app.example.com/callback&
  code_verifier=dBjftJeZSzI6Z3WNk0x9kmQVH6cYwK
```

#### OAuth 安全风险

**1. Token 泄露**
- Token 存储在浏览器（localStorage/sessionStorage/cookie）
- 通过 XSS 可窃取 localStorage 中的 token
- 防御：优先使用 HttpOnly Cookie 存储，实施 CSP 防 XSS

**2. redirect_uri 劫持**

```
# 攻击场景：redirect_uri 验证不严
# 合法：redirect_uri=https://app.example.com/callback
# 攻击：redirect_uri=https://app.example.com/callback/../../../evil.com
#      或 redirect_uri=https://app.evil.com（子域名匹配）

# 防御：精确匹配 redirect_uri（白名单），不允许通配符
```

**3. CSRF 攻击**

攻击者将自己的授权码注入受害者的会话，使受害者绑定攻击者的账号。

```
# 防御：使用 state 参数（CSRF token）
GET /authorize?
  response_type=code&
  client_id=myapp&
  state=<随机不可预测值>
# 回调时验证 state 一致
```

---

### 1.3 OpenID Connect (OIDC)

#### OIDC vs OAuth

**OIDC（OpenID Connect）** 是 OAuth 2.0 之上的认证层，将 OAuth 从"授权"扩展到"认证"。

| 维度 | OAuth 2.0 | OIDC |
|------|-----------|------|
| 目的 | 授权（Access Token） | 认证 + 授权 |
| Token 类型 | Access Token | ID Token + Access Token |
| Token 格式 | 不透明 / 自定义 | JWT（标准化） |
| 用户信息 | 需调用 UserInfo 端点 | ID Token 内含 |
| 协议层级 | 框架 | 协议 |

#### ID Token 与 JWT

**ID Token** 是 JWT 格式的安全令牌，包含用户身份声明（claims）。

**JWT 结构**：`Header.Payload.Signature`

```json
// Header
{"alg": "RS256", "typ": "JWT", "kid": "key1"}

// Payload（claims）
{
  "iss": "https://idp.example.com",        // 签发者
  "sub": "user-123",                       // 用户唯一标识
  "aud": "my-app-client-id",               // 受众
  "exp": 1747000000,                       // 过期时间
  "iat": 1746996400,                       // 签发时间
  "nonce": "nonce-value",                 // 防重放
  "email": "user@example.com",
  "name": "张三",
  "roles": ["admin", "user"]
}

// Signature
RS256(base64url(header) + "." + base64url(payload), private_key)
```

**关键 claims**：
- `iss`：签发者，必须验证
- `aud`：受众，必须匹配自己的 client_id
- `exp`：过期时间，拒绝过期 token
- `nonce`：防重放，与授权请求时一致
- `sub`：用户唯一标识

#### Discovery 与元数据

```bash
# OIDC Discovery 端点（标准化）
GET /.well-known/openid-configuration

# 响应示例
{
  "issuer": "https://idp.example.com",
  "authorization_endpoint": "https://idp.example.com/authorize",
  "token_endpoint": "https://idp.example.com/token",
  "userinfo_endpoint": "https://idp.example.com/userinfo",
  "jwks_uri": "https://idp.example.com/jwks.json",
  "scopes_supported": ["openid", "profile", "email"],
  "response_types_supported": ["code", "id_token"],
  "id_token_signing_alg_values_supported": ["RS256", "ES256"]
}

# JWKS（JSON Web Key Set）获取公钥验证签名
GET /jwks.json
{
  "keys": [
    {"kty": "RSA", "kid": "key1", "use": "sig", "n": "...", "e": "AQAB"}
  ]
}
```

---

### 1.4 其他协议

#### CAS（Central Authentication Service）

CAS 是耶鲁大学开发的开源 SSO 协议，常用于教育机构。

```
CAS 认证流程：
1. 用户访问应用 → 重定向到 CAS Server 登录
2. CAS Server 认证后，重定向回应用并附带 Service Ticket（ST）
3. 应用向 CAS Server 验证 ST 有效性
4. 验证通过后建立会话

# CAS 特点：
# - 基于票据（Ticket），票据一次性使用
# - 支持 CAS 协议和 SAML 协议
# - TGT（Ticket Granting Ticket）类似 Kerberos 的 TGT
```

#### Kerberos 跨域认证

不同域之间的 Kerberos 跨域认证需要建立信任关系：

```
# 跨域认证条件：
# 1. 建立域间信任（双向或单向）
# 2. 配置跨域路由（MIT 领域需 shared key）
# 3. KDC 之间能通过 referrals 互引

# 用户 A@DOMAIN1 访问 DOMAIN2 的服务
1. A 向 DOMAIN1 的 KDC 请求 ST
2. KDC 发现服务在 DOMAIN2，返回 referral TGT（用 DOMAIN2 的 krbtgt 哈希加密）
3. A 用 referral TGT 向 DOMAIN2 的 KDC 请求 ST
4. 获得目标服务的 ST
```

---

---

