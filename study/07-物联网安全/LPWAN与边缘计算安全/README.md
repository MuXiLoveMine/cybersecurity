# LPWAN与边缘计算安全

> 本文档整理自：`LPWAN与边缘计算安全.md`

---

## 目录

### [01. LPWAN 技术概述](./01_LPWAN 技术概述/LPWAN 技术概述.md)
  - LPWAN 定义与特点
  - LPWAN 分类

### [02. LoRaWAN 安全机制](./02_LoRaWAN 安全机制/LoRaWAN 安全机制.md)
  - LoRaWAN 协议栈与安全层位置
  - 密钥体系
  - OTAA 与 ABP 入网方式
  - 加密与完整性机制

### [03. LoRaWAN 攻击面](./03_LoRaWAN 攻击面/LoRaWAN 攻击面.md)
  - 重放攻击（Replay）
  - 确认伪造（ACK Spoofing）
  - Jamming 攻击
  - 设备克隆（Device Cloning）
  - 旁路攻击与密钥提取

### [04. NB-IoT 安全机制](./04_NB-IoT 安全机制/NB-IoT 安全机制.md)
  - NB-IoT 与蜂窝安全继承
  - EPS-AKA 认证流程
  - 密钥层级
  - NB-IoT 安全风险

### [05. Sigfox 安全机制分析](./05_Sigfox 安全机制分析/Sigfox 安全机制分析.md)
  - Sigfox 安全模型
  - 安全局限性
  - 应用层加固建议

### [06. LoRaWAN 安全测试方法与工具](./06_LoRaWAN 安全测试方法与工具/LoRaWAN 安全测试方法与工具.md)
  - 测试方法学
  - 常用工具
  - 射频抓包与解码示例
  - 协议模糊测试框架

### [07. 边缘计算安全概述](./07_边缘计算安全概述/边缘计算安全概述.md)
  - 边缘计算架构
  - 边缘安全的三大层面
  - 边缘计算安全特点（与云对比）

### [08. 边缘设备安全](./08_边缘设备安全/边缘设备安全.md)
  - 硬件安全
  - 固件安全
  - 容器安全（边缘节点）

### [09. 边缘 AI 安全](./09_边缘 AI 安全/边缘 AI 安全.md)
  - 边缘 AI 威胁模型
  - 模型保护
  - 推理安全
  - 推理数据隐私

### [10. 边缘计算与云计算协同安全](./10_边缘计算与云计算协同安全/边缘计算与云计算协同安全.md)
  - 边云协同通道安全
  - 零信任与边缘接入
  - 边云数据一致性安全
  - 边云协同的常见攻击与防御

### [11. 安全最佳实践](./11_安全最佳实践/安全最佳实践.md)
  - LPWAN 安全清单
  - 边缘计算安全清单
  - 监测与响应基线
  - 应急响应要点

### [12. 学习建议与参考资料](./12_学习建议与参考资料/学习建议与参考资料.md)
  - 学习路径建议
  - 关键参考资料
  - 实践清单

### [13. 总结](./13_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **LPWAN 技术概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **LoRaWAN 安全机制**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **LoRaWAN 攻击面**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **NB-IoT 安全机制**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Sigfox 安全机制分析**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **LoRaWAN 安全测试方法与工具**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **边缘计算安全概述**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **边缘设备安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **边缘 AI 安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **边缘计算与云计算协同安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **安全最佳实践**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **学习建议与参考资料**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：attack
- **总结**：⚠️ 需补充 3 项
  - 缺少：code
  - 缺少：tools
  - 缺少：references
