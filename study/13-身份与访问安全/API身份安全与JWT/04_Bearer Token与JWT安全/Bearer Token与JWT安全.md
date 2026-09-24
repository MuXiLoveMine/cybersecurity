# Bearer Token与JWT安全

### 4.1 JWT结构详解

```text
JWT (JSON Web Token) 结构

格式: header.payload.signature

示例:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMEJF8HK7nq

组成部分:

1. Header (头部)
   {
     "alg": "HS256",       // 签名算法
     "typ": "JWT",         // 类型
     "kid": "key-001"      // 密钥ID (可选)
   }
   → Base64URL编码

2. Payload (载荷)
   {
     "iss": "auth.example.com",  // 签发者
     "sub": "1234567890",        // 主题(用户ID)
     "aud": "api.example.com",   // 受众
     "exp": 1516239022,          // 过期时间
     "iat": 1516200000,          // 签发时间
     "nbf": 1516200000,          // 生效时间
     "jti": "unique-id-001",     // 唯一ID
     "name": "John Doe",         // 自定义声明
     "role": "admin",            // 自定义声明
     "permissions": ["read", "write"]
   }
   → Base64URL编码
   注意: Payload不是加密的，任何人可以解码

3. Signature (签名)
   HMACSHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     secret
   )
   → 防止篡改
```

### 4.2 JWT签名算法

```text
JWT签名算法分类

1. 对称签名 (HMAC)
   ├── HS256: HMAC-SHA256
   ├── HS384: HMAC-SHA384
   └── HS512: HMAC-SHA512
   特点: 签名和验证用同一密钥
   适用: 单一服务/可信服务间

2. 非对称签名 (RSA/ECDSA)
   ├── RS256: RSA-SHA256
   ├── RS384: RSA-SHA384
   ├── RS512: RSA-SHA512
   ├── ES256: ECDSA-P256-SHA256
   ├── ES384: ECDSA-P384-SHA384
   └── ES512: ECDSA-P521-SHA512
   特点: 私钥签名，公钥验证
   适用: 多方验证/公开API

3. EdDSA
   └── EdDSA: Ed25519
   特点: 高性能非对称签名
   适用: 现代应用

选择建议:
  内部服务: HS256 (简单高效)
  公开API: RS256/ES256 (安全性好)
  高性能需求: EdDSA
  国密合规: SM2-SM3

不推荐:
  none: 无签名 (极其危险!)
  RS256 with short key: 容易被破解
```

### 4.3 JWT安全风险

```text
JWT常见安全风险

风险1: alg=none攻击
  攻击者将alg设为none → 移除签名
  部分库会接受无签名JWT → 认证绕过

风险2: 算法混淆攻击
  服务端使用RS256验证
  攻击者将alg改为HS256
  用公钥作为HMAC密钥签名
  服务端用公钥验证HS256 → 验证通过

风险3: kid注入攻击
  kid参数指定密钥ID
  攻击者注入: kid=../../etc/passwd
  或: kid=key' OR '1'='1
  导致密钥加载异常或注入

风险4: 密钥强度不足
  HMAC密钥过短 → 暴力破解
  常见弱密钥: "secret", "password", "key"

风险5: 信息泄露
  Payload不是加密的
  敏感信息放在Payload → 泄露
  例: 密码、密钥、个人身份信息

风险6: 令牌过期失效
  exp设置过长 → 令牌泄露后长期有效
  无刷新机制 → 用户体验差
  无撤销机制 → 无法主动失效

风险7: 令牌存储不安全
  localStorage → XSS可窃取
  Cookie未HttpOnly → JS可读取
  无Secure → HTTP传输泄露
```

---

---

