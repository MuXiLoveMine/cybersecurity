# CRL与OCSP证书状态检查

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

---

