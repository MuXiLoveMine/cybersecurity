; ============================================================
; 08_math.asm —— 数学运算 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 08_math.asm -o 08_math.o
; 链接命令：ld 08_math.o -o 08_math
; 运行命令：./08_math
; ============================================================

section .data
    title       db  '========== 数学运算演示 ==========', 0xA
    title_len   equ $ - title

    msg_add     db  'add: 10 + 3 = '
    msg_add_len equ $ - msg_add

    msg_sub     db  'sub: 10 - 3 = '
    msg_sub_len equ $ - msg_sub

    msg_mul     db  'mul: 10 * 3 = '
    msg_mul_len equ $ - msg_mul

    msg_div     db  'div: 10 / 3 = '
    msg_div_len equ $ - msg_div

    msg_mod     db  'mod: 10 % 3 = '
    msg_mod_len equ $ - msg_mod

    msg_inc     db  'inc: 5++ = '
    msg_inc_len equ $ - msg_inc

    msg_dec     db  'dec: 5-- = '
    msg_dec_len equ $ - msg_dec

    msg_and     db  'and: 0b1100 & 0b1010 = '
    msg_and_len equ $ - msg_and

    msg_or      db  'or:  0b1100 | 0b1010 = '
    msg_or_len  equ $ - msg_or

    msg_xor     db  'xor: 0b1100 ^ 0b1010 = '
    msg_xor_len equ $ - msg_xor

    msg_not     db  'not: ~0b1100 (8位) = '
    msg_not_len equ $ - msg_not

    msg_shl     db  'shl: 1 << 3 = '
    msg_shl_len equ $ - msg_shl

    msg_shr     db  'shr: 64 >> 3 = '
    msg_shr_len equ $ - msg_shr

    msg_neg     db  'neg: -5 = '
    msg_neg_len equ $ - msg_neg

    msg_imul    db  'imul: -10 * 3 = '
    msg_imul_len equ $ - msg_imul

    msg_idiv    db  'idiv: -10 / 3 = '
    msg_idiv_len equ $ - msg_idiv

    msg_bcd     db  'BCD运算演示完成', 0xA
    msg_bcd_len equ $ - msg_bcd

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

    ; ---------- 1. 加法 add ----------
    mov     rax, 10
    add     rax, 3                      ; rax = 13
    mov     rsi, msg_add
    mov     rdx, msg_add_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 2. 减法 sub ----------
    mov     rax, 10
    sub     rax, 3                      ; rax = 7
    mov     rsi, msg_sub
    mov     rdx, msg_sub_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 3. 无符号乘法 mul ----------
    ; mul r/m  -> rdx:rax = rax * src
    mov     rax, 10
    mov     rbx, 3
    mul     rbx                         ; rax = 30, rdx = 0
    mov     rsi, msg_mul
    mov     rdx, msg_mul_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 4. 无符号除法 div ----------
    ; div r/m  -> rax = rdx:rax / src, rdx = 余数
    mov     rax, 10
    xor     rdx, rdx                    ; rdx = 0
    mov     rbx, 3
    div     rbx                         ; rax = 3, rdx = 1
    push    rdx                         ; 保存余数
    mov     rsi, msg_div
    mov     rdx, msg_div_len
    call    print_str
    call    print_num_rax
    call    print_newline

    pop     rax                         ; 取出余数
    mov     rsi, msg_mod
    mov     rdx, msg_mod_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 5. 自增 inc / 自减 dec ----------
    mov     rax, 5
    inc     rax                         ; rax = 6
    mov     rsi, msg_inc
    mov     rdx, msg_inc_len
    call    print_str
    call    print_num_rax
    call    print_newline

    mov     rax, 5
    dec     rax                         ; rax = 4
    mov     rsi, msg_dec
    mov     rdx, msg_dec_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 6. 按位与 and ----------
    ; 0b1100 (12) & 0b1010 (10) = 0b1000 (8)
    mov     rax, 12
    and     rax, 10                     ; rax = 8
    mov     rsi, msg_and
    mov     rdx, msg_and_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 7. 按位或 or ----------
    ; 0b1100 (12) | 0b1010 (10) = 0b1110 (14)
    mov     rax, 12
    or      rax, 10                     ; rax = 14
    mov     rsi, msg_or
    mov     rdx, msg_or_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 8. 按位异或 xor ----------
    ; 0b1100 (12) ^ 0b1010 (10) = 0b0110 (6)
    mov     rax, 12
    xor     rax, 10                     ; rax = 6
    mov     rsi, msg_xor
    mov     rdx, msg_xor_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 9. 按位取反 not ----------
    ; ~0b1100 (8位) = 0b11110011 = 243 (无符号) / -13 (有符号)
    mov     rax, 12
    not     al                          ; 只取反低8位
    and     rax, 0xFF                   ; 保留低8位
    mov     rsi, msg_not
    mov     rdx, msg_not_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 10. 左移 shl ----------
    ; 1 << 3 = 8
    mov     rax, 1
    shl     rax, 3                      ; rax = 8
    mov     rsi, msg_shl
    mov     rdx, msg_shl_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 11. 右移 shr ----------
    ; 64 >> 3 = 8
    mov     rax, 64
    shr     rax, 3                      ; rax = 8
    mov     rsi, msg_shr
    mov     rdx, msg_shr_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 12. 取负 neg ----------
    mov     rax, 5
    neg     rax                         ; rax = -5
    mov     rsi, msg_neg
    mov     rdx, msg_neg_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 13. 有符号乘法 imul ----------
    mov     rax, -10
    mov     rbx, 3
    imul    rbx                         ; rdx:rax = -30
    mov     rsi, msg_imul
    mov     rdx, msg_imul_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 14. 有符号除法 idiv ----------
    mov     rax, -10
    cqo                                 ; 符号扩展 rax 到 rdx:rax
    mov     rbx, 3
    idiv    rbx                         ; rax = -3, rdx = -1
    mov     rsi, msg_idiv
    mov     rdx, msg_idiv_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 15. 带进位加法 adc / 带借位减法 sbb ----------
    ; 用于大整数运算
    mov     rax, 0xFFFFFFFF             ; 低32位
    mov     rbx, 1
    add     rax, rbx                    ; rax = 0, CF = 1
    mov     rcx, 0                      ; 高32位
    adc     rcx, 0                      ; rcx += 0 + CF = 1
    ; 结果：rcx:rax = 1:0 = 0x100000000

    ; ---------- 16. 比较指令 cmp / test ----------
    mov     rax, 100
    cmp     rax, 50                     ; rax - 50，设置标志位
    ; jg 表示 rax > 50

    mov     rax, 0b1010
    test    rax, 0b0010                 ; rax & 0b0010，设置 ZF
    ; jnz 表示第1位为1

    ; ---------- BCD 运算 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_bcd
    mov     rdx, msg_bcd_len
    syscall

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

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

    test    rax, rax
    jns     pn_positive

    ; 负数，先打印负号
    push    rax
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, neg_sign
    mov     rdx, 1
    syscall
    pop     rax
    neg     rax

pn_positive:
    mov     rcx, num_buf
    add     rcx, 31
    mov     byte [rcx], 0
    mov     rbx, 10

pn_loop:
    xor     rdx, rdx
    div     rbx
    add     dl, '0'
    dec     rcx
    mov     [rcx], dl
    test    rax, rax
    jnz     pn_loop

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

section .data
    neg_sign    db  '-'

; ============================================================
; 算术与逻辑运算指令总结：
;
; 算术运算：
;   add dst, src    - dst = dst + src
;   sub dst, src    - dst = dst - src
;   inc dst         - dst = dst + 1 (不影响 CF)
;   dec dst         - dst = dst - 1 (不影响 CF)
;   neg dst         - dst = -dst (取补码)
;   mul src         - 无符号乘: rdx:rax = rax * src
;   imul src        - 有符号乘: rdx:rax = rax * src
;   div src         - 无符号除: rax=商, rdx=余数 (rdx:rax / src)
;   idiv src        - 有符号除: rax=商, rdx=余数 (rdx:rax / src)
;   adc dst, src    - dst = dst + src + CF (带进位加)
;   sbb dst, src    - dst = dst - src - CF (带借位减)
;   cbw             - AL -> AX 符号扩展
;   cwde            - AX -> EAX 符号扩展
;   cdqe            - EAX -> RAX 符号扩展
;   cwd             - AX -> DX:AX 符号扩展
;   cdq             - EAX -> EDX:EAX 符号扩展
;   cqo             - RAX -> RDX:RAX 符号扩展
;
; 逻辑运算：
;   and dst, src    - dst = dst & src
;   or  dst, src    - dst = dst | src
;   xor dst, src    - dst = dst ^ src
;   not dst         - dst = ~dst
;   test a, b       - a & b（只设置标志位，不修改操作数）
;
; 移位运算：
;   shl dst, count  - 逻辑左移（低位补0）
;   shr dst, count  - 逻辑右移（高位补0）
;   sal dst, count  - 算术左移（同 shl）
;   sar dst, count  - 算术右移（高位补符号位）
;   rol dst, count  - 循环左移
;   ror dst, count  - 循环右移
;   rcl dst, count  - 带进位循环左移
;   rcr dst, count  - 带进位循环右移
;
; 标志位影响：
;   CF - 进位/借位标志（无符号溢出）
;   OF - 溢出标志（有符号溢出）
;   ZF - 零标志（结果为0）
;   SF - 符号标志（结果为负）
;   PF - 奇偶标志（低8位1的个数为偶数）
;   AF - 辅助进位标志（BCD运算）
; ============================================================
