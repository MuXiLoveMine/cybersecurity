# 容器与Kubernetes安全实战指南

> 本文档整理自：`容器与Kubernetes安全实战指南.md`

---

## 目录

### [01. 容器安全概述](./01_容器安全概述/容器安全概述.md)
  - 容器 vs 虚拟机安全模型对比
  - 容器安全生命周期
  - 容器安全责任矩阵

### [02. Docker镜像安全](./02_Docker镜像安全/Docker镜像安全.md)
  - 镜像构建安全
  - 镜像漏洞扫描
  - 镜像仓库安全

### [03. 容器运行时安全](./03_容器运行时安全/容器运行时安全.md)
  - 容器隔离机制
  - Linux Capabilities与最小权限
  - Seccomp配置
  - AppArmor/SELinux配置
  - Docker安全加固清单
  - 容器逃逸原理与防御
  - gVisor/Kata Containers

### [04. Kubernetes安全](./04_Kubernetes安全/Kubernetes安全.md)
  - K8s架构安全概览
  - RBAC（基于角色的访问控制）
  - 网络安全
  - Pod安全
  - etcd安全
  - Secret管理
  - 准入控制器
  - K8s常见攻击面

### [05. CI/CD中的容器安全](./05_CI_CD中的容器安全/CI_CD中的容器安全.md)
  - 流水线中的镜像扫描
  - 策略即代码
  - Sigstore供应链签名验证

### [06. 容器安全监控与运营](./06_容器安全监控与运营/容器安全监控与运营.md)
  - 运行时威胁检测
  - 容器安全态势管理（CSPM）

### [07. 容器安全事件响应](./07_容器安全事件响应/容器安全事件响应.md)
  - 容器取证基础
  - 容器逃逸事件检测
  - 遭遇容器逃逸后的应急流程

### [08. Python容器安全检查脚本示例](./08_Python容器安全检查脚本示例/Python容器安全检查脚本示例.md)
  - Docker API安全检查脚本
  - K8s API安全审计脚本

### [09. 总结](./09_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：9
- 待完善章节：9

### 各章节审核状态
- **容器安全概述**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **Docker镜像安全**：⚠️ 需补充 1 项
  - 缺少：references
- **容器运行时安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **Kubernetes安全**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **CI/CD中的容器安全**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **容器安全监控与运营**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
- **容器安全事件响应**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
- **Python容器安全检查脚本示例**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **总结**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：commands
  - 缺少：attack
  - 缺少：references
