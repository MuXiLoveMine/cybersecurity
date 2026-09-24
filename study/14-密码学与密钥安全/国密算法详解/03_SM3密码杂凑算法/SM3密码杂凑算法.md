# SM3密码杂凑算法

### 3.1 SM3算法概述

**SM3** 是中国密码杂凑算法标准（GB/T 32905-2016），用于生成256位的消息摘要。

**SM3特点：**

| 特性 | 说明 |
|------|------|
| 摘要长度 | 256位（32字节） |
| 分组长度 | 512位（64字节） |
| 迭代结构 | Merkle-Damgard结构 |
| 字长度 | 32位 |
| 迭代轮数 | 64轮 |
| 等效安全 | 128位 |
| 性能 | 与SHA-256相当 |

### 3.2 SM3算法原理

#### 3.2.1 常量与初始值

```
初始值IV（8个32位字）:
  IV = 7380166F 4914B2B9 172442D7 DA8A0600 
      A96F30BC 163138AA E38DEE4D B0FB0E4E

常量:
  Tj: 
    T0~T15  = 79CC4519
    T16~T63 = 7A879D8A
```

#### 3.2.2 布尔函数

```
布尔函数FFj和GGj:

FFj(X, Y, Z):
  j ∈ [0, 15]:  FF = X XOR Y XOR Z
  j ∈ [16, 63]: FF = (X AND Y) OR (X AND Z) OR (Y AND Z)

GGj(X, Y, Z):
  j ∈ [0, 15]:  GG = X XOR Y XOR Z
  j ∈ [16, 63]: GG = (X AND Y) OR (NOT X AND Z)
```

#### 3.2.3 置换函数

```
P0(X) = X XOR (X <<< 9) XOR (X <<< 17)
P1(X) = X XOR (X <<< 15) XOR (X <<< 23)

注: <<< 表示循环左移
```

#### 3.2.4 消息扩展

```
消息扩展过程：

输入: 512位消息块 Bi (16个32位字 W0~W15)

扩展为132个字:
  W0~W15:   直接使用消息字
  
  Wj (16 ≤ j ≤ 67):
    Wj = P1(W(j-16) XOR W(j-9) XOR (W(j-3) <<< 15)) 
         XOR (W(j-13) <<< 7) XOR W(j-6)
  
  W'j (0 ≤ j ≤ 63):
    W'j = Wj XOR W(j+4)
```

#### 3.2.5 压缩函数

```
压缩函数CF:

输入: Vi-1 (256位中间哈希值), Bi (512位消息块)
输出: Vi (256位新的哈希值)

过程:
  1. 消息扩展: 将Bi扩展为W0~W67和W'0~W'63
  
  2. 初始化工作变量:
     A=V(i-1)[0], B=V(i-1)[1], ..., H=V(i-1)[7]
  
  3. 迭代压缩（64轮）:
     对于j = 0 到 63:
       SS1 = ((A <<< 12) + E + (Tj <<< j)) <<< 7
       SS2 = SS1 XOR (A <<< 12)
       TT1 = FFj(A, B, C) + D + SS2 + W'j
       TT2 = GGj(E, F, G) + H + SS1 + Wj
       D = C
       C = B <<< 9
       B = A
       A = TT1
       H = G
       G = F <<< 19
       F = E
       E = P0(TT2)
  
  4. 更新哈希值:
     V(i)[0] = V(i-1)[0] XOR A
     V(i)[1] = V(i-1)[1] XOR B
     ...
     V(i)[7] = V(i-1)[7] XOR H
```

#### 3.2.6 整体流程

```
SM3哈希流程:

  1. 消息填充:
     消息M → M || 1 || 000...0 || 64位长度
     填充使总长度 ≡ 0 (mod 512)
  
  2. 分组:
     将填充后的消息分为L个512位分组 B0, B1, ..., B(L-1)
  
  3. 迭代:
     V0 = IV
     对于i = 0 到 L-1:
       V(i+1) = CF(Vi, Bi)
  
  4. 输出:
     哈希值 = V(L) (256位)
```

### 3.3 SM3实现

```python
"""
SM3哈希算法Python实现
"""

class SM3:
    """SM3密码杂凑算法"""
    
    # 初始值
    IV = [
        0x7380166F, 0x4914B2B9, 0x172442D7, 0xDA8A0600,
        0xA96F30BC, 0x163138AA, 0xE38DEE4D, 0xB0FB0E4E
    ]
    
    # 常量
    T1 = 0x79CC4519  # 0~15轮
    T2 = 0x7A879D8A  # 16~63轮
    
    def __init__(self):
        self._buffer = b''
        self._length = 0
        self._v = list(self.IV)
    
    @staticmethod
    def _rotl(x: int, n: int) -> int:
        """循环左移"""
        n = n % 32
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF
    
    @staticmethod
    def _ff(j: int, x: int, y: int, z: int) -> int:
        """布尔函数FF"""
        if j < 16:
            return x ^ y ^ z
        else:
            return (x & y) | (x & z) | (y & z)
    
    @staticmethod
    def _gg(j: int, x: int, y: int, z: int) -> int:
        """布尔函数GG"""
        if j < 16:
            return x ^ y ^ z
        else:
            return (x & y) | ((~x & 0xFFFFFFFF) & z)
    
    @staticmethod
    def _p0(x: int) -> int:
        """置换函数P0"""
        return x ^ SM3._rotl(x, 9) ^ SM3._rotl(x, 17)
    
    @staticmethod
    def _p1(x: int) -> int:
        """置换函数P1"""
        return x ^ SM3._rotl(x, 15) ^ SM3._rotl(x, 23)
    
    def _message_expansion(self, block: bytes) -> tuple:
        """消息扩展"""
        W = []
        W_prime = []
        
        # W0~W15
        for i in range(16):
            W.append(int.from_bytes(
                block[i*4:(i+1)*4], 'big'
            ))
        
        # W16~W67
        for j in range(16, 68):
            w = self._p1(
                W[j-16] ^ W[j-9] ^ self._rotl(W[j-3], 15)
            ) ^ self._rotl(W[j-13], 7) ^ W[j-6]
            W.append(w)
        
        # W'0~W'63
        for j in range(64):
            W_prime.append(W[j] ^ W[j+4])
        
        return W, W_prime
    
    def _compress(self, v: list, block: bytes) -> list:
        """压缩函数"""
        W, W_prime = self._message_expansion(block)
        
        A, B, C, D, E, F, G, H = v
        
        for j in range(64):
            T = self.T1 if j < 16 else self.T2
            
            SS1 = self._rotl(
                (self._rotl(A, 12) + E + self._rotl(T, j % 32)) & 0xFFFFFFFF,
                7
            )
            SS2 = SS1 ^ self._rotl(A, 12)
            
            TT1 = (self._ff(j, A, B, C) + D + SS2 + W_prime[j]) & 0xFFFFFFFF
            TT2 = (self._gg(j, E, F, G) + H + SS1 + W[j]) & 0xFFFFFFFF
            
            D = C
            C = self._rotl(B, 9)
            B = A
            A = TT1
            H = G
            G = self._rotl(F, 19)
            F = E
            E = self._p0(TT2)
        
        return [
            v[0] ^ A, v[1] ^ B, v[2] ^ C, v[3] ^ D,
            v[4] ^ E, v[5] ^ F, v[6] ^ G, v[7] ^ H
        ]
    
    def update(self, data: bytes):
        """更新哈希状态"""
        self._buffer += data
        self._length += len(data)
        
        while len(self._buffer) >= 64:
            block = self._buffer[:64]
            self._buffer = self._buffer[64:]
            self._v = self._compress(self._v, block)
    
    def digest(self) -> bytes:
        """计算最终哈希值"""
        # 填充
        msg_len = self._length
        padding = b'\x80'
        padding += b'\x00' * ((56 - (msg_len + 1) % 64) % 64)
        padding += (msg_len * 8).to_bytes(8, 'big')
        
        self.update(padding)
        
        # 输出
        result = b''
        for v in self._v:
            result += v.to_bytes(4, 'big')
        
        return result
    
    def hexdigest(self) -> str:
        """计算最终哈希值（十六进制）"""
        return self.digest().hex()
    
    @staticmethod
    def hash(data: bytes) -> str:
        """一次性计算哈希"""
        h = SM3()
        h.update(data)
        return h.hexdigest()


# 测试
if __name__ == "__main__":
    # 标准测试向量
    # SM3("abc") = 66c7f0f4 62eeedd9 d1f2d46b dc10e4e2 415c5ee7 aed90318 b2f7e3b4 15e4d2d4
    test1 = SM3.hash(b"abc")
    expected1 = "66c7f0f462eeedd9d1f2d46bdc10e4e2415c5ee7aed90318b2f7e3b415e4d2d4"
    print(f"SM3('abc') = {test1}")
    print(f"预期值     = {expected1}")
    print(f"匹配: {test1 == expected1}")
    
    # 空字符串测试
    test2 = SM3.hash(b"")
    print(f"\nSM3('') = {test2}")
    
    # 长消息测试
    test3 = SM3.hash(b"abcd" * 16)
    print(f"\nSM3('abcd'*16) = {test3}")
    
    # 与gmssl对比（如果安装了）
    if HAS_GMSSL:
        from gmssl import sm3
        gmssl_hash = sm3.sm3_hash(b"abc")
        print(f"\ngmssl SM3('abc') = {gmssl_hash}")
        print(f"实现匹配: {test1 == gmssl_hash}")
```

### 3.4 SM3 HMAC

```python
"""
SM3-HMAC实现
"""
import hmac

class SM3HMAC:
    """基于SM3的HMAC"""
    
    BLOCK_SIZE = 64  # SM3分组大小
    
    @staticmethod
    def hmac(key: bytes, message: bytes) -> bytes:
        """计算HMAC-SM3"""
        # 密钥处理
        if len(key) > SM3HMAC.BLOCK_SIZE:
            key = bytes.fromhex(SM3.hash(key))
        
        if len(key) < SM3HMAC.BLOCK_SIZE:
            key = key + b'\x00' * (SM3HMAC.BLOCK_SIZE - len(key))
        
        # 内外层填充
        ipad = bytes(b ^ 0x36 for b in key)
        opad = bytes(b ^ 0x5c for b in key)
        
        # HMAC = SM3(opad || SM3(ipad || message))
        inner = bytes.fromhex(SM3.hash(ipad + message))
        outer = bytes.fromhex(SM3.hash(opad + inner))
        
        return outer
    
    @staticmethod
    def hmac_hex(key: bytes, message: bytes) -> str:
        """计算HMAC-SM3（十六进制）"""
        return SM3HMAC.hmac(key, message).hex()


# 测试
key = b"secret_key"
message = b"Hello SM3 HMAC!"
hmac_result = SM3HMAC.hmac_hex(key, message)
print(f"HMAC-SM3: {hmac_result}")
```

---

---

