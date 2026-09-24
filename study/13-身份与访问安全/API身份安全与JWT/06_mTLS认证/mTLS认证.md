# mTLS认证

### 6.1 mTLS原理

```text
mTLS (双向TLS) 认证原理

标准TLS (单向):
  客户端 → 验证服务器证书 → 建立连接
  服务器不验证客户端

mTLS (双向):
  客户端 → 验证服务器证书 → 发送客户端证书
  服务器 → 验证客户端证书 → 建立连接
  双向身份验证

mTLS认证流程:
  1. ClientHello + 客户端证书请求
  2. ServerHello + 服务器证书 + 请求客户端证书
  3. 客户端验证服务器证书
  4. 客户端发送自己的证书
  5. 服务器验证客户端证书
  6. 密钥交换
  7. 建立加密通道

mTLS优势:
  ✓ 基于证书的身份认证
  ✓ 非对称加密，安全性高
  ✓ 证书可包含身份和权限信息
  ✓ 证书可撤销（CRL/OCSP）
  ✓ 传输加密一体化

mTLS适用场景:
  ├── 服务间通信（微服务）
  ├── API网关认证
  ├── IoT设备认证
  └── 高安全API访问
```

### 6.2 证书管理

```text
mTLS证书管理体系

┌────────────────────────────────────────────────────┐
│                  根CA (Root CA)                     │
│              签发中间CA证书                         │
└──────────────────────┬─────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐
│ 服务器CA   │  │ 客户端CA   │  │ API网关CA  │
│ 签发服务器 │  │ 签发客户端 │  │ 签发网关   │
│ 证书      │  │ 证书      │  │ 证书      │
└──────┬─────┘  └──────┬─────┘  └──────┬─────┘
       │               │               │
       ▼               ▼               ▼
  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │ API服务 │    │ 客户端  │    │ API网关 │
  │ 证书   │    │ 证书   │    │ 证书   │
  └─────────┘    └─────────┘    └─────────┘

证书生命周期:
├── 生成: 生成密钥对和CSR
├── 签发: CA验证并签发证书
├── 部署: 安装到服务/客户端
├── 轮换: 定期更换证书
├── 撤销: 通过CRL/OCSP撤销
└── 过期: 证书到期后更新
```

```python
# mTLS配置示例 (Python requests)

import requests

# 客户端证书和私钥
CLIENT_CERT = '/path/to/client.crt'
CLIENT_KEY = '/path/to/client.key'
CA_CERT = '/path/to/ca.crt'

# mTLS请求
def mtls_api_call(url, method='GET', data=None):
    """mTLS认证的API请求"""
    response = requests.request(
        method,
        url,
        cert=(CLIENT_CERT, CLIENT_KEY),  # 客户端证书
        verify=CA_CERT,                   # 验证服务器证书
        json=data
    )
    return response


# Nginx mTLS配置示例
NGINX_MTLS_CONFIG = """
server {
    listen 443 ssl;
    server_name api.example.com;

    # 服务器证书
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # 要求客户端证书
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    # API路由
    location /api/v1/ {
        # 检查客户端证书验证
        if ($ssl_client_verify != SUCCESS) {
            return 403;
        }

        # 传递客户端证书信息
        proxy_set_header X-Client-Verify $ssl_client_verify;
        proxy_set_header X-Client-DN $ssl_client_s_dn;
        proxy_set_header X-Client-Cert $ssl_client_escaped_cert;

        proxy_pass http://backend:8080;
    }
}
"""
```

---

---

