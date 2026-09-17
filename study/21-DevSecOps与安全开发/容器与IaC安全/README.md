# 容器与IaC安全

> 本文档整理自：`容器与IaC安全.md`

---

## 目录

### [01. 容器安全概述](./01_容器安全概述/容器安全概述.md)
  - 容器与虚拟机安全差异
  - 容器攻击面分析

### [02. 镜像安全](./02_镜像安全/镜像安全.md)
  - 基础镜像选择
  - 镜像扫描
  - 镜像签名（Cosign）

### [03. 容器运行时安全](./03_容器运行时安全/容器运行时安全.md)
  - Seccomp 配置
  - AppArmor 配置
  - Capabilities 最小化
  - 只读根文件系统
  - 完整的安全 Dockerfile

### [04. Kubernetes 安全](./04_Kubernetes 安全/Kubernetes 安全.md)
  - RBAC 配置
  - Pod Security Standards
  - Network Policy
  - 准入控制（OPA Gatekeeper）

### [05. IaC 安全](./05_IaC 安全/IaC 安全.md)
  - Terraform 安全
  - Ansible 安全
  - IaC 安全最佳实践

### [06. 密钥管理](./06_密钥管理/密钥管理.md)
  - HashiCorp Vault
  - Sealed Secrets
  - External Secrets

### [07. 实战案例：构建安全的 Kubernetes 生产环境](./07_实战案例：构建安全的 Kubernetes 生产环境/实战案例：构建安全的 Kubernetes 生产环境.md)
  - 整体安全架构
  - 安全的 Deployment 配置
  - Network Policy 配置
  - 安全监控部署
  - CI/CD 安全流水线

### [08. 容器与 IaC 安全最佳实践总结](./08_容器与 IaC 安全最佳实践总结/容器与 IaC 安全最佳实践总结.md)
  - 容器安全清单
  - Kubernetes 安全清单
  - IaC 安全清单

---

## 📊 内容审核总览

- 总章节数：8
- 待完善章节：8

### 各章节审核状态
- **容器安全概述**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **镜像安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **容器运行时安全**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Kubernetes 安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **IaC 安全**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **密钥管理**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **实战案例：构建安全的 Kubernetes 生产环境**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **容器与 IaC 安全最佳实践总结**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
