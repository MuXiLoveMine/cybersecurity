# X.509数字证书标准

### 3.1 X.509标准概述

**X.509** 是国际电信联盟（ITU-T）制定的数字证书标准，目前广泛使用的是X.509 v3版本。

**X.509版本演进：**

| 版本 | 年份 | 主要特性 |
|------|------|---------|
| v1 | 1988 | 基本证书格式 |
| v2 | 1993 | 唯一标识符（用于CA重命名） |
| v3 | 1996 | 扩展字段（最重要的改进） |

### 3.2 X.509证书结构

一个X.509 v3证书包含以下字段：

```
Certificate ::= SEQUENCE {
    tbsCertificate       TBSCertificate,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertificate ::= SEQUENCE {
    version         [0]  EXPLICIT Version DEFAULT v1,
    serialNumber         CertificateSerialNumber,
    signature            AlgorithmIdentifier,
    issuer               Name,
    validity             Validity,
    subject              Name,
    subjectPublicKeyInfo SubjectPublicKeyInfo,
    issuerUniqueID  [1]  IMPLICIT UniqueIdentifier OPTIONAL,  -- v2+
    subjectUniqueID [2]  IMPLICIT UniqueIdentifier OPTIONAL,  -- v2+
    extensions      [3]  EXPLICIT Extensions OPTIONAL           -- v3
}
```

### 3.3 证书各字段详解

#### 3.3.1 基本字段

| 字段 | 说明 | 示例 |
|------|------|------|
| version | 证书版本号 | v3 (2) |
| serialNumber | 序列号（CA内唯一） | 0x1A2B3C |
| signature | CA签名算法 | sha256WithRSAEncryption |
| issuer | 签发者（CA）名称 | CN=DigiCert TLS RSA SHA256 2020 CA1 |
| validity | 有效期 | 2024-01-01 至 2025-01-01 |
| subject | 主体（证书所有者）名称 | CN=www.example.com |
| subjectPublicKeyInfo | 主体公钥信息 | RSA 2048位公钥 |

#### 3.3.2 主体名称（Subject Name）

证书的主体名称使用**DN（Distinguished Name，可辨别名称）**格式：

```
DN字段：
  CN (Common Name)         通用名称，通常是域名或人名
  O (Organization)          组织名称
  OU (Organizational Unit)  组织单位
  C (Country)              国家代码（两字母）
  ST (State)               州/省
  L (Locality)             城市
  E (Email)                邮箱地址

示例：
  CN=www.example.com, O=Example Inc, C=US
```

#### 3.3.3 主体公钥信息（SubjectPublicKeyInfo）

```
SubjectPublicKeyInfo ::= SEQUENCE {
    algorithm        AlgorithmIdentifier,  -- 公钥算法标识
    subjectPublicKey BIT STRING            -- 实际公钥数据
}

示例：
  algorithm: rsaEncryption (1.2.840.113549.1.1.1)
  subjectPublicKey: 3048 3089 0081 8500 0282 0100 ...
```

### 3.4 证书扩展字段（Extensions）

X.509 v3最重要的改进是引入了扩展字段，每个扩展包含：

| 属性 | 说明 |
|------|------|
| extnID | 扩展标识符（OID） |
| critical | 是否为关键扩展（必须被识别和处理） |
| extnValue | 扩展值 |

#### 3.4.1 常见扩展字段

| 扩展名称 | OID | 用途 |
|----------|-----|------|
| Subject Key Identifier | 2.5.29.14 | 主体公钥标识符 |
| Authority Key Identifier | 2.5.29.35 | 签发者公钥标识符 |
| Subject Alternative Name | 2.5.29.17 | 主体备用名称（SAN） |
| Basic Constraints | 2.5.29.19 | CA标志和路径长度 |
| Key Usage | 2.5.29.15 | 密钥用途 |
| Extended Key Usage | 2.5.29.37 | 扩展密钥用途 |
| CRL Distribution Points | 2.5.29.31 | CRL分发点 |
| Authority Information Access | 1.3.6.1.5.5.7.1.1 | CA信息访问（OCSP地址） |
| Certificate Policies | 2.5.29.32 | 证书策略 |
| Name Constraints | 2.5.29.30 | 名称约束（CA专用） |

#### 3.4.2 Subject Alternative Name（SAN）

SAN是现代证书最重要的扩展之一，允许一张证书保护多个域名：

```
Subject Alternative Name:
  DNS Name: www.example.com
  DNS Name: example.com
  DNS Name: api.example.com
  DNS Name: *.example.com  (通配符)
  IP Address: 192.168.1.1
  Email: admin@example.com
  URI: https://example.com
```

**注意：** 现代浏览器（Chrome 58+）已经**忽略CN字段**，仅通过SAN验证域名。

#### 3.4.3 Basic Constraints

```
Basic Constraints:
  cA: TRUE          ← 标记此证书为CA证书
  pathLenConstraint: 2  ← 允许的中间CA层数

  cA: FALSE         ← 标记此证书为终端实体证书
```

#### 3.4.4 Key Usage

```
Key Usage:
  Digital Signature    签名（认证、不可抵赖）
  Non Repudiation      不可抵赖（内容承诺）
  Key Encipherment     密钥加密（密钥传输）
  Data Encipherment    数据加密（直接加密数据）
  Key Agreement        密钥协商（DH/ECDH）
  Key Cert Sign        证书签名（CA证书）
  CRL Sign             CRL签名
  Encipher Only        仅加密
  Decipher Only        仅解密
```

#### 3.4.5 Extended Key Usage（EKU）

| EKU | OID | 用途 |
|-----|-----|------|
| serverAuth | 1.3.6.1.5.5.7.3.1 | TLS服务器认证 |
| clientAuth | 1.3.6.1.5.5.7.3.2 | TLS客户端认证 |
| codeSigning | 1.3.6.1.5.5.7.3.3 | 代码签名 |
| emailProtection | 1.3.6.1.5.5.7.3.4 | 邮件保护（S/MIME） |
| timeStamping | 1.3.6.1.5.5.7.3.8 | 时间戳 |
| OCSPSigning | 1.3.6.1.5.5.7.3.9 | OCSP签名 |

### 3.5 证书格式

#### 3.5.1 PEM格式

```
-----BEGIN CERTIFICATE-----
MIIDXTCCA0WgAwIBAgIJAKa1Z3Wq3J5bMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
...
BAYTAlVTMRAwDgYDVQQDDAdleGFtcGxl
-----END CERTIFICATE-----
```

- Base64编码
- 最常用的格式
- 可包含多个证书（证书链）
- 文件扩展名：.pem, .crt, .cer

#### 3.5.2 DER格式

- 二进制格式
- 不可读
- 效率更高
- 文件扩展名：.der, .cer

#### 3.5.3 PKCS#7格式

- 可包含证书链和CRL
- Base64或二进制
- 文件扩展名：.p7b, .p7c

#### 3.5.4 PKCS#12格式

- 包含证书和私钥
- 加密保护
- 文件扩展名：.p12, .pfx

```bash
# 格式转换
# PEM转DER
openssl x509 -in cert.pem -outform DER -out cert.der

# DER转PEM
openssl x509 -in cert.der -inform DER -outform PEM -out cert.pem

# PEM转PKCS#12（含私钥）
openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.p12 -name "My Cert"

# PKCS#12转PEM
openssl pkcs12 -in cert.p12 -out cert.pem -nodes
```

### 3.6 查看证书内容

```bash
# 查看证书详情
openssl x509 -in cert.pem -text -noout

# 查看证书的公钥
openssl x509 -in cert.pem -pubkey -noout

# 查看证书的指纹
openssl x509 -in cert.pem -fingerprint -sha256 -noout

# 验证证书链
openssl verify -CAfile ca.pem -untrusted intermediate.pem cert.pem

# 查看远程服务器的证书
echo | openssl s_client -connect www.example.com:443 -servername www.example.com 2>/dev/null | openssl x509 -text -noout
```

---

---

## 📋 内容审核与补充建议

> 针对「X.509数字证书标准」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
