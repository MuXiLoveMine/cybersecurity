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

> **免责声明**：本文档仅用于教育和授权安全测试目的。漏洞利用技术应在合法授权范围内使用。未经授权对他人系统进行安全测试是违法行为。

---

*本文档最后更新：2026年9月*

---

## 📋 内容审核与补充建议

> 针对「附录：pwntools常用API速查」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
