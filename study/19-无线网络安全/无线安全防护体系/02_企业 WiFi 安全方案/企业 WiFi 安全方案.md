# 企业 WiFi 安全方案

### 2.1 WPA3-Enterprise 部署

```
WPA3-Enterprise 192-bit Mode 部署方案：

安全套件（CNSA 2.0）：
├── 加密算法: AES-256-GCM
├── 密钥交换: ECDH-P384
├── 数字签名: ECDSA-P384
├── 哈希算法: SHA-384
├── 椭圆曲线: secp384r1 (P-384)
├── 证书要求: 256 位以上安全强度
└── 随机数生成: NIST SP 800-90A 兼容

部署组件：

1. CA 基础设施
├── 根 CA: 离线根证书颁发机构
├── 中间 CA: 在线中间证书颁发机构
├── 颁发 CA: 为设备/用户颁发证书
├── CRL/OCSP: 证书吊销检查服务
└── 证书模板: 按角色定义证书模板

2. RADIUS 服务器（FreeRADIUS）

# /etc/freeradius/3.0/mods-enabled/eap
eap {
    default_eap_type = tls
    
    tls-config tls-common {
        private_key_password = ${env.RADIUS_KEY_PASSWORD}
        private_key_file = /etc/freeradius/certs/server-key.pem
        certificate_file = /etc/freeradius/certs/server-cert.pem
        ca_file = /etc/freeradius/certs/ca-chain.pem
        dh_file = /etc/freeradius/certs/dh-p384.pem
        
        # WPA3-Enterprise 192-bit 套件
        cipher_list = "ECDHE-ECDSA-AES256-GCM-SHA384"
        ecdh_curve = "secp384r1"
        
        # 证书验证
        check_crl = yes
        ca_path = /etc/freeradius/certs/
        check_all_crl = yes
        allow_expired_crl = no
    }
    
    tls {
        config_section = "tls-common"
        # 要求客户端证书
        require_client_cert = yes
    }
}

# /etc/freeradius/3.0/clients.conf
client wifi_controller {
    ipaddr = 10.10.40.0/24
    secret = ${env.RADIUS_SECRET}
    require_message_authenticator = yes
    proto = tcp  # 使用 TCP 传输更可靠
}

3. AP 配置（hostapd）

# hostapd.conf - WPA3-Enterprise
interface=wlan0
driver=nl80211
ssid=CorporateSecure

# WPA3-Enterprise
wpa=2
wpa_key_mgmt=WPA-EAP-SHA256
wpa_pairwise=CCMP-256
group=CCMP-256

# 强制 PMF
ieee80211w=2

# RADIUS 配置
auth_server_addr=10.10.40.10
auth_server_port=2083
auth_server_shared_secret=${RADIUS_SECRET}
acct_server_addr=10.10.40.10
acct_server_port=2083
acct_server_shared_secret=${RADIUS_SECRET}

# RADIUS 动态授权（COA）
radius_acct_interim_interval=300

# 安全增强
wpa_strict_rekey=1
wpa_gmk_rekey=3600
wpa_ptk_rekey=600
```

### 2.2 EAP-TLS 证书管理

```
EAP-TLS 证书管理体系：

证书层级：
├── Root CA (离线)
│   ├── RSA 4096 或 ECDSA P-384
│   ├── 有效期 20 年
│   └── 离线存储，物理安全
├── Issuing CA
│   ├── RSA 4096 或 ECDSA P-384
│   ├── 有效期 10 年
│   ├── 在线服务
│   └── 颁发设备/用户证书
└── 终端证书
    ├── 服务器证书: AP/RADIUS
    ├── 设备证书: 每台设备唯一
    └── 用户证书: 可选（双因子）

证书分发流程：

1. 设备注册
   ├── 设备通过 MDM 注册
   ├── 自动生成密钥对（设备本地）
   ├── 提交 CSR（证书签名请求）
   └── CA 颁发证书

2. 证书安装
   ├── 通过 MDM 推送证书
   ├── 配置 WiFi Profile（含 CA 证书）
   ├── 绑定设备/用户身份
   └── 设置证书 PIN/生物保护

3. 证书验证
   ├── 连接时 AP 验证设备证书
   ├── 设备验证 RADIUS 证书
   ├── CRL/OCSP 检查吊销状态
   └── 证书策略验证

4. 证书更新
   ├── 自动续期（到期前 30 天）
   ├── MDM 推送新证书
   ├── 旧证书吊销
   └── 零停机切换

证书撤销：
├── 设备丢失: 立即吊销证书
├── 员工离职: 吊销用户证书
├── 证书泄露: 吊销并重新颁发
├── CRL 更新: 每小时发布
└── OCSP 响应: 实时检查
```

### 2.3 RADIUS 高可用部署

```
RADIUS 高可用架构：

              ┌──────────────────┐
              │   负载均衡器      │
              │  (HAProxy/Keepalived)│
              └──────┬─────┬─────┘
                     │     │
              ┌──────┴─────┴──────┐
              │                   │
        ┌─────┴─────┐       ┌─────┴─────┐
        │ RADIUS-1  │       │ RADIUS-2  │
        │ (Active)  │       │ (Standby) │
        └─────┬─────┘       └─────┬─────┘
              │                   │
        ┌─────┴───────────────────┘
        │         共享后端
        ├── MySQL Cluster (主从复制)
        ├── LDAP Directory (主从复制)
        └── Redis Cache (主从复制)

FreeRADIUS 高可用配置：

# radiusd.conf - 主服务器配置
radiusd {
    # 工作线程
    max_requests = 4096
    max_workers = 32
    
    # 认证超时
    max_request_time = 30
    cleanup_delay = 5
    
    # 集群配置
    listen {
        type = auth
        ipaddr = *
        port = 2083
        proto = tcp
    }
}

# 健康检查
# /etc/freeradius/3.0/sites-available/default
server default {
    listen {
        type = auth
        ipaddr = *
        port = 2083
    }
    
    # 状态检查端点
    status_server = yes
    
    # 认证处理
    authorize {
        # 检查请求是否合法
        filter_username
        # LDAP 查询用户信息
        ldap
        # EAP 处理
        eap {
            ok = return
        }
        # 默认认证
        files
    }
    
    authenticate {
        eap
    }
    
    # 计费处理
    accounting {
        detail
        sql
    }
}

# AP 端配置多个 RADIUS 服务器
auth_server_addr=10.10.40.10    # 主 RADIUS
auth_server_port=2083
auth_server_shared_secret=secret1

# 备用 RADIUS
auth_server_addr2=10.10.40.11
auth_server_port2=2083
auth_server_shared_secret2=secret2

# 故障切换策略
radius_retry_count=3
radius_retry_interval=3
radius_dead_time=300
```

### 2.4 快速漫游安全

```
802.11 漫游安全增强：

漫游问题：
├── 漫游延迟: 标准 802.11 漫游需 100-500ms
├── 重新认证: 每次漫游需完整 802.1X 认证
├── 用户体验: 语音/视频通话中断
└── 安全风险: 漫游期间可能被劫持

802.11r - 快速 BSS 切换（FT）：
├── 预共享密钥: 漫游前预计算 PMK-R0/R1
├── 漫游时间: < 50ms
├── 认证方式: FT-PSK / FT-802.1X
└── 密钥层级:
    ├── PMK-R0: 主根密钥（由初始认证生成）
    ├── PMK-R0-ID: PMK-R0 标识
    ├── PMK-R1: 每个目标 AP 的密钥
    ├── PMK-R1-ID: PMK-R1 标识
    └── PTK: 每次关联的临时密钥

# hostapd 配置 802.11r
mobility_domain=4f00    # 移动域标识
ft_over_ds=1            # 通过 DS 域切换
ft_psk_generate_local=1 # 本地生成 PSK
pmk_r1_push=1           # 推送 PMK-R1
r0_key_lifetime=10000   # PMK-R0 生命周期
r1_key_holder=000102030405060708090a0b0c0d0e0f

802.11k - 射频资源管理：
├── 邻居报告: AP 提供邻近 AP 列表
├── 信标测量: 客户端报告信号质量
├── 信道报告: 干扰和噪声信息
└── 快速漫游辅助: 减少扫描时间

802.11v - BSS 转换管理：
├── BSS 转换请求: AP 建议客户端切换
├── DMG 操作: 定向多千兆比特操作
├── 多 BSSID: 多 SSID 共享一个 Beacon
└── 省电管理: 优化客户端睡眠

协同部署：
├── 802.11r: 快速认证
├── 802.11k: 智能选择目标 AP
├── 802.11v: 主动引导漫游
├── 802.11w: PMF 保护管理帧
└── 组合部署: 实现毫秒级安全漫游
```

---

---

## 📋 内容审核与补充建议

> 针对「企业 WiFi 安全方案」部分的内容审核结果：

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
