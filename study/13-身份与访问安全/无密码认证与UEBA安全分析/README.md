# 无密码认证与UEBA安全分析

> 本文档整理自：`无密码认证与UEBA安全分析.md`

---

## 目录

### [01. 无密码认证概述](./01_无密码认证概述/无密码认证概述.md)
  - 传统密码的缺陷
  - 无密码认证趋势

### [02. FIDO2/WebAuthn 标准详解](./02_FIDO2_WebAuthn 标准详解/FIDO2_WebAuthn 标准详解.md)
  - FIDO2 技术架构
  - WebAuthn API 工作原理
  - 公钥挑战-响应认证流程
  - 设备绑定认证器 vs 漫游认证器
  - 多设备凭据管理

### [03. Passkey 技术](./03_Passkey 技术/Passkey 技术.md)
  - Passkey 概念
  - Apple Passkey 实现
  - Google Passkey 实现
  - Microsoft Passkey 实现
  - 跨平台 Passkey 互操作

### [04. FIDO2 安全分析](./04_FIDO2 安全分析/FIDO2 安全分析.md)
  - 抗钓鱼原理
  - 蓝牙跨设备认证安全
  - 中继攻击风险

### [05. FIDO2 部署实践](./05_FIDO2 部署实践/FIDO2 部署实践.md)
  - 服务端实现
  - 用户体验设计
  - 备份与恢复

### [06. UEBA 概述](./06_UEBA 概述/UEBA 概述.md)
  - 用户与实体行为分析概念
  - UEBA 与 SIEM/EDR 的关系

### [07. UEBA 技术架构](./07_UEBA 技术架构/UEBA 技术架构.md)
  - 整体架构
  - 数据采集
  - 行为基线
  - 异常检测
  - 风险评估与告警

### [08. UEBA 行为模型](./08_UEBA 行为模型/UEBA 行为模型.md)
  - 登录行为模型
  - 文件访问行为模型
  - 网络行为模型
  - 特权行为模型

### [09. UEBA 检测场景](./09_UEBA 检测场景/UEBA 检测场景.md)
  - 异常登录时间检测
  - 异常地理位置检测
  - 异常数据访问检测
  - 横向移动行为检测

### [10. UEBA 与 SIEM/EDR 集成](./10_UEBA 与 SIEM_EDR 集成/UEBA 与 SIEM_EDR 集成.md)
  - 集成架构
  - 集成实现示例

### [11. 主流 UEBA 产品对比](./11_主流 UEBA 产品对比/主流 UEBA 产品对比.md)

### [12. 实战案例：UEBA 检测内部威胁](./12_实战案例：UEBA 检测内部威胁/实战案例：UEBA 检测内部威胁.md)
  - 场景背景
  - UEBA 检测过程
  - 案例分析与改进

### [13. 总结与最佳实践](./13_总结与最佳实践/总结与最佳实践.md)
  - 无密码认证最佳实践
  - UEBA 最佳实践
  - 学习建议

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **无密码认证概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **FIDO2/WebAuthn 标准详解**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Passkey 技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **FIDO2 安全分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **FIDO2 部署实践**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **UEBA 概述**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **UEBA 技术架构**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **UEBA 行为模型**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **UEBA 检测场景**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **UEBA 与 SIEM/EDR 集成**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **主流 UEBA 产品对比**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例：UEBA 检测内部威胁**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **总结与最佳实践**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：attack
  - 缺少：references
