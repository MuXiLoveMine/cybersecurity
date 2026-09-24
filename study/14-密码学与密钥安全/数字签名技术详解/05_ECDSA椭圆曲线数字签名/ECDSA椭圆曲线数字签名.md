# ECDSA椭圆曲线数字签名

### 5.1 ECDSA概述

**ECDSA（Elliptic Curve Digital Signature Algorithm）** 是基于椭圆曲线密码学的数字签名算法，提供与RSA/DSA相同的安全服务，但密钥更短、性能更高。

**ECDSA的优势：**

| 特性 | RSA-2048 | ECDSA-256 |
|------|---------|----------|
| 安全强度 | 112位 | 128位 |
| 密钥长度 | 2048位 | 256位 |
| 签名长度 | 256字节 | 64字节 |
| 签名速度 | 慢 | 快 |
| 验证速度 | 快 | 较快 |
| 密钥生成 | 较快 | 快 |

### 5.2 椭圆曲线基础

**椭圆曲线方程：**
```
y² = x³ + ax + b (mod p)

常用曲线：
  P-256 (secp256r1):  y² = x³ - 3x + b  (NIST标准曲线)
  P-384 (secp384r1):  用于更高安全需求
  P-521 (secp521r1):  用于最高安全需求
  secp256k1:          Bitcoin使用的曲线
```

**椭圆曲线上的点运算：**
```
点加法: P + Q = R
  几何意义: 过P和Q的直线与曲线的第三个交点关于x轴的对称点

标量乘法: k * G
  G是基点，k是标量
  计算G + G + ... + G (k次)
  这是ECDSA的核心运算
```

### 5.3 ECDSA签名过程

```
ECDSA参数：
  曲线参数: (p, a, b, G, n)
  G: 基点（生成元）
  n: 基点G的阶（素数）
  
密钥对：
  私钥 d: 随机数, 1 ≤ d ≤ n-1
  公钥 Q: Q = d * G

签名过程：
  1. 选择随机数 k, 1 ≤ k ≤ n-1
  2. 计算 (x1, y1) = k * G
  3. 计算 r = x1 mod n
  4. 如果 r == 0，重新选择k
  5. 计算 s = k^(-1) * (hash(m) + d * r) mod n
  6. 如果 s == 0，重新选择k
  7. 签名 = (r, s)

验证过程：
  1. 检查 1 ≤ r ≤ n-1 和 1 ≤ s ≤ n-1
  2. 计算 w = s^(-1) mod n
  3. 计算 u1 = hash(m) * w mod n
  4. 计算 u2 = r * w mod n
  5. 计算 (x2, y2) = u1*G + u2*Q
  6. 如果 (x2, y2) 为无穷远点，验证失败
  7. 验证通过当且仅当 r ≡ x2 (mod n)
```

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature, encode_dss_signature
)

class ECDSASignature:
    """ECDSA签名实现"""
    
    # 支持的曲线
    CURVES = {
        'P-256': ec.SECP256R1(),
        'P-384': ec.SECP384R1(),
        'P-521': ec.SECP521R1(),
        'secp256k1': ec.SECP256K1(),
    }
    
    def __init__(self, curve_name: str = 'P-256'):
        curve = self.CURVES.get(curve_name)
        if curve is None:
            raise ValueError(f"不支持的曲线: {curve_name}")
        
        self.curve_name = curve_name
        self.curve = curve
        self.private_key = ec.generate_private_key(curve)
        self.public_key = self.private_key.public_key()
    
    def sign(self, message: bytes) -> bytes:
        """签名（DER格式）"""
        signature = self.private_key.sign(
            message,
            ec.ECDSA(hashes.SHA256())
        )
        return signature
    
    def sign_raw(self, message: bytes) -> tuple:
        """签名（原始r,s格式）"""
        der_sig = self.sign(message)
        r, s = decode_dss_signature(der_sig)
        return r, s
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """验证签名"""
        try:
            self.public_key.verify(
                signature,
                message,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception:
            return False
    
    def verify_raw(self, message: bytes, r: int, s: int) -> bool:
        """验证签名（原始r,s格式）"""
        der_sig = encode_dss_signature(r, s)
        return self.verify(message, der_sig)
    
    def get_key_sizes(self) -> dict:
        """获取密钥信息"""
        return {
            'curve': self.curve_name,
            'key_size_bits': self.private_key.key_size,
            'signature_size_bytes': self.private_key.key_size // 4,  # r+s
            'public_key_bytes': self.private_key.key_size // 8 * 2 + 1,  # 04+x+y
        }


# 使用示例
ecdsa = ECDSASignature('P-256')
message = b"ECDSA test message"

# 签名
sig = ecdsa.sign(message)
r, s = ecdsa.sign_raw(message)

print(f"曲线: P-256")
print(f"密钥信息: {ecdsa.get_key_sizes()}")
print(f"DER签名长度: {len(sig)} bytes")
print(f"r = {r}")
print(f"s = {s}")
print(f"验证结果: {ecdsa.verify(message, sig)}")

# 篡改验证
tampered = b"ECDSA tampered message"
print(f"篡改验证: {ecdsa.verify(tampered, sig)}")
```

### 5.4 ECDSA签名格式

**DER格式（Distinguished Encoding Rules）：**
```
DER编码的ECDSA签名：
  SEQUENCE {
    r INTEGER,
    s INTEGER
  }

示例（十六进制）：
  30 44        SEQUENCE (68 bytes)
    02 20       INTEGER (32 bytes) - r
      [r的32字节值]
    02 20       INTEGER (32 bytes) - s
      [s的32字节值]
```

**固定长度格式（如Bitcoin使用的）：**
```
r: 32字节（大端序）
s: 32字节（大端序）
总长度: 64字节
```

### 5.5 ECDSA的安全注意事项

1. **随机数k的安全**：与DSA一样，ECDSA对随机数k的安全性极度敏感
2. **侧信道攻击**：标量乘法可能泄露时序信息
3. **曲线选择**：某些曲线可能有后门嫌疑（如Dual_EC_DRBG）
4. **RFC 6979**：使用确定性k值避免随机数问题

```python
"""
RFC 6979: 确定性ECDSA签名
使用HMAC从私钥和消息确定性地生成k值
避免随机数k的安全问题
"""

# cryptography库默认使用RFC 6979
# 所以上面的ECDSASignature类已经是确定性签名

# 手动实现RFC 6979（概念性）
import hmac
import hashlib

def rfc6979_generate_k(private_key_int: int, message_hash: bytes,
                       curve_order: int, qlen: int) -> int:
    """
    RFC 6979确定性k值生成
    
    Args:
        private_key_int: 私钥（整数）
        message_hash: 消息哈希
        curve_order: 曲线阶
        qlen: 私钥位长
        
    Returns:
        确定性的k值
    """
    hlen = len(message_hash) * 8  # 哈希位长
    h1 = int.from_bytes(message_hash, 'big') % curve_order
    
    # 步骤a: 处理h1
    bits2int = lambda b: int.from_bytes(b, 'big') >> max(hlen - qlen, 0)
    
    # 步骤b: V = 0x01 0x01 ... 0x01
    V = b'\x01' * (hlen // 8)
    
    # 步骤c: K = 0x00 0x00 ... 0x00
    K = b'\x00' * (hlen // 8)
    
    # 步骤d: K = HMAC_K(V || 0x00 || int2octets(x) || bits2octets(h1))
    x_bytes = private_key_int.to_bytes((qlen + 7) // 8, 'big')
    K = hmac.new(K, V + b'\x00' + x_bytes + h1.to_bytes(
        (hlen + 7) // 8, 'big'), hashlib.sha256).digest()
    
    # 步骤e: V = HMAC_K(V)
    V = hmac.new(K, V, hashlib.sha256).digest()
    
    # 步骤f: K = HMAC_K(V || 0x01 || int2octets(x) || bits2octets(h1))
    K = hmac.new(K, V + b'\x01' + x_bytes + h1.to_bytes(
        (hlen + 7) // 8, 'big'), hashlib.sha256).digest()
    
    # 步骤g: V = HMAC_K(V)
    V = hmac.new(K, V, hashlib.sha256).digest()
    
    # 步骤h: 生成k
    while True:
        T = b''
        while len(T) * 8 < qlen:
            V = hmac.new(K, V, hashlib.sha256).digest()
            T += V
        
        k = int.from_bytes(T, 'big')
        if 1 <= k < curve_order:
            return k
        
        K = hmac.new(K, V + b'\x00', hashlib.sha256).digest()
        V = hmac.new(K, V, hashlib.sha256).digest()
```

---

---

