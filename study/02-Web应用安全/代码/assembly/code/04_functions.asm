; ============================================================
; 04_functions.asm —— 函数调用与栈 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 04_functions.asm -o 04_functions.o
; 链接命令：ld 04_functions.o -o 04_functions
; 运行命令：./04_functions
; ============================================================

section .data
    title       db  '========== 函数调用演示 ==========', 0xA
    title_len   equ $ - title

    msg_add     db  'add(10, 20) = '
    msg_add_len equ $ - msg_add

    msg_fact    db  'factorial(5) = '
    msg_fact_len equ $ - msg_fact

    msg_sum     db  'sum(1, 2, 3, 4, 5) = '
    msg_sum_len equ $ - msg_sum

    msg_strlen  db  'strlen("Hello, Assembly!") = '
    msg_strlen_len equ $ - msg_strlen

    test_str    db  'Hello, Assembly!', 0
    newline     db  0xA

section .bss
    num_buf     resb    32

section .text
    global _start

_start:
    ; ---------- 打印标题 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, title
    mov     rdx, title_len
    syscall

    ; ---------- 1. 简单函数调用 ----------
    ; x86_64 调用约定：参数依次在 rdi, rsi, rdx, rcx, r8, r9
    ; 返回值在 rax
    mov     rdi, 10
    mov     rsi, 20
    call    add_numbers                 ; rax = add(10, 20)

    mov     rsi, msg_add
    mov     rdx, msg_add_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 2. 递归函数（阶乘） ----------
    mov     rdi, 5
    call    factorial                   ; rax = 5! = 120

    mov     rsi, msg_fact
    mov     rdx, msg_fact_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 3. 多参数函数 ----------
    mov     rdi, 1
    mov     rsi, 2
    mov     rdx, 3
    mov     rcx, 4
    mov     r8, 5
    call    sum_five                    ; rax = 1+2+3+4+5 = 15

    mov     rsi, msg_sum
    mov     rdx, msg_sum_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 4. 字符串长度函数 ----------
    mov     rdi, test_str
    call    str_len                     ; rax = 字符串长度

    mov     rsi, msg_strlen
    mov     rdx, msg_strlen_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 函数：add_numbers
; 功能：两个数相加
; 参数：rdi = a, rsi = b
; 返回：rax = a + b
; ============================================================
add_numbers:
    push    rbp                         ; 保存旧的基址指针
    mov     rbp, rsp                    ; 设置新的栈帧基址
    ; [rbp+0] = 旧 rbp
    ; [rbp+8] = 返回地址

    mov     rax, rdi
    add     rax, rsi                    ; rax = a + b

    mov     rsp, rbp                    ; 恢复栈指针
    pop     rbp                         ; 恢复基址指针
    ret                                 ; 返回

; ============================================================
; 函数：factorial
; 功能：计算阶乘（递归）
; 参数：rdi = n
; 返回：rax = n!
; ============================================================
factorial:
    push    rbp
    mov     rbp, rsp

    cmp     rdi, 1                      ; 基准条件：n <= 1
    jle     fact_base

    push    rdi                         ; 保存 n
    dec     rdi
    call    factorial                   ; 递归调用 factorial(n-1)
    pop     rdi                         ; 恢复 n

    mul     rdi                         ; rax = rax * rdi = (n-1)! * n
    jmp     fact_end

fact_base:
    mov     rax, 1                      ; 0! = 1, 1! = 1

fact_end:
    mov     rsp, rbp
    pop     rbp
    ret

; ============================================================
; 函数：sum_five
; 功能：五个数相加（演示多参数传递）
; 参数：rdi=a, rsi=b, rdx=c, rcx=d, r8=e
; 返回：rax = a+b+c+d+e
; ============================================================
sum_five:
    push    rbp
    mov     rbp, rsp

    mov     rax, rdi
    add     rax, rsi
    add     rax, rdx
    add     rax, rcx
    add     rax, r8

    mov     rsp, rbp
    pop     rbp
    ret

; ============================================================
; 函数：str_len
; 功能：计算字符串长度（以0结尾）
; 参数：rdi = 字符串地址
; 返回：rax = 长度
; ============================================================
str_len:
    push    rcx
    push    rdi

    xor     rax, rax                    ; 长度计数器 = 0
    cld                                 ; 清除方向标志，递增

str_len_loop:
    cmp     byte [rdi + rax], 0         ; 检查是否到达字符串结尾
    je      str_len_done
    inc     rax
    jmp     str_len_loop

str_len_done:
    pop     rdi
    pop     rcx
    ret

; ============================================================
; 辅助函数
; ============================================================
print_str:
    push    rax
    push    rdi
    mov     rax, 1
    mov     rdi, 1
    syscall
    pop     rdi
    pop     rax
    ret

print_num_rax:
    push    rbx
    push    rcx
    push    rdx
    push    rsi
    push    rdi

    mov     rcx, num_buf
    add     rcx, 31
    mov     byte [rcx], 0
    mov     rbx, 10

print_num_loop:
    xor     rdx, rdx
    div     rbx
    add     dl, '0'
    dec     rcx
    mov     [rcx], dl
    test    rax, rax
    jnz     print_num_loop

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, rcx
    mov     rdx, num_buf
    add     rdx, 31
    sub     rdx, rcx
    syscall

    pop     rdi
    pop     rsi
    pop     rdx
    pop     rcx
    pop     rbx
    ret

print_newline:
    push    rax
    push    rdi
    push    rsi
    push    rdx
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, newline
    mov     rdx, 1
    syscall
    pop     rdx
    pop     rsi
    pop     rdi
    pop     rax
    ret

; ============================================================
; x86_64 调用约定 (System V AMD64 ABI):
;
; 参数传递：
;   第1个参数: rdi
;   第2个参数: rsi
;   第3个参数: rdx
;   第4个参数: rcx
;   第5个参数: r8
;   第6个参数: r9
;   超过6个参数: 压入栈中（从右到左）
;
; 返回值：
;   整数/指针: rax（64位）或 rax:rdx（128位）
;   浮点数: xmm0
;
; 被调用者保存寄存器 (callee-saved):
;   rbx, rbp, r12, r13, r14, r15
;   这些寄存器在函数返回后值保持不变
;
; 调用者保存寄存器 (caller-saved):
;   rax, rdi, rsi, rdx, rcx, r8, r9, r10, r11
;   这些寄存器可能被函数修改
;
; 栈帧结构：
;   高地址
;     ...
;     调用者栈帧
;     返回地址 (8字节)
;   rbp -> 旧 rbp (8字节)
;     局部变量
;   rsp -> 栈顶
;   低地址
; ============================================================
