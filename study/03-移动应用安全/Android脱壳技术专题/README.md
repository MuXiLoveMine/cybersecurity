# Android脱壳技术专题

> 本文档整理自：`Android脱壳技术专题.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Android 加固技术概述](./02_Android 加固技术概述/Android 加固技术概述.md)
  - APK 文件结构（DEX / 资源 / 签名）
  - DEX 文件格式详解
  - 加固原理
  - 主流加固厂商特征

### [03. 脱壳原理](./03_脱壳原理/脱壳原理.md)
  - 内存中 DEX 文件特征
  - 脱壳时机选择
  - 主动调用 vs 被动 Dump
  - 加固代际演进

### [04. 常见脱壳方法](./04_常见脱壳方法/常见脱壳方法.md)
  - DexExtractor 原理与使用
  - DexHound 原理
  - FRIDA-DEXDump 原理与使用
  - BlackDex 原理与使用
  - Youpk 原理
  - FART（自动化脱壳）原理
  - 各方法对比表

### [05. 实战脱壳流程](./05_实战脱壳流程/实战脱壳流程.md)
  - 判断加固类型
  - 选择脱壳方法
  - 内存 Dump DEX
  - DEX 修复（Header 修复 / CodeItem 对齐）
  - 反编译验证（jadx / JADX-GUI）

### [06. 函数抽取壳处理](./06_函数抽取壳处理/函数抽取壳处理.md)
  - 函数抽取原理
  - 主动调用触发
  - FART 自动还原
  - CodeItem 定位与提取

### [07. VMP 壳分析入门](./07_VMP 壳分析入门/VMP 壳分析入门.md)
  - VMP 原理（指令虚拟化）
  - VMP 还原难度
  - 部分还原方法

### [08. 反调试与绕过](./08_反调试与绕过/反调试与绕过.md)
  - ptrace 检测
  - /proc/self/status 检测
  - SO 层反调试
  - Frida 检测与绕过

### [09. 脱壳注意事项](./09_脱壳注意事项/脱壳注意事项.md)
  - 法律合规边界
  - 脱壳环境搭建
  - 实用工具清单

### [10. 结语](./10_结语/结语.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：attack
  - 缺少：references
- **Android 加固技术概述**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **脱壳原理**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **常见脱壳方法**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **实战脱壳流程**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **函数抽取壳处理**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **VMP 壳分析入门**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **反调试与绕过**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **脱壳注意事项**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **结语**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
