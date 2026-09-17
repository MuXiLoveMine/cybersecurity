# Native Hook技术专题

> 本文档整理自：`Native Hook技术专题.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Native Hook概述](./02_Native Hook概述/Native Hook概述.md)
  - 什么是Native Hook
  - Hook的基本原理
  - 与Java层Hook对比
  - 应用场景

### [03. PLT/GOT Hook技术](./03_PLT_GOT Hook技术/PLT_GOT Hook技术.md)
  - ELF文件格式基础
  - PLT表原理
  - GOT表修改
  - dl_iterate_phdr方法
  - PLT/GOT Hook的优缺点

### [04. Inline Hook技术](./04_Inline Hook技术/Inline Hook技术.md)
  - Inline Hook原理
  - 指令备份
  - 跳转注入
  - 架构差异对比
  - Inline Hook的优缺点

### [05. xHook框架](./05_xHook框架/xHook框架.md)
  - xHook简介
  - API详解
  - 使用方法
  - xHook使用注意事项

### [06. bhook框架](./06_bhook框架/bhook框架.md)
  - bhook简介
  - bHook与xHook对比
  - bHook API详解
  - 使用示例
  - 异步Hook

### [07. Dobby框架](./07_Dobby框架/Dobby框架.md)
  - Dobby简介
  - Dobby API
  - 使用示例
  - Dobby编译集成

### [08. Substrate框架](./08_Substrate框架/Substrate框架.md)
  - Cydia Substrate简介
  - MSHookFunction
  - Substrate for Android
  - Substrate与现代框架对比

### [09. 实战案例](./09_实战案例/实战案例.md)
  - SSL Pinning绕过（Native层实现）
  - 游戏逆向修改Native函数
  - 反调试绕过

### [10. 附录：工具快速参考](./10_附录：工具快速参考/附录：工具快速参考.md)
  - Native Hook框架选型指南
  - 常用命令速查

### [11. 参考文献](./11_参考文献/参考文献.md)

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **目录**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Native Hook概述**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **PLT/GOT Hook技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Inline Hook技术**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **xHook框架**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **bhook框架**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Dobby框架**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Substrate框架**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实战案例**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **附录：工具快速参考**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **参考文献**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
