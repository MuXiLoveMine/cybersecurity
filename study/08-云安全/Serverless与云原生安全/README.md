# Serverless与云原生安全

> 本文档整理自：`Serverless与云原生安全.md`

---

## 目录

### [01. Serverless 安全概述](./01_Serverless 安全概述/Serverless 安全概述.md)
  - 什么是 Serverless
  - FaaS 安全模型与责任边界变化
  - Serverless 攻击面模型

### [02. Serverless 攻击面详解](./02_Serverless 攻击面详解/Serverless 攻击面详解.md)
  - 事件注入
  - 权限过度
  - 依赖漏洞
  - 拒绝钱包攻击（DoW）
  - 敏感信息泄露
  - 函数执行链滥用

### [03. Serverless 安全防护](./03_Serverless 安全防护/Serverless 安全防护.md)
  - 最小权限函数
  - 依赖扫描
  - API 网关防护
  - 日志与监控
  - 函数代码加固

### [04. 云原生安全全景](./04_云原生安全全景/云原生安全全景.md)
  - 容器安全
  - 镜像扫描与签名

### [05. Kubernetes 安全](./05_Kubernetes 安全/Kubernetes 安全.md)
  - Kubernetes 攻击面
  - RBAC 最小权限
  - Pod 安全标准（PSS）
  - 网络策略（NetworkPolicy）
  - API Server 加固

### [06. Service Mesh 安全](./06_Service Mesh 安全/Service Mesh 安全.md)
  - Service Mesh 概述
  - Istio 安全功能
  - Linkerd 安全功能
  - 零信任网络

### [07. 云原生运行时安全](./07_云原生运行时安全/云原生运行时安全.md)
  - Falco
  - Tetragon
  - eBPF 安全监控原理

### [08. 云原生供应链安全](./08_云原生供应链安全/云原生供应链安全.md)
  - SBOM（软件物料清单）
  - 镜像签名与验证
  - 策略即代码
  - 供应链安全框架 SLSA

### [09. GitOps 安全](./09_GitOps 安全/GitOps 安全.md)
  - GitOps 概述
  - ArgoCD 安全
  - Flux 安全

### [10. 安全最佳实践](./10_安全最佳实践/安全最佳实践.md)
  - Serverless 最佳实践
  - 容器与 Kubernetes 最佳实践
  - Service Mesh 最佳实践
  - 运行时安全最佳实践
  - 供应链最佳实践
  - GitOps 最佳实践

### [11. 总结](./11_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：11
- 待完善章节：11

### 各章节审核状态
- **Serverless 安全概述**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Serverless 攻击面详解**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **Serverless 安全防护**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **云原生安全全景**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Kubernetes 安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **Service Mesh 安全**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **云原生运行时安全**：⚠️ 需补充 4 项
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **云原生供应链安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **GitOps 安全**：⚠️ 需补充 4 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **安全最佳实践**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **总结**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
