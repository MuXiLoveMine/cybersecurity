# 密钥交换协议

> 本文档整理自：`密钥交换协议.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 密钥交换概述](./02_密钥交换概述/密钥交换概述.md)
  - 什么是密钥交换
  - 密钥交换的分类
  - 密钥交换的安全属性
  - 密钥交换发展历史

### [03. Diffie-Hellman密钥交换](./03_Diffie-Hellman密钥交换/Diffie-Hellman密钥交换.md)
  - DH密钥交换原理
  - DH的安全参数
  - DH实现
  - DH的安全问题
  - 有限域DH vs 椭圆曲线DH

### [04. ECDH椭圆曲线密钥交换](./04_ECDH椭圆曲线密钥交换/ECDH椭圆曲线密钥交换.md)
  - ECDH原理
  - ECDH实现
  - Curve25519与X25519

### [05. 认证密钥交换（AKE）](./05_认证密钥交换（AKE）/认证密钥交换（AKE）.md)
  - 为什么需要认证密钥交换
  - STS协议（站到站）
  - MQV协议
  - HMQV协议
  - SIGMA协议

### [06. TLS密钥交换机制](./06_TLS密钥交换机制/TLS密钥交换机制.md)
  - TLS 1.2密钥交换
  - TLS 1.3密钥交换
  - TLS密钥派生

### [07. Signal协议密钥交换](./07_Signal协议密钥交换/Signal协议密钥交换.md)
  - Signal协议概述
  - X3DH密钥交换
  - Double Ratchet算法

### [08. 国密SM2密钥交换](./08_国密SM2密钥交换/国密SM2密钥交换.md)
  - SM2密钥交换协议
  - SM2密钥交换实现

### [09. 组密钥交换协议](./09_组密钥交换协议/组密钥交换协议.md)
  - 组密钥交换概述
  - Burmester-Desmedt协议
  - 树形组密钥管理

### [10. 量子密钥分发（QKD）](./10_量子密钥分发（QKD）/量子密钥分发（QKD）.md)
  - QKD概述
  - BB84协议
  - QKD实际应用

### [11. 后量子密钥交换](./11_后量子密钥交换/后量子密钥交换.md)
  - 量子计算对密钥交换的威胁
  - 格基密钥交换
  - 混合密钥交换

### [12. 密钥交换安全分析](./12_密钥交换安全分析/密钥交换安全分析.md)
  - 常见攻击类型
  - 安全模型

### [13. 密钥交换实践应用](./13_密钥交换实践应用/密钥交换实践应用.md)
  - SSH密钥交换
  - IPsec IKE密钥交换
  - WireGuard密钥交换
  - 国密VPN密钥交换

### [14. 总结与最佳实践](./14_总结与最佳实践/总结与最佳实践.md)
  - 密钥交换算法选择
  - 最佳实践
  - 常见错误
  - 参考标准

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **密钥交换概述**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Diffie-Hellman密钥交换**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **ECDH椭圆曲线密钥交换**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **认证密钥交换（AKE）**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **TLS密钥交换机制**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Signal协议密钥交换**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **国密SM2密钥交换**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **组密钥交换协议**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **量子密钥分发（QKD）**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **后量子密钥交换**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **密钥交换安全分析**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **密钥交换实践应用**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **总结与最佳实践**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
