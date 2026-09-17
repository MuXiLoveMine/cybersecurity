# 车载诊断协议安全与ISO21434

> 本文档整理自：`车载诊断协议安全与ISO21434.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. UDS 诊断协议安全](./02_UDS 诊断协议安全/UDS 诊断协议安全.md)
  - ISO 14229 UDS 协议架构
  - 诊断服务总览
  - 诊断会话模式
  - 安全访问机制（SecurityAccess, 0x27）

### [03. UDS 安全漏洞分析](./03_UDS 安全漏洞分析/UDS 安全漏洞分析.md)
  - SecurityAccess 绕过
  - 诊断会话劫持
  - 固件刷写攻击

### [04. DoIP 诊断协议安全](./04_DoIP 诊断协议安全/DoIP 诊断协议安全.md)
  - ISO 13400 DoIP 协议概述
  - 车辆发现机制
  - DoIP 安全风险与防护

### [05. SOME/IP 协议安全](./05_SOME_IP 协议安全/SOME_IP 协议安全.md)
  - SOME/IP 协议概述
  - 服务发现安全
  - Payload 安全

### [06. 车载网关安全](./06_车载网关安全/车载网关安全.md)
  - 中央网关架构
  - 路由规则
  - 网关防火墙

### [07. 车载 IDS/IPS](./07_车载 IDS_IPS/车载 IDS_IPS.md)
  - 入侵检测部署位置
  - 检测规则
  - 异常行为识别

### [08. ISO 21434 标准详解](./08_ISO 21434 标准详解/ISO 21434 标准详解.md)
  - 标准概述
  - 网络安全管理（CSMS）
  - 网络安全风险评估（TARA）
  - 网络安全目标与声明
  - 网络安全验证
  - 持续运维与事件响应

### [09. 功能安全与信息安全融合](./09_功能安全与信息安全融合/功能安全与信息安全融合.md)
  - ISO 26262 与 ISO 21434 的关系
  - 融合实践要点

### [10. 实战案例：汽车 ISO 21434 合规实践](./10_实战案例：汽车 ISO 21434 合规实践/实战案例：汽车 ISO 21434 合规实践.md)
  - 案例背景
  - 概念阶段：TARA 实践
  - 开发阶段：安全需求与实现
  - 验证阶段：渗透测试
  - 合规文档体系

### [11. 总结与学习路线](./11_总结与学习路线/总结与学习路线.md)
  - 知识体系总结
  - 学习路线建议
  - 关键要点速查

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **UDS 诊断协议安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **UDS 安全漏洞分析**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **DoIP 诊断协议安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **SOME/IP 协议安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **车载网关安全**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **车载 IDS/IPS**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **ISO 21434 标准详解**：⚠️ 需补充 2 项
  - 缺少：commands
  - 缺少：practice
- **功能安全与信息安全融合**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例：汽车 ISO 21434 合规实践**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **总结与学习路线**：⚠️ 需补充 1 项
  - 缺少：commands
