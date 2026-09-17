# 对称密码学详解

> 本文档整理自：`对称密码学详解.md`

---

## 目录

### [01. 对称加密原理](./01_对称加密原理/对称加密原理.md)
  - 基本概念
  - 核心特点
  - 对称加密分类

### [02. DES 算法原理与弱点](./02_DES 算法原理与弱点/DES 算法原理与弱点.md)
  - DES 概述
  - DES 整体结构
  - Feistel 网络详解
  - DES 轮函数 F
  - DES 密钥扩展
  - DES 的弱点
  - DES 现状

### [03. DES 与双重 DES 中间人攻击](./03_DES 与双重 DES 中间人攻击/DES 与双重 DES 中间人攻击.md)
  - 为什么需要 3DES？
  - 双重 DES（2DES）
  - 双重 DES 中间人攻击详解
  - 三重 DES（3DES）
  - 3DES 的安全性
  - 3DES 的缺点

### [04. AES 算法详解](./04_AES 算法详解/AES 算法详解.md)
  - AES 概述
  - AES 整体结构
  - 状态矩阵（State）
  - 轮函数详解
  - AES 密钥扩展
  - AES 解密
  - AES 的安全性

### [05. AES 工作模式](./05_AES 工作模式/AES 工作模式.md)
  - ECB 模式（Electronic Codebook）
  - CBC 模式（Cipher Block Chaining）
  - CFB 模式（Cipher Feedback）
  - OFB 模式（Output Feedback）
  - CTR 模式（Counter）
  - GCM 模式（Galois/Counter Mode）
  - XTS 模式（XEX Tweakable Block Cipher with Ciphertext Stealing）
  - 工作模式对比

### [06. 分组密码 vs 流密码](./06_分组密码 vs 流密码/分组密码 vs 流密码.md)
  - 分组密码（Block Cipher）
  - 流密码（Stream Cipher）
  - RC4 算法详解
  - ChaCha20 算法
  - 对比总结

### [07. 国密 SM4 算法](./07_国密 SM4 算法/国密 SM4 算法.md)
  - SM4 概述
  - SM4 整体结构
  - SM4 轮函数详解
  - SM4 密钥扩展
  - SM4 解密
  - SM4 的安全性
  - SM4 与 AES 对比

### [08. 常见实现错误与攻击](./08_常见实现错误与攻击/常见实现错误与攻击.md)
  - ECB 模式使用错误
  - IV/Nonce 使用错误
  - 填充 Oracle 攻击
  - 密钥派生错误
  - 侧信道攻击
  - 弱随机数生成
  - 密钥硬编码
  - 明文保留

### [09. 实际案例](./09_实际案例/实际案例.md)
  - 案例 1：WEP 协议破解
  - 案例 2：SSL BEAST 攻击
  - 案例 3：Heartbleed 漏洞

### [10. 学习与实践建议](./10_学习与实践建议/学习与实践建议.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **对称加密原理**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **DES 算法原理与弱点**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **DES 与双重 DES 中间人攻击**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **AES 算法详解**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **AES 工作模式**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **分组密码 vs 流密码**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **国密 SM4 算法**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **常见实现错误与攻击**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **实际案例**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **学习与实践建议**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
