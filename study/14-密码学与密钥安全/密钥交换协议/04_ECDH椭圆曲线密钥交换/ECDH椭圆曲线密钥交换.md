# ECDH椭圆曲线密钥交换

### 3.1 ECDH原理

**ECDH（Elliptic Curve Diffie-Hellman）** 是DH密钥交换在椭圆曲线上的实现。

```
ECDH密钥交换原理:

  公开参数:
    椭圆曲线: y² = x³ + ax + b (mod p)
    基点G: 曲线上的一个点
    阶n: G的阶
    
  Alice:
    1. 选择随机私钥 dA ∈ [1, n-1]
    2. 计算公钥 QA = dA * G（标量乘法）
    3. 发送 QA 给 Bob
    
  Bob:
    1. 选择随机私钥 dB ∈ [1, n-1]
    2. 计算公钥 QB = dB * G
    3. 发送 QB 给 Alice
    
  共享密钥计算:
    Alice: S = dA * QB = dA * dB * G
    Bob:   S = dB * QA = dB * dA * G
    
    两者结果相同: S = (dA * dB) * G
    
  共享密钥 = Hash(Sx)  （S的x坐标的哈希）
```

### 3.2 ECDH实现

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os

class ECDHKeyExchange:
    """ECDH椭圆曲线密钥交换"""
    
    # 支持的曲线
    CURVES = {
        'P-256': ec.SECP256R1(),
        'P-384': ec.SECP384R1(),
        'P-521': ec.SECP521R1(),
        'Curve25519': None,  # 特殊处理
    }
    
    def __init__(self, curve_name: str = 'P-256'):
        self.curve_name = curve_name
        self.curve = self.CURVES.get(curve_name)
        
        if self.curve is None and curve_name != 'Curve25519':
            raise ValueError(f"不支持的曲线: {curve_name}")
        
        self.private_key = None
        self.public_key = None
    
    def generate_keypair(self):
        """生成密钥对"""
        if self.curve_name == 'Curve25519':
            from cryptography.hazmat.primitives.asymmetric.x25519 import (
                X25519PrivateKey
            )
            self.private_key = X25519PrivateKey.generate()
        else:
            self.private_key = ec.generate_private_key(self.curve)
        
        self.public_key = self.private_key.public_key()
        return self.public_key
    
    def compute_shared_key(self, other_public_key, 
                          key_length: int = 32) -> bytes:
        """
        计算共享密钥
        
        Args:
            other_public_key: 对方公钥
            key_length: 派生密钥长度
            
        Returns:
            共享密钥
        """
        if self.curve_name == 'Curve25519':
            from cryptography.hazmat.primitives.asymmetric.x25519 import (
                X25519PublicKey
            )
            shared = self.private_key.exchange(other_public_key)
        else:
            shared = self.private_key.exchange(
                ec.ECDH(), other_public_key
            )
        
        # 使用HKDF派生密钥
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=None,
            info=b'ecdh-shared-key'
        ).derive(shared)
        
        return derived_key
    
    def export_public_key(self) -> bytes:
        """导出公钥（原始格式）"""
        from cryptography.hazmat.primitives.serialization import (
            Encoding, PublicFormat
        )
        return self.public_key.public_bytes(
            Encoding.Raw,
            PublicFormat.Raw
        )
    
    @staticmethod
    def import_public_key(key_bytes: bytes, 
                          curve_name: str = 'P-256'):
        """导入公钥"""
        if curve_name == 'Curve25519':
            from cryptography.hazmat.primitives.asymmetric.x25519 import (
                X25519PublicKey
            )
            return X25519PublicKey.from_public_bytes(key_bytes)
        else:
            curve = ECDHKeyExchange.CURVES.get(curve_name)
            return ec.EllipticCurvePublicKey.from_encoded_point(
                curve, key_bytes
            )


# 使用示例
print("=" * 60)
print("ECDH密钥交换演示")
print("=" * 60)

# Alice (P-256)
alice = ECDHKeyExchange('P-256')
alice.generate_keypair()
alice_pub_bytes = alice.export_public_key()
print(f"Alice公钥长度: {len(alice_pub_bytes)} bytes")

# Bob (P-256)
bob = ECDHKeyExchange('P-256')
bob.generate_keypair()
bob_pub_bytes = bob.export_public_key()
print(f"Bob公钥长度: {len(bob_pub_bytes)} bytes")

# 交换公钥
alice_shared = alice.compute_shared_key(
    ECDHKeyExchange.import_public_key(bob_pub_bytes, 'P-256')
)
bob_shared = bob.compute_shared_key(
    ECDHKeyExchange.import_public_key(alice_pub_bytes, 'P-256')
)

print(f"\nAlice共享密钥: {alice_shared.hex()[:32]}...")
print(f"Bob共享密钥:   {bob_shared.hex()[:32]}...")
print(f"密钥匹配: {alice_shared == bob_shared}")

# Curve25519演示
print("\n" + "=" * 60)
print("X25519 (Curve25519) 密钥交换")
print("=" * 60)

alice_x = ECDHKeyExchange('Curve25519')
alice_x.generate_keypair()
alice_x_pub = alice_x.export_public_key()
print(f"Alice公钥长度: {len(alice_x_pub)} bytes")

bob_x = ECDHKeyExchange('Curve25519')
bob_x.generate_keypair()
bob_x_pub = bob_x.export_public_key()
print(f"Bob公钥长度: {len(bob_x_pub)} bytes")

alice_x_shared = alice_x.compute_shared_key(
    ECDHKeyExchange.import_public_key(bob_x_pub, 'Curve25519')
)
bob_x_shared = bob_x.compute_shared_key(
    ECDHKeyExchange.import_public_key(alice_x_pub, 'Curve25519')
)

print(f"\nAlice共享密钥: {alice_x_shared.hex()[:32]}...")
print(f"Bob共享密钥:   {bob_x_shared.hex()[:32]}...")
print(f"密钥匹配: {alice_x_shared == bob_x_shared}")
```

### 3.3 Curve25519与X25519

**Curve25519** 是Daniel J. Bernstein设计的椭圆曲线，**X25519**是基于Curve25519的Diffie-Hellman协议。

```
Curve25519特点:
  方程: y² = x³ + 486662x² + x (mod p)
  模数: p = 2^255 - 19
  基点: x = 9
  阶: 2^252 + 2774231777373657118437490379410580678430126887995

X25519优势:
  1. 高性能: 速度快
  2. 小密钥: 32字节公钥
  3. 安全性: 抗侧信道攻击
  4. 简单性: 实现简单，不易出错
  5. 标准化: RFC 7748
```

```python
"""
X25519原始实现（概念）
"""
import os

def curve25519_clamp_scalar(scalar: bytes) -> bytes:
    """Clamping标量（Curve25519特殊处理）"""
    s = bytearray(scalar)
    s[0] &= 248    # 清除低3位
    s[31] &= 127   # 清除最高位
    s[31] |= 64    # 设置次高位
    return bytes(s)

def x25519_keygen() -> tuple:
    """
    X25519密钥生成
    
    返回: (私钥, 公钥)
    """
    # 生成随机私钥
    private = os.urandom(32)
    private = curve25519_clamp_scalar(private)
    
    # 基点x坐标
    basepoint = bytes([9]) + bytes(31)
    
    # 计算公钥（标量乘法）
    # 实际使用cryptography库的X25519
    from cryptography.hazmat.primitives.asymmetric.x25519 import (
        X25519PrivateKey, X25519PublicKey
    )
    key = X25519PrivateKey.from_private_bytes(private)
    public = key.public_key()
    
    pub_bytes = public.public_bytes(
        __import__('cryptography').hazmat.primitives.serialization.Encoding.Raw,
        __import__('cryptography').hazmat.primitives.serialization.PublicFormat.Raw
    )
    
    return private, pub_bytes

def x25519_dh(private_key: bytes, other_public: bytes) -> bytes:
    """X25519密钥交换"""
    from cryptography.hazmat.primitives.asymmetric.x25519 import (
        X25519PrivateKey, X25519PublicKey
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding, PublicFormat
    )
    
    priv = X25519PrivateKey.from_private_bytes(private_key)
    pub = X25519PublicKey.from_public_bytes(other_public)
    
    shared = priv.exchange(pub)
    return shared


# 演示
priv_a, pub_a = x25519_keygen()
priv_b, pub_b = x25519_keygen()

print(f"私钥长度: {len(priv_a)} bytes")
print(f"公钥长度: {len(pub_a)} bytes")

shared_a = x25519_dh(priv_a, pub_b)
shared_b = x25519_dh(priv_b, pub_a)

print(f"共享密钥匹配: {shared_a == shared_b}")
print(f"共享密钥: {shared_a.hex()[:32]}...")
```

---

---

## 📋 内容审核与补充建议

> 针对「ECDH椭圆曲线密钥交换」部分的内容审核结果：

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
