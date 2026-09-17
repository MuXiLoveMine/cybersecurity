# macOS vs Windows 安全对比

### 11.1 安全模型对比

| 维度 | macOS | Windows |
|------|-------|---------|
| **权限提升** | sudo（需管理员密码） | UAC（需用户确认） |
| **系统保护** | SIP（rootless） | TrustedInstaller + PatchGuard |
| **代码执行控制** | Gatekeeper + Notarization（强制公证） | SmartScreen + AppLocker（可选） |
| **沙箱** | App Sandbox（seatbelt） | AppContainer + WDAG |
| **隐私控制** | TCC（统一权限管理） | 隐私设置（逐应用控制） |
| **磁盘加密** | FileVault 2（XTS-AES-128） | BitLocker（XTS-AES-128/256） |
| **恶意软件防护** | XProtect + MRT（特征匹配） | Windows Defender（行为+ML+云） |
| **签名验证** | 代码签名 + 公证（Apple 信任链） | Authenticode（CA 信任链） |
| **启动安全** | Secure Boot + SSV | Secure Boot + Measured Boot |
| **内核保护** | KASLR + Kext 验证 | KASLR + PatchGuard + DSE |

### 11.2 威胁场景对比

| 威胁 | macOS 典型场景 | Windows 典型场景 |
|------|----------------|------------------|
| **恶意软件感染** | 伪装合法应用、伪造更新（Shlayer） | 宏文档、漏洞利用工具包、PE 感染 |
| **持久化** | LaunchAgent/Daemon、登录项 | Run 键、计划任务、服务、WMI |
| **提权** | 利用 SIP 漏洞、sudo 配置缺陷 | UAC 绕过、内核漏洞、令牌窃取 |
| **横向移动** | SSH、屏幕共享、AppleScript | SMB/RDP/WMI/PsExec |
| **数据外泄** | iCloud 同步、AirDrop | SMB 传输、云同步 |
| **网络钓鱼** | 伪造登录页面窃取 Apple ID | 伪造登录页面窃取 AD 凭据 |
| **供应链攻击** | Xcode 项目植入（XCSSET） | DLL 劫持、MSI 包篡改 |

### 11.3 企业管理对比

| 维度 | macOS | Windows |
|------|-------|---------|
| **管理协议** | MDM（APN 推送） | GPO（LDAP/SMB）、MDM（Intune） |
| **管理工具** | JAMF Pro、Profile Manager、Mosyle | GPO、SCCM、Intune、PDQ Deploy |
| **配置分发** | Configuration Profile（.mobileconfig） | Group Policy（.admx）、MSI |
| **合规审计** | JAMF Compliance Reporter、CIS Benchmark | GPO Audit、CIS Benchmark、Nessus |
| **补丁管理** | softwareupdate、JAMF Patch Management | WSUS、SCCM、Intune Update |
| **设备注册** | DEP（Device Enrollment Program） | Autopilot、DEP |
| **身份认证** | Apple ID、企业 Kerberos、SmartCard | Active Directory、Azure AD、SmartCard |
| **应用分发** | VPP（Volume Purchase Program）、Self Service | SCCM、Microsoft Store for Business |

### 11.4 综合安全建议

```
macOS 企业安全最佳实践总结：

第一层：硬件与启动安全
├─ 启用 Secure Boot（Full Security）
├─ 启用 FileVault 2 全盘加密
├─ 托管恢复密钥到 MDM
└─ 配合 T2/Secure Enclave 硬件绑定

第二层：系统安全机制
├─ 启用 SIP（默认开启，禁止禁用）
├─ 启用 Gatekeeper（仅允许 App Store + Developer ID）
├─ 启用 Notarization 验证
├─ 保持 XProtect/MRT 自动更新
└─ 启用 ALF 防火墙 + 隐身模式

第三层：访问控制
├─ 标准用户日常使用（非 admin）
├─ 配置 sudo 超时和命令限制
├─ TCC 权限最小化
├─ 禁用不必要的共享服务（SSH/AFP/SMB）
└─ 配置密码策略和账户锁定

第四层：企业管控
├─ MDM 注册和策略分发
├─ CIS Benchmark 基线合规
├─ 自动补丁管理
├─ 部署 EDR 解决方案
└─ 统一日志收集与 SIEM 集成

第五层：应急准备
├─ 建立 IR 工具清单和流程
├─ 定期备份（Time Machine + 云备份）
├─ 制定数据恢复计划
├─ 定期安全审计和渗透测试
└─ 安全意识培训
```

---

---

## 📋 内容审核与补充建议

> 针对「macOS vs Windows 安全对比」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
