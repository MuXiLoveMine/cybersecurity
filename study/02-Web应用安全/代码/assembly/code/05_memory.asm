; ============================================================
; 05_memory.asm —— 内存操作 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 05_memory.asm -o 05_memory.o
; 链接命令：ld 05_memory.o -o 05_memory
; 运行命令：./05_memory
; ============================================================

section .data
    title       db  '========== 内存操作演示 ==========', 0xA
    title_len   equ $ - title

    msg1        db  '1. 数据传送演示完成', 0xA
    msg1_len    equ $ - msg1

    msg2        db  '2. 内存拷贝 (memcpy) 演示完成', 0xA
    msg2_len    equ $ - msg2

    msg3        db  '3. 内存填充 (memset) 演示完成', 0xA
    msg3_len    equ $ - msg3

    msg4        db  '4. 内存比较 (memcmp) 演示完成', 0xA
    msg4_len    equ $ - msg4

    msg5        db  '5. 寻址方式演示完成', 0xA
    msg5_len    equ $ - msg5

    ; 源数据
    src_buf     db  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    src_len     equ $ - src_buf

    src2        db  'ABCDEF'
    src2_len    equ $ - src2

    src3        db  'ABCXYZ'
    src3_len    equ $ - src3

    table       dd  10, 20, 30, 40, 50   ; 整数数组（每个4字节）
    table_len   equ 5

    newline     db  0xA

section .bss
    dst_buf     resb    64              ; 目标缓冲区
    fill_buf    resb    32              ; 填充缓冲区
    num_buf     resb    32              ; 数字输出缓冲区

section .text
    global _start

_start:
    ; ---------- 打印标题 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, title
    mov     rdx, title_len
    syscall

    ; ---------- 1. 数据传送指令 ----------
    ; mov 指令：内存 <-> 寄存器 之间的数据传送
    ; 注意：不能直接 mov 内存到内存

    ; 立即数到内存
    mov     byte [dst_buf], 'A'         ; dst_buf[0] = 'A'
    mov     word [dst_buf + 2], 0x3132  ; dst_buf[2:3] = '21' (小端序)
    mov     dword [dst_buf + 4], 0x12345678
    mov     qword [dst_buf + 8], 0xDEADBEEFCAFEBABE

    ; 内存到寄存器
    mov     al, [dst_buf]               ; al = 'A'
    mov     rax, [dst_buf + 8]          ; rax = 0xDEADBEEFCAFEBABE

    ; 寄存器到内存
    mov     rbx, 0x1122334455667788
    mov     [dst_buf + 16], rbx

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg1
    mov     rdx, msg1_len
    syscall

    ; ---------- 2. 内存拷贝 (memcpy) ----------
    ; 将 src_buf 拷贝到 dst_buf
    mov     rsi, src_buf                ; 源地址
    mov     rdi, dst_buf                ; 目的地址
    mov     rcx, src_len                ; 拷贝长度
    cld                                 ; 方向：递增
    rep     movsb                       ; 重复 movsb 直到 rcx = 0

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg2
    mov     rdx, msg2_len
    syscall

    ; ---------- 3. 内存填充 (memset) ----------
    ; 用 'X' 填充 fill_buf
    mov     rdi, fill_buf               ; 目的地址
    mov     al, 'X'                     ; 填充字节
    mov     rcx, 32                     ; 填充长度
    cld
    rep     stosb                       ; 重复 stosb 直到 rcx = 0

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg3
    mov     rdx, msg3_len
    syscall

    ; ---------- 4. 内存比较 (memcmp) ----------
    ; 比较 src2 和 src3
    mov     rsi, src2
    mov     rdi, src3
    mov     rcx, src2_len
    cld
    repe    cmpsb                       ; 比较直到不相等或 rcx = 0
    ; ZF = 1 表示相等，ZF = 0 表示不相等

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg4
    mov     rdx, msg4_len
    syscall

    ; ---------- 5. 寻址方式演示 ----------
    ; 直接寻址
    mov     eax, [table]                ; eax = table[0] = 10

    ; 寄存器间接寻址
    mov     rbx, table
    mov     eax, [rbx]                  ; eax = *rbx = 10

    ; 基址 + 偏移量
    mov     eax, [rbx + 8]              ; eax = table[2] = 30

    ; 变址寻址 (寄存器 * 比例因子 + 基址)
    mov     rcx, 3                      ; index = 3
    mov     eax, [table + rcx * 4]      ; eax = table[3] = 40

    ; 基址 + 变址 * 比例 + 偏移量
    mov     rbx, table
    mov     rcx, 4
    mov     eax, [rbx + rcx * 4 + 0]    ; eax = table[4] = 50

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg5
    mov     rdx, msg5_len
    syscall

    ; ---------- 6. xchg 指令（交换） ----------
    mov     rax, 100
    mov     rbx, 200
    xchg    rax, rbx                    ; rax = 200, rbx = 100
    xchg    [dst_buf], al               ; 交换内存和寄存器

    ; ---------- 7. lea 指令（加载有效地址） ----------
    ; lea 不访问内存，只计算地址
    lea     rdi, [table + rcx * 4]      ; rdi = table + rcx * 4 (地址计算)
    ; lea 常用于算术运算：
    lea     rax, [rax + rax * 2]        ; rax = rax * 3
    lea     rax, [rbx + rcx * 4 + 10]   ; 复杂地址计算

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 内存操作指令速查：
;
; 数据传送：
;   mov dst, src      - 数据传送 (字节/字/双字/四字)
;   xchg a, b         - 交换 a 和 b
;   lea dst, [addr]   - 加载有效地址（只计算，不访问内存）
;
; 字符串操作（配合 rep/repe/repne 前缀）：
;   movsb/movsw/movsd/movsq  - 字符串传送 (DS:SI -> ES:DI)
;   stosb/stosw/stosd/stosq  - 字符串存储 (AL/AX/EAX/RAX -> ES:DI)
;   lodsb/lodsw/lodsd/lodsq  - 字符串加载 (DS:SI -> AL/AX/EAX/RAX)
;   cmpsb/cmpsw/cmpsd/cmpsq  - 字符串比较
;   scasb/scasw/scasd/scasq  - 字符串扫描 (AL/AX/EAX/RAX vs ES:DI)
;
; 重复前缀：
;   rep        - 重复 rcx 次
;   repe/repz  - 重复直到 rcx=0 或 ZF=0
;   repne/repnz - 重复直到 rcx=0 或 ZF=1
;
; 寻址方式：
;   立即寻址:    mov rax, 123
;   寄存器寻址:  mov rax, rbx
;   直接寻址:    mov rax, [0x123456]
;   寄存器间接:  mov rax, [rbx]
;   基址+偏移:   mov rax, [rbx + 8]
;   变址寻址:    mov rax, [table + rcx * 4]
;   基址变址:    mov rax, [rbx + rcx * 4 + 8]
;
; 比例因子：1, 2, 4, 8
; ============================================================
