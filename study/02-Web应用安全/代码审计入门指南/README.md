# 代码审计入门指南

> 本文档整理自：`代码审计入门指南.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 代码审计概述](./02_代码审计概述/代码审计概述.md)
  - 白盒测试 vs 黑盒测试
  - 代码审计方法论
  - 代码审计流程
  - 常用代码审计工具

### [03. PHP 代码审计](./03_PHP 代码审计/PHP 代码审计.md)
  - 危险函数速查
  - 文件操作漏洞审计
  - SQL 注入审计
  - 反序列化漏洞审计
  - PHP 框架审计要点
  - PHP 配置安全
  - 审计实战：模拟审计简化 CMS

### [04. Java 代码审计](./04_Java 代码审计/Java 代码审计.md)
  - Java Web 应用架构理解
  - SQL 注入审计
  - 命令注入审计
  - 反序列化漏洞审计
  - SSRF 审计
  - 表达式注入审计
  - 文件上传审计
  - Java 框架审计要点
  - 审计实战：模拟审计 Spring Boot 应用

### [05. Python 代码审计](./05_Python 代码审计/Python 代码审计.md)
  - Flask / Django 审计要点
  - 模板注入审计
  - SQL 注入审计
  - 反序列化审计
  - 命令注入审计
  - 审计实战：模拟审计 Flask 应用

### [06. 自动化代码审计](./06_自动化代码审计/自动化代码审计.md)
  - Semgrep 规则编写
  - CodeQL 查询编写
  - SonarQube 自定义规则
  - Python 简单 AST 审计脚本

### [07. 代码审计报告撰写](./07_代码审计报告撰写/代码审计报告撰写.md)
  - 漏洞描述模板
  - 风险评级标准（CVSS v3.1）
  - 修复建议撰写规范
  - 报告结构模板

### [08. 审计概述](./08_审计概述/审计概述.md)

### [09. 审计结论](./09_审计结论/审计结论.md)

### [10. 漏洞详情](./10_漏洞详情/漏洞详情.md)
  - [严重] SQL 注入 - 用户查询接口
  - [高危] ...

### [11. 安全加固建议](./11_安全加固建议/安全加固建议.md)

### [12. 附录](./12_附录/附录.md)

### [13. 总结](./13_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **目录**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **代码审计概述**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **PHP 代码审计**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：references
- **Java 代码审计**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：references
- **Python 代码审计**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：references
- **自动化代码审计**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **代码审计报告撰写**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **审计概述**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **审计结论**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **漏洞详情**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：short
  - 缺少：references
- **安全加固建议**：⚠️ 需补充 9 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **附录**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **总结**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
