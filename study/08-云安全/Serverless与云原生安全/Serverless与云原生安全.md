# Serverless与云原生安全

> 本文档面向安全学习者，系统讲解 Serverless 安全模型、攻击面与防护手段，并覆盖云原生安全全景：容器、Kubernetes、Service Mesh、运行时安全（eBPF）、供应链安全与 GitOps 安全，提供代码与配置示例及最佳实践。

---

## 一、Serverless 安全概述

### 1.1 什么是 Serverless

Serverless（无服务器）是一种云原生计算模型，开发者只需编写函数代码，云厂商负责底层服务器、扩缩容、调度。典型形式为 FaaS（Function as a Service）：
- AWS Lambda
- 阿里云函数计算（FC）
- Azure Functions
- 腾讯云 SCF

特点：
- 事件驱动：由 HTTP、对象存储、消息队列等事件触发
- 按调用计费
- 无需管理服务器
- 自动弹性伸缩
- 短时执行（通常 15 分钟内）

### 1.2 FaaS 安全模型与责任边界变化

传统云主机安全中，云厂商负责底层物理设施，客户负责操作系统以上。而 FaaS 模型下，责任边界进一步上移：

| 安全责任 | 传统云主机 | FaaS Serverless |
| --- | --- | --- |
| 物理设施 | 云厂商 | 云厂商 |
| 虚拟化层 | 云厂商 | 云厂商 |
| 操作系统 | 客户 | 云厂商 |
| 运行时（Node/Python） | 客户 | 云厂商 |
| 应用代码与依赖 | 客户 | 客户 |
| 函数权限与触发器配置 | 不适用 | 客户 |
| 事件源配置 | 不适用 | 客户 |

可见，客户的安全责任集中在：
- 函数代码本身
- 函数依赖库
- 函数执行角色权限
- 触发器与事件源映射
- 环境变量与密钥管理

### 1.3 Serverless 攻击面模型

Serverless 引入了与传统应用不同的攻击面：

```text
+---------------------------------------------------+
|                  Serverless 攻击面                  |
+---------------------------------------------------+
| 1. 事件源注入（HTTP / 消息 / 对象存储事件）         |
| 2. 函数权限过度（IAM 角色权限过大）                  |
| 3. 第三方依赖漏洞（npm / pip 包）                    |
| 4. 拒绝钱包攻击（资源消耗攻击导致计费）              |
| 5. 敏感信息泄露（环境变量 / 日志）                    |
| 6. 函数执行链滥用（跨函数横向移动）                   |
| 7. 持久化攻击（事件触发器劫持）                      |
+---------------------------------------------------+
```

---

## 二、Serverless 攻击面详解

### 2.1 事件注入

Serverless 函数由各种事件源触发，事件内容本身可能成为攻击载荷。

**案例：对象存储事件处理函数**
- 攻击者上传一个特制文件，函数读取后解析
- 文件名、文件内容、元数据都可能包含恶意载荷
- 例如 CSV 注入、XXE、反序列化漏洞

**防御代码示例（Python Lambda）**

```python
import json
import re

def lambda_handler(event, context):
    # 从 S3 事件中提取对象 key
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    # 1. 输入校验：拒绝非法路径
    if not re.match(r'^[a-zA-Z0-9/_.\-]+$', key):
        return {"statusCode": 400, "body": "非法文件名"}

    # 2. 文件类型白名单
    if not key.endswith(('.csv', '.json', '.txt')):
        return {"statusCode": 400, "body": "不支持的文件类型"}

    # 3. 限制单次处理文件大小，防止资源耗尽
    # （通过对象元数据预检查）

    # 4. 使用安全解析库，禁用外部实体
    # 业务处理 ...
    return {"statusCode": 200, "body": "处理完成"}
```

### 2.2 权限过度

Serverless 函数常被赋予过宽的 IAM 权限，例如一个仅需读取 S3 的函数却被授予 `s3:*` 或更大权限。一旦函数被攻破，攻击者可借此横向移动。

**典型过度权限示例**

```json
// 危险：授予全资源全操作
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

**最小权限示例**

```json
// 安全：仅允许读取指定桶的指定前缀
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::my-data-bucket/uploads/*"
}
```

### 2.3 依赖漏洞

函数依赖的第三方库（npm / pip）可能存在已知漏洞或被植入恶意代码。例如 2018 年 event-stream 包被植入恶意代码窃取比特币钱包。

**依赖扫描示例（pip-audit）**

```bash
# 扫描 Python 函数依赖
pip-audit -r requirements.txt

# 扫描 Node.js 依赖
npm audit --omit=dev
```

**Snyk 集成 CI 检测**

```yaml
# GitHub Actions 中扫描 Serverless 依赖
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
```

### 2.4 拒绝钱包攻击（DoW）

Serverless 按调用计费，攻击者可通过大量触发事件（如高频 HTTP 请求、循环触发队列）导致账单爆炸，称为 Denial of Wallet。

**防御手段**：
- 在 API 网关层设置速率限制与配额
- 使用 WAF 拦截异常流量
- 设置函数并发上限（reserved concurrency）
- 监控异常调用频率并自动告警

```bash
# AWS Lambda 设置预留并发上限
aws lambda put-function-concurrency \
  --function-name my-func \
  --reserved-concurrent-executions 50
```

### 2.5 敏感信息泄露

常见泄露途径：
- 环境变量硬编码密钥
- 日志输出敏感数据
- 错误堆栈暴露内部信息
- 函数返回内容包含敏感字段

**安全使用密钥（AWS Secrets Manager）**

```python
import boto3
import json

def get_secret():
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId="prod/db/password")
    return json.loads(response["SecretString"])["password"]

def lambda_handler(event, context):
    pwd = get_secret()  # 运行时获取，不在代码中硬编码
    # 业务处理
```

### 2.6 函数执行链滥用

Serverless 应用常由多个函数通过事件串联，攻击者一旦攻破一个函数，可借助其权限触发下游函数，形成横向移动链路。

**防御**：对函数间调用进行身份验证与审计，限制函数可触发的下游资源。

---

## 三、Serverless 安全防护

### 3.1 最小权限函数

原则：每个函数只授予完成其单一职责所需的最小权限。

1. 为每个函数创建独立 IAM 角色
2. 权限限定到具体资源 ARN
3. 定期使用 CIEM 工具分析权限使用率，收敛未用权限
4. 避免函数间共享角色

### 3.2 依赖扫描

1. CI 流水线中集成 SCA 工具（Snyk / Dependabot / OSV）
2. 锁定依赖版本，使用 lockfile
3. 禁止使用已废弃或有恶意历史的包
4. 定期重建与更新依赖

### 3.3 API 网关防护

API 网关是 Serverless HTTP 应用的入口，承担关键防护：

```yaml
# AWS API Gateway + Lambda + WAF 示例
# 1. 启用认证（Cognito / Lambda Authorizer）
# 2. 限速
# 3. 接入 WAF
Resources:
  MyApi:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: secure-serverless-api
  WebAcl:
    Type: AWS::WAFv2::WebACL
    Properties:
      DefaultAction:
        Allow: {}
      Rules:
        - Name: rate-limit
          Priority: 1
          Action:
            Block: {}
          VisibilityConfig:
            SampledRequestsEnabled: true
            CloudWatchMetricsEnabled: true
            MetricName: rate-limit
          RateBasedStatement:
            Limit: 100
            AggregateKeyType: IP
```

### 3.4 日志与监控

- 所有函数输出日志到 CloudWatch / SLS
- 启用函数层追踪（X-Ray / 链路追踪）
- 监控异常调用频率、错误率、执行时长
- 对异常事件（如非工作时间大量调用）自动告警

### 3.5 函数代码加固

1. 输入校验：所有事件输入视为不可信
2. 输出过滤：避免返回内部错误细节
3. 禁用危险操作：如 `eval`、`pickle.loads`
4. 使用内存中临时文件而非持久化存储
5. 函数执行超时设置合理上限

---

## 四、云原生安全全景

云原生（Cloud Native）以容器、微服务、声明式 API 为核心。其安全覆盖从代码到运行时全生命周期：

```text
代码 -> 构建 -> 部署 -> 运行
 |        |        |        |
SCA     镜像扫描   IaC扫描   运行时
SAST    SBOM     策略校验   Falco
密钥扫描  签名     准入控制   Tetragon
```

### 4.1 容器安全

容器安全核心要点：
- 镜像漏洞扫描
- 最小化基础镜像（如 distroless / alpine）
- 非 root 用户运行
- 只读文件系统
- 限制资源（CPU / 内存）
- 禁用特权模式

**安全 Pod 配置示例**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities:
        drop:
          - ALL
    resources:
      limits:
        cpu: "500m"
        memory: "256Mi"
      requests:
        cpu: "100m"
        memory: "128Mi"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

### 4.2 镜像扫描与签名

#### 镜像漏洞扫描（Trivy）

```bash
# 扫描镜像漏洞
trivy image myapp:1.0

# 在 CI 中阻断高危漏洞
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:1.0
```

#### 镜像签名（Cosign）

```bash
# 生成密钥对
cosign generate-key-pair

# 对镜像签名
cosign sign --key cosign.key myregistry/myapp:1.0

# 验证签名（部署前校验）
cosign verify --key cosign.pub myregistry/myapp:1.0
```

#### Kyverno 准入策略：只允许已签名镜像

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
  - name: check-signature
    match:
      resources:
        kinds:
        - Pod
    verifyImages:
    - imageReferences:
        - "*"
      attestors:
      - entries:
        - keys:
            publicKeys: |
              -----BEGIN PUBLIC KEY-----
              <cosign 公钥内容>
              -----END PUBLIC KEY-----
```

---

## 五、Kubernetes 安全

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

## 六、Service Mesh 安全

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

## 七、云原生运行时安全

### 7.1 Falco

Falco 是 CNCF 的运行时安全项目，基于内核驱动 / eBPF 实时检测容器异常行为。

**典型规则示例**

```yaml
# 检测容器内启动 shell
- rule: Shell in Container
  desc: Detect shell execution inside a container
  condition: container.id != host and proc.name in (bash, sh, zsh)
  output: >
    Shell opened in container
    (user=%user.name container_id=%container.id
    container_name=%container.name shell=%proc.name
    cmdline=%proc.cmdline)
  priority: WARNING
  tags: [container, shell, mitre_execution]
```

```yaml
# 检测读取敏感文件
- rule: Read Sensitive File
  desc: Detect attempts to read /etc/shadow or /etc/passwd
  condition: fd.name in (/etc/shadow, /etc/passwd) and container
  output: >
    Sensitive file accessed in container
    (file=%fd.name container=%container.name user=%user.name)
  priority: ERROR
```

### 7.2 Tetragon

Tetragon 是基于 eBPF 的高性能运行时安全与可观测工具，支持实时策略执行（可阻断而不仅是告警）。

**Tetragon 策略示例：阻断容器执行 shell**

```yaml
apiVersion: cilium.io/v1alpha1
kind: CiliumTracingPolicy
metadata:
  name: block-shell-in-container
spec:
  kprobes:
  - call: "sys_bpf"
    syscall: true
    args:
    - index: 0
      type: int
    selectors:
    - matchPIDs:
      - operator: In
        values:
        - "0"  # 匹配容器进程
      matchBinaries:
      - operator: In
        values:
        - "/bin/bash"
        - "/bin/sh"
      action: Block  # 直接阻断
```

### 7.3 eBPF 安全监控原理

eBPF（extended Berkeley Packet Filter）允许在内核中安全地运行沙箱程序，是现代云原生运行时安全的技术基础：

```text
用户态策略 --> 内核态 eBPF 程序 --> 拦截系统调用
                                       |
                       +---------------+---------------+
                       |               |               |
                    告警(Falco)     阻断(Tetragon)   指标(Pixie)
```

eBPF 优势：
- 内核态执行，性能开销极低
- 无需修改应用代码或内核
- 全局可见，容器无法绕过
- 可实时阻断，不仅是被动告警

---

## 八、云原生供应链安全

### 8.1 SBOM（软件物料清单）

SBOM 记录软件所有组件、版本、依赖关系，是供应链安全的基础。标准格式有 SPDX、CycloneDX。

**生成 SBOM 示例（Syft）**

```bash
# 为容器镜像生成 SBOM
syft myapp:1.0 -o cyclonedx-json > sbom.json

# 为源码目录生成 SBOM
syft ./src -o spdx-json > sbom.json
```

### 8.2 镜像签名与验证

如前文所述，使用 Cosign 对镜像签名，部署前用策略校验。完整流程：

1. CI 构建镜像
2. 漏洞扫描（Trivy）通过
3. 生成 SBOM
4. Cosign 签名镜像与 SBOM
5. 部署时准入控制器校验签名

### 8.3 策略即代码

使用 OPA / Kyverno 将安全策略代码化，在 CI 与准入阶段强制执行：

```rego
# OPA 策略：禁止特权容器
package k8s.admission

deny[msg] {
    container := input.request.object.spec.containers[_]
    container.securityContext.privileged == true
    msg := sprintf("容器 %s 不允许特权模式", [container.name])
}

deny[msg] {
    container := input.request.object.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("容器 %s 必须以非 root 运行", [container.name])
}
```

### 8.4 供应链安全框架 SLSA

SLSA（Supply-chain Levels for Software Artifacts）定义了供应链安全的分级标准：

| 级别 | 要求 |
| --- | --- |
| L1 | 构建过程有文档化 |
| L2 | 托管构建平台，生成 provenance |
| L3 | 构建隔离，provenance 不可篡改 |
| L4 | 两方独立复核 |

---

## 九、GitOps 安全

### 9.1 GitOps 概述

GitOps 以 Git 仓库作为基础设施与应用部署的唯一真相源，通过 ArgoCD / Flux 自动同步到集群。

安全关注点：
- Git 仓库的访问控制与签名
- 部署工具的 RBAC
- 模板与清单的安全校验
- 防止配置漂移与恶意 PR

### 9.2 ArgoCD 安全

```yaml
# ArgoCD RBAC 限制用户只能操作指定应用
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
data:
  policy.default: role:readonly
  policy.csv: |
    p, role:dev, applications, sync, dev/*, allow
    p, role:dev, applications, delete, dev/*, deny
    g, dev-team, role:dev
```

**ArgoCD 安全加固要点**：
1. 启用 SSO / OIDC 登录，禁用本地账号
2. RBAC 最小权限，生产环境只读
3. 对同步操作实施审批流程（PR 评审）
4. 启用 Git 仓库签名验证（GPG）
5. 限制 ArgoCD 服务账号权限

### 9.3 Flux 安全

Flux 通过 GitRepository 源拉取配置：

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: app-config
  namespace: flux-system
spec:
  url: https://github.com/org/app-config
  ref:
    branch: main
  secretRef:
    name: github-deploy-key  # 使用部署密钥认证
```

**Flux 安全加固**：
1. 使用部署密钥或 OIDC 而非长期 token
2. 启用签名校验（cosign + flux verification）
3. 限制 Flux 服务账号 RBAC
4. 对 HelmRelease / Kustomization 源做校验
5. 监控同步异常与漂移

---

## 十、安全最佳实践

### 10.1 Serverless 最佳实践

1. 每个函数最小权限，独立 IAM 角色
2. 所有输入视为不可信，严格校验
3. CI 集成依赖扫描与 SAST
4. 环境变量不存敏感信息，用密钥管理服务
5. API 网关启用认证、限速、WAF
6. 设置函数并发上限与超时
7. 日志统一聚合，异常告警

### 10.2 容器与 Kubernetes 最佳实践

1. 使用最小化基础镜像（distroless）
2. 镜像漏洞扫描 + 签名验证
3. 非 root 运行，只读根文件系统
4. 禁用特权模式与危险 capabilities
5. Pod Security Standard 设为 restricted
6. RBAC 最小权限
7. NetworkPolicy 默认拒绝
8. etcd 加密存储
9. 定期升级集群版本

### 10.3 Service Mesh 最佳实践

1. 全网格 mTLS STRICT 模式
2. 授权策略默认拒绝
3. JWT 校验在网格层
4. 审计所有授权决策
5. 证书自动轮转

### 10.4 运行时安全最佳实践

1. 部署 Falco / Tetragon 全集群监控
2. 关键规则：shell 执行、敏感文件访问、网络外联
3. 高危行为实时阻断
4. 告警接入 SIEM
5. 定期演练容器逃逸响应

### 10.5 供应链最佳实践

1. 全流程生成 SBOM
2. 镜像签名 + 准入校验
3. IaC 模板扫描（Checkov / tfsec）
4. OPA 策略准入控制
5. 依赖定期更新与漏洞监控
6. 私有镜像仓库 + 镜像代理缓存

### 10.6 GitOps 最佳实践

1. Git 仓库强制签名提交
2. PR 评审 + 自动扫描
3. ArgoCD / Flux 最小 RBAC
4. 生产环境同步需审批
5. 监控配置漂移
6. 回滚机制演练

---

## 十一、总结

Serverless 与云原生代表了现代应用架构的演进方向，但也带来了全新的安全模型：
- 责任边界上移，客户聚焦代码、依赖、权限、配置
- 攻击面从主机转向函数事件、容器、供应链
- 防护手段从边界转向零信任、最小权限、策略即代码

安全学习者应重点掌握：
- Serverless 攻击面与最小权限原则
- 容器与 Kubernetes 安全加固（PSS、RBAC、NetworkPolicy）
- Service Mesh 的 mTLS 与授权策略
- eBPF 运行时安全（Falco、Tetragon）
- 供应链安全（SBOM、镜像签名、SLSA）
- GitOps 安全（ArgoCD、Flux）

这些构成了云原生时代安全工程师的核心知识体系。
