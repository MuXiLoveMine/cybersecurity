# 第1章 Kubernetes安全架构概述

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

---

