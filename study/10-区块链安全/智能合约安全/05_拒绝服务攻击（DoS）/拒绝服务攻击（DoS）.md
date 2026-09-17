# 拒绝服务攻击（DoS）

### 5.1 漏洞原理

拒绝服务攻击是指攻击者通过某种方式使合约无法正常运行或无法被正常使用。

**常见类型：**
1. Gas 耗尽型 DoS
2. 意外回退型 DoS
3. 区块 Gas 限制型 DoS
4. 数组遍历型 DoS

### 5.2 Gas 耗尽型 DoS

**漏洞场景：** 合约在循环中调用外部合约，如果外部合约故意消耗所有 gas，会导致整个交易失败。

```solidity
// ⚠️ 漏洞：批量发奖，依赖外部调用
contract VulnerableAuction {
    address[] public winners;
    mapping(address => uint256) public rewards;

    // 给所有赢家发奖
    function distributeRewards() public {
        for (uint256 i = 0; i < winners.length; i++) {
            // 如果某个 winner 是合约，fallback 消耗所有 gas
            // 整个函数就会失败，其他人也拿不到奖励
            payable(winners[i]).transfer(rewards[winners[i]]);
        }
    }
}
```

**攻击：**
```solidity
contract MaliciousWinner {
    receive() external payable {
        // 消耗所有 gas，导致整个交易回滚
        while (true) {
            // 无限循环消耗 gas
        }
    }
}
```

**防御：Pull 模式**
```solidity
// 改为让用户主动领取
mapping(address => uint256) public pendingRewards;

function claimReward() public {
    uint256 reward = pendingRewards[msg.sender];
    pendingRewards[msg.sender] = 0;
    payable(msg.sender).transfer(reward);
}
```

### 5.3 数组遍历型 DoS

**漏洞场景：** 合约需要遍历一个不断增长的数组，当数组太大时，单次遍历超过区块 Gas Limit，导致永远无法执行完成。

```solidity
// ⚠️ 漏洞：遍历不断增长的数组
contract VulnerableRegistry {
    address[] public participants;

    function register() public {
        participants.push(msg.sender);
    }

    // 当 participants 很大时，这个函数会因为 gas 不足而永远失败
    function payAll(uint256 amount) public {
        for (uint256 i = 0; i < participants.length; i++) {
            payable(participants[i]).transfer(amount);
        }
    }
}
```

**防御：** 分批处理或使用 Pull 模式
```solidity
// 分批处理
function payBatch(uint256 start, uint256 end) public {
    require(end <= participants.length);
    for (uint256 i = start; i < end; i++) {
        // ...
    }
}
```

### 5.4 意外回退型 DoS

**漏洞场景：** 合约的关键功能依赖于向某个地址转账，如果该地址是合约且拒绝接收 ETH，关键功能会被阻塞。

```solidity
// ⚠️ 漏洞：竞拍依赖于退回押金
contract VulnerableAuction {
    address public highestBidder;
    uint256 public highestBid;

    function bid() public payable {
        require(msg.value > highestBid);

        // 退回上一个出价者的资金
        // 如果上一个出价者是恶意合约，revert 会导致没有人能超过他
        payable(highestBidder).transfer(highestBid);

        highestBidder = msg.sender;
        highestBid = msg.value;
    }
}
```

**攻击：**
```solidity
contract MaliciousBidder {
    function bid(address auction) external payable {
        VulnerableAuction(auction).bid{value: msg.value}();
    }

    // 拒绝接收 ETH，导致转账失败
    receive() external payable {
        revert("I don't accept ETH");
    }
}
```

**防御：Pull 模式**
```solidity
contract SafeAuction {
    address public highestBidder;
    uint256 public highestBid;
    mapping(address => uint256) public pendingReturns;

    function bid() public payable {
        require(msg.value > highestBid);

        // 记录退款，不立即转账
        pendingReturns[highestBidder] += highestBid;

        highestBidder = msg.sender;
        highestBid = msg.value;
    }

    // 用户自己提取
    function withdraw() public {
        uint256 amount = pendingReturns[msg.sender];
        pendingReturns[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
    }
}
```

---

---

## 📋 内容审核与补充建议

> 针对「拒绝服务攻击（DoS）」部分的内容审核结果：

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
