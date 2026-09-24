; ============================================================
; anti_debug.asm —— 反调试技巧 (Linux x86_64)
;
; 包含多种反调试检测方法：
;   1. ptrace 检测
;   2. 时间差检测
;   3. 软件断点检测 (INT 3 / 0xCC)
;   4. 硬件断点检测
;   5. /proc/self/status 检测
;   6. 指令时序检测
;   7. 段寄存器检测
;
; 编译：nasm -f elf64 anti_debug.asm -o anti_debug.o
; 链接：gcc -nostdlib anti_debug.o -o anti_debug
;
; 注意：本代码仅用于安全研究与学习目的
; ============================================================

section .data
    msg_normal      db  '未检测到调试器', 0xA
    msg_normal_len  equ $ - msg_normal

    msg_debug       db  '检测到调试器！', 0xA
    msg_debug_len   equ $ - msg_debug

    newline         db  0xA

section .text
    global _start

_start:
    ; ============================================================
    ; 反调试的核心思路：
    ; 1. 检测调试器是否存在
    ; 2. 如果存在，执行不同的代码路径（退出、破坏数据等）
    ; 3. 检测方法应该分散在代码各处，增加绕过难度
    ; ============================================================

    ; ---------- 方法1：ptrace 检测 ----------
    ; Linux 下进程只能被一个调试器 ptrace
    ; 如果自己 ptrace 自己失败，说明已有调试器附加
    ;
    ; long ptrace(enum __ptrace_request request, pid_t pid,
    ;             void *addr, void *data)
    ; request = PTRACE_TRACEME = 0

    mov     rax, 101                    ; sys_ptrace (x86_64 = 101)
    xor     rdi, rdi                    ; PTRACE_TRACEME = 0
    xor     rsi, rsi                    ; pid = 0 (当前进程)
    xor     rdx, rdx                    ; addr = NULL
    xor     r10, r10                    ; data = NULL
    syscall

    cmp     rax, 0
    jl      debugger_detected           ; 返回 -1 表示失败

    ; ---------- 方法2：时间差检测 ----------
    ; 正常执行两条 rdtsc 指令间隔很小
    ; 如果被单步调试，间隔会很大
    ;
    ; rdtsc: Read Time-Stamp Counter
    ; 返回：edx:eax = 64位时间戳计数器

    rdtsc                               ; 第一次读取
    shl     rdx, 32
    or      rax, rdx                    ; rax = 完整时间戳
    mov     rbx, rax                    ; 保存

    ; 插入一些正常代码
    xor     rax, rax
    xor     rcx, rcx
    mov     cx, 100
timing_loop:
    loop    timing_loop

    rdtsc                               ; 第二次读取
    shl     rdx, 32
    or      rax, rdx
    sub     rax, rbx                    ; 计算差值

    ; 阈值判断（根据实际情况调整）
    ; 正常循环几百次只需几千个周期
    cmp     rax, 100000
    jg      debugger_detected           ; 间隔过大，可能在被调试

    ; ---------- 方法3：软件断点检测 ----------
    ; 调试器设置的软件断点是 INT 3 指令（opcode = 0xCC）
    ; 检查关键代码位置是否被修改为 0xCC

    call    check_breakpoint
    ; check_breakpoint 返回后继续...

    ; ---------- 方法4：INT 3 异常处理检测 ----------
    ; 通过设置自己的异常处理，故意触发 INT 3
    ; 如果调试器存在，异常会被调试器捕获
    ; 这种方法需要信号处理，比较复杂

    ; ---------- 方法5：检查 /proc/self/status ----------
    ; TracerPid 字段不为 0 表示被调试
    ; 此方法需要文件操作，较易检测

    ; ---------- 方法6：段寄存器 FS/GS ----------
    ; 调试器可能会修改段寄存器
    ; 某些调试技术会使用 FS 寄存器

    mov     rax, fs:[0]                 ; 读取 FS 段
    ; 检查预期值...

    ; ---------- 方法7：指令前缀检测 ----------
    ; 调试器单步可能使用 TF 标志
    ; 可以通过检查 EFLAGS 的 TF 位

    pushfq
    pop     rax
    test    rax, 0x100                  ; 检查 TF 位 (bit 8)
    jnz     debugger_detected           ; TF=1，可能在单步

    ; ---------- 未检测到调试器 ----------
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_normal
    mov     rdx, msg_normal_len
    syscall
    jmp     exit_program

debugger_detected:
    mov     rax, 1
    mov     rdi, 1
    mov     rsi, msg_debug
    mov     rdx, msg_debug_len
    syscall

exit_program:
    mov     rax, 60
    mov     rdi, 0
    syscall

; ============================================================
; 函数：check_breakpoint
; 检查自身代码中的软件断点（0xCC）
; ============================================================
check_breakpoint:
    push    rbx
    push    rcx
    push    rdx
    push    rsi
    push    rdi

    ; 检查从 check_start 到 check_end 之间的代码
    ; 是否包含 0xCC (INT 3)
    mov     rsi, check_bp_start
    mov     rcx, check_bp_end - check_bp_start

scan_bp_loop:
    lodsb
    cmp     al, 0xCC                    ; INT 3 指令
    je      bp_found
    loop    scan_bp_loop

    pop     rdi
    pop     rsi
    pop     rdx
    pop     rcx
    pop     rbx
    ret

bp_found:
    pop     rdi
    pop     rsi
    pop     rdx
    pop     rcx
    pop     rbx
    jmp     debugger_detected

; 这段代码区域用于检查断点
check_bp_start:
    nop
    nop
    nop
    xor     rax, rax
    add     rax, 100
check_bp_end:
    ret

; ============================================================
; 反调试技术总结：
;
; Linux 平台反调试方法：
;
; 1. ptrace 检测
;    - 调用 ptrace(PTRACE_TRACEME, ...)
;    - 返回 -1 表示已有调试器
;    - 最简单、最常用
;
; 2. 时间差检测
;    - rdtsc 指令读取时间戳计数器
;    - 计算代码段执行时间
;    - 阈值判断是否异常
;    - 可被 RDTSC 虚拟化绕过
;
; 3. 软件断点检测
;    - 扫描自身代码寻找 0xCC (INT 3)
;    - 计算代码段哈希校验
;    - 对关键函数进行校验和检查
;
; 4. 硬件断点检测
;    - 检查 DR0-DR7 调试寄存器
;    - 这些寄存器控制硬件断点
;    - 用户模式下可通过特殊方法读取
;
; 5. /proc 文件系统检测
;    - /proc/self/status 中的 TracerPid
;    - /proc/self/stat 中的状态字段
;    - /proc/self/maps 检查映射
;
; 6. 系统调用检测
;    - 检查 ptrace 系统调用痕迹
;    - 监控异常的系统调用模式
;
; Windows 平台（补充知识）：
;
; 1. IsDebuggerPresent() API
; 2. CheckRemoteDebuggerPresent()
; 3. NtQueryInformationProcess() - ProcessDebugPort
; 4. PEB->BeingDebugged 标志
; 5. OutputDebugString() 检测
; 6. 时间差检测 (GetTickCount / QueryPerformanceCounter)
;
; 反调试绕过方法（了解对手）：
;
; 1. Hook ptrace 系统调用
; 2. 修改返回值
; 3. 修补反调试代码（NOP 掉检查）
; 4. 使用 ScyllaHide 等插件
; 5. 虚拟化/模拟执行
; 6. 手动单步绕过
;
; 反反调试对抗：
;
; 1. 多种检测方法组合使用
; 2. 检测代码分散在各处
; 3. 检测结果延迟使用（不立即退出）
; 4. 加密关键代码，检测通过后才解密
; 5. 检测 Hook 检测
; 6. 使用自修改代码
;
; 注意事项：
; - 反调试不是绝对安全的，只是增加分析成本
; - 需要平衡安全性和性能开销
; - 要考虑误报的情况（如虚拟机环境）
; ============================================================
