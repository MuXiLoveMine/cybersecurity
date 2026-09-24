# Windows 应急响应流程

### 8.1 应急响应准备

**准备工作**

1. **取证工具包**：准备好应急响应所需的工具
2. **备份策略**：确保有可靠的数据备份
3. **应急预案**：制定详细的应急响应预案
4. **联系人清单**：关键人员联系方式
5. **日志配置**：确保关键日志已启用并集中存储

**应急响应工具清单**

| 类别 | 工具 | 用途 |
|------|------|------|
| 进程分析 | Process Explorer、Process Hacker | 查看进程详情 |
| 进程监控 | Process Monitor | 监控进程行为 |
| 网络分析 | Wireshark、TCPView、netstat | 网络连接分析 |
| 启动项分析 | Autoruns | 查看所有启动项 |
| 内存取证 | FTK Imager、WinPmem、Volatility | 内存镜像和分析 |
| 注册表分析 | Regshot、Registry Explorer | 注册表对比和分析 |
| 文件分析 | Sigcheck、Strings、HashMyFiles | 文件哈希和签名验证 |
| 日志分析 | Event Log Explorer、Log Parser | 事件日志分析 |

### 8.2 事件确认与范围确定

**确认入侵迹象**

1. **防病毒/EDR 告警**：终端防护产品的告警
2. **异常行为**：用户报告的异常情况
3. **网络异常**：异常的网络连接和流量
4. **系统异常**：系统变慢、文件异常、未知进程

**初步信息收集**

```powershell
# 系统基本信息
systeminfo | findstr /i "主机名 操作系统 版本 制造商"

# 当前登录用户
query user

# 网络连接
netstat -ano | findstr /i "estab listen"

# 进程列表
tasklist /v

# 服务列表
sc query type= service state= all

# 计划任务
schtasks /query /fo LIST /v

# 用户账户
net user
net localgroup administrators
```

### 8.3 证据保全

**易失性数据收集顺序**

按照从易失到不易失的顺序收集证据：

1. 内存镜像
2. 网络连接和状态
3. 运行中的进程
4. 打开的文件
5. 系统日志
6. 硬盘镜像

**内存镜像**

```powershell
# 使用 WinPmem 提取内存镜像
winpmem_mini_x64.exe C:\evidence\memory.raw

# 使用 FTK Imager
# File → Capture Memory → 选择保存路径
```

**磁盘镜像**

```powershell
# 使用 FTK Imager 创建磁盘镜像
# File → Create Disk Image → Physical Drive → 选择磁盘 → 选择 E01/RAW 格式

# 使用 dd（Linux 下）
dd if=/dev/sda of=/evidence/disk.dd bs=4096 conv=noerror,sync
```

**日志收集**

```powershell
# 导出事件日志
wevtutil epl System C:\evidence\system.evtx
wevtutil epl Security C:\evidence\security.evtx
wevtutil epl Application C:\evidence\application.evtx

# 导出 PowerShell 日志
wevtutil epl "Windows PowerShell" C:\evidence\powershell.evtx
wevtutil epl "Microsoft-Windows-PowerShell/Operational" C:\evidence\powershell_operational.evtx

# 导出所有日志
wevtutil el > C:\evidence\loglist.txt
foreach ($log in Get-Content C:\evidence\loglist.txt) {
    wevtutil epl $log "C:\evidence\$($log.Replace('/', '_')).evtx"
}
```

### 8.4 入侵分析

**进程分析**

```
检查要点：
1. 未知的可疑进程
2. 进程路径异常（如临时目录、用户目录）
3. 进程签名验证（无签名或无效签名）
4. 异常的子进程关系（如 svchost.exe 启动 cmd.exe）
5. 进程注入迹象（内存中的可疑模块）

工具：
- Process Explorer：查看进程树、验证签名、查看 DLL
- Process Hacker：查看进程内存、句柄、网络连接
- tasklist /m：查看进程加载的 DLL
```

**网络分析**

```
检查要点：
1. 异常的对外连接（特别是未知 IP）
2. 连接到可疑端口（如 4444、8080、8443 等）
3. 大量出站连接（可能是横向移动或 C2 通信）
4. DNS 查询异常（连接到 DGA 域名）

工具：
- netstat -ano：查看网络连接
- TCPView：实时查看网络连接
- Wireshark：抓包分析
```

**启动项分析**

```
检查要点：
1. 未知的启动程序
2. 路径异常的启动项
3. 可疑的服务和驱动
4. 可疑的计划任务
5. WMI 事件订阅
6. 浏览器扩展和插件

工具：
- Autoruns：全面的启动项分析工具
- reg query：手动检查注册表启动项
```

**文件系统分析**

```
检查要点：
1. 最近创建/修改的可疑文件
2. 临时目录中的可执行文件
3. 异常命名的文件（随机字符串名称）
4. 被替换的系统文件
5. 隐藏文件和系统文件

工具：
- dir /a：显示所有文件（包括隐藏和系统文件）
- Sigcheck：验证文件签名
- Strings：提取文件中的字符串
```

### 8.5 遏制与根除

**遏制措施**

1. **网络隔离**：断开受感染主机的网络连接
2. **账户禁用**：禁用被攻陷的账户
3. **密码重置**：重置所有可能泄露的密码
4. **服务停止**：停止恶意服务
5. **进程终止**：终止恶意进程（注意：可能触发自我保护）

**根除措施**

1. **删除恶意文件**：删除所有恶意程序和相关文件
2. **清理持久化**：移除注册表启动项、服务、计划任务等
3. **修复系统文件**：修复被篡改的系统文件（sfc /scannow）
4. **恢复配置**：恢复被修改的系统配置
5. **补丁修复**：安装被利用漏洞的补丁

**系统修复命令**

```powershell
# 系统文件检查
sfc /scannow

# DISM 修复
DISM /Online /Cleanup-Image /RestoreHealth

# 检查磁盘
chkdsk C: /f /r
```

### 8.6 恢复与总结

**恢复步骤**

1. 从干净备份恢复系统（优先选择）
2. 或在确认清除恶意代码后重新接入网络
3. 加强监控，观察是否有复发迹象
4. 修复被利用的漏洞和弱点

**事件报告**

```
应急响应报告应包含：
1. 事件概述：时间、影响范围、严重程度
2. 入侵路径：攻击者是如何进入的
3. 攻击链：攻击者做了什么（时间线）
4. 影响评估：数据泄露、系统破坏、业务影响
5. 处置措施：采取了哪些遏制和根除措施
6. IOC 指标：IP、域名、文件哈希、注册表项等
7. 改进建议：如何防止类似事件再次发生
```

---

---

