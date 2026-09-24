# EdDSA签名算法

### 6.1 EdDSA概述

**EdDSA（Edwards-curve Digital Signature Algorithm）** 是基于Twisted Edwards曲线的新一代签名算法，具有高性能、高安全性和快速签名验证的特点。

**EdDSA的特点：**

| 特性 | 说明 |
|------|------|
| 确定性签名 | 不需要随机数，签名结果确定 |
| 抗侧信道攻击 | 不依赖秘密依赖的条件分支 |
| 高性能 | 签名和验证速度都快 |
| 小签名 | 64字节签名 |
| 小密钥 | 32字节公钥 |

**EdDSA曲线对比：**

| 曲线 | 签名算法 | 公钥长度 | 签名长度 | 等效安全 |
|------|---------|---------|---------|---------|
| Ed25519 | Ed25519 | 32字节 | 64字节 | 128位 |
| Ed448 | Ed448 | 57字节 | 114字节 | 224位 |

### 6.2 Ed25519签名

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)

class Ed25519Signature:
    """Ed25519签名实现"""
    
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
    
    def sign(self, message: bytes) -> bytes:
        """签名（纯签名，不需要哈希）"""
        return self.private_key.sign(message)
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """验证签名"""
        try:
            self.public_key.verify(signature, message)
            return True
        except Exception:
            return False
    
    def export_keys(self) -> tuple:
        """导出密钥"""
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PrivateFormat, PublicFormat, NoEncryption
        )
        priv_bytes = self.private_key.private_bytes(
            Encoding.Raw, PrivateFormat.Raw, NoEncryption()
        )
        pub_bytes = self.public_key.public_bytes(
            Encoding.Raw, PublicFormat.Raw
        )
        return priv_bytes, pub_bytes
    
    def import_public_key(self, key_bytes: bytes):
        """从字节导入公钥"""
        self.public_key = Ed25519PublicKey.from_public_bytes(key_bytes)


# 使用示例
ed = Ed25519Signature()
message = b"Ed25519 test message"

# 签名
sig = ed.sign(message)
priv, pub = ed.export_keys()

print(f"私钥长度: {len(priv)} bytes")
print(f"公钥长度: {len(pub)} bytes")
print(f"签名长度: {len(sig)} bytes")
print(f"验证结果: {ed.verify(message, sig)}")

# 同一消息签名相同（确定性）
sig2 = ed.sign(message)
print(f"确定性签名验证: {sig == sig2}")

# 从公钥验证
ed2 = Ed25519Signature()
ed2.import_public_key(pub)
print(f"公钥验证: {ed2.verify(message, sig)}")
```

### 6.3 EdDSA与ECDSA对比

| 特性 | ECDSA | EdDSA |
|------|-------|-------|
| 签名确定性 | 需要RFC 6979 | 天然确定性 |
| 签名速度 | 慢 | 快（2-3倍） |
| 验证速度 | 快 | 快 |
| 抗侧信道 | 需要额外保护 | 天然抗侧信道 |
| 签名格式 | 可变长度（DER） | 固定64字节 |
| 哈希选择 | 可选SHA-256等 | 内置SHA-512 |
| 批量验证 | 不支持 | 支持 |
| 标准化 | RFC 6979 | RFC 8032 |

### 6.4 Ed25519在SSH中的应用

```bash
# 生成Ed25519 SSH密钥
ssh-keygen -t ed25519 -C "user@example.com" -f ~/.ssh/id_ed25519

# 生成更高安全的Ed448（如果支持）
ssh-keygen -t ed448 -C "user@example.com" -f ~/.ssh/id_ed448

# 查看公钥
cat ~/.ssh/id_ed25519.pub
# 输出: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5... user@example.com
```

---

---

