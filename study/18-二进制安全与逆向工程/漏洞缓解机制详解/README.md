# 漏洞缓解机制详解

> 本文档整理自：`漏洞缓解机制详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 漏洞缓解机制概述](./02_漏洞缓解机制概述/漏洞缓解机制概述.md)

### [03. ASLR地址空间布局随机化](./03_ASLR地址空间布局随机化/ASLR地址空间布局随机化.md)
  - ASLR原理
  - ASLR类型
  - 绕过技术

### [04. DEP/NX数据执行防护](./04_DEP_NX数据执行防护/DEP_NX数据执行防护.md)
  - DEP原理
  - 绕过技术

### [05. Stack Canary栈保护](./05_Stack Canary栈保护/Stack Canary栈保护.md)
  - Canary原理
  - 绕过技术

### [06. RELRO只读重定位](./06_RELRO只读重定位/RELRO只读重定位.md)
  - RELRO原理
  - 绕过技术

### [07. PIE位置无关可执行文件](./07_PIE位置无关可执行文件/PIE位置无关可执行文件.md)
  - PIE原理
  - 绕过技术

### [08. CFI控制流完整性](./08_CFI控制流完整性/CFI控制流完整性.md)
  - CFI原理
  - CFG原理
  - 绕过技术

### [09. 缓解机制组合分析](./09_缓解机制组合分析/缓解机制组合分析.md)

### [10. checksec检测工具详解](./10_checksec检测工具详解/checksec检测工具详解.md)
  - checksec使用方法
  - 各保护机制检测原理
  - 一键安全检测脚本

### [11. 各机制绕过技术实战](./11_各机制绕过技术实战/各机制绕过技术实战.md)
  - ASLR绕过 - 信息泄露实战
  - DEP绕过 - ROP链构造
  - Canary绕过 - 完整exploit
  - RELRO绕过 - GOT覆写
  - PIE绕过实战
  - CFI/CFG绕过

### [12. 缓解机制对比与绕过难度](./12_缓解机制对比与绕过难度/缓解机制对比与绕过难度.md)
  - 各机制绕过技术汇总表
  - 历史CVE案例
  - 内核层缓解机制

### [13. 实战exploit开发流程](./13_实战exploit开发流程/实战exploit开发流程.md)

---

## 📊 内容审核总览

- 总章节数：13
- 待完善章节：13

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **漏洞缓解机制概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **ASLR地址空间布局随机化**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **DEP/NX数据执行防护**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Stack Canary栈保护**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RELRO只读重定位**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **PIE位置无关可执行文件**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **CFI控制流完整性**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **缓解机制组合分析**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **checksec检测工具详解**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **各机制绕过技术实战**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：references
- **缓解机制对比与绕过难度**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **实战exploit开发流程**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
