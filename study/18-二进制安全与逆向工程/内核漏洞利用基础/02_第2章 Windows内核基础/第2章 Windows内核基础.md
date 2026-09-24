# 第2章 Windows内核基础

### 2.1 Windows内核架构

Windows NT内核是一个混合内核，兼具宏内核的性能和微内核的模块化设计。

#### 2.1.1 NTOS内核组件

`ntoskrnl.exe`是Windows内核的核心文件，包含以下主要组件：

**内核层（Kernel Layer）**：
- 线程调度与上下文切换
- 中断与异常处理
- 同步原语（自旋锁、互斥量、事件等）
- 定时器管理
- 多处理器支持

**执行体层（Executive Layer）**：
- **进程管理器**：进程/线程创建与销毁
- **内存管理器**：虚拟内存管理、物理内存管理、页文件
- **I/O管理器**：I/O请求包（IRP）处理、设备驱动管理
- **对象管理器**：内核对象的创建、管理与安全
- **配置管理器**：注册表管理
- **安全引用监视器（SRM）**：安全策略执行
- **即插即用管理器**：设备枚举与驱动加载
- **电源管理器**：电源策略管理

#### 2.1.2 硬件抽象层（HAL）

HAL（`hal.dll`）的作用是屏蔽底层硬件差异，为内核提供统一的硬件访问接口。HAL处理：
- 中断控制器（APIC/IOAPIC）编程
- 系统计时器
- DMA操作
- 多处理器间通信（IPI）
- 总线适配器抽象

这使得Windows内核可以在不同硬件平台上运行，而无需大幅修改内核代码。

#### 2.1.3 驱动模型

Windows驱动程序运行在内核态，是内核攻击面的重要组成部分。

**WDM（Windows Driver Model）**：
- 分层驱动模型，由上层到下层依次为：过滤驱动 → 功能驱动 → 总线驱动
- 每个驱动创建设备对象（DEVICE_OBJECT），设备对象形成设备栈
- I/O请求以IRP（I/O Request Packet）的形式在设备栈中传递
- 驱动的入口点是`DriverEntry`，负责创建设备对象和设置分发函数

**WDF（Windows Driver Framework）**：
- 基于WDM的高级框架，分为KMDF（内核态）和UMDF（用户态）
- 封装了大量WDM的底层细节，简化驱动开发
- 提供即插即用、电源管理、I/O队列等默认实现
- UMDF驱动运行在用户态，降低了漏洞影响范围

### 2.2 系统调用机制

#### 2.2.1 系统调用分发

Windows系统调用的分发机制：

1. 用户态程序调用`ntdll.dll`中的存根函数（如`NtReadFile`）
2. 存根函数将系统调用号（SSDT索引）放入eax寄存器
3. x86_32使用`sysenter`指令，x86_64使用`syscall`指令进入内核
4. 内核的系统调用入口（`KiSystemCall64`/`KiFastCallEntry`）保存上下文
5. 根据SSDT（System Service Descriptor Table）查找处理函数地址
6. 调用对应的内核服务函数（如`NtReadFile`的内核实现）

#### 2.2.2 SSDT结构

SSDT是一个函数指针表，定义如下（简化）：

```c
typedef struct _SYSTEM_SERVICE_TABLE {
    PULONG ServiceTableBase;       // 服务函数地址表基址
    PULONG ServiceCounterTableBase; // 服务计数器表（仅Checked Build）
    ULONG NumberOfServices;         // 服务函数数量
    PUCHAR ParamTableBase;          // 参数表（每个函数的参数总长度，以字节为单位）
} SYSTEM_SERVICE_TABLE, *PSYSTEM_SERVICE_TABLE;
```

Windows有两个主要的系统服务表：
- **KeServiceDescriptorTable**：NT系统服务（Nt*系列函数）
- **KeServiceDescriptorTableShadow**：包含NT和Win32k系统服务（用于GUI线程）

**注意**：在较新的Windows版本中，SSDT的地址受到保护，且每个函数的地址经过随机化处理。

#### 2.2.3 系统调用参数传递

- **x86_32**：参数通过用户栈传递，内核从用户栈复制参数到内核栈
- **x86_64**：前4个参数通过rcx、rdx、r8、r9寄存器传递，其余通过栈传递
- 系统调用参数在内核中被验证（ProbeForRead/ProbeForWrite），确保用户态缓冲区的合法性

### 2.3 内核对象与句柄表

#### 2.3.1 内核对象体系

Windows执行体通过对象管理器统一管理各种内核资源。常见的内核对象类型包括：

- **进程对象（EPROCESS）**：表示一个进程
- **线程对象（ETHREAD）**：表示一个线程
- **文件对象（FILE_OBJECT）**：表示一个打开的文件
- **事件对象（KEVENT）**：用于线程同步
- **互斥量对象（KMUTANT）**：用于互斥访问
- **信号量对象（KSEMAPHORE）**：用于资源计数
- **令牌对象（TOKEN）**：表示进程/线程的安全上下文
- **注册表键对象（CM_KEY_BODY）**：表示打开的注册表项

每个内核对象都有：
- **对象头（OBJECT_HEADER）**：包含对象类型、引用计数、名称、安全描述符等元信息
- **对象体**：具体类型的数据结构

#### 2.3.2 句柄表机制

用户态通过**句柄（Handle）**访问内核对象，而不是直接使用内核指针。

句柄表的工作原理：
1. 每个进程有一个句柄表（Handle Table）
2. 句柄表是一个数组，每个条目（HANDLE_TABLE_ENTRY）包含一个内核对象指针和访问权限掩码
3. 用户态的HANDLE值本质上是句柄表的索引（经过编码）
4. 当调用`CreateFile`、`OpenProcess`等API时，内核创建对象并在句柄表中分配条目
5. 当调用`CloseHandle`时，减少对象引用计数，释放句柄表条目

**安全意义**：
- 句柄表隔离了用户态和内核态，防止用户态直接操纵内核对象
- 每个句柄有独立的访问权限（如PROCESS_ALL_ACCESS vs PROCESS_QUERY_INFORMATION）
- 内核漏洞利用中，常通过伪造句柄表条目来实现权限提升

### 2.4 驱动开发基础

#### 2.4.1 驱动入口与卸载

驱动程序的入口函数是`DriverEntry`，类似于用户态程序的`main`函数：

```c
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
) {
    // 设置驱动卸载函数
    DriverObject->DriverUnload = MyDriverUnload;
    
    // 设置IRP分发函数
    DriverObject->MajorFunction[IRP_MJ_CREATE] = MyCreateDispatch;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = MyCloseDispatch;
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = MyDeviceIoControlDispatch;
    
    // 创建设备对象和符号链接
    // ...
    
    return STATUS_SUCCESS;
}
```

#### 2.4.2 IRP与IOCTL

I/O请求包（IRP）是Windows内核I/O机制的核心。用户态程序通过`DeviceIoControl`与驱动通信，这会产生一个`IRP_MJ_DEVICE_CONTROL`类型的IRP。

IOCTL代码（控制码）的结构：
```
[设备类型(16位) | 功能码(12位) | 传输类型(2位) | 所需访问(2位)]
```

传输类型（最常被利用的部分）：
- **METHOD_BUFFERED**：系统将输入输出缓冲区都复制一份，最安全
- **METHOD_IN_DIRECT** / **METHOD_OUT_DIRECT**：使用MDL直接映射用户缓冲区
- **METHOD_NEITHER**：驱动直接使用用户态虚拟地址，最危险（如果驱动没有正确验证，极易导致漏洞）

**关键提示**：METHOD_NEITHER方式下，驱动直接使用用户态指针，是内核漏洞的高发区。审计驱动时应重点关注这种方式的IOCTL处理。

#### 2.4.3 内核内存管理

Windows内核的内存分配函数：

| 函数 | 用途 | 特点 |
|------|------|------|
| `ExAllocatePool` / `ExAllocatePoolWithTag` | 分配内核池内存 | 类似用户态的malloc，可指定池类型 |
| `ExFreePool` | 释放内核池内存 | 释放分配的池内存 |
| `MmAllocateNonCachedMemory` | 分配非缓存内存 | 不经过CPU缓存，适合DMA |
| `MmAllocateContiguousMemory` | 分配连续物理内存 | 物理地址连续，适合硬件DMA |
| `ExAllocatePoolWithQuota` | 带配额的池分配 | 计入进程配额 |

池类型（Pool Type）：
- **NonPagedPool**：非分页池，不会被交换到磁盘，可在任意IRQL访问
- **PagedPool**：分页池，可以被交换到磁盘，只能在PASSIVE_LEVEL访问
- **NonPagedPoolNx**：不可执行的非分页池（NX保护）

---

---

