# RSA题型

RSA是CTF密码学方向最常见的题型。RSA的安全性基于大整数因式分解的困难性。

### 2.1 RSA基础

```python
from Crypto.Util.number import long_to_bytes, bytes_to_long, GCD
from sympy import factorint

# RSA加密过程:
# 1. 选择两个大素数 p, q
# 2. n = p * q
# 3. phi(n) = (p-1) * (q-1)
# 4. 选择公钥 e (通常为65537)
# 5. 计算私钥 d = e^(-1) mod phi(n)
# 6. 加密: c = m^e mod n
# 7. 解密: m = c^d mod n

# 当我们知道p和q时，可以直接解密
def rsa_decrypt(c, e, n, p=None, q=None):
    """RSA解密"""
    if p and q:
        phi = (p - 1) * (q - 1)
    else:
        # 需要因式分解n
        factors = factorint(n)
        p, q = list(factors.keys())
        phi = (p - 1) * (q - 1)
    
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    return long_to_bytes(m)

# 示例
n = 0x76546...  # 模数
e = 65537        # 公钥
c = 0x1234...   # 密文
# 如果n可以分解
flag = rsa_decrypt(c, e, n, p, q)
```

### 2.2 共模攻击（Common Modulus Attack）

```python
from gmpy2 import invert

def common_modulus_attack(n, e1, c1, e2, c2):
    """RSA共模攻击
    条件: 相同模数n，不同公钥e1和e2，gcd(e1, e2) = 1
    """
    # 扩展欧几里得: s1*e1 + s2*e2 = 1
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x
    
    g, s1, s2 = extended_gcd(e1, e2)
    assert g == 1, "e1和e2不互质"
    
    # 处理负指数
    if s1 < 0:
        s1 = -s1
        c1 = invert(c1, n)
    if s2 < 0:
        s2 = -s2
        c2 = invert(c2, n)
    
    # m = c1^s1 * c2^s2 mod n
    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return long_to_bytes(m)

# 使用示例
n = 0x00b351...   # 共同模数
e1 = 0x10001      # 公钥1
e2 = 0x10003      # 公钥2
c1 = 0x6e62d6...  # 密文1
c2 = 0x1011c2...  # 密文2

flag = common_modulus_attack(n, e1, c1, e2, c2)
print(flag)
```

### 2.3 低解密指数攻击（Wiener Attack）

```python
from gmpy2 import iroot

def wiener_attack(e, n):
    """Wiener攻击
    条件: 私钥d较小 (d < n^0.25 / 3)
    利用连分数展开逼近
    """
    # 计算e/n的连分数
    def continued_fraction(a, b):
        cf = []
        while b:
            q = a // b
            cf.append(q)
            a, b = b, a - q * b
        return cf
    
    # 从连分数计算渐进分数
    def convergents(cf):
        convs = []
        n0, n1 = 0, 1
        d0, d1 = 1, 0
        for a in cf:
            n2 = a * n1 + n0
            d2 = a * d1 + d0
            convs.append((n2, d2))
            n0, n1 = n1, n2
            d0, d1 = d1, d2
        return convs
    
    cf = continued_fraction(e, n)
    convs = convergents(cf)
    
    for k, d in convs:
        if k == 0:
            continue
        # 检查phi是否为整数
        if (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        # 解方程 p^2 - (n - phi + 1)p + n = 0
        # 判别式 = (n - phi + 1)^2 - 4n
        discriminant = (n - phi + 1) ** 2 - 4 * n
        if discriminant < 0:
            continue
        sqrt_disc, is_perfect = iroot(discriminant, 2)
        if not is_perfect:
            continue
        p = (n - phi + 1 + sqrt_disc) // 2
        q = (n - phi + 1 - sqrt_disc) // 2
        if p * q == n:
            return d
    return None

# 使用示例
e = 0x...  # 很大的e
n = 0x...  # 模数
d = wiener_attack(e, n)
if d:
    m = pow(c, d, n)
    print(long_to_bytes(m))
```

### 2.4 低加密指数攻击（Small e Attack）

```python
def small_e_attack(c, e, n):
    """低加密指数攻击
    条件: e很小（如e=3），明文m也很小
    当m^e < n时，c = m^e，直接开e次方根
    """
    # 尝试直接开方
    from gmpy2 import iroot
    
    # 当m^e < n时
    m, is_perfect = iroot(c, e)
    if is_perfect:
        return long_to_bytes(m)
    
    # 当m^e略大于n时，尝试加上k*n
    for k in range(10000):
        m, is_perfect = iroot(c + k * n, e)
        if is_perfect:
            return long_to_bytes(m)
    
    return None

# 使用示例
n = 0x...  # 模数
e = 3       # 低位指数
c = 0x...  # 密文
flag = small_e_attack(c, e, n)
```

### 2.5 广播攻击（Broadcast Attack）

```python
def broadcast_attack(ciphertexts, moduli, e):
    """RSA广播攻击
    条件: 相同明文m，用e个不同的模数n加密
    利用中国剩余定理(CRT)恢复 m^e
    """
    # 中国剩余定理
    def crt(remainders, moduli):
        """中国剩余定理求解"""
        N = 1
        for n in moduli:
            N *= n
        
        result = 0
        for r, n in zip(remainders, moduli):
            Ni = N // n
            # 求逆元
            inv = pow(Ni, -1, n)
            result += r * Ni * inv
        
        return result % N
    
    # 使用CRT恢复m^e
    m_pow_e = crt(ciphertexts, moduli)
    
    # 开e次方根
    from gmpy2 import iroot
    m, is_perfect = iroot(m_pow_e, e)
    
    if is_perfect:
        return long_to_bytes(m)
    return None

# 使用示例: e=3, 3组密文和模数
e = 3
c = [c1, c2, c3]  # 三组密文
n = [n1, n2, n3]  # 三组模数
flag = broadcast_attack(c, n, e)
```

### 2.6 Coppersmith定理

```python
# Coppersmith定理: 当明文的高位或低位已知时，可以利用Lattice方法恢复完整明文
# 通常使用SageMath实现

# SageMath代码示例:
"""
# 已知明文高位
n = 0x...  # 模数
e = 3
c = 0x...  # 密文
# 已知明文前k位: m = m0 * 2^(bits-k) + x, 其中x未知

# SageMath Coppersmith实现:
P.<x> = PolynomialRing(Zmod(n))
m0 = 0x...  # 已知高位部分
f = (m0 + x)^e - c
# 使用small_roots方法
roots = f.small_roots(X=2^(bits-k), beta=1, epsilon=0.05)
if roots:
    x = int(roots[0])
    m = m0 + x
    print(bytes.fromhex(hex(m)[2:]))
"""

# Python中使用SageMath
def coppersmith_known_high_bits(n, e, c, known_high, unknown_bits):
    """Coppersmith高位已知攻击（需要SageMath）"""
    # 此函数需要在SageMath环境中运行
    # known_high: 已知的高位值
    # unknown_bits: 未知部分的位数
    pass  # 详见SageMath文档
```

### 2.7 选择密文攻击

```python
def rsa_chosen_ciphertext_attack(c, e, n, decrypt_oracle):
    """选择密文攻击
    条件: 拥有RSA解密Oracle
    通过构造密文获取原始明文
    """
    # 选择 r = 2^e mod n (即r是2的加密)
    r = pow(2, e, n)
    
    # 构造新密文 c' = c * r mod n
    c_prime = (c * r) % n
    
    # 让Oracle解密 c'
    m_prime = decrypt_oracle(c_prime)
    
    # 原始明文 m = m' * r^(-1) mod n
    r_inv = pow(r, -1, n)
    m = (m_prime * r_inv) % n
    
    return long_to_bytes(m)
```

---

---

## 📋 内容审核与补充建议

> 针对「RSA题型」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
