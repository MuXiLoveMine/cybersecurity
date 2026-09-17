# 二进制逆向分析基础

> 本文档整理自：`二进制逆向分析基础.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. PE文件格式详解](./02_PE文件格式详解/PE文件格式详解.md)
  - PE文件整体布局
  - DOS头
  - PE头
  - 节表
  - 导入表
  - 导出表
  - 资源表与重定位表

### [03. ELF文件格式详解](./03_ELF文件格式详解/ELF文件格式详解.md)
  - ELF整体布局
  - ELF头
  - 程序头表
  - 节区详解
  - 动态链接机制

### [04. x86/x64指令集基础](./04_x86_x64指令集基础/x86_x64指令集基础.md)
  - 寄存器体系
  - 寻址方式
  - 核心指令详解
  - 函数调用与栈帧

### [05. ARM指令集基础](./05_ARM指令集基础/ARM指令集基础.md)
  - ARM架构概述
  - 寄存器与异常模式
  - ARM指令详解
  - Thumb指令集

### [06. 静态分析方法](./06_静态分析方法/静态分析方法.md)
  - 反汇编技术
  - 反编译技术
  - 控制流图分析
  - 数据流分析

### [07. IDA Pro使用指南](./07_IDA Pro使用指南/IDA Pro使用指南.md)
  - IDA界面与视图
  - 常用快捷键速查
  - IDAPython脚本

### [08. Ghidra使用指南](./08_Ghidra使用指南/Ghidra使用指南.md)
  - Ghidra工作流程
  - Ghidra关键操作
  - Ghidra脚本

### [09. radare2使用指南](./09_radare2使用指南/radare2使用指南.md)
  - 基本使用流程
  - radare2脚本

### [10. 实战案例：逆向一个简单的CrackMe](./10_实战案例：逆向一个简单的CrackMe/实战案例：逆向一个简单的CrackMe.md)
  - 目标程序介绍
  - 分析步骤
  - 求解序列号
  - 使用动态调试验证
  - 使用pwntools自动化
  - 总结

### [11. 附录：常见代码模式识别速查表](./11_附录：常见代码模式识别速查表/附录：常见代码模式识别速查表.md)

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
  - 缺少：attack
  - 缺少：references
- **PE文件格式详解**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **ELF文件格式详解**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **x86/x64指令集基础**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **ARM指令集基础**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **静态分析方法**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **IDA Pro使用指南**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **Ghidra使用指南**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **radare2使用指南**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实战案例：逆向一个简单的CrackMe**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **附录：常见代码模式识别速查表**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
