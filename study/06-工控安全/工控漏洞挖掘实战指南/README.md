# 工控漏洞挖掘实战指南

> 本文档整理自：`工控漏洞挖掘实战指南.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 工控系统漏洞挖掘概述](./02_工控系统漏洞挖掘概述/工控系统漏洞挖掘概述.md)
  - 工控系统与IT系统的差异
  - 漏洞挖掘的核心挑战
  - 漏洞挖掘方法论

### [03. 工控固件逆向工程](./03_工控固件逆向工程/工控固件逆向工程.md)
  - 固件获取方法
  - 固件解包与文件系统提取
  - 使用Ghidra进行固件逆向
  - 固件中的凭据提取

### [04. 协议模糊测试](./04_协议模糊测试/协议模糊测试.md)
  - 模糊测试概述
  - Modbus协议模糊测试
  - S7协议模糊测试
  - DNP3协议模糊测试

### [05. 漏洞验证方法](./05_漏洞验证方法/漏洞验证方法.md)
  - 漏洞验证原则
  - 缓冲区溢出验证
  - 未授权访问验证

### [06. 常见ICS CVE深度分析](./06_常见ICS CVE深度分析/常见ICS CVE深度分析.md)
  - CVE-2021-3564 - Siemens S7 PLC权限提升
  - CVE-2020-7516 - Schneider Electric Modicon M580
  - CVE-2019-16880 - Rockwell Automation CompactLogix
  - CVE-2020-6964 - Moxa MGate
  - ICS-CERT漏洞数据库利用

### [07. 漏洞挖掘工具详解](./07_漏洞挖掘工具详解/漏洞挖掘工具详解.md)
  - AFL (American Fuzzy Lop)
  - Peach Fuzzer
  - ScadaBR
  - 工控专用工具

### [08. 实战实验室搭建](./08_实战实验室搭建/实战实验室搭建.md)
  - 基于OpenPLC的模拟环境
  - Modbus测试环境
  - 网络拓扑设计
  - Wireshark自定义协议解析器

### [09. 漏洞报告编写与披露](./09_漏洞报告编写与披露/漏洞报告编写与披露.md)
  - 漏洞报告模板

### [10. 基本信息](./10_基本信息/基本信息.md)

### [11. 受影响产品](./11_受影响产品/受影响产品.md)

### [12. 漏洞描述](./12_漏洞描述/漏洞描述.md)

### [13. 技术细节](./13_技术细节/技术细节.md)
  - 漏洞原理
  - 复现步骤
  - PoC代码
  - 影响评估

### [14. 修复建议](./14_修复建议/修复建议.md)

### [15. 时间线](./15_时间线/时间线.md)
  - 负责任披露流程

### [16. 法律合规与伦理准则](./16_法律合规与伦理准则/法律合规与伦理准则.md)
  - 法律框架
  - 伦理准则

### [17. 参考资料与扩展阅读](./17_参考资料与扩展阅读/参考资料与扩展阅读.md)
  - 标准与框架
  - 推荐工具
  - 推荐阅读
  - 在线资源

---

## 📊 内容审核总览

- 总章节数：17
- 待完善章节：17

### 各章节审核状态
- **目录**：⚠️ 需补充 3 项
  - 缺少：code
  - 缺少：commands
  - 缺少：defense
- **工控系统漏洞挖掘概述**：⚠️ 需补充 1 项
  - 缺少：tools
- **工控固件逆向工程**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **协议模糊测试**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
- **漏洞验证方法**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **常见ICS CVE深度分析**：⚠️ 需补充 2 项
  - 缺少：knowledge
  - 缺少：practice
- **漏洞挖掘工具详解**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战实验室搭建**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **漏洞报告编写与披露**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **基本信息**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **受影响产品**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **漏洞描述**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **技术细节**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **修复建议**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **时间线**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **法律合规与伦理准则**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **参考资料与扩展阅读**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
