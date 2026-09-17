# Passkey 技术

### 3.1 Passkey 概念

Passkey 是基于 FIDO2 标准的**可同步的公钥凭据**，用户可在不同设备上使用同一组凭据。

**Passkey vs 传统FIDO2凭据：**

| 特性 | 传统FIDO2凭据 | Passkey |
|------|--------------|---------|
| 同步 | 设备绑定 | 跨设备云端同步 |
| 恢复 | 设备丢失则丢失 | 可通过云账号恢复 |
| 多设备 | 每设备独立密钥 | 同步共享密钥对 |
| Backup | 无备份 | 加密云备份 |
| BE/BS Flag | 无 | 有（Backup Eligible/State） |
| 用户体验 | 需每设备注册 | 注册一次，多设备可用 |

### 3.2 Apple Passkey 实现

Apple 在 iOS 16 和 macOS Ventura 中引入 Passkey，通过 iCloud Keychain 实现端到端加密同步。

```
Apple Passkey 同步流程：

1. 注册Passkey（iPhone上）
   └── 认证器生成密钥对
   └── 私钥用设备密码派生密钥加密
   └── 加密后上传至iCloud Keychain（E2E加密）
   └── 设置 BE=1（Backup Eligible），BS=1（Backup State）

2. 同步到其他设备（iPad）
   └── iPad解锁后拉取iCloud Keychain
   └── 用设备密码派生密钥解密
   └── 本地安全区存储私钥

3. 认证时
   └── 网站请求navigator.credentials.get()
   └── iPad作为平台认证器响应
   └── Touch ID验证用户
   └── 私钥签名Challenge
```

**安全性分析：**
- iCloud Keychain 使用端到端加密，Apple 无法访问私钥
- 依赖设备密码和硬件密钥（Secure Enclave）保护
- 设备间通过加密通道传输，不经过 Apple 服务器明文

### 3.3 Google Passkey 实现

Google 通过 Google Password Manager 同步 Passkey 到 Android 设备和 Chrome 浏览器。

```
Google Passkey 同步流程：

1. Android设备注册Passkey
   └── Google Play Services FIDO2 API
   └── 密钥对存储在设备安全区域
   └── 加密同步至Google Password Manager

2. 跨设备使用
   └── 通过手机蓝牙扫码（hybrid transport）
   └── 手机作为漫游认证器为电脑认证
   └── 或Chrome浏览器直接同步凭据

3. 安全特性
   └── 同步数据E2E加密（基于Google账号密码）
   └── 屏幕锁验证后才可使用
   └── 支持远程删除设备凭据
```

### 3.4 Microsoft Passkey 实现

Microsoft 通过 Windows Hello 和 Microsoft Account 实现 Passkey 同步：

```
Microsoft Passkey 生态：

Windows 11 (Build 23H2+)：
  └── Windows Hello平台认证器生成Passkey
  └── 同步至Microsoft Account
  └── 支持Android/iOS设备通过Phone Link使用

工作流：
  ┌──────────┐    Microsoft    ┌──────────┐
  │ Windows  │   Account Sync  │  Phone   │
  │ Hello    │←──────────────→│  Link    │
  └──────────┘                 └──────────┘
       │                            │
       └── Passkey存储于TPM 2.0     └── 通过hybrid transport桥接
```

### 3.5 跨平台 Passkey 互操作

2023年 FIDO 联盟发布 Credential Exchange Protocol 草案，支持跨生态 Passkey 导出和导入：

```
跨平台Passkey迁移场景：

用户从iPhone换到Android手机：
  1. iPhone导出Passkey（扫描二维码建立BLE+TLS通道）
  2. QR码包含：origin、nonce、BLE标识
  3. Android扫描后建立安全通道
  4. iPhone逐个传输Passkey（含credentialId、私钥、RP ID）
  5. 传输使用ECDH密钥协商+AEAD加密
  6. 传输后iPhone端可选择保留或删除原Passkey
  7. 新Passkey在Android安全区域存储
```

---

---

## 📋 内容审核与补充建议

> 针对「Passkey 技术」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
