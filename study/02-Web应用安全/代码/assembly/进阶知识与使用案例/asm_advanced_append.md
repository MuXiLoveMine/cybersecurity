
---

## 四、高级实战案例

### 4.1 Egg Hunter Shellcode

Egg Hunter 是一种在内存中查找并执行主 Shellcode 的技术，适用于注入位置空间不足的场景。

```nasm
; ===== Egg Hunter (Linux x86) =====
; 原理：在内存中搜索特定的标记（egg），找到后跳转到其后执行
; egg 通常是 8 字节（如 0x5090509050905090）
; 优点：只需要很小的空间注入 egghunter，主 shellcode 可以在任意位置

section .text
global _start

_start:
    ; egg 值（必须是唯一的，8字节）
    mov eax, 0x50905090  ; egg = "PUSH NOP PUSH NOP" 的机器码
    cld                  ; 清除方向标志（正向搜索）

next_page:
    or dx, 0xfff          ; dx = 4095（页面大小-1）
next_byte:
    inc edx               ; 指向下一个地址
    lea ebx, [edx + 8]    ; 要验证的地址（egg + 8字节shellcode）
    
    ; 调用 access 系统调用检查地址是否可读
    push byte 0x43        ; sys_access
    pop eax
    int 0x80
    
    cmp al, 0xf2          ; EFAULT = 14 (0xf2 是低字节)
    jz next_page          ; 不可读，跳到下一页
    
    ; 检查 egg 是否匹配
    mov edi, edx          ; 目标地址
    scasd                 ; 比较 eax 和 [edi]，edi += 4
    jnz next_byte         ; 不匹配，继续
    scasd                 ; 再比较后4字节
    jnz next_byte         ; 不匹配，继续
    
    ; 找到了！跳转到 shellcode
    jmp edi               ; edi 现在指向 egg 后面
```

### 4.2 自定义编码 Shellcode

多种编码方式的 Shellcode 编码器和解码器。

```nasm
; ===== XOR 编码的 Shellcode 解码器 =====
; 思路：将 shellcode 用 XOR 编码，运行时动态解码再执行
; 好处：避开特征码检测，减少坏字符

section .text
global _start

_start:
    jmp short call_decoder  ; 跳到 call，利用 call 指令的特性获取地址

decoder:
    pop esi                 ; esi = shellcode 的地址（call 压入栈的返回地址）
    mov edi, esi            ; edi 也指向 shellcode（原地解码）
    mov ecx, shellcode_len  ; ecx = shellcode 长度
    mov bl, 0xAA            ; bl = XOR 密钥

decode_loop:
    mov al, [edi]           ; 取一个字节
    xor al, bl              ; XOR 解码
    stosb                   ; 写回，edi++
    loop decode_loop        ; ecx--，不为0则继续
    
    jmp short shellcode     ; 解码完成，跳过去执行

call_decoder:
    call decoder            ; call 会把下一条指令的地址压栈
    
    ; 编码后的 shellcode（XOR 0xAA）
    shellcode: db 0x9b, 0x6a, 0xfa, 0xc2, 0x85, 0x85, 0xd9, 0xc2
    shellcode_len equ $ - shellcode
```

### 4.3 反调试技术

常见的反调试技巧，用于保护代码不被动态分析。

```nasm
; ===== 反调试技术集合 =====
; 检测调试器，如果被调试则跳转到异常处理或退出

section .text
global _start

; 方法1: 检查 ptrace 状态
check_ptrace:
    mov eax, 26             ; sys_ptrace
    mov ebx, 0              ; PTRACE_TRACEME = 0
    int 0x80
    ; 如果返回值 < 0，说明已经被调试（ptrace 失败）
    test eax, eax
    js debug_detected       ; 符号位为1（负数）则跳转
    ret

; 方法2: 使用 sys_breakpoint
check_breakpoint:
    ; 检查特定地址是否有断点指令 (0xCC = INT3)
    mov eax, check_function
    cmp byte [eax], 0xCC
    je debug_detected
    ret

check_function:
    mov eax, 0x12345678
    ret

; 方法3: 时间差检测
check_timing:
    ; 读取时间戳计数器 RDTSC
    rdtsc                   ; EDX:EAX = 64位时间戳
    push edx
    push eax
    
    ; 执行一些代码
    xor ecx, ecx
    mov ecx, 1000
loop_here:
    loop loop_here
    
    ; 再次读取时间戳
    rdtsc
    pop ebx
    pop ecx
    sub eax, ebx
    sbb edx, ecx
    
    ; 如果时间差太大，说明被单步调试
    cmp eax, 100000
    jg debug_detected
    ret

; 方法4: 检查 /proc/self/status 中的 TracerPid
check_proc:
    ; Linux 下读取 /proc/self/status 查找 TracerPid
    ; 如果 TracerPid 不为 0，说明被调试
    ret

debug_detected:
    ; 检测到调试器，执行反制
    ; 可以是退出、崩溃、或执行假代码
    mov eax, 1
    mov ebx, 1
    int 0x80
    ret
```

### 4.4 反汇编混淆技术

让反汇编器难以正确解析指令的技巧。

```nasm
; ===== 反汇编混淆技巧 =====

; 技巧1: 垃圾字节 + 条件跳转混淆
    jmp short real_code     ; 无条件跳转
    db 0xE8                  ; 垃圾字节（call 操作码，使反汇编器混乱）
real_code:
    mov eax, 1
    ; 真实代码继续...

; 技巧2: 自修改代码 (运行时修改指令)
    call get_eip
get_eip:
    pop eax
    mov byte [eax + 10], 0x90  ; 修改后面的指令为 NOP
    ; 这样静态分析看到的和实际执行的不一样

; 技巧3: 不透明谓词
    ; 用一个结果确定但分析困难的条件
    mov eax, 0x12345678
    xor ebx, ebx
    test eax, ebx          ; 结果总是 0（ZF=1）
    jz real_path           ; 总是跳转到这里
    ; 假路径（永远不会执行，但反汇编器不知道）
    db 0x0f, 0x0b           ; UD2 无效指令，用于混淆
real_path:
    ; 真实代码

; 技巧4: 函数地址计算
    ; 不直接 call 函数，而是计算地址
    mov eax, base_func
    add eax, offset_delta   ; 运行时计算真正的函数地址
    call eax

; 技巧5: 异常处理流程
    ; 故意触发异常，在异常处理器中继续执行
    ; 增加动态分析的难度
```

---

## 五、进阶学习资源

### 5.1 汇编与逆向学习资源

- **x86 Assembly Guide**：https://www.cs.virginia.edu/~evans/cs216/guides/x86.html — 经典 x86 汇编指南
- **NASM 文档**：https://www.nasm.us/doc/ — NASM 汇编器官方文档
- **Intel 指令集手册**：https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html — 最权威的 x86/x64 指令集
- **Reverse Engineering for Beginners**：https://beginners.re/ — 逆向工程入门经典（多语言）

### 5.2 Shellcode 开发资源

- **Shell-Storm**：http://shell-storm.org/shellcode/ — 最大的 Shellcode 数据库
- **Exploit-DB Shellcodes**：https://www.exploit-db.com/shellcodes — Exploit-DB 的 shellcode 部分
- **Metasploit Payloads**：https://github.com/rapid7/metasploit-framework/tree/master/modules/payloads
- **pwntools shellcraft**：https://docs.pwntools.com/en/stable/shellcraft.html — Python 生成 shellcode

### 5.3 反调试与逆向对抗

- **Al-Khaser**：https://github.com/LordNoteworthy/al-khaser — 反调试技术集合
- **pintools**：各种反调试检测工具
- **ScyllaHide**：https://github.com/hollyhook/ScyllaHide — 隐藏调试器的插件
- **The Ultimate Anti-Debugging Reference** — 反调试参考大全

### 5.4 工具

- **调试器**：
  - GDB + pwndbg/GEF/peda — Linux 调试
  - x64dbg — Windows 调试
  - OllyDbg — 经典 Windows 调试

- **反汇编/反编译**：
  - IDA Pro — 行业标准（商业）
  - Ghidra — NSA 开源逆向工具
  - Radare2 / Cutter — 开源逆向框架
  - Binary Ninja — 现代逆向平台（商业）

- **其他工具**：
  - objdump / readelf — ELF 分析
  - PEview / CFF Explorer — PE 分析
  - HxD / 010 Editor — 十六进制编辑器
  - Kaitai Struct — 二进制格式解析

### 5.5 推荐书籍

- **汇编语言**：
  - 《汇编语言》（王爽）— 国内经典入门
  - 《Intel 汇编语言程序设计》— 详细全面
  - 《x86汇编语言：从实模式到保护模式》

- **逆向工程**：
  - 《逆向工程核心原理》
  - 《加密与解密》（第四版）
  - 《IDA Pro 权威指南》
  - 《恶意代码分析实战》

- **漏洞利用**：
  - 《0day 安全：软件漏洞分析技术》
  - 《The Shellcoder's Handbook》
  - 《Hacking: The Art of Exploitation》
  - 《漏洞战争》

- **系统底层**：
  - 《深入理解计算机系统》（CSAPP）
  - 《程序员的自我修养》
  - 《Windows 内核原理与实现》

### 5.6 CTF Pwn 与逆向平台

- **pwnable.kr**：https://pwnable.kr/ — PWN 挑战
- **pwnable.tw**：https://pwnable.tw/ — PWN 挑战
- **crackmes.one**：https://crackmes.one/ — Crackme 练习
- **reversing.kr**：http://reversing.kr/ — 逆向挑战
- **pwn.college**：https://pwn.college/ — 系统学习 PWN
- **Nightmare**：https://guyinatuxedo.github.io/ — 二进制安全教程
- **ROP Emporium**：https://ropemporium.com/ — ROP 练习
- **Exploit Education**：https://exploit.education/ — 漏洞利用练习

### 5.7 社区与博客

- **看雪学院**：https://www.kanxue.com/ — 软件安全与逆向
- **吾爱破解**：https://www.52pojie.cn/ — 国内逆向社区
- **安全客**：https://www.anquanke.com/ — 安全资讯
- **先知社区**：https://xz.aliyun.com/ — 阿里云安全社区
- **FreeBuf**：https://www.freebuf.com/ — 安全媒体
- **exploit-db**：https://www.exploit-db.com/ — 漏洞利用数据库

### 5.8 进阶学习路线

**第 1 阶段：汇编基础（1-2月）**
- 掌握 x86/x64 寄存器、指令集、寻址方式
- 学习栈帧、函数调用约定
- 能够阅读和编写简单的汇编程序

**第 2 阶段：逆向入门（2-3月）**
- 学习 C 语言与汇编的对应关系
- 掌握 IDA/Ghidra 基本使用
- 能够分析简单的 crackme

**第 3 阶段：漏洞利用（3-4月）**
- 栈溢出原理与利用
- Shellcode 开发与编码
- ROP 技术
- 格式化字符串漏洞

**第 4 阶段：堆利用（3-6月）**
- glibc malloc 原理
- fastbin / unlink / UAF
- tcache 攻击
- 各种 House of 技术

**第 5 阶段：高级技术（持续）**
- 内核漏洞利用
- 虚拟化与沙箱逃逸
- 固件逆向
- 反调试与混淆对抗
