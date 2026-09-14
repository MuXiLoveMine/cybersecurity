# 容器与Kubernetes安全实战指南

> 本文档面向安全工程师与运维人员，深入讲解容器与 Kubernetes 安全的全生命周期实践：从镜像构建、运行时加固、K8s 集群安全到事件响应，包含大量可落地的配置示例与检测脚本。

---

## 一、容器安全概述

### 1.1 容器 vs 虚拟机安全模型对比

容器与虚拟机（VM）在隔离模型上有根本差异，理解这一点是做好容器安全的前提：

| 安全维度 | 虚拟机（VM） | 容器（Container） |
|----------|-------------|-------------------|
| 隔离边界 | Hypervisor 硬件级隔离 | Namespace + Cgroups 进程级隔离 |
| 内核共享 | 每个 VM 独立内核 | 所有容器共享宿主机内核 |
| 逃逸难度 | 需突破 Hypervisor | 获取宿主机内核权限即可 |
| 攻击面 | 内核漏洞 + Hypervisor 漏洞 | 内核漏洞 + 容器运行时漏洞 + 配置错误 |
| 权限模型 | VM 内 root 不等于宿主 root | 容器内 root 默认映射为宿主 root |

**核心风险**：容器共享内核意味着一个容器利用内核漏洞逃逸后，可影响同一节点上的所有容器。

### 1.2 容器安全生命周期

容器安全贯穿三个阶段，缺一不可：

```
构建阶段（Build）        部署阶段（Deploy）        运行时阶段（Runtime）
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ 基础镜像选择  │       │ 镜像签名验证  │       │ 运行时威胁检测│
│ 多阶段构建    │──────▶│ 准入策略检查  │──────▶│ 容器隔离加固  │
│ 依赖漏洞扫描  │       │ Secret 注入   │       │ 网络策略执行  │
│ 镜像签名      │       │ 安全上下文    │       │ 事件响应取证  │
└──────────────┘       └──────────────┘       └──────────────┘
```

### 1.3 容器安全责任矩阵

| 安全层 | 云厂商（托管K8s） | 用户 |
|--------|-------------------|------|
| 物理设施与虚拟化 | 负责 | 不适用 |
| 控制面组件（API Server/etcd/Scheduler） | 负责 | 不适用 |
| 工作节点 OS | 托管集群由厂商负责；自管节点由用户负责 | 视模式而定 |
| 容器运行时（containerd/Docker） | 厂商维护升级 | 用户配置加固 |
| 镜像内容与依赖 | 不负责 | **负责** |
| Pod 安全策略与 RBAC | 不负责 | **负责** |
| 网络策略与 Secret 管理 | 不负责 | **负责** |
| 运行时监控与事件响应 | 提供工具可选 | **负责** |

---

## 二、Docker镜像安全

### 2.1 镜像构建安全

#### 2.1.1 最小化基础镜像选择

| 基础镜像 | 大小 | 包含 Shell | 包含包管理器 | 安全性 |
|----------|------|-----------|-------------|--------|
| ubuntu:22.04 | ~77MB | 是 | apt | 中 |
| alpine:3.18 | ~7MB | 是 | apk | 中（musl libc 兼容性问题） |
| distroless | ~2-20MB | **否** | **否** | **高** |
| scratch | 0MB | 否 | 否 | 最高（需静态编译） |

**推荐**：生产环境使用 distroless 或 Alpine，最小化攻击面。

#### 2.1.2 多阶段构建减少攻击面

```dockerfile
# 阶段1：构建阶段（包含编译工具，不进入最终镜像）
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o myapp -ldflags="-s -w" main.go

# 阶段2：最终镜像（最小化，不含编译工具链）
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/myapp /myapp
USER nonroot:nonroot
ENTRYPOINT ["/myapp"]
```

#### 2.1.3 安全的Dockerfile编写规范

```dockerfile
# 基础镜像：使用固定版本标签，禁止用 latest
FROM python:3.12-slim AS base

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser -s /sbin/nologin appuser

# 仅复制必要文件，使用 .dockerignore 排除 .git/credentials
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache /tmp/*

# 切换为非root用户
USER appuser

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

CMD ["python", "app.py"]
```

### 2.2 镜像漏洞扫描

#### 2.2.1 Trivy使用实战

```bash
# 扫描镜像漏洞
trivy image python:3.12-slim

# 仅显示高危和严重漏洞
trivy image --severity HIGH,CRITICAL python:3.12-slim

# 输出JSON格式，便于CI/CD集成
trivy image --format json -o results.json python:3.12-slim

# 扫描时跳过已修复的漏洞
trivy image --ignore-unfixed python:3.12-slim

# 使用 Trivy 内置策略检查 Dockerfile
trivy config Dockerfile
```

#### 2.2.2 Grype扫描

```bash
# 安装并扫描
grype python:3.12-slim

# 仅显示固定版本可修复的漏洞
grype python:3.12-slim --only-fixed
```

#### 2.2.3 镜像签名（Cosign）

```bash
# 生成密钥对
cosign generate-key-pair

# 对镜像签名
cosign sign --key cosign.key myregistry.com/myapp:v1.0

# 验证签名
cosign verify --key cosign.pub myregistry.com/myapp:v1.0

# 在K8s准入策略中强制验证签名（详见第四章准入控制器部分）
```

### 2.3 镜像仓库安全

#### 2.3.1 Harbor私有仓库

Harbor 是企业级私有镜像仓库，提供镜像扫描、签名验证、访问控制等能力。核心安全配置：

```yaml
# Harbor 安全配置要点
# 1. 启用漏洞扫描：每次 push 后自动扫描
# 2. 启用镜像签名：集成 Notary/Cosign
# 3. 配置机器人账户：CI/CD 使用受限 token
# 4. 配置副本与存储加密

# Harbor docker-compose 中的核心服务
core:
  environment:
    - CONFIG_PATH=/etc/core/app.conf
    - NOTARY_URL=https://notary.harbor.local
    -clair_url=http://clair:6060
    # 启用 OIDC 认证
    - OIDC_NAME=SSO
    - OIDC_ENDPOINT=https://keycloak.local/auth/realms/main
    - OIDC_CLIENTID=harbor
    - OIDC_CLIENTSECRET=<secret>
```

---

## 三、容器运行时安全

### 3.1 容器隔离机制

容器隔离依赖 Linux 内核的两大机制：

- **Namespace**：提供资源视图隔离（PID、网络、挂载、UTS、IPC、用户）
- **Cgroups**：提供资源使用限制（CPU、内存、I/O、PID 数量）

### 3.2 Linux Capabilities与最小权限

容器默认以 root 运行并携带部分 Capabilities，应移除不必要的权限：

```bash
# 查看容器当前 capabilities
docker run --rm python:3.12-slim cat /proc/1/status | grep Cap

# 运行时仅授予必要 capability（如 NET_BIND_SERVICE）
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp:v1

# Docker 默认赋予的 capabilities（应全部 DROP，按需添加）：
# CHOWN, DAC_OVERRIDE, FSETID, FOWNER, MKNOD, NET_RAW, SETGID,
# SETUID, SETFCAP, SETPCAP, NET_BIND_SERVICE, SYS_CHROOT, KILL, AUDIT_WRITE
```

### 3.3 Seccomp配置

Seccomp 限制容器可调用的系统调用，默认 Docker 已启用 default profile：

```json
// 自定义 seccomp profile：禁止容器调用 ptrace、mount、reboot
{
  "defaultAction": "SCMP_ACT_ALLOW",
  "syscalls": [
    {
      "names": ["ptrace", "mount", "umount", "reboot", "setns", "unshare"],
      "action": "SCMP_ACT_ERRNO"
    }
  ]
}
```

```bash
# 应用自定义 seccomp profile
docker run --security-opt seccomp=/path/to/profile.json myapp:v1
```

### 3.4 AppArmor/SELinux配置

```bash
# AppArmor：为容器创建 profile
docker run --security-opt apparmor=docker-default myapp:v1

# 自定义 AppArmor profile 示例
#include <tunables/global>
profile my-app-profile flags=(attach_disconnected) {
  #include <abstractions/base>
  network inet,
  deny /**w,  # 禁止写入任意路径
  /app/myapp rix,
  /tmp/ rw,
}
```

### 3.5 Docker安全加固清单

```bash
# 1. 启用用户命名空间（容器root映射为宿主非特权用户）
# /etc/docker/daemon.json
{
  "userns-remap": "default",
  "no-new-privileges": true,
  "icc": false,
  "live-restore": true,
  "userland-proxy": false,
  "disable-legacy-registry": true
}

# 2. 限制资源（CPU/内存/PID）
docker run \
  --memory=512m --memory-swap=512m \
  --cpus=1.0 --cpu-shares=512 \
  --pids-limit=100 \
  myapp:v1

# 3. 禁止特权模式
docker run --privileged=false myapp:v1

# 4. 只读文件系统 + 临时目录
docker run --read-only --tmpfs /tmp:rw,size=10m myapp:v1

# 5. 禁止 SETUID/SETGID
docker run --security-opt no-new-privileges myapp:v1
```

### 3.6 容器逃逸原理与防御

#### CVE-2019-5736（runc逃逸）

**原理**：攻击者在容器内通过覆盖宿主机上的 runc 二进制文件，当宿主机执行 `docker exec` 时触发恶意 runc，获取宿主机 root 权限。

**防御**：升级 runc 到 1.0-rc6 以上版本，使用只读的 runc 二进制路径。

#### CVE-2020-15257（containerd逃逸）

**原理**：containerd-shim 通过 abstract socket 暴露 API，攻击者可从容器网络命名空间访问该 socket 并调用 Host API 逃逸。

**防御**：升级 containerd 到 1.4.3/1.3.9 以上，限制容器网络对 abstract socket 的访问。

#### 特权容器逃逸与挂载Docker Socket逃逸

```bash
# 特权容器逃逸（危险！仅用于理解原理）
docker run --privileged -v /:/host alpine
# 此时容器拥有所有 capabilities，可挂载宿主机磁盘：
# mount /dev/sda1 /host && chroot /host

# 挂载 Docker Socket 逃逸
docker run -v /var/run/docker.sock:/var/run/docker.sock docker:dind
# 容器内可调用 Docker API 创建新容器并挂载宿主机根目录
```

#### 内核漏洞逃逸

| CVE | 漏洞 | 影响 |
|-----|------|------|
| DirtyCow (CVE-2016-5195) | 竞争条件导致只读映射可写 | 容器内可修改宿主机只读文件 |
| CVE-2022-0847 (Dirty Pipe) | pipe buffer flag 未清零 | 容器内可覆盖任意只读文件 |

**防御**：及时更新内核补丁，使用 gVisor/Kata Containers 增强隔离。

### 3.7 gVisor/Kata Containers

| 方案 | 隔离方式 | 性能损耗 | 兼容性 |
|------|---------|---------|--------|
| gVisor | 用户态内核拦截系统调用 | 中等 | 部分系统调用不兼容 |
| Kata Containers | 轻量级 VM + 容器接口 | 较高 | 完全兼容 |

```bash
# 使用 gVisor 运行容器（需先安装并配置 runtime）
docker run --runtime=runsc myapp:v1
```

---

## 四、Kubernetes安全

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

## 五、CI/CD中的容器安全

### 5.1 流水线中的镜像扫描

```yaml
# GitLab CI 示例
stages:
  - build
  - scan
  - deploy

build_image:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

scan_image:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity CRITICAL,HIGH $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  allow_failure: false  # 发现高危漏洞则流水线失败

deploy:
  stage: deploy
  script:
    - kubectl apply -f k8s/
  only:
    - main
```

### 5.2 策略即代码

在流水线中注入 Kyverno/Gatekeeper 策略检查，确保部署前策略合规：

```bash
# 在 CI 中使用 kyverno CLI 验证策略
kyverno apply policies/ --resource k8s/deployment.yaml
```

### 5.3 Sigstore供应链签名验证

```bash
# 构建后签名镜像
cosign sign --key cosign.key $REGISTRY/$IMAGE:$TAG

# 在部署前验证签名
cosign verify --key cosign.pub $REGISTRY/$IMAGE:$TAG && \
  kubectl rollout restart deployment/myapp
```

---

## 六、容器安全监控与运营

### 6.1 运行时威胁检测

#### Falco使用实战

Falco 基于 Linux 内核模块/eBPF，实时检测容器异常行为：

```yaml
# Falco 自定义规则：检测容器中执行 shell
- rule: Shell Spawned in Container
  desc: 检测容器中启动 shell 进程
  condition: >
    container.id != host and
    proc.name in (bash, sh, zsh, ash)
  output: >
    容器中执行shell (user=%user.name container=%container.name
    image=%container.image.repository cmd=%proc.cmdline)
  priority: WARNING
  tags: [container, shell, mitre_execution]

# 检测容器读取 /etc/shadow
- rule: Read Sensitive File in Container
  desc: 检测容器读取敏感文件
  condition: >
    container.id != host and
    fd.name in (/etc/shadow, /etc/passwd, /root/.ssh/id_rsa)
  output: >
    容器读取敏感文件 (container=%container.name file=%fd.name)
  priority: CRITICAL
  tags: [container, filesystem, mitre_credential_access]
```

```bash
# 运行 Falco
falco -r /etc/falco/falco_rules.local.yaml
```

#### Tetragon/Cilium Runtime Security

基于 eBPF 的高性能运行时安全方案，可在内核态直接阻断威胁：

```yaml
# Tetragon 策略：禁止容器执行 mount 命令
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata:
  name: block-mount-in-container
spec:
  kprobes:
  - call: "sys_mount"
    syscall: true
    args:
    - index: 0
      type: "string"
    selectors:
    - matchBinaries:
      - operator: "In"
        values: ["/bin/mount"]
      matchPIDs:
      - operator: "In"
        values: ["container"]  # 仅匹配容器进程
      action: Block
```

### 6.2 容器安全态势管理（CSPM）

#### kube-bench CIS基准检查

```bash
# 运行 CIS Kubernetes Benchmark 检查
kube-bench --benchmark cis-1.8

# 检查指定节点类型
kube-bench run --targets node
kube-bench run --targets master
```

#### kube-hunter漏洞发现

```bash
# 主动扫描集群安全漏洞
kube-hunter --remote  # 远程扫描
kube-hunter --pod      # 从集群内部扫描
```

#### Polaris配置审计

```bash
# 审计集群配置
polaris audit --audit-path=.

# 生成 Dashboard
polaris dashboard --audit-path=.
```

---

## 七、容器安全事件响应

### 7.1 容器取证基础

```bash
# 1. 保存容器状态为镜像（保留证据）
docker commit <container_id> forensic-evidence

# 2. 导出容器文件系统
docker export <container_id> | gzip > container_fs.tar.gz

# 3. 查看容器日志
docker logs --timestamps --details <container_id> > container.log

# 4. 检查容器进程
docker top <container_id>
```

### 7.2 容器逃逸事件检测

**可疑指标**：
- 容器内出现宿主机文件路径（如 `/host`、`/proc/1/root`）
- 容器内执行 `mount`、`nsenter`、`unshare` 命令
- 容器进程访问 `/var/run/docker.sock`
- 新容器以特权模式异常启动

### 7.3 遭遇容器逃逸后的应急流程

```
1. 隔离：立即暂停容器（docker pause），不要直接删除（保留证据）
2. 取证：导出文件系统、日志、内存快照
3. 分析：检查容器是否已横向移动到其他容器
4. 清除：删除被入侵的容器镜像，重建干净镜像
5. 修复：修复逃逸漏洞（内核补丁/运行时升级）
6. 加固：审查所有特权容器、挂载点、RBAC配置
7. 复盘：更新安全策略，部署检测规则
```

---

## 八、Python容器安全检查脚本示例

### 8.1 Docker API安全检查脚本

```python
#!/usr/bin/env python3
"""
Docker 容器安全检查脚本
检查运行中容器的安全配置，输出安全风险报告。
"""
import docker
import json
from datetime import datetime


def check_container_security(container):
    """检查单个容器的安全配置"""
    issues = []
    info = container.attrs

    # 检查1：是否以特权模式运行
    if info["HostConfig"]["Privileged"]:
        issues.append({"severity": "CRITICAL",
                       "issue": "容器以特权模式运行，存在逃逸风险"})

    # 检查2：是否以 root 运行
    user = info["Config"].get("User", "")
    if not user or user == "root" or user == "0":
        issues.append({"severity": "HIGH",
                       "issue": "容器以 root 用户运行"})

    # 检查3：是否挂载了 Docker Socket
    binds = info["HostConfig"].get("Binds", []) or []
    for bind in binds:
        if "docker.sock" in bind:
            issues.append({"severity": "CRITICAL",
                           "issue": f"挂载了 Docker Socket: {bind}"})

    # 检查4：是否挂载了宿主机敏感目录
    for bind in binds:
        for sensitive_path in ["/", "/etc", "/root", "/var/run"]:
            if bind.startswith(sensitive_path + ":") or bind.startswith(sensitive_path):
                issues.append({"severity": "CRITICAL",
                               "issue": f"挂载了宿主机敏感目录: {bind}"})

    # 检查5：是否启用只读文件系统
    if not info["HostConfig"]["ReadonlyRootfs"]:
        issues.append({"severity": "MEDIUM",
                       "issue": "未启用只读文件系统"})

    # 检查6：是否禁止 privilege escalation
    security_opt = info["HostConfig"].get("SecurityOpt", []) or []
    if "no-new-privileges" not in security_opt:
        issues.append({"severity": "MEDIUM",
                       "issue": "未禁止 privilege escalation (no-new-privileges)"})

    # 检查7：Capabilities 是否过多
    caps = info["HostConfig"].get("CapAdd", []) or []
    caps_drop = info["HostConfig"].get("CapDrop", []) or []
    if not caps_drop and not caps:
        issues.append({"severity": "LOW",
                       "issue": "使用默认 Capabilities，建议 --cap-drop ALL"})

    # 检查8：资源限制
    mem_limit = info["HostConfig"].get("Memory", 0)
    cpu_quota = info["HostConfig"].get("CpuQuota", 0)
    if mem_limit == 0:
        issues.append({"severity": "MEDIUM", "issue": "未设置内存限制"})
    if cpu_quota == 0:
        issues.append({"severity": "MEDIUM", "issue": "未设置 CPU 限制"})

    # 检查9：网络模式
    network_mode = info["HostConfig"].get("NetworkMode", "default")
    if network_mode == "host":
        issues.append({"severity": "HIGH",
                       "issue": "使用 host 网络模式，容器可访问宿主机网络"})

    return {
        "container": container.name,
        "image": info["Config"]["Image"],
        "issues": issues
    }


def main():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    report = {
        "scan_time": datetime.now().isoformat(),
        "total_containers": len(containers),
        "results": []
    }

    for container in containers:
        result = check_container_security(container)
        report["results"].append(result)

    # 统计
    critical = sum(1 for r in report["results"]
                   for i in r["issues"] if i["severity"] == "CRITICAL")
    high = sum(1 for r in report["results"]
               for i in r["issues"] if i["severity"] == "HIGH")
    print(f"\n{'='*60}")
    print(f"  Docker 容器安全检查报告")
    print(f"  扫描时间: {report['scan_time']}")
    print(f"  容器总数: {report['total_containers']}")
    print(f"  CRITICAL: {critical} | HIGH: {high}")
    print(f"{'='*60}")

    for result in report["results"]:
        if result["issues"]:
            print(f"\n  [容器] {result['container']} ({result['image']})")
            for issue in result["issues"]:
                print(f"    [{issue['severity']}] {issue['issue']}")

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

### 8.2 K8s API安全审计脚本

```python
#!/usr/bin/env python3
"""
Kubernetes 集群安全审计脚本
使用 client-python 检查 K8s 集群安全配置。
依赖: pip install kubernetes
"""
from kubernetes import client, config


class K8sSecurityAuditor:
    def __init__(self):
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.rbac = client.RbacAuthorizationV1Api()
        self.policy = client.PolicyV1Api()

    def check_anonymous_access(self):
        """检查API Server是否允许匿名访问"""
        # 模拟匿名访问（实际应通过 --anonymous-auth=false 关闭）
        issues = []
        try:
            # 检查是否有 system:anonymous 绑定
            bindings = self.rbac.list_cluster_role_binding()
            for b in bindings.items:
                for subject in (b.subjects or []):
                    if subject.name == "system:anonymous":
                        issues.append({
                            "severity": "CRITICAL",
                            "issue": f"匿名用户绑定了角色: {b.metadata.name}"
                        })
        except Exception as e:
            issues.append({"severity": "INFO",
                           "issue": f"检查异常: {e}"})
        return issues

    def check_overprivileged_rbac(self):
        """检查过度授权的RBAC配置"""
        issues = []
        # 检查 cluster-admin 绑定
        crbs = self.rbac.list_cluster_role_binding()
        for crb in crbs.items:
            if crb.role_ref.name == "cluster-admin":
                for subject in (crb.subjects or []):
                    if subject.kind == "ServiceAccount":
                        issues.append({
                            "severity": "HIGH",
                            "issue": f"ServiceAccount '{subject.name}' 拥有 cluster-admin 权限"
                        })
        return issues

    def check_pod_security(self):
        """检查Pod安全配置"""
        issues = []
        pods = self.v1.list_pod_for_all_namespaces()
        for pod in pods.items:
            for cs in pod.spec.containers:
                sc = cs.security_context
                name = f"{pod.metadata.namespace}/{pod.metadata.name}/{cs.name}"

                # 检查特权容器
                if sc and sc.privileged:
                    issues.append({
                        "severity": "CRITICAL",
                        "issue": f"特权容器: {name}"
                    })

                # 检查 root 运行
                if not sc or not sc.run_as_non_root:
                    issues.append({
                        "severity": "HIGH",
                        "issue": f"未设置 runAsNonRoot: {name}"
                    })

                # 检查 privilege escalation
                if not sc or sc.allow_privilege_escalation is not False:
                    issues.append({
                        "severity": "MEDIUM",
                        "issue": f"未禁止 allowPrivilegeEscalation: {name}"
                    })

                # 检查 capabilities
                if sc and sc.capabilities:
                    drops = sc.capabilities.drop or []
                    if "ALL" not in drops:
                        issues.append({
                            "severity": "MEDIUM",
                            "issue": f"未 drop ALL capabilities: {name}"
                        })
                else:
                    issues.append({
                        "severity": "MEDIUM",
                        "issue": f"未配置 capabilities drop: {name}"
                    })
        return issues

    def check_namespaces_with_secrets(self):
        """检查默认命名空间是否包含敏感Secret"""
        issues = []
        secrets = self.v1.list_secret_for_all_namespaces()
        for secret in secrets.items:
            if secret.type == "kubernetes.io/service-account-token":
                continue  # 跳过SA token
            if secret.data:
                issues.append({
                    "severity": "INFO",
                    "issue": f"Secret存在: {secret.metadata.namespace}/{secret.metadata.name}"
                })
        return issues

    def audit(self):
        """执行完整审计"""
        print(f"\n{'='*60}")
        print("  Kubernetes 安全审计报告")
        print(f"{'='**60}".replace("*", ""))

        checks = [
            ("匿名访问检查", self.check_anonymous_access),
            ("过度授权RBAC检查", self.check_overprivileged_rbac),
            ("Pod安全检查", self.check_pod_security),
            ("Secret检查", self.check_namespaces_with_secrets),
        ]

        for name, func in checks:
            print(f"\n  [{name}]")
            results = func()
            if not results:
                print("    通过 - 未发现问题")
            for r in results:
                print(f"    [{r['severity']}] {r['issue']}")


if __name__ == "__main__":
    auditor = K8sSecurityAuditor()
    auditor.audit()
```

---

## 总结

容器与Kubernetes安全是一个纵深防御体系，核心原则可归纳为：

1. **最小权限**：镜像最小化、Capabilities最小化、RBAC最小化
2. **纵深防御**：镜像扫描 + 运行时加固 + 网络隔离 + 准入控制 + 监控告警多层叠加
3. **供应链可信**：镜像签名验证贯穿构建到部署全流程
4. **持续运营**：CIS基准检查、运行时威胁检测、定期审计形成闭环

**学习路径建议**：

| 阶段 | 工具 | 目标 |
|------|------|------|
| 入门 | Trivy、kube-bench | 掌握镜像扫描与基准检查 |
| 进阶 | Kyverno/OPA、Falco | 掌握准入策略与运行时监控 |
| 高级 | Tetragon、Cosign、Vault | 掌握eBPF安全、供应链签名、Secret管理 |
| 实战 | Python脚本、取证流程 | 掌握自动化审计与事件响应 |
