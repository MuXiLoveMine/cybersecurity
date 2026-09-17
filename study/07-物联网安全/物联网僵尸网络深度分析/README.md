# 物联网僵尸网络深度分析

> 本文档整理自：`物联网僵尸网络深度分析.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 概述](./02_概述/概述.md)
  - IoT僵尸网络特征
  - 威胁影响

### [03. IoT僵尸网络演进史](./03_IoT僵尸网络演进史/IoT僵尸网络演进史.md)
  - 第一代：简单扫描感染（2013-2015）
  - 第二代：高效传播（2016）
  - 第三代：漏洞利用蠕虫（2017-2018）
  - 第四代：P2P去中心化（2019-至今）
  - 第五代：智能自动化（2020-至今）

### [04. Mirai架构深度剖析](./04_Mirai架构深度剖析/Mirai架构深度剖析.md)
  - 整体架构
  - CNC服务器（C2通信与控制）
  - 扫描器（Scanner）
  - Loader（注入器）
  - Bot端程序
  - Mirai攻击命令格式

### [05. Hajime隐蔽僵尸网络](./05_Hajime隐蔽僵尸网络/Hajime隐蔽僵尸网络.md)
  - 概述
  - Hajime技术特征
  - Hajime的争议性

### [06. BrickerBot破坏型僵尸网络](./06_BrickerBot破坏型僵尸网络/BrickerBot破坏型僵尸网络.md)
  - PDoS攻击概念
  - BrickerBot破坏手法
  - BrickerBot的影响

### [07. Reaper物联网蠕虫](./07_Reaper物联网蠕虫/Reaper物联网蠕虫.md)
  - Reaper概述
  - Reaper利用的漏洞列表
  - Reaper蠕虫传播机制

### [08. Mozi P2P僵尸网络](./08_Mozi P2P僵尸网络/Mozi P2P僵尸网络.md)
  - Mozi概述
  - Mozi架构
  - Mozi的P2P通信机制
  - Mozi持久化机制

### [09. C2通信协议分析](./09_C2通信协议分析/C2通信协议分析.md)
  - IoT僵尸网络常见C2协议
  - Mirai C2协议解析
  - C2流量特征检测

### [10. DDoS攻击技术详解](./10_DDoS攻击技术详解/DDoS攻击技术详解.md)
  - IoT僵尸网络DDoS攻击类型
  - 放大攻击
  - 应用层攻击

### [11. 检测与防御策略](./11_检测与防御策略/检测与防御策略.md)
  - 网络层检测
  - 设备层防御
  - ISP级防御

### [12. 实战案例分析](./12_实战案例分析/实战案例分析.md)
  - 2016 Dyn攻击事件
  - 2018年PyMine分析案例
  - Mozi僵尸网络取证分析

### [13. 未来趋势与应对](./13_未来趋势与应对/未来趋势与应对.md)
  - IoT僵尸网络演进趋势
  - 防御体系建设
  - 安全标准与法规

### [14. 总结](./14_总结/总结.md)

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
- **概述**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **IoT僵尸网络演进史**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Mirai架构深度剖析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Hajime隐蔽僵尸网络**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **BrickerBot破坏型僵尸网络**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Reaper物联网蠕虫**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
- **Mozi P2P僵尸网络**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **C2通信协议分析**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **DDoS攻击技术详解**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **检测与防御策略**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **实战案例分析**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **未来趋势与应对**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **总结**：⚠️ 需补充 2 项
  - 缺少：commands
  - 缺少：references
