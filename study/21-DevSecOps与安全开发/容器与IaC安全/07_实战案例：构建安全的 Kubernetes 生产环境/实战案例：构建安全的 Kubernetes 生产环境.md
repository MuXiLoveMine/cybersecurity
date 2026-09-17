# 实战案例：构建安全的 Kubernetes 生产环境

### 7.1 整体安全架构

```
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes 生产环境安全架构                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  集群安全                                            │   │
│  │  ├─ API Server: TLS + RBAC + OIDC 认证              │   │
│  │  ├─ etcd: 加密存储 + TLS 通信                        │   │
│  │  ├─ 准入控制: OPA Gatekeeper                         │   │
│  │  └─ 审计日志: 启用全量审计                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  工作负载安全                                        │   │
│  │  ├─ Pod Security: Restricted 级别                    │   │
│  │  ├─ 镜像安全: 扫描 + 签名验证                        │   │
│  │  ├─ 运行时安全: Seccomp + AppArmor                   │   │
│  │  └─ 资源限制: CPU/Memory limits                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  网络安全                                            │   │
│  │  ├─ Network Policy: 默认拒绝 + 最小允许             │   │
│  │  ├─ Service Mesh: mTLS (Istio/Linkerd)              │   │
│  │  ├─ Ingress: TLS 终止 + WAF                         │   │
│  │  └─ DNS 策略                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  密钥管理                                            │   │
│  │  ├─ HashiCorp Vault: 动态密钥                        │   │
│  │  ├─ Sealed Secrets: GitOps 安全                      │   │
│  │  ├─ External Secrets: 外部密钥同步                   │   │
│  │  └─ CSI Secrets: 卷挂载密钥                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  可观测性                                            │   │
│  │  ├─ Falco: 运行时安全监控                            │   │
│  │  ├─ kube-bench: 安全基准检查                         │   │
│  │  ├─ Prometheus: 指标监控                             │   │
│  │  └─ ELK: 日志聚合                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 安全的 Deployment 配置

```yaml
# production-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
  namespace: production
  labels:
    app: secure-app
    version: "1.0.0"
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: secure-app
  template:
    metadata:
      labels:
        app: secure-app
        version: "1.0.0"
      annotations:
        # Vault Agent 注入
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "secure-app"
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      # ServiceAccount 最小权限
      serviceAccountName: secure-app-sa
      automountServiceAccountToken: false  # 禁止自动挂载 ServiceAccount Token

      # Pod 级别安全上下文
      securityContext:
        runAsNonRoot: true          # 禁止 root 运行
        runAsUser: 1000            # 指定非 root UID
        runAsGroup: 1000           # 指定非 root GID
        fsGroup: 1000              # 文件系统组
        seccompProfile:
          type: RuntimeDefault      # 默认 seccomp 配置

      # 优雅终止
      terminationGracePeriodSeconds: 30

      containers:
        - name: app
          image: registry.example.com/secure-app:1.0.0
          imagePullPolicy: IfNotPresent

          # 容器级安全上下文
          securityContext:
            allowPrivilegeEscalation: false  # 禁止提权
            privileged: false                 # 禁止特权模式
            readOnlyRootFilesystem: true      # 只读根文件系统
            runAsNonRoot: true
            runAsUser: 1000
            runAsGroup: 1000
            capabilities:
              drop:
                - ALL                        # 丢弃所有 capabilities
              add:
                - NET_BIND_SERVICE            # 仅保留必要能力

          # 资源限制（防止资源耗尽）
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
              ephemeral-storage: "1Gi"
            requests:
              cpu: "250m"
              memory: "256Mi"
              ephemeral-storage: "500Mi"

          # 探针配置
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3

          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3

          # 挂载可写目录
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /app/cache
            - name: logs
              mountPath: /app/logs
            - name: vault-secrets
              mountPath: /vault/secrets
              readOnly: true

          # 环境变量（非敏感）
          env:
            - name: APP_ENV
              value: "production"
            - name: LOG_LEVEL
              value: "info"

      volumes:
        - name: tmp
          emptyDir:
            medium: Memory  # 使用 tmpfs
        - name: cache
          emptyDir:
            sizeLimit: 200Mi
        - name: logs
          emptyDir: {}
        - name: vault-secrets
          emptyDir: {}

      # 反亲和性（提高可用性）
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - secure-app
                topologyKey: kubernetes.io/hostname

      # 容忍污点（可选）
      tolerations: []

      # 拓扑分布约束
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: secure-app
```

### 7.3 Network Policy 配置

```yaml
# network-policies.yaml
---
# 默认拒绝所有入站和出站
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress

---
# 允许 frontend -> backend
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080

---
# 允许 backend -> database
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
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53

---
# 允许 HTTPS 出站（外部 API 调用）
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-https-egress
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8    # 禁止访问内网
              - 172.16.0.0/12
              - 192.168.0.0/16
      ports:
        - protocol: TCP
          port: 443
```

### 7.4 安全监控部署

**Falco 运行时安全监控**
```yaml
# falco-values.yaml - Helm 配置
daemonset:
  enabled: true
  # 安装为 DaemonSet
  # 监控所有节点的容器运行时行为

# Falco 自定义规则
# /etc/falco/falco_rules.local.yaml
- macro: allowed_containers
  condition: container.name in (allowed_container_names)

- rule: Unauthorized Container Started
  desc: 检测未授权的容器启动
  condition: container.started and not allowed_containers
  output: >
    未授权容器启动 (user=%user.name
    container_id=%container.id
    container_name=%container.name
    image=%container.image.repository)
  priority: CRITICAL
  tags: [container, security]

- rule: Shell in Container
  desc: 检测容器内执行 shell
  condition: >
    spawned_process and container
    and proc.name in (bash, sh, zsh, ash)
    and not container.name in (allowed_shell_containers)
  output: >
    容器内执行 Shell (user=%user.name
    container=%container.name
    shell=%proc.name)
  priority: WARNING
  tags: [container, shell, security]

- rule: Read Sensitive File in Container
  desc: 检测容器内读取敏感文件
  condition: >
    open_read and container
    and fd.name in (/etc/shadow, /etc/passwd, /proc/*/mem)
  output: >
    容器读取敏感文件 (user=%user.name
    container=%container.name
    file=%fd.name)
  priority: CRITICAL
  tags: [container, filesystem, security]

- rule: Network Connection Outside Allowed Ports
  desc: 检测容器异常网络连接
  condition: >
    outbound and container
    and not fd.sport in (80, 443, 8080, 5432)
  output: >
    容器异常网络连接 (container=%container.name
    sport=%fd.sport dport=%fd.dport)
  priority: WARNING
  tags: [container, network, security]
```

**kube-bench 安全基准检查**
```bash
# 运行 CIS Kubernetes Benchmark 检查
# 主节点检查
kubectl run kube-bench-master --rm -it --restart=Never \
    --image=aquasec/kube-bench:latest \
    -- kube-bench --benchmark cis-1.8 \
    --check master

# 工作节点检查
kubectl run kube-bench-worker --rm -it --restart=Never \
    --override=json='{"spec":{"nodeSelector":{"kubernetes.io/role":"worker"}}}' \
    --image=aquasec/kube-bench:latest \
    -- kube-bench --benchmark cis-1.8 \
    --check node

# 输出 JSON 报告
kubectl run kube-bench --rm -it --restart=Never \
    --image=aquasec/kube-bench:latest \
    -- kube-bench --json --outputfile /tmp/kube-bench-report.json
```

### 7.5 CI/CD 安全流水线

```yaml
# GitLab CI 容器与 IaC 安全流水线
stages:
  - validate
  - security-scan
  - build
  - deploy

# IaC 安全扫描
terraform-security:
  stage: security-scan
  image: bridgecrew/checkov:latest
  script:
    - checkov -d terraform/ -o json -o checkov-report.json
    - tfsec terraform/ --format json --out tfsec-report.json
  artifacts:
    reports:
      json:
        - checkov-report.json
        - tfsec-report.json

# Dockerfile 安全检查
dockerfile-lint:
  stage: validate
  image: hadolint/hadolint:latest
  script:
    - hadolint Dockerfile --format json > dockerfile-lint.json
  artifacts:
    reports:
      json: dockerfile-lint.json

# 构建并扫描镜像
build-and-scan:
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    # 镜像安全扫描
    - docker run --rm aquasec/trivy image
        --severity HIGH,CRITICAL
        --exit-code 1
        --format json
        --output trivy-image-report.json
        $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    # 镜像签名
    - cosign sign --key $COSIGN_KEY $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    # 推送镜像
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  artifacts:
    reports:
      json: trivy-image-report.json

# Kubernetes 清单安全检查
k8s-security:
  stage: security-scan
  image: bridgecrew/checkov:latest
  script:
    - checkov -d k8s/ --framework kubernetes -o json -o k8s-checkov-report.json
    # kube-score 检查
    - kube-score score k8s/ --output json > kube-score-report.json
  artifacts:
    reports:
      json:
        - k8s-checkov-report.json
        - kube-score-report.json
```

---

---

## 📋 内容审核与补充建议

> 针对「实战案例：构建安全的 Kubernetes 生产环境」部分的内容审核结果：

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
