# Kubernetes 安全

### 4.1 RBAC 配置

**RBAC 最小权限原则**
```yaml
# 授予最小权限的 Role 示例
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: app-deployer
rules:
  # 仅允许部署相关操作
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
  
  # 仅允许 Pod 查看（不允许创建/删除）
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  
  # 允许 Service 操作
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]

  # 禁止操作 ConfigMap 和 Secret
  # 不添加 = 默认拒绝

---
# 绑定 Role 到 ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-deployer-binding
  namespace: production
subjects:
  - kind: ServiceAccount
    name: app-deployer-sa
    namespace: production
roleRef:
  kind: Role
  name: app-deployer
  apiGroup: rbac.authorization.k8s.io
```

**避免过度授权**
```yaml
# 危险：cluster-admin 权限过度授予
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: dangerous-binding
subjects:
  - kind: User
    name: developer
roleRef:
  kind: ClusterRole
  name: cluster-admin  # 危险！授予了整个集群的管理权限
  apiGroup: rbac.authorization.k8s.io

# 安全：使用 namespace 级别的 Role
# 只授予特定 namespace 的特定操作权限
```

### 4.2 Pod Security Standards

Kubernetes Pod Security Standards 替代了已废弃的 PodSecurityPolicy。

**三个安全级别**
| 级别 | 说明 | 适用场景 |
|------|------|---------|
| Privileged | 不限制 | 系统组件、特殊需求 |
| Baseline | 基础限制 | 一般应用 |
| Restricted | 严格限制 | 生产环境应用 |

**Pod Security Admission 配置**
```yaml
# namespace 标签配置安全级别
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    # Restricted 级别：执行模式
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    # Baseline 级别：审计模式
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: latest
    # Baseline 级别：警告模式
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: latest
---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: latest
---
apiVersion: v1
kind: Namespace
metadata:
  name: system
  labels:
    # 系统命名空间允许特权
    pod-security.kubernetes.io/enforce: privileged
    pod-security.kubernetes.io/enforce-version: latest
```

**Restricted 级别强制要求**
- 禁止特权容器（privileged: true）
- 禁止提权（allowPrivilegeEscalation: true）
- 必须 runAsNonRoot: true
- 必须 drop ALL capabilities
- 必须设置 seccompProfile
- 必须 readOnlyRootFilesystem（建议）

### 4.3 Network Policy

```yaml
# 默认拒绝所有入站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}  # 选择所有 Pod
  policyTypes:
    - Ingress

---
# 允许前端访问后端
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend  # 适用于 backend Pod
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend  # 允许 frontend Pod 访问
      ports:
        - protocol: TCP
          port: 8080  # 仅允许 8080 端口

---
# 允许数据库仅被后端访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-database
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: backend
      ports:
        - protocol: TCP
          port: 5432

---
# 默认拒绝所有出站流量
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress

---
# 允许 DNS 出站
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### 4.4 准入控制（OPA Gatekeeper）

**OPA Gatekeeper 安装**
```bash
# 安装 Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml
```

**Gatekeeper 策略：禁止特权容器**
```yaml
# ConstraintTemplate 定义策略逻辑
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowprivileged
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowPrivileged
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdisallowprivileged

        # 违规：容器配置了 privileged: true
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged == true
          msg := sprintf("容器 %v 被配置为特权模式，禁止部署", [container.name])
        }

        # 同时检查 initContainers
        violation[{"msg": msg}] {
          container := input.review.object.spec.initContainers[_]
          container.securityContext.privileged == true
          msg := sprintf("初始化容器 %v 被配置为特权模式，禁止部署", [container.name])
        }

---
# Constraint 应用策略
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sDisallowPrivileged
metadata:
  name: no-privileged-containers
spec:
  enforcementAction: deny  # 拒绝违规 Pod
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    excludedNamespaces:
      - kube-system
```

**Gatekeeper 策略：禁止 latest 标签**
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8sdisallowlatesttag
spec:
  crd:
    spec:
      names:
        kind: K8sDisallowLatestTag
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8sdisallowlatesttag

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          endswith(container.image, ":latest")
          msg := sprintf("容器 %v 使用了 latest 标签，必须指定版本", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not contains(container.image, ":")
          msg := sprintf("容器 %v 未指定镜像版本标签", [container.name])
        }
```

**Gatekeeper 策略：要求资源限制**
```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredresources
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredResources
      validation:
        openAPIV3Schema:
          type: object
          properties:
            limits:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredresources

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.memory
          msg := sprintf("容器 %v 未设置内存限制", [container.name])
        }

        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.resources.limits.cpu
          msg := sprintf("容器 %v 未设置 CPU 限制", [container.name])
        }
```

---

---

## 📋 内容审核与补充建议

> 针对「Kubernetes 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
