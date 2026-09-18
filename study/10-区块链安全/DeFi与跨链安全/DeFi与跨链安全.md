# DeFi与跨链安全

> 本文档系统覆盖DeFi生态安全与跨链桥安全，包括智能合约漏洞深入分析（重入/闪电贷/MEV/治理攻击）、DeFi协议安全、跨链技术与桥安全、安全审计工具链、链上监控体系以及Python安全分析脚本示例。是区块链安全学习的核心进阶内容。

---

## 一、DeFi安全概述

### 1.1 DeFi生态与TVL

DeFi（Decentralized Finance，去中心化金融）是构建在区块链上的无需许可、非托管的金融协议生态。

**TVL（Total Value Locked，总锁仓量）变化趋势：**

```
DeFi TVL 发展历程（示意）

TVL(十亿USD)
  180 ┤                                                    ╭──●
  160 ┤                                                ╭───╯
  140 ┤                                           ╭────╯
  120 ┤                                      ╭────╯
  100 ┤                                 ╭────╯ Terra崩盘
   80 ┤                            ╭────╯   ↓
   60 ┤                       ╭────╯     FTX暴雷
   40 ┤                  ╭────╯        ↓
   20 ┤             ╭────╯
    0 ┤────────────╯──────────────────────────────────
      2020Q1    2021Q1    2022Q1    2023Q1    2024Q1  2025Q1

关键事件:
  2020 - DeFi Summer (Compound流动性挖矿引爆)
  2021 - TVL突破180B峰值
  2022 - Terra/FTC崩盘, DeFi信任危机
  2023-2025 - LST/LRT/RWA叙事推动复苏
```

**DeFi核心赛道：**

| 赛道 | 代表协议 | TVL占比 | 核心风险 |
|------|---------|---------|---------|
| DEX（去中心化交易所） | Uniswap, Curve | ~25% | 预言机操纵、滑点攻击 |
| 借贷 | Aave, Compound | ~30% | 清算攻击、坏账 |
| 稳定币 | DAI, USDC, LUSD | ~15% | 锚定脱钩、抵押率不足 |
| 流动性质押(LST) | Lido, Rocket Pool | ~20% | 罚没风险、 slashing |
| 跨链桥 | WBTC, stETH | ~10% | 桥被盗、签名中心化 |

### 1.2 DeFi vs TradFi安全差异

| 维度 | 传统金融(TradFi) | 去中心化金融(DeFi) |
|------|-----------------|-------------------|
| 代码地位 | 代码辅助人工决策 | **代码即法律**（Code is Law） |
| 不可变性 | 可热修复、回滚 | 合约部署后不可篡改（需代理模式） |
| 资金追回 | 可通过司法冻结追回 | 被盗资金几乎无法追回 |
| 审计方式 | 合规审计+内控 | 智能合约代码审计 |
| 攻击面 | 人工流程漏洞 | 代码漏洞+组合漏洞 |
| 攻击速度 | 小时~天级 | **秒级**（一笔交易即完成） |
| 匿名性 | 实名制KYC | 伪匿名地址 |
| 杠杆 | 受监管限制 | 闪电贷提供无抵押无上限杠杆 |
| 保险 | 存款保险制度 | 部分协议有保险基金，覆盖有限 |

### 1.3 DeFi攻击事件回顾

| 事件 | 时间 | 损失 | 根因 |
|------|------|------|------|
| **Ronin Bridge** | 2022.03 | $624M | 验证者私钥泄露（9/13节点被控制） |
| **Wormhole** | 2022.02 | $326M | 签名验证漏洞（伪造跨链消息） |
| **Nomad Bridge** | 2022.08 | $190M | 初始化漏洞（任意消息可通过验证） |
| **Beanstalk** | 2022.04 | $182M | 闪电贷治理攻击（借入资金投票通过恶意提案） |
| **Wormhole (V1)** | 2024.02 | - | Solana签名验证逻辑缺陷 |
| **Curve (Vyper)** | 2023.07 | $70M | Vyper编译器重入锁bug |
| **bZx** | 2020.02 | $954K | 闪电贷操纵预言机价格 |
| **Poly Network** | 2021.08 | $611M | 跨链合约函数权限缺陷（EthCrossChainManager） |
| **Ronin Bridge (2nd)** | 2024.08 | - | MEV机器人前置套利 |

---

## 二、智能合约安全漏洞深入

### 2.1 重入攻击（Reentrancy）

重入攻击是智能合约最经典的漏洞类型，攻击者利用外部调用在状态更新前重新进入合约。

#### 2.1.1 ERC-20重入

**漏洞合约（不安全）：**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract VulnerableVault {
    mapping(address => uint256) public balances;
    IERC20 public token;

    constructor(address _token) {
        token = IERC20(_token);
    }

    // ⚠️ 漏洞：先转账再更新余额
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // 1. 先执行外部调用（危险！）
        require(token.transfer(msg.sender, amount), "Transfer failed");

        // 2. 然后才更新状态（此时攻击者已重入）
        balances[msg.sender] -= amount;
    }

    function deposit(uint256 amount) external {
        require(token.transferFrom(msg.sender, address(this), amount));
        balances[msg.sender] += amount;
    }
}
```

**攻击合约：**

```solidity
contract ReentrancyAttacker {
    VulnerableVault public vault;
    IERC20 public token;

    constructor(address _vault, address _token) {
        vault = VulnerableVault(_vault);
        token = IERC20(_token);
    }

    function attack(uint256 amount) external {
        // 存入初始资金
        token.approve(address(vault), amount);
        vault.deposit(amount);

        // 触发提款 → 进入receive回调 → 再次提款
        vault.withdraw(amount);
    }

    // ERC20 transfer回调（某些代币实现会回调接收方）
    function tokensReceived(address, uint256 amount) external {
        if (token.balanceOf(address(vault)) >= amount) {
            // 重入！此时余额尚未扣减，可再次提款
            vault.withdraw(amount);
        }
    }
}
```

#### 2.1.2 ERC-721（NFT）重入

NFT重入通过`onERC721Received`回调实现，逻辑类似但利用场景不同。

**防御方案（Checks-Effects-Interactions模式）：**

```solidity
contract SafeVault {
    mapping(address => uint256) public balances;
    IERC20 public token;

    function withdraw(uint256 amount) external nonReentrant {
        // 1. Checks（检查）
        require(balances[msg.sender] >= amount, "Insufficient balance");

        // 2. Effects（更新状态）—— 先扣减余额
        balances[msg.sender] -= amount;

        // 3. Interactions（外部交互）—— 最后转账
        require(token.transfer(msg.sender, amount), "Transfer failed");
    }
}

// OpenZeppelin ReentrancyGuard
abstract contract ReentrancyGuard {
    uint256 private constant NOT_ENTERED = 1;
    uint256 private constant ENTERED = 2;
    uint256 private _status = NOT_ENTERED;

    modifier nonReentrant() {
        require(_status != ENTERED, "Reentrant call");
        _status = ENTERED;
        _;
        _status = NOT_ENTERED;
    }
}
```

### 2.2 整数溢出（SafeMath与Solidity 0.8+）

```solidity
// Solidity 0.7及以下 —— 整数溢出会静默回绕
pragma solidity ^0.7.0;
contract OldOverflow {
    function add(uint8 a, uint8 b) public pure returns (uint8) {
        return a + b; // 255 + 1 = 0 (回绕!)
    }
}

// 需要SafeMath库
library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        uint256 c = a + b;
        require(c >= a, "SafeMath: addition overflow");
        return c;
    }
    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction overflow");
        return a - b;
    }
}

// Solidity 0.8+ —— 默认溢出检查（revert）
pragma solidity ^0.8.0;
contract SafeContract {
    function add(uint8 a, uint8 b) public pure returns (uint8) {
        return a + b; // 255 + 1 直接revert，不会回绕
    }

    // 如需关闭检查以节省gas，使用unchecked
    function addUnchecked(uint256 a, uint8 b) public pure returns (uint8) {
        unchecked {
            return a + b; // 可能回绕，需自行确保安全
        }
    }
}
```

### 2.3 访问控制缺陷

```solidity
// ⚠️ 漏洞：缺少权限检查
contract VulnerableAccess {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // 任何人都能调用！
    function setOwner(address newOwner) external {
        owner = newOwner;
    }
}

// ✅ 修复：添加权限修饰符
contract SafeAccess {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    function setOwner(address newOwner) external onlyOwner {
        owner = newOwner;
    }
}
```

**常见访问控制问题：**
- 函数可见性错误（`public`应为`external`或`internal`）
- 初始化函数可被重复调用（`initialize()`无防重入）
- 角色检查使用`tx.origin`而非`msg.sender`
- 委托调用（`delegatecall`）导致上下文劫持

### 2.4 闪电贷攻击原理

**闪电贷（Flash Loan）** 是DeFi特有的无抵押借贷，借款和还款在同一笔交易内完成。如果未还款，整个交易回滚。

```
闪电贷攻击基本流程：

┌──────────────────────────────────────────────────┐
│ Step 1: 从Aave/dYdX借入大额资产（无抵押）        │
│ Step 2: 利用借入资金操纵预言机价格/流动性         │
│ Step 3: 在价格被操纵期间执行套利/清算/治理        │
│ Step 4: 归还闪电贷 + 手续费                      │
│ Step 5: 保留利润 → 攻击完成                      │
│                                                  │
│ 关键：所有操作在单个区块单笔交易内完成           │
│ 原子性：任一步骤失败则整个交易回滚               │
└──────────────────────────────────────────────────┘
```

#### 2.4.1 闪电贷经典案例（bZx/Beanstalk）

**bZx攻击（2020年2月）—— 预言机操纵鼻祖：**

```
攻击步骤：
  1. 从dYdX闪电贷借入10,000 ETH
  2. 在bZx上开5倍杠杆做多WBTC（用借来的ETH做抵押借WBTC）
  3. 向Uniswap WBTC/ETH池注入大量WBTC → 推高WBTC价格
  4. bZx预言机读取Uniswap价格 → WBTC被高估
  5. 以高估的WBTC抵押值偿还部分债务
  6. 还款dYdX闪电贷，净赚约3,500 ETH

根因：bZx使用Uniswap作为价格预言机（TWAP未启用）
```

**Beanstalk攻击（2022年4月）—— 闪电贷治理攻击：**

```
攻击步骤：
  1. 从Aave闪电贷借入大量稳定币
  2. 用借来的资产在Beanstalk协议中质押获取大量投票权
  3. 提交并投票通过恶意治理提案（提案将资金转入攻击者地址）
  4. 提案执行 → 资金被转出
  5. 归还闪电贷

损失：约$182M
根因：治理投票权无时间锁，闪电贷获取的临时投票权即可通过提案
```

#### 2.4.2 价格预言机操纵

```solidity
// ⚠️ 漏洞：直接从DEX获取即时价格
contract VulnerableOracle {
    IUniswapV3Pool public pool;

    function getPrice() external view returns (uint256) {
        // 即时spot price，可被闪电贷操纵
        (uint160 sqrtPriceX96, , , , , , ) = pool.slot0();
        return (uint256(sqrtPriceX96) * uint256(sqrtPriceX96) * 1e18) >> 192;
    }
}

// ✅ 安全：使用Chainlink去中心化预言机 + TWAP
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract SafeOracle {
    AggregatorV3Interface public priceFeed;
    IUniswapV3Pool public pool;

    function getSafePrice() external view returns (uint256) {
        // 1. Chainlink价格（去中心化聚合）
        (, int256 chainlinkPrice, , , ) = priceFeed.latestRoundData();
        require(chainlinkPrice > 0, "Invalid Chainlink price");

        // 2. Uniswap TWAP（时间加权平均价格）
        uint32[] memory secondsAgo = new uint32[](2);
        secondsAgo[0] = 1800; // 30分钟前
        secondsAgo[1] = 0;
        (int24[] memory tickCumulatives, ) = pool.observe(secondsAgo);
        int24 tick = int24((tickCumulatives[1] - tickCumulatives[0]) / 1800);

        // 3. 双源校验，价格偏差超阈值则revert
        uint256 twapPrice = TickMath.getSqrtRatioAtTick(tick);
        require(
            isClose(uint256(chainlinkPrice), twapPrice, 200), // 2%容差
            "Price deviation too high"
        );
        return uint256(chainlinkPrice);
    }
}
```

#### 2.4.3 闪电贷+套利+操纵组合

```
复杂组合攻击链：
  闪电贷 → 操纵价格 → 利用价格差异套利 → 触发清算获利 → 归还闪电贷

关键防御：
  - 使用去中心化预言机（Chainlink/Pyth/API3）
  - TWAP代替spot price
  - 多源预言机校验
  - 限制单笔交易的影响范围（时间锁、金额上限）
  - 监控大额闪电贷交易
```

### 2.5 MEV（最大可提取价值）

MEV是指验证者/矿工通过重新排序、插入或删除交易而可获取的额外价值。

#### 2.5.1 三明治攻击

```
三明治攻击（Sandwich Attack）：

用户提交大额DEX swap
       │
       ▼
  MEV机器人检测到该交易
       │
       ├──→ 前置交易(Front-run)：机器人在用户之前买入
       │    → 推高价格
       │
       ├──→ 用户交易执行：在推高后的价格买入
       │    → 用户承受更高滑点
       │
       └──→ 后置交易(Back-run)：机器人卖出
            → 赚取差价利润

用户损失 = 机器人利润 + 额外滑点
```

**防御：**
- 使用滑点保护（但过高滑点仍被利用）
- Flashbots Protect RPC：私有交易池，防止被前置
- MEV-Share/MEV-Blocker：用户可选择将MEV返还
- CowSwap批量拍卖模型：消除交易顺序依赖

#### 2.5.2 前置交易/后置交易

| 类型 | 原理 | 受害者 |
|------|------|--------|
| 前置交易（Front-running） | 看到待确认交易后抢先执行 | 原始交易发起者 |
| 后置交易（Back-running） | 在目标交易后立即执行套利 | 无直接受害者（套利） |
| 三明治攻击 | 前置+后置组合 | DEX大额交易者 |

#### 2.5.3 Flashbots

**Flashbots** 是以太坊上的MEV提取基础设施，旨在透明化MEV并减少其对普通用户的负面影响。

```
Flashbots架构：

  用户 → Flashbots Protect RPC → Flashbots私有交易池
                                    │
  搜索者(Searcher) → Flashbots Auction → 区块构建者(Builder)
                                    │
                    MEV-Boost中继 → 验证者(Validator)
                                    │
                              区块提议 → 上链

关键特性：
  - 私有交易池：交易在确认前对公开mempool不可见
  - 拍卖机制：搜索者通过priority fee竞标交易排序
  - MEV-Boost：PoS下的PBS（Proposer-Builder Separation）
  - 透明化：MEV提取可见可审计
```

### 2.6 治理攻击

```solidity
// ⚠️ 治理攻击示例：投票权无时间锁
contract VulnerableGovernance {
    IERC20 public governanceToken;
    mapping(uint256 => Proposal) public proposals;

    struct Proposal {
        address target;
        bytes data;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 deadline;
        bool executed;
    }

    // 漏洞：质押即可获得投票权，无锁定时间
    function vote(uint256 proposalId, bool support) external {
        uint256 votes = governanceToken.balanceOf(msg.sender);
        // 闪电贷借入token → 立即投票 → 归还
        if (support) {
            proposals[proposalId].forVotes += votes;
        }
    }

    function execute(uint256 proposalId) external {
        Proposal storage p = proposals[proposalId];
        require(!p.executed && block.timestamp > p.deadline);
        require(p.forVotes > p.againstVotes);
        p.executed = true;
        // 执行提案（可能转移资金）
        (bool ok,) = p.target.call(p.data);
        require(ok);
    }
}

// ✅ 防御：投票锁定 + 时间锁
contract SafeGovernance {
    // 投票权基于历史快照，而非当前余额
    // 锁定token必须超过某个时间才能投票
    // 提案执行有时间锁延迟（如48小时）
    // 大额提案需要多签/多阶段确认
}
```

### 2.7 闪电贷攻击防御

| 防御措施 | 原理 | 效果 |
|---------|------|------|
| 去中心化预言机 | 使用Chainlink而非DEX spot price | 防止价格操纵 |
| TWAP | 时间加权平均价格 | 短时操纵无效 |
| 多源校验 | 多预言机交叉验证 | 单点失效防护 |
| 治理时间锁 | 提案执行延迟 | 闪电贷无法即时通过提案 |
| 投票快照 | 基于历史余额投票 | 临时获取的代币无投票权 |
| 交易限额 | 单笔交易最大影响 | 限制操纵幅度 |
| 异常监控 | 链上实时监控 | 及时发现并暂停 |

---

## 三、DeFi协议安全

### 3.1 DEX安全（Uniswap/SushiSwap）

**Uniswap V3集中流动性风险：**

```
集中流动性（Concentrated Liquidity）风险：

  V2: 均匀分布(0~∞)  → 资金利用率低，但无无常损失风险低
  V3: 集中分布(a~b)  → 资金利用率高，但需主动管理

  风险：
  - LP需要频繁调整价格区间 → 管理成本高
  - 价格移出区间 → 流动性停止赚取手续费
  - 无常损失在集中流动性下被放大
  - JIT（Just-In-Time）流动性：套利者在大额swap前临时添加流动性
    获取大部分手续费，损害长期LP收益
```

**DEX核心安全点：**

| 风险点 | 说明 | 防御 |
|--------|------|------|
| 重入 | swap回调中重入 | Checks-Effects-Interactions + nonReentrant |
| 预言机操纵 | V3 slot0 spot price被操纵 | 使用TWAP oracle而非spot price |
| 权限管理 | owner可修改费率 | 时间锁+多签+治理投票 |
| 闪电贷套利 | 价格被短期操纵 | TWAP + 交易量异常监控 |
| 无常损失 | 非安全漏洞但影响LP收益 | 教育用户+对冲策略 |

### 3.2 借贷协议安全（Aave/Compound）

**借贷协议核心风险：**

```
借贷协议安全模型：

  存款人 → 存入资产 → 获得利息
                    ↓
  借款人 → 提供抵押 → 借入资产 → 支付利息

  核心安全参数：
  - 抵押率（Collateral Factor）: 借款/抵押比率上限
  - 清算阈值（Liquidation Threshold）: 触发清算的抵押率
  - 清算罚金（Liquidation Penalty）: 清算人获得的折扣
  - 健康因子（Health Factor）: (>1安全, <1可被清算)

  攻击场景：
  1. 操纵抵押品价格 → 借出超额贷款 → 坏账
  2. 清算攻击 → 操纵价格触发清算 → 获取清算折扣
  3. 利率操纵 → 短时间操纵利用率 → 影响利率模型
```

**Aave安全机制：**
- Chainlink预言机 + 多源校验
- 安全模块（Safety Module）：代币质押做保险池
- 冻结功能：紧急情况下冻结特定资产市场
- 渐进式上线：新资产先以低抵押率上线

### 3.3 稳定币安全

| 类型 | 代表 | 锚定机制 | 核心风险 |
|------|------|---------|---------|
| 法币抵押 | USDT, USDC | 1:1美元储备 | 透明度、冻结风险、储备审计 |
| 加密抵押 | DAI | ETH超抵押（CDP） | 清算级联、抵押品价格暴跌 |
| 算法稳定币 | UST(已崩) | 算法调控供需 | **死亡螺旋风险**（Terra崩溃） |
| 混合型 | FRAX | 部分抵押+算法 | 部分算法风险 |

**Terra/UST死亡螺旋：**

```
UST脱锚 → 抛售UST → 铸造更多LUNA → LUNA稀释暴跌
    ↑                                        │
    └──── LUNA暴跌 → UST信心崩溃 ────────────┘
    
  算法稳定币的固有缺陷：
  - 无真实价值支撑，依赖市场信心
  - 正反馈循环导致死亡螺旋
  - 闪电贷可加速脱锚
```

### 3.4 收益聚合器安全

**Yearn/Venus类型聚合器风险：**
- 策略合约漏洞（策略资产被转移）
- 组合性风险（底层协议被黑导致聚合器损失）
- 权限管理（strategist可更换策略）
- 重入风险（收益复投过程中的重入）

### 3.5 NFT安全

- **元数据篡改**：链下存储的元数据可被中心化服务器修改
- **重入攻击**：`onERC721Received`回调中的重入
- **签名验证**：EIP-712签名缺失/重放
- **版税绕过**：转移NFT规避版税支付
- **地板价操纵**：低流动性NFT价格被操纵影响借贷抵押值

---

## 四、跨链安全

### 4.1 跨链技术分类

```
┌──────────────────────────────────────────────────────────┐
│                    跨链技术分类                            │
├──────────────┬───────────────────────────────────────────┤
│ 公证人机制   │ 中心化/去中心化公证人验证跨链交易          │
│ (Notary)    │ 信任假设：公证人诚实                       │
├──────────────┼───────────────────────────────────────────┤
│ 侧链/中继链  │ Polkadot/Cosmos IBC                       │
│ (Sidechain) │ 信任假设：中继链验证者                      │
├──────────────┼───────────────────────────────────────────┤
│ 哈希锁定     │ HTLC（Hashed TimeLock Contract）          │
│ (HTLC)      │ 信任假设：无需信任（原子交换）              │
├──────────────┼───────────────────────────────────────────┤
│ 跨链桥       │ 锁定+铸造 或 流动性池模型                   │
│ (Bridge)    │ 信任假设：桥的多签/验证者                    │
└──────────────┴───────────────────────────────────────────┘
```

#### 4.1.1 公证人机制（Notary Scheme）

```
公证人跨链流程：
  源链A: 用户发起跨链交易
       → 公证人组验证交易最终性
       → 多签确认 → 在目标链B释放资产

  信任模型：
  - 中心化公证人（sMPC）：如Thorchain早期
  - 去中心化公证人：多签+链上验证者

  安全风险：
  - 公证人私钥泄露 → Ronin Bridge ($624M)
  - 公证人合谋 → 资产被盗
  - 单点故障
```

#### 4.1.2 侧链/中继链（Polkadot/Cosmos）

```
Polkadot中继链模型：
  源链(平行链A) → 中继链验证 → 目标链(平行链B)
  
  安全来源：共享Polkadot中继链的安全性
  消息传递：XCMP（跨链消息传递协议）
  验证方式：中继链验证者保证平行链状态转换有效性

Cosmos IBC模型：
  源链 → 轻客户端验证 → 目标链
  
  安全来源：各链独立安全性
  消息传递：IBC协议（packets+acknowledgements）
  验证方式：链间轻客户端验证对端共识
```

#### 4.1.3 哈希锁定（HTLC）

```solidity
// HTLC跨链原子交换合约
contract HashedTimelock {
    struct LockContract {
        address sender;       // 发起方
        address receiver;     // 接收方
        bytes32 hashlock;     // 哈希锁
        uint256 amount;       // 锁定金额
        uint256 timelock;     // 超时时间
        bool withdrawn;       // 是否已提取
        bool refunded;        // 是否已退款
    }

    mapping(bytes32 => LockContract) public contracts;

    // 发起方锁定资金
    function newContract(
        address receiver,
        bytes32 hashlock,
        uint256 timelock
    ) external payable returns (bytes32 contractId) {
        require(msg.value > 0, "Amount must be > 0");
        require(timelock > block.timestamp, "Timelock in past");

        contractId = sha256(
            abi.encodePacked(msg.sender, receiver, hashlock, msg.value, timelock)
        );
        require(contracts[contractId].sender == address(0), "Contract exists");

        contracts[contractId] = LockContract({
            sender: msg.sender,
            receiver: receiver,
            hashlock: hashlock,
            amount: msg.value,
            timelock: timelock,
            withdrawn: false,
            refunded: false
        });
    }

    // 接收方提供原像提取资金
    function withdraw(bytes32 contractId, bytes32 preimage) external {
        LockContract storage c = contracts[contractId];
        require(c.receiver == msg.sender, "Not receiver");
        require(!c.withdrawn, "Already withdrawn");
        require(block.timestamp < c.timelock, "Timelock expired");
        require(sha256(abi.encodePacked(preimage)) == c.hashlock, "Invalid preimage");

        c.withdrawn = true;
        (bool ok, ) = c.receiver.call{value: c.amount}("");
        require(ok);
    }

    // 超时后发起方退款
    function refund(bytes32 contractId) external {
        LockContract storage c = contracts[contractId];
        require(c.sender == msg.sender, "Not sender");
        require(!c.refunded, "Already refunded");
        require(block.timestamp >= c.timelock, "Not expired");

        c.refunded = true;
        (bool ok, ) = c.sender.call{value: c.amount}("");
        require(ok);
    }
}
```

#### 4.1.4 跨链桥（Bridge）

### 4.2 跨链桥安全

#### 4.2.1 锁定+铸造模型

```
锁定+铸造（Lock-Mint）模型：

源链A:  用户 → 将100 USDC存入桥合约 → 锁定
                                        ↓
目标链B:  桥验证者签名 → 铸造100 USDC.b（包装代币）→ 用户

逆向：  用户销毁USDC.b → 桥释放源链锁定的USDC

安全关键：
  - 桥验证者的签名机制（多签门限）
  - 源链锁定合约的提款权限
  - 目标链铸造权限的控制
  - 消息真实性的验证

风险：
  - 验证者私钥泄露 → 伪造提款 → 锁定资金被盗
  - 铸造权限漏洞 → 无限铸造 → 脱锚
```

#### 4.2.2 流动性池模型

```
流动性池（Liquidity Pool）模型：

源链A:  桥流动性池 (USDC: 1,000,000)
        用户存入100,000 USDC → 从池中转出

目标链B: 桥流动性池 (USDC: 1,000,000)
         消息验证通过 → 从池中转出100,000 USDC → 用户

  无需铸造，使用预先注入的流动性

优势：无铸造权限风险
风险：
  - 流动性枯竭（一方资金池被耗尽）
  - 资金效率低（需要双侧预注流动性）
  - LP资金的安全（LP承担桥被盗风险）
```

#### 4.2.3 跨链桥攻击案例

**Wormhole（$3.26亿，2022年2月）：**

```
根因：签名验证漏洞
  Wormhole在Solana端的合约使用了一种"桥接签名"机制
  攻击者通过漏洞伪造了有效签名 → 在Solana端铸造120,000 wETH
  随后将wETH跨链到以太坊提取真实ETH

  技术细节：
  - Wormhole的Guardians多签验证存在逻辑缺陷
  - 签名验证使用sysvar_instruction_account
  - 攻击者通过system program指令注入伪造的guardian set
  - 使得验证通过
```

**Ronin Bridge（$6.24亿，2022年3月）：**

```
根因：验证者私钥泄露
  Ronin Bridge使用9个验证者，需要5/9签名即可放行提款
  攻击者通过社会工程获取了4个验证者的私钥
  +1个验证者通过API漏洞被控制 → 达到5/9门限
  → 签署伪造的提款消息 → 提取173,600 ETH + 25.5M USDC

  教训：
  - 验证者私钥管理不严（未使用HSM/MPC）
  - 门限过低（5/9 = 56%，应≥67%）
  - 缺少链上异常监控
  - 验证者节点集中托管
```

**Nomad Bridge（$1.9亿，2022年8月）：**

```
根因：初始化漏洞
  Nomad的Replica合约在初始化时设置了一个"可信根"（trustedRoot）
  代码中的验证逻辑存在缺陷：
  
  // 伪代码：漏洞逻辑
  function process(bytes memory message) {
      bytes32 root = calculateRoot(message);
      // 漏洞：当trustedRoot为0x00时，任何hash以00开头的消息都通过验证
      require(acceptableRoot[root], "Invalid root");
  }
  
  攻击者发现：将消息的destination字段设为特定值
  → hash结果为0x00开头 → 通过验证
  → 无需任何签名即可提走资金
  
  且攻击公开后，任何人都能复制攻击 → 数百个地址参与
```

### 4.3 跨链消息传递安全

**跨链消息验证模型：**

| 模型 | 代表 | 安全假设 | 风险 |
|------|------|---------|------|
| 轻客户端验证 | IBC, Near Rainbow Bridge | 验证对端共识 | 轻客户端实现漏洞 |
| 中继+多签 | Wormhole, LayerZero | 中继者/预言机诚实 | 中继者合谋 |
| 乐观验证 | Nomad, Optimistic Bridge | 至少1个观察者诚实 | 观察者离线 |
| sMPC（安全多方计算） | Thorchain, Synapse | t-of-n门限安全 | 密钥泄露 |
| ZK证明 | Polyhedra | 密码学假设 | 电路实现漏洞 |

### 4.4 跨链流动性风险

- **流动性枯竭**：一侧资金池被耗尽，无法完成跨链
- **滑点风险**：大额跨链交易产生高滑点
- **延迟风险**：跨链确认延迟导致套利窗口关闭
- **重新打包风险**：交易在mempool中被前置

---

## 五、DeFi安全审计

### 5.1 静态分析工具

| 工具 | 类型 | 检测能力 | 优缺点 |
|------|------|---------|--------|
| **Slither** | 静态分析（AST） | 重入、未初始化、授权、整数溢出 | 速度快/误报较多 |
| **Mythril** | 符号执行 | 重入、访问控制、整数溢出 | 深度分析/速度慢 |
| **Securify v2** | 形式化分析 | 合约规范合规性 | 理论严谨/覆盖面有限 |
| **MythX** | 多引擎平台 | 综合分析 | 需付费/API限制 |
| **Echidna** | 模糊测试 | 属性测试 | 需手写不变量 |
| **Manticore** | 符号执行 | 深层路径探索 | 速度极慢 |

### 5.2 形式化验证

```solidity
// 形式化验证示例：使用invariant约束

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract LendingPool is ReentrancyGuard {
    // 形式化不变量（invariants）:
    // 1. totalDeposits == sum(balances[account] for all accounts)
    // 2. totalBorrows <= totalDeposits * collateralFactor
    // 3. 每个账户的健康因子 >= 1 或 处于清算状态

    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    uint256 public totalDeposits;
    uint256 public totalBorrows;
    uint256 public constant COLLATERAL_FACTOR = 80; // 80%

    // 不变量1: 存款总量守恒
    // 验证: sum(deposits[a]) == totalDeposits

    // 不变量2: 借款不超过抵押
    // 验证: borrows[a] <= deposits[a] * COLLATERAL_FACTOR / 100

    // 不变量3: 合约余额 >= totalDeposits - totalBorrows
    // 验证: address(this).balance >= totalDeposits - totalBorrows
}
```

### 5.3 审计流程与报告

```
┌──────────────────────────────────────────────────────────┐
│                 DeFi安全审计流程                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Phase 1: 预审计                                         │
│  ├─ 收集合约代码和白皮书                                 │
│  ├─ 理解协议设计和资金流向                               │
│  └─ 确定审计范围和优先级                                 │
│                                                          │
│  Phase 2: 自动化扫描                                     │
│  ├─ Slither静态分析                                      │
│  ├─ Mythril符号执行                                     │
│  ├─ Solhint/Solium代码规范检查                          │
│  └─ 自动化模糊测试(Echidna)                             │
│                                                          │
│  Phase 3: 人工审计                                       │
│  ├─ 逐函数代码审查                                       │
│  ├─ 权限和访问控制审查                                   │
│  ├─ 经济模型安全分析（预言机/清算/利率）                │
│  ├─ 升级机制和代理模式审查                               │
│  └─ 跨合约交互和组合性审查                               │
│                                                          │
│  Phase 4: 验证与报告                                     │
│  ├─ 编写PoC验证漏洞                                      │
│  ├─ 风险分级（Critical/High/Medium/Low/Info）          │
│  ├─ 提交修复建议                                         │
│  └─ 修复后复审                                           │
│                                                          │
│  Phase 5: 持续监控                                       │
│  ├─ 上线后链上监控部署                                   │
│  ├─ 漏洞赏金计划                                         │
│  └─ 迭代审计（每次升级）                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 5.4 代码审计checklist

| 检查项 | 审查要点 |
|--------|--------|
| 重入 | 外部调用后状态更新顺序、CEI模式、nonReentrant |
| 整数溢出 | Solidity版本、unchecked块使用、SafeMath |
| 访问控制 | onlyOwner/角色权限、函数可见性、initialize防重入 |
| 预言机 | 价格来源（Chainlink vs DEX）、TWAP、多源校验 |
| 闪电贷 | 价格操纵风险、治理投票时间锁、临时余额使用 |
| 升级安全 | 代理模式、升级权限管理、存储布局兼容 |
| 事件顺序 | emit事件与状态更新的顺序 |
| Gas限制 | 循环gas消耗、transfer的2300 gas限制 |
| ERC20兼容 | 转账返回值检查、fee-on-transfer处理 |
| 存储安全 | delegatecall存储布局、初始化检查 |

---

## 六、DeFi安全监控

### 6.1 链上监控

**Forta网络：**
```
Forta监控架构：
  检测代理(Detection Bots) → 实时监控链上交易
      ↓
  告警生成 → 推送到Forta网络
      ↓
  订阅者 → 接收告警 → 响应

  检测场景：
  - 大额闪电贷交易
  - 异常清算交易
  - 治理提案异常投票
  - 桥大额跨链交易
  - 合约权限变更
  - 代币异常增发
```

**CertiK Skynet：**
- 实时安全评分
- 社交媒体情绪监控
- 链上行为异常告警
- 项目方风险评估

### 6.2 异常交易检测

```
异常交易检测指标：

  1. 金额异常：单笔交易超过协议TVL的5%
  2. 频率异常：短时间内大量交互
  3. 价格异常：预言机价格偏离超过阈值
  4. 流向异常：资金流向非预期地址
  5. 组合异常：闪电贷+清算+跨链组合
  6. 合约交互异常：调用非白名单合约
  7. 治理异常：大额代币转移+投票组合
```

### 6.3 预言机监控

- **价格偏差监控**：Chainlink与DEX价格偏差超过阈值告警
- **预言机延迟监控**：预言机更新延迟超过阈值告警
- **多源一致性**：多个预言机价格不一致告警
- **预言机合约变更**：预言机地址/合约升级监控

---

## 七、Python DeFi安全分析脚本示例

### 7.1 智能合约重入检测脚本（使用AST分析）

```python
#!/usr/bin/env python3
"""
DeFi安全分析 - 智能合约重入漏洞检测（AST分析）
使用Solidity AST检测潜在重入漏洞模式
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Severity(Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"


@dataclass
class Finding:
    """漏洞发现"""
    severity: Severity
    title: str
    description: str
    line: Optional[int] = None
    pattern: Optional[str] = None


class ReentrancyDetector:
    """基于模式匹配的Solidity重入漏洞检测器"""

    # 外部调用模式（可能触发回调的函数）
    EXTERNAL_CALL_PATTERNS = [
        r'\.call\s*\{',
        r'\.call\s*\(',
        r'\.delegatecall\s*\(',
        r'\.staticcall\s*\(',
        r'\.transfer\s*\(',
        r'\.send\s*\(',
        r'token\.transfer\s*\(',
        r'token\.transferFrom\s*\(',
        r'IERC20\(.*\)\.transfer\s*\(',
        r'msg\.sender\.call\s*\{',
    ]

    # 状态更新模式
    STATE_UPDATE_PATTERNS = [
        r'\w+\s*[\+\-\*\/]?=\s*',
        r'\w+\s*\[\s*\w+\s*\]\s*=\s*',
        r'\.push\s*\(',
        r'\.pop\s*\(',
        r'\.delete\s*',
        r'delete\s+\w+',
    ]

    # nonReentrant修饰符
    REENTRANCY_GUARD_PATTERN = r'nonReentrant|nonReentrancyGuard|ReentrancyGuard'

    # Checks-Effects-Interactions违规模式
    # 外部调用后跟状态更新（非CEI顺序）
    CEI_VIOLATION = re.compile(
        r'(?:transfer|send|call|delegatecall|staticcall)\s*\('
        r'.*?\n'  # 调用行
        r'[^}]*?'  # 中间内容
        r'(?:\w+\s*[\+\-\*/]?=|delete\s+\w+|\w+\[.*?\]\s*=)',
        re.MULTILINE | re.DOTALL
    )

    def __init__(self):
        self.findings: list[Finding] = []

    def check_non_reentrant_modifier(self, source: str) -> bool:
        """检查是否使用了nonReentrant修饰符"""
        return bool(re.search(self.REENTRANCY_GUARD_PATTERN, source, re.IGNORECASE))

    def find_external_calls(self, source: str) -> list[tuple[int, str]]:
        """查找外部调用及其行号"""
        results = []
        for i, line in enumerate(source.split('\n'), 1):
            stripped = line.strip()
            # 跳过注释行
            if stripped.startswith('//') or stripped.startswith('/*'):
                continue
            for pattern in self.EXTERNAL_CALL_PATTERNS:
                if re.search(pattern, stripped):
                    results.append((i, stripped))
                    break
        return results

    def find_state_updates_after_call(
        self, source: str, call_line: int
    ) -> list[tuple[int, str]]:
        """在外部调用行之后查找状态更新"""
        lines = source.split('\n')
        updates = []
        # 在调用行之后检查（同函数内）
        brace_depth = 0
        in_function = False
        for i in range(call_line, min(call_line + 20, len(lines))):
            line = lines[i].strip()
            if '{' in lines[i]:
                brace_depth += lines[i].count('{')
                in_function = True
            if '}' in lines[i]:
                brace_depth -= lines[i].count('}')
            if in_function and brace_depth <= 0 and i > call_line:
                break
            for pattern in self.STATE_UPDATE_PATTERNS:
                if re.search(pattern, line) and not line.startswith('//'):
                    # 排除require/assert/emit中的赋值
                    if not any(kw in line for kw in ['require', 'assert', 'emit', 'return']):
                        updates.append((i + 1, line))
                        break
        return updates

    def analyze_function(self, source: str, func_name: str,
                         func_source: str) -> list[Finding]:
        """分析单个函数的重入风险"""
        findings = []

        has_guard = self.check_non_reentrant_modifier(func_source)
        external_calls = self.find_external_calls(func_source)

        if not external_calls:
            return findings

        for call_line, call_text in external_calls:
            state_updates = self.find_state_updates_after_call(
                func_source, call_line - 1
            )

            if state_updates and not has_guard:
                # 有状态更新在外部调用之后且无nonReentrant保护
                findings.append(Finding(
                    severity=Severity.HIGH,
                    title=f"重入风险: {func_name}",
                    description=(
                        f"函数 {func_name} 在第{call_line}行执行外部调用后，"
                        f"在第{state_updates[0][0]}行更新状态。"
                        f"这违反了Checks-Effects-Interactions模式，"
                        f"且未使用nonReentrant修饰符。"
                        f"\n  外部调用: {call_text.strip()}"
                        f"\n  状态更新: {state_updates[0][1].strip()}"
                    ),
                    line=call_line,
                    pattern="External call before state update"
                ))
            elif state_updates and has_guard:
                # 有nonReentrant但有CEI违规（中等风险）
                findings.append(Finding(
                    severity=Severity.LOW,
                    title=f"CEI模式违规: {func_name}",
                    description=(
                        f"函数 {func_name} 虽有nonReentrant保护，"
                        f"但仍建议遵循Checks-Effects-Interactions模式。"
                    ),
                    line=call_line,
                    pattern="CEI violation (guarded)"
                ))

        return findings

    def extract_functions(self, source: str) -> dict[str, str]:
        """提取每个函数的源代码"""
        functions = {}
        # 匹配 function 定义
        func_pattern = re.compile(
            r'function\s+(\w+)\s*\([^)]*\)[^{]*\{',
            re.MULTILINE
        )
        for match in func_pattern.finditer(source):
            func_name = match.group(1)
            start = match.start()
            # 找到匹配的大括号
            brace_count = 0
            end = match.end() - 1  # 指向 '{'
            for i in range(match.end() - 1, len(source)):
                if source[i] == '{':
                    brace_count += 1
                elif source[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            functions[func_name] = source[start:end]
        return functions

    def analyze(self, source: str) -> list[Finding]:
        """分析完整合约源码"""
        self.findings = []

        # 提取函数
        functions = self.extract_functions(source)

        for func_name, func_source in functions.items():
            func_findings = self.analyze_function(source, func_name, func_source)
            self.findings.extend(func_findings)

        # 检查合约级别的nonReentrant导入
        if not self.check_non_reentrant_modifier(source):
            if any(f.severity == Severity.HIGH for f in self.findings):
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    title="缺少ReentrancyGuard",
                    description="合约未导入ReentrancyGuard，建议从OpenZeppelin导入",
                    pattern="Missing ReentrancyGuard import"
                ))

        return self.findings


# 测试用例
VULNERABLE_CONTRACT = """
pragma solidity ^0.8.0;

contract VulnerableVault {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // 外部调用在前
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");

        // 状态更新在后 —— 重入漏洞！
        balances[msg.sender] = 0;
    }
}
"""

SAFE_CONTRACT = """
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract SafeVault is ReentrancyGuard {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external nonReentrant {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance");

        // 1. Effects: 先更新状态
        balances[msg.sender] = 0;

        // 2. Interactions: 后执行外部调用
        (bool ok, ) = msg.sender.call{value: amount}("");
        require(ok, "Transfer failed");
    }
}
"""


def main():
    print("=" * 70)
    print("DeFi安全分析 - 智能合约重入漏洞检测（AST模式分析）")
    print("=" * 70)

    detector = ReentrancyDetector()

    # 测试漏洞合约
    print("\n[1] 分析漏洞合约: VulnerableVault")
    print("-" * 50)
    findings = detector.analyze(VULNERABLE_CONTRACT)
    if findings:
        for f in findings:
            print(f"\n  [{f.severity.value}] {f.title}")
            if f.line:
                print(f"  行号: {f.line}")
            print(f"  描述: {f.description}")
    else:
        print("  未发现问题")

    # 测试安全合约
    print("\n\n[2] 分析安全合约: SafeVault")
    print("-" * 50)
    findings = detector.analyze(SAFE_CONTRACT)
    if findings:
        for f in findings:
            print(f"\n  [{f.severity.value}] {f.title}")
            if f.line:
                print(f"  行号: {f.line}")
            print(f"  描述: {f.description}")
    else:
        print("  未发现问题（合约使用了nonReentrant + CEI模式）")

    print("\n" + "=" * 70)
    print("检测完成。")
    print("提示: 此脚本使用正则模式匹配，存在误报/漏报。")
    print("      生产环境应结合Slither/Mythril等专业工具使用。")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 7.2 闪电贷攻击检测脚本（模拟链上数据分析）

```python
#!/usr/bin/env python3
"""
DeFi安全分析 - 闪电贷攻击检测（模拟链上数据分析）
通过分析交易模式检测可能的闪电贷攻击
"""

import time
import random
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional
from enum import Enum


class AlertType(Enum):
    FLASH_LOAN_LARGE = "大额闪电贷"
    PRICE_MANIPULATION = "预言机价格操纵"
    GOVERNANCE_RUSH = "治理投票急速通过"
    LIQUIDITY_DRAIN = "流动性异常抽取"
    COMBINED_ATTACK = "组合攻击模式"


@dataclass
class Transaction:
    """模拟链上交易"""
    tx_hash: str
    block_number: int
    timestamp: float
    sender: str
    actions: list[dict]  # 交易中的操作序列
    gas_used: int = 0
    flash_loan_amount: float = 0.0
    flash_loan_source: str = ""


@dataclass
class Alert:
    """安全告警"""
    alert_type: AlertType
    tx_hash: str
    description: str
    severity: str  # Critical/High/Medium
    details: dict


class FlashLoanDetector:
    """闪电贷攻击检测引擎"""

    def __init__(self):
        self.alerts: list[Alert] = []
        # 基线数据
        self.normal_daily_volume: float = 50_000_000  # $50M日均交易量
        self.price_history: dict[str, list[tuple[float, float]]] = {}
        self.protocol_tvl: dict[str, float] = {}

    def check_large_flash_loan(self, tx: Transaction) -> Optional[Alert]:
        """检测大额闪电贷"""
        if tx.flash_loan_amount <= 0:
            return None

        # 闪电贷金额超过协议TVL的10%
        tvl_ratio = tx.flash_loan_amount / max(
            self.protocol_tvl.get("total", 1), 1
        )
        if tvl_ratio > 0.10:
            severity = "Critical" if tvl_ratio > 0.30 else "High"
            return Alert(
                alert_type=AlertType.FLASH_LOAN_LARGE,
                tx_hash=tx.tx_hash,
                description=(
                    f"大额闪电贷: ${tx.flash_loan_amount:,.0f} "
                    f"占协议TVL的{tvl_ratio*100:.1f}%"
                ),
                severity=severity,
                details={
                    "amount": tx.flash_loan_amount,
                    "source": tx.flash_loan_source,
                    "tvl_ratio": tvl_ratio,
                }
            )
        return None

    def check_price_manipulation(self, tx: Transaction) -> Optional[Alert]:
        """检测预言机价格操纵"""
        # 检查交易中是否有价格剧变
        for action in tx.actions:
            if action.get("type") == "price_update":
                token = action.get("token", "")
                old_price = action.get("old_price", 0)
                new_price = action.get("new_price", 0)
                if old_price > 0 and new_price > 0:
                    change_pct = abs(new_price - old_price) / old_price
                    # 价格在单笔交易中变化超过20%
                    if change_pct > 0.20:
                        return Alert(
                            alert_type=AlertType.PRICE_MANIPULATION,
                            tx_hash=tx.tx_hash,
                            description=(
                                f"价格异常波动: {token} "
                                f"从${old_price:.2f}变至${new_price:.2f}"
                                f"(变化{change_pct*100:.1f}%)"
                            ),
                            severity="Critical" if change_pct > 0.50 else "High",
                            details={
                                "token": token,
                                "old_price": old_price,
                                "new_price": new_price,
                                "change_pct": change_pct,
                            }
                        )
        return None

    def check_governance_rush(self, tx: Transaction) -> Optional[Alert]:
        """检测闪电贷治理攻击"""
        has_flash_loan = tx.flash_loan_amount > 0
        has_governance_action = any(
            a.get("type") in ["vote", "propose", "execute_proposal"]
            for a in tx.actions
        )

        if has_flash_loan and has_governance_action:
            return Alert(
                alert_type=AlertType.GOVERNANCE_RUSH,
                tx_hash=tx.tx_hash,
                description=(
                    "闪电贷+治理操作组合: 可能是闪电贷治理攻击"
                    "（借入资金获取临时投票权通过恶意提案）"
                ),
                severity="Critical",
                details={
                    "flash_loan": tx.flash_loan_amount,
                    "actions": [a.get("type") for a in tx.actions],
                }
            )
        return None

    def check_combined_attack(self, tx: Transaction) -> Optional[Alert]:
        """检测组合攻击模式"""
        action_types = {a.get("type") for a in tx.actions}
        attack_patterns = {
            # 闪电贷+借贷+清算
            "flash_loan_attack": {"flash_loan", "borrow", "liquidate"},
            # 闪电贷+DEX套利
            "flash_arb": {"flash_loan", "swap", "swap"},
            # 闪电贷+质押+提取
            "stake_drain": {"flash_loan", "stake", "withdraw"},
        }

        for pattern_name, required_actions in attack_patterns.items():
            if required_actions.issubset(action_types):
                return Alert(
                    alert_type=AlertType.COMBINED_ATTACK,
                    tx_hash=tx.tx_hash,
                    description=(
                        f"组合攻击模式[{pattern_name}]: "
                        f"检测到{required_actions}操作组合"
                    ),
                    severity="Critical",
                    details={
                        "pattern": pattern_name,
                        "actions": list(action_types),
                    }
                )
        return None

    def check_liquidity_drain(self, tx: Transaction) -> Optional[Alert]:
        """检测流动性异常抽取"""
        for action in tx.actions:
            if action.get("type") == "withdraw":
                amount = action.get("amount", 0)
                pool = action.get("pool", "")
                pool_tvl = self.protocol_tvl.get(pool, 0)
                if pool_tvl > 0 and amount / pool_tvl > 0.30:
                    return Alert(
                        alert_type=AlertType.LIQUIDITY_DRAIN,
                        tx_hash=tx.tx_hash,
                        description=(
                            f"流动性异常抽取: 从{pool}提取"
                            f"${amount:,.0f} (占池TVL的"
                            f"{amount/pool_tvl*100:.1f}%)"
                        ),
                        severity="High",
                        details={
                            "pool": pool,
                            "amount": amount,
                            "pool_tvl": pool_tvl,
                        }
                    )
        return None

    def analyze(self, tx: Transaction):
        """分析单笔交易"""
        checks = [
            self.check_large_flash_loan,
            self.check_price_manipulation,
            self.check_governance_rush,
            self.check_combined_attack,
            self.check_liquidity_drain,
        ]
        for check in checks:
            alert = check(tx)
            if alert:
                self.alerts.append(alert)


def generate_normal_transactions(n: int = 10) -> list[Transaction]:
    """生成模拟正常交易"""
    txs = []
    for i in range(n):
        tx = Transaction(
            tx_hash=f"0x{'a' * 8}{i:04x}{'b' * 52}",
            block_number=18000000 + i,
            timestamp=time.time() + i * 12,
            sender=f"0xUser{i:04d}",
            actions=[
                {"type": "swap", "token": "ETH", "amount": random.uniform(1, 10)},
                {"type": "deposit", "pool": "Aave", "amount": random.uniform(1000, 50000)},
            ],
            gas_used=random.randint(100000, 300000),
            flash_loan_amount=0,
        )
        txs.append(tx)
    return txs


def generate_attack_transactions() -> list[Transaction]:
    """生成模拟攻击交易"""
    attacks = []

    # 攻击1：bZx式预言机操纵
    attacks.append(Transaction(
        tx_hash="0xdead0001beef0001cafe0001" + "0" * 40,
        block_number=18000010,
        timestamp=time.time() + 100,
        sender="0xAttacker01",
        actions=[
            {"type": "flash_loan", "source": "dYdX", "amount": 10000, "token": "ETH"},
            {"type": "borrow", "protocol": "bZx", "amount": 50000, "token": "WBTC"},
            {"type": "swap", "pool": "Uniswap", "token": "WBTC", "amount": 50000},
            {"type": "price_update", "token": "WBTC",
             "old_price": 30000, "new_price": 45000},  # 价格+50%
            {"type": "repay", "protocol": "bZx", "amount": 30000},
            {"type": "repay", "source": "dYdX", "amount": 10000, "token": "ETH"},
        ],
        gas_used=500000,
        flash_loan_amount=10000 * 3000,  # ~$30M ETH
        flash_loan_source="dYdX",
    ))

    # 攻击2：Beanstalk式治理攻击
    attacks.append(Transaction(
        tx_hash="0xbeef0002dead0002cafe0002" + "0" * 40,
        block_number=18000011,
        timestamp=time.time() + 112,
        sender="0xAttacker02",
        actions=[
            {"type": "flash_loan", "source": "Aave", "amount": 100000000,
             "token": "USDC"},
            {"type": "stake", "protocol": "Beanstalk", "amount": 100000000},
            {"type": "propose", "proposal": "evil_proposal_0x42"},
            {"type": "vote", "proposal": "evil_proposal_0x42", "votes": 100000000},
            {"type": "execute_proposal", "proposal": "evil_proposal_0x42"},
            {"type": "withdraw", "pool": "Beanstalk_treasury", "amount": 182000000},
            {"type": "repay", "source": "Aave", "amount": 100000000, "token": "USDC"},
        ],
        gas_used=800000,
        flash_loan_amount=100000000,  # $100M
        flash_loan_source="Aave",
    ))

    # 攻击3：闪电贷清算攻击
    attacks.append(Transaction(
        tx_hash="0xcafe0003dead0003beef0003" + "0" * 40,
        block_number=18000012,
        timestamp=time.time() + 124,
        sender="0xAttacker03",
        actions=[
            {"type": "flash_loan", "source": "Aave", "amount": 50000000,
             "token": "USDC"},
            {"type": "swap", "pool": "Uniswap", "token": "CRV", "amount": 50000000},
            {"type": "price_update", "token": "CRV",
             "old_price": 1.0, "new_price": 0.6},  # 价格-40%
            {"type": "liquidate", "protocol": "Aave",
             "borrower": "0xVictim", "amount": 10000000},
            {"type": "swap", "pool": "Uniswap", "token": "USDC", "amount": 8000000},
            {"type": "repay", "source": "Aave", "amount": 50000000, "token": "USDC"},
        ],
        gas_used=600000,
        flash_loan_amount=50000000,  # $50M
        flash_loan_source="Aave",
    ))

    return attacks


def main():
    print("=" * 70)
    print("DeFi安全分析 - 闪电贷攻击检测（模拟链上数据）")
    print("=" * 70)

    detector = FlashLoanDetector()
    detector.protocol_tvl = {
        "total": 200_000_000,  # $200M
        "Aave": 50_000_000,
        "Beanstalk_treasury": 182_000_000,
        "Uniswap_WBTC_ETH": 30_000_000,
    }

    # 1. 分析正常交易
    print("\n[1] 分析正常交易流量...")
    normal_txs = generate_normal_transactions(10)
    for tx in normal_txs:
        detector.analyze(tx)
    print(f"    分析了 {len(normal_txs)} 笔正常交易")

    # 2. 分析攻击交易
    print("\n[2] 分析可疑交易...")
    attack_txs = generate_attack_transactions()
    for tx in attack_txs:
        detector.analyze(tx)
    print(f"    分析了 {len(attack_txs)} 笔可疑交易")

    # 3. 输出告警
    print(f"\n[3] 共触发 {len(detector.alerts)} 条安全告警:\n")
    for i, alert in enumerate(detector.alerts, 1):
        print(f"  告警 #{i}")
        print(f"  类型: [{alert.alert_type.value}]")
        print(f"  严重性: {alert.severity}")
        print(f"  交易: {alert.tx_hash[:20]}...")
        print(f"  描述: {alert.description}")
        print(f"  详情: {alert.details}")
        print()

    # 4. 统计
    print("[4] 告警统计:")
    type_counts = defaultdict(int)
    severity_counts = defaultdict(int)
    for alert in detector.alerts:
        type_counts[alert.alert_type.value] += 1
        severity_counts[alert.severity] += 1
    print("    按类型:")
    for atype, count in sorted(type_counts.items()):
        print(f"      {atype}: {count}次")
    print("    按严重性:")
    for sev, count in sorted(severity_counts.items()):
        print(f"      {sev}: {count}次")

    print("\n" + "=" * 70)
    print("检测完成。")
    print("提示: 此脚本使用模拟交易数据。实际应用中应:")
    print("  - 连接以太坊节点获取实时交易数据")
    print("  - 集成Chainlink预言机价格作为基线")
    print("  - 使用Forta/CertiK Skynet等链上监控平台")
    print("  - 设置告警通知（Telegram/Discord/PagerDuty）")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

---

## 总结

本文档系统覆盖了DeFi与跨链安全的七大核心方向：

| 方向 | 核心要点 |
|------|---------|
| DeFi概述 | TVL生态、DeFi vs TradFi差异、重大攻击事件复盘 |
| 合约漏洞 | 重入（ERC-20/721）、整数溢出、访问控制、闪电贷（bZx/Beanstalk）、MEV（三明治/Flashbots）、治理攻击 |
| DeFi协议 | DEX（Uniswap V3集中流动性）、借贷（Aave清算模型）、稳定币（Terra死亡螺旋）、收益聚合器、NFT安全 |
| 跨链安全 | 公证人/侧链/HTLC/桥分类、锁定+铸造 vs 流动性池模型、Wormhole/Ronin/Nomad攻击复盘 |
| 安全审计 | Slither/Mythril/Securify工具链、形式化验证、审计流程、checklist |
| 安全监控 | Forta/CertiK Skynet链上监控、异常交易检测、预言机监控 |
| Python脚本 | Solidity重入AST检测、闪电贷攻击链上模式检测 |

**学习建议：**
1. 结合`智能合约安全.md`学习Solidity基础和常见漏洞模式
2. 参考`区块链安全审计.md`深入审计流程
3. 重点关注闪电贷+预言机操纵的组合攻击链
4. 理解跨链桥的三种安全模型及各自信任假设
5. 实践使用Foundry/Hardhat编写和测试PoC
6. 跟踪DeFi安全事件（rekt.news事件数据库）
