# Layer2安全与预言机DID安全

> 本文档整理自：`Layer2安全与预言机DID安全.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Layer2 扩容方案概述](./02_Layer2 扩容方案概述/Layer2 扩容方案概述.md)
  - 为什么需要 Layer2
  - Layer2 安全模型对比

### [03. Optimistic Rollup 安全](./03_Optimistic Rollup 安全/Optimistic Rollup 安全.md)
  - 乐观执行模型
  - 挑战期与欺诈证明
  - 欺诈证明的类型

### [04. ZK-Rollup 安全](./04_ZK-Rollup 安全/ZK-Rollup 安全.md)
  - 零知识证明验证
  - 数据可用性
  - 电路安全

### [05. Layer2 安全风险](./05_Layer2 安全风险/Layer2 安全风险.md)
  - 排序者中心化
  - 数据可用性问题
  - 提款延迟攻击
  - 桥接安全

### [06. 跨链桥安全](./06_跨链桥安全/跨链桥安全.md)
  - 锁-铸造模型
  - 验证者签名安全
  - 流动性池桥安全

### [07. 预言机安全概述](./07_预言机安全概述/预言机安全概述.md)
  - 预言机在 DeFi 中的角色
  - 预言机类型

### [08. 预言机攻击面](./08_预言机攻击面/预言机攻击面.md)
  - 数据篡改攻击
  - 闪电贷操纵预言机
  - 操纵市场攻击

### [09. 预言机安全防护](./09_预言机安全防护/预言机安全防护.md)
  - 多数据源聚合
  - 时间加权平均价格（TWAP）
  - 延迟更新与熔断

### [10. DID 去中心化身份安全](./10_DID 去中心化身份安全/DID 去中心化身份安全.md)
  - DID 架构
  - 可验证凭证（VC）
  - W3C DID 标准

### [11. DID 安全风险](./11_DID 安全风险/DID 安全风险.md)
  - 密钥管理风险
  - DID 文档篡改
  - 标识解析劫持

### [12. DAO 治理安全](./12_DAO 治理安全/DAO 治理安全.md)
  - 治理攻击概述
  - 闪电贷治理攻击
  - 防护方案

### [13. 实战案例：预言机操纵攻击分析](./13_实战案例：预言机操纵攻击分析/实战案例：预言机操纵攻击分析.md)
  - 案例概述：bZx 攻击（2020年）
  - 攻击步骤详解
  - 攻击合约代码还原
  - 防护方案

### [14. 总结与学习路线](./14_总结与学习路线/总结与学习路线.md)
  - 知识体系总结
  - 学习路线建议
  - 关键要点速查

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **Layer2 扩容方案概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Optimistic Rollup 安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **ZK-Rollup 安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Layer2 安全风险**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **跨链桥安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **预言机安全概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **预言机攻击面**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **预言机安全防护**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **DID 去中心化身份安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **DID 安全风险**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **DAO 治理安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **实战案例：预言机操纵攻击分析**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **总结与学习路线**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：commands
