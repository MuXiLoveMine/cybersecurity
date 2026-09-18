# TLS/SSL 协议详解

> TLS（Transport Layer Security）是互联网通信安全的基石，保护着从网页浏览到 API 调用的每一个加密连接。本文系统讲解 TLS 协议演进、握手过程、PKI 证书体系、安全配置、历史漏洞以及调试检测方法，帮助读者全面理解并实践 TLS 安全。

---

## 一、TLS 协议概述

### 1.1 SSL 与 TLS 演进史

| 版本 | 年份 | 状态 | 关键变化 |
|------|------|------|---------|
| SSL 2.0 | 1995 | 已废弃（RFC 6176） | Netscape 首版，存在严重缺陷 |
| SSL 3.0 | 1996 | 已废弃（POODLE 攻击） | 引入握手机制改进 |
| TLS 1.0 | 1999 | 弃用中 | 基本等同于 SSL 3.1 |
| TLS 1.1 | 2006 | 弃用中 | 修复 CBC 填充攻击 |
| TLS 1.2 | 2008 | 广泛使用 | 引入 AEAD（GCM/CCM） |
| TLS 1.3 | 2018 | 推荐 | 1-RTT 握手、0-RTT、移除不安全算法 |

### 1.2 TLS 协议栈位置

```
┌─────────────────────────────────────┐
│         应用层（HTTP/SMTP/FTP等）    │
├─────────────────────────────────────┤
│     TLS 层                          │
│  ┌─────────────────────────────┐   │
│  │  握手协议（Handshake）        │   │
│  │  记录协议（Record）           │   │
│  │  警报协议（Alert）            │   │
│  │  密码变更规范（ChangeCipherSpec）│   │
│  └─────────────────────────────┘   │
├─────────────────────────────────────┤
│         传输层（TCP）                │
├─────────────────────────────────────┤
│         网络层（IP）                 │
└─────────────────────────────────────┘
```

### 1.3 TLS 1.3 vs TLS 1.2 关键改进

| 维度 | TLS 1.2 | TLS 1.3 |
|------|---------|---------|
| 握手往返 | 2-RTT | 1-RTT（支持 0-RTT 恢复） |
| 密钥交换 | RSA/DHE/ECDHE | 仅 ECDHE/DHE（前向保密强制） |
| 对称加密 | CBC/GCM/CCM | 仅 AEAD（GCM/CCM/ChaCha20-Poly1305） |
| 签名算法 | RSA/DSA/ECDSA | RSA-PSS/ECDSA/EdDSA |
| 证书加密 | 公钥加密参与密钥交换 | 不参与（仅身份验证） |
| MAC | HMAC-SHA256（另存） | 集成于 AEAD |
| 消息压缩 | 支持（已不推荐） | 移除（消除 CRIME/BREACH 向量） |
| 静态 RSA | 支持 | 移除（无前向保密） |
| 重协商 | 支持 | 移除（消除漏洞） |

---

## 二、TLS 握手过程详解

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

## 三、TLS 证书与 PKI

### 3.1 X.509 证书结构

```bash
# 查看 X.509 证书详情
openssl x509 -in cert.pem -noout -text

# 证书结构（简化版）
Certificate:
  Version: 3 (0x2)
  Serial Number: 0x1A2B3C
  Signature Algorithm: sha256WithRSAEncryption
  Issuer: C=US, O=Let's Encrypt, CN=R3
  Validity:
    Not Before: Sep 12 00:00:00 2026
    Not After : Dec 11 23:59:59 2026
  Subject: CN=www.example.com
  Subject Public Key Info:
    Public Key Algorithm: RSA (2048-bit)
  Extensions:
    Subject Alternative Name (SAN):     ← 关键扩展
      DNS:www.example.com
      DNS:example.com
      DNS:*.api.example.com             ← 通配符
    Key Usage: Digital Signature, Key Encipherment
    Extended Key Usage: Server Auth, Client Auth
    Authority Information Access (AIA):  ← CA 在线验证信息
      CA Issuers - URI:http://r3.letsencrypt.org
    CRL Distribution Points:            ← 证书吊销列表
      URI:http://r3.letsencrypt.org.crl
    SCT (Signed Certificate Timestamp):  ← 证书透明度
```

### 3.2 证书链验证

```
信任锚（Root CA）           ← 浏览器/操作系统预装
  │
  ↓ 签名
中间 CA（Intermediate CA）
  │
  ↓ 签名
服务器证书（End-Entity）
```

**验证过程**：
1. 服务器证书由中间 CA 签名 → 验证中间 CA 签名有效
2. 中间 CA 由 Root CA 签名 → Root CA 在信任存储中 → 信任建立
3. 检查证书有效期、域名匹配（SAN）、吊销状态

```bash
# OpenSSL 验证证书链
openssl verify -CAfile chain.pem cert.pem
# 或使用中间证书
openssl verify -CAfile root.pem -untrusted intermediate.pem cert.pem

# 检查证书链是否完整（服务器是否发送了中间证书）
echo | openssl s_client -connect www.example.com:443 -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE"
# 如果只返回 1，说明服务器未发送中间证书，部分客户端将无法验证
```

### 3.3 CA 信任模型

```
┌──────────────────────────────────────────────────────┐
│                    PKI 信任模型                      │
│                                                      │
│   根 CA 模型               Web of Trust 模型         │
│   ┌─────────┐              ┌───┐ ←──→ ┌───┐         │
│   │ Root CA │              │ A │ 信任 │ B │         │
│   └────┬────┘              └───┘      └───┘         │
│    ┌────┴────┐               ↑          ↓           │
│    ▼         ▼              信任签名     信任签名      │
│   Sub1     Sub2            ┌───┐ ←──→ ┌───┐         │
│  ┌─┴─┐   ┌─┴─┐            │ C │      │ D │         │
│  │   │   │   │            └───┘      └───┘         │
│ 叶子 叶子 叶子 叶子           P2P去中心化信任          │
│                                                      │
│   集中信任              vs     分布式信任              │
└──────────────────────────────────────────────────────┘
```

### 3.4 证书透明度（CT）

**Certificate Transparency** 要求 CA 将签发的证书提交到公开日志，实现可审计性。

```bash
# 查询域名的 CT 日志
curl -s "https://crt.sh/?q=example.com&output=json" | python -m json.tool

# 检查证书是否包含 SCT（Signed Certificate Timestamp）
openssl x509 -in cert.pem -noout -text | grep -A2 "TLS Feature\|SCT"

# CT 日志可帮助发现未授权签发的证书（CA 被入侵或违规操作）
```

### 3.5 Let's Encrypt 与 ACME 协议

**ACME（Automatic Certificate Management Environment）** 协议自动化证书申请和续期。

```bash
# Certbot（Let's Encrypt 客户端）申请证书
certbot certonly --webroot -w /var/www/html -d www.example.com -d example.com

# 自动续期（建议加入 cron）
certbot renew --quiet --post-hook "systemctl reload nginx"
# 或 systemd timer
systemctl enable --now certbot.timer

# DNS-01 验证（支持通配符证书）
certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials ~/.secrets/cloudflare.ini \
  -d "*.example.com" -d "example.com"
```

### 3.6 通配符证书与 SAN

```
通配符证书：*.example.com
  匹配：www.example.com, api.example.com, mail.example.com
  不匹配：example.com, a.b.example.com（仅匹配一级子域）

SAN（Subject Alternative Name）：
  一张证书覆盖多个域名：
  DNS:www.example.com
  DNS:example.com
  DNS:api.example.com
  DNS:www.example.org
```

```bash
# 查看证书的 SAN
openssl x509 -in cert.pem -noout -ext subjectAltName
```

---

## 四、TLS 安全配置

### 4.1 Nginx 安全配置

```nginx
# /etc/nginx/conf.d/ssl.conf

# TLS 1.2 和 1.3（禁用旧版本）
ssl_protocols TLSv1.2 TLSv1.3;

# TLS 1.3 密码套件（服务器自动选择，无需手动配置）
# ssl_ciphers 指令仅控制 TLS 1.2

# TLS 1.2 密码套件（推荐配置）
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
# 优先 ECDHE 确保前向保密
# 优先 AES-GCM 和 ChaCha20-Poly1305（AEAD）
# 禁止 CBC 模式和 RC4

# 服务器密码套件优先
ssl_prefer_server_ciphers on;

# HSTS（HTTP Strict Transport Security）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

# 证书文件
ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

# 会话恢复
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets off;  # 禁用 Session Tickets（无前向保密的会话恢复）

# OCSP 装订
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;

# 证书绑定 HPKP（已不推荐，因 CA 可能更换）
# add_header Public-Key-Pins "pin-sha256=\"base64==\"; max-age=5184000" always;

# HTTP/2
listen 443 ssl http2;
listen 443 ssl http3;  # 需 Nginx 1.25+ 和 QUIC 支持
```

### 4.2 Apache 安全配置

```apache
# /etc/apache2/sites-available/default-ssl.conf

<VirtualHost *:443>
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

    # 仅 TLS 1.2 和 1.3
    SSLProtocol -all +TLSv1.2 +TLSv1.3

    # 安全密码套件
    SSLCipherSuite ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305
    SSLHonorCipherOrder on

    # HSTS
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"

    # OCSP 装订
    SSLUseStapling on
    SSLStaplingCache shmcb:/var/run/ssl_stapling(128000)

    # HTTP/2
    Protocols h2 http/1.1
</VirtualHost>
```

### 4.3 Tomcat 安全配置

```xml
<!-- server.xml -->
<Connector port="443" protocol="org.apache.coyote.http11.Http11NioProtocol"
           SSLEnabled="true" scheme="https" secure="true">
    <SSLHostConfig
        protocols="TLSv1.2,TLSv1.3"
        ciphers="TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256,
                 ECDHE-RSA-AES256-GCM-SHA384,
                 ECDHE-RSA-CHACHA20-POLY1305">
        <Certificate
            certificateKeyFile="/etc/letsencrypt/live/example.com/privkey.pem"
            certificateFile="/etc/letsencrypt/live/example.com/fullchain.pem"/>
    </SSLHostConfig>
</Connector>
```

### 4.4 密码套件推荐

| 优先级 | 密码套件 | 说明 |
|--------|---------|------|
| 1 | `ECDHE-ECDSA-AES256-GCM-SHA384` | 最强，需要 ECDSA 证书 |
| 2 | `ECDHE-RSA-AES256-GCM-SHA384` | RSA 证书的最优选 |
| 3 | `ECDHE-ECDSA-CHACHA20-POLY1305` | 无 AES-NI 时更高效 |
| 4 | `ECDHE-RSA-CHACHA20-POLY1305` | RSA 版本 |
| 禁止 | `CBC` 模式 | 易受填充攻击 |
| 禁止 | `RC4` | 已不安全 |
| 禁止 | `3DES` | Sweet32 攻击 |
| 禁止 | `RSA` 密钥交换 | 无前向保密 |

### 4.5 HSTS 与证书绑定

```bash
# HSTS 响应头
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload

# preload 列表：将域名提交到浏览器内置的 HSTS 列表
# https://hstspreload.org/

# HTTP 到 HTTPS 重定向（Nginx）
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}
```

### 4.6 OCSP 装订

```bash
# OCSP 装订：服务器代替客户端查询证书吊销状态
# 减少 OCSP 查询延迟和隐私泄露（不暴露用户访问的域名给 CA）

# 测试 OCSP 装订是否生效
openssl s_client -connect www.example.com:443 -status 2>/dev/null | grep -A2 "OCSP Response Status"
# 期望输出：OCSP Response Status: successful
```

### 4.7 HTTP/2 与 HTTP/3 (QUIC) 安全

```bash
# HTTP/2 基于 TLS 1.2+，使用 ALPN 协商
# Nginx 启用 HTTP/2
listen 443 ssl http2;

# HTTP/3 基于 QUIC（UDP），内置 TLS 1.3
# Nginx 1.25+ 支持
listen 443 quic reuseport;
add_header Alt-Svc 'h3=":443"; ma=86400';

# QUIC 优势：
# - 解决 TCP 队头阻塞
# - 连接迁移（IP 变化不断连）
# - 0-RTT 握手
```

---

## 五、TLS 攻击

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

## 六、TLS 调试与检测

### 6.1 OpenSSL s_client 使用

```bash
# 基本连接测试
openssl s_client -connect www.example.com:443

# 指定 SNI（虚拟主机）
openssl s_client -connect www.example.com:443 -servername www.example.com

# 仅 TLS 1.3
openssl s_client -connect www.example.com:443 -tls1_3

# 仅 TLS 1.2
openssl s_client -connect www.example.com:443 -tls1_2

# 查看证书链
openssl s_client -connect www.example.com:443 -showcerts

# 测试特定密码套件
openssl s_client -connect www.example.com:443 -cipher 'ECDHE-RSA-AES256-GCM-SHA384'

# 检查 ALPN（HTTP/2）
openssl s_client -connect www.example.com:443 -alpn h2

# OCSP 装订
openssl s_client -connect www.example.com:443 -status

# 导出服务器证书
echo | openssl s_client -connect www.example.com:443 2>/dev/null | openssl x509 -outform PEM > server.pem

# 验证证书
openssl s_client -connect www.example.com:443 -verify_return_error -CAfile /etc/ssl/certs/ca-certificates.crt
```

### 6.2 SSL Labs 评级

```
# SSL Labs（https://www.ssllabs.com/ssltest/）评级标准

A+：完美配置（TLS 1.3 + HSTS + 无漏洞）
A ：良好配置
B ：可接受（如仅支持 TLS 1.0/1.1）
C-F：不安全（存在已知漏洞）

# 评级考虑因素：
# - 协议版本（TLS 1.2/1.3 = 加分）
# - 密码套件强度（AEAD = 加分，CBC/RC4 = 减分）
# - 密钥交换（前向保密 = 加分）
# - 证书链完整性
# - HSTS 启用
# - 已知漏洞（Heartbleed/POODLE/ROBOT等）
```

### 6.3 testssl.sh 使用

```bash
# testssl.sh 是强大的 TLS 检测工具
# GitHub: https://github.com/drwetter/testssl.sh

# 基本扫描
./testssl.sh www.example.com

# 仅检测特定类别
./testssl.sh -E www.example.com    # 密码套件
./testssl.sh -P www.example.com    # 协议
./testssl.sh -S www.example.com    # 服务器偏好
./testssl.sh -H www.example.com    # HTTP 头
./testssl.sh -U www.example.com    # 漏洞检测

# 高速扫描（并行）
./testssl.sh --fast www.example.com

# JSON 输出（便于 CI/CD 集成）
./testssl.sh --json-pretty -o report.json www.example.com
```

### 6.4 Python TLS 安全检测脚本

```python
"""
TLS 安全检测脚本
检测项：协议版本、密码套件、证书有效性、前向保密、HSTS、已知漏洞
依赖: pip install cryptography pyOpenSSL
"""

import ssl
import socket
from datetime import datetime
from OpenSSL import crypto


class TLSScanner:
    def __init__(self, host, port=443):
        self.host = host
        self.port = port
        self.results = {}

    def check_protocol_versions(self):
        """检测支持的 TLS 协议版本"""
        versions = {
            'SSL 2.0': (ssl.PROTOCOL_SSLv23, ('SSLv2',)),
            'SSL 3.0': (ssl.PROTOCOL_SSLv23, ('SSLv3',)),
            'TLS 1.0': None,
            'TLS 1.1': None,
            'TLS 1.2': None,
            'TLS 1.3': None,
        }
        # 简化版检测（实际应逐个尝试建立连接）
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        try:
            with socket.create_connection((self.host, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    version = ssock.version()
                    cipher = ssock.cipher()
                    self.results['negotiated_version'] = version
                    self.results['cipher'] = {
                        'name': cipher[0],
                        'protocol': cipher[1],
                        'bits': cipher[2]
                    }
                    print(f"[*] Negotiated: {version} with {cipher[0]} ({cipher[2]} bits)")
        except Exception as e:
            print(f"[!] Connection failed: {e}")

    def check_certificate(self):
        """检查证书有效性"""
        context = ssl.create_default_context()
        conn = socket.create_connection((self.host, self.port))
        ssock = context.wrap_socket(conn, server_hostname=self.host)

        cert_der = ssock.getpeercert(binary_form=True)
        cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_der)

        # 证书详情
        subject = cert.get_subject()
        issuer = cert.get_issuer()
        not_before = cert.get_notBefore().decode('ascii')
        not_after = cert.get_notAfter().decode('ascii')

        # SAN 检查
        san_count = cert.get_extension_count()
        san_list = []
        for i in range(san_count):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b'subjectAltName':
                san_list = str(ext).split(', ')

        # 检查有效期
        exp_date = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
        days_remaining = (exp_date - datetime.now()).days

        cert_info = {
            'subject': str(subject),
            'issuer': str(issuer),
            'not_before': not_before,
            'not_after': not_after,
            'days_remaining': days_remaining,
            'san': san_list,
            'serial': hex(cert.get_serial_number()),
        }

        if days_remaining < 30:
            print(f"[WARNING] Certificate expires in {days_remaining} days")
        if days_remaining < 0:
            print(f"[CRITICAL] Certificate EXPIRED {-days_remaining} days ago")

        # 检查 SAN 是否匹配主机名
        host_matched = any(
            self.host == s.replace('DNS:', '').strip() or
            (s.startswith('DNS:*') and self.host.endswith(s.replace('DNS:*', '')))
            for s in san_list
        )
        cert_info['host_matches'] = host_matched
        if not host_matched:
            print(f"[WARNING] Hostname {self.host} not in SAN: {san_list}")

        self.results['certificate'] = cert_info
        ssock.close()

    def check_cipher_suites(self):
        """检查协商的密码套件安全性"""
        cipher = self.results.get('cipher', {})
        name = cipher.get('name', '')

        risks = []
        if 'CBC' in name:
            risks.append(('WARNING', f'CBC 模式: {name}（存在填充攻击风险）'))
        if 'RC4' in name:
            risks.append(('CRITICAL', f'RC4 已破解: {name}'))
        if '3DES' in name:
            risks.append(('WARNING', f'3DES 不安全: {name}（Sweet32）'))
        if 'ECDHE' in name or 'DHE' in name:
            risks.append(('OK', '前向保密已启用'))
        else:
            risks.append(('WARNING', '无前向保密（RSA 密钥交换）'))
        if 'GCM' in name or 'CHACHA20' in name:
            risks.append(('OK', '使用 AEAD 加密'))

        self.results['cipher_risks'] = risks
        for level, msg in risks:
            print(f"    [{level}] {msg}")

    def check_hsts(self):
        """检查 HSTS 头"""
        try:
            context = ssl.create_default_context()
            conn = socket.create_connection((self.host, self.port))
            ssock = context.wrap_socket(conn, server_hostname=self.host)
            ssock.send(f"HEAD / HTTP/1.1\r\nHost: {self.host}\r\nConnection: close\r\n\r\n".encode())
            response = ssock.recv(4096).decode('utf-8', errors='ignore')
            if 'strict-transport-security' in response.lower():
                print(f"[OK] HSTS header present")
                self.results['hsts'] = True
            else:
                print(f"[WARNING] HSTS header missing")
                self.results['hsts'] = False
            ssock.close()
        except Exception as e:
            print(f"[!] HSTS check failed: {e}")
            self.results['hsts'] = None

    def run_all_checks(self):
        """运行所有检查"""
        print(f"\n{'='*50}")
        print(f"TLS Security Scan: {self.host}:{self.port}")
        print(f"{'='*50}\n")

        print("[*] Checking protocol & cipher...")
        self.check_protocol_versions()

        print("\n[*] Checking certificate...")
        self.check_certificate()

        print("\n[*] Checking cipher security...")
        self.check_cipher_suites()

        print("\n[*] Checking HSTS...")
        self.check_hsts()

        print(f"\n{'='*50}")
        print("Scan complete.")
        return self.results


if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else 'www.example.com'
    scanner = TLSScanner(target)
    results = scanner.run_all_checks()
```

---

## 七、mTLS 双向认证

### 7.1 mTLS 应用场景

**mTLS（mutual TLS）** 在标准 TLS 基础上增加客户端证书验证，实现双向身份认证。

```
单向 TLS：                     双向 mTLS：
  Server → 证书 → Client          Server → 证书 → Client
  Client 验证 Server 身份          Client 验证 Server 身份
  Server 不验证 Client            Server → 证书请求 → Client
                                  Client → 证书 → Server
                                  Server 验证 Client 身份
```

**适用场景**：
- 微服务间通信（零信任网络）
- B2B API 认证
- Kubernetes API Server
- IoT 设备认证

```bash
# 创建 CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=mTLS-CA"

# 创建服务器证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=server.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# 创建客户端证书
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client-001"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# Nginx mTLS 配置
# ssl_client_certificate /etc/nginx/ssl/ca.crt;
# ssl_verify_client on;
# ssl_verify_depth 2;
```

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # 客户端证书验证
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location /api/ {
        if ($ssl_client_verify != SUCCESS) {
            return 403;
        }
        proxy_pass http://backend;
    }
}
```

### 7.2 服务网格中的 mTLS

```
┌──────────────────────────────────────────────────────────┐
│                   服务网格 mTLS 架构                      │
│                                                          │
│  ┌─────────┐     ┌───────────┐     ┌───────────┐       │
│  │ Service A│←──→│ Envoy     │←mTLS→│ Envoy     │←──→│Service B│
│  │         │    │ (Sidecar) │←───→│ (Sidecar) │    │         │
│  └─────────┘     └───────────┘     └───────────┘       │
│                                                          │
│  特点：                                                   │
│  - 应用代码无感知，mTLS 由 Sidecar 代理自动处理           │
│  - 自动证书轮换（通过 SPIFFE/SPIRE 或内置 CA）            │
│  - 细粒度授权策略（L4/L7）                               │
│  - 全量流量加密（零信任核心要求）                          │
└──────────────────────────────────────────────────────────┘
```

**Istio mTLS 配置**：

```yaml
# Istio PeerAuthentication（命名空间级强制 mTLS）
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # STRICT = 仅 mTLS，PERMISSIVE = 允许明文过渡期
---
# DestinationRule 指定客户端使用 mTLS
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: enable-mtls
spec:
  host: "*.production.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL  # 使用 Istio 内置 mTLS
```

**Linkerd mTLS 配置**：

```bash
# Linkerd 默认启用 mTLS（自动）
# 检查 mTLS 状态
linkerd check --proxy

# 查看服务间 mTLS 情况
linkerd viz edges -n production
# 输出包含 TLS 列（true = mTLS 已建立）
```

---

## 八、总结

TLS/SSL 协议是网络通信安全的基石，本文覆盖的关键要点：

- **演进方向**：全面迁移到 TLS 1.3，彻底淘汰 SSL 3.0/TLS 1.0/1.1
- **握手核心**：TLS 1.3 的 1-RTT 握手和 0-RTT 恢复大幅降低延迟
- **PKI 体系**：证书链验证、CT 日志、ACME 自动化是信任链的保障
- **安全配置**：优先 ECDHE + AEAD 密码套件，启用 HSTS，禁用 CBC/RC4/3DES
- **历史教训**：Heartbleed/POODLE/CRIME 等漏洞推动协议持续改进
- **调试工具**：OpenSSL s_client、SSL Labs、testssl.sh 是必备检测手段
- **mTLS**：服务网格零信任的关键技术，Sidecar 代理自动处理证书管理

安全工程师应定期用 testssl.sh 和 SSL Labs 扫描所有对外服务，确保 TLS 配置符合最新安全标准。
