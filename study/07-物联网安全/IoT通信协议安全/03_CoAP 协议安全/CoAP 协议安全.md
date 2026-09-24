# CoAP 协议安全

### 3.1 CoAP 协议基础

#### 3.1.1 协议简介

CoAP（Constrained Application Protocol，受限应用协议）是专为受限环境（低功耗、低算力、小内存）设计的 Web 传输协议，运行在 UDP 之上。

**核心特性**：
- 轻量级：最小 4 字节报头
- RESTful 架构：类似 HTTP 的 GET/POST/PUT/DELETE 方法
- 基于 UDP：适合低功耗设备
- 支持资源发现：通过 `/.well-known/core` 发现资源
- 支持观察模式 (Observe)：订阅资源变化
- 支持块传输 (Block-wise)：传输大数据

#### 3.1.2 协议格式

```
CoAP 报文格式：
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver| T |  TKL  |      Code     |          Message ID           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Token (if any, TKL bytes) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Options (if any) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|1 1 1 1 1 1 1 1|    Payload (if any) ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**说明**：
- Ver：版本号（2 位），固定为 1
- T：消息类型（2 位），0=Confirmable, 1=Non-confirmable, 2=Acknowledgement, 3=Reset
- TKL：Token 长度（4 位）
- Code：方法/响应码（8 位），如 0.01=GET, 2.05=Content, 4.04=Not Found

### 3.2 CoAP 安全机制

#### 3.2.1 DTLS (Datagram TLS)

CoAP 的主要安全机制是 DTLS，提供认证、加密和完整性保护。

**DTLS 安全模式**：
- **NoSec**：无安全保护
- **PreSharedKey**：预共享密钥模式
- **RawPublicKey**：原始公钥模式
- **Certificate**：证书模式

**DTLS 端口**：CoAP 默认端口 5683，CoAPS（DTLS 加密）默认端口 5684

**DTLS 握手流程**：
```
客户端                                  服务器
  |                                      |
  |----------- ClientHello ------------->|
  |<--------- HelloVerifyRequest --------|  (可选，Cookie 验证)
  |----------- ClientHello ------------->|  (携带 Cookie)
  |<--------- ServerHello ---------------|
  |<--------- Certificate ---------------|  (证书模式)
  |<--------- ServerKeyExchange ---------|  (可选)
  |<--------- CertificateRequest --------|  (可选，客户端认证)
  |<--------- ServerHelloDone -----------|
  |                                      |
  |----------- Certificate ------------->|  (如有客户端证书)
  |----------- ClientKeyExchange ------->|
  |----------- CertificateVerify ------->|  (如有客户端证书)
  |----------- ChangeCipherSpec -------->|
  |----------- Finished ---------------->|
  |                                      |
  |<--------- ChangeCipherSpec ----------|
  |<--------- Finished ------------------|
  |                                      |
  |        加密数据传输开始              |
```

#### 3.2.2 OSCORE (Object Security for Constrained RESTful Environments)

OSCORE 是一种端到端的 CoAP 安全机制，在应用层提供保护。

**特点**：
- 端到端安全：即使经过代理也能保护消息
- 轻量级：比 DTLS 更适合受限环境
- 保护报头和载荷
- 支持前向保密

### 3.3 CoAP 安全风险

| 风险类型 | 描述 | 防护措施 |
|---------|------|---------|
| **明文传输** | 未启用 DTLS 时数据明文传输 | 启用 DTLS 或 OSCORE |
| **资源枚举** | 通过 /.well-known/core 枚举所有资源 | 限制访问，增加认证 |
| **未授权访问** | 资源无认证保护 | 增加认证机制 |
| **DDoS 攻击** | CoAP 放大攻击（响应比请求大） | 速率限制、IP 白名单 |
| **重放攻击** | 重放 CoAP 请求 | 使用 Nonce、时间戳 |
| **中间人攻击** | DTLS 配置不当 | 正确验证证书 |

**CoAP 放大攻击原理**：
1. 攻击者伪造受害者 IP 向 CoAP 服务器发送请求
2. 服务器返回比请求大得多的响应（放大系数可达 10~100 倍）
3. 大量流量涌向受害者 IP，造成 DDoS

---

---

