# Active Directory 基础

### 1.1 AD 架构概述

**Active Directory** 是微软开发的目录服务，存储网络对象（用户、计算机、组等）信息，提供认证与授权服务。

**核心逻辑结构**：

```
林（Forest）── 根域 corp.local
  │
  ├── 域（Domain）corp.local
  │     ├── OU：Servers
  │     │     ├── 计算机对象：SRV-01
  │     │     └── 计算机对象：SRV-02
  │     ├── OU：Workstations
  │     │     └── 计算机对象：PC-001
  │     └── 用户容器：Users
  │           ├── 用户：admin
  │           └── 组：Domain Admins
  │
  └── 子域 child.corp.local（可选）
```

| 结构 | 说明 |
|------|------|
| **林（Forest）** | AD 最高容器，包含一个或多个共享架构和全局编录的域 |
| **域（Domain）** | 安全边界，独立管理用户/计算机/策略 |
| **OU（Organizational Unit）** | 域内组织单元，用于委派管理与组策略应用 |
| **站点（Site）** | 物理网络拓扑映射，优化复制和客户端登录 |

**关键概念**：
- **全局编录（GC）**：跨域搜索的索引，存储所有域对象的部分属性
- **FSMO 角色**：5 种灵活单主机操作角色（Schema Master、Domain Naming Master、RID Master、PDC Emulator、Infrastructure Master）
- **域功能级别**：决定可用功能与兼容性（2008R2 / 2012R2 / 2016 / 2019+）

### 1.2 域控制器与复制

**域控制器（DC）**：运行 AD DS 的服务器，存储域目录分区数据，处理认证请求。

**复制拓扑**：
- **站内复制（Intra-site）**：变更通知触发，低延迟（约15秒）
- **站间复制（Inter-site）**：按计划间隔（默认15-180分钟），压缩传输
- **多主机复制**：任何 DC 可写入变更，再同步到其他 DC（除 FSMO 单主机角色外）

```
# 查看域控复制状态
repadmin /showrepl
repadmin /replsummary
repadmin /syncall /A /d /e

# 查看域控信息
nltest /dsgetdc:corp.local
nltest /dclist:corp.local
```

### 1.3 LDAP 协议基础

**LDAP（轻量目录访问协议）**：TCP/389（明文）或 636（LDAPS/SSL），用于查询和修改 AD 数据。

**AD 目录信息树（DIT）结构**：

```
DC=corp,DC=local                      ← 域根
  ├── CN=Users                         ← 默认用户容器
  │     ├── CN=Administrator
  │     └── CN=Guest
  ├── OU=Servers                      ← 自定义OU
  │     └── CN=SRV-01
  ├── CN=Configuration                ← 配置分区
  └── CN=Schema                       ← 架构分区
```

**常用 LDAP 查询命令**：

```bash
# 使用 ldapsearch 查询域用户
ldapsearch -x -H ldap://dc01.corp.local \
  -D "admin@corp.local" -W \
  -b "DC=corp,DC=local" \
  "(objectCategory=user)" sAMAccountName memberOf

# 查询域管组
ldapsearch -x -H ldap://dc01.corp.local \
  -D "admin@corp.local" -W \
  -b "CN=Domain Admins,CN=Users,DC=corp,DC=local" member
```

### 1.4 Kerberos 认证流程详解

Kerberos 是 AD 的核心认证协议，基于票据（Ticket）的对称密钥体系。

**三方角色**：客户端（Client）、密钥分发中心（KDC，位于DC中）、服务（Service）

```
┌────────┐         ┌─────────────────┐         ┌─────────┐
│ Client │         │  KDC (域控内)    │         │ Service │
│        │         │  ┌───┐ ┌──────┐ │         │         │
│        │         │  │AS │ │ TGS  │ │         │         │
└───┬────┘         │  └───┘ └──────┘ │         └────┬────┘
    │              └────────┬────────┘              │
    │     ① AS-REQ          │                        │
    │ ────────────────────> │                        │
    │                       │                        │
    │     ② AS-REP          │                        │
    │ <──────────────────── │                        │
    │   (TGT + 会话密钥)     │                        │
    │                       │                        │
    │     ③ TGS-REQ         │                        │
    │ ────────────────────> │                        │
    │                       │                        │
    │     ④ TGS-REP         │                        │
    │ <──────────────────── │                        │
    │   (ST + 服务会话密钥)  │                        │
    │                       │                        │
    │     ⑤ AP-REQ          │                        │
    │ ────────────────────────────────────────────> │
    │     (ST + 认证符)      │                        │
    │                       │                        │
    │     ⑥ AP-REP (可选)    │                        │
    │ <──────────────────────────────────────────── │
```

**六步详解**：

| 步骤 | 名称 | 说明 |
|------|------|------|
| ① AS-REQ | 认证服务请求 | 客户端向 KDC 的 AS 发送预认证数据（用用户密码哈希加密的时间戳） |
| ② AS-REP | 认证服务响应 | AS 验证后返回 TGT（票据授予票据），用 krbtgt 账户哈希加密 |
| ③ TGS-REQ | 票据授予服务请求 | 客户端用 TGT 向 TGS 请求特定服务的票据（ST） |
| ④ TGS-REP | 票据授予服务响应 | TGS 返回 ST（服务票据），用服务账户哈希加密 |
| ⑤ AP-REQ | 应用请求 | 客户端向服务提交 ST 和认证符 |
| ⑥ AP-REP | 应用响应 | 服务验证 ST 后建立会话 |

**关键概念**：
- **TGT**：存储在客户端内存中，用 `krbtgt` 账户哈希加密，有效期默认10小时
- **PAC（Privilege Attribute Certificate）**：嵌入票据中的授权数据，包含用户SID和组成员关系
- **krbtgt 账户**：域内最关键的账户，其哈希用于加解密所有 TGT

### 1.5 NTLM 认证流程与缺陷

**NTLM（NT LAN Manager）** 是 Kerberos 的后备认证协议，在无法使用 Kerberos 时触发。

```
┌────────┐                           ┌─────────┐
│ Client │                           │   DC    │
└───┬────┘                           └────┬────┘
    │  ① Negotiate（协商）                 │
    │ ─────────────────────────────────> │
    │                                     │
    │  ② Challenge（16字节随机数）          │
    │ <───────────────────────────────── │
    │                                     │
    │  ③ Response（用密码哈希加密Challenge）│
    │ ─────────────────────────────────> │
    │                                     │
    │  ④ Authenticated                   │
    │ <───────────────────────────────── │
```

**NTLM 缺陷**：
- **无相互认证**：客户端无法验证服务器身份
- **离线破解友好**：响应中包含密码哈希衍生值，可离线爆破
- **已弃用**：微软从 Windows 11 22H2 起默认禁用 NTLM

```bash
# NTLM Hash 格式（存储在 NTDS.dit / SAM 中）
# 用户名:RID:LM哈希:NT哈希
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

# Mimikatz 抓取 NTLM 哈希（红队视角，仅用于授权测试）
mimikatz # sekurlsa::logonpasswords
mimikatz # lsadump::sam
```

---

---

## 📋 内容审核与补充建议

> 针对「Active Directory 基础」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
