; ============================================================
; 03_control_flow.asm —— 条件跳转与循环 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 03_control_flow.asm -o 03_control_flow.o
; 链接命令：ld 03_control_flow.o -o 03_control_flow
; 运行命令：./03_control_flow
; ============================================================

section .data
    title       db  '========== 控制流演示 ==========', 0xA
    title_len   equ $ - title

    msg_loop    db  '循环计数: '
    msg_loop_len equ $ - msg_loop

    msg_even    db  ' 是偶数', 0xA
    msg_even_len equ $ - msg_even

    msg_odd     db  ' 是奇数', 0xA
    msg_odd_len equ $ - msg_odd

    msg_done    db  '循环结束', 0xA
    msg_done_len equ $ - msg_done

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

    ; ---------- 1. 简单循环 (for 循环风格) ----------
    ; 打印 1 到 5
    mov     rbx, 1                      ; rbx = 计数器 (i = 1)

loop_start:
    cmp     rbx, 5                      ; 比较 i 和 5
    jg      loop_end                    ; 如果 i > 5，跳出循环

    ; 打印当前数字
    mov     rax, rbx
    call    print_num
    call    print_newline

    inc     rbx                         ; i++
    jmp     loop_start                  ; 继续循环

loop_end:
    ; ---------- 2. 条件判断（奇偶数判断） ----------
    ; 判断 1-10 中的每个数是奇数还是偶数
    mov     rbx, 1

even_odd_loop:
    cmp     rbx, 10
    jg      even_odd_end

    mov     rax, rbx
    call    print_num

    mov     rax, rbx
    and     rax, 1                      ; 检查最低位
    jz      is_even                     ; 如果最低位为0，是偶数

    ; 奇数
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_odd
    mov     rdx, msg_odd_len
    syscall
    jmp     even_odd_next

is_even:
    ; 偶数
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_even
    mov     rdx, msg_even_len
    syscall

even_odd_next:
    inc     rbx
    jmp     even_odd_loop

even_odd_end:
    ; ---------- 3. 打印完成消息 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_done
    mov     rdx, msg_done_len
    syscall

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 辅助函数：将数字转换为字符串并打印
; 输入：rax = 要打印的数字
; ============================================================
print_num:
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
    div     rbx                          ; rax = rax / 10, rdx = 余数
    add     dl, '0'                      ; 转换为 ASCII
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
; 条件跳转指令速查：
;
; 基于标志位：
;   jz / je     - 零标志 ZF=1 （等于 / 为零）
;   jnz / jne   - 零标志 ZF=0 （不等于 / 不为零）
;   jc / jb / jnae - 进位标志 CF=1 （低于 / 无进位不大于等于）
;   jnc / jae / jnb - 进位标志 CF=0 （不低于 / 大于等于）
;   jo          - 溢出标志 OF=1
;   jno         - 溢出标志 OF=0
;   js          - 符号标志 SF=1 （负数）
;   jns         - 符号标志 SF=0 （非负数）
;
; 有符号数比较（cmp a, b）：
;   jg / jnle   - 大于 (a > b)
;   jge / jnl   - 大于等于 (a >= b)
;   jl / jnge   - 小于 (a < b)
;   jle / jng   - 小于等于 (a <= b)
;
; 无符号数比较（cmp a, b）：
;   ja / jnbe   - 高于 (a > b)
;   jae / jnb   - 高于等于 (a >= b)
;   jb / jnae   - 低于 (a < b)
;   jbe / jna   - 低于等于 (a <= b)
;
; 无条件跳转：
;   jmp         - 无条件跳转
;   loop        - rcx 自减，若 rcx != 0 则跳转
; ============================================================
