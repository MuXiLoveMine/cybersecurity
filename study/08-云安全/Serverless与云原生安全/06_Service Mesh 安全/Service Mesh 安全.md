# Service Mesh 安全

### 6.1 Service Mesh 概述

Service Mesh（如 Istio、Linkerd）通过 sidecar 代理接管服务间流量，提供：
- 流量管理（路由、负载均衡）
- 可观测性（指标、链路追踪）
- 安全（mTLS、授权策略）

### 6.2 Istio 安全功能

#### mTLS 双向认证

Istio 自动为网格内服务间通信启用 mTLS，无需修改应用代码：

```yaml
# 命名空间启用严格 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
```

#### 授权策略

```yaml
# 仅允许 web 服务访问 api 服务，且必须来自特定命名空间
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-allow-web
  namespace: prod
spec:
  selector:
    matchLabels:
      app: api
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/web-sa"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

#### RequestAuthentication（JWT 校验）

```yaml
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: prod
spec:
  selector:
    matchLabels:
      app: api
  jwtRules:
  - issuer: "https://keycloak.example.com/realms/prod"
    jwksUri: "https://keycloak.example.com/realms/prod/protocol/openid-connect/certs"
    forwardOriginalToken: true
```

### 6.3 Linkerd 安全功能

Linkerd 同样提供 mTLS，配置更简单：

```bash
# 默认启用 mTLS
linkerd install | kubectl apply -f -

# 查看网格内 mTLS 状态
linkerd check --proxy
```

### 6.4 零信任网络

Service Mesh 是零信任网络的落地实现：
- 每个服务身份由证书标识
- 每次调用都双向认证
- 基于身份与请求属性做细粒度授权
- 加密所有东西向流量
- 通信不再依赖网络边界信任

---

---

## 📋 内容审核与补充建议

> 针对「Service Mesh 安全」部分的内容审核结果：

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
