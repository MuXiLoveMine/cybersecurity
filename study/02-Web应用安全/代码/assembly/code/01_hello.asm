; ============================================================
; 01_hello.asm —— Hello World (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 01_hello.asm -o 01_hello.o
; 链接命令：ld 01_hello.o -o 01_hello
; 运行命令：./01_hello
; ============================================================

section .data
    ; 定义字符串数据
    msg     db  'Hello, World!', 0xA    ; 字符串 + 换行符
    len     equ $ - msg                 ; 字符串长度（$ 表示当前地址）

    msg2    db  '你好，汇编语言！', 0xA
    len2    equ $ - msg2

    msg3    db  '========== Hello World ==========', 0xA
    len3    equ $ - msg3

section .text
    global _start                       ; 程序入口点（链接器需要）

_start:
    ; ---------- 1. 打印标题 ----------
    mov     rax, 1                      ; sys_write 系统调用号 (x86_64)
    mov     rdi, 1                      ; 文件描述符：stdout = 1
    mov     rsi, msg3                   ; 字符串地址
    mov     rdx, len3                   ; 字符串长度
    syscall                             ; 执行系统调用

    ; ---------- 2. 打印 Hello World ----------
    mov     rax, 1                      ; sys_write
    mov     rdi, 1
    mov     rsi, msg
    mov     rdx, len
    syscall

    ; ---------- 3. 打印中文问候 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg2
    mov     rdx, len2
    syscall

    ; ---------- 4. 退出程序 ----------
    mov     rax, 60                     ; sys_exit 系统调用号
    mov     rdi, 0                      ; 退出码：0 表示成功
    syscall

; ============================================================
; 说明：
; - x86_64 Linux 系统调用使用 rax 存放调用号
; - 参数依次存放在 rdi, rsi, rdx, r10, r8, r9
; - syscall 指令触发系统调用
; - 常用系统调用号：write=1, exit=60, open=2, read=0
; ============================================================
