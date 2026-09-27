# M2 Linux/Windows 操作系统基础 · 详细补充

> **模块编号**：M2
> **所属阶段**：阶段一 · 基础筑基
> **建议学习时机**：第 1-4 个月（与编程、网络并行）
> **每日投入**：2 小时（其中实操 ≥ 1.5 小时）
> **信息时效**：2026 年 9 月版

---

## 1. 模块定位与前置知识

### 模块定位
操作系统是一切安全技术的载体。不懂操作系统的安全就像空中楼阁——你连目标系统上跑的是什么都不知道，谈何攻击或防御？

本模块分为 **Linux 基础** 和 **Windows 基础** 两大部分，安全从业者必须双修：
- **Linux**：服务器占比超 80%，Web/云/内网服务器几乎全是 Linux，渗透测试主战场
- **Windows**：桌面端 + 企业域环境（Active Directory），内网渗透和红队主战场

### 前置知识
- 零基础可学，但建议先了解 M1 的 Shell 脚本基础
- 与 M3（计算机网络）并行学习效果最佳
- 需要一台能跑虚拟机的电脑（至少 16GB 内存，推荐 32GB）

### 安全从业者 OS 能力分级

| 级别 | Linux 能力 | Windows 能力 | 对应阶段 |
|------|-----------|-------------|---------|
| **L1 入门** | 常用命令、文件操作、用户权限 | 基本操作、服务管理、注册表基础 | 阶段一中 |
| **L2 实用** | 服务搭建、Shell 脚本、系统监控 | AD 基础、组策略、PowerShell 脚本 | 阶段一末 |
| **L3 熟练** | 内核模块、系统调优、安全加固 | 域渗透、权限维持、取证分析 | 阶段二末 |
| **L4 精通** | 内核漏洞、Rootkit、容器逃逸 | 内核漏洞、EDR 绕过、恶意代码分析 | 阶段三及以后 |

---

## 2. 知识图谱

```
操作系统基础（安全方向）
├── Linux 系统（60% 重点）
│   ├── 基础认知
│   │   ├── Linux 发行版（Kali / Ubuntu / CentOS / Debian）
│   │   ├── 文件系统层次结构（FHS）
│   │   ├── 启动流程（BIOS/UEFI → MBR/GPT → GRUB → Kernel → init/systemd）
│   │   └── 运行级别 / systemd 服务管理
│   │
│   ├── 命令行与 Shell
│   │   ├── 文件目录操作：ls/cd/pwd/mkdir/cp/mv/rm/find/locate
│   │   ├── 文本处理：cat/more/less/head/tail/grep/sed/awk/sort/uniq/wc
│   │   ├── 权限管理：chmod/chown/chgrp/umask/suid/sgid/sticky
│   │   ├── 进程管理：ps/top/htop/kill/nice/renice/jobs/&/nohup
│   │   ├── 用户与组：useradd/usermod/userdel/groupadd/su/sudo
│   │   ├── 网络命令：ifconfig/ip/ping/netstat/ss/traceroute/curl/wget/nc/ssh
│   │   ├── 软件包管理：apt/yum/dnf/pacman/dpkg/rpm
│   │   ├── 磁盘与文件系统：fdisk/parted/mkfs/mount/umount/df/du/fsck
│   │   └── 其他：tar/gzip/unzip/date/cal/history/man/which/whereis
│   │
│   ├── 服务搭建与配置
│   │   ├── Web：Nginx / Apache
│   │   ├── 数据库：MySQL / PostgreSQL / Redis / MongoDB
│   │   ├── 远程访问：SSH / VNC / RDP
│   │   ├── 文件传输：FTP / SFTP / Samba / NFS
│   │   ├── 邮件：Postfix / Dovecot（了解即可）
│   │   └── 代理与 VPN：Squid / OpenVPN / WireGuard
│   │
│   ├── Shell 脚本编程
│   │   ├── 变量、条件、循环、函数、参数
│   │   ├── 正则表达式与文本三剑客
│   │   └── 安全场景脚本
│   │
│   ├── Linux 安全基础
│   │   ├── 用户与权限安全、sudo 配置
│   │   ├── SSH 安全加固
│   │   ├── 防火墙：iptables / ufw / firewalld
│   │   ├── SELinux / AppArmor
│   │   ├── 日志系统：syslog / rsyslog / journald
│   │   ├── 计划任务：crontab / at / anacron
│   │   └── 常见提权方式（SUDO / SUID / 内核漏洞等）
│   │
│   └── 进阶（阶段二/三）
│       ├── 内核基础与内核模块
│       ├── 容器与 Docker 基础
│       ├── Linux 取证分析
│       └── Rootkit 与后门检测
│
└── Windows 系统（40% 重点）
    ├── 基础认知
    │   ├── Windows 版本（10/11 / Server 2016/2019/2022）
    │   ├── 系统目录结构（System32 / Program Files / Users）
    │   ├── Windows 启动流程
    │   └── Windows 内核与用户态
    │
    ├── 系统管理
    │   ├── 用户与组管理（本地用户 / 域用户）
    │   ├── 服务管理（services.msc / sc / Get-Service）
    │   ├── 注册表基础（regedit / reg / 五大配置单元）
    │   ├── 组策略（gpedit.msc / 域组策略）
    │   ├── 任务计划程序（Task Scheduler）
    │   └── 事件查看器（Event Viewer）
    │
    ├── PowerShell
    │   ├── 语法基础与常用 cmdlet
    │   ├── 管道与对象操作
    │   ├── WMI / CIM 操作
    │   ├── 脚本编写与模块
    │   └── 远程管理（WinRM / PsExec）
    │
    ├── Active Directory 基础
    │   ├── AD 概念：域 / 林 / 树 / OU / 域控制器
    │   ├── 用户 / 组 / 计算机对象
    │   ├── 组策略（GPO）基础
    │   ├── DNS 与 AD 集成
    │   └── AD 常用工具（ADUC / GPMC / RSAT）
    │
    ├── Windows 安全基础
    │   ├── Windows 安全模型（令牌 / 权限 / UAC）
    │   ├── NTFS 权限与共享权限
    │   ├── Windows Defender / 防火墙
    │   ├── BitLocker / EFS 加密
    │   ├── 常见 Windows 提权方式
    │   └── 凭据存储（SAM / NTDS.dit / LSA）
    │
    └── 进阶（阶段二/三）
        ├── 域渗透基础
        ├── Windows 取证
        ├── Sysmon 部署与日志分析
        └── 恶意代码分析基础
```

---

## 3. 学习顺序与时间表

### 总时长：约 3 个月（180 小时，与编程并行）

| 周次 | 学习内容 | 重点任务 | 实操目标 |
|------|---------|---------|---------|
| **第 1-2 周** | Linux 基础命令（上） | 文件操作、文本处理、权限管理 | 完成 50+ 个命令练习 |
| **第 3-4 周** | Linux 基础命令（下）+ 服务搭建 | 进程/用户/网络/磁盘、LAMP 搭建 | 搭出一个带数据库的博客 |
| **第 5-6 周** | Linux Shell 脚本 + 安全基础 | Shell 脚本、防火墙、日志、计划任务 | 写 10+ 个实用脚本 |
| **第 7-8 周** | Windows 系统管理 | 用户/服务/注册表/组策略/事件查看器 | 熟悉 Windows 核心管理工具 |
| **第 9-10 周** | PowerShell + AD 基础 | PowerShell 脚本、AD 概念与操作 | 搭建单域实验环境 |
| **第 11-12 周** | 双系统安全加固 + 综合实操 | Linux/Windows 安全加固、日志分析 | 输出一份系统加固报告 |

### 学习方法建议

```
1. 命令学习法：每个命令 → 查 man → 试 3 个常用场景 → 记笔记
2. 服务搭建法：先按教程搭 → 改配置故意弄坏 → 排查修复 → 写复盘
3. 对比学习法：学 Linux 的时候对比 Windows，加深理解
4. 闯关练习法：用 OverTheWire / Bandit 等闯关平台检验成果
```

---

## 4. 工具链与版本建议

### 4.1 虚拟机软件

| 工具 | 版本 | 用途 | 优先级 | 费用 |
|------|------|------|--------|------|
| **VMware Workstation Pro** | 17.x | 主力虚拟机软件，快照/克隆/网络功能强 | ⭐⭐⭐ 推荐 | 付费（可试用） |
| **VirtualBox** | 7.x | 免费开源虚拟机，功能够用 | ⭐⭐⭐ 必装 | 免费 |
| **Hyper-V** | 随 Windows | Windows 自带，适合跑 Windows 虚拟机 | ⭐⭐ 可选 | 免费 |

> **建议**：如果预算有限用 VirtualBox，预算充足 VMware 体验更好。Linux 用 VirtualBox 足够，Windows AD 实验环境可能需要 VMware 的一些高级功能。

### 4.2 Linux 发行版

| 发行版 | 版本 | 用途 | 优先级 |
|--------|------|------|--------|
| **Kali Linux** | 2026.x | 渗透测试主力系统，工具齐全 | ⭐⭐⭐ 必装 |
| **Ubuntu Server** | 22.04 LTS / 24.04 LTS | 服务搭建练习，接近生产环境 | ⭐⭐⭐ 必装 |
| **CentOS Stream / Rocky Linux** | 9.x | 红帽系练习，企业服务器常见 | ⭐⭐ 建议装 |

### 4.3 Windows 版本

| 版本 | 用途 | 优先级 |
|------|------|--------|
| **Windows 10 / 11 专业版** | 桌面端练习、加入域 | ⭐⭐⭐ 必装 |
| **Windows Server 2022** | 域控制器、AD 实验环境 | ⭐⭐⭐ 必装 |

> **获取方式**：微软评估中心可下载 180 天评估版，用于学习完全合法。

### 4.4 辅助工具

| 工具 | 用途 | 优先级 |
|------|------|--------|
| **Xshell / MobaXterm / FinalShell** | SSH 客户端（Windows 下） | ⭐⭐⭐ 必装 |
| **Terminator / Tilix** | 多终端工具（Linux 下） | ⭐⭐ 推荐 |
| **WinSCP / FileZilla** | FTP / SFTP 客户端 | ⭐⭐ 推荐 |
| **Navicat / DBeaver / phpMyAdmin** | 数据库管理工具 | ⭐⭐ 推荐 |
| **Notepad++ / VS Code** | 配置文件编辑器 | ⭐⭐⭐ 必装 |

---

## 5. 编程 / 脚本练习

### 5.1 Linux Shell 脚本练习

#### 🟢 基础练习
```bash
# 练习 1：写一个脚本，统计当前目录下各类文件的数量
#!/bin/bash
echo "Regular files: $(find . -type f | wc -l)"
echo "Directories: $(find . -type d | wc -l)"
echo "Symlinks: $(find . -type l | wc -l)"

# 练习 2：写一个备份脚本，打包指定目录并加日期后缀
#!/bin/bash
backup_dir="/var/www/html"
dest="/backup"
date=$(date +%Y%m%d_%H%M%S)
tar -czf "$dest/backup_$date.tar.gz" "$backup_dir"
echo "Backup completed: backup_$date.tar.gz"

# 练习 3：监控系统负载，超过阈值告警
# 练习 4：批量修改目录下所有 .txt 文件为 .md
# 练习 5：检查网站是否存活，挂了自动发邮件（或写日志）
```

#### 🟡 安全场景练习
```bash
# 练习 6：分析 Nginx 日志，找出访问频率最高的 IP（可能的 CC 攻击）
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -20

# 练习 7：扫描本地监听端口，检查是否有异常端口开放
netstat -tlnp | grep -v '127.0.0.1'

# 练习 8：检查系统中所有 SUID/SGID 文件（潜在提权点）
find / -perm -4000 -type f 2>/dev/null
find / -perm -2000 -type f 2>/dev/null

# 练习 9：查看最近登录失败的 IP（SSH 爆破检测）
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn

# 练习 10：检查系统中的可疑计划任务
crontab -l
cat /etc/crontab
ls -la /etc/cron.*
```

### 5.2 PowerShell 脚本练习

#### 🟢 基础练习
```powershell
# 练习 1：获取系统基本信息（OS、CPU、内存、磁盘）
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, LastBootUpTime
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Select-Object DeviceID, Size, FreeSpace

# 练习 2：批量创建本地用户（从 CSV 读取）
# 练习 3：检查系统中所有自动启动的服务
# 练习 4：导出系统安全事件日志（Event ID 4625 登录失败等）
```

#### 🟡 安全场景练习
```powershell
# 练习 5：获取本地管理员组成员
Get-LocalGroupMember -Group "Administrators"

# 练习 6：查询最近 24 小时内的登录失败事件
Get-WinEvent -FilterHashtable @{
    LogName = 'Security'
    ID = 4625
    StartTime = (Get-Date).AddHours(-24)
}

# 练习 7：列出所有监听端口及其所属进程
Get-NetTCPConnection -State Listen | ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        LocalAddress = $_.LocalAddress
        LocalPort = $_.LocalPort
        ProcessName = $proc.ProcessName
        PID = $_.OwningProcess
    }
}

# 练习 8：检查注册表中的常见自启动位置
# 练习 9：用 PowerShell 实现一个简单的端口扫描器
# 练习 10：查询 AD 中所有域管理员组成员（需域环境）
```

---

## 6. 靶场与实验环境

### 6.1 命令行闯关平台

| 平台 | 系统 | 特点 | 难度 |
|------|------|------|------|
| **OverTheWire - Bandit** | Linux | 最经典的命令行闯关，从零到进阶 | ⭐→⭐⭐⭐ |
| **OverTheWire - Natas** | Linux/Web | Web 安全入门，需要命令行基础 | ⭐⭐ |
| **OverTheWire - Krypton** | Linux | 密码学闯关 | ⭐⭐ |
| **OverTheWire - Leviathan** | Linux | 权限提升闯关 | ⭐⭐⭐ |
| **Wargames - Narnia** | Linux | 漏洞利用入门 | ⭐⭐⭐ |
| **PowerShell Challenge** | Windows | PowerShell 闯关（GitHub 上搜索） | ⭐⭐ |

### 6.2 本地实验环境搭建

#### 环境一：Linux 服务练习环境（第 1-2 月）
```
VM 1: Kali Linux (攻击机)
  ├── IP: 192.168.10.10
  └── 用途：日常工具、攻击测试

VM 2: Ubuntu Server (靶机/练习机)
  ├── IP: 192.168.10.20
  ├── 安装：Nginx + MySQL + PHP + WordPress
  ├── 安装：SSH / FTP / Samba
  └── 用途：服务搭建、漏洞练习
```

#### 环境二：Windows AD 实验环境（第 3 月）
```
VM 3: Windows Server 2022 (域控制器)
  ├── IP: 192.168.20.10
  ├── 域名：corp.local
  ├── 角色：DC + DNS + DHCP
  └── OU 结构：IT / HR / Finance / Servers

VM 4: Windows 10/11 (域成员-工作站)
  ├── IP: 192.168.20.20
  └── 加入 corp.local 域

VM 5: Windows Server 2022 (成员服务器)
  ├── IP: 192.168.20.30
  └── 文件服务器 / Web 服务器
```

#### 环境三：综合攻防环境（阶段二）
```
192.168.10.0/24 (DMZ 区)
  ├── Kali (攻击机)
  ├── Ubuntu (Web 服务器 - 有漏洞)
  └── pfSense (防火墙)

192.168.20.0/24 (内网区)
  ├── Windows Server 2022 (DC)
  ├── Windows 10 (工作站 × 2)
  └── Windows Server (文件服务器)
```

### 6.3 虚拟机快照管理最佳实践

```
系统安装完成 → 快照："初始状态 - 干净系统"
        ↓
基础配置完成（IP/工具/更新） → 快照："基础配置完成"
        ↓
服务搭建完成 → 快照："LAMP 搭建完成"
        ↓
打靶前 → 快照："实验前快照"
        ↓
实验完成 → 恢复到实验前快照，保持环境干净
```

> **关键原则**：做任何可能破坏系统的操作前，先拍快照！

---

## 7. 推荐资料

### 📚 书籍

| 书名 | 系统 | 难度 | 备注 |
|------|------|------|------|
| 《鸟哥的 Linux 私房菜：基础学习篇》第 4 版 | Linux | ⭐ 入门 | 中文 Linux 入门经典，内容详尽 |
| 《鸟哥的 Linux 私房菜：服务器架设篇》第 3 版 | Linux | ⭐⭐ 进阶 | 服务搭建大全 |
| 《Linux 命令行与 Shell 脚本编程大全》第 4 版 | Linux | ⭐⭐ 入门 | Shell 脚本系统学习 |
| 《Linux 就该这么学》第 2 版 | Linux | ⭐ 入门 | 刘遄著，适合入门 |
| 《Windows PowerShell 实战指南》第 3 版 | Windows | ⭐⭐ 入门 | PowerShell 系统学习 |
| 《Windows 内核原理与实现》 | Windows | ⭐⭐⭐⭐ 选学 | 深入 Windows 内核 |
| 《Active Directory 管理指南》 | Windows AD | ⭐⭐ 入门 | AD 系统管理 |
| 《内网安全攻防：渗透测试实战指南》 | 双系统 | ⭐⭐⭐ 进阶 | 内网渗透必读，阶段二用 |

### 🌐 在线教程与文档

| 资源 | 系统 | 关键词 | 特点 |
|------|------|--------|------|
| **Linux man 手册** | Linux | man7.org | 最权威的命令参考 |
| **Linux 工具快速教程** | Linux | linuxtools.linux.cn | 中文命令速查 |
| **菜鸟教程 Linux 教程** | Linux | runoob.com/linux | 入门友好 |
| **Ubuntu 官方文档** | Linux | help.ubuntu.com | Ubuntu 官方参考 |
| **Microsoft Learn** | Windows | learn.microsoft.com | 微软官方学习平台，免费 |
| **PowerShell 文档** | Windows | learn.microsoft.com/powershell | PS 官方文档 |
| **AD 分步指南** | Windows AD | learn.microsoft.com | AD 官方教程 |

### 🎥 视频课程

| 课程 | 平台 | 适合人群 |
|------|------|---------|
| **鸟哥 Linux 视频教程** | B 站 | Linux 零基础入门 |
| **黑马程序员 Linux 教程** | B 站 | 系统全面 |
| **尚硅谷 Linux 教程** | B 站 | 入门到进阶 |
| **PowerShell 从入门到精通** | B 站 | Windows 安全必备 |
| **Active Directory 系列教程** | B 站 / YouTube | AD 入门 |
| **NetworkChuck Linux 系列** | YouTube | 英文，讲得有趣 |
| **John Hammond Windows 安全** | YouTube | 英文，安全视角 |

### 🎯 实操平台

| 平台 | 用途 | 费用 |
|------|------|------|
| **TryHackMe Pre Security / Linux Fundamentals** | Linux 基础路径 | 免费 + 付费 |
| **TryHackMe Windows Fundamentals** | Windows 基础路径 | 免费 + 付费 |
| **HTB Academy - Linux Fundamentals** | Linux 系统课程 | 付费 |
| **OverTheWire** | 命令行闯关 | 免费 |
| **HackTheBox Starting Point** | 渗透入门靶机 | 免费 |

---

## 8. 实战项目

### 项目一：LAMP + WordPress 搭建与加固（Linux）

**目标**：从零搭建一个完整的 Web 服务，并进行安全加固。

**任务清单**：
1. 安装 Ubuntu Server，配置网络和 SSH
2. 安装 Nginx/Apache、MySQL/MariaDB、PHP（LAMP 栈）
3. 部署 WordPress 博客，配置数据库和虚拟主机
4. 配置 HTTPS（自签证书或 Let's Encrypt）
5. 安全加固：
   - SSH：改端口、禁 root 登录、密钥登录
   - 防火墙：配置 iptables/ufw，只开放必要端口
   - MySQL：删默认库、禁远程登录、强密码
   - PHP：禁用危险函数、配置 open_basedir
   - Nginx：隐藏版本号、配置安全头
6. 输出一份《Web 服务器安全加固报告》

**预计耗时**：20 小时
**产出物**：运行中的博客 + 加固报告

---

### 项目二：Active Directory 域环境搭建（Windows）

**目标**：从零搭建一个企业级 AD 域环境，理解域管理。

**任务清单**：
1. 安装 Windows Server 2022，升级为域控制器
   - 域名：corp.local
   - 配置 DNS、DHCP
2. 创建 OU 结构：
   - IT / HR / Finance / Servers / Workstations
3. 创建用户和组：
   - 每个 OU 下创建 5+ 个用户
   - 创建组：Domain Admins、IT_Admins、HR_Users 等
4. 配置组策略（GPO）：
   - 密码策略（复杂度、长度、过期时间）
   - 账户锁定策略
   - 桌面壁纸 / 文件夹重定向
   - 软件部署
5. 加入 2 台客户端（Windows 10/11）到域
6. 部署文件服务器，配置共享权限和 NTFS 权限
7. 输出一份《AD 域环境搭建与配置手册》

**预计耗时**：25 小时
**产出物**：运行中的域环境 + 配置手册

---

### 项目三：日志分析与入侵检测实战

**目标**：在两个系统上模拟攻击，然后通过日志发现入侵痕迹。

**Linux 部分任务**：
1. 配置 rsyslog 集中收集日志
2. 模拟 SSH 暴力破解攻击（用 hydra）
3. 分析 auth.log，找出攻击 IP 和时间
4. 模拟 Web 攻击（SQL 注入 / XSS），分析 Nginx access.log
5. 写一个 Shell 脚本，自动提取攻击特征

**Windows 部分任务**：
1. 配置安全审计策略，开启登录事件审计
2. 安装 Sysmon，配置基础规则
3. 模拟 RDP 爆破 / 本地提权 / 横向移动
4. 用事件查看器 + PowerShell 分析安全日志
5. 用 Sysmon 日志检测恶意进程创建 / 网络连接

**预计耗时**：20 小时
**产出物**：日志分析报告 + 检测脚本

---

### 项目四：系统安全基线核查脚本

**目标**：编写自动化脚本，检查系统的安全配置是否符合基线。

**Linux 核查项**（参考 CIS Benchmark）：
- SSH 配置检查（Protocol 版本、root 登录、空密码等）
- 用户密码策略检查
- 文件权限检查（/etc/passwd、/etc/shadow 等）
- 防火墙状态检查
- 不必要服务检查
- 日志审计配置检查
- SUID/SGID 文件检查

**Windows 核查项**（参考 CIS Benchmark）：
- 密码策略与账户锁定策略
- 审计策略配置
- Windows 防火墙状态
- 自动更新配置
- UAC 配置
- 不必要服务检查
- 共享文件夹检查

**预计耗时**：25 小时
**产出物**：两个系统的安全核查脚本 + HTML 报告生成功能

---

## 9. 常见误区

### ❌ 误区 1：Linux 用图形界面，Windows 用鼠标点
**现象**：装了 Linux 也用图形界面，Linux 命令一个不会。
**纠正**：Linux 服务器基本都是无图形界面的，强制自己用命令行操作。Kali 的图形界面是为了跑 Burp 等 GUI 工具，系统管理必须用命令行。

### ❌ 误区 2：命令靠背，不用记原理
**现象**：背了一堆命令参数，换个场景就不会用了。
**纠正**：理解命令的工作原理，掌握核心参数，其他查 man 手册。重要的是知道"有这个工具"和"能做什么"，具体参数可以查。

### ❌ 误区 3：只学 Linux，不学 Windows
**现象**：觉得"黑客都用 Kali"，Windows 完全不懂。
**纠正**：企业内网 90% 以上是 Windows 域环境，内网渗透、红队、蓝队都离不开 Windows。Linux 和 Windows 至少三七开，不能偏科。

### ❌ 误区 4：虚拟机环境乱搞，不做快照
**现象**：实验搞崩了系统，又得重装，浪费时间。
**纠正**：养成操作前拍快照的好习惯。系统干净状态拍一个，关键节点拍一个，搞崩了直接回滚。

### ❌ 误区 5：服务搭建按教程复制粘贴，不理解原理
**现象**：照着教程一步步复制粘贴命令，搭好了也不知道每个配置什么意思。
**纠正**：每改一个配置，先想"为什么要这么改？改了有什么效果？"故意改错几个参数，看会出什么问题，排查过程才是最大的收获。

### ❌ 误区 6：不重视权限模型
**现象**：对 Linux 文件权限、Windows ACL、AD 权限一知半解。
**纠正**：权限模型是安全的核心。提权、横向移动、权限维持本质上都是在玩权限。把权限模型吃透，后续学渗透会轻松很多。

---

## 10. 自测题与产出物

### 10.1 Linux 自测题

**基础操作题**：
1. 如何递归查找 /var 目录下所有大于 100MB 的 .log 文件？
2. 如何查看哪个进程占用了 8080 端口？
3. 如何给脚本添加执行权限？SUID 和 SGID 有什么区别？
4. 如何修改 SSH 默认端口并禁止 root 登录？
5. 如何查看系统中所有监听的端口和对应的进程？

**进阶问题**：
6. Linux 启动流程是什么？从按下电源键到登录界面经历了哪些阶段？
7. 什么是 inode？硬链接和软链接有什么区别？
8. 常见的 Linux 提权方式有哪些？（至少说 5 种）
9. iptables 的四表五链是什么？如何添加一条规则禁止 192.168.1.0/24 访问 22 端口？
10. 如何排查 Linux 系统被入侵？从哪些方面入手？

**实操题**：
1. 30 分钟内从零搭建 LAMP 环境并部署 WordPress
2. 用一条命令分析 Nginx 日志，统计 Top 10 404 URL
3. 写一个脚本，监控磁盘使用率，超过 90% 自动清理 7 天前的日志

### 10.2 Windows 自测题

**基础操作题**：
1. Windows 注册表的五大配置单元（Hive）是什么？
2. 如何用命令行（cmd 和 PowerShell）查看本机 IP 地址？
3. 什么是 UAC？它有几个级别？
4. NTFS 权限和共享权限有什么区别？同时设置时以哪个为准？
5. 如何查看系统中所有自动启动的程序和服务？

**AD 相关题**：
6. 什么是域、林、树、OU？它们之间的关系是什么？
7. 域用户和本地用户有什么区别？
8. 组策略的应用顺序是什么（LSDOU）？
9. AD 中的组作用域有哪几种（本地域组 / 全局组 / 通用组）？区别是什么？
10. 常见的域内权限维持方式有哪些？

**实操题**：
1. 2 小时内从零搭建一个单域环境（1DC + 1 客户端）
2. 用 PowerShell 查询最近 7 天的登录失败记录
3. 用 PowerShell 获取所有域管理员组的成员列表

### 10.3 阶段产出物清单

完成本模块后，你应该拥有以下产出物：

- [ ] **运行中的实验环境**
  - [ ] Kali Linux 虚拟机（攻击机）
  - [ ] Ubuntu Server 虚拟机（LAMP + WordPress）
  - [ ] Windows Server 2022 域控制器
  - [ ] Windows 10/11 域成员主机
- [ ] **脚本工具集**
  - [ ] 10+ 个 Linux 运维/安全脚本
  - [ ] 10+ 个 PowerShell 安全脚本
  - [ ] 系统安全基线核查脚本（Linux + Windows）
- [ ] **技术文档**
  - [ ] Linux 常用命令速查表
  - [ ] LAMP 搭建与加固手册
  - [ ] AD 域环境搭建手册
  - [ ] 日志分析报告（2 份以上）
- [ ] **闯关记录**
  - [ ] OverTheWire Bandit 通关至 Level 25+
  - [ ] TryHackMe Linux Fundamentals 路径 100%
  - [ ] TryHackMe Windows Fundamentals 路径 100%

---

> **下一步建议**：操作系统和网络是安全的两大基石，学完 M2 后立即进入 **M3 计算机网络**，两者结合才能理解"攻击是怎么发生的"。同时，每天保持 30 分钟命令行练习，不要手生。
