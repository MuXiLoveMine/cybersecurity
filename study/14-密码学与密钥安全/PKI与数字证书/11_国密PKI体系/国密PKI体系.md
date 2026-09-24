# 国密PKI体系

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

---

