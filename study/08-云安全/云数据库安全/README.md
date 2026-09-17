# 云数据库安全

> 本文档整理自：`云数据库安全.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 云数据库安全概述](./02_云数据库安全概述/云数据库安全概述.md)
  - 云数据库类型
  - 共享责任模型
  - 云数据库安全威胁全景

### [03. 公网暴露风险](./03_公网暴露风险/公网暴露风险.md)
  - 暴露场景
  - 攻击手法
  - 检测与防御

### [04. 弱密码与认证安全](./04_弱密码与认证安全/弱密码与认证安全.md)
  - 弱密码风险
  - 认证加固

### [05. 存储加密](./05_存储加密/存储加密.md)
  - TDE透明数据加密
  - CMK客户管理密钥
  - 传输加密

### [06. 云上SQL注入](./06_云上SQL注入/云上SQL注入.md)
  - 注入风险场景
  - 防御措施

### [07. 备份安全](./07_备份安全/备份安全.md)

### [08. 数据库防火墙](./08_数据库防火墙/数据库防火墙.md)

### [09. 审计日志](./09_审计日志/审计日志.md)

### [10. 网络隔离](./10_网络隔离/网络隔离.md)

### [11. 各云厂商安全配置](./11_各云厂商安全配置/各云厂商安全配置.md)

### [12. AWS RDS安全深度配置](./12_AWS RDS安全深度配置/AWS RDS安全深度配置.md)
  - RDS安全参数组详解
  - RDS增强监控与性能洞察
  - RDS多可用区与故障转移
  - RDS安全自动化检测脚本

### [13. Azure SQL Database安全配置](./13_Azure SQL Database安全配置/Azure SQL Database安全配置.md)
  - Azure SQL安全基线配置
  - Azure SQL TDE与Always Encrypted
  - Azure SQL审计日志配置
  - Azure SQL动态数据掩码

### [14. MongoDB Atlas安全加固](./14_MongoDB Atlas安全加固/MongoDB Atlas安全加固.md)
  - Atlas网络与访问控制
  - MongoDB角色与权限管理

### [15. Redis安全加固](./15_Redis安全加固/Redis安全加固.md)
  - Redis安全配置
  - Redis漏洞与防护

### [16. 数据库漏洞扫描工具](./16_数据库漏洞扫描工具/数据库漏洞扫描工具.md)
  - 开源数据库漏洞扫描
  - 数据库安全基线检查脚本

### [17. 云数据库安全事件响应](./17_云数据库安全事件响应/云数据库安全事件响应.md)
  - 数据库泄露事件响应流程
  - 数据库取证脚本

---

## 📊 内容审核总览

- 总章节数：17
- 待完善章节：17

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **云数据库安全概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **公网暴露风险**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **弱密码与认证安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **存储加密**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **云上SQL注入**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **备份安全**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **数据库防火墙**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **审计日志**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **网络隔离**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **各云厂商安全配置**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **AWS RDS安全深度配置**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Azure SQL Database安全配置**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **MongoDB Atlas安全加固**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Redis安全加固**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **数据库漏洞扫描工具**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **云数据库安全事件响应**：⚠️ 需补充 2 项
  - 缺少：commands
  - 缺少：practice
