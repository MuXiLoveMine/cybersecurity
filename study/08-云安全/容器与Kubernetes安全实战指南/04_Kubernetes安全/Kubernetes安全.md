# Kubernetes安全

### 4.1 K8s架构安全概览

```
┌─────────────── 控制面 ───────────────┐
│  API Server (认证/授权/准入)          │
│  etcd (集群状态存储, 需TLS+加密)      │
│  Controller Manager / Scheduler       │
└──────────────────────────────────────┘
          │
┌─────────────── 工作节点 ─────────────┐
│  kubelet (与API Server通信)          │
│  kube-proxy (网络转发)               │
│  container runtime (containerd)     │
└──────────────────────────────────────┘
```

**控制面安全要点**：API Server 是唯一入口，所有请求经过 认证→授权(RBAC)→准入控制 三层检查。etcd 存储所有集群状态，包含 Secret，必须加密静态数据。

### 4.2 RBAC（基于角色的访问控制）

#### 角色绑定关系

```
User/ServiceAccount ──RoleBinding──▶ Role (namespace范围)
User/ServiceAccount ──ClusterRoleBinding──▶ ClusterRole (集群范围)
```

#### 最小权限配置示例

```yaml
# 仅授予读取指定 namespace Pod 的权限
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]  # 不给 create/delete
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: production
  name: read-pods
subjects:
- kind: ServiceAccount
  name: my-sa
  namespace: production
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**RBAC审计检查**：

```bash
# 查找 cluster-admin 绑定（过度授权检查）
kubectl get clusterrolebinding -o json | jq -r '.items[] | select(.roleRef.name=="cluster-admin") | .metadata.name'

# 检查是否有匿名用户绑定
kubectl get clusterrolebinding -o json | jq -r '.items[] | select(.subjects[]?.name=="system:anonymous") | .metadata.name'
```

### 4.3 网络安全

#### NetworkPolicy网络隔离

```yaml
# 默认拒绝所有入站和出站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  namespace: production
  name: default-deny-all
spec:
  podSelector: {}  # 选中所有Pod
  policyTypes: [Ingress, Egress]
---
# 仅允许前端访问后端，后端仅允许访问数据库
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  namespace: production
  name: backend-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

#### Service Mesh安全（Istio mTLS）

Istio 自动在服务间启用双向 TLS，无需修改应用代码：

```yaml
# Istio PeerAuthentication：全命名空间严格 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  namespace: production
  name: default
spec:
  mtls:
    mode: STRICT  # 强制双向TLS
```

### 4.4 Pod安全

#### Pod Security Standards

| 级别 | 限制 | 适用场景 |
|------|------|---------|
| Privileged | 无限制 | 系统组件，不推荐业务使用 |
| Baseline | 禁止特权模式、宿主PID/网络 | 一般业务 |
| Restricted | 强制runAsNonRoot、drop ALL caps、seccomp | 安全敏感业务 |

```yaml
# 命名空间级别启用 Restricted Pod Security
apiVersion: v1
kind: Namespace
metadata:
  name: restricted-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### SecurityContext配置

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp:v1
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
      runAsNonRoot: true
      runAsUser: 1000
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
```

### 4.5 etcd安全

```bash
# 1. etcd 加密静态数据（K8s 1.13+）
# 创建 EncryptionConfiguration
cat > /etc/kubernetes/enc/encryption-config.yaml <<'EOF'
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  - configmaps
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}
EOF

# 2. 修改 API Server 参数
# --encryption-provider-config=/etc/kubernetes/enc/encryption-config.yaml

# 3. 重新加密所有 Secret
kubectl get secrets --all-namespaces -o json | \
  kubectl replace -f -
```

**etcd备份与恢复安全**：

```bash
# 备份 etcd（需TLS证书）
ETCDCTL_API=3 etcdctl snapshot save backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/etcd/ca.crt \
  --cert=/etc/etcd/peer.crt \
  --key=/etc/etcd/peer.key

# 加密备份文件
gpg --symmetric --cipher-algo AES256 backup.db
```

### 4.6 Secret管理

#### K8s Secret加密

K8s 原生 Secret 默认仅 base64 编码（非加密），需配合上述 etcd 加密使用。更安全的方案是外部 Secret 管理：

```yaml
# External Secrets Operator + Vault
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  namespace: production
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: db-credentials-secret
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/production/db
      property: password
```

### 4.7 准入控制器

#### Kyverno策略示例

```yaml
# 禁止特权容器
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-containers
spec:
  validationFailureAction: Enforce
  rules:
  - name: no-privileged
    match:
      resources:
        kinds: [Pod]
    validate:
      message: "禁止使用特权容器"
      pattern:
        spec:
          containers:
          - "=securityContext":
              "privileged": "false"

---
# 强制镜像签名验证（结合 Cosign）
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-signature
    match:
      resources:
        kinds: [Pod]
    verifyImages:
    - imageReferences:
      - "myregistry.com/*"
      attestors:
      - entries:
        - keys:
            publicKeys: |
              -----BEGIN PUBLIC KEY-----
              <cosign-public-key>
              -----END PUBLIC KEY-----
```

#### OPA Gatekeeper策略示例

```yaml
# 禁止 latest 标签镜像
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: disallow-latest-tag
spec:
  crd:
    spec:
      names:
        kind: DisallowLatestTag
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package disallowlatesttag
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        endswith(container.image, ":latest")
        msg := sprintf("禁止使用 latest 标签: %v", [container.image])
      }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: DisallowLatestTag
metadata:
  name: no-latest
spec:
  enforcementAction: deny
  match:
    kinds:
    - apiGroups: [""]
      kinds: [Pod]
```

### 4.8 K8s常见攻击面

| 攻击面 | 风险 | 检测与防御 |
|--------|------|-----------|
| 暴露的API Server | 匿名访问/未授权 | `kubectl get --raw /` 验证；关闭匿名认证 |
| 暴露的kubelet API | 命令执行 | 检查 10250 端口；启用认证 |
| 暴露的etcd | 集群接管 | 检查 2379 端口；启用TLS+认证 |
| 暴露的Dashboard | 未授权操作 | 检查 30000 端口；禁用 skip-login |
| CVE-2018-1002105 | API Server提权 | 升级到 1.10.11/1.11.5 以上 |

```bash
# 检测匿名访问
kubectl -s https://k8s-api:6443 get --raw / --insecure
# 检测 kubelet 匿名访问
curl -k https://node:10250/pods
# 检测 etcd 未授权
curl -k https://node:2379/v2/keys/?recursive=true
```

---

---

