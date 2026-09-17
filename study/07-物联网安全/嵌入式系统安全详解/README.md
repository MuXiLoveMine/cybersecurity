# 嵌入式系统安全详解

> 本文档整理自：`嵌入式系统安全详解.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. 嵌入式系统安全概述](./02_嵌入式系统安全概述/嵌入式系统安全概述.md)
  - 嵌入式系统的安全挑战
  - 嵌入式系统安全层次模型

### [03. ARM架构安全特性](./03_ARM架构安全特性/ARM架构安全特性.md)
  - ARM安全扩展概览
  - ARM TrustZone架构
  - ARM内存保护机制
  - ARM异常等级与权限

### [04. MIPS架构安全特性](./04_MIPS架构安全特性/MIPS架构安全特性.md)
  - MIPS安全概述
  - MIPS内存段保护

### [05. RISC-V架构安全特性](./05_RISC-V架构安全特性/RISC-V架构安全特性.md)
  - RISC-V安全扩展
  - RISC-V PMP配置

### [06. TrustZone与TEE技术](./06_TrustZone与TEE技术/TrustZone与TEE技术.md)
  - TrustZone工作原理
  - OP-TEE架构
  - 可信应用 (TA) 开发

### [07. RTOS安全分析](./07_RTOS安全分析/RTOS安全分析.md)
  - FreeRTOS安全
  - Zephyr RTOS安全
  - ThreadX (Azure RTOS) 安全

### [08. 嵌入式Linux安全加固](./08_嵌入式Linux安全加固/嵌入式Linux安全加固.md)
  - 内核安全配置
  - 用户空间安全加固
  - 嵌入式Linux安全工具

### [09. 安全启动链详解](./09_安全启动链详解/安全启动链详解.md)
  - 安全启动概念
  - U-Boot安全启动
  - 固件签名验证

### [10. JTAG/SWD调试安全](./10_JTAG_SWD调试安全/JTAG_SWD调试安全.md)
  - 调试接口风险
  - 调试接口保护方案
  - UART安全

### [11. 参考资料](./11_参考资料/参考资料.md)
  - 标准与规范
  - 开源项目
  - 推荐阅读

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **目录**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
- **嵌入式系统安全概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **ARM架构安全特性**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **MIPS架构安全特性**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **RISC-V架构安全特性**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **TrustZone与TEE技术**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **RTOS安全分析**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **嵌入式Linux安全加固**：⚠️ 需补充 3 项
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **安全启动链详解**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **JTAG/SWD调试安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **参考资料**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
