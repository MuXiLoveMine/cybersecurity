# PLT/GOT Hook技术

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

---

