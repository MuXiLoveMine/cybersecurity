# TLS 调试与检测

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

---

