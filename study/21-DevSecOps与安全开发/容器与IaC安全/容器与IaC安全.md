# 容器与 IaC 安全

> 容器化和基础设施即代码（IaC）是云原生时代的基础，但其安全风险与传统基础设施截然不同。本文档系统讲解容器安全、Kubernetes 安全和 IaC 安全的防护体系。

---

## 一、容器安全概述

### 1.1 容器与虚拟机安全差异

| 特性 | 虚拟机 | 容器 |
|------|-------|------|
| 隔离机制 | 硬件级隔离（Hypervisor） | 进程级隔离（Namespace + Cgroup） |
| 内核共享 | 独立内核 | 共享宿主机内核 |
| 攻击面 | 较小 | 较大（共享内核） |
| 逃逸难度 | 高 | 相对较低 |
| 安全边界 | Hypervisor | 容器运行时 |
| 资源限制 | 硬件隔离 | Cgroup 限制 |
| 网络隔离 | 虚拟网络 | 网络命名空间 |

**容器安全的核心挑战**
- 共享内核：容器共享宿主机内核，内核漏洞可导致逃逸
- 权限提升：容器可能以 root 运行，具有危险 capabilities
- 镜像供应链：第三方镜像可能包含恶意代码或漏洞
- 网络隔离弱：默认情况下容器间网络可互通
- 密钥管理：容器环境中的密钥管理更复杂

### 1.2 容器攻击面分析

```
┌─────────────────────────────────────────────────────────┐
│                   容器攻击面分析                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 容器镜像层                                          │
│     ├─ 基础镜像漏洞（OS 包、基础软件）                   │
│     ├─ 应用依赖漏洞（npm、pip 包）                      │
│     ├─ 恶意镜像（镜像投毒）                             │
│     ├─ 敏感信息泄露（镜像中的硬编码密钥）                 │
│     └─ 镜像篡改（未签名验证）                           │
│                                                         │
│  2. 容器运行时层                                        │
│     ├─ 容器逃逸（privileged 模式）                      │
│     ├─ Capabilities 滥用                               │
│     ├─ 文件系统挂载（敏感目录挂载）                      │
│     ├─ 容器间攻击（网络可达性）                         │
│     └─ 资源耗尽（DoS）                                 │
│                                                         │
│  3. 编排平台层（Kubernetes）                            │
│     ├─ RBAC 配置错误                                   │
│     ├─ API Server 暴露                                 │
│     ├─ etcd 未授权访问                                  │
│     ├─ Dashboard 暴露                                  │
│     ├─ Pod 间网络互通                                  │
│     └─ 准入控制缺失                                    │
│                                                         │
│  4. 供应链层                                            │
│     ├─ CI/CD 流水线安全                                │
│     ├─ 制品仓库安全                                    │
│     ├─ IaC 配置错误                                    │
│     └─ 密钥管理不当                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 二、镜像安全

### 2.1 基础镜像选择

**基础镜像选择原则**
1. 使用官方镜像而非第三方镜像
2. 选择精简版本（slim/alpine）减少攻击面
3. 固定版本标签而非使用 latest
4. 定期更新基础镜像
5. 从可信仓库拉取镜像

**基础镜像对比**
```dockerfile
# 不安全：使用完整镜像 + latest 标签
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 python3-pip
COPY . /app
CMD ["python3", "/app/main.py"]
# 问题：镜像大(约100MB+)、包含大量不必要软件、latest不可追溯

# 安全：使用官方精简镜像 + 固定版本
FROM python:3.11.7-slim-bookworm
# 精简镜像仅约45MB，减少了攻击面

# 更安全：使用 distroless 镜像
FROM gcr.io/distroless/python3-debian12:nonroot
COPY app /app
WORKDIR /app
CMD ["main.py"]
# distroless 镜像不含 shell、包管理器，攻击面最小
```

### 2.2 镜像扫描

#### 2.2.1 Trivy 镜像扫描

```bash
# 基础镜像扫描
trivy image python:3.11-slim

# 扫描自定义镜像
trivy image myapp:1.0.0

# 设置严重级别过滤
trivy image --severity HIGH,CRITICAL myapp:1.0.0

# 输出 JSON 格式
trivy image --format json -o trivy-report.json myapp:1.0.0

# 输出 SARIF 格式（GitHub Code Scanning）
trivy image --format sarif -o trivy-results.sarif myapp:1.0.0

# 阻断构建（有 Critical 漏洞时退出码 1）
trivy image --exit-code 1 --severity CRITICAL myapp:1.0.0

# 忽略不可修复的漏洞
trivy image --ignore-unfixed myapp:1.0.0

# 使用忽略文件
trivy image --ignorefile .trivyignore myapp:1.0.0

# 扫描远程仓库镜像
trivy image registry.example.com/myapp:1.0.0

# 生成 SBOM
trivy image --format cyclonedx --output sbom.json myapp:1.0.0
```

#### 2.2.2 Grype 镜像扫描

```bash
# 安装
# macOS: brew install grype
# Linux: curl -sSf https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh

# 扫描镜像
grype myapp:1.0.0

# 设置严重级别
grype myapp:1.0.0 --fail-on high

# 输出 JSON
grype myapp:1.0.0 -o json > grype-report.json

# 输出 SARIF
grype myapp:1.0.0 -o sarif > grype-results.sarif

# 扫描 SBOM 文件
grype sbom:./sbom.json

# 只显示可修复的漏洞
grype myapp:1.0.0 --only-fixed
```

#### 2.2.3 Docker Scout

```bash
# 扫描镜像
docker scout cve myapp:1.0.0

# 比较两个镜像
docker scout compare myapp:1.0.0 myapp:2.0.0

# 查看镜像推荐
docker scout recommendations myapp:1.0.0

# 输出 JSON
docker scout cve --format json myapp:1.0.0
```

### 2.3 镜像签名（Cosign）

#### 2.3.1 Cosign 签名与验证

```bash
# 安装 Cosign
# macOS: brew install cosign
# Linux: go install github.com/sigstore/cosign/cmd/cosign@latest

# 生成密钥对
cosign generate-key-pair
# 输出: cosign.key（私钥）, cosign.pub（公钥）

# 使用私钥签名镜像
COSIGN_PASSWORD=your-password cosign sign \
    --key cosign.key \
    registry.example.com/myapp:1.0.0

# 使用公钥验证签名
cosign verify \
    --key cosign.pub \
    registry.example.com/myapp:1.0.0

# 使用 keyless 签名（基于 OIDC）
cosign sign registry.example.com/myapp:1.0.0
# 自动使用 GitHub OIDC 进行认证

# 在 CI/CD 中验证签名
cosign verify \
    --key cosign.pub \
    registry.example.com/myapp:1.0.0 || exit 1
```

#### 2.3.2 Cosign 在 CI/CD 中的使用

```yaml
# GitHub Actions 签名流程
name: Build and Sign Image
on: [push]

jobs:
  build-sign:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # OIDC 权限

    steps:
      - uses: actions/checkout@v4

      - name: 构建镜像
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .

      - name: 登录镜像仓库
        run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin

      - name: 推送镜像
        run: docker push ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: 安装 Cosign
        uses: sigstore/cosign-installer@v3

      - name: Keyless 签名
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: 验证签名
        run: |
          cosign verify \
            ghcr.io/${{ github.repository }}:${{ github.sha }} \
            --certificate-identity https://github.com/${{ github.repository }}/.github/workflows/build-and-sign.yml@refs/heads/${{ github.ref_name }} \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

---

## 三、容器运行时安全

### 3.1 Seccomp 配置

Seccomp（Secure Computing Mode）限制容器可用的系统调用。

**默认 Seccomp 配置**
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "defaultErrnoRet": 1,
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "names": [
        "accept", "accept4", "access", "bind", "brk",
        "chmod", "chown", "clone", "close", "connect",
        "dup", "dup2", "exit", "exit_group", "fcntl",
        "fork", "getpid", "getuid", "listen", "mmap",
        "mprotect", "munmap", "open", "openat", "read",
        "write", "writev", "socket", "setsockopt"
      ],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": [
        "reboot",
        "mount",
        "umount2",
        "kexec_load",
        "init_module",
        "finit_module",
        "delete_module",
        "iopl",
        "ioperm",
        "kexec_file_load",
        "open_by_handle_at",
        "ptrace",
        "setns",
        "unshare"
      ],
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}
```

**Kubernetes 中使用 Seccomp**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: seccomp-demo
  annotations:
    # 使用默认 seccomp 配置（推荐）
    seccomp.security.alpha.kubernetes.io/pod: "RuntimeDefault"
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault  # 使用容器运行时默认配置
  containers:
  - name: app
    image: myapp:1.0.0
    securityContext:
      seccompProfile:
        type: Localhost  # 使用本地自定义配置
        localhostProfile: profiles/custom-seccomp.json
```

### 3.2 AppArmor 配置

AppArmor 通过路径强制访问控制限制容器权限。

**AppArmor 配置示例**
```
#include <tunables/global>

profile docker-app flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  network inet,
  network inet6,

  # 允许访问应用目录
  /app/** r,
  /app/** rw,
  /tmp/** rw,
  /app/logs/** rw,

  # 允许读取系统库
  /lib/** mr,
  /usr/lib/** mr,
  /lib64/** mr,

  # 禁止访问敏感路径
  deny /etc/shadow r,
  deny /etc/passwd w,
  deny /proc/*/mem r,
  deny /proc/sys/** rw,
  deny /sys/** rw,
  deny /var/run/docker.sock rw,

  # 允许信号
  signal,
  signal send,
  signal receive,

  # 限制能力
  deny capability sys_admin,
  deny capability sys_ptrace,
  deny capability sys_module,
  deny capability net_admin,
  deny capability net_raw,
}
```

**在 Kubernetes 中使用 AppArmor**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: apparmor-demo
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: localhost/docker-app
spec:
  containers:
  - name: app
    image: myapp:1.0.0
```

### 3.3 Capabilities 最小化

**Linux Capabilities 默认集与危险集**

| Capability | 说明 | 风险 |
|-----------|------|------|
| CAP_SYS_ADMIN | 系统管理（最危险） | 容器逃逸 |
| CAP_NET_ADMIN | 网络配置 | 网络攻击 |
| CAP_SYS_PTRACE | 进程跟踪 | 进程注入 |
| CAP_SYS_MODULE | 加载内核模块 | 内核攻击 |
| CAP_DAC_OVERRIDE | 绕过文件权限 | 任意文件访问 |
| CAP_SETUID | 设置用户ID | 权限提升 |
| CAP_NET_RAW | 原始网络访问 | 网络攻击 |
| CAP_CHOWN | 修改文件属主 | 权限提升 |
| CAP_KILL | 杀死进程 | DoS |

**安全配置：丢弃所有 Capabilities**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: minimal-capabilities
spec:
  containers:
  - name: app
    image: myapp:1.0.0
    securityContext:
      capabilities:
        drop:
          - ALL          # 丢弃所有 capabilities
        add:
          - NET_BIND_SERVICE  # 仅保留绑定 80/443 端口的能力
```

### 3.4 只读根文件系统

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readonly-rootfs
spec:
  containers:
  - name: app
    image: myapp:1.0.0
    securityContext:
      readOnlyRootFilesystem: true   # 只读根文件系统
      runAsNonRoot: true             # 非 root 运行
      runAsUser: 1000
    volumeMounts:
    - name: tmp
      mountPath: /tmp                # 挂载可写目录
    - name: cache
      mountPath: /app/cache          # 应用缓存目录
    - name: logs
      mountPath: /app/logs           # 日志目录
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir:
      sizeLimit: 500Mi
  - name: logs
    emptyDir: {}
```

### 3.5 完整的安全 Dockerfile

```dockerfile
# ==========================================
# 安全 Dockerfile 最佳实践示例
# ==========================================

# 第一阶段：构建阶段
FROM golang:1.21-alpine AS builder

# 安装必要工具
RUN apk add --no-cache git ca-certificates

# 设置工作目录
WORKDIR /build

# 复制依赖文件（利用 Docker 缓存层）
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 编译静态二进制文件
# - CGO_ENABLED=0: 禁用 CGO，生成静态链接
# - -ldflags='-s -w': 去除调试信息，减小镜像
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags='-s -w -extldflags "-static"' \
    -o /app/server \
    ./cmd/server

# 第二阶段：运行阶段
FROM scratch

# 添加 CA 证书（支持 HTTPS 请求）
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# 复制编译好的二进制文件
COPY --from=builder /app/server /server

# 创建非 root 用户（scratch 镜像需要手动指定 UID/GID）
USER 65534:65534

# 设置安全标签
# 使用只读根文件系统
# 不需要设置 EXPOSE 如果应用不需要网络

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["/server", "-health"]

# 启动命令
ENTRYPOINT ["/server"]
```

---

## 四、Kubernetes 安全

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

## 五、IaC 安全

### 5.1 Terraform 安全

#### 5.1.1 Terraform 常见安全风险

```hcl
# 危险：安全组规则过于开放
resource "aws_security_group" "web" {
  name = "web-sg"
  
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 危险：SSH 对全互联网开放
  }
  
  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 危险：数据库对全互联网开放
  }
}

# 安全：限制来源 IP
resource "aws_security_group" "web_secure" {
  name = "web-sg-secure"
  
  ingress {
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS 可以开放
  }
  
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["10.0.0.0/8"]  # 仅内网访问 SSH
  }
}

# 危险：S3 存储桶公开
resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
  acl = "public-read"  # 危险：公开读
}

# 安全：S3 私有 + 加密
resource "aws_s3_bucket" "data_secure" {
  bucket = "my-data-bucket-secure"
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data_secure.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data_secure.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 危险：IAM 策略权限过大
resource "aws_iam_role_policy" "app" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "*"          # 危险：所有权限
      Resource = "*"         # 危险：所有资源
    }]
  })
}

# 安全：最小权限 IAM
resource "aws_iam_role_policy" "app_secure" {
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::my-data-bucket-secure/*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query"
        ]
        Resource = "arn:aws:dynamodb:*:*:table/my-table"
      }
    ]
  })
}

# 危险：数据库未加密
resource "aws_db_instance" "database" {
  engine = "mysql"
  storage_encrypted = false  # 危险：未加密
}

# 安全：加密数据库 + 网络隔离
resource "aws_db_instance" "database_secure" {
  engine = "mysql"
  storage_encrypted = true                    # 启用存储加密
  kms_key_id = aws_kms_key.db.arn             # 使用 KMS 密钥
  publicly_accessible = false                  # 禁止公网访问
  vpc_security_group_ids = [aws_security_group.db.id]
  backup_retention_period = 7                  # 启用备份
  deletion_protection = true                   # 启用删除保护
}
```

#### 5.1.2 Terraform 安全扫描工具

**tfsec 使用**
```bash
# 安装
# macOS: brew install tfsec
# Linux: go install github.com/aquasecurity/tfsec/cmd/tfsec@latest

# 扫描目录
tfsec terraform/

# 输出 JSON
tfsec terraform/ -f json -o tfsec-report.json

# 输出 SARIF
tfsec terraform/ -f sarif -o tfsec-results.sarif

# 设置退出码级别
tfsec terraform/ --soft-fail=false  # 任何问题都返回非0退出码

# 忽略特定规则
# 在代码中添加注释
# tfsec:ignore:AWS006
resource "aws_security_group" "web" {
  # ...
}

# 使用配置文件
# .tfsec/config.yml
```

**Checkov 使用**
```bash
# 安装
pip install checkov

# 扫描 Terraform 目录
checkov -d terraform/

# 扫描单个文件
checkov -f main.tf

# 输出 JSON
checkov -d terraform/ -o json > checkov-report.json

# 输出 SARIF
checkov -d terraform/ -o sarif > checkov-results.sarif

# 只运行特定检查
checkov -d terraform/ -c CKV_AWS_18,CKV_AWS_19

# 跳过特定检查
checkov -d terraform/ -s CKV_AWS_20

# 使用框架特定的检查
checkov -d cloudformation/ --framework cloudformation
checkov -d k8s/ --framework kubernetes
checkov -d helm/ --framework helm
```

**Checkov 在 CI/CD 中使用**
```yaml
# .github/workflows/terraform-security.yml
name: Terraform Security Scan
on: [push, pull_request]

jobs:
  terraform-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Terraform 格式检查
        run: terraform fmt -check -recursive
      
      - name: Terraform 初始化
        run: terraform init -backend=false
      
      - name: Checkov 安全扫描
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file: checkov-results.sarif
          soft_fail: false
      
      - name: tfsec 安全扫描
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working_directory: terraform/
      
      - name: 上传结果
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: checkov-results.sarif
```

### 5.2 Ansible 安全

**Ansible 安全最佳实践**

```yaml
# 危险：明文存储敏感变量
# group_vars/production.yml
---
db_password: "SuperSecret123!"  # 危险：明文存储
api_key: "abc123xyz"           # 危险：明文存储

# 安全：使用 Ansible Vault 加密
# 创建加密文件
# ansible-vault encrypt group_vars/production/vault.yml
---
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  6230313662646630653530363338653535306362383739333934656361653763...
api_key: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  346537633866353332653735383861616261626338656432356533623162...

# 安全：使用 HashiCorp Vault 获取密钥
---
- name: 获取数据库密码
  hosts: database
  tasks:
    - name: 从 Vault 获取密钥
      hashivault_read:
        url: https://vault.example.com
        authtoken: "{{ vault_token }}"
        path: secret/data/database
        key: password
      register: db_password_result

    - name: 配置数据库
      mysql_user:
        name: app
        password: "{{ db_password_result.value }}"
        priv: '*.*:ALL'
```

**Ansible 安全配置**
```ini
# ansible.cfg
[defaults]
# 禁用 SSH 密钥检查
host_key_checking = False
# 使用加密的密码文件
vault_password_file = /etc/ansible/vault_password
# 提权方式
[privilege_escalation]
become = True
become_method = sudo
# 禁止明文密码传递
pipelining = True

# 安全：SSH 配置
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
          -o StrictHostKeyChecking=yes
          -o UserKnownHostsFile=/dev/null
```

### 5.3 IaC 安全最佳实践

**安全 IaC 清单**
```yaml
# IaC 安全最佳实践清单
security_checklist:
  # 1. 网络安全
  - 禁止 0.0.0.0/0 的入站规则（除 443/80 外）
  - 安全组规则最小化
  - 数据库禁止公网访问
  - 使用私有子网部署内部服务

  # 2. 身份与访问
  - IAM 策略最小权限
  - 禁止使用通配符权限（Action: *）
  - 使用角色而非长期访问密钥
  - 定期轮换密钥

  # 3. 数据保护
  - 存储服务启用加密
  - 数据库启用存储加密
  - 传输加密（TLS）
  - 备份启用加密

  # 4. 日志审计
  - 启用 CloudTrail / 操作日志
  - 启用 CloudWatch / 监控告警
  - 启用 VPC Flow Logs
  - 启用 API Gateway 日志

  # 5. 密钥管理
  - 禁止硬编码密钥
  - 使用 Vault / KMS 管理密钥
  - 敏感数据使用 Ansible Vault
  - .gitignore 排除密钥文件

  # 6. 资源保护
  - 启用删除保护
  - 启用版本控制
  - 启用防篡改
  - 启用 MFA 删除
```

---

## 六、密钥管理

### 6.1 HashiCorp Vault

**Vault 架构**
```
┌─────────────────────────────────────────────────┐
│                Vault 密钥管理架构                 │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │ 应用 Pod  │───→│ Vault    │───→│ 后端存储  │ │
│  │          │    │ Agent    │    │ (KMS等)  │ │
│  │ Sidecar  │    │          │    │          │ │
│  └──────────┘    └────┬─────┘    └──────────┘ │
│                       │                        │
│              ┌────────▼────────┐               │
│              │  Vault Server   │               │
│              │  - 认证引擎     │               │
│              │  - 密钥引擎     │               │
│              │  - 密钥轮换     │               │
│              │  - 审计日志     │               │
│              └─────────────────┘               │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Vault Kubernetes 集成配置**
```yaml
# Vault Agent 注入配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      annotations:
        # 启用 Vault Agent 注入
        vault.hashicorp.com/agent-inject: "true"
        # 配置 Vault 服务器地址
        vault.hashicorp.com/role: "myapp-role"
        # 注入数据库密码到文件
        vault.hashicorp.com/agent-inject-secret-db-password: "database/creds/myapp"
        # 模板渲染
        vault.hashicorp.com/agent-inject-template-db-password: |
          {{- with secret "database/creds/myapp" -}}
          export DB_PASSWORD={{ .Data.password }}
          {{- end }}
    spec:
      serviceAccountName: myapp-sa
      containers:
        - name: myapp
          image: myapp:1.0.0
          command: ["/bin/sh"]
          args: ["-c", "source /vault/secrets/db-password && /app/server"]
```

**Vault 动态数据库凭据**
```bash
# 配置数据库引擎
vault secrets enable database

# 配置数据库连接
vault write database/config/myapp \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(db.internal:3306)/myapp" \
    allowed_roles="myapp"

# 创建角色（动态凭据）
vault write database/roles/myapp \
    db_name=myapp \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}'; \
        GRANT SELECT ON myapp.* TO '{{name}}'@'%';" \
    default_ttl="1h" \
    max_ttl="24h"

# 获取动态凭据
vault read database/creds/myapp
# 输出:
#  username    v-token-myapp-abc123
#  password    def456ghi789
```

### 6.2 Sealed Secrets

```yaml
# 安装 Sealed Secrets
# kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.19.0/controller.yaml

# 加密 Secret
# 1. 创建普通 Secret
echo -n 'my-secret-password' | kubectl create secret generic app-secret \
    --dry-run=client --from-file=password=/dev/stdin -o yaml > secret.yaml

# 2. 加密为 SealedSecret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 3. SealedSecret 可以安全地提交到 Git
cat sealed-secret.yaml
# apiVersion: bitnami.com/v1alpha1
# kind: SealedSecret
# metadata:
#   name: app-secret
# spec:
#   encryptedData:
#     password: AgBh...加密内容...

# 4. 部署到集群
kubectl apply -f sealed-secret.yaml
# 控制器自动解密为普通 Secret
```

### 6.3 External Secrets

```yaml
# External Secrets Operator - 从外部密钥管理器同步密钥
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-external-secret
spec:
  refreshInterval: 1h  # 每小时刷新
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: app-secret  # 创建的 Kubernetes Secret 名称
    creationPolicy: Owner
  data:
    - secretKey: database_password
      remoteRef:
        key: database/creds/myapp
        property: password
    - secretKey: api_key
      remoteRef:
        key: api/myapp
        property: key

---
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "kv"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "external-secrets"
          serviceAccountRef:
            name: external-secrets-sa
```

---

## 七、实战案例：构建安全的 Kubernetes 生产环境

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

## 八、容器与 IaC 安全最佳实践总结

### 8.1 容器安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| 镜像安全 | 使用官方精简基础镜像 | 高 |
| 镜像安全 | 固定镜像版本标签 | 高 |
| 镜像安全 | 定期扫描镜像漏洞 | 高 |
| 镜像安全 | 镜像签名验证 | 中 |
| 镜像安全 | 不在镜像中存储密钥 | 高 |
| 运行时安全 | 非 root 用户运行 | 高 |
| 运行时安全 | 只读根文件系统 | 高 |
| 运行时安全 | 丢弃所有 capabilities | 高 |
| 运行时安全 | 启用 Seccomp | 中 |
| 运行时安全 | 资源限制 | 高 |
| 运行时安全 | 运行时安全监控 | 中 |

### 8.2 Kubernetes 安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| RBAC | 最小权限配置 | 高 |
| RBAC | 禁止 cluster-admin 过度授权 | 高 |
| Pod Security | Restricted 安全级别 | 高 |
| Pod Security | 禁止特权容器 | 高 |
| 网络安全 | 默认拒绝 Network Policy | 高 |
| 网络安全 | 最小允许网络策略 | 高 |
| 网络安全 | mTLS 服务网格 | 中 |
| 准入控制 | OPA Gatekeeper 策略 | 高 |
| 准入控制 | 镜像签名验证 | 中 |
| 密钥管理 | Vault 动态密钥 | 高 |
| 密钥管理 | 禁止 Secret 明文存储 | 高 |
| 审计 | 启用审计日志 | 高 |
| 监控 | 运行时安全监控(Falco) | 中 |
| 监控 | 安全基准检查(kube-bench) | 中 |

### 8.3 IaC 安全清单

| 类别 | 检查项 | 优先级 |
|------|-------|-------|
| 网络安全 | 安全组最小化规则 | 高 |
| 网络安全 | 禁止 0.0.0.0/0 入站 | 高 |
| 网络安全 | 数据库禁止公网访问 | 高 |
| IAM | 最小权限策略 | 高 |
| IAM | 禁止通配符权限 | 高 |
| 数据保护 | 存储加密 | 高 |
| 数据保护 | 数据库加密 | 高 |
| 数据保护 | 传输加密(TLS) | 高 |
| 密钥管理 | 禁止硬编码密钥 | 高 |
| 密钥管理 | 使用 Vault/KMS | 高 |
| 日志审计 | 启用操作日志 | 中 |
| 资源保护 | 启用删除保护 | 中 |
| IaC扫描 | tfsec/Checkov 扫描 | 高 |

---

> **总结**：容器与 IaC 安全是云原生安全的基石。容器安全需要从镜像构建到运行时全链路防护，Kubernetes 安全需要从集群到工作负载多层防御，IaC 安全需要将安全检查嵌入代码管理流程。关键是通过自动化工具链实现持续安全验证，确保基础设施配置始终符合安全标准。通过"安全即代码"的方式，将安全策略版本化管理、自动化验证、持续监控，才能真正构建安全的云原生生产环境。
