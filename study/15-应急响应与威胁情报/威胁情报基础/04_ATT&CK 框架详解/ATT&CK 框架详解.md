# ATT&CK 框架详解

### 4.1 ATT&CK 概述

**MITRE ATT&CK**（Adversarial Tactics, Techniques, and Common Knowledge）是 MITRE 公司提出的一个全球可访问的基于真实观察的对手战术和技术知识库。

**全称解释：**
- **A**dversarial - 对手的、攻击者的
- **T**actics - 战术（攻击的目标/目的）
- **T**echniques - 技术（实现目标的方法）
- **and** - 和
- **C**ommon - 通用的、常见的
- **K**nowledge - 知识

**ATT&CK 的核心思想：**
- 从攻击者的角度思考问题
- 基于真实的攻击数据（不是理论假设）
- 用统一的框架描述攻击行为
- 社区协作，持续更新

### 4.2 ATT&CK 矩阵结构

ATT&CK 以矩阵（Matrix）的形式呈现：

```
|          战术（列）           |
| 侦察 | 初始访问 | 执行 | ... |
--------------------------------
  技    技术1     技术1    ...
  术    技术2     技术2
  （    技术3     ...
  行）   ...
```

- **列（战术/Tactics）**：攻击的目标/目的，即攻击者"想要做什么"
- **行（技术/Techniques）**：实现战术目标的具体方法，即攻击者"怎么做"
- **子技术（Sub-techniques）**：技术的更细粒度划分

### 4.3 ATT&CK 战术详解

ATT&CK for Enterprise 包含 14 个战术：

#### 战术 1：侦察（Reconnaissance）
**目标**：收集信息，为后续攻击做准备。

**常用技术：**
- 主动扫描（Active Scanning）
- 钓鱼（Phishing，侦察阶段的钓鱼，如钓鱼邮件探测）
- Gather Victim Host Information
- Gather Victim Identity Information
- Gather Victim Network Information
- Gather Victim Org Information
- 搜索开放网站/域名（Search Open Websites/Domains）
- 搜索开放数据库（Search Open Technical Databases）
- 搜索victim 自有网站（Search Victim-Owned Websites）

**说明**：侦察是攻击的第一步，攻击者通过各种方式收集目标信息。

#### 战术 2：资源开发（Resource Development）
**目标**：建立攻击所需的资源和基础设施。

**常用技术：**
- 获取账号（Acquire Account）
- 获取基础设施（Acquire Infrastructure）
- 攻陷基础设施（Compromise Infrastructure）
- 开发能力（Develop Capabilities）
- 建立账户（Establish Accounts）
- 搭建基础设施（Stage Capabilities）

**说明**：攻击者在攻击前需要准备各种资源，如域名、服务器、恶意代码等。

#### 战术 3：初始访问（Initial Access）
**目标**：获得对目标网络/系统的初始访问权限。

**常用技术：**
- 钓鱼（Phishing） - T1566
- 利用面向公众的应用漏洞（Exploit Public-Facing Application） - T1190
- 利用外部远程服务（External Remote Services） - T1133
- 硬件添加（Hardware Additions） - T1200
- 供应链妥协（Supply Chain Compromise） - T1195
- 可移动介质（Replication Through Removable Media） - T1091
- 可信关系（Trusted Relationship） - T1199
- 有效账户（Valid Accounts） - T1078

**案例**：通过钓鱼邮件获取用户凭证，利用 Web 漏洞获取服务器权限。

#### 战术 4：执行（Execution）
**目标**：在目标系统上执行恶意代码。

**常用技术：**
- 命令和脚本解释器（Command and Scripting Interpreter） - T1059
- 利用客户端执行（User Execution） - T1204
- 利用漏洞执行（Exploitation for Client Execution） - T1203
- 计划任务/作业（Scheduled Task/Job） - T1053
- 服务执行（Service Execution） - T1569
- WMI（Windows Management Instrumentation） - T1047
- 引导或登录初始化脚本（Boot or Logon Initialization Scripts） - T1037
- 办公应用程序（Office Application Startup） - T1137

**案例**：用户打开钓鱼邮件附件中的恶意 Word 文档，宏代码执行。

#### 战术 5：持久化（Persistence）
**目标**：保持对系统的持续访问，即使系统重启也不丢失。

**常用技术：**
- 账户操作（Account Manipulation） - T1098
- 引导或登录初始化脚本（Boot or Logon Initialization Scripts） - T1037
- 浏览器扩展（Browser Extensions） - T1176
- 组件固件（Component Firmware） - T1542
- 创建或修改系统进程（Create or Modify System Process） - T1543
- 事件触发执行（Event Triggered Execution） - T1546
- 内核模块和扩展（Kernel Modules and Extensions） - T1547
- 启动或登录自动启动（Boot or Logon Autostart Execution） - T1547
- 办公应用程序启动（Office Application Startup） - T1137
- 计划任务/作业（Scheduled Task/Job） - T1053
- 服务器软件组件（Server Software Component） - T1505
- 服务（Create or Modify System Process: Windows Service）
- 有效账户（Valid Accounts） - T1078

**案例**：攻击者创建后门账户，或添加注册表启动项。

#### 战术 6：权限提升（Privilege Escalation）
**目标**：获取更高的系统权限。

**常用技术：**
- 访问令牌操作（Access Token Manipulation） - T1134
- 利用漏洞提权（Exploitation for Privilege Escalation） - T1068
- 进程注入（Process Injection） - T1055
- 计划任务/作业（Scheduled Task/Job） - T1053
- 服务（Services）
- 引导或登录自动启动（Boot or Logon Autostart Execution） - T1547
- 内核模块和扩展（Kernel Modules and Extensions） - T1547
- 有效账户（Valid Accounts） - T1078

**案例**：攻击者利用系统漏洞从普通用户提升到 SYSTEM/root 权限。

#### 战术 7：防御绕过（Defense Evasion）
**目标**：躲避安全检测和防护。

**常用技术：**
- 禁用或修改安全工具（Disable or Modify Tools） - T1562
- 混淆文件和信息（Obfuscated Files or Information） - T1027
- 防虚拟化/反调试（Virtualization/Sandbox Evasion） - T1497
- 系统配置修改（Modify System Configuration） - T1601
- 间接命令执行（Indirect Command Execution） - T1202
- 进程注入（Process Injection） - T1055
- 根套件（Rootkit） - T1014
- 有效账户（Valid Accounts） - T1078
- 系统二进制文件代理执行（Signed Binary Proxy Execution） - T1218
- 伪装/伪装（Masquerading） - T1036
- 文件删除（File Deletion） - T1070
- 清除命令历史（Clear Command History） - T1070

**案例**：攻击者使用加壳、混淆技术躲避杀毒软件检测。

#### 战术 8：凭证访问（Credential Access）
**目标**：获取账号密码等凭证信息。

**常用技术：**
- 凭证转储（Credential Dumping） - T1003
  - LSASS 内存（LSASS Memory） - T1003.001
  - SAM 数据库（Security Account Manager） - T1003.002
  - NTDS（NTDS） - T1003.003
  - 凭证管理器（Credential Manager） - T1003.005
- 键盘记录（Input Capture: Keylogging） - T1056
- 浏览器凭证（Credentials from Password Stores） - T1555
- 网络嗅探（Network Sniffing） - T1040
- 暴力破解（Brute Force） - T1110
- 凭证钓鱼（Credential Phishing）
- 未授权的密码重置（Unauthorized Password Reset）

**案例**：攻击者使用 Mimikatz 从内存中提取明文密码和哈希。

#### 战术 9：发现（Discovery）
**目标**：探索系统和网络，了解环境。

**常用技术：**
- 账户发现（Account Discovery） - T1087
- 应用窗口发现（Application Window Discovery） - T1010
- 浏览器书签发现（Browser Information Discovery） - T1217
- 文件和目录发现（File and Directory Discovery） - T1083
- 网络服务发现（Network Service Discovery） - T1046
- 网络共享发现（Network Share Discovery） - T1135
- 网络拓扑发现（Network Sniffing） - T1040
- 权限组发现（Permission Groups Discovery） - T1069
- 进程发现（Process Discovery） - T1057
- 远程系统发现（Remote System Discovery） - T1018
- 软件发现（Software Discovery） - T1518
- 系统信息发现（System Information Discovery） - T1082
- 系统网络配置发现（System Network Configuration Discovery） - T1016
- 系统网络连接发现（System Network Connections Discovery） - T1049
- 系统所有者/用户发现（System Owner/User Discovery） - T1033
- 系统服务发现（System Service Discovery） - T1033

**案例**：攻击者执行 `whoami`、`ipconfig`、`net view` 等命令了解系统环境。

#### 战术 10：横向移动（Lateral Movement）
**目标**：从一台机器移动到网络中的其他机器。

**常用技术：**
- 利用远程服务（Remote Services） - T1021
  - SSH（SSH） - T1021.004
  - RDP（Remote Desktop Protocol） - T1021.001
  - SMB/Admin Shares（SMB/Windows Admin Shares） - T1021.002
  - WinRM（Windows Remote Management） - T1021.006
  - VNC（VNC） - T1021.005
- 传递哈希（Pass the Hash） - T1550.002
- 传递票据（Pass the Ticket） - T1550.003
- 替代身份验证材料（Use Alternate Authentication Material） - T1550
- 内部幽灵（Internal Spearphishing）
- 利用远程服务漏洞（Exploitation of Remote Services） - T1210
- 软件部署工具（Software Deployment Tools） - T1072

**案例**：攻击者使用获取到的管理员哈希，通过 PsExec 登录其他服务器。

#### 战术 11：收集（Collection）
**目标**：收集有价值的数据和信息。

**常用技术：**
- 音频捕获（Audio Capture） - T1123
- 剪贴板数据（Clipboard Data） - T1115
- 数据存贮设备（Data from Removable Media） - T1025
- 电子邮件收集（Email Collection） - T1114
- 文件和目录收集（Data from Local System） - T1005
- 信息窃取（Input Capture） - T1056
- 屏幕截图（Screen Capture） - T1113
- 视频捕获（Video Capture） - T1123
- 浏览器信息（Browser Information Discovery） - T1217
- 数据从网络共享收集（Data from Network Shared Drive） - T1039
- 数据从信息库收集（Data from Information Repositories） - T1213

**案例**：攻击者扫描并收集目标系统中的文档、表格等敏感文件。

#### 战术 12：命令与控制（Command and Control，C2）
**目标**：攻击者与被控系统通信，发送指令、接收数据。

**常用技术：**
- 应用层协议（Application Layer Protocol） - T1071
  - Web 协议（Web Protocols） - T1071.001
  - DNS 协议（DNS） - T1071.004
  - 邮件协议（Mail Protocols） - T1071.003
- 非应用层协议（Non-Application Layer Protocol） - T1095
- 加密通道（Encrypted Channel） - T1573
- 协议隧道（Protocol Tunneling） - T1572
- 代理（Proxy） - T1090
- 远程访问工具（Remote Access Software） - T1219
- 流量签名（Traffic Signaling） - T1049
- 连接代理（Connection Proxy） - T1090
- 滥用连接控件（Abuse Elevation Control Mechanism）

**案例**：恶意软件通过 HTTPS 与 C2 服务器通信，流量伪装成正常 Web 流量。

#### 战术 13：数据渗出（Exfiltration）
**目标**：将窃取的数据从目标网络传输出去。

**常用技术：**
- 通过 C2 通道渗出（Exfiltration Over C2 Channel） - T1041
- 通过其他网络渠道渗出（Exfiltration Over Alternative Protocol） - T1048
- 通过物理介质渗出（Exfiltration Over Physical Medium） - T1052
- 自动渗出（Automated Exfiltration） - T1020
- 计划传输（Scheduled Transfer） - T1029
- 传输数据大小限制限制（Exfiltration Over Asymmetric Encrypted Non-C2 Protocol）
- 数据压缩（Data Compressed） - T1560
- 数据加密（Data Encrypted） - T1560

**案例**：攻击者将窃取的数据加密后，通过 FTP 上传到境外服务器。

#### 战术 14：影响（Impact）
**目标**：对目标系统、数据或业务造成破坏和影响。

**常用技术：**
- 数据破坏（Data Destruction） - T1485
- 拒绝服务（Denial of Service） - T1498
- 磁盘结构擦除（Disk Structure Wipe） - T1561
- 资源劫持（Resource Hijacking） - T1496（如挖矿）
- 勒索软件（Data Encrypted for Impact） - T1486
- 服务停止（Service Stop） - T1489
- 固件破坏（Firmware Corruption） - T1495
- 账户访问权限删除（Account Access Removal） - T1531
- 数据篡改（Data Manipulation） - T1565
- 系统 shutdown/reboot（System Shutdown/Reboot） - T1529
- 抑制恢复（Inhibit System Recovery） - T1490

**案例**：勒索软件加密用户文件并索要赎金，造成业务中断和数据损失。

### 4.4 ATT&CK 的矩阵类型

MITRE ATT&CK 包含多个矩阵：

| 矩阵 | 说明 | 适用场景 |
|------|------|----------|
| **Enterprise** | 企业矩阵 | 企业网络和系统 |
| **Mobile** | 移动设备矩阵 | 移动设备（iOS、Android） |
| **ICS** | 工业控制系统矩阵 | 工业控制系统（ICS/SCADA） |
| **Cloud** | 云矩阵 | 云环境 |

### 4.5 ATT&CK 的应用

#### 4.5.1 威胁建模
- 使用 ATT&CK 框架梳理可能的攻击路径
- 评估自身防御覆盖情况
- 识别防御盲区

#### 4.5.2 检测规则开发
- 针对具体技术开发检测规则
- 用 ATT&CK 标签管理检测规则
- 评估检测覆盖率

#### 4.5.3 红队评估
- 基于 ATT&CK 规划红队行动
- 用 ATT&CK 描述红队活动
- 评估蓝队检测能力

#### 4.5.4 威胁情报
- 用 ATT&CK 描述攻击组织的 TTP
- 标准化威胁情报格式
- 情报关联和共享

#### 4.5.5 安全评估
- 使用 ATT&CK 评估安全能力
- 识别防御差距
- 指导安全建设

### 4.6 ATT&CK 导航器

ATT&CK Navigator 是一个可视化工具，用于展示和操作 ATT&CK 矩阵。

**主要功能：**
- 可视化展示 ATT&CK 矩阵
- 标记覆盖的技术（检测/防护）
- 对比不同组织的覆盖情况
- 标记攻击组织使用的技术
- 导出和分享图层

**应用场景：**
- 展示检测覆盖率
- 展示攻击组织 TTP
- 红蓝对抗评估
- 安全能力评估

---

---

