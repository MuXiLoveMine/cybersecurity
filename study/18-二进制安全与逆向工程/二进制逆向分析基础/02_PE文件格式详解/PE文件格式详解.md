# PE文件格式详解

PE（Portable Executable）是Windows操作系统的可执行文件格式，其扩展名包括.exe、.dll、.sys、.ocx等。理解PE格式是Windows平台逆向分析的基础。

### 1.1 PE文件整体布局

```
+---------------------------+  文件起始
|    DOS MZ Header          |  64字节，固定大小
+---------------------------+
|    DOS Stub               |  变长，实模式下的提示程序
+---------------------------+
|    PE Signature           |  4字节 "PE\0\0"
+---------------------------+
|    COFF File Header       |  20字节，固定大小
+---------------------------+
|    Optional Header        |  PE32: 224字节 / PE32+: 240字节
+---------------------------+
|    Section Table          |  每项40字节，节区数量由File Header指定
+---------------------------+
|    Sections (.text)       |
|    Sections (.data)       |  各节区的实际数据
|    Sections (.rsrc)       |
|    ...                    |
+---------------------------+  文件结束
```

### 1.2 DOS头

DOS头位于文件最开始，共64字节。在32/64位PE文件中，它的主要作用是定位PE签名。

**IMAGE_DOS_HEADER结构（C语言表示）：**

```c
typedef struct _IMAGE_DOS_HEADER {
    WORD e_magic;      // MZ签名 0x5A4D ("MZ")
    WORD e_cblp;       // 最后一页的字节数
    WORD e_cp;         // 文件中的页数
    WORD e_crlc;       // 重定位项数
    WORD e_cparhdr;    // 头部大小（以段落为单位）
    WORD e_minalloc;   // 所需最小额外段落数
    WORD e_maxalloc;   // 所需最大额外段落数
    WORD e_ss;         // 初始SS
    WORD e_sp;         // 初始SP
    WORD e_csum;       // 校验和
    WORD e_ip;         // 初始IP
    WORD e_cs;         // 初始CS
    WORD e_lfarlc;     // 重定位表偏移
    WORD e_ovno;       // 覆盖号
    WORD e_res[4];      // 保留字
    WORD e_oemid;       // OEM标识符
    WORD e_oeminfo;     // OEM信息
    WORD e_res2[10];    // 保留字
    LONG e_lfanew;      // PE签名的文件偏移 ★关键字段
} IMAGE_DOS_HEADER;
```

**关键字段解析：**
- `e_magic`：固定为0x5A4D（小端存储为"MZ"），用于标识DOS/PE文件
- `e_lfanew`：指向PE签名的文件偏移，通常为0x80或更大值，是定位PE头的核心字段

**Python解析DOS头示例：**

```python
import struct

def parse_dos_header(data):
    """解析PE文件的DOS头"""
    if len(data) < 64:
        return None
    
    # 解包DOS头结构
    dos_header = struct.unpack_from('<2sHHHHHHHHHHHHHHHHHHH4xHH10xI', data, 0)
    
    result = {
        'e_magic': dos_header[0],       # MZ签名
        'e_lfanew': dos_header[-1],     # PE签名偏移
    }
    
    # 验证MZ签名
    if result['e_magic'] != b'MZ':
        print("[!] 无效的DOS头：缺少MZ签名")
        return None
    
    print(f"[+] DOS头解析成功")
    print(f"    MZ签名: {result['e_magic']}")
    print(f"    PE偏移: 0x{result['e_lfanew']:08X}")
    
    return result
```

### 1.3 PE头

PE头由PE签名、COFF文件头和可选头三部分组成。

**PE签名：** 4字节，固定为"PE\0\0"（0x00004550）

**IMAGE_FILE_HEADER（COFF文件头）结构：**

```c
typedef struct _IMAGE_FILE_HEADER {
    WORD Machine;              // 目标机器类型
    WORD NumberOfSections;     // 节区数量
    DWORD TimeDateStamp;       // 时间戳
    DWORD PointerToSymbolTable;// 符号表偏移（COFF格式，通常为0）
    DWORD NumberOfSymbols;     // 符号数量
    WORD SizeOfOptionalHeader; // 可选头大小
    WORD Characteristics;      // 文件属性标志
} IMAGE_FILE_HEADER;
```

**Machine字段常见值：**

| 值 | 常量 | 说明 |
|----|------|------|
| 0x014C | IMAGE_FILE_MACHINE_I386 | x86 |
| 0x8664 | IMAGE_FILE_MACHINE_AMD64 | x64 |
| 0x01C0 | IMAGE_FILE_MACHINE_ARM | ARM (little endian) |
| 0xAA64 | IMAGE_FILE_MACHINE_ARM64 | ARM64 |

**Characteristics标志位：**

| 位 | 常量 | 说明 |
|----|------|------|
| 0x0002 | IMAGE_FILE_EXECUTABLE_IMAGE | 可执行文件（非DLL） |
| 0x0008 | IMAGE_FILE_LINE_NUMS_STRIPPED | 行号信息已移除 |
| 0x0100 | IMAGE_FILE_32BIT_MACHINE | 32位机器 |
| 0x2000 | IMAGE_FILE_DLL | DLL文件 |
| 0x4000 | IMAGE_FILE_SYSTEM | 系统文件 |

**IMAGE_OPTIONAL_HEADER关键结构（PE32）：**

```c
typedef struct _IMAGE_OPTIONAL_HEADER {
    WORD Magic;                    // 0x10B=PE32, 0x20B=PE32+(64位)
    BYTE MajorLinkerVersion;       // 链接器主版本
    BYTE MinorLinkerVersion;       // 链接器次版本
    DWORD SizeOfCode;              // 代码段总大小
    DWORD SizeOfInitializedData;   // 已初始化数据大小
    DWORD SizeOfUninitializedData; // 未初始化数据大小
    DWORD AddressOfEntryPoint;     // 入口点(RVA) ★关键
    DWORD BaseOfCode;              // 代码段基址(RVA)
    DWORD BaseOfData;              // 数据段基址(RVA)
    DWORD ImageBase;               // 映像基址 ★关键
    DWORD SectionAlignment;        // 节区对齐
    DWORD FileAlignment;           // 文件对齐
    WORD MajorOperatingSystemVersion;
    WORD MinorOperatingSystemVersion;
    WORD MajorImageVersion;
    WORD MinorImageVersion;
    WORD MajorSubsystemVersion;
    WORD MinorSubsystemVersion;
    DWORD Win32VersionValue;
    DWORD SizeOfImage;             // 映像总大小
    DWORD SizeOfHeaders;            // 头部大小
    DWORD CheckSum;                 // 校验和
    WORD Subsystem;                 // 子系统类型
    WORD DllCharacteristics;         // DLL特性标志
    DWORD SizeOfStackReserve;        // 栈保留大小
    DWORD SizeOfStackCommit;        // 栈提交大小
    DWORD SizeOfHeapReserve;        // 堆保留大小
    DWORD SizeOfHeapCommit;         // 堆提交大小
    DWORD LoaderFlags;
    DWORD NumberOfRvaAndSizes;       // 数据目录项数
    IMAGE_DATA_DIRECTORY DataDirectory[16]; // 数据目录 ★关键
} IMAGE_OPTIONAL_HEADER32;
```

**关键安全相关字段（DllCharacteristics）：**

| 位 | 常量 | 说明 |
|----|------|------|
| 0x0020 | IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA | 高熵ASLR |
| 0x0040 | IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE | ASLR |
| 0x0080 | IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY | 强制完整性检查 |
| 0x0100 | IMAGE_DLLCHARACTERISTICS_NX_COMPAT | DEP/NX |
| 0x4000 | IMAGE_DLLCHARACTERISTICS_GUARD_CF | CFG |
| 0x8000 | IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE | 终端服务器感知 |

**数据目录（DataDirectory）16项：**

| 索引 | 名称 | 说明 |
|------|------|------|
| 0 | Export Table | 导出表 |
| 1 | Import Table | 导入表 |
| 2 | Resource Table | 资源表 |
| 3 | Exception Table | 异常表 |
| 4 | Certificate Table | 证书表 |
| 5 | Base Relocation Table | 基址重定位表 |
| 6 | Debug | 调试信息 |
| 7 | Architecture | 保留 |
| 8 | Global Ptr | 保留 |
| 9 | TLS Table | 线程局部存储 |
| 10 | Load Config Table | 加载配置表 |
| 11 | Bound Import | 绑定导入表 |
| 12 | IAT | 导入地址表 |
| 13 | Delay Import Descriptor | 延迟导入表 |
| 14 | CLR Runtime Header | CLR运行时头 |
| 15 | Reserved | 保留 |

### 1.4 节表

节表紧跟在可选头之后，每个节表项描述对应节区的属性。

**IMAGE_SECTION_HEADER结构：**

```c
typedef struct _IMAGE_SECTION_HEADER {
    BYTE Name[8];               // 节区名称（最长8字符）
    union {
        DWORD PhysicalAddress;
        DWORD VirtualSize;      // 虚拟大小
    } Misc;
    DWORD VirtualAddress;       // 虚拟地址(RVA)
    DWORD SizeOfRawData;        // 文件中的原始大小
    DWORD PointerToRawData;     // 文件中的偏移
    DWORD PointerToRelocations; // 重定位项偏移
    DWORD PointerToLinenumbers;// 行号信息偏移
    WORD NumberOfRelocations;   // 重定位项数
    WORD NumberOfLinenumbers;   // 行号数
    DWORD Characteristics;      // 节区属性 ★关键
} IMAGE_SECTION_HEADER;
```

**常见节区说明：**

| 节名 | 内容 | 典型属性 |
|------|------|---------|
| .text | 程序代码 | 可读+可执行 |
| .data | 已初始化数据 | 可读+可写 |
| .rdata | 只读数据 | 只读 |
| .bss | 未初始化数据 | 可读+可写 |
| .rsrc | 资源 | 只读 |
| .reloc | 重定位信息 | 只读 |
| .tls | 线程局部存储 | 可读+可写 |
| .gfids | CFG信息 | 只读 |
| .idata | 导入表 | 可读+可写(IAT) |

**节区属性标志位（Characteristics）：**

| 值 | 常量 | 说明 |
|----|------|------|
| 0x00000020 | IMAGE_SCN_CNT_CODE | 包含代码 |
| 0x00000040 | IMAGE_SCN_CNT_INITIALIZED_DATA | 包含已初始化数据 |
| 0x00000080 | IMAGE_SCN_CNT_UNINITIALIZED_DATA | 包含未初始化数据 |
| 0x20000000 | IMAGE_SCN_MEM_EXECUTE | 可执行 |
| 0x40000000 | IMAGE_SCN_MEM_READ | 可读 |
| 0x80000000 | IMAGE_SCN_MEM_WRITE | 可写 |

**RVA与文件偏移转换：**

RVA（Relative Virtual Address）是相对虚拟地址，需要转换为文件偏移才能在文件中定位。

```
文件偏移 = RVA - 节区VirtualAddress + 节区PointerToRawData
```

转换步骤：
1. 找到包含该RVA的节区（VirtualAddress <= RVA < VirtualAddress + VirtualSize）
2. 计算节内偏移：offset_in_section = RVA - Section.VirtualAddress
3. 文件偏移 = Section.PointerToRawData + offset_in_section

```python
def rva_to_offset(rva, sections):
    """将RVA转换为文件偏移"""
    for section in sections:
        section_start = section['VirtualAddress']
        section_end = section_start + section['VirtualSize']
        if section_start <= rva < section_end:
            offset = rva - section_start + section['PointerToRawData']
            return offset
    return None  # RVA不在任何节区内，可能在头部
```

### 1.5 导入表

导入表记录了程序调用的所有外部DLL函数，是逆向分析中定位关键功能的重要依据。

**IMAGE_IMPORT_DESCRIPTOR结构：**

```c
typedef struct _IMAGE_IMPORT_DESCRIPTOR {
    union {
        DWORD Characteristics;
        DWORD OriginalFirstThunk;   // 原始Thunk（INT）的RVA
    };
    DWORD TimeDateStamp;            // 时间戳
    DWORD ForwarderChain;           // 转发链
    DWORD Name;                      // DLL名称字符串的RVA
    DWORD FirstThunk;               // 第一Thunk（IAT）的RVA
} IMAGE_IMPORT_DESCRIPTOR;
```

**导入机制详解：**

1. **INT（Import Name Table）**：OriginalFirstThunk指向的数组，每项是一个RVA，指向IMAGE_IMPORT_BY_NAME结构（包含hint和函数名）
2. **IAT（Import Address Table）**：FirstThunk指向的数组，加载前与INT相同，加载后被写入函数实际地址
3. **绑定导入**：如果IAT在文件中已被绑定（预先填充），可以加速加载

**IMAGE_IMPORT_BY_NAME结构：**

```c
typedef struct _IMAGE_IMPORT_BY_NAME {
    WORD Hint;    // 函数导出序号提示
    BYTE Name[1]; // 函数名（以null结尾的变长字段）
} IMAGE_IMPORT_BY_NAME;
```

**Python解析导入表示例：**

```python
def parse_import_table(data, pe_header, sections):
    """解析PE文件的导入表"""
    # 获取导入表的数据目录
    import_dir_rva = pe_header['DataDirectory'][1]['VirtualAddress']
    import_dir_size = pe_header['DataDirectory'][1]['Size']
    
    if import_dir_rva == 0:
        print("[*] 无导入表")
        return []
    
    # RVA转文件偏移
    offset = rva_to_offset(import_dir_rva, sections)
    if offset is None:
        return []
    
    imports = []
    while True:
        # 读取IMAGE_IMPORT_DESCRIPTOR（20字节）
        if offset + 20 > len(data):
            break
        
        descriptor = struct.unpack_from('<IIIII', data, offset)
        original_thunk = descriptor[0]
        name_rva = descriptor[3]
        first_thunk = descriptor[4]
        
        # 全零表示导入表结束
        if original_thunk == 0 and name_rva == 0:
            break
        
        # 读取DLL名称
        name_offset = rva_to_offset(name_rva, sections)
        if name_offset:
            dll_name = read_cstring(data, name_offset)
        else:
            dll_name = "未知"
        
        # 读取导入函数列表
        thunk = original_thunk if original_thunk else first_thunk
        func_offset = rva_to_offset(thunk, sections)
        
        while func_offset:
            if pe_header['Magic'] == 0x20B:  # PE32+
                thunk_data = struct.unpack_from('<Q', data, func_offset)[0]
                func_offset += 8
            else:  # PE32
                thunk_data = struct.unpack_from('<I', data, func_offset)[0]
                func_offset += 4
            
            if thunk_data == 0:
                break
            
            # 检查是否为序号导入
            if thunk_data & 0x80000000:  # 最高位为1
                ordinal = thunk_data & 0xFFFF
                imports.append({
                    'dll': dll_name,
                    'function': f'序号#{ordinal}',
                    'type': 'ordinal'
                })
            else:  # 名称导入
                func_name_rva = thunk_data
                func_name_offset = rva_to_offset(func_name_rva, sections)
                if func_name_offset:
                    # 跳过2字节的Hint
                    func_name = read_cstring(data, func_name_offset + 2)
                    imports.append({
                        'dll': dll_name,
                        'function': func_name,
                        'type': 'name'
                    })
        
        offset += 20  # 下一个描述符
    
    return imports
```

### 1.6 导出表

导出表用于DLL文件，记录该DLL对外提供的函数。

**IMAGE_EXPORT_DIRECTORY结构：**

```c
typedef struct _IMAGE_EXPORT_DIRECTORY {
    DWORD Characteristics;      // 保留
    DWORD TimeDateStamp;       // 时间戳
    WORD MajorVersion;
    WORD MinorVersion;
    DWORD Name;                 // DLL名称的RVA
    DWORD Base;                 // 导出函数起始序号
    DWORD NumberOfFunctions;    // 导出函数数量
    DWORD NumberOfNames;        // 有名称的导出函数数量
    DWORD AddressOfFunctions;    // 函数地址表(EAT)的RVA
    DWORD AddressOfNames;        // 函数名表(ENT)的RVA
    DWORD AddressOfNameOrdinals; // 序号表的RVA
} IMAGE_EXPORT_DIRECTORY;
```

**导出函数查找流程：**
1. 在ENT（名称表）中搜索函数名，获取索引
2. 用该索引在序号表中获取序号
3. 用序号在EAT（地址表）中获取函数RVA

### 1.7 资源表与重定位表

**资源表**采用树形结构，分为三层：
- 资源类型层（Type）：RT_CURSOR=1, RT_BITMAP=2, RT_DIALOG=5, RT_STRING=6, RT_VERSION=16, RT_MANIFEST=24等
- 资源名称层（Name）
- 资源语言层（Language）

**基址重定位表**记录了需要修正的地址，当模块无法加载到首选基址时使用。重定位项以页（4KB）为单位分组。

---

---

## 📋 内容审核与补充建议

> 针对「PE文件格式详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
