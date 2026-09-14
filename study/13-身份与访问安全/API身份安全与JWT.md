# API身份安全与JWT

> 本文档深入讲解API身份认证与授权安全，涵盖API Key管理、Basic Auth风险、Bearer Token与JWT安全、OAuth 2.0、mTLS认证、HMAC签名验证、JWT安全风险（alg=none、密钥混淆、kid注入）及API安全最佳实践。

---

## 目录

- [一、API身份认证概述](#一api身份认证概述)
  - [1.1 API安全挑战](#11-api安全挑战)
  - [1.2 认证方式分类](#12-认证方式分类)
- [二、API Key管理](#二api-key管理)
  - [2.1 API Key原理](#21-api-key原理)
  - [2.2 API Key安全实践](#22-api-key安全实践)
- [三、Basic Auth风险分析](#三basic-auth风险分析)
  - [3.1 Basic Auth原理](#31-basic-auth原理)
  - [3.2 安全风险](#32-安全风险)
- [四、Bearer Token与JWT安全](#四bearer-token与jwt安全)
  - [4.1 JWT结构详解](#41-jwt结构详解)
  - [4.2 JWT签名算法](#42-jwt签名算法)
  - [4.3 JWT安全风险](#43-jwt安全风险)
- [五、OAuth 2.0 for APIs](#五oauth-20-for-apis)
  - [5.1 OAuth 2.0授权流程](#51-oauth-20授权流程)
  - [5.2 客户端凭证模式](#52-客户端凭证模式)
- [六、mTLS认证](#六mtls认证)
  - [6.1 mTLS原理](#61-mtls原理)
  - [6.2 证书管理](#62-证书管理)
- [七、HMAC签名验证](#七hmac签名验证)
  - [7.1 HMAC签名原理](#71-hmac签名原理)
  - [7.2 请求签名实现](#72-请求签名实现)
- [八、JWT安全漏洞详解](#八jwt安全漏洞详解)
  - [8.1 alg=none攻击](#81-algnone攻击)
  - [8.2 密钥混淆攻击](#82-密钥混淆攻击)
  - [8.3 kid注入攻击](#83-kid注入攻击)
- [九、API安全最佳实践](#九api安全最佳实践)
- [十、代码实战示例](#十代码实战示例)

---

## 一、API身份认证概述

### 1.1 API安全挑战

```text
API安全核心挑战

┌──────────────────────────────────────────────────────────┐
│                    API安全威胁                             │
├──────────────────────────────────────────────────────────┤
│ 认证威胁                                                  │
│ ├── 未授权访问: 无认证直接访问API                          │
│ ├── 凭据泄露: API Key/Token被窃取                        │
│ ├── 暴力破解: 针对认证端点的密码猜解                      │
│ └── 令牌重用: 令牌在不同上下文中重用                      │
│                                                          │
│ 授权威胁                                                  │
│ ├── 权限提升: 获取超出分配的权限                          │
│ ├── 水平越权: 访问同级用户数据                            │
│ ├── 垂直越权: 低权限访问高权限功能                        │
│ └── 功能滥用: 合法权限的非法使用                          │
│                                                          │
│ 传输威胁                                                  │
│ ├── 中间人攻击: 拦截/篡改API通信                          │
│ ├── 重放攻击: 重发有效请求                                │
│ └── 注入攻击: SQL/XSS/命令注入                           │
│                                                          │
│ 业务威胁                                                  │
│ ├── 速率滥用: 超量调用API                                 │
│ ├── 数据爬取: 批量获取数据                                │
│ └── 业务逻辑漏洞: 绕过业务约束                            │
└──────────────────────────────────────────────────────────┘
```

### 1.2 认证方式分类

| 认证方式 | 认证对象 | 安全等级 | 适用场景 |
|---------|---------|---------|---------|
| API Key | 应用/服务 | 低-中 | 服务间调用 |
| Basic Auth | 用户 | 低 | 简单认证 |
| Bearer Token/JWT | 用户/应用 | 中 | Web/移动应用 |
| OAuth 2.0 | 第三方应用 | 中-高 | 第三方授权 |
| mTLS | 服务/设备 | 高 | 服务间通信 |
| HMAC签名 | 请求 | 高 | API请求验证 |

---

## 二、API Key管理

### 2.1 API Key原理

```text
API Key认证流程

1. 申请API Key
   开发者 → API平台: 申请API Key
   API平台 → 生成: key_id + secret
   开发者: 获取并安全存储

2. 使用API Key
   开发者 → API请求: Header: X-API-Key: abc123
   API网关: 验证Key → 限制/计费
   API网关 → 路由到后端服务

3. API Key格式
   ├── 明文Key: "sk-abc123xyz..." (直接传递)
   ├── 哈希Key: 存储 Key 的哈希值
   └── 前缀Key: "pk_live_xxx" / "sk_test_xxx"

API Key vs JWT:
  API Key: 静态，长期有效，无状态
  JWT: 动态，短期有效，自包含
```

### 2.2 API Key安全实践

```python
class APIKeyManager:
    """API Key安全管理器"""

    def __init__(self):
        self.key_store = {}  # key_id → {secret_hash, permissions, rate_limit}

    def generate_api_key(self, owner, permissions, environment='production'):
        """生成API Key"""
        import secrets
        import hashlib

        # 生成Key ID和Secret
        key_id = f"key_{secrets.token_hex(8)}"
        secret = secrets.token_urlsafe(32)

        # 环境前缀
        prefix = 'sk_live_' if environment == 'production' else 'sk_test_'
        api_key = f"{prefix}{key_id}_{secret}"

        # 存储哈希值（不存储明文）
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        self.key_store[key_id] = {
            'secret_hash': secret_hash,
            'owner': owner,
            'permissions': permissions,
            'environment': environment,
            'created_at': time.time(),
            'last_used': None,
            'rate_limit': 1000  # 每分钟1000次
        }

        return {
            'api_key': api_key,
            'key_id': key_id,
            'instructions': '请安全保存API Key，不会再次显示'
        }

    def validate_api_key(self, api_key):
        """验证API Key"""
        import hashlib

        # 解析Key
        try:
            prefix, rest = api_key.split('_', 2)[0] + '_' + \
                           api_key.split('_', 2)[1], api_key.split('_', 2)[2]
            key_id, secret = rest.split('_', 1) if '_' in rest else (rest, '')
            # 更精确的解析
            parts = api_key.split('_', 2)
            key_id = parts[1]
            secret = parts[2]
        except Exception:
            return {'valid': False, 'reason': 'API Key格式错误'}

        # 查找Key
        full_key_id = f"key_{key_id}"
        if full_key_id not in self.key_store:
            return {'valid': False, 'reason': 'API Key不存在'}

        key_info = self.key_store[full_key_id]

        # 验证Secret
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        if secret_hash != key_info['secret_hash']:
            return {'valid': False, 'reason': 'API Key无效'}

        # 检查状态
        if key_info.get('revoked', False):
            return {'valid': False, 'reason': 'API Key已撤销'}

        # 更新最后使用时间
        key_info['last_used'] = time.time()

        return {
            'valid': True,
            'owner': key_info['owner'],
            'permissions': key_info['permissions'],
            'environment': key_info['environment']
        }

    def revoke_api_key(self, key_id):
        """撤销API Key"""
        if key_id in self.key_store:
            self.key_store[key_id]['revoked'] = True
            return True
        return False

    def rotate_api_key(self, key_id):
        """轮换API Key"""
        import secrets
        import hashlib

        if key_id not in self.key_store:
            return None

        new_secret = secrets.token_urlsafe(32)
        new_secret_hash = hashlib.sha256(new_secret.encode()).hexdigest()
        self.key_store[key_id]['secret_hash'] = new_secret_hash
        self.key_store[key_id]['rotated_at'] = time.time()

        return {
            'api_key': f"sk_live_{key_id.replace('key_', '')}_{new_secret}",
            'key_id': key_id
        }


import time

# 演示
def demo_api_key():
    manager = APIKeyManager()

    # 生成
    result = manager.generate_api_key(
        owner='developer@example.com',
        permissions=['read:users', 'write:posts'],
        environment='production'
    )
    print(f"生成的API Key: {result['api_key'][:30]}...")

    # 验证
    valid = manager.validate_api_key(result['api_key'])
    print(f"验证结果: {valid['valid']}, 权限: {valid.get('permissions')}")

    # 撤销
    manager.revoke_api_key(result['key_id'])
    valid = manager.validate_api_key(result['api_key'])
    print(f"撤销后验证: {valid['valid']}, 原因: {valid.get('reason')}")


if __name__ == "__main__":
    demo_api_key()
```

---

## 三、Basic Auth风险分析

### 3.1 Basic Auth原理

```text
Basic Auth认证原理

请求格式:
  GET /api/v1/users HTTP/1.1
  Host: api.example.com
  Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=

其中 "dXNlcm5hbWU6cGFzc3dvcmQ=" 是 "username:password" 的Base64编码

验证流程:
  1. 客户端: username:password → Base64编码 → Authorization Header
  2. 服务端: Base64解码 → 提取username:password → 验证凭据
  3. 成功: 返回数据
  4. 失败: 返回401 Unauthorized
```

### 3.2 安全风险

```text
Basic Auth安全风险

风险1: 明文传输（如果不用HTTPS）
  Base64 ≠ 加密
  Base64可以轻易解码
  如果HTTP传输 → 凭据暴露

风险2: 凭据长期有效
  username:password不会过期
  泄露后需要修改密码
  无法临时撤销

风险3: 无法细粒度授权
  只有用户级权限
  无法区分API操作权限

风险4: 无法限制来源
  任何拿到凭据的人都能使用
  无IP绑定/设备绑定

风险5: 审计困难
  所有请求用同一凭据
  无法区分不同客户端

结论: Basic Auth仅适用于简单场景
  必须配合HTTPS使用
  不推荐用于生产API
```

---

## 四、Bearer Token与JWT安全

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

## 五、OAuth 2.0 for APIs

### 5.1 OAuth 2.0授权流程

```text
OAuth 2.0授权码流程 (Authorization Code Flow)

┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  用户    │    │ 客户端   │    │ 授权服务  │    │ 资源服务  │
│ (User)  │    │ (Client)│    │ (Auth)   │    │ (API)    │
└─────┬────┘    └────┬────┘    └────┬─────┘    └────┬─────┘
      │              │              │               │
      │  1. 点击授权  │              │               │
      │─────────────►│              │               │
      │              │  2. 重定向到授权页面          │
      │              │─────────────►│               │
      │  3. 登录+授权 │              │               │
      │◄─────────────────────────────│               │
      │              │  4. 回调+授权码│               │
      │              │◄─────────────│               │
      │              │  5. 用码换令牌│               │
      │              │─────────────►│               │
      │              │  6. Access Token              │
      │              │◄─────────────│               │
      │              │  7. 用Token访问API            │
      │              │──────────────────────────────►│
      │              │  8. 返回数据                  │
      │              │◄──────────────────────────────│

令牌类型:
├── Access Token: 用于API访问（短期，1小时）
├── Refresh Token: 用于刷新Access Token（长期，30天）
└── ID Token: 用户身份信息（OIDC）
```

### 5.2 客户端凭证模式

```python
"""
OAuth 2.0 客户端凭证模式 (Client Credentials)
适用于服务间认证
"""

import requests
import time
import base64
import hashlib
import secrets

class OAuth2Client:
    """OAuth 2.0客户端"""

    def __init__(self, token_endpoint, client_id, client_secret,
                 scope='api.read api.write'):
        self.token_endpoint = token_endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token = None
        self.token_expiry = 0

    def get_token(self):
        """获取Access Token（客户端凭证模式）"""
        # 检查现有Token是否有效
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        # 请求新Token
        response = requests.post(
            self.token_endpoint,
            data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': self.scope
            }
        )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expiry = time.time() + token_data.get('expires_in', 3600)
            return self.access_token
        else:
            raise Exception(f"获取Token失败: {response.status_code} {response.text}")

    def api_request(self, method, url, **kwargs):
        """带认证的API请求"""
        token = self.get_token()
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        return requests.request(method, url, headers=headers, **kwargs)


# 授权服务器端
from flask import Flask, request as flask_request, jsonify

app = Flask(__name__)

# 客户端注册信息
REGISTERED_CLIENTS = {
    'client_001': {
        'client_secret': 'super_secret_value',
        'scope': 'api.read api.write',
        'name': 'Service A'
    }
}

# 生成的Token
ACTIVE_TOKENS = {}


@app.route('/oauth/token', methods=['POST'])
def issue_token():
    """颁发Token"""
    grant_type = flask_request.form.get('grant_type')
    client_id = flask_request.form.get('client_id')
    client_secret = flask_request.form.get('client_secret')
    scope = flask_request.form.get('scope', '')

    # 验证客户端
    if client_id not in REGISTERED_CLIENTS:
        return jsonify({'error': 'invalid_client'}), 401

    client = REGISTERED_CLIENTS[client_id]
    if client['client_secret'] != client_secret:
        return jsonify({'error': 'invalid_client'}), 401

    if grant_type == 'client_credentials':
        # 生成Access Token
        token = secrets.token_urlsafe(32)
        ACTIVE_TOKENS[token] = {
            'client_id': client_id,
            'scope': scope,
            'issued_at': time.time(),
            'expires_in': 3600
        }

        return jsonify({
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'scope': scope
        })

    return jsonify({'error': 'unsupported_grant_type'}), 400


@app.route('/api/v1/protected')
def protected_api():
    """受保护的API"""
    auth_header = flask_request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return jsonify({'error': 'invalid_token'}), 401

    token = auth_header[7:]
    if token not in ACTIVE_TOKENS:
        return jsonify({'error': 'invalid_token'}), 401

    token_info = ACTIVE_TOKENS[token]
    if time.time() - token_info['issued_at'] > token_info['expires_in']:
        del ACTIVE_TOKENS[token]
        return jsonify({'error': 'token_expired'}), 401

    return jsonify({
        'message': '访问成功',
        'client': token_info['client_id'],
        'scope': token_info['scope']
    })
```

---

## 六、mTLS认证

### 6.1 mTLS原理

```text
mTLS (双向TLS) 认证原理

标准TLS (单向):
  客户端 → 验证服务器证书 → 建立连接
  服务器不验证客户端

mTLS (双向):
  客户端 → 验证服务器证书 → 发送客户端证书
  服务器 → 验证客户端证书 → 建立连接
  双向身份验证

mTLS认证流程:
  1. ClientHello + 客户端证书请求
  2. ServerHello + 服务器证书 + 请求客户端证书
  3. 客户端验证服务器证书
  4. 客户端发送自己的证书
  5. 服务器验证客户端证书
  6. 密钥交换
  7. 建立加密通道

mTLS优势:
  ✓ 基于证书的身份认证
  ✓ 非对称加密，安全性高
  ✓ 证书可包含身份和权限信息
  ✓ 证书可撤销（CRL/OCSP）
  ✓ 传输加密一体化

mTLS适用场景:
  ├── 服务间通信（微服务）
  ├── API网关认证
  ├── IoT设备认证
  └── 高安全API访问
```

### 6.2 证书管理

```text
mTLS证书管理体系

┌────────────────────────────────────────────────────┐
│                  根CA (Root CA)                     │
│              签发中间CA证书                         │
└──────────────────────┬─────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ 服务器CA   │  │ 客户端CA   │  │ API网关CA  │
│ 签发服务器 │  │ 签发客户端 │  │ 签发网关   │
│ 证书      │  │ 证书      │  │ 证书      │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │               │               │
       ▼               ▼               ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ API服务 │    │ 客户端  │    │ API网关 │
  │ 证书   │    │ 证书   │    │ 证书   │
  └─────────┘    └─────────┘    └─────────┘

证书生命周期:
├── 生成: 生成密钥对和CSR
├── 签发: CA验证并签发证书
├── 部署: 安装到服务/客户端
├── 轮换: 定期更换证书
├── 撤销: 通过CRL/OCSP撤销
└── 过期: 证书到期后更新
```

```python
# mTLS配置示例 (Python requests)

import requests

# 客户端证书和私钥
CLIENT_CERT = '/path/to/client.crt'
CLIENT_KEY = '/path/to/client.key'
CA_CERT = '/path/to/ca.crt'

# mTLS请求
def mtls_api_call(url, method='GET', data=None):
    """mTLS认证的API请求"""
    response = requests.request(
        method,
        url,
        cert=(CLIENT_CERT, CLIENT_KEY),  # 客户端证书
        verify=CA_CERT,                   # 验证服务器证书
        json=data
    )
    return response


# Nginx mTLS配置示例
NGINX_MTLS_CONFIG = """
server {
    listen 443 ssl;
    server_name api.example.com;

    # 服务器证书
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # 要求客户端证书
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    # API路由
    location /api/v1/ {
        # 检查客户端证书验证
        if ($ssl_client_verify != SUCCESS) {
            return 403;
        }

        # 传递客户端证书信息
        proxy_set_header X-Client-Verify $ssl_client_verify;
        proxy_set_header X-Client-DN $ssl_client_s_dn;
        proxy_set_header X-Client-Cert $ssl_client_escaped_cert;

        proxy_pass http://backend:8080;
    }
}
"""
```

---

## 七、HMAC签名验证

### 7.1 HMAC签名原理

```text
HMAC API签名认证原理

原理:
  使用共享密钥对请求内容生成HMAC签名
  服务端用相同密钥验证签名
  不传输密钥本身，只传签名

签名内容:
  HTTP方法 + URI + 请求体哈希 + 时间戳 + nonce

签名过程:
  1. 构造签名字符串:
     string_to_sign = method + "\n" + path + "\n" + body_hash + "\n" + timestamp
  2. 计算HMAC:
     signature = HMAC-SHA256(string_to_sign, secret_key)
  3. 发送:
     Authorization: HMAC-SHA256 Credential=ACCESS_KEY, SignedHeaders=..., Signature=...

验证过程:
  1. 解析Authorization头
  2. 获取ACCESS_KEY → 查找对应的SECRET_KEY
  3. 重新构造签名字符串
  4. 重新计算HMAC
  5. 比较签名

优势:
  ✓ 无状态（不需要维护Token）
  ✓ 防篡改（签名覆盖请求内容）
  ✓ 防重放（时间戳+nonce）
  ✓ 性能好（HMAC比RSA快）
```

### 7.2 请求签名实现

```python
import hmac
import hashlib
import base64
import time
import secrets

class HMACSigner:
    """HMAC请求签名器"""

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key.encode('utf-8')

    def sign_request(self, method, path, body=b'', headers=None):
        """签名请求"""
        if headers is None:
            headers = {}

        # 生成时间戳和nonce
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(8)

        # 计算请求体哈希
        body_hash = hashlib.sha256(body).hexdigest()

        # 构造签名字符串
        string_to_sign = '\n'.join([
            method.upper(),
            path,
            body_hash,
            timestamp,
            nonce
        ])

        # 计算HMAC-SHA256
        signature = hmac.new(
            self.secret_key,
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()

        signature_b64 = base64.b64encode(signature).decode('utf-8')

        # 设置请求头
        headers['X-Auth-AccessKey'] = self.access_key
        headers['X-Auth-Timestamp'] = timestamp
        headers['X-Auth-Nonce'] = nonce
        headers['X-Auth-Signature'] = signature_b64

        return headers

    @staticmethod
    def verify_request(method, path, body, headers, get_secret_func):
        """验证请求签名"""
        access_key = headers.get('X-Auth-AccessKey', '')
        timestamp = headers.get('X-Auth-Timestamp', '')
        nonce = headers.get('X-Auth-Nonce', '')
        signature_b64 = headers.get('X-Auth-Signature', '')

        if not all([access_key, timestamp, nonce, signature_b64]):
            return False, '缺少认证参数'

        # 验证时间戳新鲜性（5分钟内）
        try:
            ts = int(timestamp)
            if abs(time.time() - ts) > 300:
                return False, '时间戳过期'
        except ValueError:
            return False, '时间戳无效'

        # 获取密钥
        secret_key = get_secret_func(access_key)
        if not secret_key:
            return False, '无效的Access Key'

        # 重新构造签名字符串
        if isinstance(body, str):
            body = body.encode('utf-8')
        body_hash = hashlib.sha256(body).hexdigest()

        string_to_sign = '\n'.join([
            method.upper(),
            path,
            body_hash,
            timestamp,
            nonce
        ])

        # 重新计算HMAC
        expected_signature = hmac.new(
            secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).digest()

        expected_b64 = base64.b64encode(expected_signature).decode('utf-8')

        # 比较签名（常量时间比较）
        if not hmac.compare_digest(signature_b64, expected_b64):
            return False, '签名验证失败'

        return True, '验证通过'


# 演示
def demo_hmac_signing():
    """HMAC签名演示"""
    access_key = 'AKID1234567890'
    secret_key = 'super_secret_key_value'

    signer = HMACSigner(access_key, secret_key)

    # 签名请求
    method = 'POST'
    path = '/api/v1/users'
    body = b'{"name": "John", "email": "john@example.com"}'

    signed_headers = signer.sign_request(method, path, body)

    print("签名后的请求头:")
    for k, v in signed_headers.items():
        print(f"  {k}: {v[:40]}{'...' if len(v) > 40 else ''}")

    # 验证
    def get_secret(ak):
        if ak == access_key:
            return secret_key
        return None

    valid, reason = HMACSigner.verify_request(
        method, path, body, signed_headers, get_secret
    )
    print(f"\n验证结果: {valid}, {reason}")

    # 篡改测试
    tampered_body = b'{"name": "Hacker", "email": "hacker@evil.com"}'
    valid, reason = HMACSigner.verify_request(
        method, path, tampered_body, signed_headers, get_secret
    )
    print(f"篡改后验证: {valid}, {reason}")


if __name__ == "__main__":
    demo_hmac_signing()
```

---

## 八、JWT安全漏洞详解

### 8.1 alg=none攻击

```text
alg=none攻击详解

漏洞原理:
  JWT标准允许alg=none（无签名）
  部分JWT库在alg=none时跳过签名验证
  攻击者可以构造任意Payload

攻击步骤:
  1. 获取一个合法JWT
  2. 解码Header: {"alg":"HS256","typ":"JWT"}
  3. 修改Header: {"alg":"none","typ":"JWT"}
  4. 修改Payload: {"sub":"admin","role":"superuser"}
  5. 签名设为空: header.payload.
  6. 发送伪造JWT

防御措施:
  1. 在代码中显式禁止alg=none
  2. 指定允许的算法白名单
  3. 使用更新的JWT库
  4. 永远不信任Header中的alg值
```

```python
import jwt
import base64
import json

class JWTNoneAttack:
    """演示alg=none攻击与防御"""

    @staticmethod
    def create_none_jwt():
        """创建alg=none的JWT"""
        # Header
        header = {"alg": "none", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).rstrip(b'=').decode()

        # Payload (修改为admin)
        payload = {
            "sub": "admin",
            "role": "superuser",
            "exp": 9999999999  # 远期过期
        }
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b'=').decode()

        # 签名为空
        jwt_token = f"{header_b64}.{payload_b64}."

        return jwt_token

    @staticmethod
    def vulnerable_verify(token, secret):
        """有漏洞的验证（不检查alg）"""
        try:
            # 漏洞: 不指定允许的算法
            payload = jwt.decode(token, secret, options={'verify_exp': False})
            return payload
        except Exception:
            return None

    @staticmethod
    def secure_verify(token, secret):
        """安全的验证"""
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=['HS256'],  # 明确指定算法
                options={
                    'verify_exp': True,
                    'verify_signature': True,  # 必须验证签名
                    'require': ['exp', 'iat', 'sub']  # 必需声明
                }
            )
            return payload
        except Exception as e:
            return {'error': str(e)}


def demo_none_attack():
    """alg=none攻击演示"""
    secret = 'my_secret'
    attacker = JWTNoneAttack()

    # 生成alg=none的JWT
    fake_token = attacker.create_none_jwt()
    print(f"伪造JWT: {fake_token[:50]}...")

    # 有漏洞的验证
    result = attacker.vulnerable_verify(fake_token, secret)
    print(f"有漏洞验证: {result}")

    # 安全的验证
    result = attacker.secure_verify(fake_token, secret)
    print(f"安全验证: {result}")


if __name__ == "__main__":
    demo_none_attack()
```

### 8.2 密钥混淆攻击

```text
密钥混淆攻击 (Algorithm Confusion / Key Confusion)

漏洞原理:
  服务端使用RS256(非对称): 私钥签名，公钥验证
  攻击者获取公钥
  将JWT的alg改为HS256(对称)
  用公钥作为HMAC密钥签名
  服务端用公钥验证HS256 → 通过

攻击步骤:
  1. 获取服务端公钥（通常公开）
  2. 修改JWT Header: alg: RS256 → HS256
  3. 修改Payload: 任意内容
  4. 用公钥作为HMAC密钥签名
  5. 发送伪造JWT

防御措施:
  1. 明确指定算法: algorithms=['RS256']
  2. 不要信任Header中的alg
  3. 分离HS256和RS256的密钥
  4. 使用不同的密钥对用于不同算法
```

```python
class KeyConfusionAttack:
    """密钥混淆攻击演示"""

    @staticmethod
    def attack(public_key_pem):
        """
        使用公钥伪造HS256 JWT
        """
        # 获取公钥内容
        public_key_bytes = public_key_pem.encode('utf-8')

        # 构造Header: 声称使用HS256
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = base64.urlsafe_b64encode(
            json.dumps(header).encode()
        ).rstrip(b'=').decode()

        # 构造Payload
        payload = {"sub": "admin", "role": "superuser"}
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b'=').decode()

        # 用公钥作为HMAC密钥签名
        message = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(public_key_bytes, message, hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

        return f"{header_b64}.{payload_b64}.{sig_b64}"

    @staticmethod
    def defense():
        """防御策略"""
        return {
            'strategy_1': '验证时明确指定算法白名单: algorithms=["RS256"]',
            'strategy_2': '不信任JWT Header中的alg字段',
            'strategy_3': '对称和非对称密钥完全分离',
            'strategy_4': '使用jwk_set时验证密钥类型与算法匹配',
            'strategy_5': '使用库的strict模式（如PyJWT的strict_mode）'
        }
```

### 8.3 kid注入攻击

```text
kid注入攻击 (Key ID Injection)

漏洞原理:
  JWT Header中的kid字段用于指定使用哪个密钥
  服务端根据kid从密钥库查找对应密钥
  如果kid处理不当，可能被注入

攻击类型:

1. 目录遍历
   kid: "../../../../dev/null"
   → 使用/dev/null的空内容作为密钥
   → 攻击者用空密钥签名

2. SQL注入
   kid: "key' UNION SELECT 'attacker_secret' --"
   → 注入SQL获取攻击者控制的密钥
   → 攻击者用已知密钥签名

3. 命令注入
   kid: "key; cat /etc/shadow"
   → 可能执行系统命令

4. SSRF
   kid: "http://attacker.com/key"
   → 服务端请求攻击者控制的URL获取密钥

防御措施:
  1. kid白名单验证
  2. kid格式限制（仅字母数字）
  3. 参数化查询
  4. 不从外部URL加载密钥
  5. 使用jku/jwk时验证信任域
```

---

## 九、API安全最佳实践

```text
API安全最佳实践清单

[认证与授权]
□ 使用OAuth 2.0 / JWT替代API Key/Basic Auth
□ JWT使用RS256/ES256非对称签名
□ 明确指定算法白名单（不允许alg=none）
□ 实施最小权限原则
□ 使用scope限制API访问范围
□ 高敏感操作需要MFA
□ 定期轮换API密钥和JWT密钥

[JWT安全]
□ 设置合理的过期时间（1小时）
□ 实施刷新令牌机制
□ 使用jti防止重放
□ 验证iss/aud/sub
□ 不在Payload中存储敏感信息
□ 使用HTTPS传输JWT
□ 安全存储JWT（HttpOnly Cookie）

[传输安全]
□ 强制使用HTTPS（TLS 1.2+）
□ 实施HSTS
□ 考虑mTLS用于服务间通信
□ 使用证书固定(Certificate Pinning)

[请求安全]
□ 实施速率限制
□ 输入验证和参数白名单
□ 请求大小限制
□ SQL注入防护（参数化查询）
□ XSS防护（输出编码）
□ CSRF防护（SameSite Cookie）

[API网关]
□ 统一入口管理
□ 认证授权前置
□ 请求路由和过滤
□ 速率限制和配额
□ API版本管理
□ 请求/响应日志
□ WAF集成

[监控与审计]
□ 记录所有API访问日志
□ 异常请求检测
□ 认证失败告警
□ 权限变更审计
□ 数据访问审计
□ 安全事件响应

[密钥管理]
□ 使用KMS管理密钥
□ 密钥分级管理
□ 定期轮换
□ 访问控制
□ 使用HSM保护根密钥
```

---

## 十、代码实战示例

### 10.1 完整的JWT安全验证中间件

```python
"""
JWT安全验证中间件 - 包含所有安全检查
"""

import jwt
import time
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify, g

class JWTSecurityMiddleware:
    """JWT安全验证中间件"""

    def __init__(self, public_key, private_key=None):
        self.public_key = public_key  # RS256公钥
        self.private_key = private_key  # RS256私钥（签发用）
        self.allowed_algorithms = ['RS256']  # 算法白名单
        self.required_claims = ['sub', 'iat', 'exp', 'iss', 'aud']
        self.trusted_issuers = {'https://auth.example.com'}
        self.trusted_audiences = {'api.example.com'}
        self.revoked_jtis = set()  # 已撤销的JWT ID

    def sign_token(self, payload, expiry_seconds=3600):
        """签发JWT"""
        now = int(time.time())
        import secrets

        full_payload = {
            **payload,
            'iss': 'https://auth.example.com',
            'aud': 'api.example.com',
            'iat': now,
            'nbf': now,
            'exp': now + expiry_seconds,
            'jti': secrets.token_urlsafe(16)  # 唯一ID
        }

        token = jwt.encode(
            full_payload,
            self.private_key,
            algorithm='RS256',
            headers={'typ': 'JWT', 'kid': 'key-001'}
        )

        return token

    def verify_token(self, token):
        """验证JWT - 安全检查"""
        try:
            # 1. 解码Header（不验证签名先看）
            unverified_header = jwt.get_unverified_header(token)

            # 2. 检查算法白名单
            alg = unverified_header.get('alg')
            if alg not in self.allowed_algorithms:
                return {'valid': False, 'reason': f'不允许的算法: {alg}'}

            if alg == 'none' or alg is None:
                return {'valid': False, 'reason': '无签名JWT被拒绝'}

            # 3. 验证签名和声明
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=self.allowed_algorithms,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_nbf': True,
                    'verify_aud': True,
                    'verify_iss': True,
                    'require': self.required_claims
                },
                issuer=list(self.trusted_issuers),
                audience=list(self.trusted_audiences)
            )

            # 4. 检查JTI是否已撤销
            jti = payload.get('jti')
            if jti and jti in self.revoked_jtis:
                return {'valid': False, 'reason': '令牌已被撤销'}

            return {'valid': True, 'payload': payload}

        except jwt.ExpiredSignatureError:
            return {'valid': False, 'reason': '令牌已过期'}
        except jwt.InvalidAudienceError:
            return {'valid': False, 'reason': '无效的受众'}
        except jwt.InvalidIssuerError:
            return {'valid': False, 'reason': '无效的签发者'}
        except jwt.InvalidAlgorithmError:
            return {'valid': False, 'reason': '无效的算法'}
        except jwt.InvalidTokenError as e:
            return {'valid': False, 'reason': f'无效令牌: {str(e)}'}
        except Exception as e:
            return {'valid': False, 'reason': f'验证异常: {str(e)}'}

    def revoke_token(self, jti):
        """撤销JWT"""
        self.revoked_jtis.add(jti)

    def require_auth(self, f):
        """认证装饰器"""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')

            if not auth_header.startswith('Bearer '):
                return jsonify({'error': '缺少认证令牌'}), 401

            token = auth_header[7:]
            result = self.verify_token(token)

            if not result['valid']:
                return jsonify({
                    'error': '认证失败',
                    'reason': result['reason']
                }), 401

            # 注入用户信息
            g.current_user = result['payload']

            return f(*args, **kwargs)

        return decorated

    def require_permission(self, permission):
        """权限装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                user = getattr(g, 'current_user', None)
                if not user:
                    return jsonify({'error': '未认证'}), 401

                permissions = user.get('permissions', [])
                if permission not in permissions:
                    return jsonify({
                        'error': '权限不足',
                        'required': permission
                    }), 403

                return f(*args, **kwargs)
            return decorated
        return decorator


# 使用示例
app = Flask(__name__)

# 生成RSA密钥对
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key_obj = rsa.generate_private_key(public_exponent=65537, key_size=2048)
private_pem = private_key_obj.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
public_pem = private_key_obj.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

jwt_middleware = JWTSecurityMiddleware(public_pem, private_pem)

@app.route('/api/v1/login', methods=['POST'])
def login():
    """登录获取JWT"""
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'secret':
        token = jwt_middleware.sign_token({
            'sub': 'user_001',
            'name': 'Admin',
            'role': 'admin',
            'permissions': ['read:users', 'write:users', 'delete:users']
        })
        return jsonify({'access_token': token, 'token_type': 'Bearer'})
    return jsonify({'error': '认证失败'}), 401

@app.route('/api/v1/users')
@jwt_middleware.require_auth
@jwt_middleware.require_permission('read:users')
def list_users():
    """获取用户列表（需要read:users权限）"""
    return jsonify({
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ],
        'requested_by': g.current_user.get('name')
    })

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
@jwt_middleware.require_auth
@jwt_middleware.require_permission('delete:users')
def delete_user(user_id):
    """删除用户（需要delete:users权限）"""
    return jsonify({'success': True, 'deleted': user_id})
```

---

> **参考文献：**
> - RFC 7519: JSON Web Token (JWT)
> - RFC 6749: The OAuth 2.0 Authorization Framework
> - RFC 8446: TLS 1.3
> - OWASP API Security Top 10
> - OWASP JWT Cheat Sheet
> - Auth0 JWT Best Practices

---

*本文档为网络安全学习资料，所涉及的安全漏洞技术仅用于安全研究和防御目的。*
