# 移动应用渗透测试完整教程

> 本文档整理自：`移动应用渗透测试完整教程.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. OWASP Mobile Top 10 详解](./02_OWASP Mobile Top 10 详解/OWASP Mobile Top 10 详解.md)
  - M1: Improper Platform Usage（平台使用不当）
  - M2: Insecure Data Storage（不安全的数据存储）
  - M3: Insecure Communication（不安全的通信）
  - M4: Insufficient Authentication（认证不足）
  - M5: Insufficient Cryptography（加密不足）
  - M6: Insecure Authorization（授权不足）
  - M7: Insecure Code Quality（不安全的代码质量）
  - M8: Code Tampering（代码篡改）
  - M9: Reverse Engineering（逆向工程）
  - M10: Extraneous Functionality（多余功能）

### [03. Android 渗透测试完整流程](./03_Android 渗透测试完整流程/Android 渗透测试完整流程.md)
  - 信息收集
  - 静态分析（反编译 / 敏感信息 / 硬编码）
  - 动态分析（Frida Hook / 调试 / MITM）
  - 数据存储安全
  - 通信安全（HTTPS / SSL Pinning / Certificate）
  - 组件安全（Activity / Service / Receiver / Provider）
  - WebView 安全
  - 第三方 SDK 安全
  - Root 检测与绕过
  - 完整性校验与绕过

### [04. iOS 渗透测试流程](./04_iOS 渗透测试流程/iOS 渗透测试流程.md)
  - 越狱环境搭建
  - IPA 解包与分析
  - 动态分析（Frida / Cycript）
  - Keychain 数据
  - App Transport Security (ATS)
  - 剪贴板安全
  - URL Scheme 安全

### [05. 移动端 MITM 测试](./05_移动端 MITM 测试/移动端 MITM 测试.md)
  - 证书安装与信任
  - SSL Pinning 绕过方法汇总
  - 流量分析与篡改
  - WebSocket / gRPC 流量

### [06. 移动端自动化测试](./06_移动端自动化测试/移动端自动化测试.md)
  - MobSF（Mobile Security Framework）
  - Drozer Android 攻击面分析
  - QARK 自动化审计
  - Python 自动化测试脚本示例

### [07. 移动应用渗透测试报告模板](./07_移动应用渗透测试报告模板/移动应用渗透测试报告模板.md)

### [08. 基本信息](./08_基本信息/基本信息.md)

### [09. 测试概要](./09_测试概要/测试概要.md)

### [10. 漏洞详情](./10_漏洞详情/漏洞详情.md)
  - 漏洞 1: [漏洞名称]
  - 漏洞 2: ...

### [11. OWASP Mobile Top 10 测试结果](./11_OWASP Mobile Top 10 测试结果/OWASP Mobile Top 10 测试结果.md)

### [12. 修复建议汇总](./12_修复建议汇总/修复建议汇总.md)

### [13. 附录](./13_附录/附录.md)

### [14. 结语](./14_结语/结语.md)

---

## 📊 内容审核总览

- 总章节数：14
- 待完善章节：14

### 各章节审核状态
- **目录**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **OWASP Mobile Top 10 详解**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
- **Android 渗透测试完整流程**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
- **iOS 渗透测试流程**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **移动端 MITM 测试**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **移动端自动化测试**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **移动应用渗透测试报告模板**：⚠️ 需补充 8 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **基本信息**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
  - 缺少：references
- **测试概要**：⚠️ 需补充 8 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：short
  - 缺少：references
- **漏洞详情**：⚠️ 需补充 6 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **OWASP Mobile Top 10 测试结果**：⚠️ 需补充 7 项
  - 缺少：code
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **修复建议汇总**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **附录**：⚠️ 需补充 6 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：short
- **结语**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
