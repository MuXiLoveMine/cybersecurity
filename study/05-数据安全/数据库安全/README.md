# 数据库安全

> 本文档整理自：`数据库安全.md`

---

## 目录

### [01. 数据库安全概述](./01_数据库安全概述/数据库安全概述.md)
  - 数据库安全三大维度
  - 常见数据库安全威胁
  - 数据库安全法规要求

### [02. MySQL 安全](./02_MySQL 安全/MySQL 安全.md)
  - 安全加固清单
  - 权限管理
  - 审计日志
  - 数据加密（TDE）
  - 备份与恢复安全
  - MySQL 常见漏洞

### [03. PostgreSQL 安全](./03_PostgreSQL 安全/PostgreSQL 安全.md)
  - pg_hba.conf 认证配置
  - 角色与权限管理
  - 行级安全（RLS）
  - 审计（pgAudit）
  - 数据加密（pgcrypto）

### [04. MongoDB 安全](./04_MongoDB 安全/MongoDB 安全.md)
  - 认证配置
  - 授权（内置角色）
  - 网络安全
  - 加密
  - 常见安全问题

### [05. Redis 安全](./05_Redis 安全/Redis 安全.md)
  - 认证配置
  - 命令禁用
  - 网络隔离
  - 常见攻击

### [06. MSSQL 安全](./06_MSSQL 安全/MSSQL 安全.md)
  - 身份验证模式
  - 权限管理
  - TDE 加密
  - 审计（SQL Server Audit）
  - 常见漏洞

### [07. 数据库安全审计与扫描](./07_数据库安全审计与扫描/数据库安全审计与扫描.md)
  - 数据库漏洞扫描工具
  - 数据库审计系统
  - 敏感数据发现

### [08. 数据库防火墙](./08_数据库防火墙/数据库防火墙.md)
  - WAF vs 数据库防火墙
  - SQL 注入防护规则
  - 异常访问检测

### [09. Python 数据库安全检查脚本示例](./09_Python 数据库安全检查脚本示例/Python 数据库安全检查脚本示例.md)
  - MySQL 安全配置检查脚本
  - MongoDB 未授权访问检测脚本

### [10. 数据库加密技术](./10_数据库加密技术/数据库加密技术.md)
  - 透明数据加密(TDE)
  - 应用层加密与列级加密

### [11. 数据库安全基线检查](./11_数据库安全基线检查/数据库安全基线检查.md)
  - MySQL安全基线检查清单
  - PostgreSQL安全基线
  - SQL Server安全基线

### [12. NoSQL数据库安全](./12_NoSQL数据库安全/NoSQL数据库安全.md)
  - MongoDB安全加固
  - Redis安全加固
  - Elasticsearch安全加固

### [13. 数据库备份安全](./13_数据库备份安全/数据库备份安全.md)
  - 备份加密与验证
  - 备份策略与RPO

### [14. 数据库渗透测试方法](./14_数据库渗透测试方法/数据库渗透测试方法.md)
  - 数据库渗透测试流程
  - 数据库渗透测试工具
  - 数据库漏洞利用案例

### [15. 数据库安全审计最佳实践](./15_数据库安全审计最佳实践/数据库安全审计最佳实践.md)
  - 审计策略设计
  - 审计日志分析与告警

### [16. 总结](./16_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：16
- 待完善章节：16

### 各章节审核状态
- **数据库安全概述**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **MySQL 安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **PostgreSQL 安全**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **MongoDB 安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Redis 安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **MSSQL 安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **数据库安全审计与扫描**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **数据库防火墙**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Python 数据库安全检查脚本示例**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **数据库加密技术**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数据库安全基线检查**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **NoSQL数据库安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **数据库备份安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数据库渗透测试方法**：⚠️ 需补充 2 项
  - 缺少：knowledge
  - 缺少：references
- **数据库安全审计最佳实践**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **总结**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
