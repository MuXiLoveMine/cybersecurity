# CTF-PWN与逆向方向详解

> 本文档整理自：`CTF-PWN与逆向方向详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. PWN基础](./02_PWN基础/PWN基础.md)
  - ELF文件结构
  - 保护机制检查
  - pwntools使用详解

### [03. 栈溢出题型](./03_栈溢出题型/栈溢出题型.md)
  - ret2text
  - ret2shellcode
  - ret2libc
  - ret2csu
  - 栈迁移（Stack Pivot）

### [04. ROP利用](./04_ROP利用/ROP利用.md)
  - ROPgadget使用
  - 多段ROP链
  - SROP（Sigreturn Oriented Programming）

### [05. 格式化字符串漏洞](./05_格式化字符串漏洞/格式化字符串漏洞.md)
  - 漏洞原理
  - 任意地址读
  - 任意地址写
  - 泄露canary

### [06. 堆利用](./06_堆利用/堆利用.md)
  - fastbin dup（Double Free）
  - unsorted bin attack
  - tcache利用（glibc 2.26+）
  - house of系列

### [07. 内核PWN基础](./07_内核PWN基础/内核PWN基础.md)
  - kernel ROP
  - ret2usr
  - modprobe_path利用

### [08. 逆向分析题型](./08_逆向分析题型/逆向分析题型.md)
  - 静态逆向
  - 动态调试
  - 算法还原
  - UPX脱壳

### [09. 混淆对抗](./09_混淆对抗/混淆对抗.md)
  - 反调试
  - 控制流平坦化
  - VM混淆
  - angr符号执行

### [10. 实战案例](./10_实战案例/实战案例.md)
  - 案例1：ret2libc - BUUCTF [BJDCTF 2nd]r2t3
  - 案例2：格式化字符串 - BUUCTF [Harekaze]fmt
  - 案例3：堆利用 - fastbin dup
  - 案例4：逆向 - 攻防世界 re1
  - 案例5：UPX脱壳逆向

### [11. 安全最佳实践](./11_安全最佳实践/安全最佳实践.md)
  - 二进制安全防御
  - 安全编码建议
  - 学习建议

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **PWN基础**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **栈溢出题型**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **ROP利用**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **格式化字符串漏洞**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **堆利用**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **内核PWN基础**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **逆向分析题型**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
- **混淆对抗**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实战案例**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：references
- **安全最佳实践**：⚠️ 需补充 1 项
  - 缺少：references
