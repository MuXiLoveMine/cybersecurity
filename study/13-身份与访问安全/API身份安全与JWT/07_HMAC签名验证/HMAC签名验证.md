# HMAC签名验证

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

---

