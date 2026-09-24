# FIDO2与WebAuthn

### 9.1 FIDO2架构

```text
FIDO2标准体系

FIDO2 = WebAuthn + CTAP

WebAuthn (Web Authentication):
├── W3C标准
├── 浏览器API
├── 网站与认证器之间的认证协议
└── 替代密码的Web认证

CTAP (Client to Authenticator Protocol):
├── FIDO Alliance标准
├── 客户端与认证器之间的通信协议
├── CTAP1: 基于U2F的USB/NFC协议
└── CTAP2: 支持平台认证器和更多功能

核心概念:
├── 认证器 (Authenticator): 存储密钥的设备
│   ├── 平台认证器: 内置于设备（如TouchID）
│   ├── 漫游认证器: 外部设备（如YubiKey）
│   └── 安全密钥: USB/NFC/BLE

├── 依赖方 (Relying Party, RP): 网站或应用
│   └── 依赖认证器进行用户认证

├── 凭据 (Credential):
│   ├── 公钥: 发送给RP存储
│   └── 私钥: 存储在认证器中，不可导出

└── 挑战 (Challenge):
    └── RP生成的随机数，防重放

FIDO2安全特性:
├── 非对称加密: 私钥不离开认证器
├── 域绑定: 密钥绑定到特定域名
├── 防钓鱼: 不同域名使用不同密钥
├── 用户验证: 生物识别/PIN
├── 设备绑定: 绑定到特定认证器
├── 多设备: 可注册多个认证器
└── 无密码: 替代传统密码
```

### 9.2 WebAuthn流程

```text
WebAuthn注册流程

1. RP生成挑战
   RP → 浏览器: PublicKeyCredentialCreationOptions
   包含:
   ├── challenge: 随机挑战值
   ├── rp: {name, id} (RP信息)
   ├── user: {id, name, displayName} (用户信息)
   ├── pubKeyCredParams: 支持的算法
   ├── authenticatorSelection: 认证器要求
   │   ├── userVerification: required/preferred/discouraged
   │   ├── authenticatorAttachment: platform/cross-platform
   │   └── requireResidentKey: 是否需要存储用户信息
   └── excludeCredentials: 排除已注册的凭据

2. 浏览器调用认证器
   浏览器 → 认证器: navigator.credentials.create(options)
   用户: 进行生物识别/PIN验证

3. 认证器生成密钥对
   认证器:
   ├── 生成非对称密钥对
   ├── 私钥安全存储(不可导出)
   ├── 生成凭据ID
   ├── 用RP的公钥签名attestation
   └── 返回: {credentialId, publicKey, attestation}

4. 浏览器返回结果
   浏览器 → RP: AuthenticatorAttestationResponse
   包含:
   ├── clientDataJSON: 客户端数据
   ├── attestationObject: 认证器签名数据
   └── 包含公钥和签名

5. RP验证并存储
   RP:
   ├── 验证challenge
   ├── 验证origin
   ├── 验证attestation签名
   ├── 存储公钥和凭据ID
   └── 注册完成

WebAuthn认证流程

1. RP生成挑战
   RP → 浏览器: PublicKeyCredentialRequestOptions
   包含:
   ├── challenge: 随机挑战值
   ├── rpId: RP标识
   ├── allowCredentials: 允许的凭据列表
   └── userVerification: 验证要求

2. 浏览器调用认证器
   浏览器 → 认证器: navigator.credentials.get(options)
   用户: 生物识别/PIN验证

3. 认证器签名
   认证器:
   ├── 用私钥签名(challenge + origin + counter)
   ├── 返回签名和计数器
   └── counter: 防克隆(每次递增)

4. RP验证
   RP:
   ├── 验证challenge
   ├── 验证origin
   ├── 验证签名(用存储的公钥)
   ├── 验证计数器(必须递增)
   └── 认证完成
```

```python
"""
WebAuthn服务端验证实现
"""
import base64
import json
import secrets
import hashlib

class WebAuthnServer:
    """WebAuthn服务端"""

    def __init__(self, rp_id, rp_name, origin):
        self.rp_id = rp_id  # 例: "example.com"
        self.rp_name = rp_name
        self.origin = origin  # 例: "https://example.com"
        self.registered_credentials = {}  # user_id → [credentials]

    def generate_registration_options(self, user_id, username,
                                        user_display_name):
        """生成注册选项"""
        challenge = secrets.token_bytes(32)

        options = {
            'challenge': base64.urlsafe_b64encode(challenge).decode(),
            'rp': {
                'name': self.rp_name,
                'id': self.rp_id
            },
            'user': {
                'id': base64.urlsafe_b64encode(user_id.encode()).decode(),
                'name': username,
                'displayName': user_display_name
            },
            'pubKeyCredParams': [
                {'type': 'public-key', 'alg': -7},   # ES256
                {'type': 'public-key', 'alg': -257},  # RS256
            ],
            'authenticatorSelection': {
                'authenticatorAttachment': 'platform',
                'userVerification': 'required',
                'requireResidentKey': False
            },
            'timeout': 60000,
            'excludeCredentials': []
        }

        return options, challenge

    def verify_registration(self, user_id, credential_response,
                             expected_challenge):
        """验证注册响应"""
        try:
            # 解析clientDataJSON
            client_data = json.loads(
                base64.urlsafe_b64decode(
                    credential_response['clientDataJSON']
                ).decode()
            )

            # 验证类型
            if client_data.get('type') != 'webauthn.create':
                return {'success': False, 'error': '错误的类型'}

            # 验证挑战
            received_challenge = base64.urlsafe_b64decode(
                client_data['challenge']
            )
            if received_challenge != expected_challenge:
                return {'success': False, 'error': '挑战不匹配'}

            # 验证来源
            if client_data.get('origin') != self.origin:
                return {'success': False, 'error': '来源不匹配'}

            # 解析attestationObject（简化）
            # 实际需要解析CBOR格式
            # 提取公钥和凭据ID

            # 存储凭据
            credential_id = credential_response.get('id', '')
            public_key = b'extracted_public_key'  # 实际从attestation提取

            if user_id not in self.registered_credentials:
                self.registered_credentials[user_id] = []

            self.registered_credentials[user_id].append({
                'credential_id': credential_id,
                'public_key': public_key,
                'counter': 0,
                'created_at': int(time.time())
            })

            return {
                'success': True,
                'credential_id': credential_id,
                'message': '注册成功'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_authentication_options(self, user_id):
        """生成认证选项"""
        challenge = secrets.token_bytes(32)

        # 获取用户已注册的凭据
        credentials = self.registered_credentials.get(user_id, [])
        allow_credentials = [
            {'type': 'public-key', 'id': c['credential_id']}
            for c in credentials
        ]

        options = {
            'challenge': base64.urlsafe_b64encode(challenge).decode(),
            'rpId': self.rp_id,
            'allowCredentials': allow_credentials,
            'userVerification': 'required',
            'timeout': 60000
        }

        return options, challenge

    def verify_authentication(self, user_id, assertion_response,
                                expected_challenge):
        """验证认证断言"""
        try:
            # 解析clientDataJSON
            client_data = json.loads(
                base64.urlsafe_b64decode(
                    assertion_response['clientDataJSON']
                ).decode()
            )

            # 验证类型
            if client_data.get('type') != 'webauthn.get':
                return {'success': False, 'error': '错误的类型'}

            # 验证挑战
            received_challenge = base64.urlsafe_b64decode(
                client_data['challenge']
            )
            if received_challenge != expected_challenge:
                return {'success': False, 'error': '挑战不匹配'}

            # 验证来源
            if client_data.get('origin') != self.origin:
                return {'success': False, 'error': '来源不匹配'}

            # 验证签名
            credential_id = assertion_response.get('id', '')
            authenticator_data = base64.urlsafe_b64decode(
                assertion_response['authenticatorData']
            )
            signature = base64.urlsafe_b64decode(
                assertion_response['signature']
            )

            # 查找凭据
            credentials = self.registered_credentials.get(user_id, [])
            credential = None
            for c in credentials:
                if c['credential_id'] == credential_id:
                    credential = c
                    break

            if not credential:
                return {'success': False, 'error': '凭据未找到'}

            # 验证签名（使用存储的公钥）
            # 实际需要用公钥验证签名
            # verify(credential['public_key'], signature, data)

            # 验证计数器（防克隆）
            # 从authenticatorData中提取计数器
            new_counter = int.from_bytes(authenticator_data[33:37], 'big')
            if new_counter <= credential['counter']:
                return {'success': False, 'error': '计数器异常(可能的克隆攻击)'}

            credential['counter'] = new_counter

            return {
                'success': True,
                'user_id': user_id,
                'message': '认证成功'
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}


import time

# 演示
def demo_webauthn():
    """WebAuthn演示"""
    server = WebAuthnServer(
        rp_id='example.com',
        rp_name='Example App',
        origin='https://example.com'
    )

    print("=" * 50)
    print("WebAuthn流程演示")
    print("=" * 50)

    # 注册
    print("\n1. 注册流程")
    options, challenge = server.generate_registration_options(
        user_id='user_001',
        username='john@example.com',
        user_display_name='John Doe'
    )
    print(f"   RP ID: {options['rp']['id']}")
    print(f"   Challenge: {options['challenge'][:20]}...")
    print(f"   支持算法: {[p['alg'] for p in options['pubKeyCredParams']]}")

    # 模拟认证器响应（实际由浏览器/认证器生成）
    mock_response = {
        'id': 'cred_001',
        'clientDataJSON': base64.urlsafe_b64encode(
            json.dumps({
                'type': 'webauthn.create',
                'challenge': base64.urlsafe_b64encode(challenge).decode(),
                'origin': 'https://example.com'
            }).encode()
        ).decode(),
        'attestationObject': base64.urlsafe_b64encode(b'mock').decode()
    }

    result = server.verify_registration('user_001', mock_response, challenge)
    print(f"   注册结果: {result['success']}, {result.get('message')}")

    # 认证
    print("\n2. 认证流程")
    auth_options, auth_challenge = server.generate_authentication_options(
        'user_001'
    )
    print(f"   RP ID: {auth_options['rpId']}")
    print(f"   Challenge: {auth_options['challenge'][:20]}...")
    print(f"   允许凭据: {len(auth_options['allowCredentials'])}个")


if __name__ == "__main__":
    demo_webauthn()
```

---

---

