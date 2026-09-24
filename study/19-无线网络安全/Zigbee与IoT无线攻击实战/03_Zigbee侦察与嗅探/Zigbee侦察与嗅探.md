# Zigbee侦察与嗅探

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

---

