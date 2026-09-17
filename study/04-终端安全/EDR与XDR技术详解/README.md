# EDR与XDR技术详解

> 本文档整理自：`EDR与XDR技术详解.md`

---

## 目录

### [01. EDR 架构原理](./01_EDR 架构原理/EDR 架构原理.md)
  - 什么是 EDR
  - EDR 系统架构
  - EDR 四层架构详解

### [02. EDR 数据采集技术](./02_EDR 数据采集技术/EDR 数据采集技术.md)
  - ETW（Event Tracing for Windows）
  - 内核回调
  - 文件系统过滤驱动
  - 网络过滤

### [03. EDR 检测技术](./03_EDR 检测技术/EDR 检测技术.md)
  - 特征检测
  - 行为检测
  - 机器学习检测
  - 关联分析

### [04. EDR 响应能力](./04_EDR 响应能力/EDR 响应能力.md)
  - 隔离（Isolation）
  - 终止与回滚

### [05. XDR 概念与架构](./05_XDR 概念与架构/XDR 概念与架构.md)
  - 什么是 XDR
  - XDR 核心能力
  - XDR vs EDR vs SIEM

### [06. 主流 EDR 产品分析](./06_主流 EDR 产品分析/主流 EDR 产品分析.md)
  - 产品对比
  - CrowdStrike Falcon
  - Microsoft Defender for Endpoint

### [07. EDR 绕过技术](./07_EDR 绕过技术/EDR 绕过技术.md)
  - 直接系统调用（Direct Syscalls）
  - AMSI 绕过
  - ETW 绕过
  - 进程注入检测绕过

### [08. EDR 部署与运营最佳实践](./08_EDR 部署与运营最佳实践/EDR 部署与运营最佳实践.md)
  - 部署策略
  - 规则调优
  - 威胁狩猎（Threat Hunting）
  - EDR vs EDR 攻防对抗

---

## 📊 内容审核总览

- 总章节数：8
- 待完善章节：8

### 各章节审核状态
- **EDR 架构原理**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **EDR 数据采集技术**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **EDR 检测技术**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **EDR 响应能力**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **XDR 概念与架构**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **主流 EDR 产品分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **EDR 绕过技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **EDR 部署与运营最佳实践**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
