# Kubernetes 安全

### 5.1 Kubernetes 攻击面

```text
+--------------------------------------------+
|            K8s 攻击面                       |
+--------------------------------------------+
| 1. API Server 暴露与未授权访问              |
| 2. kubelet API 滥用                        |
| 3. etcd 未加密访问                          |
| 4. RBAC 权限过度                            |
| 5. 容器逃逸（特权 / 挂载宿主）              |
| 6. Pod 间横向移动                          |
| 7. 服务账号 Token 滥用                      |
| 8. Dashboard / Ingress 暴露                |
+--------------------------------------------+
```

### 5.2 RBAC 最小权限

```yaml
# 服务账号仅可读取指定命名空间 Pod
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: prod
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: prod
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: prod
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 5.3 Pod 安全标准（PSS）

Kubernetes 1.25+ 用 Pod Security Admission 替代 PodSecurityPolicy：

| 级别 | 说明 |
| --- | --- |
| privileged | 最宽松，不推荐 |
| baseline | 基础加固，拒绝最危险配置 |
| restricted | 最严格，遵循最佳实践 |

```yaml
# 命名空间强制 restricted 策略
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 5.4 网络策略（NetworkPolicy）

```yaml
# 默认拒绝所有入站，仅允许指定应用访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-web
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - protocol: TCP
      port: 5432
```

### 5.5 API Server 加固

- 禁用匿名访问 `--anonymous-auth=false`
- 启用 RBAC `--authorization-mode=Node,RBAC`
- 启用审计日志 `--audit-log-path`
- 限制 kubelet 只读端口访问
- etcd 启用静态加密 `--encryption-provider-config`

```yaml
# etcd 静态加密配置
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64 编码密钥>
  - identity: {}
```

---

---

