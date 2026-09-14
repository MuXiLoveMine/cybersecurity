# CTF 密码学与Misc方向详解

> 本文档详细讲解CTF竞赛中密码学和Misc（杂项）方向的各类题型，包括古典密码、RSA、AES、哈希、椭圆曲线、隐写术、流量分析、编码解码、取证分析等，每类题型附带代码示例和实战案例。

---

## 目录

- [一、古典密码题型](#一古典密码题型)
- [二、RSA题型](#二rsa题型)
- [三、AES题型](#三aes题型)
- [四、哈希题型](#四哈希题型)
- [五、椭圆曲线密码](#五椭圆曲线密码)
- [六、隐写术](#六隐写术)
- [七、流量分析](#七流量分析)
- [八、编码解码](#八编码解码)
- [九、Forensics取证](#九forensics取证)
- [十、实战案例](#十实战案例)

---

## 一、古典密码题型

### 1.1 凯撒密码（Caesar Cipher）

凯撒密码是最简单的替换密码，通过将字母表位移固定位数实现加密。

```python
def caesar_cipher(text, shift):
    """凯撒密码加密/解密
    text: 明文或密文
    shift: 位移量（正数为加密，负数为解密）
    """
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

# 加密
plaintext = "flag{caesar_cipher}"
ciphertext = caesar_cipher(plaintext, 3)  # 位移3
print(f"密文: {ciphertext}")  # iodj{fdhvdu_flskhu}

# 解密
decrypted = caesar_cipher(ciphertext, -3)
print(f"明文: {decrypted}")

# 暴力破解（遍历所有26种可能）
def caesar_brute_force(ciphertext):
    """凯撒密码暴力破解"""
    for shift in range(26):
        result = caesar_cipher(ciphertext, -shift)
        if 'flag{' in result.lower():
            print(f"[+] 位移={shift}: {result}")

# ROT13是shift=13的特例（加密解密相同）
```

### 1.2 维吉尼亚密码（Vigenere Cipher）

维吉尼亚密码是多表替换密码，使用关键字控制位移。

```python
def vigenere_encrypt(plaintext, key):
    """维吉尼亚密码加密"""
    result = ""
    key = key.upper()
    ki = 0
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('A')
            result += chr((ord(char) - base + shift) % 26 + base)
            ki += 1
        else:
            result += char
    return result

def vigenere_decrypt(ciphertext, key):
    """维吉尼亚密码解密"""
    result = ""
    key = key.upper()
    ki = 0
    for char in ciphertext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shift = ord(key[ki % len(key)]) - ord('A')
            result += chr((ord(char) - base - shift) % 26 + base)
            ki += 1
        else:
            result += char
    return result

# 使用示例
plaintext = "attackatdawn"
key = "LEMON"
ciphertext = vigenere_encrypt(plaintext, key)
print(f"密文: {ciphertext}")  # LXFOPVEFRNHR

# 卡西斯基试验破解
def kasiski_examination(ciphertext):
    """通过分析重复序列推断密钥长度"""
    # 1. 找到重复的3字符以上序列
    repeats = {}
    for i in range(len(ciphertext) - 2):
        for j in range(i + 3, len(ciphertext)):
            seq = ciphertext[i:i+3]
            if seq in ciphertext[j:j+3]:
                dist = j - i
                # 计算距离的因子
                for f in range(2, dist + 1):
                    if dist % f == 0:
                        repeats[f] = repeats.get(f, 0) + 1
    
    # 2. 频率最高的因子可能是密钥长度
    if repeats:
        likely_length = max(repeats, key=repeats.get)
        return likely_length
    return None
```

### 1.3 栅栏密码（Rail Fence Cipher）

```python
def rail_fence_encrypt(text, rails):
    """栅栏密码加密
    text: 明文
    rails: 栅栏数（栏数）
    """
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    
    for char in text:
        fence[rail].append(char)
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction *= -1
    
    return ''.join(''.join(r) for r in fence)

def rail_fence_decrypt(ciphertext, rails):
    """栅栏密码解密"""
    # 计算每个栏的字符数
    fence_len = [0] * rails
    rail = 0
    direction = 1
    for _ in range(len(ciphertext)):
        fence_len[rail] += 1
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction *= -1
    
    # 分割密文到各栏
    idx = 0
    fence = []
    for length in fence_len:
        fence.append(list(ciphertext[idx:idx+length]))
        idx += length
    
    # 交替读取
    result = ""
    rail = 0
    direction = 1
    for _ in range(len(ciphertext)):
        result += fence[rail].pop(0)
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction *= -1
    
    return result

# 使用示例
plaintext = "flag{rail_fence_cipher}"
encrypted = rail_fence_encrypt(plaintext, 3)
print(f"密文: {encrypted}")

# 暴力破解（尝试不同栏数）
for rails in range(2, 10):
    result = rail_fence_decrypt(ciphertext, rails)
    if 'flag{' in result:
        print(f"[+] 栏数={rails}: {result}")
```

### 1.4 培根密码（Bacon Cipher）

```python
def bacon_decode(encoded):
    """培根密码解码
    每个字母用5位二进制表示（A=00000, B=10000, ...）
    """
    bacon_table = {
        'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D',
        'AABAA': 'E', 'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H',
        'ABAAA': 'I', 'ABAAB': 'J', 'ABABA': 'K', 'ABABB': 'L',
        'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O', 'ABBBB': 'P',
        'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
        'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X',
        'BBAAA': 'Y', 'BBAAB': 'Z',
    }
    
    # 将大小写转换为A/B
    binary = ""
    for char in encoded:
        if char.isupper():
            binary += 'B'
        elif char.islower():
            binary += 'A'
    
    # 每5位解码
    result = ""
    for i in range(0, len(binary) - 4, 5):
        five = binary[i:i+5]
        if five in bacon_table:
            result += bacon_table[five]
    
    return result

# 培根密码可能用不同方式编码A和B
# 例如: 字体大小、斜体/非斜体、两种字符等
```

### 1.5 仿射密码（Affine Cipher）

```python
def affine_encrypt(plaintext, a, b):
    """仿射密码加密: E(x) = (a*x + b) mod 26
    a必须与26互质
    """
    result = ""
    for char in plaintext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            result += chr((a * x + b) % 26 + base)
        else:
            result += char
    return result

def affine_decrypt(ciphertext, a, b):
    """仿射密码解密: D(x) = a_inv * (x - b) mod 26"""
    # 求a的模逆元
    a_inv = pow(a, -1, 26)
    result = ""
    for char in ciphertext:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            x = ord(char) - base
            result += chr((a_inv * (x - b)) % 26 + base)
        else:
            result += char
    return result

# 暴力破解
def affine_brute_force(ciphertext):
    """仿射密码暴力破解"""
    # a的取值: 与26互质的数 [1,3,5,7,9,11,15,17,19,21,23,25]
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    
    for a in valid_a:
        for b in range(26):
            result = affine_decrypt(ciphertext, a, b)
            if 'flag{' in result.lower():
                print(f"[+] a={a}, b={b}: {result}")
```

### 1.6 替换密码频率分析

```python
import collections

def frequency_analysis(ciphertext):
    """替换密码频率分析"""
    # 英文字母频率（从高到低）
    eng_freq = "ETAOINSRHLDCUMWFGYPBVKJXQZ"
    
    # 统计密文字母频率
    letters_only = [c for c in ciphertext.upper() if c.isalpha()]
    freq = collections.Counter(letters_only)
    
    # 按频率排序
    sorted_cipher = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    cipher_order = ''.join(c for c, _ in sorted_cipher)
    
    # 创建映射
    mapping = {}
    for i, (cipher_char, _) in enumerate(sorted_cipher):
        if i < len(eng_freq):
            mapping[cipher_char] = eng_freq[i]
    
    # 应用映射
    result = ""
    for char in ciphertext:
        if char.upper() in mapping:
            mapped = mapping[char.upper()]
            result += mapped.lower() if char.islower() else mapped
        else:
            result += char
    
    return result, mapping

# 使用示例
ciphertext = "Xkcwpxmacnxa..."
result, mapping = frequency_analysis(ciphertext)
print(f"初步结果: {result}")
# 频率分析只能给出大致方向，需要人工调整
```

---

## 二、RSA题型

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

## 三、AES题型

### 3.1 ECB模式重放

```python
from Crypto.Cipher import AES

# ECB模式特点:
# 1. 每个块独立加密
# 2. 相同明文块产生相同密文块
# 3. 可以重放/替换密文块

# 利用ECB模式替换密文块
def ecb_block_substitution(ciphertext, old_block, new_block, block_size=16):
    """替换ECB模式中的密文块"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    
    for i, block in enumerate(blocks):
        if block == old_block:
            blocks[i] = new_block
    
    return b''.join(blocks)

# ECB模式信息泄露
# 可以通过密文块的模式推断明文结构
# 例如: 相同密文块表示相同明文块
```

### 3.2 CBC字节翻转攻击

```python
def cbc_bit_flip_attack(ciphertext, target_block_idx, target_pos, 
                        original_byte, desired_byte, block_size=16):
    """CBC字节翻转攻击
    条件: 修改前一个密文块可以改变当前块的解密结果
    
    CBC解密: P[i] = D(C[i]) XOR C[i-1]
    如果修改C[i-1]的第j字节，则P[i]的第j字节也会改变
    """
    blocks = [bytearray(ciphertext[i:i+block_size]) 
              for i in range(0, len(ciphertext), block_size)]
    
    # 修改前一个块的对应位置
    prev_block_idx = target_block_idx - 1
    pos = target_pos
    
    # 翻转公式: new_prev[pos] = old_prev[pos] XOR original XOR desired
    blocks[prev_block_idx][pos] ^= original_byte ^ desired_byte
    
    return b''.join(bytes(b) for b in blocks)

# 使用示例
# 目标: 将第2块的解密结果中的第6字节从'A'改为';'
# original_byte = ord('A') = 0x41
# desired_byte = ord(';') = 0x3b
# 需要修改第1块的第6字节

# 实战场景: 修改Cookie中的admin=false为admin=true
def cbc_cookie_attack(ciphertext):
    """修改加密的Cookie"""
    # 假设Cookie格式: "id=1&admin=false&time=123"
    # 在第2个块中, "admin=false" 中的 'f' 改为 't'
    
    block_size = 16
    blocks = [bytearray(ciphertext[i:i+block_size]) 
              for i in range(0, len(ciphertext), block_size)]
    
    # 找到 "false" 中 'f' 在哪个块的哪个位置
    # 假设在第2块(offset=16)的第11个字节处
    # prev_block = blocks[1], target_pos = 10
    # original = ord('f'), desired = ord('t')
    
    blocks[1][10] ^= ord('f') ^ ord('t')
    
    return b''.join(bytes(b) for b in blocks)
```

### 3.3 Padding Oracle攻击

```python
import requests

def padding_oracle_attack(ciphertext, iv, oracle_url, block_size=16):
    """Padding Oracle攻击
    条件: 服务端返回Padding是否正确（通过错误信息或响应差异）
    
    原理: CBC解密时 P[i] = D(C[i]) XOR C[i-1]
    通过修改C[i-1]并观察Padding是否正确
    可以逐字节恢复中间值 D(C[i])
    然后与原始C[i-1]异或得到明文
    """
    def check_padding(c, iv):
        """检查Padding是否有效"""
        data = iv + c
        r = requests.get(oracle_url, params={"data": data.hex()})
        return "padding valid" in r.text  # 根据实际响应判断
    
    blocks = [ciphertext[i:i+block_size] 
              for i in range(0, len(ciphertext), block_size)]
    
    plaintext = b''
    
    for block_idx in range(len(blocks)):
        # 中间值
        intermediate = bytearray(block_size)
        # 当前块
        target_block = blocks[block_idx]
        # 前一个块（第0块用IV）
        prev_block = bytearray(iv) if block_idx == 0 else bytearray(blocks[block_idx - 1])
        
        # 从最后一个字节开始
        for pos in range(block_size - 1, -1, -1):
            # 当前Padding值
            pad_val = block_size - pos
            
            # 设置已知中间值
            test_prev = bytearray(block_size)
            for i in range(pos + 1, block_size):
                test_prev[i] = intermediate[i] ^ pad_val
            
            # 暴力当前字节
            found = False
            for guess in range(256):
                test_prev[pos] = guess
                
                if check_padding(bytes(target_block), bytes(test_prev)):
                    # 需要验证（可能是Padding巧合）
                    if pos > 0:
                        # 修改前一个字节验证
                        test_prev2 = bytearray(test_prev)
                        test_prev2[pos - 1] ^= 1
                        if not check_padding(bytes(target_block), bytes(test_prev2)):
                            continue
                    
                    # 中间值 = guess XOR pad_val
                    intermediate[pos] = guess ^ pad_val
                    # 明文字节 = 中间值 XOR 原始前块
                    plaintext_byte = intermediate[pos] ^ prev_block[pos]
                    print(f"[+] 块{block_idx} 位置{pos}: {chr(plaintext_byte)}")
                    found = True
                    break
            
            if not found:
                print(f"[-] 块{block_idx} 位置{pos} 破解失败")
                return None
        
        # 组装明文
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev_block[i]])
    
    return plaintext

# 使用示例
ciphertext = bytes.fromhex("...")
iv = bytes.fromhex("...")
plaintext = padding_oracle_attack(ciphertext, iv, "http://example.com/decrypt")
print(plaintext)
```

---

## 四、哈希题型

### 4.1 长度扩展攻击

```python
# 长度扩展攻击利用: 
# Merkle-Damgard结构的哈希函数（MD5, SHA-1, SHA-256）
# 如果知道 H(secret || message) 的结果
# 可以计算 H(secret || message || padding || extension) 而不需要知道secret

# 使用HashPumpy工具
# pip install hashpumpy

def hash_length_extension():
    """MD5长度扩展攻击"""
    import hashpumpy
    
    # 已知信息
    known_hash = "5f4dcc3b5aa765d61d8327deb882cf99"  # H(secret || message)
    known_message = b"key=value"
    appended_data = b"&admin=true"
    
    # key_length需要爆破
    for key_length in range(1, 50):
        new_hash, new_message = hashpumpy.hashpump(
            known_hash,      # 已知哈希
            known_message,   # 已知消息
            appended_data,   # 追加的数据
            key_length        # 密钥长度
        )
        print(f"[*] key_len={key_length}: hash={new_hash}, msg={new_message}")
        # 发送新hash和消息验证是否成功

# 手动实现MD5长度扩展
def md5_length_extension_manual(original_hash, original_msg, append_data, key_len):
    """手动实现MD5长度扩展攻击"""
    from struct import pack
    
    # 1. 计算原始消息的padding
    msg_len = key_len + len(original_msg)
    padding = b'\x80'
    padding += b'\x00' * ((55 - msg_len % 64) % 64)
    padding += pack('<Q', msg_len * 8)
    
    # 2. 构造新消息
    new_msg = original_msg + padding + append_data
    
    # 3. 从原始哈希恢复MD5内部状态
    # MD5状态是4个32位整数
    state = [int(original_hash[i:i+8], 16) for i in range(0, 32, 8)]
    
    # 4. 计算append_data的padding
    append_len = len(new_msg)
    append_padding = b'\x80'
    append_padding += b'\x00' * ((55 - append_len % 64) % 64)
    append_padding += pack('<Q', append_len * 8)
    
    # 5. 使用恢复的状态继续哈希append_data
    # 需要修改MD5实现，接受初始状态和消息长度
    # ...（此处省略具体MD5实现）
    
    return new_msg  # 返回构造的新消息
```

### 4.2 哈希碰撞

```python
# MD5碰撞构造
# 使用HashClash工具或fastcoll工具

# fastcoll使用:
# ./fastcoll -o prefix1.bin prefix2.bin
# 生成两个前缀相同但MD5值相同的文件

# CTF中常见的哈希碰撞场景:
# 1. 找到两个不同输入产生相同的MD5
# 2. 绕过"不等于"的检查

import hashlib

# 生成碰撞对（使用预计算结果）
collision1 = bytes.fromhex("d131dd02c5e8eec00993766a...")  # 碰撞消息1
collision2 = bytes.fromhex("d131dd02c5e8eec00993766a...")  # 碰撞消息2

assert collision1 != collision2
assert hashlib.md5(collision1).hexdigest() == hashlib.md5(collision2).hexdigest()
print("[+] MD5碰撞验证成功")
```

### 4.3 彩虹表攻击

```python
# 彩虹表是预计算的哈希-明文对照表
# 常用于破解常见密码的哈希

# 使用在线彩虹表
rainbow_table_sites = [
    "https://crackstation.net/",
    "https://cmd5.com/",       # 中文密码哈希查询
    "https://www.hashkiller.io/",
]

# Python实现简单的哈希爆破
import hashlib
import itertools
import string

def hash_brute_force(target_hash, hash_type='md5', 
                     charset=string.ascii_lowercase + string.digits,
                     max_length=8):
    """暴力破解哈希"""
    if hash_type == 'md5':
        hash_func = hashlib.md5
    elif hash_type == 'sha256':
        hash_func = hashlib.sha256
    else:
        hash_func = hashlib.md5
    
    for length in range(1, max_length + 1):
        for candidate in itertools.product(charset, repeat=length):
            plaintext = ''.join(candidate)
            h = hash_func(plaintext.encode()).hexdigest()
            if h == target_hash:
                return plaintext
    return None

# 使用示例
target = "d41d8cd98f00b204e9800998ecf8427e"  # md5("")
# 注意: 空字符串的MD5
result = hash_brute_force(target, 'md5')
if result is not None:
    print(f"[+] 破解结果: {result}")
```

---

## 五、椭圆曲线密码

### 5.1 ECDLP（椭圆曲线离散对数问题）

```python
# ECC密码基于椭圆曲线离散对数问题(ECDLP)
# 在椭圆曲线 y^2 = x^3 + ax + b (mod p) 上
# 给定基点G和Q = kG，求k是困难的

# SageMath中的ECC操作
"""
# SageMath代码:
# 定义椭圆曲线
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
E = EllipticCurve(GF(p), [a, b])

# 定义基点
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = E(Gx, Gy)

# 计算公钥
k = 12345  # 私钥
Q = k * G   # 公钥
print(Q)
"""

# Pohlig-Hellman算法
# 当曲线阶的因子较小时，可以分解问题
def pohlig_hellman_ecdlp():
    """Pohlig-Hellman算法求解ECDLP
    条件: 椭圆曲线的阶有小的素因子
    """
    # SageMath实现:
    """
    # 假设曲线阶 n = p1^e1 * p2^e2 * ... * pk^ek
    # 其中pi都是小素数
    
    # 对每个因子pi:
    # 计算 ki = k mod pi^ei
    # 使用Pohlig-Hellman分解:
    
    n = E.order()  # 曲线阶
    factors = factor(n)  # 因式分解
    
    remainders = []
    moduli = []
    
    for p, e in factors:
        # 计算k mod p^e
        Qi = Q * (n // (p^e))
        Gi = G * (n // (p^e))
        ki = discrete_log(Qi, Gi, operation='+')  # 在小阶子群上求解
        remainders.append(ki)
        moduli.append(p^e)
    
    # 使用CRT组合结果
    k = CRT(remainders, moduli)
    """
    pass
```

---

## 六、隐写术

### 6.1 图片LSB隐写

```python
from PIL import Image
import numpy as np

def lsb_extract(image_path):
    """提取图片LSB隐写数据"""
    img = Image.open(image_path)
    pixels = np.array(img)
    
    # 提取每个像素的最低位
    bits = []
    for row in pixels:
        for pixel in row:
            for channel in pixel[:3]:  # RGB三通道
                bits.append(channel & 1)
    
    # 将bit序列转换为字节
    data = b''
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        data += bytes([byte])
        if data[-2:] == b'\x00\x00':  # 遇到结束标记
            break
    
    return data

# 使用StegSolve工具
# StegSolve可以查看图片的各个位平面
# Analyze > Data Extract 可以提取LSB数据
# 常用组合: Red0 Green0 Blue0 (RGB各最低位)

# 使用zsteg工具（自动检测PNG/BMP隐写）
# zsteg image.png
# zsteg -a image.png  # 尝试所有方法
```

### 6.2 图片尾部数据

```python
def extract_trailing_data(image_path):
    """提取图片文件尾部隐藏的数据"""
    with open(image_path, 'rb') as f:
        content = f.read()
    
    # 检查常见的文件头签名
    signatures = {
        b'PK': 'ZIP',
        b'\x89PNG': 'PNG',
        b'\xff\xd8\xff': 'JPEG',
        b'GIF89a': 'GIF',
        b'%PDF': 'PDF',
        b'Rar': 'RAR',
        b'7z': '7z',
    }
    
    # 找到第一个文件结束后的附加数据
    for sig, name in signatures.items():
        pos = content.find(sig, 10)  # 跳过文件头
        if pos > 0:
            print(f"[+] 在偏移 {pos} 发现 {name} 文件")
            with open(f'extracted_{name.lower()}', 'wb') as f:
                f.write(content[pos:])
            return content[pos:]
    
    return None

# 使用binwalk自动提取
# binwalk image.png
# binwalk -e image.png  # 自动提取嵌入文件
```

### 6.3 音频隐写

```python
# 音频隐写常见方法:
# 1. 频谱图中隐藏文字（需要打开频谱图查看）
# 2. LSB隐写（类似图片）
# 3. DTMF信号解码
# 4. 摩斯电码

# 使用Audacity查看频谱图:
# 打开音频 → 切换到频谱图视图

# Python提取音频LSB
def audio_lsb_extract(audio_path):
    """提取WAV音频LSB隐写"""
    import wave
    
    with wave.open(audio_path, 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        n_frames = wav.getnframes()
        frames = wav.readframes(n_frames)
    
    # 根据采样宽度解析数据
    if sample_width == 1:
        samples = np.frombuffer(frames, dtype=np.uint8)
    elif sample_width == 2:
        samples = np.frombuffer(frames, dtype=np.int16)
    
    # 提取LSB
    bits = samples & 1
    data = b''
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        data += bytes([byte])
        if len(data) > 2 and data[-2:] == b'\x00\x00':
            break
    
    return data
```

### 6.4 文档隐写

```python
# Word文档隐写
def extract_word_hidden(word_path):
    """提取Word文档隐藏内容"""
    import zipfile
    
    # Word文档本质是ZIP文件
    with zipfile.ZipFile(word_path, 'r') as z:
        # 检查document.xml中的隐藏文本
        # <w:vanish> 标记的文本是隐藏的
        # document.xml.rels 中可能有隐藏链接
        for name in z.namelist():
            print(f"[*] 文件: {name}")
        
        # 读取document.xml
        with z.open('word/document.xml') as f:
            content = f.read().decode('utf-8', errors='ignore')
            # 查找隐藏文本标记
            if 'vanish' in content:
                print("[+] 发现隐藏文本标记")
            # 查找白色字体
            if 'FFFFFF' in content or 'ffffff' in content:
                print("[+] 发现白色字体（可能隐藏文本）")

# PDF隐写
def extract_pdf_hidden(pdf_path):
    """提取PDF隐藏内容"""
    # 方法1: 查看PDF对象中的未引用流
    # 方法2: 检查JavaScript
    # 方法3: 检查注释层
    # 使用pdftk或qpdf提取
    pass
```

### 6.5 StegSolve使用

```
StegSolve是Java写的图片隐写分析工具:
java -jar StegSolve.jar

功能:
1. File > Open - 打开图片
2. 左右箭头 - 切换不同位平面查看
3. Analyze > Data Extract - 提取位数据
   - Bit Planes: 选择提取哪些位
   - Order: MSB/LSB, Row/Column
4. Analyze > Frame Browser - 查看GIF帧
5. Analyze > Steregram Solve - 立体图隐写
6. Analyse > File Format - 查看文件格式信息
```

---

## 七、流量分析

### 7.1 Wireshark过滤

```python
# Wireshark常用过滤器
wireshark_filters = {
    # 协议过滤
    "http": "显示所有HTTP流量",
    "dns": "显示DNS查询",
    "tcp": "显示TCP流量",
    "icmp": "显示Ping流量",
    "ftp": "显示FTP流量",
    
    # HTTP过滤
    "http.method == POST": "POST请求",
    "http.method == GET": "GET请求",
    "http.response.code == 200": "200响应",
    "http.request.uri contains flag": "URL包含flag",
    "http.host contains example.com": "特定主机",
    "http.cookie": "包含Cookie的请求",
    "http.authorization": "包含认证信息",
    
    # TCP过滤
    "tcp.port == 80": "端口80",
    "tcp.port == 443": "端口443",
    "tcp.flags.syn == 1": "SYN包",
    
    # 字符串过滤
    'frame contains "flag"': '帧数据包含flag',
    'http contains "password"': 'HTTP数据包含password',
    
    # 组合过滤
    "http and ip.src == 192.168.1.1": "来自特定IP的HTTP",
    "tcp.port == 80 and http.request.method == POST": "POST到80端口",
}

# tshark命令行工具
tshark_commands = """
# 提取HTTP流
tshark -r capture.pcapng -Y "http" -T fields -e http.request.uri

# 导出HTTP对象（文件）
tshark -r capture.pcapng --export-objects http,./output/

# 提取特定字段
tshark -r capture.pcapng -Y "http" -T fields -e ip.src -e http.host -e http.request.uri

# 过滤并显示
tshark -r capture.pcapng -Y "http.request.method == POST" -T fields -e tcp.payload

# 提取TCP流
tshark -r capture.pcapng -Y "tcp.stream eq 0" -T fields -e tcp.payload
"""
```

### 7.2 USB流量还原

```python
def analyze_usb_traffic(pcap_path):
    """分析USB键盘流量"""
    # 使用tshark提取USB数据
    import subprocess
    
    # 提取USB HID数据
    result = subprocess.run(
        ['tshark', '-r', pcap_path, '-Y', 'usb.capdata', 
         '-T', 'fields', '-e', 'usb.capdata'],
        capture_output=True, text=True
    )
    
    # USB键盘键值映射表
    keymap = {
        0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd',
        0x08: 'e', 0x09: 'f', 0x0a: 'g', 0x0b: 'h',
        0x0c: 'i', 0x0d: 'j', 0x0e: 'k', 0x0f: 'l',
        0x10: 'm', 0x11: 'n', 0x12: 'o', 0x13: 'p',
        0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
        0x18: 'u', 0x19: 'v', 0x1a: 'w', 0x1b: 'x',
        0x1c: 'y', 0x1d: 'z', 0x1e: '1', 0x1f: '2',
        0x20: '3', 0x21: '4', 0x22: '5', 0x23: '6',
        0x24: '7', 0x25: '8', 0x26: '9', 0x27: '0',
        0x28: 'Enter', 0x29: 'ESC', 0x2a: 'DEL',
        0x2b: 'TAB', 0x2c: 'SPACE', 0x2d: '-',
        0x2e: '=', 0x2f: '[', 0x30: ']',
        0x33: ';', 0x34: "'", 0x36: ',',
        0x37: '.', 0x38: '/',
    }
    
    # 解析键盘输入
    output = ""
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        # USB HID格式: 修饰键 保留键 键码1 键码2...
        parts = line.strip().split(':')
        if len(parts) >= 3:
            keycode = int(parts[2], 16)
            if keycode in keymap:
                key = keymap[keycode]
                # Shift键修饰
                modifier = int(parts[0], 16)
                if modifier in (0x02, 0x20):  # 左Shift或右Shift
                    key = key.upper() if key.isalpha() else key
                output += key
    
    return output

# USB鼠标流量分析
def analyze_usb_mouse(pcap_path):
    """分析USB鼠标流量"""
    import subprocess
    
    result = subprocess.run(
        ['tshark', '-r', pcap_path, '-Y', 'usb.capdata',
         '-T', 'fields', '-e', 'usb.capdata'],
        capture_output=True, text=True
    )
    
    # 鼠标数据格式: 按键状态 X位移 Y位移
    positions = [(0, 0)]
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.strip().split(':')
        if len(parts) >= 3:
            buttons = int(parts[0], 16)
            x = int(parts[1] + parts[2], 16)  # 小端序
            y = int(parts[3] + parts[4], 16) if len(parts) > 4 else 0
            # 转换为有符号整数
            if x > 32767: x -= 65536
            if y > 32767: y -= 65536
            
            last_x, last_y = positions[-1]
            positions.append((last_x + x, last_y + y))
            
            # 左键按下
            if buttons & 1:
                print(f"点击位置: ({last_x + x}, {last_y + y})")
    
    return positions
```

### 7.3 TLS密钥提取

```python
# 当PCAP文件包含TLS加密流量时
# 需要TLS密钥才能解密

# 方法1: 从浏览器导出TLS密钥
# 设置环境变量 SSLKEYLOGFILE=/path/to/keys.log
# 然后在Wireshark中: Edit > Preferences > Protocols > TLS > (Pre)-Master-Secret log filename

# 方法2: 从内存dump中提取
def extract_tls_keys_from_memory(dump_path):
    """从内存dump中提取TLS密钥"""
    with open(dump_path, 'rb') as f:
        data = f.read()
    
    # 搜索TLS Client Random模式
    # TLS 1.2 Master Secret格式:
    # "CLIENT_RANDOM" + " " + client_random_hex + " " + master_secret_hex
    
    import re
    pattern = rb'CLIENT_RANDOM ([0-9a-f]{64}) ([0-9a-f]{96})'
    matches = re.findall(pattern, data)
    
    with open('sslkeys.log', 'w') as f:
        for client_random, master_secret in matches:
            line = f"CLIENT_RANDOM {client_random.decode()} {master_secret.decode()}\n"
            f.write(line)
            print(f"[+] 提取密钥: {line.strip()}")
    
    return 'sslkeys.log'
```

---

## 八、编码解码

### 8.1 Base系列

```python
import base64
import base58

# Base16 (Hex)
def base16_encode(data):
    return data.hex()
def base16_decode(data):
    return bytes.fromhex(data)

# Base32
def base32_encode(data):
    return base64.b32encode(data).decode()
def base32_decode(data):
    return base64.b32decode(data)

# Base58
def base58_encode(data):
    return base58.b58encode(data).decode()
def base58_decode(data):
    return base58.b58decode(data).decode()

# Base64
def base64_encode(data):
    return base64.b64encode(data).decode()
def base64_decode(data):
    # 处理缺少padding的情况
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.b64decode(data)

# Base85 (Ascii85)
def base85_encode(data):
    return base64.a85encode(data).decode()
def base85_decode(data):
    return base64.a85decode(data)

# 自动识别Base编码
def auto_decode(encoded):
    """自动尝试多种解码"""
    decoders = [
        ('Base16', base16_decode),
        ('Base32', base32_decode),
        ('Base58', base58_decode),
        ('Base64', base64_decode),
        ('Base85', base85_decode),
    ]
    
    results = []
    for name, decoder in decoders:
        try:
            decoded = decoder(encoded)
            if decoded and all(32 <= b < 127 for b in decoded):
                results.append((name, decoded))
        except:
            pass
    
    return results
```

### 8.2 URL编码

```python
import urllib.parse

# URL编码/解码
def url_encode(data):
    return urllib.parse.quote(data)

def url_decode(data):
    return urllib.parse.unquote(data)

# 多重URL编码
def multi_url_decode(data, max_iter=10):
    """多重URL解码"""
    for i in range(max_iter):
        decoded = urllib.parse.unquote(data)
        if decoded == data:
            break
        data = decoded
    return data
```

### 8.3 Unicode编码

```python
def unicode_decode(data):
    """Unicode多种格式解码"""
    import re
    
    # \uXXXX 格式
    unicode_pattern = r'\\u([0-9a-fA-F]{4})'
    result = re.sub(unicode_pattern, 
                    lambda m: chr(int(m.group(1), 16)), data)
    
    # &#XXXX; 格式 (HTML实体)
    html_pattern = r'&#(\d+);'
    result = re.sub(html_pattern,
                    lambda m: chr(int(m.group(1))), result)
    
    # &#xXXXX; 格式 (HTML十六进制实体)
    html_hex_pattern = r'&#x([0-9a-fA-F]+);'
    result = re.sub(html_hex_pattern,
                    lambda m: chr(int(m.group(1), 16)), result)
    
    return result

# 宽字节/全角字符转换
def fullwidth_to_halfwidth(text):
    """全角字符转半角"""
    result = ""
    for char in text:
        code = ord(char)
        if code == 0x3000:
            code = 0x20
        elif 0xFF01 <= code <= 0xFF5E:
            code -= 0xFEE0
        result += chr(code)
    return result
```

### 8.4 Morse电码

```python
MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
    '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9', '-----': '0',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
    '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')',
    '.-...': '&', '---...': ':', '-.-.-.': ';', '-...-': '=',
    '.-.-.': '+', '-....-': '-', '..--.-': '_', '.-..-.': '"',
    '...-..-': '$', '.--.-.': '@',
}

def morse_decode(morse_text):
    """摩斯电码解码"""
    # 分隔符可能是空格或斜杠
    words = morse_text.strip().split(' / ')  # 单词间用/分隔
    
    result = ""
    for word in words:
        letters = word.strip().split()
        for letter in letters:
            if letter in MORSE_CODE:
                result += MORSE_CODE[letter]
            else:
                result += '?'
        result += ' '
    
    return result.strip()

def morse_encode(text):
    """摩斯电码编码"""
    reverse_morse = {v: k for k, v in MORSE_CODE.items()}
    result = []
    for char in text.upper():
        if char in reverse_morse:
            result.append(reverse_morse[char])
        elif char == ' ':
            result.append('/')
    return ' '.join(result)
```

### 8.5 Brainfuck

```python
def brainfuck_interpret(code):
    """Brainfuck解释器"""
    tape = [0] * 30000
    ptr = 0
    pc = 0
    output = ""
    
    # 预处理匹配括号
    bracket_map = {}
    stack = []
    for i, c in enumerate(code):
        if c == '[':
            stack.append(i)
        elif c == ']':
            if stack:
                j = stack.pop()
                bracket_map[i] = j
                bracket_map[j] = i
    
    while pc < len(code):
        cmd = code[pc]
        if cmd == '>': ptr += 1
        elif cmd == '<': ptr -= 1
        elif cmd == '+': tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == '-': tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == '.': output += chr(tape[ptr])
        elif cmd == ',': pass  # 需要输入
        elif cmd == '[':
            if tape[ptr] == 0:
                pc = bracket_map[pc]
        elif cmd == ']':
            if tape[ptr] != 0:
                pc = bracket_map[pc]
        pc += 1
    
    return output

# Ook!语言（Brainfuck的变体）
def ook_decode(ook_code):
    """Ook!语言解码"""
    # Ook! . = >, Ook! ? = <, Ook! ! = +
    # 各种组合对应Brainfuck指令
    ook_to_bf = {
        'Ook. Ook?': '>', 'Ook? Ook.': '<',
        'Ook. Ook.': '+', 'Ook! Ook!': '-',
        'Ook! Ook.': '.', 'Ook. Ook!': ',',
        'Ook! Ook?': '[', 'Ook? Ook!': ']',
    }
    
    bf_code = ook_code
    for ook, bf in ook_to_bf.items():
        bf_code = bf_code.replace(ook, bf)
    
    return brainfuck_interpret(bf_code)
```

---

## 九、Forensics取证

### 9.1 磁盘取证

```python
# 使用Autopsy进行磁盘取证分析
# Autopsy是基于The Sleuth Kit的图形化取证工具

# 常见磁盘取证分析:
disk_forensics = {
    "文件恢复": "使用foremost/photorec恢复已删除文件",
    "时间线分析": "分析文件的MAC时间（Modified/Accessed/Created）",
    "隐藏分区": "检查分区表中的隐藏分区",
    " slack空间": "检查文件slack空间中的隐藏数据",
    "交换分区": "分析swap分区中的数据",
    "磁盘镜像": "使用dd制作磁盘镜像",
}

# 使用foremost恢复文件
# foremost -i image.dd -o output/
# foremost -t jpeg,png -i image.dd  # 指定恢复类型

# 使用tshark分析网络取证
# tshark -r evidence.pcap -Y "http" -T fields -e http.request.uri

# 分析NTFS Alternate Data Stream (ADS)
# dir /r  # Windows查看ADS
```

### 9.2 内存取证

```python
# 使用Volatility进行内存分析
# Volatility是内存取证的标准工具

volatility_commands = {
    # 基本信息识别
    "imageinfo": "volatility -f mem.dmp imageinfo",
    
    # 进程分析
    "pslist": "volatility -f mem.dmp --profile=Win7SP1x64 pslist",
    "pstree": "volatility -f mem.dmp --profile=Win7SP1x64 pstree",
    "psscan": "volatility -f mem.dmp --profile=Win7SP1x64 psscan",  # 发现已隐藏进程
    
    # 网络连接
    "netscan": "volatility -f mem.dmp --profile=Win7SP1x64 netscan",
    "connections": "volatility -f mem.dmp --profile=Win7SP1x64 connections",
    
    # 注册表
    "hivelist": "volatility -f mem.dmp --profile=Win7SP1x64 hivelist",
    "hashdump": "volatility -f mem.dmp --profile=Win7SP1x64 hashdump",  # 提取密码哈希
    
    # 文件提取
    "filescan": "volatility -f mem.dmp --profile=Win7SP1x64 filescan",
    "dump-files": "volatility -f mem.dmp --profile=Win7SP1x64 dump-files -D output/",
    
    # 命令行历史
    "cmdline": "volatility -f mem.dmp --profile=Win7SP1x64 cmdline",
    "consoles": "volatility -f mem.dmp --profile=Win7SP1x64 consoles",
    
    # 恶意代码检测
    "malfind": "volatility -f mem.dmp --profile=Win7SP1x64 malfind",
    "yarascan": "volatility -f mem.dmp --profile=Win7SP1x64 yarascan",
    
    # 进程内存dump
    "memdump": "volatility -f mem.dmp --profile=Win7SP1x64 memdump -p <PID> -D output/",
}

# Python辅助分析
def analyze_memory_dump(dump_path, profile):
    """分析内存dump"""
    import subprocess
    
    # 获取进程列表
    result = subprocess.run(
        ['volatility', '-f', dump_path, '--profile', profile, 'pslist'],
        capture_output=True, text=True
    )
    
    # 解析进程列表
    processes = []
    for line in result.stdout.split('\n')[3:]:  # 跳过表头
        parts = line.split()
        if len(parts) >= 6:
            processes.append({
                'pid': parts[2],
                'ppid': parts[3],
                'name': parts[4] if len(parts) > 4 else 'Unknown',
            })
    
    return processes
```

### 9.3 日志分析

```python
import re
from collections import Counter

def analyze_apache_log(log_path):
    """分析Apache/Nginx访问日志"""
    with open(log_path, 'r') as f:
        lines = f.readlines()
    
    # 统计IP访问频率
    ip_counter = Counter()
    url_counter = Counter()
    status_counter = Counter()
    
    # Apache日志格式示例:
    # 192.168.1.1 - - [10/Oct/2023:13:55:36] "GET /admin HTTP/1.1" 200 1234
    log_pattern = r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+)'
    
    for line in lines:
        match = re.match(log_pattern, line)
        if match:
            ip, time, method, url, status = match.groups()
            ip_counter[ip] += 1
            url_counter[url] += 1
            status_counter[status] += 1
    
    print("=== 访问频率最高的IP ===")
    for ip, count in ip_counter.most_common(10):
        print(f"  {ip}: {count}次")
    
    print("=== 访问频率最高的URL ===")
    for url, count in url_counter.most_common(10):
        print(f"  {url}: {count}次")
    
    print("=== 状态码分布 ===")
    for status, count in status_counter.most_common():
        print(f"  {status}: {count}次")
    
    # 检测攻击行为
    attack_patterns = {
        "SQL注入": r"union|select|'|or 1=1|information_schema",
        "XSS": r"<script|onerror|alert|javascript:",
        "目录遍历": r"\.\./|%2e%2e%2f",
        "命令注入": r";|cat|ls|whoami|id",
        "文件包含": r"php://|file://|data://",
    }
    
    print("=== 可疑请求 ===")
    for line in lines:
        for attack, pattern in attack_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                print(f"  [{attack}] {line.strip()[:100]}")
                break
```

---

## 十、实战案例

### 案例1：RSA共模攻击

```python
"""
题目: 给出两组RSA密文，使用相同的n
n = 0x00...
e1 = 0x10001
e2 = 0x10003
c1 = 0x...
c2 = 0x...
"""
from Crypto.Util.number import long_to_bytes
from gmpy2 import invert

n = 0x00b351a5...
e1 = 0x10001
e2 = 0x10003
c1 = 0x6e62d6...
c2 = 0x1011c2...

# 共模攻击
def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x

g, s1, s2 = extended_gcd(e1, e2)

if s1 < 0:
    s1 = -s1
    c1 = invert(c1, n)
if s2 < 0:
    s2 = -s2
    c2 = invert(c2, n)

m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
flag = long_to_bytes(m)
print(f"[+] Flag: {flag}")
```

### 案例2：AES-CBC Padding Oracle

```python
"""
题目: Web应用使用AES-CBC加密，返回Padding错误信息
URL: http://example.com/decrypt?iv=xxxx&data=yyyy
"""
import requests

def padding_oracle_exploit(url, iv, ciphertext):
    """Padding Oracle攻击获取明文"""
    block_size = 16
    blocks = [ciphertext[i:i+block_size] 
              for i in range(0, len(ciphertext), block_size)]
    
    plaintext = b''
    
    for bi in range(len(blocks)):
        intermediate = bytearray(block_size)
        prev = bytearray(iv) if bi == 0 else bytearray(blocks[bi-1])
        
        for pos in range(block_size-1, -1, -1):
            pad_val = block_size - pos
            test_prev = bytearray(block_size)
            
            for i in range(pos+1, block_size):
                test_prev[i] = intermediate[i] ^ pad_val
            
            for guess in range(256):
                test_prev[pos] = guess
                params = {
                    'iv': bytes(test_prev).hex(),
                    'data': blocks[bi].hex()
                }
                r = requests.get(url, params=params)
                
                if "padding error" not in r.text.lower():
                    intermediate[pos] = guess ^ pad_val
                    plaintext_byte = intermediate[pos] ^ prev[pos]
                    print(f"[+] 块{bi} 字节{pos}: {chr(plaintext_byte)}")
                    break
        
        for i in range(block_size):
            plaintext += bytes([intermediate[i] ^ prev[i]])
    
    return plaintext

# 执行攻击
iv = bytes.fromhex("...")
ciphertext = bytes.fromhex("...")
result = padding_oracle_exploit("http://example.com/decrypt", iv, ciphertext)
print(result)
```

### 案例3：图片LSB隐写

```python
"""
题目: 给出一张PNG图片，Flag隐藏在LSB中
"""
from PIL import Image
import numpy as np

def lsb_stego_extract(image_path):
    """提取LSB隐写数据"""
    img = Image.open(image_path)
    pixels = list(img.getdata())
    
    bits = []
    for pixel in pixels:
        # RGBA或RGB
        for channel in pixel[:3]:
            bits.append(channel & 1)
    
    # 转换为字节
    data = b''
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        data += bytes([byte])
        if data.endswith(b'\x00'):
            break
    
    # 查找flag
    if b'flag{' in data or b'CTF{' in data:
        start = data.find(b'flag{') if b'flag{' in data else data.find(b'CTF{')
        end = data.find(b'}', start) + 1
        print(f"[+] Flag: {data[start:end].decode()}")
    else:
        print(f"[*] 提取数据: {data[:100]}")

lsb_stego_extract("challenge.png")
```

### 案例4：流量分析 - HTTP请求提取Flag

```python
"""
题目: 给出一个PCAP文件，Flag在某HTTP请求中
"""
import subprocess

def analyze_pcap(pcap_path):
    """分析PCAP文件"""
    # 提取所有HTTP请求
    result = subprocess.run(
        ['tshark', '-r', pcap_path, '-Y', 'http.request',
         '-T', 'fields', '-e', 'http.request.uri',
         '-e', 'http.host', '-e', 'http.request.method'],
        capture_output=True, text=True
    )
    
    for line in result.stdout.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 3:
            uri, host, method = parts
            print(f"[*] {method} {host}{uri}")
            
            # 检查是否包含flag
            if 'flag' in uri.lower():
                print(f"[+] 可能在URL中: {uri}")
    
    # 导出HTTP对象
    subprocess.run(
        ['tshark', '-r', pcap_path, 
         '--export-objects', f'http,{"./output/"}'],
        capture_output=True
    )
    
    # 检查导出的文件
    import os
    for f in os.listdir('./output/'):
        with open(f'./output/{f}', 'rb') as fp:
            content = fp.read()
            if b'flag{' in content:
                idx = content.find(b'flag{')
                end = content.find(b'}', idx) + 1
                print(f"[+] Flag: {content[idx:end].decode()}")

analyze_pcap("capture.pcapng")
```

### 案例5：内存取证 - Volatility分析

```python
"""
题目: 给出一个Windows内存dump文件，找到Flag
"""
import subprocess

def memory_forensics(mem_path):
    """内存取证分析"""
    # 步骤1: 识别操作系统版本
    result = subprocess.run(
        ['volatility', '-f', mem_path, 'imageinfo'],
        capture_output=True, text=True
    )
    # 从输出中提取profile
    profile = "Win7SP1x64"  # 根据实际输出确定
    
    # 步骤2: 查看进程列表
    result = subprocess.run(
        ['volatility', '-f', mem_path, '--profile', profile, 'pslist'],
        capture_output=True, text=True
    )
    print("[*] 进程列表:")
    print(result.stdout)
    
    # 步骤3: 搜索包含flag的字符串
    result = subprocess.run(
        ['volatility', '-f', mem_path, '--profile', profile,
         'filescan', '--name=flag'],
        capture_output=True, text=True
    )
    print("[*] 文件扫描:")
    print(result.stdout)
    
    # 步骤4: 检查命令行历史
    result = subprocess.run(
        ['volatility', '-f', mem_path, '--profile', profile, 'cmdline'],
        capture_output=True, text=True
    )
    print("[*] 命令行历史:")
    print(result.stdout)
    
    # 步骤5: 如果找到相关进程，dump其内存
    # vol.py -f mem.dmp --profile=Win7SP1x64 memdump -p <PID> -D ./dump/
    # 然后在dump文件中搜索flag

memory_forensics("challenge.dmp")
```

---

## 十一、安全最佳实践

### 11.1 密码学安全

```python
# 密码学安全建议
crypto_security = {
    "不要使用弱算法": "避免MD5、SHA-1、DES、RC4等已被攻破的算法",
    "使用标准实现": "使用PyCryptodome/OpenSSL等成熟库，不要自己实现",
    "随机数安全": "使用secrets模块而非random模块生成密钥",
    "密钥管理": "密钥不应硬编码，使用KMS或环境变量",
    "IV/Nonce唯一性": "CBC的IV必须不可预测，CTR的Nonce必须唯一",
    "填充安全": "使用PKCS7填充并验证Padding",
    "完整性验证": "加密后必须使用HMAC验证完整性（Encrypt-then-MAC）",
    "使用AEAD": "优先使用AES-GCM等认证加密模式",
}
```

### 11.2 隐写术防御

```python
# 隐写检测与防御
stego_defense = {
    "LSB检测": "统计分析位平面分布，检测异常",
    "文件完整性": "校验文件哈希，检测修改",
    "隐写分析工具": "使用StegDetect、zsteg等工具检测",
    "图片水印": "添加数字水印追踪来源",
    "格式校验": "严格校验文件格式，拒绝修改过的文件",
}
```

---

## 十二、学习总结

### 12.1 Crypto方向学习路线

```
密码学学习路线:
1. 理解对称/非对称加密原理
2. 掌握古典密码（凯撒、维吉尼亚、栅栏等）
3. 深入学习RSA原理和攻击
4. 学习AES各模式及攻击
5. 掌握哈希算法及长度扩展攻击
6. 学习椭圆曲线密码
7. 了解格密码和后量子密码
```

### 12.2 Misc方向学习路线

```
Misc学习路线:
1. 掌握各种编码解码（Base、URL、Morse等）
2. 学习隐写术（图片、音频、文档）
3. 熟练使用Wireshark进行流量分析
4. 学习取证技术（磁盘、内存、日志）
5. 了解硬件安全和侧信道分析
6. 培养综合分析能力和直觉
```

### 12.3 常用工具速查

```
Crypto工具:
├── SageMath (数学计算)
├── PyCryptodome (Python密码学库)
├── RsaCtfTool (RSA自动攻击)
├── HashPumpy (哈希长度扩展)
├── yafu (大数分解)
└── hashcat (哈希破解)

Misc工具:
├── CyberChef (编码解码)
├── StegSolve (图片隐写)
├── zsteg (PNG/BMP隐写)
├── Wireshark (流量分析)
├── Audacity (音频分析)
├── Volatility (内存取证)
├── foremost (文件恢复)
├── binwalk (固件分析)
└── 010 Editor (十六进制编辑)
```

---

> **安全提示**：密码学和隐写技术仅用于CTF竞赛和安全研究。破解他人系统的加密数据属于违法行为。请始终在授权环境中学习，遵守相关法律法规。
