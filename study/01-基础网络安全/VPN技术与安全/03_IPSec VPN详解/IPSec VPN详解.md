# IPSec VPN详解

### 2.1 IKE协商过程

IKE（Internet Key Exchange）负责在通信双方之间动态建立安全关联(SA)。IKE分两个阶段：

**IKE Phase 1（建立管理SA）：**

```
发起方(Initiator)                     响应方(Responder)
     |                                      |
     |---- SAi提案(加密算法/哈希/DH组) ----->|
     |                                      |
     |<------ SAr选择 + DH公钥 + Nonce -----|
     |                                      |
     |------- DH公钥 + Nonze + ID + AUTH -->|  (身份认证)
     |                                      |
     |<----------- AUTH + 确认 --------------|
     |                                      |
     |======= IKE SA 建立 (管理通道) ========|
```

**IKE Phase 2（建立数据SA）：**

```
     |---- HASH + SA提案(ESP/AH) + DH(可选) ->|   快速模式
     |                                      |
     |<----------- HASH + SA选择 ------------|
     |                                      |
     |======= IPSec SA 建立 (数据通道) =======|
     |                                      |
     |== ESP加密数据传输 ===>|
```

### 2.2 ESP/AH协议

**ESP（Encapsulating Security Payload）协议 - IP协议号50：**

```
ESP传输模式（主机到主机）:
[新IP头 | ESP头 | 加密(原始数据) | ESP尾 | ICV]

ESP隧道模式（站点到站点）:
[新IP头 | ESP头 | 加密(原始IP头 | 原始数据) | ESP尾 | ICV]
                          └──────受保护部分──────┘

ESP提供:
├── 机密性（加密数据载荷）
├── 完整性（HMAC/AEAD校验）
├── 认证（可选抗重放保护）
└── 抗重放（序列号+滑动窗口）
```

**AH（Authentication Header）协议 - IP协议号51：**

```
AH传输模式:
[新IP头 | AH头 | 原始IP头 | 原始数据]
           └──────完整性保护范围──────┘

AH仅提供:
├── 完整性验证
├── 数据源认证
└── 抗重放保护
（不提供加密，实际应用中常与ESP结合使用或被ESP取代）
```

**ESP vs AH对比：**

| 特性 | ESP | AH |
|------|-----|-----|
| 加密 | 支持 | 不支持 |
| 完整性 | 支持 | 支持 |
| NAT兼容 | 支持(NAT-T) | 不兼容 |
| 使用频率 | 广泛 | 较少 |

### 2.3 IPSec配置示例（StrongSwan）

**ipsec.conf 配置：**

```ini
# /etc/ipsec.conf

config setup
    charondebug="ike 2, knl 2, cfg 2"
    uniqueids=no

# 站点到站点VPN配置
conn site-to-site
    authby=secret
    auto=start
    keyexchange=ikev2

    # 左端（本端）
    left=%defaultroute
    leftid=@vpn-gateway-hq
    leftsubnet=10.1.0.0/24

    # 右端（对端）
    right=203.0.113.50
    rightid=@vpn-gateway-branch
    rightsubnet=10.2.0.0/24

    # 加密算法（IKEv2阶段1）
    ike=aes256-sha256-modp2048!
    # ESP加密算法（阶段2）
    esp=aes256gcm16!
    # DH组
    keyingtries=%forever
    ikelifetime=86400s
    lifetime=3600s
    dpdaction=restart
    dpddelay=30s
```

**ipsec.secrets 密钥配置：**

```ini
# /etc/ipsec.secrets
# PSK方式
@vpn-gateway-hq @vpn-gateway-branch : PSK "UseAStrongPreSharedKey!2024#"

# 证书方式（更安全推荐）
# : RSA "vpn-gateway-hq.key"
```

**验证与调试命令：**

```bash
# 查看SA状态
ipsec statusall

# 查看已建立的SA
ipsec status

# 重新加载配置
ipsec reload

# 重启连接
ipsec up site-to-site

# 查看详细日志
tail -f /var/log/syslog | grep charon

# 查看内核XFRM策略
ip xfrm policy
ip xfrm state
```

---

---

## 📋 内容审核与补充建议

> 针对「IPSec VPN详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
