# GitOps 安全

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

---

