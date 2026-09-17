# 前置交易（Front-running）

### 6.1 漏洞原理

前置交易（又称抢跑交易）是指攻击者观察到交易池（mempool）中的有利可图的交易后，以更高的 Gas 价格发送一笔类似的交易，使其被优先打包，从而抢占利益。

**攻击图示：**

```
交易池（Mempool）中的交易：
  1. 用户 A：以 100 USDC 购买 1 ETH（Gas Price: 1 gwei）← 攻击者观察到
  2. 攻击者：以 100 USDC 购买 1 ETH（Gas Price: 100 gwei）← 抢先提交

矿工按 Gas Price 排序打包：
  区块中：[攻击者的交易] → [用户 A 的交易]
  
结果：攻击者先买到了 ETH，价格被推高，用户 A 买到更贵的 ETH
```

### 6.2 常见攻击场景

#### 6.2.1 DEX 抢跑

攻击者在 Uniswap 等 DEX 上观察到大额交易，抢先买入推高价格，再卖给后来的交易者。

```
1. 攻击者监控 mempool，发现大额买单
2. 攻击者用更高 gas 抢先买入
3. 大额买单成交，价格上涨
4. 攻击者卖出获利
```

#### 6.2.2 三明治攻击（Sandwich Attack）

```
攻击前价格：1 ETH = 1000 USDC

1. 攻击者观察到大额买单（100 ETH）
2. 攻击者先买入 10 ETH → 价格涨到 1 ETH = 1050 USDC
3. 受害者买单成交 → 价格涨到 1 ETH = 1100 USDC
4. 攻击者卖出 10 ETH → 获利约 50 USDC
```

### 6.3 防御方法

#### 方法一：提交-揭示方案（Commit-Reveal）

```solidity
contract CommitReveal {
    mapping(address => bytes32) public commits;
    mapping(address => uint256) public revealedValues;

    // 阶段 1：提交哈希
    function commit(bytes32 _hash) public {
        commits[msg.sender] = _hash;
    }

    // 阶段 2：揭示原值
    function reveal(uint256 _value, string memory _salt) public {
        bytes32 hash = keccak256(abi.encodePacked(_value, _salt));
        require(hash == commits[msg.sender], "Invalid reveal");
        revealedValues[msg.sender] = _value;
    }
}
```

#### 方法二：私有交易池（Private Mempool）

- 使用 Flashbots 等私有交易池
- 交易不公开广播，直接发送给矿工

#### 方法三：限价与滑点保护

```solidity
// Uniswap V2 的滑点保护
function swap(uint256 amountOutMin) public {
    // 要求最少得到 amountOutMin 数量的代币
    // 如果价格滑点太大，交易失败
    uint256 amountOut = getAmountOut();
    require(amountOut >= amountOutMin, "Slippage too high");
}
```

#### 方法四：批量处理

使用 TWAP（时间加权平均价格）或批量结算，减少单笔交易对价格的影响。

---

---

## 📋 内容审核与补充建议

> 针对「前置交易（Front-running）」部分的内容审核结果：

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
