# PKI部署与运维实践

### 9.1 企业PKI架构设计

```
企业PKI典型架构：

  ┌──────────────────────────────────────────────────┐
  │                  离线根CA                          │
  │  ┌─────────┐  ┌──────────┐  ┌──────────┐        │
  │  │ HSM     │  │ 审计日志  │  │ 备份系统  │        │
  │  │ (FIPS   │  │          │  │          │        │
  │  │  140-3) │  │          │  │          │        │
  │  └─────────┘  └──────────┘  └──────────┘        │
  └────────────────────┬─────────────────────────────┘
                       │ 离线签发
  ┌────────────────────▼─────────────────────────────┐
  │              在线中间CA（Issuing CA）              │
  │  ┌─────────┐  ┌──────────┐  ┌──────────┐        │
  │  │ HSM     │  │ RA       │  │ CRL/OCSP │        │
  │  │         │  │ 审批系统  │  │ 响应器   │        │
  │  └─────────┘  └──────────┘  └──────────┘        │
  └────────────────────┬─────────────────────────────┘
                       │ 在线签发
  ┌────────────────────▼─────────────────────────────┐
  │                  终端实体                          │
  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │
  │  │Web  │ │API  │ │邮件 │ │VPN  │ │设备 │      │
  │  │服务 │ │服务 │ │服务 │ │网关 │ │证书 │      │
  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘      │
  └──────────────────────────────────────────────────┘
```

### 9.2 使用OpenSSL搭建CA

```bash
#!/bin/bash
# OpenSSL CA搭建脚本

# CA目录结构
CA_DIR="./myCA"
mkdir -p "$CA_DIR"/{certs,crl,newcerts,private,csr}
chmod 700 "$CA_DIR/private"
touch "$CA_DIR/index.txt"
echo 1000 > "$CA_DIR/serial"
echo 1000 > "$CA_DIR/crlnumber"

# CA配置文件
cat > "$CA_DIR/openssl.cnf" << 'EOF'
[ca]
default_ca = CA_default

[CA_default]
dir               = ./myCA
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
RANDFILE          = $dir/private/.rand
certificate       = $dir/cacert.pem
private_key       = $dir/private/cakey.pem
default_md        = sha256
preserve          = no
policy            = policy_match
default_days      = 365
default_crl_days  = 30

[policy_match]
countryName             = match
stateOrProvinceName     = optional
organizationName        = match
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[req]
default_bits       = 2048
default_keyfile    = privkey.pem
default_md        = sha256
distinguished_name = req_distinguished_name
req_extensions    = v3_req

[req_distinguished_name]
countryName             = Country Name (2 letter code)
stateOrProvinceName     = State or Province Name
localityName            = Locality Name
organizationName        = Organization Name
organizationalUnitName  = Organizational Unit Name
commonName              = Common Name
emailAddress            = Email Address

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth

[v3_ca]
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints = CA:true
keyUsage = cRLSign, keyCertSign

[server_cert]
basicConstraints = CA:FALSE
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer:always
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
authorityInfoAccess = OCSP;URI:http://ocsp.example.com
crlDistributionPoints = URI:http://crl.example.com/ca.crl
EOF

# 1. 生成CA密钥对和根证书
echo "=== 创建根CA ==="
openssl req -config "$CA_DIR/openssl.cnf" \
    -new -x509 -extensions v3_ca \
    -keyout "$CA_DIR/private/cakey.pem" \
    -out "$CA_DIR/cacert.pem" \
    -days 3650 -sha256 \
    -subj "/C=CN/O=MyOrg/CN=My Root CA"

chmod 400 "$CA_DIR/private/cakey.pem"

# 2. 签发服务器证书
echo "=== 签发服务器证书 ==="

# 2.1 生成服务器密钥对和CSR
openssl genrsa -out "$CA_DIR/private/server.key" 2048

openssl req -config "$CA_DIR/openssl.cnf" \
    -new -key "$CA_DIR/private/server.key" \
    -out "$CA_DIR/csr/server.csr" \
    -subj "/C=CN/O=MyOrg/CN=www.example.com"

# 2.2 用CA签发证书
openssl ca -config "$CA_DIR/openssl.cnf" \
    -extensions server_cert \
    -in "$CA_DIR/csr/server.csr" \
    -out "$CA_DIR/certs/server.crt" \
    -batch

# 3. 生成CRL
echo "=== 生成CRL ==="
openssl ca -config "$CA_DIR/openssl.cnf" \
    -gencrl -out "$CA_DIR/crl/ca.crl"

echo "=== 完成 ==="
echo "CA证书: $CA_DIR/cacert.pem"
echo "服务器证书: $CA_DIR/certs/server.crt"
echo "服务器私钥: $CA_DIR/private/server.key"
```

### 9.3 证书监控与告警

```python
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from cryptography import x509
import os
import json

class CertificateMonitor:
    """证书监控与告警系统"""
    
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.cert_paths = self.config.get('certificates', [])
        self.thresholds = self.config.get('thresholds', {
            'critical': 7,
            'warning': 30,
            'notice': 60
        })
        self.smtp_config = self.config.get('smtp', {})
        self.alert_recipients = self.config.get('alert_recipients', [])
        
    def scan_certificates(self) -> list:
        """扫描所有证书"""
        results = []
        
        for cert_info in self.cert_paths:
            path = cert_info['path']
            name = cert_info.get('name', path)
            
            if not os.path.exists(path):
                results.append({
                    'name': name,
                    'path': path,
                    'status': 'not_found',
                    'error': '证书文件不存在'
                })
                continue
            
            try:
                with open(path, 'rb') as f:
                    cert_data = f.read()
                
                # 尝试PEM格式
                try:
                    cert = x509.load_pem_x509_certificate(cert_data)
                except Exception:
                    cert = x509.load_der_x509_certificate(cert_data)
                
                now = datetime.utcnow()
                expiry = cert.not_valid_after
                days_remaining = (expiry - now).days
                
                if days_remaining < 0:
                    status = 'expired'
                elif days_remaining <= self.thresholds['critical']:
                    status = 'critical'
                elif days_remaining <= self.thresholds['warning']:
                    status = 'warning'
                elif days_remaining <= self.thresholds['notice']:
                    status = 'notice'
                else:
                    status = 'ok'
                
                # 提取SAN域名
                san_domains = []
                try:
                    san = cert.extensions.get_extension_for_class(
                        x509.SubjectAlternativeName
                    )
                    san_domains = san.value.get_values_for_type(
                        x509.DNSName
                    )
                except x509.ExtensionNotFound:
                    pass
                
                results.append({
                    'name': name,
                    'path': path,
                    'status': status,
                    'subject': cert.subject.rfc4514_string(),
                    'issuer': cert.issuer.rfc4514_string(),
                    'serial': hex(cert.serial_number),
                    'not_before': cert.not_valid_before.isoformat(),
                    'not_after': expiry.isoformat(),
                    'days_remaining': days_remaining,
                    'san_domains': san_domains
                })
                
            except Exception as e:
                results.append({
                    'name': name,
                    'path': path,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def send_alert(self, results: list):
        """发送告警邮件"""
        alerts = [r for r in results if r['status'] in 
                  ['expired', 'critical', 'warning']]
        
        if not alerts:
            print("没有需要告警的证书")
            return
        
        # 构建邮件内容
        subject = f"[证书告警] {len(alerts)}个证书需要关注"
        
        body = "以下证书需要关注:\n\n"
        for alert in alerts:
            body += f"--- {alert['name']} ---\n"
            body += f"状态: {alert['status']}\n"
            if 'days_remaining' in alert:
                body += f"剩余天数: {alert['days_remaining']}\n"
            if 'not_after' in alert:
                body += f"到期时间: {alert['not_after']}\n"
            if 'subject' in alert:
                body += f"主题: {alert['subject']}\n"
            body += f"路径: {alert['path']}\n\n"
        
        # 发送邮件
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = self.smtp_config.get('from')
        msg['To'] = ', '.join(self.alert_recipients)
        
        try:
            with smtplib.SMTP(
                self.smtp_config['host'],
                self.smtp_config['port']
            ) as server:
                if self.smtp_config.get('use_tls', True):
                    server.starttls()
                if self.smtp_config.get('username'):
                    server.login(
                        self.smtp_config['username'],
                        self.smtp_config['password']
                    )
                server.send_message(msg)
            print(f"告警邮件已发送给 {len(self.alert_recipients)} 个收件人")
        except Exception as e:
            print(f"发送邮件失败: {e}")
    
    def run(self):
        """执行监控"""
        print(f"[{datetime.now().isoformat()}] 开始证书监控...")
        
        results = self.scan_certificates()
        
        # 输出报告
        print("\n" + "=" * 60)
        print("证书扫描报告")
        print("=" * 60)
        
        for result in results:
            status_emoji = {
                'ok': '[OK]',
                'notice': '[NOTICE]',
                'warning': '[WARNING]',
                'critical': '[CRITICAL]',
                'expired': '[EXPIRED]',
                'error': '[ERROR]',
                'not_found': '[NOT_FOUND]'
            }.get(result['status'], '[UNKNOWN]')
            
            print(f"\n{status_emoji} {result['name']}")
            if 'days_remaining' in result:
                print(f"  剩余: {result['days_remaining']}天")
            if 'not_after' in result:
                print(f"  到期: {result['not_after']}")
            if 'error' in result:
                print(f"  错误: {result['error']}")
        
        # 发送告警
        self.send_alert(results)
        
        return results


# 配置文件示例 (cert_monitor.json)
"""
{
    "certificates": [
        {"path": "/etc/ssl/certs/server1.pem", "name": "Web服务器1"},
        {"path": "/etc/ssl/certs/server2.pem", "name": "API服务器"},
        {"path": "/etc/pki/tls/certs/mail.pem", "name": "邮件服务器"}
    ],
    "thresholds": {
        "critical": 7,
        "warning": 30,
        "notice": 60
    },
    "smtp": {
        "host": "smtp.example.com",
        "port": 587,
        "from": "cert-monitor@example.com",
        "username": "user",
        "password": "pass",
        "use_tls": true
    },
    "alert_recipients": [
        "admin@example.com",
        "ops@example.com"
    ]
}
"""
```

---

---

## 📋 内容审核与补充建议

> 针对「PKI部署与运维实践」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
