# 网络访问控制NAC

### 5.1 802.1X认证

802.1X是IEEE定义的网络访问控制标准，基于端口认证实现对网络访问的控制。它在设备接入网络时进行身份验证，只有认证通过的设备才能访问网络资源。

**802.1X架构组件：**

```
802.1X认证流程：

┌──────────┐         ┌──────────┐         ┌──────────┐
│  Supplicant │ ←──EAP──→ │  Authenticator│ ←──RADIUS──→ │  Authentication │
│  (客户端)   │         │  (交换机/AP)   │         │  Server(RADIUS) │
└──────────┘         └──────────┘         └──────────┘

认证流程：
1. 客户端连接交换机端口
2. 交换机端口处于未授权状态（只能发EAP包）
3. 交换机发送EAP-Request/Identity
4. 客户端回EAP-Response/Identity（用户名）
5. 交换机转发给RADIUS服务器
6. RADIUS选择认证方法（EAP-TLS/PEAP/MSCHAPv2）
7. 双方完成认证交互
8. RADIUS返回Accept/Reject
9. 交换机开放端口或保持关闭
```

**Cisco 802.1X配置：**

```
! 全局配置
aaa new-model
aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius

! RADIUS服务器配置
radius server ISE_SERVER
  address ipv4 10.1.1.100 auth-port 1812 acct-port 1813
  key 7 StrongSharedSecret123
  timeout 5
  retransmit 3

! 启用Dot1x
dot1x system-auth-control

! 接口配置
interface GigabitEthernet0/1
  switchport mode access
  switchport access vlan 100
  authentication port-control auto
  dot1x pae authenticator
  dot1x timeout quiet-period 10
  dot1x timeout tx-period 5
  dot1x max-req 3
  dot1x max-reauth-req 2

  ! Guest VLAN（认证失败的访客VLAN）
  dot1x guest-vlan 200

  ! Critical VLAN（RADIUS不可达时的VLAN）
  authentication event server dead action authorize vlan 300

  ! MAC旁路（非802.1X设备）
  dot1x mac-auth-bypass

  ! 端口安全
  switchport port-security
  switchport port-security maximum 2
  switchport port-security violation restrict
!
```

### 5.2 终端安全检查

NAC通常结合终端安全检查，确保接入设备满足安全基线要求（如防病毒软件安装、系统补丁更新等）。

**Cisco ISE终端安全检查配置：**

```xml
<!-- ISE Posture Policy -->
<posture-policy>
  <name>Corporate_Standard_Posture</name>
  <conditions>
    <!-- 防病毒软件检查 -->
    <condition name="AV_Installed">
      <type>file</type>
      <check>
        <path>C:\Program Files\Antivirus\av.exe</path>
        <must-exist>true</must-exist>
      </check>
    </condition>

    <!-- 系统补丁检查 -->
    <condition name="Patch_Level">
      <type>registry</type>
      <check>
        <key>HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate</key>
        <value>LastUpdate</value>
        <min-days-ago>30</min-days-ago>
      </check>
    </condition>

    <!-- 防火墙启用检查 -->
    <condition name="Firewall_Enabled">
      <type>service</type>
      <check>
        <service>MpsSvc</service>
        <must-be-running>true</must-be-running>
      </check>
    </condition>
  </conditions>

  <actions>
    <on-success>
      <assign-vlan>100</assign-vlan>
      <download-acl>permit_any</download-acl>
    </on-success>
    <on-failure>
      <assign-vlan>200</assign-vlan>
      <redirect-url>https://ise.example.com/remediation</redirect-url>
    </on-failure>
  </actions>
</posture-policy>
```

### 5.3 准入控制

准入控制是基于认证结果和终端安全检查结果，动态分配网络访问权限的机制。

```
准入控制策略矩阵：

┌────────────────┬────────────────┬────────────────┬──────────┐
│ 设备类型        │ 认证状态        │ 安全检查       │ VLAN分配 │
├────────────────┼────────────────┼────────────────┼──────────┤
│ 企业PC          │ 802.1X认证通过 │ 通过           │ VLAN 100  │
│ 企业PC          │ 802.1X认证通过 │ 不通过         │ VLAN 200  │
│ 企业PC          │ 认证失败       │ -              │ VLAN 300  │
│ 访客设备        │ Web认证通过    │ -              │ VLAN 400  │
│ IP电话          │ MAB认证通过    │ -              │ VLAN 500  │
│ 摄像头          │ MAB认证通过    │ -              │ VLAN 600  │
│ 未知设备        │ 无认证         │ -              │ VLAN 999  │
└────────────────┴────────────────┴────────────────┴──────────┘
```

### 5.4 动态VLAN分配

通过RADIUS返回VLAN属性，实现基于认证结果的动态VLAN分配：

```
! FreeRADIUS用户配置（动态VLAN）

# /etc/freeradius/3.0/mods-config/files/authorize

# 企业员工 - 完全访问
user1 Cleartext-Password := "password123"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "100"

# 不合规设备 - 隔离VLAN
user2 Cleartext-Password := "password456"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "200"

# 访客 - 访客VLAN
guest_user Cleartext-Password := "guest"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "400"
    Session-Timeout = 3600,
    Idle-Timeout = 600
```

**基于MAC地址的设备识别（MAB）：**

```
! 交换机配置MAB
interface GigabitEthernet0/1
  switchport mode access
  mab
  dot1x pae authenticator
  dot1x mac-auth-bypass
  dot1x timeout server-timeout 10
  authentication port-control auto
  authentication order mab dot1x
  authentication priority dot1x mab
!

! FreeRADIUS MAC地址白名单
# 打印机MAC地址
001122334455 User-Password == "001122334455"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "700"

# IP电话MAC地址
0066778899AA User-Password == "0066778899AA"
    Tunnel-Type = 13,
    Tunnel-Medium-Type = 6,
    Tunnel-Private-Group-Id = "500"
```

---

---

## 📋 内容审核与补充建议

> 针对「网络访问控制NAC」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
