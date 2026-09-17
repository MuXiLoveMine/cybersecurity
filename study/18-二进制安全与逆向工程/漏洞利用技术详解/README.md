# 漏洞利用技术详解

> 本文档整理自：`漏洞利用技术详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 栈溢出原理与利用](./02_栈溢出原理与利用/栈溢出原理与利用.md)
  - 栈溢出基础原理
  - ret2text
  - ret2shellcode
  - ret2libc
  - ROP链构造

### [03. 堆溢出与堆利用](./03_堆溢出与堆利用/堆溢出与堆利用.md)
  - ptmalloc内存管理基础
  - fastbin attack
  - unsorted bin attack
  - tcache攻击
  - House of系列技术

### [04. 格式化字符串漏洞利用](./04_格式化字符串漏洞利用/格式化字符串漏洞利用.md)

### [05. UAF漏洞利用](./05_UAF漏洞利用/UAF漏洞利用.md)

### [06. 整数溢出](./06_整数溢出/整数溢出.md)

### [07. 竞争条件漏洞](./07_竞争条件漏洞/竞争条件漏洞.md)

### [08. 漏洞缓解机制绕过](./08_漏洞缓解机制绕过/漏洞缓解机制绕过.md)
  - ASLR绕过
  - ROP绕过DEP
  - Bypass Canary
  - SROP

### [09. 实战案例：从漏洞发现到利用全流程](./09_实战案例：从漏洞发现到利用全流程/实战案例：从漏洞发现到利用全流程.md)
  - 目标程序
  - 安全机制检查
  - 利用步骤
  - 完整exploit脚本
  - 调试技巧
  - 安全修复建议

### [10. 附录：pwntools常用API速查](./10_附录：pwntools常用API速查/附录：pwntools常用API速查.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **栈溢出原理与利用**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **堆溢出与堆利用**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **格式化字符串漏洞利用**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **UAF漏洞利用**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **整数溢出**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **竞争条件漏洞**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **漏洞缓解机制绕过**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **实战案例：从漏洞发现到利用全流程**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **附录：pwntools常用API速查**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
