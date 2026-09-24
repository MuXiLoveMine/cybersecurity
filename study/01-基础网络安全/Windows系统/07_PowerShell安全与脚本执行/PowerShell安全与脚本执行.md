# PowerShell安全与脚本执行

### 7.1 PowerShell执行策略

#### 7.1.1 执行策略概述

PowerShell执行策略（Execution Policy）是PowerShell的安全机制，用于控制脚本的执行条件：
- 执行策略不是安全边界（可被轻易绕过），而是防止用户无意中执行脚本的"护栏"
- 执行策略的作用范围：本地计算机、当前用户、当前会话

#### 7.1.2 执行策略级别

| 策略 | 说明 | 安全等级 |
|------|------|----------|
| Restricted | 默认设置，不允许运行脚本，仅可单独执行命令 | 最高 |
| AllSigned | 仅允许运行受信任发布者签名的脚本 | 高 |
| RemoteSigned | 本地脚本可直接运行，来自网络的脚本需要签名 | 中 |
| Unrestricted | 允许运行所有脚本，对网络脚本显示警告 | 低 |
| Bypass | 不阻止任何脚本，无警告或提示 | 最低 |
| Undefined | 未定义，使用更高级别的策略（默认） | - |

#### 7.1.3 执行策略的作用域

| 作用域 | 说明 | 优先级 |
|--------|------|--------|
| MachinePolicy | 计算机组策略 | 最高 |
| UserPolicy | 用户组策略 | 高 |
| Process | 当前进程（仅当前会话有效） | 中 |
| CurrentUser | 当前用户 | 低 |
| LocalMachine | 本地计算机 | 最低 |

优先级从高到低：MachinePolicy > UserPolicy > Process > CurrentUser > LocalMachine

#### 7.1.4 执行策略管理

```powershell
# 查看当前执行策略
Get-ExecutionPolicy
Get-ExecutionPolicy -List          # 查看所有作用域的执行策略

# 设置执行策略（需管理员权限）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope LocalMachine

# 临时更改当前会话执行策略（不修改系统配置）
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 恢复默认
Set-ExecutionPolicy -ExecutionPolicy Undefined -Scope CurrentUser
```

#### 7.1.5 执行策略绕过方法

了解绕过方法有助于理解执行策略的局限性：

```powershell
# 方法1：命令行参数绕过
powershell.exe -ExecutionPolicy Bypass -File script.ps1
powershell.exe -ExecutionPolicy Unrestricted -File script.ps1

# 方法2：管道输入绕过
Get-Content script.ps1 | PowerShell.exe -noprofile -
type script.ps1 | powershell -noprofile -

# 方法3：进程作用域绕过
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process; .\script.ps1"

# 方法4：-Command参数直接执行
powershell -Command "Write-Host 'Hello World'"
```

### 7.2 PowerShell 2.0降级攻击与防御

#### 7.2.1 降级攻击原理

PowerShell 2.0是一个特殊版本，缺乏许多安全功能：
- 不支持PowerShell 5.0引入的脚本块日志
- 不支持AMSI集成
- 不支持约束语言模式的完整实现
- 攻击者通过强制使用PowerShell 2.0来规避检测

```powershell
# 降级攻击示例
powershell.exe -Version 2.0 -Command "恶意代码"
powershell.exe -v 2 -File malicious.ps1
```

#### 7.2.2 检测PowerShell 2.0使用

```powershell
# 检查PowerShell 2.0引擎事件
# 事件ID 400：引擎状态，可用EngineVersion字段判断版本
Get-WinEvent -LogName "Windows PowerShell" -FilterXPath "*[System[EventID=400]]" -MaxEvents 20 |
    Where-Object { $_.Message -match 'EngineVersion=2' }

# 检查是否安装了PowerShell 2.0
Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2
```

#### 7.2.3 防御措施：禁用PowerShell 2.0

```powershell
# Windows 10/Server 2016及以上版本
# 禁用PowerShell 2.0引擎
Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root
Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2

# 验证是否已禁用
Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2
```

```cmd
:: 使用Dism命令
dism /online /disable-feature /featurename:MicrosoftWindowsPowerShellV2Root
dism /online /disable-feature /featurename:MicrosoftWindowsPowerShellV2
```

### 7.3 约束语言模式（Constrained Language Mode）

#### 7.3.1 什么是约束语言模式

约束语言模式（Constrained Language Mode，CLM）限制PowerShell中可用的语言元素：
- 是Windows Defender应用程序控制策略（WDAC/AppLocker）的配套功能
- 当WDAC/AppLocker处于允许模式时，PowerShell自动进入约束语言模式
- 限制了攻击者可利用的PowerShell功能

#### 7.3.2 约束语言模式的限制

**允许的操作**：
- 所有PowerShell cmdlet
- 基本语言元素（变量、函数、循环、条件判断）
- 允许的.NET类型（基本类型、数学函数等）

**禁止/限制的操作**：
- 调用任意.NET方法（仅允许允许列表中的类型）
- 使用Add-Type加载自定义程序集
- 使用New-Object创建任意对象
- 脚本中定义的类（class关键字）
- 反射API的使用
- Windows API调用（P/Invoke）
- 解析CIM/WMI对象的原始对象
- 转换XAML输入

#### 7.3.3 查看当前语言模式

```powershell
# 查看当前语言模式
$ExecutionContext.SessionState.LanguageMode
```

返回值：
- `FullLanguage`：完整语言模式（默认，无限制）
- `ConstrainedLanguage`：约束语言模式
- `NoLanguage`：无语言模式（仅限命令）
- `RestrictedLanguage`：受限语言模式

#### 7.3.4 配置约束语言模式

约束语言模式通常由WDAC/AppLocker自动触发，也可手动测试：

```powershell
# 手动设置当前会话为约束语言模式（仅测试用）
$ExecutionContext.SessionState.LanguageMode = "ConstrainedLanguage"

# 测试：尝试调用禁止的方法
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
# 在约束语言模式下会报错
```

### 7.4 AMSI与PowerShell保护

#### 7.4.1 AMSI概述

AMSI（Antimalware Scan Interface，反恶意软件扫描接口）是Windows 10引入的安全接口：
- 允许应用程序将内容提交给反恶意软件进行扫描
- PowerShell v5.1及以上版本集成了AMSI
- 在脚本执行前对脚本内容进行恶意软件检测
- 支持文件内容、内存内容、交互式输入的扫描

#### 7.4.2 AMSI工作原理

```
脚本内容 → AMSI接口 → 反恶意软件提供程序 → 返回扫描结果 → 决定是否执行
```

- PowerShell在执行前会将脚本内容通过AMSI发送给杀毒软件
- 如果被检测为恶意，PowerShell会抛出错误并阻止执行
- AMSI支持动态扫描：可检测混淆、编码后的恶意脚本

#### 7.4.3 AMSI绕过方法

了解绕过方法有助于更好地防护：

**常见绕过技术**：
- AMSI补丁（内存中修补AMSI函数）
- 字符串混淆和编码
- 降级到PowerShell 2.0（无AMSI）
- 使用.NET而非PowerShell执行恶意代码
- 从非托管代码执行（绕过AMSI Hook）

#### 7.4.4 AMSI防护增强

```powershell
# 检查AMSI是否启用
# PowerShell 5.1+默认启用AMSI
$PSVersionTable.PSVersion

# 确保使用最新版本的PowerShell
# 安装PowerShell 7.x可获得更好的安全防护
```

**最佳实践**：
- 保持Windows和反恶意软件更新
- 启用实时保护
- 使用最新版本的PowerShell
- 配合脚本块日志和模块日志进行监控
- 部署EDR产品增强检测能力

### 7.5 脚本签名与证书

#### 7.5.1 脚本签名概述

脚本签名使用数字证书对PowerShell脚本进行签名：
- 确保脚本的完整性（未被篡改）
- 验证脚本的来源（发布者身份）
- 配合AllSigned执行策略使用

#### 7.5.2 创建代码签名证书

```powershell
# 1. 创建自签名证书（测试用）
$cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=TestCodeSign" -CertStoreLocation "Cert:\CurrentUser\My"

# 2. 查看证书
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert
```

**生产环境建议**：
- 使用企业CA颁发的代码签名证书
- 或购买第三方代码签名证书（如VeriSign、DigiCert）
- 妥善保管私钥，使用硬件安全模块（HSM）

#### 7.5.3 签名脚本

```powershell
# 获取代码签名证书
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1

# 对脚本进行签名
Set-AuthenticodeSignature -FilePath "C:\scripts\test.ps1" -Certificate $cert

# 使用时间戳服务器签名（推荐）
Set-AuthenticodeSignature -FilePath "C:\scripts\test.ps1" -Certificate $cert -TimestampServer "http://timestamp.digicert.com"

# 查看脚本签名
Get-AuthenticodeSignature -FilePath "C:\scripts\test.ps1"
```

#### 7.5.4 管理受信任发布者

```powershell
# 查看受信任发布者
Get-ChildItem -Path Cert:\CurrentUser\TrustedPublisher

# 将证书添加到受信任发布者（当前用户）
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Select-Object -First 1
$store = Get-Item -Path Cert:\CurrentUser\TrustedPublisher
$store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
$store.Add($cert)
$store.Close()
```

### 7.6 PowerShell日志记录

#### 7.6.1 模块日志（Module Logging）

模块日志记录PowerShell模块的管道执行事件：
- 记录使用的cmdlet和参数
- 日志位置：`Microsoft-Windows-PowerShell/Operational`
- 事件ID：4103（管道执行）

```
组策略配置路径：
计算机配置 → 管理模板 → Windows组件 → Windows PowerShell → 打开模块日志记录
```

```powershell
# 注册表配置模块日志
Set-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -Name "EnableModuleLogging" -Value 1 -Type DWord
Set-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -Name "ModuleNames" -Value "*" -Type MultiString
```

#### 7.6.2 脚本块日志（Script Block Logging）

脚本块日志记录所有PowerShell脚本块的内容：
- 记录完整的脚本内容，包括混淆和解密后的代码
- 日志位置：`Microsoft-Windows-PowerShell/Operational`
- 事件ID：4104（创建脚本块）
- 是检测PowerShell恶意活动的最有效方式

```
组策略配置路径：
计算机配置 → 管理模板 → Windows组件 → Windows PowerShell → 打开PowerShell脚本块日志记录
```

```powershell
# 注册表配置脚本块日志
$registryPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force | Out-Null
}
Set-ItemProperty -Path $registryPath -Name "EnableScriptBlockLogging" -Value 1 -Type DWord
```

#### 7.6.3 转录日志（Transcription）

PowerShell转录记录完整的PowerShell会话：
- 记录所有输入命令和输出结果
- 保存为文本文件
- 可配置集中存储位置
- 包含会话元数据（用户、计算机、时间等）

```
组策略配置路径：
计算机配置 → 管理模板 → Windows组件 → Windows PowerShell → 打开PowerShell转录
```

```powershell
# 注册表配置转录
$registryPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription"
if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force | Out-Null
}
Set-ItemProperty -Path $registryPath -Name "EnableTranscripting" -Value 1 -Type DWord
Set-ItemProperty -Path $registryPath -Name "OutputDirectory" -Value "C:\PowerShellTranscripts" -Type String
Set-ItemProperty -Path $registryPath -Name "EnableInvocationHeader" -Value 1 -Type DWord
```

#### 7.6.4 手动启动转录

```powershell
# 启动转录
Start-Transcript -Path "C:\transcripts\session.log"

# 追加到现有转录文件
Start-Transcript -Path "C:\transcripts\session.log" -Append

# 停止转录
Stop-Transcript
```

### 7.7 常用安全命令与安全实践

#### 7.7.1 安全相关命令

```powershell
# 执行策略相关
Get-ExecutionPolicy -List
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 证书相关
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert
Get-AuthenticodeSignature -FilePath script.ps1

# 语言模式
$ExecutionContext.SessionState.LanguageMode

# 版本信息
$PSVersionTable
$PSVersionTable.PSVersion

# 安全策略
Get-ExecutionPolicy -List
```

#### 7.7.2 PowerShell安全最佳实践

**系统配置层面**：
1. 使用最新版本的PowerShell（5.1或7.x）
2. 禁用PowerShell 2.0
3. 启用脚本块日志记录
4. 启用模块日志记录
5. 启用转录日志
6. 配置合理的执行策略
7. 部署WDAC/AppLocker以启用约束语言模式
8. 确保AMSI正常工作，反恶意软件实时保护开启

**使用安全层面**：
1. 不要以管理员身份运行PowerShell（除非必要）
2. 不要随意执行来源不明的脚本
3. 执行前审查脚本内容
4. 对重要脚本进行数字签名
5. 使用受限会话（JEA）进行远程管理
6. 定期审计PowerShell日志

**检测与响应层面**：
1. 监控PowerShell日志中的异常行为
2. 关注事件ID 4104（脚本块日志）中的可疑内容
3. 建立PowerShell恶意活动检测规则
4. 将PowerShell日志接入SIEM系统
5. 定期进行PowerShell安全审计

#### 7.7.3 常见恶意PowerShell特征

检测时应关注以下特征：
- Base64编码命令（-EncodedCommand）
- 调用WebClient下载和执行（DownloadString/Invoke-Expression）
- 大量使用Invoke-Expression（IEX）
- 内存中加载.NET程序集（Assembly.Load）
- 反射API调用
- AMSI绕过代码
- PowerShell降级（-Version 2）
- 执行策略绕过（-ExecutionPolicy Bypass）
- 长时间运行的PowerShell进程

---

---

## 🛠️ 补充：实战拓展

### 命令速查表

```powershell
# PowerShell安全配置审计脚本
function Invoke-PSSecurityAudit {
    Write-Host "=== PowerShell版本信息 ===" -ForegroundColor Cyan
    $PSVersionTable | Format-Table -AutoSize

    Write-Host "=== 执行策略 ===" -ForegroundColor Cyan
    Get-ExecutionPolicy -List | Format-Table -AutoSize

    Write-Host "=== 当前语言模式 ===" -ForegroundColor Cyan
    Write-Host $ExecutionContext.SessionState.LanguageMode

    Write-Host "=== 脚本块日志状态 ===" -ForegroundColor Cyan
    $sbLog = Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -ErrorAction SilentlyContinue
    if ($sbLog) { Write-Host "脚本块日志: $($sbLog.EnableScriptBlockLogging -eq 1)" }
    else { Write-Host "脚本块日志: 未配置" }

    Write-Host "=== 模块日志状态 ===" -ForegroundColor Cyan
    $modLog = Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging" -ErrorAction SilentlyContinue
    if ($modLog) { Write-Host "模块日志: $($modLog.EnableModuleLogging -eq 1)" }
    else { Write-Host "模块日志: 未配置" }

    Write-Host "=== 转录日志状态 ===" -ForegroundColor Cyan
    $trans = Get-ItemProperty -Path "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription" -ErrorAction SilentlyContinue
    if ($trans) { 
        Write-Host "转录日志: $($trans.EnableTranscripting -eq 1)"
        Write-Host "输出目录: $($trans.OutputDirectory)"
    }
    else { Write-Host "转录日志: 未配置" }

    Write-Host "=== PowerShell 2.0状态 ===" -ForegroundColor Cyan
    $v2 = Get-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2 -ErrorAction SilentlyContinue
    Write-Host "PowerShell 2.0状态: $($v2.State)"
}
```

### PowerShell安全加固脚本

```powershell
# PowerShell安全加固配置脚本（需管理员权限）
function Invoke-PSHardening {
    Write-Host "开始PowerShell安全加固..." -ForegroundColor Yellow

    # 1. 设置执行策略
    Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PowerShell\1\ShellIds\Microsoft.PowerShell" -Name "ExecutionPolicy" -Value "RemoteSigned" -Type String
    Write-Host "[+] 已设置执行策略为RemoteSigned" -ForegroundColor Green

    # 2. 启用脚本块日志
    $sbPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"
    if (-not (Test-Path $sbPath)) { New-Item -Path $sbPath -Force | Out-Null }
    Set-ItemProperty -Path $sbPath -Name "EnableScriptBlockLogging" -Value 1 -Type DWord
    Write-Host "[+] 已启用脚本块日志记录" -ForegroundColor Green

    # 3. 启用模块日志
    $modPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\ModuleLogging"
    if (-not (Test-Path $modPath)) { New-Item -Path $modPath -Force | Out-Null }
    Set-ItemProperty -Path $modPath -Name "EnableModuleLogging" -Value 1 -Type DWord
    Set-ItemProperty -Path $modPath -Name "ModuleNames" -Value "*" -Type MultiString
    Write-Host "[+] 已启用模块日志记录" -ForegroundColor Green

    # 4. 启用转录日志
    $transPath = "HKLM:\SOFTWARE\Wow6432Node\Policies\Microsoft\Windows\PowerShell\Transcription"
    if (-not (Test-Path $transPath)) { New-Item -Path $transPath -Force | Out-Null }
    $transDir = "C:\PowerShellTranscripts"
    if (-not (Test-Path $transDir)) { New-Item -Path $transDir -ItemType Directory -Force | Out-Null }
    Set-ItemProperty -Path $transPath -Name "EnableTranscripting" -Value 1 -Type DWord
    Set-ItemProperty -Path $transPath -Name "OutputDirectory" -Value $transDir -Type String
    Set-ItemProperty -Path $transPath -Name "EnableInvocationHeader" -Value 1 -Type DWord
    Write-Host "[+] 已启用转录日志，输出目录: $transDir" -ForegroundColor Green

    # 5. 禁用PowerShell 2.0
    try {
        Disable-WindowsOptionalFeature -Online -FeatureName MicrosoftWindowsPowerShellV2Root -NoRestart -ErrorAction Stop
        Write-Host "[+] 已禁用PowerShell 2.0（需重启生效）" -ForegroundColor Green
    } catch {
        Write-Host "[!] 禁用PowerShell 2.0失败: $_" -ForegroundColor Yellow
    }

    Write-Host "`nPowerShell安全加固完成！" -ForegroundColor Green
}
```

---

