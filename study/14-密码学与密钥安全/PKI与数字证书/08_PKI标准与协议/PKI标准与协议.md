# PKI标准与协议

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

---

## 📋 内容审核与补充建议

> 针对「PKI标准与协议」部分的内容审核结果：

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
