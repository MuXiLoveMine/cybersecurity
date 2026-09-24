# Zigbee 安全

### 6.1 Zigbee 安全架构

```
Zigbee 安全架构：

安全层级：
├── MAC 层安全（IEEE 802.15.4）
│   ├── AES-128 对称加密
│   ├── CCM* 操作模式
│   ├── 帧计数器防重放
│   └── 可选安全等级
├── 网络层安全（NWK）
│   ├── 网络密钥（Network Key）
│   ├── 所有设备共享
│   ├── 用于网络层帧加密
│   └── 信任中心分发
├── 应用层安全（APS）
│   ├── 链接密钥（Link Key）
│   ├── 设备间专用密钥
│   ├── 应用层帧加密
│   └── 端到端安全
└── 信任中心（Trust Center）
    ├── 密钥管理
    ├── 设备入网控制
    └── 密钥更新

Zigbee 密钥体系：

1. 网络密钥（Network Key）
   ├── 128 位 AES 密钥
   ├── 网络中所有设备共享
   ├── 用于网络层加密
   ├── 定期更新
   └── 信任中心生成和分发

2. 链接密钥（Link Key）
   ├── 128 位 AES 密钥
   ├── 设备与信任中心之间
   ├── 用于 APS 层加密
   ├── 全局链接密钥（默认）
   └── 个体链接密钥（推荐）

3. 应用密钥（Application Key）
   ├── 应用层端到端密钥
   ├── 两个应用之间共享
   └── 通过 APS 传输

4. 安装码（Install Code）
   ├── 用于设备入网
   ├── 防止伪造设备加入
   ├── 厂商预置或现场输入
   └── 用于派生链接密钥
```

### 6.2 Zigbee 安全流程

```
Zigbee 设备入网安全流程：

1. 设备发现
   ├── 新设备发送 Beacon Request
   ├── 路由器/协调器响应 Beacon
   └── 设备选择网络加入

2. 关联请求
   ├── 新设备发送 Association Request
   ├── 包含设备能力信息
   └── 协调器/路由器决定是否允许

3. 密钥协商
   ├── 方式A: 预配置链接密钥
   │   ├── 设备出厂预置
   │   ├── 安装码派生
   │   └── 直接使用预共享密钥
   ├── 方式B: 信任中心分发
   │   ├── 信任中心生成密钥
   │   ├── 通过 APS Transport Key 命令分发
   │   └── 使用链接密钥加密传输

4. 网络密钥分发
   ├── 信任中心发送网络密钥
   ├── 使用链接密钥加密
   ├── 设备存储网络密钥
   └── 开始加密通信

5. 密钥更新
   ├── 信任中心定期更新网络密钥
   ├── 帧计数器防止重放
   └── 平滑过渡到新密钥

安全等级：
├── 无安全 (None): 无加密无认证
├── 认证 (MIC-32/64/128): 仅完整性
├── 加密 (ENC-MIC-32/64/128): 加密+完整性
└── CCM* 模式支持所有等级
```

### 6.3 Zigbee 攻击工具

```
Zigbee 安全测试工具：

1. KillerBee
   ├── Zigbee 安全研究框架
   ├── 支持多种硬件（ApiMote, rzusbstick）
   ├── 数据包注入和嗅探
   └── Python API

# 安装 KillerBee
git clone https://github.com/riverloopsec/killerbee.git
cd killerbee
pip install .

# 嗅探 Zigbee 流量
zbdump -f 11 -c 11 -w capture.pcap

# 注入数据包
zbassocflod -p AA:BB -c 11

# 分析数据
zbconvert -i capture.pcap -o output.pcap

2. Atmel RZ Raven
   ├── 硬件 Zigbee 开发工具
   ├── 支持监听和注入
   ├── USB 接口
   └── AVR 微控制器

3. ApiMote v4
   ├── 开源 Zigbee 测试硬件
   ├── 基于 Atmel AT86RF230
   ├── 支持 KillerBee
   └── 支持数据包注入

4. EFR32 Mighty Gecko
   ├── Silicon Labs 开发板
   ├── 支持 Zigbee 3.0
   ├── 内置协议分析器
   └── 支持 ARM TrustZone

已知 Zigbee 漏洞：

1. 默认链接密钥
   ├── Zigbee Alliance 默认密钥: wellknownkey
   ├── 很多设备不修改默认密钥
   ├── 攻击者可解密密钥传输
   └── 获取网络密钥

2. Z-Stack 漏洞
   ├── Texas Instruments Z-Stack
   ├── 内存损坏漏洞
   ├── 可远程代码执行
   └── 影响多种 IoT 设备

3. 关联泛洪
   ├── 发送大量关联请求
   ├── 消耗协调器资源
   ├── DoS 攻击
   └── KillerBee zbstumbler

4. 密钥窃取
   ├── 如果使用默认链接密钥
   ├── 可解密网络密钥传输
   ├── 获取网络密钥
   └── 解密/注入网络流量

5. Rejoin 攻击
   ├── 伪造 Rejoin Request
   ├── 使用默认链接密钥
   ├── 绕过入网控制
   └── 获取网络访问权限

防御措施：
├── 修改默认链接密钥
├── 使用安装码入网
├── 个体链接密钥（非全局）
├── 定期更新网络密钥
├── 禁用不必要的 Rejoin
├── 部署 Zigbee 安全网关
└── 固件安全更新
```

---

---

