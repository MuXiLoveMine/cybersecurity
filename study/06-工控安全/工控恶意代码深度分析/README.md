# 工控恶意代码深度分析

> 本文档整理自：`工控恶意代码深度分析.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 工控恶意代码概述](./02_工控恶意代码概述/工控恶意代码概述.md)
  - 工控恶意代码的发展历程
  - 工控恶意代码与传统恶意代码的差异
  - 工控恶意代码分类

### [03. Stuxnet深度分析](./03_Stuxnet深度分析/Stuxnet深度分析.md)
  - 概述
  - 攻击链详细分析
  - 关键技术分析
  - 攻击效果评估
  - Stuxnet代码结构

### [04. Duqu分析](./04_Duqu分析/Duqu分析.md)
  - 概述
  - 技术特征
  - Duqu与Stuxnet对比

### [05. Flame分析](./05_Flame分析/Flame分析.md)
  - 概述
  - 技术特征
  - 独特的C2机制

### [06. Havex分析](./06_Havex分析/Havex分析.md)
  - 概述
  - OPC数据枚举

### [07. BlackEnergy分析](./07_BlackEnergy分析/BlackEnergy分析.md)
  - 概述
  - 乌克兰电网攻击详细分析
  - BlackEnergy 3技术分析

### [08. Industroyer (CrashOverride) 分析](./08_Industroyer (CrashOverride) 分析/Industroyer (CrashOverride) 分析.md)
  - 概述
  - 攻击架构
  - 工控协议攻击实现

### [09. Triton (TRITON) 分析](./09_Triton (TRITON) 分析/Triton (TRITON) 分析.md)
  - 概述
  - 攻击架构
  - TriStation协议逆向

### [10. 工控恶意代码检测方法](./10_工控恶意代码检测方法/工控恶意代码检测方法.md)
  - 网络流量检测
  - 主机行为检测

### [11. ICS专属IOC指标](./11_ICS专属IOC指标/ICS专属IOC指标.md)
  - 文件IOC
  - 网络IOC
  - 注册表IOC

### [12. 防御与缓解策略](./12_防御与缓解策略/防御与缓解策略.md)
  - 防御框架
  - Snort/Suricata检测规则
  - 加固检查清单

### [13. 参考资料](./13_参考资料/参考资料.md)
  - 技术分析报告
  - 在线资源
  - 推荐阅读

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
- **工控恶意代码概述**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **Stuxnet深度分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Duqu分析**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Flame分析**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Havex分析**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **BlackEnergy分析**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Industroyer (CrashOverride) 分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Triton (TRITON) 分析**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **工控恶意代码检测方法**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **ICS专属IOC指标**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **防御与缓解策略**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **参考资料**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
