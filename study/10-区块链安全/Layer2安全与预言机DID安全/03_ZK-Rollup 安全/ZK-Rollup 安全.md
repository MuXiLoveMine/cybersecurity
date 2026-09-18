# ZK-Rollup 安全

### 3.1 零知识证明验证

ZK-Rollup 使用零知识证明（ZKP）来验证 L2 状态转换的正确性。与 Optimistic Rollup 不同，ZK-Rollup 不依赖挑战期，而是通过数学证明确保安全。

```
ZK-Rollup 运行流程：

L1 (以太坊主网)                         L2 (Rollup 链)
    │                                       │
    │   1. 用户在 L2 上交易                     │
    │◄──────────────────────────────────────│
    │                                       │
    │   2. 排序者打包交易为批次                 │
    │   计算新的状态根                          │
    │   生成零知识证明 (zk-SNARK/STARK)         │
    │◄── 批次 + 证明 + 状态根 ──────────────────│
    │                                       │
    │   3. L1 验证者合约验证证明                │
    │      ┌────────────────────┐             │
    │      │ Verify(proof, pub_inputs) │      │
    │      │ → True: 状态转换有效       │      │
    │      │ → False: 拒绝              │      │
    │      └────────────────────┘             │
    │                                       │
    │   4. 证明通过 → 状态根立即最终确认        │
    │      无需等待挑战期                       │
    │                                       │
    │   5. 即时提款（证明验证后即可提取）       │
    │◄──────────────────────────────────────│

核心优势：
  - 数学保证：不依赖任何诚实假设
  - 即时最终性：证明验证后即最终确认
  - 更快的提款：无需等待 7 天挑战期
```

### 3.2 数据可用性

ZK-Rollup 的数据可用性是安全的关键环节。即使有了零知识证明，用户仍需要访问交易数据以验证自己的资产：

```
数据可用性方案：

方案 1: On-chain Data Availability (DA)
  ├── 交易数据完整发布在 L1 的 calldata 或 blobs 中
  ├── 任何人可从 L1 获取完整数据
  ├── 安全性最高，但 Gas 成本较高
  └── 代表：zkSync Era, StarkNet (优先模式)

方案 2: Off-chain DA with DAC (Data Availability Committee)
  ├── 交易数据由委员会链下存储
  ├── 委员会签名证明数据可用
  ├── Gas 成本低，但引入信任假设
  └── 代表：Validium 模式 (如 Immutable X)

方案 3: Volition (混合模式)
  ├── 高价值交易使用链上 DA
  ├── 低价值交易使用链下 DA
  └── 用户可自行选择数据可用性级别

方案 4: Celestia / EigenDA 等专用 DA 层
  ├── 专用数据可用性层
  ├── 通过 DAS（数据可用性采样）保证可用性
  └── 解耦 DA 与共识
```

### 3.3 电路安全

ZK-Rollup 的安全性最终依赖于零知识证明电路的正确性。电路安全包括：

```
电路安全分析维度：

1. 电路正确性 (Circuit Correctness)
   ├── 电路逻辑是否正确实现了状态转换规则
   ├── 风险：电路 Bug 导致无效状态被证明为有效
   └── 防护：形式化验证、电路审计、测试向量

2. 可信设置 (Trusted Setup)
   ├── zk-SNARK 需可信设置（如 Groth16）
   ├── 风险：设置参数泄露可伪造证明
   └── 防护：多方参与仪式(MPC)、Powers of Tau

3. 证明系统安全 (Proof System Security)
   ├── 不同方案安全性不同：
   │   ├── Groth16: 需可信设置，证明小且快
   │   ├── PLONK: 通用可信设置，证明中等
   │   ├── STARK: 无需可信设置，证明大但后量子安全
   │   └── Halo2: 无需可信设置，递归证明
   └── 防护：选择经过充分审计的证明系统

4. 生成证明的计算安全
   ├── 证明生成可能在不可信环境中进行
   ├── 证明者可能尝试生成虚假证明
   └── 防护：证明系统本身的可靠性（计算可行性假设）
```

```solidity
// 简化的 ZK 验证器合约接口
contract ZKVerifier {
    // 验证 zk-SNARK 证明
    function verifyProof(
        uint[2] memory a,        // 证明 A (G1 点)
        uint[2][2] memory b,      // 证明 B (G2 点)
        uint[2] memory c,        // 证明 C (G1 点)
        uint[] memory input       // 公共输入（状态根等）
    ) public view returns (bool) {
        // 调用预编译合约进行配对检查
        // 验证 e(A, B) = e(alpha, beta) * e(C, gamma) * e(sum_input, delta)
        return pairingCheck(a, b, c, input);
    }
    
    // Rollup 提交函数
    function commitZKBatch(
        bytes32 oldStateRoot,
        bytes32 newStateRoot,
        uint256 batchId,
        uint[2] memory proofA,
        uint[2][2] memory proofB,
        uint[2] memory proofC
    ) external {
        require(batches[batchId].stateRoot == oldStateRoot, "Invalid old root");
        
        // 公共输入包含: 旧状态根 + 新状态根 + 批次ID
        uint[] memory publicInputs = new uint[](3);
        publicInputs[0] = uint(oldStateRoot);
        publicInputs[1] = uint(newStateRoot);
        publicInputs[2] = batchId;
        
        // 验证零知识证明
        require(
            verifyProof(proofA, proofB, proofC, publicInputs),
            "Invalid ZK proof"
        );
        
        // 证明通过，状态根立即更新（无需挑战期）
        batches[batchId].stateRoot = newStateRoot;
        batches[batchId].finalized = true;
        
        emit ZKBatchVerified(batchId, newStateRoot);
    }
}
```

---

---

## 📋 内容审核与补充建议

> 针对「ZK-Rollup 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
