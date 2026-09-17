# Solidity 基础与常见陷阱

### 1.1 Solidity 简介

Solidity 是以太坊智能合约的主要编程语言，语法类似于 JavaScript/C++，是一种静态类型、面向对象的高级语言。

**特点：**
- 运行在 EVM（以太坊虚拟机）上
- 静态类型语言，编译为字节码
- 支持继承、库、接口等面向对象特性
- 内置加密函数和区块链相关全局变量

### 1.2 数据类型与注意事项

#### 1.2.1 整数类型

```solidity
// 有符号整数：int8 ~ int256（步长 8）
int8  public a = -128;     // 范围：-128 ~ 127
int256 public b = 100;     // 范围：-2^255 ~ 2^255-1

// 无符号整数：uint8 ~ uint256（步长 8）
uint8  public c = 255;     // 范围：0 ~ 255
uint256 public d = 100;    // 范围：0 ~ 2^256-1

// uint 是 uint256 的别名
uint public e = 100;       // 等同于 uint256
```

**⚠️ 常见陷阱：**
- Solidity 0.8 之前的版本，整数溢出不会报错，会静默回绕
- 不同类型的整数运算可能导致隐式转换问题
- 使用 `uint` 时注意不能为负数

#### 1.2.2 地址类型

```solidity
address public owner;           // 20 字节地址
address payable public receiver; // 可接收 ETH 的地址

// 地址类型的成员
// - balance：地址的 ETH 余额（单位：wei）
// - transfer(amount)：发送 ETH，失败则抛出异常（2300 gas）
// - send(amount)：发送 ETH，失败返回 bool（2300 gas）
// - call(...)：底层调用，返回 (bool, bytes)（转发所有 gas）
// - delegatecall(...)：委托调用，使用调用者的上下文
// - staticcall(...)：静态调用，不修改状态
```

**⚠️ 常见陷阱：**
- `transfer` 和 `send` 只有 2300 gas，接收方如果 fallback 函数复杂会失败
- `call` 会转发所有 gas，可能导致重入攻击
- 地址和合约地址无法在编译时区分
- 向非 payable 地址发送 ETH 会失败

#### 1.2.3 映射（Mapping）

```solidity
mapping(address => uint256) public balances;
mapping(address => mapping(address => uint256)) public allowance;

// 特点：
// 1. 无法遍历所有 key
// 2. 不存在的 key 返回默认值（0/false/空地址）
// 3. 不能作为返回值（外部函数）
// 4. 存储在 storage 中
```

**⚠️ 常见陷阱：**
- 无法判断一个 key 是否存在（因为默认值就是 0）
- 不能获取 mapping 的长度
- 无法删除整个 mapping

### 1.3 函数可见性

```solidity
// public：内部外部都可调用
function publicFunc() public { }

// external：只能从外部调用（合约内部不能直接调用，需用 this.调用）
function externalFunc() external { }

// internal：只能在当前合约和继承合约中调用
function internalFunc() internal { }

// private：只能在当前合约中调用
function privateFunc() private { }
```

**⚠️ 常见陷阱：**
- 默认可见性是 `public`（旧版本），显式声明更安全
- `external` 比 `public` 更省 gas（因为不需要复制参数到内存）
- 敏感函数不能设为 `public` 或 `external` 而不加权限控制

### 1.4 存储位置

```solidity
// storage：存储在区块链上，永久保存（状态变量）
uint256 public storedData;  // storage

// memory：函数执行时的临时内存，执行完即销毁
function test(uint256[] memory array) public pure {
    uint256[] memory tempArray = new uint256[](10);  // memory
}

// calldata：只读的函数参数存储（external 函数的参数）
function test(uint256[] calldata array) external pure {
    // array 是只读的，不能修改
}

// stack：EVM 栈上的局部变量（值类型）
```

**⚠️ 常见陷阱：**
- storage 引用可能意外覆盖状态变量
- memory 数组不能直接赋值给 storage 数组
- 复杂类型的存储位置容易混淆

### 1.5 特殊全局变量

```solidity
// 区块相关
block.number       // 当前区块高度
block.timestamp    // 当前区块时间戳（秒）
block.difficulty   // 区块难度
block.gaslimit     // 区块 gas 限制
block.coinbase     // 矿工地址
blockhash(uint n)  // 第 n 个区块的哈希（最近 256 个区块）

// 交易相关
msg.sender         // 消息发送者（直接调用者）
msg.value          // 发送的 ETH 数量（wei）
msg.data           // 完整的 calldata
msg.sig            // 函数选择器（前 4 字节）
tx.origin          // 交易的原始发送者（整个调用链的起点）
tx.gasprice        // 交易的 gas 价格

// 其他
address(this)      // 当前合约地址
this.balance       // 当前合约余额（同 address(this).balance）
gasleft()          // 剩余 gas
```

**⚠️ 常见陷阱：**
- 不要用 `block.timestamp` 做随机数或关键时间判断（矿工可操纵）
- 不要用 `tx.origin` 做权限验证（可能被钓鱼攻击）
- `msg.sender` 是直接调用者，不是交易发起者

### 1.6 Solidity 版本差异

| 版本 | 重要变化 |
|------|---------|
| **0.4.x** | 早期版本，函数可见性默认 public |
| **0.5.0** | 明确要求函数可见性声明；引入 calldata 位置 |
| **0.6.0** | 引入 try/catch；引入 virtual/override |
| **0.7.0** | 移除 NatSpec 注释校验；调整全局变量 |
| **0.8.0** | 内置整数溢出/下溢检查（默认 revert）；引入 custom error |
| **0.8.4** | 引入自定义错误（custom error）更省 gas |
| **0.8.7** | 引入 block.basefee（EIP-1559） |

**注意：** Solidity 0.8 之前整数溢出是静默的，需要使用 SafeMath 库。0.8 及以后版本内置溢出检查，溢出会 revert。

---

---

## 📋 内容审核与补充建议

> 针对「Solidity 基础与常见陷阱」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
