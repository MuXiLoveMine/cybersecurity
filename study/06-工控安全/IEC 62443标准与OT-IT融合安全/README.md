# IEC 62443标准与OT-IT融合安全

> 本文档整理自：`IEC 62443标准与OT-IT融合安全.md`

---

## 目录

### [01. IEC 62443 标准体系概述](./01_IEC 62443 标准体系概述/IEC 62443 标准体系概述.md)
  - 标准的由来与定位
  - 标准系列总览
  - 三层责任主体

### [02. IEC 62443 安全等级（SL1-SL4）](./02_IEC 62443 安全等级（SL1-SL4）/IEC 62443 安全等级（SL1-SL4）.md)
  - 安全等级定义
  - SL 目标（SL-T）与 SL 能力（SL-C）
  - SL 等级选择的影响

### [03. 区域和管道模型（Zones and Conduits）](./03_区域和管道模型（Zones and Conduits）/区域和管道模型（Zones and Conduits）.md)
  - 模型核心思想
  - 区域划分方法（依据 62443-3-2）
  - 区域划分示例图
  - 管道安全要求

### [04. 工控安全要求详解](./04_工控安全要求详解/工控安全要求详解.md)
  - 系统安全要求（62443-3-3）
  - 技术安全要求（62443-4-2）
  - 策略与程序要求（62443-2-1）

### [05. OT 与 IT 融合安全挑战](./05_OT 与 IT 融合安全挑战/OT 与 IT 融合安全挑战.md)
  - 三大差异模型对比
  - 文化差异
  - 协议差异
  - 安全模型差异

### [06. OT-IT 融合安全架构](./06_OT-IT 融合安全架构/OT-IT 融合安全架构.md)
  - 典型融合架构（基于 Purdue 模型 + DMZ）
  - DMZ 部署要点
  - 单向网闸（Data Diode）
  - OPC UA 网关

### [07. 功能安全与信息安全的融合](./07_功能安全与信息安全的融合/功能安全与信息安全的融合.md)
  - IEC 61508 与 SIL 等级
  - SIL 与 SL 的关系
  - 安全功能与网络安全的隔离原则
  - 协同安全分析示例

### [08. 工控网络分段与微隔离](./08_工控网络分段与微隔离/工控网络分段与微隔离.md)
  - 宏观分段（Zone 级）
  - 微隔离（Micro-segmentation）
  - 工控协议 DPI 配置示例

### [09. 工控安全管理生命周期](./09_工控安全管理生命周期/工控安全管理生命周期.md)
  - 生命周期阶段
  - 关键阶段要求
  - 变更管理流程示例

### [10. 实战案例：IEC 62443 在工业企业的落地实践](./10_实战案例：IEC 62443 在工业企业的落地实践/实战案例：IEC 62443 在工业企业的落地实践.md)
  - 案例背景
  - 落地阶段与里程碑
  - 关键实践要点
  - 经验教训总结
  - 安全基线配置片段（工业防火墙）

### [11. 学习建议与参考资料](./11_学习建议与参考资料/学习建议与参考资料.md)
  - 学习路径建议
  - 关键参考资料
  - 实践清单

### [12. 总结](./12_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：12
- 待完善章节：12

### 各章节审核状态
- **IEC 62443 标准体系概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **IEC 62443 安全等级（SL1-SL4）**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **区域和管道模型（Zones and Conduits）**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **工控安全要求详解**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **OT 与 IT 融合安全挑战**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **OT-IT 融合安全架构**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **功能安全与信息安全的融合**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **工控网络分段与微隔离**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **工控安全管理生命周期**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
- **实战案例：IEC 62443 在工业企业的落地实践**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **学习建议与参考资料**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
- **总结**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
