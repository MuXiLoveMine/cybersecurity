# API安全完整指南

> 本文档整理自：`API安全完整指南.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. API安全概述](./02_API安全概述/API安全概述.md)
  - API安全重要性
  - RESTful API vs GraphQL vs gRPC 安全考量
  - API安全生命周期

### [03. OWASP API Security Top 10 (2023) 详解](./03_OWASP API Security Top 10 (2023) 详解/OWASP API Security Top 10 (2023) 详解.md)
  - API1: Broken Object Level Authorization (BOLA) / IDOR
  - API2: Broken Authentication
  - API3: Broken Object Property Level Authorization
  - API4: Unrestricted Resource Consumption
  - API5: Broken Function Level Authorization (BFLA)
  - API6: Unrestricted Access to Sensitive Business Flows
  - API7: SSRF (Server-Side Request Forgery)
  - API8: Security Misconfiguration
  - API9: Improper Inventory Management
  - API10: Unsafe Consumption of APIs

### [04. REST API安全实战](./04_REST API安全实战/REST API安全实战.md)
  - 认证方案对比
  - 授权与访问控制
  - 输入验证与输出编码
  - 速率限制与配额管理
  - API版本管理与废弃

### [05. GraphQL安全](./05_GraphQL安全/GraphQL安全.md)
  - 内省攻击与防护
  - 批量查询攻击
  - 深度嵌套攻击
  - GraphQL认证与授权

### [06. API安全测试](./06_API安全测试/API安全测试.md)
  - Postman/Newman API安全测试
  - Burp Suite API测试
  - 自动化API安全扫描工具
  - API模糊测试

### [07. API网关与WAF](./07_API网关与WAF/API网关与WAF.md)
  - API网关安全功能
  - API WAF规则配置
  - API监控与异常检测

### [08. Python API安全测试脚本示例](./08_Python API安全测试脚本示例/Python API安全测试脚本示例.md)
  - JWT安全检测脚本
  - API端点枚举脚本
  - BOLA漏洞检测脚本

### [09. 总结](./09_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：9
- 待完善章节：9

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **API安全概述**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **OWASP API Security Top 10 (2023) 详解**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **REST API安全实战**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **GraphQL安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **API安全测试**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **API网关与WAF**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **Python API安全测试脚本示例**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **总结**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
