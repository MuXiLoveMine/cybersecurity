# 容器与Kubernetes多云安全

### 13.1 多云Kubernetes架构

```text
多云Kubernetes部署模式:

模式1: 单集群多区域 (Single Cluster Multi-Region)
  - 一个控制平面,多区域节点
  - 优势: 统一管理
  - 劣势: 控制平面单点

模式2: 多集群联邦 (Multi-Cluster Federation)
  - 每个云一个集群,联邦管理
  - 优势: 故障隔离,数据主权
  - 劣势: 管理复杂

模式3: 混合集群 (Hybrid Cluster)
  - 控制平面在本地,工作节点在云
  - 优势: 数据控制
  - 劣势: 网络延迟

工具选择:
  - Google Anthos: 多云K8s管理
  - Azure Arc: 多云K8s管理
  - EKS Anywhere: AWS混合云K8s
  - Tanzu: VMware多云K8s
  - Rancher: 开源多云K8s管理
```

### 13.2 多云K8s安全策略

```yaml
# Kubernetes NetworkPolicy - 跨云统一网络策略
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multi-cloud-default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              environment: production
    - from:
        - ipBlock:
            cidr: 10.0.0.0/16
    - from:
        - ipBlock:
            cidr: 172.16.0.0/16
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              environment: production
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8
              - 172.16.0.0/12
              - 192.168.0.0/16
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              role: dns

---
# Pod Security Policy / Security Context
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      image: company/app:latest
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        runAsNonRoot: true
        runAsUser: 1000
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE
      resources:
        limits:
          cpu: "2"
          memory: "2Gi"
        requests:
          cpu: "500m"
          memory: "512Mi"
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

### 13.3 多云镜像仓库安全

```bash
# 多云容器镜像安全基线
# 1. 使用私有镜像仓库,禁止使用latest标签
# 2. 镜像签名验证 (Cosign/Sigstore)
# 3. 镜像漏洞扫描 (Trivy/Clair)
# 4. 准入控制器验证

# AWS ECR镜像扫描
aws ecr put-image-scanning-configuration \
    --repository-name my-repo \
    --image-scanning-configuration scanOnPush=true

# Azure ACR镜像扫描
az acr config content-scanning update \
    --name myacr \
    --enabled true

# Cosign镜像签名
# 安装
go install github.com/sigstore/cosign/cmd/cosign@latest

# 生成密钥对
cosign generate-key-pair

# 签名镜像
cosign sign --key cosign.key myregistry.com/app:v1.0

# 验证签名
cosign verify --key cosign.pub myregistry.com/app:v1.0

# 准入控制器策略
# Kyverno策略: 禁止未签名镜像
cat > disallow-unsigned-images.yaml << 'EOF'
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-unsigned-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-image-signature
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
                      ...
                      -----END PUBLIC KEY-----
EOF
```

---

---

## 📋 内容审核与补充建议

> 针对「容器与Kubernetes多云安全」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
