# Windows 域环境基础

### 2.1 Active Directory 架构

**AD 核心组件**
- 域控制器（DC）：存储 AD 数据库
- 全局目录（GC）：全局目录服务器
- FSMO 角色：域级和林级操作主机
- 站点（Site）：网络拓扑表示
- 组织单元（OU）：域内容器
- 组策略（GPO）：策略下发

**AD 关键对象**
- 用户对象：域用户、服务账户、计算机账户
- 组对象：安全组、通讯组
- 计算机对象：域加入机器
- 服务账户：运行服务的域账户

### 2.2 Kerberos 认证机制

**Kerberos 认证流程**
```
阶段1: AS-REQ / AS-REP（认证服务交换）
├── 客户端 → KDC: 发送 AS-REQ（包含预加密的用户哈希）
└── KDC → 客户端: 返回 AS-REP（包含 TGT 和 Session Key）

阶段2: TGS-REQ / TGS-REP（票据授权服务交换）
├── 客户端 → KDC: 发送 TGS-REQ（TGT + 请求的服务 SPN）
└── KDC → 客户端: 返回 TGS-REP（包含 ST 和服务 Session Key）

阶段3: AP-REQ / AP-REP（应用服务交换）
├── 客户端 → 服务: 发送 AP-REQ（ST + 认证符）
└── 服务 → 客户端: 返回 AP-REP（可选双向认证）
```

**Kerberos 攻击面**
- AS-REP Roasting：离线爆破 AS-REP 响应
- Kerberoasting：离线爆破 TGS-REP 响应
- 黄金票据（Golden Ticket）：伪造 TGT
- 白银票据（Silver Ticket）：伪造 TGS
- Pass the Key / Overpass the Hash：使用 AES 密钥获取 TGT
- DCSync：模拟 DC 同步凭据

### 2.3 NTLM 认证机制

**NTLM 认证流程**
```
1. 协商: 客户端 → 服务器（协商消息）
2. 挑战: 服务器 → 客户端（挑战消息，含随机 Challenge）
3. 认证: 客户端 → 服务器（使用 NTLM Hash 加密 Challenge）
```

**NTLM 攻击面**
- Pass the Hash：使用 NTLM Hash 认证
- NTLM Relay：中继 NTLM 认证
- 离线破解 NTLM Hash

---

---

