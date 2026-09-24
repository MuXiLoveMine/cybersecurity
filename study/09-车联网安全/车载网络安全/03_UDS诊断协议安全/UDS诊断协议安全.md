# UDS诊断协议安全

### 3.1 UDS概述

**UDS（Unified Diagnostic Services，统一诊断服务）** 是汽车诊断的国际标准（ISO 14229），定义了诊断仪与ECU之间的诊断服务。

**用途：**
- 读取/清除故障码（DTC）
- 读取ECU数据（传感器值、版本信息等）
- 输入输出控制（强制执行器动作）
- 例程控制（执行特殊功能）
- 固件刷写（更新ECU程序）
- 安全访问（安全相关功能需先解锁）

### 3.2 UDS协议基础

#### 3.2.1 服务ID（SID）

UDS请求报文的第一个字节是服务ID（SID），响应报文的SID为请求SID + 0x40。

| 服务ID | 服务名称 | 说明 |
|--------|---------|------|
| 0x10 | DiagnosticSessionControl | 诊断会话控制 |
| 0x11 | ECUReset | ECU复位 |
| 0x14 | ClearDiagnosticInformation | 清除诊断信息 |
| 0x19 | ReadDTCInformation | 读取故障码信息 |
| 0x22 | ReadDataByIdentifier | 根据标识符读取数据 |
| 0x27 | SecurityAccess | 安全访问 |
| 0x28 | CommunicationControl | 通信控制 |
| 0x2E | WriteDataByIdentifier | 根据标识符写入数据 |
| 0x2F | InputOutputControlByIdentifier | 输入输出控制 |
| 0x31 | RoutineControl | 例程控制 |
| 0x34 | RequestDownload | 请求下载 |
| 0x36 | TransferData | 数据传输 |
| 0x37 | RequestTransferExit | 请求退出传输 |
| 0x3E | TesterPresent | 测试仪在线 |

#### 3.2.2 肯定响应与否定响应

**肯定响应格式：**
```
[SID + 0x40] [数据...]
例: 请求0x22 → 响应0x62 0xF1 0x90 [VIN码数据]
```

**否定响应格式：**
```
0x7F [请求SID] [否定响应码NRC]
例: 0x7F 0x27 0x35  (密钥无效)
```

**常见否定响应码（NRC）：**

| NRC | 名称 | 说明 |
|-----|------|------|
| 0x10 | generalReject | 通用拒绝 |
| 0x11 | serviceNotSupported | 服务不支持 |
| 0x12 | subFunctionNotSupported | 子功能不支持 |
| 0x13 | incorrectMessageLengthOrInvalidFormat | 消息长度或格式错误 |
| 0x22 | conditionsNotCorrect | 条件不正确 |
| 0x24 | requestSequenceError | 请求顺序错误 |
| 0x31 | requestOutOfRange | 请求超出范围 |
| 0x33 | securityAccessDenied | 安全访问被拒绝 |
| 0x35 | invalidKey | 密钥无效 |
| 0x36 | exceededNumberOfAttempts | 超过尝试次数 |
| 0x37 | requiredTimeDelayNotExpired | 时间延迟未到 |

### 3.3 安全访问机制（Security Access - 0x27）

安全访问是UDS中保护敏感操作的核心机制。

#### 3.3.1 认证流程

```
诊断仪（客户端）                          ECU（服务器）
    │                                       │
    │── 0x27 0x01（请求种子，level 1） ──→│
    │                                       │
    │←── 0x67 0x01 [种子SEED] ────────────│
    │                                       │
    │  本地计算密钥：KEY = f(SEED, PIN)     │
    │                                       │
    │── 0x27 0x02 [密钥KEY] ─────────────→│
    │                                       │
    │                     ECU验证密钥是否正确 │
    │                                       │
    │←── 0x67 0x02（成功）────────────────│
    │     或 0x7F 27 35（失败）             │
    │                                       │
```

#### 3.3.2 安全等级

| 等级 | 子功能（请求种子） | 子功能（发送密钥） | 保护的操作 |
|------|------------------|------------------|-----------|
| Level 1 | 0x01 | 0x02 | 一般配置修改 |
| Level 2 | 0x03 | 0x04 | 较敏感操作 |
| Level 3 | 0x05 | 0x06 | 敏感操作（如刷写） |
| Level 4 | 0x07 | 0x08 | 最高安全级操作 |

### 3.4 UDS安全风险

#### 3.4.1 安全访问算法泄露

**风险：** 安全访问的密钥计算算法如果被逆向出来，攻击者可以轻松通过认证。

**常见问题：**
- 算法过于简单（如简单的异或、移位）
- 密钥硬编码在固件中
- 种子生成可预测

**案例：** 多款车型的UDS安全访问算法被逆向破解，攻击者可解锁诊断功能进行固件刷写。

#### 3.4.2 暴力破解

**风险：** 如果没有尝试次数限制，攻击者可以暴力枚举密钥。

**防护机制：**
- 错误次数限制（如3次失败后延迟10分钟）
- 递增延迟机制

#### 3.4.3 诊断功能滥用

**风险：** 获得诊断权限后，攻击者可以：
- 读取敏感数据（VIN、密钥、固件）
- 修改配置参数（如里程数）
- 强制控制执行器（喷油、刹车）
- 刷写恶意固件

#### 3.4.4 诊断会话保持

**风险：** UDS需要周期性发送TesterPresent（0x3E）保持会话。如果ECU没有合理的超时机制，攻击者可长期保持已认证状态。

### 3.5 UDS刷写流程（固件更新）

```
① 0x10 0x02          → 进入编程会话
② 0x27 0x03          → 请求种子（安全访问Level 3）
③ 0x27 0x04 [KEY]    → 发送密钥，通过认证
④ 0x34 [地址] [大小]  → 请求下载
⑤ 0x36 [数据...]     → 传输固件数据（分多包）
⑥ 0x37               → 请求退出传输
⑦ 0x31 0x01 [校验]   → 例程控制（校验固件）
⑧ 0x11 0x01          → ECU复位
```

**安全风险：** 如果安全访问机制被绕过，攻击者可以刷入恶意固件，获得ECU的完全控制权。

---

---

