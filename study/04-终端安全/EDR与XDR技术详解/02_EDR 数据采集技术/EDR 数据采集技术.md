# EDR 数据采集技术

### 2.1 ETW（Event Tracing for Windows）

**ETW** 是 Windows 内核提供的高性能事件追踪机制，EDR 广泛使用 ETW 采集系统行为数据。

**ETW 架构**：

```
┌────────────────────────────────────────┐
│           EDR Agent (消费者)             │
│  EnableTraceEx / EventRegister          │
└───────────────────┬────────────────────┘
                    │ 接收事件
┌───────────────────▼────────────────────┐
│           ETW 核心 (内核层)              │
│  事件缓冲区 / 事件会话 / 事件 Provider   │
└──────┬──────┬──────┬──────┬────────────┘
       │      │      │      │
┌──────▼┐ ┌──▼──┐ ┌▼────┐ ┌▼──────────┐
│内核   │ │磁盘  │ │网络 │ │进程/线程   │
│Provider│ │IO   │ │Provider│Provider │
└──────┘ └────┘ └────┘ └──────────┘
```

**关键 ETW Provider**：

| Provider GUID | 名称 | 采集内容 |
|---------------|------|----------|
| `22fb2cd6-0e7b-422b-a0c7-2f1f1b29...` | Microsoft-Windows-Kernel-Process | 进程创建/终止/映像加载 |
| `ed1fe634-cd9e-4c9d-97d3-4e7e1b0a...` | Microsoft-Windows-Kernel-File | 文件操作 |
| `2021bd22-286b-4a88-9e9a-1f6a...` | Microsoft-Windows-Kernel-Network | 网络连接 |
| `ff56960e-4e70-4b95-9f8c-9e2c...` | Microsoft-Windows-Kernel-Registry | 注册表操作 |
| `e41412e8-9bf7-4be0-9ae3...` | Microsoft-Antimalware-ScanInterface (AMSI) | 脚本内容 |

**ETW 采集代码示例（C#）**：

```csharp
using System.Diagnostics.Tracing;

// 启动 ETW 会话采集进程创建事件
public class ProcessEventListener : EventListener
{
    private const int EventId_ProcessStart = 1;
    private const int EventId_ProcessStop = 2;
    
    protected override void OnEventSourceCreated(EventSource eventSource)
    {
        if (eventSource.Name == "Microsoft-Windows-Kernel-Process")
        {
            EnableEvents(eventSource, EventLevel.Informational, 
                (EventKeywords)0x10); // ProcessKeyword = 0x10
        }
    }
    
    protected override void OnEventWritten(EventWrittenEventArgs eventData)
    {
        switch (eventData.EventId)
        {
            case EventId_ProcessStart:
                var pid = eventData.Payload["ProcessID"];
                var imageName = eventData.Payload["ImageName"];
                var parentPid = eventData.Payload["ParentProcessID"];
                // 上报至 EDR 管理平台
                Console.WriteLine($"[进程创建] PID={pid} " +
                    $"Image={imageName} ParentPID={parentPid}");
                break;
            case EventId_ProcessStop:
                var exitPid = eventData.Payload["ProcessID"];
                var exitCode = eventData.Payload["ExitCode"];
                Console.WriteLine($"[进程退出] PID={exitPid} " +
                    $"ExitCode={exitCode}");
                break;
        }
    }
}

// C++ 原生 ETW 采集
// #include <evntrace.h>
// #include <tdh.h>
// 
// EVENT_TRACE_LOGFILE logFile = {0};
// logFile.LoggerName = KERNEL_LOGGER_NAME;
// logFile.EventRecordCallback = OnEventRecord;  // 回调函数
// TRACEHANDLE hTrace = OpenTrace(&logFile);
// ProcessTrace(&hTrace, 1, NULL, NULL);
```

### 2.2 内核回调

EDR 驱动通过注册内核回调函数来监控系统行为，这是最底层、最可靠的数据采集方式。

**关键内核回调函数**：

```c
// 内核驱动注册回调示例 (WDM/WDF 驱动)

// 1. 进程创建/退出通知
VOID ProcessNotifyCallback(
    HANDLE ParentId,     // 父进程PID
    HANDLE ProcessId,    // 进程PID
    BOOLEAN Create       // TRUE=创建, FALSE=退出
)
{
    if (Create) {
        // 记录进程创建事件
        PEPROCESS process;
        PsLookupProcessByProcessId(ProcessId, &process);
        // 获取进程映像路径、命令行等信息
    }
}

// 注册: PsSetCreateProcessNotifyRoutineEx(ProcessNotifyCallback, FALSE);

// 2. 映像加载通知
VOID ImageLoadCallback(
    PIMAGE_INFO ImageInfo,  // 映像信息
    HANDLE ProcessId,       // 加载进程PID
)
{
    // 检测 DLL 注入、可疑模块加载
    if (ImageInfo->ImageFullPathName) {
        // 记录: 进程加载了哪个 DLL/SYS
    }
}

// 注册: PsSetLoadImageNotifyRoutine(ImageLoadCallback);

// 3. 句柄操作通知
VOID HandleCallback(
    PSYSTEM_HANDLE_INFORMATION HandleInfo
)
{
    // 检测跨进程句柄操作（如 OpenProcess 注入）
}

// 注册: ObRegisterCallbacks(&callbackRegistration, &hCallback);

// 4. CNG（加密）通知
VOID CngCallback(...) {
    // 监控加密操作（检测勒索软件加密行为）
}
```

### 2.3 文件系统过滤驱动

文件系统过滤驱动（MiniFilter）是 EDR 监控文件操作的核心技术：

```c
// MiniFilter 驱动注册示例

// 注册 Pre 回调（操作前）
FLT_PREOP_CALLBACK_STATUS PreOperationCallback(
    PFLT_CALLBACK_DATA Data,     // 操作数据
    PFLT_CONTEXT Context,        // 上下文
    PFLT_RELATED_OBJECTS FltObjects  // 关联对象
)
{
    switch (Data->Iopb->MajorFunction)
    {
        case IRP_MJ_CREATE:
            // 文件创建/打开
            // 记录: 文件路径、访问模式、进程信息
            break;
        case IRP_MJ_WRITE:
            // 文件写入 - 检测勒索软件加密行为
            // 触发条件: 大量文件快速修改 + 文件扩展名变更
            break;
        case IRP_MJ_SET_INFORMATION:
            // 文件重命名/删除
            break;
    }
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// 注册回调
const FLT_OPERATION_REGISTRATION Callbacks[] = {
    { IRP_MJ_CREATE,        0, PreOperationCallback, PostOperationCallback },
    { IRP_MJ_WRITE,         0, PreOperationCallback, PostOperationCallback },
    { IRP_MJ_SET_INFORMATION,0, PreOperationCallback, NULL },
    { IRP_MJ_OPERATION_END }
};
```

### 2.4 网络过滤

EDR 的网络监控通过 WFP（Windows Filtering Platform）或 NDIS 驱动实现：

```c
// WFP callout 驱动示例
// 监控网络连接

// ALE（Application Layer Enforcement）层 Callout
void NTAPI CalloutClassify(
    const FWPS_INCOMING_VALUES *inFixedValues,
    const FWPS_INCOMING_METADATA_VALUES *inMetaValues,
    void *layerData,
    const void *classifyContext,
    const FWPS_FILTER *filter,
    UINT64 flowContext,
    FWPS_CLASSIFY_OUT *classifyOut
)
{
    // 获取远程地址、端口
    UINT32 remoteIp = inFixedValues->incomingValue
        [FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_ADDRESS].value.uint32;
    UINT16 remotePort = inFixedValues->incomingValue
        [FWPS_FIELD_ALE_AUTH_CONNECT_V4_IP_REMOTE_PORT].value.uint16;
    
    // 获取发起进程
    UINT64 processId = inMetaValues->processId;
    
    // 记录: PID -> IP:Port 连接信息
    // 可阻断已知恶意 C2 通信
}
```

---

---

## 📋 内容审核与补充建议

> 针对「EDR 数据采集技术」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
