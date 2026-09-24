# WiFi 防御措施

### 4.1 WPA3 部署

```
WPA3 部署指南：

迁移策略：
├── 评估现有设备兼容性
├── 优先升级 AP 固件支持 WPA3
├── 使用 WPA3/WPA2 过渡模式
│   ├── 同时支持 WPA2 和 WPA3
│   ├── 新设备使用 WPA3
│   └── 旧设备回退 WPA2
├── 逐步淘汰不支持 WPA3 的旧设备
└── 最终切换到纯 WPA3 模式

WPA3-Personal 配置（hostapd）：
# hostapd.conf
ssid=SecureNetwork
wpa=2                    # 或 wpa=3 同时支持 WPA2
wpa_key_mgmt=SAE         # WPA3 Personal
sae_password=MyPassword  # WPA3 密码
ieee80211w=2             # 强制 PMF
sae_groups=19 20 21      # 支持的椭圆曲线组
# 19 = P-256, 20 = P-384, 21 = P-521

WPA3-Enterprise 配置：
ssid=EnterpriseNetwork
wpa=2
wpa_key_mgmt=WPA-EAP-SHA256  # 192-bit mode
ieee80211w=2                  # 强制 PMF
eap_server=1
eap_user_file=/etc/hostapd/eap_users
ca_cert=/etc/hostapd/ca.pem
server_cert=/etc/hostapd/server.pem
private_key=/etc/hostapd/server.key
# 192-bit 安全套件
openssl_ciphers=SUITEB192

OWE 配置（开放网络加密）：
ssid=OpenNetwork
wpa=2
wpa_key_mgmt=OWE
ieee80211w=2
# 过渡模式（同时支持开放和 OWE）
owe_transition_ssid=OpenNetwork
owe_transition_bssid=00:11:22:33:44:55
```

### 4.2 企业级 802.1X

```
企业级 WiFi 认证方案：

架构组件：
├── Supplicant: 客户端设备
├── Authenticator: AP / 控制器
└── Authentication Server: RADIUS 服务器

EAP 方法对比：

EAP-TLS（推荐）：
├── 双向证书认证
├── 安全性最高
├── 需要管理客户端证书
├── 适合企业环境
└── 适用于高安全要求场景

PEAP-MSCHAPv2（常用）：
├── 服务器端证书 + 用户名密码
├── 部署较简单
├── 易受 Evil Twin 攻击
├── 客户端需验证服务器证书
└── 中等安全性

EAP-TTLS：
├── 类似 PEAP
├── 支持多种内层认证
└── 灵活性更高

EAP-SIM/AKA：
├── 使用 SIM 卡认证
├── 适用于移动运营商网络
└── 需要特殊硬件

FreeRADIUS 配置示例：
# /etc/freeradius/3.0/clients.conf
client wifi_ap {
    ipaddr = 192.168.1.0/24
    secret = shared_secret_key
    require_message_authenticator = yes
}

# /etc/freeradius/3.0/mods-enabled/eap
eap {
    default_eap_type = tls
    tls-config tls-common {
        private_key_file = /etc/freeradius/certs/server.key
        certificate_file = /etc/freeradius/certs/server.pem
        ca_file = /etc/freeradius/certs/ca.pem
        cipher_list = "DEFAULT"
        ecdh_curve = "secp384r1"
    }
    tls {
        config_section = "tls-common"
    }
    peap {
        default_eap_type = mschapv2
        copy_request_to_tunnel = yes
        use_tunneled_reply = yes
    }
}

# /etc/freeradius/3.0/users
# EAP-TLS 用户（基于证书）
"client-cert" TLS-Client-Cert-Subject == "CN=client-device" {
    Auth-Type = Accept
}

# PEAP 用户（用户名密码）
"user1" Cleartext-Password := "secure_password_123" {
    MS-CHAP-Use-NTLM-Auth = 0
}
```

### 4.3 WIDS/WIPS 部署

```
企业级 WIDS/WIPS 部署方案：

部署架构：
├── 传感器层: 专用无线传感器分布部署
├── 分析引擎: 集中式流量分析和威胁检测
├── 管理平台: 统一管理和告警
└── 集成接口: SIEM/NAC 集成

检测能力清单：
├── Rogue AP 检测
│   ├── 对比授权 AP 白名单
│   ├── 检测有线侧桥接
│   └── 自动分类和告警
├── Evil Twin 检测
│   ├── BSSID/SSID 冲突检测
│   ├── 信道异常检测
│   └── 信号强度异常
├── 无线钓鱼 AP
│   ├── 相似 SSID 检测
│   └── Captive Portal 检测
├── Ad-hoc 网络检测
├── 无线桥接检测
├── MAC 欺骗检测
├── Deauth 攻击检测
├── 未授权设备探测
└── 无线策略违规

响应能力：
├── 主动抑制: 发送 Deauth 切断非法连接
├── 自动定位: 三角定位非法设备
├── 端口关闭: 联动交换机关闭 Rogue AP 端口
├── 告警通知: 邮件/短信/SIEM
└── 取证记录: 保存无线流量用于取证

开源方案 - Kismet WIDS：
# Kismet 配置
source=wlan0:type=linuxwifi
alert_seqnum=true
detect_fakemac=true
deny_unique_mac_change=true
# 配置 Rogue AP 白名单
apcsvfile=/etc/kismet/known_aps.csv
# 告警配置
alert_emails=security@company.com
alert_smtp_server=smtp.company.com
```

### 4.4 MAC 白名单局限性

```
MAC 地址白名单分析：

工作原理：
├── AP 维护允许的 MAC 地址列表
├── 仅允许列表中的 MAC 关联
├── 通常作为附加安全层
└── 常被误认为是有效的安全措施

局限性分析：
├── MAC 地址在空中明文传输
│   └── 监听即可获得合法 MAC
├── MAC 地址可伪造
│   ├── Linux: ip link set dev wlan0 address XX:XX:XX:XX:XX:XX
│   ├── macOS: ifconfig wlan0 ether XX:XX:XX:XX:XX:XX
│   └── Windows: 注册表修改或专用工具
├── 管理开销大
│   ├── 需要维护 MAC 列表
│   ├── 设备更换需更新列表
│   └── 不适合大规模部署
├── 不提供加密保护
│   └── 即使 MAC 验证通过，数据仍需 WPA 加密
└── 无法防止 Rogue AP
    └── 攻击者可克隆合法 AP 的 MAC

正确使用方式：
├── 作为辅助安全层，不作为主要防护
├── 结合 802.1X 进行设备认证
├── 配合 NAC 进行设备合规检查
├── 使用设备指纹（不止 MAC）进行识别
└── 定期审计 MAC 白名单
```

---

---

