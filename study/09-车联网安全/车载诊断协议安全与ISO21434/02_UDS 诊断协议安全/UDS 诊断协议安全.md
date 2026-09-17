# UDS 诊断协议安全

### 1.1 ISO 14229 UDS 协议架构

UDS（Unified Diagnostic Services，统一诊断服务）是 ISO 14229 定义的车载诊断通信协议标准。它运行在 OSI 模型的应用层（Layer 7），可以基于多种传输层：CAN（ISO 15765）、CAN FD、FlexRay、以太网（DoIP/ISO 13400）等。

**协议分层架构：**

```
+--------------------------------------------------+
|            应用层 (Application Layer)             |
|         ISO 14229 UDS 诊断服务                    |
+--------------------------------------------------+
|        传输层 / 网络层 (Transport/Network)         |
|   ISO 15765 (CAN/CAN FD) | ISO 13400 (DoIP)       |
+--------------------------------------------------+
|        数据链路层 / 物理层 (Data Link/Physical)     |
|   CAN/CAN FD | FlexRay | 100BASE-T1 | LIN         |
+--------------------------------------------------+
```

UDS 采用客户端/服务器模型：诊断测试仪（Tester）作为客户端发起请求，ECU 作为服务器进行响应。所有通信以"服务"为单位，每个服务用唯一的 SID（Service Identifier）标识。

### 1.2 诊断服务总览

UDS 定义了 6 大类诊断服务，涵盖诊断管理、数据传输、输入输出控制、例程控制、上传下载等。以下列出核心服务及其安全相关性：

| SID  | 服务名称                      | 功能说明                       | 安全关注点                     |
|------|-------------------------------|-------------------------------|-------------------------------|
| 0x10 | DiagnosticSessionControl      | 切换诊断会话模式               | 会话权限隔离、会话超时         |
| 0x11 | ECUReset                      | 重置 ECU                       | 拒绝服务、非授权重置           |
| 0x22 | ReadDataByIdentifier          | 读取 ECU 数据                  | 敏感数据泄露                   |
| 0x2E | WriteDataByIdentifier         | 写入 ECU 数据                  | 非授权数据篡改                 |
| 0x27 | SecurityAccess                | 安全访问（种子-密钥认证）      | 认证绕过、密钥破解             |
| 0x31 | RoutineControl                | 执行例程                       | 非授权执行危险例程             |
| 0x34 | RequestDownload               | 请求下载固件                  | 固件刷写安全                    |
| 0x36 | TransferData                 | 传输数据块                     | 固件完整性                     |
| 0x37 | RequestTransferExit          | 结束传输                      | 刷写完成校验                   |
| 0x3E | TesterPresent                 | 保活诊断会话                   | 会话保持滥用                   |
| 0x14 | ClearDiagnosticInformation    | 清除 DTC                       | 故障码篡改                     |
| 0x19 | ReadDTCInformation            | 读取故障码                     | 故障信息泄露                   |
| 0x85 | ControlDTCSetting            | 控制 DTC 设置                  | 屏蔽故障上报                   |

### 1.3 诊断会话模式

UDS 通过 `DiagnosticSessionControl`（0x10）服务切换三种会话模式，不同模式下可用的服务集合不同：

```
会话模式切换流程：

默认会话 (0x01)
    │  请求: 10 03
    ▼
非默认会话 (0x03)  ──────── 需要通过 SecurityAccess (0x27)
    │  请求: 10 02             提升到扩展会话后才能解锁
    ▼
编程会话 (0x02)  ──────── 用于固件刷写，安全等级最高
```

**三种会话模式：**
- **默认会话（Default Session, 0x01）**：车辆正常工作时所处会话，仅允许基础诊断服务。
- **非默认会话（Non-Default Session, 0x03）**：扩展诊断功能，需要 tester 保持活跃。
- **编程会话（Programming Session, 0x02）**：用于 ECU 刷写与配置，安全要求最高。

安全设计要点：编程会话必须要求 SecurityAccess 解锁后才允许固件刷写相关服务（0x34/0x36/0x37），并设置会话超时机制（S3 Server 超时，默认 5 秒）。

### 1.4 安全访问机制（SecurityAccess, 0x27）

SecurityAccess 是 UDS 中最核心的安全机制，采用"种子-密钥"（Seed-Key）挑战-响应认证模型：

```
认证流程：

Tester (客户端)                          ECU (服务器)
    │                                         │
    │── 27 01 (Request Seed) ────────────────▶│
    │                                         │  生成随机种子 Seed
    │◀─────────────── (响应: 67 01 [Seed]) ────│
    │                                         │
    │  计算 Key = f(Seed, Secret)             │
    │── 27 02 [Key] (Send Key) ──────────────▶│
    │                                         │  验证 Key == f(Seed, Secret)
    │◀─────────── (响应: 67 02 / 7F 27 NRC) ────│
    │                                         │
    │  认证成功，解锁高级服务                    │

子功能说明：
  01 = Request Seed（请求种子）
  02 = Send Key  （发送密钥）
  03 = Request Seed（第二组种子，多级认证）
  04 = Send Key  （第二组密钥）
  ...
  0D = Request Seed（第七组）
  0E = Send Key  （第七组）
```

**密钥生成算法安全性要点：**
- 密钥派生函数 `f()` 通常由 OEM 自定义实现，常见的有 CRC32、AES-CMAC、HMAC-SHA256 等。
- 弱算法（如简单 CRC 或 XOR）容易被逆向破解。
- 种子长度至少 4 字节（CAN）/ 8 字节（DoIP 推荐），防止暴力枚举。
- 种子应使用硬件随机数生成器（TRNG），避免伪随机可预测。

**常见 NRC（否定响应码）：**
- `0x22`：条件不满足（Conditions Not Correct）
- `0x24`：请求序列错误
- `0x27`：安全访问拒绝——密钥错误
- `0x35`：密钥无效
- `0x36`：超出尝试次数限制（Exceeded Number Of Attempts）

**安全策略配置示例（伪代码）：**

```python
# SecurityAccess 安全策略配置
security_config = {
    "seed_length": 8,              # 种子长度 8 字节
    "max_attempts": 3,             # 最大尝试次数
    "lockout_time": 7200,          # 锁定时间 2 小时（秒）
    "key_algorithm": "HMAC-SHA256", # 密钥算法
    "session_timeout": 5,          # S3 超时 5 秒
    "anti_scan_delay": 0.5,        # 请求间隔限制
}

def handle_security_access(sid, sub_function, data):
    if sub_function % 2 == 1:  # 奇数 = Request Seed
        if is_locked():
            return negative_response(0x36)  # 超出尝试次数
        seed = generate_random_seed(security_config["seed_length"])
        store_pending_seed(seed)
        return positive_response(0x67, sub_function, seed)

    elif sub_function % 2 == 0:  # 偶数 = Send Key
        expected_key = compute_key(stored_seed, secret_key)
        if data == expected_key:
            unlock_security_level(sub_function // 2)
            reset_failed_attempts()
            return positive_response(0x67, sub_function)
        else:
            increment_failed_attempts()
            if failed_attempts >= security_config["max_attempts"]:
                lock_device(security_config["lockout_time"])
                return negative_response(0x36)
            return negative_response(0x27)
```

---

---

## 📋 内容审核与补充建议

> 针对「UDS 诊断协议安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
