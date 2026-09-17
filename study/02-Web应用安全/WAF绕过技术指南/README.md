# WAF绕过技术指南

> 本文档整理自：`WAF绕过技术指南.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. WAF概述](./02_WAF概述/WAF概述.md)
  - 什么是WAF
  - WAF类型
  - WAF检测原理
  - WAF局限性

### [03. SQL注入WAF绕过](./03_SQL注入WAF绕过/SQL注入WAF绕过.md)
  - 大小写绕过
  - 注释绕过
  - 编码绕过
  - 等价函数绕过
  - 内联注释绕过
  - 空格绕过
  - HTTP参数污染（HPP）
  - 分块传输绕过
  - 综合绕过示例

### [04. XSS绕过技术](./04_XSS绕过技术/XSS绕过技术.md)
  - 标签变形
  - 事件绕过
  - 编码绕过
  - Content-Type绕过
  - 上下文相关绕过
  - CSP绕过

### [05. 文件上传WAF绕过](./05_文件上传WAF绕过/文件上传WAF绕过.md)
  - Content-Type修改
  - 文件头伪造
  - 后缀变形
  - htaccess绕过
  - user.ini绕过（PHP）
  - multipart/form-data绕过
  - 竞争条件绕过

### [06. 命令注入绕过](./06_命令注入绕过/命令注入绕过.md)
  - 通配符绕过
  - 变量替换
  - 编码绕过
  - 空格绕过
  - 引号绕过
  - 综合命令注入绕过示例

### [07. 通用WAF绕过技巧](./07_通用WAF绕过技巧/通用WAF绕过技巧.md)
  - HTTP参数污染（HPP）
  - 分块传输编码（Chunked Transfer）
  - 超长URL/请求体
  - 请求方法变换
  - 协议层绕过
  - 超时绕过

### [08. 自动化WAF绕过工具](./08_自动化WAF绕过工具/自动化WAF绕过工具.md)
  - sqlmap --tamper
  - wafw00f
  - bypass-firewall-by-fuzzing
  - 其他工具
  - 自定义绕过Payload测试框架

### [09. WAF配置与防护最佳实践](./09_WAF配置与防护最佳实践/WAF配置与防护最佳实践.md)
  - WAF规则配置
  - 防护加固措施
  - 多层防护体系
  - WAF规则测试与调优
  - WAF运维最佳实践

### [10. 附录：WAF绕过速查表](./10_附录：WAF绕过速查表/附录：WAF绕过速查表.md)
  - A. SQL注入绕过速查
  - B. XSS绕过速查
  - C. 命令注入绕过速查

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **WAF概述**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **SQL注入WAF绕过**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **XSS绕过技术**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **文件上传WAF绕过**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **命令注入绕过**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **通用WAF绕过技巧**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **自动化WAF绕过工具**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **WAF配置与防护最佳实践**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **附录：WAF绕过速查表**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
