# 智能合约安全

> 本文档整理自：`智能合约安全.md`

---

## 目录

### [01. Solidity 基础与常见陷阱](./01_Solidity 基础与常见陷阱/Solidity 基础与常见陷阱.md)
  - Solidity 简介
  - 数据类型与注意事项
  - 函数可见性
  - 存储位置
  - 特殊全局变量
  - Solidity 版本差异

### [02. 重入攻击（Reentrancy）](./02_重入攻击（Reentrancy）/重入攻击（Reentrancy）.md)
  - 漏洞原理
  - 漏洞代码示例
  - 攻击合约
  - 攻击步骤详解
  - 防御方法
  - 真实案例：The DAO 攻击

### [03. 整数溢出/下溢](./03_整数溢出_下溢/整数溢出_下溢.md)
  - 漏洞原理
  - 漏洞代码示例
  - 另一个溢出漏洞：批量转账
  - 真实案例：美链 BEC 溢出
  - 防御方法

### [04. 访问控制漏洞](./04_访问控制漏洞/访问控制漏洞.md)
  - 漏洞原理
  - 缺少权限检查
  - tx.origin 钓鱼攻击
  - 初始化函数漏洞（UUPS/代理模式）
  - 真实案例：Parity 钱包漏洞（2017）

### [05. 拒绝服务攻击（DoS）](./05_拒绝服务攻击（DoS）/拒绝服务攻击（DoS）.md)
  - 漏洞原理
  - Gas 耗尽型 DoS
  - 数组遍历型 DoS
  - 意外回退型 DoS

### [06. 前置交易（Front-running）](./06_前置交易（Front-running）/前置交易（Front-running）.md)
  - 漏洞原理
  - 常见攻击场景
  - 防御方法

### [07. 逻辑漏洞](./07_逻辑漏洞/逻辑漏洞.md)
  - 漏洞原理
  - 价格预言机操纵
  - 闪电贷攻击
  - 治理攻击

### [08. 合约安全审计方法](./08_合约安全审计方法/合约安全审计方法.md)
  - 审计流程
  - 审计关注点清单

### [09. 安全工具介绍](./09_安全工具介绍/安全工具介绍.md)
  - Mythril
  - Slither
  - Oyente
  - Manticore
  - Echidna
  - 工具对比
  - 工具使用建议

### [10. 参考资源](./10_参考资源/参考资源.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **Solidity 基础与常见陷阱**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
- **重入攻击（Reentrancy）**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **整数溢出/下溢**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **访问控制漏洞**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **拒绝服务攻击（DoS）**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **前置交易（Front-running）**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **逻辑漏洞**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **合约安全审计方法**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **安全工具介绍**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **参考资源**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
