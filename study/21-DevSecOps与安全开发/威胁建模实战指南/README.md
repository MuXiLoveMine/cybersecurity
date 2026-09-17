# 威胁建模实战指南

> 本文档整理自：`威胁建模实战指南.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 第1章 威胁建模概述](./02_第1章 威胁建模概述/第1章 威胁建模概述.md)
  - 什么是威胁建模
  - 威胁建模的价值与意义
  - 威胁建模在SSDLC中的位置
  - 威胁建模的时机与频率
  - 谁应该参与威胁建模

### [03. 第2章 威胁建模方法论](./03_第2章 威胁建模方法论/第2章 威胁建模方法论.md)
  - STRIDE方法详解
  - PASTA方法
  - OCTAVE方法
  - DREAD风险评估模型
  - 各方法对比与选择

### [04. 第3章 威胁建模完整流程](./04_第3章 威胁建模完整流程/第3章 威胁建模完整流程.md)
  - 第1步：明确安全目标
  - 第2步：系统图与架构图绘制
  - 第3步：威胁识别与枚举
  - 第4步：风险评估与排序
  - 第5步：缓解措施设计
  - 第6步：验证与迭代

### [05. 第4章 数据流图（DFD）绘制](./05_第4章 数据流图（DFD）绘制/第4章 数据流图（DFD）绘制.md)
  - DFD基本元素
  - 信任边界（Trust Boundary）
  - DFD层次结构
  - 绘制工具
  - 绘制最佳实践
  - 常见架构的DFD示例

### [06. 第5章 Microsoft Threat Modeling Tool使用](./06_第5章 Microsoft Threat Modeling Tool使用/第5章 Microsoft Threat Modeling Tool使用.md)
  - 工具介绍与安装
  - 创建威胁建模项目
  - 绘制系统架构图
  - 选择威胁模型（STRIDE）
  - 自动生成威胁报告
  - 缓解措施建议
  - 报告生成与导出
  - 团队协作与版本管理

### [07. 第6章 常见威胁与缓解措施速查](./07_第6章 常见威胁与缓解措施速查/第6章 常见威胁与缓解措施速查.md)
  - 身份认证相关威胁与缓解
  - 访问控制相关威胁与缓解
  - 输入验证相关威胁与缓解
  - 数据加密相关威胁与缓解
  - 会话管理相关威胁与缓解
  - 错误处理相关威胁与缓解
  - 日志审计相关威胁与缓解
  - 第三方组件相关威胁与缓解

### [08. 第7章 实战案例](./08_第7章 实战案例/第7章 实战案例.md)
  - 案例1：用户登录系统威胁建模
  - 案例2：电商支付系统威胁建模
  - 案例3：微服务架构威胁建模
  - 案例4：API网关威胁建模

### [09. 第8章 威胁建模在敏捷/DevOps中的应用](./09_第8章 威胁建模在敏捷_DevOps中的应用/第8章 威胁建模在敏捷_DevOps中的应用.md)
  - 敏捷开发中的威胁建模挑战
  - 轻量化威胁建模方法
  - 冲刺（Sprint）中的威胁建模
  - 自动化威胁建模工具
  - 威胁建模与CI/CD集成
  - 威胁即代码（Threat Modeling as Code）

### [10. 第9章 常见误区与最佳实践](./10_第9章 常见误区与最佳实践/第9章 常见误区与最佳实践.md)
  - 常见错误与陷阱
  - 最佳实践总结
  - 如何推动威胁建模落地
  - 度量指标与效果评估

### [11. 第10章 工具与资源](./11_第10章 工具与资源/第10章 工具与资源.md)
  - 威胁建模工具汇总
  - 威胁库与检查清单
  - 学习资源推荐
  - 模板与示例

### [12. 项目概述](./12_项目概述/项目概述.md)

### [13. 安全目标](./13_安全目标/安全目标.md)

### [14. 系统架构](./14_系统架构/系统架构.md)
  - 系统描述
  - 架构图/DFD图
  - 信任边界说明
  - 外部依赖

### [15. 威胁分析](./15_威胁分析/威胁分析.md)
  - 威胁识别
  - 风险评估
  - 威胁优先级排序

### [16. 缓解措施](./16_缓解措施/缓解措施.md)
  - 缓解措施清单
  - 残留风险评估

### [17. 验证计划](./17_验证计划/验证计划.md)

### [18. 附录](./18_附录/附录.md)

---

## 📊 内容审核总览

- 总章节数：18
- 待完善章节：18

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第1章 威胁建模概述**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **第2章 威胁建模方法论**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：defense
- **第3章 威胁建模完整流程**：⚠️ 需补充 1 项
  - 缺少：practice
- **第4章 数据流图（DFD）绘制**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **第5章 Microsoft Threat Modeling Tool使用**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **第6章 常见威胁与缓解措施速查**：⚠️ 需补充 2 项
  - 缺少：knowledge
  - 缺少：practice
- **第7章 实战案例**：⚠️ 需补充 1 项
  - 缺少：references
- **第8章 威胁建模在敏捷/DevOps中的应用**：⚠️ 需补充 2 项
  - 缺少：defense
  - 缺少：references
- **第9章 常见误区与最佳实践**：⚠️ 需补充 1 项
  - 缺少：commands
- **第10章 工具与资源**：⚠️ 需补充 2 项
  - 缺少：commands
  - 缺少：references
- **项目概述**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **安全目标**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **系统架构**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **威胁分析**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **缓解措施**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **验证计划**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **附录**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
