# 第6章 API密钥与令牌安全

### 6.1 API密钥最佳实践

#### 6.1.1 API密钥设计原则

**密钥命名规范：**
- 使用前缀标识环境和用途：`sk_live_`、`sk_test_`、`pk_prod_`
- 密钥长度建议：至少32字节的随机数据（base64编码后约43字符）
- 包含可校验前缀，便于快速识别

**安全设计：**
1. **服务端只存储哈希值**：类似密码，API密钥也应哈希存储
2. **密钥指纹**：使用密钥的前几位或哈希值作为标识
3. **过期机制**：设置密钥有效期，支持自动过期
4. **速率限制**：每个密钥独立的速率限制
5. **IP白名单**：高安全等级的密钥可绑定IP

#### 6.1.2 API密钥存储与传输

**传输安全：**
- 必须使用HTTPS传输
- 禁止在URL参数中传递API密钥（会被日志记录）
- 使用Authorization请求头传递
- 避免在客户端（浏览器、移动APP）存储长期API密钥

**正确方式：**
```http
GET /api/v1/users HTTP/1.1
Host: api.example.com
Authorization: Bearer sk_live_abc123def456...
```

**错误方式：**
```http
GET /api/v1/users?api_key=sk_live_abc123... HTTP/1.1
Host: api.example.com
```

**服务端存储：**
```python
import hashlib
import secrets
import hmac

def generate_api_key(prefix: str = "sk") -> tuple[str, str]:
    """生成API密钥，返回(明文密钥, 哈希值)"""
    raw_key = secrets.token_bytes(32)
    api_key = f"{prefix}_{raw_key.hex()}"
    # 使用SHA-256哈希存储
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key, key_hash

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """验证API密钥"""
    computed_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return hmac.compare_digest(computed_hash, stored_hash)
```

#### 6.1.3 API密钥生命周期管理

**创建阶段：**
- 明确密钥的用途和所有者
- 设置适当的权限范围（Scope）
- 设置过期时间
- 记录创建人和创建时间

**使用阶段：**
- 监控每个密钥的使用情况
- 检测异常使用模式
- 定期审查密钥的必要性

**轮换阶段：**
- 支持双密钥并行（新旧密钥同时有效）
- 提供轮换过渡期（建议7-30天）
- 通知密钥所有者进行更新

**撤销阶段：**
- 支持立即撤销和定时撤销
- 记录撤销原因
- 审计撤销前的使用记录

### 6.2 OAuth令牌安全管理

#### 6.2.1 OAuth 2.0令牌类型

**Access Token（访问令牌）：**
- 用于访问受保护资源
- 生命周期短（通常15分钟到1小时）
- 应使用短有效期减少泄露风险
- 泄露后影响范围受限于权限和有效期

**Refresh Token（刷新令牌）：**
- 用于获取新的访问令牌
- 生命周期长（天/周/月级别）
- 必须安全存储（服务端安全存储）
- 泄露危害更大，需严格保护

**ID Token（身份令牌）：**
- JWT格式，包含用户身份信息
- 仅用于身份认证，不用于授权
- 有明确的受众（audience）限制

#### 6.2.2 令牌安全最佳实践

**Access Token安全：**
- 使用短有效期（15-30分钟）
- 遵循令牌受众（audience）限制
- 验证令牌签名和有效期
- 实现令牌撤销机制（Token Revocation）

**Refresh Token安全：**
- 服务端安全存储（加密存储）
- 绑定客户端信息（IP、User-Agent）
- 使用旋转刷新令牌（Rotation Refresh Token）
- 设置合理的有效期和闲置超时
- 支持立即撤销

**前端应用令牌安全：**
- 单页应用（SPA）使用Authorization Code + PKCE流程
- 避免在localStorage中存储令牌（XSS风险）
- 使用HttpOnly + Secure Cookie存储刷新令牌
- 实现令牌自动续期和过期处理

#### 6.2.3 令牌泄露应对

**检测令牌泄露：**
- 异常的地理位置访问
- 同一令牌多处同时使用
- 令牌使用量异常增加
- 异常的API调用模式

**应对措施：**
1. 立即撤销泄露的令牌
2. 撤销关联的刷新令牌
3. 通知用户重新认证
4. 审计令牌使用记录
5. 加强安全措施（MFA、设备绑定）

### 6.3 JWT安全配置

#### 6.3.1 JWT结构回顾

JWT（JSON Web Token）由三部分组成：Header.Payload.Signature

**Header：**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload：**
```json
{
  "sub": "user123",
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "exp": 1704067200,
  "iat": 1704063600,
  "scope": "read write"
}
```

#### 6.3.2 JWT常见安全问题

**1. 算法混淆攻击（Alg=none）**
攻击者将alg设置为none，服务器如果支持none算法就会接受无签名的令牌。

**防护：**
```python
# 明确指定允许的算法，禁用none
import jwt

decoded = jwt.decode(
    token,
    public_key,
    algorithms=["RS256", "ES256"],  # 白名单方式
    options={"verify_signature": True}
)
```

**2. 弱密钥（HS256 + 弱密钥）**
使用HS256算法时，如果密钥强度不足，攻击者可以暴力破解。

**防护：**
- HS256密钥长度至少256位（32字节随机字符串）
- 优先使用非对称算法（RS256、ES256）
- 定期轮换签名密钥

**3. 未验证所有声明（Claims）**
只验证签名而不验证exp、iss、aud等声明。

**必须验证的声明：**
- `exp`：过期时间
- `nbf`：生效时间
- `iss`：签发者
- `aud`：受众
- `iat`：签发时间（用于检测异常早的令牌）

#### 6.3.3 JWT安全最佳实践

```python
import jwt
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def create_jwt(user_id: str, private_key_path: str) -> str:
    """安全创建JWT"""
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iss": "https://auth.example.com",
        "aud": "https://api.example.com",
        "iat": now,
        "exp": now + 900,  # 15分钟过期
        "nbf": now,
        "jti": generate_unique_id(),  # 令牌唯一标识，用于撤销
    }
    
    return jwt.encode(payload, private_key, algorithm="RS256")

def verify_jwt(token: str, public_key_path: str) -> dict:
    """安全验证JWT"""
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(
            f.read(), backend=default_backend()
        )
    
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="https://api.example.com",
        issuer="https://auth.example.com",
        options={
            "require": ["exp", "iat", "sub", "iss", "aud"],
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": True,
        }
    )
```

---

---

## 📋 内容审核与补充建议

> 针对「第6章 API密钥与令牌安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
