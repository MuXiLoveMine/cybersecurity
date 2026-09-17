# 红队终端对抗技术

> 本文档整理自：`红队终端对抗技术.md`

---

## 目录

### [01. 权限提升技术](./01_权限提升技术/权限提升技术.md)
  - Windows 提权
  - Linux 提权
  - 提权信息收集自动化

### [02. 进程注入与迁移](./02_进程注入与迁移/进程注入与迁移.md)
  - Windows 进程注入
  - Linux 进程注入

### [03. 持久化技术](./03_持久化技术/持久化技术.md)
  - Windows 持久化
  - Linux 持久化

### [04. 红队终端检测绕过（EDR Bypass）](./04_红队终端检测绕过（EDR Bypass）/红队终端检测绕过（EDR Bypass）.md)
  - AMSI 绕过
  - PowerShell 安全日志绕过
  - 直接系统调用（Syscall）
  - Living off the Land（LOTL）
  - LOLBins 利用
  - 内存执行无文件攻击
  - 混淆与加密 Shellcode
  - C2 框架检测绕过思路

### [05. 凭证获取技术](./05_凭证获取技术/凭证获取技术.md)
  - Windows 凭据
  - Linux 凭据

### [06. 横向移动基础](./06_横向移动基础/横向移动基础.md)
  - Pass-the-Hash（PTH）
  - Pass-the-Ticket（PTT）
  - Overpass-the-Hash
  - 远程执行技术
  - PsExec/WMIC/DCOM 利用

### [07. 防御视角与检测](./07_防御视角与检测/防御视角与检测.md)
  - Windows 日志审计关键事件 ID
  - Sysmon 配置与检测规则
  - Sigma 规则编写
  - 检测提权/持久化/横向移动的日志特征
  - Python 日志分析脚本示例

### [08. 总结](./08_总结/总结.md)

---

## 📊 内容审核总览

- 总章节数：8
- 待完善章节：8

### 各章节审核状态
- **权限提升技术**：⚠️ 需补充 1 项
  - 缺少：practice
- **进程注入与迁移**：⚠️ 需补充 2 项
  - 缺少：practice
  - 缺少：references
- **持久化技术**：⚠️ 需补充 4 项
  - 缺少：tools
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **红队终端检测绕过（EDR Bypass）**：⚠️ 需补充 2 项
  - 缺少：code
  - 缺少：practice
- **凭证获取技术**：⚠️ 需补充 1 项
  - 缺少：practice
- **横向移动基础**：⚠️ 需补充 5 项
  - 缺少：code
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **防御视角与检测**：⚠️ 需补充 4 项
  - 缺少：knowledge
  - 缺少：practice
  - 缺少：defense
  - 缺少：references
- **总结**：⚠️ 需补充 4 项
  - 缺少：code
  - 缺少：tools
  - 缺少：practice
  - 缺少：references
