# int 0x80 / syscall - 汇编系统调用

> x86/x86_64 汇编语言的系统调用方式，Linux 下通过中断或 syscall 指令进入内核。

---

## 一、x86 (32位) 系统调用 - int 0x80

### 1.1 基本用法

```nasm
; int 0x80 - Linux 32位系统调用
; 
; 调用约定:
;   eax = 系统调用号
;   ebx = 第1个参数
;   ecx = 第2个参数
;   edx = 第3个参数
;   esi = 第4个参数
;   edi = 第5个参数
;   ebp = 第6个参数
;
; 返回值: eax
;   正数/0 = 成功
;   负数 = 错误码（取反即为 errno）

; 示例: sys_write (调用号 4)
; ssize_t write(int fd, const void *buf, size_t count)

section .data
    msg db 'Hello, World!', 0xA
    len equ $ - msg

section .text
    global _start

_start:
    mov eax, 4          ; sys_write 系统调用号
    mov ebx, 1          ; 第1参数: 文件描述符 (1 = stdout)
    mov ecx, msg        ; 第2参数: 字符串地址
    mov edx, len        ; 第3参数: 字符串长度
    int 0x80            ; 触发系统调用
    
    ; sys_exit (调用号 1)
    mov eax, 1          ; sys_exit
    mov ebx, 0          ; 退出状态码
    int 0x80
```

### 1.2 常用系统调用

```nasm
; ===== 系统调用表（x86 32位）=====
; 调用号  名称        原型
; 1       sys_exit    void exit(int status)
; 2       sys_fork    pid_t fork(void)
; 3       sys_read    ssize_t read(int fd, void *buf, size_t count)
; 4       sys_write   ssize_t write(int fd, const void *buf, size_t count)
; 5       sys_open    int open(const char *pathname, int flags, mode_t mode)
; 6       sys_close   int close(int fd)
; 11      sys_execve  int execve(const char *filename, char *const argv[], char *const envp[])
; 33      sys_access  int access(const char *pathname, int mode)
; 45      sys_brk     void *brk(void *addr)
; 54      sys_ioctl   int ioctl(int fd, unsigned long request, ...)
; 63      sys_dup2    int dup2(int oldfd, int newfd)
; 90      sys_mmap    void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)
; 91      sys_munmap  int munmap(void *addr, size_t length)
; 102     sys_socketcall  int socketcall(int call, unsigned long *args)
; 120     sys_clone   int clone(int (*fn)(void *), void *child_stack, int flags, void *arg, ...)
; 122     sys_uname   int uname(struct utsname *buf)
; 125     sys_mprotect  int mprotect(void *addr, size_t len, int prot)
; 140     sys__llseek  int _llseek(unsigned int fd, unsigned long offset_high, ...)
; 168     sys_poll    int poll(struct pollfd *fds, nfds_t nfds, int timeout)
; 174     sys_rt_sigaction  int rt_sigaction(int sig, ...)
; 175     sys_rt_sigprocmask int rt_sigprocmask(int how, ...)
; 192     sys_mmap2   void *mmap2(void *addr, size_t length, int prot, ...)
; 221     sys_fcntl64 int fcntl64(int fd, int cmd, ...)
; 224     sys_gettid  pid_t gettid(void)
; 240     sys_futex   int futex(int *uaddr, int futex_op, int val, ...)
; 252     sys_epoll_create int epoll_create(int size)
; 253     sys_epoll_ctl int epoll_ctl(int epfd, int op, int fd, ...)
; 254     sys_epoll_wait int epoll_wait(int epfd, ...)
; 265     sys_clock_gettime int clock_gettime(clockid_t clk_id, ...)
; 311     sys_socket  int socket(int domain, int type, int protocol)
; 312     sys_bind    int bind(int sockfd, const struct sockaddr *addr, ...)
; 313     sys_connect int connect(int sockfd, const struct sockaddr *addr, ...)
; 314     sys_listen  int listen(int sockfd, int backlog)
; 315     sys_accept  int accept(int sockfd, struct sockaddr *addr, ...)
; 316     sys_getsockname int getsockname(int sockfd, ...)
; 317     sys_getpeername int getpeername(int sockfd, ...)
; 318     sys_socketpair int socketpair(int domain, int type, int protocol, int sv[2])
; 319     sys_send    ssize_t send(int sockfd, const void *buf, size_t len, int flags)
; 320     sys_recv    ssize_t recv(int sockfd, void *buf, size_t len, int flags)
; 321     sys_sendto  ssize_t sendto(int sockfd, const void *buf, size_t len, int flags, ...)
; 322     sys_recvfrom ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags, ...)
; 323     sys_shutdown int shutdown(int sockfd, int how)
; 324     sys_setsockopt int setsockopt(int sockfd, int level, int optname, ...)
; 325     sys_getsockopt int getsockopt(int sockfd, int level, int optname, ...)
```

### 1.3 文件操作示例

```nasm
; ===== 读取文件示例 =====
section .data
    filename db 'test.txt', 0

section .bss
    buffer resb 1024

section .text
    global _start

_start:
    ; sys_open (eax=5)
    ; int open(const char *pathname, int flags, mode_t mode)
    mov eax, 5          ; sys_open
    mov ebx, filename   ; 文件名
    mov ecx, 0          ; O_RDONLY
    mov edx, 0          ; mode (不需要)
    int 0x80
    
    test eax, eax
    js exit_error       ; 负数表示错误
    
    mov ebx, eax        ; 保存文件描述符
    
    ; sys_read (eax=3)
    ; ssize_t read(int fd, void *buf, size_t count)
    mov eax, 3
    mov ecx, buffer
    mov edx, 1024
    int 0x80
    
    ; 写入到 stdout
    mov edx, eax        ; 读取的字节数
    mov eax, 4
    mov ebx, 1          ; stdout
    mov ecx, buffer
    int 0x80
    
    ; sys_close (eax=6)
    mov eax, 6
    ; ebx 已经是文件描述符
    int 0x80
    
    ; 正常退出
    mov eax, 1
    mov ebx, 0
    int 0x80
    
exit_error:
    mov eax, 1
    mov ebx, 1
    int 0x80
```

---

## 二、x86_64 (64位) 系统调用 - syscall

### 2.1 基本用法

```nasm
; syscall - Linux 64位系统调用
; 
; 调用约定 (System V AMD64 ABI):
;   rax = 系统调用号
;   rdi = 第1个参数
;   rsi = 第2个参数
;   rdx = 第3个参数
;   r10 = 第4个参数（注意：不是 rcx，因为 syscall 会用 rcx 存 rip）
;   r8  = 第5个参数
;   r9  = 第6个参数
;
; 返回值: rax
;   正数/0 = 成功
;   -1 到 -4095 = 错误（-rax 即为 errno）
;
; 被破坏的寄存器: rcx, r11（syscall 指令自动使用）

section .data
    msg db 'Hello, World!', 0xA
    len equ $ - msg

section .text
    global _start

_start:
    ; sys_write (调用号 1)
    mov rax, 1          ; sys_write
    mov rdi, 1          ; fd = 1 (stdout)
    mov rsi, msg        ; buf
    mov rdx, len        ; count
    syscall
    
    ; sys_exit (调用号 60)
    mov rax, 60         ; sys_exit
    mov rdi, 0          ; 退出码
    syscall
```

### 2.2 x86_64 系统调用号

```nasm
; ===== 部分 x86_64 系统调用号 =====
; 0   sys_read
; 1   sys_write
; 2   sys_open
; 3   sys_close
; 4   sys_stat
; 5   sys_fstat
; 6   sys_lstat
; 7   sys_poll
; 8   sys_lseek
; 9   sys_mmap
; 10  sys_mprotect
; 11  sys_munmap
; 12  sys_brk
; 13  sys_rt_sigaction
; 14  sys_rt_sigprocmask
; 15  sys_rt_sigreturn
; 16  sys_ioctl
; 17  sys_pread64
; 18  sys_pwrite64
; 19  sys_readv
; 20  sys_writev
; 21  sys_access
; 22  sys_pipe
; 23  sys_select
; 24  sys_sched_yield
; 25  sys_mremap
; 26  sys_msync
; 27  sys_mincore
; 28  sys_madvise
; 29  sys_shmget
; 30  sys_shmat
; 31  sys_shmctl
; 32  sys_dup
; 33  sys_dup2
; 34  sys_pause
; 35  sys_nanosleep
; 36  sys_getitimer
; 37  sys_alarm
; 38  sys_setitimer
; 39  sys_getpid
; 40  sys_sendfile
; 41  sys_socket
; 42  sys_connect
; 43  sys_accept
; 44  sys_sendto
; 45  sys_recvfrom
; 46  sys_sendmsg
; 47  sys_recvmsg
; 48  sys_shutdown
; 49  sys_bind
; 50  sys_listen
; 51  sys_getsockname
; 52  sys_getpeername
; 53  sys_socketpair
; 54  sys_setsockopt
; 55  sys_getsockopt
; 56  sys_clone
; 57  sys_fork
; 58  sys_vfork
; 59  sys_execve
; 60  sys_exit
; 61  sys_wait4
; 62  sys_kill
; 63  sys_uname
; ...
; 257 sys_openat
; 258 sys_mkdirat
; 259 sys_mknodat
; 260 sys_fchownat
; 261 sys_futimesat
; 262 sys_newfstatat
; 263 sys_unlinkat
; 264 sys_renameat
; 265 sys_linkat
; 266 sys_symlinkat
; 267 sys_readlinkat
; 268 sys_fchmodat
; 269 sys_faccessat
; 270 sys_pselect6
; 271 sys_ppoll
; 272 sys_unshare
; 273 sys_set_robust_list
; 274 sys_get_robust_list
; 275 sys_splice
; 276 sys_tee
; 277 sys_sync_file_range
; 278 sys_vmsplice
; 279 sys_move_pages
; 280 sys_utimensat
; 281 sys_epoll_pwait
; 282 sys_signalfd
; 283 sys_timerfd_create
; 284 sys_eventfd
; 285 sys_fallocate
; 286 sys_timerfd_settime
; 287 sys_timerfd_gettime
; 288 sys_accept4
; 289 sys_signalfd4
; 290 sys_eventfd2
; 291 sys_epoll_create1
; 292 sys_dup3
; 293 sys_pipe2
; 294 sys_inotify_init
; 295 sys_inotify_add_watch
; 296 sys_inotify_rm_watch
; 297 sys_preadv
; 298 sys_pwritev
; 299 sys_rt_tgsigqueueinfo
; 300 sys_perf_event_open
; 301 sys_recvmmsg
; 302 sys_fanotify_init
; 303 sys_fanotify_mark
; 304 sys_prlimit64
; 305 sys_name_to_handle_at
; 306 sys_open_by_handle_at
; 307 sys_clock_adjtime
; 308 sys_syncfs
; 309 sys_sendmmsg
; 310 sys_setns
; 311 sys_getcpu
; 312 sys_process_vm_readv
; 313 sys_process_vm_writev
; 314 sys_kcmp
; 315 sys_finit_module
; 316 sys_sched_setattr
; 317 sys_sched_getattr
; 318 sys_renameat2
; 319 sys_seccomp
; 320 sys_getrandom
; 321 sys_memfd_create
; 322 sys_kexec_file_load
; 323 sys_bpf
; 324 sys_execveat
; 325 sys_userfaultfd
; 326 sys_membarrier
; 327 sys_mlock2
; 328 sys_copy_file_range
; 329 sys_preadv2
; 330 sys_pwritev2
; 331 sys_pkey_mprotect
; 332 sys_pkey_alloc
; 333 sys_pkey_free
; 334 sys_statx
; 335 sys_io_pgetevents
; 336 sys_rseq
```

---

## 三、安全相关内容

### 3.1 Shellcode 基础

```nasm
; ===== 什么是 Shellcode =====
; Shellcode 是用于漏洞利用的机器码
; 特点：
; 1. 不能包含 null 字节（0x00），因为 strcpy 等函数会在 null 处截断
; 2. 位置无关（PIC），因为不知道注入到哪个地址
; 3. 尽量短小

; ===== 经典 execve /bin/sh shellcode (x86) =====
; 目标: execve("/bin/sh", ["/bin/sh", NULL], NULL)

; 传统写法（有 null 字节问题）
;     xor eax, eax
;     push eax              ; NULL 终止符
;     push 0x68732f2f       ; "//sh"
;     push 0x6e69622f       ; "/bin"
;     mov ebx, esp          ; 路径指针
;     push eax
;     push ebx
;     mov ecx, esp          ; argv
;     xor edx, edx          ; envp = NULL
;     mov al, 0xb           ; execve 系统调用号 11
;     int 0x80

; ===== x86_64 execve shellcode =====
; execve("/bin/sh", NULL, NULL)
; 
;     xor rax, rax
;     push rax
;     mov rbx, 0x68732f6e69622f2f  ; "//bin/sh"
;     push rbx
;     mov rdi, rsp          ; path = "/bin/sh"
;     xor rsi, rsi          ; argv = NULL
;     xor rdx, rdx          ; envp = NULL
;     mov al, 0x3b          ; execve 系统调用号 59
;     syscall

; ===== 检测空字节 =====
; 编译后用 objdump 查看机器码，检查是否有 00 字节
; 如果有，需要修改代码避免
;
; 常见避免 null 字节的技巧：
; 1. xor eax, eax 代替 mov eax, 0
; 2. mov al, 0xb 代替 mov eax, 11
; 3. push 0 改成 xor eax, eax; push eax
; 4. 使用 inc/dec 代替直接赋值
```

### 3.2 系统调用安全

```nasm
; ===== 危险的系统调用 =====
; 以下系统调用在漏洞利用中常用：

; execve (0xb / 59) - 执行程序
; 用于获得 shell

; mmap / mprotect - 内存权限
; 用于将内存改为可执行（绕过 NX）
; void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset);
; int mprotect(void *addr, size_t len, int prot);
; PROT_EXEC = 0x4 （可执行）

; setuid / setreuid - 提权
; 用于从低权限提升到高权限
; int setuid(uid_t uid);
; int setreuid(uid_t ruid, uid_t euid);

; open / read / write - 文件操作
; 用于读取敏感文件（如 /etc/passwd, /etc/shadow）

; socket / connect - 网络
; 用于反弹 shell

; ===== 安全防护机制 =====
; 
; 1. NX (No eXecute) / DEP
;    - 栈和堆不可执行
;    - 绕过: ROP (Return-Oriented Programming)
;
; 2. ASLR (Address Space Layout Randomization)
;    - 地址空间随机化
;    - 绕过: 信息泄露、部分覆盖
;
; 3. Stack Canary / 栈保护
;    - 栈上放置金丝雀值，溢出时检测
;    - 绕过: 泄露 canary、逐字节爆破
;
; 4. PIE (Position Independent Executable)
;    - 可执行文件也是随机地址
;    - 绕过: 信息泄露
;
; 5. RELRO (Relocation Read-Only)
;    - GOT 表只读
;    - 绕过: 用其他攻击面
;
; 6. seccomp
;    - 限制可用的系统调用
;    - 绕过: 找到允许的系统调用组合
```

### 3.3 常见汇编漏洞模式

```nasm
; ===== 1. 缓冲区溢出 =====
; 典型的 gets/strcpy 模式
;
; char buf[64];
; gets(buf);        ← 危险！
; strcpy(buf, input); ← 危险！
;
; 利用：覆盖返回地址
; 32位：缓冲区 + 填充 + 返回地址
; 64位：缓冲区 + 填充 + saved rbp + 返回地址

; ===== 2. 格式化字符串漏洞 =====
; printf(user_input);  ← 危险！
;
; 利用：
; %x - 泄露栈内存
; %s - 读取任意地址内存（可能崩溃）
; %n - 写入任意地址（严重）

; ===== 3. Use-After-Free =====
; free(ptr);
; use ptr;  ← 危险！
;
; 利用：重用已释放的 chunk，控制内容

; ===== 4. 整数溢出 =====
; int size = user_input * 4;
; malloc(size);  ← 可能溢出分配很小的内存
;
; 利用：整数溢出导致分配不足，后续写入溢出

; ===== 5. 竞态条件 (TOCTOU) =====
; if (access(file, R_OK) == 0) {
;     fd = open(file, O_RDONLY);  ← 中间文件可能被替换
;     read(fd, buf, size);
; }
;
; 利用：符号链接竞争
```

---

## 四、常用寄存器速查

| 寄存器 (64位) | 32位 | 16位 | 8位 | 用途 |
|--------------|------|------|-----|------|
| `rax` | `eax` | `ax` | `al/ah` | 累加器，返回值，系统调用号 |
| `rbx` | `ebx` | `bx` | `bl/bh` | 基址，被调用者保存 |
| `rcx` | `ecx` | `cx` | `cl/ch` | 计数器，第4参数(syscall) |
| `rdx` | `edx` | `dx` | `dl/dh` | 数据，第3参数 |
| `rsi` | `esi` | `si` | `sil` | 源索引，第2参数 |
| `rdi` | `edi` | `di` | `dil` | 目标索引，第1参数 |
| `rbp` | `ebp` | `bp` | `bpl` | 基址指针，被调用者保存 |
| `rsp` | `esp` | `sp` | `spl` | 栈指针 |
| `r8` - `r15` | `r8d`-`r15d` | `r8w`-`r15w` | `r8b`-`r15b` | 额外寄存器 |
| `rip` | `eip` | `ip` | - | 指令指针 |
| `rflags` | `eflags` | `flags` | - | 标志寄存器 |

---

## 五、标志位

| 标志 | 位 | 含义 |
|------|----|------|
| CF | 0 | 进位标志 (Carry Flag) |
| PF | 2 | 奇偶标志 (Parity Flag) |
| AF | 4 | 辅助进位 (Auxiliary Carry) |
| ZF | 6 | 零标志 (Zero Flag) |
| SF | 7 | 符号标志 (Sign Flag) |
| TF | 8 | 陷阱标志 (Trap Flag) |
| IF | 9 | 中断允许 (Interrupt Enable) |
| DF | 10 | 方向标志 (Direction Flag) |
| OF | 11 | 溢出标志 (Overflow Flag) |
