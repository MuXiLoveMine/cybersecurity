# Native Hook技术专题

> 本文档系统讲解Android/iOS Native层Hook技术的原理、框架使用与实战应用，涵盖PLT/GOT Hook、Inline Hook、xHook、bhook、Dobby、Substrate等主流框架的深入剖析。

---

## 目录

1. [Native Hook概述](#1-native-hook概述)
2. [PLT/GOT Hook技术](#2-pltgot-hook技术)
3. [Inline Hook技术](#3-inline-hook技术)
4. [xHook框架](#4-xhook框架)
5. [bhook框架](#5-bhook框架)
6. [Dobby框架](#6-dobby框架)
7. [Substrate框架](#7-substrate框架)
8. [实战案例](#8-实战案例)

---

## 1. Native Hook概述

### 1.1 什么是Native Hook

Native Hook是指在Native层（C/C++编译生成的机器码）对函数调用进行拦截和修改的技术。与Java层Hook不同，Native Hook直接操作二进制机器码或动态链接表，能够在更底层的位置介入程序执行流程。

在Android安全研究中，Native Hook具有不可替代的价值。许多安全敏感操作（如SSL/TLS加密、反调试检测、游戏逻辑核心算法）都在Native层实现，仅靠Java层Hook无法触及。Native Hook使得安全研究人员能够：

- **拦截和修改Native函数的参数与返回值**：例如修改加密函数的输入输出
- **监控敏感API调用**：追踪文件操作、网络通信、加密运算
- **绕过安全机制**：如SSL Pinning、Root检测、调试器检测
- **动态分析恶意代码**：在运行时观察恶意软件行为
- **游戏逆向分析**：修改游戏逻辑、内存数值、反作弊机制

### 1.2 Hook的基本原理

Hook的核心思想是"劫持控制流"。具体而言，当程序执行到某个函数调用点时，通过修改代码或数据结构，使执行流跳转到Hook处理函数，完成自定义逻辑后再返回原函数（或完全不返回）。

Native Hook主要有以下几种技术路线：

```
┌─────────────────────────────────────────────────────────────┐
│                  Native Hook 技术分类                         │
├─────────────┬───────────────┬───────────────┬───────────────┤
│  PLT/GOT    │  Inline Hook  │  GOT Hook     │  Symbol Hook  │
│  Hook       │  (指令修改)    │  (地址替换)    │  (dlsym拦截)   │
├─────────────┼───────────────┼───────────────┼───────────────┤
│ 修改PLT表   │ 修改函数入口   │ 修改GOT表     │ 拦截dlsym调用  │
│ 中间跳转    │ 注入跳转指令   │ 替换函数地址   │ 返回自定义地址  │
└─────────────┴───────────────┴───────────────┴───────────────┘
```

### 1.3 与Java层Hook对比

| 对比维度 | Java层Hook（Frida/Xposed） | Native Hook |
|---------|---------------------------|-------------|
| **作用层级** | Java虚拟机层 | 原生机器码层 |
| **技术基础** | ART/Dexby修改、JNI函数表 | 机器码修改、动态链接表修改 |
| **适用范围** | Java方法、部分JNI调用 | 所有Native函数，包括系统库 |
| **性能影响** | 相对较高（涉及虚拟机交互） | 较低（直接机器码级别） |
| **对抗能力** | 容易被Java层反Hook检测 | 较难检测，可绕过Java层防护 |
| **跨语言能力** | 仅限Java/Kotlin | 可Hook任意C/C++函数 |
| **开发难度** | 相对简单 | 需要理解ABI、指令集、内存布局 |
| **典型工具** | Xposed、Frida（Java层） | Frida（Native层）、xHook、Dobby |

### 1.4 应用场景

**安全研究场景：**
- 绕过SSL Pinning，抓取HTTPS明文流量
- 绕过Root检测、调试器检测、模拟器检测
- 分析加密算法实现，提取密钥和算法逻辑
- 恶意软件行为分析（API调用追踪）

**逆向工程场景：**
- 游戏内存修改与反作弊绕过
- 协议分析（修改请求/响应参数）
- 算法还原（追踪加密/签名算法）

**安全防护场景：**
- 应用加固（Hook检测与反调试）
- 动态插桩（性能分析、漏洞挖掘）
- 安全SDK开发（运行时行为监控）

---

## 2. PLT/GOT Hook技术

### 2.1 ELF文件格式基础

要理解PLT/GOT Hook，首先需要理解ELF（Executable and Linkable Format）文件格式中的动态链接机制。

ELF文件包含以下关键段：

```
ELF文件结构
├── .text         — 代码段（机器指令）
├── .plt          — 过程链接表（PLT）
├── .got          — 全局偏移表（GOT）
├── .got.plt      — GOT的PLT专用区域
├── .rel.plt      — PLT重定位信息
├── .dynsym       — 动态符号表
├── .dynstr       — 动态字符串表
└── .dynamic      — 动态链接信息
```

### 2.2 PLT表原理

PLT（Procedure Linkage Table，过程链接表）是ELF文件中用于实现延迟绑定的机制。其核心思想是"第一次调用时解析，后续调用直接跳转"。

以ARM架构为例，调用`open()`函数的PLT表条目通常如下：

```asm
// PLT入口（简化版）
PLT_open:
    ldr     ip, [pc, #offset]     // 从GOT加载地址
    add     ip, pc, ip            // 计算GOT条目地址
    ldr     pc, [ip]              // 跳转到GOT中存储的地址

// 第一次调用时，GOT中存储的是PLT下一条指令的地址
// 该指令会跳转到动态链接器进行符号解析
    add     ip, pc, #...          // 传递重定位索引
    ldr     pc, [pc, #...]        // 跳转到dl_runtime_resolve
```

**PLT执行流程：**

```
程序调用open()
    │
    v
跳转到PLT[open]
    │
    v
从GOT[open]读取地址 ────────── 第一次调用 ──────> 跳转到dl_runtime_resolve
    │                                              │
    │ ──────── 后续调用 ──────>                  解析open()真实地址
    │                                              │
    v                                              v
直接跳转到open()真实地址 <────────────── 写入GOT[open]
```

### 2.3 GOT表修改

GOT（Global Offset Table）存储了外部符号的实际运行时地址。GOT Hook的核心就是修改GOT表中的函数地址指针，使其指向自定义的Hook函数。

**GOT Hook基本步骤：**

```c
#include <stdio.h>
#include <dlfcn.h>
#include <elf.h>
#include <link.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

// 定义函数指针类型
typedef int (*orig_open_t)(const char *pathname, int flags, ...);

// 原始函数指针
static orig_open_t orig_open = NULL;

// Hook函数
int hook_open(const char *pathname, int flags, ...) {
    printf("[Hook] open() called: %s\n", pathname);

    // 调用原始函数
    va_list args;
    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);

    int result = orig_open(pathname, flags, mode);
    printf("[Hook] open() returned fd: %d\n", result);
    return result;
}

// 修改GOT表
int got_hook(const char *target_lib, const char *symbol, void *new_func, void **orig_func) {
    // 1. 获取目标库的基地址和ELF头
    void *handle = dlopen(target_lib, RTLD_NOW);
    if (!handle) return -1;

    // 2. 获取原始函数地址
    *orig_func = dlsym(handle, symbol);
    if (!*orig_func) return -1;

    // 3. 遍历重定位表，找到GOT中对应条目
    // 4. 修改GOT条目权限（mprotect）
    // 5. 写入新函数地址
    // 6. 恢复权限

    return 0;
}
```

### 2.4 dl_iterate_phdr方法

`dl_iterate_phdr`是Linux/Android提供的API，用于遍历当前进程加载的所有共享库的ELF程序头。这是GOT Hook中定位目标库的标准方法。

```c
#include <link.h>
#include <elf.h>

struct got_hook_ctx {
    const char *target_lib;   // 目标库名
    const char *symbol;       // 目标符号
    void *new_func;           // 新函数地址
    void **orig_func;         // 原始函数地址输出
    int found;
};

// dl_iterate_phdr回调函数
static int dl_callback(struct dl_phdr_info *info, size_t size, void *data) {
    struct got_hook_ctx *ctx = (struct got_hook_ctx *)data;

    // 检查是否为目标库
    if (!strstr(info->dlpi_name, ctx->target_lib)) {
        return 0;
    }

    ElfW(Addr) base_addr = info->dlpi_addr;

    // 遍历程序头
    for (int i = 0; i < info->dlpi_phnum; i++) {
        const ElfW(Phdr) *phdr = &info->dlpi_phdr[i];

        if (phdr->p_type == PT_DYNAMIC) {
            // 找到动态段
            ElfW(Dyn) *dyn = (ElfW(Dyn) *)(base_addr + phdr->p_vaddr);

            ElfW(Sym) *symtab = NULL;
            const char *strtab = NULL;
            ElfW(Rel) *rel_plt = NULL;
            size_t rel_plt_count = 0;
            ElfW(Rel) *rel_dyn = NULL;
            size_t rel_dyn_count = 0;
            size_t *got_plt = NULL;

            // 解析动态段
            for (ElfW(Dyn) *d = dyn; d->d_tag != DT_NULL; d++) {
                switch (d->d_tag) {
                    case DT_SYMTAB:
                        symtab = (ElfW(Sym) *)(base_addr + d->d_un.d_ptr);
                        break;
                    case DT_STRTAB:
                        strtab = (const char *)(base_addr + d->d_un.d_ptr);
                        break;
                    case DT_JMPREL:
                        rel_plt = (ElfW(Rel) *)(base_addr + d->d_un.d_ptr);
                        break;
                    case DT_PLTRELSZ:
                        rel_plt_count = d->d_un.d_val / sizeof(ElfW(Rel));
                        break;
                    case DT_RELA:
                    case DT_REL:
                        rel_dyn = (ElfW(Rel) *)(base_addr + d->d_un.d_ptr);
                        break;
                    case DT_PLTGOT:
                        got_plt = (size_t *)(base_addr + d->d_un.d_ptr);
                        break;
                }
            }

            // 遍历PLT重定位表
            for (size_t j = 0; j < rel_plt_count; j++) {
                ElfW(Sym) *sym = &symtab[ELF_R_SYM(rel_plt[j].r_info)];
                const char *sym_name = strtab + sym->st_name;

                if (strcmp(sym_name, ctx->symbol) == 0) {
                    // 找到目标符号
                    size_t got_offset = rel_plt[j].r_offset;
                    void **got_entry = (void **)(base_addr + got_offset);

                    // 保存原始地址
                    *ctx->orig_func = *got_entry;

                    // 修改内存权限
                    size_t page_size = sysconf(_SC_PAGESIZE);
                    uintptr_t addr = (uintptr_t)got_entry;
                    uintptr_t page = addr & ~(page_size - 1);
                    mprotect((void *)page, page_size, PROT_READ | PROT_WRITE);

                    // 写入Hook函数地址
                    *got_entry = ctx->new_func;

                    // 恢复权限
                    mprotect((void *)page, page_size, PROT_READ | PROT_WRITE);

                    ctx->found = 1;
                    return 1; // 停止遍历
                }
            }
        }
    }
    return 0;
}

// GOT Hook入口
int do_got_hook(const char *lib, const char *sym, void *new_func, void **orig_func) {
    struct got_hook_ctx ctx = {
        .target_lib = lib,
        .symbol = sym,
        .new_func = new_func,
        .orig_func = orig_func,
        .found = 0
    };

    dl_iterate_phdr(dl_callback, &ctx);
    return ctx.found ? 0 : -1;
}
```

### 2.5 PLT/GOT Hook的优缺点

**优点：**
- 实现相对简单，不涉及指令修改
- 稳定性高，不会破坏代码完整性
- 可逆性强，恢复原值即可取消Hook
- 对所有通过PLT/GOT的调用都有效

**缺点：**
- 只能Hook通过PLT/GOT调用的外部符号
- 无法Hook内部函数调用（直接call/jmp）
- 无法Hook通过dlsym获取地址后直接调用的函数
- 无法Hook系统调用（syscall）
- 需要目标符号在动态符号表中可见

---

## 3. Inline Hook技术

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

## 4. xHook框架

### 4.1 xHook简介

xHook是爱奇艺开源的PLT/GOT Hook框架，专注于Android平台Native层函数Hook。它通过修改ELF文件的PLT/GOT表实现函数拦截，具有轻量、稳定、易用的特点。

**项目地址：** https://github.com/iqiyi/xHook

**核心特性：**
- 纯C实现，无依赖
- 支持ARM/ARM64/x86/x86_64架构
- 基于PLT/GOT修改，稳定性高
- 提供简洁的API接口
- 支持批量注册和取消Hook

### 4.2 API详解

```c
// xHook核心API

// 注册Hook
// param 1: 被Hook库名的正则表达式（匹配.so文件名）
// param 2: 被Hook的函数名
// param 3: 新函数地址
// param 4: 输出原始函数地址
int xhook_register(const char *pathname_regex_str,
                    const char *symbol,
                    void *new_func,
                    void **proto_func);

// 取消Hook
int xhook_unregister(const char *pathname_regex_str,
                     const char *symbol);

// 取消所有Hook
int xhook_unregister_all();

// 刷新Hook（重新扫描已加载的库）
int xhook_refresh(int async);

// 清除缓存
void xhook_clear();

// 启用/禁用调试日志
void xhook_enable_debug(int flag);

// 启用/禁用签名校验
void xhook_enable_sigsegv_protect(int flag);
```

### 4.3 使用方法

**CMakeLists.txt配置：**
```cmake
cmake_minimum_required(VERSION 3.4.1)

# 添加xHook源码
add_library(xhook SHARED
    src/xh_core.c
    src/xh_core.h
    src/xh_iter.c
    src/xh_iter.h
    src/xh_elf.c
    src/xh_elf.h
    src/xh_log.c
    src/xh_log.h
    src/xh_util.c
    src/xh_util.h
    src/xh_version.h
)

# 链接依赖库
target_link_libraries(xhook log)
```

**Android.mk配置：**
```makefile
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := xhook
LOCAL_SRC_FILES := \
    xhook/src/xh_core.c \
    xhook/src/xh_iter.c \
    xhook/src/xh_elf.c \
    xhook/src/xh_util.c \
    xhook/src/xh_log.c
LOCAL_C_INCLUDES := $(LOCAL_PATH)/xhook/src
LOCAL_EXPORT_C_INCLUDES := $(LOCAL_PATH)/xhook/src
LOCAL_LDLIBS := -llog
include $(BUILD_SHARED_LIBRARY)
```

**实战示例 - Hook libc的open函数：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdarg.h>
#include "xhook.h"

// 原始函数指针
static int (*orig_open)(const char *pathname, int flags, ...) = NULL;

// Hook函数
static int hook_open(const char *pathname, int flags, ...) {
    // 提取可变参数
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }

    // 记录调用信息
    __android_log_print(ANDROID_LOG_INFO, "XhookDemo",
                        "open(%s, %d, %d)", pathname, flags, mode);

    // 调用原始函数
    int fd = orig_open ? orig_open(pathname, flags, mode)
                       : open(pathname, flags, mode);

    __android_log_print(ANDROID_LOG_INFO, "XhookDemo",
                        "open() returned fd=%d", fd);

    return fd;
}

// 初始化Hook
void init_hooks() {
    // Hook所有.so中的open函数
    if (xhook_register(".*/lib\\.so$", "open",
                        (void *)hook_open, (void **)&orig_open) != 0) {
        __android_log_print(ANDROID_LOG_ERROR, "XhookDemo",
                            "Failed to hook open()");
    }

    // 刷新
    xhook_refresh(0);
}

// JNI接口供Java层调用
JNIEXPORT void JNICALL
Java_com_example_security_NativeHook_initXHook(JNIEnv *env, jobject thiz) {
    init_hooks();
}
```

**Hook多个函数的批量示例：**

```c
// Hook libc中的多个文件操作函数
static int (*orig_open)(const char *, int, ...) = NULL;
static int (*orig_close)(int) = NULL;
static ssize_t (*orig_read)(int, void *, size_t) = NULL;
static ssize_t (*orig_write)(int, const void *, size_t) = NULL;

static int hook_open(const char *pathname, int flags, ...) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] open(%s)", pathname);
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }
    return orig_open(pathname, flags, mode);
}

static int hook_close(int fd) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] close(%d)", fd);
    return orig_close(fd);
}

static ssize_t hook_read(int fd, void *buf, size_t count) {
    ssize_t ret = orig_read(fd, buf, count);
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] read(fd=%d, count=%zu) = %zd",
                        fd, count, ret);
    return ret;
}

static ssize_t hook_write(int fd, const void *buf, size_t count) {
    __android_log_print(ANDROID_LOG_INFO, "FileMonitor",
                        "[CALL] write(fd=%d, count=%zu)", fd, count);
    return orig_write(fd, buf, count);
}

void init_file_monitor() {
    xhook_register(".+\\.so$", "open",  (void *)hook_open,  (void **)&orig_open);
    xhook_register(".+\\.so$", "close", (void *)hook_close, (void **)&orig_close);
    xhook_register(".+\\.so$", "read",  (void *)hook_read,  (void **)&orig_read);
    xhook_register(".+\\.so$", "write", (void *)hook_write, (void **)&orig_write);
    xhook_refresh(0);
}
```

### 4.4 xHook使用注意事项

1. **符号匹配范围**：`pathname_regex_str`使用POSIX正则，需精确匹配库名
2. **线程安全**：Hook初始化应在程序启动早期完成，避免多线程竞争
3. **Hook顺序**：多次Hook同一符号时，需注意Hook链的顺序
4. **dlopen延迟加载**：对于运行时动态加载的库，需要调用`xhook_refresh()`重新扫描
5. **ART虚拟机内部函数**：xHook无法HookART内部函数（非PLT调用）

---

## 5. bhook框架

### 5.1 bhook简介

bhook（ByteHook）是字节跳动开源的Android PLT Hook框架，是xHook的继任者。相比xHook，bhook在性能、稳定性和功能上都有显著提升。

**项目地址：** https://github.com/bytedance/bhook

**核心特性：**
- **异步Hook**：支持异步刷新，不阻塞主线程
- **高性能**：优化了ELF解析算法，Hook速度更快
- **高稳定性**：完善的错误处理和回退机制
- **支持Hook链**：允许多个Hook同时作用于一个函数
- **线程安全**：内置线程安全机制
- **全面架构支持**：ARM/ARM64/x86/x86_64

### 5.2 bHook与xHook对比

| 特性 | xHook | bHook |
|------|-------|-------|
| 异步Hook | 不支持 | 支持 |
| Hook链 | 不支持 | 支持 |
| 稳定性 | 一般 | 更高（错误回退） |
| 性能 | 一般 | 更快 |
| 内存管理 | 手动 | 自动 |
| 架构支持 | ARM/ARM64/x86 | ARM/ARM64/x86/x86_64 |
| 维护状态 | 维护减少 | 活跃维护 |

### 5.3 bHook API详解

```c
#include "bytehook.h"

// 注册Hook（单个符号）
// param 1: 被Hook库的路径正则（NULL匹配所有）
// param 2: 被Hook函数名
// param 3: Hook回调函数
// param 4: 调用者地址（用于Hook链标识）
bytehook_stub_t bytehook_hook_single(
    const char *caller_path_regex,
    const char *callee_func_name,
    void *hook_func,
    void *arg);

// 注册Hook（所有匹配的符号）
bytehook_stub_t bytehook_hook_all(
    const char *caller_path_regex,
    const char *callee_func_name,
    void *hook_func,
    void *arg);

// 取消Hook
int bytehook_unhook(bytehook_stub_t stub);

// 取消所有Hook
int bytehook_unhook_all();

// 刷新（扫描新加载的库）
int bytehook_refresh(int async);

// 获取原始函数地址（用于Hook链中调用）
void *bytehook_get_orig(void *func, int *status);
```

### 5.4 使用示例

**Hook libc的malloc/free进行内存监控：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>
#include <android/log.h>
#include "bytehook.h"

#define TAG "BhookDemo"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// 全局统计
static size_t total_alloc = 0;
static size_t total_free = 0;
static int alloc_count = 0;

// Hook malloc
static void *hook_malloc(size_t size, void *arg) {
    // 获取原始函数并调用
    void *ptr = malloc(size);

    // 统计
    __sync_fetch_and_add(&total_alloc, size);
    __sync_fetch_and_add(&alloc_count, 1);

    // 大内存分配告警
    if (size > 1024 * 1024) {
        LOGI("[LargeAlloc] malloc(%zu) = %p", size, ptr);
    }

    return ptr;
}

// Hook free
static void hook_free(void *ptr, void *arg) {
    if (ptr) {
        __sync_fetch_and_add(&total_free, 1);
    }
    free(ptr);
}

// Hook calloc
static void *hook_calloc(size_t nmemb, size_t size, void *arg) {
    void *ptr = calloc(nmemb, size);
    __sync_fetch_and_add(&total_alloc, nmemb * size);
    LOGI("[calloc] nmemb=%zu, size=%zu, ptr=%p", nmemb, size, ptr);
    return ptr;
}

// 初始化内存监控
void init_memory_monitor() {
    // Hook所有库中的malloc
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc, NULL);
    bytehook_hook_single(NULL, "free",
                         (void *)hook_free, NULL);
    bytehook_hook_single(NULL, "calloc",
                         (void *)hook_calloc, NULL);

    LOGI("Memory monitor initialized");
}

// 获取统计报告
void get_memory_report() {
    LOGI("=== Memory Monitor Report ===");
    LOGI("Total allocated: %zu bytes", total_alloc);
    LOGI("Total freed: %zu", total_free);
    LOGI("Alloc count: %d", alloc_count);
}
```

**使用Hook链进行多重Hook：**

```c
// 第一个Hook：记录调用
static void *hook_malloc_log(size_t size, void *arg) {
    LOGI("[Hook1] malloc(%zu)", size);
    // 调用Hook链中的下一个函数
    void *(*orig)(size_t) = bytehook_get_orig(
        (void *)hook_malloc_log, NULL);
    return orig ? orig(size) : malloc(size);
}

// 第二个Hook：大小限制
static void *hook_malloc_limit(size_t size, void *arg) {
    if (size > 100 * 1024 * 1024) {  // 限制100MB
        LOGI("[Hook2] Blocked large malloc(%zu)", size);
        return NULL;
    }
    void *(*orig)(size_t) = bytehook_get_orig(
        (void *)hook_malloc_limit, NULL);
    return orig ? orig(size) : malloc(size);
}

// 注册Hook链
void init_chained_hook() {
    // 先注册的Hook在外层
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc_log, NULL);
    bytehook_hook_single(NULL, "malloc",
                         (void *)hook_malloc_limit, NULL);
}
```

### 5.5 异步Hook

bHook支持异步刷新机制，适用于需要Hook大量库的场景：

```c
// 异步刷新回调
static void on_refresh_done(int status, void *arg) {
    LOGI("Async refresh done, status=%d", status);
}

void init_async_hook() {
    // 注册Hook
    bytehook_hook_all(".*/libnative\\.so$", "open",
                      (void *)hook_open, NULL);

    // 异步刷新
    bytehook_refresh(1);  // 1 = async

    // 注册刷新完成回调
    bytehook_register_refresh_callback(on_refresh_done, NULL);
}
```

---

## 6. Dobby框架

### 6.1 Dobby简介

Dobby是一个跨架构的Inline Hook框架，支持ARM/ARM64/x86/x86_64架构。与xHook/bHook的PLT/GOT Hook不同，Dobby使用Inline Hook技术，可以Hook任意函数（包括内部函数），功能更强大。

**项目地址：** https://github.com/jmpews/Dobby

**核心特性：**
- **Inline Hook**：直接修改函数入口指令，可Hook任意函数
- **跨架构支持**：ARM/Thumb/ARM64/x86/x86_64
- **指令重定位**：内置完整的指令重定位引擎
- **Near Trampoline**：支持近距离跳转，减少跳转开销
- **Function Inline Hook**：支持完全内联Hook
- **兼容性好**：可与Frida、xHook等框架共存

### 6.2 Dobby API

```c
#include "dobby.h"

// Hook函数（核心API）
// param 1: 目标函数地址
// param 2: 新函数地址
// param 3: 输出原始函数地址（用于调用原始逻辑）
int DobbyHook(void *address,
              void *replace_call,
              void **origin_call);

// 取消Hook
int DobbyUnHook(void *address);

// 获取指令地址（用于Hook函数中间）
void *DobbyInstructionAddress(void *address);

// 注册调试回调
void DobbyDebugCallback(void (*callback)(void *address, const char *info));
```

### 6.3 使用示例

**Hook Native加密函数：**

```c
#include <stdio.h>
#include <string.h>
#include <android/log.h>
#include "dobby.h"

#define TAG "DobbyDemo"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// 假设这是目标应用中的加密函数
// 签名: int encrypt_data(const char *input, int input_len, char *output, int *output_len)
typedef int (*encrypt_data_t)(const char *, int, char *, int *);

static encrypt_data_t orig_encrypt = NULL;

// Hook函数
static int hook_encrypt_data(const char *input, int input_len,
                              char *output, int *output_len) {
    LOGI("[Hook] encrypt_data called");
    LOGI("[Hook] input_len=%d", input_len);

    // 打印输入数据
    if (input && input_len > 0) {
        char hex_buf[1024] = {0};
        for (int i = 0; i < input_len && i < 512; i++) {
            sprintf(hex_buf + i * 2, "%02x", (unsigned char)input[i]);
        }
        LOGI("[Hook] input(hex): %s", hex_buf);
    }

    // 调用原始函数
    int ret = orig_encrypt(input, input_len, output, output_len);

    // 打印输出数据
    if (output && output_len && *output_len > 0) {
        char hex_buf[1024] = {0};
        for (int i = 0; i < *output_len && i < 512; i++) {
            sprintf(hex_buf + i * 2, "%02x", (unsigned char)output[i]);
        }
        LOGI("[Hook] output(hex): %s", hex_buf);
    }
    LOGI("[Hook] encrypt_data returned %d", ret);

    return ret;
}

// 通过JNI获取目标函数地址并Hook
JNIEXPORT void JNICALL
Java_com_example_security_NativeHook_initDobby(JNIEnv *env, jobject thiz,
                                                jlong target_addr) {
    LOGI("Target function address: 0x%llx", target_addr);

    int ret = DobbyHook((void *)target_addr,
                        (void *)hook_encrypt_data,
                        (void **)&orig_encrypt);

    if (ret == 0) {
        LOGI("Dobby hook success!");
    } else {
        LOGI("Dobby hook failed! ret=%d", ret);
    }
}
```

**通过符号名Hook（需dlsym）：**

```c
#include <dlfcn.h>

// 通过符号名Hook
void hook_by_symbol(const char *lib_name, const char *symbol) {
    void *handle = dlopen(lib_name, RTLD_NOW);
    if (!handle) {
        LOGI("Failed to open %s: %s", lib_name, dlerror());
        return;
    }

    void *target = dlsym(handle, symbol);
    if (!target) {
        LOGI("Symbol %s not found", symbol);
        return;
    }

    LOGI("Found %s at %p", symbol, target);

    // 使用Dobby Hook
    int ret = DobbyHook(target,
                        (void *)hook_encrypt_data,
                        (void **)&orig_encrypt);

    LOGI("Dobby hook %s: %s", symbol, ret == 0 ? "success" : "failed");
}
```

**Hook libc的syscall wrapper：**

```c
// Hook ptrace（反调试）
typedef long (*orig_ptrace_t)(int request, pid_t pid,
                               void *addr, void *data);
static orig_ptrace_t orig_ptrace = NULL;

static long hook_ptrace(int request, pid_t pid,
                         void *addr, void *data) {
    LOGI("[Anti-Debug] ptrace(%d, %d) intercepted!", request, pid);
    // 返回0表示成功，欺骗反调试检测
    return 0;
}

void init_anti_debug_bypass() {
    void *ptrace_addr = dlsym(RTLD_DEFAULT, "ptrace");
    if (ptrace_addr) {
        DobbyHook(ptrace_addr,
                  (void *)hook_ptrace,
                  (void **)&orig_ptrace);
        LOGI("ptrace hooked at %p", ptrace_addr);
    }
}
```

### 6.4 Dobby编译集成

**CMakeLists.txt：**
```cmake
cmake_minimum_required(VERSION 3.4.1)

# 添加Dobby子模块
add_subdirectory(Dobby)

# 你的库
add_library(native_hook SHARED
    native_hook.cpp)

# 链接Dobby
target_link_libraries(native_hook
    dobby
    log
    dl)
```

---

## 7. Substrate框架

### 7.1 Cydia Substrate简介

Cydia Substrate（原名MobileSubstrate）是最早的移动平台Hook框架之一，最初为iOS越狱开发，后来推出了Android版本（Substrate for Android）。它提供了系统级的Hook能力，包括Java层和Native层。

**核心组件：**
- **Substrate**：核心Hook引擎
- **SubstrateBootstrap**：Zygote注入器
- **MSHookFunction**：Native层Inline Hook API
- **MS.hookMethod**：Java层Hook API

### 7.2 MSHookFunction

`MSHookFunction`是Substrate的Native层Hook核心API，使用Inline Hook技术：

```c
#include <substrate.h>

// MSHookFunction函数签名
// param 1: 目标函数地址
// param 2: 替换函数地址
// param 3: 输出原始函数指针
void MSHookFunction(void *symbol, void *replace, void **result);

// 示例：Hook libc的open函数
static int (*orig_open)(const char *pathname, int flags, ...) = NULL;

static int my_open(const char *pathname, int flags, ...) {
    // 获取可变参数
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }

    LOGI("Substrate: open(%s, %d, %d)", pathname, flags, mode);

    return orig_open(pathname, flags, mode);
}

// 初始化
void init_substrate_hook() {
    void *open_addr = dlsym(RTLD_DEFAULT, "open");
    MSHookFunction(open_addr,
                   (void *)my_open,
                   (void **)&orig_open);
}
```

### 7.3 Substrate for Android

在Android上使用Substrate需要Root权限和Substrate框架的安装：

**AndroidManifest.xml配置：**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.substratehook">

    <!-- 声明为Substrate扩展 -->
    <application>
        <meta-data android:name="com.saurik.substrate.meta"
                   android:value="com.example.substratehook.MainHook"/>
    </application>

    <!-- 需要注入的目标应用 -->
    <meta-data android:name="com.saurik.substrate.appid"
               android:value="com.target.app"/>
</manifest>
```

**Hook入口类：**
```java
package com.example.substratehook;

import com.saurik.substrate.MS;

public class MainHook {
    public static void initialize() {
        // Java层Hook
        MS.hookClassLoad("android.telephony.TelephonyManager",
            new MS.ClassLoadHook() {
                @Override
                public void classLoaded(Class<?> telephonyClass) {
                    // Hook getDeviceId
                    MS.hookMethod(telephonyClass,
                        "getDeviceId",
                        new MS.MethodAlterer() {
                        @Override
                        public Object invoked(Object obj,
                                               Object... args)
                                               throws Throwable {
                            // 返回自定义IMEI
                            return "123456789012345";
                        }
                    });
                }
            });
    }
}
```

### 7.4 Substrate与现代框架对比

| 特性 | Substrate | Frida | Dobby |
|------|-----------|-------|-------|
| 工作模式 | 需要框架安装 | 动态注入 | 库集成 |
| Root要求 | 需要 | 需要或Frida Server | 不需要 |
| 架构支持 | ARM/ARM64 | 全架构 | ARM/ARM64/x86 |
| Native Hook | MSHookFunction | Interceptor | DobbyHook |
| Java Hook | MS.hookMethod | Java API | 无 |
| 热重载 | 不支持 | 支持 | 不支持 |
| 跨平台 | iOS/Android | 全平台 | Android/iOS |
| 维护状态 | 停止维护 | 活跃 | 活跃 |

> 注意：Substrate目前已基本停止维护，在现代Android版本（Android 10+）上兼容性较差。建议优先使用Frida、Dobby或bHook等活跃维护的框架。

---

## 8. 实战案例

### 8.1 SSL Pinning绕过（Native层实现）

许多安全应用在Native层实现了SSL Pinning（证书固定），即使Hook了Java层的SSL相关类也无法绕过。以下是使用Dobby绕过Native层SSL Pinning的方案：

**目标分析：**
SSL Pinning在Native层通常通过以下方式实现：
1. 自定义X509证书验证函数（注册到SSL_CTX）
2. 直接调用OpenSSL的SSL_CTX_set_verify
3. 在TLS握手阶段验证服务器证书

**Hook方案：**

```c
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <android/log.h>
#include "dobby.h"

#define TAG "SSLBypass"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// OpenSSL函数类型定义
typedef int (*SSL_CTX_set_verify_t)(void *ctx, int mode,
                                      void *verify_callback);
typedef int (*SSL_get_verify_result_t)(void *ssl);
typedef long (*SSL_CTX_ctrl_t)(void *ctx, int cmd, long larg, void *parg);

static SSL_CTX_set_verify_t orig_SSL_CTX_set_verify = NULL;
static SSL_get_verify_result_t orig_SSL_get_verify_result = NULL;
static SSL_CTX_ctrl_t orig_SSL_CTX_ctrl = NULL;

// Hook SSL_CTX_set_verify - 禁用证书验证
static int hook_SSL_CTX_set_verify(void *ctx, int mode,
                                     void *verify_callback) {
    LOGI("[SSL] SSL_CTX_set_verify intercepted, mode=%d", mode);
    // 设置为SSL_VERIFY_NONE (0)
    return orig_SSL_CTX_set_verify(ctx, 0, NULL);
}

// Hook SSL_get_verify_result - 总是返回成功
static int hook_SSL_get_verify_result(void *ssl) {
    LOGI("[SSL] SSL_get_verify_result intercepted");
    // 0 = X509_V_OK
    return 0;
}

// Hook SSL_CTX_ctrl - 拦截证书pinning设置
static long hook_SSL_CTX_ctrl(void *ctx, int cmd, long larg, void *parg) {
    LOGI("[SSL] SSL_CTX_ctrl(cmd=%d)", cmd);
    // SSL_CTRL_SET_VERIFY_CERT_CB = 89 (某些版本)
    // 拦截证书验证回调设置
    if (cmd == 89) {  // 证书验证回调
        LOGI("[SSL] Blocking verify cert callback");
        return 0;
    }
    return orig_SSL_CTX_ctrl(ctx, cmd, larg, parg);
}

// BoringSSL的SSL_CTX_set_verify_proc Hook
typedef void (*SSL_CTX_set_verify_proc_t)(void *ctx,
    void (*verify_proc)(void *ssl, int *out_status));
static SSL_CTX_set_verify_proc_t orig_set_verify_proc = NULL;

static void hook_verify_proc(void *ssl, int *out_status) {
    LOGI("[BoringSSL] verify_proc intercepted");
    *out_status = 0;  // X509_V_OK
}

static void hook_SSL_CTX_set_verify_proc(void *ctx,
    void (*verify_proc)(void *ssl, int *out_status)) {
    LOGI("[BoringSSL] SSL_CTX_set_verify_proc intercepted");
    // 替换为我们的验证函数
    orig_set_verify_proc(ctx, hook_verify_proc);
}

// 初始化SSL Pinning绕过
void init_ssl_bypass() {
    void *handle = NULL;

    // 尝试加载BoringSSL（Android系统库）
    handle = dlopen("libssl.so", RTLD_NOW | RTLD_GLOBAL);
    if (!handle) {
        handle = dlopen("libboringssl.so", RTLD_NOW | RTLD_GLOBAL);
    }

    if (handle) {
        // Hook SSL_CTX_set_verify
        void *func = dlsym(handle, "SSL_CTX_set_verify");
        if (func) {
            DobbyHook(func, (void *)hook_SSL_CTX_set_verify,
                      (void **)&orig_SSL_CTX_set_verify);
            LOGI("Hooked SSL_CTX_set_verify at %p", func);
        }

        // Hook SSL_get_verify_result
        func = dlsym(handle, "SSL_get_verify_result");
        if (func) {
            DobbyHook(func, (void *)hook_SSL_get_verify_result,
                      (void **)&orig_SSL_get_verify_result);
            LOGI("Hooked SSL_get_verify_result at %p", func);
        }

        // Hook SSL_CTX_ctrl
        func = dlsym(handle, "SSL_CTX_ctrl");
        if (func) {
            DobbyHook(func, (void *)hook_SSL_CTX_ctrl,
                      (void **)&orig_SSL_CTX_ctrl);
            LOGI("Hooked SSL_CTX_ctrl at %p", func);
        }
    }

    // Hook应用自身的证书验证函数（通过符号搜索）
    // 需要根据具体应用分析确定函数地址
    LOGI("SSL Pinning bypass initialized");
}
```

**配合Frida使用的完整方案：**

```javascript
// frida脚本：结合Native Hook绕过SSL Pinning
function bypass_ssl_pinning() {
    // 1. Java层绕过
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');

        var TrustManager = Java.registerClass({
            name: 'com.mypackage.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {},
                getAcceptedIssuers: function() { return []; }
            }
        });

        var init = SSLContext.init.overload(
            '[Ljavax.net.ssl.KeyManager;',
            '[Ljavax.net.ssl.TrustManager;',
            'java.security.SecureRandom'
        );
        init.implementation = function(km, tm, sr) {
            init.call(this, km, [TrustManager.$new()], sr);
        };
    } catch(e) {
        console.log("Java bypass failed: " + e);
    }

    // 2. Native层绕过
    var ssl_set_verify = Module.findExportByName("libssl.so",
                                                   "SSL_CTX_set_verify");
    if (ssl_set_verify) {
        Interceptor.replace(ssl_set_verify, new NativeCallback(
            function(ctx, mode, cb) {
                // 设置SSL_VERIFY_NONE
                var SSL_VERIFY_NONE = 0;
                this(ctx, SSL_VERIFY_NONE, ptr(0));
            },
            'void', ['pointer', 'int', 'pointer']
        ));
    }

    // 3. Hook证书验证结果
    var get_verify_result = Module.findExportByName("libssl.so",
        "SSL_get_verify_result");
    if (get_verify_result) {
        Interceptor.replace(get_verify_result, new NativeCallback(
            function(ssl) {
                return 0; // X509_V_OK
            }, 'int', ['pointer']
        ));
    }
}

bypass_ssl_pinning();
```

### 8.2 游戏逆向修改Native函数

**场景：** 某手游在Native层计算伤害值，需要分析并修改伤害计算公式。

**步骤1：定位目标函数**

```bash
# 使用IDA Pro分析libgame.so
# 搜索关键字符串 "damage" "attack" "critical"
# 定位到 Java_com_game_Combat_calculateDamage 函数
```

**步骤2：分析函数签名**

```c
// IDA反编译结果
int Java_com_game_Combat_calculateDamage(
    JNIEnv *env, jobject thiz,
    int attacker_atk,    // 攻击力
    int defender_def,    // 防御力
    float crit_rate,     // 暴击率
    float crit_damage    // 暴击伤害倍率
) {
    // 伤害计算公式
    float base_damage = attacker_atk - defender_def * 0.5;
    if (base_damage < 1) base_damage = 1;

    // 暴击判定
    float rand_val = (float)rand() / RAND_MAX;
    if (rand_val < crit_rate) {
        base_damage *= crit_damage;
    }

    return (int)base_damage;
}
```

**步骤3：使用Dobby修改伤害计算**

```c
#include <stdlib.h>
#include <android/log.h>
#include "dobby.h"

#define TAG "GameHack"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// 原始函数指针
typedef int (*calculate_damage_t)(JNIEnv *, jobject,
                                    int, int, float, float);
static calculate_damage_t orig_calculate_damage = NULL;

// Hook函数 - 修改伤害为最大值
static int hook_calculate_damage(
    JNIEnv *env, jobject thiz,
    int attacker_atk, int defender_def,
    float crit_rate, float crit_damage
) {
    LOGI("[Game] Original: atk=%d, def=%d, crit_rate=%.2f, crit_dmg=%.2f",
         attacker_atk, defender_def, crit_rate, crit_damage);

    // 调用原始函数获取基础伤害
    int orig_damage = orig_calculate_damage(env, thiz,
        attacker_atk, defender_def, crit_rate, crit_damage);

    // 修改伤害值 - 乘以倍数
    int modified_damage = orig_damage * 100;  // 伤害放大100倍

    LOGI("[Game] orig_damage=%d, modified=%d",
         orig_damage, modified_damage);

    return modified_damage;
}

// 动态定位并Hook目标函数
JNIEXPORT void JNICALL
Java_com_example_gamehack_Hack_init(JNIEnv *env, jobject thiz) {
    // 方法1：通过JNI函数名规律定位
    // Java_com_game_Combat_calculateDamage
    void *target = NULL;

    // 在libgame.so中搜索符号
    void *handle = dlopen("libgame.so", RTLD_NOW);
    if (handle) {
        target = dlsym(handle,
            "Java_com_game_Combat_calculateDamage");
    }

    if (!target) {
        // 方法2：通过基址+偏移定位（需IDA分析偏移）
        // 需要先获取libgame.so的加载基址
        // target = (void *)(base_addr + 0x12345);
        LOGI("Target not found, need manual address");
        return;
    }

    LOGI("Target function at %p", target);

    int ret = DobbyHook(target,
                        (void *)hook_calculate_damage,
                        (void **)&orig_calculate_damage);

    LOGI("Dobby hook result: %d", ret);
}
```

**步骤4：获取库基址的方法**

```c
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>

// 方法1：通过/proc/self/maps
void *get_module_base(const char *module_name) {
    FILE *fp = fopen("/proc/self/maps", "r");
    if (!fp) return NULL;

    char line[512];
    void *base = NULL;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, module_name)) {
            sscanf(line, "%p", &base);
            break;
        }
    }
    fclose(fp);
    return base;
}

// 方法2：通过dl_iterate_phdr
#include <link.h>

static const char *g_target_module = NULL;
static void *g_module_base = NULL;

static int module_callback(struct dl_phdr_info *info,
                            size_t size, void *data) {
    if (strstr(info->dlpi_name, g_target_module)) {
        g_module_base = (void *)info->dlpi_addr;
        return 1;
    }
    return 0;
}

void *get_module_base2(const char *module_name) {
    g_target_module = module_name;
    g_module_base = NULL;
    dl_iterate_phdr(module_callback, NULL);
    return g_module_base;
}
```

### 8.3 反调试绕过

**常见反调试手段及Native Hook绕过：**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <dlfcn.h>
#include <android/log.h>
#include "dobby.h"

#define TAG "AntiAntiDebug"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)

// ============ 1. 绕过ptrace反调试 ============
typedef long (*ptrace_t)(int, pid_t, void *, void *);
static ptrace_t orig_ptrace = NULL;

static long hook_ptrace(int request, pid_t pid,
                         void *addr, void *data) {
    LOGI("[Bypass] ptrace(%d) intercepted", request);
    // PTRACE_TRACEME = 0, 返回0表示成功
    return 0;
}

// ============ 2. 绕过/proc/self/status检测 ============
typedef int (*open_t)(const char *, int, ...);
static open_t orig_open = NULL;

static int hook_open(const char *pathname, int flags, ...) {
    // 拦截对/proc/self/status、/proc/self/stat的访问
    if (strstr(pathname, "/proc/self/status") ||
        strstr(pathname, "/proc/self/stat")) {
        // 重定向到我们准备好的假文件
        return orig_open("/data/local/tmp/fake_status", flags);
    }
    // 拦截TracerPid检测
    if (strstr(pathname, "/proc/self/task")) {
        LOGI("[Bypass] Blocking access to %s", pathname);
    }

    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, mode_t);
        va_end(args);
    }
    return orig_open(pathname, flags, mode);
}

// ============ 3. 绕过/proc/self/wchan检测 ============
// 读取wchan如果是ptrace_stop表示被调试
typedef ssize_t (*read_t)(int, void *, size_t);
static read_t orig_read = NULL;

static ssize_t hook_read(int fd, void *buf, size_t count) {
    ssize_t ret = orig_read(fd, buf, count);
    // 检查是否是wchan内容
    if (ret > 0) {
        char *content = (char *)buf;
        if (ret < 64 && strstr(content, "ptrace")) {
            // 替换内容
            const char *fake = "0\n";
            size_t fake_len = strlen(fake);
            if (count >= fake_len) {
                memcpy(buf, fake, fake_len);
                ret = fake_len;
                LOGI("[Bypass] Replaced wchan content");
            }
        }
    }
    return ret;
}

// ============ 4. 绕过kill(0,0)检测 ============
typedef int (*kill_t)(pid_t, int);
static kill_t orig_kill = NULL;

static int hook_kill(pid_t pid, int sig) {
    LOGI("[Bypass] kill(%d, %d) intercepted", pid, sig);
    // kill(0, 0)用于检测调试器是否附加
    // 返回0表示没有信号被发送
    return 0;
}

// ============ 5. 绕过ptrace枚举子线程 ============
typedef int (*pthread_kill_t)(pthread_t, int);
static pthread_kill_t orig_pthread_kill = NULL;

static int hook_pthread_kill(pthread_t thread, int sig) {
    LOGI("[Bypass] pthread_kill(sig=%d) intercepted", sig);
    return 0;
}

// ============ 初始化所有反调试绕过 ============
void init_anti_debug_bypass() {
    LOGI("Initializing anti-debug bypass...");

    // Hook ptrace
    void *ptrace_addr = dlsym(RTLD_DEFAULT, "ptrace");
    if (ptrace_addr) {
        DobbyHook(ptrace_addr, (void *)hook_ptrace,
                  (void **)&orig_ptrace);
        LOGI("Hooked ptrace");
    }

    // Hook open
    void *open_addr = dlsym(RTLD_DEFAULT, "open");
    if (open_addr) {
        DobbyHook(open_addr, (void *)hook_open,
                  (void **)&orig_open);
        LOGI("Hooked open");
    }

    // Hook read
    void *read_addr = dlsym(RTLD_DEFAULT, "read");
    if (read_addr) {
        DobbyHook(read_addr, (void *)hook_read,
                  (void **)&orig_read);
        LOGI("Hooked read");
    }

    // Hook kill
    void *kill_addr = dlsym(RTLD_DEFAULT, "kill");
    if (kill_addr) {
        DobbyHook(kill_addr, (void *)hook_kill,
                  (void **)&orig_kill);
        LOGI("Hooked kill");
    }

    // Hook pthread_kill
    void *pthread_kill_addr = dlsym(RTLD_DEFAULT, "pthread_kill");
    if (pthread_kill_addr) {
        DobbyHook(pthread_kill_addr, (void *)hook_pthread_kill,
                  (void **)&orig_pthread_kill);
        LOGI("Hooked pthread_kill");
    }

    LOGI("Anti-debug bypass initialized");
}
```

**使用Frida的反调试绕过脚本（简化版）：**

```javascript
// Frida反调试绕过脚本
function bypass_anti_debug() {
    // 1. ptrace绕过
    var ptrace = Module.findExportByName("libc.so", "ptrace");
    if (ptrace) {
        Interceptor.replace(ptrace, new NativeCallback(
            function(request, pid, addr, data) {
                console.log("[Bypass] ptrace intercepted");
                return 0;
            }, 'long', ['int', 'int', 'pointer', 'pointer']
        ));
    }

    // 2. /proc/self/status 中的 TracerPid 绕过
    var fopen = Module.findExportByName("libc.so", "fopen");
    if (fopen) {
        Interceptor.attach(fopen, {
            onEnter: function(args) {
                var path = args[0].readUtf8String();
                if (path && path.indexOf("/proc/") >= 0) {
                    this.is_proc = true;
                    this.path = path;
                }
            },
            onLeave: function(retval) {
                if (this.is_proc) {
                    console.log("[Bypass] fopen: " + this.path);
                }
            }
        });
    }

    // 3. kill绕过
    var kill = Module.findExportByName("libc.so", "kill");
    if (kill) {
        Interceptor.replace(kill, new NativeCallback(
            function(pid, sig) {
                console.log("[Bypass] kill intercepted");
                return 0;
            }, 'int', ['int', 'int']
        ));
    }

    // 4. 检测调试器附加状态
    var fgets = Module.findExportByName("libc.so", "fgets");
    if (fgets) {
        Interceptor.attach(fgets, {
            onLeave: function(retval) {
                if (this.context) {
                    try {
                        var buf = this.args[0].readUtf8String();
                        if (buf && buf.indexOf("TracerPid") >= 0) {
                            // 替换TracerPid为0
                            var fake = "TracerPid:\t0\n";
                            this.args[0].writeUtf8String(fake);
                            console.log("[Bypass] Replaced TracerPid");
                        }
                    } catch(e) {}
                }
            }
        });
    }
}

bypass_anti_debug();
```

---

## 附录：工具快速参考

### Native Hook框架选型指南

| 需求场景 | 推荐框架 | 理由 |
|---------|---------|------|
| Hook外部库函数（PLT调用） | xHook/bHook | 稳定、简单、不需要Root |
| Hook任意函数（含内部函数） | Dobby | Inline Hook能力强 |
| 快速动态分析 | Frida | 热重载、JavaScript脚本 |
| 内存分配监控 | bHook | 异步Hook、Hook链 |
| SSL Pinning绕过 | Dobby + Frida | 需同时覆盖Java和Native层 |
| 游戏逆向 | Dobby | 可Hook内部函数 |
| 反调试绕过 | Dobby/Frida | 需Hook系统调用wrapper |
| 生产环境监控 | bHook | 高性能、高稳定性 |

### 常用命令速查

```bash
# 查看进程加载的库
cat /proc/<pid>/maps | grep ".so"

# 使用nm查看符号
nm -D libxxx.so | grep <symbol>

# 使用objdump查看PLT/GOT
objdump -R libxxx.so

# 使用readelf查看ELF信息
readelf -d libxxx.so
readelf -r libxxx.so

# Frida列出进程
frida-ps -U

# Frida附加进程
frida -U -p <pid> -l script.js

# Frida spawn模式
frida -U -f com.example.app -l script.js --no-pause
```

---

## 参考文献

1. xHook项目: https://github.com/iqiyi/xHook
2. bHook项目: https://github.com/bytedance/bhook
3. Dobby项目: https://github.com/jmpews/Dobby
4. Frida官方文档: https://frida.re/docs
5. ELF格式规范: https://refspecs.linuxbase.org/elf/elf.pdf
6. Android NDK开发指南: https://developer.android.com/ndk/guides
7. ARM Architecture Reference Manual: https://developer.arm.com/documentation
8. 《Android软件安全权威指南》——丰生强
9. 《加密与解密（第四版）》——段钢
