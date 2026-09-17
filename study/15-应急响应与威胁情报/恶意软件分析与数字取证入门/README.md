# 恶意软件分析与数字取证入门

> 本文档整理自：`恶意软件分析与数字取证入门.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 恶意软件分类与特征](./02_恶意软件分类与特征/恶意软件分类与特征.md)
  - 恶意软件基本分类
  - 恶意软件命名规范
  - 常见恶意软件家族
  - 恶意软件传播途径

### [03. 静态分析技术](./03_静态分析技术/静态分析技术.md)
  - 静态分析概述
  - PE文件结构分析
  - 字符串提取与分析
  - 反汇编与反编译
  - 特征码识别
  - 加壳与脱壳

### [04. 动态分析技术](./04_动态分析技术/动态分析技术.md)
  - 动态分析环境搭建
  - 沙箱分析
  - API监控与Hook
  - 网络行为分析
  - 注册表与文件系统监控

### [05. 行为分析与威胁狩猎](./05_行为分析与威胁狩猎/行为分析与威胁狩猎.md)
  - 行为分析方法论
  - 攻击指标提取
  - 杀伤链映射
  - MITRE ATT&CK框架应用

### [06. 数字取证流程](./06_数字取证流程/数字取证流程.md)
  - 取证原则与规范
  - 取证流程详解
  - 证据保全与链式监管
  - 取证报告撰写

### [07. 文档信息](./07_文档信息/文档信息.md)

### [08. 执行摘要](./08_执行摘要/执行摘要.md)

### [09. 事件背景](./09_事件背景/事件背景.md)
  - 事件概述
  - 影响范围
  - 涉及系统

### [10. 证据清单](./10_证据清单/证据清单.md)

### [11. 分析方法](./11_分析方法/分析方法.md)
  - 使用工具
  - 分析流程

### [12. 详细分析结果](./12_详细分析结果/详细分析结果.md)
  - 时间线分析
  - 恶意软件分析
  - 网络活动分析
  - 系统变更分析

### [13. 结论](./13_结论/结论.md)

### [14. 建议](./14_建议/建议.md)

### [15. 附录](./15_附录/附录.md)
  - A. 完整IOC列表
  - B. 工具输出日志
  - C. 证据链记录

### [16. 内存取证技术](./16_内存取证技术/内存取证技术.md)
  - 内存取证基础
  - Volatility框架详解
  - 内存证据提取与分析
  - 内存中的恶意代码检测

### [17. 取证工具详解](./17_取证工具详解/取证工具详解.md)
  - 磁盘取证工具
  - 网络取证工具
  - 综合取证平台
  - 开源取证工具集

### [18. 恶意软件分析自动化](./18_恶意软件分析自动化/恶意软件分析自动化.md)
  - 自动化分析管道
  - 沙箱自动化
  - YARA规则引擎
  - 机器学习辅助分析

### [19. 实际案例分析](./19_实际案例分析/实际案例分析.md)
  - 勒索软件分析案例
  - APT攻击取证案例
  - 无文件恶意软件分析

### [20. 总结与最佳实践](./20_总结与最佳实践/总结与最佳实践.md)
  - 恶意软件分析最佳实践
  - 数字取证最佳实践
  - 工具选择指南

---

## 📊 内容审核总览

- 总章节数：20
- 待完善章节：20

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **恶意软件分类与特征**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **静态分析技术**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
- **动态分析技术**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **行为分析与威胁狩猎**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **数字取证流程**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **文档信息**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **执行摘要**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **事件背景**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **证据清单**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **分析方法**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **详细分析结果**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **结论**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **建议**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **附录**：⚠️ 需补充 7 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **内存取证技术**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **取证工具详解**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **恶意软件分析自动化**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实际案例分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **总结与最佳实践**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
