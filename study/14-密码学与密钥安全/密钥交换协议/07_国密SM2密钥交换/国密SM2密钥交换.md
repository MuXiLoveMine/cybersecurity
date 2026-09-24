# 国密SM2密钥交换

### 7.1 SM2密钥交换协议

**SM2密钥交换协议** （GB/T 32918.3）是基于椭圆曲线的认证密钥交换协议，类似于MQV协议。

```
SM2密钥交换流程:

  前置条件:
    Alice: 静态私钥dA, 静态公钥PA = dA*G
    Bob:   静态私钥dB, 静态公钥PB = dB*G
    ZA, ZB: 用户标识哈希值
  
  1. Alice生成临时密钥对: rA, RA = rA*G
     Alice → Bob: RA
  
  2. Bob生成临时密钥对: rB, RB = rB*G
     Bob计算:
       x̄B = 2^(⌈⌈log2(n)⌉/2⌉-1) + (RBx & (2^(⌈⌈log2(n)⌉/2⌉-1) - 1))
       tB = (dB + x̄B * rB) mod n
       点U = [h * tB](PA + [x̄A] * RA)
       KB = KDF(Ux || Uy || ZA || ZB, klen)
     Bob → Alice: RB, 验证信息
  
  3. Alice计算:
       x̄A = 2^(⌈⌈log2(n)⌉/2⌉-1) + (RAx & (2^(⌈⌈log2(n)⌉/2⌉-1) - 1))
       tA = (dA + x̄A * rA) mod n
       点V = [h * tA](PB + [x̄B] * RB)
       KA = KDF(Vx || Vy || ZA || ZB, klen)
  
  如果 U == V，则 KA == KB，密钥交换成功
  
  其中:
    x̄ = 取x坐标的高⌈log2(n)/2⌉位，再设置最高位
    h = 余因子
    KDF = SM3-based密钥派生函数
```

### 7.2 SM2密钥交换实现

```python
"""
SM2密钥交换实现
使用gmssl库
"""

try:
    from gmssl import sm2, func, sm3
    HAS_GMSSL = True
except ImportError:
    HAS_GMSSL = False


class SM2KeyExchange:
    """SM2密钥交换协议"""
    
    DEFAULT_USER_ID = "1234567812345678"
    
    def __init__(self, user_id: str = None):
        if not HAS_GMSSL:
            raise ImportError("需要gmssl库: pip install gmssl")
        
        self.user_id = user_id or self.DEFAULT_USER_ID
        
        # 生成静态密钥对
        self.static_priv = func.random_hex(64)
        crypt = sm2.CryptSM2(
            pubkey='', privkey=self.static_priv
        )
        pub = crypt._kg(
            int(self.static_priv, 16), crypt.pointG
        )
        self.static_pub = '%064x%064x' % pub
    
    def generate_ephemeral_key(self) -> tuple:
        """生成临时密钥对"""
        ephemeral_priv = func.random_hex(64)
        crypt = sm2.CryptSM2(
            pubkey='', privkey=ephemeral_priv
        )
        pub = crypt._kg(
            int(ephemeral_priv, 16), crypt.pointG
        )
        ephemeral_pub = '%064x%064x' % pub
        
        return ephemeral_priv, ephemeral_pub
    
    def compute_shared_key(self, remote_static_pub: str,
                           remote_ephemeral_pub: str,
                           self_ephemeral_priv: str,
                           key_length: int = 32) -> bytes:
        """
        计算共享密钥（概念实现）
        
        实际实现需要完整的SM2密钥交换协议
        """
        # 注意: 这是概念性实现
        # 完整实现需要:
        # 1. 计算ZA, ZB
        # 2. 计算x̄A, x̄B
        # 3. 计算tA或tB
        # 4. 计算点U/V
        # 5. KDF派生密钥
        
        # 这里仅展示概念
        combined = (
            self_ephemeral_priv +
            remote_static_pub +
            remote_ephemeral_pub
        )
        
        # 使用SM3作为KDF基础
        kdf_input = combined.encode('utf-8')
        
        # KDF
        ct = 1
        result = b''
        while len(result) < key_length:
            block = sm3.sm3_hash(
                kdf_input + ct.to_bytes(4, 'big')
            )
            result += bytes.fromhex(block)
            ct += 1
        
        return result[:key_length]


if HAS_GMSSL:
    print("=" * 60)
    print("SM2密钥交换演示")
    print("=" * 60)
    
    alice = SM2KeyExchange("Alice_12345678")
    bob = SM2KeyExchange("Bob_12345678")
    
    # 生成临时密钥
    a_eph_priv, a_eph_pub = alice.generate_ephemeral_key()
    b_eph_priv, b_eph_pub = bob.generate_ephemeral_key()
    
    print(f"Alice静态公钥: {alice.static_pub[:24]}...")
    print(f"Bob静态公钥: {bob.static_pub[:24]}...")
    print(f"Alice临时公钥: {a_eph_pub[:24]}...")
    print(f"Bob临时公钥: {b_eph_pub[:24]}...")
    
    # 计算共享密钥
    alice_key = alice.compute_shared_key(
        bob.static_pub, b_eph_pub, a_eph_priv
    )
    bob_key = bob.compute_shared_key(
        alice.static_pub, a_eph_pub, b_eph_priv
    )
    
    print(f"\nAlice共享密钥: {alice_key.hex()[:24]}...")
    print(f"Bob共享密钥: {bob_key.hex()[:24]}...")
    print(f"密钥匹配: {alice_key == bob_key}")
```

---

---

