# 数字签名技术详解

> 本文档整理自：`数字签名技术详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 数字签名概述](./02_数字签名概述/数字签名概述.md)
  - 什么是数字签名
  - 数字签名的安全服务
  - 数字签名的发展历史
  - 法律地位

### [03. 数字签名原理](./03_数字签名原理/数字签名原理.md)
  - 数字签名的基本流程
  - 签名过程的详细步骤
  - 哈希函数在签名中的作用
  - 签名方案的安全性要求

### [04. RSA数字签名](./04_RSA数字签名/RSA数字签名.md)
  - RSA签名原理
  - RSA签名填充方案
  - RSA密钥长度与安全性
  - OpenSSL RSA签名命令

### [05. DSA数字签名](./05_DSA数字签名/DSA数字签名.md)
  - DSA算法概述
  - DSA签名过程
  - DSA的随机数问题

### [06. ECDSA椭圆曲线数字签名](./06_ECDSA椭圆曲线数字签名/ECDSA椭圆曲线数字签名.md)
  - ECDSA概述
  - 椭圆曲线基础
  - ECDSA签名过程
  - ECDSA签名格式
  - ECDSA的安全注意事项

### [07. EdDSA签名算法](./07_EdDSA签名算法/EdDSA签名算法.md)
  - EdDSA概述
  - Ed25519签名
  - EdDSA与ECDSA对比
  - Ed25519在SSH中的应用

### [08. 国密SM2数字签名](./08_国密SM2数字签名/国密SM2数字签名.md)
  - SM2签名概述
  - SM2曲线参数
  - SM2签名流程
  - SM2签名格式

### [09. 数字签名标准与规范](./09_数字签名标准与规范/数字签名标准与规范.md)
  - CMS/PKCS#7签名
  - PAdES（PDF高级电子签名）
  - XAdES（XML高级电子签名）
  - CAdES（CMS高级电子签名）

### [10. 数字时间戳服务](./10_数字时间戳服务/数字时间戳服务.md)
  - 时间戳概述
  - RFC 3161时间戳协议
  - 长期签名验证（LTV）

### [11. 数字签名攻击与防御](./11_数字签名攻击与防御/数字签名攻击与防御.md)
  - 常见攻击类型
  - 签名替换攻击
  - 证书混淆攻击

### [12. 数字签名实践应用](./12_数字签名实践应用/数字签名实践应用.md)
  - 软件代码签名
  - 电子合同签名
  - 区块链交易签名
  - JWT签名

### [13. 后量子数字签名](./13_后量子数字签名/后量子数字签名.md)
  - 量子计算对签名的威胁
  - NIST后量子签名标准
  - 混合签名方案

### [14. 总结与最佳实践](./14_总结与最佳实践/总结与最佳实践.md)
  - 签名算法选择指南
  - 数字签名最佳实践
  - 常见错误
  - 参考标准

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **数字签名概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数字签名原理**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RSA数字签名**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **DSA数字签名**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **ECDSA椭圆曲线数字签名**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **EdDSA签名算法**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **国密SM2数字签名**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数字签名标准与规范**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数字时间戳服务**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **数字签名攻击与防御**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **数字签名实践应用**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **后量子数字签名**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **总结与最佳实践**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
