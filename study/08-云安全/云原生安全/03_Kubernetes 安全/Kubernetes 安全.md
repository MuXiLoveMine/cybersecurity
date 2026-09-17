# Kubernetes 安全

### 3.1 K8s 安全架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                       集群安全（Cluster Security）               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  API Server   │  │   etcd 安全   │  │   控制平面加固        │  │
│  │  认证/授权    │  │   加密存储     │  │   网络隔离           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       工作负载安全（Workload Security）          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   RBAC 权限   │  │  Pod 安全上下文│  │   准入控制           │  │
│  │  ServiceAccount│  │  安全策略     │  │   资源限制           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       网络安全（Network Security）               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  网络策略      │  │  服务网格     │  │   入口控制器安全      │  │
│  │  NetworkPolicy│  │  Istio/Linkerd│  │   Ingress Security   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       数据安全（Data Security）                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Secrets     │  │   加密存储    │  │   密钥管理            │  │
│  │   管理        │  │   etcd 加密   │  │   KMS 集成           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 RBAC（基于角色的访问控制）

#### 3.2.1 RBAC 核心概念

| 资源 | 说明 |
|------|------|
| Role | 命名空间内的角色，定义权限规则 |
| ClusterRole | 集群级别的角色 |
| RoleBinding | 将 Role 绑定到用户/组/ServiceAccount |
| ClusterRoleBinding | 将 ClusterRole 绑定到用户/组/ServiceAccount |
| ServiceAccount | Pod 使用的身份 |

#### 3.2.2 RBAC 策略示例

**示例 1：命名空间只读权限（Role）**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]  # "" 表示核心 API 组
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**示例 2：集群管理员（ClusterRole，危险）**
```yaml
# 警告：这是集群完全管理员权限，应谨慎授予
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-admin-binding
subjects:
- kind: User
  name: admin-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

**示例 3：ServiceAccount 权限**
```yaml
# 创建 ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: production
---
# 创建 Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: configmap-reader
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list"]
---
# 绑定 Role 到 ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-read-configmap
  namespace: production
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: production
roleRef:
  kind: Role
  name: configmap-reader
  apiGroup: rbac.authorization.k8s.io
```

#### 3.2.3 RBAC 安全最佳实践

| 最佳实践 | 说明 |
|----------|------|
| 最小权限原则 | 只授予必要的最小权限 |
| 避免使用 cluster-admin | 集群管理员权限应极少授予 |
| 使用命名空间隔离 | 不同环境/团队使用不同命名空间 |
| 定期审计 RBAC | 检查是否有权限过大的情况 |
| 谨慎使用通配符 | 避免在 resources 和 verbs 中使用 "*" |
| ServiceAccount 最小化 | 每个应用使用独立的 SA，权限最小化 |
| 禁用默认 SA 自动挂载 | 不需要时关闭 automountServiceAccountToken |

#### 3.2.4 危险的 RBAC 配置

**危险配置 1：通配符权限**
```yaml
# 危险：拥有所有资源的所有操作权限
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**危险配置 2：可以创建 Pod 的权限 + 特权容器 = 逃逸**
```yaml
# 如果可以创建特权 Pod，基本等于获得节点 root 权限
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "update"]
```

**危险配置 3：可以修改 ClusterRoleBinding**
```yaml
# 可以修改 ClusterRoleBinding = 可以提升自己的权限
rules:
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["clusterrolebindings"]
  verbs: ["create", "update", "patch"]
```

### 3.3 Pod 安全上下文（Security Context）

#### 3.3.1 安全上下文配置

Pod 安全上下文定义了 Pod 和容器的安全设置。

**完整的安全配置示例**：
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  # Pod 级别的安全上下文
  securityContext:
    runAsNonRoot: true           # 禁止以 root 用户运行
    runAsUser: 1000              # 指定运行用户 ID
    runAsGroup: 3000             # 指定运行组 ID
    fsGroup: 2000                # 文件系统组 ID
    seccompProfile:
      type: RuntimeDefault       # 使用默认 seccomp 配置
  containers:
  - name: app
    image: my-app:latest
    # 容器级别的安全上下文
    securityContext:
      allowPrivilegeEscalation: false  # 禁止权限提升
      readOnlyRootFilesystem: true     # 只读根文件系统
      capabilities:
        drop:
        - ALL                          # 丢弃所有 capabilities
        add:
        - NET_BIND_SERVICE             # 只添加必要的
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

#### 3.3.2 Pod 安全策略（PSP）与 Pod 安全标准（PSS）

PodSecurityPolicy 已在 Kubernetes 1.25 中被移除，替代方案是 Pod Security Admission（PSA）和 Pod Security Standards（PSS）。

**Pod 安全标准（PSS）三个级别**：

| 级别 | 说明 | 适用场景 |
|------|------|----------|
| Privileged | 无限制，完全开放 | 系统级组件、需要特权的工作负载 |
| Baseline | 基本安全限制，防止常见的提权手段 | 默认策略，大多数应用 |
| Restricted | 严格限制，遵循当前 Pod 加固最佳实践 | 高安全要求环境、不可信代码 |

**启用 Pod 安全准入（PSA）**：
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # 强制实施 restricted 策略
    pod-security.kubernetes.io/enforce: restricted
    # 审计模式（记录但不阻止）
    pod-security.kubernetes.io/audit: restricted
    # 警告模式（给出警告但不阻止）
    pod-security.kubernetes.io/warn: restricted
```

### 3.4 网络策略（Network Policy）

#### 3.4.1 网络策略概述

默认情况下，Kubernetes 中所有 Pod 之间可以互相通信。网络策略用于限制 Pod 之间的网络流量。

**前提条件**：需要使用支持 NetworkPolicy 的网络插件，如 Calico、Cilium 等。

#### 3.4.2 网络策略示例

**示例 1：默认拒绝所有入站流量**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}    # 空选择器匹配所有 Pod
  policyTypes:
  - Ingress
  # 没有 ingress 规则 = 拒绝所有入站
```

**示例 2：允许特定命名空间访问数据库**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-db
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database    # 匹配数据库 Pod
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web     # 只允许 web Pod 访问
    ports:
    - protocol: TCP
      port: 5432       # 只允许 PostgreSQL 端口
```

**示例 3：限制出站流量**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Egress
  egress:
  # 允许 DNS 查询
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  # 允许访问数据库
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

#### 3.4.3 网络策略最佳实践

1. **默认拒绝**：每个命名空间设置默认拒绝所有入站和出站流量
2. **白名单模式**：只显式允许必要的流量
3. **按应用分层**：Web → App → DB 逐层限制
4. **限制出站**：不仅限制入站，也要限制出站（防止横向移动和数据外发）
5. **命名空间隔离**：不同环境（dev/staging/prod）使用不同命名空间并设置网络策略

### 3.5 Secret 管理

#### 3.5.1 Secret 基础

Kubernetes Secret 用于存储敏感信息，如密码、令牌、密钥等。

**Secret 类型**：
- Opaque：通用 Secret，base64 编码
- kubernetes.io/service-account-token：ServiceAccount 令牌
- kubernetes.io/dockerconfigjson：Docker 镜像仓库凭证
- kubernetes.io/tls：TLS 证书

**Secret 使用示例**：
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=      # base64 编码的 "admin"
  password: cGFzc3dvcmQ=  # base64 编码的 "password"
---
# 在 Pod 中使用 Secret（环境变量方式）
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: my-app
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
---
# 在 Pod 中使用 Secret（挂载文件方式）
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: my-app
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

#### 3.5.2 Secret 的安全问题

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| base64 不是加密 | 只是编码，可直接解码 | 启用 etcd 加密 |
| etcd 中明文存储 | 默认情况下 Secret 在 etcd 中是明文 | 启用 etcd 静态加密 |
| 访问权限控制 | 能 list secret 的用户能看到所有 secret | RBAC 严格控制 Secret 访问 |
| 镜像中泄露 | 应用日志可能打印 Secret | 日志脱敏处理 |
| YAML 文件泄露 | Secret YAML 提交到代码仓库 | 使用 SealedSecret 或外部密钥管理 |

#### 3.5.3 Secret 安全最佳实践

1. **启用 etcd 加密**：
```yaml
# 在 kube-apiserver 配置中启用加密
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
    - secrets
    providers:
    - aescbc:
        keys:
        - name: key1
          secret: <base64-encoded-32-byte-key>
    - identity: {}
```

2. **使用外部密钥管理服务**：
   - HashiCorp Vault
   - AWS Secrets Manager
   - 阿里云密钥管理服务（KMS）
   - 通过 External Secrets Operator 同步到 K8s

3. **RBAC 严格控制 Secret 访问**

4. **不要在代码或配置文件中硬编码 Secret**

5. **定期轮换 Secret**

### 3.6 Kubernetes 安全工具

#### 3.6.1 静态扫描工具

| 工具 | 用途 | 说明 |
|------|------|------|
| kube-bench | CIS Benchmark 检查 | 检查 K8s 集群是否符合 CIS 基准 |
| kube-hunter | 渗透测试 | 主动扫描 K8s 集群漏洞 |
| Trivy | 多类型扫描 | 镜像、配置、K8s YAML 扫描 |
| Checkov | IaC 扫描 | Terraform、CloudFormation、K8s YAML |
| KubeLinter | YAML 静态检查 | 检查 K8s YAML 最佳实践 |
| kubescape | 安全框架 | 综合 K8s 安全扫描 |

**kube-bench 使用示例**：
```bash
# 运行 kube-bench 检查集群安全
docker run --rm -v `pwd`:/output:rw \
    -v /etc:/etc:ro \
    -v /var/lib/etcd:/var/lib/etcd:ro \
    aquasec/kube-bench:latest run --json > kube-bench-report.json
```

**kube-hunter 使用示例**：
```bash
# 被动扫描（远程，不登录集群）
kube-hunter --remote <master-ip>

# 主动扫描（更全面）
kube-hunter --remote <master-ip> --active

# 列出所有可测试的漏洞
kube-hunter --list
```

#### 3.6.2 运行时安全工具

| 工具 | 用途 | 说明 |
|------|------|------|
| Falco | 运行时威胁检测 | 基于 eBPF 的内核级监控，检测异常行为 |
| Calico | 网络安全与网络策略 | 网络策略、流量可视化 |
| Cilium | eBPF 网络安全 | 基于 eBPF 的高性能网络和安全 |
| Aqua/Twistlock/Sysdig | 容器安全平台 | 商业化全栈容器安全 |

**Falco 规则示例**：
```yaml
# 检测在容器内执行 shell
- rule: Terminal shell in container
  desc: A shell was used as the entrypoint/exec point into a container
  condition: >
    spawned_process and container
    and shell_procs and proc.tty != 0
    and container_entrypoint
  output: >
    A shell was spawned in a container with an attached terminal
    (user=%user.name container_id=%container.id container_name=%container.name
    shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline
    terminal=%proc.tty container_started_ts=%container.start_ts)
  priority: WARNING
```

---

---

## 📋 内容审核与补充建议

> 针对「Kubernetes 安全」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
