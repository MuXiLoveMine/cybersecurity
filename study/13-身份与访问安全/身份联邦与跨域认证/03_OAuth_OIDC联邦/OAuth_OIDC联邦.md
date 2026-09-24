# OAuth/OIDC联邦

### 3.1 OIDC联邦架构

```text
OIDC联邦架构 (OpenID Connect Federation)

OIDC联邦通过联邦信任链实现多组织信任:

┌──────────────────────────────────────────────────────┐
│              联邦权威 (Federation Authority)           │
│          (Trust Anchor / 根信任锚)                     │
│        签发联邦操作者证书                               │
└──────────────────────┬───────────────────────────────┘
                       │ 签发
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 中间CA       │ │ 中间CA       │ │ 中间CA       │
│ (Org A)     │ │ (Org B)     │ │ (Org C)     │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │签发              │签发            │签发
       ▼                  ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ IdP/SP      │ │ IdP/SP      │ │ IdP/SP      │
│ (实体A)     │ │ (实体B)     │ │ (实体C)     │
└──────────────┘ └──────────────┘ └──────────────┘

信任链验证:
  实体A → 联邦权威 的信任链:
  联邦权威签名 → 中间CA签名 → 实体A
  验证: 验证签名链直至信任锚

OIDC联邦元数据:
  每个实体发布元数据声明:
  ├── OIDC配置端点
  ├── 支持的范围
  ├── 公钥(JWK Set)
  ├── 联邦角色
  └── 联邦信任链
```

```python
class OIDCFederation:
    """OIDC联邦实现"""

    def __init__(self, entity_id, role='OP'):
        """
        :param entity_id: 实体标识URL
        :param role: 'OP'(OpenID Provider) 或 'RP'(Relying Party)
        """
        self.entity_id = entity_id
        self.role = role
        self.federation_endpoints = {}
        self.trust_anchors = {}  # 信任锚
        self.trusted_entities = {}  # 已验证信任的实体

    def get_federation_metadata(self):
        """获取联邦元数据"""
        metadata = {
            'iss': self.entity_id,
            'sub': self.entity_id,
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,
            'jwks': {
                'keys': [
                    {'kty': 'RSA', 'kid': 'key-001',
                     'use': 'sig', 'n': '...', 'e': 'AQAB'}
                ]
            },
            'metadata': {
                self.role: {
                    'issuer': self.entity_id,
                    'authorization_endpoint': f'{self.entity_id}/auth',
                    'token_endpoint': f'{self.entity_id}/token',
                    'jwks_uri': f'{self.entity_id}/jwks',
                    'response_types_supported': ['code'],
                    'subject_types_supported': ['public'],
                    'id_token_signing_alg_values_supported': ['RS256'],
                    'scopes_supported': ['openid', 'profile', 'email']
                }
            }
        }

        if self.role == 'OP':
            metadata['metadata'][self.role].update({
                'userinfo_endpoint': f'{self.entity_id}/userinfo',
                'token_endpoint_auth_methods_supported': [
                    'client_secret_basic',
                    'client_secret_post',
                    'private_key_jwt'
                ]
            })

        return metadata

    def establish_trust(self, target_entity_id, trust_anchor_metadata):
        """建立信任关系"""
        # 1. 获取目标实体元数据
        target_metadata = self._fetch_entity_statement(target_entity_id)

        # 2. 验证信任链
        trust_chain = self._verify_trust_chain(
            target_entity_id, trust_anchor_metadata
        )

        if trust_chain['valid']:
            self.trusted_entities[target_entity_id] = {
                'metadata': target_metadata,
                'trust_chain': trust_chain,
                'trust_anchor': trust_anchor_metadata
            }
            return True
        return False

    def _fetch_entity_statement(self, entity_id):
        """获取实体声明"""
        # 实际通过HTTP获取
        return {
            'iss': entity_id,
            'sub': entity_id,
            'metadata': {}
        }

    def _verify_trust_chain(self, entity_id, trust_anchor):
        """验证信任链"""
        # 简化验证
        return {
            'valid': True,
            'chain': [entity_id, trust_anchor.get('entity_id', '')]
        }

    def generate_authorization_request(self, client_id, redirect_uri,
                                         scope='openid profile'):
        """生成授权请求"""
        import urllib.parse

        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': self._generate_state(),
            'nonce': self._generate_nonce()
        }

        auth_url = f"{self.entity_id}/auth?{urllib.parse.urlencode(params)}"
        return {
            'url': auth_url,
            'state': params['state'],
            'nonce': params['nonce']
        }

    @staticmethod
    def _generate_state():
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def _generate_nonce():
        import secrets
        return secrets.token_urlsafe(32)


import time
```

### 3.2 联邦信任传递

```text
OIDC联邦信任传递机制

信任传递过程:
  联邦权威 → 中间CA → 实体
  
  每一层签发实体声明(Entity Statement)
  实体声明包含:
  ├── 签发者(iss)
  ├── 主题(sub)
  ├── 元数据(metadata)
  ├── 公钥(jwks)
  ├── 约束(constraints)
  └── 签名(signature)

信任链验证:
  1. RP需要访问OP
  2. RP获取OP的实体声明
  3. RP验证信任链: OP → 中间CA → 联邦权威
  4. 信任锚验证通过 → 信任OP
  5. 使用OP的元数据进行OIDC认证

信任约束:
  ├── 范围限制: 限制实体可以请求的范围
  ├── 操作限制: 限制实体可以执行的操作
  ├── 时间限制: 信任有效期
  └── 层级限制: 最大信任链长度
```

---

---

