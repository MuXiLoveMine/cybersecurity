# 多方安全计算（MPC）

### 3.1 MPC 概念与安全模型

**多方安全计算（Secure Multi-Party Computation, MPC）** 允许多方在不泄露各自输入的情况下共同计算一个函数。

```
场景：百万富翁问题（姚期智，1982）

Alice 财产 A，Bob 财产 B
目标：比较 A 和 B 谁更大
约束：不泄露 A 和 B 的具体值

MPC 解决方案：
f(A, B) = (A > B) ? "Alice 更富" : "Bob 更富"
→ 双方输入各自财产值，得到比较结果
→ 双方都不知道对方的具体财产
```

**安全模型：**

```
┌──────────────────────────────────────────────────────┐
│  半诚实模型（Semi-Honest / Honest-but-Curious）       │
│  参与方遵守协议，但记录所有中间信息试图推断他人输入   │
│                                                      │
│  恶意模型（Malicious）                                │
│  参与方可能偏离协议，发送错误数据，主动作弊           │
└──────────────────────────────────────────────────────┘

恶意模型需要更强的保护：
- 零知识证明（证明输入格式正确）
- 消息认证码（MAC，防止篡改）
- 承诺方案（防止反悔）
- 秘密共享验证（VSS）
```

### 3.2 秘密共享

**Shamir 秘密共享（t-out-of-n 门限）**

```
原理：利用多项式插值
- 将秘密 S 分配给 n 个参与方
- 任意 t 个可以重构秘密
- 少于 t 个无法获取任何信息

构造：
1. 选随机多项式 f(x) = S + a₁x + a₂x² + ... + a_{t-1}x^{t-1} mod p
2. 第 i 方获得份额 sᵢ = f(i)
3. 重构：利用 t 个份额的拉格朗日插值恢复 f(0) = S
```

```python
import random
from functools import reduce

def shamir_share(secret, t, n, prime=2**521 - 1):
    """Shamir (t, n) 秘密共享"""
    # 生成随机多项式
    coeffs = [secret] + [random.randrange(1, prime) for _ in range(t - 1)]
    # 计算各份额
    shares = []
    for i in range(1, n + 1):
        share = sum(c * pow(i, j, prime) for j, c in enumerate(coeffs)) % prime
        shares.append((i, share))
    return shares

def shamir_reconstruct(shares, prime=2**521 - 1):
    """利用拉格朗日插值重构秘密"""
    secret = 0
    for i, (xi, yi) in enumerate(shares):
        # 拉格朗日基函数 L_i(0)
        num = 1
        den = 1
        for j, (xj, _) in enumerate(shares):
            if i == j:
                continue
            num = (num * (-xj)) % prime
            den = (den * (xi - xj)) % prime
        # 模逆元
        den_inv = mod_inverse(den % prime, prime)
        lagrange = (num * den_inv) % prime
        secret = (secret + yi * lagrange) % prime
    return secret

# 示例：3-out-of-5 秘密共享
secret = 12345
shares = shamir_share(secret, t=3, n=5)
print(f"原始秘密: {secret}")

# 用任意 3 个份额重构
reconstructed = shamir_reconstruct(shares[:3])
print(f"重构秘密: {reconstructed}")
assert secret == reconstructed
```

**加法秘密共享**

```python
def additive_share(secret, n, field_size=2**64):
    """加法秘密共享"""
    shares = [random.randrange(field_size) for _ in range(n - 1)]
    shares.append((secret - sum(shares)) % field_size)
    return shares

# 加法秘密共享支持加法同态
# s1 + s2 = (a1+b1, a2+b2, ..., an+bn) → 重构 = secret1 + secret2
```

### 3.3 混淆电路（Garbled Circuit）

Yao 提出的混淆电路是两方安全计算的经典协议。

```
混淆电路流程（以 2 方为例）：
┌──────────────────────────────────────────────┐
│ 1. Alice 生成混淆电路                        │
│    - 对每个逻辑门的真值表进行加密/打乱       │
│    - 每个_wire_用两个随机标签表示 0 和 1     │
│                                              │
│ 2. Alice 发送混淆电路 + 自己输入的标签       │
│                                              │
│ 3. Bob 通过不经意传输获取自己输入的标签       │
│    (Alice 不知道 Bob 选了哪个标签)            │
│                                              │
│ 4. Bob 评估电路，得到加密输出                 │
│                                              │
│ 5. Alice 和 Bob 共同解读输出                 │
└──────────────────────────────────────────────┘
```

**一个 AND 门的混淆示例：**

```
AND 门真值表：           混淆后：
a  b  | out              Enc(K_a0, K_b0, K_out0)
0  0  | 0                Enc(K_a0, K_b1, K_out0)
0  1  | 0                Enc(K_a1, K_b0, K_out0)
1  0  | 0                Enc(K_a1, K_b1, K_out1)
1  1  | 1
                        随机打乱顺序

K_a0, K_a1: 输入a的0/1标签
K_b0, K_b1: 输入b的0/1标签
K_out0, K_out1: 输出的0/1标签

评估者有 K_a1 和 K_b0
→ 尝试解密每行，只有对应行能成功解密
→ 得到 K_out0（对应输出 0）
```

### 3.4 不经意传输（Oblivious Transfer, OT）

**不经意传输** 是 MPC 的核心组件，允许接收方从发送方的多个消息中选择一个，且发送方不知道选了哪个，接收方只能获得所选消息。

```
1-out-of-2 OT：
Alice 有 (m₀, m₁)
Bob 选择 b ∈ {0, 1}

结果：
- Bob 得到 m_b
- Bob 不知道 m_{1-b}
- Alice 不知道 b
```

```python
# 基于 RSA 的 1-out-of-2 OT 简化实现
from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes

def ot_alice(m0, m1, rsa_key):
    """Alice 端"""
    e, n, d = rsa_key.e, rsa_key.n, rsa_key.d
    # 生成两个随机数
    x0 = secrets.randbelow(n)
    x1 = secrets.randbelow(n)
    # 发送 x0, x1 给 Bob
    # 接收来自 Bob 的 v
    # ...
    # 用 d 处理
    k0 = (v - x0) ** d % n  # 如果 Bob 选了 0
    k1 = (v - x1) ** d % n  # 如果 Bob 选了 1
    # 加密消息发送
    c0 = m0 ^ sha256(k0)  # 简化
    c1 = m1 ^ sha256(k1)
    return c0, c1

# 实际工程中通常使用 OT 扩展（OT Extension）提高效率
# 基础 OT 数百次，扩展出百万次 OT
```

### 3.5 MPC 协议

| 协议 | 参与方 | 模型 | 特点 |
|------|--------|------|------|
| Yao（GC） | 2 方 | 半诚实 | 混淆电路 |
| GMW | 多方 | 半诚实 | 秘密共享 + 电路 |
| BGW | 多方 | 半诚实 | Shamir 共享 + 电路 |
| SPDZ | 多方 | 恶意 | MAC 认证 + 预处理 |

**SPDZ 协议** 是目前最实用的恶意安全 MPC 协议：

```
SPDZ 核心思路：
1. 预处理阶段（离线）
   - 生成乘法三元组（a, b, c），满足 a*b = c
   - 使用不经意传输或同态加密生成
   
2. 在线阶段
   - 输入用加法秘密共享
   - 乘法利用三元组实现
   - 每个 MAC 认证份额防止篡改
   
3. 正确性验证
   - 计算完成后验证所有 MAC
   - 检测恶意行为
```

### 3.6 MPC 应用场景

```
┌──────────────────┬──────────────────────────────────────┐
│ 场景              │ 说明                                 │
├──────────────────┼──────────────────────────────────────┤
│ 隐私集合求交(PSI) │ 多方求交集不泄露非交集元素             │
│ 联邦学习          │ 加密聚合梯度，保护训练数据           │
│ 密钥生成          │ 多方协作生成密钥，无单点信任         │
│ 安全拍卖          │ 计算最高出价不泄露其他出价           │
│ 暗标竞标          │ 比较加密报价确定中标者               │
└──────────────────┴──────────────────────────────────────┘
```

---

---

## 📋 内容审核与补充建议

> 针对「多方安全计算（MPC）」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
