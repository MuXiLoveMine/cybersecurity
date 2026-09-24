; ============================================================
; 02_registers.asm —— 寄存器使用演示 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 02_registers.asm -o 02_registers.o
; 链接命令：ld 02_registers.o -o 02_registers
; 运行命令：./02_registers
; ============================================================

section .data
    title       db  '========== 寄存器演示 ==========', 0xA
    title_len   equ $ - title

    msg1        db  '通用寄存器操作演示完成', 0xA
    msg1_len    equ $ - msg1

    msg2        db  '使用 exit 系统调用退出', 0xA
    msg2_len    equ $ - msg2

    newline     db  0xA

section .bss
    num_buf     resb    32              ; 数字转字符串缓冲区

section .text
    global _start

_start:
    ; ---------- 打印标题 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, title
    mov     rdx, title_len
    syscall

    ; ---------- 1. 通用寄存器数据传送 ----------
    ; 64位寄存器：rax, rbx, rcx, rdx, rsi, rdi, rbp, rsp, r8-r15
    ; 32位：eax, ebx, ecx, edx ...
    ; 16位：ax, bx, cx, dx ...
    ; 8位：  al, ah, bl, bh ...

    mov     rax, 100                    ; rax = 100 (64位)
    mov     eax, 200                    ; eax = 200 (高32位清零)
    mov     ax, 300                     ; ax = 300 (低16位)
    mov     al, 0x41                    ; al = 'A' (低8位)
    ; 此时 rax = 0x41 ('A')

    mov     rbx, rax                    ; rbx = rax (寄存器间传送)
    mov     rcx, 0x123456789ABCDEF0     ; 立即数到寄存器

    ; ---------- 2. 指针寄存器 ----------
    ; rsp: 栈指针   rbp: 基址指针
    ; rsi: 源索引   rdi: 目的索引

    mov     rsi, msg1                   ; 源地址（用于字符串操作）
    mov     rdi, num_buf                ; 目的地址

    ; ---------- 3. 标志寄存器 (RFLAGS) ----------
    ; 常用标志位：
    ;   CF (bit 0):  进位标志
    ;   ZF (bit 6):  零标志
    ;   SF (bit 7):  符号标志
    ;   OF (bit 11): 溢出标志
    ;   DF (bit 10): 方向标志

    mov     rax, 5
    sub     rax, 5                      ; rax = 0, ZF = 1
    ; jz / je 指令会检查 ZF 标志

    std                                 ; 设置方向标志（字符串操作递减）
    cld                                 ; 清除方向标志（字符串操作递增）

    ; ---------- 4. 段寄存器（了解即可） ----------
    ; cs: 代码段  ds: 数据段  ss: 栈段
    ; es, fs, gs: 附加段（64位模式下用于 TLS 等）

    ; ---------- 5. 控制寄存器（特权级操作） ----------
    ; cr0, cr2, cr3, cr4 等（用户模式不可直接访问）

    ; ---------- 打印消息1 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg1
    mov     rdx, msg1_len
    syscall

    ; ---------- 6. 栈寄存器操作演示 ----------
    push    123                         ; 将 123 压入栈
    push    456                         ; 将 456 压入栈
    pop     rax                         ; rax = 456 (后进先出)
    pop     rbx                         ; rbx = 123

    pushfq                              ; 压入 RFLAGS
    pop     rax                         ; rax = RFLAGS 值

    ; ---------- 打印消息2 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg2
    mov     rdx, msg2_len
    syscall

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; x86_64 常用寄存器速查表：
;
; 通用寄存器：
;   rax - 累加器 (Accumulator)，常用于返回值、乘除运算
;   rbx - 基址寄存器 (Base)，被调用者保存
;   rcx - 计数寄存器 (Counter)，常用于循环计数
;   rdx - 数据寄存器 (Data)，常用于乘除运算、I/O
;   rsi - 源索引 (Source Index)，字符串操作源
;   rdi - 目的索引 (Destination Index)，字符串操作目的
;   rbp - 基址指针 (Base Pointer)，栈帧基址
;   rsp - 栈指针 (Stack Pointer)，栈顶指针
;   r8 - r15 - 新增通用寄存器
;
; 系统调用参数传递 (x86_64 Linux):
;   rax = 系统调用号
;   rdi = 参数1, rsi = 参数2, rdx = 参数3
;   r10 = 参数4, r8 = 参数5, r9 = 参数6
;   返回值在 rax 中
; ============================================================
