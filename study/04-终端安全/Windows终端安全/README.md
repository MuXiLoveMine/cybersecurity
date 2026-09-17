# Windows终端安全

> 本文档整理自：`Windows终端安全.md`

---

## 目录

### [01. Windows 安全机制](./01_Windows 安全机制/Windows 安全机制.md)
  - 用户账户控制（UAC）
  - 地址空间随机化（ASLR）
  - 数据执行保护（DEP/NX）
  - 结构化异常处理覆盖保护（SEHOP）
  - 强制完整性控制（MIC）

### [02. Windows 安全配置基线](./02_Windows 安全配置基线/Windows 安全配置基线.md)
  - 账户策略
  - 审核策略
  - 防火墙配置

### [03. Windows 常见漏洞类型](./03_Windows 常见漏洞类型/Windows 常见漏洞类型.md)
  - 缓冲区溢出
  - 释放后使用（UAF）
  - 整数溢出

### [04. Windows 提权方法](./04_Windows 提权方法/Windows 提权方法.md)
  - 内核漏洞提权
  - 服务权限配置错误
  - 注册表权限配置错误
  - 计划任务提权
  - 令牌窃取与 AlwaysInstallElevated

### [05. Windows 横向移动](./05_Windows 横向移动/Windows 横向移动.md)
  - SMB 横向移动
  - WMI 横向移动
  - WinRM 横向移动
  - RDP 横向移动

### [06. Windows 权限维持](./06_Windows 权限维持/Windows 权限维持.md)
  - 注册表持久化
  - 服务持久化
  - 计划任务持久化
  - WMI 事件订阅持久化

### [07. Windows 恶意代码分析基础](./07_Windows 恶意代码分析基础/Windows 恶意代码分析基础.md)
  - PE 文件结构
  - 导入表分析
  - 恶意代码常见行为
  - 加壳与脱壳

### [08. Windows 应急响应流程](./08_Windows 应急响应流程/Windows 应急响应流程.md)
  - 应急响应准备
  - 事件确认与范围确定
  - 证据保全
  - 入侵分析
  - 遏制与根除
  - 恢复与总结

### [09. Windows 安全加固检查清单](./09_Windows 安全加固检查清单/Windows 安全加固检查清单.md)
  - 系统更新
  - 账户安全
  - 审核与日志
  - 网络安全
  - 服务加固
  - 注册表加固
  - UAC 配置
  - RDP 安全
  - 恶意软件防护
  - 数据保护
  - 应用安全

---

## 📊 内容审核总览

- 总章节数：9
- 待完善章节：9

### 各章节审核状态
- **Windows 安全机制**：⚠️ 需补充 3 项
  - 缺少：tools
  - 缺少：defense
  - 缺少：references
- **Windows 安全配置基线**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：attack
  - 缺少：references
- **Windows 常见漏洞类型**：⚠️ 需补充 2 项
  - 缺少：tools
  - 缺少：references
- **Windows 提权方法**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：defense
- **Windows 横向移动**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **Windows 权限维持**：⚠️ 需补充 5 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：attack
  - 缺少：references
- **Windows 恶意代码分析基础**：⚠️ 需补充 3 项
  - 缺少：commands
  - 缺少：practice
  - 缺少：references
- **Windows 应急响应流程**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **Windows 安全加固检查清单**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：tools
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：references
