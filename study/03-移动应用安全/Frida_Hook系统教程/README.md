# Frida_Hook系统教程

> 本文档整理自：`Frida_Hook系统教程.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Frida 概述](./02_Frida 概述/Frida 概述.md)
  - 动态插桩技术原理
  - Frida 架构（Agent / Server / Gum Stalker）
  - Frida vs Xposed 对比
  - 环境搭建

### [03. Frida JavaScript API 详解](./03_Frida JavaScript API 详解/Frida JavaScript API 详解.md)
  - Process / Module / Pointer API
  - Interceptor（函数 Hook 基础）
  - Memory（内存读写搜索）
  - Java.perform（Android Java 层 Hook）
  - ObjC（iOS Objective-C Hook）
  - NativeFunction / NativeCallback
  - RPC（远程调用）

### [04. Android Hook 实战](./04_Android Hook 实战/Android Hook 实战.md)
  - Hook Java 方法（重载方法、构造函数、内部类）
  - Hook Native 函数（JNI 函数、SO 库函数）
  - 主动调用方法
  - 内存搜索与修改
  - SSL Pinning 绕过
  - Root 检测绕过
  - Frida 自身反调试绕过
  - 完整示例：分析加固 APP 登录流程

### [05. iOS Hook 实战](./05_iOS Hook 实战/iOS Hook 实战.md)
  - Hook Objective-C 方法
  - Hook Swift 方法
  - iOS Keychain 操作
  - SSL Pinning 绕过（iOS）
  - 越狱检测绕过

### [06. 高级技巧](./06_高级技巧/高级技巧.md)
  - Frida 脚本混淆与加密
  - Gum Stalker 代码跟踪
  - Frida 编译自定义 Agent
  - Hook 绕过 Frida 检测的方法
  - 群控/批量 Hook 框架

### [07. 常用 Frida 脚本集合](./07_常用 Frida 脚本集合/常用 Frida 脚本集合.md)
  - 常用 Hook 模板
  - 工具推荐

### [08. 结语](./08_结语/结语.md)

---

## 📊 内容审核总览

- 总章节数：8
- 待完善章节：8

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Frida 概述**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Frida JavaScript API 详解**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Android Hook 实战**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **iOS Hook 实战**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **高级技巧**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **常用 Frida 脚本集合**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **结语**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：commands
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
