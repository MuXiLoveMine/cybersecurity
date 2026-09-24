# 第三章：CPU 架构与指令集

### 3.1 CPU 基本结构

CPU（中央处理器）是计算机的核心处理单元，负责执行指令和处理数据。

```
┌──────────────────────────────────────┐
│                 CPU                   │
│  ┌──────────┐  ┌──────────────────┐  │
│  │ 控制单元  │  │  寄存器组        │  │
│  │   (CU)   │  │  EAX/EBX/ECX/EDX│  │
│  │          │  │  ESI/EDI/EBP/ESP│  │
│  │          │  │  EIP/EFLAGS     │  │
│  └──────────┘  └──────────────────┘  │
│  ┌──────────────────────────────────┐│
│  │          运算单元（ALU）          ││
│  │   算术运算 | 逻辑运算 | 移位运算  ││
│  └──────────────────────────────────┘│
│  ┌──────────────────────────────────┐│
│  │          缓存（Cache）           ││
│  │   L1 Cache（指令+数据缓存）       ││
│  │   L2 Cache（统一缓存）            ││
│  │   L3 Cache（多核共享缓存）        ││
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

**关键寄存器说明（x86 架构）**：

| 寄存器 | 名称 | 用途 | 安全相关性 |
|--------|------|------|-----------|
| EAX/RAX | 累加器 | 函数返回值、算术运算 | syscall 编号 |
| ECX/RCX | 计数器 | 循环计数、syscall 参数 | rep 指令计数 |
| EDX/RDX | 数据寄存器 | 乘除运算、syscall 参数 | syscall 参数 |
| EBX/RBX | 基址寄存器 | 内存基址 | syscall 参数 |
| ESP/RSP | 栈指针 | 指向栈顶 | 栈溢出利用关键 |
| EBP/RBP | 基址指针 | 指向栈帧基址 | 函数栈帧定位 |
| ESI/RSI | 源索引 | 字符串操作源地址 | syscall 参数 |
| EDI/RDI | 目标索引 | 字符串操作目标地址 | syscall 参数 |
| EIP/RIP | 指令指针 | 指向下一条要执行的指令 | 控制流劫持目标 |
| EFLAGS | 标志寄存器 | 存储运算标志位 | 条件判断 |

### 3.2 指令集架构

| 架构 | 位数 | 特点 | 应用场景 | 安全工具 |
|------|------|------|---------|---------|
| **x86** | 32位 | CISC，复杂指令集 | 桌面/服务器 | GDB, Immunity |
| **x86-64 (AMD64)** | 64位 | x86 扩展，更多寄存器 | 现代桌面/服务器 | GDB, x64dbg |
| **ARM** | 32/64位 | RISC，精简指令集 | 移动设备/IoT | GDB, Frida |
| **MIPS** | 32/64位 | RISC，固定长度指令 | 路由器/嵌入式 | GDB, IDA |
| **RISC-V** | 32/64位 | 开源 RISC | 研究/新兴设备 | GDB |

### 3.3 CPU 特权级与保护环

```
Ring 0（内核态）  — 操作系统内核、驱动程序
  ↓ 系统调用
Ring 3（用户态）  — 应用程序、用户进程

Ring 0：可执行所有指令（包括特权指令如 HLT、MOV CRn）
Ring 3：只能执行普通指令，特权指令触发异常

安全意义：
  - 用户态程序通过系统调用进入内核态
  - 内核漏洞（如 dirty cow）可从 Ring 3 提权到 Ring 0
  - 容器/沙箱利用特权级隔离限制应用权限
```

### 3.4 汇编语言基础（x86-64）

```nasm
; 基本数据传送
mov rax, 0x1          ; 将 1 存入 rax
mov rbx, rax          ; 将 rax 的值复制到 rbx
push rbp              ; 将 rbp 压入栈
pop rbp               ; 从栈弹出到 rbp
lea rax, [rbp-0x10]   ; 计算地址但不访问内存

; 算术运算
add rax, rbx          ; rax = rax + rbx
sub rax, 0x10         ; rax = rax - 0x10
inc rax               ; rax++
dec rax               ; rax--
imul rax, rbx         ; rax = rax * rbx

; 逻辑运算
and rax, 0xff         ; 按位与
or rax, rbx           ; 按位或
xor rax, rax          ; rax 清零（常见优化）
shl rax, 4            ; 左移 4 位
shr rax, 4            ; 右移 4 位

; 比较与跳转
cmp rax, rbx          ; 比较 rax 和 rbx
je label              ; 相等则跳转
jne label             ; 不等则跳转
jg label              ; 大于则跳转
jl label              ; 小于则跳转
jmp label             ; 无条件跳转

; 函数调用
call function_name    ; 调用函数（push 返回地址 + jmp）
ret                   ; 返回（pop 返回地址 + jmp）

; 系统调用（Linux x86-64）
mov rax, 59           ; sys_execve 编号
mov rdi, path         ; 参数1：程序路径
mov rsi, argv         ; 参数2：参数数组
mov rdx, envp         ; 参数3：环境变量
syscall               ; 执行系统调用
```

### 3.5 函数调用约定

| 调用约定 | 平台 | 参数传递 | 栈清理 | 返回值 |
|---------|------|---------|--------|--------|
| **cdecl** | C 语言（x86） | 栈（右到左） | 调用方 | EAX |
| **stdcall** | Windows API（x86） | 栈（右到左） | 被调用方 | EAX |
| **fastcall** | MSVC（x86） | 寄存器+栈 | 被调用方 | EAX |
| **System V AMD64** | Linux/macOS（x64） | RDI,RSI,RDX,RCX,R8,R9 | 调用方 | RAX |
| **Microsoft x64** | Windows（x64） | RCX,RDX,R8,R9+栈 | 调用方 | RAX |

**System V AMD64 调用约定（Linux 64 位）**：
```
参数传递顺序：
  参数1 → RDI
  参数2 → RSI
  参数3 → RDX
  参数4 → RCX
  参数5 → R8
  参数6 → R9
  参数7+ → 栈

函数序言（Prologue）：
  push rbp
  mov rbp, rsp
  sub rsp, <局部变量大小>

函数结语（Epilogue）：
  mov rsp, rbp
  pop rbp
  ret

安全意义：
  - ROP（返回导向编程）利用 ret 指令链控制执行流
  - 栈帧结构决定了缓冲区溢出时覆盖返回地址的偏移量
```

---

---

