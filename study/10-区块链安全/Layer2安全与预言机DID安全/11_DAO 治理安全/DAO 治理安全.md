# DAO 治理安全

### 11.1 治理攻击概述

```
DAO 治理攻击类型：

1. 投票权垄断 (Vote Monopolization)
   ├── 攻击者大量购入治理代币
   ├── 获得超过 50% 投票权
   └── 通过恶意提案

2. 委托投票攻击 (Delegation Attack)
   ├── 攻击者收集大量委托投票权
   ├── 利用未参与投票用户的委托
   └── 在关键提案中控制多数

3. 闪电贷治理攻击 (Flash Loan Governance)
   ├── 闪电贷借入大量治理代币
   ├── 利用借入的代币投票
   ├── 在同一区块执行提案并归还
   └── 无需任何本金

4. 女巫攻击 (Sybil Attack)
   ├── 创建大量地址
   ├── 如果投票权重 = 地址数（一人一票）
   └── 虚假控制多数

5. 时间窗口攻击 (Time Window Attack)
   ├── 利用治理参数的延迟期
   ├── 在关键时间窗口执行组合操作
   └── 利用提案执行与市场反应的时间差
```

### 11.2 闪电贷治理攻击

```
闪电贷治理攻击流程：

区块 N:
  1. 从 Aave 闪电贷借入 10,000 ETH
  2. 用 10,000 ETH 购买 1,000,000 治理代币 GOV
  3. 用 1,000,000 GOV 对恶意提案投票（提案要求: 500,000 票通过）
  4. 提案通过
  5. 提案执行：将协议金库中的 5,000 ETH 转给攻击者
  6. 卖出 1,000,000 GOV 换回 10,000 ETH
  7. 归还闪电贷 10,000 ETH + 手续费
  8. 净获利: 5,000 ETH - 闪电贷手续费

关键条件:
  - 治理代币在 DEX 上有充足流动性（可大额买卖）
  - 提案投票和执行在同一区块（或同一交易）
  - 无投票锁定期（买入即可投票）
  - 无提案延迟执行期
```

### 11.3 防护方案

```solidity
// 安全的 DAO 治理合约
contract SafeDAOGovernance {
    IGovToken public immutable govToken;
    
    // 防护措施 1: 投票锁定期（Vote Lockup）
    uint256 public constant VOTE_LOCKUP_PERIOD = 3 days;
    // 代币必须在投票前锁定 3 天才能投票
    
    // 防护措施 2: 提案延迟执行（Timelock）
    uint256 public constant EXECUTION_DELAY = 2 days;
    // 提案通过后 2 天才能执行
    
    // 防护措施 3: 投票快照（Snapshot）
    // 投票权基于提案创建时的快照，而非投票时
    
    struct Proposal {
        uint256 id;
        address proposer;
        bytes   callData;        // 执行的调用数据
        uint256 snapshotBlock;   // 快照区块
        uint256 voteStart;      // 投票开始时间
        uint256 voteEnd;        // 投票结束时间
        uint256 executionTime;  // 可执行时间
        bool    executed;
        uint256 forVotes;
        uint256 againstVotes;
    }
    
    // 投票权快照：基于历史余额
    function getPriorVotes(address account, uint256 blockNumber) 
        public view returns (uint256) 
    {
        return govToken.getPriorVotes(account, blockNumber);
    }
    
    // 创建提案
    function propose(bytes calldata callData) external returns (uint256) {
        // 防护 4: 提案门槛
        require(
            getPriorVotes(msg.sender, block.number - 1) >= PROPOSAL_THRESHOLD,
            "Below proposal threshold"
        );
        
        uint256 proposalId = nextProposalId++;
        proposals[proposalId] = Proposal({
            id: proposalId,
            proposer: msg.sender,
            callData: callData,
            snapshotBlock: block.number,
            voteStart: block.timestamp + 1 days,     // 1天后开始投票
            voteEnd: block.timestamp + 1 days + 3 days, // 投票期3天
            executionTime: block.timestamp + 1 days + 3 days + EXECUTION_DELAY,
            executed: false,
            forVotes: 0,
            againstVotes: 0
        });
        
        return proposalId;
    }
    
    // 投票（基于快照余额）
    function castVote(uint256 proposalId, bool support) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp >= p.voteStart, "Voting not started");
        require(block.timestamp < p.voteEnd, "Voting ended");
        
        // 防护 5: 基于快照的投票权（闪电贷买入的代币在快照后无效）
        uint256 votes = getPriorVotes(msg.sender, p.snapshotBlock);
        require(votes > 0, "No voting power");
        
        if (support) {
            p.forVotes += votes;
        } else {
            p.againstVotes += votes;
        }
    }
    
    // 执行提案（有延迟）
    function executeProposal(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        require(!p.executed, "Already executed");
        require(block.timestamp >= p.executionTime, "Execution delay not met");
        require(p.forVotes > p.againstVotes, "Proposal rejected");
        require(p.forVotes >= QUORUM, "Quorum not met");
        
        p.executed = true;
        // 执行提案
        (bool success,) = address(this).call(p.callData);
        require(success, "Execution failed");
    }
}
```

---

---

