# Windows CMD 与 PowerShell 核心命令详解

> 本文按功能分类介绍 Windows CMD 与 PowerShell 的核心命令、参数和调用案例。CMD 有大量内/外部命令，PowerShell 有数千 Cmdlet，本文聚焦**核心命令 + 功能分类 + 代表性案例**，不求全但求精。面向系统管理员与安全工程师，深度覆盖操作参考与安全加固。示例适用 Windows 10/11 与 Windows Server 2019/2022。

---

## 目录

- [一、CMD 命令](#一cmd-命令)
- [二、PowerShell Cmdlet](#二powershell-cmdlet)
- [三、reg 命令族与 PowerShell 注册表提供程序](#三reg-命令族与-powershell-注册表提供程序)
- [四、CMD 与 PowerShell 的选择建议](#四cmd-与-powershell-的选择建议)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、CMD 命令

### 1.1 CMD 基础

CMD（Command Prompt）是 Windows 的命令行解释器，继承自 MS-DOS，文件为 `cmd.exe`。

| 概念 | 说明 |
|------|------|
| **内部命令** | 内置在 cmd.exe 中，无需额外文件（dir、cd、copy、del 等） |
| **外部命令** | 独立的 .exe/.com 程序（ipconfig、ping、netstat 等） |
| **批处理** | .bat / .cmd 脚本文件，按行执行 CMD 命令 |
| **环境变量** | `%VAR%` 形式，如 `%SystemRoot%`、`%USERPROFILE%` |
| **重定向** | `>` 覆盖、`>>` 追加、`<` 输入、`|` 管道 |

### 1.2 系统管理

#### （1）系统管理控制台（.msc）

这些是图形化管理工具，在 CMD 中输入名称直接打开。

| 命令 | 全称 | 用途 | 适用场景 |
|------|------|------|---------|
| `gpedit.msc` | Group Policy Editor | 本地组策略编辑器 | 配置系统策略、安全设置 |
| `services.msc` | Services | 服务管理器 | 管理系统服务的启停 |
| `compmgmt.msc` | Computer Management | 计算机管理（综合控制台） | 磁盘、服务、事件查看器一站式 |
| `taskmgr` | Task Manager | 任务管理器 | 查看进程、性能、启动项 |
| `msconfig` | System Configuration | 系统配置（启动/服务/引导） | 排查启动问题、诊断模式 |
| `eventvwr.msc` | Event Viewer | 事件查看器 | 查看系统/安全/应用日志 |
| `devmgmt.msc` | Device Manager | 设备管理器 | 管理硬件设备和驱动 |
| `diskmgmt.msc` | Disk Management | 磁盘管理 | 分区、格式化、盘符分配 |
| `regedit` | Registry Editor | 注册表编辑器 | 查看/修改注册表 |
| `secpol.msc` | Local Security Policy | 本地安全策略 | 安全设置审计策略 |
| `wf.msc` | Windows Firewall | 高级安全防火墙 | 配置防火墙规则 |

```cmd
:: 打开服务管理器
services.msc

:: 打开本地组策略（需管理员权限）
gpedit.msc

:: 打开计算机管理
compmgmt.msc
```

> **管理员标识**：本文中需要管理员权限的命令标注为 🔑。

#### （2）shutdown — 关机/重启/注销

```
语法：
  shutdown [/i | /l | /s | /sg | /r | /g | /a | /p | /h | /e | /o]
           [/hybrid] [/soft] [/fw] [/f]
           [/m \\computer][/t xxx][/d [p|u:]xx:yy [/c "comment"]]

核心参数：
  /s          关闭计算机
  /r          关闭并重启计算机
  /l          注销（不能与 /m 或 /d 一起用）
  /a          中止系统关闭（在超时内有效）
  /t xxx      设置关闭前的超时时间（秒），默认 30
  /f          强制关闭正在运行的应用程序，不警告用户
  /m \\pc     指定远程计算机
  /c "comment" 关机原因注释（最多 512 字符）
  /g          重启后自动重启所有注册应用
  /hybrid     混合关机（快速启动用）
```

```cmd
:: 立即关机
shutdown /s /t 0

:: 60 秒后重启，并显示注释
shutdown /r /t 60 /c "计划维护，系统即将重启"

:: 取消已计划的关机
shutdown /a

:: 强制立即重启（不等待程序保存）
shutdown /r /f /t 0

:: 远程关机（需管理员权限 + 目标机开启远程管理）🔑
shutdown /s /m \\PC-NAME /t 30
```

> ⚠️ **风险提示**：`/f` 参数会强制关闭所有程序，未保存的数据会丢失。远程关机需谨慎操作。

#### （3）sfc — 系统文件检查器 🔑

```
语法：
  sfc [/scannow] [/verifyonly] [/scanfile=<file>] [/verifyfile=<file>]
      [/offbootdir=<dir>] [/offwindir=<dir>]

核心参数：
  /scannow        扫描所有受保护系统文件的完整性，并修复问题文件
  /verifyonly     仅扫描，不修复
  /scanfile=<f>   扫描指定文件，损坏则修复
  /verifyfile=<f> 验证指定文件，不修复
  /offbootdir=<d> 离线修复：指定脱机启动目录（WinPE 环境用）
  /offwindir=<d>  离线修复：指定脱机 Windows 目录
```

```cmd
:: 扫描并修复系统文件（需管理员）🔑
sfc /scannow

:: 仅扫描验证，不修复
sfc /verifyonly

:: 扫描并修复特定文件🔑
sfc /scanfile=C:\Windows\System32\kernel32.dll

:: 配合 DISM 使用的标准修复流程（管理员）🔑
:: 1. 修复组件存储
DISM /Online /Cleanup-Image /RestoreHealth
:: 2. 修复系统文件
sfc /scannow
```

> **适用场景**：系统文件损坏导致异常（蓝屏、程序崩溃、功能异常）时的标准修复手段。

#### （4）chkdsk — 磁盘检查 🔑

```
语法：
  chkdsk [volume:] [/F] [/R] [/X] [/B] [/V] [/scan] [/spotfix]

核心参数：
  volume:    指定驱动器号（如 C:）
  /F         修复磁盘上的错误（需要独占访问，可能需重启）
  /R         查找坏扇区并恢复可读信息（隐含 /F，耗时长）
  /X         强制先卸载卷（隐含 /F）
  /B         重新评估坏簇（NTFS 专用，隐含 /R）
  /scan      在线扫描（不修复，NTFS，Windows 8+）
  /spotfix   现场修复（NTFS，快速修复已知问题点）
  /V         详细模式（显示文件名等信息）
```

```cmd
:: 检查 C 盘但不修复
chkdsk C:

:: 修复 C 盘错误（若正在使用，会提示下次重启时执行）🔑
chkdsk C: /F

:: 全面检查并修复坏扇区（最彻底，耗时长）🔑
chkdsk C: /R

:: 在线扫描（Windows 8+，不中断系统运行）
chkdsk C: /scan

:: 现场修复（快速修复已知问题）
chkdsk C: /spotfix
```

> ⚠️ **风险提示**：`chkdsk /R` 可能需要数小时甚至更久，执行期间系统可能无法使用。在生产服务器上操作前务必评估维护窗口。/F 在系统盘上通常需要重启后在开机阶段执行。

### 1.3 文件与目录

| 命令 | 类型 | 用途 |
|------|------|------|
| **dir** | 内部 | 列出目录内容 |
| **cd / chdir** | 内部 | 切换目录 |
| **copy** | 内部 | 复制文件 |
| **xcopy** | 外部 | 扩展复制（支持目录树） |
| **robocopy** | 外部 | 强大的文件复制工具（推荐） |
| **del / erase** | 内部 | 删除文件 |
| **mkdir / md** | 内部 | 创建目录 |
| **rmdir / rd** | 内部 | 删除目录 |
| **attrib** | 外部 | 显示/修改文件属性 |
| **ren / rename** | 内部 | 重命名文件 |
| **move** | 内部 | 移动文件/目录 |
| **type** | 内部 | 显示文本文件内容 |
| **find** | 外部 | 在文件中查找文本 |
| **findstr** | 外部 | 增强的字符串搜索（支持正则） |

#### （1）dir — 列出目录

```
核心参数：
  /w        宽格式（多列）
  /p        分页显示
  /s        包含子目录
  /b        简要格式（只显示文件名）
  /a[:attr] 显示指定属性的文件（d=目录, h=隐藏, s=系统, r=只读）
  /o[:sort] 排序（n=名称, s=大小, d=日期, e=扩展名）
  /q        显示文件所有者
  /t[:time] 时间字段（c=创建, a=访问, w=修改）
```

```cmd
:: 列出当前目录文件
dir

:: 列出所有文件（含隐藏和系统）
dir /a

:: 递归列出所有 .exe 文件，只显示路径
dir /s /b *.exe

:: 按大小排序（从大到小）
dir /o-s

:: 分页显示系统目录
dir %SystemRoot%\System32 /p
```

#### （2）cd — 切换目录

```cmd
:: 切换到 C 盘根目录
cd C:\

:: 切换到上一级目录
cd ..

:: 切换到用户目录
cd %USERPROFILE%

:: 切换盘符（注意：cd 不能直接切盘，需用 /d 或直接输入盘符）
cd /d D:\data
:: 或
D:

:: 回到当前目录的根
cd \
```

#### （3）copy / xcopy / robocopy — 复制文件

```cmd
:: copy：简单文件复制
copy source.txt dest.txt
copy file1.txt + file2.txt combined.txt   :: 合并文件
copy *.txt D:\backup\                       :: 批量复制

:: xcopy：目录树复制
xcopy source_dir dest_dir /E /I /H
::   /E  复制所有子目录（包括空目录）
::   /I  如果目标不存在且复制多个文件，假定目标是目录
::   /H  复制隐藏和系统文件
::   /Y  不提示直接覆盖

:: robocopy：强大的复制工具（推荐用于同步/备份）
robocopy source dest /MIR /Z /R:3 /W:5
::   /MIR 镜像目录树（删除目标中源没有的文件）
::   /Z   可重启模式（大文件中断后可续传）
::   /R:n 失败重试 n 次
::   /W:n 重试等待 n 秒
::   /E   复制子目录（含空目录）
::   /COPY:DAT  复制数据、属性、时间戳（默认）
::   /COPYALL   复制所有信息（含权限、所有者、审计）
::   /XD dir    排除指定目录
::   /XF *.tmp  排除指定文件
```

> ⚠️ **风险提示**：`robocopy /MIR` 会**删除**目标目录中源目录没有的文件，使用前请确认路径正确，先加 `/L` 参数预览（仅列出不执行）。

```cmd
:: 安全预览（只列出不执行）
robocopy source dest /MIR /L

:: 实际执行镜像同步
robocopy D:\data E:\backup\data /MIR /Z /R:2 /W:3 /XD temp /XF *.tmp

:: 复制时保留 ACL 权限（需管理员）🔑
robocopy source dest /E /COPYALL
```

#### （4）del / rmdir — 删除

```cmd
:: 删除单个文件
del file.txt

:: 删除所有 .log 文件
del *.log

:: 强制删除只读文件
del /F readonly.txt

:: 递归删除所有 .tmp 文件
del /S *.tmp

:: 删除空目录
rmdir empty_dir

:: 删除目录及其所有内容（危险！）
rmdir /S /Q target_dir
::   /S  删除目录树（目录+所有子目录和文件）
::   /Q  安静模式，不提示确认
```

> ⚠️ **极高风险**：`rmdir /S /Q` 会**直接删除整个目录树，不做确认，且不进回收站**。使用前务必确认路径正确。建议先 `dir` 列出要删除的内容再操作。

#### （5）attrib — 文件属性

```
属性：
  R  只读（Read-only）
  A  存档（Archive）
  S  系统（System）
  H  隐藏（Hidden）
  +  设置属性
  -  清除属性
  /S 应用到子目录
  /D 也处理目录
```

```cmd
:: 查看文件属性
attrib file.txt

:: 设置文件为隐藏
attrib +H secret.txt

:: 取消隐藏和系统属性
attrib -H -S hidden_file.txt

:: 递归显示所有文件的属性
attrib /S /D

:: 给所有 .doc 文件设置只读
attrib +R *.doc
```

> **安全提示**：恶意软件常设置文件为隐藏+系统属性（`attrib +H +S`）来隐藏自身。排查时用 `dir /a` 或 `attrib /S` 查看所有文件。

### 1.4 网络

#### （1）ipconfig — IP 配置

```
核心参数：
  (无参数)    基本 IP 地址、子网掩码、网关
  /all        详细信息（含 MAC、DNS、DHCP 等）
  /release    释放 IP 地址（DHCP）
  /renew      续订 IP 地址（DHCP）
  /flushdns   刷新 DNS 解析缓存
  /displaydns 显示 DNS 解析缓存内容
  /registerdns 刷新 DHCP 租约并注册 DNS
  /allcompartments /all  所有隔离区的详细信息
```

```cmd
:: 查看基本网络配置
ipconfig

:: 查看详细信息（MAC、DNS、DHCP 等）
ipconfig /all

:: 刷新 DNS 缓存（解析异常时常用）
ipconfig /flushdns

:: 查看 DNS 缓存内容
ipconfig /displaydns

:: 释放并重新获取 IP（DHCP 环境）🔑
ipconfig /release
ipconfig /renew
```

#### （2）ping — 连通性测试

```
核心参数：
  -t          持续 ping，直到 Ctrl+C 停止
  -n count    发送请求数（默认 4）
  -l size     发送缓冲区大小（字节，默认 32）
  -f          在数据包中设置"不分段"标志
  -i TTL      生存时间
  -w timeout  等待每次回复的超时时间（毫秒）
  -a          将地址解析为主机名
```

```cmd
:: 测试到 google.com 的连通性
ping google.com

:: 持续 ping（监控网络稳定性）
ping -t 8.8.8.8

:: 发送 10 个大包测试
ping -n 10 -l 1400 192.168.1.1

:: 快速测试 DNS 解析 + 连通性
ping -a server01
```

#### （3）netstat — 网络连接统计

```
核心参数：
  -a        显示所有连接和监听端口
  -n        以数字形式显示地址和端口号（不解析名称，更快）
  -o        显示每个连接关联的进程 ID
  -b        显示每个连接涉及的可执行文件（需管理员）🔑
  -r        显示路由表
  -s        显示各协议统计信息
  -p proto  只显示指定协议的连接（TCP/UDP/ICMP）
  -ano      最常用组合：所有连接 + 数字 + PID
```

```cmd
:: 查看所有网络连接和监听端口（带 PID）
netstat -ano

:: 查找占用 8080 端口的进程
netstat -ano | findstr :8080

:: 查看 TCP 连接
netstat -anp TCP

:: 显示路由表
netstat -r

:: 查看连接对应的程序名（需管理员）🔑
netstat -nb
```

#### （4）tracert — 路由跟踪

```
核心参数：
  -d          不将地址解析成主机名（更快）
  -h max_hops 最大跃点数（默认 30）
  -w timeout  每次回复的等待时间（毫秒）
```

```cmd
:: 跟踪到目标的路由
tracert google.com

:: 不解析名称，快速跟踪
tracert -d 8.8.8.8

:: 限制最大 15 跳
tracert -h 15 server01
```

#### （5）nslookup — DNS 查询

```
交互模式：
  nslookup
  > server 8.8.8.8    切换 DNS 服务器
  > google.com         查询 A 记录
  > set type=mx        查询 MX 记录
  > set type=ns        查询 NS 记录
  > set type=txt       查询 TXT 记录
  > exit               退出

非交互模式：
  nslookup domain [dns-server]
```

```cmd
:: 基本查询（用默认 DNS）
nslookup google.com

:: 指定 DNS 服务器查询
nslookup google.com 8.8.8.8

:: 查询 MX 记录（邮件服务器）
nslookup -type=mx gmail.com

:: 查询 TXT 记录（SPF/DKIM 等）
nslookup -type=txt example.com
```

#### （6）netsh — 网络配置 Shell 🔑

netsh 是一个强大的网络配置命令行工具，支持多种上下文（context）。

```
常用上下文：
  netsh interface       接口配置
  netsh advfirewall     高级防火墙
  netsh wlan            无线网络
  netsh winhttp         WinHTTP 代理
  netsh http            HTTP 服务配置
  netsh int ip          IP 配置
```

```cmd
:: 查看 IP 地址配置（等价于 ipconfig）
netsh interface ip show config

:: 设置静态 IP🔑
netsh interface ip set address "以太网" static 192.168.1.100 255.255.255.0 192.168.1.1

:: 设置 DNS 服务器🔑
netsh interface ip set dns "以太网" static 8.8.8.8 primary

:: 查看防火墙状态
netsh advfirewall show allprofiles state

:: 启用防火墙（所有配置文件）🔑
netsh advfirewall set allprofiles state on

:: 添加防火墙入站规则（允许 8080 端口）🔑
netsh advfirewall firewall add rule name="Allow Port 8080" dir=in action=allow protocol=TCP localport=8080

:: 导出防火墙策略
netsh advfirewall export "C:\backup\firewall.wfw"

:: 查看已保存的 WiFi 配置文件
netsh wlan show profiles

:: 查看 WiFi 密码（需管理员）🔑
netsh wlan show profile name="WiFi名" key=clear
```

> ⚠️ **风险提示**：netsh 可直接修改网络配置和防火墙规则，误操作可能导致网络中断。生产环境操作前需确认影响范围。

### 1.5 net 命令族

`net` 命令是 Windows 网络管理的瑞士军刀，涵盖用户、组、共享、服务等多方面。

| 命令 | 用途 |
|------|------|
| `net user` | 用户账户管理 |
| `net localgroup` | 本地组管理 |
| `net share` | 共享资源管理 |
| `net use` | 网络驱动器映射 |
| `net start / stop` | 启动/停止服务 |
| `net accounts` | 用户账户策略 |
| `net view` | 查看网络计算机/共享 |
| `net session` | 查看会话连接 |
| `net file` | 查看打开的共享文件 |
| `net config` | 查看配置 |

#### （1）net user — 用户管理 🔑

```cmd
:: 列出所有本地用户
net user

:: 查看指定用户详细信息
net user administrator

:: 创建新用户（需管理员）🔑
net user john Password123 /add

:: 删除用户🔑
net user john /delete

:: 修改用户密码🔑
net user john NewPassword456

:: 启用/禁用用户账户🔑
net user john /active:yes
net user john /active:no

:: 设置用户账户永不过期🔑
net user john /expires:never
```

#### （2）net localgroup — 本地组管理 🔑

```cmd
:: 列出所有本地组
net localgroup

:: 查看组成员
net localgroup Administrators

:: 将用户添加到管理员组（提权操作！）🔑
net localgroup Administrators john /add

:: 从组中移除用户🔑
net localgroup Administrators john /delete

:: 创建新组🔑
net localgroup SecurityTeam /add /comment:"安全团队"
```

> ⚠️ **安全提示**：`net localgroup Administrators <user> /add` 是典型的提权操作。安全审计时应定期检查 Administrators 组成员。

#### （3）net share — 共享管理 🔑

```cmd
:: 查看所有共享
net share

:: 创建共享🔑
net share DataShare=C:\Data /remark:"数据共享" /grant:everyone,read

:: 创建带用户限制的共享🔑
net share DataShare=C:\Data /users:10

:: 删除共享🔑
net share DataShare /delete
```

#### （4）net use — 网络驱动器映射

```cmd
:: 查看已映射的网络驱动器
net use

:: 映射网络驱动器
net use Z: \\server\share

:: 映射并指定凭据
net use Z: \\server\share /user:DOMAIN\username password

:: 映射并保存凭据（持久化）
net use Z: \\server\share /persistent:yes

:: 删除映射
net use Z: /delete

:: 删除所有映射
net use * /delete
```

#### （5）net start / net stop — 服务管理 🔑

```cmd
:: 列出所有已启动的服务
net start

:: 启动服务🔑
net start Spooler
net start "Windows Update"

:: 停止服务🔑
net stop Spooler

:: 暂停/继续服务（支持暂停的服务）🔑
net pause Spooler
net continue Spooler
```

> **注意**：服务名有空格时需要加引号。服务名≠服务显示名，可用 `sc query` 查找服务名。

#### （6）net accounts — 账户策略 🔑

```cmd
:: 查看当前账户策略
net accounts

:: 设置密码最小长度为 8 位🔑
net accounts /minpwlen:8

:: 设置密码最长使用期限 42 天🔑
net accounts /maxpwage:42

:: 设置密码最短使用期限 1 天🔑
net accounts /minpwage:1

:: 设置账户锁定阈值（5 次失败锁定）🔑
net accounts /lockoutthreshold:5

:: 设置锁定时间 30 分钟🔑
net accounts /lockoutduration:30
```

### 1.6 磁盘与进程

#### （1）diskpart — 磁盘分区 🔑

diskpart 是交互式磁盘分区工具，功能强大但危险。

```cmd
:: 启动 diskpart（需管理员）🔑
diskpart

:: 常用子命令：
list disk          列出所有磁盘
list volume        列出所有卷
list partition     列出选中磁盘的分区
select disk n      选择磁盘 n
select volume n    选择卷 n
create partition primary size=102400   创建主分区（MB）
format fs=ntfs quick label="Data"     快速格式化为 NTFS
assign letter=D    分配盘符 D
extend             扩展分区（需右侧有未分配空间）
shrink desired=10240   收缩 10 GB
clean              清除磁盘上的所有分区（危险！）
exit               退出
```

> ⚠️ **极高风险**：diskpart 的 `clean` 命令会**清除整个磁盘的分区表**，数据不可恢复。`select disk` 时务必确认选对了磁盘。生产环境操作前务必备份数据。

#### （2）tasklist — 进程列表

```
核心参数：
  /S system         连接远程系统
  /U user           指定用户
  /P password       指定密码
  /M [module]       列出加载指定 DLL 的进程
  /SVC              显示每个进程中的服务
  /V                详细信息（含用户名、CPU 时间、窗口标题）
  /FI filter        过滤器
  /FO format        输出格式（TABLE / LIST / CSV）
```

```cmd
:: 列出所有进程
tasklist

:: 查看进程中的服务
tasklist /svc

:: 查看详细信息（含用户和窗口标题）
tasklist /v

:: 查找特定进程
tasklist | findstr notepad

:: 列出加载了特定 DLL 的进程
tasklist /M kernel32.dll

:: 过滤显示进程名含 chrome 的进程
tasklist /FI "IMAGENAME eq chrome.exe"

:: 输出为 CSV 格式
tasklist /FO CSV /V > processes.csv
```

#### （3）taskkill — 结束进程 🔑

```
核心参数：
  /PID pid        指定进程 ID
  /IM imagename   指定映像名称（支持通配符 *）
  /F              强制终止
  /T              终止进程及其子进程（进程树）
  /FI filter      过滤器
```

```cmd
:: 按 PID 终止进程
taskkill /PID 1234

:: 按映像名终止进程
taskkill /IM notepad.exe

:: 强制终止（不等待程序响应）
taskkill /F /IM notepad.exe

:: 强制终止进程树（进程 + 所有子进程）
taskkill /F /T /PID 1234

:: 批量终止所有 chrome 进程
taskkill /F /IM chrome.exe

:: 按窗口标题终止（支持通配符）
taskkill /FI "WINDOWTITLE eq 无标题 - 记事本"
```

> ⚠️ **风险提示**：`taskkill /F` 会强制终止进程，未保存的数据会丢失。/T 会终止整个进程树，可能误杀相关子进程。

#### （4）sc — 服务控制管理器 🔑

sc 比 `net start/stop` 功能更全面，可查询、配置、创建和删除服务。

```cmd
:: 查看服务状态
sc query Spooler
sc query type= service state= all   :: 所有服务

:: 启动/停止/暂停/继续服务🔑
sc start Spooler
sc stop Spooler
sc pause Spooler
sc continue Spooler

:: 查看服务详细配置
sc qc Spooler

:: 配置服务启动类型（auto/demand/disabled）🔑
sc config Spooler start= auto
sc config Spooler start= disabled

:: 修改服务描述🔑
sc description Spooler "打印后台处理服务"

:: 创建新服务（危险！）🔑
sc create MyService binPath= "C:\service.exe" start= auto DisplayName= "我的服务"

:: 删除服务（危险！）🔑
sc delete MyService
```

> ⚠️ **安全提示**：`sc create` 可以创建任意服务，`sc config binPath=` 可以修改服务可执行路径，是提权和持久化的常用手段。审计时应关注服务的 ImagePath 和启动账户。
>
> **注意语法**：sc 命令的 `=` 后面必须有一个空格（如 `start= auto` 而非 `start=auto`）。

#### （5）wmic — WMI 命令行 🔑

wmic 是 WMI（Windows Management Instrumentation）的命令行接口，功能极其强大。

> **注意**：wmic 在 Windows 10 21H1 之后已被弃用，推荐使用 PowerShell 的 CIM Cmdlet（Get-CimInstance）。

```cmd
:: 查看操作系统信息
wmic os get Name,Version,BuildNumber,LastBootUpTime

:: 查看进程列表
wmic process get Name,ProcessId,CommandLine

:: 查看服务列表
wmic service get Name,State,StartMode

:: 查看已安装软件
wmic product get Name,Version,Vendor

:: 查看启动项
wmic startup get Name,Command,Location

:: 查看用户账户
wmic useraccount get Name,SID,Status

:: 查看逻辑磁盘
wmic logicaldisk get Name,Size,FreeSpace,FileSystem

:: 调用方法：创建进程
wmic process call create "notepad.exe"

:: 调用方法：终止进程
wmic process where name="notepad.exe" call terminate
```

### 1.7 注册表命令

> ⚠️ **通用警告**：修改注册表前务必导出备份。优先使用组策略，不要直接编辑注册表。

#### reg 命令族

| 命令 | 用途 |
|------|------|
| `reg query` | 查询注册表值 |
| `reg add` | 添加/修改注册表值 |
| `reg delete` | 删除注册表值或键 |
| `reg copy` | 复制注册表项 |
| `reg export` | 导出为 .reg 文件 |
| `reg import` | 导入 .reg 文件 |
| `reg save` | 保存整个配置单元（Hive） |
| `reg restore` | 还原配置单元 |
| `reg load` | 加载 Hive 到临时位置 |
| `reg unload` | 卸载加载的 Hive |
| `reg compare` | 比较两个注册表项 |

```cmd
:: ========== reg query 查询 ==========

:: 查询单个键的所有值
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

:: 查询特定值
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "SecurityHealth"

:: 递归查询子键
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /s

:: 查找包含 "chrome" 的值（精确匹配值名）
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v chrome /s

:: 按数据内容搜索（值数据中含 "chrome"）
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /d chrome /s

:: 查询远程计算机的注册表
reg query "\\PC-NAME\HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"


:: ========== reg add 添加/修改 ==========

:: 添加字符串值（REG_SZ）
reg add "HKCU\Software\MyApp" /v "Setting1" /t REG_SZ /d "Value1"

:: 添加 DWORD 值
reg add "HKCU\Software\MyApp" /v "Enabled" /t REG_DWORD /d 1

:: 不提示直接覆盖（加 /f）
reg add "HKCU\Software\MyApp" /v "Setting1" /t REG_SZ /d "NewValue" /f


:: ========== reg delete 删除 ==========

:: 删除单个值（需确认）
reg delete "HKCU\Software\MyApp" /v "Setting1"

:: 不提示直接删除
reg delete "HKCU\Software\MyApp" /v "Setting1" /f

:: 删除整个子键树（危险！）
reg delete "HKCU\Software\MyApp" /f


:: ========== reg export/import 导出/导入 ==========

:: 导出键为 .reg 文件（备份）
reg export "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "C:\backup\run_backup.reg"

:: 从 .reg 文件导入
reg import "C:\backup\run_backup.reg"


:: ========== reg save/restore 保存/还原 Hive ==========

:: 保存 SAM Hive（需 SYSTEM 权限）🔑
reg save HKLM\SAM "C:\backup\sam.hive"

:: 还原 Hive（需重启到安全模式）🔑
reg restore HKLM\SAM "C:\backup\sam.hive"
```

#### regedit 静默导入

```cmd
:: 静默导入 .reg 文件（不显示确认对话框）
regedit /s "C:\backup\settings.reg"

:: 静默导出
regedit /e "C:\backup\export.reg" "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
```

---

## 二、PowerShell Cmdlet

### 2.1 PowerShell 基础

| 概念 | 说明 |
|------|------|
| **Cmdlet** | PowerShell 命令，遵循「动词-名词」命名规范 |
| **管道** | `|` 将前一个命令的输出对象传给下一个命令 |
| **对象** | PowerShell 输出的是 .NET 对象，不是纯文本 |
| **别名** | 兼容 CMD/Linux 命令的别名（如 ls/dir/cd/cat） |
| **模块** | 一组相关 Cmdlet 的集合（如 ActiveDirectory 模块） |
| **执行策略** | 限制脚本运行的安全机制（Restricted/RemoteSigned/AllSigned/Unrestricted/Bypass） |

**动词-名词命名规范**：

| 常用动词 | 含义 | 示例 |
|---------|------|------|
| **Get** | 获取/查询 | Get-Process、Get-Service |
| **Set** | 设置/修改 | Set-Service、Set-ItemProperty |
| **New** | 新建 | New-Item、New-Service |
| **Add** | 添加 | Add-Content、Add-Member |
| **Remove** | 删除 | Remove-Item、Remove-Service |
| **Start** | 启动 | Start-Service、Start-Process |
| **Stop** | 停止 | Stop-Service、Stop-Process |
| **Restart** | 重启 | Restart-Service、Restart-Computer |
| **Export** | 导出到文件 | Export-Csv、Export-Clixml |
| **Import** | 从文件导入 | Import-Csv、Import-Module |
| **Invoke** | 调用/执行 | Invoke-Command、Invoke-WebRequest |
| **Where** | 筛选（管道中） | Where-Object |
| **Select** | 选择属性/对象 | Select-Object |
| **ForEach** | 遍历 | ForEach-Object |
| **Sort** | 排序 | Sort-Object |
| **Format** | 格式化输出 | Format-Table、Format-List |

**获取帮助**：

```powershell
# 查看 Cmdlet 帮助
Get-Help Get-Process
Get-Help Get-Process -Detailed   # 详细帮助
Get-Help Get-Process -Examples   # 仅示例
Get-Help Get-Process -Full       # 完整帮助

# 查看命令示例（最常用）
Get-Help Get-Process -Examples

# 更新帮助（需管理员）🔑
Update-Help
```

### 2.2 文件系统

| Cmdlet | 别名 | 用途 |
|--------|------|------|
| **Get-ChildItem** | dir / ls | 列出目录内容 |
| **Set-Location** | cd / chdir | 切换目录 |
| **New-Item** | md / mkdir | 创建文件或目录 |
| **Copy-Item** | copy / cp | 复制项目 |
| **Move-Item** | move / mv | 移动项目 |
| **Remove-Item** | del / rm / rd | 删除项目 |
| **Rename-Item** | ren / mv | 重命名 |
| **Get-Content** | type / cat | 读取文件内容 |
| **Set-Content** | — | 写入文件内容 |
| **Add-Content** | — | 追加内容到文件 |
| **Get-Item** | — | 获取文件/目录对象 |
| **Get-Acl** | — | 获取访问控制列表 |
| **Set-Acl** | — | 设置访问控制列表 |

#### （1）Get-ChildItem — 列出目录

```
核心参数：
  -Path <path>      指定路径
  -Recurse          递归子目录
  -Filter <string>  过滤器（如 *.txt）
  -Include <string> 包含模式（需 -Recurse）
  -Exclude <string> 排除模式
  -File             只显示文件
  -Directory        只显示目录
  -Hidden           显示隐藏文件
  -Force            显示所有文件（含隐藏/系统）
  -Depth <n>        递归深度
```

```powershell
# 列出当前目录
Get-ChildItem

# 列出所有文件（含隐藏）
Get-ChildItem -Force

# 只列出目录
Get-ChildItem -Directory

# 递归查找所有 .log 文件
Get-ChildItem -Path C:\ -Recurse -Filter *.log -ErrorAction SilentlyContinue

# 查找大于 100MB 的文件
Get-ChildItem -Path C:\ -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 100MB } |
    Sort-Object Length -Descending |
    Select-Object FullName, @{Name="SizeMB";Expression={[math]::Round($_.Length/1MB,2)}}

# 按大小排序（从大到小），取前 10
Get-ChildItem | Sort-Object Length -Descending | Select-Object -First 10
```

#### （2）New-Item / Remove-Item

```powershell
# 创建目录
New-Item -Path "C:\temp\mydir" -ItemType Directory
# 或简写（使用别名 mkdir）
mkdir C:\temp\mydir

# 创建文件
New-Item -Path "C:\temp\test.txt" -ItemType File -Value "Hello World"

# 创建符号链接（需管理员）🔑
New-Item -ItemType SymbolicLink -Path "C:\link.txt" -Target "C:\target.txt"

# 删除文件
Remove-Item -Path "C:\temp\test.txt"

# 删除目录树（强制）
Remove-Item -Path "C:\temp\mydir" -Recurse -Force
```

> ⚠️ **风险提示**：`Remove-Item -Recurse -Force` 会强制删除目录树，且不进回收站。使用前请确认路径正确。

#### （3）Get-Content / Add-Content

```powershell
# 读取文件内容
Get-Content -Path "C:\temp\test.txt"

# 读取前 10 行
Get-Content -Path "C:\temp\test.txt" -TotalCount 10

# 读取最后 5 行（类似 tail）
Get-Content -Path "C:\temp\test.txt" -Tail 5

# 实时监控文件（类似 tail -f）
Get-Content -Path "C:\temp\log.txt" -Wait

# 写入文件（覆盖）
Set-Content -Path "C:\temp\test.txt" -Value "新内容"

# 追加内容
Add-Content -Path "C:\temp\test.txt" -Value "追加的一行"

# 在文件中查找字符串（类似 grep）
Get-Content "C:\temp\log.txt" | Select-String "error"
```

### 2.3 进程与服务

#### （1）进程管理

| Cmdlet | 用途 |
|--------|------|
| **Get-Process** | 获取进程列表 |
| **Stop-Process** | 停止进程 |
| **Start-Process** | 启动进程 |
| **Wait-Process** | 等待进程结束 |

```powershell
# 获取所有进程
Get-Process

# 获取指定进程
Get-Process -Name notepad
Get-Process -Id 1234

# 获取进程的详细信息（命令行、路径等）
Get-Process -Name notepad | Select-Object Name,Id,Path,StartTime,CPU,WorkingSet

# 按 CPU 排序，取前 10
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name,Id,CPU,WS

# 启动进程
Start-Process notepad.exe
Start-Process "C:\Program Files\Mozilla Firefox\firefox.exe"

# 以管理员身份启动🔑
Start-Process powershell -Verb RunAs

# 停止进程
Stop-Process -Name notepad

# 强制停止所有 chrome 进程
Stop-Process -Name chrome -Force

# 查找并停止特定命令行的进程
Get-WmiObject Win32_Process -Filter "name='cmd.exe'" |
    Where-Object { $_.CommandLine -like "*malware*" } |
    ForEach-Object { $_.Terminate() }
```

#### （2）服务管理

| Cmdlet | 用途 |
|--------|------|
| **Get-Service** | 获取服务列表 |
| **Start-Service** | 启动服务 |
| **Stop-Service** | 停止服务 |
| **Restart-Service** | 重启服务 |
| **Suspend-Service** | 暂停服务 |
| **Resume-Service** | 恢复服务 |
| **Set-Service** | 配置服务 |
| **New-Service** | 创建新服务 |
| **Remove-Service** | 删除服务（PowerShell 6+） |

```powershell
# 获取所有服务
Get-Service

# 获取特定服务
Get-Service -Name Spooler

# 查看运行中的服务
Get-Service | Where-Object { $_.Status -eq "Running" }

# 查看设置为自动但未运行的服务（异常检查）
Get-Service | Where-Object { $_.StartType -eq "Automatic" -and $_.Status -ne "Running" }

# 启动/停止/重启服务🔑
Start-Service -Name Spooler
Stop-Service -Name Spooler
Restart-Service -Name Spooler

# 修改服务启动类型🔑
Set-Service -Name Spooler -StartupType Automatic
Set-Service -Name Spooler -StartupType Disabled

# 获取服务的详细信息（可执行文件路径、账户等）
Get-CimInstance Win32_Service -Filter "Name='Spooler'" |
    Select-Object Name, DisplayName, State, StartMode, PathName, StartName

# 查找未加引号的服务路径（提权审计）
Get-CimInstance Win32_Service |
    Where-Object { $_.PathName -notmatch '^".*"$' -and $_.PathName -match '\s' } |
    Select-Object Name, PathName
```

### 2.4 注册表操作

PowerShell 将注册表作为驱动器（Registry Drive）访问，用法类似文件系统。

| 操作 | 命令 |
|------|------|
| 进入注册表 | `Set-Location HKLM:` |
| 列出子键 | `Get-ChildItem HKLM:\SOFTWARE` |
| 读取值 | `Get-ItemProperty` |
| 设置值 | `Set-ItemProperty` |
| 新建值 | `New-ItemProperty` |
| 删除值 | `Remove-ItemProperty` |
| 新建键 | `New-Item` |
| 删除键 | `Remove-Item` |

```powershell
# ========== 查询 ==========

# 列出 HKLM:\SOFTWARE 下的子键
Get-ChildItem HKLM:\SOFTWARE

# 进入注册表驱动器
Set-Location HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion
Get-ChildItem

# 读取 Run 键的所有值
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"

# 读取特定值
(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run").SecurityHealth

# 获取某个值的类型
(Get-Item "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run").GetValueKind("SecurityHealth")


# ========== 修改 ==========

# 创建新的注册表值
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1" -Value "Hello" -PropertyType String

# 修改已有值
Set-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1" -Value "World"

# 创建 DWORD 值
New-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Enabled" -Value 1 -PropertyType DWord

# 删除值
Remove-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1"

# 创建新键
New-Item -Path "HKCU:\Software\MyApp\Settings" -Force

# 删除键
Remove-Item -Path "HKCU:\Software\MyApp\Settings" -Recurse
```

**PropertyType 对应关系**：

| PowerShell 属性类型 | 注册表值类型 |
|-------------------|-------------|
| String | REG_SZ |
| ExpandString | REG_EXPAND_SZ |
| Binary | REG_BINARY |
| DWord | REG_DWORD |
| QWord | REG_QWORD |
| MultiString | REG_MULTI_SZ |

### 2.5 网络与系统

| Cmdlet | 用途 |
|--------|------|
| **Get-NetIPAddress** | 获取 IP 地址 |
| **Get-NetTCPConnection** | 获取 TCP 连接 |
| **Test-Connection** | Ping 测试 |
| **Resolve-DnsName** | DNS 解析 |
| **Test-NetConnection** | 端口连通性测试 |
| **Get-ComputerInfo** | 系统信息 |
| **Get-EventLog / Get-WinEvent** | 事件日志 |
| **Get-HotFix** | 已安装补丁 |

```powershell
# ========== 网络 ==========

# 获取 IP 地址配置
Get-NetIPAddress | Select-Object IPAddress, InterfaceAlias, AddressFamily

# 查看所有 TCP 连接（类似 netstat -ano）
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess,State

# 查找占用 8080 端口的进程
Get-NetTCPConnection -LocalPort 8080 |
    ForEach-Object { Get-Process -Id $_.OwningProcess } |
    Select-Object Name,Id,Path

# Ping 测试
Test-Connection -ComputerName google.com -Count 4

# DNS 解析
Resolve-DnsName -Name google.com
Resolve-DnsName -Name google.com -Type MX

# 测试端口连通性（类似 telnet）
Test-NetConnection -ComputerName google.com -Port 443
Test-NetConnection -ComputerName 192.168.1.1 -Port 3389 -InformationLevel Detailed


# ========== 系统 ==========

# 获取系统信息
Get-ComputerInfo | Select-Object WindowsVersion, OSVersion, CsName, CsProcessors

# 查看已安装补丁
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 HotFixID, InstalledOn

# 查看安全事件日志（最近 20 条）
Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4624} -MaxEvents 20 |
    Select-Object TimeCreated, Id, Message

# 查看登录失败事件（暴力破解检测）
Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4625} -MaxEvents 50 |
    Group-Object -Property @{e={$_.Properties[5].Value}} |
    Sort-Object Count -Descending |
    Select-Object Count, Name

# 查看系统事件日志中的错误
Get-WinEvent -FilterHashtable @{LogName="System"; Level=2} -MaxEvents 20 |
    Select-Object TimeCreated, Id, ProviderName, Message
```

### 2.6 管道与筛选

PowerShell 的管道传递的是对象，不是文本，这是其最大优势。

| Cmdlet | 别名 | 用途 |
|--------|------|------|
| **Where-Object** | ? / where | 筛选对象 |
| **Sort-Object** | sort | 排序 |
| **Select-Object** | select | 选择属性/数量 |
| **ForEach-Object** | % / foreach | 遍历处理 |
| **Group-Object** | group | 分组 |
| **Measure-Object** | measure | 统计（计数/求和/平均） |
| **Format-Table** | ft | 表格格式输出 |
| **Format-List** | fl | 列表格式输出 |
| **Out-GridView** | ogv | 图形化网格视图 |

```powershell
# ========== Where-Object 筛选 ==========

# 获取所有大于 100MB 的进程
Get-Process | Where-Object { $_.WorkingSet -gt 100MB }

# 简写语法（PowerShell 3.0+）
Get-Process | Where-Object WorkingSet -gt 100MB

# 多条件筛选
Get-Service | Where-Object { $_.Status -eq "Running" -and $_.StartType -eq "Automatic" }


# ========== Sort-Object 排序 ==========

# 按内存排序（从大到小）
Get-Process | Sort-Object WorkingSet -Descending

# 多字段排序
Get-Service | Sort-Object Status, DisplayName


# ========== Select-Object 选择 ==========

# 选择指定属性
Get-Process | Select-Object Name, Id, CPU, WS

# 选择前 10 个
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10

# 计算属性（自定义列名）
Get-ChildItem | Select-Object Name, @{Name="SizeKB"; Expression={[math]::Round($_.Length/1KB,2)}}


# ========== ForEach-Object 遍历 ==========

# 对每个进程执行操作
Get-Service | Where-Object { $_.Status -eq "Stopped" -and $_.StartType -eq "Automatic" } |
    ForEach-Object {
        Write-Host "启动服务: $($_.Name)"
        Start-Service $_.Name
    }

# 简写（% 代表 ForEach-Object）
1..10 | % { $_ * 2 }


# ========== 组合使用 ==========

# 统计各状态的服务数量
Get-Service | Group-Object Status | Select-Object Name, Count

# 找出占用内存前 5 的进程，输出为表格
Get-Process |
    Sort-Object WS -Descending |
    Select-Object -First 5 Name, Id, @{N="MemMB";E={[math]::Round($_.WS/1MB,1)}}, CPU |
    Format-Table -AutoSize

# 导出到 CSV
Get-Process |
    Select-Object Name, Id, CPU, WS |
    Export-Csv -Path "C:\temp\processes.csv" -NoTypeInformation -Encoding UTF8
```

### 2.7 导出与输出

| Cmdlet | 用途 |
|--------|------|
| **Export-Csv** | 导出为 CSV 文件 |
| **Import-Csv** | 从 CSV 导入 |
| **ConvertTo-Html** | 转换为 HTML |
| **ConvertTo-Json** | 转换为 JSON |
| **ConvertFrom-Json** | 从 JSON 解析 |
| **Out-File** | 输出到文件 |
| **Out-GridView** | 图形网格视图 |
| **Export-Clixml** | 导出为 XML（保留对象结构） |

```powershell
# 导出进程列表为 CSV
Get-Process | Export-Csv -Path "C:\temp\processes.csv" -NoTypeInformation -Encoding UTF8

# 从 CSV 导入
$data = Import-Csv -Path "C:\temp\processes.csv"

# 生成 HTML 报告
Get-Service |
    Select-Object Name, DisplayName, Status, StartType |
    ConvertTo-Html -Title "服务状态报告" -CssUri "style.css" |
    Out-File "C:\temp\services.html"

# 转换为 JSON
Get-Process | Select-Object Name,Id,CPU,WS | ConvertTo-Json | Out-File "C:\temp\processes.json"

# 输出到文件
Get-Process | Out-File -FilePath "C:\temp\processes.txt" -Width 200

# 图形化查看（交互式）
Get-Service | Out-GridView -Title "服务列表" -PassThru
```

### 2.8 远程管理

PowerShell 远程管理是 Windows 自动化运维的核心功能。

| Cmdlet | 用途 |
|--------|------|
| **Invoke-Command** | 在远程计算机上执行命令 |
| **Enter-PSSession** | 进入远程交互式会话 |
| **New-PSSession** | 创建持久化远程会话 |
| **Get-PSSession** | 获取现有会话 |
| **Remove-PSSession** | 关闭会话 |
| **Enable-PSRemoting** | 启用 PowerShell 远程管理🔑 |

```powershell
# ========== 启用远程管理（目标机，需管理员）🔑 ==========
Enable-PSRemoting -Force

# 配置 WinRM 服务
Set-Service WinRM -StartupType Automatic
Start-Service WinRM


# ========== 单条命令远程执行 ==========

# 在单台远程计算机上执行命令
Invoke-Command -ComputerName Server01 -ScriptBlock { Get-Process }

# 使用凭据
$cred = Get-Credential
Invoke-Command -ComputerName Server01 -Credential $cred -ScriptBlock { Get-Service }

# 在多台计算机上并行执行
Invoke-Command -ComputerName Server01, Server02, Server03 -ScriptBlock {
    Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 3
}


# ========== 交互式远程会话 ==========

# 进入远程会话（类似 SSH）
Enter-PSSession -ComputerName Server01
# 执行命令...
Exit-PSSession


# ========== 持久化会话 ==========

# 创建会话
$session = New-PSSession -ComputerName Server01 -Credential $cred

# 使用会话执行多个命令（共享状态）
Invoke-Command -Session $session -ScriptBlock { $var = "Hello" }
Invoke-Command -Session $session -ScriptBlock { $var }  # 输出 Hello

# 复制文件到远程
Copy-Item -Path "C:\local\file.txt" -Destination "C:\remote\" -ToSession $session

# 从远程复制文件
Copy-Item -Path "C:\remote\file.txt" -Destination "C:\local\" -FromSession $session

# 关闭会话
Remove-PSSession $session
```

> **安全提示**：PowerShell 远程管理使用 WinRM（端口 5985 HTTP / 5986 HTTPS）。生产环境应配置 HTTPS 传输和证书认证，避免使用 HTTP 明文传输。使用 Just Enough Administration (JEA) 限制远程用户权限。

---

## 三、reg 命令族与 PowerShell 注册表提供程序

### 3.1 两种方式对比

| 特性 | reg 命令 | PowerShell 注册表提供程序 |
|------|---------|------------------------|
| **语法** | `reg query/add/delete` | `Get/Set/New-ItemProperty` |
| **类型** | 字符串 + `/t` 参数指定类型 | `-PropertyType` 参数 |
| **返回值** | 文本输出 | .NET 对象（可管道操作） |
| **管道支持** | 不支持 | 支持（管道链式操作） |
| **远程操作** | 支持（`\\computername`） | 支持（Invoke-Command / .NET Remote） |
| **Hive 操作** | reg save/restore/load/unload | 需调用 reg 或 WMI |
| **事务支持** | 不支持 | 支持（Start-Transaction） |
| **学习曲线** | 简单直接 | 稍复杂但更强大 |
| **适用场景** | 简单查询、批处理脚本 | 复杂自动化、管道操作、脚本开发 |

### 3.2 常见操作对照表

| 操作 | reg 命令 | PowerShell |
|------|---------|-----------|
| **查询值** | `reg query "HKLM\SOFTWARE\...\Run"` | `Get-ItemProperty "HKLM:\SOFTWARE\...\Run"` |
| **添加值** | `reg add ... /v name /t REG_SZ /d data` | `New-ItemProperty ... -Name name -Value data -PropertyType String` |
| **修改值** | `reg add ... /v name /d newdata /f` | `Set-ItemProperty ... -Name name -Value newdata` |
| **删除值** | `reg delete ... /v name /f` | `Remove-ItemProperty ... -Name name` |
| **递归查询** | `reg query ... /s` | `Get-ChildItem ... -Recurse` |
| **导出** | `reg export ... file.reg` | `reg export ... file.reg`（PS 无原生导出） |
| **导入** | `reg import file.reg` | `reg import file.reg`（同上） |
| **保存 Hive** | `reg save HKLM\SAM sam.hive` | `reg save ...`（调用外部命令） |

### 3.3 PowerShell 注册表事务

PowerShell 支持注册表操作的事务机制，可在出错时回滚：

```powershell
# 启动事务
Start-Transaction

# 事务内的操作（加 -UseTransaction 参数）
New-Item -Path "HKCU:\Software\TestKey" -UseTransaction
New-ItemProperty -Path "HKCU:\Software\TestKey" -Name "Value1" -Value "test" -PropertyType String -UseTransaction

# 检查操作（不在事务内看不到）
Get-ItemProperty "HKCU:\Software\TestKey" -ErrorAction SilentlyContinue  # 找不到

# 提交事务
Complete-Transaction

# 或回滚事务
# Undo-Transaction
```

> **适用场景**：对多个注册表值进行原子修改，要么全部成功，要么全部回滚。

### 3.4 安全建议

```
注册表操作安全原则：

1. 优先使用组策略（GPO）
   - 组策略有中央管理、回滚、审计等机制
   - 修改可追踪、可批量部署

2. 修改前必须备份
   - 单键：reg export / Backup-Item
   - 系统级：系统还原点
   - 全量：VSS 快照

3. 最小权限原则
   - 能改 HKCU 就别改 HKLM
   - 能用普通用户就别用管理员

4. 测试环境先行
   - 先在测试机验证
   - 确认无误再上生产

5. 操作留痕
   - 记录改了什么、为什么改、谁改的
   - 启用注册表审计（事件 ID 4657）

6. 清理验证
   - 修改后验证是否生效
   - 检查是否有副作用
```

---

## 四、CMD 与 PowerShell 的选择建议

### 4.1 适用场景对比

| 场景 | 推荐 CMD | 推荐 PowerShell | 理由 |
|------|---------|----------------|------|
| 简单文件操作 | ✅ | — | CMD 命令短，上手快 |
| 批处理脚本（.bat/.cmd） | ✅ | — | 兼容性好，所有 Windows 都有 |
| 快速查看信息 | ✅ | — | `ipconfig` / `ping` 等直接敲 |
| 系统信息查询 | — | ✅ | 对象输出，易筛选格式化 |
| 复杂管道操作 | — | ✅ | 对象管道比文本管道强大得多 |
| WMI/CIM 操作 | — | ✅ | PowerShell 原生支持 |
| 注册表操作 | ✅/— | ✅ | 简单用 reg，复杂用 PS 提供程序 |
| 远程管理 | — | ✅ | PowerShell Remoting 是标准方案 |
| 自动化运维 | — | ✅ | 模块丰富，结构化输出 |
| 安全审计 | — | ✅ | 事件日志、过滤、导出报告 |
| 旧系统兼容（WinXP/2003） | ✅ | — | 旧系统可能没装 PowerShell |
| 文本处理（grep/sed 类） | — | ✅ | Select-String + 正则更强 |
| GUI 交互（Out-GridView） | — | ✅ | 图形化输出更直观 |

### 4.2 互操作方式

```
PowerShell 中运行 CMD 命令：
  - 直接输入 CMD 命令即可（大部分有别名）
  - dir / ipconfig / ping 等可直接用
  - cmd /c "dir /s /b" （完整 CMD 语法）

CMD 中运行 PowerShell：
  - powershell -Command "Get-Process"
  - powershell -File script.ps1
  - 调用脚本：powershell -ExecutionPolicy Bypass -File script.ps1

互调用示例：
```

```cmd
:: CMD 中调用 PowerShell 命令
powershell -Command "Get-Service | Where-Object { $_.Status -eq 'Running' } | Export-Csv services.csv"

:: CMD 中调用 PowerShell 脚本
powershell -ExecutionPolicy Bypass -File "C:\scripts\migration.ps1"
```

```powershell
# PowerShell 中调用 CMD 命令（直接输入即可）
ipconfig /all
netstat -ano

# PowerShell 中运行批处理文件
& "C:\scripts\old_script.bat"

# PowerShell 中用 cmd /c 运行复杂 CMD 语法
cmd /c "dir /s /b C:\*.log > logfiles.txt"
```

### 4.3 自动化与脚本建议

```
脚本选择决策树：

脚本用途是什么？
├── 10 行以内的简单任务
│   ├── 只做文件/目录操作 → CMD 批处理
│   └── 涉及对象/筛选 → PowerShell 单行
│
├── 中等复杂度（10-100 行）
│   ├── 旧系统兼容 → CMD 批处理
│   └── 现代系统 → PowerShell 脚本（.ps1）
│
└── 复杂自动化（100+ 行）
    ├── 系统管理 → PowerShell + DSC
    ├── 云运维 → PowerShell + Az 模块
    └── 安全审计 → PowerShell + ADSI / Graph
```

**PowerShell 脚本最佳实践**：

```powershell
# 1. 脚本开头的标准模板
<#
.SYNOPSIS
  脚本功能简介

.DESCRIPTION
  详细描述

.PARAMETER ComputerName
  参数说明

.EXAMPLE
  使用示例
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName
)

# 2. 错误处理
$ErrorActionPreference = "Stop"
try {
    # 主逻辑
}
catch {
    Write-Error "操作失败: $_"
    exit 1
}

# 3. 需要管理员时检查
#Requires -RunAsAdministrator

# 4. 日志记录
Start-Transcript -Path "C:\logs\script.log" -Append
# ... 脚本逻辑 ...
Stop-Transcript
```

---

## 附：优化后的提示词模板

以下是可复用的命令行工具知识查询提示词模板：

```markdown
# 角色
你是一名资深【系统/平台】命令行专家，精通【Shell/命令行工具】的
核心命令、参数和自动化脚本，擅长按功能分类讲解命令、参数和调用案例。

# 任务
请系统介绍【平台】的【命令行工具】核心命令、参数和调用案例。

重要说明：命令数量庞大，无法全部穷举。请按功能分类列出核心命令，
并给出代表性案例。

内容包括：
1. 基础概念（什么是 Shell、内部/外部命令、脚本文件、环境变量）
2. 文件与目录操作（列出、复制、移动、删除、权限、搜索）
3. 系统管理（服务、进程、用户、系统信息、更新）
4. 网络操作（IP配置、连通性、DNS、路由、防火墙）
5. 文本处理（查找、替换、过滤、排序、统计）
6. 配置数据库操作（如注册表/plist/sysctl）
7. 远程管理（远程执行、文件传输）
8. 脚本基础（变量、条件、循环、函数、错误处理）
9. 自动化与安全建议

# 输出要求
- 使用 Markdown
- 按大类、小类组织
- 关键内容用表格对比
- 每个命令附：语法、核心参数、至少一个调用示例、适用场景、风险提示
- 命令示例必须准确、可执行、可复制
- 重要术语中英文对照
- 示例标注适用版本：【当前主流版本】
- 面向：【系统管理员 + 安全工程师】
- 深度：【操作参考 + 安全加固】

# 约束
- 不声称列出全部命令，改为"核心命令 + 功能分类 + 代表性案例"
- 命令示例必须准确
- 高风险命令给出警告
- 需要管理员权限的命令进行标注
- 注册表/配置操作前提示备份
- 用表格对比不同工具的差异
- 最后附"优化后的提示词模板"
```

**使用说明**：将【系统/平台】和【Shell/命令行工具】替换为对应组合，如"Linux + Bash"、"macOS + zsh"、"Python + subprocess"等，即可生成同等深度的命令行知识文档。

---

> **总结**：CMD 和 PowerShell 是 Windows 命令行的两大工具——CMD 轻量简洁、兼容性好，适合简单操作和旧脚本；PowerShell 功能强大、面向对象，适合自动化、远程管理和安全审计。掌握核心命令的语法、参数和场景，理解两种工具的选择原则和互操作方式，是系统管理员和安全工程师的必备技能。记住：命令不在多而在精，熟练掌握核心命令 + 知道查帮助的方法 > 死记硬背所有命令。
