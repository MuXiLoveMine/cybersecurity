# PKI与数字证书

> PKI（公钥基础设施）是现代网络安全的核心基石，它通过数字证书、证书机构和信任链机制，解决了公钥的信任分发问题。本文全面讲解PKI体系架构、X.509证书标准、CA运作机制、证书生命周期管理以及实际部署中的安全考量。

---

## 目录

1. [PKI概述](#一pki概述)
2. [PKI体系架构](#二pki体系架构)
3. [X.509数字证书标准](#三x509数字证书标准)
4. [证书机构（CA）运作机制](#四证书机构ca运作机制)
5. [信任链与证书验证](#五信任链与证书验证)
6. [证书生命周期管理](#六证书生命周期管理)
7. [CRL与OCSP证书状态检查](#七crl与ocsp证书状态检查)
8. [PKI标准与协议](#八pki标准与协议)
9. [PKI部署与运维实践](#九pki部署与运维实践)
10. [PKI安全威胁与防护](#十pki安全威胁与防护)
11. [国密PKI体系](#十一国密pki体系)
12. [云原生PKI与自动化证书管理](#十二云原生pki与自动化证书管理)
13. [PKI应用场景分析](#十三pki应用场景分析)
14. [总结与最佳实践](#十四总结与最佳实践)

---

## 一、PKI概述

### 1.1 什么是PKI

**PKI（Public Key Infrastructure，公钥基础设施）** 是一套用公钥密码技术提供安全服务的通用基础平台和规范集合，它能够为网络应用提供密钥和证书管理体系，支持加密、数字签名、身份认证等安全服务。

**PKI的核心价值：**
- 解决公钥的信任分发问题
- 实现网络身份的可信认证
- 支撑机密性、完整性、不可抵赖性服务
- 是HTTPS/TLS、代码签名、邮件加密等的基础

### 1.2 为什么需要PKI

在公钥密码学中，用户拥有公钥和私钥对。公钥可以公开，私钥必须保密。但核心问题是：**如何确认一个公钥确实属于声称的所有者？**

```
没有PKI的世界：
  Alice的公钥 → 如何证明这确实是Alice的公钥？
  
  攻击者Mallory可以：
  1. 替换Alice的公钥为自己的公钥
  2. 冒充Alice与他人通信
  3. 中间人攻击（MITM）
  
有了PKI：
  可信第三方（CA）为Alice的公钥签发数字证书
  证书 = Alice的公钥 + Alice的身份信息 + CA的签名
  验证证书 = 验证CA的签名 → 确认公钥归属
```

### 1.3 PKI发展简史

| 时间 | 事件 | 意义 |
|------|------|------|
| 1976年 | Diffie-Hellman提出公钥密码思想 | 公钥密码学诞生 |
| 1978年 | RSA算法发表 | 第一个实用的公钥算法 |
| 1988年 | X.509 v1标准发布 | 数字证书标准化 |
| 1993年 | X.509 v2标准发布 | 引入CA和证书撤销列表 |
| 1995年 | Verisign成立 | 首批商业CA |
| 1996年 | X.509 v3标准发布 | 支持证书扩展字段 |
| 2002年 | Let's Encrypt提出 | 推动免费证书普及 |
| 2015年 | Let's Encrypt正式提供服务 | HTTPS大规模普及 |
| 2015年 | 证书透明度（CT）机制推出 | 证书签发可审计 |
| 2018年 | eTLS/RFC 8446（TLS 1.3） | 简化证书验证流程 |

### 1.4 PKI的核心组成

```
┌─────────────────────────────────────────────────────────┐
│                    PKI体系架构                            │
├─────────────┬───────────────────────────────────────────┤
│   证书机构   │  签发和管理数字证书的信任机构                 │
│   （CA）     │  根CA → 中间CA → 终端证书                    │
├─────────────┼───────────────────────────────────────────┤
│   注册机构   │  证书注册的审批机构                           │
│   （RA）     │  身份审核 → 证书申请审批                      │
├─────────────┼───────────────────────────────────────────┤
│   证书库    │  证书的存储和查询服务                          │
│  （Repository）│  LDAP/HTTP协议查询                          │
├─────────────┼───────────────────────────────────────────┤
│   CRL发布者  │  证书撤销列表的发布                           │
│             │  列出已撤销的证书                             │
├─────────────┼───────────────────────────────────────────┤
│   OCSP响应者 │  在线证书状态查询服务                         │
│             │  实时返回证书状态                              │
├─────────────┼───────────────────────────────────────────┤
│   终端实体   │  证书的持有者和依赖方                         │
│   （EE）     │  使用证书进行安全通信                          │
└─────────────┴───────────────────────────────────────────┘
```

### 1.5 PKI提供的安全服务

| 安全服务 | 说明 | 实现方式 |
|----------|------|---------|
| 身份认证 | 确认通信对方的真实身份 | 证书证明公钥归属，数字签名验证身份 |
| 机密性 | 防止信息被未授权者获取 | 用对方公钥加密会话密钥 |
| 完整性 | 防止信息被篡改 | 数字签名 + 消息认证码 |
| 不可抵赖性 | 防止发送方否认发送过信息 | 数字签名 + 时间戳 + 审计日志 |

---

## 二、PKI体系架构

### 2.1 PKI组件详解

#### 2.1.1 证书机构（CA）

**CA（Certificate Authority，证书机构）** 是PKI的信任核心，负责签发和管理数字证书。

**CA的分类：**

| 类型 | 说明 | 示例 |
|------|------|------|
| 公共CA | 面向公众提供证书服务 | DigiCert, Let's Encrypt, GlobalSign |
| 私有CA | 组织内部使用的CA | 企业内部PKI、OpenSSL自签CA |
| 根CA | PKI信任链的起点 | 预装在操作系统/浏览器中的根证书 |
| 中间CA | 由根CA授权，签发终端证书 | CA的分支机构 |
| 策略CA | 定义证书策略的CA | 特定行业或用途的CA |

**CA的核心功能：**
1. 密钥对生成（可选）
2. 证书签发
3. 证书撤销
4. 证书状态查询
5. 证书归档
6. 密钥托管（可选）
7. 证书策略发布

**CA的安全要求：**
- 根CA私钥必须在HSM（硬件安全模块）中生成和存储
- 根CA必须离线运行
- CA操作必须有审计日志
- CA系统必须有物理安全防护
- CA必须有灾难恢复计划

#### 2.1.2 注册机构（RA）

**RA（Registration Authority，注册机构）** 是CA的附属机构，负责处理证书注册的审批。

**RA的职责：**
1. 接收证书申请
2. 验证申请者身份
3. 审核申请信息的准确性
4. 批准或拒绝证书申请
5. 生成密钥对（可选，在线方式）
6. 密钥托管（可选）
7. 证书撤销请求审批

**RA与CA的分工：**

```
证书申请流程中RA与CA的分工：

  申请者 → RA → CA
           │     │
           │     ├── 签发证书
           │     └── 管理证书生命周期
           │
           ├── 身份验证
           ├── 信息审核
           └── 审批申请
```

#### 2.1.3 证书库

证书库用于存储已签发的证书，供依赖方查询和获取。

| 实现方式 | 协议 | 特点 |
|----------|------|------|
| LDAP目录 | LDAP v3 | 传统PKI的标准方式 |
| HTTP/REST | HTTP | 现代Web应用常用 |
| 数据库 | SQL | 企业内部CA常用 |
| 分布式存储 | DHT/P2P | 去中心化PKI |

### 2.2 信任模型

#### 2.2.1 层次模型（Hierarchical Model）

```
          ┌──────────┐
          │  根CA     │  ← 信任锚点
          └────┬─────┘
        ┌──────┼──────┐
        ▼      ▼      ▼
    ┌─────┐┌─────┐┌─────┐
    │中间CA││中间CA││中间CA│
    └──┬──┘└──┬──┘└──┬──┘
       │      │      │
    终端证书  终端证书  终端证书
```

**特点：**
- 所有信任最终追溯到同一个根CA
- 验证路径清晰：终端 → 中间CA → 根CA
- 适合集中式管理
- 单点失效风险（根CA被攻破则全盘崩溃）

#### 2.2.2 网状模型（Mesh Model）

```
    CA1 ←────→ CA2
    │  ╲      ╱  │
    │   ╲    ╱   │
    │    ╲  ╱    │
    │  ╲  ╲╱  ╱  │
    ▼   ╲╱╲ ╱    ▼
    CA3 ←────→ CA4
```

**特点：**
- 多个CA之间建立交叉认证
- 没有单一信任锚点
- 验证路径复杂，可能存在多条路径
- 更好的容错性
- 适合多方协作场景

#### 2.2.3 桥CA模型（Bridge CA Model）

```
    ┌──────────┐
    │  桥CA     │  ← 连接不同PKI域
    └──┬─┬─┬──┘
       │ │ │
    ┌──┘ │ └──┐
    ▼    ▼    ▼
  ┌───┐┌───┐┌───┐
  │PKI1││PKI2││PKI3│
  │域  ││域  ││域  │
  └───┘└───┘└───┘
```

**特点：**
- 桥CA与各PKI域的根CA建立交叉认证
- 不同PKI域之间通过桥CA互信
- 桥CA本身不是信任锚点
- 适合跨组织/跨行业协作

#### 2.2.4 Web of Trust模型

```
    Alice ←────→ Bob
     │  ╲      ╱  │
     │   ╲    ╱   │
     │    ╲  ╱    │
     ▼     ╲╱     ▼
    Carol ←────→ Dave
```

**特点：**
- 没有中心化的CA
- 用户之间互相签名认证
- 信任是传递的（但会衰减）
- PGP/GnuPG使用的模型
- 适合小规模、去中心化场景

### 2.3 PKI信任锚点

**信任锚点（Trust Anchor）** 是PKI中验证链的最顶层信任来源。

| 信任锚点类型 | 说明 | 示例 |
|------------|------|------|
| 操作系统信任库 | 预装在OS中的根证书 | Windows证书存储、macOS Keychain |
| 浏览器信任库 | 预装在浏览器中的根证书 | Firefox自带根证书库 |
| 应用配置 | 应用自行配置的信任根 | 自定义CA的根证书 |
| 硬件安全模块 | HSM中存储的信任根 | 国密SM2根证书 |

**信任锚点管理：**

```python
# 查看系统信任的根证书（Linux）
# cat /etc/ssl/certs/ca-certificates.crt | openssl x509 -text -noout

# 查看Windows证书存储
# PowerShell:
Get-ChildItem -Path Cert:\LocalMachine\Root | Format-List Subject, Thumbprint, NotAfter

# 查看macOS系统根证书
# security find-certificate -a -p /Library/Keychains/System.keychain
```

---

## 三、X.509数字证书标准

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

## 四、证书机构（CA）运作机制

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

## 五、信任链与证书验证

### 5.1 证书链验证流程

证书验证是一个从终端证书追溯到信任锚点的过程：

```
验证流程：

  终端证书 ← 中间CA签发
      ↓
  中间CA证书 ← 根CA签发
      ↓
  根CA证书 ← 操作系统/浏览器信任库
  
验证步骤：
  1. 检查证书签名（逐级验证）
  2. 检查有效期
  3. 检查证书撤销状态（CRL/OCSP）
  4. 检查域名匹配（SAN/CN）
  5. 检查密钥用途（Key Usage/EKU）
  6. 检查Basic Constraints
  7. 检查策略约束
  8. 检查名称约束
```

### 5.2 证书路径构建

```python
class CertificatePathValidator:
    """证书路径验证器"""
    
    def __init__(self, trust_store: list):
        """
        Args:
            trust_store: 受信任的根CA证书列表
        """
        self.trust_store = trust_store
        
    def build_path(self, cert: x509.Certificate, 
                   intermediate_certs: list) -> list:
        """
        构建证书路径
        
        Args:
            cert: 终端证书
            intermediate_certs: 可用的中间CA证书
            
        Returns:
            证书路径列表 [终端证书, 中间CA, ..., 根CA]
        """
        path = [cert]
        current = cert
        
        while True:
            # 检查是否自签名（根CA）
            if current.subject == current.issuer:
                # 检查是否在信任库中
                for trusted in self.trust_store:
                    if trusted.subject == current.subject:
                        path.append(trusted)
                        return path
                raise ValueError(f"自签名证书不在信任库中: {current.subject}")
            
            # 查找签发者
            issuer = self._find_issuer(current, intermediate_certs)
            if issuer is None:
                raise ValueError(f"找不到证书签发者: {current.issuer}")
            
            path.append(issuer)
            current = issuer
            
            # 检查路径长度限制
            if len(path) > 10:
                raise ValueError("证书路径过长（超过10级）")
        
    def _find_issuer(self, cert: x509.Certificate, 
                     candidates: list) -> x509.Certificate:
        """在候选证书中查找签发者"""
        for candidate in candidates:
            if candidate.subject == cert.issuer:
                return candidate
        # 检查信任库
        for trusted in self.trust_store:
            if trusted.subject == cert.issuer:
                return trusted
        return None
    
    def validate_path(self, path: list, hostname: str = None) -> dict:
        """
        验证证书路径
        
        Args:
            path: 证书路径
            hostname: 要验证的主机名
            
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 1. 验证每级签名
        for i in range(len(path) - 1):
            cert = path[i]
            issuer = path[i + 1]
            
            try:
                issuer.public_key().verify(
                    cert.signature,
                    cert.tbs_certificate_bytes,
                    cert.signature_algorithm
                )
            except Exception as e:
                result['valid'] = False
                result['errors'].append(f"签名验证失败: {e}")
        
        # 2. 验证根CA在信任库中
        root = path[-1]
        if root not in self.trust_store:
            result['valid'] = False
            result['errors'].append("根CA不在信任库中")
        
        # 3. 检查有效期
        now = datetime.datetime.utcnow()
        for cert in path:
            if now < cert.not_valid_before:
                result['valid'] = False
                result['errors'].append(
                    f"证书尚未生效: {cert.subject}"
                )
            if now > cert.not_valid_after:
                result['valid'] = False
                result['errors'].append(
                    f"证书已过期: {cert.subject}"
                )
        
        # 4. 检查主机名匹配
        if hostname:
            leaf = path[0]
            if not self._check_hostname(leaf, hostname):
                result['valid'] = False
                result['errors'].append(f"主机名不匹配: {hostname}")
        
        # 5. 检查Basic Constraints
        for i, cert in enumerate(path[1:]):  # 跳过终端证书
            try:
                bc = cert.extensions.get_extension_for_class(
                    x509.BasicConstraints
                )
                if not bc.value.ca:
                    result['valid'] = False
                    result['errors'].append(
                        f"非CA证书签发了其他证书: {cert.subject}"
                    )
                # 检查路径长度
                if bc.value.path_length is not None:
                    if i > bc.value.path_length:
                        result['valid'] = False
                        result['errors'].append(
                            f"超过路径长度限制: {cert.subject}"
                        )
            except x509.ExtensionNotFound:
                result['warnings'].append(
                    f"缺少Basic Constraints: {cert.subject}"
                )
        
        # 6. 检查Key Usage
        for cert in path[1:]:
            try:
                ku = cert.extensions.get_extension_for_class(x509.KeyUsage)
                if not ku.value.key_cert_sign:
                    result['valid'] = False
                    result['errors'].append(
                        f"证书无签名权限: {cert.subject}"
                    )
            except x509.ExtensionNotFound:
                pass
        
        return result
    
    def _check_hostname(self, cert: x509.Certificate, 
                        hostname: str) -> bool:
        """检查主机名是否匹配证书"""
        # 检查SAN
        try:
            san = cert.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            )
            dns_names = san.value.get_values_for_type(x509.DNSName)
            for name in dns_names:
                if self._match_hostname(name, hostname):
                    return True
        except x509.ExtensionNotFound:
            pass
        
        # 回退到CN（不推荐）
        cn_attrs = cert.subject.get_attributes_for_oid(
            NameOID.COMMON_NAME
        )
        if cn_attrs:
            return self._match_hostname(cn_attrs[0].value, hostname)
        
        return False
    
    @staticmethod
    def _match_hostname(pattern: str, hostname: str) -> bool:
        """匹配主机名（支持通配符）"""
        if pattern.startswith('*.'):
            # 通配符匹配
            suffix = pattern[1:]  # .example.com
            return hostname.endswith(suffix) and \
                   hostname.count('.') == pattern.count('.')
        return pattern.lower() == hostname.lower()
```

### 5.3 证书绑定（Certificate Pinning）

证书绑定是一种额外的安全机制，将特定的证书或公钥与某个域名/应用绑定。

```
证书绑定方式：
  1. 证书绑定（绑定完整证书）
  2. 公钥绑定（绑定公钥，推荐）
  3. SPKI绑定（绑定公钥的哈希）

SPKI Pin格式：
  pin-sha256="base64(sha256(SPKI))"
  
示例（Google的pins）：
  pin-sha256="YLh1dUR9y6Kja30R3..."  (Google Root CA)
  pin-sha256="Vfd95BxB..."  (Google中间CA)
```

```python
import hashlib
import base64

def generate_spki_pin(cert_pem: bytes) -> str:
    """
    从证书生成SPKI pin
    
    Args:
        cert_pem: PEM格式证书
        
    Returns:
        pin-sha256="..." 格式的pin
    """
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    
    cert = x509.load_pem_x509_certificate(cert_pem)
    public_key = cert.public_key()
    
    # 获取SPKI DER编码
    spki_der = public_key.public_bytes(
        Encoding.DER,
        PublicFormat.SubjectPublicKeyInfo
    )
    
    # 计算SHA256哈希
    hash_value = hashlib.sha256(spki_der).digest()
    base64_hash = base64.b64encode(hash_value).decode('ascii')
    
    return f'pin-sha256="{base64_hash}"'


# HPKP (HTTP Public Key Pinning) 示例
# 注意: HPKP已被废弃，但概念仍在使用
"""
HTTP头示例：
Public-Key-Pins: 
  pin-sha256="YLh1dUR9y6Kja30R3...", 
  pin-sha256="Vfd95BxB...",
  max-age=5184000,
  includeSubDomains
"""
```

**注意：** HPKP（HTTP Public Key Pinning）已被各大浏览器废弃，因为它的误用可能导致永久性的站点锁定。但证书绑定的概念在移动应用和客户端软件中仍然广泛使用。

---

## 六、证书生命周期管理

### 6.1 证书生命周期总览

```
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
│ 申请  │→ │ 审批  │→ │ 签发  │→ │ 使用  │→ │ 续期  │→ │ 撤销  │
└──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘
                                       │                      │
                                       ▼                      ▼
                                  ┌──────┐             ┌──────┐
                                  │ 归档  │             │ 销毁  │
                                  └──────┘             └──────┘
```

### 6.2 证书申请流程

```
证书申请流程（CSR方式）：

  1. 申请者生成密钥对
     ├── 私钥保存在安全位置
     └── 公钥用于创建CSR

  2. 创建CSR（证书签名请求）
     ├── 主题信息（CN, O, C等）
     ├── 公钥
     └── 申请者私钥签名

  3. 提交CSR给CA
     └── 通过RA进行身份验证

  4. CA审核
     ├── 验证域名所有权
     ├── 验证组织信息（OV/EV）
     └── 审批申请

  5. CA签发证书
     ├── 用CA私钥签名
     ├── 添加扩展字段
     └── 返回证书给申请者
```

**CSR生成：**

```bash
# 使用OpenSSL生成CSR
# 1. 生成私钥
openssl genrsa -out server.key 2048

# 2. 生成CSR
openssl req -new -key server.key -out server.csr -sha256

# 按提示输入信息：
# Country Name (2 letter code): CN
# State or Province Name: Beijing
# Locality Name: Beijing
# Organization Name: Example Inc
# Common Name: www.example.com
# Email Address: admin@example.com

# 3. 查看CSR内容
openssl req -in server.csr -text -noout

# 4. 带SAN的CSR（需要配置文件）
cat > san.cnf << 'EOF'
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = CN
O = Example Inc
CN = www.example.com

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = www.example.com
DNS.2 = example.com
DNS.3 = api.example.com
IP.1 = 192.168.1.1
EOF

openssl req -new -key server.key -out server.csr -config san.cnf -sha256
```

```python
# 使用Python生成CSR
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

def generate_csr(common_name, organization, country, san_domains, key_size=2048):
    """
    生成CSR（证书签名请求）
    
    Args:
        common_name: 通用名称
        organization: 组织名
        country: 国家代码
        san_domains: SAN域名列表
        key_size: 密钥大小
        
    Returns:
        (CSR PEM, 私钥 PEM)
    """
    # 生成密钥对
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size
    )
    
    # 构建CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(d) for d in san_domains
        ]),
        critical=False
    ).sign(private_key, hashes.SHA256())
    
    csr_pem = csr.public_bytes(Encoding.PEM)
    key_pem = private_key.private_bytes(
        Encoding.PEM,
        PrivateFormat.TraditionalOpenSSL,
        NoEncryption()
    )
    
    return csr_pem, key_pem


# 使用示例
csr_pem, key_pem = generate_csr(
    common_name="www.example.com",
    organization="Example Inc",
    country="CN",
    san_domains=["www.example.com", "example.com", "api.example.com"]
)

with open("server.csr", "wb") as f:
    f.write(csr_pem)
with open("server.key", "wb") as f:
    f.write(key_pem)

print("CSR生成完成")
print(f"CSR内容预览:\n{csr_pem.decode()[:500]}...")
```

### 6.3 证书续期

```python
class CertificateRenewalManager:
    """证书续期管理器"""
    
    RENEWAL_THRESHOLDS = {
        'critical': 7,    # 7天内到期 - 紧急
        'warning': 30,    # 30天内到期 - 警告
        'notice': 60,     # 60天内到期 - 通知
    }
    
    @staticmethod
    def check_renewal_needed(cert_pem: bytes) -> dict:
        """
        检查证书是否需要续期
        
        Returns:
            {
                'needs_renewal': bool,
                'days_remaining': int,
                'status': 'ok'/'notice'/'warning'/'critical'/'expired',
                'not_after': datetime
            }
        """
        cert = x509.load_pem_x509_certificate(cert_pem)
        
        now = datetime.datetime.utcnow()
        expiry = cert.not_valid_after
        days_remaining = (expiry - now).days
        
        if days_remaining < 0:
            status = 'expired'
            needs_renewal = True
        elif days_remaining <= CertificateRenewalManager.RENEWAL_THRESHOLDS['critical']:
            status = 'critical'
            needs_renewal = True
        elif days_remaining <= CertificateRenewalManager.RENEWAL_THRESHOLDS['warning']:
            status = 'warning'
            needs_renewal = True
        elif days_remaining <= CertificateRenewalManager.RENEWAL_THRESHOLDS['notice']:
            status = 'notice'
            needs_renewal = True
        else:
            status = 'ok'
            needs_renewal = False
        
        return {
            'needs_renewal': needs_renewal,
            'days_remaining': days_remaining,
            'status': status,
            'not_after': expiry,
            'subject': cert.subject.rfc4514_string()
        }
    
    @staticmethod
    def batch_check(certificates: dict) -> list:
        """
        批量检查证书续期状态
        
        Args:
            certificates: {name: cert_pem}
            
        Returns:
            排序后的检查结果列表
        """
        results = []
        for name, cert_pem in certificates.items():
            result = CertificateRenewalManager.check_renewal_needed(cert_pem)
            result['name'] = name
            results.append(result)
        
        # 按剩余天数排序（最紧急的在前）
        results.sort(key=lambda x: x['days_remaining'])
        
        return results
```

### 6.4 证书撤销

**证书撤销原因代码（RFC 5280）：**

| 代码 | 原因 | 说明 |
|------|------|------|
| 0 | unspecified | 未指定 |
| 1 | keyCompromise | 密钥泄露 |
| 2 | cACompromise | CA被攻破 |
| 3 | affiliationChanged | 附属关系变更 |
| 4 | superseded | 证书被替代 |
| 5 | cessationOfOperation | 停止运营 |
| 6 | certificateHold | 证书暂停 |
| 8 | removeFromCRL | 从CRL中移除 |
| 9 | privilegeWithdrawn | 权限撤回 |
| 10 | aACompromise | AA被攻破 |

**撤销流程：**
```
1. 证书持有者向CA提交撤销请求
2. CA验证撤销请求的合法性
3. CA将证书加入CRL
4. CA更新OCSP响应
5. 依赖方通过CRL/OCSP获知证书已撤销
```

---

## 七、CRL与OCSP证书状态检查

### 7.1 CRL（证书撤销列表）

**CRL** 是CA定期发布的一个已撤销证书的列表。

```
CRL结构：
  ├── 版本号
  ├── 签名算法
  ├── 签发者（CA名称）
  ├── 更新时间
  ├── 下次更新时间
  ├── 撤销证书列表
  │   ├── 序列号
  │   ├── 撤销时间
  │   └── 撤销原因
  ├── CRL扩展
  └── CA签名
```

**CRL的优缺点：**

| 优点 | 缺点 |
|------|------|
| 离线验证 | 列表可能很大 |
| 简单实现 | 不是实时状态 |
| 一次下载可验证多张证书 | 下载延迟 |
| 可缓存 | 可能过期 |

### 7.2 OCSP（在线证书状态协议）

**OCSP** 允许依赖方实时查询证书的撤销状态。

```
OCSP请求/响应流程：

  客户端                    OCSP响应者
    │                          │
    │── OCSPRequest ──────────→│
    │   (证书序列号)            │
    │                          │ 查询数据库
    │                          │
    │←── OCSPResponse ─────────│
    │   (状态 + 签名)           │
    
OCSP状态：
  good      证书有效
  revoked   证书已撤销
  unknown   无法确定
```

```python
import http.client
from urllib.parse import urlparse
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class OCSPClient:
    """OCSP客户端"""
    
    @staticmethod
    def get_ocsp_url(cert: x509.Certificate) -> str:
        """从证书中获取OCSP URL"""
        try:
            aia = cert.extensions.get_extension_for_class(
                x509.AuthorityInformationAccess
            )
            for desc in aia.value:
                if desc.access_method == \
                   x509.AuthorityInformationAccessOID.OCSP:
                    return desc.access_location.value
        except x509.ExtensionNotFound:
            pass
        return None
    
    @staticmethod
    def check_status(cert_pem: bytes, issuer_cert_pem: bytes) -> dict:
        """
        检查证书的OCSP状态
        
        Args:
            cert_pem: 要检查的证书
            issuer_cert_pem: 签发者CA证书
            
        Returns:
            状态信息字典
        """
        cert = x509.load_pem_x509_certificate(cert_pem)
        issuer = x509.load_pem_x509_certificate(issuer_cert_pem)
        
        # 获取OCSP URL
        ocsp_url = OCSPClient.get_ocsp_url(cert)
        if not ocsp_url:
            return {'status': 'unknown', 'error': 'No OCSP URL'}
        
        # 构建OCSP请求
        builder = x509.OCSPRequestBuilder()
        builder = builder.add_certificate(cert, issuer, hashes.SHA1())
        # 注意: 实际使用应使用SHA256，某些CA可能只支持SHA1
        request = builder.build()
        
        # 序列化请求
        request_der = request.public_bytes(serialization.Encoding.DER)
        
        # 发送HTTP请求
        parsed = urlparse(ocsp_url)
        conn = http.client.HTTPSConnection(parsed.netloc)
        conn.request(
            "POST",
            parsed.path,
            body=request_der,
            headers={
                "Content-Type": "application/ocsp-request",
                "Accept": "application/ocsp-response"
            }
        )
        
        response = conn.getresponse()
        response_data = response.read()
        conn.close()
        
        # 解析响应
        ocsp_response = x509.ocsp.load_der_ocsp_response(response_data)
        
        result = {
            'status': ocsp_response.certificate_status.name,
            'response_time': ocsp_response.response_time,
            'this_update': ocsp_response.this_update,
            'next_update': ocsp_response.next_update,
            'ocsp_url': ocsp_url
        }
        
        if ocsp_response.certificate_status == \
           x509.OCSPCertStatus.REVOKED:
            result['revocation_time'] = \
                ocsp_response.revocation_time
            result['revocation_reason'] = \
                ocsp_response.revocation_reason.name \
                if ocsp_response.revocation_reason else 'unspecified'
        
        return result
```

### 7.3 OCSP装订（OCSP Stapling）

**OCSP装订** 是一种优化机制，由服务器代替客户端获取OCSP响应，并在TLS握手时一并发送。

```
无OCSP装订：
  客户端 → 服务器（TLS握手）
  客户端 → OCSP响应者（查询证书状态）
  客户端 → 服务器（继续通信）
  
有OCSP装订：
  服务器 → OCSP响应者（预先获取OCSP响应，缓存）
  客户端 → 服务器（TLS握手 + OCSP响应一起发送）
  客户端 → 服务器（继续通信）
```

**OCSP装订的优点：**
- 减少客户端到OCSP响应者的请求
- 保护客户端隐私
- 加快TLS握手速度
- 避免OCSP响应者不可用的问题

**Nginx配置OCSP装订：**
```nginx
# OCSP Stapling配置
ssl_stapling on;
ssl_stapling_verify on;
ssl_stapling_responder http://ocsp.example.com;

# 需要完整的证书链
ssl_trusted_certificate /path/to/chain.pem;

# 错误日志
error_log /var/log/nginx/ocsp_error.log warn;

# 解析器配置（用于DNS查询OCSP响应者）
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

---

## 八、PKI标准与协议

### 8.1 PKI相关标准

| 标准 | 说明 |
|------|------|
| X.509 | 证书格式标准 |
| RFC 5280 | Internet X.509 PKI证书和CRL规范 |
| RFC 6960 | OCSP协议 |
| RFC 5755 | PKI属性证书 |
| PKCS #1 | RSA密码学标准 |
| PKCS #7 | 密码消息语法（CMS） |
| PKCS #8 | 私钥信息语法 |
| PKCS #10 | CSR格式标准 |
| PKCS #11 | 加密设备接口标准 |
| PKCS #12 | PFX个人信息交换语法 |
| SCEP | 简单证书注册协议 |
| EST | 安全证书注册协议（基于TLS） |
| ACME | 自动化证书管理环境 |
| CMP | 证书管理协议 |

### 8.2 ACME协议

**ACME（Automated Certificate Management Environment）** 是Let's Encrypt使用的自动化证书管理协议（RFC 8555）。

```
ACME协议流程：

  1. 客户端注册账户
     Client → ACME Server: POST /new-account
     
  2. 客户端下单
     Client → ACME Server: POST /new-order
     Server → Client: 返回挑战（challenges）
     
  3. 客户端完成挑战
     ├── HTTP-01: 在指定路径放置验证文件
     ├── DNS-01: 在DNS中添加TXT记录
     └── TLS-ALPN-01: 通过TLS扩展验证
     
  4. 客户端通知完成
     Client → ACME Server: POST /challenge/xxx
     
  5. 服务器验证挑战
     
  6. 客户端发送CSR
     Client → ACME Server: POST /finalize
     (CSR中包含公钥和域名信息)
     
  7. 服务器签发证书
     Client → ACME Server: POST /cert/xxx
     Server → Client: 返回证书
```

```python
# ACME客户端示例（使用acme库）
"""
使用acme库与Let's Encrypt交互

安装: pip install acme cryptography
"""

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from acme import client, messages, crypto_util
import jose

class ACMERegistration:
    """ACME自动注册管理"""
    
    def __init__(self, directory_url: str):
        """
        Args:
            directory_url: ACME目录URL
        """
        self.directory_url = directory_url
        self.account_key = None
        self.client = None
        
    def register_account(self, email: str):
        """注册ACME账户"""
        # 生成账户密钥
        self.account_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # 创建ACME客户端
        key = jose.JWKRSA(key=self.account_key)
        net = client.ClientNetwork(key)
        directory = messages.Directory.from_json(
            net.get(self.directory_url).json()
        )
        self.client = client.ClientV2(directory, net=net)
        
        # 注册账户
        registration = messages.NewRegistration.from_data(
            email=email,
            terms_of_service_agreed=True
        )
        self.client.net.account = self.client.new_account(registration)
        
        return self.client.net.account
    
    def order_certificate(self, domains: list, cert_key):
        """
        下单申请证书
        
        Args:
            domains: 要申请证书的域名列表
            cert_key: 证书私钥
            
        Returns:
            证书PEM
        """
        # 创建订单
        order = self.client.new_order(
            [messages.Identifier(typ=messages.IDENTIFIER_FQDN, 
                                value=d) for d in domains]
        )
        
        # 获取挑战
        authzrs = order.authorizations
        challenges = {}
        
        for authzr in authzrs:
            domain = authzr.identifier.value
            # 选择HTTP-01挑战
            for challenge in authzr.body.challenges:
                if challenge.typ == 'http-01':
                    challenges[domain] = challenge
                    break
        
        # 完成挑战（需要用户在Web服务器上放置验证文件）
        for domain, challenge in challenges.items():
            # 获取验证内容
            token = challenge.token
            key_authorization = \
                self.client.key_authorization(challenge)
            
            print(f"请在 {domain} 的 /.well-known/acme-challenge/\
                   {token} 放置以下内容：")
            print(f"  {key_authorization}")
            
            input("放置完成后按Enter继续...")
            
            # 通知ACME服务器
            self.client.answer_challenge(challenge, \
                challenge.response(self.account_key))
        
        # 等待验证完成
        for authzr in authzrs:
            self.client.poll(authzr)
        
        # 生成CSR
        csr = crypto_util.make_csr(
            cert_key, domains, 
            self.client.net.account.kid
        )
        
        # 完成订单
        order = self.client.finalize_order(order, csr)
        
        # 下载证书
        cert_pem = order.fullchain_pem
        
        return cert_pem
```

### 8.3 SCEP协议

**SCEP（Simple Certificate Enrollment Protocol）** 是Cisco开发的证书自动注册协议，广泛用于网络设备和企业环境。

```
SCEP操作类型：
  GetCACert    - 获取CA证书
  GetCACaps    - 获取CA能力
  PKIOperation - PKI操作（含消息类型）
    ├── PKCSReq     - 证书请求（PKCS#10 CSR）
    ├── CertRep     - 证书响应
    ├── GetCertInit - 获取初始证书
    ├── GetCert     - 获取证书
    └── GetCRL      - 获取CRL
```

---

## 九、PKI部署与运维实践

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

## 十、PKI安全威胁与防护

### 10.1 CA被攻破

**历史案例：**

| 事件 | 年份 | 影响 |
|------|------|------|
| Comodo欺诈签发 | 2011 | 9个欺诈证书（Gmail, Skype等） |
| DigiNotar被攻破 | 2011 | 500+欺诈证书，CA破产 |
| TurkTrust错误签发 | 2012 | 为google.com签发证书 |
| CNNIC违规 | 2015 | 为中间人测试签发证书 |
| Symantec不规范 | 2015-2017 | 多次违规，最终被Chrome移除 |

**防护措施：**
1. CA必须使用HSM保护私钥
2. 定期安全审计
3. 证书透明度（CT）强制
4. 多方签名（Multi-Party Authorization）
5. 严格的安全基线要求

### 10.2 中间人攻击

```
中间人攻击场景：

  Alice ←→ Mallory ←→ Bob
         (Mallory用自己的证书
          替换双方的证书)

防护：
  1. 证书绑定（Pinning）
  2. CT监控
  3. DNS CAA记录限制
  4. HSTS（HTTP严格传输安全）
  5. 证书透明度通知
```

### 10.3 DNS CAA记录

**CAA（Certification Authority Authorization）** DNS记录允许域名所有者指定哪些CA可以为其签发证书。

```
DNS CAA记录示例：

;; 只允许Let's Encrypt签发
example.com.    CAA 0 issue "letsencrypt.org"

;; 允许DigiCert和Let's Encrypt
example.com.    CAA 0 issue "digicert.com"
example.com.    CAA 0 issue "letsencrypt.org"

;; 指定违规报告邮箱
example.com.    CAA 0 iodef "mailto:security@example.com"

;; 禁止所有CA签发（通配符需要特殊授权）
example.com.    CAA 0 issuewild ";"
```

### 10.4 私钥泄露

**私钥泄露的应对：**
1. 立即撤销证书
2. 生成新密钥对
3. 申请新证书
4. 更新所有使用旧证书的服务
5. 调查泄露原因
6. 修复安全漏洞

---

## 十一、国密PKI体系

### 11.1 国密算法在PKI中的应用

中国商用密码算法在PKI中的应用：

| 算法 | 用途 | 对应国际算法 |
|------|------|------------|
| SM2 | 签名/密钥交换 | RSA/ECDSA |
| SM3 | 哈希 | SHA-256 |
| SM4 | 对称加密 | AES |
| SM9 | 标识签名 | 无（基于身份的密码） |

### 11.2 国密证书特点

国密证书与国际标准证书的主要区别：

| 特性 | 国际标准 | 国密标准 |
|------|---------|---------|
| 签名算法 | RSA/ECDSA/EdDSA | SM2 |
| 哈希算法 | SHA-256/384/512 | SM3 |
| 对称加密 | AES | SM4 |
| 证书格式 | X.509 v3 | GB/T 20518（兼容X.509 v3） |
| OID | 国际OID | 国密OID |

**国密算法OID：**
```
SM2签名:     1.2.156.10197.1.501
SM2加密:     1.2.156.10197.1.301
SM3哈希:     1.2.156.10197.1.401
SM4 ECB:    1.2.156.10197.1.104.1
SM4 CBC:    1.2.156.10197.1.104.2
```

### 11.3 GMSSL工具

```bash
# 使用GmSSL生成国密证书
# GmSSL是支持国密算法的OpenSSL分支

# 1. 生成SM2密钥对
gmssl ecparam -genkey -name sm2p256v1 -out sm2_key.pem

# 2. 生成CSR
gmssl req -new -key sm2_key.pem -out sm2.csr \
    -subj "/C=CN/O=MyOrg/CN=www.example.com" \
    -sm3

# 3. 自签名证书
gmssl req -new -x509 -key sm2_key.pem -out sm2_cert.pem \
    -days 365 -sm3 \
    -subj "/C=CN/O=MyOrg/CN=www.example.com"

# 4. 查看国密证书
gmssl x509 -in sm2_cert.pem -text -noout
```

### 11.4 双证书体系

中国金融等领域使用**双证书体系**：

```
双证书体系：
  签名证书：用于数字签名（签名密钥对）
    └── 私钥由用户自己保管，CA不知道

  加密证书：用于加密通信（加密密钥对）
    └── 私钥由CA托管，用于密钥恢复

签名密钥和加密密钥是不同的密钥对
```

---

## 十二、云原生PKI与自动化证书管理

### 12.1 cert-manager（Kubernetes证书管理）

**cert-manager** 是Kubernetes生态中最流行的证书管理工具。

```yaml
# cert-manager安装（Helm）
# helm repo add jetstack https://charts.jetstack.io
# helm install cert-manager jetstack/cert-manager

# 1. 配置Let's Encrypt签发者
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx

---
# 2. 申请证书
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com-tls
  namespace: default
spec:
  secretName: example-com-tls
  duration: 2160h  # 90天
  renewBefore: 360h  # 提前15天续期
  dnsNames:
  - example.com
  - www.example.com
  - api.example.com
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer

---
# 3. 使用证书的Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - example.com
    - www.example.com
    secretName: example-com-tls
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
```

### 12.2 内部CA自动化

```python
"""
HashiCorp Vault作为内部CA
Vault可以充当PKI后端，提供自动化证书管理
"""

# Vault PKI配置（命令行）
"""
# 1. 启用PKI密钥引擎
vault secrets enable -path=pki pki

# 2. 配置CA
vault write pki/root/generate/internal \
    common_name="Internal Root CA" \
    ttl=87600h  # 10年

# 3. 配置URL
vault write pki/config/urls \
    issuing_certificates="https://vault.internal:8200/v1/pki/ca" \
    crl_distribution_points="https://vault.internal:8200/v1/pki/crl"

# 4. 创建角色（定义证书策略）
vault write pki/roles/example-dot-com \
    allowed_domains="example.com" \
    allow_subdomains=true \
    max_ttl="720h"  # 30天

# 5. 签发证书
vault write pki/issue/example-dot-com \
    common_name="www.example.com" \
    ttl="24h"
"""

# Python客户端
import hvac

class VaultCAClient:
    """Vault PKI客户端"""
    
    def __init__(self, url: str, token: str, pki_path: str = "pki"):
        self.client = hvac.Client(url=url, token=token)
        self.pki_path = pki_path
    
    def issue_certificate(
        self,
        common_name: str,
        role: str,
        ttl: str = "24h",
        alt_names: str = None,
        ip_sans: str = None
    ) -> dict:
        """
        通过Vault签发证书
        
        Args:
            common_name: 通用名称
            role: Vault PKI角色名
            ttl: 有效期
            alt_names: 备用域名
            ip_sans: IP SAN
            
        Returns:
            包含证书和私钥的字典
        """
        data = {
            "common_name": common_name,
            "ttl": ttl
        }
        
        if alt_names:
            data["alt_names"] = alt_names
        if ip_sans:
            data["ip_sans"] = ip_sans
        
        response = self.client.write(
            f"{self.pki_path}/issue/{role}",
            **data
        )
        
        return response['data']
    
    def revoke_certificate(self, serial_number: str) -> dict:
        """撤销证书"""
        response = self.client.write(
            f"{self.pki_path}/revoke",
            serial_number=serial_number
        )
        return response['data']
    
    def get_crl(self, format_type: str = "pem") -> str:
        """获取CRL"""
        response = self.client.read(
            f"{self.pki_path}/crl"
        )
        return response['data']['crl']
```

### 12.3 SPIFFE/SPIRE

**SPIFFE（Secure Production Identity Framework for Everyone）** 是云原生工作负载身份标准。

```
SPIFFE身份格式：
  spiffe://<trust-domain>/<workload-identifier>
  
示例：
  spiffe://example.com/backend/payments
  spiffe://example.com/frontend/web
  spiffe://staging.example.com/database/mysql

SPIFFE组件：
  SPIRE Server  - 签发SVID（SPIFFE身份验证文件）
  SPIRE Agent   - 在节点上运行，为工作负载提供SVID
  
SVID类型：
  X.509 SVID  - 基于X.509证书的工作负载身份
  JWT SVID    - 基于JWT的工作负载身份
```

---

## 十三、PKI应用场景分析

### 13.1 HTTPS/TLS

PKI最广泛的应用场景，保护Web通信安全。

```
HTTPS证书验证流程：
  1. 浏览器连接服务器（TCP三次握手）
  2. TLS握手（服务器发送证书）
  3. 浏览器验证证书链
  4. 浏览器检查域名匹配
  5. 浏览器检查证书状态（OCSP/CRL）
  6. 密钥交换（生成会话密钥）
  7. 加密通信
```

### 13.2 代码签名

```
代码签名证书类型：
  ├── 标准代码签名（OV）
  ├── 扩展验证代码签名（EV）
  └── 内核驱动签名（WHQL/交叉签名）

签名流程：
  1. 计算文件哈希
  2. 用私钥签名哈希
  3. 将签名和证书嵌入文件
  4. 可选：添加时间戳
  
验证流程：
  1. 提取签名和证书
  2. 验证证书链
  3. 验证签名
  4. 验证时间戳
  5. 比对文件哈希
```

### 13.3 邮件安全（S/MIME）

```
S/MIME证书用途：
  ├── 加密邮件内容
  ├── 数字签名邮件
  └── 验证发件人身份

S/MIME操作：
  签名：用发件人私钥签名邮件
  加密：用收件人公钥加密邮件
  验证：用发件人公钥验证签名
  解密：用收件人私钥解密邮件
```

### 13.4 VPN认证

```
VPN中的证书用途：
  ├── 服务器身份认证
  ├── 客户端身份认证
  └── 双向TLS认证（mTLS）

IPSec VPN证书：
  - IKE协商中使用证书进行身份认证
  - 支持RSA和ECDSA签名

OpenVPN证书：
  - TLS双向认证
  - 服务器证书 + 客户端证书
  - 证书撤销列表控制访问
```

### 13.5 物联网设备认证

```
物联网PKI特点：
  ├── 大规模证书管理（百万级设备）
  ├── 设备证书自动注册（SCEP/EST）
  ├── 证书自动轮换
  ├── 轻量级证书格式
  └── 硬件安全存储（TPM/SE）

典型架构：
  设备 → 制造时注入证书 → 连接时mTLS认证 → OTA时证书更新
```

---

## 十四、总结与最佳实践

### 14.1 PKI最佳实践

| 实践领域 | 最佳实践 |
|----------|---------|
| 密钥管理 | 使用HSM保护CA私钥 |
| 密钥长度 | RSA至少2048位（推荐4096），ECC至少256位 |
| 签名算法 | 使用SHA-256或更高，禁用SHA-1和MD5 |
| 证书有效期 | 公网证书不超过397天，内部证书不超过1年 |
| 证书续期 | 提前30天开始续期流程 |
| 密钥轮换 | 定期更换密钥对，不要复用旧密钥 |
| SAN使用 | 所有域名必须通过SAN指定，不依赖CN |
| CT监控 | 监控CT日志，发现未授权证书签发 |
| CAA记录 | 配置DNS CAA记录限制可签发证书的CA |
| OCSP装订 | 启用OCSP Stapling优化性能 |
| 证书撤销 | 建立快速撤销响应流程 |
| 审计日志 | 记录所有证书操作，保留至少2年 |

### 14.2 PKI未来趋势

| 趋势 | 说明 |
|------|------|
| 自动化 | ACME协议普及，证书全生命周期自动化 |
| 短有效期 | 证书有效期越来越短（90天甚至更短） |
| 证书透明度 | CT日志成为强制要求 |
| 后量子密码 | 抗量子计算攻击的证书算法 |
| 去中心化 | 区块链技术在PKI中的应用探索 |
| 零信任 | PKI作为零信任架构的身份基础设施 |
| 云原生 | Kubernetes原生证书管理 |
| 国密化 | 中国市场的国密算法证书普及 |

### 14.3 参考资源

| 资源 | 说明 |
|------|------|
| RFC 5280 | Internet X.509 PKI证书和CRL规范 |
| RFC 6960 | OCSP协议规范 |
| RFC 8555 | ACME协议规范 |
| RFC 8446 | TLS 1.3协议规范 |
| CA/Browser Forum | CA基线要求 |
| NIST SP 800-57 | 密钥管理指南 |
| NIST FIPS 186-5 | 数字签名标准 |
| GM/T 0015 | 数字证书格式（国密标准） |

---

> **总结：** PKI是现代网络安全的基石。理解PKI体系架构、证书格式、信任模型、生命周期管理和安全威胁，对于任何网络安全从业者都是必备知识。随着云计算、物联网和零信任架构的发展，PKI的应用场景和重要性只会不断增加。掌握PKI的自动化管理和监控能力，是现代安全运维的核心技能。
