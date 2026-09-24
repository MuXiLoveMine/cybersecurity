# Windows 入侵排查

### 2.1 排查思路与原则

**排查思路：由外到内、由表及里、循序渐进**

1. 先看整体状态（进程、网络、用户）
2. 再看启动项和持久化机制
3. 再看日志和历史记录
4. 最后深入分析恶意代码

**排查原则：**
- 保护证据，操作前先备份
- 使用可信工具，避免使用系统自带的可能被篡改的工具
- 记录所有操作
- 由浅入深，逐步深入

### 2.2 进程排查

#### 2.2.1 使用任务管理器（快速查看）

**操作步骤：**
1. 按 `Ctrl+Shift+Esc` 打开任务管理器
2. 查看"详细信息"选项卡
3. 按 CPU、内存排序，查找异常高占用进程
4. 查看进程路径、命令行参数、发行者信息

**异常特征：**
- 进程名称伪装成系统进程（如 `svch0st.exe`，注意是数字0不是字母o）
- 进程路径不在系统目录（如在临时目录、用户目录）
- 无发行者信息或发行者异常
- 命令行参数异常
- CPU/内存占用异常高

#### 2.2.2 使用 Process Explorer（详细分析）

**下载地址**：微软官方 Sysinternals 工具集

**常用操作：**
1. **验证签名**：Options → Verify Signers（验证进程数字签名）
2. **查看进程树**：View → Show Process Tree
3. **查看网络连接**：View → Lower Pane View → Handles 或 DLLs
4. **查看 DLL**：选中进程 → 下方显示加载的 DLL
5. **查看句柄**：选中进程 → 下方显示打开的句柄
6. **挂起进程**：右键进程 → Suspend
7. **结束进程**：右键进程 → Kill Process

**排查重点：**
- 无签名的系统进程（正常系统进程都有微软签名）
- 运行在临时目录的进程
- 可疑的进程名（与系统进程相似但有细微差别）
- 未知发行者的进程

#### 2.2.3 使用命令行工具

```cmd
:: 查看所有进程（包含命令行参数）
wmic process get name,processid,commandline,executablepath /format:list

:: 使用 tasklist 查看进程
tasklist /v
tasklist /svc
tasklist /m

:: 查看进程启动时间
wmic process get name,processid,creationdate

:: 查看特定进程详细信息
wmic process where name="svchost.exe" get name,processid,commandline
```

#### 2.2.4 常见可疑进程

| 可疑特征 | 可能的威胁 |
|----------|-----------|
| `svch0st.exe`（数字0） | 木马伪装成 svchost.exe |
| `expl0rer.exe`（数字0） | 木马伪装成 explorer.exe |
| 位于 `C:\Users\用户名\AppData\Local\Temp\` 的进程 | 恶意软件 |
| 位于 `C:\ProgramData\` 的随机命名进程 | 挖矿程序或木马 |
| CPU 占用持续很高的未知进程 | 挖矿程序 |
| 大量同名进程 | 病毒或蠕虫 |

### 2.3 网络连接排查

#### 2.3.1 使用 netstat 命令

```cmd
:: 查看所有网络连接和监听端口
netstat -ano

:: 查看建立的连接
netstat -ano | findstr "ESTABLISHED"

:: 查看监听端口
netstat -ano | findstr "LISTENING"

:: 查看指定端口的连接
netstat -ano | findstr ":3389"

:: 查看进程对应的网络连接
:: 先获取 PID，再根据 PID 查找
tasklist | findstr "cmd.exe"
netstat -ano | findstr "1234"
```

#### 2.3.2 使用 TCPView 工具

TCPView 是 Sysinternals 工具集中的图形化网络连接查看工具。

**特点：**
- 实时显示所有网络连接
- 显示进程名、本地地址、远程地址、状态
- 彩色标记不同状态的连接
- 可以直接结束进程或关闭连接

**排查重点：**
- 连接到境外 IP 的进程
- 连接到高位端口（非标准端口）的进程
- 大量对外连接（可能是 C2 通信或横向移动）
- 监听非标准端口的进程
- 系统进程的异常网络连接

#### 2.3.3 使用 CurrPorts

CurrPorts 是 NirSoft 出品的免费网络连接查看工具，功能比 TCPView 更丰富。

**特点：**
- 显示更详细的连接信息
- 可以导出连接列表
- 可以标记可疑连接
- 可以查看连接所属进程的详细信息

#### 2.3.4 常见可疑网络连接

| 可疑特征 | 可能的威胁 |
|----------|-----------|
| 连接到已知恶意 IP | C2 通信 |
| 连接到境外高位端口 | 木马回连 |
| 系统进程连接到非标准端口 | 系统进程被注入 |
| 大量 445/SMB 端口连接 | 横向移动 |
| 3389/RDP 端口有大量失败登录 | 暴力破解 |
| 监听非标准端口的系统服务 | 后门 |

### 2.4 日志排查

#### 2.4.1 Windows 事件日志

Windows 事件日志是排查入侵的最重要依据之一。

**日志位置**：`%SystemRoot%\System32\winevt\Logs\`

**主要日志文件：**
- `Security.evtx` - 安全日志（登录、权限等）
- `System.evtx` - 系统日志（服务、启动等）
- `Application.evtx` - 应用程序日志

#### 2.4.2 关键事件 ID

| 事件 ID | 说明 | 重要性 |
|---------|------|--------|
| **4624** | 登录成功 | 高 |
| **4625** | 登录失败 | 高 |
| **4634** | 注销 | 中 |
| **4647** | 用户启动注销 | 中 |
| **4672** | 使用特殊权限登录 | 高 |
| **4688** | 进程创建 | 高 |
| **4697** | 服务安装 | 高 |
| **4698** | 计划任务创建 | 高 |
| **4700** | 计划任务启用 | 中 |
| **4702** | 计划任务更新 | 中 |
| **4720** | 用户创建 | 高 |
| **4722** | 用户账户启用 | 高 |
| **4724** | 尝试重置密码 | 高 |
| **4726** | 用户删除 | 高 |
| **4728** | 成员添加到启用安全的全局组 | 高 |
| **4732** | 成员添加到启用安全的本地组 | 高 |
| **4738** | 用户账户更改 | 中 |
| **4756** | 成员添加到启用安全的通用组 | 高 |
| **4776** | 域控制器尝试验证账户凭据 | 高 |
| **7045** | 服务安装（系统日志） | 高 |
| **1102** | 日志被清除 | 高 |
| **104** | 日志被清除（系统日志） | 高 |

#### 2.4.3 使用事件查看器

**打开方式**：`eventvwr.msc` 或 控制面板 → 管理工具 → 事件查看器

**常用操作：**
1. 筛选事件 ID
   - 右键日志 → 筛选当前日志
   - 输入事件 ID（多个用逗号分隔）
2. 自定义视图
   - 创建自定义视图，筛选特定事件
3. 导出日志
   - 右键日志 → 另存为
   - 可导出为 evtx、txt、csv 格式

#### 2.4.4 使用 wevtutil 命令行

```cmd
:: 导出安全日志
wevtutil epl Security C:\temp\security.evtx

:: 查询特定事件 ID
wevtutil qe Security /q:"*[System/EventID=4624]" /c:10 /f:text

:: 查询指定时间范围内的事件
wevtutil qe Security /q:"*[System[EventID=4625 and TimeCreated[@SystemTime>='2024-01-01T00:00:00']]]" /f:text

:: 查看日志列表
wevtutil el
```

#### 2.4.5 使用 Log Parser

Log Parser 是微软的日志分析工具，支持 SQL 语句查询日志。

```cmd
:: 查询登录失败事件
LogParser "SELECT TimeGenerated,EventID,Message INTO C:\temp\logon_failures.csv FROM Security WHERE EventID=4625" -i:EVT -o:CSV

:: 查询特定用户的登录事件
LogParser "SELECT TimeGenerated,EventID,Message FROM Security WHERE EventID IN (4624;4625) AND Message LIKE '%admin%'" -i:EVT
```

#### 2.4.6 日志分析技巧

1. **登录分析**
   ```cmd
   :: 查看所有登录成功事件，重点关注异常时间、异常IP的登录
   wevtutil qe Security /q:"*[System/EventID=4624]" /f:text | findstr /i "ip address 时间"
   ```

2. **暴力破解检测**
   - 短时间内大量 4625 事件（登录失败）
   - 可能来自同一 IP 或不同 IP
   - 之后可能有 4624 事件（登录成功）

3. **横向移动检测**
   - 4624 事件中的登录类型为 3（网络登录）或 10（远程交互）
   - 登录源地址来自内网其他机器
   - 使用管理员账户登录

4. **持久化检测**
   - 4698/4700/4702：计划任务创建/启用/修改
   - 4697/7045：服务安装
   - 4720/4722：用户创建/启用

### 2.5 启动项排查

#### 2.5.1 使用 Autoruns

Autoruns 是 Sysinternals 工具集中最强大的启动项管理工具。

**下载地址**：微软官方 Sysinternals 工具集

**常用功能：**
1. **验证签名**：Options → Verify Signatures（验证数字签名）
2. **隐藏微软条目**：Options → Hide Microsoft Entries（只显示第三方条目）
3. **扫描启动项**：自动扫描所有自启动位置
4. **禁用启动项**：取消勾选即可禁用
5. **删除启动项**：右键 → Delete

**启动项分类：**
- **Logon**：登录自启动（注册表 Run 项、启动文件夹等）
- **Explorer**：资源管理器相关（Shell 扩展等）
- **Internet Explorer**：IE 相关（BHO、工具栏等）
- **Services**：系统服务
- **Drivers**：驱动程序
- **Scheduled Tasks**：计划任务
- **AppInit DLLs**：AppInit DLL
- **Boot Execute**：启动时执行
- **Image Hijacks**：镜像劫持
- **WMI**：WMI 事件订阅
- **Office**：Office 插件

**排查重点：**
- 无签名的启动项
- 路径异常的启动项（临时目录、用户目录等）
- 可疑名称的启动项
- 新增的启动项（与正常基线对比）

#### 2.5.2 使用 msconfig

**打开方式**：运行 → `msconfig`

**功能：**
- 查看系统配置
- 管理启动项（Win10 已移至任务管理器）
- 管理服务
- 管理启动选项

#### 2.5.3 使用任务管理器

Win10 及以上版本可以在任务管理器中管理启动项：
- 打开任务管理器 → "启动"选项卡
- 查看启动项的名称、发布者、状态、启动影响

#### 2.5.4 常见启动项位置

**注册表启动项：**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run
HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run
```

**启动文件夹：**
```
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\
C:\Users\用户名\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\
```

**计划任务：**
- 位置：`C:\Windows\System32\Tasks\`
- 管理工具：任务计划程序（`taskschd.msc`）

**服务：**
- 注册表位置：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\`
- 管理工具：服务（`services.msc`）

### 2.6 用户账号排查

#### 2.6.1 查看用户账号

```cmd
:: 查看所有用户
net user

:: 查看管理员组用户
net localgroup administrators

:: 查看远程桌面用户组
net localgroup "Remote Desktop Users"

:: 查看用户详细信息
net user 用户名
```

#### 2.6.2 检查可疑用户

**排查重点：**
- 未知的管理员账户
- 名称类似系统账户的隐藏账户（如 `admin$`）
- 最近新增的账户
- 禁用状态但被启用的账户
- 有远程桌面权限的账户

#### 2.6.3 隐藏账户检测

```cmd
:: 查看注册表 SAM 中的用户（需要 SYSTEM 权限）
:: 使用 psexec 以 SYSTEM 权限运行 regedit
psexec -s -i regedit.exe

:: 导航到：
:: HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\Names\
:: 这里列出了所有用户，包括隐藏用户
```

### 2.7 计划任务排查

#### 2.7.1 查看计划任务

```cmd
:: 列出所有计划任务
schtasks /query /fo LIST /v

:: 使用任务计划程序 GUI
taskschd.msc
```

#### 2.7.2 排查重点

- 名称可疑的任务（随机字符、伪装成系统任务）
- 任务执行的程序路径异常
- 任务执行频率异常
- 最近创建的任务
- 以 SYSTEM 权限运行的任务

### 2.8 服务排查

#### 2.8.1 查看服务

```cmd
:: 列出所有服务
sc query state= all

:: 查看服务配置
sc qc 服务名

:: 使用服务管理 GUI
services.msc
```

#### 2.8.2 排查重点

- 名称可疑的服务
- 服务可执行文件路径异常
- 最近安装的服务
- 以 SYSTEM 权限运行的服务
- 描述为空或异常的服务

### 2.9 文件排查

#### 2.9.1 最近修改的文件

```cmd
:: 查看最近 24 小时修改的文件（系统目录）
forfiles /p C:\Windows\System32 /s /d -1 /c "cmd /c echo @file @fdate @ftime"

:: 查看最近 7 天创建的可执行文件
forfiles /p C:\ /s /m *.exe /d -7 /c "cmd /c echo @path @fdate"
```

#### 2.9.2 临时目录排查

```cmd
:: 查看用户临时目录
dir %temp%
dir C:\Users\用户名\AppData\Local\Temp\

:: 查看系统临时目录
dir C:\Windows\Temp\
dir C:\ProgramData\
```

### 2.10 Windows 入侵排查清单

**快速排查清单（15分钟内完成）：**

- [ ] 查看异常进程（任务管理器/Process Explorer）
- [ ] 查看异常网络连接（TCPView/netstat）
- [ ] 查看异常启动项（Autoruns）
- [ ] 查看异常用户（net user / net localgroup administrators）
- [ ] 查看异常服务（services.msc）
- [ ] 查看异常计划任务（任务计划程序）
- [ ] 查看安全日志中的登录事件（4624/4625）
- [ ] 查看安全日志中的进程创建（4688）
- [ ] 查看最近修改的系统文件
- [ ] 查看临时目录中的可疑文件

**深入排查清单：**

- [ ] 内存镜像分析（Volatility）
- [ ] 磁盘镜像分析（FTK/Autopsy）
- [ ] 完整的日志分析（全量日志）
- [ ] Webshell 检测（Web 目录）
- [ ] Rootkit 检测（GMER/RootkitRevealer）
- [ ] 恶意代码分析（沙箱/静态动态分析）
- [ ] 流量分析（Wireshark）
- [ ] 注册表分析（注册表变化检测）
- [ ] 浏览器历史记录分析
- [ ] 最近打开的文件分析

---

---

