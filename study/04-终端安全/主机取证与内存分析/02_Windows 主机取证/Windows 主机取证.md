# Windows 主机取证

### 2.1 事件日志分析

Windows 事件日志是主机取证最重要的数据源之一，包含安全、系统、应用程序等多类日志。

**关键日志文件**：

```
日志文件位置: C:\Windows\System32\winevt\Logs\

安全日志:      Security.evtx
系统日志:      System.evtx
应用程序日志:  Application.evtx
PowerShell:    Windows PowerShell.evtx
                           PowerShell%4Operational.evtx
防火墙日志:    Microsoft-Windows-Windows Firewall With Security%4Operational.evtx
Sysmon日志:    Microsoft-Windows-Sysmon%4Operational.evtx
```

**关键事件 ID**：

| 事件 ID | 日志类型 | 含义 |
|---------|----------|------|
| 4624 | Security | 登录成功（记录登录类型） |
| 4625 | Security | 登录失败（暴力破解检测） |
| 4634 | Security | 注销 |
| 4648 | Security | 显式凭据登录（RunAs） |
| 4672 | Security | 特权用户登录 |
| 4688 | Security | 进程创建 |
| 4698 | Security | 计划任务创建 |
| 4720 | Security | 用户账户创建 |
| 4722 | Security | 用户账户启用 |
| 4732 | Security | 成员加入安全组 |
| 4776 | Security | NTLM 认证尝试 |
| 4825 | Security | 网络共享违规 |
| 7045 | System | 服务安装 |
| 1 | Sysmon | 进程创建（含命令行） |
| 3 | Sysmon | 网络连接 |
| 7 | Sysmon | 镜像加载（DLL加载） |
| 8 | Sysmon | 远程线程创建 |
| 11 | Sysmon | 文件创建 |
| 13 | Sysmon | 注册表值设置 |

**日志分析命令**：

```powershell
# 使用 PowerShell 分析事件日志

# 导出安全日志
wevtutil epl Security C:\forensics\Security.evtx

# 查询登录失败事件（暴力破解检测）
Get-WinEvent -FilterHashtable @{
    LogName='Security'; 
    Id=4625
} | Select-Object TimeCreated, 
    @{N='User';E={$_.Properties[5].Value}},
    @{N='SourceIP';E={$_.Properties[19].Value}},
    @{N='LogonType';E={$_.Properties[10].Value}}
    | Format-Table -AutoSize

# 检测 4624 登录成功中的网络登录（类型3）
Get-WinEvent -FilterHashtable @{
    LogName='Security';
    Id=4624
} | Where-Object {
    $_.Properties[8].Value -eq 3  # LogonType 3 = 网络登录
} | Select-Object TimeCreated,
    @{N='User';E={$_.Properties[5].Value}},
    @{N='SourceIP';E={$_.Properties[18].Value}}
    | Format-Table -AutoSize

# 检测横向移动 - 查找特定用户的多主机登录
Get-WinEvent -FilterHashtable @{
    LogName='Security';
    Id=4624
} | Group-Object {
    $_.Properties[5].Value  # 按用户名分组
} | Where-Object {
    $_.Group | Select-Object -ExpandProperty Message |
    Select-String "Network Information" -Quiet
} | Select-Object Count, Name

# 检测进程创建（需启用 4688 审计+命令行记录）
Get-WinEvent -FilterHashtable @{
    LogName='Security';
    Id=4688
} | Where-Object {
    $_.Message -match 'powershell|cmd.exe|certutil|mimikatz|procdump'
} | Select-Object TimeCreated, 
    @{N='Process';E={$_.Properties[5].Value}},  # 新进程
    @{N='Parent';E={$_.Properties[13].Value}},   # 父进程
    @{N='CmdLine';E={$_.Properties[8].Value}}     # 命令行
    | Format-List

# 检测服务安装（恶意服务/持久化）
Get-WinEvent -FilterHashtable @{
    LogName='System';
    Id=7045
} | Select-Object TimeCreated,
    @{N='Service';E={$_.Properties[0].Value}},
    @{N='Path';E={$_.Properties[1].Value}}
    | Format-Table -AutoSize
```

### 2.2 注册表取证

```
Windows 注册表取证关键位置:

# 自启动项（持久化）
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon (Userinit, Shell)

# 服务（持久化）
HKLM\SYSTEM\CurrentControlSet\Services\

# 计划任务（持久化）
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\TaskCache\

# AppInit_DLLs（DLL注入）
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows\AppInit_DLLs

# 最近活动
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs\
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU\
HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths\

# USB 设备历史
HKLM\SYSTEM\CurrentControlSet\Enum\USBSTOR\
HKLM\SYSTEM\MountedDevices
```

```powershell
# 注册表取证脚本

# 导出注册表配置单元
reg save HKLM\SYSTEM C:\forensics\SYSTEM.hiv
reg save HKLM\SOFTWARE C:\forensics\SOFTWARE.hiv
reg save HKLM\SAM C:\forensics\SAM.hiv
reg save HKLM\SECURITY C:\forensics\SECURITY.hiv
reg save HKLM\HARDWARE C:\forensics\HARDWARE.hiv

# 查找 Run 键自启动项
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" |
    Format-List

# 查找可疑服务
Get-WmiObject Win32_Service |
    Where-Object {
        $_.PathName -match 'temp|appdata|programdata|public'
    } | Select-Object Name, DisplayName, PathName, StartMode |
    Format-List

# USB 设备历史分析
$usbDevices = Get-ChildItem "HKLM:\SYSTEM\CurrentControlSet\Enum\USBSTOR" |
    Get-ChildItem | Get-ChildItem
foreach ($device in $usbDevices) {
    $props = Get-ItemProperty $device.PSPath
    Write-Output "设备: $($props.FriendlyName)"
    Write-Output "  序列号: $($device.PSChildName)"
    Write-Output "  类: $($props.Class)"
}
```

### 2.3 文件系统取证

```
文件系统取证要点:

# NTFS 关键时间戳（MACE）
M - Modified    （修改时间 - 文件内容最后修改）
A - Accessed    （访问时间 - 最后被读取）
C - Changed     （MFT修改时间 - 元数据变更）
E - Entry      （创建时间 - MFT记录创建）

# 可疑文件位置
C:\Users\*\AppData\Local\Temp\          # 临时文件释放
C:\Users\*\AppData\Roaming\              # 恶意软件常用目录
C:\Users\*\AppData\Local\                # 持久化常见位置
C:\ProgramData\                          # 系统级持久化
C:\Windows\Temp\                         # 系统临时目录
C:\Windows\System32\                    # DLL替换攻击
C:\$Recycle.Bin\                        # 回收站（删除文件恢复）

# Prefetch 文件（程序执行历史）
C:\Windows\Prefetch\*.pf
# 记录了程序执行的次数、时间、引用的文件

# Amcache.hve（程序执行记录）
# C:\Windows\AppCompat\Programs\Amcache.hve
# 记录了执行过的程序路径、SHA-1 哈希等
```

### 2.4 USN 日志分析

**USN（Update Sequence Number）日志** 是 NTFS 的变更日志，记录文件系统上所有的文件变更操作。

```powershell
# 使用 fsutil 查看 USN 日志
fsutil usn readjournal C: |
    Select-String "Add|Delete|Modify" |
    Select-Object -First 100

# 使用第三方工具分析 USN
# Tool: UsnJrnl2csv / python-evt
# python usn_parser.py C:\forensics\usnjrnl.bin -o usn_output.csv
```

```python
# Python USN 日志解析示例
import struct

def parse_usn_journal(journal_path):
    """
    解析 USN 日志记录
    """
    with open(journal_path, 'rb') as f:
        # 跳过 $J 的 $DATA 属性头部
        # 实际解析需要先从 MFT 中定位 $J
        offset = 0
        records = []
        
        while offset < os.path.getsize(journal_path):
            f.seek(offset)
            data = f.read(8)
            if len(data) < 8:
                break
            
            record_len = struct.unpack('<I', data[:4])[0]
            if record_len == 0:
                offset += 4
                continue
            
            f.seek(offset)
            record_data = f.read(record_len)
            
            # 解析 USN 记录结构
            # 偏移 0:  RecordLength (4 bytes)
            # 偏移 4:  MajorVersion (2 bytes)
            # 偏移 6:  MinorVersion (2 bytes)
            # 偏移 8:  FileReferenceNumber (8 bytes)
            # 偏移 16: ParentFileReference (8 bytes)
            # 偏移 24: Usn (8 bytes)
            # 偏移 32: TimeStamp (8 bytes)
            # 偏移 40: Reason (4 bytes) - 变更原因标志
            # 偏移 44: SourceInfo (4 bytes)
            # 偏移 48: SecurityId (4 bytes)
            # 偏移 52: FileAttributes (4 bytes)
            # 偏移 56: FileNameLength (2 bytes)
            # 偏移 58: FileNameOffset (2 bytes)
            # 偏移 60: FileName (Unicode)
            
            reason = struct.unpack('<I', record_data[40:44])[0]
            file_ref = struct.unpack('<Q', record_data[8:16])[0]
            
            reason_map = {
                0x00000001: 'DATA_OVERWRITE',
                0x00000002: 'DATA_EXTEND',
                0x00000004: 'DATA_TRUNCATION',
                0x00000010: 'NAMED_DATA_OVERWRITE',
                0x00000100: 'FILE_CREATE',
                0x00000200: 'FILE_DELETE',
                0x00000400: 'EA_CHANGE',
                0x00000800: 'SECURITY_CHANGE',
                0x00001000: 'RENAME_OLD_NAME',
                0x00002000: 'RENAME_NEW_NAME',
                0x00008000: 'BASIC_INFO_CHANGE',
                0x00010000: 'CLOSE',
            }
            
            reasons = [name for bit, name in reason_map.items() 
                       if reason & bit]
            
            name_len = struct.unpack('<H', record_data[56:58])[0]
            name = record_data[60:60+name_len].decode('utf-16-le')
            
            records.append({
                'file': name,
                'actions': reasons,
                'file_ref': file_ref
            })
            
            offset += record_len
        
        return records
```

---

---

