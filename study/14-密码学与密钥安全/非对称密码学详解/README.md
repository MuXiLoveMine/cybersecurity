# 非对称密码学详解

> 本文档整理自：`非对称密码学详解.md`

---

## 目录

### [01. 公钥密码学原理](./01_公钥密码学原理/公钥密码学原理.md)
  - 基本概念
  - 数学基础：陷门单向函数
  - 对称 vs 非对称对比

### [02. RSA 算法原理](./02_RSA 算法原理/RSA 算法原理.md)
  - RSA 概述
  - 数学基础
  - RSA 密钥生成
  - RSA 加密解密
  - RSA 数字签名
  - RSA 填充方案
  - RSA 实现优化

### [03. RSA 常见攻击](./03_RSA 常见攻击/RSA 常见攻击.md)
  - 因数分解攻击
  - 共模攻击（Common Modulus Attack）
  - 低加密指数攻击
  - 低解密指数攻击（Wiener's Attack）
  - 选择密文攻击（CCA）
  - 侧信道攻击

### [04. ECC 椭圆曲线密码学](./04_ECC 椭圆曲线密码学/ECC 椭圆曲线密码学.md)
  - ECC 概述
  - 椭圆曲线数学基础
  - ECC 加密（ECIES）
  - ECDSA 椭圆曲线数字签名算法
  - 常见椭圆曲线
  - Curve25519 / Ed25519

### [05. 国密 SM2 算法](./05_国密 SM2 算法/国密 SM2 算法.md)
  - SM2 概述
  - SM2 曲线参数
  - SM2 数字签名
  - SM2 加密解密
  - SM2 密钥交换
  - SM2 与 ECDSA 对比

### [06. DH 密钥交换](./06_DH 密钥交换/DH 密钥交换.md)
  - DH 概述
  - DH 原理
  - 离散对数问题（DLP）
  - DH 的问题：中间人攻击
  - DH 参数选择
  - 前向保密（Forward Secrecy）

### [07. ECDH 椭圆曲线密钥交换](./07_ECDH 椭圆曲线密钥交换/ECDH 椭圆曲线密钥交换.md)
  - ECDH 原理
  - ECDH 的优势
  - ECDH 安全注意事项

### [08. 数字签名](./08_数字签名/数字签名.md)
  - 数字签名概述
  - 数字签名原理
  - RSA 签名
  - ECDSA 签名
  - EdDSA / Ed25519
  - SM2 签名
  - 签名算法对比

### [09. 实际案例](./09_实际案例/实际案例.md)
  - 案例 1：索尼 PS3 ECDSA 破解
  - 案例 2：Heartbleed 与私钥泄露
  - 案例 3：ROCA 漏洞（Return of Coppersmith's Attack）

### [10. 学习与实践建议](./10_学习与实践建议/学习与实践建议.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **公钥密码学原理**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **RSA 算法原理**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RSA 常见攻击**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **ECC 椭圆曲线密码学**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：references
- **国密 SM2 算法**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **DH 密钥交换**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **ECDH 椭圆曲线密钥交换**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **数字签名**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实际案例**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **学习与实践建议**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
