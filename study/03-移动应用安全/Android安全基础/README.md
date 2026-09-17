# Android安全基础

> 本文档整理自：`Android安全基础.md`

---

## 目录

### [01. Android 系统架构](./01_Android 系统架构/Android 系统架构.md)
  - 四层架构详解
  - 系统启动流程

### [02. 四大组件安全](./02_四大组件安全/四大组件安全.md)
  - Activity 组件安全
  - Service 组件安全
  - BroadcastReceiver 组件安全
  - ContentProvider 组件安全
  - Intent 注入漏洞

### [03. Android 权限机制](./03_Android 权限机制/Android 权限机制.md)
  - 权限分类
  - 危险权限分组（运行时权限）
  - 权限声明
  - 运行时权限申请（代码示例）
  - 权限提升漏洞

### [04. APK 文件结构详解](./04_APK 文件结构详解/APK 文件结构详解.md)
  - APK 整体结构
  - 各文件详细说明

### [05. Android 签名机制](./05_Android 签名机制/Android 签名机制.md)
  - v1 签名（JAR 签名）
  - v2 签名（APK Signature Scheme v2）
  - v3 签名（APK Signature Scheme v3）
  - 签名验证优先级
  - 实际操作示例
  - 签名绕过与二次打包

### [06. 沙箱与 SELinux](./06_沙箱与 SELinux/沙箱与 SELinux.md)
  - Android 沙箱机制
  - SELinux 基础
  - 沙箱绕过

### [07. 数据存储安全](./07_数据存储安全/数据存储安全.md)
  - SharedPreferences 安全
  - 文件存储安全
  - SQLite 数据库安全
  - 硬编码敏感信息
  - 日志泄露

### [08. 通信安全](./08_通信安全/通信安全.md)
  - HTTPS 与证书校验
  - 常见证书校验漏洞
  - SSL Pinning（证书固定）
  - 抓包检测与对抗

### [09. 代码混淆与加固](./09_代码混淆与加固/代码混淆与加固.md)
  - 代码混淆（ProGuard / R8）
  - 应用加固
  - 防调试与反调试

### [10. WebView 安全](./10_WebView 安全/WebView 安全.md)
  - WebView 常见漏洞
  - WebView 安全配置

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **Android 系统架构**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **四大组件安全**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **Android 权限机制**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：references
- **APK 文件结构详解**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **Android 签名机制**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **沙箱与 SELinux**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **数据存储安全**：⚠️ 需补充 3 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **通信安全**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：defense
- **代码混淆与加固**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **WebView 安全**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：defense
  - 缺少：references
