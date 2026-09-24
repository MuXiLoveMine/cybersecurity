# mTLS 双向认证

### 7.1 mTLS 应用场景

**mTLS（mutual TLS）** 在标准 TLS 基础上增加客户端证书验证，实现双向身份认证。

```
单向 TLS：                     双向 mTLS：
  Server → 证书 → Client          Server → 证书 → Client
  Client 验证 Server 身份          Client 验证 Server 身份
  Server 不验证 Client            Server → 证书请求 → Client
                                  Client → 证书 → Server
                                  Server 验证 Client 身份
```

**适用场景**：
- 微服务间通信（零信任网络）
- B2B API 认证
- Kubernetes API Server
- IoT 设备认证

```bash
# 创建 CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=mTLS-CA"

# 创建服务器证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=server.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365

# 创建客户端证书
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=client-001"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# Nginx mTLS 配置
# ssl_client_certificate /etc/nginx/ssl/ca.crt;
# ssl_verify_client on;
# ssl_verify_depth 2;
```

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # 客户端证书验证
    ssl_client_certificate /etc/nginx/ssl/ca.crt;
    ssl_verify_client on;
    ssl_verify_depth 2;

    location /api/ {
        if ($ssl_client_verify != SUCCESS) {
            return 403;
        }
        proxy_pass http://backend;
    }
}
```

### 7.2 服务网格中的 mTLS

```
┌──────────────────────────────────────────────────────────┐
│                   服务网格 mTLS 架构                      │
│                                                          │
│  ┌─────────┐     ┌───────────┐     ┌───────────┐       │
│  │ Service A│←──→│ Envoy     │←mTLS→│ Envoy     │←──→│Service B│
│  │         │    │ (Sidecar) │←───→│ (Sidecar) │    │         │
│  └─────────┘     └───────────┘     └───────────┘       │
│                                                          │
│  特点：                                                   │
│  - 应用代码无感知，mTLS 由 Sidecar 代理自动处理           │
│  - 自动证书轮换（通过 SPIFFE/SPIRE 或内置 CA）            │
│  - 细粒度授权策略（L4/L7）                               │
│  - 全量流量加密（零信任核心要求）                          │
└──────────────────────────────────────────────────────────┘
```

**Istio mTLS 配置**：

```yaml
# Istio PeerAuthentication（命名空间级强制 mTLS）
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # STRICT = 仅 mTLS，PERMISSIVE = 允许明文过渡期
---
# DestinationRule 指定客户端使用 mTLS
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: enable-mtls
spec:
  host: "*.production.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL  # 使用 Istio 内置 mTLS
```

**Linkerd mTLS 配置**：

```bash
# Linkerd 默认启用 mTLS（自动）
# 检查 mTLS 状态
linkerd check --proxy

# 查看服务间 mTLS 情况
linkerd viz edges -n production
# 输出包含 TLS 列（true = mTLS 已建立）
```

---

---

