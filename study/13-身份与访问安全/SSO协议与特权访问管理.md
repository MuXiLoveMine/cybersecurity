# SSO 协议与特权访问管理

> 单点登录（SSO）协议是现代身份与访问管理的基石，特权访问管理（PAM）则是高权限账户的最后防线。本文深入讲解 SAML、OAuth、OIDC 协议原理与安全风险，PAM 体系设计，以及无密码认证技术，帮助读者构建完整的身份安全知识体系。

---

## 一、SSO 协议详解

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

## 二、特权访问管理（PAM）

### 2.1 PAM 概念与必要性

**PAM（Privileged Access Management）** 是对高权限账户的发现、监控、控制和审计的系统性方案。

**为什么需要 PAM**：
- 特权账户是攻击者的首要目标（"皇冠上的宝石"）
- 内部威胁：管理员过度权限和滥用
- 合规要求（SOX、PCI-DSS、GDPR、等保2.0）
- 横向移动的跳板：一旦特权账户失陷，整个域/云环境沦陷

### 2.2 PAM 核心功能

```
┌────────────────────────────────────────────────────────┐
│                   PAM 核心功能                          │
├────────────────┬────────────────┬─────────────────────┤
│  特权账户发现   │  密码保险库     │  会话录制与审计     │
│  & 登记        │  & 自动轮换     │                    │
├────────────────┼────────────────┼─────────────────────┤
│  即时访问(JIT) │  最小权限       │  审批流程           │
│  & 临时凭证    │  & 角色控制     │  & 工作流          │
└────────────────┴────────────────┴─────────────────────┘
```

#### 特权账户发现与登记

```python
# 特权账户发现示例（扫描域环境中的高权账户）
# 依赖: pip install ldap3

from ldap3 import Server, Connection, ALL

def discover_privileged_accounts(ldap_server, bind_dn, password, base_dn):
    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=bind_dn, password=password, auto_bind=True)

    privileged_groups = [
        "Domain Admins", "Enterprise Admins", "Schema Admins",
        "Administrators", "Account Operators", "Server Operators",
        "Backup Operators", "Print Operators"
    ]

    findings = []
    for group_name in privileged_groups:
        cn = f"CN={group_name},CN=Users,{base_dn}"
        conn.search(cn, '(objectClass=group)', attributes=['member'])
        if conn.entries:
            for entry in conn.entries:
                members = entry.member.values if entry.member else []
                findings.append({'group': group_name, 'members': members})
                print(f"[+] {group_name}: {len(members)} member(s)")
    return findings
```

#### 密码保险库与自动轮换

**密码保险库**：集中存储特权账户密码，密码使用强加密保管，使用后自动轮换。

```
# 密码轮换策略
- 长期特权账户：每次使用后立即轮换
- 服务账户密码：每30-90天轮换
- 紧急访问账户（Break-Glass）：每次使用后轮换并通知
- API密钥：定期轮换 + 过期策略

# PAM 会话流程
1. 管理员请求访问 → 审批流程
2. 审批通过后 → PAM 检出密码并注入会话通道
3. 管理员通过 PAM 代理连接目标系统（密码不暴露给管理员）
4. 会话全程录制
5. 会话结束后 → PAM 自动轮换目标系统密码
```

#### 会话录制与审计

- **实时监控**：安全团队实时查看活跃会话
- **录制回放**：完整记录键盘输入和屏幕输出
- **关键字告警**：检测危险命令（rm -rf、format、shutdown）
- **行为基线**：建立正常行为模式，偏离时告警

#### 即时访问（JIT）

**JIT（Just-in-Time Access）**：按需授予临时权限，使用后自动回收。

```
传统模式（常驻权限）：
  管理员 → 拥有持续的管理员权限 → 风险高

JIT 模式（临时权限）：
  管理员 → 申请权限 → 审批 → 获得2小时临时权限 → 自动回收
```

#### 最小权限与审批流程

```
# 特权访问审批工作流
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ 申请者 │───→ │ 直属经理 │───→ │ 安全团队  │───→ │ 自动审批  │
│ 提交   │     │ 审批     │     │ 审批      │     │ 策略引擎  │
│ 请求   │     │          │     │           │     │           │
└────────┘     └──────────┘     └──────────┘     └──────────┘
                                                      │
                                            ┌──────────▼───────────┐
                                            │  授予临时权限（TTL）  │
                                            │  启动会话录制         │
                                            │  通知 SOC             │
                                            └──────────────────────┘
```

### 2.3 PAM 产品对比

| 产品 | 优势 | 适用场景 |
|------|------|---------|
| **CyberArk** | 功能最全，企业级标杆，深度AD集成 | 大型企业，复杂合规需求 |
| **BeyondTrust** | 远程访问强，支持云和IoT | 跨混合环境，远程运维 |
| **Delinea**（原Thycotic） | 部署快，UI友好，性价比高 | 中型企业，快速落地 |
| **Teleport** | 开源友好，SSH/Web/DB统一，零信任原生 | DevOps/SRE团队，云原生 |
| **HashiCorp Vault** | 基础设施即代码，API密钥管理强 | 开发团队，动态密钥 |

### 2.4 PAM 实施路线图

```
阶段1（0-3月）：发现与盘点
  ├── 盘点所有特权账户（域管/云管/数据库/网络设备/应用）
  ├── 识别过度权限和僵尸账户
  └── 建立特权账户资产台账

阶段2（3-6月）：核心部署
  ├── 部署密码保险库
  ├── 接入核心系统（域控/数据库/关键服务器）
  ├── 实施密码自动轮换
  └── 启用会话录制

阶段3（6-12月）：深化与优化
  ├── 实施 JIT 临时权限
  ├── 建立审批工作流
  ├── 集成 SIEM/SOC
  └── 覆盖云环境和 API 密钥

阶段4（12月+）：持续运营
  ├── 定期权限审查
  ├── 行为分析与异常检测
  ├── 自动化策略调优
  └── 合规报告生成
```

### 2.5 云环境 PAM

**AWS IAM 特权访问**：

```bash
# AWS IAM 临时凭证（JIT 模式）
# 使用 STS AssumeRole 获取临时凭证
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/PrivilegedRole" \
  --role-session-name "admin-session" \
  --duration-seconds 3600  # 最长1小时

# IAM Access Analyzer 检测过度权限
aws accessanalyzer create-analyzer \
  --analyzer-name production-analyzer \
  --type ACCOUNT

# Session Policies 实现权限降级
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/Role" \
  --policy '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"s3:Get*","Resource":"*"}]}'
```

**Azure PIM（Privileged Identity Management）**：

```bash
# 启用角色（JIT）
az role assignment create \
  --assignee user@example.com \
  --role "Virtual Machine Contributor" \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg} \
  --condition "@RequestTimeWithin('P1H')"  # 1小时内有效

# 查看 PIM 活动日志
az rest --method get \
  --url "https://management.azure.com/providers/Microsoft.Authorization/roleManagementPolicies?api-version=2020-10-01"
```

---

## 三、无密码认证深入

### 3.1 FIDO2 / WebAuthn 原理

**FIDO2** = **WebAuthn**（浏览器 API） + **CTAP**（客户端到认证器协议）

```
┌──────────┐                    ┌──────────┐               ┌──────────┐
│  依赖方   │                    │  浏览器   │               │ 认证器    │
│  (RP)    │                    │ (Client) │               │(Authenticator)│
└────┬─────┘                    └────┬─────┘               └────┬─────┘
     │                               │                          │
     │  ① 注册：challenge + RP ID    │                          │
     │ ────────────────────────────> │                          │
     │                               │  ② 传递到认证器            │
     │                               │ ────────────────────────> │
     │                               │                          │
     │                               │     ③ 用户验证（PIN/生物） │
     │                               │                          │
     │                               │  ④ 生成密钥对             │
     │                               │     公钥+attestation      │
     │                               │ <──────────────────────── │
     │  ⑤ 返回公钥+attestation        │                          │
     │ <──────────────────────────── │                          │
     │  ⑥ RP 存储公钥                │                          │

认证流程：
     │  ① challenge + credentialId   │                          │
     │ ────────────────────────────> │                          │
     │                               │  ② 传递到认证器            │
     │                               │ ────────────────────────> │
     │                               │     ③ 用户验证             │
     │                               │  ④ 用私钥签名challenge    │
     │                               │ <──────────────────────── │
     │  ⑤ 返回签名+authData           │                          │
     │ <──────────────────────────── │                          │
     │  ⑥ RP 用公钥验证签名           │                          │
```

**关键安全特性**：
- **非对称密钥**：私钥永不离开认证器（硬件安全模块/TEE）
- **域名绑定**：密钥对与 RP ID 绑定，防钓鱼
- **抗重放**：每次认证包含随机 challenge
- **用户存在性验证**：需要用户本地操作（触摸/PIN/生物）

### 3.2 Passkey

**Passkey** 是 FIDO2 凭证的消费级品牌名，支持跨设备同步：

```
# Passkey 类型
设备级 Passkey：
  - 存储在单一设备的安全模块中
  - 不可同步（如 YubiKey 硬件密钥）

同步 Passkey：
  - 通过 OS 厂商的云服务同步（Apple iCloud Keychain / Google Password Manager）
  - 跨设备使用，方便用户
  - 私钥在同步过程中端到端加密

# Passkey 优势
- 无需密码 → 消除密码泄露风险
- 抗钓鱼 → 域名绑定验证
- 快速认证 → 生物识别或设备PIN
```

### 3.3 生物认证安全

| 维度 | 说明 |
|------|------|
| **本地验证** | 生物特征不上传服务器，本地比对 |
| **活体检测** | 防止照片/模型欺骗（3D结构光、红外） |
| **不可撤销性** | 生物特征不可更改，泄露后果严重 |
| **FIDO 架构** | 生物认证仅作为认证器解锁手段，不作为网络传输凭证 |
| **安全等级** | FIDO2 Level 3 (L3) 要求硬件安全模块 |

---

## 四、Python SSO 安全测试脚本示例

### 4.1 JWT 安全检测脚本

```python
"""
JWT 安全检测脚本
检测项：弱签名算法、密钥泄露、claims 验证缺失、敏感信息泄露
依赖: pip install pyjwt cryptography requests
"""

import jwt
import json
import base64
import requests
from datetime import datetime


class JWTSafetyChecker:
    def __init__(self, token):
        self.token = token
        self.header = None
        self.payload = None
        self._decode_unsafe()

    def _decode_unsafe(self):
        """不验证签名地解码（仅用于安全检查）"""
        try:
            parts = self.token.split('.')
            self.header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
            self.payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
        except Exception as e:
            print(f"[!] Failed to decode JWT: {e}")

    def check_algorithm(self):
        """检查签名算法安全性"""
        alg = self.header.get('alg', 'none')
        risks = []
        if alg.lower() == 'none':
            risks.append(('CRITICAL', 'alg=none，无签名，可伪造任意内容'))
        if alg.lower() == 'hs256':
            risks.append(('WARNING', 'HS256 对称算法，若密钥泄露可伪造 token'))
        if alg.lower() in ('rs256', 'es256'):
            risks.append(('INFO', f'{alg} 非对称算法，安全性较好'))
        return risks

    def check_alg_confusion(self, public_key):
        """检测 alg 混淆攻击（RS256→HS256）"""
        try:
            # 尝试用公钥作为 HMAC 密钥验证
            jwt.decode(self.token, key=public_key, algorithms=['HS256'])
            return [('CRITICAL', 'alg 混淆攻击成功！RS256→HS256 可伪造 token')]
        except jwt.InvalidSignatureError:
            return [('OK', 'alg 混淆攻击不可行')]
        except Exception:
            return [('OK', 'alg 混淆攻击不可行')]

    def check_claims(self):
        """检查关键 claims 是否存在且合理"""
        risks = []
        required = ['iss', 'sub', 'aud', 'exp', 'iat']
        for claim in required:
            if claim not in self.payload:
                risks.append(('WARNING', f'缺少 {claim} claim'))

        exp = self.payload.get('exp')
        if exp:
            if exp > datetime.now().timestamp() + 86400:
                risks.append(('WARNING', 'exp 过长（>24h），增加 token 泄露风险窗口'))
            if exp < datetime.now().timestamp():
                risks.append(('INFO', 'token 已过期'))
        return risks

    def check_sensitive_data(self):
        """检查是否包含敏感数据"""
        sensitive_keys = ['password', 'secret', 'ssn', 'credit_card', 'api_key']
        risks = []
        for key, value in self.payload.items():
            if any(s in key.lower() for s in sensitive_keys):
                risks.append(('CRITICAL', f'Payload 包含敏感字段: {key}'))
        return risks

    def try_default_secrets(self):
        """尝试常见弱密钥"""
        common_secrets = [
            'secret', 'password', '123456', 'jwt_secret',
            'your-256-bit-secret', 'default', 'changeme'
        ]
        risks = []
        alg = self.header.get('alg', '')
        if alg.startswith('HS'):
            for secret in common_secrets:
                try:
                    jwt.decode(self.token, key=secret, algorithms=[alg])
                    risks.append(('CRITICAL', f'弱密钥爆破成功: {secret}'))
                    break
                except jwt.InvalidTokenError:
                    continue
            if not risks:
                risks.append(('OK', '常见弱密钥不可用'))
        return risks

    def run_all_checks(self, public_key=None):
        """运行所有检查"""
        print(f"[*] JWT Header: {json.dumps(self.header)}")
        print(f"[*] JWT Payload: {json.dumps(self.payload)}\n")

        all_checks = [
            ('Algorithm Security', self.check_algorithm()),
            ('Claims Validation', self.check_claims()),
            ('Sensitive Data', self.check_sensitive_data()),
            ('Default Secrets', self.try_default_secrets()),
        ]
        if public_key:
            all_checks.append(('Alg Confusion', self.check_alg_confusion(public_key)))

        for name, results in all_checks:
            print(f"[*] {name}:")
            for level, msg in results:
                print(f"    [{level}] {msg}")
            print()


if __name__ == '__main__':
    # 示例 JWT（仅用于测试）
    test_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJ0ZXN0LmlvIiwic3ViIjoiMTIzNDUiLCJhdWQiOiJteS1hcHAiLCJ"
        "leHAiOjk5OTk5OTk5OTksImlhdCI6MTU5OTk5OTk5OX0."
        "weak_signature_here"
    )
    checker = JWTSafetyChecker(test_token)
    checker.run_all_checks()
```

### 4.2 SAML 断言解析与验证脚本

```python
"""
SAML 断言解析与安全验证脚本
检测项：签名验证、时间窗口、受众、XXE、XSW
依赖: pip install lxml signxml python3-saml
"""

from lxml import etree
from signxml import XMLVerifier
from datetime import datetime, timezone
import re


class SAMLChecker:
    def __init__(self, saml_response_xml):
        """saml_response_xml: SAML Response 的 XML 字符串"""
        # 安全解析（禁用 DTD 和外部实体，防 XXE）
        parser = etree.XMLParser(
            no_network=True,
            resolve_entities=False,
            dtd_validation=False,
            huge_tree=False
        )
        self.root = etree.fromstring(saml_response_xml.encode(), parser=parser)
        self.ns = {'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
                   'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
                   'ds': 'http://www.w3.org/2000/09/xmldsig#'}

    def check_xxe(self):
        """检测 XXE 风险（已通过安全解析器消除）"""
        risks = []
        xml_text = etree.tostring(self.root).decode()
        if '<!DOCTYPE' in xml_text or '<!ENTITY' in xml_text:
            risks.append(('WARNING', '检测到 DTD/Entity，已安全过滤'))
        else:
            risks.append(('OK', '无 DTD/Entity，XXE 风险低'))
        return risks

    def check_signature(self, idp_cert):
        """验证 SAML 断言签名"""
        risks = []
        try:
            XMLVerifier().verify(self.root, x509_cert=idp_cert)
            risks.append(('OK', '签名验证通过'))
        except Exception as e:
            risks.append(('CRITICAL', f'签名验证失败: {e}'))
        return risks

    def check_conditions(self, expected_audience):
        """检查 Conditions 时间窗口和受众"""
        risks = []
        conditions = self.root.find('.//saml:Conditions', self.ns)
        if conditions is not None:
            not_before = conditions.get('NotBefore')
            not_on_or_after = conditions.get('NotOnOrAfter')
            now = datetime.now(timezone.utc)

            if not_before:
                nb = datetime.fromisoformat(not_before.replace('Z', '+00:00'))
                if now < nb:
                    risks.append(('WARNING', f'NotBefore 在未来: {not_before}'))

            if not_on_or_after:
                exp = datetime.fromisoformat(not_on_or_after.replace('Z', '+00:00'))
                if now > exp:
                    risks.append(('WARNING', f'断言已过期: {not_on_or_after}'))
                window = (exp - nb).total_seconds() if not_before else 0
                if window > 300:
                    risks.append(('WARNING', f'时间窗口过大: {window}s'))
            audience_restriction = conditions.find('.//saml:Audience', self.ns)
            if audience_restriction is not None:
                audience = audience_restriction.text
                if audience != expected_audience:
                    risks.append(('CRITICAL', f'受众不匹配: {audience}'))
                else:
                    risks.append(('OK', f'受众验证通过: {audience}'))
            else:
                risks.append(('WARNING', '缺少 AudienceRestriction'))
        else:
            risks.append(('CRITICAL', '缺少 Conditions 元素'))
        return risks

    def check_xsw(self):
        """检测 XML 签名包装攻击可能性"""
        risks = []
        assertions = self.root.findall('.//saml:Assertion', self.ns)
        if len(assertions) > 1:
            risks.append(('CRITICAL', f'检测到多个 Assertion（{len(assertions)}个），可能存在 XSW'))
        signatures = self.root.findall('.//ds:Signature', self.ns)
        for sig in signatures:
            ref = sig.find('.//ds:Reference', self.ns)
            if ref is not None:
                uri = ref.get('URI', '')
                if not uri or uri == '':
                    risks.append(('WARNING', '签名 Reference URI 为空，可能存在 XSW'))
        return risks

    def extract_claims(self):
        """提取断言中的属性声明"""
        claims = {}
        attrs = self.root.findall('.//saml:Attribute', self.ns)
        for attr in attrs:
            name = attr.get('Name')
            values = [v.text for v in attr.findall('.//saml:AttributeValue', self.ns)]
            claims[name] = values
        name_id = self.root.find('.//saml:NameID', self.ns)
        if name_id is not None:
            claims['NameID'] = name_id.text
        return claims

    def run_all_checks(self, idp_cert=None, expected_audience=None):
        """运行所有检查"""
        all_checks = [
            ('XXE Protection', self.check_xxe()),
            ('XSW Detection', self.check_xsw()),
        ]
        if idp_cert:
            all_checks.append(('Signature', self.check_signature(idp_cert)))
        if expected_audience:
            all_checks.append(('Conditions', self.check_conditions(expected_audience)))

        for name, results in all_checks:
            print(f"[*] {name}:")
            for level, msg in results:
                print(f"    [{level}] {msg}")
            print()

        claims = self.extract_claims()
        print(f"[*] Extracted Claims: {claims}")


if __name__ == '__main__':
    # 示例用法
    sample_saml = """
    <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
      <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_abc123">
        <saml:Issuer>https://idp.example.com</saml:Issuer>
        <saml:Subject>
          <saml:NameID>user@example.com</saml:NameID>
        </saml:Subject>
        <saml:Conditions NotBefore="2026-09-12T10:00:00Z" NotOnOrAfter="2026-09-12T10:05:00Z">
          <saml:AudienceRestriction>
            <saml:Audience>https://sp.example.com</saml:Audience>
          </saml:AudienceRestriction>
        </saml:Conditions>
      </saml:Assertion>
    </samlp:Response>
    """
    checker = SAMLChecker(sample_saml)
    checker.run_all_checks(expected_audience='https://sp.example.com')
```

---

## 五、总结

本文覆盖了 SSO 协议与特权访问管理的核心知识：

- **SAML 2.0**：企业 SSO 的基石，警惕 XSW/XXE/SSRF 攻击
- **OAuth 2.0**：授权框架，PKCE 是标配，严格验证 redirect_uri 和 state
- **OIDC**：认证协议，ID Token 必须验证 iss/aud/exp/nonce
- **PAM**：特权账户管理的核心——发现、轮换、录制、JIT、审批
- **无密码认证**：FIDO2/WebAuthn 是密码终结者，Passkey 兼顾安全与体验
- **安全测试**：Python 脚本可快速检测 JWT 和 SAML 安全风险

安全工程师应将这些协议的攻击面纳入渗透测试范围，同时确保 PAM 覆盖所有特权入口。
