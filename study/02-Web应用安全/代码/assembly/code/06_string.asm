; ============================================================
; 06_string.asm —— 字符串操作 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 06_string.asm -o 06_string.o
; 链接命令：ld 06_string.o -o 06_string
; 运行命令：./06_string
; ============================================================

section .data
    title       db  '========== 字符串操作演示 ==========', 0xA
    title_len   equ $ - title

    msg1        db  '1. 字符串长度: '
    msg1_len    equ $ - msg1

    msg2        db  '2. 字符串拷贝完成', 0xA
    msg2_len    equ $ - msg2

    msg3        db  '3. 字符串比较结果: '
    msg3_len    equ $ - msg3

    msg4        db  '4. 字符查找 (strchr) 演示完成', 0xA
    msg4_len    equ $ - msg4

    msg5        db  '5. 字符串连接 (strcat) 完成', 0xA
    msg5_len    equ $ - msg5

    msg_eq      db  '相等', 0xA
    msg_eq_len  equ $ - msg_eq

    msg_neq     db  '不相等', 0xA
    msg_neq_len equ $ - msg_neq

    str1        db  'Hello, Assembly!', 0
    str1_len    equ $ - str1 - 1

    str2        db  'Hello, Assembly!', 0

    str3        db  'Hello, World!', 0

    src_str     db  'Source String', 0
    append_str  db  ' + Append', 0

    newline     db  0xA

section .bss
    dst_str     resb    128
    cat_buf     resb    128
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

    ; ---------- 1. 字符串长度 (strlen) ----------
    mov     rdi, str1
    call    my_strlen                   ; rax = 字符串长度

    mov     rsi, msg1
    mov     rdx, msg1_len
    call    print_str
    call    print_num_rax
    call    print_newline

    ; ---------- 2. 字符串拷贝 (strcpy) ----------
    mov     rsi, src_str                ; 源
    mov     rdi, dst_str                ; 目的
    call    my_strcpy

    mov     rsi, msg2
    mov     rdx, msg2_len
    call    print_str

    ; ---------- 3. 字符串比较 (strcmp) ----------
    ; 比较 str1 和 str2（应该相等）
    mov     rsi, str1
    mov     rdi, str2
    call    my_strcmp

    mov     rsi, msg3
    mov     rdx, msg3_len
    call    print_str

    test    rax, rax
    jz      print_eq

    mov     rsi, msg_neq
    mov     rdx, msg_neq_len
    call    print_str
    jmp     cmp_done

print_eq:
    mov     rsi, msg_eq
    mov     rdx, msg_eq_len
    call    print_str

cmp_done:
    ; ---------- 4. 字符查找 (strchr) ----------
    ; 在 str1 中查找 'A'
    mov     rdi, str1
    mov     sil, 'A'
    call    my_strchr                   ; rax = 找到的位置地址，或 NULL

    mov     rsi, msg4
    mov     rdx, msg4_len
    call    print_str

    ; ---------- 5. 字符串连接 (strcat) ----------
    ; 先拷贝第一个字符串
    mov     rsi, src_str
    mov     rdi, cat_buf
    call    my_strcpy

    ; 再追加第二个字符串
    mov     rsi, append_str
    mov     rdi, cat_buf
    call    my_strcat

    mov     rsi, msg5
    mov     rdx, msg5_len
    call    print_str

    ; ---------- 6. 字符串扫描 (scasb) ----------
    ; 使用 scasb 查找字符串中的逗号
    mov     rdi, str1
    mov     al, ','
    call    my_strlen
    mov     rcx, rax                    ; 扫描长度
    cld
    repne   scasb                       ; 扫描直到找到或 rcx=0
    ; 找到后 rdi 指向匹配字符的下一个位置
    ; ZF = 1 表示找到，ZF = 0 表示未找到

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 函数：my_strlen
; 参数：rdi = 字符串地址
; 返回：rax = 长度
; ============================================================
my_strlen:
    push    rcx
    push    rdi

    xor     rax, rax                    ; 计数器 = 0

strlen_loop:
    cmp     byte [rdi + rax], 0
    je      strlen_done
    inc     rax
    jmp     strlen_loop

strlen_done:
    pop     rdi
    pop     rcx
    ret

; ============================================================
; 函数：my_strcpy
; 参数：rdi = 目的地址, rsi = 源地址
; 返回：rax = 目的地址
; ============================================================
my_strcpy:
    push    rdi
    push    rsi

    cld

strcpy_loop:
    lodsb                               ; al = [rsi++], 加载字节
    stosb                               ; [rdi++] = al, 存储字节
    test    al, al                      ; 检查是否为 0
    jnz     strcpy_loop

    pop     rsi
    pop     rdi
    mov     rax, rdi                    ; 返回目的地址
    ret

; ============================================================
; 函数：my_strcmp
; 参数：rdi = str1, rsi = str2
; 返回：rax = 0(相等), <0(str1<str2), >0(str1>str2)
; ============================================================
my_strcmp:
    cld

strcmp_loop:
    mov     al, [rdi]
    mov     bl, [rsi]
    cmp     al, bl
    jne     strcmp_diff                 ; 不相等

    test    al, al                      ; 都到达结尾？
    jz      strcmp_eq

    inc     rdi
    inc     rsi
    jmp     strcmp_loop

strcmp_eq:
    xor     rax, rax
    ret

strcmp_diff:
    sub     al, bl
    movsx   rax, al                     ; 符号扩展
    ret

; ============================================================
; 函数：my_strchr
; 参数：rdi = 字符串地址, sil = 查找字符
; 返回：rax = 找到的地址或 0
; ============================================================
my_strchr:
    push    rcx
    push    rdi

    ; 先获取长度
    push    rdi
    call    my_strlen
    mov     rcx, rax
    pop     rdi

    inc     rcx                         ; 包含结束符 0
    mov     al, sil
    cld
    repne   scasb                       ; 扫描

    je      strchr_found
    xor     rax, rax                    ; 未找到，返回 0
    jmp     strchr_done

strchr_found:
    lea     rax, [rdi - 1]              ; 指向找到的字符

strchr_done:
    pop     rdi
    pop     rcx
    ret

; ============================================================
; 函数：my_strcat
; 参数：rdi = 目的地址, rsi = 源地址
; 返回：rax = 目的地址
; ============================================================
my_strcat:
    push    rdi
    push    rsi
    push    rbx

    mov     rbx, rdi                    ; 保存目的地址

    ; 找到目的字符串结尾
    call    my_strlen
    add     rdi, rax                    ; rdi 指向结尾

    ; 拷贝源字符串到结尾
    call    my_strcpy

    mov     rax, rbx                    ; 返回目的地址

    pop     rbx
    pop     rsi
    pop     rdi
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

; ============================================================
; 字符串操作指令总结：
;
; 字符串指令（源 DS:RSI，目的 ES:RDI）：
;   movsb  - 字节传送: [RDI] = [RSI]; RSI++; RDI++
;   stosb  - 字节存储: [RDI] = AL; RDI++
;   lodsb  - 字节加载: AL = [RSI]; RSI++
;   cmpsb  - 字节比较: [RSI] - [RDI]; RSI++; RDI++
;   scasb  - 字节扫描: AL - [RDI]; RDI++
;
; 重复前缀：
;   rep        - 重复 RCX 次
;   repe/repz  - 重复直到 RCX=0 或 ZF=0
;   repne/repnz - 重复直到 RCX=0 或 ZF=1
;
; 方向标志 DF：
;   cld - 清除 DF，地址递增
;   std - 设置 DF，地址递减
; ============================================================
