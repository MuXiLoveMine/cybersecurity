# Linux 系统基础

> 本文档系统介绍 Linux 操作系统的核心概念、文件系统结构以及基于 Linux 架构的主流发行版，为网络安全学习奠定基础。

---

## 目录

- [第一章：什么是 Linux 系统](#第一章什么是-linux-系统)
- [第二章：Linux 系统的文件系统结构](#第二章linux-系统的文件系统结构)
- [第三章：基于 Linux 架构的系统](#第三章基于-linux-架构的系统)

---

## 第一章：什么是 Linux 系统

### 1.1 Linux 的定义

Linux 是一种开源的类 Unix 操作系统内核，由芬兰计算机科学家 Linus Torvalds 于 1991 年首次发布。严格来说，"Linux"一词仅指操作系统内核，但在日常使用中，人们通常用"Linux"来指代基于该内核构建的完整操作系统（即 Linux 发行版）。

Linux 遵循 GNU 通用公共许可证（GPL），任何人都可以自由使用、修改和分发其源代码，这也是 Linux 能够快速发展和广泛应用的根本原因。

### 1.2 Linux 的核心特征

| 特征 | 说明 |
|------|------|
| **开源免费** | 源代码完全公开，任何人都可以查看、修改和重新分发 |
| **多用户多任务** | 支持多个用户同时登录使用，多个任务并发执行 |
| **稳定可靠** | 内核设计成熟，可长期不间断运行，常用于关键服务器 |
| **安全性强** | 严格的权限管理机制，用户和进程隔离，内核漏洞修复迅速 |
| **可定制性高** | 从嵌入式设备到超级计算机，均可裁剪适配 |
| **跨平台** | 支持 x86、ARM、MIPS、RISC-V 等多种 CPU 架构 |

### 1.3 Linux 的架构组成

Linux 操作系统采用分层架构，自底向上分为以下层次：

```
┌─────────────────────────────────────┐
│         用户应用程序层               │
│   (浏览器、办公软件、服务器程序等)    │
├─────────────────────────────────────┤
│         系统调用接口层               │
│   (System Call Interface / API)     │
├─────────────────────────────────────┤
│            Linux 内核               │
│  ┌─────────┬─────────┬───────────┐  │
│  │ 进程管理 │ 内存管理 │ 文件系统  │  │
│  │ 设备驱动 │ 网络协议 │ 安全模块  │  │
│  └─────────┴─────────┴───────────┘  │
├─────────────────────────────────────┤
│           硬件层                     │
│   (CPU、内存、磁盘、网卡等)          │
└─────────────────────────────────────┘
```

各层职责说明：

- **硬件层**：计算机的物理组件，包括 CPU、内存、硬盘、网络设备等。
- **内核层**：操作系统的核心，负责管理硬件资源、调度进程、管理内存和文件系统、处理网络通信等。内核是硬件和软件之间的桥梁。
- **系统调用接口层**：内核提供给用户空间程序的编程接口，应用程序通过系统调用请求内核服务（如读写文件、创建进程等）。
- **用户应用层**：用户直接交互的应用程序，包括命令行工具、图形桌面环境和各类服务程序。

### 1.4 Linux 与 Unix 的关系

Linux 受 Unix 设计哲学影响深远，但两者有本质区别：

| 对比项 | Unix | Linux |
|--------|------|-------|
| 起源 | 1969 年 AT&T 贝尔实验室 | 1991 年 Linus Torvalds 个人项目 |
| 源代码 | 最初闭源，后有多种开源版本 | 完全开源（GPL 协议） |
| 内核 | 各厂商独立维护 | 统一的 Linux 内核 |
| 成本 | 多为商业付费 | 绝大多数免费 |
| 适用范围 | 主要用于大型机和高端服务器 | 从嵌入式到超级计算机全覆盖 |

### 1.5 Linux 在网络安全中的地位

Linux 在网络安全领域占据核心地位，主要原因包括：

- **渗透测试平台**：Kali Linux、Parrot OS 等安全专用发行版预装数百种安全工具。
- **服务器安全**：全球绝大多数 Web 服务器、数据库服务器运行在 Linux 上。
- **开源可审计**：源代码公开，安全漏洞可被社区快速发现和修复。
- **权限控制精细**：SELinux、AppArmor 等安全模块提供强制访问控制。
- **网络工具丰富**：内置 tcpdump、nmap、Wireshark 等网络分析工具的原生支持。

---

## 第二章：Linux 系统的文件系统结构

### 2.1 文件系统层次标准（FHS）

Linux 采用文件系统层次标准（Filesystem Hierarchy Standard，FHS），以树形目录结构组织所有文件和目录。整个文件系统从根目录 `/` 开始，所有设备、分区都挂载到这个统一的目录树下。

```
/
├── bin        essential user command binaries
├── boot       static files of the boot loader
├── dev        device files
├── etc        host-specific system configuration
├── home       user home directories
├── lib        essential shared libraries and kernel modules
├── media      mount point for removable media
├── mnt        mount point for mounting a filesystem temporarily
├── opt        add-on application software packages
├── proc       kernel and process information virtual filesystem
├── root       root user home directory
├── run        data relevant to running processes
├── sbin       system administration binaries
├── srv        data for services provided by the system
├── sys        kernel and firmware virtual filesystem
├── tmp        temporary files
├── usr        secondary hierarchy (user applications)
└── var        variable data (logs, mail, spool)
```

### 2.2 核心目录详解

#### 2.2.1 `/bin` — 基本命令二进制文件

存放所有用户都可使用的基本命令的可执行文件。在单用户模式下也可使用。

| 常见文件/命令 | 说明 |
|--------------|------|
| `bash` | Bash Shell 解释器 |
| `ls` | 列出目录内容 |
| `cp` | 复制文件 |
| `mv` | 移动/重命名文件 |
| `cat` | 查看文件内容 |
| `grep` | 文本搜索工具 |
| `ps` | 查看进程信息 |

> **注意**：在较新的 Linux 发行版（如 Fedora、Arch）中，`/bin` 已合并到 `/usr/bin`。

#### 2.2.2 `/boot` — 启动相关文件

存放系统启动时需要的文件，包括 Linux 内核镜像和引导加载程序配置。

| 文件 | 说明 |
|------|------|
| `vmlinuz` | 压缩的 Linux 内核镜像 |
| `initrd` / `initramfs` | 初始化 RAM 磁盘镜像 |
| `grub/` | GRUB 引导加载程序配置目录 |
| `config` | 内核编译配置文件 |

#### 2.2.3 `/dev` — 设备文件

Linux 中"一切皆文件"理念的体现，硬件设备以文件形式存在于此目录。

| 设备文件 | 说明 |
|---------|------|
| `/dev/sda` | 第一块 SCSI/SATA 硬盘 |
| `/dev/sda1` | 第一块硬盘的第一个分区 |
| `/dev/nvme0n1` | 第一块 NVMe 固态硬盘 |
| `/dev/null` | 黑洞设备，丢弃所有写入数据 |
| `/dev/zero` | 零设备，读取时产生无限零字节 |
| `/dev/random` | 随机数生成器 |
| `/dev/tty` | 终端设备 |

#### 2.2.4 `/etc` — 系统配置文件

存放系统级配置文件，这是系统管理员最常操作的目录之一。

| 配置文件 | 说明 |
|---------|------|
| `/etc/passwd` | 用户账户信息 |
| `/etc/shadow` | 用户密码哈希（仅 root 可读） |
| `/etc/group` | 用户组信息 |
| `/etc/hosts` | 主机名与 IP 地址映射 |
| `/etc/resolv.conf` | DNS 解析配置 |
| `/etc/fstab` | 文件系统挂载表 |
| `/etc/hostname` | 系统主机名 |
| `/etc/ssh/sshd_config` | SSH 服务配置 |
| `/etc/network/interfaces` | 网络接口配置（Debian 系） |
| `/etc/crontab` | 系统级定时任务 |

#### 2.2.5 `/home` — 用户主目录

普通用户的个人文件存放位置，每个用户有一个以用户名命名的子目录。

```
/home/
├── alice/
│   ├── .bashrc       # Bash 配置
│   ├── .ssh/         # SSH 密钥
│   ├── Documents/    # 文档
│   ├── Downloads/    # 下载
│   └── .config/      # 应用配置
└── bob/
    └── ...
```

#### 2.2.6 `/lib` — 共享库文件

存放系统启动和 `/bin`、`/sbin` 中命令运行所需的共享库文件和内核模块。

| 路径 | 说明 |
|------|------|
| `/lib/libc.so` | C 标准库 |
| `/lib/modules/` | 内核模块（驱动程序等） |
| `/lib/systemd/` | systemd 服务单元文件 |

> **注意**：较新发行版中，`/lib` 已合并到 `/usr/lib`。

#### 2.2.7 `/proc` — 进程信息虚拟文件系统

这是一个虚拟文件系统（procfs），不占用磁盘空间，内容由内核动态生成，反映系统运行状态。

| 路径 | 说明 |
|------|------|
| `/proc/cpuinfo` | CPU 信息 |
| `/proc/meminfo` | 内存使用情况 |
| `/proc/version` | 内核版本信息 |
| `/proc/loadavg` | 系统负载平均值 |
| `/proc/[pid]/` | 特定进程的信息目录 |
| `/proc/filesystems` | 内核支持的文件系统类型 |
| `/proc/net/` | 网络协议栈信息 |

#### 2.2.8 `/root` — root 用户主目录

系统管理员（root 用户）的主目录，与普通用户的 `/home` 分开存放，确保即使 `/home` 分区不可用，root 仍可登录。

#### 2.2.9 `/sbin` — 系统管理命令

存放系统管理相关的可执行文件，通常需要 root 权限才能执行。

| 命令 | 说明 |
|------|------|
| `fdisk` | 磁盘分区工具 |
| `fsck` | 文件系统检查与修复 |
| `ifconfig` | 网络接口配置 |
| `iptables` | 防火墙规则管理 |
| `reboot` | 重启系统 |
| `shutdown` | 关机命令 |
| `systemctl` | 服务管理 |

#### 2.2.10 `/tmp` — 临时文件

存放临时文件，系统重启后通常会清空此目录。所有用户都有读写权限。

#### 2.2.11 `/usr` — 用户程序与资源

Linux 文件系统中最大的目录之一，包含用户应用程序、库文件、文档等。它本身也是一个层次结构。

| 子目录 | 说明 |
|--------|------|
| `/usr/bin` | 用户命令（非启动必需） |
| `/usr/sbin` | 系统管理命令（非启动必需） |
| `/usr/lib` | 应用程序共享库 |
| `/usr/local` | 本地编译安装的软件 |
| `/usr/share` | 架构无关的共享数据（文档、图标等） |
| `/usr/src` | 内核源代码（如安装） |
| `/usr/include` | C/C++ 头文件 |

#### 2.2.12 `/var` — 可变数据文件

存放在系统运行过程中不断变化的数据，如日志、缓存、邮件等。

| 子目录 | 说明 |
|--------|------|
| `/var/log/` | 系统日志文件 |
| `/var/log/auth.log` | 认证日志（Debian 系） |
| `/var/log/messages` | 系统消息日志（RHEL 系） |
| `/var/log/syslog` | 系统日志（Debian 系） |
| `/var/spool/` | 打印队列、邮件队列、cron 任务等 |
| `/var/cache/` | 应用缓存数据 |
| `/var/lib/` | 应用状态数据 |
| `/var/tmp` | 比 `/tmp` 保留更久的临时文件 |

#### 2.2.13 `/sys` — 内核虚拟文件系统

sysfs 虚拟文件系统，提供内核设备、总线和驱动的结构化视图。

```
/sys/
├── block/       # 块设备信息
├── bus/         # 总线信息
├── class/       # 设备类别
├── devices/     # 所有设备
├── firmware/    # 固件信息
└── kernel/      # 内核信息
```

#### 2.2.14 其他目录

| 目录 | 说明 |
|------|------|
| `/media` | 可移动媒体（U 盘、CD）的自动挂载点 |
| `/mnt` | 临时手动挂载文件系统的挂载点 |
| `/opt` | 第三方或可选软件包安装目录 |
| `/run` | 系统启动以来的运行时数据（PID 文件等） |
| `/srv` | 系统提供的服务的数据（如 Web 网页文件） |

### 2.3 文件类型

Linux 中有七种基本文件类型：

| 类型标识 | 类型名称 | 说明 | 示例 |
|---------|---------|------|------|
| `-` | 普通文件 | 文本、二进制、图片等 | `file.txt` |
| `d` | 目录文件 | 包含其他文件和目录的索引 | `/home` |
| `l` | 符号链接 | 指向另一个文件的路径 | `ln -s` 创建的链接 |
| `c` | 字符设备 | 按字符流读写的设备 | `/dev/tty` |
| `b` | 块设备 | 按数据块读写的设备 | `/dev/sda` |
| `p` | 管道文件 | 进程间通信的命名管道 | `mkfifo` 创建 |
| `s` | 套接字文件 | 进程间网络通信 | `/var/run/docker.sock` |

### 2.4 文件权限

Linux 采用基于用户和组的权限控制机制，每个文件有三组权限：

```
-rwxr-xr--
│├─┤├─┤├─┤
│ │  │  └── 其他用户权限：r-- (读)
│ │  └───── 组权限：r-x (读+执行)
│ └──────── 所有者权限：rwx (读+写+执行)
└────────── 文件类型：- (普通文件)
```

| 权限 | 数字表示 | 对文件的含义 | 对目录的含义 |
|------|---------|-------------|-------------|
| `r` (read) | 4 | 可查看文件内容 | 可列出目录内容 |
| `w` (write) | 2 | 可修改文件内容 | 可在目录中创建/删除文件 |
| `x` (execute) | 1 | 可执行文件 | 可进入目录（cd） |

常用权限组合：

| 数字 | 符号 | 说明 |
|------|------|------|
| `755` | `rwxr-xr-x` | 所有者全权限，其他用户读和执行 |
| `644` | `rw-r--r--` | 所有者读写，其他用户只读 |
| `600` | `rw-------` | 仅所有者读写（如 SSH 私钥） |
| `777` | `rwxrwxrwx` | 所有用户全权限（不安全，慎用） |

---

## 第三章：基于 Linux 架构的系统

### 3.1 Linux 发行版概述

Linux 发行版（Distribution，简称 Distro）是指基于 Linux 内核构建的完整操作系统，通常包含内核、GNU 工具集、图形桌面环境、包管理器和各类应用软件。不同的发行版面向不同的使用场景和用户群体。

### 3.2 主流发行版家族

Linux 发行版主要分为三大家族，每个家族有其独特的包管理器和发展路线：

```
                        ┌── Debian
                        │   ├── Ubuntu
                        │   │   ├── Linux Mint
                        │   │   ├── Pop!_OS
                        │   │   └── Kali Linux
            Debian 系   │   └── Raspberry Pi OS
            (APT/DPKG)  └── ...
   ─────────────────────────────────────────────────
                        ┌── RHEL (商业版)
            Red Hat 系  │   ├── CentOS (已停止维护)
            (RPM/YUM)   │   ├── Rocky Linux
                        │   ├── AlmaLinux
                        │   └── Fedora
   ─────────────────────────────────────────────────
                        ┌── Arch Linux
            Arch 系     │   ├── Manjaro
            (Pacman)    │   └── EndeavourOS
                        └── ...
```

### 3.3 Debian 系发行版

#### 3.3.1 Debian

Debian 是最早的 Linux 发行版之一，以稳定性和自由软件理念著称。它是 Ubuntu、Kali 等众多发行版的上游基础。

- **包管理器**：APT（Advanced Package Tool）+ dpkg
- **特点**：极度稳定、完全社区驱动、软件包经过严格测试
- **适用场景**：服务器、开发环境
- **发布周期**：约 2 年一个大版本

#### 3.3.2 Ubuntu

基于 Debian 开发，由 Canonical 公司维护，是最流行的桌面 Linux 发行版。

- **包管理器**：APT + dpkg
- **特点**：用户友好、文档丰富、社区活跃、定期 LTS（长期支持）版本
- **适用场景**：桌面、服务器、云计算、物联网
- **发布周期**：每 6 个月一个版本，每 2 年一个 LTS 版本（支持 5 年）

#### 3.3.3 Kali Linux

专为渗透测试和安全审计设计的发行版，由 Offensive Security 维护。

- **包管理器**：APT + dpkg
- **特点**：预装 600+ 安全工具（Nmap、Metasploit、Burp Suite 等）、支持 Live 模式
- **适用场景**：渗透测试、安全研究、数字取证
- **安全工具分类**：信息收集、漏洞分析、无线攻击、Web 应用测试、密码破解、社会工程学

#### 3.3.4 Linux Mint

基于 Ubuntu 的桌面发行版，以易用性和 Windows 风格界面著称。

- **特点**：开箱即用、Cinnamon 桌面环境、低资源占用
- **适用场景**：桌面日常使用、Linux 初学者

#### 3.3.5 Pop!_OS

由 System76 公司开发的 Ubuntu 衍生版，面向开发者和创意工作者。

- **特点**：优秀的硬件兼容性（特别是 NVIDIA 显卡）、窗口管理流畅、预装开发工具
- **适用场景**：开发工作站、游戏、AI/ML 开发

### 3.4 Red Hat 系发行版

#### 3.4.1 Red Hat Enterprise Linux（RHEL）

Red Hat 公司的商业企业级 Linux 发行版，是企业服务器的标杆。

- **包管理器**：RPM + DNF（原 YUM）
- **特点**：企业级支持、高稳定性、安全认证齐全
- **适用场景**：企业服务器、金融系统、政府机构
- **支持周期**：每个大版本支持 10 年

#### 3.4.2 CentOS / Rocky Linux / AlmaLinux

这三个发行版都是 RHEL 的免费替代品，与 RHEL 二进制兼容。

| 发行版 | 说明 |
|--------|------|
| **CentOS** | 原为 RHEL 的社区重建版，2021 年底改为 CentOS Stream（RHEL 上游），传统 CentOS 已停止维护 |
| **Rocky Linux** | CentOS 原创始人发起的 RHEL 兼容替代版，由 Rocky Enterprise Software Foundation 维护 |
| **AlmaLinux** | 由 CloudLinux 公司发起的 RHEL 兼容发行版，由非营利基金会管理 |

#### 3.4.3 Fedora

Red Hat 赞助的社区发行版，是 RHEL 的上游试验场。

- **包管理器**：RPM + DNF
- **特点**：采用最新技术、快速迭代、前沿特性
- **适用场景**：开发者桌面、新技术试验
- **发布周期**：约 6 个月一个版本

### 3.5 Arch 系发行版

#### 3.5.1 Arch Linux

以简洁、轻量和极致可定制性著称的滚动更新发行版。

- **包管理器**：Pacman
- **特点**：滚动更新（无大版本升级）、AUR（Arch User Repository）海量软件、DIY 安装
- **适用场景**：高级用户、追求最新软件、学习 Linux 内部原理
- **设计哲学**：KISS（Keep It Simple, Stupid）

#### 3.5.2 Manjaro

基于 Arch Linux 的用户友好发行版，降低了 Arch 的使用门槛。

- **特点**：图形化安装器、预配置桌面环境、自动硬件检测、稳定滚动更新
- **适用场景**：桌面日常使用、游戏

### 3.6 其他重要发行版

#### 3.6.1 SUSE / openSUSE

欧洲流行的企业级 Linux 发行版，由德国 SUSE 公司维护。

| 版本 | 说明 |
|------|------|
| **SUSE Linux Enterprise Server（SLES）** | 商业企业版，与 RHEL 竞争 |
| **openSUSE Leap** | 社区稳定版，与 SLES 共享代码库 |
| **openSUSE Tumbleweed** | 社区滚动更新版 |

- **包管理器**：RPM + Zypper
- **特色工具**：YaST（全功能系统管理工具）

#### 3.6.2 Gentoo

源代码编译安装的发行版，极致优化但维护成本高。

- **包管理器**：Portage
- **特点**：所有软件从源码编译，可针对特定 CPU 优化
- **适用场景**：追求极致性能、学习 Linux 编译原理

#### 3.6.3 Alpine Linux

面向安全和资源效率的轻量级发行版。

- **特点**：使用 musl libc 和 BusyBox、镜像仅约 5MB、默认启用安全加固
- **适用场景**：Docker 容器基础镜像、嵌入式设备、防火墙路由器

#### 3.6.4 Parrot Security OS

面向安全测试和隐私保护的发行版，是 Kali Linux 的主要替代品。

- **特点**：预装安全工具、注重隐私保护、界面美观、资源占用低于 Kali
- **适用场景**：渗透测试、隐私保护、日常安全使用

### 3.7 基于 Linux 的专用系统

除了通用 Linux 发行版，Linux 内核还被广泛应用于各种专用系统中：

#### 3.7.1 Android

Google 开发的移动操作系统，基于 Linux 内核，是全球使用人数最多的操作系统。

- **内核**：修改版 Linux 内核（增加 Binder IPC、电源管理等）
- **应用层**：Java/Kotlin + Android Runtime
- **市场地位**：全球移动市场份额约 70%

#### 3.7.2 Chrome OS

Google 开发的轻量级操作系统，基于 Linux 内核和 Chrome 浏览器。

- **特点**：以 Web 应用为主、启动快、安全性高、依赖云端
- **适用场景**：教育市场、轻量办公

#### 3.7.3 路由器与嵌入式系统

众多网络设备和嵌入式系统基于 Linux 内核构建：

| 系统 | 说明 |
|------|------|
| **OpenWrt** | 开源路由器固件，支持各种路由器硬件 |
| **DD-WRT** | 另一流行开源路由器固件 |
| **OpenWrt** | 物联网设备常用嵌入式 Linux |
| **Tizen** | 三星开发的嵌入式系统，用于智能手表和家电 |
| **YOCTO** | 用于构建定制嵌入式 Linux 的框架 |

#### 3.7.4 车载系统

现代智能汽车普遍采用 Linux 作为车载信息娱乐系统（IVI）的基础：

| 系统 | 说明 |
|------|------|
| **Automotive Grade Linux（AGL）** | Linux 基金会主导的车载 Linux 平台 |
| **Tesla 软件** | Tesla 车载系统基于定制 Linux |
| **Android Automotive** | Google 的车载 Android 系统 |

#### 3.7.5 云计算与容器

| 技术/系统 | 说明 |
|----------|------|
| **CoreOS / Container Linux** | 专为容器化工作负载设计的 Linux |
| **RancherOS** | 以 Docker 容器为系统进程的轻量级 Linux |
| **Bottlerocket** | Amazon 开发的容器优化 Linux |
| **Kubernetes 节点 OS** | 多种 Linux 发行版用于 K8s 集群节点 |

### 3.8 发行版选择指南

| 使用场景 | 推荐发行版 | 理由 |
|---------|-----------|------|
| **网络安全学习/渗透测试** | Kali Linux / Parrot OS | 预装安全工具，安全社区支持 |
| **Linux 初学者** | Ubuntu / Linux Mint | 文档丰富，社区活跃，易上手 |
| **服务器部署** | Ubuntu Server / Rocky Linux / Debian | 稳定可靠，长期支持 |
| **开发工作站** | Fedora / Pop!_OS / Ubuntu | 最新开发工具，硬件兼容好 |
| **企业生产环境** | RHEL / SLES | 商业支持，安全认证 |
| **容器/Docker** | Alpine Linux / Ubuntu Minimal | 体积小，安全 |
| **极致定制/学习** | Arch Linux | 从零构建，理解每个组件 |
| **旧硬件复活** | Linux Mint XFCE / Lubuntu | 低资源占用 |

### 3.9 各发行版包管理器对比

| 家族 | 包格式 | 包管理器 | 安装命令示例 |
|------|--------|---------|-------------|
| Debian 系 | `.deb` | apt / dpkg | `apt install nginx` |
| Red Hat 系 | `.rpm` | dnf / rpm | `dnf install nginx` |
| Arch 系 | `.pkg.tar.zst` | pacman | `pacman -S nginx` |
| SUSE 系 | `.rpm` | zypper / rpm | `zypper install nginx` |
| Alpine | `.apk` | apk | `apk add nginx` |
| Gentoo | ebuild | emerge | `emerge nginx` |

---

## 总结

Linux 作为开源操作系统的代表，凭借其稳定性、安全性和灵活性，已成为从嵌入式设备到超级计算机、从个人桌面到云计算基础设施的核心操作系统。理解 Linux 的基本概念、文件系统结构和主流发行版，是网络安全学习的重要基础。

**关键要点回顾**：

1. Linux 本质上是一个操作系统内核，配合 GNU 工具链和各类软件构成完整的发行版。
2. Linux 文件系统采用统一的树形目录结构（FHS），"一切皆文件"是其核心理念。
3. 基于 Linux 架构的系统涵盖桌面、服务器、移动设备、嵌入式设备等各个领域，选择合适的发行版取决于具体使用场景。

---

> **延伸学习**：结合本目录中的《Linux 全部命令手册》实践命令操作，配合《Kali 基本配置指南》搭建安全测试环境，逐步深入 Linux 系统管理与网络安全领域。
