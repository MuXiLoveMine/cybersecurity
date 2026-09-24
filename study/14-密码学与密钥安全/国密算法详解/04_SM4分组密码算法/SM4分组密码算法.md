# SM4分组密码算法

### 4.1 SM4算法概述

**SM4** 是中国分组密码算法标准（GB/T 32907-2016），用于无线局域网产品等的数据加密保护。

**SM4特点：**

| 特性 | 说明 |
|------|------|
| 分组长度 | 128位（16字节） |
| 密钥长度 | 128位（16字节） |
| 迭代轮数 | 32轮 |
| 结构 | Feistel变体（非平衡Feistel） |
| S盒 | 8位输入/输出 |
| 等效安全 | 128位 |
| 设计理念 | 与AES设计不同 |

### 4.2 SM4算法原理

#### 4.2.1 基本运算

```
SM4基本运算:
  ⊕: 32位异或
  <<<i: 32位循环左移i位
  
S盒: 8位输入→8位输出的查找表
  SBOX = [
    0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,0x05,
    0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
    0x9c,0x66,0x42,0x25,0xf0,0x91,0x33,0x88,0xf9,0x32,0xa9,0xf1,0xd0,0xe7,0xe6,0x80,
    0xe6,0xfc,0xaa,0xa9,0xe1,0x0e,0x19,0x21,0x12,0xc9,0xe6,0x92,0xe5,0xdd,0x8c,0x88,
    ...（完整S盒见标准）
  ]
```

#### 4.2.2 密钥扩展

```
SM4密钥扩展:

系统参数:
  FK = [0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC]

固定参数CK:
  CKi = (ck(4i), ck(4i+1), ck(4i+2), ck(4i+3))
  其中ck(i) = (4i+7) mod 7 或查表

轮密钥生成:
  输入: 128位密钥 K = (K0, K1, K2, K3)
  
  1. (K0, K1, K2, K3) = (K0⊕FK0, K1⊕FK1, K2⊕FK2, K3⊕FK3)
  
  2. 对于i = 0 到 31:
     rki = Ki ⊕ T'(Ki+1 ⊕ Ki+2 ⊕ Ki+3 ⊕ CKi)
     Ki+4 = rki
  
  其中T'变换:
    T'(B) = B' = (b0,b1,b2,b3)' = (S(b0), S(b1), S(b2), S(b3))
    然后 B' = B' ⊕ (B' <<< 13) ⊕ (B' <<< 23)
```

#### 4.2.3 加密流程

```
SM4加密流程:

输入: 128位明文 X = (X0, X1, X2, X3)
     32位轮密钥 rk0~rk31

32轮迭代:
  对于i = 0 到 31:
    Xi+4 = Xi ⊕ T(Xi+1 ⊕ Xi+2 ⊕ Xi+3 ⊕ rki)
    
    其中T变换:
      T(A) = L(τ(A))
      τ(A) = (S(a0), S(a1), S(a2), S(a3))  # S盒替换
      L(B) = B ⊕ (B <<< 2) ⊕ (B <<< 10) ⊕ (B <<< 18) ⊕ (B <<< 24)

输出: 密文 = (X35, X34, X33, X32)  # 注意顺序反转

解密:
  与加密流程相同，但轮密钥使用逆序 rk31, rk30, ..., rk0
```

### 4.3 SM4实现

```python
"""
SM4分组密码算法Python实现
"""

class SM4:
    """SM4分组密码算法"""
    
    # S盒
    SBOX = [
        0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,0x05,
        0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
        0x9c,0x66,0x42,0x25,0xf0,0x91,0x33,0x88,0xf9,0x32,0xa9,0xf1,0xd0,0xe7,0xe6,0x80,
        0xe6,0xfc,0xaa,0xa9,0xe1,0x0e,0x19,0x21,0x12,0xc9,0xe6,0x92,0xe5,0xdd,0x8c,0x88,
        0x69,0x18,0x4b,0x55,0x64,0x07,0xf6,0x9d,0x81,0xa3,0xc1,0x25,0x4a,0x6e,0x2e,0xf8,
        0x70,0xc7,0x4f,0xa2,0x8c,0x55,0xc4,0x7e,0xd0,0x39,0x69,0x3a,0xf0,0xed,0x5b,0xc0,
        0x5c,0xb1,0x2e,0x7b,0xa2,0x49,0x76,0x93,0x28,0x64,0xc7,0x0d,0x56,0x01,0x3e,0xae,
        0x9c,0x43,0x12,0x9e,0xa0,0x2a,0x82,0xc1,0x39,0x51,0x30,0x02,0xe6,0x12,0xc6,0x19,
        0x07,0x0f,0x21,0x65,0xc9,0x7a,0x84,0x80,0x20,0x54,0x1f,0x4a,0x95,0x96,0x28,0xf0,
        0x28,0x59,0x07,0x45,0xc6,0x7e,0xe6,0xa1,0x6c,0x19,0x6f,0xc4,0x4a,0x56,0x4c,0xa1,
        0x49,0x48,0x5b,0x64,0x13,0x6c,0x3e,0x14,0x87,0x2a,0xe6,0xc6,0x91,0x39,0x09,0x1f,
        0xb1,0x6e,0x19,0xe7,0x7c,0xc6,0x2a,0x9c,0xe4,0x49,0x5a,0x3a,0x20,0x4a,0x6e,0xea,
        0x8c,0x3c,0x2e,0x36,0x24,0x3a,0x9c,0x3e,0x27,0x4d,0x07,0x0d,0x0e,0x06,0x19,0x9c,
        0x2c,0x91,0x69,0x21,0x5c,0x3a,0x27,0x44,0x6e,0x19,0x91,0x06,0x1f,0x2a,0x32,0x49,
        0x9c,0x16,0xc6,0x2e,0x24,0x9a,0x0d,0x3f,0x17,0x4e,0xc4,0x94,0x1d,0x49,0x87,0x0e,
        0x06,0x56,0x18,0x90,0xe1,0x24,0x21,0x64,0x1f,0x2a,0x12,0x95,0x14,0x49,0x27,0x8a
    ]
    
    # 系统参数
    FK = [0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC]
    
    # 固定参数
    CK = [
        0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
        0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
        0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
        0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
        0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
        0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
        0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
        0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
    ]
    
    @staticmethod
    def _rotl(x: int, n: int) -> int:
        """32位循环左移"""
        n = n % 32
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
    
    @staticmethod
    def _tau(a: int) -> int:
        """S盒替换（32位→32位）"""
        b0 = (a >> 24) & 0xFF
        b1 = (a >> 16) & 0xFF
        b2 = (a >> 8) & 0xFF
        b3 = a & 0xFF
        return (SM4.SBOX[b0] << 24) | (SM4.SBOX[b1] << 16) | \
               (SM4.SBOX[b2] << 8) | SM4.SBOX[b3]
    
    @staticmethod
    def _t(a: int) -> int:
        """T变换（加密用）"""
        b = SM4._tau(a)
        return b ^ SM4._rotl(b, 2) ^ SM4._rotl(b, 10) ^ \
               SM4._rotl(b, 18) ^ SM4._rotl(b, 24)
    
    @staticmethod
    def _t_prime(a: int) -> int:
        """T'变换（密钥扩展用）"""
        b = SM4._tau(a)
        return b ^ SM4._rotl(b, 13) ^ SM4._rotl(b, 23)
    
    @staticmethod
    def _key_expansion(key: bytes) -> list:
        """密钥扩展"""
        K = [int.from_bytes(key[i*4:(i+1)*4], 'big') for i in range(4)]
        
        # 与FK异或
        for i in range(4):
            K[i] ^= SM4.FK[i]
        
        rk = []
        for i in range(32):
            tmp = K[1] ^ K[2] ^ K[3] ^ SM4.CK[i]
            tmp = SM4._t_prime(tmp)
            rki = K[0] ^ tmp
            rk.append(rki)
            
            K[0] = K[1]
            K[1] = K[2]
            K[2] = K[3]
            K[3] = rki
        
        return rk
    
    @staticmethod
    def _crypt_block(block: bytes, rk: list, decrypt: bool = False) -> bytes:
        """加密/解密一个分组"""
        X = [int.from_bytes(block[i*4:(i+1)*4], 'big') for i in range(4)]
        
        keys = rk if not decrypt else rk[::-1]
        
        for i in range(32):
            tmp = X[1] ^ X[2] ^ X[3] ^ keys[i]
            tmp = SM4._t(tmp)
            new_x = X[0] ^ tmp
            X[0] = X[1]
            X[1] = X[2]
            X[2] = X[3]
            X[3] = new_x
        
        # 输出反转
        result = X[3]
        result = (result << 32) | X[2]
        result = (result << 32) | X[1]
        result = (result << 32) | X[0]
        
        return result.to_bytes(16, 'big')
    
    @staticmethod
    def encrypt_block(plaintext: bytes, key: bytes) -> bytes:
        """加密单个分组"""
        assert len(plaintext) == 16
        assert len(key) == 16
        rk = SM4._key_expansion(key)
        return SM4._crypt_block(plaintext, rk, decrypt=False)
    
    @staticmethod
    def decrypt_block(ciphertext: bytes, key: bytes) -> bytes:
        """解密单个分组"""
        assert len(ciphertext) == 16
        assert len(key) == 16
        rk = SM4._key_expansion(key)
        return SM4._crypt_block(ciphertext, rk, decrypt=True)
    
    @staticmethod
    def encrypt_ecb(plaintext: bytes, key: bytes) -> bytes:
        """ECB模式加密"""
        # PKCS7填充
        pad_len = 16 - (len(plaintext) % 16)
        plaintext += bytes([pad_len] * pad_len)
        
        rk = SM4._key_expansion(key)
        ciphertext = b''
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            ciphertext += SM4._crypt_block(block, rk, decrypt=False)
        
        return ciphertext
    
    @staticmethod
    def decrypt_ecb(ciphertext: bytes, key: bytes) -> bytes:
        """ECB模式解密"""
        rk = SM4._key_expansion(key)
        plaintext = b''
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            plaintext += SM4._crypt_block(block, rk, decrypt=True)
        
        # 去除PKCS7填充
        pad_len = plaintext[-1]
        if 1 <= pad_len <= 16:
            plaintext = plaintext[:-pad_len]
        
        return plaintext
    
    @staticmethod
    def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
        """CBC模式加密"""
        # PKCS7填充
        pad_len = 16 - (len(plaintext) % 16)
        plaintext += bytes([pad_len] * pad_len)
        
        rk = SM4._key_expansion(key)
        prev = iv
        ciphertext = b''
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # 与前一密文块异或
            xored = bytes(a ^ b for a, b in zip(block, prev))
            encrypted = SM4._crypt_block(xored, rk, decrypt=False)
            ciphertext += encrypted
            prev = encrypted
        
        return ciphertext
    
    @staticmethod
    def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """CBC模式解密"""
        rk = SM4._key_expansion(key)
        prev = iv
        plaintext = b''
        
        for i in range(0, len(ciphertext), 16):
            block = ciphertext[i:i+16]
            decrypted = SM4._crypt_block(block, rk, decrypt=True)
            # 与前一密文块异或
            xored = bytes(a ^ b for a, b in zip(decrypted, prev))
            plaintext += xored
            prev = block
        
        # 去除PKCS7填充
        pad_len = plaintext[-1]
        if 1 <= pad_len <= 16:
            plaintext = plaintext[:-pad_len]
        
        return plaintext
    
    @staticmethod
    def encrypt_ctr(plaintext: bytes, key: bytes, nonce: bytes) -> bytes:
        """CTR模式加密"""
        rk = SM4._key_expansion(key)
        counter = int.from_bytes(nonce, 'big')
        ciphertext = b''
        
        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16]
            # 生成密钥流
            ctr_block = counter.to_bytes(16, 'big')
            keystream = SM4._crypt_block(ctr_block, rk, decrypt=False)
            # 异或
            encrypted = bytes(a ^ b for a, b in zip(block, keystream[:len(block)]))
            ciphertext += encrypted
            counter += 1
        
        return ciphertext
    
    @staticmethod
    def decrypt_ctr(ciphertext: bytes, key: bytes, nonce: bytes) -> bytes:
        """CTR模式解密（与加密相同）"""
        return SM4.encrypt_ctr(ciphertext, key, nonce)


# 测试
if __name__ == "__main__":
    # 标准测试向量
    key = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    plaintext = bytes.fromhex("0123456789ABCDEFFEDCBA9876543210")
    
    # ECB加密
    encrypted = SM4.encrypt_block(plaintext, key)
    decrypted = SM4.decrypt_block(encrypted, key)
    
    print(f"密钥: {key.hex()}")
    print(f"明文: {plaintext.hex()}")
    print(f"加密: {encrypted.hex()}")
    print(f"解密: {decrypted.hex()}")
    print(f"验证: {plaintext == decrypted}")
    
    # ECB模式
    data = b"Hello SM4 encryption test message!"
    enc = SM4.encrypt_ecb(data, key)
    dec = SM4.decrypt_ecb(enc, key)
    print(f"\nECB加密: {enc.hex()[:48]}...")
    print(f"ECB解密: {dec}")
    print(f"验证: {data == dec}")
    
    # CBC模式
    iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    enc_cbc = SM4.encrypt_cbc(data, key, iv)
    dec_cbc = SM4.decrypt_cbc(enc_cbc, key, iv)
    print(f"\nCBC加密: {enc_cbc.hex()[:48]}...")
    print(f"CBC解密: {dec_cbc}")
    print(f"验证: {data == dec_cbc}")
    
    # CTR模式
    nonce = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    enc_ctr = SM4.encrypt_ctr(data, key, nonce)
    dec_ctr = SM4.decrypt_ctr(enc_ctr, key, nonce)
    print(f"\nCTR加密: {enc_ctr.hex()[:48]}...")
    print(f"CTR解密: {dec_ctr}")
    print(f"验证: {data == dec_ctr}")
```

### 4.4 SM4工作模式

SM4支持多种工作模式，与国际AES模式类似：

| 工作模式 | 特点 | 适用场景 |
|----------|------|---------|
| ECB | 简单，不安全 | 不推荐使用 |
| CBC | 需要IV，加密串行 | 通用加密 |
| CTR | 并行加密，流密码 | 高性能加密 |
| CFB | 流密码模式 | 流式数据 |
| OFB | 流密码模式 | 流式数据 |
| GCM | AEAD认证加密 | TLS通信 |

---

---

