# RSA数字签名

### 3.1 RSA签名原理

RSA签名利用RSA公钥密码算法的特性实现：

```
RSA算法基本操作：
  加密: c = m^e mod n   （用公钥加密）
  解密: m = c^d mod n   （用私钥解密）
  
RSA签名（反过来用）：
  签名: s = hash(m)^d mod n   （用私钥签名）
  验证: hash(m) = s^e mod n   （用公钥验证）
  
其中:
  n = p * q  （模数）
  e = 公钥指数
  d = 私钥指数
```

### 3.2 RSA签名填充方案

直接对哈希值进行RSA运算是**不安全**的，需要使用填充方案。

#### 3.2.1 PKCS#1 v1.5填充

**PKCS#1 v1.5** 是最传统的RSA签名填充方案。

```
PKCS#1 v1.5签名格式：
  0x00 || 0x01 || PS || 0x00 || T
  
  其中:
    0x00, 0x01: 固定头部
    PS: 填充字节 0xFF...0xFF
    0x00: 分隔符
    T: DigestInfo（哈希算法OID + 哈希值）
  
  DigestInfo结构:
    SHA-256: 30 31 30 0d 06 09 60 86 48 01 65 03 04 02 01 05 00 04 20 [hash]
    SHA-384: 30 41 30 0d 06 09 60 86 48 01 65 03 04 02 02 05 00 04 30 [hash]
    SHA-512: 30 51 30 0d 06 09 60 86 48 01 65 03 04 02 03 05 00 04 40 [hash]
```

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

class RSASignature:
    """RSA签名实现"""
    
    def __init__(self, key_size: int = 2048):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        self.public_key = self.private_key.public_key()
    
    def sign_pkcs1v15(self, message: bytes) -> bytes:
        """PKCS#1 v1.5签名"""
        signature = self.private_key.sign(
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature
    
    def verify_pkcs1v15(self, message: bytes, signature: bytes) -> bool:
        """PKCS#1 v1.5验证"""
        try:
            self.public_key.verify(
                signature,
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def sign_pss(self, message: bytes) -> bytes:
        """PSS签名（更安全）"""
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_pss(self, message: bytes, signature: bytes) -> bool:
        """PSS验证"""
        try:
            self.public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def export_keypair(self) -> tuple:
        """导出密钥对"""
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, PublicFormat, NoEncryption
        )
        priv_pem = self.private_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        )
        pub_pem = self.public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )
        return priv_pem, pub_pem


# 使用示例
rsa_sig = RSASignature(key_size=2048)
message = b"Important document content"

# PKCS#1 v1.5
sig1 = rsa_sig.sign_pkcs1v15(message)
print(f"PKCS1v15签名验证: {rsa_sig.verify_pkcs1v15(message, sig1)}")

# PSS
sig2 = rsa_sig.sign_pss(message)
print(f"PSS签名验证: {rsa_sig.verify_pss(message, sig2)}")
```

#### 3.2.2 PSS填充方案

**PSS（Probabilistic Signature Scheme）** 是概率性签名方案，比PKCS#1 v1.5更安全。

```
PSS签名过程：
  1. 生成随机盐值（salt）
  2. 计算 M' = Hash(0x00..00 || mHash || salt)
  3. 计算 H = Hash(M')
  4. 用0xBC填充
  5. 生成DB = PS || 0x01 || salt
  6. 用MGF掩码DB
  7. 组合签名块
  
PSS验证过程：
  1. 从签名中恢复DB
  2. 提取salt
  3. 重新计算M'和H
  4. 比较H是否匹配
```

**PSS vs PKCS#1 v1.5对比：**

| 特性 | PKCS#1 v1.5 | PSS |
|------|------------|-----|
| 确定性 | 确定性（同一消息签名相同） | 概率性（同一消息签名不同） |
| 安全性证明 | 无形式化证明 | 有安全证明 |
| 安全等级 | 较低 | 较高 |
| 兼容性 | 广泛 | 需要新系统支持 |
| 推荐 | 旧系统兼容 | 新系统推荐 |

### 3.3 RSA密钥长度与安全性

| 密钥长度 | 等效对称密钥 | 安全评估 | 推荐使用 |
|----------|------------|---------|---------|
| 1024位 | 80位 | 不安全 | 禁止 |
| 2048位 | 112位 | 基本安全 | 最低要求 |
| 3072位 | 128位 | 安全 | 推荐 |
| 4096位 | 152位 | 高安全 | 高安全场景 |
| 8192位 | 200位 | 过度 | 不推荐（性能差） |

### 3.4 OpenSSL RSA签名命令

```bash
# 生成RSA密钥对
openssl genrsa -out private_key.pem 2048

# 提取公钥
openssl rsa -in private_key.pem -pubout -out public_key.pem

# 签名（PKCS#1 v1.5）
openssl dgst -sha256 -sign private_key.pem -out signature.bin message.txt

# 验证签名
openssl dgst -sha256 -verify public_key.pem -signature signature.bin message.txt

# PSS签名
openssl dgst -sha256 \
    -sigopt rsa_padding_mode:pss \
    -sigopt rsa_pss_saltlen:32 \
    -sign private_key.pem \
    -out signature_pss.bin message.txt

# PSS验证
openssl dgst -sha256 \
    -sigopt rsa_padding_mode:pss \
    -sigopt rsa_pss_saltlen:32 \
    -verify public_key.pem \
    -signature signature_pss.bin message.txt
```

---

---

## 📋 内容审核与补充建议

> 针对「RSA数字签名」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
