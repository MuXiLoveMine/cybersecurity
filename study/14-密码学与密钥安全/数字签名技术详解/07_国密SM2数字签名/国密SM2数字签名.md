# 国密SM2数字签名

### 7.1 SM2签名概述

**SM2** 是中国密码管理局发布的椭圆曲线公钥密码算法，包含数字签名、密钥交换和公钥加密三个部分。SM2签名是国密PKI体系的核心。

**SM2与ECDSA的对比：**

| 特性 | ECDSA | SM2 |
|------|-------|-----|
| 曲线 | NIST曲线 | SM2曲线 |
| 签名流程 | 标准ECDSA | 增加了ZA和Z值 |
| 哈希 | SHA-256 | SM3 |
| 签名长度 | 64字节（P-256） | 64字节 |
| 国际标准 | FIPS 186 | GB/T 32918 |

### 7.2 SM2曲线参数

```
SM2椭圆曲线参数：
  方程: y² = x³ + ax + b (mod p)
  
  p = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF 00000000 FFFFFFFF FFFFFFFF
  
  a = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF 00000000 FFFFFFFF FFFFFFFC
  
  b = 28E9FA9E 9D9F5E34 4D5A9E4B CF659098 E0369503 E0B68A65 C39E2E0C 9EDE51E6
  
  基点G:
    Gx = 32C4AE2C 1F198119 5F990446 6C5A9EC3 7D9E2A3D E0F4A7D3 89C8B71C 225BE9DD
    Gy = 9E6E9E3A 6E5C5D51 5B6B6C6C 9E6E2E4F 2D5C5E51 5E5E5E51 7C8C8C8C 5E5E5E5E
  
  阶n:
    n = FFFFFFFE FFFFFFFF FFFFFFFF FFFFFFFF 7203DF6B 21C6052B 53BBF409 39D54123
```

### 7.3 SM2签名流程

```
SM2签名过程：

  预处理：
  1. 计算ZA = SM3(ENTL || ID || a || b || Gx || Gy || Px || Py)
     其中:
       ENTL = ID的位长度（2字节）
       ID = 用户标识（默认"1234567812345678"）
       a, b = 曲线参数
       Gx, Gy = 基点坐标
       Px, Py = 公钥坐标

  签名：
  1. 计算e = SM3(ZA || M)，M为待签消息
  2. 选择随机数k, 1 ≤ k ≤ n-1
  3. 计算(x1, y1) = k * G
  4. 计算r = (e + x1) mod n
  5. 如果r == 0或r+k == n，重新选择k
  6. 计算s = ((1 + d)^(-1)) * (k - r*d) mod n
  7. 如果s == 0，重新选择k
  8. 签名 = (r, s)

  验证：
  1. 检查 1 ≤ r ≤ n-1 和 1 ≤ s ≤ n-1
  2. 计算e = SM3(ZA || M)
  3. 计算t = (r + s) mod n
  4. 如果t == 0，验证失败
  5. 计算(x2, y2) = s*G + t*Q
  6. 计算R = (e + x2) mod n
  7. 验证通过当且仅当 R == r
```

```python
"""
SM2签名实现
使用gmssl库: pip install gmssl
"""

try:
    from gmssl import sm2, func
    HAS_GMSSL = True
except ImportError:
    HAS_GMSSL = False
    print("请安装gmssl库: pip install gmssl")


class SM2Signature:
    """SM2数字签名实现"""
    
    DEFAULT_USER_ID = "1234567812345678"  # 默认用户标识
    
    def __init__(self):
        if not HAS_GMSSL:
            raise ImportError("需要gmssl库")
        
        # 生成SM2密钥对
        self.private_key = func.random_hex(64)  # 256位私钥
        
        # 创建SM2对象
        sm2_crypt = sm2.CryptSM2(
            pubkey='',  # 公钥稍后计算
            privkey=self.private_key
        )
        self.public_key = sm2_crypt._kg(  # 计算公钥
            int(self.private_key, 16),
            sm2_crypt.pointG
        )
        # 转为十六进制字符串
        self.public_key = '%064x%064x' % self.public_key
        
        # 创建完整的SM2对象
        self.sm2_crypt = sm2.CryptSM2(
            pubkey=self.public_key,
            privkey=self.private_key
        )
    
    def sign(self, message: bytes, user_id: str = None) -> bytes:
        """
        SM2签名
        
        Args:
            message: 待签名消息
            user_id: 用户标识
            
        Returns:
            签名（DER格式）
        """
        if user_id is None:
            user_id = self.DEFAULT_USER_ID
        
        # SM2签名
        signature = self.sm2_crypt.sign(
            message.encode('utf-8') if isinstance(message, str) else message,
            user_id.encode('utf-8')
        )
        
        return signature
    
    def verify(self, message: bytes, signature: bytes, 
               user_id: str = None) -> bool:
        """
        SM2验证签名
        
        Args:
            message: 原始消息
            signature: 签名
            user_id: 用户标识
            
        Returns:
            验证结果
        """
        if user_id is None:
            user_id = self.DEFAULT_USER_ID
        
        msg_bytes = message.encode('utf-8') if isinstance(message, str) \
                    else message
        
        return self.sm2_crypt.verify(
            signature,
            msg_bytes,
            user_id.encode('utf-8')
        )
    
    def export_keypair(self) -> dict:
        """导出密钥对"""
        return {
            'private_key': self.private_key,
            'public_key': self.public_key,
            'curve': 'SM2',
            'key_size': 256,
            'signature_size': 64  # r(32) + s(32)
        }


if HAS_GMSSL:
    # 使用示例
    sm2_sig = SM2Signature()
    message = "SM2签名测试消息"
    
    print(f"私钥: {sm2_sig.private_key[:32]}...")
    print(f"公钥: {sm2_sig.public_key[:32]}...")
    
    sig = sm2_sig.sign(message)
    print(f"签名: {sig.hex()[:60]}...")
    
    valid = sm2_sig.verify(message, sig)
    print(f"验证结果: {valid}")
```

### 7.4 SM2签名格式

```
SM2签名DER格式（GB/T 32918.2）:
  SEQUENCE {
    r INTEGER,
    s INTEGER
  }

原始格式:
  r: 32字节（大端序）
  s: 32字节（大端序）
  总长度: 64字节
```

---

---

