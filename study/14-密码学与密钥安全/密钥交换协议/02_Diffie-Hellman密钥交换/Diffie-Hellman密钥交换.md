# Diffie-Hellman密钥交换

### 2.1 DH密钥交换原理

**Diffie-Hellman（DH）密钥交换** 是世界上第一个公钥密码协议，由Whitfield Diffie和Martin Hellman于1976年提出。

**数学基础：离散对数问题（DLP）**

```
DH密钥交换原理:

  公开参数:
    p: 大素数
    g: 模p的本原根（生成元）
    
  Alice:
    1. 选择随机私钥 a ∈ [1, p-1]
    2. 计算公钥 A = g^a mod p
    3. 发送 A 给 Bob
    
  Bob:
    1. 选择随机私钥 b ∈ [1, p-1]
    2. 计算公钥 B = g^b mod p
    3. 发送 B 给 Alice
    
  共享密钥计算:
    Alice: K = B^a mod p = (g^b)^a mod p = g^(ab) mod p
    Bob:   K = A^b mod p = (g^a)^b mod p = g^(ab) mod p
    
  两者计算结果相同: K = g^(ab) mod p

攻击者Eve可以看到: p, g, A, B
  要计算K，需要知道a或b
  即从g^a mod p求a（离散对数问题）
  这是数学上公认的困难问题
```

### 2.2 DH的安全参数

| 参数 | 最小推荐值 | 说明 |
|------|----------|------|
| p（模数） | 2048位 | 等效112位安全 |
| p（模数） | 3072位 | 等效128位安全 |
| g（生成元） | 2 | 最常用的生成元 |
| 私钥长度 | ≥224位 | 随机数 |

**安全素数选择：**
```
安全素数: p = 2q + 1，其中q也是素数

选择安全素数的原因：
  1. 防止小子群攻击
  2. 确保离散对数的困难性
  
验证方法:
  1. p是素数
  2. q = (p-1)/2是素数
  3. g生成大子群
```

### 2.3 DH实现

```python
import os
import random

class DiffieHellman:
    """Diffie-Hellman密钥交换"""
    
    # RFC 3526推荐的参数（MODP Group 14, 2048位）
    P = int(
        "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
        "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
        "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
        "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
        "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
        "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
        "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
        "670C354E4ABCED0BC976BE5FC8A9C4E9A4E5B7A1E5B7A1E5"
        "B7A1E5B7A1E5B7A1E5B7A1E5B7A1E5B7A1E5B7A1E5B7A1"
        "E5B7A1E5B7A1E5B7A1E5B7A1", 16
    )
    
    G = 2
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.shared_key = None
    
    @staticmethod
    def _generate_random(bits: int) -> int:
        """生成密码学安全随机数"""
        return int.from_bytes(os.urandom(bits // 8), 'big')
    
    def generate_keypair(self, bits: int = 256):
        """生成密钥对"""
        # 选择随机私钥
        self.private_key = self._generate_random(bits)
        # 确保私钥在有效范围内
        self.private_key %= (self.P - 1)
        if self.private_key < 2:
            self.private_key = 2
        
        # 计算公钥 A = g^a mod p
        self.public_key = pow(self.G, self.private_key, self.P)
        
        return self.public_key
    
    def compute_shared_key(self, other_public_key: int) -> bytes:
        """计算共享密钥"""
        # 验证对方公钥
        if other_public_key < 2 or other_public_key >= self.P:
            raise ValueError("无效的公钥")
        
        # 计算共享密钥 K = B^a mod p
        shared = pow(other_public_key, self.private_key, self.P)
        
        # 转换为字节
        shared_bytes = shared.to_bytes(
            (shared.bit_length() + 7) // 8, 'big'
        )
        
        # 密钥派生（使用哈希）
        import hashlib
        self.shared_key = hashlib.sha256(shared_bytes).digest()
        
        return self.shared_key
    
    def get_public_key(self) -> int:
        """获取公钥"""
        return self.public_key
    
    def get_shared_key(self) -> bytes:
        """获取共享密钥"""
        return self.shared_key


# 使用示例
print("=" * 60)
print("Diffie-Hellman密钥交换演示")
print("=" * 60)

# Alice
alice = DiffieHellman()
alice.generate_keypair()
print(f"Alice公钥: {hex(alice.get_public_key())[:40]}...")

# Bob
bob = DiffieHellman()
bob.generate_keypair()
print(f"Bob公钥: {hex(bob.get_public_key())[:40]}...")

# 交换公钥并计算共享密钥
alice_shared = alice.compute_shared_key(bob.get_public_key())
bob_shared = bob.compute_shared_key(alice.get_public_key())

print(f"\nAlice共享密钥: {alice_shared.hex()[:32]}...")
print(f"Bob共享密钥:   {bob_shared.hex()[:32]}...")
print(f"密钥匹配: {alice_shared == bob_shared}")

# 使用共享密钥加密通信
from cryptography.hazmat.primitives.ciphers import (
    Cipher, algorithms, modes
)
from cryptography.hazmat.primitives import padding

key = alice_shared[:16]  # 使用前16字节作为AES密钥
iv = os.urandom(16)

# Alice加密消息
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
encryptor = cipher.encryptor()
padder = padding.PKCS7(128).padder()
plaintext = b"Hello from Alice via DH key exchange!"
padded = padder.update(plaintext) + padder.finalize()
ciphertext = encryptor.update(padded) + encryptor.finalize()

print(f"\n加密消息: {ciphertext.hex()[:48]}...")

# Bob解密消息
cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
decryptor = cipher.decryptor()
unpadder = padding.PKCS7(128).unpadder()
decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

print(f"解密消息: {decrypted.decode()}")
```

### 2.4 DH的安全问题

#### 2.4.1 中间人攻击

```
无认证的DH密钥交换容易受到中间人攻击:

  Alice ←→ Mallory ←→ Bob
  
  1. Alice发送A给"Bob"（实际发给Mallory）
  2. Mallory截获A，生成自己的M1，发送M1给Bob
  3. Bob发送B给"Alice"（实际发给Mallory）
  4. Mallory截获B，生成自己的M2，发送M2给Alice
  
  结果:
    Alice和Mallory共享密钥K1
    Mallory和Bob共享密钥K2
    Alice和Bob之间没有真正的共享密钥
    
  Mallory可以:
    - 解密Alice的消息，重新加密发给Bob
    - 解密Bob的消息，重新加密发给Alice
    - 双方都以为在直接通信

防护:
  1. 使用数字签名认证交换消息（STS协议）
  2. 使用证书验证对方身份
  3. 使用预共享密钥认证
  4. 使用带认证的密钥交换协议（如TLS）
```

#### 2.4.2 小子群攻击

```
小子群攻击:

  如果p-1有小因子，攻击者可以利用小子群
    
  防护:
  1. 使用安全素数 p = 2q + 1
  2. 验证公钥的阶足够大
  3. 使用RFC 7919推荐的参数组
  4. 验证 1 < A < p-1
```

### 2.5 有限域DH vs 椭圆曲线DH

| 特性 | 有限域DH (FFDH) | 椭圆曲线DH (ECDH) |
|------|----------------|-------------------|
| 数学基础 | 离散对数 | 椭圆曲线离散对数 |
| 密钥长度 | 2048位 | 256位 |
| 安全强度 | 112位 | 128位 |
| 计算效率 | 较慢 | 更快 |
| 带宽消耗 | 大 | 小 |
| 标准化 | RFC 3526等 | RFC 7748等 |

---

---

