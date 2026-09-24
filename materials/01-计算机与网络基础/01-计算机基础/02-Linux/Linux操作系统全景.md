# Linux 操作系统全景

> 本文系统介绍 Linux 操作系统的全貌，从内核架构、文件系统、权限模型、进程管理、常用命令、网络配置、安全机制到 Shell 脚本与包管理。面向系统管理员、运维工程师和安全工程师，深度覆盖操作参考 + 原理理解 + 安全加固。示例覆盖 Ubuntu/Debian、CentOS/RHEL、Arch 等主流发行版。

---

## 目录

- [一、Linux 的定义、历史与发行版](#一linux-的定义历史与发行版)
- [二、内核架构](#二内核架构)
- [三、文件系统与目录结构](#三文件系统与目录结构)
- [四、用户与权限](#四用户与权限)
- [五、进程与服务](#五进程与服务)
- [六、常用命令](#六常用命令)
- [七、网络配置](#七网络配置)
- [八、安全机制](#八安全机制)
- [九、Shell 与脚本](#九shell-与脚本)
- [十、包管理](#十包管理)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、Linux 的定义、历史与发行版

### 1.1 什么是 Linux

Linux 是一套**免费、开源、类 UNIX 的操作系统内核**（Kernel），由 Linus Torvalds 于 1991 年首次发布。严格来说，"Linux"指的是内核，而"Linux 操作系统"指的是基于 Linux 内核、搭配 GNU 工具链和各种应用程序的完整操作系统（也称为 GNU/Linux）。

```
Linux 操作系统 = Linux 内核 + GNU 工具 + 系统库 + 应用程序 + 桌面环境/Shell
```

| 概念 | 英文 | 说明 |
|------|------|------|
| **内核** | Kernel | 操作系统核心，管理硬件和资源（Linux 就是内核） |
| **发行版** | Distribution | 内核 + 软件包的完整集合（Ubuntu、CentOS 等） |
| **GNU** | GNU's Not Unix | 自由软件项目，提供了 Linux 的大部分工具链 |
| **POSIX** | Portable Operating System Interface | 操作系统接口标准，Linux 兼容 |

### 1.2 历史时间线

```
1969  Unix 在贝尔实验室诞生
1983  GNU 项目启动（Richard Stallman）
1987  MINIX 发布（Andrew Tanenbaum，教学用）
1991  Linus Torvalds 发布 Linux 0.01（~1 万行代码）
1992  Linux 采用 GPL v2 许可证
1993  Slackware 发行（第一个广泛使用的发行版）
1993  Debian 项目启动
1994  Linux 1.0 发布（~17 万行代码）
1995  Red Hat 成立
1996  Linux 2.0（支持 SMP 多处理器）
2003  Linux 2.6（革命性更新，持续 15 年）
2004  Ubuntu 首个版本发布
2014  CentOS 加入 Red Hat
2015  Linux 4.0
2019  Linux 5.0
2022  Linux 6.0（~3000 万行代码）
2024  Linux 6.8+
```

### 1.3 内核 vs 发行版

```
┌──────────────────────────────────────────────────┐
│                  应用程序层                        │
│  Web服务器 / 数据库 / 桌面环境 / 办公软件 / 游戏...   │
├──────────────────────────────────────────────────┤
│                  系统库 / 工具                     │
│  glibc / bash / coreutils / systemd / Xorg...      │
├──────────────────────────────────────────────────┤
│               Linux 内核（Kernel）                  │
│  进程调度 / 内存管理 / 文件系统 / 驱动 / 网络栈       │
├──────────────────────────────────────────────────┤
│                      硬件                          │
│  CPU / 内存 / 磁盘 / 网卡 / GPU / 外设               │
└──────────────────────────────────────────────────┘
```

| 维度 | 内核（Kernel） | 发行版（Distribution） |
|------|---------------|---------------------|
| **定义** | 操作系统的核心 | 内核 + 软件包的完整系统 |
| **开发方** | 全球社区，Linus 维护 | 各发行版厂商/社区 |
| **更新** | 持续开发，新版本频繁 | 有发布周期（LTS/滚动） |
| **数量** | 只有一个（不同版本） | 数百种 |
| **例子** | Linux 5.15、Linux 6.5 | Ubuntu 22.04、CentOS 7、Arch |

### 1.4 主流发行版分类

```
                    Linux 发行版家族
                          │
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
     Debian 系         Red Hat 系      Arch 系
          │               │               │
    ┌─────┴─────┐    ┌────┴─────┐    ┌──┴────┐
    ↓           ↓    ↓          ↓    ↓       ↓
  Ubuntu     Debian  RHEL     CentOS  Arch   Manjaro
    │           │    │          Stream │
    ↓           ↓    ↓          ↓    ↓
  Mint/Kali   ...  Fedora    Rocky/   ...
                              Alma
```

| 发行版 | 所属家族 | 包管理器 | 特点 | 适用场景 |
|--------|---------|---------|------|---------|
| **Ubuntu** | Debian 系 | apt/dpkg | 易用、社区大、LTS 支持 | 桌面/服务器/云 |
| **Debian** | Debian 系 | apt/dpkg | 稳定、自由软件严格 | 服务器/桌面 |
| **CentOS/Rocky/Alma** | RHEL 系 | yum/dnf/rpm | 企业级稳定、兼容 RHEL | 企业服务器 |
| **RHEL** | RHEL 系 | yum/dnf/rpm | 商业支持、最稳定 | 企业生产环境 |
| **Fedora** | RHEL 系 | dnf/rpm | 前沿技术、快速迭代 | 桌面/开发机 |
| **Arch Linux** | Arch 系 | pacman | 滚动更新、KISS 原则 | 高级用户/定制 |
| **openSUSE** | SUSE 系 | zypper/rpm | 稳定、YaST 管理 | 企业/桌面 |
| **Kali Linux** | Debian 系 | apt/dpkg | 安全测试工具集 | 渗透测试 |

---

## 二、内核架构

Linux 内核是**宏内核（Monolithic Kernel）**设计，所有核心服务运行在内核态（Ring 0），但通过可加载内核模块（LKM）实现了模块化扩展。

### 2.1 内核架构全景

```
┌──────────────────────────────────────────────────────────┐
│                    用户空间（User Space）                    │
│  Shell / 应用程序 / 系统库（glibc）                          │
├───────────────────── 系统调用接口 ─────────────────────────┤
│                    内核空间（Kernel Space）                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   系统调用接口层                        │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  进程管理子系统        │        内存管理子系统           │  │
│  │  - 调度器（CFS）       │        - 虚拟内存              │  │
│  │  - 进程创建/销毁       │        - 伙伴系统              │  │
│  │  - 进程间通信（IPC）   │        - Slab/Slub 分配器      │  │
│  │  - 信号处理           │        - 页表管理              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │              VFS（虚拟文件系统）                        │  │
│  │  ext4 / xfs / btrfs / nfs / proc / sysfs / tmpfs       │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  I/O 子系统           │        网络子系统               │  │
│  │  - 块设备层           │        - TCP/IP 协议栈          │  │
│  │  - I/O 调度器         │        - Netfilter / nftables   │  │
│  │  - 设备驱动           │        - 套接字层               │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │           安全子系统（LSM 框架）                         │  │
│  │         SELinux / AppArmor / Landlock                  │  │
│  └──────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────┤
│                       硬件层                                │
└──────────────────────────────────────────────────────────┘
```

### 2.2 进程调度子系统

| 组件 | 说明 |
|------|------|
| **CFS（完全公平调度器）** | Linux 默认调度器，基于红黑树，按虚拟运行时间排序 |
| **调度类** | Deadline（实时）、RT（实时 FIFO/RR）、CFS（普通）、Idle |
| **进程优先级** | nice 值（-20 ~ 19）→ 映射到 100~139 的静态优先级 |
| **时间片** | CFS 无固定时间片，按权重分配 CPU 时间 |
| **调度实体** | 可被调度的单位（进程/线程/进程组） |
| **SMP 负载均衡** | 多核之间平衡负载 |

```
CFS 工作原理：
  - 每个进程有一个"虚拟运行时间"（vruntime）
  - 运行时 vruntime 增加（优先级越高，增加越慢）
  - 总是选择 vruntime 最小的进程运行
  - 用红黑树组织就绪队列，O(log n) 查找
```

### 2.3 内存管理子系统

| 组件 | 说明 |
|------|------|
| **虚拟内存** | 每个进程独立地址空间，通过页表映射到物理内存 |
| **伙伴系统** | 物理页分配器，按 2 的幂次分配，减少外部碎片 |
| **Slab/Slub 分配器** | 内核小对象分配（如 inode、task_struct），缓存常用对象 |
| **页表** | x86_64 四级页表（PML4→PDPT→PD→PT） |
| **缺页中断** | 访问未加载页面时触发，从磁盘加载 |
| **OOM Killer** | 内存不足时选择进程杀掉以释放内存 |
| **Swap** | 磁盘交换分区/文件，扩展可用内存 |

### 2.4 文件系统子系统（VFS）

VFS（Virtual File System）是 Linux 的文件系统抽象层，为上层提供统一接口，下层对接各种具体文件系统。

```
用户进程
   │ read() / write()
   ↓
glibc（系统调用封装）
   │ syscall
   ↓
VFS（虚拟文件系统）
   │ 统一接口
   ├── ext4 ─┐
   ├── xfs   ├── 磁盘文件系统
   ├── btrfs ─┘
   ├── proc  ─┐
   ├── sysfs  ├── 伪文件系统
   ├── tmpfs ─┘
   ├── nfs   ─┐
   ├── cifs   ├── 网络文件系统
   └── 9p    ─┘
```

### 2.5 网络子系统

```
应用层 → socket()/recv()/send()
             │
         套接字层（Socket Layer）
             │  L4
         协议族层（TCP/UDP/ICMP/RAW）
             │  L3
         IP 层（路由/转发/分片）
             │  L2
         网络设备层（net_device）
             │
         网卡驱动（Driver）
             │
         物理网卡（NIC）

关键组件：
  - Netfilter：包过滤框架（iptables/nftables 底层）
  - eBPF：可编程内核网络（现代扩展）
  - TCP 协议栈：拥塞控制（BBR/CUBIC）
  - 连接跟踪（conntrack）：NAT/防火墙基础
```

### 2.6 设备驱动

| 驱动类型 | 说明 | 示例 |
|---------|------|------|
| **字符设备** | 按字节流访问 | 串口、终端、/dev/null |
| **块设备** | 按块随机访问 | 磁盘、SSD、RAM 盘 |
| **网络设备** | 数据包收发 | 网卡、虚拟网卡 |
| **平台设备** | 板级设备 | I2C、SPI、GPIO |
| **USB 设备** | USB 总线设备 | U 盘、USB 网卡 |

```
可加载内核模块（LKM）：
  - 内核可以动态加载/卸载驱动
  - 文件格式：.ko（Kernel Object）
  - 命令：insmod / rmmod / modprobe
  - 查看：lsmod
  - 位置：/lib/modules/$(uname -r)/
```

> 🔑 **安全提示**：加载恶意内核模块可以获得最高权限（Ring 0）。生产环境应启用 Secure Boot + 内核模块签名，限制未签名模块加载。

### 2.7 安全子系统（LSM）

LSM（Linux Security Modules）是 Linux 内核的安全框架，允许"插接"不同的安全模型。

| LSM 模块 | 类型 | 说明 |
|---------|------|------|
| **SELinux** | MAC | 强制访问控制，RHEL/CentOS 默认启用 |
| **AppArmor** | MAC | 基于路径的强制访问控制，Ubuntu 默认 |
| **Landlock** | 沙箱 | 进程级沙箱，无全局策略 |
| **Smack** | MAC | 简化 MAC，嵌入式用 |
| **TOMOYO** | MAC | 路径为基础的 MAC |

---

## 三、文件系统与目录结构

### 3.1 常见文件系统

| 文件系统 | 类型 | 最大文件 | 最大卷 | 日志 | 特点 | 典型场景 |
|---------|------|---------|--------|------|------|---------|
| **ext4** | 本地 | 16TB | 1EB | ✅ | 稳定、成熟、Linux 默认 | 通用服务器 |
| **XFS** | 本地 | 8EB | 8EB | ✅ | 高性能、大文件、RHEL 默认 | 大数据/数据库 |
| **btrfs** | 本地 | 16EB | 16EB | ✅(CoW) | 快照、校验、子卷、压缩 | 桌面/备份 |
| **ZFS** | 本地 | 16EB | 256ZB | ✅(CoW) | 企业级、数据完整性、RAID-Z | 文件服务器/NAS |
| **tmpfs** | 内存 | — | RAM 大小 | — | 内存文件系统，断电丢失 | /tmp、缓存 |
| **procfs** | 伪 | — | — | — | 进程/内核信息（/proc） | 系统监控 |
| **sysfs** | 伪 | — | — | — | 设备/驱动信息（/sys） | 设备管理 |
| **nfs** | 网络 | — | — | — | 网络文件共享 | NAS/集群 |
| **cifs/smbfs** | 网络 | — | — | — | Windows 文件共享 | 跨平台共享 |
| **overlayfs** | 层叠 | — | — | — | 联合挂载（上层可写下层只读） | Docker/容器 |

### 3.2 inode

inode（索引节点）是 Linux 文件系统的核心概念，存储文件的元数据。

```
inode 包含的信息：
  ✓ 文件类型（普通文件/目录/符号链接/设备等）
  ✓ 权限位（rwxrwxrwx）
  ✓ 所有者 UID / 所属组 GID
  ✓ 文件大小（字节）
  ✓ 时间戳（atime/mtime/ctime）
  ✓ 硬链接数
  ✓ 数据块指针（直接/间接/三重间接）

✗ inode 不包含：文件名（文件名存在目录项中）
```

| 概念 | 说明 |
|------|------|
| **inode 号** | 每个文件的唯一编号 |
| **目录项（dentry）** | 文件名 → inode 号的映射 |
| **硬链接** | 多个文件名指向同一个 inode（同文件系统内） |
| **符号链接** | 文件内容是另一个文件的路径（可跨文件系统） |

```bash
# 查看文件 inode 号
ls -i filename
stat filename

# 查看文件系统 inode 使用情况
df -i

# 硬链接
ln source target

# 软链接（符号链接）
ln -s source target
```

### 3.3 FHS 目录结构

FHS（Filesystem Hierarchy Standard）定义了 Linux 目录结构的标准。

```
/                               根目录
├── bin/                        基本命令二进制（所有用户）
├── boot/                       引导加载文件（内核、initrd、GRUB）
├── dev/                        设备文件（/dev/null、/dev/sda、/dev/tty）
├── etc/                        系统配置文件
│   ├── passwd                  用户信息
│   ├── shadow                  用户密码哈希
│   ├── group                   组信息
│   ├── hosts                   主机名映射
│   ├── resolv.conf             DNS 配置
│   ├── fstab                   挂载表
│   ├── crontab                 全局定时任务
│   ├── sysconfig/              系统配置（RHEL 系）
│   ├── network/                网络配置（Debian 系）
│   ├── apt/                    apt 配置（Debian 系）
│   ├── yum/                    yum 配置（RHEL 系）
│   ├── ssh/                    SSH 配置
│   ├── sudoers                 sudo 配置
│   └── systemd/                systemd 配置
├── home/                       用户主目录
│   ├── alice/                  用户 alice 的目录
│   └── bob/                    用户 bob 的目录
├── lib/                        基本共享库和内核模块
├── lib64/                      64 位共享库
├── media/                      可移动媒体挂载点（U盘、光盘）
├── mnt/                        临时挂载点
├── opt/                        可选软件包
├── proc/                       进程和内核信息虚拟文件系统
│   ├── cpuinfo                 CPU 信息
│   ├── meminfo                 内存信息
│   ├── version                 内核版本
│   ├── sys/                    内核参数
│   ├── <pid>/                  各进程信息
│   └── net/                    网络信息
├── root/                       root 用户主目录
├── run/                        运行时数据（系统启动以来）
├── sbin/                       系统管理二进制（root 用）
├── srv/                        服务数据（www、ftp）
├── sys/                        系统设备虚拟文件系统
├── tmp/                        临时文件（重启可能清空）
├── usr/                        Unix System Resources（用户程序和数据）
│   ├── bin/                    用户命令
│   ├── sbin/                   系统管理命令
│   ├── lib/                    共享库
│   ├── lib64/                  64 位共享库
│   ├── local/                  本地安装软件
│   ├── include/                头文件
│   └── share/                  共享数据（文档、图标、man）
└── var/                        可变数据
    ├── log/                    系统日志
    ├── spool/                  打印/邮件队列
    ├── cache/                  缓存数据
    ├── lib/                    应用状态数据
    ├── tmp/                    重启保留的临时文件
    └── www/                    Web 根目录
```

### 3.4 挂载

挂载（Mount）是将文件系统附加到目录树的指定位置（挂载点）的操作。

```bash
# 查看挂载信息
mount
df -h
cat /proc/mounts

# 挂载磁盘
mount /dev/sdb1 /data

# 挂载指定文件系统类型
mount -t ext4 /dev/sdb1 /data

# 挂载 ISO 文件（回环设备）
mount -o loop /path/to/image.iso /mnt/iso

# 卸载
umount /data
umount /dev/sdb1

# 强制卸载（占用时慎用）
umount -f /data

# 按 fstab 挂载所有
mount -a
```

**/etc/fstab 格式**：

```
# <设备>        <挂载点>  <文件系统>  <挂载选项>              <dump> <fsck>
/dev/sda1       /boot     ext4        defaults                0      1
/dev/sda2       /         ext4        defaults                0      1
/dev/sda3       swap      swap        defaults                0      0
/dev/sdb1       /data     xfs         defaults,noatime        0      0
tmpfs           /tmp      tmpfs       defaults,size=2G       0      0
```

| 字段 | 说明 |
|------|------|
| **设备** | 设备路径、UUID、LABEL |
| **挂载点** | 挂载到哪个目录 |
| **文件系统** | ext4/xfs/swap/tmpfs 等 |
| **挂载选项** | defaults/noatime/ro/nodev 等 |
| **dump** | 0=不备份，1=备份 |
| **fsck** | 0=不检查，1=最先检查（根分区），2=其他 |

> **安全提示**：挂载选项如 `nodev`（不解释设备文件）、`nosuid`（忽略 SUID/SGID）、`noexec`（不允许执行）可用于加固。例如 /tmp 分区应挂载为 `nodev,nosuid,noexec`。

---

## 四、用户与权限

### 4.1 用户与组

| 概念 | 英文 | 说明 |
|------|------|------|
| **用户** | User | 系统登录身份，有唯一 UID |
| **组** | Group | 用户集合，有唯一 GID |
| **UID** | User ID | 用户标识符（0=root，1-999=系统，1000+=普通） |
| **GID** | Group ID | 组标识符 |
| **主组** | Primary Group | 用户默认组，创建文件时的所属组 |
| **附加组** | Supplementary Group | 用户额外所属的组 |

```bash
# 查看当前用户
whoami
id

# 查看用户信息
cat /etc/passwd
# 格式：用户名:x:UID:GID:注释:主目录:登录Shell

# 查看密码信息（需 root）🔑
cat /etc/shadow
# 格式：用户名:密码哈希:上次修改:最小年龄:最大年龄:警告:禁用:过期:保留

# 查看组
cat /etc/group
groups username

# 创建用户（需 root）🔑
useradd -m -s /bin/bash username
# -m 创建主目录，-s 指定登录 Shell

# 删除用户
userdel -r username   # -r 同时删除主目录

# 修改密码
passwd username

# 创建组
groupadd groupname

# 将用户加入组
usermod -aG groupname username

# 切换用户
su - username        # 登录式切换（环境变量重置）
su username          # 非登录式切换
```

### 4.2 文件权限

```
权限表示（10 位）：

-rwxr-xr-- 1 user group 4096 Sep 24 10:00 file.txt
││││││││││
│││││││││└── 其他用户（Other）：只读
││││││││└─── 其他用户的执行位
│││││││└──── 其他用户的写位
││││││└───── 其他用户的读位
│││││└────── 所属组（Group）：读+执行
││││└─────── 组执行位
│││└──────── 组写位
││└───────── 组读位
│└────────── 所有者（Owner）：读+写+执行
└─────────── 文件类型（-=普通文件 d=目录 l=符号链接 b=块设备 c=字符设备）
```

| 权限 | 对文件的意义 | 对目录的意义 |
|------|-------------|-------------|
| **r（读）** | 可以读取文件内容 | 可以列出目录内容（ls） |
| **w（写）** | 可以修改文件内容 | 可以在目录中增删文件 |
| **x（执行）** | 可以执行文件（程序/脚本） | 可以进入目录（cd） |

**数字表示法**：

```
r = 4
w = 2
x = 1

rwxr-xr-- = 754
rwx = 4+2+1 = 7（所有者）
r-x = 4+0+1 = 5（组）
r-- = 4+0+0 = 4（其他）

常见权限：
  755  rwxr-xr-x   可执行文件/目录（所有者可写，其他人可读执行）
  644  rw-r--r--   普通文件（所有者可写，其他人只读）
  600  rw-------   私密文件（仅所有者读写，如 SSH 私钥）
  700  rwx------   私密目录（仅所有者完全控制，如 ~/.ssh）
  777  rwxrwxrwx   完全开放（⚠️ 危险，尽量不用）
```

```bash
# 修改权限
chmod 755 filename
chmod u+x filename          # 所有者加执行权限
chmod g-w filename          # 组减写权限
chmod o-rwx filename        # 其他用户去掉所有权限
chmod -R 644 /data/*.txt    # 递归修改

# 修改所有者
chown user:group filename   # 同时改所有者和组🔑
chown user filename         # 只改所有者🔑
chgrp group filename        # 只改组🔑
chown -R user:group /dir    # 递归修改🔑
```

### 4.3 特殊权限位

| 权限 | 文件 | 目录 | 数字 |
|------|------|------|------|
| **SUID** | 执行时获得文件所有者权限 | 无意义 | 4000 |
| **SGID** | 执行时获得文件所属组权限 | 新建文件继承目录的组 | 2000 |
| **Sticky Bit** | 无意义 | 只有所有者/root 能删除自己的文件 | 1000 |

```bash
# 设置 SUID
chmod u+s /path/to/program
chmod 4755 /path/to/program

# 设置 SGID（目录）
chmod g+s /data/shared
chmod 2775 /data/shared

# 设置 Sticky Bit
chmod +t /tmp
chmod 1777 /tmp

# 查看 SUID/SGID 文件
find / -perm -4000 2>/dev/null
find / -perm -2000 2>/dev/null
```

> ⚠️ **安全提示**：SUID 程序是提权常见路径。例如有漏洞的 SUID 程序可被用来获得 root 权限。应定期审计系统中的 SUID 文件。

### 4.4 ACL

ACL（Access Control List）提供比传统 rwx 更细粒度的权限控制。

```bash
# 安装 ACL 工具
# Debian/Ubuntu
apt install acl
# RHEL/CentOS
yum install acl

# 查看 ACL
getfacl filename

# 设置 ACL
setfacl -m u:alice:rwx filename    # 给用户 alice 读写执行
setfacl -m g:developers:rw filename  # 给组 developers 读写
setfacl -m o::--- filename        # 其他用户无权限

# 递归设置
setfacl -R -m u:alice:rwx /data/

# 删除 ACL
setfacl -x u:alice filename        # 删除 alice 的 ACL
setfacl -b filename                # 删除所有 ACL
```

### 4.5 sudo

sudo（SuperUser DO）允许普通用户以其他用户身份（通常是 root）执行命令。

```bash
# 基本用法
sudo command

# 以 root 身份打开 Shell
sudo -i
sudo su -

# 以指定用户执行
sudo -u username command

# 编辑 sudoers 文件（推荐用 visudo）🔑
visudo
# 直接编辑 /etc/sudoers 有语法错误会导致 sudo 不可用

# 查看当前用户的 sudo 权限
sudo -l
```

**sudoers 配置示例**：

```sudoers
# 允许用户 alice 执行所有命令（需密码）
alice ALL=(ALL:ALL) ALL

# 允许用户 bob 执行所有命令（无需密码）
bob ALL=(ALL:ALL) NOPASSWD: ALL

# 允许组 admins 管理服务
%admins ALL=(ALL) /usr/bin/systemctl restart nginx, /usr/bin/systemctl reload nginx

# 禁止用户执行特定命令
mallory ALL=(ALL) ALL, !/usr/bin/su, !/bin/bash
```

> ⚠️ **安全提示**：NOPASSWD 配置应谨慎使用。如果 sudo 配置允许执行任意命令且无需密码，等同于 root 权限。

### 4.6 PAM

PAM（Pluggable Authentication Modules）是 Linux 的可插拔认证框架，各种认证方式以模块形式存在，可灵活组合。

```
PAM 配置文件：
  /etc/pam.d/             各服务的 PAM 配置
  /etc/pam.d/login        登录
  /etc/pam.d/sshd         SSH
  /etc/pam.d/su           su 命令
  /etc/pam.d/sudo         sudo
  /etc/pam.d/passwd       修改密码

PAM 模块：
  pam_unix.so           传统 Unix 认证（/etc/shadow）
  pam_ldap.so           LDAP 认证
  pam_krb5.so           Kerberos 认证
  pam_cracklib.so       密码复杂度检查
  pam_tally2.so         登录失败锁定
  pam_limits.so         资源限制
  pam_motd.so           登录提示信息
```

```bash
# 查看资源限制（ulimit）
ulimit -a

# 修改资源限制（临时）
ulimit -n 65535    # 打开文件数

# 永久修改（/etc/security/limits.conf）
# *  soft  nofile  65535
# *  hard  nofile  65535
```

---

## 五、进程与服务

### 5.1 进程基础

| 概念 | 英文 | 说明 |
|------|------|------|
| **进程** | Process | 程序的一次执行，资源分配单位 |
| **线程** | Thread | 进程内的执行流，CPU 调度单位 |
| **PID** | Process ID | 进程唯一标识 |
| **PPID** | Parent PID | 父进程 ID |
| **前台进程** | Foreground | 占据终端，可交互 |
| **后台进程** | Background | 不占据终端，独立运行 |
| **守护进程** | Daemon | 长期运行的后台进程（如 sshd、nginx） |
| **僵尸进程** | Zombie | 已终止但父进程未回收 |
| **孤儿进程** | Orphan | 父进程已死，由 init 接管 |

**进程状态**：

| 状态 | ps 代码 | 说明 |
|------|---------|------|
| **运行** | R | 正在 CPU 上运行或在就绪队列 |
| **睡眠（可中断）** | S | 等待事件，可被信号唤醒 |
| **睡眠（不可中断）** | D | 等待 I/O，不可被信号唤醒 |
| **停止** | T | 被暂停（如 Ctrl+Z） |
| **僵尸** | Z | 已终止，等待父进程回收 |
| **死亡** | X | 即将被销毁 |

### 5.2 信号（Signal）

信号是进程间通信的一种方式，用于通知进程发生了某个事件。

| 信号 | 编号 | 名称 | 作用 |
|------|------|------|------|
| **SIGHUP** | 1 | 挂起 | 终端断开，常用于重新加载配置 |
| **SIGINT** | 2 | 中断 | Ctrl+C，终止进程 |
| **SIGQUIT** | 3 | 退出 | Ctrl+\，终止并产生 core dump |
| **SIGKILL** | 9 | 杀死 | 强制终止，不可捕获/忽略 |
| **SIGUSR1** | 10 | 用户信号1 | 自定义用途 |
| **SIGSEGV** | 11 | 段错误 | 内存访问违规 |
| **SIGTERM** | 15 | 终止 | 优雅终止（可捕获） |
| **SIGCHLD** | 17 | 子进程终止 | 子进程退出时通知父进程 |
| **SIGSTOP** | 19 | 停止 | 暂停进程，不可捕获/忽略 |
| **SIGTSTP** | 20 | 终端停止 | Ctrl+Z |

```bash
# 发送信号
kill -TERM <PID>     # 优雅终止
kill -9 <PID>        # 强制杀死（SIGKILL）
kill -HUP <PID>      # 重新加载配置（很多服务用）
killall processname  # 按名称杀进程
pkill processname    # 按模式杀进程
```

> ⚠️ **风险提示**：`kill -9` 不可被进程捕获或忽略，进程没有机会清理资源。生产环境应先用 SIGTERM（默认），确认进程无法优雅终止后再用 SIGKILL。

### 5.3 作业控制

```bash
# 启动后台进程
command &

# 暂停前台进程
Ctrl + Z

# 查看作业
jobs

# 后台继续运行
bg %1

# 前台继续运行
fg %1

# 终止作业
kill %1

# 退出终端后进程仍运行
nohup command &          # no hang up，输出到 nohup.out
command & disown         # 从 shell 作业表移除
setsid command           # 新会话运行
```

### 5.4 systemd 服务管理

systemd 是现代 Linux 的 init 系统和服务管理器（PID 1）。

| 概念 | 说明 |
|------|------|
| **Unit** | systemd 管理的基本单元 |
| **Service Unit** | 服务单元（.service） |
| **Target** | 运行级别集合（.target） |
| **Socket** | 套接字激活（.socket） |
| **Timer** | 定时任务（.timer） |

**service 文件位置**：

```
/etc/systemd/system/      管理员自定义（优先级最高）
/run/systemd/system/      运行时生成
/usr/lib/systemd/system/  发行版提供的系统服务
```

**systemctl 常用命令**：

```bash
# 查看服务状态
systemctl status nginx

# 启动/停止/重启/重载
systemctl start nginx
systemctl stop nginx
systemctl restart nginx
systemctl reload nginx         # 重新加载配置（不中断）

# 开机自启/禁用
systemctl enable nginx
systemctl disable nginx
systemctl is-enabled nginx     # 查看是否开机自启

# 查看所有服务
systemctl list-units --type=service
systemctl list-unit-files --type=service    # 含已禁用的

# 查看失败的服务
systemctl --failed

# 查看服务依赖
systemctl list-dependencies nginx

# 重新加载 systemd 配置（修改 .service 文件后）
systemctl daemon-reload

# 查看服务日志
journalctl -u nginx
journalctl -u nginx -f              # 实时跟踪
journalctl -u nginx --since today   # 今天的日志

# 系统管理
systemctl reboot       # 重启
systemctl poweroff     # 关机
systemctl suspend      # 挂起
systemctl hibernate    # 休眠

# 查看默认 target
systemctl get-default
systemctl set-default multi-user.target    # 设置为文本模式
systemctl set-default graphical.target     # 设置为图形模式
```

**service 文件结构示例**：

```ini
[Unit]
Description=Nginx Web Server
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/nginx
ExecReload=/usr/sbin/nginx -s reload
ExecStop=/usr/sbin/nginx -s stop
PIDFile=/run/nginx.pid
User=nginx
Group=nginx
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.5 进程监控命令

| 命令 | 用途 |
|------|------|
| **ps** | 进程快照 |
| **top / htop** | 实时进程监控 |
| **pstree** | 进程树 |
| **pgrep** | 按名称查找 PID |
| **pidof** | 查找进程 PID |
| **vmstat** | 虚拟内存统计 |
| **iostat** | I/O 统计 |
| **sar** | 系统活动报告 |
| **strace** | 跟踪系统调用 |
| **lsof** | 列出打开的文件 |

```bash
# ps 常用组合
ps aux              # BSD 风格：所有用户的所有进程
ps -ef              # SYSV 风格：全格式
ps -eLf             # 显示线程
ps aux --sort=-%cpu | head -10    # 按 CPU 排序 top10

# 实时监控
top
htop          # 更友好（需安装）

# 进程树
pstree
pstree -p     # 显示 PID

# 查找进程
pgrep nginx
pidof nginx

# 跟踪系统调用
strace -p <PID>
strace -f -e trace=file command    # 跟踪文件操作

# 查看打开的文件
lsof -p <PID>           # 进程打开的文件
lsof /path/to/file      # 哪个进程打开了文件
lsof -i :80             # 哪个进程占用 80 端口
```

---

## 六、常用命令

> 按功能分类列出核心命令，每个命令给代表性用法。

### 6.1 文件与目录

| 命令 | 用途 | 核心示例 |
|------|------|---------|
| **ls** | 列出目录 | `ls -la`（详细+隐藏）、`ls -lh`（人类可读大小）、`ls -R`（递归） |
| **cd** | 切换目录 | `cd ~`（回家）、`cd -`（回上一次）、`cd ..`（上一级） |
| **pwd** | 显示当前路径 | `pwd`、`pwd -P`（物理路径，解引用符号链接） |
| **cp** | 复制 | `cp -r src dest`（递归）、`cp -a src dest`（归档，保留权限/时间） |
| **mv** | 移动/重命名 | `mv old new`、`mv file /dir/` |
| **rm** | 删除 | `rm file`、`rm -rf dir`（递归强制，⚠️危险） |
| **mkdir** | 创建目录 | `mkdir dir`、`mkdir -p a/b/c`（创建多级） |
| **rmdir** | 删除空目录 | `rmdir emptydir` |
| **touch** | 创建空文件/改时间 | `touch file`、`touch -d "2024-01-01" file` |
| **find** | 查找文件 | 见下方详细示例 |
| **ln** | 链接 | `ln src hardlink`（硬链接）、`ln -s src symlink`（软链接） |
| **file** | 识别文件类型 | `file filename` |
| **stat** | 文件详细信息 | `stat filename` |
| **du** | 磁盘使用 | `du -sh /dir`（汇总）、`du -h --max-depth=1`（一级目录） |
| **df** | 磁盘空间 | `df -h`（人类可读）、`df -i`（inode 使用） |

**find 命令示例**：

```bash
# 按名称查找
find /path -name "*.log"
find /path -iname "readme.txt"    # 不区分大小写

# 按类型查找
find /path -type f       # 文件
find /path -type d       # 目录
find /path -type l       # 符号链接

# 按大小查找
find /path -size +100M   # 大于 100MB
find /path -size -10k    # 小于 10KB

# 按时间查找
find /path -mtime -7     # 7 天内修改过
find /path -atime +30    # 30 天前访问过
find /path -mmin -60     # 60 分钟内修改过

# 按权限查找
find /path -perm 755     # 精确匹配 755
find /path -perm -4000   # 有 SUID 位
find /path -perm /u+x    # 所有者有执行权限

# 按所有者查找
find /path -user root
find /path -group admin

# 执行操作（对找到的文件）
find /path -name "*.tmp" -delete              # 删除
find /path -name "*.bak" -exec cp {} /backup/ \;  # 复制
find /path -name "*.log" -exec gzip {} \;     # 压缩

# 查找并限制深度
find /path -maxdepth 2 -name "*.conf"
```

> ⚠️ **风险提示**：`find ... -delete` 和 `find ... -exec rm {} \;` 会直接删除文件，不可恢复。使用前先用 `find ...` 不带操作确认结果正确。

### 6.2 文本处理

| 命令 | 用途 | 核心示例 |
|------|------|---------|
| **cat** | 显示文件 | `cat file`、`cat -n file`（行号） |
| **less** | 分页查看 | `less file`（搜索 /pattern，退出 q） |
| **head** | 显示头部 | `head file`（默认 10 行）、`head -20 file`（20 行） |
| **tail** | 显示尾部 | `tail file`、`tail -f file`（实时跟踪）、`tail -F file`（重命名后重连） |
| **wc** | 统计 | `wc -l file`（行数）、`wc -w file`（单词数）、`wc -c file`（字节数） |
| **grep** | 文本搜索 | 见下方详细示例 |
| **sed** | 流编辑器 | 见下方详细示例 |
| **awk** | 文本处理语言 | 见下方详细示例 |
| **sort** | 排序 | `sort file`、`sort -rn file`（反向数值排序）、`sort -u file`（去重） |
| **uniq** | 去重（需先排序） | `sort file \| uniq`、`sort file \| uniq -c`（计数） |
| **cut** | 按列切割 | `cut -d: -f1 /etc/passwd`（冒号分隔，取第 1 列） |
| **paste** | 合并文件 | `paste file1 file2` |
| **tr** | 字符替换 | `tr a-z A-Z < file`（小写转大写）、`tr -d '\r' < file`（删除回车） |
| **diff** | 比较文件 | `diff file1 file2`、`diff -u file1 file2`（统一格式） |
| **tee** | 分流输出 | `command \| tee output.txt`（既显示又保存） |
| **xargs** | 参数转换 | `find . -name "*.log" \| xargs rm`（⚠️小心） |

**grep 示例**：

```bash
# 基本搜索
grep "pattern" file

# 常用选项
grep -i "pattern" file        # 不区分大小写
grep -n "pattern" file        # 显示行号
grep -v "pattern" file        # 反向匹配（不包含）
grep -c "pattern" file        # 计数匹配行数
grep -r "pattern" /dir        # 递归搜索目录
grep -l "pattern" *.txt       # 只显示匹配的文件名
grep -A 3 "pattern" file      # 显示匹配行后 3 行
grep -B 3 "pattern" file      # 显示匹配行前 3 行
grep -C 3 "pattern" file      # 显示匹配行前后 3 行
grep -E "pat1|pat2" file      # 扩展正则（或关系）
grep -P "\d+" file            # Perl 正则（支持 \d 等）

# 管道中使用
ps aux | grep nginx
netstat -an | grep :80
cat /var/log/syslog | grep -i error
```

**sed 示例**：

```bash
# 替换（s 命令）
sed 's/old/new/' file          # 每行替换第一个
sed 's/old/new/g' file         # 全局替换
sed -i 's/old/new/g' file      # 直接修改文件（危险！）
sed 's#/usr/bin#/bin#g' file   # 使用不同分隔符（避免转义 /）

# 删除行
sed '5d' file                  # 删除第 5 行
sed '/pattern/d' file          # 删除匹配行
sed '$d' file                  # 删除最后一行

# 插入/追加
sed '5i\new line' file         # 第 5 行前插入
sed '5a\new line' file         # 第 5 行后追加

# 打印指定行
sed -n '5,10p' file            # 打印第 5-10 行
sed -n '/pattern/p' file       # 打印匹配行
```

> ⚠️ **风险提示**：`sed -i` 直接修改文件，不可撤销。重要文件操作前先备份。

**awk 示例**：

```bash
# 按列处理（默认空白分隔）
awk '{print $1}' file          # 打印第 1 列
awk '{print $1, $3}' file      # 打印第 1、3 列
awk -F: '{print $1}' /etc/passwd   # 指定分隔符为冒号

# 条件判断
awk '$3 > 100 {print $1, $3}' file   # 第 3 列 > 100 的行

# 内建变量
awk '{print NR, $0}' file      # NR = 行号
awk -F: '{print NF}' file      # NF = 字段数
awk 'END {print NR}' file      # END 块：结束时执行（总行数）

# 计算求和
awk '{sum += $3} END {print sum}' file

# 组合示例：统计 IP 访问量
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10
```

### 6.3 系统监控

| 命令 | 用途 | 核心示例 |
|------|------|---------|
| **uptime** | 运行时间/负载 | `uptime`（1/5/15 分钟负载） |
| **free** | 内存使用 | `free -h`（人类可读） |
| **top / htop** | 实时监控 | `top`、`htop` |
| **vmstat** | 虚拟内存统计 | `vmstat 1`（每秒更新） |
| **iostat** | I/O 统计 | `iostat -x 1`（详细 I/O） |
| **sar** | 系统活动报告 | `sar -u`（CPU）、`sar -r`（内存）、`sar -n DEV`（网络） |
| **mpstat** | CPU 统计 | `mpstat -P ALL 1`（每个 CPU） |
| **dstat** | 全能监控 | `dstat`（综合 cpu/磁盘/网络/内存） |
| **glances** | 现代监控 | `glances`（高颜值综合监控） |

```bash
# 查看内存
free -h

# 查看 CPU 信息
cat /proc/cpuinfo
nproc    # CPU 核心数

# 查看负载
uptime
# load average: 0.50, 0.30, 0.10
# 分别是 1 分钟、5 分钟、15 分钟的平均负载

# 实时 I/O 监控
iostat -xz 1

# 虚拟内存统计（每秒）
vmstat 1
# r=运行队列 b=不可中断睡眠 si/so=换入换出 bi/bo=块I/O us/sy/id=CPU
```

### 6.4 包管理命令（对比速查）

| 操作 | Debian/Ubuntu (apt) | RHEL/CentOS (yum/dnf) | Arch (pacman) |
|------|---------------------|---------------------|---------------|
| 更新包列表 | `apt update` | `yum check-update` | `pacman -Sy` |
| 升级所有包 | `apt upgrade` | `yum update` | `pacman -Syu` |
| 安装包 | `apt install pkg` | `yum install pkg` | `pacman -S pkg` |
| 卸载包 | `apt remove pkg` | `yum remove pkg` | `pacman -R pkg` |
| 卸载（含配置） | `apt purge pkg` | `yum remove pkg` | `pacman -Rn pkg` |
| 搜索包 | `apt search name` | `yum search name` | `pacman -Ss name` |
| 查看包信息 | `apt show pkg` | `yum info pkg` | `pacman -Si pkg` |
| 查看已安装 | `dpkg -l` | `rpm -qa` | `pacman -Q` |
| 查看文件属哪个包 | `dpkg -S /path` | `rpm -qf /path` | `pacman -Qo /path` |
| 查看包文件列表 | `dpkg -L pkg` | `rpm -ql pkg` | `pacman -Ql pkg` |
| 安装本地包 | `dpkg -i pkg.deb` | `rpm -i pkg.rpm` | `pacman -U pkg.tar.xz` |

---

## 七、网络配置

### 7.1 网络配置命令

| 操作 | 传统命令（net-tools） | 现代命令（iproute2） |
|------|---------------------|---------------------|
| 查看接口 | `ifconfig` | `ip addr show` / `ip a` |
| 查看路由 | `route -n` | `ip route show` / `ip r` |
| 查看邻居 | `arp -a` | `ip neigh show` |
| 启用接口 | `ifconfig eth0 up` | `ip link set eth0 up` |
| 设置 IP | `ifconfig eth0 192.168.1.100` | `ip addr add 192.168.1.100/24 dev eth0` |
| 添加路由 | `route add default gw 192.168.1.1` | `ip route add default via 192.168.1.1` |

> **注意**：`ifconfig`、`route`、`arp` 属于 net-tools 包，已逐渐被 iproute2（`ip` 命令）取代。现代系统可能默认未安装 net-tools。

```bash
# 查看所有网络接口
ip addr show
ip link show

# 查看指定接口
ip addr show eth0

# 配置 IP 地址（临时，重启失效）🔑
ip addr add 192.168.1.100/24 dev eth0

# 启用/禁用接口🔑
ip link set eth0 up
ip link set eth0 down

# 查看路由表
ip route show

# 添加默认网关🔑
ip route add default via 192.168.1.1 dev eth0

# 添加静态路由🔑
ip route add 10.0.0.0/8 via 192.168.1.254 dev eth0

# 查看 ARP 表
ip neigh show
```

### 7.2 永久网络配置

**Debian/Ubuntu 系**：

```bash
# 传统方式（/etc/network/interfaces）
# /etc/network/interfaces
auto eth0
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4

# 现代方式：Netplan（Ubuntu 18.04+）
# /etc/netplan/00-installer-config.yaml
network:
  version: 2
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

# 应用配置🔑
netplan apply
```

**RHEL/CentOS 系**：

```bash
# 配置文件位置
# /etc/sysconfig/network-scripts/ifcfg-eth0

TYPE=Ethernet
BOOTPROTO=static
NAME=eth0
DEVICE=eth0
ONBOOT=yes
IPADDR=192.168.1.100
PREFIX=24
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4

# 重启网络🔑
systemctl restart network
# 或
nmcli connection reload

# 用 nmcli 配置🔑
nmcli connection show
nmcli connection modify eth0 ipv4.addresses 192.168.1.100/24
nmcli connection modify eth0 ipv4.gateway 192.168.1.1
nmcli connection up eth0
```

### 7.3 DNS 配置

```bash
# 查看 DNS 配置
cat /etc/resolv.conf

# systemd-resolved 管理的系统
systemd-resolve --status
resolvectl status

# DNS 测试
nslookup example.com
dig example.com
dig example.com MX           # 查询 MX 记录
dig example.com +trace       # 跟踪解析过程
dig -x 8.8.8.8               # 反向解析
host example.com

# 修改 DNS（Debian/Ubuntu 用 resolvconf/systemd-resolved）
# RHEL/CentOS 在 ifcfg 文件中设置 DNS1=
```

### 7.4 网络测试工具

| 命令 | 用途 | 示例 |
|------|------|------|
| **ping** | 连通性测试 | `ping google.com`、`ping -c 4 8.8.8.8` |
| **traceroute** | 路由跟踪 | `traceroute google.com` |
| **mtr** | 组合 ping+traceroute | `mtr google.com` |
| **netstat** | 网络连接/统计 | `netstat -tlnp`、`netstat -an` |
| **ss** | 现代网络连接工具 | `ss -tlnp`、`ss -s`（统计） |
| **telnet** | 端口测试 | `telnet 192.168.1.1 22` |
| **nc / netcat** | 网络瑞士军刀 | `nc -zv 192.168.1.1 22`（端口测试）、`nc -l 8080`（监听） |
| **tcpdump** | 抓包 | `tcpdump -i eth0 port 80` |
| **wireshark / tshark** | 图形/命令行抓包 | `tshark -i eth0 -f "port 80"` |
| **curl / wget** | HTTP 测试 | `curl -I https://example.com`、`wget https://example.com/file` |
| **iperf3** | 带宽测试 | `iperf3 -s`（服务端）、`iperf3 -c server`（客户端） |
| **ethtool** | 网卡信息 | `ethtool eth0` |

```bash
# 查看监听端口
ss -tlnp                # TCP 监听
ss -ulnp                # UDP 监听
ss -tulnp               # 全部监听
ss -s                   # 连接统计

# 查看已建立连接
ss -tn state established

# 端口连通性测试
nc -zv 192.168.1.1 22
curl -v telnet://192.168.1.1:22

# HTTP 测试
curl -I https://example.com          # 仅看响应头
curl -X POST -d "data=xxx" url       # POST 请求
curl -k https://self-signed.example.com  # 跳过证书验证
curl --resolve example.com:443:1.2.3.4 https://example.com  # 指定解析

# 抓包
tcpdump -i eth0 -n port 80           # 抓取 80 端口
tcpdump -i any -w capture.pcap       # 保存到文件
tcpdump -r capture.pcap              # 读取文件
```

### 7.5 防火墙

#### iptables（传统）

```
iptables 四表五链：

表（Tables）：
  raw       → 原始数据包处理（连接跟踪前）
  mangle    → 数据包修改（TOS、TTL、MARK）
  nat       → 地址转换（SNAT/DNAT）
  filter    → 包过滤（默认表）

链（Chains）：
  INPUT     → 进入本机的包
  OUTPUT    → 本机发出的包
  FORWARD   → 转发的包
  PREROUTING  → 路由前（DNAT）
  POSTROUTING → 路由后（SNAT）
```

```bash
# 查看规则
iptables -L -n -v
iptables -L -n --line-numbers
iptables -t nat -L -n

# 基本策略设置🔑
iptables -P INPUT DROP           # 默认拒绝入站
iptables -P OUTPUT ACCEPT        # 默认允许出站
iptables -P FORWARD DROP         # 默认拒绝转发

# 允许已建立连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许特定端口
iptables -A INPUT -p tcp --dport 22 -j ACCEPT     # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT     # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT    # HTTPS
iptables -A INPUT -s 192.168.1.0/24 -j ACCEPT    # 允许内网

# NAT（地址伪装）🔑
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 删除规则
iptables -D INPUT 3                 # 按行号删除
iptables -D INPUT -p tcp --dport 80 -j ACCEPT   # 按内容删除

# 清空规则
iptables -F
iptables -t nat -F

# 保存规则
iptables-save > /etc/iptables/rules.v4

# 恢复规则
iptables-restore < /etc/iptables/rules.v4
```

> ⚠️ **风险提示**：远程服务器上配置 iptables 时，如果 INPUT 默认策略设为 DROP 且没有允许 SSH 端口，会立刻断开连接，无法恢复。建议先配置规则再改默认策略，或使用定时脚本自动回滚。

#### nftables（现代）

nftables 是 iptables 的继任者，提供更统一的语法和更好的性能。

```bash
# 查看规则
nft list ruleset

# 基本操作
nft add table inet filter
nft add chain inet filter input { type filter hook input priority 0 \; }
nft add rule inet filter input tcp dport 22 accept

# Debian/Ubuntu 切换到 nftables
# 已默认使用 nftables 后端

# RHEL/CentOS 8+ 已默认使用 nftables
```

#### firewalld（RHEL/CentOS 系）

```bash
# 查看状态
firewall-cmd --state
firewall-cmd --list-all

# 查看当前 zone
firewall-cmd --get-default-zone

# 开放端口（临时）🔑
firewall-cmd --add-port=8080/tcp

# 开放端口（永久）🔑
firewall-cmd --permanent --add-port=8080/tcp
firewall-cmd --reload          # 重新加载永久配置

# 开放服务
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https

# 移除端口/服务
firewall-cmd --permanent --remove-port=8080/tcp
firewall-cmd --reload

# 富规则（更细粒度）
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" service name="ssh" accept'
```

#### ufw（Ubuntu/Debian 系）

```bash
# 查看状态
ufw status
ufw status verbose

# 默认策略
ufw default deny incoming     # 默认拒绝入站
ufw default allow outgoing    # 默认允许出站

# 允许端口🔑
ufw allow 22/tcp              # SSH
ufw allow 80/tcp              # HTTP
ufw allow 443/tcp             # HTTPS
ufw allow from 192.168.1.0/24  # 允许内网

# 禁止端口
ufw deny 23/tcp

# 删除规则
ufw delete allow 80/tcp
ufw delete 3                  # 按编号删除

# 启用/禁用
ufw enable
ufw disable

# 列出规则编号
ufw status numbered
```

### 7.6 SSH

```bash
# 基本连接
ssh user@hostname
ssh -p 2222 user@hostname          # 指定端口
ssh -i /path/to/key user@hostname  # 指定私钥

# 执行远程命令
ssh user@hostname "ls -la /tmp"

# SCP 传输文件
scp localfile user@hostname:/remote/path/
scp user@hostname:/remote/file local/path/
scp -r localdir user@hostname:/remote/     # 递归目录
scp -P 2222 file user@host:/path/          # 指定端口

# SFTP（交互式文件传输）
sftp user@hostname

# SSH 配置文件（~/.ssh/config）
Host server01
    HostName 192.168.1.100
    User alice
    Port 22
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60

# 生成密钥对
ssh-keygen -t rsa -b 4096 -C "your@email.com"
ssh-keygen -t ed25519 -C "your@email.com"     # 推荐，更短更安全

# 公钥推送（免密登录）
ssh-copy-id user@hostname
# 或手动追加公钥到 ~/.ssh/authorized_keys
```

**SSH 服务端安全配置**（/etc/ssh/sshd_config）：

```ssh-config
Port 22                              # 建议改为非默认端口
Protocol 2                           # 仅使用 SSH 协议 2
PermitRootLogin no                   # 禁止 root 直接登录
PasswordAuthentication no            # 禁用密码登录（用密钥）
PubkeyAuthentication yes             # 启用公钥认证
PermitEmptyPasswords no              # 禁止空密码
MaxAuthTries 3                       # 最大尝试次数
AllowUsers alice bob                 # 只允许特定用户登录
X11Forwarding no                     # 禁用 X11 转发
ClientAliveInterval 300              # 客户端超时
ClientAliveCountMax 2                # 最大超时次数
```

> 🔑 修改 sshd_config 后，用 `sshd -t` 测试配置，再 `systemctl reload sshd` 重载。

---

## 八、安全机制

### 8.1 安全机制全景

```
Linux 安全体系
│
├── 认证与授权
│   ├── /etc/shadow（密码哈希）
│   ├── PAM（可插拔认证模块）
│   ├── sudo（权限委派）
│   └── SSH 密钥/证书
│
├── 强制访问控制（MAC）
│   ├── SELinux
│   └── AppArmor
│
├── 防火墙与网络安全
│   ├── iptables / nftables
│   ├── firewalld / ufw
│   └── TCP Wrappers（已淘汰）
│
├── 审计与监控
│   ├── auditd（审计框架）
│   ├── AIDE / Tripwire（完整性检查）
│   └── 日志系统（syslog / journald）
│
├── 内核加固
│   ├── sysctl 内核参数
│   ├── KASLR / SMEP / SMAP
│   ├── 模块签名
│   └── Landlock / seccomp
│
└── 容器与沙箱
    ├── Docker / Podman
    ├── cgroups / namespaces
    └── seccomp / AppArmor / SELinux
```

### 8.2 SELinux

SELinux（Security-Enhanced Linux）是 NSA 开发的强制访问控制（MAC）系统，RHEL/CentOS 默认启用。

| 模式 | 说明 |
|------|------|
| **enforcing** | 强制模式，违反策略即拒绝 |
| **permissive** | 宽容模式，只记录不拒绝（调试用） |
| **disabled** | 完全禁用 |

```bash
# 查看 SELinux 状态
getenforce
sestatus

# 临时切换模式🔑
setenforce 0     # 切换到 permissive
setenforce 1     # 切换到 enforcing

# 永久修改（/etc/selinux/config）
SELINUX=enforcing
SELINUXTYPE=targeted

# 查看文件安全上下文
ls -Z /path/to/file

# 查看进程安全上下文
ps -eZ

# 查看 SELinux 布尔值
getsebool -a
getsebool httpd_enable_homedirs

# 修改布尔值🔑
setsebool httpd_enable_homedirs on
setsebool -P httpd_enable_homedirs on    # 永久

# 恢复文件默认安全上下文
restorecon -Rv /path/to/dir

# 查看审计日志中的 SELinux 拒绝
ausearch -m avc -ts recent
sealert -a /var/log/audit/audit.log
```

> **安全提示**：生产环境不应禁用 SELinux。遇到问题时先用 permissive 模式调试，再通过修改策略或布尔值解决，而不是直接关闭。

### 8.3 AppArmor

AppArmor 是基于路径的 MAC 系统，Ubuntu/Debian 默认启用。

```bash
# 查看状态
aa-status
apparmor_status

# 配置文件位置
/etc/apparmor.d/

# 加载/卸载配置
apparmor_parser -r /etc/apparmor.d/usr.bin.nginx    # 重新加载
ln -s /etc/apparmor.d/profile /etc/apparmor.d/disable/  # 禁用
aa-complain /usr/bin/nginx    # 切换到 complain（宽容）模式
aa-enforce /usr/bin/nginx     # 切换到 enforce（强制）模式
```

### 8.4 系统审计（auditd）

auditd 是 Linux 的审计子系统，可以记录系统调用、文件访问、权限变更等事件。

```bash
# 安装
# Debian/Ubuntu
apt install auditd audispd-plugins
# RHEL/CentOS
yum install audit

# 查看状态
service auditd status

# 审计规则（/etc/audit/rules.d/audit.rules）

# 监控文件访问
-w /etc/passwd -p wa -k passwd_changes
# -w 监控路径 -p 权限(r/w/x/a) -k 关键词标签

# 监控系统调用
-a always,exit -F arch=b64 -S execve -k exec_events

# 查看审计日志
ausearch -k passwd_changes       # 按关键词搜索
ausearch -m avc -ts today        # 今天的 SELinux 拒绝
aureport -a                       # 认证报告
aureport -f                       # 文件访问报告
```

### 8.5 sysctl 内核参数加固

```bash
# 查看所有参数
sysctl -a

# 查看单个参数
sysctl net.ipv4.ip_forward

# 临时设置🔑
sysctl -w net.ipv4.ip_forward=1

# 永久设置（/etc/sysctl.conf 或 /etc/sysctl.d/*.conf）
# 然后执行：sysctl -p
```

**常见安全加固参数**：

```
# IP 转发（路由器才需要，普通服务器禁用）
net.ipv4.ip_forward = 0

# 防止 SYN 洪水攻击
net.ipv4.tcp_syncookies = 1

# 忽略 ICMP 广播请求
net.ipv4.icmp_echo_ignore_broadcasts = 1

# 忽略 bogus ICMP 响应
net.ipv4.icmp_ignore_bogus_error_responses = 1

# 禁用源路由
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# 禁用 ICMP 重定向（防止中间人）
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# 启用反向路径过滤（防 IP 欺骗）
net.ipv4.conf.all.rp_filter = 1

# 随机化内存映射地址（ASLR）
kernel.randomize_va_space = 2

# 限制 core dump（防止敏感信息泄露）
fs.suid_dumpable = 0

# 禁用 Magic SysRq
kernel.sysrq = 0

# 限制同时打开文件数
fs.file-max = 65535
```

### 8.6 日志系统

**系统日志位置**：

```
/var/log/syslog            系统日志（Debian/Ubuntu）
/var/log/messages          系统日志（RHEL/CentOS）
/var/log/auth.log          认证日志（Debian/Ubuntu）
/var/log/secure            安全/认证日志（RHEL/CentOS）
/var/log/kern.log          内核日志（Debian/Ubuntu）
/var/log/cron              cron 日志
/var/log/audit/audit.log   审计日志
/var/log/nginx/            Nginx 日志
/var/log/apache2/          Apache 日志（Debian）
/var/log/httpd/            Apache 日志（RHEL）
```

**journalctl（systemd 日志）**：

```bash
# 查看所有日志
journalctl

# 查看内核日志
journalctl -k
journalctl -k -b            # 本次启动的内核日志

# 按服务查看
journalctl -u nginx
journalctl -u sshd

# 实时跟踪
journalctl -u nginx -f

# 按时间过滤
journalctl --since "2024-01-01" --until "2024-01-02"
journalctl --since "1 hour ago"
journalctl --since today

# 按优先级（0=emerg 到 7=debug）
journalctl -p err
journalctl -p warning

# 查看启动耗时
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
```

### 8.7 安全加固清单

```
基础安全加固 TOP 15：

1.  修改 root 密码，禁用 root 远程登录
2.  创建普通用户，配置 sudo 权限
3.  SSH 密钥登录，禁用密码认证
4.  修改 SSH 默认端口
5.  启用并配置防火墙（只开放必要端口）
6.  启用 SELinux / AppArmor
7.  配置系统审计（auditd）
8.  加固 sysctl 内核参数
9.  安装并配置 fail2ban（防暴力破解）
10. 定期更新系统（apt update / yum update）
11. 设置密码策略（复杂度、过期时间）
12. 配置时间同步（NTP/chrony）
13. 关闭不必要的服务
14. 配置日志集中收集与轮转
15. 安装入侵检测（AIDE / rkhunter）
```

---

## 九、Shell 与脚本

### 9.1 Shell 基础

| 概念 | 说明 |
|------|------|
| **Shell** | 命令行解释器，用户与内核之间的接口 |
| **Bash** | Bourne Again Shell，Linux 默认 Shell |
| **Zsh** | 扩展 Bash，功能更强大（Oh My Zsh） |
| **脚本** | 包含命令的文本文件，可批量执行 |

**第一个脚本**：

```bash
#!/bin/bash
# hello.sh - 我的第一个脚本

echo "Hello, World!"
echo "当前用户: $USER"
echo "当前目录: $(pwd)"
```

```bash
# 添加执行权限
chmod +x hello.sh

# 运行
./hello.sh
bash hello.sh
sh hello.sh
```

### 9.2 变量

```bash
# 定义变量（等号两边不能有空格）
name="Alice"
age=25

# 引用变量
echo "My name is $name"
echo "Age: ${age} years old"

# 只读变量
readonly PI=3.14159

# 环境变量（子进程继承）
export MY_VAR="hello"

# 特殊变量
echo $0          # 脚本名称
echo $1          # 第一个参数
echo $2          # 第二个参数
echo $#          # 参数个数
echo $@          # 所有参数（列表）
echo $*          # 所有参数（字符串）
echo $?          # 上一条命令的退出码
echo $$          # 当前进程 PID
echo $!          # 最近后台进程 PID

# 命令替换
files=$(ls)
today=$(date +%Y-%m-%d)

# 变量默认值
echo ${var:-default}    # var 未设置则用 default
echo ${var:=default}    # var 未设置则赋值为 default
```

### 9.3 流程控制

**if 条件**：

```bash
if [ condition ]; then
    # do something
elif [ condition ]; then
    # do something else
else
    # do other
fi

# 常见条件判断
[ -f file ]          # 文件存在
[ -d dir ]           # 目录存在
[ -r file ]          # 文件可读
[ -w file ]          # 文件可写
[ -x file ]          # 文件可执行
[ -s file ]          # 文件非空
[ $a -eq $b ]        # 等于（数字）
[ $a -ne $b ]        # 不等于
[ $a -gt $b ]        # 大于
[ $a -lt $b ]        # 小于
[ $a -ge $b ]        # 大于等于
[ $a -le $b ]        # 小于等于
[ "$str1" = "$str2" ]  # 字符串相等
[ "$str1" != "$str2" ] # 字符串不等
[ -z "$str" ]        # 字符串为空
[ -n "$str" ]        # 字符串非空

# 逻辑与/或
[ $a -gt 0 ] && [ $a -lt 10 ]
[ $a -eq 0 ] || [ $b -eq 0 ]

# 示例
if [ -f /etc/passwd ]; then
    echo "文件存在"
fi

if [ $# -lt 1 ]; then
    echo "用法: $0 <filename>"
    exit 1
fi
```

**for 循环**：

```bash
# 遍历列表
for i in 1 2 3 4 5; do
    echo "Number: $i"
done

# 遍历文件
for file in *.txt; do
    echo "Processing $file"
done

# C 风格 for 循环
for ((i=0; i<10; i++)); do
    echo $i
done

# 遍历命令输出
for user in $(cat /etc/passwd | cut -d: -f1); do
    echo "User: $user"
done
```

**while 循环**：

```bash
# 计数
i=1
while [ $i -le 10 ]; do
    echo $i
    i=$((i + 1))
done

# 逐行读取文件
while read line; do
    echo "Line: $line"
done < file.txt

# 无限循环
while true; do
    echo "looping..."
    sleep 1
done
```

**case 分支**：

```bash
case $var in
    value1)
        echo "Value 1"
        ;;
    value2)
        echo "Value 2"
        ;;
    value3|value4)
        echo "Value 3 or 4"
        ;;
    *)
        echo "Other"
        ;;
esac
```

### 9.4 函数

```bash
# 定义函数
function greet {
    echo "Hello, $1!"
    return 0
}

# 简写
greet() {
    echo "Hello, $1!"
}

# 调用函数
greet "World"

# 函数返回值（通过 $? 获取）
add() {
    return $(($1 + $2))
}
add 3 5
echo "Result: $?"

# 函数中使用局部变量
calculate() {
    local result=$(( $1 * $2 ))
    echo $result
}
```

### 9.5 数组

```bash
# 定义数组
fruits=("apple" "banana" "cherry")

# 访问元素
echo ${fruits[0]}     # apple
echo ${fruits[@]}     # 所有元素
echo ${#fruits[@]}    # 数组长度
echo ${!fruits[@]}    # 所有索引

# 添加元素
fruits+=("date")

# 删除元素
unset fruits[1]

# 遍历
for fruit in "${fruits[@]}"; do
    echo $fruit
done
```

### 9.6 常用脚本技巧

```bash
# 1. 脚本开头的最佳实践
#!/bin/bash
set -e          # 遇错即退出
set -u          # 使用未定义变量时报错
set -o pipefail # 管道中任何命令失败，整体失败
set -x          # 调试模式（打印执行的命令）

# 2. 检查是否为 root
if [ "$(id -u)" -ne 0 ]; then
    echo "请以 root 身份运行此脚本" >&2
    exit 1
fi

# 3. 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 4. 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}
log "脚本开始执行"

# 5. 错误处理
trap 'echo "错误发生在第 $LINENO 行"' ERR

# 6. 清理函数
cleanup() {
    echo "清理中..."
    rm -f /tmp/tempfile
}
trap cleanup EXIT

# 7. 彩色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
echo -e "${GREEN}成功${NC}"
echo -e "${RED}失败${NC}"
```

---

## 十、包管理

### 10.1 主流包管理器对比

| 发行版家族 | 包格式 | 底层工具 | 高层工具 | 配置目录 |
|-----------|--------|---------|---------|---------|
| Debian/Ubuntu | .deb | dpkg | apt / apt-get | /etc/apt/ |
| RHEL/CentOS/Fedora | .rpm | rpm | yum / dnf | /etc/yum.repos.d/ |
| Arch Linux | .pkg.tar.zst | — | pacman | /etc/pacman.conf |
| openSUSE | .rpm | rpm | zypper | /etc/zypp/ |
| Alpine | .apk | apk | apk | /etc/apk/ |
| Gentoo | ebuild（源码） | — | emerge | /etc/portage/ |

### 10.2 Debian/Ubuntu (apt/dpkg)

```bash
# ========== 更新 ==========
apt update                    # 更新包列表
apt upgrade                   # 升级所有可升级的包
apt full-upgrade              # 智能升级（可能删除冲突包）
apt dist-upgrade              # 同上（传统名）

# ========== 安装/卸载 ==========
apt install package           # 安装包
apt install -y package        # 自动确认🔑
apt remove package            # 卸载（保留配置）
apt purge package             # 卸载（删除配置）🔑
apt autoremove                # 自动移除不再需要的依赖🔑
apt clean                     # 清理下载的包缓存

# ========== 查询 ==========
apt search keyword            # 搜索包
apt show package              # 查看包信息
apt list --installed          # 列出已安装包
apt list --upgradable         # 列出可升级包
apt depends package           # 查看依赖
apt rdepends package          # 查看反向依赖（谁依赖它）
apt policy package            # 查看包版本和优先级

# ========== dpkg 底层操作 ==========
dpkg -i package.deb           # 安装本地 deb 包🔑
dpkg -r package               # 卸载（保留配置）
dpkg -P package               # 卸载（删除配置）🔑
dpkg -l                       # 列出所有已安装包
dpkg -L package               # 列出包安装的文件
dpkg -S /path/to/file         # 查找文件属于哪个包
dpkg -s package               # 查看包状态
dpkg-reconfigure package      # 重新配置包
```

**apt 配置文件**：

```
/etc/apt/sources.list              主源列表
/etc/apt/sources.list.d/*.list     第三方源
/etc/apt/apt.conf.d/               配置片段
```

### 10.3 RHEL/CentOS (yum/dnf)

```bash
# ========== 更新 ==========
yum check-update              # 检查更新
yum update                    # 更新所有包
yum update package            # 更新指定包

# ========== 安装/卸载 ==========
yum install package           # 安装包
yum install -y package        # 自动确认🔑
yum remove package            # 卸载
yum erase package             # 同上🔑
yum autoremove                # 自动移除无用依赖

# ========== 查询 ==========
yum search keyword            # 搜索
yum info package              # 包信息
yum list installed            # 已安装列表
yum list updates              # 可更新列表
yum provides /path/to/file    # 哪个包提供此文件
yum deplist package           # 依赖列表
yum history                   # 查看 yum 操作历史
yum history undo N            # 撤销第 N 次操作

# ========== 仓库管理 ==========
yum repolist                  # 列出启用的仓库
yum repolist all              # 列出所有仓库
yum-config-manager --add-repo URL    # 添加仓库
yum-config-manager --enable repo    # 启用仓库
yum-config-manager --disable repo   # 禁用仓库

# ========== rpm 底层 ==========
rpm -ivh package.rpm          # 安装🔑
rpm -e package                # 卸载
rpm -qa                       # 列出所有已安装包
rpm -ql package               # 列出包的文件
rpm -qf /path/to/file         # 文件属哪个包
rpm -qi package               # 包信息
rpm -q --scripts package      # 安装/卸载脚本
rpm -Va                       # 校验所有已安装包
```

> **注意**：RHEL 8+ 和 Fedora 已使用 dnf 替代 yum（dnf 是 yum 的下一代，更快、更好的依赖解析）。大多数 yum 命令在 dnf 中同样适用。

### 10.4 Arch Linux (pacman)

```bash
# ========== 更新 ==========
pacman -Sy                   # 同步数据库
pacman -Syu                  # 全系统更新（滚动发行版核心命令）

# ========== 安装/卸载 ==========
pacman -S package            # 安装包
pacman -R package            # 卸载（保留依赖）
pacman -Rs package           # 卸载 + 删除无用依赖
pacman -Rns package          # 卸载 + 删除依赖 + 删除配置

# ========== 查询 ==========
pacman -Ss keyword           # 搜索包
pacman -Si package           # 包信息（远程）
pacman -Qi package           # 包信息（本地）
pacman -Qs keyword           # 搜索已安装包
pacman -Q                    # 列出所有已安装
pacman -Qe                   # 列出显式安装的包
pacman -Ql package           # 列出包文件
pacman -Qo /path/to/file     # 文件属哪个包
pacman -Qdt                  # 列出孤立包（不再需要的依赖）

# ========== 清理 ==========
pacman -Sc                   # 清理未安装包的缓存
pacman -Scc                  # 清理所有缓存

# ========== 其他 ==========
pacman -U package.tar.zst    # 安装本地包
pacman -F filename           # 搜索哪个包包含文件（需 pacman -Fy 更新数据库）
```

### 10.5 包管理安全

```
包管理安全要点：

1. 只使用官方软件源
   - 第三方源可能包含恶意软件
   - 添加源前验证其可信度

2. 验证包签名
   - Debian：用 GPG 签名验证 .deb
   - RHEL：RPM 包签名验证
   - Arch：pacman-key 验证

3. 定期更新
   - 安全补丁及时安装
   - 但生产环境更新前在测试环境验证

4. 最小化安装
   - 只安装需要的包
   - 减少攻击面

5. 定期审计已安装包
   - 检查不必要的服务包
   - 检查 setuid/setgid 二进制
   - rpm -Va / debsums 校验包完整性
```

---

## 附：优化后的提示词模板

以下是可复用的操作系统全景知识查询提示词模板：

```markdown
# 角色
你是一名资深【系统/平台】系统专家，精通内核、文件系统、命令行、权限、进程、
网络、安全与脚本，擅长按层次和分类讲清复杂概念。

# 任务
请系统介绍【操作系统】"是什么"，包括：
1. 定义、历史、内核与发行版/分支的区别
2. 内核架构：进程调度、内存管理、文件系统、设备驱动、网络协议栈
3. 文件系统与目录结构：标准目录、inode、挂载、常见文件系统
4. 用户与权限：用户、组、权限位、ACL、提权机制、认证框架
5. 进程与服务：进程、线程、信号、init 系统、作业控制
6. 常用命令：文件、文本、进程、网络、包管理、系统监控
7. 网络配置：IP、路由、DNS、防火墙、远程登录
8. 安全机制：强制访问控制、防火墙、审计、内核加固
9. Shell 与脚本：Shell 特性、变量、流程控制、函数、自动化
10. 包管理：主流包管理器对比、常用命令、安全实践

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 重要术语中英文对照
- 每个命令附语法、参数、示例
- 面向：【系统管理员 + 运维工程师 + 安全工程师】
- 深度：操作参考 + 原理理解 + 安全加固
- 示例标注适用发行版/版本

# 约束
- 不穷举全部命令，按功能分类列出核心命令
- 高风险操作给出警告
- 区分不同发行版/版本的差异
- 修改系统配置前提示备份
- 对需要 root 权限的命令进行标注
- 用 ASCII 图展示架构与流程
- 最后附"优化后的提示词模板"
```

**使用说明**：将【操作系统】替换为"FreeBSD""macOS""OpenBSD"等，即可生成同等深度的系统全景知识文档。

---

> **总结**：Linux 是一个庞大而精密的操作系统家族。从内核架构到文件系统，从权限模型到进程管理，从命令行工具到 Shell 脚本，从网络配置到安全加固，每一个领域都值得深入学习。本文提供了全景地图和核心命令速查——但命令不在多而在精，掌握原理 + 熟练核心工具 + 知道查文档的方法，才是高效学习之道。
