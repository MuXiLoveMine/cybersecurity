# Inline Hook技术

### 3.1 Inline Hook原理

Inline Hook是一种更强大的Hook技术，它直接修改目标函数入口处的机器码指令，将其替换为跳转到Hook函数的指令。与PLT/GOT Hook不同，Inline Hook可以拦截任何函数调用，包括内部函数调用。

**Inline Hook工作流程：**

```
原始函数入口:
    push    {r4-r7, lr}       ← 原始指令1
    sub     sp, #0x20         ← 原始指令2
    ...

Hook后:
    ldr     pc, [pc, #0]     ← 跳转指令（覆盖原始指令1）
    .word   hook_func_addr   ← Hook函数地址
    sub     sp, #0x20        ← 原始指令2（保留）
    ...

执行流程:
目标函数被调用
    → 执行跳转指令
    → 跳转到Hook函数
    → Hook函数处理（可选调用原始函数）
    → 恢复原始指令执行
    → 跳回原函数+偏移
```

### 3.2 指令备份

Inline Hook的关键挑战是指令备份（Trampoline/蹦床）。当覆盖函数入口指令时，被覆盖的指令不能丢失，需要保存到一块独立的可执行内存中，以便Hook函数调用原始函数时能执行完整的原始逻辑。

**指令备份原则：**

1. **完整性**：备份的指令必须是完整的指令序列，不能截断一条指令
2. **位置无关性**：备份的指令如果包含相对跳转/相对寻址，需要重定位
3. **执行连续性**：备份指令后需要跳转回原函数未被Hook的部分

```c
// 指令备份示例（ARM64架构）

// ARM64单条指令4字节，跳转指令需要5条指令（20字节）
// 备份原始的前5条指令
void *backup_instructions(void *target, size_t backup_size) {
    // 1. 分配可执行内存（RWX）
    void *trampoline = mmap(NULL, backup_size + 16,
                            PROT_READ | PROT_WRITE | PROT_EXEC,
                            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (trampoline == MAP_FAILED) return NULL;

    // 2. 复制原始指令
    memcpy(trampoline, target, backup_size);

    // 3. 处理需要重定位的指令
    //    - B/BL（相对跳转）：重新计算偏移
    //    - ADR/ADRP：重新计算目标地址
    //    - LDR（PC相对）：重新计算地址

    // 4. 添加跳回指令
    //    ARM64: LDR X16, #8; BR X16; .quad addr
    void *return_addr = (void *)((uintptr_t)target + backup_size);
    uint32_t *jump_back = (uint32_t *)((uintptr_t)trampoline + backup_size);
    // ldr x16, #8
    jump_back[0] = 0x58000050;
    // br x16
    jump_back[1] = 0xD61F0200;
    // 地址
    *(uint64_t *)&jump_back[2] = (uint64_t)return_addr;

    // 5. 修改内存权限为只读可执行
    mprotect(trampoline, backup_size + 16, PROT_READ | PROT_EXEC);

    return trampoline;
}
```

### 3.3 跳转注入

不同架构的跳转指令实现方式不同：

**ARM32 Thumb模式：**
```asm
// Thumb16跳转（2字节+4字节地址 = 6字节，需备份3条2字节指令）
ldr     r0, [pc, #0]     // 2字节：从PC相对地址加载
bx      r0               // 2字节：跳转到r0
.word   hook_addr         // 4字节：Hook函数地址
```

**ARM64（AArch64）：**
```asm
// ARM64跳转（16字节 = 4条指令）
ldr     x16, #8          // 4字节：从PC+8加载地址到x16
br      x16              // 4字节：跳转到x16
.quad   hook_addr        // 8字节：Hook函数地址
// 需要备份前2条原始指令（8字节）
```

**x86/x86_64：**
```asm
// x86跳转（5字节）
jmp     <hook_addr>       // 5字节：E9 + 4字节相对偏移
// 需要备份前5字节原始指令（注意指令对齐）

// x86_64也可以用绝对跳转（14字节）
mov     rax, <hook_addr>  // 10字节：48 B8 + 8字节地址
jmp     rax               // 2字节：FF E0
// 需要备份前3条指令（12字节，确保指令完整性）
```

### 3.4 架构差异对比

| 特性 | x86/x86_64 | ARM32 | ARM64 |
|------|-----------|-------|-------|
| **指令长度** | 变长（1-15字节） | 定长2字节(Thumb)/4字节(ARM) | 定长4字节 |
| **跳转指令大小** | 5字节(JMP) | 8字节(Thumb)/12字节(ARM) | 16字节 |
| **备份指令数** | 需动态计算（变长） | 3条(Thumb)/3条(ARM) | 4条 |
| **指令重定位** | 需处理相对跳转、RIP相对寻址 | 需处理PC相对跳转 | 需处理ADR/ADRP/B/BL |
| **Thumb/ARM切换** | 无 | 需要处理模式切换(BX) | 无 |
| **内存权限** | mprotect RWX | mprotect RWX | mprotect RWX |
| **缓存一致性** | 无需特殊处理 | 需flush icache | 需flush icache |

**ARM缓存一致性处理：**
```c
#include <sys/cachectl.h>

void flush_icache(void *addr, size_t size) {
#if defined(__arm__)
    // ARM32需要刷新指令缓存
    cacheflush((long)addr, (long)size, 0);
#elif defined(__aarch64__)
    // ARM64需要刷新指令缓存
    __builtin___clear_cache((char *)addr, (char *)addr + size);
#endif
}
```

### 3.5 Inline Hook的优缺点

**优点：**
- 可以Hook任何函数，包括内部函数
- 不依赖PLT/GOT机制
- 拦截范围更广，包括直接调用和间接调用

**缺点：**
- 实现复杂，需要处理指令重定位
- 稳定性风险较高，指令修改错误会导致崩溃
- 需要处理缓存一致性
- 线程安全问题（多线程同时执行被Hook函数可能崩溃）
- 容易被完整性检测发现（代码段被修改）

---

---

## 📋 内容审核与补充建议

> 针对「Inline Hook技术」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
