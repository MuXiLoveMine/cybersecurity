# ELF文件格式详解

ELF（Executable and Linkable Format）是Unix/Linux系统的标准可执行文件格式，同样用于目标文件(.o)、共享库(.so)和core dump文件。

### 2.1 ELF整体布局

```
+---------------------------+
|    ELF Header             |  52字节(32位) / 64字节(64位)
+---------------------------+
|    Program Header Table   |  描述段(Segment)信息
+---------------------------+
|    Section .text          |
|    Section .rodata        |  各节区数据
|    Section .data          |
|    Section .bss           |
|    ...                    |
+---------------------------+
|    Section Header Table   |  描述节区(Section)信息
+---------------------------+
```

### 2.2 ELF头

**32位ELF头结构：**

```c
typedef struct {
    unsigned char e_ident[16];  // ELF标识
    Elf32_Half e_type;          // 文件类型
    Elf32_Half e_machine;       // 目标机器
    Elf32_Word e_version;       // ELF版本
    Elf32_Addr e_entry;         // 入口点地址 ★关键
    Elf32_Off e_phoff;          // 程序头表偏移
    Elf32_Off e_shoff;          // 节区头表偏移
    Elf32_Word e_flags;         // 处理器特定标志
    Elf32_Half e_ehsize;        // ELF头大小
    Elf32_Half e_phentsize;     // 程序头表项大小
    Elf32_Half e_phnum;         // 程序头表项数
    Elf32_Half e_shentsize;     // 节区头表项大小
    Elf32_Half e_shnum;         // 节区头表项数
    Elf32_Half e_shstrndx;      // 节区名字符串表索引
} Elf32_Ehdr;
```

**e_ident魔数：**

| 偏移 | 值 | 说明 |
|------|-----|------|
| 0-3 | 0x7F 'E' 'L' 'F' | 魔数标识 |
| 4 | EI_CLASS | 1=32位, 2=64位 |
| 5 | EI_DATA | 1=小端, 2=大端 |
| 6 | EI_VERSION | ELF版本(=1) |
| 7 | EI_OSABI | 操作系统ABI |
| 8-15 | EI_PAD | 保留 |

**e_type文件类型：**

| 值 | 常量 | 说明 |
|----|------|------|
| 0 | ET_NONE | 无类型 |
| 1 | ET_REL | 可重定位文件(.o) |
| 2 | ET_EXEC | 可执行文件 |
| 3 | ET_DYN | 共享库(.so) |
| 4 | ET_CORE | Core dump文件 |

### 2.3 程序头表

程序头描述了加载到内存时的段信息。

```c
typedef struct {
    Elf32_Word p_type;     // 段类型
    Elf32_Off p_offset;   // 文件中的偏移
    Elf32_Addr p_vaddr;   // 虚拟地址
    Elf32_Addr p_paddr;   // 物理地址（通常忽略）
    Elf32_Word p_filesz;  // 文件中的大小
    Elf32_Word p_memsz;   // 内存中的大小
    Elf32_Word p_flags;   // 段标志
    Elf32_Word p_align;   // 对齐
} Elf32_Phdr;
```

**p_type常见值：**

| 值 | 常量 | 说明 |
|----|------|------|
| 0 | PT_NULL | 无效段 |
| 1 | PT_LOAD | 需加载的段 |
| 2 | PT_DYNAMIC | 动态链接信息 |
| 3 | PT_INTERP | 解释器路径 |
| 4 | PT_NOTE | 辅助信息 |
| 6 | PT_PHDR | 程序头表自身 |
| 0x6474e550 | PT_GNU_EH_FRAME | 异常处理帧 |
| 0x6474e551 | PT_GNU_STACK | 栈属性（可执行性） |
| 0x6474e552 | PT_GNU_RELRO | 只读重定位 |

### 2.4 节区详解

**常见节区：**

| 节名 | 类型 | 说明 |
|------|------|------|
| .text | SHT_PROGBITS | 可执行代码 |
| .rodata | SHT_PROGBITS | 只读数据 |
| .data | SHT_PROGBITS | 已初始化数据 |
| .bss | SHT_NOBITS | 未初始化数据 |
| .got | SHT_PROGBITS | 全局偏移表 |
| .got.plt | SHT_PROGBITS | PLT的GOT |
| .plt | SHT_PROGBITS | 过程链接表 |
| .rela.plt | SHT_RELA | PLT重定位 |
| .rela.dyn | SHT_RELA | 数据重定位 |
| .dynamic | SHT_DYNAMIC | 动态链接信息 |
| .dynsym | SHT_DYNSYM | 动态符号表 |
| .dynstr | SHT_STRTAB | 动态字符串表 |
| .symtab | SHT_SYMTAB | 符号表 |
| .strtab | SHT_STRTAB | 字符串表 |
| .init | SHT_PROGBITS | 初始化代码 |
| .fini | SHT_PROGBITS | 终结代码 |
| .init_array | SHT_INIT_ARRAY | 初始化函数指针数组 |
| .fini_array | SHT_FINI_ARRAY | 终结函数指针数组 |

### 2.5 动态链接机制

**PLT/GOT工作原理：**

1. 程序调用外部函数时，跳转到PLT表项
2. PLT表项跳转到GOT表中存储的地址
3. 首次调用时，GOT表项指向PLT中的resolver代码
4. Resolver调用`_dl_runtime_resolve`解析函数地址
5. 解析后将真实地址写入GOT表
6. 后续调用直接通过GOT跳转到真实地址

```
代码中调用 printf:
    call printf@plt      -> 跳转到 .plt 中 printf 的表项

.plt 中 printf 表项:
    jmp *printf@GOTPLT   -> 第一次: 指向 resolver
                          -> 后续: 指向 printf 真实地址
```

**.dynamic节结构：**

```c
typedef struct {
    Elf32_Sword d_tag;    // 标签类型
    union {
        Elf32_Word d_val; // 值
        Elf32_Addr d_ptr;  // 指针
    } d_un;
} Elf32_Dyn;
```

关键d_tag：DT_NEEDED（依赖的共享库）、DT_PLTGOT（GOT地址）、DT_JMPREL（PLT重定位表）等。

---

---

