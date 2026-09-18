# Optimistic Rollup 安全

### 2.1 乐观执行模型

Optimistic Rollup 的核心理念是"乐观假设"：默认所有提交的状态转换都是正确的，只有在挑战期内被证明欺诈时才回滚。

```
Optimistic Rollup 运行流程：

L1 (以太坊主网)                        L2 (Rollup 链)
    │                                      │
    │  1. 用户在 L2 上交易                    │
    │◄─────────────────────────────────────│  交易在 L2 执行
    │                                      │
    │  2. 排序者(Sequencer)打包批次          │
    │◄────────── 批次提交 ──────────────────│  提交交易批次+状态根
    │                                      │
    │  3. 挑战期开始 (7天)                    │
    │     ┌──────────────────────┐          │
    │     │   挑战窗口 (7天)      │          │
    │     │   任何人可提交欺诈证明  │          │
    │     └──────────────────────┘          │
    │                                      │
    │  4a. 无挑战 → 批次最终确认              │
    │      状态根被最终确认                   │
    │                                      │
    │  4b. 有挑战 → 验证欺诈证明              │
    │      证明有效 → 回滚状态根,惩罚排序者     │
    │      证明无效 → 挑战者被罚没             │
    │                                      │
    │  5. 提款流程                            │
    │     L2 → L1 资产退出 (需等待挑战期)     │
    │◄─────────────────────────────────────│
```

### 2.2 挑战期与欺诈证明

**挑战期（Challenge Period）**是 Optimistic Rollup 安全的基石。在挑战期内，任何观察者都可以对提交的状态根提出异议，通过欺诈证明（Fraud Proof）证明某个状态转换无效。

```solidity
// 简化的欺诈证明验证合约
contract FraudProofVerifier {
    uint256 public constant CHALLENGE_PERIOD = 7 days;
    
    struct Batch {
        bytes32 stateRoot;       // 提交的状态根
        uint256 submitTime;       // 提交时间
        bool    finalized;        // 是否已最终确认
        address submitter;        // 提交者
        uint256 collateral;       // 质押保证金
    }
    
    mapping(uint256 => Batch) public batches;
    
    // 排序者提交新批次
    function submitBatch(uint256 batchId, bytes32 stateRoot) external payable {
        require(msg.value >= MIN_COLLATERAL, "Insufficient collateral");
        batches[batchId] = Batch({
            stateRoot: stateRoot,
            submitTime: block.timestamp,
            finalized: false,
            submitter: msg.sender,
            collateral: msg.value
        });
        emit BatchSubmitted(batchId, stateRoot, msg.sender);
    }
    
    // 挑战者提交欺诈证明
    function challengeBatch(
        uint256 batchId,
        bytes memory proofData,       // 欺诈证明数据
        bytes memory executionTrace   // 执行轨迹（用于 L1 重新执行验证）
    ) external {
        Batch storage batch = batches[batchId];
        require(!batch.finalized, "Batch already finalized");
        require(
            block.timestamp <= batch.submitTime + CHALLENGE_PERIOD,
            "Challenge period expired"
        );
        
        // L1 上重新执行被质疑的交易
        bytes32 computedRoot = verifyExecution(proofData, executionTrace);
        
        if (computedRoot != batch.stateRoot) {
            // 欺诈证明有效：状态根不匹配
            batch.finalized = true;
            // 罚没提交者的保证金
            payable(msg.sender).transfer(batch.collateral);
            emit FraudProven(batchId, batch.submitter, msg.sender);
            
            // 回滚到上一个有效状态根
            rollbackState(batchId);
        } else {
            // 欺诈证明无效：挑战者被罚没
            revert("Invalid fraud proof");
        }
    }
    
    // 挑战期结束后最终确认
    function finalizeBatch(uint256 batchId) external {
        Batch storage batch = batches[batchId];
        require(!batch.finalized, "Already finalized");
        require(
            block.timestamp > batch.submitTime + CHALLENGE_PERIOD,
            "Challenge period not over"
        );
        batch.finalized = true;
        // 退还提交者的保证金
        payable(batch.submitter).transfer(batch.collateral);
        emit BatchFinalized(batchId, batch.stateRoot);
    }
}
```

### 2.3 欺诈证明的类型

```
欺诈证明类型：

1. 执行欺诈 (Execution Fraud)
   ├── 交易执行结果错误（如余额计算错误）
   ├── 证明方法：在 L1 上重新执行该交易
   └── 验证：计算的状态根 ≠ 提交的状态根

2. 数据可用性欺诈 (Data Availability Fraud)
   ├── 排序者提交了状态根但未公开交易数据
   ├── 证明方法：提交数据不可用证明
   └── 验证：无法获取交易数据 → 批次无效

3. 排序欺诈 (Sequencing Fraud)
   ├── 排序者重新排序交易（如插入自己的 MEV 交易）
   ├── 证明方法：展示交易时间戳与排序不一致
   └── 验证：违反 FIFO 或预确认规则

4. 无效退出欺诈 (Invalid Exit Fraud)
   ├── 恶意用户提交超出余额的退出请求
   ├── 证明方法：展示该用户在 L2 的实际余额
   └── 验证：退出金额 > 实际余额
```

---

---

## 📋 内容审核与补充建议

> 针对「Optimistic Rollup 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
