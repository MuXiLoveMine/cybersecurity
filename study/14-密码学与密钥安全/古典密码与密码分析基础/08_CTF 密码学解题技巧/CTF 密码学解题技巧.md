# CTF 密码学解题技巧

### 8.1 常见 CTF 密码学题型

```
CTF Crypto 题型分类
├── 编码题
│   ├── Base系列（Base16/32/64/85/91）
│   ├── 多重编码嵌套
│   └── 自定义编码
├── 古典密码
│   ├── 凯撒/仿射/维吉尼亚
│   ├── 栅栏/列置换
│   ├── 培根密码/猪圈密码
│   └── 键盘密码
├── 对称密码
│   ├── AES/DES 弱配置
│   ├── ECB模式弱点
│   └──padding oracle攻击
├── 非对称密码
│   ├── RSA（小指数/共模/Wiener）
│   ├── ECC（弱曲线）
│   └── DH（弱素数）
├── 哈希
│   ├── MD5碰撞
│   ├── 长度扩展攻击
│   └── 彩虹表
├── 前沿方向
│   ├── 格密码（LLL/CVP）
│   ├── 同态加密
│   └── 零知识证明
└── 逆向+密码
    ├── 自定义算法逆向
    └── 白盒密码
```

### 8.2 解题工具与脚本库

**常用工具：**

| 工具 | 用途 | 语言 |
|------|------|------|
| SageMath | 数论计算、格约简、椭圆曲线 | Python |
| PyCryptodome | Python 加密库 | Python |
| RsaCtfTool | RSA 攻击工具集 | Python |
| CyberChef | 编码/解码瑞士军刀 | Web |
| hashcat | 哈希爆破 | C |
| yafu | 大整数分解 | C |
| RSAtool | RSA 参数计算 | Python |

**SageMath 常用功能：**

```python
# SageMath 代码示例

# 1. RSA 小明文攻击
from sage.all import *

n = 0x...  # 模数
e = 3      # 小公钥指数
c = 0x...  # 密文

# 如果明文很小，c = m^3，直接开立方根
m = Integer(c).nth_root(e)  # 直接开方
print(bytes.fromhex(hex(int(m))[2:]))

# 2. Wiener 攻击（e 很大，d 很小）
from Crypto.Util.number import long_to_bytes
# continued_fraction 展开 e/n
cf = continued_fraction(e/n)
convergents = cf.convergents()
for k, d in convergents:
    if k == 0:
        continue
    phi = (e * d - 1) / k
    if phi.is_integer():
        m = power_mod(c, int(d), n)
        print(long_to_bytes(int(m)))
        break

# 3. 共模攻击（相同 n，不同 e）
from math import gcd
n = ...
e1, c1 = ..., ...
e2, c2 = ..., ...
g = gcd(e1, e2)
if g == 1:
    # 使用扩展欧几里得
    _, s, t = xgcd(e1, e2)
    m = (power_mod(c1, s, n) * power_mod(c2, t, n)) % n
    print(long_to_bytes(int(m)))
```

**Python 常用 CTF 脚本片段：**

```python
# Base 编码识别与解码
import base64

def try_all_bases(data):
    """尝试多种 Base 解码"""
    results = {}
    try:
        results['base64'] = base64.b64decode(data)
    except: pass
    try:
        results['base32'] = base64.b32decode(data)
    except: pass
    try:
        results['base16'] = base64.b16decode(data)
    except: pass
    return results

# RSA 常见漏洞检测
def check_rsa_vulnerability(n, e, c):
    """检测 RSA 常见漏洞"""
    # 检查小公钥指数
    if e == 3:
        return "可能存在小明文攻击，尝试开立方根"
    # 检查大公钥指数（可能 d 很小）
    if e > n // 2:
        return "可能存在 Wiener 攻击，尝试连分数展开"
    # 检查 n 是否为素数
    from sympy import isprime
    if isprime(n):
        return "n 是素数，可以直接计算 phi(n) = n-1"
    # 检查 n 是否可分解
    from sympy import factorint
    try:
        factors = factorint(n, limit=10**6)
        if factors:
            return f"n 可分解: {factors}"
    except: pass
    return "未检测到明显漏洞"

# 维吉尼亚自动破解
def auto_break_vigenere(ciphertext):
    """自动破解维吉尼亚密码"""
    # 1. Kasiski + IC 确定密钥长度
    # 2. 分组频率分析
    # 3. 组合得到密钥并解密
    key_length = find_key_length_vigenere(ciphertext)
    # ...（使用前面定义的函数）
    pass
```

### 8.3 实战案例

**案例1：RSA 小明文攻击**

```python
# 题目给出 n, e=3, c，但明文很小
# c = m^3 mod n，如果 m^3 < n，则 c = m^3（无取模）
# 直接对 c 开立方根即可

from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes

n = 0x00b2a...  # 很大的 n
e = 3
c = 0x3a...     # 相对较小的密文

# 方法1：直接开立方根
m, is_exact = iroot(c, 3)
if is_exact:
    flag = long_to_bytes(int(m))
    print(f"Flag: {flag}")

# 方法2：如果 m^3 略大于 n，尝试 m^3 = c + k*n
for k in range(1000):
    m, is_exact = iroot(c + k * n, 3)
    if is_exact:
        flag = long_to_bytes(int(m))
        print(f"Flag: {flag}")
        break
```

**案例2：AES ECB 模式弱点**

```python
# ECB 模式：相同明文块产生相同密文块
# 可以通过分析重复密文块推断明文结构

from Crypto.Cipher import AES

def ecb_oracle(plaintext, secret_key, prefix=b''):
    """模拟加密 Oracle"""
    cipher = AES.new(secret_key, AES.MODE_ECB)
    full_input = prefix + plaintext
    # PKCS7 填充
    pad_len = 16 - (len(full_input) % 16)
    full_input += bytes([pad_len]) * pad_len
    return cipher.encrypt(full_input)

# 字节逐个恢复明文
def ecb_attack(oracle, block_size=16):
    """ECB 字节恢复攻击"""
    recovered = b''
    for i in range(block_size):
        # 构造输入使未知字节恰好对齐块边界
        padding = b'A' * (block_size - 1 - i)
        # 获取目标密文块
        target = oracle(padding)[:block_size]
        # 枚举最后一个字节
        for b in range(256):
            test_input = padding + recovered + bytes([b])
            test_output = oracle(test_input)[:block_size]
            if test_output == target:
                recovered += bytes([b])
                break
    return recovered
```

**案例3：哈希长度扩展攻击**

```python
# 利用 Merkle-Damgard 结构的弱点
# 已知 hash(secret || message)，可以计算 hash(secret || message || padding || extension)

import struct
from Crypto.Hash import MD5

def md5_length_extension():
    """MD5 长度扩展攻击演示"""
    # 已知：secret = "secret", message = "data"
    # 目标：计算 hash(secret || "data" || padding || "admin=1")

    original_hash = "5f4dcc3b5aa765d61d8327deb882cf99"  # md5("secret"+"data")

    # 重构 MD5 内部状态
    # 将原始哈希作为初始状态，继续从指定长度追加数据
    # 需要手动实现 MD5 状态注入

    # 工具：hashpumpy 或 HashExtender
    # import hashpumpy
    # new_hash, new_msg = hashpumpy.hashpump(original_hash, "data", "admin=1", len("secret"))
    # print(f"新哈希: {new_hash}")
    # print(f"新消息: {new_msg}")
    pass
```

### 8.4 CTF 密码学解题方法论

```
解题流程：
1. 识别编码/密码类型
   ├── 观察密文格式（十六进制？Base64？ASCII？）
   ├── 寻找题目提示（算法名称、年代、人物）
   └── 分析密文特征（长度、字符集、模式）

2. 分析漏洞点
   ├── 参数是否异常（e=3? n 太小? IV 固定?）
   ├── 模式是否安全（ECB? CBC with predictable IV?）
   └── 是否有额外信息（已知明文？Oracle？）

3. 查找利用方法
   ├── 查阅论文和 Writeup
   ├── 使用现成工具（RsaCtfTool, SageMath）
   └── 编写 exploit 脚本

4. 验证与调整
   ├── 检查输出是否为可读文本
   ├── 尝试不同编码解码
   └── 检查是否有多层加密
```

**学习资源推荐：**

| 资源 | 说明 |
|------|------|
| CryptoHack | 交互式密码学 CTF 训练平台 |
| Cryptopals | 经典密码学挑战集 |
| pwntools | CTF 通用工具库 |
| SageMath | 数论与代数计算利器 |
| 《Applied Cryptanalysis》 | 密码分析教材 |

---

---

