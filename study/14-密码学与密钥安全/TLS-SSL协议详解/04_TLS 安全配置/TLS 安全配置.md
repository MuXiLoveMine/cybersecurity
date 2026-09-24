# TLS 安全配置

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

---

