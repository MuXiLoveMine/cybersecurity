# 第3章 Linux内核基础

### 3.1 Linux内核架构

Linux内核是一个单体内核（Monolithic Kernel），采用模块化设计。了解内核的子系统划分是漏洞分析的基础。

#### 3.1.1 内核子系统划分

**进程调度子系统（Scheduler）**：
- 负责CPU资源分配，决定哪个进程何时运行
- CFS（完全公平调度器）是默认调度器
- 关键数据结构：`task_struct`（进程描述符）、`sched_entity`、`rq`（运行队列）

**内存管理子系统（MM）**：
- 虚拟内存管理：地址空间、VMA（虚拟内存区域）
- 物理内存管理：伙伴系统（Buddy System）、slab/slub分配器
- 页表管理：三级/四级/五级页表
- 反向映射（RMAP）：从物理页找到映射它的所有页表项
- 关键数据结构：`mm_struct`、`vm_area_struct`、`page`

**文件系统子系统（VFS）**：
- 虚拟文件系统（VFS）抽象层，统一文件操作接口
- 具体文件系统：ext4、xfs、btrfs、tmpfs、procfs、sysfs等
- 页缓存（Page Cache）：加速文件I/O
- 关键数据结构：`file`、`inode`、`dentry`、`super_block`

**网络子系统（Net）**：
- 协议栈：TCP、UDP、IP、ICMP等
- 套接字层：统一的socket API
- 网络设备驱动
- Netfilter：网络包过滤框架
- 关键数据结构：`sock`、`sk_buff`、`net_device`

**设备驱动子系统**：
- 字符设备驱动：`/dev`下的字符设备
- 块设备驱动：磁盘等块设备
- 网络设备驱动：网卡驱动
- 总线框架：PCI、USB、SPI、I2C等

#### 3.1.2 内核源码结构

Linux内核源码的主要目录：

```
linux/
├── arch/          # 架构相关代码（x86、arm、mips等）
├── block/         # 块设备层
├── crypto/        # 加密算法
├── Documentation/ # 文档
├── drivers/       # 设备驱动（最大的目录）
├── fs/            # 文件系统
├── include/       # 头文件
├── init/          # 内核初始化（main.c等）
├── ipc/           # 进程间通信
├── kernel/        # 核心子系统（调度、时间、信号等）
├── lib/           # 通用库函数
├── mm/            # 内存管理
├── net/           # 网络协议栈
├── samples/       # 示例代码
├── security/      # 安全模块（LSM、SELinux、AppArmor等）
├── sound/         # 音频子系统
├── tools/         # 工具
└── virt/          # 虚拟化（KVM等）
```

### 3.2 系统调用机制

#### 3.2.1 系统调用入口

Linux的系统调用机制随架构不同而有所差异。以x86_64为例：

1. 用户态将系统调用号存入`rax`寄存器
2. 参数依次存入`rdi`、`rsi`、`rdx`、`r10`、`r8`、`r9`
3. 执行`syscall`指令
4. CPU切换到内核态，跳转到`entry_SYSCALL_64`
5. 保存寄存器上下文（pt_regs结构）
6. 根据rax中的系统调用号，在系统调用表中查找处理函数
7. 调用处理函数，返回值存入rax
8. 通过`swapgs`和`sysretq`返回用户态

#### 3.2.2 系统调用表

系统调用表是一个函数指针数组，定义在`arch/x86/entry/syscalls/syscall_64.tbl`中。

```c
// 简化示例
asmlinkage const sys_call_ptr_t sys_call_table[__NR_syscalls_max + 1] = {
    [0 ... __NR_syscalls_max] = &sys_ni_syscall,
    #include <asm/syscalls_64.h>
};
```

每个系统调用号对应一个内核函数，例如：
- 0号：`sys_read`
- 1号：`sys_write`
- 2号：`sys_open`
- 59号：`sys_execve`

**注意**：在内核漏洞利用中，`sys_call_table`是一个重要的目标。如果能修改它，就可以hook系统调用实现Rootkit功能。但现代内核中，sys_call_table所在的内存页是只读的。

#### 3.2.3 系统调用参数验证

内核在处理用户态传来的指针时必须格外小心，使用专用函数进行安全访问：

- `copy_from_user()`：从用户空间复制数据到内核空间，会检查用户指针的有效性
- `copy_to_user()`：从内核空间复制数据到用户空间
- `get_user()` / `put_user()`：简单类型的安全读写
- `access_ok()`：检查用户空间指针的可访问性

如果驱动或内核代码直接使用用户态指针而不经过这些函数，就可能导致安全漏洞。

### 3.3 内核模块编程

#### 3.3.1 内核模块基础

Linux内核模块（LKM）是可以动态加载和卸载的内核代码扩展。最简单的内核模块：

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Author");
MODULE_DESCRIPTION("A simple example Linux module.");
MODULE_VERSION("0.01");

static int __init hello_init(void) {
    printk(KERN_INFO "Hello, World!\n");
    return 0;
}

static void __exit hello_exit(void) {
    printk(KERN_INFO "Goodbye, World!\n");
}

module_init(hello_init);
module_exit(hello_exit);
```

#### 3.3.2 模块加载与卸载

```bash
# 加载模块
insmod mymodule.ko
modprobe mymodule

# 查看已加载模块
lsmod

# 卸载模块
rmmod mymodule
```

#### 3.3.3 字符设备驱动

字符设备是最常见的驱动类型，也是漏洞利用的常见入口：

```c
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>

#define DEVICE_NAME "mydevice"
#define BUF_LEN 1024

static int major;
static char msg[BUF_LEN];
static struct cdev my_cdev;

static int my_open(struct inode *inode, struct file *file) {
    return 0;
}

static ssize_t my_read(struct file *file, char __user *buf,
                       size_t len, loff_t *offset) {
    int bytes_read = 0;
    // 注意：必须使用copy_to_user而不是直接memcpy
    if (copy_to_user(buf, msg, len)) {
        return -EFAULT;
    }
    return len;
}

static ssize_t my_write(struct file *file, const char __user *buf,
                        size_t len, loff_t *offset) {
    // 漏洞示例：没有检查len的大小，可能导致缓冲区溢出
    if (copy_from_user(msg, buf, len)) {
        return -EFAULT;
    }
    return len;
}

static long my_ioctl(struct file *file, unsigned int cmd, unsigned long arg) {
    // IOCTL处理
    return 0;
}

static struct file_operations fops = {
    .owner = THIS_MODULE,
    .open = my_open,
    .read = my_read,
    .write = my_write,
    .unlocked_ioctl = my_ioctl,
};
```

**漏洞审计要点**：
- 检查用户输入的长度是否被正确验证
- 检查是否所有用户态指针都通过`copy_from_user`/`copy_to_user`访问
- 检查IOCTL命令处理是否验证了参数的合法性

### 3.4 内核数据结构

#### 3.4.1 链表（list_head）

Linux内核广泛使用双向循环链表，定义在`<linux/list.h>`中：

```c
struct list_head {
    struct list_head *next, *prev;
};
```

使用方式（嵌入到宿主结构中）：

```c
struct my_struct {
    int data;
    struct list_head list;  // 链表节点
};

// 初始化
LIST_HEAD(my_list);

// 添加节点
struct my_struct *node = kmalloc(sizeof(*node), GFP_KERNEL);
node->data = 42;
list_add(&node->list, &my_list);

// 遍历
struct my_struct *pos;
list_for_each_entry(pos, &my_list, list) {
    printk(KERN_INFO "data: %d\n", pos->data);
}
```

`list_entry(ptr, type, member)`宏通过链表节点指针反向获取宿主结构体指针，其实现利用了`container_of`宏：

```c
#define container_of(ptr, type, member) ({              \
    const typeof( ((type *)0)->member ) *__mptr = (ptr); \
    (type *)( (char *)__mptr - offsetof(type,member) );})
```

**安全意义**：内核堆溢出中，通过覆盖链表的next/prev指针可以实现任意地址写（类似用户态的unlink攻击）。

#### 3.4.2 哈希表（hlist）

Linux内核使用`hlist`（哈希链表）实现哈希表，特点是头节点只需要一个指针：

```c
struct hlist_head {
    struct hlist_node *first;
};

struct hlist_node {
    struct hlist_node *next;
    struct hlist_node **pprev;
};
```

hlist广泛用于内核中的各种缓存和查找表，如文件描述符表、inode缓存等。

#### 3.4.3 红黑树（rbtree）

Linux内核中的红黑树用于需要有序查找的数据结构，如CFS调度器的运行队列、内存区域管理等。定义在`<linux/rbtree.h>`中。

#### 3.4.4 RCU（Read-Copy-Update）

RCU是Linux内核中一种重要的同步机制，适用于读多写少的场景。

核心思想：
- 读者不需要任何锁，直接读取
- 写者修改数据时，先创建副本，修改副本，然后在适当时机替换原数据
- 被替换的旧数据需要等所有读者都离开临界区后才能释放（宽限期，Grace Period）

常用API：
- `rcu_read_lock()` / `rcu_read_unlock()`：读者端临界区
- `synchronize_rcu()`：等待宽限期结束
- `call_rcu()`：异步等待宽限期，完成后调用回调函数
- `rcu_assign_pointer()`：安全地赋值RCU保护的指针
- `rcu_dereference()`：安全地读取RCU保护的指针

**安全意义**：RCU的使用引入了新的竞态条件类型——use-after-free的变体。如果在宽限期结束前就释放了对象，或者读者端没有正确使用`rcu_dereference`，就可能导致漏洞。

---

---

## 📋 内容审核与补充建议

> 针对「第3章 Linux内核基础」部分的内容审核结果：

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
