# TLS 证书与 PKI

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

---

## 📋 内容审核与补充建议

> 针对「TLS 证书与 PKI」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
