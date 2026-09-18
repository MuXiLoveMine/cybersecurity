# DHCP攻击检测方法

### 3.1 基于流量的检测

**异常DHCP流量监控**

正常网络环境中DHCP流量具有规律性模式。异常检测关注以下指标：

| 指标 | 正常范围 | 异常表现 |
|------|----------|----------|
| DHCPDISCOVER速率 | <10/分钟 | >100/分钟可能饥饿攻击 |
| MAC地址多样性 | 合法设备数 | 短时间内大量不同MAC |
| DHCP服务器数量 | 1-2台 | 多台服务器响应 |
| 地址池利用率 | <80% | 突然达到100% |
| DHCP报文比率 | DISCOVER:OFFER≈1:1 | DISCOVER远多于OFFER |

**流量采集与统计**

使用SNMP或NetFlow监控DHCP流量：

```
# Cisco设备查看DHCP统计
show ip dhcp binding
show ip dhcp server statistics
show ip dhcp conflict

# Linux统计DHCP流量
tcpdump -i eth0 -nn port 67 or port 68 -c 1000 | \
  awk '{print $NF}' | sort | uniq -c | sort -rn
```

### 3.2 基于行为的检测

**MAC地址异常检测**

DHCP饥饿攻击需要伪造大量MAC地址，检测策略包括：

- **MAC地址变化率**：同一端口短时间内出现大量不同MAC地址
- **MAC地址格式异常**：非OUI分配的MAC地址（随机生成的MAC通常本地管理位置1）
- **MAC-Port绑定异常**：同一MAC在多个端口出现

**响应时间分析**

伪造DHCP服务器通常比合法服务器响应更快。通过测量DHCPDISCOVER到DHCPOFFER的延迟可以识别异常：

- 正常服务器延迟：10-100ms（包括地址选择和冲突检测）
- 伪造服务器延迟：<10ms（不做冲突检测）
- 如果网络中存在响应延迟差异大的DHCP服务器，需要排查

### 3.3 基于特征的检测

**DHCP报文特征匹配**

- **Option 54不匹配**：DHCPOFFER/DHCPACK中的Server Identifier不是已知合法服务器
- **Option 82异常**：中继代理信息与预期不符
- **服务器MAC不匹配**：发送DHCP响应的设备MAC不在白名单中
- **异常Option组合**：报文中包含非标准或异常的选项组合

### 3.4 自动化检测工具

**DHCP探测工具**

DHCPing是一个DHCP服务器探测工具：

```bash
# 探测网络中的DHCP服务器
dhcping -s 255.255.255.255 -c

# 查看特定服务器的响应
dhcping -s 192.168.1.1 -r
```

**使用Scapy构建检测脚本**

```python
from scapy.all import *
import time
from collections import defaultdict

class DHCPDetector:
    """DHCP攻击检测器"""

    def __init__(self, interface, legit_servers=None):
        self.interface = interface
        self.legit_servers = legit_servers or []
        self.discover_count = defaultdict(int)
        self.server_set = set()
        self.mac_set = set()
        self.start_time = time.time()
        self.alerts = []

    def detect_starvation(self, packet):
        """检测DHCP饥饿攻击"""
        if packet.haslayer(DHCP):
            for opt in packet[DHCP].options:
                if opt[0] == 'message-type' and opt[1] == 1:
                    # DHCPDISCOVER
                    src_mac = packet[Ether].src
                    self.mac_set.add(src_mac)

                    # 统计每分钟DISCOVER数量
                    elapsed = time.time() - self.start_time
                    if elapsed > 0:
                        rate = len(self.mac_set) / elapsed * 60
                        if rate > 50:  # 阈值：50个不同MAC/分钟
                            alert = f'[!] 可能的DHCP饥饿攻击! ' \
                                   f'检测到{len(self.mac_set)}个不同MAC, ' \
                                   f'速率: {rate:.1f}/分钟'
                            self.alerts.append(alert)
                            print(alert)

    def detect_rogue_server(self, packet):
        """检测伪造DHCP服务器"""
        if packet.haslayer(DHCP):
            for opt in packet[DHCP].options:
                if opt[0] == 'message-type' and opt[1] in (2, 5):
                    # DHCPOFFER or DHCPACK
                    server_ip = packet[IP].src
                    self.server_set.add(server_ip)

                    if self.legit_servers and server_ip not in self.legit_servers:
                        alert = f'[!] 检测到伪造DHCP服务器! ' \
                               f'服务器IP: {server_ip}'
                        self.alerts.append(alert)
                        print(alert)

    def start(self):
        """启动检测"""
        print(f'[*] DHCP攻击检测器已启动, 监听接口: {self.interface}')
        print(f'[*] 合法DHCP服务器: {self.legit_servers}')

        def callback(packet):
            self.detect_starvation(packet)
            self.detect_rogue_server(packet)

        sniff(iface=self.interface, filter='udp port 67 or udp port 68',
              prn=callback, store=0)

if __name__ == '__main__':
    detector = DHCPDetector(
        interface='eth0',
        legit_servers=['192.168.1.1']
    )
    detector.start()
```

---

---

## 📋 内容审核与补充建议

> 针对「DHCP攻击检测方法」部分的内容审核结果：

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
