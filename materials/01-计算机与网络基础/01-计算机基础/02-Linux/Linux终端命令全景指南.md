# Linux 终端命令全景指南

> 本文系统介绍 Linux 终端命令体系，涵盖命令层级认知、11 大类核心命令分类、参数与案例呈现规范、速查表、高风险命令清单、学习路径及 2026 年免费学习资源。Linux 命令数量庞大，本文聚焦**核心命令 + 功能分类 + 代表性案例**，不求全但求精。面向 Linux 运维工程师、安全工程师和初学者，深度覆盖操作参考 + 案例实战 + 安全加固。示例覆盖 Ubuntu/Debian、CentOS/RHEL、Fedora、Arch 等主流发行版。

---

## 目录

- [一、命令体系认知](#一命令体系认知)
  - [1.1 Linux 命令的层级划分](#11-linux-命令的层级划分)
  - [1.2 命令的构成](#12-命令的构成)
  - [1.3 如何查询命令](#13-如何查询命令)
- [二、核心命令分类体系](#二核心命令分类体系)
  - [类别 1：文件与目录操作](#类别-1文件与目录操作)
  - [类别 2：文本查看与处理](#类别-2文本查看与处理)
  - [类别 3：文件压缩与归档](#类别-3文件压缩与归档)
  - [类别 4：用户与权限管理](#类别-4用户与权限管理)
  - [类别 5：进程与作业控制](#类别-5进程与作业控制)
  - [类别 6：系统信息与监控](#类别-6系统信息与监控)
  - [类别 7：网络工具](#类别-7网络工具)
  - [类别 8：包管理](#类别-8包管理)
  - [类别 9：服务与 systemd](#类别-9服务与-systemd)
  - [类别 10：Shell 内置命令与脚本](#类别-10shell-内置命令与脚本)
  - [类别 11：开发与调试工具](#类别-11开发与调试工具)
- [三、命令参数与案例的呈现要求](#三命令参数与案例的呈现要求)
- [四、常用命令速查表](#四常用命令速查表)
- [五、高风险命令清单](#五高风险命令清单)
- [六、学习路径](#六学习路径)
- [七、2026 年免费学习资源](#七2026-年免费学习资源)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、命令体系认知

### 1.1 Linux 命令的层级划分

Linux 终端中的命令并非来自单一来源，而是按功能层次分布在不同的软件层中。理解命令的来源有助于排查"command not found"问题、理解命令行为差异（如 `cd` 是 Shell 内置而非外部程序）以及在不同发行版间迁移。

| 层级 | 英文 | 来源 | 代表命令 | 特点 |
|------|------|------|----------|------|
| **Shell 内置命令** | Shell Builtins | Bash/Shell 自身 | `cd`、`echo`、`alias`、`type`、`export`、`source`、`history`、`pwd`、`read`、`printf` | 无需外部二进制文件，执行速度快，操作 Shell 自身状态 |
| **GNU Coreutils** | GNU Core Utilities | coreutils 软件包 | `ls`、`cp`、`mv`、`rm`、`cat`、`cut`、`sort`、`uniq`、`wc`、`head`、`tail`、`chmod`、`chown`、`date`、`who`、`id` 等 ~90 个 | 近 90 个基础命令，涵盖文件操作、文本处理、系统信息、权限管理、编码校验、进程控制 |
| **系统管理工具** | System Administration | util-linux、procps、systemd 等 | `systemctl`、`journalctl`、`crontab`、`fdisk`、`mount`、`kill`、`ps`、`top`、`free`、`dmidecode` | 管理系统服务、进程、磁盘、计划任务 |
| **网络工具** | Networking Tools | iproute2、iputils、curl 等 | `ip`、`ss`、`curl`、`ssh`、`tcpdump`、`ping`、`traceroute`、`wget`、`scp`、`rsync` | 配置网络、诊断连通性、传输数据 |
| **开发与调试工具** | Development & Debugging | gcc、gdb、binutils、strace 等 | `gcc`、`gdb`、`strace`、`ldd`、`nm`、`objdump`、`make`、`pkg-config` | 编译、调试、分析二进制、依赖管理 |
| **安全工具** | Security Tools | audit、iptables、policycoreutils 等 | `iptables`、`nftables`、`auditd`、`getenforce`、`sestatus`、`aide`、`openssl` | 防火墙、审计、强制访问控制、加密 |

> **如何区分内置与外部命令？** 使用 `type command_name`：若输出 `xxx is a shell builtin` 则为内置命令；若输出路径（如 `/usr/bin/xxx`）则为外部命令。

```bash
# 判断命令来源
type cd        # cd is a shell builtin
type ls        # ls is aliased to 'ls --color=auto' 或 /usr/bin/ls
type systemctl  # systemctl is /usr/bin/systemctl

# 查看所有 Shell 内置命令
help            # Bash 内置命令列表
enable -a       # 列出所有内置命令及启用状态
```

#### 各层级详解

**1. Shell 内置命令（Builtins）**

内置命令直接由 Shell 解释器执行，不调用外部程序。它们能直接读取和修改 Shell 进程的环境变量、当前目录、别名等状态。

| 命令 | 功能 | 说明 |
|------|------|------|
| `cd` | 切换目录 | 改变 Shell 当前工作目录，外部程序无法做到 |
| `echo` | 输出文本 | 打印到标准输出 |
| `alias` | 设置别名 | 创建命令别名，仅当前 Shell 有效 |
| `type` | 查看命令类型 | 区分内置/外部/别名/函数 |
| `export` | 导出环境变量 | 将变量传递给子进程 |
| `source` / `.` | 执行脚本 | 在当前 Shell 上下文中执行，不创建子进程 |
| `history` | 命令历史 | 查看和管理命令历史记录 |
| `pwd` | 显示当前路径 | Print Working Directory |
| `read` | 读取输入 | 从标准输入读取到变量 |
| `printf` | 格式化输出 | 比 echo 更灵活的格式控制 |

**2. GNU Coreutils**

Coreutils 是 GNU 项目的基础工具集，提供 ~90 个命令，是日常使用最频繁的命令来源。

| 分类 | 代表命令 | 说明 |
|------|----------|------|
| 文件操作 | `ls`、`cp`、`mv`、`rm`、`ln`、`mkdir`、`rmdir`、`touch` | 浏览、创建、复制、移动、删除文件和目录 |
| 文本处理 | `cat`、`cut`、`sort`、`uniq`、`wc`、`head`、`tail`、`tr`、`tac`、`nl` | 查看、过滤、转换、统计文本 |
| 权限管理 | `chmod`、`chown`、`chgrp`、`umask` | 修改文件权限和所有者 |
| 系统信息 | `uname`、`hostname`、`date`、`uptime`、`who`、`id`、`whoami` | 主机名、时间、用户、系统信息 |
| 进程控制 | `kill`、`nice` | 发送信号、调整优先级 |
| 编码校验 | `md5sum`、`sha256sum`、`base64` | 校验和、编码 |

**3. 系统管理工具**

来自 `util-linux`、`procps`、`systemd` 等软件包，用于系统级管理。

| 分类 | 代表命令 | 来源包 |
|------|----------|--------|
| 服务管理 | `systemctl`、`journalctl` | systemd |
| 进程管理 | `ps`、`top`、`free`、`vmstat`、`pkill`、`pgrep` | procps / procps-ng |
| 磁盘管理 | `fdisk`、`mount`、`umount`、`lsblk`、`blkid` | util-linux |
| 计划任务 | `crontab`、`at` | cron / at |

**4. 网络工具**

来自 `iproute2`、`iputils`、`curl` 等软件包。

| 分类 | 代表命令 | 来源包 |
|------|----------|--------|
| 接口配置 | `ip`、`ethtool`、`nmcli` | iproute2 / ethtool / NetworkManager |
| 连通性 | `ping`、`traceroute`、`mtr`、`tracepath` | iputils / traceroute / mtr |
| 连接查看 | `ss`、`netstat` | iproute2 / net-tools（已过时） |
| 数据传输 | `curl`、`wget`、`scp`、`rsync` | curl / wget / openssh / rsync |
| 抓包 | `tcpdump` | tcpdump |

**5. 开发与调试工具**

| 分类 | 代表命令 | 用途 |
|------|----------|------|
| 编译 | `gcc`、`g++`、`make` | C/C++ 编译和构建 |
| 调试 | `gdb`、`strace`、`ltrace` | 程序调试、系统调用追踪 |
| 依赖 | `ldd`、`ldconfig`、`pkg-config` | 动态库依赖分析 |
| 二进制 | `nm`、`objdump`、`readelf` | 符号表、反汇编、ELF 信息 |
| 版本控制 | `git` | 代码版本管理 |

**6. 安全工具**

| 分类 | 代表命令 | 用途 |
|------|----------|------|
| 防火墙 | `iptables`、`nftables`、`firewalld`、`ufw` | 网络访问控制 |
| 审计 | `auditd`、`auditctl`、`ausearch` | 系统调用审计 |
| 强制访问控制 | `getenforce`、`setenforce`、`sestatus`、`chcon` | SELinux |
| 文件完整性 | `aide`、`tripwire` | 文件完整性校验 |
| 加密 | `openssl`、`gpg`、`ssh-keygen` | 加密、签名、密钥管理 |

---

### 1.2 命令的构成

一条 Linux 命令的基本结构如下：

```
command [options] [arguments]
│        │          │
│        │          └── 参数：命令操作的对象（文件名、目录、用户名等）
│        └── 选项：修改命令行为的开关或参数
└── 命令名称：程序名或内置命令名
```

#### 选项的类型

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| **短选项** | `-字母` | `-l`、`-a`、`-h` | 单个字母，前缀一个连字符 |
| **长选项** | `--单词` | `--all`、`--human-readable` | 完整单词，前缀两个连字符 |
| **带值选项** | `-值` 或 `--opt=值` | `-T 4`、`--lines=20` | 选项后接参数值 |
| **组合短选项** | `-abc` | `-lah`（= `-l -a -h`） | 多个短选项可合并，仅最后可带值 |

```bash
# 短选项
ls -l
ls -a

# 长选项（与短选项等价）
ls --all
ls --human-readable

# 组合短选项
ls -lah        # 等同于 ls -l -a -h

# 带值选项
head -n 20 file.txt
head --lines=20 file.txt

# 选项位置：选项通常在参数前，但 GNU 工具也支持参数后加选项
ls -l /etc
ls /etc -l     # 也可工作（GNU Coreutils）
```

#### 通配符与正则表达式

| 类型 | 字符 | 含义 | 示例 |
|------|------|------|------|
| **通配符** | `*` | 匹配任意数量字符 | `ls *.txt` |
| | `?` | 匹配单个字符 | `ls file?.txt` |
| | `[abc]` | 匹配括号内任一字符 | `ls file[123].txt` |
| | `[a-z]` | 匹配范围 | `ls file[a-z].txt` |
| | `[!abc]` | 匹配不在括号内的字符 | `ls file[!0-9].txt` |
| **正则（BRE）** | `.` | 匹配任意单字符 | `grep a.c file` |
| | `^` | 行首 | `grep '^root' /etc/passwd` |
| | `$` | 行尾 | `grep 'bash$' /etc/passwd` |
| | `*` | 前一字符出现 0 次或多次 | `grep 'ab*c' file` |
| **正则（ERE）** | `+` | 前一字符出现 1 次或多次 | `grep -E 'go+gle' file` |
| | `?` | 前一字符出现 0 次或 1 次 | `grep -E 'colou?r' file` |
| | `\|` | 或 | `grep -E 'cat\|dog' file` |
| | `()` | 分组 | `grep -E '(ab)+' file` |

> **关键区别**：通配符（Globbing）由 Shell 展开，用于文件名匹配；正则表达式由命令（如 grep、sed、awk）解析，用于文本内容匹配。`*` 在通配符中匹配任意字符串，在正则中表示前一字符出现 0 次或多次。

```bash
# 通配符示例（Shell 展开）
ls *.log               # 列出所有 .log 文件
rm file[1-9].tmp       # 删除 file1.tmp ~ file9.tmp
cp /var/log/*.log /backup/  # 复制所有日志文件

# 正则表达式示例（命令解析）
grep '^ERROR' /var/log/syslog     # 查找以 ERROR 开头的行
grep -E '[0-9]{1,3}\.' /etc/hosts # 查找 IP 地址片段
```

---

### 1.3 如何查询命令

| 工具 | 用途 | 示例 |
|------|------|------|
| `man` | 查看完整手册页 | `man ls` |
| `--help` | 查看简要帮助 | `ls --help` |
| `info` | 查看 GNU 信息页（更详细） | `info coreutils` |
| `apropos` | 按关键字搜索命令 | `apropos password` |
| `whatis` | 查看命令一句话描述 | `whatis ls` |
| `type` | 查看命令来源类型 | `type cd` |
| `which` | 查找命令的可执行文件路径 | `which python3` |
| `whereis` | 查找二进制、源码、手册路径 | `whereis ls` |

#### man 手册分区

| 区号 | 内容 | 示例 |
|------|------|------|
| 1 | 用户命令 | `man 1 ls` |
| 2 | 系统调用 | `man 2 open` |
| 3 | 库函数 | `man 3 printf` |
| 4 | 设备文件 | `man 4 null` |
| 5 | 配置文件格式 | `man 5 passwd` |
| 6 | 游戏 | `man 6 fortune` |
| 7 | 约定与杂项 | `man 7 regex` |
| 8 | 系统管理命令 | `man 8 fdisk` |

```bash
# 查看 ls 手册
man ls

# 查看 passwd 配置文件格式（而非 passwd 命令）
man 5 passwd

# 搜索与 "password" 相关的命令
apropos password
# 输出示例：passwd (1)           - change user password
#           passwd (5)           - the password file

# 查看一句话描述
whatis ls
# ls (1) - list directory contents

# 定位命令的可执行文件
which python3
# /usr/bin/python3

# 查看二进制、手册、源码位置
whereis ls
# ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz

# 查看命令类型
type ls        # ls is aliased to 'ls --color=auto'
type cd        # cd is a shell builtin
type ll        # ll is aliased to 'ls -alF'
```

---

## 二、核心命令分类体系

### 类别 1：文件与目录操作

#### 浏览与定位

**ls — 列出目录内容**

```
├── 语法：ls [选项] [路径...]
├── 核心参数：
│   ├── -l          长格式（权限/所有者/大小/时间）
│   ├── -a          显示隐藏文件（含 . 和 ..）
│   ├── -A          显示隐藏文件（不含 . 和 ..）
│   ├── -h          人类可读大小（K/M/G），配合 -l 使用
│   ├── -t          按修改时间排序（最新在前）
│   ├── -S          按大小排序（最大在前）
│   ├── -r          反向排序
│   ├── -R          递归列出子目录
│   ├── -d          只列目录本身
│   ├── -i          显示 inode 号
│   └── -Z          显示 SELinux 安全上下文
├── 调用案例：
│   ├── 基础用法：ls /etc
│   ├── 组合用法：ls -lah /var/log
│   └── 管道用法：ls -lhS /var/log | head -11
├── 适用场景：日常目录浏览、快速定位大文件
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
# 基础用法
ls
ls /etc

# 详细列表 + 隐藏文件 + 人类可读
ls -lah

# 按时间排序（最新的在最后）
ls -ltr /var/log

# 按大小排序，取前 10 大文件
ls -lhS /var/log | head -11

# 递归列出子目录
ls -R /etc/ssh

# 只列目录本身
ls -d /etc/*/

# 显示 SELinux 上下文（CentOS/RHEL）
ls -Z /var/www/
```

**cd — 切换目录（Shell 内置）**

```
├── 语法：cd [目录]
├── 核心参数：
│   ├── ~           用户主目录
│   ├── -           上次所在目录
│   ├── ..          上一级目录
│   └── 无参数      回到主目录
├── 调用案例：
│   ├── cd /var/log
│   ├── cd ~
│   └── cd -
├── 适用场景：目录导航
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
cd /etc              # 切换到 /etc
cd                   # 回到主目录
cd ~                 # 回到主目录
cd ..                # 上一级
cd ../..             # 上两级
cd -                 # 回到上次目录
cd /var/log          # 切换到日志目录
```

**pwd — 显示当前路径（Shell 内置）**

```
├── 语法：pwd [选项]
├── 核心参数：
│   ├── -P           显示物理路径（解析符号链接）
│   └── -L           显示逻辑路径（默认）
├── 调用案例：
│   ├── pwd
│   └── pwd -P
├── 适用场景：确认当前工作目录
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
pwd                  # /home/user/projects
pwd -P               # 解析符号链接后的真实路径
```

**tree — 树形显示目录结构**

```
├── 语法：tree [选项] [路径]
├── 核心参数：
│   ├── -L n         只显示 n 层深度
│   ├── -d           只显示目录
│   ├── -a           显示隐藏文件
│   ├── -f           显示完整路径前缀
│   ├── -p           显示权限
│   ├── -u           显示所有者
│   └── -h           显示文件大小
├── 调用案例：
│   ├── tree -L 2 /etc
│   └── tree -d /var/log
├── 适用场景：可视化目录结构
└── 风险等级：★☆☆☆☆（低风险）
```

> **安装**：`sudo apt install tree`（Ubuntu/Debian）| `sudo dnf install tree`（Fedora/CentOS）

```bash
tree -L 2 /etc/ssh           # 显示 /etc/ssh 两层结构
tree -d /var/log              # 只显示目录
tree -a -L 1 ~                # 显示主目录全部内容（含隐藏）
tree -p /etc/nginx            # 带权限显示
```

#### 创建与删除

**mkdir — 创建目录**

```
├── 语法：mkdir [选项] 目录...
├── 核心参数：
│   ├── -p           递归创建（父目录不存在时自动创建）
│   ├── -m MODE      创建时指定权限
│   └── -v           显示创建过程
├── 调用案例：
│   ├── mkdir mydir
│   ├── mkdir -p a/b/c/d
│   └── mkdir -m 700 privatedir
├── 适用场景：创建目录结构
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
mkdir mydir                    # 创建单个目录
mkdir -p a/b/c/d               # 创建多级目录
mkdir -m 700 privatedir       # 创建时指定权限
mkdir dir1 dir2 dir3           # 同时创建多个目录
mkdir -v project/{src,doc,bin}  # 花括号展开（Bash 特性）
```

**rmdir — 删除空目录**

```
├── 语法：rmdir [选项] 目录...
├── 核心参数：
│   ├── -p           递归删除多级空目录
│   └── -v           显示删除过程
├── 调用案例：
│   ├── rmdir emptydir
│   └── rmdir -p a/b/c/d
├── 适用场景：删除空目录（非空目录需用 rm -r）
└── 风险等级：★☆☆☆☆（低风险，只删空目录）
```

```bash
rmdir emptydir                 # 删除空目录
rmdir -p a/b/c/d               # 递归删除多级空目录
```

**touch — 创建空文件/修改时间戳**

```
├── 语法：touch [选项] 文件...
├── 核心参数：
│   ├── -a           只修改访问时间
│   ├── -m           只修改修改时间
│   ├── -t STAMP     使用指定时间（[[CC]YY]MMDDhhmm[.ss]）
│   ├── -d STRING    使用字符串指定时间
│   └── -r FILE      参照另一文件的时间
├── 调用案例：
│   ├── touch newfile.txt
│   └── touch -t 202601010000 old.txt
├── 适用场景：创建空文件、修改文件时间戳
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
touch newfile.txt              # 创建空文件（或更新已有文件时间戳）
touch file1 file2 file3       # 创建多个文件
touch -t 202601010000.00 file.txt  # 设置指定时间
touch -r ref.txt target.txt   # 参照 ref.txt 的时间
```

**rm — 删除文件/目录**

```
├── 语法：rm [选项] 文件/目录...
├── 核心参数：
│   ├── -f           强制删除，不提示确认
│   ├── -r / -R      递归删除目录及其内容
│   ├── -i           删除前逐一确认
│   ├── -I           删除超过 3 个文件或递归删除时确认一次
│   ├── -d           删除空目录
│   ├── --preserve-root   保护根目录（默认，/ 处拒绝）
│   └── --no-preserve-root  不保护根目录（极度危险！）
├── 调用案例：
│   ├── 基础用法：rm file.txt
│   ├── 组合用法：rm -rf /tmp/test
│   └── 安全用法：rm -ri /old_data
├── 适用场景：删除不需要的文件和目录
└── 风险等级：★★★★★（高风险，特别是 -rf 选项）
    ⚠️ 警告：rm -rf 不可逆！删除前确认路径。
    ⚠️ 绝对不要执行 rm -rf / 或 rm -rf /*。
    ⚠️ 使用 -i 或 -I 增加确认环节。
    回滚方案：无直接回滚。建议使用 trash-cli 替代或先 tar 备份。
```

```bash
rm file.txt                    # 删除单个文件
rm -i important.conf           # 删除前确认
rm -rf /tmp/old_build/         # 递归删除目录（确认路径！）
rm -ri /old_data/              # 递归删除，逐一确认（安全）
rm -- -filename                # 删除以 - 开头的文件

# 安全替代方案：安装 trash-cli
# sudo apt install trash-cli   # Ubuntu/Debian
# trash-put file.txt            # 移入回收站而非直接删除
```

> **风险警告**：`rm -rf` 删除的数据无法通过常规手段恢复。在生产环境中，建议先 `ls` 确认路径再 `rm`，或使用 `mv` 移到临时目录待确认后删除。

#### 复制与移动

**cp — 复制文件/目录**

```
├── 语法：cp [选项] 源 目标  |  cp [选项] 源... 目录
├── 核心参数：
│   ├── -r / -R      递归复制目录
│   ├── -a           归档模式（= -dR --preserve=all）
│   ├── -p           保留权限/所有者/时间戳
│   ├── -i           覆盖前确认
│   ├── -v           显示复制过程
│   ├── -u           仅复制比目标更新的文件（增量更新）
│   ├── -l           创建硬链接而非复制
│   ├── -s           创建符号链接而非复制
│   └── --backup     覆盖前创建备份
├── 调用案例：
│   ├── cp file.txt /backup/
│   ├── cp -a /etc/nginx /backup/nginx
│   └── cp -uv src/ /dest/
├── 适用场景：备份、分发、增量复制
└── 风险等级：★★☆☆☆（中低风险）
    ⚠️ 覆盖目标文件前不加 -i 可能丢失原有文件。
```

```bash
cp file.txt /tmp/                  # 复制文件到目录
cp -r project/ /backup/            # 递归复制目录
cp -a /etc/nginx /backup/nginx     # 归档模式（保留所有属性）
cp -i file.txt existing.txt        # 覆盖前确认
cp -uv src/*.py /dest/             # 仅复制更新的文件（增量备份）
cp --backup=numbered file.txt dest.txt  # 覆盖前创建编号备份
```

**mv — 移动/重命名**

```
├── 语法：mv [选项] 源 目标  |  mv [选项] 源... 目录
├── 核心参数：
│   ├── -i           覆盖前确认
│   ├── -f           强制覆盖
│   ├── -n           不覆盖已存在文件
│   ├── -u           仅移动比目标更新的文件
│   └── -v           显示移动过程
├── 调用案例：
│   ├── mv old.txt new.txt
│   └── mv file.txt /tmp/
├── 适用场景：重命名、移动文件、批量整理
└── 风险等级：★★☆☆☆（中低风险）
    ⚠️ 同分区 mv 是原子操作；跨分区 mv 等同 cp + rm。
```

```bash
mv old.txt new.txt               # 重命名
mv file.txt /tmp/                # 移动文件到 /tmp
mv -i file.txt existing.txt     # 覆盖前确认
mv -u src/*.log /archive/       # 仅移动更新的日志文件
mv dir1/ /target/                # 移动整个目录
```

**ln — 创建链接**

```
├── 语法：ln [选项] 目标 链接名
├── 核心参数：
│   ├── -s           创建符号链接（软链接）
│   ├── -f           强制删除已有链接
│   ├── -i           交互确认
│   ├── -n           将符号链接到目录视为普通文件
│   └── -v           显示创建过程
├── 调用案例：
│   ├── ln -s /var/log /loglink
│   └── ln file.txt hardlink.txt
├── 适用场景：创建快捷方式、版本固定
└── 风险等级：★★☆☆☆（中低风险）
```

| 特性 | 硬链接（Hard Link） | 符号链接（Symbolic Link / Soft Link） |
|------|---------------------|--------------------------------------|
| 命令 | `ln target name` | `ln -s target name` |
| inode | 相同 inode | 不同 inode |
| 跨文件系统 | 不支持 | 支持 |
| 链接目录 | 不支持 | 支持 |
| 原文件删除 | 数据仍在（引用计数减 1） | 链接失效（悬空链接） |

```bash
# 符号链接（最常用）
ln -s /var/log /loglink              # 创建指向 /var/log 的符号链接
ln -sf /opt/nginx/sbin/nginx /usr/local/bin/  # 强制重建链接

# 硬链接
ln file.txt hardlink.txt              # 创建硬链接（同分区）
```

#### 查找与搜索

**find — 查找文件**

```
├── 语法：find [路径] [表达式]
├── 核心参数：
│   ├── -name PATTERN     按文件名匹配（支持通配符）
│   ├── -iname PATTERN    忽略大小写
│   ├── -type f/d/l       按类型（文件/目录/链接）
│   ├── -size +Nc         按大小（+大于 / -小于 / 无=等于）
│   ├── -mtime -N         N 天内修改过
│   ├── -mtime +N         N 天前修改过
│   ├── -user NAME        按所有者
│   ├── -perm MODE        按权限
│   ├── -maxdepth N       最大搜索深度
│   ├── -exec CMD {} \;   对结果执行命令
│   └── -delete           删除匹配的文件
├── 调用案例：
│   ├── find /etc -name "*.conf" -type f
│   ├── find /var/log -mtime +30 -delete
│   └── find . -size +100M
├── 适用场景：按条件查找文件、批量处理、清理旧文件
└── 风险等级：★★★☆☆（中风险，特别是 -delete 和 -exec）
    ⚠️ -delete 和 -exec rm 慎用，先用 -print 确认。
```

```bash
# 按名称查找
find /etc -name "*.conf" -type f           # 查找所有 .conf 文件
find /home -iname "*.PDF"                  # 忽略大小写

# 按时间查找
find /var/log -mtime +30 -type f           # 30 天前修改的文件
find /var/log -mtime -1 -type f            # 1 天内修改的文件

# 按大小查找
find / -size +100M -type f 2>/dev/null     # 大于 100MB 的文件
find / -size +1G -type f 2>/dev/null       # 大于 1GB 的文件

# 按权限查找（安全审计）
find / -perm -4000 -type f 2>/dev/null     # 查找 SUID 文件
find / -perm -2000 -type f 2>/dev/null     # 查找 SGID 文件

# 批量执行
find /tmp -name "*.tmp" -mtime +7 -delete  # 删除 7 天前的 .tmp 文件
# 安全做法：先 print 确认，再 delete
find /tmp -name "*.tmp" -mtime +7 -print   # 先查看
find /tmp -name "*.tmp" -mtime +7 -delete  # 确认后删除

# 批量修改权限
find /var/www -name "*.php" -exec chmod 644 {} \;
```

**locate — 快速查找（基于数据库）**

```
├── 语法：locate [选项] 模式
├── 核心参数：
│   ├── -i           忽略大小写
│   ├── -r          使用正则表达式
│   ├── -c          只输出匹配数量
│   └── -d DB       指定数据库
├── 调用案例：
│   ├── locate nginx.conf
│   └── locate -i '\.pdf$'
├── 适用场景：快速全盘搜索文件名
└── 风险等级：★☆☆☆☆（低风险）
    数据库非实时，可能滞后。更新：sudo updatedb
```

```bash
locate nginx.conf               # 查找所有名为 nginx.conf 的文件
locate -i firefox              # 忽略大小写
locate -r '\.conf$'            # 正则：以 .conf 结尾
sudo updatedb                  # 手动更新数据库
```

**which / whereis**

```
├── which：查找命令的可执行文件路径
│   ├── 语法：which [选项] 命令名
│   └── 示例：which python3
├── whereis：查找二进制/源码/手册路径
│   ├── 语法：whereis [选项] 文件名
│   └── 示例：whereis ls
├── 适用场景：确认命令安装位置、排查 PATH 问题
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
which python3                   # /usr/bin/python3
which docker                    # /usr/bin/docker 或无输出
whereis ls                      # ls: /usr/bin/ls /usr/share/man/man1/ls.1.gz
whereis -b nginx                # 只查二进制：nginx: /usr/sbin/nginx
```

#### 文件属性

**stat — 文件/文件系统详细信息**

```
├── 语法：stat [选项] 文件...
├── 核心参数：
│   ├── -f           显示文件系统状态（而非文件状态）
│   ├── -c FORMAT    自定义输出格式
│   └── -t           简洁模式
├── 调用案例：
│   ├── stat file.txt
│   └── stat -f /
├── 适用场景：查看 inode、时间戳、文件系统信息
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
stat file.txt                   # 文件详细信息（大小/inode/时间戳/权限）
stat -f /                       # 文件系统信息（块大小/总量/可用）
stat -c '%n %s %y' file.txt     # 自定义格式：文件名 大小 修改时间
```

**file — 识别文件类型**

```
├── 语法：file [选项] 文件...
├── 核心参数：
│   ├── -b           不显示文件名（简洁输出）
│   ├── -i           输出 MIME 类型
│   ├── -z           查看压缩包内文件
│   └── -L           跟随符号链接
├── 调用案例：
│   ├── file image.png
│   └── file -b unknown.dat
├── 适用场景：确认文件真实类型（不依赖扩展名）
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
file image.png                  # PNG image data, 1920 x 1080
file script.sh                  # Bourne-Again shell script
file -b unknown.dat             # ELF 64-bit LSB executable
file -i document.pdf            # application/pdf
file -z archive.tar.gz          # 查看压缩包内文件类型
```

**chattr / lsattr — 文件属性**

```
├── chattr：修改文件扩展属性
│   ├── 语法：chattr [选项] [+-=属性] 文件...
│   ├── +i          不可变（Immutable）— 不能删除/修改/重命名
│   ├── +a          只能追加（Append-only）— 只能追加内容
│   ├── -i          取消不可变
│   ├── -a          取消只能追加
│   └── -R          递归处理目录
├── lsattr：查看文件扩展属性
│   ├── 语法：lsattr [选项] 文件...
│   └── -R          递归查看
├── 调用案例：
│   ├── chattr +i /etc/resolv.conf
│   └── chattr +a /var/log/audit.log
├── 适用场景：保护关键配置文件不被修改
└── 风险等级：★★★☆☆（中风险）
    ⚠️ +i 属性使 root 也无法修改文件（除非先 chattr -i）。
    ⚠️ 需 root 权限。
    回滚方案：chattr -i file 或 chattr -a file
```

```bash
# 保护配置文件不被修改
sudo chattr +i /etc/resolv.conf        # 设置不可变
lsattr /etc/resolv.conf                # 查看属性
sudo chattr -i /etc/resolv.conf        # 取消不可变

# 日志文件仅追加
sudo chattr +a /var/log/custom.log    # 只能追加
sudo chattr -a /var/log/custom.log    # 取消追加限制
```

---

### 类别 2：文本查看与处理

#### 查看

| 命令 | 全称 | 功能 | 风险等级 |
|------|------|------|---------|
| **cat** | concatenate | 查看完整文件/拼接文件 | ★☆☆☆☆ |
| **tac** | cat 反转 | 逆向显示（最后一行在前） | ★☆☆☆☆ |
| **more** | more | 分页查看（只能向前） | ★☆☆☆☆ |
| **less** | less | 分页查看（可前后翻） | ★☆☆☆☆ |
| **head** | head | 显示开头 N 行 | ★☆☆☆☆ |
| **tail** | tail | 显示末尾 N 行 / 实时追踪 | ★☆☆☆☆ |
| **nl** | number lines | 显示带行号的文件 | ★☆☆☆☆ |

```bash
# cat — 查看完整文件
cat /etc/hostname                      # 查看主机名
cat -n /etc/fstab                      # 带行号显示
cat file1.txt file2.txt > merged.txt  # 拼接多个文件

# tac — 逆向显示
tac /var/log/auth.log                  # 最新日志在前

# less — 分页查看（推荐替代 cat 查看大文件）
less /var/log/syslog                   # 空格翻页，q 退出
less +F /var/log/syslog                # 类似 tail -f（Ctrl+C 退出追踪模式）

# head — 开头行
head -n 20 /var/log/syslog             # 前 20 行
head -c 1024 binary.dat                # 前 1024 字节

# tail — 末尾行 / 实时追踪
tail -n 50 /var/log/syslog             # 最后 50 行
tail -f /var/log/syslog                # 实时追踪（运维最常用）
tail -f /var/log/nginx/access.log      # 追踪 Nginx 访问日志
tail -n +2 data.csv                    # 从第 2 行开始（跳过表头）

# nl — 带行号
nl -ba /etc/passwd                     # 所有行编号
```

#### 过滤

**grep — 文本搜索**

```
├── 语法：grep [选项] 模式 [文件...]
├── 核心参数：
│   ├── -i           忽略大小写
│   ├── -v           反转匹配（输出不匹配的行）
│   ├── -r / -R      递归搜索目录
│   ├── -n           显示行号
│   ├── -c           只输出匹配行数
│   ├── -l           只输出含匹配行的文件名
│   ├── -o           只输出匹配部分
│   ├── -E           扩展正则表达式（= egrep）
│   ├── -F           固定字符串（= fgrep，不解析正则）
│   ├── -A N         匹配行后 N 行
│   ├── -B N         匹配行前 N 行
│   ├── -C N         匹配行前后各 N 行
│   ├── --color      匹配文本高亮
│   └── -e PATTERN   指定多个模式
├── 调用案例：
│   ├── 基础用法：grep "error" /var/log/syslog
│   ├── 组合用法：grep -rn "TODO" /project/
│   └── 管道用法：ps aux | grep nginx | grep -v grep
├── 适用场景：日志分析、代码搜索、文本过滤
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
# 基本搜索
grep "error" /var/log/syslog               # 搜索含 error 的行
grep -i "error" /var/log/syslog            # 忽略大小写
grep -v "#" /etc/fstab                     # 排除注释行
grep -n "root" /etc/passwd                 # 带行号

# 递归搜索
grep -rn "password" /etc/                  # 递归搜索含 password 的文件
grep -rl "192.168.1.100" /var/log/         # 只列出含匹配的文件名

# 扩展正则（ERE）
grep -E "error|warning|critical" /var/log/syslog  # 多关键词
grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" /etc/hosts  # IP 地址

# 上下文
grep -C 3 "panic" /var/log/kern.log       # 匹配行前后各 3 行

# 管道过滤
ps aux | grep nginx | grep -v grep        # 查找 nginx 进程（排除 grep 自身）
dmesg | grep -i "error\|fail\|warn"       # 内核日志中的错误

# 统计
grep -c "Failed password" /var/log/auth.log  # 统计失败登录次数

# 安全场景：查找 SUID 二进制
find / -perm -4000 -type f 2>/dev/null | xargs grep -l "system"
```

**egrep / fgrep**

```bash
# egrep = grep -E（扩展正则）
egrep "error|warning" /var/log/syslog

# fgrep = grep -F（固定字符串，不解析正则，速度快）
fgrep "192.168.1.100" /var/log/access.log
```

#### 转换与提取

**cut — 按列提取**

```
├── 语法：cut [选项] [文件...]
├── 核心参数：
│   ├── -d SEP       指定分隔符
│   ├── -f N         提取第 N 列（配合 -d）
│   ├── -c N-M       按字符位置提取
│   ├── -b N-M       按字节位置提取
│   └── --complement 补集（提取指定列之外的内容）
├── 调用案例：
│   ├── cut -d: -f1 /etc/passwd
│   └── cut -c1-10 file.txt
├── 适用场景：提取 CSV/TSV/冒号分隔文件的特定列
└── 风险等级：★☆☆☆☆（低风险）
```

```bash
cut -d: -f1 /etc/passwd                  # 提取用户名（第 1 列）
cut -d: -f1,3 /etc/passwd                # 提取第 1 和 3 列
cut -d, -f2 data.csv                     # CSV 第 2 列
cut -c1-10 /etc/hostname                 # 前 10 个字符
echo "hello" | cut -c2-4                 # ell
```

**tr — 字符转换/删除**

```
├── 语法：tr [选项] SET1 [SET2]
├── 核心参数：
│   ├── -d           删除指定字符
│   ├── -s           压缩重复字符
│   ├── -c           取补集
│   └── [:upper:]/[:lower:]  大小写字符集
├── 调用案例：
│   ├── echo "Hello" | tr 'a-z' 'A-Z'
│   └── tr -d '\r' < file.txt
├── 适用场景：大小写转换、删除字符、压缩空格
└── 风险等级：★☆☆☆☆（低风险）
    注意：tr 只能通过管道或重定向接收输入，不能直接接文件名。
```

```bash
echo "Hello World" | tr 'a-z' 'A-Z'       # HELLO WORLD
echo "Hello" | tr '[:lower:]' '[:upper:]' # HELLO
echo "aabbcc" | tr -s 'a-z'               # abc（压缩重复）
tr -d '\r' < windows.txt > unix.txt       # 删除 Windows 换行符 \r
echo "hello world" | tr ' ' '-'           # hello-world
tr -dc '[:print:]' < binary.dat           # 只保留可打印字符
```

**sed — 流编辑器**

```
├── 语法：sed [选项] '命令' [文件...]
├── 核心参数：
│   ├── -n           安静模式（只输出被处理过的行）
│   ├── -i           直接修改原文件（就地编辑）
│   ├── -i.bak       修改前创建 .bak 备份
│   ├── -E           扩展正则表达式
│   ├── -r           同 -E（旧写法）
│   └── -f FILE      从文件读取 sed 脚本
├── 常用命令：
│   ├── s/old/new/   替换（第一个匹配）
│   ├── s/old/new/g  全局替换
│   ├── s/old/new/gi 全局替换 + 忽略大小写
│   ├── p             打印（配合 -n）
│   ├── d             删除行
│   ├── a\text        在行后追加
│   ├── i\text        在行前插入
│   └── Np            处理第 N 行
├── 调用案例：
│   ├── sed 's/old/new/g' file.txt
│   ├── sed -i 's/80/8080/g' config.conf
│   └── sed -n '10,20p' file.txt
├── 适用场景：批量替换、行删除、内容提取
└── 风险等级：★★★☆☆（中风险）
    ⚠️ -i 直接修改原文件，建议先用 -i.bak 或预览（不带 -i）。
    回滚方案：使用 -i.bak 保留备份。
```

```bash
# 替换（预览模式，不修改文件）
sed 's/error/ERROR/g' /var/log/syslog         # 全局替换（仅输出）
sed 's/localhost/127.0.0.1/' config.conf       # 替换第一个匹配

# 就地编辑（建议先备份）
sed -i.bak 's/port=80/port=8080/g' app.conf    # 替换并创建 .bak 备份
sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config  # 修改 SSH 配置

# 删除行
sed '/^#/d' /etc/fstab                        # 删除注释行
sed '/^$/d' file.txt                          # 删除空行
sed '/search_pattern/d' data.txt              # 删除含匹配的行

# 提取行
sed -n '10,20p' file.txt                      # 打印第 10-20 行
sed -n '/error/p' /var/log/syslog             # 打印含 error 的行

# 插入和追加
sed '2a\new line' file.txt                    # 第 2 行后追加
sed '/^root/i\# Important' /etc/passwd         # root 行前插入

# 多命令组合
sed -e 's/foo/bar/g' -e 's/baz/qux/g' file.txt  # 多次替换
```

**awk — 模式扫描与处理语言**

```
├── 语法：awk [选项] '模式 {动作}' [文件...]
├── 核心参数：
│   ├── -F SEP       指定字段分隔符
│   ├── -v var=val   赋值变量
│   ├── -f FILE      从文件读取 awk 脚本
│   └── -O FS        指定输出分隔符
├── 内置变量：
│   ├── $0           整行
│   ├── $1/$2/...    第 N 个字段
│   ├── NF           字段数（列数）
│   ├── NR           当前行号
│   ├── FS           字段分隔符（默认空格）
│   ├── OFS          输出字段分隔符
│   └── RS           行分隔符
├── 调用案例：
│   ├── awk -F: '{print $1}' /etc/passwd
│   ├── awk '{sum+=$1} END{print sum}' data.txt
│   └── awk -F, '$3>100 {print $1,$3}' sales.csv
├── 适用场景：列提取、条件过滤、数据统计
└── 风险等级：★☆☆☆☆（低风险，只读分析）
```

```bash
# 提取列
awk -F: '{print $1}' /etc/passwd              # 提取用户名
awk -F: '{print $1, $7}' /etc/passwd          # 用户名和 Shell
awk '{print $2}' file.txt                     # 第 2 列（空格分隔）

# 条件过滤
awk -F: '$3 >= 1000 {print $1}' /etc/passwd    # UID >= 1000 的用户
awk '$3 > 100 {print $1, $3}' sales.csv       # 第 3 列 > 100 的行
awk '/error/ {print}' /var/log/syslog         # 含 error 的行

# 统计
awk '{sum += $1} END {print "Total:", sum}' data.txt   # 求和
awk '{sum += $2; count++} END {print "Avg:", sum/count}' data.txt  # 平均值
awk '{print NR, $0}' file.txt                # 加行号

# 格式化输出
awk -F: 'BEGIN{OFS=" | "} {print $1, $3, $6}' /etc/passwd  # 格式化

# 日志分析
# 统计 Nginx 访问日志中 IP 出现次数 Top 10
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```

**sort / uniq / wc**

```bash
# sort — 排序
sort file.txt                         # 按字母升序
sort -n numbers.txt                   # 按数值排序
sort -rn numbers.txt                  # 按数值降序
sort -t: -k3 -n /etc/passwd          # 以冒号分隔，按第 3 列（UID）数值排序
sort -u file.txt                     # 排序并去重

# uniq — 去重（需先排序）
sort file.txt | uniq                 # 去重
sort file.txt | uniq -c              # 去重并统计次数
sort file.txt | uniq -d              # 只显示重复行
sort access.log | uniq -c | sort -rn | head  # 统计 Top 访问

# wc — 统计
wc -l /etc/passwd                     # 行数
wc -w file.txt                        # 词数
wc -c file.txt                        # 字节数
wc -l *.py                            # 统计多个文件的行数
```

#### 比较

```bash
# diff — 比较两个文件的差异
diff file1.txt file2.txt
diff -u file1.txt file2.txt           # 统一格式（patch 用的格式）
diff -r dir1/ dir2/                   # 递归比较目录
diff -q dir1/ dir2/                   # 只报告是否不同

# vimdiff — Vim 可视化比较
vimdiff file1.txt file2.txt

# comm — 比较两个已排序文件
comm file1.txt file2.txt              # 三列：仅file1 / 仅file2 / 共有
comm -12 file1.txt file2.txt          # 只显示共有行（交集）
comm -23 file1.txt file2.txt          # 只显示 file1 独有的行（差集）
```

#### 合并

```bash
# paste — 按列合并
paste file1.txt file2.txt             # 逐行合并（Tab 分隔）
paste -d, file1.txt file2.txt         # 逗号分隔

# join — 按共同字段连接
join -t, -1 1 -2 1 file1.csv file2.csv  # 按第 1 列连接

# split — 分割文件
split -l 1000 largefile.txt part_     # 每 1000 行分割
split -b 10m largefile.bin part_      # 每 10MB 分割
split -d -l 500 data.txt part_       # 数字后缀
cat part_* > merged.txt              # 合并
```

---

### 类别 3：文件压缩与归档

| 工具 | 格式 | 压缩率 | 速度 | 常用扩展名 |
|------|------|--------|------|-----------|
| **gzip** | gzip | 中 | 快 | .gz |
| **bzip2** | bzip2 | 高 | 中 | .bz2 |
| **xz** | xz/LZMA | 最高 | 慢 | .xz |
| **zip** | zip | 中 | 快 | .zip |
| **tar** | 归档（不压缩） | — | 快 | .tar |

**tar — 归档工具（最常用）**

```
├── 语法：tar [选项] 归档文件 [文件/目录...]
├── 核心参数：
│   ├── -c           创建归档（Create）
│   ├── -x           解压归档（eXtract）
│   ├── -t           列出内容（lisT）
│   ├── -f FILE      指定归档文件名（必须放最后）
│   ├── -v           显示过程（Verbose）
│   ├── -z           使用 gzip 压缩/解压（.tar.gz / .tgz）
│   ├── -j           使用 bzip2 压缩/解压（.tar.bz2）
│   ├── -J           使用 xz 压缩/解压（.tar.xz）
│   ├── -C DIR       解压到指定目录
│   ├── -r           追加文件到归档
│   ├── -u           仅追加更新的文件
│   ├── --exclude=PATTERN  排除匹配的文件
│   └── -A           追加 tar 文件到另一个 tar
├── 调用案例：
│   ├── tar -czvf backup.tar.gz /home/user/
│   ├── tar -xzvf backup.tar.gz
│   └── tar -tzf archive.tar.gz
├── 适用场景：备份、分发、解压源码包
└── 风险等级：★★☆☆☆（中低风险）
    ⚠️ 解压到错误目录可能覆盖文件，建议先 -t 查看，再用 -C 指定目录。
```

```bash
# 创建归档
tar -cvf archive.tar /path/to/dir/              # 仅归档（不压缩）
tar -czvf backup.tar.gz /home/user/              # gzip 压缩（最常用）
tar -cjvf backup.tar.bz2 /home/user/             # bzip2 压缩（更高压缩率）
tar -cJvf backup.tar.xz /home/user/              # xz 压缩（最高压缩率）

# 排除文件
tar -czvf backup.tar.gz --exclude='*.log' /var/www/
tar -czvf backup.tar.gz --exclude='node_modules' --exclude='.git' /project/

# 查看内容（不解压）
tar -tf archive.tar                               # 列出文件
tar -tzf archive.tar.gz                           # 列出 gz 归档内容
tar -tvzf archive.tar.gz                          # 详细列表

# 解压
tar -xvf archive.tar                              # 解压 tar
tar -xzvf backup.tar.gz                           # 解压 tar.gz
tar -xjvf backup.tar.bz2                          # 解压 tar.bz2
tar -xJvf backup.tar.xz                           # 解压 tar.xz
tar -xzvf backup.tar.gz -C /opt/                  # 解压到指定目录
tar -xzvf backup.tar.gz path/to/file              # 只解压指定文件

# 追加和更新
tar -rvf archive.tar newfile.txt                  # 追加文件到 tar（仅未压缩 tar）
```

**gzip / bzip2 / xz / zip / unzip**

```bash
# gzip — 压缩/解压 .gz
gzip file.txt                          # 压缩（原文件被替换）
gzip -k file.txt                       # 压缩（保留原文件）
gzip -d file.txt.gz                    # 解压
gzip -9 file.txt                       # 最高压缩率
zcat file.txt.gz                       # 查看压缩文件内容（不解压）

# bzip2 — 压缩/解压 .bz2
bzip2 file.txt                         # 压缩
bzip2 -k file.txt                      # 保留原文件
bzip2 -d file.txt.bz2                  # 解压
bzcat file.txt.bz2                     # 查看内容

# xz — 压缩/解压 .xz
xz file.txt                            # 压缩（高压缩率）
xz -k file.txt                         # 保留原文件
xz -d file.txt.xz                      # 解压
xzcat file.txt.xz                     # 查看内容

# zip / unzip — 跨平台压缩
zip -r archive.zip /path/to/dir/       # 递归压缩目录
zip -e archive.zip file.txt            # 加密压缩
unzip archive.zip                      # 解压
unzip archive.zip -d /target/          # 解压到指定目录
unzip -l archive.zip                   # 查看内容
```

---

### 类别 4：用户与权限管理

#### 用户管理

**useradd / usermod / userdel / passwd / chage**

```
├── useradd：创建用户
│   ├── 语法：useradd [选项] 用户名
│   ├── -m           创建主目录
│   ├── -d PATH      指定主目录路径
│   ├── -s SHELL     指定登录 Shell
│   ├── -G GROUPS    附加组（逗号分隔）
│   ├── -u UID       指定 UID
│   └── -e DATE      账户过期日期
├── usermod：修改用户
│   ├── -aG GROUP    追加到附加组（-a 必须与 -G 一起用）
│   ├── -s SHELL     修改 Shell
│   ├── -L           锁定账户
│   ├── -U           解锁账户
│   └── -e DATE       设置过期日期
├── userdel：删除用户
│   ├── -r           同时删除主目录和邮件池
│   └── -f           强制删除（即使用户在线）
├── passwd：修改密码
│   ├── -l           锁定密码
│   ├── -u           解锁密码
│   ├── -e           强制下次登录改密
│   ├── -S           查看密码状态
│   └── --status     密码状态
├── chage：修改密码策略
│   ├── -M DAYS      密码最大使用天数
│   ├── -m DAYS      密码最小使用天数
│   ├── -W DAYS      密码过期前警告天数
│   ├── -I DAYS      密码过期后宽限天数
│   ├── -E DATE      账户过期日期
│   └── -l           查看密码策略
├── 适用场景：用户生命周期管理
└── 风险等级：★★★☆☆（中风险，需 root 权限）
    ⚠️ userdel -r 会删除用户主目录，无法恢复。
```

```bash
# 创建用户
sudo useradd -m -s /bin/bash newuser          # 创建用户并建主目录
sudo passwd newuser                           # 设置密码
sudo useradd -m -s /bin/bash -G sudo,docker devuser  # 创建并加入附加组

# 修改用户
sudo usermod -aG docker newuser               # 追加到 docker 组（-a 必须配合 -G）
sudo usermod -s /bin/zsh newuser              # 修改 Shell
sudo usermod -L newuser                       # 锁定账户
sudo usermod -U newuser                       # 解锁账户
sudo usermod -e 2026-12-31 tempuser           # 设置过期日期

# 查看用户信息
id newuser                                    # UID/GID/组
groups newuser                                # 所属组
chage -l newuser                              # 密码策略

# 设置密码策略
sudo chage -M 90 newuser                      # 90 天必须改密
sudo chage -m 7 newuser                       # 最短 7 天才能改密
sudo chage -W 7 newuser                       # 过期前 7 天警告
sudo chage -E 2026-12-31 tempuser             # 账户过期日期

# 删除用户
sudo userdel newuser                          # 删除用户（保留主目录）
sudo userdel -r newuser                       # 删除用户和主目录
```

#### 组管理

```bash
# 创建组
sudo groupadd developers                     # 创建组
sudo groupadd -g 2000 developers             # 指定 GID

# 修改组
sudo groupmod -n devs developers             # 重命名组
sudo groupmod -g 2001 developers            # 修改 GID

# 删除组
sudo groupdel developers

# 管理组成员
sudo gpasswd -a user group                    # 添加用户到组
sudo gpasswd -d user group                    # 从组中移除用户
sudo gpasswd -A user group                    # 设置组管理员

# 查看组
cat /etc/group                                # 查看所有组
getent group docker                           # 查看 docker 组成员
```

#### 权限修改

**chmod — 修改权限**

```
├── 语法：chmod [选项] MODE 文件...
├── 核心参数：
│   ├── -R           递归修改
│   ├── -v           显示修改过程
│   ├── -c           只显示有变化的
│   └── --reference=FILE  参照另一文件的权限
├── 权限模式：
│   ├── 符号模式：u/g/o/a +-= r/w/x
│   └── 数字模式：3 位八进制（属主/组/其他）
├── 调用案例：
│   ├── chmod 755 script.sh
│   ├── chmod -R 644 /var/www/
│   └── chmod u+x,g-w file.txt
├── 适用场景：文件权限管理
└── 风险等级：★★★☆☆（中风险）
    ⚠️ chmod -R 777 / 是极度危险操作，会让所有文件可读写执行。
    ⚠️ 对系统关键目录（/etc, /usr/bin）修改权限可能导致系统不可用。
    回滚方案：使用 --reference=恢复参照，或从备份恢复。
```

| 数字 | 权限 | 符号 | 说明 |
|------|------|------|------|
| 7 | rwx | rwx | 读+写+执行 |
| 6 | rw- | rw- | 读+写 |
| 5 | r-x | r-x | 读+执行 |
| 4 | r-- | r-- | 只读 |
| 0 | --- | --- | 无权限 |

```bash
# 数字模式
chmod 755 script.sh                      # rwxr-xr-x
chmod 644 config.conf                    # rw-r--r--
chmod 600 id_rsa                         # rw-------（SSH 私钥）
chmod 700 ~/.ssh                         # rwx------（SSH 目录）

# 符号模式
chmod u+x script.sh                      # 属主加执行权限
chmod g-w file.txt                       # 组去掉写权限
chmod o-r file.txt                       # 其他去掉读权限
chmod a+r file.txt                       # 所有加读权限
chmod ugo=r file.txt                     # 所有设为只读

# 递归
chmod -R 755 /var/www/html/              # 递归修改目录权限
# 分别设置目录和文件权限（Web 服务器最佳实践）
find /var/www -type d -exec chmod 755 {} \;   # 目录 755
find /var/www -type f -exec chmod 644 {} \;   # 文件 644

# 特殊权限
chmod 4755 /usr/bin/passwd              # SUID（4= SUID + 755）
chmod 2755 /shared                      # SGID（2= SGID + 755）
chmod 1777 /tmp                         # Sticky Bit（1= Sticky + 777）
```

**特殊权限详解**

| 特殊权限 | 符号 | 数字前缀 | 作用 | 典型示例 |
|----------|------|----------|------|----------|
| SUID | `u+s` | 4 | 以文件所有者身份执行 | `/usr/bin/passwd`（4755） |
| SGID | `g+s` | 2 | 以组所有者身份执行；目录下新文件继承组 | 共享目录（2770） |
| Sticky Bit | `+t` | 1 | 目录下只有所有者能删除自己的文件 | `/tmp`（1777） |

```bash
# 查找 SUID/SGID 文件（安全审计）
find / -perm -4000 -type f 2>/dev/null     # SUID 文件
find / -perm -2000 -type f 2>/dev/null     # SGID 文件

# 设置共享目录（组协作）
sudo chmod 2770 /shared/project           # SGID + rwxrws---
sudo chown root:developers /shared/project
# 此后 /shared/project 下新建文件自动属于 developers 组
```

**chown — 修改所有者**

```
├── 语法：chown [选项] [所有者][:[组]] 文件...
├── 核心参数：
│   ├── -R           递归修改
│   ├── -v           显示过程
│   ├── -h           修改符号链接本身（不跟随）
│   └── --reference=FILE  参照另一文件
├── 调用案例：
│   ├── chown user:group file
│   ├── chown -R www-data:www-data /var/www/
│   └── chown user file
├── 适用场景：修改文件所有者和组
└── 风险等级：★★★☆☆（中风险，需 root 权限）
```

```bash
sudo chown newuser file.txt               # 修改所有者
sudo chown newuser:developers file.txt    # 修改所有者和组
sudo chown :developers file.txt           # 只修改组
sudo chown -R www-data:www-data /var/www/ # 递归修改 Web 目录
sudo chown --reference=ref.txt target.txt  # 参照 ref.txt 的属主属组
```

**umask — 默认权限掩码**

```bash
umask                          # 查看当前 umask（如 0022）
umask 022                      # 设置 umask（文件默认 644，目录默认 755）
umask 077                      # 更安全（文件默认 600，目录默认 700）

# 计算规则：默认权限 = 基础权限 - umask
# 文件基础：666 → 666 - 022 = 644（rw-r--r--）
# 目录基础：777 → 777 - 022 = 755（rwxr-xr-x）

# 永久设置（写入 ~/.bashrc 或 /etc/profile）
echo 'umask 027' >> ~/.bashrc   # 文件 640，目录 750
```

#### ACL

```bash
# 查看文件 ACL
getfacl file.txt                       # 查看文件的 ACL
getfacl /var/www                      # 查看目录的 ACL

# 设置 ACL
setfacl -m u:newuser:rwx /shared/     # 给 newuser 读写执行权限
setfacl -m g:developers:rw /shared/   # 给 developers 组读写权限
setfacl -m u:guest:r-- /shared/       # 给 guest 只读
setfacl -x u:guest /shared/           # 移除 guest 的 ACL 条目
setfacl -b /shared/                    # 移除所有 ACL
setfacl -R -m u:newuser:rwx /shared/  # 递归设置

# ACL 与普通权限的区别
# 普通权限只有三组（属主/组/其他）
# ACL 可以为任意用户/组单独设置权限
```

> **ACL 前提**：文件系统需挂载时支持 ACL（`mount -o acl`），现代文件系统（ext4/xfs）默认支持。

#### 切换身份

```bash
# su — 切换用户
su -                      # 切换到 root（加载环境变量）
su - newuser              # 切换到 newuser
su -c "command" newuser   # 以 newuser 执行命令

# sudo — 以管理员执行
sudo command              # 以 root 执行
sudo -u newuser command   # 以 newuser 执行
sudo -k                  # 重置 sudo 密码缓存
sudo -l                  # 查看当前用户的 sudo 权限
sudo -i                  # 进入 root 交互式 Shell
sudo -E command           # 保留当前环境变量
```

> **sudo 配置**：`sudo visudo` 编辑 /etc/sudoers（必须用 visudo 以防语法错误锁死 sudo）。

---

### 类别 5：进程与作业控制

#### 查看

**ps — 进程快照**

```
├── 语法：ps [选项]
├── 核心参数：
│   ├── aux            查看所有进程（BSD 风格，最常用）
│   ├── -ef            查看所有进程（System V 风格，显示 PPID）
│   ├── -e             所有进程
│   ├── -f             完整格式
│   ├── -u USER        指定用户进程
│   ├── -p PID         指定 PID
│   ├── --sort         排序
│   └── -o FORMAT      自定义输出列
├── 调用案例：
│   ├── ps aux
│   ├── ps -ef | grep nginx
│   └── ps aux --sort=-%mem | head
├── 适用场景：查看进程状态、资源占用
└── 风险等级：★☆☆☆☆（低风险，只读）
```

```bash
ps aux                           # 所有进程（BSD 风格）
ps -ef                           # 所有进程（System V 风格）
ps aux | grep nginx              # 查找 nginx 进程
ps -u www-data                   # www-data 用户的进程
ps -p 1234                       # PID 为 1234 的进程
ps aux --sort=-%cpu | head -11  # CPU 占用 Top 10
ps aux --sort=-%mem | head -11  # 内存占用 Top 10
ps -eo pid,ppid,user,%cpu,%mem,cmd --sort=-%cpu | head -11  # 自定义列

# 常用列含义
# USER  PID  %CPU  %MEM   VSZ   RSS  TTY  STAT  START  TIME  COMMAND
```

**top / htop — 实时监控**

```bash
# top — 系统资源实时监控
top                              # 交互式监控
top -d 2                         # 每 2 秒刷新
top -p 1234                      # 只监控 PID 1234
top -u www-data                  # 只监控 www-data 用户
# top 交互命令：
#   P   按 CPU 排序
#   M   按内存排序
#   T   按时间排序
#   k   杀死进程
#   1   显示各 CPU 核心
#   q   退出

# htop — 增强版 top（彩色/鼠标/树形）
sudo apt install htop            # Ubuntu/Debian
sudo dnf install htop            # Fedora/CentOS
htop                             # 启动
# htop 交互：
#   F5  树形显示
#   F6  排序
#   F9  发送信号
#   /   搜索
```

**pstree — 进程树**

```bash
pstree                          # 树形显示所有进程
pstree -p                       # 显示 PID
pstree -u                       # 显示用户
pstree -a                       # 显示命令行参数
pstree -p 1                     # 以 PID 1 为根的进程树
```

#### 控制

**kill / killall / pkill**

```
├── kill：按 PID 发送信号
│   ├── 语法：kill [选项] PID...
│   ├── -l           列出所有信号
│   ├── -SIGNAL      指定信号（数字或名称）
│   └── 默认         SIGTERM (15)
├── killall：按进程名发送信号
│   ├── 语法：killall [选项] 进程名
│   ├── -u USER      指定用户
│   ├── -e           精确匹配
│   └── -I           忽略大小写
├── pkill：按模式发送信号
│   ├── 语法：pkill [选项] 模式
│   ├── -u USER      指定用户
│   ├── -t TTY       指定终端
│   └── -f           匹配完整命令行
├── 适用场景：终止进程、重载配置
└── 风险等级：★★★☆☆（中风险）
    ⚠️ kill -9 是强杀，进程无法清理资源，可能导致数据损坏。
    ⚠️ kill -9 -1 杀死所有可杀进程，极度危险！
    回滚方案：无。应优先使用 SIGTERM (15)，最后才用 SIGKILL (9)。
```

| 信号 | 名称 | 编号 | 含义 | 安全度 |
|------|------|------|------|--------|
| SIGHUP | Hangup | 1 | 挂起/重载配置 | ★★★★☆ |
| SIGINT | Interrupt | 2 | 中断（= Ctrl+C） | ★★★★☆ |
| SIGQUIT | Quit | 3 | 退出（+ core dump） | ★★★☆☆ |
| SIGTERM | Terminate | 15 | 优雅终止（默认） | ★★★★★ |
| SIGKILL | Kill | 9 | 强制终止 | ★☆☆☆☆ |
| SIGSTOP | Stop | 19 | 暂停（不可捕获） | ★★★☆☆ |
| SIGCONT | Continue | 18 | 继续 | ★★★★☆ |
| SIGUSR1 | User1 | 10 | 自定义（如重载日志） | ★★★☆☆ |
| SIGUSR2 | User2 | 12 | 自定义 | ★★★☆☆ |

```bash
# 列出所有信号
kill -l

# 优雅终止（推荐）
kill 1234                        # SIGTERM（默认，进程可清理后退出）
kill -15 1234                    # 同上

# 强制终止（最后手段）
kill -9 1234                     # SIGKILL（立即终止，不可捕获）

# 重载配置
kill -HUP $(pidof nginx)         # SIGHUP（nginx 重载配置）

# 按进程名终止
killall nginx                    # 终止所有名为 nginx 的进程
killall -u olduser               # 终止 olduser 的所有进程
killall -9 stale_process         # 强杀

# 按模式终止
pkill -f "python.*script.py"     # 终止匹配的进程
pkill -u www-data                # 终止 www-data 的所有进程
pkill -t pts/0                  # 终止 pts/0 终端的进程
```

**nice / renice — 进程优先级**

```bash
# nice — 启动时设置优先级
# 优先级范围：-20（最高）到 19（最低），默认 0
# 普通用户只能调高 nice 值（降低优先级），root 可调低
nice -n 10 backup.sh                    # 以 nice 10 启动（低优先级）
nice -n -5 make -j4                     # 以 nice -5 启动（高优先级，需 root）
nice -n 19 tar -czf backup.tar.gz /data/  # 最低优先级运行备份

# renice — 修改运行中进程的优先级
renice 5 -p 1234                        # PID 1234 的 nice 改为 5
renice -5 -p 1234                       # 提高优先级（需 root）
renice 10 -u www-data                   # www-data 所有进程 nice+10
```

#### 作业

```bash
# 前台/后台切换
command &                    # 后台运行
Ctrl+Z                       # 挂起到后台（SIGTSTP）
jobs                         # 查看后台作业
jobs -l                      # 含 PID
bg                           # 让挂起的作业在后台继续
bg %2                        # 指定作业号
fg                           # 将后台作业拉到前台
fg %1                        # 指定作业号

# nohup — 脱离终端运行
nohup command &              # 终端关闭后仍运行
nohup ./long_task.sh > output.log 2>&1 &  # 输出重定向

# disown — 从 Shell 作业表移除
disown %1                    # 从作业表移除（不发送 SIGHUP）
disown -a                    # 移除所有作业
disown -h %1                  # 标记为不接收 SIGHUP
```

```bash
# 综合示例：长时间任务管理
# 1. 启动后台任务
nohup rsync -av /data/ /backup/ > rsync.log 2>&1 &

# 2. 查看任务
jobs -l

# 3. 监控进度
tail -f rsync.log

# 4. 如果需要在前台查看
fg %1
```

---

### 类别 6：系统信息与监控

#### 系统信息

```bash
# uname — 内核信息
uname -a                       # 全部信息
uname -r                       # 内核版本
uname -m                       # 机器架构（x86_64）

# hostname — 主机名
hostname                       # 查看主机名
hostname newname               # 临时修改（重启失效）
hostnamectl set-hostname newname  # 永久修改（systemd）

# uptime — 运行时间与负载
uptime                         # 运行时间 + 用户数 + 平均负载
uptime -p                      # 仅显示运行时间
# 平均负载含义：1/5/15 分钟的平均运行队列长度
# 单核 CPU：1.0 = 满载；>1.0 = 过载
# 多核 CPU：满载值 = 核心数（如 4 核 = 4.0）

# date — 时间
date                           # 当前日期时间
date +%Y-%m-%d                 # 格式化日期
date +%H:%M:%S                 # 格式化时间
date -s "2026-09-24 10:00:00"  # 设置时间（需 root）
timedatectl                    # 时区管理（systemd）
timedatectl set-timezone Asia/Shanghai  # 设置时区

# cal — 日历
cal                            # 当月日历
cal 2026                       # 2026 全年
cal 9 2026                     # 2026 年 9 月
```

#### 磁盘

```bash
# df — 磁盘使用情况
df -h                          # 人类可读
df -h /                        # 查看根分区
df -i                          # inode 使用情况
df -T                          # 显示文件系统类型

# du — 目录大小
du -sh /var/log                # 查看目录总大小
du -sh *                       # 当前目录各项大小
du -h --max-depth=1 /var/      # 一层深度
du -sh /var/* | sort -rh | head -10  # 最大的 10 个子目录

# lsblk — 块设备
lsblk                          # 列出块设备
lsblk -f                       # 含文件系统
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT  # 自定义列

# fdisk — 分区管理
sudo fdisk -l                  # 列出所有磁盘和分区
sudo fdisk /dev/sdb            # 交互式分区（高风险！）

# blkid — 设备标识
sudo blkid                     # 查看 UUID 和文件系统类型
```

> **风险警告**：`fdisk`、`parted` 等分区操作是高风险操作，操作前务必备份重要数据。生产环境请在维护窗口操作。

#### 内存与性能

```bash
# free — 内存使用
free -h                        # 人类可读
free -m                        # MB 为单位
free -g                        # GB 为单位
free -s 2                      # 每 2 秒刷新

# vmstat — 虚拟内存统计
vmstat                         # 一次
vmstat 2 5                     # 每 2 秒，共 5 次
vmstat -w                      # 宽输出
# 关键列：r（运行队列）、si/so（交换）、bi/bo（I/O）、us/sy（CPU）

# iostat — I/O 统计（需 sysstat 包）
iostat                         # CPU + 磁盘 I/O
iostat -x 2                    # 扩展信息，每 2 秒
iostat -d sda 2                # 只看 sda

# sar — 历史性能数据（需 sysstat 包）
sar -u                         # CPU 使用率
sar -r                         # 内存
sar -d                         # 磁盘 I/O
sar -n DEV                     # 网络流量
sar -f /var/log/sa/sa24        # 查看某天数据

# mpstat — 多核 CPU
mpstat -P ALL 2                # 所有核心，每 2 秒
```

#### 日志

```bash
# dmesg — 内核环形缓冲区日志
dmesg                          # 内核日志
dmesg -T                       # 带时间戳
dmesg --level=err,warn         # 只看错误和警告
dmesg | grep -i "usb\|sata\|eth"

# journalctl — systemd 日志（见类别 9 详解）
journalctl                     # 所有日志
journalctl -u nginx            # 指定服务
journalctl --since today       # 今日日志
journalctl -p err              # 错误级别
journalctl -f                  # 实时追踪
```

---

### 类别 7：网络工具

#### 网络接口

**ip — 网络配置（iproute2，推荐）**

```
├── 语法：ip [选项] 对象 命令
├── 核心对象：
│   ├── addr          地址管理
│   ├── link          链路/网卡
│   ├── route         路由表
│   ├── neigh         ARP 缓存
│   ├── rule          策略路由
│   └── tunnel       隧道
├── 调用案例：
│   ├── ip addr show
│   ├── ip route show
│   └── ip link set eth0 up
├── 适用场景：网络配置与诊断
└── 风险等级：★★★☆☆（中风险）
    ⚠️ 修改 IP 配置可能导致远程连接断开！
    ⚠️ 需 root 权限修改配置。
    回滚方案：记录原配置，或通过物理终端恢复。
```

```bash
# 查看地址
ip addr show                       # 查看所有接口地址
ip addr show eth0                  # 查看 eth0
ip -br addr                        # 简洁模式
ip -4 addr                         # 只看 IPv4
ip -6 addr                         # 只看 IPv6

# 配置地址（临时，重启失效）
sudo ip addr add 192.168.1.100/24 dev eth0     # 添加 IP
sudo ip addr del 192.168.1.100/24 dev eth0     # 删除 IP

# 链路管理
ip link show                       # 查看所有网卡
ip link set eth0 up                # 启用网卡
ip link set eth0 down              # 禁用网卡
ip link set eth0 mtu 1500          # 设置 MTU

# 路由
ip route show                       # 查看路由表
ip route get 8.8.8.8               # 查看到 8.8.8.8 的路由
sudo ip route add 10.0.0.0/24 via 192.168.1.1  # 添加静态路由
sudo ip route del 10.0.0.0/24      # 删除路由
sudo ip route add default via 192.168.1.1      # 设置默认网关

# ARP 缓存
ip neigh show                      # 查看 ARP 缓存
sudo ip neigh flush all            # 清空 ARP 缓存

# 永久配置（根据发行版）
# Ubuntu/Debian: /etc/netplan/*.yaml (netplan)
# CentOS/RHEL 8+: nmcli 或 /etc/sysconfig/network-scripts/
# CentOS/RHEL 9+: NetworkManager (nmcli)
```

**ifconfig / ethtool**

```bash
# ifconfig — 已过时（被 ip 替代），部分老系统仍有
ifconfig                          # 查看所有接口
ifconfig eth0                     # 查看 eth0
sudo ifconfig eth0 192.168.1.100 netmask 255.255.255.0  # 临时设 IP

# ethtool — 网卡硬件信息
sudo ethtool eth0                 # 网卡信息（速率/双工/驱动）
sudo ethtool -i eth0              # 驱动信息
sudo ethtool -S eth0              # 统计信息（错误包等）
sudo ethtool -s eth0 speed 1000 duplex full autoneg off  # 设置速率（高风险！可能断连）
```

#### 连通性

```bash
# ping — ICMP 连通性测试
ping 8.8.8.8                      # 持续 ping
ping -c 4 8.8.8.8                 # 发 4 个包后停止
ping -i 0.5 8.8.8.8               # 每 0.5 秒发一次（需 root 改频率）
ping -s 1000 -c 3 8.8.8.8         # 指定包大小
ping6 2001:4860:4860::8888        # IPv6

# traceroute — 路径追踪
traceroute 8.8.8.8                # 追踪路由路径
traceroute -n 8.8.8.8             # 不解析域名（快）
traceroute -T -p 443 8.8.8.8      # TCP 方式（穿防火墙）
traceroute6 2001:4860:4860::8888  # IPv6

# mtr — 综合 ping + traceroute（推荐）
sudo apt install mtr              # Ubuntu/Debian
mtr 8.8.8.8                       # 交互式路径诊断
mtr -n 8.8.8.8                    # 不解析域名
mtr -r -c 10 8.8.8.8              # 报告模式，10 次

# tracepath — 路径 MTU 发现
tracepath 8.8.8.8                 # 发现路径 MTU
tracepath -n 8.8.8.8
```

#### 连接查看

**ss — Socket 统计（推荐，替代 netstat）**

```
├── 语法：ss [选项]
├── 核心参数：
│   ├── -t           TCP 连接
│   ├── -u           UDP 连接
│   ├── -l           监听状态
│   ├── -n           不解析端口名（数字）
│   ├── -p           显示进程
│   ├── -a           所有状态
│   ├── -e           扩展信息
│   ├── -m           内存使用
│   ├── -i           TCP 内部信息
│   └── -4 / -6      IPv4 / IPv6
├── 调用案例：
│   ├── ss -tlnp
│   ├── ss -tnp | grep :80
│   └── ss -s
├── 适用场景：端口/连接排查、安全审计
└── 风险等级：★☆☆☆☆（低风险，只读）
```

```bash
ss -tlnp                          # 所有 TCP 监听端口 + 进程
ss -ulnp                          # 所有 UDP 监听端口 + 进程
ss -tnp                           # 所有 TCP 连接 + 进程
ss -tn state ESTABLISHED          # 已建立的连接
ss -tnp | grep :80                # 查看端口 80 的连接
ss -tlnp | grep nginx             # 查看 nginx 监听的端口
ss -s                             # 连接统计摘要
ss -tn state TIME-WAIT            # TIME-WAIT 状态连接（排查连接泄漏）
ss -tn src 192.168.1.0/24        # 来自指定网段的连接

# netstat — 已过时（被 ss 替代），老系统仍有
netstat -tlnp                     # TCP 监听
netstat -an | grep :80            # 端口 80 连接
netstat -rn                       # 路由表（= ip route）
netstat -i                        # 接口统计
```

#### 数据传输

**curl — HTTP/FTP/API 工具**

```
├── 语法：curl [选项] URL
├── 核心参数：
│   ├── -o FILE         输出到文件
│   ├── -O              用远程文件名保存
│   ├── -L              跟随重定向
│   ├── -I              只获取 HTTP 头
│   ├── -X METHOD       指定 HTTP 方法
│   ├── -d DATA         POST 数据
│   ├── -H HEADER       添加请求头
│   ├── -u USER:PASS    认证
│   ├── -k              跳过 TLS 证书验证
│   ├── -s              安静模式
│   ├── -v              详细输出
│   ├── -w FORMAT       输出格式
│   ├── --connect-timeout SEC  连接超时
│   └── -x PROXY        代理
├── 调用案例：
│   ├── curl -O https://example.com/file.zip
│   ├── curl -X POST -d '{"key":"value"}' -H "Content-Type: application/json" https://api.example.com
│   └── curl -I https://example.com
├── 适用场景：下载、API 测试、调试 HTTP
└── 风险等级：★☆☆☆☆（低风险）
    ⚠️ -k 跳过证书验证存在中间人风险，仅用于调试。
```

```bash
# 基础
curl https://example.com                    # 获取网页内容
curl -o page.html https://example.com       # 保存到文件
curl -O https://example.com/file.zip        # 用远程文件名保存
curl -L https://short.url/abc              # 跟随重定向

# HTTP 方法
curl -X POST https://api.example.com/users  # POST 请求
curl -X DELETE https://api.example.com/users/1  # DELETE 请求
curl -X PUT -d '{"name":"test"}' -H "Content-Type: application/json" https://api.example.com/users/1

# API 调试
curl -H "Authorization: Bearer TOKEN" https://api.example.com/data
curl -d "username=admin&password=secret" https://example.com/login  # 表单 POST
curl -d '{"key":"value"}' -H "Content-Type: application/json" https://api.example.com  # JSON POST

# 下载
curl -L -o go.tar.gz https://go.dev/dl/go1.23.0.linux-amd64.tar.gz  # 下载文件
curl -C - -o file.zip https://example.com/file.zip    # 断点续传
curl --limit-rate 1M -O https://example.com/large.iso  # 限速下载

# 调试
curl -v https://example.com                  # 详细输出（请求/响应头）
curl -I https://example.com                  # 只看响应头
curl -w "%{http_code} %{time_total}s\n" -o /dev/null -s https://example.com  # 只看状态码和时间

# 认证
curl -u admin:password https://example.com/protected  # Basic 认证
curl -k https://self-signed.example.com     # 跳过证书验证（仅调试用）
```

**wget — 下载工具**

```bash
wget https://example.com/file.zip             # 下载文件
wget -c https://example.com/file.zip          # 断点续传
wget -O newname.zip https://example.com/file.zip  # 指定保存名
wget -m https://example.com/                  # 镜像网站
wget -r -l 2 -A pdf https://example.com/      # 递归下载 PDF
wget --limit-rate=1M https://example.com/file.iso  # 限速
wget -q https://example.com/file.zip          # 安静模式
```

**scp / rsync — 远程复制**

```bash
# scp — 安全复制
scp file.txt user@remote:/path/              # 本地 → 远程
scp user@remote:/path/file.txt .             # 远程 → 本地
scp -r dir/ user@remote:/path/               # 递归（目录）
scp -P 2222 file.txt user@remote:/path/      # 指定端口
scp -i key.pem file.txt user@remote:/path/   # 指定密钥

# rsync — 增量同步（推荐）
rsync -av /src/ /dest/                       # 本地同步（-a 归档 -v 详细）
rsync -avz /src/ user@remote:/dest/          # 远程同步（-z 压缩）
rsync -av --delete /src/ /dest/             # 删除目标多余的文件
rsync -av --exclude='*.log' /src/ /dest/     # 排除文件
rsync -av -e "ssh -p 2222" /src/ user@remote:/dest/  # 指定 SSH 端口
rsync -av --partial --progress /src/ user@remote:/dest/  # 断点续传
rsync -av --link-dest=/prev/ /src/ /dest/    # 硬链接增量备份

# 重要：/src/ 和 /src 的区别
# /src/  → 传输 src 目录的内容到 dest
# /src   → 传输 src 目录本身到 dest（dest/src/...）
```

#### 远程连接

```bash
# ssh — 安全远程连接
ssh user@remote                          # 连接远程主机
ssh -p 2222 user@remote                  # 指定端口
ssh -i key.pem user@remote               # 指定密钥
ssh user@remote command                  # 远程执行命令
ssh -L 8080:localhost:80 user@remote     # 本地端口转发
ssh -R 8080:localhost:80 user@remote     # 远程端口转发
ssh -D 1080 user@remote                  # SOCKS 代理
ssh -N -L 8080:localhost:80 user@remote  # 只端口转发不执行命令
ssh-copy-id user@remote                  # 安装公钥到远程
ssh-keygen -t ed25519 -C "comment"       # 生成密钥对
ssh-keygen -t rsa -b 4096 -C "comment"  # RSA 密钥

# ssh-agent — 密钥代理
eval $(ssh-agent)                        # 启动 agent
ssh-add ~/.ssh/id_ed25519                # 添加密钥
ssh-add -l                               # 列出已加载密钥
```

#### 抓包

```bash
# tcpdump — 数据包捕获
sudo tcpdump -i eth0                     # 抓取 eth0 接口
sudo tcpdump -i eth0 -n                  # 不解析名称
sudo tcpdump -i eth0 -nn port 80         # 只看 80 端口
sudo tcpdump -i eth0 host 192.168.1.100  # 指定主机
sudo tcpdump -i eth0 -c 100              # 抓 100 个包
sudo tcpdump -i eth0 -w capture.pcap     # 保存为 pcap 文件
sudo tcpdump -i eth0 -r capture.pcap     # 读取 pcap 文件
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'  # 只看 SYN 包
sudo tcpdump -i eth0 'port 80 and host 192.168.1.100'  # 组合过滤
sudo tcpdump -i eth0 -nn -X 'port 443'   # 十六进制+ASCII 显示
```

> **风险提示**：抓包可能捕获敏感信息（密码、Token），仅限授权环境操作。`tcpdump` 需要 root 权限。

#### 防火墙

**iptables — 传统防火墙规则**

```
├── 语法：iptables [选项] [链] [规则]
├── 核心参数：
│   ├── -L             列出规则
│   ├── -A CHAIN       追加规则
│   ├── -I CHAIN       插入规则
│   ├── -D CHAIN       删除规则
│   ├── -F             清空规则（高风险！）
│   ├── -P CHAIN      设置默认策略
│   ├── -p PROTO      协议（tcp/udp/icmp）
│   ├── -s IP         源地址
│   ├── -d IP         目标地址
│   ├── --sport PORT  源端口
│   ├── --dport PORT  目标端口
│   ├── -j TARGET     动作（ACCEPT/DROP/REJECT/LOG）
│   └── -t TABLE      表（filter/nat/mangle/raw）
├── 调用案例：
│   ├── iptables -L -n
│   ├── iptables -A INPUT -p tcp --dport 22 -j ACCEPT
│   └── iptables -A INPUT -s 1.2.3.4 -j DROP
├── 适用场景：防火墙规则管理
└── 风险等级：★★★★☆（高风险）
    ⚠️ iptables -F 清空所有规则可能导致 SSH 断连！
    ⚠️ 操作前确保有规则放行 SSH（端口 22）。
    回滚方案：iptables-save > backup.rules；恢复：iptables-restore < backup.rules
    永久保存：Ubuntu 用 iptables-persistent，CentOS 用 firewalld 或 iptables-services
```

```bash
# 查看规则
sudo iptables -L -n -v                  # 查看所有规则（详细）
sudo iptables -L -n --line-numbers      # 带行号（用于删除）
sudo iptables -t nat -L -n              # 查看 NAT 表

# 允许 SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 允许 HTTP/HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 允许已建立连接
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 拒绝特定 IP
sudo iptables -A INPUT -s 1.2.3.4 -j DROP

# 允许 ping
sudo iptables -A INPUT -p icmp -j ACCEPT

# 设置默认策略
sudo iptables -P INPUT DROP              # 默认拒绝入站（高风险！先确保 SSH 放行）
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# 保存和恢复
sudo iptables-save > /tmp/iptables.rules     # 备份
sudo iptables-restore < /tmp/iptables.rules  # 恢复

# 永久保存
# Ubuntu/Debian:
sudo apt install iptables-persistent
sudo netfilter-persistent save
# CentOS/RHEL（传统）:
sudo service iptables save
```

**nftables / firewalld / ufw**

```bash
# nftables — 新一代防火墙（替代 iptables）
sudo nft list ruleset                   # 查看规则
sudo nft add rule inet filter input tcp dport 22 accept  # 允许 SSH

# firewalld — CentOS/RHEL/Fedora 推荐
sudo firewall-cmd --list-all            # 查看所有规则
sudo firewall-cmd --add-port=80/tcp --permanent   # 永久开放 80 端口
sudo firewall-cmd --add-service=ssh --permanent   # 永久开放 SSH
sudo firewall-cmd --reload              # 重新加载规则
sudo firewall-cmd --list-ports          # 查看已开放端口

# ufw — Ubuntu/Debian 推荐
sudo ufw status                         # 查看状态
sudo ufw allow 22/tcp                   # 允许 SSH
sudo ufw allow 80/tcp                   # 允许 HTTP
sudo ufw allow 443/tcp                  # 允许 HTTPS
sudo ufw enable                         # 启用防火墙
sudo ufw deny 3306/tcp                  # 拒绝 MySQL
sudo ufw status verbose                 # 详细状态
```

---

### 类别 8：包管理

#### Debian/Ubuntu（apt / dpkg）

| 操作 | apt（推荐） | apt-get | dpkg |
|------|-------------|---------|------|
| 安装 | `apt install pkg` | `apt-get install pkg` | `dpkg -i pkg.deb` |
| 更新 | `apt install pkg` | `apt-get install --only-upgrade pkg` | — |
| 卸载（保留配置） | `apt remove pkg` | `apt-get remove pkg` | `dpkg -r pkg` |
| 卸载（含配置） | `apt purge pkg` | `apt-get purge pkg` | `dpkg -P pkg` |
| 搜索 | `apt search keyword` | `apt-cache search keyword` | `dpkg -l \| grep` |
| 列表 | `apt list --installed` | `dpkg -l` | `dpkg -l` |
| 信息 | `apt show pkg` | `apt-cache show pkg` | `dpkg -s pkg` |
| 更新索引 | `apt update` | `apt-get update` | — |
| 升级全部 | `apt upgrade` | `apt-get upgrade` | — |

```bash
# 更新软件源索引（必须先执行）
sudo apt update                        # 更新包索引
sudo apt upgrade                       # 升级所有可升级包
sudo apt full-upgrade                  # 升级（含依赖变更，可能卸载旧包）

# 安装
sudo apt install nginx                 # 安装 nginx
sudo apt install nginx=1.24.*          # 安装指定版本
sudo apt install -y htop git curl      # 批量安装，-y 自动确认

# 搜索
apt search "web server"                # 搜索
apt list --installed                   # 列出已安装
apt list --upgradable                  # 列出可升级
apt show nginx                         # 查看包信息

# 卸载
sudo apt remove nginx                  # 卸载（保留配置）
sudo apt purge nginx                   # 卸载（含配置）
sudo apt autoremove                    # 自动清理不需要的依赖
sudo apt autoclean                     # 清理旧版本包缓存

# dpkg — 底层包管理
sudo dpkg -i package.deb               # 安装 .deb 文件
sudo dpkg -r package                   # 移除
sudo dpkg -P package                   # 移除（含配置）
dpkg -l                                # 列出所有已安装包
dpkg -L nginx                          # 查看 nginx 安装的文件列表
dpkg -S /usr/bin/curl                  # 查询文件属于哪个包

# 清理
sudo apt clean                         # 清空缓存
sudo apt autoclean                     # 只清理旧版本
sudo apt autoremove --purge            # 清理不需要的包及配置

# 修复依赖
sudo apt --fix-broken install          # 修复损坏的依赖
sudo dpkg --configure -a              # 修复未完成的配置
```

#### RHEL/CentOS/Fedora（dnf / yum / rpm）

| 操作 | dnf（RHEL 8+/Fedora） | yum（RHEL 7/CentOS 7） | rpm |
|------|----------------------|----------------------|------|
| 安装 | `dnf install pkg` | `yum install pkg` | `rpm -ivh pkg.rpm` |
| 更新 | `dnf upgrade pkg` | `yum update pkg` | — |
| 卸载 | `dnf remove pkg` | `yum remove pkg` | `rpm -e pkg` |
| 搜索 | `dnf search keyword` | `yum search keyword` | — |
| 信息 | `dnf info pkg` | `yum info pkg` | `rpm -qi pkg` |
| 列出 | `dnf list installed` | `yum list installed` | `rpm -qa` |
| 清理缓存 | `dnf clean all` | `yum clean all` | — |

```bash
# 安装
sudo dnf install nginx                 # RHEL/Fedora
sudo yum install nginx                 # CentOS 7

# 更新
sudo dnf check-update                  # 检查可用更新
sudo dnf upgrade                       # 升级所有
sudo dnf upgrade nginx                 # 只升级 nginx

# 搜索
dnf search "web server"                # 搜索
dnf list installed                     # 列出已安装
dnf info nginx                         # 包信息

# 卸载
sudo dnf remove nginx                  # 卸载
sudo dnf autoremove                     # 清理不需要的依赖

# rpm — 底层包管理
sudo rpm -ivh package.rpm              # 安装（i=install v=verbose h=hash）
sudo rpm -Uvh package.rpm              # 升级安装
sudo rpm -e package                    # 卸载
rpm -qa                                # 列出所有已安装包
rpm -ql nginx                          # 查看 nginx 安装的文件列表
rpm -qf /usr/bin/curl                  # 查询文件属于哪个包
rpm -qi nginx                          # 包信息
rpm -Va                                # 校验所有包（安全审计）

# 包组管理
dnf grouplist                          # 列出包组
dnf groupinstall "Development Tools"   # 安装开发工具组
dnf groupremove "Development Tools"    # 卸载包组
```

#### Arch（pacman）

```bash
sudo pacman -Syu                       # 更新整个系统
sudo pacman -S nginx                   # 安装
sudo pacman -Rs nginx                  # 卸载（含不需要的依赖）
sudo pacman -Rns nginx                 # 卸载（含配置和依赖）
pacman -Ss nginx                       # 搜索
pacman -Q                              # 列出已安装
pacman -Qi nginx                       # 包信息
pacman -Ql nginx                       # 安装的文件列表
pacman -Qo /usr/bin/curl               # 查询文件属于哪个包
sudo pacman -Sc                        # 清理缓存
sudo pacman -Scc                       # 清理所有缓存

# AUR（Arch User Repository）
# 使用 yay 或 paru：
yay -S package                         # 从 AUR 安装
```

#### openSUSE（zypper）

```bash
sudo zypper install nginx              # 安装
sudo zypper update                     # 更新
sudo zypper remove nginx               # 卸载
zypper search nginx                    # 搜索
zypper packages --installed            # 列出已安装
sudo zypper clean                      # 清理缓存
```

---

### 类别 9：服务与 systemd

**systemctl — 服务管理**

```
├── 语法：systemctl [选项] 命令 [服务名]
├── 核心命令：
│   ├── start         启动服务
│   ├── stop          停止服务
│   ├── restart       重启服务
│   ├── reload        重载配置（不中断）
│   ├── status        查看状态
│   ├── enable        开机自启
│   ├── disable       取消开机自启
│   ├── is-enabled    查看是否开机自启
│   ├── is-active     查看是否运行中
│   ├── list-units    列出所有单元
│   ├── list-unit-files  列出所有单元文件
│   ├── daemon-reload 重新加载 systemd 配置
│   ├── edit          编辑服务覆盖配置
│   ├── cat           查看服务单元文件内容
│   └── mask/unmask   禁止/允许启动
├── 调用案例：
│   ├── systemctl status nginx
│   ├── systemctl restart nginx
│   └── systemctl enable --now nginx
├── 适用场景：服务生命周期管理
└── 风险等级：★★☆☆☆（中低风险）
    ⚠️ restart 会短暂中断服务。生产环境建议用 reload。
    ⚠️ 需 root 权限。
```

```bash
# 查看状态
systemctl status nginx                # 查看 nginx 服务状态
systemctl is-active nginx             # 是否运行中（输出 active/inactive）
systemctl is-enabled nginx            # 是否开机自启（输出 enabled/disabled）
systemctl is-failed nginx             # 是否失败

# 启停重启
sudo systemctl start nginx            # 启动
sudo systemctl stop nginx             # 停止
sudo systemctl restart nginx          # 重启
sudo systemctl reload nginx           # 重载配置（不中断连接）
sudo systemctl try-restart nginx      # 仅在运行时重启

# 开机自启
sudo systemctl enable nginx           # 设为开机自启
sudo systemctl disable nginx          # 取消开机自启
sudo systemctl enable --now nginx     # 设为开机自启 + 立即启动
sudo systemctl mask nginx             # 完全禁止启动（无法手动启动）
sudo systemctl unmask nginx           # 解除禁止

# 列出服务
systemctl list-units --type=service              # 所有服务
systemctl list-units --type=service --state=running  # 运行中的
systemctl list-units --type=service --state=failed   # 失败的
systemctl list-unit-files --type=service         # 所有服务文件
systemctl list-units --type=service --state=enabled   # 开机自启的

# 查看单元文件
systemctl cat nginx                   # 查看 nginx.service 文件内容
systemctl list-dependencies nginx     # 查看依赖
systemctl show nginx                  # 详细属性

# 编辑覆盖配置
sudo systemctl edit nginx             # 创建覆盖文件（不改原文件）
# 在编辑器中写入 [Service] 区段覆盖

# 重新加载 systemd 配置（修改了 unit 文件后必须执行）
sudo systemctl daemon-reload
```

**journalctl — 日志查询**

```
├── 语法：journalctl [选项]
├── 核心参数：
│   ├── -u UNIT        指定服务
│   ├── --since TIME   从何时开始
│   ├── --until TIME   到何时结束
│   ├── -p LEVEL       日志级别
│   ├── -f             实时追踪
│   ├── -n N           最后 N 行
│   ├── --no-pager     不分页
│   ├── -o FORMAT      输出格式
│   ├── -k             内核日志
│   ├── _PID=PID       按 PID 过滤
│   └── --disk-usage   日志磁盘占用
├── 调用案例：
│   ├── journalctl -u nginx --since today
│   ├── journalctl -p err -n 50
│   └── journalctl -f -u nginx
├── 适用场景：日志分析、故障排查
└── 风险等级：★☆☆☆☆（低风险，只读）
```

```bash
# 按服务
journalctl -u nginx                    # nginx 服务全部日志
journalctl -u nginx -u php-fpm         # 多个服务
journalctl -u nginx --since today      # 今日 nginx 日志
journalctl -u nginx --since "1 hour ago"  # 最近 1 小时
journalctl -u nginx --since "2026-09-24" --until "2026-09-24 12:00"

# 按级别
journalctl -p err                      # 所有错误
journalctl -p warning -u nginx         # nginx 警告及以上
# 级别：emerg(0) alert(1) crit(2) err(3) warning(4) notice(5) info(6) debug(7)

# 实时追踪
journalctl -f                          # 实时追踪所有日志
journalctl -f -u nginx                 # 实时追踪 nginx

# 按数量
journalctl -n 50                       # 最后 50 行
journalctl -n 50 -u nginx              # nginx 最后 50 行

# 按内核
journalctl -k                          # 内核日志
journalctl -k --since "1 hour ago"

# 按 PID/用户
journalctl _PID=1234                   # 指定 PID 的日志
journalctl _UID=1000                   # 指定 UID 的日志

# 输出格式
journalctl -o json                     # JSON 格式
journalctl -o json-pretty              # 美化 JSON
journalctl -o cat                      # 只输出消息（不带元数据）
journalctl -o short-iso                # ISO 时间戳

# 日志管理
journalctl --disk-usage                # 日志占用磁盘
sudo journalctl --vacuum-size=500M     # 限制日志大小为 500MB
sudo journalctl --vacuum-time=7d       # 只保留 7 天日志
```

**service — 传统服务管理（向后兼容）**

```bash
sudo service nginx start              # = systemctl start nginx
sudo service nginx stop
sudo service nginx restart
sudo service nginx status
sudo service --status-all              # 列出所有服务状态
```

---

### 类别 10：Shell 内置命令与脚本

#### 变量与环境

```bash
# 变量赋值（注意：= 两边不能有空格）
VAR="hello"
NUM=42
TODAY=$(date +%Y%m%d)

# 引用变量
echo $VAR
echo ${VAR}
echo "Value: ${VAR}"                  # 双引号中会展开变量
echo 'Value: ${VAR}'                  # 单引号中不会展开

# 环境变量
export PATH="/opt/bin:$PATH"          # 导出环境变量
export JAVA_HOME="/usr/lib/jvm/java-17"
export MY_VAR="global"                # 子进程可访问

# 查看环境变量
env                                    # 所有环境变量
printenv HOME                          # 查看指定变量
echo $PATH                             # 查看 PATH
echo $HOME                             # 查看主目录

# 删除变量
unset VAR                              # 删除普通变量
unset MY_VAR                           # 删除环境变量
```

#### 流程控制

```bash
# if 语句
if [ "$VAR" = "yes" ]; then
    echo "Confirmed"
elif [ "$VAR" = "no" ]; then
    echo "Denied"
else
    echo "Unknown"
fi

# for 循环
for file in *.txt; do
    echo "Processing: $file"
done

for i in 1 2 3 4 5; do
    echo "Number: $i"
done

for i in $(seq 1 10); do
    echo "Count: $i"
done

# while 循环
count=0
while [ $count -lt 10 ]; do
    echo "Count: $count"
    count=$((count + 1))
done

# 无限循环
while true; do
    echo "Running..."
    sleep 5
done

# case 语句
case "$1" in
    start)
        echo "Starting..."
        ;;
    stop)
        echo "Stopping..."
        ;;
    restart)
        echo "Restarting..."
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac
```

#### 别名与函数

```bash
# alias — 设置别名
alias ll='ls -alF'                     # 列表长格式
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias df='df -h'
alias free='free -h'
alias ports='ss -tlnp'

# 永久设置：写入 ~/.bashrc 或 ~/.bash_aliases
echo "alias ll='ls -alF'" >> ~/.bashrc
source ~/.bashrc                       # 立即生效

# unalias
unalias ll                             # 移除别名

# function — 定义函数
greeting() {
    echo "Hello, $1!"
}
greeting "World"                       # 调用：Hello, World!

# 带返回值的函数
check_root() {
    if [ "$(id -u)" -eq 0 ]; then
        return 0                      # true
    else
        return 1                      # false
    fi
}

if check_root; then
    echo "Running as root"
fi

# 带局部变量的函数
process() {
    local file="$1"
    local count=$(wc -l < "$file")
    echo "$file: $count lines"
}
```

#### 命令历史

```bash
history                               # 查看命令历史
history 20                            # 最近 20 条
!!                                    # 执行上一条命令
sudo !!                               # 以 root 执行上一条
!123                                  # 执行第 123 条历史命令
!grep                                 # 执行最后一条以 grep 开头的命令
!$                                    # 上一条命令的最后一个参数
Ctrl+R                                # 反向搜索历史
Ctrl+P / Ctrl+N                       # 上一条/下一条

# 配置
export HISTSIZE=1000                  # 命令历史条数
export HISTFILESIZE=2000              # 历史文件行数
export HISTCONTROL=ignoredups         # 忽略重复命令
export HISTTIMEFORMAT='%F %T '        # 记录时间戳
```

#### 输入输出

```bash
# echo — 简单输出
echo "Hello World"
echo -n "No newline"                  # 不换行
echo -e "Line1\nLine2"                # 解释转义字符
echo -e "\033[31mRed Text\033[0m"     # 彩色输出

# printf — 格式化输出
printf "%-10s %5d\n" "Name" 42        # 左对齐10字符 整数5位
printf "Date: %s\n" "$(date)"
printf "PID: %d\n" $$

# read — 读取输入
read -p "Enter name: " name          # 提示输入
read -s -p "Password: " pass         # 静默输入（密码）
read -t 5 -p "Timeout (5s): " input   # 5秒超时
read -a arr                           # 读取数组（空格分隔）

# tee — 双向输出（屏幕 + 文件）
echo "log entry" | tee -a /var/log/custom.log  # 追加到文件同时显示
command 2>&1 | tee output.txt         # 标准输出和错误都 tee
```

#### 重定向与管道

| 操作符 | 含义 | 示例 |
|--------|------|------|
| `>` | 标准输出重定向（覆盖） | `command > file` |
| `>>` | 标准输出追加 | `command >> file` |
| `2>` | 标准错误重定向 | `command 2> error.log` |
| `2>&1` | 标准错误合并到标准输出 | `command > all.log 2>&1` |
| `&>` | 全部重定向（Bash 4+） | `command &> all.log` |
| `<` | 标准输入重定向 | `command < input.txt` |
| `<<` | Here Document | `command << 'EOF'` |
| `<<<` | Here String | `command <<< "text"` |
| `|` | 管道 | `command1 \| command2` |
| `\|&` | 管道含标准错误 | `command1 \|& command2` |

```bash
# 重定向
echo "text" > file.txt                # 覆盖写入
echo "more" >> file.txt               # 追加写入
command 2> error.log                  # 错误输出到文件
command > all.log 2>&1               # 标准输出和错误合并
command &> all.log                   # 同上（Bash 4+ 简写）
command > /dev/null 2>&1             # 丢弃所有输出
command < input.txt                  # 从文件读输入

# 管道
ps aux | grep nginx                   # 进程过滤
cat file | sort | uniq -c | sort -rn  # 统计排序
ls -l | wc -l                         # 计数
dmesg | grep -i "error" | less        # 分页查看

# Here Document
cat << 'EOF' > /tmp/config.txt
server {
    listen 80;
    server_name example.com;
}
EOF

# Here String
grep "keyword" <<< "This has keyword in it"

# 进程替换
diff <(ls dir1) <(ls dir2)            # 比较两个命令的输出
comm <(sort file1) <(sort file2)      # 交集差集
```

---

### 类别 11：开发与调试工具

#### 编译

```bash
# gcc — C 编译器
gcc -o program source.c               # 编译
gcc -Wall -g -o program source.c      # 警告 + 调试信息
gcc -O2 -o program source.c           # 优化
gcc -c source.c                       # 只编译不链接（生成 .o）
gcc -lm -o program source.c           # 链接数学库
gcc -shared -fPIC -o libfoo.so foo.c  # 编译动态库

# g++ — C++ 编译器
g++ -std=c++17 -o program source.cpp  # C++17 标准
g++ -Wall -g -o program source.cpp     # 警告 + 调试

# make — 构建工具
make                                   # 编译（默认 target）
make clean                             # 清理
make install                           # 安装
make -j4                               # 4 线程并行编译
make target_name                       # 指定 target
```

#### 调试

```bash
# gdb — 程序调试器
gdb ./program                         # 启动调试
# gdb 内部命令：
#   break main        设置断点
#   run               运行
#   next              单步（不进入函数）
#   step              单步（进入函数）
#   print var         查看变量
#   backtrace         调用栈
#   continue          继续
#   quit              退出

gdb -batch -ex "run" -ex "bt" ./program  # 崩溃时打印调用栈

# strace — 系统调用追踪
strace ./program                      # 追踪所有系统调用
strace -p 1234                        # 追踪运行中进程
strace -e trace=network ./program     # 只追踪网络调用
strace -e trace=file ./program        # 只追踪文件操作
strace -c ./program                   # 统计系统调用
strace -f ./program                   # 追踪子进程

# ltrace — 库函数追踪
ltrace ./program                     # 追踪库函数调用
ltrace -p 1234                       # 追踪运行中进程
```

#### 依赖

```bash
# ldd — 动态库依赖
ldd /usr/bin/curl                     # 查看 curl 的动态库依赖
ldd /usr/bin/nginx                    # 查看 nginx 的库依赖

# ldconfig — 动态链接器配置
sudo ldconfig                         # 刷新动态库缓存
ldconfig -p                           # 查看缓存中的库
sudo ldconfig /opt/lib                # 添加自定义库路径

# pkg-config — 编译标志查询
pkg-config --cflags openssl           # 获取编译头文件路径
pkg-config --libs openssl             # 获取链接库路径
pkg-config --list-all                 # 列出所有已知包
```

#### 版本控制

```bash
# git — 基础命令
git init                              # 初始化仓库
git clone https://github.com/repo.git # 克隆
git status                            # 查看状态
git add file.txt                      # 暂存
git add .                             # 暂存所有变更
git commit -m "message"              # 提交
git log --oneline                     # 简洁日志
git log --graph --oneline --all       # 图形日志
git push origin main                  # 推送
git pull origin main                  # 拉取
git branch feature                    # 创建分支
git checkout feature                  # 切换分支
git merge feature                     # 合并分支
git diff                              # 查看未暂存变更
git diff --cached                     # 查看已暂存变更
git remote -v                         # 查看远程
git stash                             # 暂存当前工作
git stash pop                         # 恢复暂存
```

---

## 三、命令参数与案例的呈现要求

### 1. 每个命令的标准呈现格式

本文档采用统一的树状结构呈现每个命令：

```
命令名称
├── 语法：command [options] [arguments]
├── 核心参数：
│   ├── -a / --all：说明
│   ├── -l / --long：说明
│   └── -h / --human-readable：说明
├── 调用案例：
│   ├── 基础用法：command file
│   ├── 组合用法：command -al /path
│   └── 管道用法：command | grep pattern
├── 适用场景：说明
└── 风险提示：如有高风险操作则标注
```

### 2. 参数说明的要求

| 要求 | 说明 | 示例 |
|------|------|------|
| 区分短/长选项 | 同时列出两种写法 | `-a` / `--all` |
| 标注可组合性 | 说明能否与其他选项合并 | `-lah`（= `-l -a -h`） |
| 标注默认值 | 如有默认值则标注 | `head -n 10`（默认 10 行） |
| 标注互斥关系 | 不可同时使用的选项 | `-a` 与 `-d` 互斥 |

### 3. 案例的要求

| 要求 | 说明 |
|------|------|
| 案例数量 | 每个命令至少 2 个案例 |
| 准确性 | 案例必须准确、可执行、可复制 |
| 发行版标注 | 标注适用发行版（Ubuntu/Debian、CentOS/RHEL 等） |
| 风险标注 | 高风险案例必须标注警告 |

### 4. 风险等级说明

| 等级 | 星级 | 含义 | 示例 |
|------|------|------|------|
| 低 | ★☆☆☆☆ | 只读/低影响 | `ls`、`cat`、`grep` |
| 中低 | ★★☆☆☆ | 修改文件但不影响系统 | `cp`、`mv`、`tar` |
| 中 | ★★★☆☆ | 修改系统配置/权限 | `chmod`、`useradd`、`kill` |
| 高 | ★★★★☆ | 修改网络/防火墙 | `iptables`、`ip` 配置 |
| 极高 | ★★★★★ | 不可逆/系统级 | `rm -rf`、`dd`、`mkfs` |

---

## 四、常用命令速查表

| 命令 | 功能说明 | 常用参数 | 典型示例 | 风险等级 |
|------|----------|----------|----------|---------|
| `ls` | 列出目录内容 | `-l` `-a` `-h` | `ls -lah /var/log` | 低 |
| `cd` | 切换目录 | `~` `-` | `cd /var/log` | 低 |
| `pwd` | 显示当前路径 | `-P` | `pwd -P` | 低 |
| `cp` | 复制文件/目录 | `-r` `-a` `-i` | `cp -a /etc/nginx /backup/` | 中低 |
| `mv` | 移动/重命名 | `-i` `-f` | `mv old.txt new.txt` | 中低 |
| `rm` | 删除文件/目录 | `-r` `-f` `-i` | `rm -rf /tmp/old/` | 高 |
| `find` | 查找文件 | `-name` `-type` `-exec` | `find /etc -name "*.conf"` | 中 |
| `grep` | 文本搜索 | `-r` `-i` `-n` | `grep -rn "error" /var/log/` | 低 |
| `sed` | 流编辑 | `-i` `-n` `s///g` | `sed -i 's/old/new/g' file` | 中 |
| `awk` | 列处理 | `-F` `{print}` | `awk -F: '{print $1}' /etc/passwd` | 低 |
| `tar` | 归档压缩 | `-czvf` `-xzvf` | `tar -czvf bak.tar.gz /home/` | 中低 |
| `chmod` | 修改权限 | `-R` `755` `u+x` | `chmod 755 script.sh` | 中 |
| `chown` | 修改所有者 | `-R` `user:group` | `chown -R www:www /var/www/` | 中 |
| `ps` | 进程快照 | `aux` `-ef` | `ps aux \| grep nginx` | 低 |
| `kill` | 终止进程 | `-9` `-15` `-HUP` | `kill -9 1234` | 中 |
| `top` | 实时监控 | `-d` `-p` | `top` | 低 |
| `df` | 磁盘使用 | `-h` `-i` | `df -h` | 低 |
| `du` | 目录大小 | `-sh` `--max-depth` | `du -sh /var/log` | 低 |
| `free` | 内存使用 | `-h` `-m` | `free -h` | 低 |
| `ss` | 连接统计 | `-tlnp` | `ss -tlnp` | 低 |
| `ip` | 网络配置 | `addr` `route` `link` | `ip addr show` | 中 |
| `curl` | HTTP 工具 | `-O` `-X` `-d` `-H` | `curl -O https://example.com/file` | 低 |
| `wget` | 下载工具 | `-c` `-O` | `wget -c https://example.com/file` | 低 |
| `ssh` | 远程连接 | `-p` `-i` `-L` | `ssh -p 2222 user@host` | 低 |
| `systemctl` | 服务管理 | `status` `restart` `enable` | `systemctl restart nginx` | 中低 |
| `journalctl` | 日志查询 | `-u` `-f` `--since` | `journalctl -u nginx -f` | 低 |
| `apt` | 包管理(Ubuntu) | `install` `update` `search` | `sudo apt install nginx` | 中低 |
| `dnf` | 包管理(RHEL) | `install` `upgrade` `search` | `sudo dnf install nginx` | 中低 |
| `iptables` | 防火墙 | `-L` `-A` `-F` | `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` | 高 |
| `git` | 版本控制 | `clone` `commit` `push` | `git commit -m "fix"` | 低 |

---

## 五、高风险命令清单

> **以下命令可能导致数据丢失、系统崩溃或服务中断。操作前务必确认路径、备份重要数据，并在维护窗口执行。**

### 5.1 递归强制删除

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `rm -rf /` | 删除整个根文件系统 | ★★★★★ | 绝对禁止！系统有 `--preserve-root` 保护，但加 `--no-preserve-root` 可绕过 | 无法回滚，需从备份恢复整个系统 |
| `rm -rf *` | 删除当前目录所有文件 | ★★★★★ | 先 `ls` 确认当前目录，使用 `rm -ri` 交互确认 | 无直接回滚 |
| `rm -rf $VAR/` | 变量为空时变成 `rm -rf /` | ★★★★★ | 使用 `set -u`（引用未定义变量报错），或在命令前加 `[ -n "$VAR" ] &&` | 无直接回滚 |

```bash
# 危险示例（绝对不要执行！）
# rm -rf /                          # 删除根文件系统
# rm -rf *                          # 删除当前目录全部
# rm -rf $UNSET_VAR/                # 变量为空时等同 rm -rf /

# 安全做法
set -u                               # 引用未定义变量报错
rm -ri /old/data/                    # 交互确认
# 或使用 trash-cli
trash-put /old/data/                 # 移入回收站
```

### 5.2 磁盘写入操作

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `dd if=/dev/zero of=/dev/sda` | 覆盖整个磁盘 | ★★★★★ | 确认 `of=` 设备名，用 `lsblk` 先查看 | 无回滚，磁盘数据全毁 |
| `dd if=image.iso of=/dev/sdb` | 写入磁盘镜像 | ★★★★☆ | 确认目标设备，先用 `lsblk` 核对 | 无回滚 |
| `> /dev/sda` | 重定向覆盖磁盘 | ★★★★★ | 避免对块设备使用重定向 | 无回滚 |

```bash
# 危险示例（绝对不要执行！）
# dd if=/dev/zero of=/dev/sda bs=1M   # 用零覆盖整个磁盘
# dd if=/dev/random of=/dev/sda       # 用随机数据覆盖
# > /dev/sda                          # 重定向覆盖

# 安全做法
lsblk                                   # 先确认设备名
sudo dd if=image.iso of=/dev/sdb bs=4M status=progress  # 确认 of= 是正确的设备
sync                                    # 确保写入完成
```

### 5.3 格式化文件系统

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `mkfs.ext4 /dev/sda1` | 格式化分区 | ★★★★★ | 确认设备名，数据全丢 | 无回滚，需从备份恢复 |
| `mkfs.xfs /dev/sdb1` | 格式化 XFS | ★★★★★ | 同上 | 无回滚 |
| `mkswap /dev/sda2` | 创建交换分区 | ★★★★☆ | 确认设备 | 无回滚 |

```bash
# 危险示例
# mkfs.ext4 /dev/sda1          # 格式化 sda1（数据全丢！）

# 安全做法
lsblk                               # 确认设备
sudo mkfs.ext4 /dev/sdb1            # 确认 sdb1 不是系统分区
```

### 5.4 分区操作

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `fdisk /dev/sda` | 修改分区表 | ★★★★☆ | 先备份分区表 `sfdisk -d`，操作前 `lsblk` 确认 | `sfdisk /dev/sda < backup.pt` |
| `parted /dev/sda` | 修改分区表 | ★★★★☆ | 同上 | 同上 |
| `wipefs -a /dev/sda` | 清除文件系统签名 | ★★★★☆ | 确认设备 | 无回滚 |

```bash
# 分区表备份（操作前务必执行）
sudo sfdisk -d /dev/sda > sda_partition_backup.txt  # 备份分区表
# 恢复
sudo sfdisk /dev/sda < sda_partition_backup.txt
```

### 5.5 防火墙规则清空

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `iptables -F` | 清空所有防火墙规则 | ★★★★☆ | 可能导致 SSH 断连 | `iptables-restore < backup` |
| `iptables -P INPUT ACCEPT` | 默认策略改为放行 | ★★★☆☆ | 降低安全性 | 恢复为 DROP |
| `ufw disable` | 关闭防火墙 | ★★★☆☆ | 暴露所有端口 | `ufw enable` |

```bash
# 备份防火墙规则（操作前务必执行）
sudo iptables-save > /tmp/iptables_backup.rules

# 安全清空（先放行 SSH）
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# 然后再操作其他规则

# 恢复
sudo iptables-restore < /tmp/iptables_backup.rules
```

### 5.6 递归开放权限

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `chmod -R 777 /` | 全系统可读写执行 | ★★★★★ | 绝对禁止！系统文件权限混乱 | 需从备份恢复或重装 |
| `chmod -R 777 /var/www` | Web 目录全开放 | ★★★★☆ | 目录应 755，文件应 644 | `find /var/www -type d -exec chmod 755 {} \;` |
| `chown -R nobody:nobody /etc` | 修改系统文件所有者 | ★★★★★ | 绝对禁止！ | 需从备份恢复 |

```bash
# 安全的 Web 目录权限设置
sudo find /var/www -type d -exec chmod 755 {} \;   # 目录 755
sudo find /var/www -type f -exec chmod 644 {} \;   # 文件 644
sudo chown -R www-data:www-data /var/www/          # 统一所有者
```

### 5.7 杀死所有进程

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `kill -9 -1` | 杀死当前用户可杀的所有进程 | ★★★★★ | 绝对禁止！系统崩溃 | 重启系统 |
| `killall -9` | 无参数杀所有同名进程 | ★★★★☆ | 指定进程名 | 重启服务 |
| `pkill -9 ssh` | 杀死所有 SSH 进程 | ★★★★☆ | 可能断连 | 重启 sshd |

```bash
# 安全做法
kill -15 1234                    # 先用 SIGTERM 优雅终止
# 等待几秒后检查
ps -p 1234
# 只有确认进程无响应才用
kill -9 1234
```

### 5.8 Fork 炸弹

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `:(){ :\|:& };:` | Fork 炸弹，瞬间耗尽进程 | ★★★★★ | 绝对禁止！系统死锁 | 强制重启（可能需要硬重启） |

```bash
# 危险示例（绝对不要执行！）
# :(){ :|:& };:                   # Bash Fork 炸弹

# 防护措施
# 1. 限制用户进程数（/etc/security/limits.conf）
# *    hard   nproc   500
# *    soft   nproc   200

# 2. systemd 限制
# [Service]
# LimitNPROC=100
```

### 5.9 覆盖磁盘设备

| 命令 | 风险点 | 风险等级 | 安全建议 | 回滚方案 |
|------|--------|---------|----------|---------|
| `> /dev/sda` | 用空输出覆盖磁盘 | ★★★★★ | 绝对不要对块设备使用重定向 | 无回滚 |
| `cp file /dev/sda` | 覆盖磁盘设备 | ★★★★★ | 确认目标路径 | 无回滚 |
| `shred /dev/sda` | 安全擦除磁盘 | ★★★★☆ | 确认设备（仅用于数据销毁） | 无回滚 |

### 5.10 高风险操作通用安全原则

| 原则 | 说明 |
|------|------|
| **先备份** | 任何高风险操作前，先备份配置和数据 |
| **先预览** | `rm` 前先 `ls`，`sed -i` 前先 `sed`（不带 -i） |
| **交互确认** | 使用 `-i` 或 `-I` 增加确认步骤 |
| **限制范围** | 使用精确路径，避免通配符 `*` |
| **变量检查** | 使用 `set -u`，检查变量非空 |
| **维护窗口** | 生产环境在维护窗口操作 |
| **回滚方案** | 操作前准备回滚方案并验证 |
| **最小权限** | 只授予必要权限，避免 `chmod 777` |

---

## 六、学习路径

### 第一阶段：文件与目录操作 + 文本查看与处理

**学习目标**：掌握日常 80% 的文件操作命令

| 目标 | 命令 | 验收标准 |
|------|------|----------|
| 目录导航 | `ls`、`cd`、`pwd`、`tree` | 能快速定位任意目录 |
| 文件操作 | `cp`、`mv`、`rm`、`touch`、`mkdir` | 能安全地创建、复制、删除文件 |
| 文本查看 | `cat`、`less`、`head`、`tail` | 能查看大文件并实时追踪日志 |
| 文本过滤 | `grep`、`cut`、`sort`、`uniq`、`wc` | 能从日志中提取关键信息 |

**实战任务**：

```bash
# 任务 1：创建项目目录结构
mkdir -p ~/projects/{src,doc,bin,test}
tree ~/projects

# 任务 2：查找大文件并排序
find /var/log -type f -size +10M -exec ls -lh {} \; | sort -k5 -rh | head -10

# 任务 3：日志分析
grep "error" /var/log/syslog | grep -v "debug" | sort | uniq -c | sort -rn | head -20

# 任务 4：文件备份与压缩
tar -czvf backup_$(date +%Y%m%d).tar.gz ~/projects/
```

**推荐练习**：
- Linux Journey（免费在线）：基础命令练习
- OverTheWire Bandit（安全向命令练习）：闯关式学习

### 第二阶段：用户与权限 + 进程管理

**学习目标**：理解 Linux 权限模型，能管理进程

| 目标 | 命令 | 验收标准 |
|------|------|----------|
| 权限管理 | `chmod`、`chown`、`umask` | 能正确设置文件/目录权限 |
| 用户管理 | `useradd`、`usermod`、`passwd` | 能创建/修改/删除用户 |
| 特殊权限 | SUID、SGID、Sticky | 理解特殊权限的作用和风险 |
| 进程查看 | `ps`、`top`、`htop` | 能查看进程状态和资源占用 |
| 进程控制 | `kill`、`killall`、`pkill` | 能安全终止异常进程 |

**实战任务**：

```bash
# 任务 1：创建用户并设置权限
sudo useradd -m -s /bin/bash devuser
sudo passwd devuser
sudo usermod -aG sudo devuser

# 任务 2：安全设置 Web 目录权限
sudo chown -R www-data:www-data /var/www/
sudo find /var/www -type d -exec chmod 755 {} \;
sudo find /var/www -type f -exec chmod 644 {} \;

# 任务 3：查找 SUID 文件（安全审计）
find / -perm -4000 -type f 2>/dev/null

# 任务 4：终止异常进程
ps aux | grep "100% CPU"
kill -15 <PID>
# 确认无响应后再
kill -9 <PID>
```

### 第三阶段：网络工具 + 包管理

**学习目标**：掌握网络诊断和软件包管理

| 目标 | 命令 | 验收标准 |
|------|------|----------|
| 网络配置 | `ip`、`ss`、`ethtool` | 能查看和配置网络接口 |
| 连通性 | `ping`、`traceroute`、`mtr` | 能诊断网络连通性问题 |
| 数据传输 | `curl`、`wget`、`scp`、`rsync` | 能下载文件和远程传输 |
| 包管理 | `apt`/`dnf`/`pacman` | 能安装、更新、卸载软件 |
| 防火墙 | `ufw`/`firewalld`/`iptables` | 能配置基本防火墙规则 |

**实战任务**：

```bash
# 任务 1：网络诊断全流程
ip addr show                          # 查看接口
ping -c 4 8.8.8.8                     # 测试连通性
traceroute 8.8.8.8                    # 追踪路径
ss -tlnp                              # 查看监听端口

# 任务 2：安装 Nginx 并开放端口
sudo apt install nginx                # Ubuntu/Debian
# 或
sudo dnf install nginx                # Fedora/CentOS
sudo ufw allow 80/tcp                 # 开放 80 端口
sudo systemctl enable --now nginx     # 启动并设为自启

# 任务 3：使用 curl 测试 API
curl -v -H "Content-Type: application/json" \
     -d '{"name":"test"}' \
     https://httpbin.org/post

# 任务 4：rsync 远程备份
rsync -avz --progress ~/data/ user@server:/backup/data/
```

### 第四阶段：系统监控 + 服务管理

**学习目标**：掌握系统性能分析和服务生命周期管理

| 目标 | 命令 | 验收标准 |
|------|------|----------|
| 系统信息 | `uname`、`hostname`、`uptime` | 能查看系统基本信息 |
| 磁盘监控 | `df`、`du`、`lsblk` | 能分析磁盘空间问题 |
| 内存性能 | `free`、`vmstat`、`top` | 能分析内存和 CPU 瓶颈 |
| I/O 性能 | `iostat`、`sar` | 能分析 I/O 瓶颈 |
| 服务管理 | `systemctl`、`journalctl` | 能管理服务并查询日志 |

**实战任务**：

```bash
# 任务 1：系统资源巡检
echo "=== CPU ===" && uptime
echo "=== Memory ===" && free -h
echo "=== Disk ===" && df -h
echo "=== Top CPU ===" && ps aux --sort=-%cpu | head -6
echo "=== Top Memory ===" && ps aux --sort=-%mem | head -6

# 任务 2：查找磁盘空间不足的原因
df -h                                 # 找到满的分区
sudo du -sh /var/* | sort -rh | head -10  # 找最大的子目录
sudo du -sh /var/log/* | sort -rh | head -10  # 日志目录

# 任务 3：服务故障排查
systemctl status nginx                # 查看状态
journalctl -u nginx --since "1 hour ago"  # 查看最近日志
journalctl -u nginx -p err            # 只看错误
systemctl restart nginx               # 重启服务

# 任务 4：日志清理
sudo journalctl --vacuum-size=500M    # 限制 journal 日志大小
sudo find /var/log -name "*.gz" -mtime +30 -delete  # 删除 30 天前的日志
```

### 第五阶段：Shell 脚本 + 开发调试

**学习目标**：能编写 Shell 脚本自动化任务，掌握基础调试

| 目标 | 命令 | 验收标准 |
|------|------|----------|
| 脚本基础 | `if`、`for`、`while`、`case` | 能编写 50 行以上的 Shell 脚本 |
| 文本处理 | `sed`、`awk`、`grep -E` | 能用管道组合处理复杂文本 |
| 计划任务 | `crontab` | 能设置定时任务 |
| 调试 | `bash -x`、`strace` | 能调试脚本和程序 |
| 版本控制 | `git` | 能用 git 管理脚本和配置 |

**实战任务**：

```bash
# 任务 1：编写系统巡检脚本
cat << 'SCRIPT' > ~/health_check.sh
#!/bin/bash
echo "=== System Health Check $(date) ==="
echo "--- Uptime ---"
uptime
echo "--- Disk Usage ---"
df -h | awk '$5+0 > 80 {print "WARNING: "$0}'
echo "--- Memory ---"
free -h
echo "--- Failed Services ---"
systemctl list-units --type=service --state=failed
echo "--- High CPU Processes ---"
ps aux --sort=-%cpu | head -6
SCRIPT
chmod +x ~/health_check.sh
# 测试运行
~/health_check.sh
# 设置定时任务
crontab -e
# 添加：0 9 * * * /home/user/health_check.sh >> /var/log/health_check.log 2>&1

# 任务 2：批量日志分析
cat << 'SCRIPT' > ~/analyze_log.sh
#!/bin/bash
LOG="$1"
[ -z "$LOG" ] && echo "Usage: $0 <logfile>" && exit 1
echo "=== Top IPs ==="
awk '{print $1}' "$LOG" | sort | uniq -c | sort -rn | head -10
echo "=== Status Codes ==="
awk '{print $9}' "$LOG" | sort | uniq -c | sort -rn
echo "=== Top URLs ==="
awk '{print $7}' "$LOG" | sort | uniq -c | sort -rn | head -10
SCRIPT
chmod +x ~/analyze_log.sh
./analyze_log.sh /var/log/nginx/access.log

# 任务 3：使用 sed 批量修改配置
# 预览
sed 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
# 确认后修改（带备份）
sudo sed -i.bak 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl reload sshd

# 任务 4：Git 管理配置
cd /etc
sudo git init
sudo git add -A
sudo git commit -m "baseline configuration"
# 修改后
sudo git diff
sudo git commit -am "update nginx config"
```

### 学习路径检查点

| 阶段 | 检查点 | 通过标准 |
|------|--------|----------|
| 1 | 不看文档完成日常文件操作 | 5 分钟内完成目录创建、文件复制、日志查看 |
| 2 | 独立完成用户和权限配置 | 能创建用户、设置权限、终止异常进程 |
| 3 | 完成网络诊断全流程 | 从 IP 配置到连通性测试一气呵成 |
| 4 | 完成系统资源巡检 | 5 分钟内输出 CPU/内存/磁盘/服务状态报告 |
| 5 | 编写自动化脚本 | 能编写并部署定时巡检脚本 |

---

## 七、2026 年免费学习资源

### 综合命令参考

| 资源 | 说明 | 链接 | 时效性 |
|------|------|------|--------|
| **liuzi6612/linux-manual** | Linux 常用命令参考手册，一张网页概括，涵盖文件、系统管理、网络等分类 | [github.com/liuzi6612/linux-manual](https://github.com/liuzi6612/linux-manual) | 2026 年活跃维护 |
| **Ubuntu 官方 Command-line cheat sheet** | Ubuntu 官方命令行速查表，涵盖文件系统、文件操作、用户权限、搜索、重定向、管道等 | [ubuntu.com/server/docs/command-line](https://ubuntu.com/server/docs/command-line-for-beginners) | 官方持续更新 |
| **trinib/Linux-Bash-Commands** | A-Z 命令列表，涵盖从 accept 到 zypper 的全部命令说明 | [github.com/trinib/Linux-Bash-Commands](https://github.com/trinib/Linux-Bash-Commands) | 社区维护 |
| **Alibaba Cloud Linux 系统常用命令** | 阿里云官方文档，按进程、网络、磁盘等分类整理常用命令及参数说明 | [help.aliyun.com](https://help.aliyun.com/document_detail/152648.html) | 官方持续更新 |
| **Linux 运维必备 150 个命令** | 按功能分类的运维命令清单，涵盖文件、文本、压缩、权限等 | 社区整理资源 | 2026 年有效 |

### 在线学习平台

| 资源 | 说明 | 链接 |
|------|------|------|
| **Linux Journey** | 免费在线 Linux 学习平台，从入门到高级，涵盖命令、文本处理、网络、安全等 | [linuxjourney.com](https://linuxjourney.com/) |
| **OverTheWire Bandit** | 闯关式安全学习平台，通过解题学习 Linux 命令 | [overthewire.org/wargames/bandit](https://overthewire.org/wargames/bandit) |
| **LinuxCommand.org** | 经典 Linux 命令学习网站，涵盖 Shell 脚本教程 | [linuxcommand.org](http://linuxcommand.org/) |
| **ExplainShell** | 在线解释命令参数含义，输入命令自动解析每个参数 | [explainshell.com](https://explainshell.com/) |
| **tldr pages** | 简化版 man 页，用示例说明命令用法 | [tldr.sh](https://tldr.sh/) |

### 实用工具

| 工具 | 说明 | 链接 |
|------|------|------|
| **cheat** | 命令速查工具，提供常用命令的示例 | [github.com/cheat](https://github.com/cheat/cheat) |
| **bat** | cat 的增强替代，带语法高亮和行号 | [github.com/sharkdp/bat](https://github.com/sharkdp/bat) |
| **exa / eza** | ls 的增强替代，彩色显示、Git 集成 | [github.com/eza-community/eza](https://github.com/eza-community/eza) |
| **ripgrep** | grep 的高速替代，递归搜索更快 | [github.com/BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) |
| **fd** | find 的友好替代，语法更简洁 | [github.com/sharkdp/fd](https://github.com/sharkdp/fd) |
| **htop** | top 的增强替代，彩色交互式 | [htop.dev](https://htop.dev/) |
| **btop** | 系统资源监控的终极工具 | [github.com/aristocratos/btop](https://github.com/aristocratos/btop) |
| **ncdu** | du 的交互式替代，快速分析磁盘占用 | [dev.yorhel.nl/ncdu](https://dev.yorhel.nl/ncdu) |

### Shell 脚本学习

| 资源 | 说明 | 链接 |
|------|------|------|
| **ShellCheck** | Shell 脚本静态分析工具，检测常见错误 | [shellcheck](https://www.shellcheck.net/) |
| **Bash Hackers Wiki** | Bash 脚本技巧和陷阱 wiki | [wiki.bash-hackers.org](https://wiki.bash-hackers.org/) |
| **LinuxCommand Shell Scripting** | Shell 脚本系统教程 | [linuxcommand.org/scripting.php](http://linuxcommand.org/lc3_learning_the_shell.php) |
| **Pure Bash Bible** | 纯 Bash 实现常见任务，无需外部依赖 | [github.com/dylanaraps/pure-bash-bible](https://github.com/dylanaraps/pure-bash-bible) |

### 安全方向

| 资源 | 说明 | 链接 |
|------|------|------|
| **Linux Hardening Guide** | Linux 安全加固指南 | [github.com/trimstray/the-practical-linux-hardening-guide](https://github.com/trimstray/the-practical-linux-hardening-guide) |
| **CIS Benchmarks** | CIS 安全基线检查（Linux 部分） | [cisecurity.org](https://www.cisecurity.org/cis-benchmarks/) |
| **Lynis** | 开源 Linux 安全审计工具 | [github.com/CISOfy/lynis](https://github.com/CISOfy/lynis) |
| **Linux Audit** | Linux 审计和日志分析资源 | [linuxaudit.com](https://linuxaudit.com/) |

---

## 附：优化后的提示词模板

```markdown
# 文件名：linux-commands-complete-prompt.md

# 角色
你是一名资深 Linux 系统专家，精通 Linux 命令行体系、Shell 编程、系统管理、网络工具与安全加固，擅长按功能分类系统讲解命令、参数和调用案例。

# 任务
请系统介绍 Linux 终端命令，包括：

## 一、命令体系认知
1. Linux 命令的层级划分（Shell 内置、GNU Coreutils、系统管理、网络、开发调试、安全）
2. 命令的构成（名称 + 选项 + 参数，通配符与正则）
3. 如何查询命令（man / --help / info / apropos / type / which / whereis）

## 二、核心命令分类体系（11 大类）
- 文件与目录、文本处理、压缩归档、用户权限、进程控制、系统监控、网络工具、包管理、服务 systemd、Shell 脚本、开发调试

## 三、命令参数与案例的呈现要求
- 统一树状格式、区分短/长选项、至少 2 个案例、标注发行版和风险

## 四、常用命令速查表
## 五、高风险命令清单
## 六、学习路径（5 阶段 + 检查点）
## 七、2026 年免费学习资源

# 输出要求
- Markdown 格式，按大类小类组织
- 关键内容用表格对比
- 重要术语给出中英文
- 每个命令附语法、核心参数、至少 2 个调用案例
- 提供速查表和高风险命令清单
- 面向：Linux 运维工程师 + 安全工程师 + 初学者
- 深度：操作参考 + 案例实战 + 安全加固
- 标注适用发行版

# 约束
- 不声称列出全部命令
- 高风险命令给出警告和回滚方案
- 需 root 权限的命令进行标注
- 仅限授权环境操作
- 资源标注 2026 年时效性
```

---

> **文档说明**
> - 本文不声称列出"全部命令"，聚焦核心命令 + 功能分类 + 代表性案例
> - 所有命令示例经过准确性检查，但不同发行版和版本可能有细微差异
> - 高风险命令均标注风险等级、安全建议和回滚方案
> - 需 root 权限的命令使用 `sudo` 前缀标注
> - 学习资源标注 2026 年时效性，链接可能随时间变化
> - 仅限授权测试环境进行安全相关操作