# DEP/NX数据执行防护

### 3.1 DEP原理

DEP (Data Execution Prevention) / NX (No-eXecute) 利用CPU的NX位标记内存页是否可执行。

```
内存页权限:
  可读(R) + 可写(W) + 可执行(X)

  正常段权限:
  .text:  R + X (代码段可执行)
  .data:  R + W (数据段可写不可执行)
  .bss:   R + W
  栈:     R + W (DEP关闭时可能 R+W+X)
  堆:     R + W

DEP开启后:
  栈: R + W (不可执行!)
  堆: R + W (不可执行!)

  尝试在栈上执行代码 -> CPU异常(SIGSEGV)
```

**DEP工作模式**

```
Windows DEP模式:
  OptIn (默认): 仅保护Windows组件和指定进程
  OptOut: 保护所有进程(白名单除外)
  AlwaysOn: 强制保护所有进程
  AlwaysOff: 关闭DEP

Linux NX:
  通过PaX或内核CONFIG_ARCH_MMAP_RND_BITS实现
  默认在支持NX的CPU上启用
```

### 3.2 绕过技术

**ret2libc (return-to-libc)**

```
原理: 不执行shellcode，而是跳转到已存在的可执行代码

传统shellcode:
  栈上放置shellcode -> 跳转到栈地址执行

ret2libc:
  覆盖返回地址为system()函数地址
  栈上构造system("/bin/sh")的参数

  栈布局:
  [填充数据]
  [system地址]     <- 覆盖的返回地址
  [返回地址(可选)]
  ["/bin/sh"地址]  <- system的参数
```

**Return-Oriented Programming (ROP)**

```
ROP原理:
  在可执行代码中寻找以ret结尾的小代码片段(gadget)
  通过连续跳转到不同gadget实现任意功能

  gadget示例:
  0x08048453: pop eax ; ret
  0x08048454: pop ebx ; ret
  0x08048455: mov [eax], ebx ; ret

  ROP链:
  [gadget1地址]  -> pop eax; ret
  [0xbss_addr]   -> eax = bss段地址
  [gadget2地址]  -> pop ebx; ret
  [shellcode]    -> ebx = shellcode内容
  [gadget3地址]  -> mov [eax], ebx; ret (写入shellcode到bss)
  [bss_addr]     -> 跳转到bss执行shellcode

  工具:
  - ROPgadget: 自动搜索gadget
  - Ropper: 另一个gadget搜索工具
  - Pwntools: 自动构造ROP链
```

```bash
# 搜索gadget
ROPgadget --binary ./target
ROPgadget --binary ./target --only "pop|ret"
ROPgadget --binary ./target --depth 10

# 使用pwntools构造ROP
from pwn import *
elf = ELF('./target')
rop = ROP(elf)
rop.call('system', ['/bin/sh'])
print(rop.dump())
```

**ret2syscall**

```
通过ROP调用系统调用:
  eax = 11 (execve系统调用号)
  ebx = "/bin/sh"地址
  ecx = 0
  edx = 0
  int 0x80

  ROP链:
  pop eax; ret      -> eax = 11
  pop ebx; ret       -> ebx = "/bin/sh"地址
  pop ecx; ret       -> ecx = 0
  pop edx; ret       -> edx = 0
  int 0x80
```

**ret2csu (x64)**

```
x64下利用__libc_csu_init函数中的gadget:
  控制rdi/rsi/rdx寄存器(函数参数)
  实现任意函数调用

  __libc_csu_init中的gadget:
  0x_csu1: pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
  0x_csu2: mov rdx, r15; mov rsi, r14; mov edi, r13d; call [r12+rbx*8]
```

---

---

