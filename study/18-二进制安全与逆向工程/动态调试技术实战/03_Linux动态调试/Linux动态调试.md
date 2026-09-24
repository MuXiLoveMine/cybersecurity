# Linux动态调试

### 3.1 GDB基础与进阶

GDB 是 Linux 平台最强大的调试器，既可调试用户态程序也可调试内核。下面从基础到进阶列出核心命令。

**基础命令：**

```
gdb ./target                    启动调试
gdb -pid 1234                   附加到运行中的进程
break main                      在main函数设断点
break *0x401234                 在地址处设断点
watch *0x601040                 写监视点（内存被修改时断下）
rwatch *0x601040                读监视点
awatch *0x601040                读写监视点
run arg1 arg2                   带参数运行
continue / c                    继续执行
next / n                        步过
step / s                        步入
finish                          步出（运行到函数返回
info registers                  显示所有寄存器
info breakpoints                显示断点列表
backtrace / bt                  显示调用栈
```

**进阶命令：**

```
set disassembly-flavor intel    设置Intel语法（默认AT&T）
disas main                      反汇编函数
x/20x 0x601040                  以十六进制查看20字节内存
x/10i $eip                      以指令形式查看10条指令
x/s 0x401234                    以字符串形式查看内存
print/x $eax                    十六进制打印寄存器
set $eax = 0x1234               修改寄存器
set {int}0x601040 = 0xDEAD     修改内存
set follow-fork-mode child      跟踪子进程
catch syscall open              捕获open系统调用
```

**条件断点与命令序列：**

```
break 42 if i==100              条件断点
commands 1                      断点1命中时执行的命令序列
silent
  printf "i=%d, buf=%s\n", i, buf
  continue
end
```

### 3.2 GDB脚本与插件

**.gdbinit 配置文件**：GDB 启动时自动加载 `~/.gdbinit`，常用于设置默认参数。

```
# ~/.gdbinit
set disassembly-flavor intel
set follow-fork-mode child
set print pretty on
set disassemble-next-line on
```

**GDB Python 脚本**：GDB 内置 Python 解释器，可以编写强大的调试脚本。

```python
# trace_decrypt.py - 跟踪解密函数并提取解密结果
import gdb

class TraceDecrypt(gdb.Breakpoint):
    def __init__(self, addr):
        super().__init__("*" + addr, internal=True)
        self.count = 0

    def stop(self):
        self.count += 1
        rdi = int(gdb.parse_and_eval("$rdi"))  # 第一个参数：密文地址
        rsi = int(gdb.parse_and_eval("$rsi"))  # 第二个参数：长度
        inf = gdb.selected_inferior()
        data = bytes(inf.read_memory(rdi, rsi))
        print(f"[Decrypt #{self.count}] len={rsi}, data={data.hex()}")
        gdb.execute("continue")

# 设置断点
TraceDecrypt("0x401234")
print("解密跟踪断点已设置")
```

在 GDB 中加载：
```
(gdb) source trace_decrypt.py
(gdb) run
```

**主流增强插件：**

| 插件 | 特点 | 安装 |
|------|------|------|
| pwndbg | 专注pwn，增强内存/堆显示 | `git clone github.com/pwndbg/pwndbg && ./setup.sh` |
| GEF | 多架构支持、丰富的实用命令 | `echo 'source ~/.gdbinit-gef.py' >> ~/.gdbinit` |
| peda | 经典插件，含pattern等工具 | `echo 'source ~/peda/peda.py' >> ~/.gdbinit` |

pwndbg 常用增强命令：
```
pwndbg> context         显示完整上下文（寄存器/反汇编/栈）
pwndbg> heap            查看堆块
pwndbg> bins            查看fastbin/unsorted bin
pwndbg> cyclic 100      生成De Bruijn pattern
pwndbg> cyclic_offset   查找偏移
pwndbg> ropgadget       查找ROP gadget
pwndbg> vmmap           显示内存映射
pwndbg> search -t string "flag"  搜索内存中的字符串
```

### 3.3 strace/ltrace系统调用跟踪

**strace** 跟踪进程的系统调用，用于分析程序与内核的交互；**ltrace** 跟踪库函数调用。

```bash
# 跟踪所有系统调用
strace ./program arg1

# 只跟踪文件相关
strace -e trace=open,read,write,close ./program

# 跟踪网络相关
strace -e trace=network ./program

# 统计系统调用次数
strace -c ./program

# 跟踪子进程
strace -f ./program

# 附加到运行中的进程
strace -p 1234

# 输出时间戳
strace -t -T ./program

# ltrace 跟踪库函数
ltrace -e malloc+free+strcpy ./program
```

strace 输出示例分析：
```
open("/etc/config", O_RDONLY)          = 3     // 打开文件成功，fd=3
read(3, "secret_data", 11)             = 11   // 读取成功
write(1, "result", 6)                  = 6    // 写入stdout
connect(3, {sa_family=AF_INET, sin_addr=inet_addr("192.168.1.1"), sin_port=htons(80)}, 16) = 0
```

### 3.4 动态链接库调试与核心转储

**LD_PRELOAD 注入**：在目标程序加载前注入自定义库，用于 Hook 函数。

```c
// hook.c - Hook libc的rand函数
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>

int rand(void) {
    static int (*real_rand)(void) = NULL;
    if (!real_rand)
        real_rand = dlsym(RTLD_NEXT, "rand");

    int result = real_rand();
    fprintf(stderr, "[Hook] rand() = %d\n", result);
    return result;
}
```

```bash
gcc -shared -fPIC -o hook.so hook.c -ldl
LD_PRELOAD=./hook.so ./target_program
```

**核心转储分析**：

```bash
# 启用核心转储
ulimit -c unlimited

# 运行崩溃程序
./crash_program
# 输出: Segmentation fault (core dumped)

# 使用GDB分析core文件
gdb ./crash_program core
(gdb) bt                 # 查看崩溃时的调用栈
(gdb) info registers     # 查看崩溃时的寄存器
(gdb) x/i $pc            # 查看崩溃时的指令
```

在 `/proc/sys/kernel/core_pattern` 设置 core 文件的存储路径和命名规则。

---

---

