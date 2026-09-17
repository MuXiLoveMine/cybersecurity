# 符号执行与angr实战

> 本文档整理自：`符号执行与angr实战.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 符号执行基础](./02_符号执行基础/符号执行基础.md)
  - 什么是符号执行
  - 符号执行原理
  - 符号执行的应用场景
  - 常用符号执行引擎介绍

### [03. angr入门](./03_angr入门/angr入门.md)
  - angr安装与环境配置
  - angr基本架构
  - 第一个angr脚本：加载二进制文件
  - 基本概念

### [04. angr核心功能](./04_angr核心功能/angr核心功能.md)
  - 符号变量创建与约束添加（claripy使用）
  - 状态探索策略
  - 地址与符号跳转控制
  - Hook函数与SimProcedure
  - 条件断点与状态检查
  - 内存与寄存器操作
  - State 的类型与创建
  - 选项配置（State Options）

### [05. CTF逆向解题实战](./05_CTF逆向解题实战/CTF逆向解题实战.md)
  - 案例1：简单的验证程序（找到正确输入）
  - 案例2：复杂条件判断（多分支路径探索）
  - 案例3：加密算法逆向（约束求解解密）
  - 案例4：反逆向对抗（混淆代码分析）
  - 案例5：Patch文件与内存补丁技巧
  - CTF解题通用模板

### [06. 漏洞挖掘与利用](./06_漏洞挖掘与利用/漏洞挖掘与利用.md)
  - 使用angr发现漏洞
  - 自动化漏洞利用生成
  - ROP链辅助构造
  - 与其他工具结合

### [07. 高级技巧与优化](./07_高级技巧与优化/高级技巧与优化.md)
  - 符号执行加速技巧
  - 处理循环与递归
  - 处理复杂系统调用
  - Veritesting技术详解
  - 自定义探索策略
  - 性能调优检查清单

### [08. angr插件与生态](./08_angr插件与生态/angr插件与生态.md)
  - angrutils使用
  - angrop（ROP链自动生成）
  - rex（漏洞利用自动生成）
  - 其他有用的插件

### [09. 常见问题与解决方案](./09_常见问题与解决方案/常见问题与解决方案.md)
  - 路径爆炸问题与缓解
  - 内存模型限制
  - 环境模拟不完整的处理
  - 性能调优建议
  - 学习资源与社区

### [10. 总结](./10_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **符号执行基础**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **angr入门**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **angr核心功能**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **CTF逆向解题实战**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：attack
  - 缺少：references
- **漏洞挖掘与利用**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **高级技巧与优化**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **angr插件与生态**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **常见问题与解决方案**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **总结**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
