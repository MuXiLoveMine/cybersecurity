# TLS 攻击

### 5.1 历史漏洞

| 漏洞 | 年份 | 目标 | 原理 | 修复 |
|------|------|------|------|------|
| **BEAST** | 2011 | TLS 1.0 CBC | 选择明文攻击恢复 Cookie | 使用 GCM/1.1+ |
| **CRIME** | 2012 | TLS 压缩 | 压缩泄露长度侧信道 | 禁用压缩 |
| **BREACH** | 2013 | HTTP 压缩 | 类似 CRIME 但在 HTTP 层 | 禁用 HTTP 压缩 |
| **POODLE** | 2014 | SSL 3.0 CBC | 填充降级攻击 | 禁用 SSL 3.0 |
| **Lucky 13** | 2013 | TLS CBC MAC | 时间侧信道 | 使用 AEAD |
| **Sweet32** | 2016 | 3DES/Blowfish | 生日攻击块密码 | 禁用 64位块密码 |
| **DROWN** | 2016 | SSL 2.0 | 跨协议攻击 SSL 2.0 暴露 RSA | 禁用 SSL 2.0 |
| **ROBOT** | 2017 | RSA PKCS#1 | Bleichenbacher 时序攻击 | 禁用 RSA 密钥交换 |

### 5.2 Heartbleed（CVE-2014-0160）

**原理**：OpenSSL 的 TLS Heartbeat Extension 实现存在缓冲区越界读取漏洞，攻击者可通过发送恶意心跳包读取服务器内存（最多64KB/次），可能获取私钥、会话密钥等。

```bash
# 检测 Heartbleed 漏洞
nmap -p 443 --script ssl-heartbleed www.example.com

# Python 检测（简化版原理示意，仅用于授权测试）
import socket
import struct

def heartbleed_check(host, port=443):
    """检测 Heartbleed 漏洞"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 构造恶意心跳包：声明长度远大于实际数据长度
    heartbeat_type = 1
    payload_length = 16384  # 请求 16KB，但实际发送很少
    record_type = 24  # heartbeat
    tls_version = b'\x03\x03'  # TLS 1.2

    # 构造 TLS 记录
    hb_payload = b'\x01'  # heartbeat_request
    hb_payload += struct.pack('>H', payload_length)
    hb_payload += b'\x00' * 3  # 极少的实际数据

    record = struct.pack('>BHH', record_type, len(tls_version + hb_payload), 0x0303)
    # 简化版，实际需要先完成 TLS 握手
    print(f"[!] Sending malicious heartbeat to {host}:{port}")
    # 实际利用需要先完成完整 TLS 握手才能发送心跳
    sock.close()
    return "请使用 nmap 或专用工具在授权环境下检测"

# 推荐使用 nmap 或 testssl.sh 检测
```

### 5.3 中间人攻击与证书钉扎

```
# 中间人攻击（MITM）场景
正常：Client ←→ Server（TLS 加密）
攻击：Client ←→ 攻击者（自签证书）←→ Server

# 证书钉扎（Certificate Pinning）
# 客户端内置期望的证书公钥哈希，拒绝其他证书
# 即使 CA 被入侵签发假证书也能检测到

# 示例：Android 证书钉扎（已废弃 NetworkSecurityConfig）
<network-security-config>
  <pin-set expiration="2026-12-31">
    <pin digest="SHA-256">base64_encoded_hash=</pin>
    <pin digest="SHA-256">backup_pin_hash=</pin>
  </pin-set>
</network-security-config>

# 注意：钉扎需谨慎，证书轮换时可能导致应用无法连接
```

### 5.4 TLS 1.3 安全增强

- **移除 RSA 密钥交换** → 前向保密强制（无法解密历史流量）
- **移除 CBC 模式** → 消除填充攻击向量
- **握手加密** → 减少指纹泄露
- **移除压缩** → 消除 CRIME/BREACH 向量
- **移除重协商** → 消除相关漏洞

---

---

## 📋 内容审核与补充建议

> 针对「TLS 攻击」部分的内容审核结果：

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
