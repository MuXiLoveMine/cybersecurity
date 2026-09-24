# 零知识证明（ZKP）

### 2.1 ZKP 基本原理

**零知识证明（Zero-Knowledge Proof）** 是一种协议，证明者（Prover）可以向验证者（Verifier）证明自己知道某个秘密，但不泄露该秘密的任何信息。

**三个基本性质：**

```
┌────────────────────────────────────────────────────────┐
│  1. 完整性（Completeness）                              │
│     如果陈述为真且双方诚实执行，验证者必接受             │
│                                                        │
│  2. 可靠性（Soundness）                                │
│     如果陈述为假，任何作弊的证明者都无法使验证者接受     │
│                                                        │
│  3. 零知识性（Zero-Knowledge）                          │
│     验证者除了"陈述为真"之外，学不到任何信息            │
└────────────────────────────────────────────────────────┘
```

**经典类比：阿里巴巴洞穴**

```
        ┌─────────────────┐
        │    洞穴内部      │
        │                 │
   入口 │  A ──────────B  │
   ───→ │  │           │  │ ← 验证者在入口
        │  └──门（需要密码）┘ │
        └─────────────────┘

1. 证明者随机从 A 或 B 进入洞穴
2. 验证者在入口（看不到内部）
3. 验证者随机要求证明者从 A 或 B 出来
4. 如果证明者知道密码（开门），总能按要求出来
5. 如果不知道密码，每次有 50% 概率被识破
6. 重复 n 次，作弊概率 = (1/2)^n
```

### 2.2 经典 ZKP 协议

**Schnorr 协议（身份证明）**

证明者知道离散对数 x（满足 g^x = y），不泄露 x：

```
公共参数：循环群 G，生成元 g，阶 p
公钥：y = g^x mod p
私钥：x

协议三步：
1. 承诺（Commit）：证明者选随机数 r，发送 R = g^r mod p
2. 挑战（Challenge）：验证者发送随机挑战 c
3. 响应（Response）：证明者发送 s = r + c*x mod p

验证：g^s = g^(r+cx) = g^r * g^(cx) = R * y^c mod p
      检查 g^s ≡ R * y^c (mod p)
```

```python
import secrets

# Schnorr 协议演示
p = 2**521 - 1  # 大素数（Mersenne prime）
g = 2

# 密钥生成
x = secrets.randbelow(p)  # 私钥
y = pow(g, x, p)          # 公钥

# --- 协议交互 ---

# 1. 承诺
r = secrets.randbelow(p)
R = pow(g, r, p)

# 2. 挑战
c = secrets.randbelow(p)

# 3. 响应
s = (r + c * x) % p

# --- 验证 ---
left = pow(g, s, p)
right = (R * pow(y, c, p)) % p
assert left == right, "验证失败"
print("Schnorr 协议验证成功")
```

**Fiat-Shamir 变换（非交互式化）**

交互式协议需要多轮通信，Fiat-Shamir 变换将挑战替换为哈希值，实现非交互式：

```
交互式：                          非交互式（Fiat-Shamir）：
1. R = Commit(x, r)              1. R = Commit(x, r)
2. c ← 验证者随机选择             2. c = Hash(R || 公共参数)  ← 用哈希代替
3. s = Response(r, c, x)          3. s = Response(r, c, x)
                                  4. 发送 (R, s) 给验证者
```

### 2.3 zk-SNARKs

**zk-SNARK（Zero-Knowledge Succinct Non-interactive ARgument of Knowledge）** 是简洁的非交互式零知识证明。

```
zk-SNARK 特性：
┌────────────────┬────────────────────────────────────┐
│ Zero-Knowledge │ 不泄露证明内容                       │
│ Succinct       │ 证明极短，验证极快                   │
│ Non-interactive│ 无需多轮交互                        │
│ Argument       │ 计算可靠性（非信息论安全）           │
│ of Knowledge   │ 证明者必须真正知道见证               │
└────────────────┴────────────────────────────────────┘
```

**Groth16 方案**

```
构建流程：
1. 将待证明程序转换为算术电路
2. 电路 → R1CS（Rank-1 Constraint System）
3. R1CS → QAP（Quadratic Arithmetic Program）
4. QAP + 可信设置 → Groth16 证明

证明大小：约 200 字节（固定）
验证时间：约 10 毫秒
```

**PLONK 方案**

```
改进点：
- 通用可信设置（Universal Trusted Setup）
  └─ 只需一次设置，所有电路复用
- 证明大小：~500 字节
- 验证时间：~20 毫秒
- 支持查找门（Lookup Gates）
```

**zk-SNARK 工程实现（Circom + snarkjs）**

```javascript
// Circom 电路：证明知道 x 使得 x^2 + x = 42
pragma circom 2.0.0;

template QuadraticEquation() {
    signal input x;
    signal output out;

    // 约束：x * x + x === 42
    x * x + x === 42;
    out <== 1;
}

component main = QuadraticEquation();

// 编译与证明流程：
// circom circuit.circom --r1cs --wasm --sym
// snarkjs groth16 setup circuit.r1cs powersOfTau28_hez_final_14.ptau
// snarkjs groth16 prove circuit_0000.zkey witness.wtns proof.json public.json
// snarkjs groth16 verify verification_key.json public.json proof.json
```

### 2.4 zk-STARKs

**zk-STARK（Scalable Transparent ARgument of Knowledge）**

```
zk-STARK vs zk-SNARK：
┌──────────────┬───────────────┬───────────────┐
│ 特性          │ zk-SNARK      │ zk-STARK      │
├──────────────┼───────────────┼───────────────┤
│ 可信设置      │ 需要           │ 不需要         │
│ 后量子安全    │ 否             │ 是            │
│ 证明大小      │ ~200 字节      │ ~100 KB       │
│ 验证时间      │ 毫秒级         │ 毫秒级         │
│ 证明时间      │ 秒级           │ 秒级           │
│ 密码学假设    │ 椭圆曲线        │ 哈希函数        │
└──────────────┴───────────────┴───────────────┘
```

### 2.5 ZKP 在区块链中的应用

**Zcash（隐私币）**
- 使用 zk-SNARK 隐藏交易金额、发送方、接收方
- 证明交易有效但不暴露细节

```
Zcash 屏蔽交易证明：
"我知道一组旧Note的私钥，且这些Note的总金额 >= 新Note的总金额 + 交易费"
→ 用 zk-SNARK 证明上述陈述，不泄露具体金额
```

**zk-Rollup（以太坊扩容）**
- 将大量交易打包成一批
- 用 ZKP 证明批次处理的正确性
- 将证明提交到链上，大幅降低 Gas 费

```
zk-Rollup 流程：
1. 用户在 L2 提交交易
2. 排序器收集并打包交易
3. 执行交易，生成新状态
4. 用 zk-SNARK 生成正确性证明
5. 将证明 + 状态根提交到 L1
6. L1 验证证明（快速），确认最终状态
```

### 2.6 ZKP 开发工具

| 工具 | 语言 | 方案 | 适用场景 |
|------|------|------|----------|
| libsnark | C++ | Groth16 | 高性能证明 |
| Circom+snarkjs | JS | Groth16/PLONK | Web 应用 |
| Halo2 | Rust | PLONKish | 无可信设置 |
| StarkWare | | zk-STARK | 高吞吐扩容 |
| Noir | Rust | 抽象层 | 通用 ZKP DSL |
| ZoKrates | Solidity-like | 多种 | 以太坊智能合约 |

---

---

