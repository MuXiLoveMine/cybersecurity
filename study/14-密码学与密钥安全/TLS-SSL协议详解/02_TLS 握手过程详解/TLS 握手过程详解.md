# TLS 握手过程详解

### 2.1 TLS 1.2 握手流程

```
┌────────┐                                        ┌─────────┐
│ Client │                                        │ Server  │
└───┬────┘                                        └────┬────┘
    │  ① ClientHello (支持的密码套件/版本/随机数)    │
    │ ──────────────────────────────────────────────> │
    │                                                 │
    │  ② ServerHello (选定的套件/版本/随机数)          │
    │     Certificate (服务器证书)                    │
    │     ServerKeyExchange (DH参数，仅DHE时)          │
    │     ServerHelloDone                             │
    │ <───────────────────────────────────────────── │
    │                                                 │
    │  ③ ClientKeyExchange (加密的PreMasterSecret)    │
    │     ChangeCipherSpec                           │
    │     Finished (加密的握手摘要)                    │
    │ ──────────────────────────────────────────────> │
    │                                                 │
    │  ④ ChangeCipherSpec                            │
    │     Finished (加密的握手摘要)                    │
    │ <───────────────────────────────────────────── │
    │                                                 │
    │  ════════ 应用数据（加密传输）══════════════════ │
    │ <─────────────────────────────────────────────> │
```

**步骤详解**：

**① ClientHello**
- 客户端发送支持的 TLS 版本、密码套件列表、客户端随机数（32字节）
- 可包含 SNI（Server Name Indication）指定目标主机名
- 可包含会话恢复信息（Session ID 或 Session Ticket）

**② ServerHello + Certificate**
- 服务器选定一个密码套件、TLS 版本、服务器随机数（32字节）
- 发送服务器证书链（服务器证书 + 中间证书）
- 发送密钥交换参数（DHE/ECDHE 的公钥部分）

**③ 密钥计算**
- 客户端生成 PreMasterSecret（用服务器公钥加密发送，或通过 DH 计算）
- 双方使用 Client Random + Server Random + PreMasterSecret 计算主密钥
- 主密钥派生出加密密钥和 MAC 密钥

**④ ChangeCipherSpec + Finished**
- 双方发送 ChangeCipherSpec 标记后续消息加密
- Finished 消息包含之前所有握手消息的 MAC，验证握手完整性

### 2.2 TLS 1.3 握手流程

#### 1-RTT 握手

```
┌────────┐                                        ┌─────────┐
│ Client │                                        │ Server  │
└───┬────┘                                        └────┬────┘
    │  ① ClientHello                              │
    │     (密码套件列表 + 客户端ECDHE公钥          │
    │      + 客户端随机数 + SNI)                   │
    │ ──────────────────────────────────────────────> │
    │                                                 │
    │  ② ServerHello                              │
    │     (选定套件 + 服务器ECDHE公钥 + 服务器随机数) │
    │     EncryptedExtensions                       │
    │     Certificate (服务器证书)                   │
    │     CertificateVerify (证书签名)               │
    │     Finished (握手摘要)                       │
    │ <───────────────────────────────────────────── │
    │                                                 │
    │  ③ Finished (客户端握手摘要)                    │
    │     (从②开始已加密)                            │
    │ ──────────────────────────────────────────────> │
    │                                                 │
    │  ════════ 应用数据（加密传输）══════════════════ │
```

**关键区别**：服务器在发送 Hello 后立即用协商出的密钥加密后续消息（证书、Finished），减少一轮往返。

#### 0-RTT 恢复

```
# 前提：客户端之前已与服务器建立过连接，持有 PSK（预共享密钥）

① ClientHello
   + early_data（在密钥协商完成前就发送应用数据）
   + PSK 标识

② Server 接受 early_data → 直接处理
   ServerHello + Finished

③ 客户端发送 Finished
   后续数据正常加密
```

**0-RTT 风险**：早期数据无前向保密，且可被重放。防御措施：0-RTT 数据仅用于幂等请求（GET），禁止用于 POST 等状态变更操作。

#### 密钥调度

```
TLS 1.3 密钥派生层次：

Early Secret = HKDF-Extract(0, PSK 或 0)
  ↓
Handshake Secret = HKDF-Extract(Derived(Early Secret), ECDHE 共享密钥)
  ↓ 派生 → 客户端/服务器握手流量密钥
  ↓
Master Secret = HKDF-Extract(Derived(Handshake Secret), 0)
  ↓ 派生 → 客户端/服务器应用流量密钥
  ↓ 派生 → resumption_master_secret（用于0-RTT恢复）
```

### 2.3 密码套件组成与选择

**TLS 1.2 密码套件命名**：`TLS_<密钥交换>_<认证>_<加密>_<MAC>`

```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
     │       │         │     │     │
     │       │         │     │     └─ MAC 算法
     │       │         │     └─────── 加密算法+密钥长度+模式
     │       │         └─────────────── 认证算法
     │       └───────────────────────── 密钥交换算法
     └─────────────────────────────────── 协议标识
```

**TLS 1.3 密码套件命名**（简化）：`TLS_AES_256_GCM_SHA384`

```
# TLS 1.3 不需要指定密钥交换和认证（固定 ECDHE + 证书）
TLS_AES_256_GCM_SHA384         ← 推荐
TLS_CHACHA20_POLY1305_SHA256   ← 移动端推荐（无AES-NI时）
TLS_AES_128_GCM_SHA256         ← 轻量级
```

---

---

## 📋 内容审核与补充建议

> 针对「TLS 握手过程详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
