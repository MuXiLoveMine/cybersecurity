# ARM架构安全特性

### 2.1 ARM安全扩展概览

```
ARM架构安全扩展发展:

ARMv6:
  - TrustZone技术引入
  - 安全世界/正常世界隔离

ARMv7-A:
  - TrustZone增强
  - 安全监控模式
  - MMU虚拟化扩展

ARMv8-A:
  - AArch64安全状态
  - EL3安全监控层
  - 虚拟化扩展 (EL2)
  - PAN (Privileged Access Never)

ARMv8.1-A+:
  - AArch64增强
  - RAS (可靠性/可用性/可维护性)
  - PAE (物理地址扩展)

ARMv9-A:
  - CCA (Confidential Compute Architecture)
  - RME (Realm Management Extension)
  - MPAM (Memory System Resource Partitioning)
  - SVE2 (Scalable Vector Extension 2)
```

### 2.2 ARM TrustZone架构

```
ARM TrustZone架构:

┌─────────────────────────────────────────────────────────────┐
│                    正常世界 (Normal World)                    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                      │
│  │ 用户态   │  │ 内核态   │  │ 虚拟化   │                      │
│  │ EL0     │  │ EL1     │  │ EL2     │                      │
│  └─────────┘  └─────────┘  └─────────┘                      │
│  富执行环境 (REE - Rich Execution Environment)              │
├─────────────────────────────────────────────────────────────┤
│              SMC (Secure Monitor Call)                        │
│                    EL3 (安全监控层)                           │
├─────────────────────────────────────────────────────────────┤
│                    安全世界 (Secure World)                    │
│  ┌─────────────────────────────────────┐                     │
│  │   TEE (Trusted Execution Environment) │                     │
│  │   ┌─────────┐  ┌─────────┐         │                     │
│  │   │ TA      │  │ TA      │         │                     │
│  │   │ (可信   │  │ (可信   │         │                     │
│  │   │  应用)  │  │  应用)  │         │                     │
│  │   └─────────┘  └─────────┘         │                     │
│  │   ┌─────────────────────┐          │                     │
│  │   │  Trusted OS         │          │                     │
│  │   │  (OP-TEE/QSEE)     │          │                     │
│  │   └─────────────────────┘          │                     │
│  └─────────────────────────────────────┘                     │
│  筒执行环境 (TEE - Trusted Execution Environment)            │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 ARM内存保护机制

```
ARM内存保护:

1. MMU (Memory Management Unit) - ARMv7-A/ARMv8-A:
   - 虚拟地址到物理地址映射
   - 页表权限控制 (AP, UXN, PXN)
   - 内存属性 (Normal/Device/Strongly-Ordered)
   - ASID (Address Space IDentifier)

2. MPU (Memory Protection Unit) - ARMv7-M/ARMv8-M:
   - 区域 (Region) 基于的内存保护
   - 8-16个可配置区域
   - 起始/结束地址 + 权限
   - Cortex-M系列使用

3. PMSAv8-MA (ARMv8-M Architecture):
   - 增强的MPU
   - 支持TrustZone for Cortex-M
   - 安全/非安全区域隔离

MPU配置示例 (Cortex-M):
// MPU区域配置
typedef struct {
    uint32_t base_addr;     // 区域基地址
    uint32_t size;          // 区域大小
    uint32_t access_perm;   // 访问权限
    uint32_t exec_perm;     // 执行权限
    uint32_t cache_attr;    // 缓存属性
    uint32_t secure_attr;   // 安全属性
} mpu_region_t;

// 配置非安全区域
mpu_region_t user_region = {
    .base_addr = 0x20000000,
    .size = MPU_SIZE_256KB,
    .access_perm = MPU_ACCESS_FULL,
    .exec_perm = MPU_EXEC_ALLOW,
    .cache_attr = MPU_CACHE_WB,
    .secure_attr = MPU_NON_SECURE,
};

// 配置安全区域
mpu_region_t secure_region = {
    .base_addr = 0x30000000,
    .size = MPU_SIZE_128KB,
    .access_perm = MPU_ACCESS_PRIV_ONLY,
    .exec_perm = MPU_EXEC_ALLOW,
    .cache_attr = MPU_CACHE_WT,
    .secure_attr = MPU_SECURE,
};
```

### 2.4 ARM异常等级与权限

```
ARMv8-A异常等级:

┌──────────────────────────────────────────────────────────┐
│ EL0: 用户应用                                            │
│  - 最低权限                                               │
│  - 应用程序运行在此                                      │
│  - 不可直接访问硬件                                       │
├──────────────────────────────────────────────────────────┤
│ EL1: 操作系统内核                                         │
│  - 内核权限                                               │
│  - Linux内核运行在此                                      │
│  - 可配置MMU/中断                                        │
├──────────────────────────────────────────────────────────┤
│ EL2: 虚拟机监控器 (Hypervisor)                           │
│  - 虚拟化管理                                            │
│  - Stage-2 MMU                                          │
│  - 虚拟中断控制                                          │
├──────────────────────────────────────────────────────────┤
│ EL3: 安全监控 (Secure Monitor)                           │
│  - 最高权限                                              │
│  - 安全世界/正常世界切换                                  │
│  - ARM Trusted Firmware (TF-A)                           │
└──────────────────────────────────────────────────────────┘

安全状态:
- Secure state: EL0(S)-EL3
- Non-secure state: EL0(NS)-EL2
- Root state: EL3 (RME扩展)
```

---

---

