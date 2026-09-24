# 证书机构（CA）运作机制

### 4.1 CA信任框架

现代浏览器和操作系统内置了大量受信任的根CA证书。这些根CA是整个PKI信任体系的基石。

```
信任层次：

  浏览器/操作系统信任库
       │
       ├── 根CA证书（自签名，预装）
       │      │
       │      ├── 中间CA证书
       │      │      │
       │      │      ├── 终端证书（网站）
       │      │      └── 终端证书（网站）
       │      │
       │      └── 中间CA证书
       │             │
       │             └── 终端证书（网站）
       │
       └── 根CA证书
              │
              └── ...
```

### 4.2 CA认证级别

**CA/浏览器论坛（CA/Browser Forum）** 定义了两种主要的证书认证级别：

| 类型 | 验证要求 | 验证内容 | 签发时间 |
|------|---------|---------|---------|
| DV (Domain Validation) | 域名控制验证 | 仅验证域名所有权 | 几分钟 |
| OV (Organization Validation) | 组织验证 | 验证组织实体和域名 | 1-3天 |
| EV (Extended Validation) | 扩展验证 | 最严格的身份验证 | 3-7天 |

**DV证书验证方式：**
1. **电子邮件验证**：向域名WHOIS中的邮箱发送验证邮件
2. **DNS TXT记录**：在域名DNS中添加特定TXT记录
3. **HTTP文件验证**：在网站根目录放置验证文件
4. **TLS-ALPN验证**：通过TLS扩展进行验证

**EV证书特征：**
- 证书中包含完整的组织信息
- 地址栏显示组织名称（旧版浏览器）
- 审计要求严格
- 签发前需要严格的文件审核

### 4.3 CA运营要求

**CA/Browser Forum基线要求（Baseline Requirements）：**

| 要求领域 | 说明 |
|----------|------|
| 身份验证 | 严格的申请者身份验证流程 |
| 密钥管理 | CA私钥必须使用HSM保护，至少FIPS 140-2 Level 3 |
| 审计 | 年度WebTrust或ETSI审计 |
| 证书撤销 | 24小时内处理撤销请求 |
| 安全 incident | 必须在24小时内报告安全事件 |
| 日志记录 | 保留至少2年的操作日志 |
| 灾难恢复 | 必须有灾难恢复计划 |
| 网络安全 | 符合网络安全框架要求 |

### 4.4 证书透明度（Certificate Transparency）

**证书透明度（CT）** 是一个公开审计框架，要求CA将签发的证书提交到公开的CT日志中。

**CT的目的：**
- 让域名所有者发现未经授权的证书签发
- 让CA的签发行为可审计
- 防止CA恶意或错误签发证书

**CT架构：**

```
┌────────┐    提交证书    ┌──────────────┐
│   CA    │ ──────────→ │  CT日志       │
└────────┘              │  (append-only)│
                         └──────┬───────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
         ┌────────┐       ┌────────┐       ┌────────┐
         │ 监控者  │       │ 审计者  │       │ 查询者  │
         │Monitor │       │Auditor │       │ Lookup │
         └────────┘       └────────┘       └────────┘
```

**SCT（Signed Certificate Timestamp）：**
CA提交证书到CT日志后，会收到一个SCT（签名证书时间戳），证明证书已被记录。

```
SCT包含：
  - 版本号
  - 日志ID
  - 时间戳
  - 证书条目
  - 扩展数据
  - 日志签名
```

**CT强制要求：**
- Chrome要求所有新签发的证书必须包含SCT
- 否则浏览器会显示证书错误

### 4.5 自建CA实践

```python
#!/usr/bin/env python3
"""
自建CA管理系统
使用Python cryptography库实现完整的CA功能
"""

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import datetime
import ipaddress
from typing import Optional, List

class CertificateAuthority:
    """自建CA管理系统"""
    
    def __init__(self, ca_cert_path: str, ca_key_path: str):
        """
        初始化CA
        
        Args:
            ca_cert_path: CA证书路径
            ca_key_path: CA私钥路径
        """
        self.ca_cert = self._load_cert(ca_cert_path)
        self.ca_key = self._load_key(ca_key_path)
        
    def _load_cert(self, path: str) -> x509.Certificate:
        """加载PEM格式证书"""
        with open(path, 'rb') as f:
            return x509.load_pem_x509_certificate(f.read())
    
    def _load_key(self, path: str) -> rsa.RSAPrivateKey:
        """加载PEM格式私钥"""
        with open(path, 'rb') as f:
            return serialization.load_pem_private_key(
                f.read(), password=None
            )
    
    @staticmethod
    def create_root_ca(
        common_name: str,
        organization: str,
        country: str,
        key_size: int = 4096,
        validity_years: int = 20
    ) -> tuple:
        """
        创建根CA
        
        Args:
            common_name: CA名称
            organization: 组织名
            country: 国家代码
            key_size: 密钥大小
            validity_years: 有效年数
            
        Returns:
            (证书PEM, 私钥PEM)
        """
        # 生成CA密钥对
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # 证书主题
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # 构建证书
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365*validity_years)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()),
            critical=False
        ).sign(ca_key, hashes.SHA256())
        
        # 序列化
        cert_pem = cert.public_bytes(Encoding.PEM)
        key_pem = ca_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            NoEncryption()
        )
        
        return cert_pem, key_pem
    
    def create_intermediate_ca(
        self,
        common_name: str,
        organization: str,
        country: str,
        path_length: int = 0,
        validity_years: int = 10
    ) -> tuple:
        """
        创建中间CA
        
        Args:
            common_name: 中间CA名称
            organization: 组织名
            country: 国家代码
            path_length: 路径长度约束
            validity_years: 有效年数
            
        Returns:
            (证书PEM, 私钥PEM)
        """
        # 生成中间CA密钥对
        int_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        
        # 证书主题
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # 用根CA签发
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            int_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365*validity_years)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=path_length),
            critical=True
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(int_key.public_key()),
            critical=False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(self.ca_key.public_key()),
            critical=False
        ).sign(self.ca_key, hashes.SHA256())
        
        cert_pem = cert.public_bytes(Encoding.PEM)
        key_pem = int_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            NoEncryption()
        )
        
        return cert_pem, key_pem
    
    def sign_server_certificate(
        self,
        common_name: str,
        san_domains: List[str],
        san_ips: Optional[List[str]] = None,
        organization: str = "",
        country: str = "",
        key_type: str = "rsa",
        key_size: int = 2048,
        validity_days: int = 365
    ) -> tuple:
        """
        签发服务器证书
        
        Args:
            common_name: 通用名称（主域名）
            san_domains: SAN域名列表
            san_ips: SAN IP地址列表
            organization: 组织名
            country: 国家代码
            key_type: 密钥类型 (rsa/ec)
            key_size: RSA密钥大小
            validity_days: 有效天数
            
        Returns:
            (证书PEM, 私钥PEM)
        """
        # 生成密钥对
        if key_type == "rsa":
            server_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
        elif key_type == "ec":
            server_key = ec.generate_private_key(ec.SECP256R1())
        else:
            raise ValueError(f"不支持的密钥类型: {key_type}")
        
        # 证书主题
        name_attrs = []
        if country:
            name_attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, country))
        if organization:
            name_attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))
        name_attrs.append(x509.NameAttribute(NameOID.COMMON_NAME, common_name))
        
        subject = x509.Name(name_attrs)
        
        # 构建SAN列表
        san_list = [x509.DNSName(d) for d in san_domains]
        if san_ips:
            san_list.extend([x509.IPAddress(ipaddress.ip_address(ip)) for ip in san_ips])
        
        # 签发证书
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            server_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        ).add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH
            ]),
            critical=False
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(server_key.public_key()),
            critical=False
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(self.ca_key.public_key()),
            critical=False
        ).add_extension(
            x509.CRLDistributionPoints([
                x509.DistributionPoint(
                    full_name=[x509.UniformResourceIdentifier("http://ca.example.com/crl/ca.crl")],
                    relative_name=None,
                    reasons=None,
                    crl_issuer=None
                )
            ]),
            critical=False
        ).add_extension(
            x509.AuthorityInformationAccess([
                x509.AccessDescription(
                    x509.AuthorityInformationAccessOID.OCSP,
                    x509.UniformResourceIdentifier("http://ocsp.ca.example.com")
                ),
                x509.AccessDescription(
                    x509.AuthorityInformationAccessOID.CA_ISSUERS,
                    x509.UniformResourceIdentifier("http://ca.example.com/ca.crt")
                )
            ]),
            critical=False
        ).sign(self.ca_key, hashes.SHA256())
        
        cert_pem = cert.public_bytes(Encoding.PEM)
        key_pem = server_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            NoEncryption()
        )
        
        return cert_pem, key_pem
    
    def verify_certificate(self, cert_pem: bytes) -> dict:
        """
        验证证书
        
        Returns:
            验证结果字典
        """
        cert = x509.load_pem_x509_certificate(cert_pem)
        
        result = {
            'subject': cert.subject.rfc4514_string(),
            'issuer': cert.issuer.rfc4514_string(),
            'serial': hex(cert.serial_number),
            'not_valid_before': cert.not_valid_before.isoformat(),
            'not_valid_after': cert.not_valid_after.isoformat(),
            'is_expired': datetime.datetime.utcnow() > cert.not_valid_after,
            'is_ca': False,
            'san_domains': [],
            'key_usage': {},
            'signature_valid': False,
        }
        
        # 检查Basic Constraints
        try:
            bc = cert.extensions.get_extension_for_class(x509.BasicConstraints)
            result['is_ca'] = bc.value.ca
        except x509.ExtensionNotFound:
            pass
        
        # 检查SAN
        try:
            san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            result['san_domains'] = san.value.get_values_for_type(x509.DNSName)
        except x509.ExtensionNotFound:
            pass
        
        # 检查Key Usage
        try:
            ku = cert.extensions.get_extension_for_class(x509.KeyUsage)
            result['key_usage'] = {
                'digital_signature': ku.value.digital_signature,
                'key_encipherment': ku.value.key_encipherment,
                'key_cert_sign': ku.value.key_cert_sign,
            }
        except x509.ExtensionNotFound:
            pass
        
        # 验证签名
        try:
            self.ca_cert.public_key().verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                cert.signature_algorithm,
            )
            result['signature_valid'] = True
        except Exception:
            result['signature_valid'] = False
        
        return result


# ==============================================================
# 使用示例
# ==============================================================

if __name__ == "__main__":
    import os
    
    # 1. 创建根CA
    print("=" * 60)
    print("步骤1: 创建根CA")
    print("=" * 60)
    
    root_cert, root_key = CertificateAuthority.create_root_ca(
        common_name="My Root CA",
        organization="My Organization",
        country="CN"
    )
    
    with open("root_ca.pem", "wb") as f:
        f.write(root_cert)
    with open("root_ca.key", "wb") as f:
        f.write(root_key)
    
    print("根CA证书: root_ca.pem")
    print("根CA私钥: root_ca.key")
    
    # 2. 创建中间CA
    print("\n" + "=" * 60)
    print("步骤2: 创建中间CA")
    print("=" * 60)
    
    ca = CertificateAuthority("root_ca.pem", "root_ca.key")
    
    int_cert, int_key = ca.create_intermediate_ca(
        common_name="My Intermediate CA",
        organization="My Organization",
        country="CN",
        path_length=0
    )
    
    with open("int_ca.pem", "wb") as f:
        f.write(int_cert)
    with open("int_ca.key", "wb") as f:
        f.write(int_key)
    
    print("中间CA证书: int_ca.pem")
    print("中间CA私钥: int_ca.key")
    
    # 3. 签发服务器证书
    print("\n" + "=" * 60)
    print("步骤3: 签发服务器证书")
    print("=" * 60)
    
    int_ca = CertificateAuthority("int_ca.pem", "int_ca.key")
    
    server_cert, server_key = int_ca.sign_server_certificate(
        common_name="www.example.com",
        san_domains=["www.example.com", "example.com", "api.example.com"],
        san_ips=["192.168.1.100"],
        organization="Example Inc",
        country="CN",
        key_type="rsa",
        key_size=2048,
        validity_days=365
    )
    
    with open("server.pem", "wb") as f:
        f.write(server_cert)
    with open("server.key", "wb") as f:
        f.write(server_key)
    
    print("服务器证书: server.pem")
    print("服务器私钥: server.key")
    
    # 4. 验证证书
    print("\n" + "=" * 60)
    print("步骤4: 验证证书")
    print("=" * 60)
    
    result = int_ca.verify_certificate(server_cert)
    for k, v in result.items():
        print(f"  {k}: {v}")
```

---

---

