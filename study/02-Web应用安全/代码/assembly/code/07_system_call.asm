; ============================================================
; 07_system_call.asm —— 系统调用 (Linux x86_64, NASM语法)
; 编译命令：nasm -f elf64 07_system_call.asm -o 07_system_call.o
; 链接命令：ld 07_system_call.o -o 07_system_call
; 运行命令：./07_system_call
; ============================================================

section .data
    title       db  '========== 系统调用演示 ==========', 0xA
    title_len   equ $ - title

    msg1        db  '1. sys_write: 标准输出', 0xA
    msg1_len    equ $ - msg1

    msg2        db  '2. sys_read: 读取输入（本示例无交互模式）', 0xA
    msg2_len    equ $ - msg2

    msg3        db  '3. sys_open/sys_close: 文件操作', 0xA
    msg3_len    equ $ - msg3

    msg4        db  '4. sys_brk: 内存分配', 0xA
    msg4_len    equ $ - msg4

    msg5        db  '5. sys_getpid: 获取进程ID', 0xA
    msg5_len    equ $ - msg5

    msg6        db  '6. sys_exit: 退出程序', 0xA
    msg6_len    equ $ - msg6

    filename    db  'test_output.txt', 0
    file_content db  'Hello from Assembly sys_write!', 0xA
    file_content_len equ $ - file_content

    newline     db  0xA

section .bss
    buf         resb    256
    num_buf     resb    32

section .text
    global _start

_start:
    ; ---------- 打印标题 ----------
    mov     rax, 1                      ; sys_write
    mov     rdi, 1                      ; stdout
    mov     rsi, title
    mov     rdx, title_len
    syscall

    ; ---------- 1. sys_write ----------
    ; 系统调用号：1
    ; 参数：rdi = fd, rsi = buf, rdx = count
    ; 返回：rax = 写入的字节数
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg1
    mov     rdx, msg1_len
    syscall

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg2
    mov     rdx, msg2_len
    syscall

    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg3
    mov     rdx, msg3_len
    syscall

    ; ---------- 2. sys_open ----------
    ; 系统调用号：2
    ; 参数：rdi = filename, rsi = flags, rdx = mode
    ; 返回：rax = 文件描述符（正数成功，负数失败）
    ; flags: O_WRONLY=1, O_CREAT=0x40, O_TRUNC=0x200
    mov     rax, 2                      ; sys_open
    mov     rdi, filename
    mov     rsi, 0x241                  ; O_WRONLY | O_CREAT | O_TRUNC
    mov     rdx, 0644o                  ; 文件权限
    syscall

    cmp     rax, 0
    jl      file_open_fail              ; 打开失败

    mov     r8, rax                     ; 保存文件描述符

    ; sys_write 写入文件
    mov     rax, 1
    mov     rdi, r8
    mov     rsi, file_content
    mov     rdx, file_content_len
    syscall

    ; sys_close 关闭文件
    mov     rax, 3                      ; sys_close
    mov     rdi, r8
    syscall

file_open_fail:

    ; ---------- 3. sys_brk (内存分配) ----------
    ; 系统调用号：12
    ; 参数：rdi = 新的 program break 地址
    ; 返回：rax = 新的 program break
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg4
    mov     rdx, msg4_len
    syscall

    ; 获取当前 program break
    mov     rax, 12                     ; sys_brk
    mov     rdi, 0                      ; 传 0 表示查询
    syscall
    ; rax = 当前 program break

    ; 分配 4096 字节内存
    mov     rbx, rax                    ; 保存当前 break
    add     rbx, 4096                   ; 新的 break
    mov     rax, 12
    mov     rdi, rbx
    syscall
    ; 现在可以使用 [old_break ... new_break) 这段内存

    ; ---------- 4. sys_getpid ----------
    ; 系统调用号：39
    ; 返回：rax = PID
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg5
    mov     rdx, msg5_len
    syscall

    mov     rax, 39                     ; sys_getpid
    syscall
    ; rax = 当前进程 PID

    ; ---------- 5. sys_getuid / sys_getgid ----------
    mov     rax, 102                    ; sys_getuid
    syscall
    ; rax = UID

    mov     rax, 104                    ; sys_getgid
    syscall
    ; rax = GID

    ; ---------- 6. 退出消息 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg6
    mov     rdx, msg6_len
    syscall

    ; ---------- 7. sys_exit ----------
    ; 系统调用号：60
    ; 参数：rdi = 退出码
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; Linux x86_64 常用系统调用表：
;
; 编号  名称        参数                                          说明
; 0     sys_read    rdi=fd, rsi=buf, rdx=count                  读取文件
; 1     sys_write   rdi=fd, rsi=buf, rdx=count                  写入文件
; 2     sys_open    rdi=name, rsi=flags, rdx=mode               打开文件
; 3     sys_close   rdi=fd                                       关闭文件
; 8     sys_lseek   rdi=fd, rsi=offset, rdx=whence              文件定位
; 9     sys_mmap    rdi=addr, rsi=len, rdx=prot, r10=flags,     内存映射
;                   r8=fd, r9=off
; 10    sys_mprotect rdi=addr, rsi=len, rdx=prot                 内存保护
; 11    sys_munmap  rdi=addr, rsi=len                           解除映射
; 12    sys_brk     rdi=brk                                      设置堆大小
; 21    sys_access  rdi=name, rsi=mode                          检查文件权限
; 39    sys_getpid  -                                            获取进程ID
; 42    sys_connect rdi=fd, rsi=addr, rdx=len                   连接套接字
; 49    sys_socket  rdi=family, rsi=type, rdx=protocol           创建套接字
; 56    sys_clone   rdi=flags, rsi=stack, ...                    创建线程/进程
; 57    sys_fork    -                                            创建子进程
; 59    sys_execve  rdi=path, rsi=argv, rdx=envp                 执行程序
; 60    sys_exit    rdi=code                                     退出进程
; 62    sys_kill    rdi=pid, rsi=sig                             发送信号
; 72    sys_fcntl   rdi=fd, rsi=cmd, rdx=arg                    文件控制
; 102   sys_getuid  -                                            获取用户ID
; 104   sys_getgid  -                                            获取组ID
; 231   sys_exit_group rdi=code                                  退出线程组
;
; 系统调用约定：
;   - rax 存放系统调用号
;   - 参数顺序：rdi, rsi, rdx, r10, r8, r9
;   - 使用 syscall 指令触发
;   - 返回值在 rax 中
;   - 错误时 rax 为负数（绝对值为 errno）
;   - 被破坏的寄存器：rcx, r11 (由 syscall 指令保存)
; ============================================================
