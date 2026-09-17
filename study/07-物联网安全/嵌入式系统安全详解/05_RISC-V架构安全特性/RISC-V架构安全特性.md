# RISC-V架构安全特性

### 4.1 RISC-V安全扩展

```
RISC-V安全扩展:

1. PMP (Physical Memory Protection):
   - 区域式内存保护
   - 16个可配置区域
   - 每区域独立的读/写/执行权限
   - 机器模式 (M-mode) 可配置

2. 多模式特权架构:
   ┌──────────────────────────────────┐
   │ M-mode (Machine)                 │
   │  - 最高权限                      │
   │  - 硬件访问                      │
   │  - PMP配置                       │
   ├──────────────────────────────────┤
   │ S-mode (Supervisor)              │
   │  - 操作系统内核                  │
   │  - 页表管理 (Sv39/Sv48)          │
   │  - SBI调用                        │
   ├──────────────────────────────────┤
   │ U-mode (User)                    │
   │  - 用户应用                      │
   │  - 最低权限                      │
   └──────────────────────────────────┘

3. Keystone TEE:
   - 开源TEE实现
   - 基于Enclave的安全执行
   - 内存加密隔离

4. 密码学扩展:
   - Scalar Cryptography Extension
   - 硬件加速AES/SHA/RSA/ECC
   - 向量密码学扩展 (V扩展相关)
```

### 4.2 RISC-V PMP配置

```c
// RISC-V PMP配置示例
// 寄存器: pmpcfg0-pmpcfg15, pmpaddr0-pmpaddr15

// 配置PMP区域0: 只读区域
// pmpcfg0:
//   L = 0 (不锁定)
//   A = 1 (TOR - Top of Range)
//   X = 0 (不可执行)
//   W = 0 (不可写)
//   R = 1 (可读)
pmpcfg0 = 0x01;  // A=TOR, R=1
pmpaddr0 = 0x80000000 >> 2;  // 基地址

// 配置PMP区域1: 可读写区域
pmpcfg1 = 0x1B;  // A=NAPOT, R=1, W=1, X=0
pmpaddr1 = 0x801FFFFF >> 2;

// 配置PMP区域2: 默认拒绝 (U模式)
// 最后一个区域设置为NAPOT, size=0
// 匹配所有未匹配的地址
pmpcfg15 = 0x1A;  // A=NAPOT, W=1 (deny)
pmpaddr15 = 0x0;

// PMP区域优先级
// 编号小的优先级高
// 第一个匹配的区域决定权限
```

---

---

## 📋 内容审核与补充建议

> 针对「RISC-V架构安全特性」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
