# CTF-Web方向详解

> 本文档整理自：`CTF-Web方向详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. SQL注入CTF题型](./02_SQL注入CTF题型/SQL注入CTF题型.md)
  - 联合查询注入（UNION Based）
  - 盲注（Boolean Based & Time Based）
  - 堆叠注入（Stacked Queries）
  - 绕过WAF技巧
  - NoSQL注入

### [03. XSS CTF题型](./03_XSS CTF题型/XSS CTF题型.md)
  - 反射型XSS
  - 存储型XSS
  - DOM型XSS
  - CSP绕过
  - XSS利用框架

### [04. SSRF CTF题型](./04_SSRF CTF题型/SSRF CTF题型.md)
  - 内网探测
  - Redis利用
  - Gopher协议利用
  - MySQL利用
  - 云服务元数据
  - SSRF绕过技巧

### [05. SSTI模板注入](./05_SSTI模板注入/SSTI模板注入.md)
  - 检测与识别
  - Jinja2（Python Flask）
  - Twig（PHP）
  - Freemarker（Java）
  - Smarty（PHP）

### [06. 反序列化漏洞](./06_反序列化漏洞/反序列化漏洞.md)
  - PHP反序列化
  - Java反序列化
  - Python pickle反序列化

### [07. 文件上传漏洞](./07_文件上传漏洞/文件上传漏洞.md)
  - 绕过后缀检查
  - 绕过Content-Type
  - 图片马制作
  - htaccess利用

### [08. 命令注入](./08_命令注入/命令注入.md)
  - 无回显注入
  - 绕过过滤
  - Linux特殊字符

### [09. 实战案例](./09_实战案例/实战案例.md)
  - 案例1：SQL注入 - BUUCTF [SUCTF 2019]EasySQL
  - 案例2：SSTI - 攻防世界 Web类 bad_python
  - 案例3：反序列化 - BUUCTF [0CTF 2016]piapiapia
  - 案例4：SSRF - BUUCTF [SSRF]LFI
  - 案例5：文件上传 - CTFHub 技能树

### [10. Web安全最佳实践](./10_Web安全最佳实践/Web安全最佳实践.md)
  - SQL注入防御
  - XSS防御
  - SSRF防御
  - 文件上传防御

### [11. Web方向学习总结](./11_Web方向学习总结/Web方向学习总结.md)
  - 解题流程
  - 工具清单
  - 常用Payload速查

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **SQL注入CTF题型**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **XSS CTF题型**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **SSRF CTF题型**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **SSTI模板注入**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **反序列化漏洞**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **文件上传漏洞**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **命令注入**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **Web安全最佳实践**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Web方向学习总结**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
