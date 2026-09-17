# 密钥管理

> 本文档整理自：`密钥管理.md`

---

## 目录

### [01. 密钥管理概述](./01_密钥管理概述/密钥管理概述.md)
  - 什么是密钥管理
  - 密钥管理的目标
  - 密钥管理原则
  - 密钥管理标准和法规

### [02. 密钥生命周期](./02_密钥生命周期/密钥生命周期.md)
  - 生命周期总览
  - 密钥生成
  - 密钥分发
  - 密钥存储
  - 密钥使用
  - 密钥轮换
  - 密钥归档
  - 密钥销毁

### [03. 密钥分级](./03_密钥分级/密钥分级.md)
  - 为什么需要密钥分级
  - 密钥分层模型
  - 各层密钥详解
  - 密钥分层的优势

### [04. 密钥存储技术](./04_密钥存储技术/密钥存储技术.md)
  - 硬件安全模块（HSM）
  - 密钥管理系统（KMS）
  - 可信平台模块（TPM）
  - 智能卡 / USB Key
  - 软件密钥存储

### [05. 密钥分发协议](./05_密钥分发协议/密钥分发协议.md)
  - 密钥分发的需求
  - 密钥分发中心（KDC）
  - 公钥加密分发
  - Diffie-Hellman 密钥交换
  - 预共享密钥（PSK）

### [06. 密钥轮换策略](./06_密钥轮换策略/密钥轮换策略.md)
  - 轮换策略设计
  - 轮换方式
  - 无缝轮换实现
  - 轮换后的旧密钥处理
  - 轮换的审计与验证

### [07. PKI 体系](./07_PKI 体系/PKI 体系.md)
  - PKI 概述
  - PKI 组成
  - 数字证书
  - 证书生命周期
  - 根证书信任
  - 证书透明性（Certificate Transparency）

### [08. 密钥管理的常见问题与最佳实践](./08_密钥管理的常见问题与最佳实践/密钥管理的常见问题与最佳实践.md)
  - 常见错误
  - 最佳实践总结
  - 关键指标（KPI）

### [09. 实际案例](./09_实际案例/实际案例.md)
  - 案例 1：Code Spaces 被黑客删除所有数据
  - 案例 2：Uber 数据泄露（2016）
  - 案例 3：DigiNotar CA 被黑

### [10. 学习与实践建议](./10_学习与实践建议/学习与实践建议.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **密钥管理概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **密钥生命周期**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **密钥分级**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **密钥存储技术**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **密钥分发协议**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **密钥轮换策略**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **PKI 体系**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **密钥管理的常见问题与最佳实践**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：attack
  - 缺少：references
- **实际案例**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **学习与实践建议**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
