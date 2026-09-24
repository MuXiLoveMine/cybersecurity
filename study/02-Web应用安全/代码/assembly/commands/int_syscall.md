# int_syscall

> **分类**：系统调用
> **说明**：触发系统调用（int 0x80 / syscall）

---

## 语法

```nasm
int 0x80     ; 32位 Linux\nsyscall       ; 64位 Linux
```

## 32位 Linux

eax=调用号 / ebx=arg1 / ecx=arg2 / edx=arg3 / esi=arg4 / edi=arg5 / ebp=arg6

## 64位 Linux

rax=调用号 / rdi=arg1 / rsi=arg2 / rdx=arg3 / r10=arg4 / r8=arg5 / r9=arg6

## 常用调用号

32位: exit=1 / fork=2 / read=3 / write=4 / open=5 / close=6 / execve=11

## 示例代码

```nasm
; ===== 32位 Linux int 0x80 =====

; write(1, msg, len) - 输出字符串
section .data
    msg db "Hello, World!", 0xA
    len equ $ - msg

section .text
global _start
_start:
    mov eax, 4          ; sys_write
    mov ebx, 1          ; stdout
    mov ecx, msg        ; buffer
    mov edx, len        ; length
    int 0x80            ; 触发系统调用

    ; exit(0)
    mov eax, 1          ; sys_exit
    mov ebx, 0          ; exit code
    int 0x80

; ===== 常用系统调用号（32位 x86） =====
; 0 - sys_setup (unused)
; 1 - sys_exit
; 2 - sys_fork
; 3 - sys_read
; 4 - sys_write
; 5 - sys_open
; 6 - sys_close
; 11 - sys_execve
; 12 - sys_brk
; 45 - sys_brk (malloc)
; 102 - sys_socketcall
; 120 - sys_clone

; ===== 64位 Linux syscall =====

section .data
    msg db "Hello, 64-bit!", 0xA
    len equ $ - msg

section .text
global _start
_start:
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg        ; buffer
    mov rdx, len        ; length
    syscall             ; 触发系统调用

    ; exit(0)
    mov rax, 60         ; sys_exit
    mov rdi, 0          ; exit code
    syscall

; ===== 常用系统调用号（64位 x64） =====
; 0 - sys_read
; 1 - sys_write
; 2 - sys_open
; 3 - sys_close
; 9 - sys_mmap
; 12 - sys_brk
; 59 - sys_execve
; 60 - sys_exit
; 200 - sys_tkill
; 231 - sys_exit_group

; ===== execve 示例（32位） =====
; 执行 /bin/sh
section .text
global _start
_start:
    ; execve("/bin//sh", ["/bin//sh", NULL], NULL)
    xor eax, eax
    push eax            ; NULL 终止符
    push "//sh"
    push "/bin"
    mov ebx, esp        ; ebx = "/bin//sh"

    push eax
    push ebx
    mov ecx, esp        ; ecx = [ebx, NULL]

    xor edx, edx        ; edx = NULL

    mov al, 11          ; sys_execve
    int 0x80

; ===== Windows Win32 API 调用 =====
; 不同的机制，通常通过导入表调用
; 简单示例（需要链接 kernel32.dll）
; invoke MessageBoxA, 0, title, text, 0
; invoke ExitProcess, 0
```
