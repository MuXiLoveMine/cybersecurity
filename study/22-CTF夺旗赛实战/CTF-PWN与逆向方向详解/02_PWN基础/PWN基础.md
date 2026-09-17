# PWN基础

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

---

## 📋 内容审核与补充建议

> 针对「PWN基础」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
