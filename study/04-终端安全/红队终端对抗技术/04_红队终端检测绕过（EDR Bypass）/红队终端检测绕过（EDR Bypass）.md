# 红队终端检测绕过（EDR Bypass）

### 4.1 AMSI 绕过

AMSI（Anti-Malware Scan Interface）是 Windows 10 引入的恶意脚本扫描接口，PowerShell、VBScript 等脚本引擎在执行前将内容提交给 AMSI 扫描。绕过思路：

- **反射式 patching**：在内存中将 `amsi.dll` 的 `AmsiScanBuffer` 函数入口修改为直接返回 `S_OK`（`0x80070057`），使扫描结果始终为"干净"
- **反射式加载**：通过反射式加载.NET 程序集绕过 AMSI 的脚本扫描
- **编码混淆**：Base64/XOR 编码 payload 规避签名匹配

> 防御要点：监控 `amsi.dll` 内存修改行为，以及 PowerShell 脚本块日志（ScriptBlock Logging）中的混淆模式。

### 4.2 PowerShell 安全日志绕过

PowerShell 存在多级日志机制：模块日志（Event ID 4103）、脚本块日志（Event ID 4104）、转录日志。绕过思路包括使用 `PowerShell CLM（Constrained Language Mode）` 兼容路径、间接调用 `System.Management.Automation` 程序集，以及使用 C# 直接编译执行替代 PowerShell 脚本。

### 4.3 直接系统调用（Syscall）

EDR 通常通过用户态 hook（如 `ntdll.dll` 中的 API）监控系统调用。直接系统调用技术绕过用户态 hook，直接通过 `syscall` 指令调用内核函数。实现方式：在代码中硬编码或动态解析系统调用号，使用内联汇编 `syscall` 指令直接进入内核。高级 EDR 可能通过内核回调（ETW Threat Intelligence、ObRegisterCallbacks 等）在内核态检测。

### 4.4 Living off the Land（LOTL）

红队利用系统自带的合法工具执行攻击操作，避免投放自定义工具被 EDR 检测。

### 4.5 LOLBins 利用

| 工具 | 用途 | 检测难点 |
|------|------|----------|
| `certutil` | 下载文件、Base64 解码 | 合法证书工具被滥用 |
| `bitsadmin` | 后台下载文件 | 系统内置传输工具 |
| `msiexec` | 执行远程 MSI 包 | 正常安装行为 |
| `rundll32` | 加载任意 DLL | 系统核心工具 |
| `regsvr32` | 注册 COM 组件 | 合法功能被滥用 |
| `wmic` | WMI 命令执行 | 系统管理工具 |
| `mshta` | 执行 HTA 文件 | HTML 应用宿主 |

### 4.6 内存执行无文件攻击

无文件攻击指不在磁盘留下可执行文件，全程在内存中执行 payload。典型方式：通过 PowerShell 将 Shellcode 加载到内存并执行，或通过 .NET 反射式加载程序集。由于磁盘上无恶意文件，传统文件扫描无法检测。

### 4.7 混淆与加密 Shellcode

- **编码器**：对 Shellcode 进行 XOR/AES 加密，运行时在内存中解密后执行
- **分段加载**：将 Shellcode 分割为多段分散加载，规避内存扫描的单段特征
- **动态 API 解析**：不直接引用 API 函数，运行时通过 hash 查找动态解析

### 4.8 C2 框架检测绕过思路

C2（Command & Control）通信是 EDR 检测重点。绕过方向包括：使用合法协议（HTTPS/DNS）伪装正常流量、域名前置（Domain Fronting）、使用云服务作为中继（如 Cloudflare Workers）、Jitter 抖动打乱通信间隔规律性、自定义加密协议规避流量特征匹配。

---

---

## 📋 内容审核与补充建议

> 针对「红队终端检测绕过（EDR Bypass）」部分的内容审核结果：

### 💻 代码示例
- ⚠️ 缺少code相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
