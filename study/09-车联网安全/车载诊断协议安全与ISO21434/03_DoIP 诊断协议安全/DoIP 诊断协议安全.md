# DoIP 诊断协议安全

### 3.1 ISO 13400 DoIP 协议概述

DoIP（Diagnostics over IP）是 ISO 13400 标准定义的基于以太网的车载诊断协议。随着车载以太网（100BASE-T1 / 1000BASE-T1）普及，DoIP 正成为高速诊断和大规模固件刷写的首选方案。

**DoIP 协议栈：**

```
+---------------------------+
|  UDS 诊断服务 (ISO 14229) |  ← 应用层
+---------------------------+
|  DoIP 协议 (ISO 13400)    |  ← 诊断传输层
+---------------------------+
|  TCP/UDP (IP 层)          |  ← 传输层
+---------------------------+
|  车载以太网 (100BASE-T1)  |  ← 物理层
+---------------------------+
```

**DoIP 端口分配：**

| 端口  | 协议 | 用途                           |
|-------|------|-------------------------------|
| 13400 | TCP  | DoIP 数据通信（诊断请求/响应） |
| 13400 | UDP  | 车辆发现与状态通告             |

### 3.2 车辆发现机制

DoIP 使用 UDP 广播进行车辆发现，Tester 发送 `Vehicle Identification Request`，车辆响应身份信息：

```
车辆发现流程：

Tester                                   车辆/ECU
  │                                          │
  │── UDP Broadcast: DoIP Vehicle ID Req ──▶│  (广播到 255.255.255.255:13400)
  │                                          │
  │◀──────── DoIP Vehicle ID Response ──────│  (单播响应)
  │     包含: VIN, Logical Address, EID      │
  │                                          │
  │── TCP Connect to Vehicle IP:13400 ─────▶│  建立 TCP 连接
  │                                          │
  │── DoIP Routing Activation Request ──────▶│  路由激活
  │     包含: Source Address, Activation Type │
  │                                          │
  │◀────── DoIP Routing Activation Response ─│  激活成功/失败
  │     包含: Response Code                  │
  │                                          │
  │  此后可发送 UDS 诊断请求                   │
```

**DoIP 报文格式：**

```
DoIP Payload Header (8 字节固定头):

  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |Protocol Version| Inverse Protocol Version  |    Payload Type  |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                       Payload Length                           |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

 关键 Payload Type：
   0x0001: Vehicle Identification Request Message
   0x0004: Vehicle Announcement Message
   0x0005: Routing Activation Request
   0x0006: Routing Activation Response
   0x8001: Diagnostic Message (请求)
   0x8002: Diagnostic Message (响应)
   0x0008: Alive Check Request
   0x0009: Alive Check Response
```

### 3.3 DoIP 安全风险与防护

**风险 1：未认证的车辆发现**

UDP 广播的车辆发现消息不包含认证，任何接入网络的设备都能获取 VIN 和 ECU 逻辑地址。

**风险 2：TCP 连接劫持**

DoIP 的 TCP 连接若无 TLS 保护，存在中间人攻击和会话劫持风险。

**风险 3：路由激活滥用**

路由激活允许任何源地址激活路由，攻击者可伪装为合法 Tester 获取诊断通道。

**防护方案：**

```python
# DoIP 安全路由激活实现
class DoIPSecurityHandler:
    def __init__(self):
        self.authorized_testers = set()  # 已授权 Tester 列表
        self.connection_attempts = {}    # 连接尝试记录
        self.tls_required = True         # 强制 TLS

    def handle_routing_activation(self, source_addr, activation_type, client_cert=None):
        # 1. TLS 证书验证
        if self.tls_required:
            if client_cert is None:
                return ROUTING_REJECTED_NO_CERT
            if not self.verify_client_cert(client_cert):
                return ROUTING_REJECTED_INVALID_CERT
            if not self.check_cert_revocation(client_cert):
                return ROUTING_REJECTED_REVOKED_CERT

        # 2. 源地址白名单检查
        if source_addr not in self.allowed_tester_addresses:
            self.log_security_event("Unauthorized source address: %04X" % source_addr)
            return ROUTING_REJECTED_UNKNOWN_SOURCE

        # 3. 连接频率限制
        attempts = self.connection_attempts.get(source_addr, 0)
        if attempts >= MAX_ROUTING_ATTEMPTS:
            return ROUTING_REJECTED_TOO_MANY_ATTEMPTS
        self.connection_attempts[source_addr] = attempts + 1

        # 4. 激活类型验证
        if activation_type not in [ACTIVATION_DEFAULT, ACTIVATION_CENTRAL]:
            return ROUTING_REJECTED_INVALID_TYPE

        self.authorized_testers.add(source_addr)
        return ROUTING_ACTIVATION_SUCCESS

    def verify_client_cert(self, cert):
        # 验证证书链和有效期
        return self.ca_store.verify(cert)

    def check_cert_revocation(self, cert):
        # OCSP / CRL 检查
        return not self.revocation_list.is_revoked(cert)
```

---

---

