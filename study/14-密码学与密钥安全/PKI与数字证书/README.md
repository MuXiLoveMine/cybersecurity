# PKI与数字证书

> 本文档整理自：`PKI与数字证书.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. PKI概述](./02_PKI概述/PKI概述.md)
  - 什么是PKI
  - 为什么需要PKI
  - PKI发展简史
  - PKI的核心组成
  - PKI提供的安全服务

### [03. PKI体系架构](./03_PKI体系架构/PKI体系架构.md)
  - PKI组件详解
  - 信任模型
  - PKI信任锚点

### [04. X.509数字证书标准](./04_X.509数字证书标准/X.509数字证书标准.md)
  - X.509标准概述
  - X.509证书结构
  - 证书各字段详解
  - 证书扩展字段（Extensions）
  - 证书格式
  - 查看证书内容

### [05. 证书机构（CA）运作机制](./05_证书机构（CA）运作机制/证书机构（CA）运作机制.md)
  - CA信任框架
  - CA认证级别
  - CA运营要求
  - 证书透明度（Certificate Transparency）
  - 自建CA实践

### [06. 信任链与证书验证](./06_信任链与证书验证/信任链与证书验证.md)
  - 证书链验证流程
  - 证书路径构建
  - 证书绑定（Certificate Pinning）

### [07. 证书生命周期管理](./07_证书生命周期管理/证书生命周期管理.md)
  - 证书生命周期总览
  - 证书申请流程
  - 证书续期
  - 证书撤销

### [08. CRL与OCSP证书状态检查](./08_CRL与OCSP证书状态检查/CRL与OCSP证书状态检查.md)
  - CRL（证书撤销列表）
  - OCSP（在线证书状态协议）
  - OCSP装订（OCSP Stapling）

### [09. PKI标准与协议](./09_PKI标准与协议/PKI标准与协议.md)
  - PKI相关标准
  - ACME协议
  - SCEP协议

### [10. PKI部署与运维实践](./10_PKI部署与运维实践/PKI部署与运维实践.md)
  - 企业PKI架构设计
  - 使用OpenSSL搭建CA
  - 证书监控与告警

### [11. PKI安全威胁与防护](./11_PKI安全威胁与防护/PKI安全威胁与防护.md)
  - CA被攻破
  - 中间人攻击
  - DNS CAA记录
  - 私钥泄露

### [12. 国密PKI体系](./12_国密PKI体系/国密PKI体系.md)
  - 国密算法在PKI中的应用
  - 国密证书特点
  - GMSSL工具
  - 双证书体系

### [13. 云原生PKI与自动化证书管理](./13_云原生PKI与自动化证书管理/云原生PKI与自动化证书管理.md)
  - cert-manager（Kubernetes证书管理）
  - 内部CA自动化
  - SPIFFE/SPIRE

### [14. PKI应用场景分析](./14_PKI应用场景分析/PKI应用场景分析.md)
  - HTTPS/TLS
  - 代码签名
  - 邮件安全（S/MIME）
  - VPN认证
  - 物联网设备认证

### [15. 总结与最佳实践](./15_总结与最佳实践/总结与最佳实践.md)
  - PKI最佳实践
  - PKI未来趋势
  - 参考资源

---

## 📊 内容审核总览

- 总章节数：15
- 待完善章节：15

### 各章节审核状态
- **目录**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **PKI概述**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **PKI体系架构**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **X.509数字证书标准**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **证书机构（CA）运作机制**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **信任链与证书验证**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **证书生命周期管理**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **CRL与OCSP证书状态检查**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **PKI标准与协议**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **PKI部署与运维实践**：⚠️ 需补充 6 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **PKI安全威胁与防护**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **国密PKI体系**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **云原生PKI与自动化证书管理**：⚠️ 需补充 5 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **PKI应用场景分析**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **总结与最佳实践**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
