# Android组件安全专题

> 本文档整理自：`Android组件安全专题.md`

---

## 目录

### [01. 目录](./01_目录/目录.md)

### [02. Android安全模型概述](./02_Android安全模型概述/Android安全模型概述.md)
  - 沙箱隔离机制
  - 权限模型
  - 签名机制

### [03. Activity安全](./03_Activity安全/Activity安全.md)
  - Activity基础
  - exported属性风险
  - 隐式Intent风险
  - Task和Back Stack安全
  - Activity劫持
  - 实战漏洞案例

### [04. Service安全](./04_Service安全/Service安全.md)
  - Service基础
  - 导出Service风险
  - IntentService与JobService
  - 前台Service安全
  - 实战漏洞案例

### [05. BroadcastReceiver安全](./05_BroadcastReceiver安全/BroadcastReceiver安全.md)
  - BroadcastReceiver基础
  - 广播窃听
  - 广播伪造
  - LocalBroadcastManager
  - 实战漏洞案例

### [06. ContentProvider安全](./06_ContentProvider安全/ContentProvider安全.md)
  - ContentProvider基础
  - 数据泄露
  - SQL注入
  - 路径遍历
  - URI权限授予
  - 实战漏洞案例

### [07. Intent安全机制](./07_Intent安全机制/Intent安全机制.md)
  - 显式Intent与隐式Intent
  - PendingIntent安全
  - Intent重定向攻击
  - Intent伪造攻击

### [08. 权限强制执行](./08_权限强制执行/权限强制执行.md)
  - 自定义权限
  - 运行时权限
  - 权限保护级别

### [09. ADB调试风险](./09_ADB调试风险/ADB调试风险.md)
  - debuggable属性
  - 备份风险
  - WebView调试风险

### [10. 组件安全最佳实践](./10_组件安全最佳实践/组件安全最佳实践.md)
  - 最小暴露原则
  - 输入验证
  - 安全配置清单
  - 自动化检测工具

---

## 📊 内容审核总览

- 总章节数：10
- 待完善章节：10

### 各章节审核状态
- **目录**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：defense
  - 缺少：references
- **Android安全模型概述**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Activity安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **Service安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：references
- **BroadcastReceiver安全**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：references
- **ContentProvider安全**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **Intent安全机制**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **权限强制执行**：⚠️ 需补充 7 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **ADB调试风险**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
- **组件安全最佳实践**：⚠️ 需补充 5 项
  - 缺少：commands
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
