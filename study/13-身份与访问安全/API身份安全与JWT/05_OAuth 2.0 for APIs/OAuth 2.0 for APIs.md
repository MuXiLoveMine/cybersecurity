# OAuth 2.0 for APIs

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

---

## 📋 内容审核与补充建议

> 针对「OAuth 2.0 for APIs」部分的内容审核结果：

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
