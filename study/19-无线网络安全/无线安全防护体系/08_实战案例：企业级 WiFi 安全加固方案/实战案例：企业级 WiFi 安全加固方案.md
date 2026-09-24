# 实战案例：企业级 WiFi 安全加固方案

### 8.1 项目背景

```
项目概况：

客户: 某大型企业（2000+ 员工，5 栋办公楼）
问题: 现有 WiFi 网络安全评估发现多个问题
目标: 全面加固企业 WiFi 安全

现有问题清单：
├── 使用 WPA2-PSK 共享密码（3年未更换）
├── 员工和访客使用同一 SSID
├── 无 802.1X 认证
├── 无 WIDS/WIPS 部署
├── AP 固件版本过旧
├── WPS 功能未禁用
├── 管理员密码为默认值
├── 无客户端隔离
├── 管理接口可通过无线访问
└── 无安全监控和告警
```

### 8.2 加固方案设计

```
加固方案架构：

┌─────────────────────────────────────────────────┐
│                  互联网                          │
├─────────────────────────────────────────────────┤
│              下一代防火墙                        │
├─────────┬──────────┬──────────┬─────────────────┤
│ VLAN 10 │ VLAN 20  │ VLAN 30  │   VLAN 99       │
│ 员工网   │ 访客网    │ IoT网    │   安管网        │
│ WPA3-   │ Portal   │ WPA3-   │   WIDS/WIPS     │
│ Ent     │ 认证     │ Personal │   传感器        │
│ EAP-TLS │ 短信验证 │ SAE     │                 │
├─────────┴──────────┴──────────┴─────────────────┤
│            WLC (主备冗余)                        │
├─────────────────────────────────────────────────┤
│    RADIUS集群 (主备) + CA基础设施 + SIEM        │
└─────────────────────────────────────────────────┘
```

### 8.3 实施步骤

```
分阶段实施计划：

阶段1: 基础设施准备（第1-2周）

1.1 VLAN 规划和配置
# 核心交换机配置
# VLAN 10 - 员工
interface vlan10
  description Employee-WiFi
  ip address 10.10.10.1 255.255.255.0
  ip access-group apply employee-acl in
  
# VLAN 20 - 访客
interface vlan20
  description Guest-WiFi
  ip address 10.10.20.1 255.255.255.0
  ip access-group apply guest-acl in
  
# ACL: 访客仅允许上网，禁止内网
ip access-list extended guest-acl
  permit tcp any any eq 80 443
  permit udp any any eq 53
  deny ip any 10.10.0.0 255.255.0.0
  permit ip any any

1.2 CA 基础设施搭建
# OpenSSL 创建 CA
# 根 CA
openssl genrsa -out root-ca.key 4096
openssl req -new -x509 -key root-ca.key \
  -out root-ca.crt -days 3650 \
  -subj "/C=CN/O=Company/CN=Company Root CA"

# 颁发 CA
openssl genrsa -out issuing-ca.key 4096
openssl req -new -key issuing-ca.key \
  -out issuing-ca.csr \
  -subj "/C=CN/O=Company/CN=Company Issuing CA"
openssl x509 -req -in issuing-ca.csr \
  -CA root-ca.crt -CAkey root-ca.key \
  -CAcreateserial -out issuing-ca.crt \
  -days 1825 -extfile ca-ext.cnf

1.3 RADIUS 部署
# FreeRADIUS 安装和配置
apt install freeradius freeradius-mysql
# 配置 EAP-TLS（见 2.1 节配置）
# 测试认证
radtest -t tls user@company.com password localhost 0 testing123

阶段2: WiFi 安全升级（第3-4周）

2.1 AP 固件升级
# 批量升级 AP 固件
for ap_ip in $(cat ap_list.txt); do
    ssh admin@$ap_ip "upgrade firmware wpa3-support.bin"
done

2.2 WPA3-Enterprise 部署
# WLC 配置 WPA3-Enterprise
wlan security wpa3 enable
wlan security wpa3-enterprise
wlan security 802.1x enable
wlan security pmf mandatory

2.3 访客 Portal 部署
# Portal 服务器配置
# HTTPS 证书部署
# 短信验证接口对接
# COA 授权配置

阶段3: 安全监控部署（第5-6周）

3.1 WIDS 传感器部署
# 每层楼部署 2 个传感器
# 配置监控覆盖
# 关联 WLC 和 SIEM

3.2 告警策略配置
# Rogue AP 检测
# Evil Twin 检测
# Deauth 攻击检测
# 异常行为检测

阶段4: 客户端迁移（第7-8周）

4.1 证书分发
# MDM 推送 WiFi Profile
# 包含 CA 证书和客户端证书
# 配置证书验证

4.2 分批迁移
# 第一批: IT 部门（试点）
# 第二批: 管理层
# 第三批: 全体员工
# 每批观察 3 天再推进

阶段5: 验收和运维（第9-10周）

5.1 安全验证
# 渗透测试
# 配置审计
# 合规检查

5.2 运维交接
# 运维文档
# 培训
# 监控面板
```

### 8.4 安全效果评估

```
加固前后对比：

安全指标          加固前          加固后
认证方式          WPA2-PSK       WPA3-Enterprise (EAP-TLS)
加密强度          AES-128        AES-256-GCM
密钥管理          共享密码        证书+PKI
网络隔离          无              4个VLAN隔离
Rogue AP检测     无              实时检测+自动响应
管理帧保护        无              PMF强制启用
固件更新          3年未更新       自动更新
访客安全          共享网络        Portal+隔离
监控告警          无              7x24 WIDS+SIEM
安全策略          无              完整安全体系

残余风险评估：
├── 旧设备兼容性: 部分 802.1x 不支持的设备需单独处理
├── 用户适应性: 证书认证初期可能有用户体验问题
├── 运维复杂度: 安全架构增加运维复杂度
└── 持续改进: 需要定期评估和更新
```

---

---

