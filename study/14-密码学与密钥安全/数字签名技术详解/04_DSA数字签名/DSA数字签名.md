# DSA数字签名

### 4.1 DSA算法概述

**DSA（Digital Signature Algorithm）** 是NIST于1991年发布的数字签名标准（DSS）中的签名算法。

**DSA与RSA的对比：**

| 特性 | RSA | DSA |
|------|-----|-----|
| 数学基础 | 大整数分解 | 离散对数 |
| 签名速度 | 较慢 | 快 |
| 验证速度 | 快 | 较慢 |
| 加密能力 | 有 | 无（仅签名） |
| 密钥生成 | 较快 | 较慢 |
| 签名确定性 | PKCS1v15确定/PSS随机 | 随机（依赖随机数k） |

### 4.2 DSA签名过程

```
DSA参数：
  p: 大素数（L位，1024/2048/3072）
  q: 160/224/256位素数，整除(p-1)
  g: 模p的生成元，g^q ≡ 1 (mod p)
  
密钥对：
  私钥 x: 随机数，1 < x < q
  公钥 y: y = g^x mod p

签名过程：
  1. 选择随机数 k, 0 < k < q
  2. 计算 r = (g^k mod p) mod q
  3. 计算 k_inv = k^(-1) mod q
  4. 计算 s = k_inv * (hash(m) + x*r) mod q
  5. 签名 = (r, s)

验证过程：
  1. 检查 0 < r < q 和 0 < s < q
  2. 计算 w = s^(-1) mod q
  3. 计算 u1 = hash(m) * w mod q
  4. 计算 u2 = r * w mod q
  5. 计算 v = ((g^u1 * y^u2) mod p) mod q
  6. 如果 v == r，则验证通过
```

### 4.3 DSA的随机数问题

DSA签名中使用的随机数k如果泄露或可预测，会导致私钥泄露。

```python
"""
DSA随机数k泄露导致私钥恢复的演示
如果两次签名使用了相同的k，可以恢复私钥
"""

def recover_private_key_from_repeated_k(
    m1_hash: int, r1: int, s1: int,
    m2_hash: int, r2: int, s2: int,
    q: int
) -> int:
    """
    从两次使用相同k的签名中恢复私钥
    
    当k相同时: r1 == r2 = r
    s1 = k^(-1) * (H(m1) + x*r) mod q
    s2 = k^(-1) * (H(m2) + x*r) mod q
    
    s1 - s2 = k^(-1) * (H(m1) - H(m2)) mod q
    k = (H(m1) - H(m2)) * (s1 - s2)^(-1) mod q
    
    x = (s1 * k - H(m1)) * r^(-1) mod q
    """
    # 恢复k
    delta_s = (s1 - s2) % q
    delta_h = (m1_hash - m2_hash) % q
    k = (delta_h * pow(delta_s, -1, q)) % q
    
    # 恢复私钥x
    r = r1  # r1 == r2 因为k相同
    x = ((s1 * k - m1_hash) * pow(r, -1, q)) % q
    
    return x


# 示例（概念性演示）
"""
历史案例：索尼PS3 ECDSA私钥泄露
  Sony在PS3的ECDSA签名中重复使用了固定的k值
  导致私钥被恢复，破解了PS3的安全系统
"""
```

**注意：** DSA已被FIPS 186-5标准废弃，推荐使用ECDSA或EdDSA替代。

---

---

