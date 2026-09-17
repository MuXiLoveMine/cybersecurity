# iOS逆向工具链详解

> 本文档整理自：`iOS逆向工具链详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. iOS逆向环境搭建](./02_iOS逆向环境搭建/iOS逆向环境搭建.md)
  - Ubuntu逆向环境
  - Theos越狱开发框架
  - SDK与工具链配置

### [03. class-dump与头文件提取](./03_class-dump与头文件提取/class-dump与头文件提取.md)
  - class-dump基础
  - 头文件分析技巧

### [04. Cycript动态分析](./04_Cycript动态分析/Cycript动态分析.md)
  - Cycript基础语法
  - 实例变量与方法Hook
  - 消息转发分析

### [05. Hopper与IDA Pro逆向](./05_Hopper与IDA Pro逆向/Hopper与IDA Pro逆向.md)
  - Hopper Disassembler
  - IDA Pro iOS逆向

### [06. Frida iOS Hooking](./06_Frida iOS Hooking/Frida iOS Hooking.md)
  - ObjC Hook
  - Swift Hook
  - Native Hook

### [07. objection自动化](./07_objection自动化/objection自动化.md)
  - 越狱检测绕过
  - SSL Pinning绕过
  - Keychain Dump

### [08. LLVM Pass与静态分析](./08_LLVM Pass与静态分析/LLVM Pass与静态分析.md)

### [09. iOS应用脱壳](./09_iOS应用脱壳/iOS应用脱壳.md)
  - frida-ios-dump
  - Clutch
  - 其他脱壳工具

### [10. Tweak开发](./10_Tweak开发/Tweak开发.md)
  - Theos项目创建
  - Logos语法
  - Cydia Substrate

### [11. iOS越狱生态](./11_iOS越狱生态/iOS越狱生态.md)
  - 越狱工具
  - 包管理器

### [12. 总结](./12_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：12
- 待完善章节：12

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **iOS逆向环境搭建**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **class-dump与头文件提取**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Cycript动态分析**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Hopper与IDA Pro逆向**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
- **Frida iOS Hooking**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **objection自动化**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **LLVM Pass与静态分析**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **iOS应用脱壳**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Tweak开发**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **iOS越狱生态**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **总结**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
