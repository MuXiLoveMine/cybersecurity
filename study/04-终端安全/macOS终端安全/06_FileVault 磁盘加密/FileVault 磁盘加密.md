# FileVault 磁盘加密

### 6.1 FileVault 2 原理

FileVault 2 引入于 Mac OS X 10.7（Lion），使用 XTS-AES-128 加密算法对整个磁盘进行全盘加密。

**加密原理**

```
XTS-AES-128（XEX-based Tweaked-codebook mode with ciphertext Stealing）

  ┌─────────────────────────────────────────┐
  │  密钥结构                                │
  │  ├─ 数据加密密钥（DEK）：AES-256        │
  │  │   用于实际数据加密                     │
  │  ├─ 卷主密钥（VMK）：包装 DEK            │
  │  │   由用户密码/恢复密钥包装              │
  │  └─ 硬件密钥（T2/Secure Enclave）       │
  │      包装 VMK，绑定硬件                  │
  └─────────────────────────────────────────┘

加密流程：
  1. 用户密码 → PBKDF2 派生 → 密钥包装密钥
  2. 密钥包装密钥 → 解密 → 卷主密钥（VMK）
  3. VMK → 解密 → 数据加密密钥（DEK）
  4. DEK + XTS 模式 → 实时加解密磁盘扇区
  5. 硬件密钥绑定 → 仅在原硬件上可解密 VMK
```

**FileVault 状态管理**

```bash
# 查看 FileVault 状态
fdesetup status
# 输出：FileVault is On.（或 Off.）

# 查看已授权解锁用户
fdesetup list

# 启用 FileVault
sudo fdesetup enable
# 此命令会生成恢复密钥并开始加密

# 禁用 FileVault（解密过程，耗时较长）
sudo fdesetup disable

# 添加解锁用户
sudo fdesetup add -usertoadd username

# 导出恢复密钥信息
sudo fdesetup changerecovery -personal
```

### 6.2 恢复密钥管理

**恢复密钥类型**

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| 个人恢复密钥 | 由系统生成，用户保管 | 个人用户 |
| 机构恢复密钥 | 由 MDM 管理员生成和托管 | 企业环境 |
| iCloud 恢复 | 存储在 iCloud 钥匙串 | 个人用户（可选） |

**企业环境恢复密钥管理**

```bash
# MDM 下启用 FileVault 并托管机构密钥
# 通过 Configuration Profile 部署：
# PayloadType: com.apple.security.FDE
# PayloadContent:
#   ShowRecoveryKey: true  ← 显示恢复密钥给用户
#   RecoveryKeyEscrow:
#     URL: https://mdm.example.com/escrow  ← 托管地址
#   DestroyFVKeyOnStandby: true  ← 待机时销毁密钥

# 使用 fdesetup 在 MDM 环境中生成密钥文件
sudo fdesetup enable -outputplist /tmp/fv_key.plist
# 输出文件包含恢复密钥和加密信息
```

### 6.3 FileVault 与硬件安全

**T2 芯片 / Secure Enclave 的作用**

```
Apple T2 / M系列芯片安全架构：
┌──────────────────────────────────────┐
│  Secure Enclave（安全隔区）           │
│  ├─ 硬件密钥存储（不可导出）          │
│  ├─ UID（设备唯一标识符）             │
│  └─ 密钥派生与包装                    │
├──────────────────────────────────────┤
│  启动安全性                           │
│  ├─ Secure Boot Chain                 │
│  ├─ Kernel Integrity                  │
│  └─ 签名系统卷（SSV）                 │
├──────────────────────────────────────┤
│  FileVault 集成                      │
│  ├─ 硬件绑定（VMK 绑定到芯片）         │
│  ├─ 密钥不可提取                      │
│  └─ 离机解锁需要恢复密钥              │
├──────────────────────────────────────┤
│  Touch ID / 指纹                      │
│  └─ 指纹验证解锁 FileVault            │
└──────────────────────────────────────┘
```

### 6.4 磁盘加密攻击与防御

| 攻击方式 | 原理 | 防御建议 |
|----------|------|----------|
| 冷启动攻击 | 从内存中提取密钥 | 设置短超时锁屏，启用 DestroyFVKeyOnStandby |
| 恶意 DMA | 通过 Thunderbolt/USB-C 进行 DMA 内存读取 | 禁用未授权的 Thunderbolt 设备，启用内核扩展限制 |
| 密码暴力破解 | 离线破解用户密码 | 设置强密码，增加 PBKDF2 迭代次数 |
| 恢复密钥泄露 | 恢复密钥保管不当 | 使用 MDM 托管，密钥加密存储 |
| 固件攻击 | 修改 EFI/ROM | Secure Boot 验证固件完整性 |
| 物理提取 | 拆硬盘到其他机器读取 | 硬件绑定（T2/M 芯片），不可离机解密 |

```bash
# 配置安全超时（锁屏后销毁 FileVault 密钥）
sudo fdesetup changesetting -DestroyFVKeyOnStandby true

# 配置系统待机延迟（减少密钥在内存中的时间）
sudo pmset -a standbydelayhigh 900   # 高电量待机延迟 15 分钟
sudo pmset -a standbydelaylow 300    # 低电量待机延迟 5 分钟
```

---

---

## 📋 内容审核与补充建议

> 针对「FileVault 磁盘加密」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
