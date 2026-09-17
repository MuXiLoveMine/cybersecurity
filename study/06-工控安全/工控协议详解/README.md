# 工控协议详解

> 本文档整理自：`工控协议详解.md`

---

## 目录

### [01. Modbus TCP/RTU 协议详解](./01_Modbus TCP_RTU 协议详解/Modbus TCP_RTU 协议详解.md)
  - Modbus 协议概述
  - Modbus 数据模型
  - Modbus RTU 帧格式
  - Modbus TCP 帧格式
  - 常用 Modbus 功能码
  - 异常响应
  - Modbus 安全风险

### [02. Siemens S7 协议分析](./02_Siemens S7 协议分析/Siemens S7 协议分析.md)
  - S7 协议概述
  - S7 协议栈结构
  - ISO-on-TCP (RFC1006) 头
  - COTP 头
  - S7 PDU 结构
  - 常用 S7 功能（Function Code）
  - S7 通信流程示例
  - 读取数据块（Read Var）详解
  - S7 协议安全风险

### [03. DNP3 协议](./03_DNP3 协议/DNP3 协议.md)
  - DNP3 协议概述
  - DNP3 帧结构
  - DNP3 功能码
  - DNP3 数据对象
  - DNP3 安全机制
  - DNP3 安全风险

### [04. IEC 60870-5-104 协议](./04_IEC 60870-5-104 协议/IEC 60870-5-104 协议.md)
  - IEC 104 概述
  - IEC 104 协议栈
  - APCI（应用规约控制信息）
  - ASDU（应用服务数据单元）
  - IEC 104 通信流程
  - IEC 104 安全风险

### [05. OPC UA 协议](./05_OPC UA 协议/OPC UA 协议.md)
  - OPC UA 概述
  - OPC UA 架构
  - OPC UA 安全模型
  - OPC UA 地址空间模型
  - OPC UA 服务
  - OPC UA 安全风险

### [06. 协议抓包与分析方法](./06_协议抓包与分析方法/协议抓包与分析方法.md)
  - Wireshark 抓包分析
  - Scapy 协议分析
  - 协议逆向分析方法

### [07. 协议漏洞与安全风险](./07_协议漏洞与安全风险/协议漏洞与安全风险.md)
  - 工控协议漏洞分类
  - 常见协议漏洞列表
  - 协议攻击方法

### [08. 实践建议](./08_实践建议/实践建议.md)
  - 学习路径
  - 实践环境
  - 安全提示

---

## 📊 内容审核总览

- 总章节数：8
- 待完善章节：8

### 各章节审核状态
- **Modbus TCP/RTU 协议详解**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Siemens S7 协议分析**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
- **DNP3 协议**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **IEC 60870-5-104 协议**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **OPC UA 协议**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
- **协议抓包与分析方法**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **协议漏洞与安全风险**：⚠️ 需补充 2 项
  - 缺少：defense
  - 缺少：references
- **实践建议**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
