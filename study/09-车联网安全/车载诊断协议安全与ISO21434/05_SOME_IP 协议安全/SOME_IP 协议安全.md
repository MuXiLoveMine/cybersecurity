# SOME/IP 协议安全

### 4.1 SOME/IP 协议概述

SOME/IP（Scalable service-Oriented MiddlewarE over IP）是 AUTOSAR 定义的面向服务的车载以太网通信中间件协议，广泛用于 ADAS、信息娱乐系统等高带宽场景。

**SOME/IP 核心机制：**
- **服务发现（Service Discovery, SD）**：动态发现可用服务实例
- **事件订阅**：客户端订阅服务端的事件通知
- **远程过程调用（RPC）**：请求-响应和通知模式
- **Payload 序列化**：支持二进制和 Protobuf 序列化

### 4.2 服务发现安全

SOME/IP-SD 使用 UDP 多播（默认 224.224.224.245:30490）进行服务发现：

```
服务发现流程：

Offering Node (服务提供方)         Subscribing Node (订阅方)
     │                                    │
     │── SD Offer (Multicast) ──────────▶│  通告可用服务
     │     Service ID, Instance ID       │
     │     Major/Minor Version           │
     │                                    │
     │◀── SD Subscribe (Unicast) ───────│  订阅事件组
     │     Eventgroup ID, TTL            │
     │                                    │
     │── SD Subscribe Ack ──────────────▶│  确认订阅
     │                                    │
     │── Event Notification ────────────▶│  推送事件数据
     │     (持续推送)                     │
```

**安全风险：**
- **服务伪装**：攻击者发送伪造 Offer，伪装为合法服务实例。
- **事件劫持**：攻击者订阅受害节点的事件，窃听敏感数据。
- **服务发现洪水**：发送大量 Offer/Subscribe 消息导致 SD 协议处理耗尽资源。
- **TTL 操纵**：使用极长 TTL 使恶意服务通告持续有效。

**防护建议：**
- 使用 VLAN 隔离诊断域和功能域
- SOME/IP-SD 端口限制（基于 MAC 地址的端口过滤）
- 服务实例身份认证（TLS 或 IPSec）
- 服务发现消息速率限制

### 4.3 Payload 安全

SOME/IP Payload 在无 TLS 保护时以明文传输，存在以下风险：

```
SOME/IP 报文结构：

+-------------------------------------------------+
| Message Header (16 bytes)                       |
|  - Service ID (16 bit)                          |
|  - Method/Event ID (16 bit)                    |
|  - Length (32 bit, 含后续字段总长度)              |
|  - Client ID (16 bit)                           |
|  - Session ID (16 bit)                          |
|  - Protocol Version (8 bit)                    |
|  - Interface Version (8 bit)                   |
|  - Message Type (8 bit)                         |
|  - Return Code (8 bit)                          |
+-------------------------------------------------+
| Payload (变长)                                   |
|  可被攻击者篡改/注入                             |
+-------------------------------------------------+
```

**Payload 篡改攻击示例：**

```python
# SOME/IP Payload 篡改攻击模拟
# 假设 ADAS 模块通过 SOME/IP 发送前方障碍物距离

import struct

def craft_someip_message(service_id, method_id, client_id, session_id, payload):
    """构造 SOME/IP 报文"""
    msg_type = 0x02  # Request
    protocol_ver = 0x01
    interface_ver = 0x01
    return_code = 0x00

    header = struct.pack(">HHIHHBBBB",
        service_id, method_id,
        8 + len(payload),  # Length
        client_id, session_id,
        protocol_ver, interface_ver, msg_type, return_code
    )
    return header + payload

# 合法报文：障碍物距离 = 50 米
legit_payload = struct.pack(">f", 50.0)
legit_msg = craft_someip_message(0x1234, 0x0001, 0x0001, 0x0001, legit_payload)

# 攻击者篡改：障碍物距离 = 999 米（诱骗 ADAS 制动）
# 或篡改为 0 米（诱骗 ADAS 紧急制动）
attack_payload = struct.pack(">f", 0.0)
attack_msg = craft_someip_message(0x1234, 0x0001, 0x0001, 0x0001, attack_payload)

# 防护：使用 TLS 加密 + HMAC 签名
def secure_someip_message(service_id, method_id, client_id, session_id, payload, hmac_key):
    msg = craft_someip_message(service_id, method_id, client_id, session_id, payload)
    tag = hmac.new(hmac_key, msg, hashlib.sha256).digest()[:16]
    return msg + tag  # 附带认证标签
```

---

---

## 📋 内容审核与补充建议

> 针对「SOME/IP 协议安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
