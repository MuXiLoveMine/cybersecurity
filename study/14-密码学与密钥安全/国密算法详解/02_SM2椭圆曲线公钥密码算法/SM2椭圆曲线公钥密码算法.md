# SM2椭圆曲线公钥密码算法

### 2.1 SM2算法概述

**SM2** 是基于椭圆曲线的公钥密码算法标准（GB/T 32918），包含数字签名、密钥交换和公钥加密三个部分。

**SM2标准系列：**

| 标准号 | 名称 | 内容 |
|--------|------|------|
| GB/T 32918.1 | 总则 | 曲线参数、算法基础 |
| GB/T 32918.2 | 数字签名 | SM2签名算法 |
| GB/T 32918.3 | 密钥交换 | SM2密钥交换协议 |
| GB/T 32918.4 | 公钥加密 | SM2公钥加密算法 |
| GB/T 32918.5 | 参数定义 | 推荐曲线参数 |
| GB/T 32918.7 | SM9算法 | 标识密码算法 |

### 2.2 SM2椭圆曲线参数

```
SM2使用256位素数域上的椭圆曲线：
  方程: y² = x³ + ax + b (mod p)

推荐曲线参数（SM2-P-256）：
  p = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF 
      FFFFFFFF 00000000 FFFFFFFF FFFFFFFF
      
  a = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF 
      FFFFFFFF 00000000 FFFFFFFF FFFFFFFC
      
  b = 28E9FA9E 9D9F5E34 4D5A9E4B CF659098 
      E0369503 E0B68A65 C39E2E0C 9EDE51E6

  基点G:
    Gx = 32C4AE2C 1F198119 5F990446 6C5A9EC3 
         7D9E2A3D E0F4A7D3 89C8B71C 225BE9DD
         
    Gy = 9E6E9E3A 6E5C5D51 5B6B6C6C 9E6E2E4F 
         2D5C5E51 5E5E5E51 7C8C8C8C 5E5E5E5E

  阶n:
    n = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF 
        7203DF6B 21C6052B 53BBF409 39D54123

  余因子h: 1
```

**SM2与NIST P-256曲线对比：**

| 参数 | SM2 | NIST P-256 |
|------|------|-----------|
| 域类型 | 素数域 | 素数域 |
| 模数p | 256位 | 256位 |
| a | -2 (mod p) | -3 |
| 随机曲线 | 是（b随机生成） | 是 |
| 等效安全 | 128位 | 128位 |

### 2.3 SM2数字签名

#### 2.3.1 签名算法

```
SM2数字签名算法

输入：
  消息M、用户ID、私钥d、公钥P = dG

预处理（计算Z值）：
  1. ENTL = 用户ID的位长度（2字节）
  2. Z = SM3(ENTL || ID || a || b || Gx || Gy || Px || Py)

签名过程：
  1. e = SM3(Z || M)，取e的左前n位作为整数
  
  2. 生成随机数k ∈ [1, n-1]
  
  3. (x1, y1) = k * G
  
  4. r = (e + x1) mod n
     如果r == 0 或 r+k == n，返回步骤2
  
  5. s = ((1 + d)⁻¹ * (k - r * d)) mod n
     如果s == 0，返回步骤2
  
  6. 签名 = (r, s)
```

#### 2.3.2 验证算法

```
SM2签名验证算法

输入：
  消息M、签名(r,s)、用户ID、公钥P

验证过程：
  1. 检查 r ∈ [1, n-1]
  2. 检查 s ∈ [1, n-1]
  
  3. 计算Z值（同签名预处理）
  
  4. e = SM3(Z || M)
  
  5. t = (r + s) mod n
     如果t == 0，验证失败
  
  6. (x2, y2) = s*G + t*P
  
  7. R = (e + x2) mod n
  
  8. 如果 R == r，验证成功；否则验证失败
```

### 2.4 SM2公钥加密

SM2公钥加密使用了密钥派生函数KDF和消息认证码MAC的组合方案。

```
SM2公钥加密算法

加密过程：
  输入：明文M、公钥P
  
  1. 生成随机数k ∈ [1, n-1]
  
  2. C1 = k*G  （椭圆曲线点，公钥部分）
  
  3. S = k*P  （共享密钥点）
     如果S是无穷远点，返回步骤1
  
  4. 派生密钥: K = KDF(Sx || Sy, klen)
     klen = 明文长度 + SM3输出长度
  
  5. C2 = M XOR K[0:klen]  （密文）
  
  6. C3 = SM3(Sx || M || Sy)  （消息认证码）
  
  7. 密文 = C1 || C2 || C3

解密过程：
  输入：密文C1||C2||C3、私钥d
  
  1. 从C1恢复点(x1,y1)
  
  2. S = d * C1  （共享密钥点）
  
  3. 派生密钥: K = KDF(Sx || Sy, klen)
  
  4. M' = C2 XOR K[0:klen]  （解密明文）
  
  5. 验证: SM3(Sx || M' || Sy) == C3
     如果不等，解密失败
  
  6. 返回M'
```

### 2.5 SM2密钥交换

```
SM2密钥交换协议

前置条件：
  服务器A: 私钥dA, 公钥PA = dA*G
  客户端B: 私钥dB, 公钥PB = dB*G
  
交换过程：

  A → B: RA = rA*G (A的临时公钥)
  B → A: RB = rB*G (B的临时公钥)

  A计算:
    x = 椭圆曲线点RA的x坐标
    x̄ = 2^(⌈log2(n)⌉-1) + (x & (2^(⌈log2(n)⌉-1) - 1))
    tA = (dA + x̄ * rA) mod n
    
    点V = [h * tA] * (PB + [x̄B] * RB)
    
    密钥: KA = KDF(Vx || Vy || ZA || ZB, klen)

  B计算:
    x = 椭圆曲线点RB的x坐标
    x̄ = 2^(⌈log2(n)⌉-1) + (x & (2^(⌈log2(n)⌉-1) - 1))
    tB = (dB + x̄ * rB) mod n
    
    点U = [h * tB] * (PA + [x̄A] * RA)
    
    密钥: KB = KDF(Ux || Uy || ZA || ZB, klen)

  如果 V == U，则 KA == KB，密钥交换成功
```

### 2.6 SM2密钥派生函数KDF

```
KDF（Key Derivation Function）:

输入: Z（密钥材料比特串）、klen（派生密钥长度）
输出: K（派生密钥，长度klen）

过程:
  ct = 0x00000001
  counter = 1
  
  对于i从1到⌈klen/v⌉:
    Hai = SM3(Z || ct)
    ct = ct + 1
  
  K = Hai || Ha2 || ... || Ha⌈klen/v⌉
  K = K的前klen位
  
  返回K
```

```python
"""
SM2算法Python实现
依赖: pip install gmssl
"""

try:
    from gmssl import sm2, func, sm3
    HAS_GMSSL = True
except ImportError:
    HAS_GMSSL = False


class SM2Cipher:
    """SM2公钥加密/解密"""
    
    def __init__(self, pubkey: str = None, privkey: str = None):
        """
        Args:
            pubkey: 十六进制公钥字符串（04 || X || Y）
            privkey: 十六进制私钥字符串
        """
        if not HAS_GMSSL:
            raise ImportError("需要gmssl库: pip install gmssl")
        
        if privkey and not pubkey:
            # 从私钥推导公钥
            crypt = sm2.CryptSM2(pubkey='', privkey=privkey)
            pub = crypt._kg(int(privkey, 16), crypt.pointG)
            pubkey = '%064x%064x' % pub
        
        self.pubkey = pubkey
        self.privkey = privkey
        self.sm2_crypt = sm2.CryptSM2(
            pubkey=pubkey or '',
            privkey=privkey or ''
        )
    
    @staticmethod
    def generate_keypair() -> tuple:
        """生成SM2密钥对"""
        privkey = func.random_hex(64)  # 256位
        crypt = sm2.CryptSM2(pubkey='', privkey=privkey)
        pub = crypt._kg(int(privkey, 16), crypt.pointG)
        pubkey = '%064x%064x' % pub
        return privkey, pubkey
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """SM2加密"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        return self.sm2_crypt.encrypt(plaintext)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        """SM2解密"""
        return self.sm2_crypt.decrypt(ciphertext)


class SM2Signature:
    """SM2数字签名"""
    
    DEFAULT_USER_ID = "1234567812345678"
    
    def __init__(self, pubkey: str, privkey: str):
        self.pubkey = pubkey
        self.privkey = privkey
        self.sm2_crypt = sm2.CryptSM2(
            pubkey=pubkey,
            privkey=privkey
        )
    
    def sign(self, data: bytes, user_id: str = None) -> bytes:
        """签名"""
        if user_id is None:
            user_id = self.DEFAULT_USER_ID
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        sig = self.sm2_crypt.sign(data, user_id.encode('utf-8'))
        return sig
    
    def verify(self, data: bytes, signature: bytes,
               user_id: str = None) -> bool:
        """验证签名"""
        if user_id is None:
            user_id = self.DEFAULT_USER_ID
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return self.sm2_crypt.verify(
            signature, data, user_id.encode('utf-8')
        )


if HAS_GMSSL:
    # 使用示例
    
    # 1. 密钥对生成
    privkey, pubkey = SM2Cipher.generate_keypair()
    print(f"私钥: {privkey[:32]}...")
    print(f"公钥: {pubkey[:32]}...")
    
    # 2. 加密/解密
    cipher = SM2Cipher(pubkey=pubkey, privkey=privkey)
    plaintext = b"Hello SM2 encryption!"
    ciphertext = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(ciphertext)
    print(f"\n加密/解密测试:")
    print(f"明文: {plaintext}")
    print(f"解密: {decrypted}")
    print(f"验证: {plaintext == decrypted}")
    
    # 3. 签名/验证
    signer = SM2Signature(pubkey=pubkey, privkey=privkey)
    message = b"Message to sign with SM2"
    signature = signer.sign(message)
    valid = signer.verify(message, signature)
    print(f"\n签名/验证测试:")
    print(f"消息: {message}")
    print(f"签名验证: {valid}")
    
    # 4. 篡改检测
    tampered = b"Tampered message"
    tampered_valid = signer.verify(tampered, signature)
    print(f"篡改验证: {tampered_valid}")
```

---

---

